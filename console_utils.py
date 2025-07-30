#!/usr/bin/env python3
"""
Biblioteka z funkcjami stylizacji konsoli dla skryptów
"""

import sys
from typing import Dict, Any, Union


def print_if_not_quiet(text):
    """Wyświetl tekst tylko jeśli nie jest w trybie cichym"""
    if not ConsoleStyle.QUIET_MODE:
        print(text)


class ConsoleStyle:
    """Klasa do stylizacji komunikatów w konsoli"""

    # Emoji dla różnych typów komunikatów
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_INFO = "ℹ️"
    ICON_PROCESSING = "🔄"
    ICON_DELETE = "🗑️"

    # Kolory ANSI (dla terminali wspierających kolory)
    FORMAT_RESET = "\033[0m"
    FORMAT_BOLD = "\033[1m"
    COLOR_RED = "\033[31m"
    COLOR_RED_HIGHLIGHT = "\033[91m"
    COLOR_GREEN = "\033[32m"
    COLOR_GREEN_HIGHLIGHT = "\033[92m"
    COLOR_YELLOW = "\033[33m"
    COLOR_YELLOW_HIGHLIGHT = "\033[93m"
    COLOR_BLUE = "\033[34m"
    COLOR_BLUE_HIGHLIGHT = "\033[94m"
    COLOR_MAGENTA = "\033[35m"
    COLOR_MAGENTA_HIGHLIGHT = "\033[95m"
    COLOR_CYAN = "\033[36m"
    COLOR_CYAN_HIGHLIGHT = "\033[96m"
    COLOR_WHITE = "\033[37m"

    # Style dla różnych typów komunikatów
    HEADER = f"{FORMAT_BOLD}{COLOR_CYAN}"
    SUCCESS_NORMAL = f"{COLOR_GREEN}"
    SUCCESS_HIGHLIGHT = f"{COLOR_GREEN_HIGHLIGHT}"
    ERROR_NORMAL = f"{COLOR_RED}"
    ERROR_HIGHLIGHT = f"{COLOR_RED_HIGHLIGHT}"
    WARNING_NORMAL = f"{COLOR_YELLOW}"
    WARNING_HIGHLIGHT = f"{COLOR_YELLOW_HIGHLIGHT}"
    INFO_NORMAL = f"{COLOR_BLUE}"
    INFO_HIGHLIGHT = f"{COLOR_BLUE_HIGHLIGHT}"
    PROCESS_NORMAL = f"{COLOR_MAGENTA}"
    PROCESS_HIGHLIGHT = f"{COLOR_MAGENTA_HIGHLIGHT}"

    # Tryb cichy
    QUIET_MODE = False

    @staticmethod
    def set_quiet_mode(enabled: bool = True):
        """Ustaw tryb cichy"""
        ConsoleStyle.QUIET_MODE = enabled

    @staticmethod
    def colorize(text: str, color: str) -> Union[str, None]:
        """Dodaj kolor do tekstu (tylko jeśli terminal wspiera kolory)"""
        if ConsoleStyle.QUIET_MODE:
            return None
        if sys.stdout.isatty():
            return f"{color}{text}{ConsoleStyle.FORMAT_RESET}"
        return text

    @staticmethod
    def header(text: str) -> Union[str, None]:
        """Stylizuj nagłówek sekcji"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return ConsoleStyle.colorize(f"\n{text}", ConsoleStyle.HEADER)

    @staticmethod
    def success(text: str) -> Union[str, None]:
        """Stylizuj komunikat sukcesu"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.SUCCESS_HIGHLIGHT).replace("]", ConsoleStyle.SUCCESS_NORMAL)
        return ConsoleStyle.colorize(f"{ConsoleStyle.ICON_SUCCESS}  {text}", ConsoleStyle.SUCCESS_NORMAL)

    @staticmethod
    def error(text: str) -> str:
        """Stylizuj komunikat o błędzie"""
        text = text.replace("[", ConsoleStyle.ERROR_HIGHLIGHT).replace("]", ConsoleStyle.ERROR_NORMAL)
        return ConsoleStyle.colorize(f"{ConsoleStyle.ICON_ERROR}  {text}", ConsoleStyle.ERROR_NORMAL)

    @staticmethod
    def warning(text: str) -> Union[str, None]:
        """Stylizuj komunikat ostrzeżenia"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.WARNING_HIGHLIGHT).replace("]", ConsoleStyle.WARNING_NORMAL)
        return ConsoleStyle.colorize(f"{ConsoleStyle.ICON_WARNING}  {text}", ConsoleStyle.WARNING_NORMAL)

    @staticmethod
    def delete(text: str) -> Union[str, None]:
        """Stylizuj komunikat usuwania"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.WARNING_HIGHLIGHT).replace("]", ConsoleStyle.WARNING_NORMAL)
        return ConsoleStyle.colorize(f"{ConsoleStyle.ICON_DELETE}  {text}", ConsoleStyle.WARNING_NORMAL)

    @staticmethod
    def info(text: str) -> Union[str, None]:
        """Stylizuj komunikat informacyjny"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.INFO_HIGHLIGHT).replace("]", ConsoleStyle.INFO_NORMAL)
        return ConsoleStyle.colorize(f"{ConsoleStyle.ICON_INFO}  {text}", ConsoleStyle.INFO_NORMAL)

    @staticmethod
    def process(text: str) -> Union[str, None]:
        """Stylizuj komunikat procesu"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.PROCESS_HIGHLIGHT).replace("]", ConsoleStyle.PROCESS_NORMAL)
        return ConsoleStyle.colorize(f"{ConsoleStyle.ICON_PROCESSING}  {text}", ConsoleStyle.PROCESS_NORMAL)

    @staticmethod
    def section(title: str) -> Union[str, None]:
        """Stylizuj tytuł sekcji"""
        if ConsoleStyle.QUIET_MODE:
            return None
        title = title.replace("[", ConsoleStyle.COLOR_CYAN_HIGHLIGHT).replace("]", ConsoleStyle.HEADER + ConsoleStyle.FORMAT_BOLD)
        return ConsoleStyle.colorize(f"\n{title}", ConsoleStyle.HEADER + ConsoleStyle.FORMAT_BOLD)

    @staticmethod
    def divider(char: str = "=", length: int = 50) -> Union[str, None]:
        """Utwórz separator"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return char * length

    @staticmethod
    def print_stats(stats_dict: Dict[str, Any], title: str = "🔍 Statystyki", divider_sign: str = "="):
        """Wyświetl statystyki w ładnej tabeli"""
        if ConsoleStyle.QUIET_MODE or not stats_dict:
            return

        ConsoleStyle.print_section(title, divider_sign)
        max_key_length = max(len(str(key)) for key in stats_dict.keys()) + 2

        for key, value in stats_dict.items():
            key_padded = str(key).ljust(max_key_length)
            if type(value) == str:
                value = value.replace("[", ConsoleStyle.COLOR_CYAN_HIGHLIGHT).replace("]", ConsoleStyle.COLOR_CYAN)
            print_if_not_quiet(
                ConsoleStyle.colorize(f"  {ConsoleStyle.FORMAT_BOLD}{key_padded}{ConsoleStyle.FORMAT_RESET}: {value}",
                                      ConsoleStyle.COLOR_CYAN))

    @staticmethod
    def print_section(title: str, divider_sign: str = "="):
        """Wyświetl sekcję z tytułem i opcjonalną zawartością"""
        if ConsoleStyle.QUIET_MODE:
            return

        print(ConsoleStyle.section(title))
        print(ConsoleStyle.divider(divider_sign))

    @staticmethod
    def print_summary(success_count: int, total_count: int, errors: list = None):
        """Wyświetl podsumowanie operacji"""
        if ConsoleStyle.QUIET_MODE:
            return

        stats = {
            "Sukces": f"{success_count}/{total_count}",
            "Niepowodzenia": total_count - success_count,
            "Procent sukcesu": f"{(success_count / total_count * 100):.1f}%" if total_count > 0 else "0%"
        }
        ConsoleStyle.print_stats(stats, "🔍 PODSUMOWANIE")

        if errors:
            print(ConsoleStyle.error("BŁĘDY:"))
            for error in errors:
                print(f"  - {error}")
        else:
            print(ConsoleStyle.success("Wszystkie operacje zakończone pomyślnie!"))

    @staticmethod
    def print_file_operation(operation: str, file_path: str, status: str = "OK"):
        """Wyświetl informację o operacji na pliku"""
        if ConsoleStyle.QUIET_MODE:
            return

        if status == "OK":
            print(ConsoleStyle.success(f"{operation}: {file_path}"))
        elif status == "ERROR":
            print(ConsoleStyle.error(f"{operation}: {file_path}"))
        elif status == "WARNING":
            print(ConsoleStyle.warning(f"{operation}: {file_path}"))
        else:
            print(ConsoleStyle.info(f"{operation}: {file_path}"))

    @staticmethod
    def print_build_info(build_type: str, output_path: str, file_size: str = ""):
        """Wyświetl informacje o budowaniu"""
        if ConsoleStyle.QUIET_MODE:
            return

        print(ConsoleStyle.section(f"⚒️ BUDOWANIE {build_type.upper()}"))
        print(ConsoleStyle.divider())
        print(ConsoleStyle.success(f"Utworzono: {output_path}"))
        if file_size:
            print(ConsoleStyle.info(f"Rozmiar: {file_size}"))
        print(ConsoleStyle.divider())

    @staticmethod
    def print_installation_info(pack_name: str, install_path: str):
        """Wyświetl informacje o instalacji"""
        if ConsoleStyle.QUIET_MODE:
            return

        print(ConsoleStyle.section("INSTALACJA"))
        print(ConsoleStyle.divider())
        print(ConsoleStyle.success(f"Zainstalowano: {pack_name}"))
        print(ConsoleStyle.info(f"Lokalizacja: {install_path}"))
        print(ConsoleStyle.divider())


def rsort(sizes: Dict[str, Any]) -> Dict[str, Any]:
    return dict(sorted(sizes.items(), key=lambda x: x[1], reverse=True))
