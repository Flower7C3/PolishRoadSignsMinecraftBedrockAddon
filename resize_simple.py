#!/usr/bin/env python3
import json
import os
import subprocess
import re
import sys
import time
from pathlib import Path

def normalize_sign_id(sign_code):
    """Normalizuj kod znaku do formatu używanych w bazie danych"""
    # Usuń spacje i zamień na podkreślenie
    normalized = sign_code.strip().replace(' ', '_')
    
    # Zamień myślniki na podkreślenia
    normalized = normalized.replace('-', '_')
    
    # Zamień na małe litery
    normalized = normalized.lower()
    
    # Jeśli kod nie ma podkreślnika, dodaj go przed liczbą
    # Przykład: "a1" -> "a_1", "b5" -> "b_5", "c10" -> "c_10"
    if '_' not in normalized and len(normalized) > 1:
        # Znajdź pierwszą cyfrę
        for i, char in enumerate(normalized):
            if char.isdigit():
                # Wstaw podkreślnik przed pierwszą cyfrą
                normalized = normalized[:i] + '_' + normalized[i:]
                break
    
    return normalized

def find_sign_in_database(sign_id, data):
    """Znajdź znak w bazie danych"""
    for category in ['A', 'B', 'C', 'D']:
        if sign_id in data['road_signs'][category]['signs']:
            return data['road_signs'][category]['signs'][sign_id]
    return None

def download_wikipedia_page(url):
    """Pobierz stronę Wikipedii"""
    try:
        result = subprocess.run(['curl', '-A', 'Mozilla/5.0', '-L', '--insecure', url], 
                              capture_output=True, text=True, timeout=30)
        return result.stdout
    except Exception as e:
        print(f"Błąd pobierania strony: {e}")
        return None

def extract_svg_url(html_content):
    """Wyciągnij link do pliku SVG z HTML - ulepszona wersja"""
    # Najpierw szukaj w .fullImageLink (lepsze parsowanie)
    full_image_pattern = r'href="([^"]*\.svg)"[^>]*class="[^"]*fullImageLink[^"]*"'
    match = re.search(full_image_pattern, html_content)
    if match:
        svg_url = match.group(1)
        if svg_url.startswith('//'):
            svg_url = 'https:' + svg_url
        elif svg_url.startswith('/'):
            svg_url = 'https://pl.wikipedia.org' + svg_url
        print(f"✓ Znaleziono SVG (fullImageLink): {svg_url}")
        return svg_url
    
    # Fallback: szukaj linku do pliku SVG w upload.wikimedia.org
    upload_pattern = r'href="//upload\.wikimedia\.org/wikipedia/commons/[^"]*\.svg"'
    match = re.search(upload_pattern, html_content)
    if match:
        svg_url = "https:" + match.group().replace('href="', '').replace('"', '')
        print(f"✓ Znaleziono SVG (fallback): {svg_url}")
        return svg_url
    
    # Dodatkowy fallback: szukaj bezpośrednich linków
    direct_pattern = r'https://upload\.wikimedia\.org/[^"]*\.svg'
    match = re.search(direct_pattern, html_content)
    if match:
        svg_url = match.group(0)
        print(f"✓ Znaleziono SVG (direct): {svg_url}")
        return svg_url
    
    return None

def download_svg(svg_url, output_path):
    """Pobierz plik SVG"""
    try:
        result = subprocess.run(['curl', '-A', 'Mozilla/5.0', '-L', '--insecure', svg_url, '-o', output_path], 
                              capture_output=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"Błąd pobierania SVG: {e}")
        return False

def convert_svg_to_png(svg_path, png_path, target_width):
    """Konwertuj SVG na PNG z określoną szerokością"""
    try:
        result = subprocess.run([
            'inkscape', 
            '--export-type=png', 
            f'--export-width={target_width}',
            f'--export-filename={png_path}',
            svg_path
        ], capture_output=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"Błąd konwersji SVG: {e}")
        return False

def get_image_dimensions(png_path):
    """Pobierz wymiary obrazka PNG - ulepszona wersja"""
    try:
        # Najpierw spróbuj z identify (szybsze)
        result = subprocess.run(['identify', '-format', '%wx%h', png_path], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            dimensions = result.stdout.strip()
            width, height = map(int, dimensions.split('x'))
            return width, height
    except:
        pass
    
    # Fallback: użyj PIL jeśli identify nie działa
    try:
        from PIL import Image
        with Image.open(png_path) as img:
            return img.size[0], img.size[1]
    except Exception as e:
        print(f"Błąd pobierania wymiarów: {e}")
    return None, None

def create_model_if_needed(width, height):
    """Twórz model jeśli nie istnieje"""
    model_name = f"road_sign_rectangle_{width}x{height}"
    model_path = f"RP/models/blocks/{model_name}.geo.json"
    
    if os.path.exists(model_path):
        print(f"✓ Model już istnieje: {model_name}")
        return model_name
    
    # Twórz model na podstawie szablonu
    template = {
        "format_version": "1.21.90",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": f"geometry.{model_name}",
                    "texture_width": width,
                    "texture_height": height,
                    "visible_bounds_width": width / 64,
                    "visible_bounds_height": height / 64,
                    "visible_bounds_offset": [0, height / 128, 0]
                },
                "bones": [
                    {
                        "name": "block",
                        "pivot": [0, 0, 0],
                        "rotation": [0, 180, 0],
                        "cubes": [
                            {
                                "origin": [-width // 16, 0, 0],
                                "size": [width // 8, height // 8, 0.1],
                                "uv": {
                                    "north": {"uv": [0, 0], "uv_size": [width, height]},
                                    "east": {"uv": [0, 0], "uv_size": [width, height]},
                                    "south": {"uv": [0, 0], "uv_size": [width, height]},
                                    "west": {"uv": [0, 0], "uv_size": [width, height]},
                                    "up": {"uv": [width // 8, width // 8], "uv_size": [width, height]},
                                    "down": {"uv": [width // 8, width // 8], "uv_size": [width, height]}
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    with open(model_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✓ Utworzono model: {model_name}")
    return model_name

def create_background_texture_if_needed(width, height):
    """Twórz teksturę tła jeśli nie istnieje"""
    texture_name = f"rectangle_back_{width}x{height}"
    texture_path = f"RP/textures/blocks/sign_backs/{texture_name}.png"
    
    if os.path.exists(texture_path):
        print(f"✓ Tekstura tła już istnieje: {texture_name}")
        return texture_name
    
    # Twórz szarą teksturę tła w formacie RGB
    try:
        subprocess.run(['magick', '-size', f'{width}x{height}', 'xc:#808080', '-define', 'png:color-type=2', texture_path], check=True)
        print(f"✓ Utworzono teksturę tła: {texture_name}")
    except subprocess.CalledProcessError as e:
        print(f"Błąd tworzenia tekstury tła {texture_name}: {e}")
        return None
    
    return texture_name

def add_to_terrain_texture(texture_name):
    """Dodaj teksturę do terrain_texture.json"""
    terrain_path = "RP/textures/terrain_texture.json"
    
    with open(terrain_path, 'r') as f:
        terrain = json.load(f)
    
    # Sprawdź czy już istnieje
    if f"polish_road_sign:{texture_name}" in terrain["texture_data"]:
        print(f"✓ Tekstura {texture_name} już istnieje w terrain_texture.json")
        return
    
    # Dodaj wpis tekstury
    terrain["texture_data"][f"polish_road_sign:{texture_name}"] = {
        "textures": f"textures/blocks/sign_backs/{texture_name}.png"
    }
    
    with open(terrain_path, 'w') as f:
        json.dump(terrain, f, indent=2)
    
    print(f"✓ Dodano {texture_name} do terrain_texture.json")

def update_block_definition(sign_id, model_name, background_name):
    """Zaktualizuj definicję bloku"""
    category = sign_id.split('_')[0]
    block_path = f"BP/blocks/{category}/{sign_id}.block.json"
    
    if not os.path.exists(block_path):
        print(f"⚠️  Nie znaleziono pliku bloku: {block_path}")
        return False
    
    with open(block_path, 'r') as f:
        block_data = json.load(f)
    
    # Zaktualizuj geometrię
    block_data["minecraft:block"]["components"]["minecraft:geometry"] = f"geometry.{model_name}"
    
    # Zaktualizuj teksturę tła
    for face, material in block_data["minecraft:block"]["components"]["minecraft:material_instances"].items():
        if face == "north":  # Tylna strona
            material["texture"] = f"polish_road_sign:{background_name}"
            break
    
    # Zapisz zaktualizowany blok
    with open(block_path, 'w') as f:
        json.dump(block_data, f, indent=2)
    
    print(f"✓ Zaktualizowano blok {sign_id}: model={model_name}, tło={background_name}")
    return True

def update_database(database_path, sign_id, width, height):
    """Zaktualizuj bazę danych z nowymi wymiarami"""
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Znajdź znak w bazie
        for category in ['A', 'B', 'C', 'D']:
            if sign_id in data['road_signs'][category]['signs']:
                data['road_signs'][category]['signs'][sign_id]['image_width'] = str(width)
                data['road_signs'][category]['signs'][sign_id]['image_height'] = str(height)
                
                # Dodaj image_dimensions jeśli istnieje
                if 'image_dimensions' in data['road_signs'][category]['signs'][sign_id]:
                    data['road_signs'][category]['signs'][sign_id]['image_dimensions'] = f"{width}x{height}"
                break
        
        # Zapisz zaktualizowaną bazę
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Zaktualizowano bazę dla {sign_id}: {width}x{height}")
        return True
    except Exception as e:
        print(f"Błąd aktualizacji bazy: {e}")
        return False

def process_sign(sign_id, wikipedia_file_page, target_width, database_path):
    """Przetwórz pojedynczy znak z automatycznym tworzeniem modeli i tekstur"""
    print(f"\n🔍 Przetwarzanie {sign_id}...")
    
    # Pobierz stronę Wikipedii
    html_content = download_wikipedia_page(wikipedia_file_page)
    if not html_content:
        print(f"❌ Nie udało się pobrać strony dla {sign_id}")
        return False
    
    # Wyciągnij link do SVG
    svg_url = extract_svg_url(html_content)
    if not svg_url:
        print(f"❌ Nie znaleziono linku SVG dla {sign_id}")
        return False
    
    # Przygotuj katalogi
    category = sign_id.split('_')[0]
    target_dir = f"RP/textures/blocks/{category}"
    os.makedirs(target_dir, exist_ok=True)
    
    # Pobierz SVG do katalogu cache obok PNG
    svg_path = f"{target_dir}/{sign_id}.svg"
    if not download_svg(svg_url, svg_path):
        print(f"❌ Nie udało się pobrać SVG dla {sign_id}")
        return False
    
    print(f"✓ Pobrano SVG: {svg_path}")
    
    # Konwertuj na PNG w tym samym katalogu
    png_path = f"{target_dir}/{sign_id}.png"
    if not convert_svg_to_png(svg_path, png_path, target_width):
        print(f"❌ Nie udało się skonwertować SVG dla {sign_id}")
        return False
    
    print(f"✓ Skonwertowano na PNG: {png_path}")
    
    # Pobierz rzeczywiste wymiary
    width, height = get_image_dimensions(png_path)
    if width is None or height is None:
        print(f"❌ Nie udało się pobrać wymiarów dla {sign_id}")
        return False
    
    print(f"✓ Wymiary: {width}x{height}")
    
    # Automatycznie twórz model i teksturę tła
    model_name = create_model_if_needed(width, height)
    background_name = create_background_texture_if_needed(width, height)
    
    if background_name:
        add_to_terrain_texture(background_name)
    
    # Zaktualizuj definicję bloku
    if update_block_definition(sign_id, model_name, background_name):
        print(f"✓ Zaktualizowano definicję bloku {sign_id}")
    
    # Zaktualizuj bazę danych
    if update_database(database_path, sign_id, width, height):
        print(f"✅ {sign_id} - gotowe!")
        return True
    else:
        print(f"❌ Błąd aktualizacji bazy dla {sign_id}")
        return False

def main():
    """Główna funkcja"""
    database_path = "road_signs_full_database.json"
    
    if not os.path.exists(database_path):
        print(f"❌ Nie znaleziono bazy danych: {database_path}")
        return
    
    # Sprawdź argumenty
    if len(sys.argv) < 2:
        print("❌ Użycie: python resize_simple.py <kod_znaku1> [kod_znaku2] [kod_znaku3] ...")
        print("   Przykłady:")
        print("     python resize_simple.py a-1")
        print("     python resize_simple.py B_5 c-10 d_25")
        print("     python resize_simple.py A1 B2 C3 D4")
        print("     python resize_simple.py all  # przetwórz wszystkie znaki")
        return
    
    # Wczytaj bazę danych
    with open(database_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🚀 Rozpoczynam pobieranie obrazków...")
    print("=" * 50)
    
    success_count = 0
    total_count = 0
    errors = []
    
    # Sprawdź czy przetwarzamy wszystkie znaki
    if len(sys.argv) == 2 and sys.argv[1].lower() == 'all':
        print("📋 Przetwarzanie wszystkich znaków z bazy danych...")
        
        for category in ['A', 'B', 'C', 'D']:
            if category in data['road_signs']:
                print(f"\n📁 Kategoria {category}...")
                signs = data['road_signs'][category]['signs']
                
                for sign_id in signs:
                    total_count += 1
                    
                    # Sprawdź czy znak ma link do Wikipedii
                    if 'wikipedia_file_page' not in signs[sign_id]:
                        print(f"⚠️  {sign_id}: brak linku do Wikipedii")
                        continue
                    
                    wikipedia_file_page = signs[sign_id]['wikipedia_file_page']
                    target_width = int(signs[sign_id].get('image_width', 128))
                    
                    if process_sign(sign_id, wikipedia_file_page, target_width, database_path):
                        success_count += 1
                    else:
                        errors.append(f"{sign_id}: błąd przetwarzania")
                    
                    # Dodaj delay między requestami (szanuj serwery)
                    time.sleep(1)
    else:
        # Przetwórz podane znaki
        for sign_code in sys.argv[1:]:
            total_count += 1
            
            # Normalizuj kod znaku
            sign_id = normalize_sign_id(sign_code)
            print(f"\n📋 Kod: {sign_code} → {sign_id}")
            
            # Znajdź znak w bazie
            sign_data = find_sign_in_database(sign_id, data)
            if not sign_data:
                print(f"❌ Nie znaleziono znaku {sign_id} w bazie danych")
                errors.append(f"{sign_id}: nie znaleziono w bazie")
                continue
            
            # Sprawdź czy znak ma link do Wikipedii
            if 'wikipedia_file_page' not in sign_data:
                print(f"⚠️  {sign_id}: brak linku do Wikipedii")
                errors.append(f"{sign_id}: brak linku do Wikipedii")
                continue
            
            wikipedia_file_page = sign_data['wikipedia_file_page']
            target_width = int(sign_data.get('image_width', 128))
            
            print(f"📏 Docelowa szerokość: {target_width}px")
            
            if process_sign(sign_id, wikipedia_file_page, target_width, database_path):
                success_count += 1
            else:
                errors.append(f"{sign_id}: błąd przetwarzania")
    
    print("\n" + "=" * 50)
    print(f"📊 PODSUMOWANIE:")
    print(f"   Sukces: {success_count}/{total_count}")
    print(f"   Niepowodzenia: {total_count - success_count}")
    
    if errors:
        print(f"\n❌ BŁĘDY:")
        for error in errors:
            print(f"   - {error}")
    else:
        print(f"\n✅ Wszystkie znaki przetworzone pomyślnie!")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 