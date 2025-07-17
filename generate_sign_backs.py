import os
from PIL import Image, ImageDraw

SIGN_BACKS_PATH = 'RP/textures/blocks/sign_backs'

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def create_gray_sign_back(width, height, filename):
    """Stwórz szary tył znaku o podanych wymiarach"""
    # Utwórz obrazek z przezroczystym tłem
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Szary kolor dla tyłu znaku (RGB: 128, 128, 128)
    gray_color = (128, 128, 128, 255)
    
    # Narysuj szary prostokąt z małym marginesem
    margin = 2
    draw.rectangle([margin, margin, width - margin, height - margin], 
                  fill=gray_color)
    
    # Zapisz plik
    filepath = os.path.join(SIGN_BACKS_PATH, filename)
    img.save(filepath, 'PNG')
    print(f"Utworzono: {filename} ({width}x{height})")

def main():
    print("=== Generowanie szarych tyłów znaków ===")
    
    ensure_dir(SIGN_BACKS_PATH)
    
    # Standardowe rozmiary (już istnieją)
    print("Standardowe rozmiary (120x120) - już istnieją")
    
    # Nietypowe rozmiary do stworzenia
    sign_backs = [
        # 120x150 - wyższe prostokąty
        (120, 150, "rectangle_vertical_back.png"),
        (120, 150, "rectangle_vertical_tall_back.png"),
        
        # 120x60 - szersze prostokąty
        (120, 60, "rectangle_horizontal_wide_back.png"),
        
        # 60x30 - bardzo szerokie prostokąty
        (60, 30, "rectangle_horizontal_extra_wide_back.png"),
        
        # 180x180 - duże kwadraty
        (180, 180, "square_large_back.png"),
    ]
    
    for width, height, filename in sign_backs:
        create_gray_sign_back(width, height, filename)
    
    print(f"\n=== Zakończono ===")
    print(f"Utworzono {len(sign_backs)} nowych tyłów znaków")

if __name__ == "__main__":
    main() 