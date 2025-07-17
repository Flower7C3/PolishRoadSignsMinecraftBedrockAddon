import os
from PIL import Image
import glob

BASE_TEXTURE_PATH = 'RP/textures/blocks'

def resize_image_to_min_128(filepath):
    """Przeskaluj obrazek do minimum 128x128 px z zachowaniem proporcji"""
    try:
        img = Image.open(filepath)
        
        # Konwertuj na RGBA jeśli to PNG
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Sprawdź czy już ma odpowiedni rozmiar
        w, h = img.size
        if w >= 128 and h >= 128:
            print(f"  {filepath}: już ma odpowiedni rozmiar ({w}x{h})")
            return True
        
        print(f"  {filepath}: przeskaluj z {w}x{h} do min. 128x128")
        
        # Oblicz nowe wymiary zachowując proporcje
        if w > h:
            new_w = max(128, w)
            new_h = int((h * new_w) / w)
        else:
            new_h = max(128, h)
            new_w = int((w * new_h) / h)
        
        # Przeskaluj
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Utwórz nowy obrazek 128x128 z przezroczystym tłem
        new_img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        
        # Wycentruj oryginalny obrazek
        x = (128 - new_w) // 2
        y = (128 - new_h) // 2
        new_img.paste(img, (x, y), img)
        
        # Zapisz
        new_img.save(filepath, 'PNG')
        print(f"    Zapisano: {filepath} (128x128)")
        return True
        
    except Exception as e:
        print(f"    Błąd przetwarzania {filepath}: {e}")
        return False

def main():
    print("=== Przeskalowanie wszystkich tekstur do minimum 128x128 px ===")
    
    # Znajdź wszystkie pliki PNG
    png_files = []
    for pattern in ['*.png', '*/*.png', '*/*/*.png']:
        png_files.extend(glob.glob(os.path.join(BASE_TEXTURE_PATH, pattern)))
    
    print(f"Znaleziono {len(png_files)} plików PNG")
    
    success_count = 0
    error_count = 0
    
    for filepath in sorted(png_files):
        if resize_image_to_min_128(filepath):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n=== Zakończono ===")
    print(f"Pomyślnie przetworzono: {success_count}")
    print(f"Błędy: {error_count}")

if __name__ == "__main__":
    main() 