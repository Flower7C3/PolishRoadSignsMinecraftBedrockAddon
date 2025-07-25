# Polish Road Signs - Minecraft Bedrock Addon

Polskie znaki drogowe dla Minecraft Bedrock Edition.

## 📋 Opis

Ten addon dodaje do Minecraft wszystkie polskie znaki drogowe zgodne z przepisami ruchu drogowego w Polsce. Znaki są
podzielone na kategorie zgodnie z polskimi przepisami.

## 🚦 Zawartość

### Kategorie znaków

Znaki są podzielone na kategorie zgodnie z polskimi przepisami ruchu drogowego i znajdują się w odpowiednich katalogach w strukturze projektu.

### Funkcje

- ✅ Wszystkie znaki z oficjalnymi nazwami polskimi
- ✅ Dokładne tłumaczenia angielskie
- ✅ Pionowe ustawienie znaków
- ✅ Realistyczne tekstury z neutralnymi białymi tłem
- ✅ Grupowanie w kreatywnym trybie
- ✅ Kompatybilność z serwerami
- ✅ Automatyczne usuwanie starych wersji przy instalacji
- ✅ Automatyczne pobieranie i skalowanie obrazków z Wikipedii

## 🛠️ Instalacja

### Lokalnie (Minecraft Bedrock)

#### Metoda 1: Automatyczna instalacja (zalecana)

1. Pobierz plik `.mcaddon` z
   sekcji [Releases](https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon/releases)
2. Uruchom skrypt instalacji:
   ```bash
   python3 build.py --mcaddon --test-on-local
   ```
3. Uruchom Minecraft i włącz paczki (patrz sekcja "Aktywacja w grze")

#### Metoda 2: Ręczna instalacja

1. Pobierz plik `.mcaddon` z
   sekcji [Releases](https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon/releases)
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
    - Powinny pojawić się jako niestandardowe bloki z neutralnymi białymi tłem

### Rozwiązywanie problemów

Jeśli nie widzisz znaków w grze:

1. **Sprawdź czy używasz właściwego launcher'a Minecraft**: Paczki są zainstalowane dla mcpelauncher. Upewnij się, że
   używasz tego launcher'a, a nie oficjalnego launcher'a Minecraft.

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
python3 build.py --mcaddon
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

Skrypt `road_sign_processor.py` automatycznie pobiera obrazki znaków z Wikipedii i zarządza plikami:

```bash
# Pobierz i przeskaluj pojedynczy znak
python3 road_sign_processor.py a_1

# Pobierz i przeskaluj wszystkie znaki
python3 road_sign_processor.py all

# Przetwórz konkretną kategorię
python3 road_sign_processor.py category:A
python3 road_sign_processor.py category:B --skip-download

# Użyj lokalnych plików SVG (tryb offline)
python3 road_sign_processor.py a_1 --skip-download
python3 road_sign_processor.py all --skip-download

**💡 Funkcje zarządzania plikami:**
- Automatyczne usuwanie plików dla znaków usuniętych z bazy danych
- Dynamiczne aktualizowanie plików językowych i katalogu crafting
- Naturalne sortowanie znaków w menu crafting

# Funkcje skryptu:
# - Pobiera SVG z Wikipedii przez .fullImageLink
# - Skaluje z zachowaniem proporcji do 128px szerokości
# - Konwertuje SVG→PNG używając Inkscape
# - Zapisuje SVG jako cache obok PNG plików
# - Automatycznie tworzy modele 3D dla nowych wymiarów
# - Automatycznie tworzy neutralne białe tekstury tła
# - Automatycznie dostosowuje collision_box i selection_box
# - Aktualizuje bazę danych z wymiarami obrazków
# - Podsumowuje błędy na końcu
# - Tryb offline z flagą --skip-download
# - Przetwarzanie kategorii z automatycznym czyszczeniem
```

### Skrypty

```bash
# Budowanie paczek
python3 build.py --mcaddon                    # Buduje tylko .mcaddon
python3 build.py --mcpack                     # Buduje tylko .mcpack
python3 build.py --all                        # Buduje oba formaty
python3 build.py --all --no-bump              # Buduje bez zwiększania wersji
python3 build.py --mcaddon --test-on-local    # Buduj i przetestuj lokalnie
python3 build.py --all --test-on-local        # Buduj wszystko i przetestuj

# Generowanie komend testowych
python3 generate_examples.py              # Generuje wszystkie komendy
python3 generate_examples.py --test       # Tylko komendy testowe
python3 generate_examples.py --dev        # Tylko komendy deweloperskie

# Aktualizacja katalogu craftingowego
# (skrypt usunięty - funkcjonalność wbudowana w road_sign_processor.py)

# Pobieranie i skalowanie obrazków
python3 road_sign_processor.py [sign_id]

# Pobieranie w trybie offline (użyj lokalnych plików SVG)
python3 road_sign_processor.py [sign_id] --skip-download


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
- **Dokładne collision boxy** - collision_box i selection_box odpowiadają rzeczywistym wymiarom modeli
- **Precyzyjne klikanie** - gracze mogą dokładnie kliknąć na znaki bez problemów z niewidocznymi obszarami

## 🌐 Tłumaczenia

Addon zawiera dokładne tłumaczenia w:

- 🇵🇱 **Polski** - oficjalne nazwy znaków zgodne z przepisami
- 🇬🇧 **Angielski** - precyzyjne tłumaczenia nazw

### Przykłady tłumaczeń

| Polski                                 | Angielski                         |
|----------------------------------------|-----------------------------------|
| A-1: niebezpieczny zakręt w prawo      | A-1: Dangerous curve to the right |
| B-20: stop                             | B-20: Stop                        |
| C-1: nakaz jazdy w prawo przed znakiem | C-1: Turn right before sign       |
| D-1: droga z pierwszeństwem            | D-1: Priority road                |

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