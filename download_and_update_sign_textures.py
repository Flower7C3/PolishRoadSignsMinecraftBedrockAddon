import os
import json
import requests
from PIL import Image
from io import BytesIO
import re
from bs4 import BeautifulSoup
import time

DB_PATH = 'road_signs_full_database.json'
BASE_TEXTURE_PATH = 'RP/textures/blocks'

# Konfiguracja sesji requests z odpowiednim User-Agent
session = requests.Session()
session.headers.update({
    'User-Agent': 'PolishRoadSigns/1.0 (https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon; bot@example.com) Python/3.13'
})

def load_db():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def find_image_on_wikipedia_page(wikipedia_url, sign_code):
    """Znajdź obrazek znaku drogowego na stronie Wikipedii"""
    try:
        print(f"  Szukam obrazka dla {sign_code} na: {wikipedia_url}")
        resp = session.get(wikipedia_url, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Szukaj obrazków w sekcji ze znakiem
        # Najpierw spróbuj znaleźć sekcję z kodem znaku
        sign_section = None
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            if sign_code.lower() in heading.get_text().lower():
                sign_section = heading.find_parent()
                break
        
        if sign_section:
            # Szukaj obrazków w sekcji znaku
            images = sign_section.find_all('img')
        else:
            # Szukaj wszystkich obrazków na stronie
            images = soup.find_all('img')
        
        # Szukaj obrazków SVG lub PNG ze znakami drogowymi
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            
            # Sprawdź czy to może być znak drogowy
            if (sign_code.lower() in alt or 
                'znak' in alt or 
                'sign' in alt or
                'drogowy' in alt):
                
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://pl.wikipedia.org' + src
                elif not src.startswith('http'):
                    src = 'https://pl.wikipedia.org' + src
                
                print(f"    Znaleziono potencjalny obrazek: {src}")
                return src
        
        # Jeśli nie znaleziono, spróbuj znaleźć SVG
        for img in images:
            src = img.get('src', '')
            if 'svg' in src.lower() and 'znak' in img.get('alt', '').lower():
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://pl.wikipedia.org' + src
                elif not src.startswith('http'):
                    src = 'https://pl.wikipedia.org' + src
                
                print(f"    Znaleziono SVG: {src}")
                return src
        
        print(f"    Nie znaleziono obrazka dla {sign_code}")
        return None
        
    except Exception as e:
        print(f"    Błąd podczas wyszukiwania obrazka: {e}")
        return None

def download_image(url):
    """Pobierz obrazek z URL"""
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"    Błąd pobierania obrazka: {e}")
        return None

def resize_image(image_data, min_size=128):
    """Przeskaluj obrazek do minimum 128x128 px z zachowaniem proporcji"""
    try:
        img = Image.open(BytesIO(image_data))
        
        # Konwertuj na RGBA jeśli to PNG
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Oblicz nowe wymiary zachowując proporcje
        w, h = img.size
        if w >= min_size and h >= min_size:
            # Obrazek już ma odpowiedni rozmiar
            return img
        
        # Oblicz nowe wymiary
        if w > h:
            new_w = max(min_size, w)
            new_h = int((h * new_w) / w)
        else:
            new_h = max(min_size, h)
            new_w = int((w * new_h) / h)
        
        # Przeskaluj
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Utwórz nowy obrazek 128x128 z przezroczystym tłem
        new_img = Image.new('RGBA', (min_size, min_size), (0, 0, 0, 0))
        
        # Wycentruj oryginalny obrazek
        x = (min_size - new_w) // 2
        y = (min_size - new_h) // 2
        new_img.paste(img, (x, y), img)
        
        return new_img
        
    except Exception as e:
        print(f"    Błąd przetwarzania obrazka: {e}")
        return None

def save_image(img, filepath):
    """Zapisz obrazek do pliku"""
    try:
        ensure_dir(os.path.dirname(filepath))
        img.save(filepath, 'PNG')
        print(f"    Zapisano: {filepath}")
        return True
    except Exception as e:
        print(f"    Błąd zapisywania: {e}")
        return False

def process_sign(sign_data, category, sign_id):
    """Przetwórz pojedynczy znak drogowy"""
    code = sign_data.get('code', '')
    wikipedia_url = sign_data.get('wikipedia_url', '')
    current_image_url = sign_data.get('image_url', '')
    
    print(f"\nPrzetwarzam {code} ({category}/{sign_id})")
    
    # Określ ścieżkę pliku
    if category == 'A':
        filepath = f"{BASE_TEXTURE_PATH}/a/{sign_id}.png"
    elif category == 'B':
        filepath = f"{BASE_TEXTURE_PATH}/b/{sign_id}.png"
    elif category == 'C':
        filepath = f"{BASE_TEXTURE_PATH}/c/{sign_id}.png"
    elif category == 'D':
        filepath = f"{BASE_TEXTURE_PATH}/d/{sign_id}.png"
    else:
        print(f"  Nieznana kategoria: {category}")
        return False
    
    # Sprawdź czy istnieje obrazek w bazie
    if current_image_url and current_image_url.startswith('http'):
        print(f"  Próbuję pobrać z istniejącego URL: {current_image_url}")
        image_data = download_image(current_image_url)
        if image_data:
            img = resize_image(image_data)
            if img and save_image(img, filepath):
                return True
    
    # Jeśli nie ma obrazka lub nie udało się pobrać, szukaj na Wikipedii
    if wikipedia_url:
        print(f"  Szukam obrazka na Wikipedii...")
        new_image_url = find_image_on_wikipedia_page(wikipedia_url, code)
        
        if new_image_url:
            print(f"  Pobieram nowy obrazek: {new_image_url}")
            image_data = download_image(new_image_url)
            if image_data:
                img = resize_image(image_data)
                if img and save_image(img, filepath):
                    # Zaktualizuj bazę z nowym URL
                    return new_image_url
    
    print(f"  Nie udało się znaleźć obrazka dla {code}")
    return False

def main():
    print("=== Pobieranie i aktualizacja tekstur znaków drogowych ===")
    
    # Załaduj bazę
    db = load_db()
    updated_count = 0
    new_urls = 0
    
    # Przetwórz wszystkie znaki
    for category in ['A', 'B', 'C', 'D']:
        if category in db['road_signs']:
            print(f"\n=== Kategoria {category} ===")
            
            for sign_id, sign_data in db['road_signs'][category]['signs'].items():
                result = process_sign(sign_data, category, sign_id)
                
                if result and isinstance(result, str):
                    # Zaktualizuj URL w bazie
                    db['road_signs'][category]['signs'][sign_id]['image_url'] = result
                    new_urls += 1
                    updated_count += 1
                elif result:
                    updated_count += 1
                
                # Krótka przerwa między żądaniami
                time.sleep(0.5)
    
    # Zapisz zaktualizowaną bazę
    if new_urls > 0:
        save_db(db)
        print(f"\nZaktualizowano {new_urls} URL-i w bazie danych")
    
    print(f"\n=== Zakończono ===")
    print(f"Przetworzono: {updated_count} znaków")
    print(f"Nowe URL-e: {new_urls}")

if __name__ == "__main__":
    main() 