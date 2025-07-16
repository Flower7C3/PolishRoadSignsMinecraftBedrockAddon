# Polish Road Signs - Minecraft Bedrock Addon

Polskie znaki drogowe dla Minecraft Bedrock Edition.

## 📋 Opis

Ten addon dodaje do Minecraft wszystkie polskie znaki drogowe zgodne z przepisami ruchu drogowego w Polsce. Znaki są podzielone na kategorie A (ostrzegawcze), B (zakazu), C (nakazu) i D (informacyjne).

## 🚦 Zawartość

### Kategorie znaków:
- **A (Ostrzegawcze)** - 34 znaki (A-1 do A-34)
- **B (Zakazu)** - 43 znaki (B-1 do B-43)
- **C (Nakazu)** - 19 znaków (C-1 do C-19)
- **D (Informacyjne)** - 47 znaków (D-1 do D-47)

### Funkcje:
- ✅ Wszystkie znaki z oficjalnymi nazwami polskimi
- ✅ Tłumaczenia angielskie
- ✅ Pionowe ustawienie znaków
- ✅ Realistyczne tekstury
- ✅ Grupowanie w kreatywnym trybie
- ✅ Kompatybilność z serwerami

## 🛠️ Instalacja

### Lokalnie (Minecraft Bedrock)

1. Pobierz plik `.mcaddon` z sekcji [Releases](https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon/releases)
2. Otwórz plik w Minecraft Bedrock
3. Aktywuj paczkę w ustawieniach → Global Resources

### Na serwerze (Aternos)

1. Pobierz pliki `.mcpack` (BP i RP)
2. Wgraj oba pliki na serwer Aternos
3. Uruchom serwer

## 🏗️ Budowanie

### GitHub Actions (Automatyczne)

Projekt używa GitHub Actions do automatycznego budowania:

- **Automatyczne budowanie** przy każdym push do main/master
- **Testowanie** struktury projektu i manifestów  
- **Automatyczne releases** z auto-version bump
- **Integracja** - jeden workflow dla build, test i release

### Wymagania:
- Python 3.7+
- Minecraft Bedrock Edition

### Środowisko wirtualne (venv) - macOS:

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

### Skrypty:

```bash
# Budowanie paczki .mcaddon (lokalnie)
python3 build_mcaddon.py

# Budowanie paczek .mcpack (serwery)
python3 build_mcpack.py

# Instalacja lokalna
python3 unpack_and_install_mcaddon.py
```

## 📁 Struktura projektu

```
PolishRoadSigns/
├── BP/                          # Behavior Pack
│   ├── blocks/                  # Definicje bloków
│   │   ├── a/                  # Znaki ostrzegawcze
│   │   ├── b/                  # Znaki zakazu
│   │   ├── c/                  # Znaki nakazu
│   │   └── d/                  # Znaki informacyjne
│   ├── item_catalog/           # Katalog przedmiotów
│   └── manifest.json           # Manifest BP
├── RP/                          # Resource Pack
│   ├── textures/               # Tekstury
│   │   └── blocks/
│   │       ├── a/             # Tekstury znaków A
│   │       ├── b/             # Tekstury znaków B
│   │       ├── c/             # Tekstury znaków C
│   │       └── d/             # Tekstury znaków D
│   ├── texts/                  # Tłumaczenia
│   └── manifest.json           # Manifest RP
├── dist/                       # Zbudowane paczki
├── build_mcaddon.py           # Skrypt budowania .mcaddon
├── build_mcpack.py            # Skrypt budowania .mcpack
├── unpack_and_install_mcaddon.py # Skrypt instalacji
├── setup_venv.sh              # Skrypt konfiguracji venv (macOS)
├── requirements.txt            # Zależności Python
└── .github/workflows/         # GitHub Actions
    └── build.yml              # Automatyczne budowanie, testowanie i release
```

## 🎮 Użycie

### W grze:
1. Przejdź do trybu kreatywnego
2. Znajdź kategorię "Construction" w kreatywnym menu
3. Wybierz grupę znaków (A, B, C, D)
4. Umieść znaki w świecie

### Właściwości bloków:
- **Pionowe ustawienie** - znaki są automatycznie ustawione pionowo
- **Obrót** - możesz obracać znaki w 4 kierunkach
- **Trwałość** - znaki można zniszczyć młotkiem
- **Dźwięk** - znaki wydają dźwięk kamienia

## 🌐 Tłumaczenia

Addon zawiera tłumaczenia w:
- 🇵🇱 **Polski** - oficjalne nazwy znaków
- 🇬🇧 **Angielski** - tłumaczenia nazw

## 🔧 Konfiguracja

### Manifesty:
- **Wersja**: Automatycznie zwiększana przy budowaniu
- **UUID**: Unikalne identyfikatory dla BP i RP
- **min_engine_version**: 1.16.0 (kompatybilne z 1.21+)

### Nazewnictwo:
- Wszystkie nazwy plików w małych literach
- Identyfikatory bloków: `polish_road_sign:sign_code`
- Tekstury: `textures/blocks/category/sign_code.png`

## 📝 Licencja

MIT License - zobacz plik [LICENSE](LICENSE) dla szczegółów.

## 👥 Autorzy

- **Flower7C3** - główny developer
- **Współpraca** - poprawki i sugestie

## 🔗 Linki

- [GitHub Repository](https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon)
- [Issues](https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon/issues)
- [Releases](https://github.com/Flower7C3/PolishRoadSignsMinecraftBedrockAddon/releases)

## 🐛 Znane problemy

- Brak znanych problemów w aktualnej wersji

## 📈 Historia wersji

### v1.0.32 (2025-07-16)
- ✅ Uproszczono workflowy GitHub Actions
- ✅ Zintegrowano build, test i release w jeden workflow
- ✅ Usunięto niepotrzebne pliki workflow
- ✅ Automatyczne releases z auto-version bump

### v1.0.31 (2025-07-16)
- ✅ Naprawiono nazewnictwo (małe litery)
- ✅ Poprawiono manifesty (spójne wersje)
- ✅ Dodano wsparcie dla serwerów Aternos
- ✅ Posprzątano kod projektu

### v1.0.0 (2025-07-16)
- 🎉 Pierwsza wersja
- ✅ Wszystkie polskie znaki drogowe
- ✅ Tekstury i tłumaczenia
- ✅ Kompatybilność z Minecraft Bedrock

---

**Uwaga**: Ten addon jest zgodny z polskimi przepisami ruchu drogowego i może być używany do edukacji o znakach drogowych. 