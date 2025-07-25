#!/usr/bin/env python3
import os
import json
import shutil
import zipfile
import sys
import argparse
from datetime import datetime
from pathlib import Path
from console_utils import ConsoleStyle, print_build_info, print_header, print_usage, print_installation_info


# Pack name constant
PACK_NAME = "PolishRoadSigns"


def get_minecraft_dir():
    """Try to auto-detect Minecraft com.mojang folder"""
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


def install_mcaddon(mcaddon_path, clean_existing=True):
    """Install .mcaddon file to local Minecraft directory"""
    mc_dir = get_minecraft_dir()
    if not mc_dir:
        print(ConsoleStyle.error("Nie można automatycznie wykryć katalogu Minecraft com.mojang. Instalacja nie powiodła się."))
        return False

    print(ConsoleStyle.info(f"Katalog Minecraft: {mc_dir}"))

    # Remove existing packs if requested
    if clean_existing:
        remove_existing_packs(mc_dir)

    # Install new packs
    print(ConsoleStyle.process("Instalowanie nowych pakietów..."))
    file_count = 0
    
    with zipfile.ZipFile(mcaddon_path, 'r') as zf:
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
    return True


def read_manifest(file_path):
    """Read manifest file and return name and version"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['header']['name'], data['header']['version']


def bump_version(version):
    """Bump patch version"""
    version[2] += 1
    return version


def update_version(file_path, new_version):
    """Update version in manifest file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update header version
    data['header']['version'] = new_version

    # Update all module versions
    for module in data.get('modules', []):
        if 'version' in module:
            module['version'] = new_version

    # Update all dependency versions
    for dependency in data.get('dependencies', []):
        if 'version' in dependency:
            dependency['version'] = new_version

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_mcaddon(bp_version, rp_version, plugin_name, output_dir, timestamp):
    """Build the .mcaddon package"""
    mcaddon_name = f"{plugin_name}_v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}_{timestamp}.mcaddon"
    mcaddon_path = os.path.join(output_dir, mcaddon_name)

    print(ConsoleStyle.process(f"Tworzenie {mcaddon_path}..."))

    file_count = 0
    with zipfile.ZipFile(mcaddon_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add BP files
        for root, dirs, files in os.walk('BP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)
                file_count += 1

        # Add RP files
        for root, dirs, files in os.walk('RP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)
                file_count += 1

    file_size = os.path.getsize(mcaddon_path) / 1024 / 1024
    print_build_info("MCADDON", mcaddon_path, f"{file_size:.2f} MB")
    print(ConsoleStyle.info(f"Liczba plików: {file_count}"))

    return mcaddon_path


def build_mcpack(bp_version, rp_version, bp_name, rp_name, output_dir, timestamp):
    """Build separate .mcpack files for BP and RP"""
    # Build BP .mcpack
    bp_plugin_name = bp_name.replace(" BP", "").replace(" ", "")
    bp_mcpack_name = f"{bp_plugin_name}_BP_v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}_{timestamp}.mcpack"
    bp_mcpack_path = os.path.join(output_dir, bp_mcpack_name)

    print(ConsoleStyle.process(f"Tworzenie BP: {bp_mcpack_path}..."))

    with zipfile.ZipFile(bp_mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('BP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)

    print(ConsoleStyle.success(f"BP utworzony: {bp_mcpack_path}"))
    print(ConsoleStyle.info(f"Rozmiar BP: {os.path.getsize(bp_mcpack_path) / 1024:.2f} KB"))

    # Build RP .mcpack
    rp_plugin_name = rp_name.replace(" RP", "").replace(" ", "")
    rp_mcpack_name = f"{rp_plugin_name}_RP_v{rp_version[0]}.{rp_version[1]}.{rp_version[2]}_{timestamp}.mcpack"
    rp_mcpack_path = os.path.join(output_dir, rp_mcpack_name)

    print(ConsoleStyle.process(f"Tworzenie RP: {rp_mcpack_path}..."))

    with zipfile.ZipFile(rp_mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('RP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)

    print(ConsoleStyle.success(f"RP utworzony: {rp_mcpack_path}"))
    print(ConsoleStyle.info(f"Rozmiar RP: {os.path.getsize(rp_mcpack_path) / 1024:.2f} KB"))

    return bp_mcpack_path, rp_mcpack_path


def main():
    """Main build function"""
    parser = argparse.ArgumentParser(
        description="Buduje pakiety Minecraft (.mcaddon i/lub .mcpack)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python3 build.py --mcaddon                    # Buduje tylko .mcaddon
  python3 build.py --mcpack                     # Buduje tylko .mcpack
  python3 build.py --all                        # Buduje oba formaty
  python3 build.py --all --no-bump              # Buduje bez zwiększania wersji
  python3 build.py --mcaddon --test-on-local    # Buduj i przetestuj lokalnie
  python3 build.py --all --test-on-local        # Buduj wszystko i przetestuj
  python3 build.py --help                       # Wyświetla pomoc
        """
    )
    
    parser.add_argument('--mcaddon', action='store_true', 
                       help='Buduj pakiet .mcaddon')
    parser.add_argument('--mcpack', action='store_true', 
                       help='Buduj pakiety .mcpack (BP i RP)')
    parser.add_argument('--all', action='store_true', 
                       help='Buduj wszystkie formaty')
    parser.add_argument('--no-bump', action='store_true', 
                       help='Nie zwiększaj wersji (użyj obecnej)')
    parser.add_argument('--test-on-local', action='store_true',
                       help='Automatycznie zainstaluj i przetestuj lokalnie')
    parser.add_argument('--no-clean', action='store_true',
                       help='Nie usuwaj starych pakietów przed instalacją (tylko z --test-on-local)')
    
    args = parser.parse_args()
    
    # Sprawdź, czy podano jakąś opcję
    if not any([args.mcaddon, args.mcpack, args.all]):
        parser.print_help()
        return

    print_header("BUDOWANIE PAKIETÓW MINECRAFT")

    # Read current versions and names
    bp_name, bp_version = read_manifest('BP/manifest.json')
    rp_name, rp_version = read_manifest('RP/manifest.json')

    print(ConsoleStyle.info(f"Obecna wersja BP: {bp_version}"))
    print(ConsoleStyle.info(f"Obecna wersja RP: {rp_version}"))

    # Determine new version
    if args.no_bump:
        new_version = bp_version.copy()
        print(ConsoleStyle.info(f"Używam obecnej wersji: {new_version}"))
    else:
        new_version = bump_version(bp_version.copy())
        print(ConsoleStyle.info(f"Nowa wersja: {new_version}"))
        
        # Update manifests with new version
        update_version('BP/manifest.json', new_version)
        update_version('RP/manifest.json', new_version)

    # Extract plugin name
    plugin_name = bp_name.replace(" BP", "").replace(" ", "")
    print(ConsoleStyle.info(f"Nazwa pluginu: {plugin_name}"))

    # Create output directory
    output_dir = 'dist'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build requested formats
    mcaddon_path = None
    if args.mcaddon or args.all:
        mcaddon_path = build_mcaddon(new_version, new_version, plugin_name, output_dir, timestamp)

    if args.mcpack or args.all:
        build_mcpack(new_version, new_version, bp_name, rp_name, output_dir, timestamp)

    # Install for local testing if requested
    if args.test_on_local and mcaddon_path:
        print(ConsoleStyle.divider())
        print(ConsoleStyle.section("TESTOWANIE LOKALNE"))
        
        clean_existing = not args.no_clean
        if install_mcaddon(mcaddon_path, clean_existing):
            print(ConsoleStyle.success("✅ Pakiet zainstalowany i gotowy do testowania!"))
            print(ConsoleStyle.info("Uruchom Minecraft i sprawdź nowe znaki drogowe"))
        else:
            print(ConsoleStyle.error("❌ Instalacja nie powiodła się"))

    print(ConsoleStyle.divider())
    print(ConsoleStyle.success("Budowanie zakończone pomyślnie!"))


if __name__ == "__main__":
    main() 