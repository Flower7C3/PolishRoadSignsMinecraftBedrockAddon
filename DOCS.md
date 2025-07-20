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
│   ├── a/                    # Znaki ostrzegawcze (34)
│   ├── b/                    # Znaki zakazu (44)
│   ├── c/                    # Znaki nakazu (19)
│   └── d/                    # Znaki informacyjne (55)
└── item_catalog/             # Katalog przedmiotów
    └── crafting_item_catalog.json

RP/
├── manifest.json              # Konfiguracja RP
├── textures/                  # Tekstury
│   ├── terrain_texture.json   # Mapowanie tekstur
│   └── blocks/               # Tekstury bloków
│       ├── a/               # Tekstury znaków A
│       ├── b/               # Tekstury znaków B
│       ├── c/               # Tekstury znaków C
│       ├── d/               # Tekstury znaków D
│       └── sign_backs/      # Tła znaków
├── texts/                     # Tłumaczenia
│   ├── pl_PL.lang           # Polski
│   └── en_US.lang           # Angielski
├── models/                    # Modele 3D
│   └── blocks/
│       ├── road_sign_triangle.geo.json
│       ├── road_sign_circle.geo.json
│       ├── road_sign_square.geo.json
│       ├── road_sign_diamond.geo.json
│       ├── road_sign_octagon.geo.json
│       ├── road_sign_rectangle_128x160.geo.json
│       ├── road_sign_rectangle_160x128.geo.json
│       ├── road_sign_rectangle_128x128.geo.json
│       ├── road_sign_rectangle_160x160.geo.json
│       ├── road_sign_rectangle_192x128.geo.json
│       ├── road_sign_rectangle_128x192.geo.json
│       └── road_sign_inverted_triangle.geo.json
└── blocks.json               # Konfiguracja bloków
```

## 🔧 Konfiguracja manifestów

### BP/manifest.json

```json
{
  "format_version": 2,
  "header": {
    "name": "Polish Road Signs BP",
    "description": "Behavior Pack for Polish Road Signs addon",
    "uuid": "b8c7d9e0-f1a2-3456-7890-abcdef123456",
    "version": [1, 0, 46],
    "min_engine_version": [1, 16, 0]
  },
  "modules": [
    {
      "description": "Behavior",
      "type": "data",
      "version": [1, 0, 46],
      "uuid": "c9d8e7f6-2345-6789-0123-456789abcdef"
    }
  ],
  "dependencies": [
    {
      "uuid": "d0e9f8a7-3456-7890-1234-567890bcdef1",
      "version": [1, 0, 46]
    }
  ]
}
```

### RP/manifest.json

```json
{
  "format_version": 2,
  "header": {
    "name": "Polish Road Signs RP",
    "description": "Resource Pack for Polish Road Signs addon",
    "uuid": "d0e9f8a7-3456-7890-1234-567890bcdef1",
    "version": [1, 0, 46],
    "min_engine_version": [1, 16, 0]
  },
  "modules": [
    {
      "type": "resources",
      "version": [1, 0, 46],
      "uuid": "e1f0a9b8-4567-8901-2345-678901cdef12"
    }
  ]
}
```

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
# Przetwórz kategorię A (ostrzegawcze)
python3 road_sign_processor.py category:A

# Przetwórz kategorię B (zakazu) w trybie offline
python3 road_sign_processor.py category:B --skip-download

# Przetwórz kategorię C (nakazu)
python3 road_sign_processor.py category:C

# Przetwórz kategorię D (informacyjne)
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

# Użycie:
python3 road_sign_processor.py a_1    # Pojedynczy znak
python3 road_sign_processor.py all    # Wszystkie znaki
python3 road_sign_processor.py category:A    # Przetwórz kategorię A
python3 road_sign_processor.py category:B --skip-download    # Kategoria B offline
python3 road_sign_processor.py a_1 --skip-download    # Tryb offline
python3 road_sign_processor.py all --skip-download    # Wszystkie w trybie offline
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

### build_mcaddon.py
Buduje paczkę .mcaddon:
- Automatycznie zwiększa wersję
- Tworzy strukturę BP i RP
- Pakuje do pliku .mcaddon

### build_mcpack.py
Buduje paczki .mcpack dla serwerów:
- Tworzy osobne pliki BP i RP
- Optymalizuje dla serwerów

### unpack_and_install_mcaddon.py
Instaluje paczkę lokalnie:
- Automatycznie usuwa stare wersje
- Instaluje w katalogu Minecraft
- Obsługuje flagę --no-clean

### update_crafting_catalog.py
Aktualizuje katalog craftingowy:
- Synchronizuje z definicjami bloków
- Dodaje nowe znaki automatycznie

## 📊 Statystyki projektu

### Liczba znaków
- **A (Ostrzegawcze)**: 34 znaki
- **B (Zakazu)**: 44 znaki  
- **C (Nakazu)**: 19 znaków
- **D (Informacyjne)**: 55 znaków
- **Łącznie**: 152 znaki

### Modele 3D
- **Trójkąt**: Znaki ostrzegawcze (A)
- **Koło**: Znaki zakazu (B)
- **Kwadrat**: Znaki nakazu (C)
- **Prostokąt**: Znaki informacyjne (D)
- **Ośmiokąt**: Stop (B-20)
- **Odwrócony trójkąt**: Ustąp pierwszeństwa (A-7)

### Tekstury
- **Rozmiar**: 128x128 pikseli
- **Format**: PNG z przezroczystością
- **Tło**: Neutralne białe dla wszystkich znaków
- **Źródło**: Wikipedia (automatyczne pobieranie)

## 🔍 Weryfikacja jakości

### verify_all.py - Raport

```
📊 VERIFICATION SUMMARY
==================================================
✅ Block definitions: 206 found
✅ Terrain textures: 212 found
✅ Block textures: 225 total (14 missing in terrain)
✅ 3D models: 6 used
✅ Texture-model matches: 8 mismatches
✅ Missing models: 28 (some replaced by similar existing models)
✅ Translations: 100% complete
✅ Missing blocks: 0
✅ Missing PNGs: 0
```

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