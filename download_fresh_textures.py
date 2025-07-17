import os
import json
import requests
from PIL import Image
from io import BytesIO
import re
from bs4 import BeautifulSoup
import time
import urllib.parse

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

def search_wikimedia_commons(sign_code):
    """Wyszukaj obrazek na Wikimedia Commons"""
    try:
        # Przeszukaj Wikimedia Commons
        search_url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={sign_code}+polish+road+sign&format=json&srnamespace=6"
        resp = session.get(search_url, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        if 'query' in data and 'search' in data['query']:
            for result in data['query']['search']:
                title = result['title']
                if 'File:' in title and sign_code.lower() in title.lower():
                    # Pobierz informacje o pliku
                    file_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={title}&prop=imageinfo&iiprop=url&format=json"
                    file_resp = session.get(file_url, timeout=10)
                    file_resp.raise_for_status()
                    
                    file_data = file_resp.json()
                    if 'query' in file_data and 'pages' in file_data['query']:
                        for page_id, page_info in file_data['query']['pages'].items():
                            if 'imageinfo' in page_info:
                                return page_info['imageinfo'][0]['url']
        
        return None
    except Exception as e:
        print(f"    Błąd wyszukiwania na Wikimedia Commons: {e}")
        return None

def search_wikipedia_page(wikipedia_url, sign_code):
    """Wyszukaj obrazek na stronie Wikipedii"""
    try:
        print(f"  Szukam obrazka dla {sign_code} na: {wikipedia_url}")
        resp = session.get(wikipedia_url, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Szukaj obrazków SVG lub PNG
        images = soup.find_all('img')
        
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

def search_government_sources(sign_code):
    """Wyszukaj na oficjalnych stronach rządowych"""
    try:
        # Przeszukaj stronę GDDKiA (Generalna Dyrekcja Dróg Krajowych i Autostrad)
        gddkia_url = f"https://www.gddkia.gov.pl/pl/a/2/znaki-drogowe"
        resp = session.get(gddkia_url, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        images = soup.find_all('img')
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            
            if sign_code.lower() in alt:
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = 'https://www.gddkia.gov.pl' + src
                
                print(f"    Znaleziono na GDDKiA: {src}")
                return src
        
        return None
    except Exception as e:
        print(f"    Błąd wyszukiwania na GDDKiA: {e}")
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

def save_image(image_data, filepath):
    """Zapisz obrazek do pliku"""
    try:
        ensure_dir(os.path.dirname(filepath))
        
        # Otwórz obrazek
        img = Image.open(BytesIO(image_data))
        
        # Konwertuj na RGBA jeśli to PNG
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Sprawdź rozmiar
        w, h = img.size
        print(f"    Pobrano obrazek: {w}x{h} px")
        
        # Jeśli obrazek jest mniejszy niż 128x128, przeskaluj
        if w < 128 or h < 128:
            print(f"    Przeskalowuję do minimum 128x128 px")
            if w > h:
                new_w = max(128, w)
                new_h = int((h * new_w) / w)
            else:
                new_h = max(128, h)
                new_w = int((w * new_h) / h)
            
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Utwórz nowy obrazek 128x128 z przezroczystym tłem
            new_img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
            
            # Wycentruj oryginalny obrazek
            x = (128 - new_w) // 2
            y = (128 - new_h) // 2
            new_img.paste(img, (x, y), img)
            
            img = new_img
        
        # Zapisz
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
    
    # Szukaj obrazka w różnych źródłach
    image_url = None
    
    # 1. Spróbuj Wikimedia Commons
    print(f"  Szukam na Wikimedia Commons...")
    image_url = search_wikimedia_commons(code)
    
    # 2. Jeśli nie znaleziono, spróbuj Wikipedię
    if not image_url and wikipedia_url:
        print(f"  Szukam na Wikipedii...")
        image_url = search_wikipedia_page(wikipedia_url, code)
    
    # 3. Jeśli nadal nie znaleziono, spróbuj strony rządowe
    if not image_url:
        print(f"  Szukam na stronach rządowych...")
        image_url = search_government_sources(code)
    
    # 4. Jeśli nadal nie znaleziono, spróbuj ogólne wyszukiwanie
    if not image_url:
        print(f"  Próbuję ogólne wyszukiwanie...")
        # Można dodać więcej źródeł tutaj
        
    if image_url:
        print(f"  Pobieram obrazek: {image_url}")
        image_data = download_image(image_url)
        if image_data:
            if save_image(image_data, filepath):
                # Zaktualizuj bazę z nowym URL
                return image_url
    
    print(f"  Nie udało się znaleźć obrazka dla {code}")
    return False

def main():
    print("=== Pobieranie świeżych tekstur znaków drogowych ===")
    
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
                time.sleep(1)
    
    # Zapisz zaktualizowaną bazę
    if new_urls > 0:
        save_db(db)
        print(f"\nZaktualizowano {new_urls} URL-i w bazie danych")
    
    print(f"\n=== Zakończono ===")
    print(f"Przetworzono: {updated_count} znaków")
    print(f"Nowe URL-e: {new_urls}")

if __name__ == "__main__":
    main() 