import os
import sys
import zipfile
import shutil
from pathlib import Path

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
    win_path = os.path.join(home, "AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang")
    if os.path.exists(win_path):
        return win_path
    # Linux/Android (user must specify)
    return None

def remove_existing_packs(mc_dir):
    """Remove existing PolishRoadSigns packs from Minecraft directory"""
    bp_dir = os.path.join(mc_dir, 'behavior_packs', PACK_NAME)
    rp_dir = os.path.join(mc_dir, 'resource_packs', PACK_NAME)
    
    if os.path.exists(bp_dir):
        print(f"Removing existing behavior pack: {bp_dir}")
        shutil.rmtree(bp_dir)
    
    if os.path.exists(rp_dir):
        print(f"Removing existing resource pack: {rp_dir}")
        shutil.rmtree(rp_dir)

def main():
    # Parse command line arguments
    if len(sys.argv) < 2 or not sys.argv[1].endswith('.mcaddon'):
        print("Usage: python unpack_and_install_mcaddon.py <file.mcaddon> [--clean]")
        print("  --clean: Remove existing packs before installing (default: True)")
        sys.exit(1)
    
    mcaddon = sys.argv[1]
    clean_existing = True  # Default behavior
    
    # Check for --clean flag
    if len(sys.argv) > 2:
        if sys.argv[2] == '--clean':
            clean_existing = True
        elif sys.argv[2] == '--no-clean':
            clean_existing = False
        else:
            print("Unknown option. Use --clean or --no-clean")
            sys.exit(1)
    
    if not os.path.isfile(mcaddon):
        print(f"File not found: {mcaddon}")
        sys.exit(1)
    
    mc_dir = get_minecraft_dir()
    if not mc_dir:
        print("Could not auto-detect Minecraft com.mojang folder. Please copy the packs manually.")
        sys.exit(1)
    
    # Remove existing packs if requested
    if clean_existing:
        remove_existing_packs(mc_dir)
    
    # Install new packs
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
    
    print(f"Installed to {mc_dir}/behavior_packs/{PACK_NAME} and resource_packs/{PACK_NAME}")

if __name__ == "__main__":
    main() 