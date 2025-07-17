#!/usr/bin/env python3
"""
Skrypt do aktualizacji bloków zgodnie z nowymi wymiarami tekstur.
"""

import json
import os
from pathlib import Path

# Mapowanie wymiarów na modele i tła
SIZE_TO_MODEL_AND_BACK = {
    "120x120": {
        "model": "geometry.road_sign_square",
        "back": "square_back"
    },
    "120x150": {
        "model": "geometry.road_sign_rectangle_vertical_tall",
        "back": "rectangle_vertical_tall_back"
    },
    "120x60": {
        "model": "geometry.road_sign_rectangle_horizontal_wide",
        "back": "rectangle_horizontal_wide_back"
    },
    "60x30": {
        "model": "geometry.road_sign_rectangle_horizontal_small",
        "back": "rectangle_horizontal_small_back"
    },
    "180x180": {
        "model": "geometry.road_sign_square_large",
        "back": "square_large_back"
    }
}

# Mapowanie znaków na wymiary (z texture-sizes.txt)
SIGN_TO_SIZE = {
    # 120x150
    "b_39": "120x150", "c_17": "120x150",
    "d_7": "120x150", "d_8": "120x150", "d_9": "120x150", "d_10": "120x150",
    "d_11": "120x150", "d_12": "120x150", "d_12a": "120x150", "d_12b": "120x150",
    "d_13": "120x150", "d_13a": "120x150", "d_13b": "120x150", "d_14": "120x150",
    "d_15": "120x150", "d_16": "120x150", "d_17": "120x150", "d_18a": "120x150",
    "d_18b": "120x150", "d_22": "120x150", "d_23a": "120x150", "d_23b": "120x150",
    "d_23c": "120x150", "d_24": "120x150", "d_25": "120x150", "d_26": "120x150",
    "d_26a": "120x150", "d_26b": "120x150", "d_26c": "120x150", "d_26d": "120x150",
    "d_34a": "120x150", "d_44": "120x150", "d_45": "120x150", "d_48": "120x150",
    "d_48a": "120x150", "d_49": "120x150", "d_50": "120x150", "d_51": "120x150",
    "d_51a": "120x150", "d_51b": "120x150",
    
    # 120x60
    "d_34b": "120x60", "d_46": "120x60", "d_47": "120x60", "d_40": "120x60",
    "d_41": "120x60", "d_42": "120x60", "d_43": "120x60", "d_52": "120x60",
    "d_53": "120x60",
    
    # 60x30
    "d_19": "60x30", "d_20": "60x30",
    
    # 180x180
    "d_39": "180x180", "d_39a": "180x180"
}

def update_block_file(block_path, sign_id, size):
    """Aktualizuje plik bloku z nowym modelem i tłem."""
    
    if size not in SIZE_TO_MODEL_AND_BACK:
        print(f"Brak mapowania dla rozmiaru {size}")
        return
    
    model_and_back = SIZE_TO_MODEL_AND_BACK[size]
    
    try:
        with open(block_path, 'r', encoding='utf-8') as f:
            block_data = json.load(f)
        
        # Aktualizuj model
        block_data['minecraft:block']['components']['minecraft:geometry'] = model_and_back['model']
        
        # Aktualizuj tło (north face)
        material_instances = block_data['minecraft:block']['components']['minecraft:material_instances']
        material_instances['north']['texture'] = model_and_back['back']
        
        # Zapisz zaktualizowany plik
        with open(block_path, 'w', encoding='utf-8') as f:
            json.dump(block_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Zaktualizowano {sign_id} -> {size} ({model_and_back['model']}, {model_and_back['back']})")
        
    except Exception as e:
        print(f"✗ Błąd przy aktualizacji {sign_id}: {e}")

def main():
    """Główna funkcja skryptu."""
    
    bp_dir = Path("BP/blocks")
    
    print("Aktualizacja bloków zgodnie z nowymi wymiarami tekstur...")
    print("=" * 60)
    
    updated_count = 0
    
    # Przejdź przez wszystkie kategorie (a, b, c, d)
    for category in ['a', 'b', 'c', 'd']:
        category_dir = bp_dir / category
        
        if not category_dir.exists():
            continue
        
        # Przejdź przez wszystkie pliki bloków w kategorii
        for block_file in category_dir.glob("*.block.json"):
            sign_id = block_file.stem  # Nazwa pliku bez rozszerzenia
            
            # Sprawdź czy znak ma specjalny rozmiar
            if sign_id in SIGN_TO_SIZE:
                size = SIGN_TO_SIZE[sign_id]
                update_block_file(block_file, sign_id, size)
                updated_count += 1
            else:
                # Domyślnie 120x120 (kwadrat)
                update_block_file(block_file, sign_id, "120x120")
                updated_count += 1
    
    print("=" * 60)
    print(f"Zaktualizowano {updated_count} bloków.")
    print("\nPodsumowanie mapowań:")
    for size, config in SIZE_TO_MODEL_AND_BACK.items():
        signs = [sign for sign, s in SIGN_TO_SIZE.items() if s == size]
        print(f"{size}: {config['model']} + {config['back']} ({len(signs)} znaków)")

if __name__ == "__main__":
    main() 