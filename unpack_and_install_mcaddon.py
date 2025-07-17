import os
import sys
import zipfile
import shutil
from pathlib import Path

# Try to auto-detect Minecraft com.mojang folder (works for Windows, macOS)
def get_minecraft_dir():
    home = str(Path.home())
    # macOS
    mac_path = os.path.join(home, "Library/Application Support/minecraftpe")
    if os.path.exists(mac_path):
        return mac_path
    # Windows
    win_path = os.path.join(home, "AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang")
    if os.path.exists(win_path):
        return win_path
    # Linux/Android (user must specify)
    return None

def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.mcaddon'):
        print("Usage: python unpack_and_install_mcaddon.py <file.mcaddon>")
        sys.exit(1)
    mcaddon = sys.argv[1]
    if not os.path.isfile(mcaddon):
        print(f"File not found: {mcaddon}")
        sys.exit(1)
    mc_dir = get_minecraft_dir()
    if not mc_dir:
        print("Could not auto-detect Minecraft com.mojang folder. Please copy the packs manually.")
        sys.exit(1)
    with zipfile.ZipFile(mcaddon, 'r') as zf:
        for member in zf.namelist():
            if member.startswith('BP/'):
                out_dir = os.path.join(mc_dir, 'behavior_packs', 'PolishRoadSigns')
                rel_path = os.path.relpath(member, 'BP')
            elif member.startswith('RP/'):
                out_dir = os.path.join(mc_dir, 'resource_packs', 'PolishRoadSigns')
                rel_path = os.path.relpath(member, 'RP')
            else:
                continue
            target_path = os.path.join(out_dir, rel_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as src, open(target_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
    print(f"Installed to {mc_dir}/behavior_packs/PolishRoadSigns and resource_packs/PolishRoadSigns")

if __name__ == "__main__":
    main() 