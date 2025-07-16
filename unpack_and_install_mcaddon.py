#!/usr/bin/env python3
import os
import zipfile
import glob
import shutil

# Paths
DIST_DIR = 'dist'
MINECRAFT_DIR = os.path.expanduser('~/Library/Application Support/mcpelauncher/games/com.mojang')
BP_TARGET = os.path.join(MINECRAFT_DIR, 'behavior_packs')
RP_TARGET = os.path.join(MINECRAFT_DIR, 'resource_packs')

# Find latest .mcaddon
mcaddons = sorted(glob.glob(os.path.join(DIST_DIR, '*.mcaddon')))
if not mcaddons:
    print('Brak plików .mcaddon w katalogu dist/')
    exit(1)
latest = mcaddons[-1]
print(f'Najbardziej aktualna paczka: {latest}')

# Extract plugin name from filename (e.g., "PolishRoadSigns_v1.0.29_20250716_224949.mcaddon" -> "PolishRoadSigns")
plugin_name = os.path.basename(latest).split('_v')[0]
print(f'Nazwa paczki: {plugin_name}')

# Unpack
unpack_dir = 'unpacked_mcaddon'
if os.path.exists(unpack_dir):
    shutil.rmtree(unpack_dir)
os.makedirs(unpack_dir, exist_ok=True)
with zipfile.ZipFile(latest, 'r') as zip_ref:
    zip_ref.extractall(unpack_dir)
print(f'Rozpakowano do: {unpack_dir}')

# Copy BP and RP with plugin name
for folder, target in [('BP', BP_TARGET), ('RP', RP_TARGET)]:
    src = os.path.join(unpack_dir, folder)
    if os.path.exists(src):
        dst = os.path.join(target, plugin_name)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f'Skopiowano {src} do {dst}')
    else:
        print(f'Brak folderu {src} w paczce!')

print(f'Gotowe! BP i RP są wgrane do Minecraft jako {plugin_name}.') 
