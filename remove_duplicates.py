#!/usr/bin/env python3

# Ścieżka do pliku językowego
LANG_FILE = 'RP/texts/pl_PL.lang'

# Wczytaj obecny plik językowy
with open(LANG_FILE, 'r', encoding='utf-8') as f:
    lang_lines = f.read().splitlines()

# Usuń duplikaty, zostawiając tylko wpisy z pełnymi nazwami
seen_keys = set()
unique_lines = []

for line in lang_lines:
    if '=' in line:
        key, value = line.split('=', 1)
        key = key.strip()
        
        # Jeśli to klucz tile.polish_road_sign
        if key.startswith('tile.polish_road_sign:'):
            # Sprawdź czy to już widzieliśmy
            if key in seen_keys:
                continue  # Pomiń duplikat
            seen_keys.add(key)
            
            # Sprawdź czy wartość zawiera pełną nazwę (nie tylko kod)
            if '(' in value and ')' in value:
                # To jest pełna nazwa, zostaw ją
                unique_lines.append(line)
            else:
                # To jest tylko kod, pomiń (zostanie zastąpiony pełną nazwą)
                continue
        else:
            # To nie jest klucz tile, zostaw bez zmian
            unique_lines.append(line)

# Zapisz plik bez duplikatów
with open(LANG_FILE, 'w', encoding='utf-8') as f:
    for line in unique_lines:
        f.write(line + '\n')

print(f'Usunięto duplikaty z pliku {LANG_FILE}') 