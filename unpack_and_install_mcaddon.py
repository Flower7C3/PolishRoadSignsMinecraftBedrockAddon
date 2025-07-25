#!/usr/bin/env python3

import os
import sys
import zipfile
import shutil
from pathlib import Path
from console_utils import ConsoleStyle, print_installation_info, print_usage, print_header

# Pack name constant
PACK_NAME = "PolishRoadSigns"


# Try to auto-detect Minecraft com.mojang folder (works for Windows, macOS)
def get_minecraft_dir():
    home = str(Path.home())
    # macOS
    mac_path = os.path.join(home, "Library/Application Support/minecraftpe")
    if os.path.exists(mac_path):
        return mac_path
    # mcpelauncher
    mcpelauncher_path = os.path.join(home, "Library/Application Support/mcpelauncher/games/com.mojang")
    if os.path.exists(mcpelauncher_path):
        return mcpelauncher_path
    # Windows
    win_path = os.path.join(home,
                            "AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang")
    if os.path.exists(win_path):
        return win_path
    # Linux/Android (user must specify)
    return None


def remove_existing_packs(mc_dir):
    """Remove existing PolishRoadSigns packs from the Minecraft directory"""
    bp_dir = os.path.join(mc_dir, 'behavior_packs', PACK_NAME)
    rp_dir = os.path.join(mc_dir, 'resource_packs', PACK_NAME)

    if os.path.exists(bp_dir):
        print(ConsoleStyle.warning(f"Usuwanie istniejącego behavior pack: {bp_dir}"))
        shutil.rmtree(bp_dir)

    if os.path.exists(rp_dir):
        print(ConsoleStyle.warning(f"Usuwanie istniejącego resource pack: {rp_dir}"))
        shutil.rmtree(rp_dir)


def main():
    print_header("INSTALACJA PAKIETU MCADDON")
    
    # Parse command line arguments
    if len(sys.argv) < 2 or not sys.argv[1].endswith('.mcaddon'):
        examples = [
            "python3 unpack_and_install_mcaddon.py PolishRoadSigns_v1.0.0_20231201_120000.mcaddon",
            "python3 unpack_and_install_mcaddon.py PolishRoadSigns_v1.0.0_20231201_120000.mcaddon --clean",
            "python3 unpack_and_install_mcaddon.py PolishRoadSigns_v1.0.0_20231201_120000.mcaddon --no-clean"
        ]
        print_usage("python3 unpack_and_install_mcaddon.py", examples, 
                   "Instaluje pakiety BP i RP do katalogu Minecraft")
        sys.exit(1)

    mcaddon = sys.argv[1]
    clean_existing = True  # Default behavior

    # Check for the "--clean" flag
    if len(sys.argv) > 2:
        if sys.argv[2] == '--clean':
            clean_existing = True
        elif sys.argv[2] == '--no-clean':
            clean_existing = False
        else:
            print(ConsoleStyle.error("Nieznana opcja. Użyj --clean lub --no-clean"))
            sys.exit(1)

    if not os.path.isfile(mcaddon):
        print(ConsoleStyle.error(f"Nie znaleziono pliku: {mcaddon}"))
        sys.exit(1)

    mc_dir = get_minecraft_dir()
    if not mc_dir:
        print(ConsoleStyle.error("Nie można automatycznie wykryć katalogu Minecraft com.mojang. Skopiuj pakiety ręcznie."))
        sys.exit(1)

    print(ConsoleStyle.info(f"Katalog Minecraft: {mc_dir}"))

    # Remove existing packs if requested
    if clean_existing:
        remove_existing_packs(mc_dir)

    # Install new packs
    print(ConsoleStyle.process("Instalowanie nowych pakietów..."))
    file_count = 0
    
    with zipfile.ZipFile(mcaddon, 'r') as zf:
        for member in zf.namelist():
            if member.startswith('BP/'):
                out_dir = os.path.join(mc_dir, 'behavior_packs', PACK_NAME)
                rel_path = os.path.relpath(member, 'BP')
            elif member.startswith('RP/'):
                out_dir = os.path.join(mc_dir, 'resource_packs', PACK_NAME)
                rel_path = os.path.relpath(member, 'RP')
            else:
                continue
            target_path = os.path.join(out_dir, rel_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as src, open(target_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            file_count += 1

    print(ConsoleStyle.success(f"Zainstalowano {file_count} plików"))
    print_installation_info(PACK_NAME, mc_dir)


if __name__ == "__main__":
    main()
