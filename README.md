# Polish Road Signs - Minecraft Bedrock Addon

Polskie znaki drogowe dla Minecraft Bedrock Edition.

## 📋 Opis

Ten addon dodaje do Minecraft wszystkie polskie znaki drogowe zgodne z przepisami ruchu drogowego w Polsce. Znaki są podzielone na kategorie A (ostrzegawcze), B (zakazu), C (nakazu) i D (informacyjne).

## 🚦 Zawartość

### Kategorie znaków

- **A (Ostrzegawcze)** - 34 znaki (A-1 do A-34)
- **B (Zakazu)** - 44 znaki (B-1 do B-44)
- **C (Nakazu)** - 19 znaków (C-1 do C-19)
- **D (Informacyjne)** - 55 znaków (D-1 do D-55)

### Funkcje

- ✅ Wszystkie znaki z oficjalnymi nazwami polskimi
- ✅ Dokładne tłumaczenia angielskie
- ✅ Pionowe ustawienie znaków
- ✅ Realistyczne tekstury z szarymi tłem
- ✅ Grupowanie w kreatywnym trybie
- ✅ Kompatybilność z serwerami
- ✅ Automatyczne usuwanie starych wersji przy instalacji
- ✅ Automatyczne pobieranie i skalowanie obrazków z Wikipedii

## 🛠️ Instalacja

### Lokalnie (Minecraft Bedrock)

#### Metoda 1: Automatyczna instalacja (zalecana)

1. Pobierz plik `.mcaddon` z sekcji [Releases](https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon/releases)
2. Uruchom skrypt instalacji:
   ```bash
   python3 unpack_and_install_mcaddon.py dist/PolishRoadSigns_v*.mcaddon
   ```
3. Uruchom Minecraft i włącz paczki (patrz sekcja "Aktywacja w grze")

#### Metoda 2: Ręczna instalacja

1. Pobierz plik `.mcaddon` z sekcji [Releases](https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon/releases)
2. Otwórz plik w Minecraft Bedrock
3. Aktywuj paczkę w ustawieniach → Global Resources

### Na serwerze (Aternos)

1. Pobierz pliki `.mcpack` (BP i RP)
2. Wgraj oba pliki na serwer Aternos
3. Uruchom serwer

### Aktywacja w grze

Po zainstalowaniu paczek, musisz je aktywować w Minecraft:

1. **Zamknij Minecraft** (jeśli jest uruchomiony)

2. **Otwórz Minecraft** i przejdź do:
   - Ustawienia → Zasoby globalne
   - Znajdź "Polish Road Signs RP" i włącz ją (przesuń na prawą stronę)

3. **Włącz eksperymenty**:
   - Przejdź do Ustawienia → Eksperymenty
   - Włącz "Holiday Creator Features" (wymagane dla niestandardowych bloków)

4. **Utwórz lub edytuj świat**:
   - Utwórz nowy świat lub edytuj istniejący
   - W ustawieniach świata upewnij się, że "Holiday Creator Features" jest włączone
   - Paczka zachowań powinna być automatycznie włączona po włączeniu paczki zasobów

5. **Przetestuj znaki**:
   - W grze otwórz swój ekwipunek
   - Znajdź polskie znaki drogowe w kreatywnym ekwipunku
   - Powinny pojawić się jako niestandardowe bloki z szarymi tłem

### Rozwiązywanie problemów

Jeśli nie widzisz znaków w grze:

1. **Sprawdź czy używasz właściwego launcher'a Minecraft**: Paczki są zainstalowane dla mcpelauncher. Upewnij się, że używasz tego launcher'a, a nie oficjalnego launcher'a Minecraft.

2. **Spróbuj świeżego świata**: Utwórz całkowicie nowy świat z włączonymi "Holiday Creator Features".

3. **Sprawdź wersję gry**: Upewnij się, że używasz Minecraft Bedrock Edition w wersji 1.16.0 lub wyższej.

4. **Uruchom ponownie Minecraft**: Czasami musisz całkowicie uruchomić ponownie Minecraft po zainstalowaniu paczek.

5. **Sprawdź czy paczki są zainstalowane**:
   ```bash
   # Sprawdź czy paczki są w odpowiednim katalogu
   ls "/Users/bartlomiej.kwiatek/Library/Application Support/mcpelauncher/games/com.mojang/behavior_packs/PolishRoadSigns"
   ls "/Users/bartlomiej.kwiatek/Library/Application Support/mcpelauncher/games/com.mojang/resource_packs/PolishRoadSigns"
   ```

## 🏗️ Budowanie

### GitHub Actions (Automatyczne)

Projekt używa GitHub Actions do automatycznego budowania:

- **Weryfikacja projektu** - sprawdza integralność przed budowaniem
- **Automatyczne budowanie** przy każdym push do main/master
- **Testowanie** struktury projektu i manifestów  
- **Automatyczne releases** z auto-version bump
- **Integracja** - jeden workflow dla build, test i release

### Wymagania

- Python 3.7+
- Minecraft Bedrock Edition
- Inkscape (do konwersji SVG→PNG)
- curl (do pobierania obrazków)

### Środowisko wirtualne (venv) - macOS

Przed uruchomieniem skryptów na macOS, zalecane jest utworzenie środowiska wirtualnego:

```bash
# Automatyczna konfiguracja (zalecane)
./setup_venv.sh

# Lub ręcznie:
# Utwórz środowisko wirtualne
python3 -m venv venv

# Aktywuj środowisko
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom skrypty
python3 build_mcaddon.py
```

### Weryfikacja projektu

Przed budowaniem, możesz uruchomić pełną weryfikację projektu:

```bash
# Sprawdź integralność projektu
python3 verify_all.py

# Sprawdź czy wszystko jest w porządku
# - Tekstury, modele 3D, definicje bloków
# - Baza danych, tłumaczenia, struktura
# - Nadmiarowe/brakujące pliki
```

### Pobieranie i skalowanie obrazków

Skrypt `resize_simple.py` automatycznie pobiera obrazki znaków z Wikipedii:

```bash
# Pobierz i przeskaluj pojedynczy znak
python3 resize_simple.py a_1

# Pobierz i przeskaluj wszystkie znaki
python3 resize_simple.py

# Funkcje skryptu:
# - Pobiera SVG z Wikipedii przez .fullImageLink a
# - Skaluje z zachowaniem proporcji do 128px szerokości
# - Konwertuje SVG→PNG używając Inkscape
# - Aktualizuje bazę danych z wymiarami obrazków
# - Podsumowuje błędy na końcu
```

### Skrypty

```bash
# Budowanie paczki .mcaddon (lokalnie)
python3 build_mcaddon.py

# Budowanie paczek .mcpack (serwery)
python3 build_mcpack.py

# Instalacja lokalna (z automatycznym usuwaniem starych wersji)
python3 unpack_and_install_mcaddon.py dist/PolishRoadSigns_v*.mcaddon

# Instalacja bez usuwania starych wersji
python3 unpack_and_install_mcaddon.py dist/PolishRoadSigns_v*.mcaddon --no-clean

# Aktualizacja katalogu craftingowego
python3 update_crafting_catalog.py

# Pobieranie i skalowanie obrazków
python3 resize_simple.py [sign_id]
```

## 📁 Struktura projektu

```text
PolishRoadSigns/
├── BP/                          # Behavior Pack
│   ├── blocks/                  # Definicje bloków
│   │   ├── a/                  # Znaki ostrzegawcze (34)
│   │   ├── b/                  # Znaki zakazu (44)
│   │   ├── c/                  # Znaki nakazu (19)
│   │   └── d/                  # Znaki informacyjne (55)
│   ├── item_catalog/           # Katalog przedmiotów
│   └── manifest.json           # Manifest BP
├── RP/                          # Resource Pack
│   ├── textures/               # Tekstury
│   │   └── blocks/
│   │       ├── a/             # Tekstury znaków A
│   │       ├── b/             # Tekstury znaków B
│   │       ├── c/             # Tekstury znaków C
│   │       ├── d/             # Tekstury znaków D
│   │       └── sign_backs/    # Tła znaków
│   ├── texts/                  # Tłumaczenia
│   │   ├── pl_PL.lang         # Polski
│   │   └── en_US.lang         # Angielski
│   ├── models/                 # Modele 3D
│   └── manifest.json           # Manifest RP
├── dist/                       # Zbudowane paczki
├── build_mcaddon.py           # Skrypt budowania .mcaddon
├── build_mcpack.py            # Skrypt budowania .mcpack
├── unpack_and_install_mcaddon.py # Skrypt instalacji z auto-clean
├── update_crafting_catalog.py # Skrypt aktualizacji katalogu craftingowego
├── verify_all.py              # Skrypt weryfikacji projektu
├── resize_simple.py           # Skrypt pobierania i skalowania obrazków
├── setup_venv.sh              # Skrypt konfiguracji venv (macOS)
├── requirements.txt            # Zależności Python
├── road_signs_full_database.json # Pełna baza danych znaków
└── .github/workflows/         # GitHub Actions
    └── build.yml              # Automatyczne budowanie, testowanie i release
```

## 🎮 Użycie

### W grze

1. Przejdź do trybu kreatywnego
2. Znajdź kategorię "Construction" w kreatywnym menu
3. Wybierz grupę znaków (A, B, C, D)
4. Umieść znaki w świecie

### Właściwości bloków

- **Pionowe ustawienie** - znaki są automatycznie ustawione pionowo
- **Obrót** - możesz obracać znaki w 4 kierunkach
- **Trwałość** - znaki można zniszczyć młotkiem
- **Dźwięk** - znaki wydają dźwięk kamienia
- **Szare tło** - wszystkie znaki mają realistyczne szare tło

## 🌐 Tłumaczenia

Addon zawiera dokładne tłumaczenia w:

- 🇵🇱 **Polski** - oficjalne nazwy znaków zgodne z przepisami
- 🇬🇧 **Angielski** - precyzyjne tłumaczenia nazw

### Przykłady tłumaczeń

| Polski | Angielski |
|--------|-----------|
| A-1: niebezpieczny zakręt w prawo | A-1: Dangerous curve to the right |
| B-20: stop | B-20: Stop |
| C-1: nakaz jazdy w prawo przed znakiem | C-1: Turn right before sign |
| D-1: droga z pierwszeństwem | D-1: Priority road |

## 🔧 Konfiguracja

### Manifesty

- **Wersja**: Automatycznie zwiększana przy budowaniu
- **UUID**: Unikalne identyfikatory dla BP i RP
- **min_engine_version**: 1.16.0 (kompatybilne z 1.21+)

### Nazewnictwo

- Wszystkie nazwy plików w małych literach
- Identyfikatory bloków: `polish_road_sign:sign_code`
- Tekstury: `textures/blocks/category/sign_code.png`
- Tłumaczenia: `tile.polish_road_sign:sign_code.name`

### Baza danych

Plik `road_signs_full_database.json` zawiera:
- Pełne informacje o wszystkich znakach
- Linki do Wikipedii dla pobierania obrazków
- Wymiary obrazków (aktualizowane automatycznie)
- Tłumaczenia polskie i angielskie

## 📝 Licencja

MIT License - zobacz plik [LICENSE](LICENSE) dla szczegółów.

## 👥 Autorzy

- **Flower7C3** - główny developer
- **Współpraca** - poprawki i sugestie