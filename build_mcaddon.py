#!/usr/bin/env python3
import os
import json
import shutil
import zipfile
from datetime import datetime


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


def build_mcaddon():
    """Build the .mcaddon package"""

    # Read current versions and names
    bp_name, bp_version = read_manifest('BP/manifest.json')
    rp_name, rp_version = read_manifest('RP/manifest.json')

    print(f"Current BP version: {bp_version}")
    print(f"Current RP version: {rp_version}")

    # Use the same version for both BP and RP
    new_version = bump_version(bp_version.copy())

    print(f"New version (both BP and RP): {new_version}")

    # Update manifests with same version
    update_version('BP/manifest.json', new_version)
    update_version('RP/manifest.json', new_version)

    # Extract plugin name from BP manifest (remove " BP" suffix and spaces)
    plugin_name = bp_name.replace(" BP", "").replace(" ", "")
    print(f"Plugin name: {plugin_name}")

    # Create output directory
    output_dir = 'dist'
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Create .mcaddon file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mcaddon_name = f"{plugin_name}_v{new_version[0]}.{new_version[1]}.{new_version[2]}_{timestamp}.mcaddon"
    mcaddon_path = os.path.join(output_dir, mcaddon_name)

    print(f"Creating {mcaddon_path}...")

    with zipfile.ZipFile(mcaddon_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add BP files
        for root, dirs, files in os.walk('BP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)
                print(f"  Added: {arc_name}")

        # Add RP files
        for root, dirs, files in os.walk('RP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)
                print(f"  Added: {arc_name}")

    print(f"\nPackage created successfully: {mcaddon_path}")
    print(f"File size: {os.path.getsize(mcaddon_path) / 1024 / 1024:.2f} MB")

    return mcaddon_path


if __name__ == "__main__":
    build_mcaddon()
