#!/usr/bin/env python3
import json
import re

BLOCKS_JSON = 'RP/blocks.json'

with open(BLOCKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Nowy słownik bez prefiksów
fixed_data = {}
for key, value in data.items():
    # Usuń polish_road_sign: z początku klucza
    new_key = re.sub(r'^polish_road_sign:', '', key)
    fixed_data[new_key] = value

with open(BLOCKS_JSON, 'w', encoding='utf-8') as f:
    json.dump(fixed_data, f, indent=2, ensure_ascii=False)

print('Usunięto prefiks polish_road_sign: ze wszystkich kluczy w RP/blocks.json.') 