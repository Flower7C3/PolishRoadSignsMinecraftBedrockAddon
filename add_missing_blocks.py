import json
import os
import glob

def add_missing_blocks():
    """Dodaj brakujące bloki do blocks.json"""
    
    # Wczytaj obecny plik blocks.json
    with open('RP/blocks.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Znajdź wszystkie pliki bloków w BP
    bp_blocks = []
    for block_file in glob.glob('BP/blocks/**/*.block.json', recursive=True):
        block_id = block_file.replace('BP/blocks/', '').replace('.block.json', '')
        bp_blocks.append(block_id)
    
    # Sprawdź, które bloki już są zarejestrowane
    registered_blocks = set()
    for key in data.keys():
        if key.startswith('polish_road_sign:'):
            registered_blocks.add(key.replace('polish_road_sign:', ''))
    
    # Dodaj brakujące bloki
    added_count = 0
    for block_id in bp_blocks:
        if block_id not in registered_blocks:
            data[f'polish_road_sign:{block_id}'] = {
                "sound": "stone"
            }
            print(f"Dodano: {block_id}")
            added_count += 1
    
    # Zapisz zaktualizowany plik
    with open('RP/blocks.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nDodano {added_count} brakujących bloków")

if __name__ == "__main__":
    add_missing_blocks() 