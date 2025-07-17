import json

# Nowe tyły znaków do dodania
new_sign_backs = [
    "rectangle_vertical_back",
    "rectangle_vertical_tall_back", 
    "rectangle_horizontal_wide_back",
    "rectangle_horizontal_extra_wide_back",
    "square_large_back"
]

def add_new_sign_backs():
    """Dodaj nowe tyły znaków do terrain_texture.json"""
    
    # Wczytaj obecny plik
    with open('RP/textures/terrain_texture.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Dodaj nowe tyły znaków
    for sign_back in new_sign_backs:
        data['texture_data'][sign_back] = {
            "textures": f"textures/blocks/sign_backs/{sign_back}.png"
        }
        print(f"Dodano: {sign_back}")
    
    # Zapisz zaktualizowany plik
    with open('RP/textures/terrain_texture.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nDodano {len(new_sign_backs)} nowych tyłów znaków")

if __name__ == "__main__":
    add_new_sign_backs() 