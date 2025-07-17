#!/usr/bin/env python3
import json
import re

TERRAIN_TEXTURE = 'RP/textures/terrain_texture.json'

with open(TERRAIN_TEXTURE, 'r', encoding='utf-8') as f:
    data = json.load(f)

texture_data = data['texture_data']
new_texture_data = {}
renamed = 0
for key, value in texture_data.items():
    # Zamień klucz typu b_b_32a na b_32a
    new_key = re.sub(r'^([a-d])_\1_', r'\1_', key)
    # Popraw ścieżkę do pliku tekstury jeśli trzeba
    if isinstance(value, dict) and 'textures' in value:
        value['textures'] = re.sub(r'/([a-d])_\1_', r'/\1_', value['textures'])
    if new_key != key:
        renamed += 1
    new_texture_data[new_key] = value

# Zapisz poprawiony plik
data['texture_data'] = new_texture_data
with open(TERRAIN_TEXTURE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Poprawiono {renamed} nazw tekstur i ścieżek w terrain_texture.json') 