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

def build_mcpack():
    """Build separate .mcpack files for BP and RP"""
    
    # Read current versions and names
    bp_name, bp_version = read_manifest('BP/manifest.json')
    rp_name, rp_version = read_manifest('RP/manifest.json')
    
    print(f"BP version: {bp_version}")
    print(f"RP version: {rp_version}")
    
    # Create output directory
    output_dir = 'dist'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Build BP .mcpack
    bp_plugin_name = bp_name.replace(" BP", "").replace(" ", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bp_mcpack_name = f"{bp_plugin_name}_BP_v{bp_version[0]}.{bp_version[1]}.{bp_version[2]}_{timestamp}.mcpack"
    bp_mcpack_path = os.path.join(output_dir, bp_mcpack_name)
    
    print(f"Creating BP: {bp_mcpack_path}...")
    
    with zipfile.ZipFile(bp_mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('BP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)
                print(f"  Added: {arc_name}")
    
    print(f"BP created: {bp_mcpack_path}")
    print(f"BP size: {os.path.getsize(bp_mcpack_path) / 1024:.2f} KB")
    
    # Build RP .mcpack
    rp_plugin_name = rp_name.replace(" RP", "").replace(" ", "")
    rp_mcpack_name = f"{rp_plugin_name}_RP_v{rp_version[0]}.{rp_version[1]}.{rp_version[2]}_{timestamp}.mcpack"
    rp_mcpack_path = os.path.join(output_dir, rp_mcpack_name)
    
    print(f"Creating RP: {rp_mcpack_path}...")
    
    with zipfile.ZipFile(rp_mcpack_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('RP'):
            for file in files:
                if file.endswith('.DS_Store'):
                    continue
                file_path = os.path.join(root, file)
                arc_name = file_path
                zipf.write(file_path, arc_name)
                print(f"  Added: {arc_name}")
    
    print(f"RP created: {rp_mcpack_path}")
    print(f"RP size: {os.path.getsize(rp_mcpack_path) / 1024:.2f} KB")
    
    print(f"\nBoth .mcpack files created successfully!")
    print(f"Upload these files to your Aternos server:")
    print(f"1. {bp_mcpack_name}")
    print(f"2. {rp_mcpack_name}")
    
    return bp_mcpack_path, rp_mcpack_path

if __name__ == "__main__":
    build_mcpack() 