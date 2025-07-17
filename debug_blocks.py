#!/usr/bin/env python3
"""
Skrypt debug do sprawdzenia dlaczego znaki nie są znajdowane.
"""

from pathlib import Path

# Mapowanie znaków na wymiary (tylko znaki, które rzeczywiście istnieją)
SIGN_TO_SIZE = {
    # 120x150 - znaki, które rzeczywiście istnieją
    "b_39": "120x150", "c_17": "120x150",
    "d_7": "120x150", "d_8": "120x150", "d_9": "120x150", "d_10": "120x150",
    "d_11": "120x150", "d_13": "120x150", "d_14": "120x150", "d_15": "120x150",
    "d_16": "120x150", "d_17": "120x150", "d_22": "120x150", "d_24": "120x150",
    "d_25": "120x150", "d_26": "120x150", "d_44": "120x150", "d_45": "120x150",
    
    # 120x60 - znaki, które rzeczywiście istnieją
    "d_40": "120x60", "d_41": "120x60", "d_42": "120x60", "d_43": "120x60",
    "d_46": "120x60", "d_47": "120x60",
    
    # 60x30 - znaki, które rzeczywiście istnieją
    "d_19": "60x30", "d_20": "60x30",
    
    # 180x180 - znaki, które rzeczywiście istnieją
    "d_39": "180x180"
}

def main():
    """Główna funkcja skryptu."""
    
    bp_dir = Path("BP/blocks")
    
    print("Debug - sprawdzanie znaków...")
    print("=" * 60)
    
    found_special = []
    found_normal = []
    
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
                found_special.append((sign_id, size))
                print(f"✓ Znaleziono specjalny: {sign_id} -> {size}")
            else:
                found_normal.append(sign_id)
    
    print("=" * 60)
    print(f"Znaki ze specjalnymi wymiarami: {len(found_special)}")
    print(f"Znaki normalne: {len(found_normal)}")
    
    print("\nZnaki ze specjalnymi wymiarami:")
    for sign_id, size in found_special:
        print(f"  {sign_id} -> {size}")
    
    print(f"\nPierwsze 10 znaków normalnych:")
    for sign_id in found_normal[:10]:
        print(f"  {sign_id}")

if __name__ == "__main__":
    main() 