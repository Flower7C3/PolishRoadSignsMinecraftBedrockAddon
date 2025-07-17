#!/usr/bin/env python3
"""
Naprawa modeli i szarych tyłów dla nietypowych kształtów znaków (trójkąty, koła, ośmiokąty, diamenty, odwrócone trójkąty).
"""
import json
from pathlib import Path

# Mapowanie znaków na (model, tło)
# Uzupełnij tę listę na podstawie dokumentacji lub oryginalnych plików!
SPECIAL_SIGNS = {
    # Trójkąty
    'a_1': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_2': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_3': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_4': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_5': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_6a': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_6b': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_6c': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_6d': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_6e': ('geometry.road_sign_triangle', 'triangle_back'),
    'a_7': ('geometry.road_sign_inverted_triangle', 'inverted_triangle_back'),
    # Koła
    'c_1': ('geometry.road_sign_circle', 'circle_back'),
    'c_2': ('geometry.road_sign_circle', 'circle_back'),
    'c_3': ('geometry.road_sign_circle', 'circle_back'),
    'c_4': ('geometry.road_sign_circle', 'circle_back'),
    'c_5': ('geometry.road_sign_circle', 'circle_back'),
    'c_6': ('geometry.road_sign_circle', 'circle_back'),
    'c_7': ('geometry.road_sign_circle', 'circle_back'),
    'c_8': ('geometry.road_sign_circle', 'circle_back'),
    'c_9': ('geometry.road_sign_circle', 'circle_back'),
    'c_10': ('geometry.road_sign_circle', 'circle_back'),
    'c_11': ('geometry.road_sign_circle', 'circle_back'),
    'c_12': ('geometry.road_sign_circle', 'circle_back'),
    # Ośmiokąty
    'b_20': ('geometry.road_sign_octagon', 'octagon_back'),
    # Diamenty
    'd_2': ('geometry.road_sign_diamond', 'diamond_back'),
}

BP_BLOCKS = Path('BP/blocks')

def fix_block(category, sign_id, model, back):
    block_path = BP_BLOCKS / category / f'{sign_id}.block.json'
    if not block_path.exists():
        print(f'Brak pliku: {block_path}')
        return
    with open(block_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['minecraft:block']['components']['minecraft:geometry'] = model
    data['minecraft:block']['components']['minecraft:material_instances']['north']['texture'] = back
    with open(block_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f'✓ Naprawiono {category}/{sign_id}: {model}, {back}')

def main():
    for sign_id, (model, back) in SPECIAL_SIGNS.items():
        # Kategorie: a, b, c, d
        for category in ['a', 'b', 'c', 'd']:
            block_path = BP_BLOCKS / category / f'{sign_id}.block.json'
            if block_path.exists():
                fix_block(category, sign_id, model, back)
                break

if __name__ == '__main__':
    main() 