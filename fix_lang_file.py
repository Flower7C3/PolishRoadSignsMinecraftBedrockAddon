#!/usr/bin/env python3
import json
import os

# Wczytaj bazę danych znaków
with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
    database = json.load(f)

# Ścieżka do pliku językowego
LANG_FILE = 'RP/texts/pl_PL.lang'

# Funkcja do pobierania nazwy znaku z bazy danych
def get_sign_name(sign_id):
    """Pobiera oficjalną nazwę znaku z bazy danych lub zwraca kod znaku."""
    category = sign_id[0].upper()  # A, B, C, D
    if category in database['road_signs']:
        signs = database['road_signs'][category]['signs']
        if sign_id in signs:
            name = signs[sign_id]['name']
            code = signs[sign_id]['code']
            # Jeśli nazwa jest zbyt długa, użyj tylko kodu
            if len(name) > 50:
                return code
            return f"{name} ({code})"
    # Jeśli nie ma w bazie, zwróć kod znaku
    return sign_id.upper().replace("_", "-")

# Zbierz wszystkie identyfikatory bloków
block_files = []
for cat in ['a', 'b', 'c', 'd']:
    folder = f'BP/blocks/{cat}'
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            if f.endswith('.block.json'):
                sign_id = f.replace('.block.json', '')
                block_files.append(sign_id)

# Utwórz nowy plik językowy
lang_entries = []

# Dodaj wpisy dla wszystkich znaków
for sign_id in sorted(block_files):
    sign_name = get_sign_name(sign_id)
    lang_key = f'tile.polish_road_sign:{sign_id}.name'
    lang_entries.append(f'{lang_key}={sign_name}')

# Dodaj kategorie
lang_entries.append('polish_road_sign:information_signs=Znaki informacyjne')
lang_entries.append('polish_road_sign:mandatory_signs=Znaki nakazu')
lang_entries.append('polish_road_sign:prohibition_signs=Znaki zakazu')
lang_entries.append('polish_road_sign:warning_signs=Znaki ostrzegawcze')

# Zapisz plik językowy
with open(LANG_FILE, 'w', encoding='utf-8') as f:
    for entry in lang_entries:
        f.write(entry + '\n')

print(f'Utworzono nowy plik językowy z {len(block_files)} znakami bez duplikatów.') 