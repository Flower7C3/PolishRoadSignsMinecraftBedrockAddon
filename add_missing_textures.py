import json

# Lista brakujących tekstur
missing_textures = [
    "b/b_32a", "b/b_32b", "b/b_32c", "b/b_32d", "b/b_32e", "b/b_32f",
    "b/b_35a", "b/b_35b", "b/b_35c", "b/b_44",
    "d/d_12", "d/d_12a", "d/d_12b", "d/d_13a", "d/d_13b",
    "d/d_18a", "d/d_18b", "d/d_21a", "d/d_23a", "d/d_23b", "d/d_23c",
    "d/d_26a", "d/d_26b", "d/d_26c", "d/d_26d", "d/d_34a", "d/d_34b",
    "d/d_35a", "d/d_36a", "d/d_39a", "d/d_48", "d/d_48a", "d/d_49",
    "d/d_4c", "d/d_50", "d/d_51", "d/d_51a", "d/d_51b", "d/d_52",
    "d/d_53", "d/d_54", "d/d_55", "d/d_6a", "d/d_6b"
]

def add_missing_textures():
    """Dodaj brakujące tekstury do terrain_texture.json"""
    
    # Wczytaj obecny plik
    with open('RP/textures/terrain_texture.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Dodaj brakujące tekstury
    for texture in missing_textures:
        texture_id = texture.replace('/', '_')
        data['texture_data'][texture_id] = {
            "textures": f"textures/blocks/{texture}.png"
        }
        print(f"Dodano: {texture_id}")
    
    # Zapisz zaktualizowany plik
    with open('RP/textures/terrain_texture.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nDodano {len(missing_textures)} brakujących tekstur")

if __name__ == "__main__":
    add_missing_textures() 