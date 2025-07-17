import os
import json
import requests
from PIL import Image
from io import BytesIO
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

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def download_and_resize_image(sign_data):
    """Pobierz obrazek i przeskaluj z zachowaniem proporcji"""
    try:
        # Sprawdź czy jest image_url
        if 'image_url' not in sign_data or not sign_data['image_url']:
            print(f"  Brak URL dla {sign_data['code']}")
            return False
        
        url = sign_data['image_url']
        print(f"  Pobieranie {sign_data['code']} z {url}")
        
        # Pobierz obrazek
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
        
        # Otwórz obrazek
        img = Image.open(BytesIO(resp.content))
        
        # Konwertuj na RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Sprawdź wymiary
        w, h = img.size
        print(f"    Oryginalny rozmiar: {w}x{h}")
        
        # Przeskaluj - dłuższy bok będzie miał 128px
        if w > h:
            # Szerokość jest większa
            new_w = 128
            new_h = int(h * 128 / w)
        else:
            # Wysokość jest większa lub równa
            new_h = 128
            new_w = int(w * 128 / h)
        
        # Przeskaluj obrazek
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Zapisz
        category = sign_data['code'].split('-')[0].lower()
        filename = sign_data['code'].replace('-', '_').lower()
        filepath = os.path.join(BASE_TEXTURE_PATH, category, f"{filename}.png")
        
        ensure_dir(os.path.dirname(filepath))
        img.save(filepath, 'PNG')
        
        print(f"    Zapisano: {filepath} ({new_w}x{new_h})")
        return True
        
    except Exception as e:
        print(f"  Błąd dla {sign_data['code']}: {e}")
        return False

def main():
    print("=== Pobieranie i przeskalowanie tekstur z zachowaniem proporcji ===")
    
    # Wczytaj bazę danych
    db = load_db()
    
    success_count = 0
    error_count = 0
    
    # Przejdź przez wszystkie kategorie znaków
    for category_key, category_data in db['road_signs'].items():
        print(f"\nPrzetwarzanie kategorii: {category_key}")
        
        # Przejdź przez wszystkie znaki w kategorii
        for sign_key, sign_data in category_data['signs'].items():
            if download_and_resize_image(sign_data):
                success_count += 1
            else:
                error_count += 1
            
            # Krótka przerwa między pobieraniami
            time.sleep(0.5)
    
    print(f"\n=== Zakończono ===")
    print(f"Pomyślnie pobrano: {success_count}")
    print(f"Błędy: {error_count}")

if __name__ == "__main__":
    main() 