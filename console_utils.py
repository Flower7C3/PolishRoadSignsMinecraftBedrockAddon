#!/usr/bin/env python3
"""
Biblioteka z funkcjami stylizacji konsoli dla skryptów
"""

import sys
from typing import Dict, Any, Union


def print_if_not_quiet(text):
    """Wyświetl tekst, tylko jeśli nie jest w trybie cichym"""
    if not ConsoleStyle.QUIET_MODE:
        print(text)


class ConsoleStyle:
    """Klasa do stylizacji komunikatów w konsoli"""

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
    def _colorize(color: str, text: str, padding: int = 0, icon: str = "", prefix: str = "", suffix: str = "") -> Union[
        str, None]:
        """Dodaj kolor do tekstu (tylko jeśli terminal wspiera kolory)"""
        if ConsoleStyle.QUIET_MODE:
            return None
        if sys.stdout.isatty():
            return f"{color}{prefix}{' ' * padding}{f'{icon} ' if icon else ''}{text}{suffix}{ConsoleStyle.FORMAT_RESET}"
        return text

    @staticmethod
    def success(text: str, padding: int = 0, icon: str = "✅️") -> Union[str, None]:
        """Stylizuj komunikat sukcesu"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.SUCCESS_HIGHLIGHT).replace("]", ConsoleStyle.SUCCESS_NORMAL)
        return ConsoleStyle._colorize(ConsoleStyle.SUCCESS_NORMAL, text, padding, icon)

    @staticmethod
    def error(text: str, padding: int = 0, icon: str = "❌️") -> str:
        """Stylizuj komunikat o błędzie"""
        text = text.replace("[", ConsoleStyle.ERROR_HIGHLIGHT).replace("]", ConsoleStyle.ERROR_NORMAL)
        return ConsoleStyle._colorize(ConsoleStyle.ERROR_NORMAL, text, padding, icon)

    @staticmethod
    def warning(text: str, padding: int = 0, icon: str = "⚠️") -> Union[str, None]:
        """Stylizuj komunikat ostrzeżenia"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.WARNING_HIGHLIGHT).replace("]", ConsoleStyle.WARNING_NORMAL)
        return ConsoleStyle._colorize(ConsoleStyle.WARNING_NORMAL, text, padding, icon)

    @staticmethod
    def delete(text: str, padding: int = 0, icon: str = "🗑️") -> Union[str, None]:
        """Stylizuj komunikat usuwania"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.WARNING_HIGHLIGHT).replace("]", ConsoleStyle.WARNING_NORMAL)
        return ConsoleStyle._colorize(ConsoleStyle.WARNING_NORMAL, text, padding, icon)

    @staticmethod
    def info(text: str, padding: int = 0, icon: str = "ℹ️") -> Union[str, None]:
        """Stylizuj komunikat informacyjny"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.INFO_HIGHLIGHT).replace("]", ConsoleStyle.INFO_NORMAL)
        return ConsoleStyle._colorize(ConsoleStyle.INFO_NORMAL, text, padding, icon)

    @staticmethod
    def process(text: str, padding: int = 0, icon: str = "🔄️") -> Union[str, None]:
        """Stylizuj komunikat procesu"""
        if ConsoleStyle.QUIET_MODE:
            return None
        text = text.replace("[", ConsoleStyle.PROCESS_HIGHLIGHT).replace("]", ConsoleStyle.PROCESS_NORMAL)
        return ConsoleStyle._colorize(ConsoleStyle.PROCESS_NORMAL, text, padding, icon)

    @staticmethod
    def section(title: str, icon: str = "") -> Union[str, None]:
        """Stylizuj tytuł sekcji"""
        if ConsoleStyle.QUIET_MODE:
            return None
        title = title.replace("[", ConsoleStyle.COLOR_CYAN_HIGHLIGHT).replace("]",
                                                                              ConsoleStyle.HEADER + ConsoleStyle.FORMAT_BOLD)
        return ConsoleStyle._colorize(ConsoleStyle.HEADER + ConsoleStyle.FORMAT_BOLD, title, icon=icon, prefix="\n")

    @staticmethod
    def divider(char: str = "=", length: int = 50) -> Union[str, None]:
        """Utwórz separator"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return char * length

    @staticmethod
    def print_stats(stats_dict: Dict[str, Any], title: str = "Statistics", divider_sign: str = "=", icon: str = "📊"):
        """Wyświetl statystyki w ładnej tabeli"""
        if ConsoleStyle.QUIET_MODE or not stats_dict:
            return

        ConsoleStyle.print_section(title, divider_sign, icon=icon)
        max_key_length = max(len(str(key)) for key in stats_dict.keys()) + 2

        for key, value in stats_dict.items():
            key_padded = str(key).ljust(max_key_length)
            if type(value) == str:
                value = value.replace("[", ConsoleStyle.COLOR_CYAN_HIGHLIGHT).replace("]", ConsoleStyle.COLOR_CYAN)
            print_if_not_quiet(
                ConsoleStyle._colorize(ConsoleStyle.COLOR_CYAN,
                                       f"  {ConsoleStyle.FORMAT_BOLD}{key_padded}{ConsoleStyle.FORMAT_RESET}: {value}"))

    @staticmethod
    def print_section(title: str, divider_sign: str = "=", icon: str = ""):
        """Wyświetl sekcję z tytułem i opcjonalną zawartością"""
        if ConsoleStyle.QUIET_MODE:
            return

        print(ConsoleStyle.section(title, icon=icon))
        print(ConsoleStyle.divider(divider_sign))

    @staticmethod
    def print_summary(success_count: int, total_count: int, errors: list = None):
        """Wyświetl podsumowanie operacji"""
        if ConsoleStyle.QUIET_MODE:
            return

        stats = {
            "Successes": f"{success_count}/{total_count}",
            "Failures": total_count - success_count,
            "Success rate": f"{(success_count / total_count * 100):.1f}%" if total_count > 0 else "0%"
        }
        ConsoleStyle.print_stats(stats, "SUMMARY")

        if errors:
            print(ConsoleStyle.error("ERRORS:"))
            for error in errors:
                print(ConsoleStyle.error(f"- {error}", 3))
        else:
            print(ConsoleStyle.success("All operations finalized correctly!"))

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

        print(ConsoleStyle.success(f"Created: {output_path}"))
        if file_size:
            print(ConsoleStyle.info(f"Size: {file_size}"))

    @staticmethod
    def print_installation_info(pack_name: str, install_path: str):
        """Wyświetl informacje o instalacji"""
        if ConsoleStyle.QUIET_MODE:
            return

        print(ConsoleStyle.success(f"Installed: {pack_name}"))
        print(ConsoleStyle.info(f"Location: {install_path}"))


def rsort(sizes: Dict[str, Any]) -> Dict[str, Any]:
    return dict(sorted(sizes.items(), key=lambda x: x[1], reverse=True))
