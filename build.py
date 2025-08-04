#!/usr/bin/env python3
"""
Build Script for Minecraft Bedrock Addon
"""

import os
import json
import shutil
import zipfile
import argparse
from datetime import datetime
from pathlib import Path
from console_utils import ConsoleStyle

# Pack name from directory name
PACK_NAME = os.path.basename(os.getcwd()).replace(" ", "_").replace("-", "_").lower()


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
    """Remove existing packs from the Minecraft directory"""
    bp_dir = os.path.join(mc_dir, 'behavior_packs', PACK_NAME)
    rp_dir = os.path.join(mc_dir, 'resource_packs', PACK_NAME)

    if os.path.exists(bp_dir):
        print(ConsoleStyle.delete(f"Removing existing behavior pack: {bp_dir}"))
        shutil.rmtree(bp_dir)

    if os.path.exists(rp_dir):
        print(ConsoleStyle.delete(f"Removing existing resource pack: {rp_dir}"))
        shutil.rmtree(rp_dir)


def install_mcaddon(mcaddon_path, clean_existing=True):
    """Install .mcaddon file to the local Minecraft directory"""
    mc_dir = get_minecraft_dir()
    if not mc_dir:
        print(ConsoleStyle.error("Cannot auto-detect Minecraft com.mojang directory. Installation failed."))
        return False

    print(ConsoleStyle.info(f"Minecraft directory [{mc_dir}]"))

    # Remove existing packs if requested
    if clean_existing:
        remove_existing_packs(mc_dir)

    # Install new packs
    print(ConsoleStyle.process("Installing new packs..."))
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

    print(ConsoleStyle.success(f"Installed [{file_count}] files"))
    ConsoleStyle.print_installation_info(PACK_NAME, mc_dir)
    return True


def read_manifest(file_path):
    """Read manifest file and return name and version"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['header']['name'], data['header']['version']


def bump_version(version):
    """Bump patch version"""
    new_version = version.copy()
    new_version[2] += 1
    return new_version


def update_version(file_path, new_version):
    """Update version in manifest file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data['header']['version'] = new_version

    # Update all module versions
    for module in data.get('modules', []):
        if 'version' in module:
            module['version'] = new_version

    # Update all dependency versions EXCEPT @minecraft/server
    for dependency in data.get('dependencies', []):
        if 'version' in dependency:
            # Don't update @minecraft/server version - keep it as "1.19.0"
            if dependency.get('module_name') != '@minecraft/server':
                dependency['version'] = new_version

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_mcaddon(bp_version, rp_version, plugin_name, output_dir, timestamp, simplify_name):
    """Build the .mcaddon package"""
    if simplify_name:
        mcaddon_name = f"{plugin_name}.mcaddon"
    else:
        mcaddon_name = f"{plugin_name}-v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}_{timestamp}.mcaddon"
    mcaddon_path = os.path.join(output_dir, mcaddon_name)

    print(ConsoleStyle.process(f"Building {mcaddon_name}..."))

    with zipfile.ZipFile(mcaddon_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add BP files
        for root, dirs, files in os.walk('BP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)

        # Add RP files
        for root, dirs, files in os.walk('RP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)

    mcaddon_size = os.path.getsize(mcaddon_path) / 1024 / 1024
    ConsoleStyle.print_build_info("MCADDON", mcaddon_path, f"{mcaddon_size:.2f} MB")

    return mcaddon_path, mcaddon_size


def build_mcpack(bp_version, rp_version, bp_plugin_name, rp_plugin_name, output_dir, timestamp, simplify_name):
    """Build separate .mcpack files for BP and RP"""

    # Build BP .mcpack
    if simplify_name:
        bp_mcpack_name = f"{bp_plugin_name}.mcpack"
    else:
        bp_mcpack_name = f"{bp_plugin_name}-v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}_{timestamp}.mcpack"
    bp_mcpack_path = os.path.join(output_dir, bp_mcpack_name)

    print(ConsoleStyle.process(f"Building {bp_mcpack_name}..."))

    with zipfile.ZipFile(bp_mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('BP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)

    bp_size = os.path.getsize(bp_mcpack_path) / 1024 / 1024
    ConsoleStyle.print_build_info("BP MCPACK", bp_mcpack_path, f"{bp_size:.2f} MB")

    # Build RP .mcpack
    if simplify_name:
        rp_mcpack_name = f"{rp_plugin_name}.mcpack"
    else:
        rp_mcpack_name = f"{rp_plugin_name}_v{rp_version[0]}.{rp_version[1]}.{rp_version[2]}_{timestamp}.mcpack"
    rp_mcpack_path = os.path.join(output_dir, rp_mcpack_name)

    print(ConsoleStyle.process(f"Building {rp_mcpack_path}..."))

    with zipfile.ZipFile(rp_mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('RP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)

    rp_size = os.path.getsize(rp_mcpack_path) / 1024 / 1024
    ConsoleStyle.print_build_info("RP MCPACK", rp_mcpack_path, f"{rp_size:.2f} MB")

    return bp_mcpack_path, rp_mcpack_path, bp_size, rp_size


def count_files():
    """Count total files in BP and RP directories"""
    file_count = 0
    for root, dirs, files in os.walk("BP"):
        file_count += len(files)
    for root, dirs, files in os.walk("RP"):
        file_count += len(files)
    return file_count


def main():
    """Main build function"""
    parser = argparse.ArgumentParser(description=f"Build {PACK_NAME} Minecraft Addon",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
examples:
  python3 build.py --mcaddon
  python3 build.py --all --test-on-local
  python3 build.py --mcpack --no-bump
                                     """
                                     )
    parser.add_argument("--mcaddon", '-a', action="store_true", help="build .mcaddon package")
    parser.add_argument("--mcpack", '-p', action="store_true", help="build separate .mcpack packages")
    parser.add_argument("--all", action="store_true", help="build all package types")
    parser.add_argument("--no-bump", '-n', action="store_true", help="don't bump version")
    parser.add_argument("--test-on-local", '-t', action="store_true", help="install to local Minecraft after building")
    parser.add_argument('--no-clean', '-c', action='store_true',
                        help='do not clean old packages before installation (only with --test-on-local)')
    parser.add_argument('--simplify-name', '-s', action='store_true',
                        help='simplify package file name (do not append version and timestamp)')
    parser.add_argument("--output", '-o', default="dist", help="output directory")

    args = parser.parse_args()

    if not any([args.mcaddon, args.mcpack, args.all]):
        parser.print_help()
        return

    ConsoleStyle.print_section("BUILDING MINECRAFT PACKAGES", icon="🏗️")

    # Read current versions and names
    bp_name, bp_version = read_manifest('BP/manifest.json')
    rp_name, rp_version = read_manifest('RP/manifest.json')

    print(ConsoleStyle.info(f"BP: {bp_name} v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}"))
    print(ConsoleStyle.info(f"RP: {rp_name} v{rp_version[0]}.{rp_version[1]}.{rp_version[2]}"))

    # Bump version if requested
    if not args.no_bump:
        print(ConsoleStyle.process("Bumping version..."))
        new_bp_version = bump_version(bp_version.copy())
        new_rp_version = bump_version(rp_version.copy())

        update_version("BP/manifest.json", new_bp_version)
        update_version("RP/manifest.json", new_rp_version)

        bp_version = new_bp_version
        rp_version = new_rp_version
        print(ConsoleStyle.success(f"Version bumped to [{bp_version[0]}.{bp_version[1]}.{bp_version[2]}]"))

    # Create an output directory
    output_dir = 'dist'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build requested formats
    mcaddon_path = None
    bp_mcpack_path = None
    rp_mcpack_path = None

    if args.mcaddon or args.all:
        mcaddon_path, mcaddon_size = build_mcaddon(bp_version, rp_version, PACK_NAME, args.output, timestamp,
                                                   args.simplify_name)

    if args.mcpack or args.all:
        bp_mcpack_path, rp_mcpack_path, bp_size, rp_size = build_mcpack(
            bp_version, rp_version, f"{PACK_NAME}_BP", f"{PACK_NAME}_RP", args.output, timestamp, args.simplify_name
        )

    stats = {
        "📦Total files": count_files()
    }
    if mcaddon_path:
        stats["📦 .mcaddon"] = os.path.basename(mcaddon_path)
    if bp_mcpack_path and rp_mcpack_path:
        stats["📦 .mcpack"] = f"{os.path.basename(bp_mcpack_path)}, {os.path.basename(rp_mcpack_path)}"
    ConsoleStyle.print_stats(stats, "BUILD SUMMARY")

    # Install to local Minecraft if requested
    if args.test_on_local:
        ConsoleStyle.print_section("INSTALLATION", "")
        print(ConsoleStyle.process("Installing to local Minecraft..."))
        clean_existing = not args.no_clean
        if install_mcaddon(mcaddon_path, clean_existing):
            print(ConsoleStyle.success("Installation completed successfully!"))
        else:
            print(ConsoleStyle.error("Installation failed!"))

    print(ConsoleStyle.success("Build completed successfully!"))


if __name__ == "__main__":
    main()
