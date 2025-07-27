# Polish Road Signs - Dokumentacja techniczna

## 📚 Przegląd techniczny

### Architektura addona

Addon składa się z dwóch głównych komponentów:

1. **Behavior Pack (BP)** - definiuje logikę bloków
2. **Resource Pack (RP)** - zawiera tekstury i tłumaczenia

### Struktura plików

```text
BP/
├── manifest.json              # Konfiguracja BP
├── blocks/                    # Definicje bloków
│   └── [kategorie]/          # Definicje bloków według kategorii
└── item_catalog/             # Katalog przedmiotów
    └── crafting_item_catalog.json

RP/
├── manifest.json              # Konfiguracja RP
├── textures/                  # Tekstury
│   ├── terrain_texture.json   # Mapowanie tekstur
│   └── blocks/               # Tekstury bloków
│       ├── averse/           # Tekstury przodu znaków
│       │   └── [kategorie]/  # Podkatalogi kategorii znaków
│       └── reverse/          # Tekstury tyłu znaków
├── texts/                     # Tłumaczenia
│   ├── pl_PL.lang           # Polski
│   └── en_US.lang           # Angielski
├── models/                    # Modele 3D
│   └── blocks/               # Modele geometryczne
└── blocks.json               # Konfiguracja bloków
```

## 🔧 Konfiguracja manifestów



## 📦 Definicje bloków

### Format pliku bloku

```json
{
  "format_version": "1.20.60",
  "minecraft:block": {
    "description": {
      "identifier": "polish_road_sign:a_1",
      "menu_category": {
        "category": "construction"
      },
      "traits": {
        "minecraft:placement_direction": {
          "enabled_states": [
            "minecraft:cardinal_direction"
          ]
        }
      }
    },
    "components": {
      "minecraft:collision_box": {
        "origin": [-8, 0, -8],
        "size": [16, 16, 2]
      },
      "minecraft:selection_box": {
        "origin": [-8, 0, -8],
        "size": [16, 16, 2]
      },
      "minecraft:destructible_by_mining": {
        "seconds_to_destroy": 1
      },
      "minecraft:destructible_by_explosion": {
        "explosion_resistance": 30
      },
      "minecraft:geometry": "geometry.road_sign_triangle",
      "minecraft:material_instances": {
        "north": {
          "texture": "polish_road_sign:a_1",
          "render_method": "alpha_test_single_sided"
        },
        "south": {
          "texture": "polish_road_sign_back:triangle_128x113",
          "render_method": "alpha_test_single_sided"
        }
      }
    }
  }
}
```

### Właściwości bloków

- **Identifier**: `polish_road_sign:sign_code`
- **Geometry**: Różne modele w zależności od kształtu znaku
- **Textures**:
  - `*` - szary beton (ramka)
  - `south` - tekstura znaku (przezroczysta)
- **Collision**: 16x16x2 piksele
- **Placement**: 4 kierunki (N, S, E, W)

## 🎨 System tekstur

### terrain_texture.json

```json
{
  "resource_pack_name": "polish_road_sign",
  "texture_name": "atlas.terrain",
  "padding": 8,
  "num_mip_levels": 4,
  "texture_data": {
    "a_1": {
      "textures": "textures/blocks/a/a_1.png"
    }
  }
}
```

### Konwencje nazewnictwa

- **Tekstury**: `textures/blocks/category/sign_code.png`
- **Klucze**: `sign_code` (np. `a_1`, `b_20`)
- **Format**: PNG z przezroczystością
- **Rozmiar**: 128x128 pikseli (skalowane z zachowaniem proporcji)
- **Tła**: Neutralne białe tło dla wszystkich znaków (automatycznie generowane)

### Tekstury tła

Tekstury tła są automatycznie generowane dla każdego kształtu znaku:
- **Trójkąt**: Biały trójkąt na przezroczystym tle
- **Odwrócony trójkąt**: Biały odwrócony trójkąt
- **Koło**: Białe koło
- **Kwadrat**: Biały kwadrat
- **Prostokąt**: Biały prostokąt
- **Ośmiokąt**: Biały ośmiokąt
- **Diament**: Biały diament

**Lokalizacja**: `RP/textures/blocks/sign_backs/`
**Format**: PNG z kanałem alpha
**Kolor**: Neutralny biały (#FFFFFF)

## 🌐 System tłumaczeń

### Format pliku .lang

```
tile.polish_road_sign:a_1.name=A-1: niebezpieczny zakręt w prawo
tile.polish_road_sign:b_20.name=B-20: stop
tile.polish_road_sign:c_1.name=C-1: nakaz jazdy w prawo przed znakiem
tile.polish_road_sign:d_1.name=D-1: droga z pierwszeństwem
```

### Konwencje tłumaczeń

- **Polski**: Oficjalne nazwy zgodne z przepisami
- **Angielski**: Precyzyjne tłumaczenia nazw
- **Format**: `tile.polish_road_sign:sign_code.name`
- **Struktura**: `KOD: nazwa znaku`

## 🔄 Automatyzacja

### Przetwarzanie kategorii

Skrypt obsługuje przetwarzanie całych kategorii z automatycznym czyszczeniem:

```bash
# Przetwórz przykładową kategorię
python3 road_sign_processor.py category:A

# Przetwórz kategorię w trybie offline
python3 road_sign_processor.py category:B --skip-download

# Przetwórz inną kategorię
python3 road_sign_processor.py category:C

# Przetwórz kategorię informacyjną
python3 road_sign_processor.py category:D
```

**Funkcje czyszczenia kategorii:**
- Usuwa wszystkie bloki z danej kategorii
- Usuwa wszystkie tekstury PNG z kategorii
- Usuwa wpisy z terrain_texture.json dla znaków z kategorii
- Zachowuje pliki SVG i inne kategorie
- Automatycznie wywoływane przed przetwarzaniem

### Dynamiczne kategorie

Skrypt pobiera kategorie dynamicznie z bazy danych:
- Nie używa statycznych list kategorii
- Działa z dowolną liczbą kategorii
- Automatycznie wykrywa nowe kategorie
- Waliduje istnienie kategorii przed przetwarzaniem

### Skrypt road_sign_processor.py

Skrypt automatycznie pobiera i przetwarza obrazki znaków:

```python
# Funkcje:
# - Pobiera SVG z Wikipedii przez .fullImageLink
# - Skaluje z zachowaniem proporcji do 128px szerokości
# - Konwertuje SVG→PNG używając Inkscape
# - Tworzy neutralne białe tekstury tła automatycznie
# - Aktualizuje collision_box i selection_box
# - Aktualizuje bazę danych z wymiarami obrazków
# - Podsumowuje błędy na końcu
# - Tryb offline z flagą --skip-download
# - Przetwarzanie kategorii z automatycznym czyszczeniem
# - Dynamiczne pobieranie kategorii z bazy danych
# - Automatyczne czyszczenie plików dla usuniętych znaków

# Użycie:
python3 road_sign_processor.py a_1    # Pojedynczy znak
python3 road_sign_processor.py all    # Wszystkie znaki
python3 road_sign_processor.py category:A    # Przetwórz kategorię A
python3 road_sign_processor.py category:B --skip-download    # Kategoria B offline
python3 road_sign_processor.py category:B -s    # Kategoria B offline (skrót)
python3 road_sign_processor.py a_1 --skip-download    # Tryb offline
python3 road_sign_processor.py a_1 -s    # Tryb offline (skrót)
python3 road_sign_processor.py all --skip-download    # Wszystkie w trybie offline
python3 road_sign_processor.py all -s    # Wszystkie w trybie offline (skrót)
python3 road_sign_processor.py a_1 --force-rebuild    # Wymuś przebudowanie
python3 road_sign_processor.py a_1 -f    # Wymuś przebudowanie (skrót)
python3 road_sign_processor.py a_1 --quiet    # Tryb cichy
python3 road_sign_processor.py a_1 -q    # Tryb cichy (skrót)
```

### Baza danych road_signs_full_database.json

```json
{
  "road_signs": {
    "A": {
      "signs": {
        "a_1": {
          "code": "A-1",
          "translation_pl": "Niebezpieczny zakręt w prawo (A-1)",
          "translation_en": "Dangerous curve to the right (A-1)",
          "wikipedia_url": "https://pl.wikipedia.org/wiki/Znaki_ostrzegawcze_w_Polsce",
          "wikipedia_file_page": "https://pl.wikipedia.org/wiki/Plik:Znak_A-1.svg",
          "image_width": "128",
          "image_height": "128"
        }
      }
    }
  }
}
```

## 🛠️ Skrypty narzędziowe

### verify_all.py
Sprawdza integralność całego projektu:
- Weryfikuje tekstury i modele 3D
- Sprawdza definicje bloków
- Waliduje bazę danych i tłumaczenia
- Wykrywa nadmiarowe/brakujące pliki

### build.py
Buduje pakiety Minecraft (.mcaddon i/lub .mcpack):
- **--mcaddon** / **-m** - Buduje tylko pakiet .mcaddon
- **--mcpack** / **-p** - Buduje tylko pakiety .mcpack (BP i RP)
- **--all** / **-a** - Buduje wszystkie formaty
- **--no-bump** / **-n** - Nie zwiększa wersji (używa obecnej)
- **--test-on-local** / **-t** - Automatycznie zainstaluj i przetestuj lokalnie
- **--no-clean** / **-c** - Nie usuwaj starych pakietów przed instalacją
- Automatycznie zwiększa wersję (chyba że użyto --no-bump)
- Tworzy strukturę BP i RP
- Pakuje do odpowiednich formatów

### generate_examples.py
Generuje przykładowe komendy testowe i deweloperskie:
- **--test** / **-t** - Generuje komendy testowe dla różnych kombinacji kształtów/wymiarów
- **--dev** / **-d** - Generuje komendy deweloperskie (weryfikacja, budowanie, testowanie)
- Automatycznie wykrywa kombinacje kształtów i wymiarów z bazy danych
- Generuje komendy z `--test-on-local` dla automatycznego testowania

### road_sign_processor.py
Przetwarza znaki drogowe:
- **--skip-download** / **-s** - Tryb offline (użyj lokalnych plików SVG)
- **--force-rebuild** / **-f** - Wymuś przebudowanie tekstur
- **--quiet** / **-q** - Tryb cichy (tylko błędy)
- Pobiera SVG z Wikipedii przez .fullImageLink
- Skaluje z zachowaniem proporcji
- Konwertuje SVG→PNG używając Inkscape
- Tworzy neutralne białe tekstury tła automatycznie
- Aktualizuje collision_box i selection_box
- Aktualizuje bazę danych z wymiarami obrazków
- Dynamiczne pobieranie kategorii z bazy danych
- Automatyczne czyszczenie plików dla usuniętych znaków

### Aktualizacja katalogu crafting
Funkcjonalność wbudowana w `road_sign_processor.py`:
- Dynamiczne tworzenie grup na podstawie bazy danych
- Konfigurowalne ikony kategorii przez `icon` w bazie danych
- Naturalne sortowanie elementów (`natsorted`)
- Automatyczne wywołanie po przetworzeniu znaków



## 🔍 Weryfikacja jakości



## 🚀 Deployment

### GitHub Actions
Automatyczne budowanie i release:
- Weryfikacja projektu
- Budowanie paczek
- Testowanie struktury
- Automatyczne releases
- Version bump

### Wymagania systemowe
- Python 3.7+
- Inkscape (konwersja SVG→PNG)
- curl (pobieranie obrazków)
- Minecraft Bedrock Edition 1.16.0+

## 📝 Licencja

MIT License - zobacz plik [LICENSE](LICENSE) dla szczegółów.

---

**Uwaga**: Ta dokumentacja jest aktualizowana automatycznie przy każdej zmianie w projekcie.