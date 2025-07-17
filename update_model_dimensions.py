import os
import json
import glob

MODELS_PATH = 'RP/models/blocks'

def update_model_dimensions(filepath):
    """Zaktualizuj wymiary tekstur w modelu 3D z 16x16 na 128x128"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        
        # Aktualizuj wszystkie geometrie w pliku
        for geometry in data['minecraft:geometry']:
            # Aktualizuj wymiary tekstur
            if 'description' in geometry:
                desc = geometry['description']
                if 'texture_width' in desc and desc['texture_width'] == 16:
                    desc['texture_width'] = 128
                    updated = True
                if 'texture_height' in desc and desc['texture_height'] == 16:
                    desc['texture_height'] = 128
                    updated = True
            
            # Aktualizuj UV mapping dla wszystkich kostek
            if 'bones' in geometry:
                for bone in geometry['bones']:
                    if 'cubes' in bone:
                        for cube in bone['cubes']:
                            if 'uv' in cube:
                                uv = cube['uv']
                                # Aktualizuj wszystkie strony kostki
                                for side in ['north', 'east', 'south', 'west', 'up', 'down']:
                                    if side in uv:
                                        side_uv = uv[side]
                                        if 'uv_size' in side_uv:
                                            # Skaluj UV size z 16 na 128 (8x większy)
                                            if side_uv['uv_size'][0] == 16:
                                                side_uv['uv_size'][0] = 128
                                                updated = True
                                            if side_uv['uv_size'][1] == 16:
                                                side_uv['uv_size'][1] = 128
                                                updated = True
                                            if side_uv['uv_size'][0] == -16:
                                                side_uv['uv_size'][0] = -128
                                                updated = True
                                            if side_uv['uv_size'][1] == -16:
                                                side_uv['uv_size'][1] = -128
                                                updated = True
        
        if updated:
            # Zapisz zaktualizowany plik
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  Zaktualizowano: {filepath}")
            return True
        else:
            print(f"  Brak zmian: {filepath}")
            return False
            
    except Exception as e:
        print(f"  Błąd przetwarzania {filepath}: {e}")
        return False

def main():
    print("=== Aktualizacja wymiarów tekstur w modelach 3D ===")
    print("Zmiana z 16x16 na 128x128 pikseli")
    
    # Znajdź wszystkie pliki modeli
    model_files = glob.glob(os.path.join(MODELS_PATH, "*.geo.json"))
    
    print(f"Znaleziono {len(model_files)} plików modeli")
    
    success_count = 0
    error_count = 0
    
    for filepath in sorted(model_files):
        if update_model_dimensions(filepath):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n=== Zakończono ===")
    print(f"Pomyślnie zaktualizowano: {success_count}")
    print(f"Błędy: {error_count}")

if __name__ == "__main__":
    main() 