# Polish Road Signs - Dokumentacja techniczna

## 📚 Przegląd techniczny

### Architektura addona

Addon składa się z dwóch głównych komponentów:

1. **Behavior Pack (BP)** - definiuje logikę bloków
2. **Resource Pack (RP)** - zawiera tekstury i tłumaczenia

### Struktura plików

```
BP/
├── manifest.json              # Konfiguracja BP
├── blocks/                    # Definicje bloków
│   ├── a/                    # Znaki ostrzegawcze
│   ├── b/                    # Znaki zakazu  
│   ├── c/                    # Znaki nakazu
│   └── d/                    # Znaki informacyjne
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
│       └── d/               # Tekstury znaków D
├── texts/                     # Tłumaczenia
│   ├── pl_PL.lang           # Polski
│   └── en_US.lang           # Angielski
├── models/                    # Modele 3D
│   └── blocks/
│       └── road_sign.geo.json
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
    "version": [1, 0, 31],
    "min_engine_version": [1, 16, 0]
  },
  "modules": [
    {
      "description": "Behavior",
      "type": "data",
      "version": [1, 0, 31],
      "uuid": "c9d8e7f6-2345-6789-0123-456789abcdef"
    }
  ],
  "dependencies": [
    {
      "uuid": "d0e9f8a7-3456-7890-1234-567890bcdef1",
      "version": [1, 0, 31]
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
    "version": [1, 0, 31],
    "min_engine_version": [1, 16, 0]
  },
  "modules": [
    {
      "type": "resources",
      "version": [1, 0, 31],
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
      "minecraft:geometry": "geometry.polish_road_sign",
      "minecraft:material_instances": {
        "*": {
          "texture": "gray_concrete",
          "render_method": "opaque"
        },
        "south": {
          "texture": "a_1",
          "render_method": "alpha_test"
        }
      }
    }
  }
}
```

### Właściwości bloków

- **Identifier**: `polish_road_sign:sign_code`
- **Geometry**: Wspólny model `road_sign.geo.json`
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
- **Rozmiar**: 16x16 pikseli

## 🌐 System tłumaczeń

### Format pliku .lang

```
tile.polish_road_sign:a_1.name=Znak ostrzegawczy A-1
tile.polish_road_sign:a_1.desc=Niebezpieczny zakręt w prawo
```

### Struktura tłumaczeń

- **Klucz**: `tile.polish_road_sign:sign_code.name`
- **Opis**: `tile.polish_road_sign:sign_code.desc`
- **Języki**: pl_PL.lang, en_US.lang

## 📋 Katalog przedmiotów

### crafting_item_catalog.json

```json
{
  "format_version": "1.21.60",
  "minecraft:crafting_items_catalog": {
    "categories": [
      {
        "category_name": "construction",
        "groups": [
          {
            "group_identifier": {
              "icon": "polish_road_sign:a_1",
              "name": "polish_road_sign:warning_signs"
            },
            "items": [
              "polish_road_sign:a_1",
              "polish_road_sign:a_2"
            ]
          }
        ]
      }
    ]
  }
}
```

### Grupy znaków

- **A**: `warning_signs` - znaki ostrzegawcze
- **B**: `prohibition_signs` - znaki zakazu
- **C**: `mandatory_signs` - znaki nakazu
- **D**: `information_signs` - znaki informacyjne

## 🛠️ Skrypty budowania

### build_mcaddon.py

Buduje pojedynczy plik .mcaddon zawierający BP i RP:

```python
# Funkcje:
- read_manifest() - odczytuje nazwę i wersję z manifestu
- bump_version() - zwiększa wersję o 1
- update_version() - aktualizuje manifesty
- build_mcaddon() - główna funkcja budowania
```

### build_mcpack.py

Buduje osobne pliki .mcpack dla BP i RP:

```python
# Funkcje:
- build_mcpack() - buduje osobne pliki .mcpack
- Automatyczne nazewnictwo plików
- Kompatybilność z serwerami Aternos
```

### unpack_and_install_mcaddon.py

Instaluje paczkę lokalnie:

```python
# Funkcje:
- Rozpakowuje .mcaddon
- Kopiuje BP i RP do katalogów Minecraft
- Automatyczne nazewnictwo katalogów
```

## 🔄 GitHub Workflows

### Automatyczne budowanie

Projekt używa GitHub Actions do automatycznego budowania i testowania:

#### build.yml
- **Trigger**: Push do main/master, Pull Request, Manual dispatch
- **Funkcje**:
  - Buduje .mcaddon i .mcpack pliki
  - Uploaduje artifacts
  - Tworzy releases (manual dispatch z wersją)

#### test.yml
- **Trigger**: Push do main/master, Pull Request
- **Funkcje**:
  - Waliduje strukturę projektu
  - Sprawdza zgodność manifestów
  - Testuje proces budowania
  - Uploaduje test artifacts

#### version-bump.yml
- **Trigger**: Po udanym build workflow
- **Funkcje**:
  - Automatycznie zwiększa patch version
  - Aktualizuje manifesty BP i RP
  - Commit i push zmian

### Środowisko wirtualne (venv) - macOS

Przed uruchomieniem skryptów na macOS:

```bash
# Utwórz środowisko wirtualne
python3 -m venv venv

# Aktywuj środowisko
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom skrypty
python3 build_mcaddon.py
```

### requirements.txt

```txt
# Core dependencies
json5>=0.9.0
pathlib2>=2.3.0

# Development dependencies (optional)
# requests>=2.25.0  # For downloading textures
# Pillow>=8.0.0     # For image processing
```

## 🔍 Debugowanie

### Sprawdzanie manifestów

```bash
# Sprawdź wersje
grep "version" BP/manifest.json RP/manifest.json

# Sprawdź UUID
grep "uuid" BP/manifest.json RP/manifest.json

# Sprawdź zależności
grep -A 5 "dependencies" BP/manifest.json
```

### Sprawdzanie tekstur

```bash
# Sprawdź terrain_texture.json
cat RP/textures/terrain_texture.json | jq '.texture_data | keys'

# Sprawdź pliki tekstur
find RP/textures/blocks -name "*.png" | wc -l
```

### Sprawdzanie bloków

```bash
# Sprawdź liczbę bloków
find BP/blocks -name "*.block.json" | wc -l

# Sprawdź identyfikatory
grep "identifier" BP/blocks/*/*.block.json
```

## 📊 Statystyki projektu

### Liczba znaków:
- **A (Ostrzegawcze)**: 34 znaki
- **B (Zakazu)**: 43 znaki  
- **C (Nakazu)**: 19 znaków
- **D (Informacyjne)**: 47 znaków
- **Łącznie**: 143 znaki

### Pliki:
- **Bloki**: 143 pliki .block.json
- **Tekstury**: 143 pliki .png
- **Tłumaczenia**: 286 wpisów (2 języki × 143 znaki)

## 🚀 Rozwój

### Dodawanie nowego znaku

1. **Dodaj blok**:
   ```bash
   cp BP/blocks/a/a_1.block.json BP/blocks/a/a_35.block.json
   # Edytuj identifier i teksturę
   ```

2. **Dodaj teksturę**:
   ```bash
   # Umieść a_35.png w RP/textures/blocks/a/
   ```

3. **Zaktualizuj terrain_texture.json**:
   ```json
   "a_35": {
     "textures": "textures/blocks/a/a_35.png"
   }
   ```

4. **Dodaj tłumaczenia**:
   ```bash
   # Dodaj do RP/texts/pl_PL.lang i en_US.lang
   ```

5. **Zaktualizuj katalog**:
   ```bash
   # Dodaj do BP/item_catalog/crafting_item_catalog.json
   ```

### Konwencje kodowania

- **Nazwy plików**: małe litery, podkreślniki
- **Identyfikatory**: `polish_road_sign:category_number`
- **Tekstury**: `category/number.png`
- **Tłumaczenia**: `tile.polish_road_sign:identifier.name`

## 🔗 Zasoby zewnętrzne

### Dokumentacja Minecraft Bedrock
- [Behavior Pack Documentation](https://docs.microsoft.com/en-us/minecraft/creator/documents/behaviorpack)
- [Resource Pack Documentation](https://docs.microsoft.com/en-us/minecraft/creator/documents/resourcepack)
- [Block Documentation](https://docs.microsoft.com/en-us/minecraft/creator/reference/content/blockreference)

### Narzędzia
- [Blockbench](https://www.blockbench.net/) - edytor modeli i tekstur
- [Minecraft Bedrock Dedicated Server](https://www.minecraft.net/en-us/download/server/bedrock)

---

**Uwaga**: Ta dokumentacja jest przeznaczona dla developerów i contributorów projektu. 