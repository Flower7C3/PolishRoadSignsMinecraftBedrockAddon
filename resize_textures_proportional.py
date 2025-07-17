import os
from PIL import Image
import glob

BASE_TEXTURE_PATH = 'RP/textures/blocks'

def resize_image_proportional(filepath):
    """Przeskaluj obrazek tak, że dłuższy bok będzie miał 128 pikseli"""
    try:
        img = Image.open(filepath)
        
        # Konwertuj na RGBA jeśli to PNG
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Sprawdź obecne wymiary
        w, h = img.size
        
        # Jeśli już ma odpowiedni rozmiar (dłuższy bok 128px)
        if w == 128 or h == 128:
            print(f"  {filepath}: już ma odpowiedni rozmiar ({w}x{h})")
            return True
        
        print(f"  {filepath}: przeskaluj z {w}x{h}")
        
        # Oblicz nowe wymiary - dłuższy bok będzie miał 128px
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
        img.save(filepath, 'PNG')
        print(f"    -> przeskalowano do {new_w}x{new_h}")
        return True
        
    except Exception as e:
        print(f"  Błąd przetwarzania {filepath}: {e}")
        return False

def main():
    print("=== Przeskalowanie tekstur - dłuższy bok 128px ===")
    
    # Znajdź wszystkie pliki PNG
    png_files = glob.glob(os.path.join(BASE_TEXTURE_PATH, "**/*.png"), recursive=True)
    
    print(f"Znaleziono {len(png_files)} plików PNG")
    
    success_count = 0
    error_count = 0
    
    for filepath in sorted(png_files):
        if resize_image_proportional(filepath):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n=== Zakończono ===")
    print(f"Pomyślnie przeskalowano: {success_count}")
    print(f"Błędy: {error_count}")

if __name__ == "__main__":
    main() 