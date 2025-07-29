# 🚦 Polish Road Signs — Minecraft Bedrock Addon

Polskie znaki drogowe dla Minecraft Bedrock Edition.

---

## 📋 Opis

Ten dodatek pozwala używać większość polskich znaków drogowych zgodne z przepisami ruchu drogowego w Polsce. Może być
używany do edukacji o znakach drogowych.

### ✨ Funkcjonalności

- ✅ Wszystkie znaki z oficjalnymi nazwami polskimi
- ✅ Dokładne tłumaczenia angielskie
- ✅ Pionowe ustawienie znaków
- ✅ Realistyczne tekstury z neutralnymi białymi tłem
- ✅ Grupowanie w kreatywnym trybie
- ✅ Kompatybilność z serwerami
- ✅ Automatyczne usuwanie starych wersji przy instalacji
- ✅ Automatyczne pobieranie i skalowanie obrazków z Wikipedii

---

## 🛠️ Instalacja

### 🏠 Lokalnie (Minecraft Bedrock) ze zbudowanych paczek

1. Pobierz plik `.mcaddon` z
   sekcji [Releases](https://github.com/Flower7C3/polish-road-signs-minecraft-bedrock-addon/releases
2. Otwórz go w Minecraft Bedrock
3. Włącz paczki Włącz paczki:
    - Ustawienia → Zasoby globalne
    - Znajdź "Polish Road Signs RP" i włącz ją (przesuń na prawą stronę)
4. Włącz eksperymenty:
    - Przejdź do Ustawienia → Eksperymenty
    - Włącz "Holiday Creator Features" (wymagane dla niestandardowych bloków)
5. Utwórz lub edytuj świat:
    - Utwórz nowy świat lub edytuj istniejący
    - W ustawieniach świata upewnij się, że "Holiday Creator Features" jest włączone
    - Paczka zachowań powinna być automatycznie włączona po włączeniu paczki zasobów

### 🌐 Na serwerze (Aternos)

1. Pobierz pliki `.mcpack` z
   sekcji [Releases](https://github.com/Flower7C3/polish-road-signs-minecraft-bedrock-addon/releases)
2. Wgraj je na serwer Aternos
3. Uruchom serwer i dołącz do gry

> Pliki paczki możesz również zbudować lokalnie. Zobacz więcej w sekcji [Budowanie](#%EF%B8%8F-budowanie)").

### 🔧 Rozwiązywanie problemów

Jeśli nie widzisz znaków w grze:

1. **Sprawdź, czy używasz właściwego launcher'a Minecraft**: Paczki są zainstalowane dla mcpelauncher. Upewnij się, że
   używasz tego launcher'a, a nie oficjalnego launcher'a Minecraft.

2. **Spróbuj świeżego świata**: Utwórz całkowicie nowy świat z włączonymi "Holiday Creator Features".

3. **Sprawdź wersję gry**: Upewnij się, że używasz Minecraft Bedrock Edition w wersji 1.16.0 lub wyższej.

4. **Uruchom ponownie Minecraft**: Czasami musisz całkowicie uruchomić ponownie Minecraft po zainstalowaniu paczek.

5. **Sprawdź, czy paczki są zainstalowane w odpowiednim katalogu**, np.:
   ```bash
   ls "/Users/bartlomiej.kwiatek/Library/Application Support/mcpelauncher/games/com.mojang/behavior_packs/PolishRoadSigns"
   ls "/Users/bartlomiej.kwiatek/Library/Application Support/mcpelauncher/games/com.mojang/resource_packs/PolishRoadSigns"
   ```

### 🎮 Użycie w grze

1. Przejdź do trybu kreatywnego
2. Znajdź kategorię "Construction" w kreatywnym menu
3. Wybierz grupę znaków (A, B, C, D)
4. Umieść znaki w świecie

### ⚙️ Właściwości bloków

- **Pionowe ustawienie** — znaki są automatycznie ustawione pionowo
- **Obrót** — możesz obracać znaki w 4 kierunkach
- **Trwałość** — znaki można zniszczyć młotkiem
- **Dźwięk** — znaki wydają dźwięk kamienia
- **Szare tło** — wszystkie znaki mają realistyczne szare tło
- **Dokładne collision boxy** - collision_box i selection_box odpowiadają rzeczywistym wymiarom modeli
- **Precyzyjne klikanie** — gracze mogą dokładnie kliknąć znaki bez problemów z niewidocznymi obszarami

---

## 🏗️ Budowanie

### 🤖 GitHub Actions (Automatyczne)

Projekt używa GitHub Actions do automatycznego budowania i wydawania wersji.

- **Weryfikacja projektu** — sprawdza integralność przed budowaniem
- **Automatyczne budowanie** przy każdym push do main/master
- **Testowanie** struktury projektu i manifestów
- **Automatyczne releases** z auto-version bump
- **Integracja** – jeden workflow dla build, test i release

### 💻 Lokalnie

> #### Wymagania
> - **Minecraft Bedrock** — z eksperymentalnymi funkcjami
> - **Python** 3.7+ – do budowania paczek
> - **Inkscape** – do konwersji SVG→PNG
> - **curl** – do pobierania obrazków

Pobierz repozytorium i wejdź do katalogu projektu:

```bash
git clone https://github.com/Flower7C3/polish-road-signs-minecraft-bedrock-addon.git
cd polish-road-signs-minecraft-bedrock-addon
```

> #### Środowisko wirtualne (venv) - macOS
> Przed uruchomieniem skryptów na macOS, zalecane jest utworzenie i uruchomienie środowiska wirtualnego:
> ```bash
> ./setup_venv.sh
> source venv/bin/activate
> ```

Przed budowaniem, możesz uruchomić pełną weryfikację projektu:

```bash
python3 verify_all.py
```

Gdy już wszystko gotowe możesz uruchomić skrypt budowania, który pokaże dostępne opcje:

```bash
python3 build.py
```

Np. możesz uruchomić skrypt budowania z instalacją bez podnoszenia wersji:

```bash
python3 build.py --mcaddon --test-on-local --no-bump
```

### ➕ Dodawanie nowych znaków

Plik [road_signs_full_database.json](road_signs_full_database.json) zawiera:

- Pełne informacje o wszystkich znakach
- Linki do Wikipedii dla pobierania obrazków
- Wymiary obrazków (aktualizowane automatycznie)
- Tłumaczenia polskie i angielskie

Jeżeli zmienisz w nim dane, możesz wygenerować na nowo pliki paczki, używając odpowiedniego skryptu:

- [road_sign_processor.py](road_sign_processor.py) automatycznie pobiera obrazki znaków z Wikipedii i zarządza plikami.
  Aby dowiedzieć się więcej uruchom:
    ```bash
    python3 road_sign_processor.py --help
    ```

- [generate_examples.py](generate_examples.py) generuje przykładowe znaki. Więcej informacji:
    ```bash
    python3 generate_examples.py --help
    ```

---

## 📄 Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik [LICENSE](LICENSE) dla szczegółów.

---

## 👥 Autorzy

- **Flower7C3** - główny developer
- **🤝 Współpraca** — poprawki i sugestie
