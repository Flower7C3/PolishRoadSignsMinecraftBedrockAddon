#!/usr/bin/env python3
"""
Biblioteka z funkcjami stylizacji konsoli dla skryptów
"""

import sys
import os
from typing import Dict, Any, Optional


def print_if_not_quiet(text):
    """Wyświetl tekst tylko jeśli nie jest None (tryb cichy)"""
    if text is not None:
        print(text)


class ConsoleStyle:
    """Klasa do stylizacji komunikatów w konsoli"""
    
    # Emoji dla różnych typów komunikatów
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    PROCESSING = "🔄"
    DOWNLOAD = "⏬"
    CREATE = "🆕"
    UPDATE = "🆙"
    EXISTS = "🆗"
    DELETE = "🗑️"
    CLEAN = "🧹"
    SEARCH = "🔍"
    STATS = "📊"
    LIST = "📋"
    FOLDER = "📁"
    FILE = "📄"
    DIMENSIONS = "📐"
    CONVERT = "🔀"
    MODEL = "📦"
    TEXTURE = "🎨"
    BLOCK = "⏹️"
    LANGUAGE = "🌐"
    CRAFTING = "🔨"
    START = "🚀"
    COMPLETE = "🎉"
    VERIFY = "🔍"
    BUILD = "🔨"
    INSTALL = "📦"
    TEST = "🧪"
    
    # Kolory ANSI (dla terminali wspierających kolory)
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Style dla różnych typów komunikatów
    HEADER = f"{BOLD}{CYAN}"
    SUCCESS_MSG = f"{GREEN}"
    ERROR_MSG = f"{RED}"
    WARNING_MSG = f"{YELLOW}"
    INFO_MSG = f"{BLUE}"
    PROCESS_MSG = f"{MAGENTA}"
    
    # Tryb cichy
    QUIET_MODE = False
    
    @staticmethod
    def set_quiet_mode(enabled: bool = True):
        """Ustaw tryb cichy"""
        ConsoleStyle.QUIET_MODE = enabled
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Dodaj kolor do tekstu (tylko jeśli terminal wspiera kolory)"""
        if ConsoleStyle.QUIET_MODE:
            return None
        if sys.stdout.isatty():
            return f"{color}{text}{ConsoleStyle.RESET}"
        return text
    
    @staticmethod
    def header(text: str) -> str:
        """Stylizuj nagłówek sekcji"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return ConsoleStyle.colorize(f"\n{text}", ConsoleStyle.HEADER)
    
    @staticmethod
    def success(text: str) -> str:
        """Stylizuj komunikat sukcesu"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return ConsoleStyle.colorize(f"{ConsoleStyle.SUCCESS}  {text}", ConsoleStyle.SUCCESS_MSG)
    
    @staticmethod
    def error(text: str) -> str:
        """Stylizuj komunikat błędu"""
        return ConsoleStyle.colorize(f"{ConsoleStyle.ERROR}  {text}", ConsoleStyle.ERROR_MSG)
    
    @staticmethod
    def warning(text: str) -> str:
        """Stylizuj komunikat ostrzeżenia"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return ConsoleStyle.colorize(f"{ConsoleStyle.WARNING}  {text}", ConsoleStyle.WARNING_MSG)
    
    @staticmethod
    def delete(text: str) -> str:
        """Stylizuj komunikat usuwania"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return ConsoleStyle.colorize(f"{ConsoleStyle.DELETE}  {text}", ConsoleStyle.WARNING_MSG)

    @staticmethod
    def info(text: str) -> str:
        """Stylizuj komunikat informacyjny"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return ConsoleStyle.colorize(f"{ConsoleStyle.INFO}  {text}", ConsoleStyle.INFO_MSG)
    
    @staticmethod
    def process(text: str) -> str:
        """Stylizuj komunikat procesu"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return ConsoleStyle.colorize(f"{ConsoleStyle.PROCESSING}  {text}", ConsoleStyle.PROCESS_MSG)
    
    @staticmethod
    def section(title: str) -> str:
        """Stylizuj tytuł sekcji"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return ConsoleStyle.colorize(f"\n{title}", ConsoleStyle.HEADER + ConsoleStyle.BOLD)
    
    @staticmethod
    def divider(char: str = "=", length: int = 50) -> str:
        """Utwórz separator"""
        if ConsoleStyle.QUIET_MODE:
            return None
        return char * length
    
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 40, prefix: str = "Postęp") -> str:
        """Utwórz pasek postępu"""
        if total == 0 or ConsoleStyle.QUIET_MODE:
            return ""
        
        percentage = current / total
        filled = int(width * percentage)
        bar = "█" * filled + "░" * (width - filled)
        percentage_text = f"{percentage:.1%}"
        
        return f"{prefix}: [{bar}] {percentage_text} ({current}/{total})"
    
    @staticmethod
    def print_progress(current: int, total: int, prefix: str = "Postęp"):
        """Wyświetl pasek postępu"""
        if total > 0 and not ConsoleStyle.QUIET_MODE:
            progress = ConsoleStyle.progress_bar(current, total, prefix=prefix)
            print(f"\r{progress}", end="", flush=True)
            if current == total:
                print()  # Nowa linia na końcu
    
    @staticmethod
    def print_stats(stats_dict: Dict[str, Any], title: str = "Statystyki"):
        """Wyświetl statystyki w ładnej tabeli"""
        if ConsoleStyle.QUIET_MODE or not stats_dict:
            return
        
        print(ConsoleStyle.section(title))
        max_key_length = max(len(str(key)) for key in stats_dict.keys())
        
        for key, value in stats_dict.items():
            key_padded = str(key).ljust(max_key_length)
            print(f"  {key_padded}: {value}")
        print()
    
    @staticmethod
    def print_section(title: str, content: str = ""):
        """Wyświetl sekcję z tytułem i opcjonalną zawartością"""
        if ConsoleStyle.QUIET_MODE:
            return
        
        print(ConsoleStyle.section(title))
        if content:
            print(content)
        print(ConsoleStyle.divider())
    
    @staticmethod
    def print_summary(success_count: int, total_count: int, errors: list = None):
        """Wyświetl podsumowanie operacji"""
        if ConsoleStyle.QUIET_MODE:
            return
        
        stats = {
            "Sukces": f"{success_count}/{total_count}",
            "Niepowodzenia": total_count - success_count,
            "Procent sukcesu": f"{(success_count/total_count*100):.1f}%" if total_count > 0 else "0%"
        }
        ConsoleStyle.print_stats(stats, "PODSUMOWANIE")
        
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


def print_header(title: str, version: str = ""):
    """Wyświetl nagłówek aplikacji"""
    if ConsoleStyle.QUIET_MODE:
        return
    
    print(ConsoleStyle.section(title))
    if version:
        print(ConsoleStyle.info(f"Wersja: {version}"))
    print(ConsoleStyle.divider())


def print_usage(script_name: str, examples: list, description: str = ""):
    """Wyświetl informacje o użyciu skryptu"""
    if ConsoleStyle.QUIET_MODE:
        return
    
    print(ConsoleStyle.error(f"Nieprawidłowe użycie: {script_name}"))
    if description:
        print(ConsoleStyle.info(description))
    
    print(ConsoleStyle.section("Przykłady użycia:"))
    for example in examples:
        print(f"  {example}")
    print()


def print_verification_results(results: Dict[str, Any]):
    """Wyświetl wyniki weryfikacji"""
    if ConsoleStyle.QUIET_MODE:
        return
    
    print(ConsoleStyle.section("WERYFIKACJA PROJEKTU"))
    print(ConsoleStyle.divider())
    
    # Statystyki ogólne
    stats = {
        "Znaki drogowe": results.get('total_signs', 0),
        "Kategorie": results.get('categories', 0),
        "Pliki bloków": results.get('block_files', 0),
        "Tekstury": results.get('textures', 0),
        "Modele 3D": results.get('models', 0),
        "Tłumaczenia": results.get('translations', 0)
    }
    ConsoleStyle.print_stats(stats, "STATYSTYKI OGÓLNE")
    
    # Problemy
    issues = results.get('issues', {})
    if issues:
        print(ConsoleStyle.error("WYKRYTE PROBLEMY:"))
        for issue_type, count in issues.items():
            if count > 0:
                print(f"  ❌ {issue_type}: {count}")
    else:
        print(ConsoleStyle.success("Nie wykryto problemów!"))
    
    print(ConsoleStyle.divider())


def print_build_info(build_type: str, output_path: str, file_size: str = ""):
    """Wyświetl informacje o budowaniu"""
    if ConsoleStyle.QUIET_MODE:
        return
    
    print(ConsoleStyle.section(f"BUDOWANIE {build_type.upper()}"))
    print(ConsoleStyle.divider())
    print(ConsoleStyle.success(f"Utworzono: {output_path}"))
    if file_size:
        print(ConsoleStyle.info(f"Rozmiar: {file_size}"))
    print(ConsoleStyle.divider())


def print_installation_info(pack_name: str, install_path: str):
    """Wyświetl informacje o instalacji"""
    if ConsoleStyle.QUIET_MODE:
        return
    
    print(ConsoleStyle.section("INSTALACJA"))
    print(ConsoleStyle.divider())
    print(ConsoleStyle.success(f"Zainstalowano: {pack_name}"))
    print(ConsoleStyle.info(f"Lokalizacja: {install_path}"))
    print(ConsoleStyle.divider()) 