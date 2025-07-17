#!/usr/bin/env python3
import json
import os
import re
from collections import defaultdict

def get_png_files():
    """Get all PNG files from texture directories"""
    png_files = {}
    
    for category in ['a', 'b', 'c', 'd']:
        texture_dir = f'RP/textures/blocks/{category}'
        if os.path.exists(texture_dir):
            png_files[category] = []
            for filename in os.listdir(texture_dir):
                if filename.endswith('.png'):
                    png_files[category].append(filename.replace('.png', ''))
    
    return png_files

def get_block_files():
    """Get all block files from BP/blocks"""
    block_files = {}
    
    for category in ['a', 'b', 'c', 'd']:
        category_path = f'BP/blocks/{category}'
        if os.path.exists(category_path):
            block_files[category] = []
            for filename in os.listdir(category_path):
                if filename.endswith('.block.json'):
                    block_files[category].append(filename.replace('.block.json', ''))
    
    return block_files

def get_texture_database():
    """Get texture database from terrain_texture.json"""
    try:
        with open('RP/textures/terrain_texture.json', 'r', encoding='utf-8') as f:
            terrain_data = json.load(f)
        return terrain_data['texture_data']
    except Exception as e:
        print(f"Error reading terrain_texture.json: {e}")
        return {}

def get_sign_types():
    """Get sign types and their characteristics"""
    sign_types = {
        'a': {'shape': 'triangle', 'back_texture': 'triangle_back', 'description': 'Warning signs (triangles)'},
        'b': {'shape': 'circle', 'back_texture': 'circle_back', 'description': 'Prohibition signs (circles)'},
        'c': {'shape': 'circle', 'back_texture': 'circle_back', 'description': 'Mandatory signs (circles)'},
        'd': {'shape': 'rectangle_horizontal', 'back_texture': 'rectangle_horizontal_back', 'description': 'Information signs (rectangles)'}
    }
    return sign_types

def get_file_sizes():
    """Get file sizes of PNG files"""
    file_sizes = {}
    
    for category in ['a', 'b', 'c', 'd']:
        texture_dir = f'RP/textures/blocks/{category}'
        if os.path.exists(texture_dir):
            for filename in os.listdir(texture_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(texture_dir, filename)
                    try:
                        size = os.path.getsize(filepath)
                        texture_name = filename.replace('.png', '')
                        file_sizes[texture_name] = size
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
    
    return file_sizes

def verify_project():
    """Comprehensive project verification"""
    print("=== POLISH ROAD SIGNS PROJECT VERIFICATION ===\n")
    
    # Get data
    png_files = get_png_files()
    block_files = get_block_files()
    texture_db = get_texture_database()
    sign_types = get_sign_types()
    file_sizes = get_file_sizes()
    
    # Statistics
    total_png = sum(len(files) for files in png_files.values())
    total_blocks = sum(len(files) for files in block_files.values())
    total_textures_in_db = len(texture_db)
    
    print(f"📊 STATISTICS:")
    print(f"   PNG files: {total_png}")
    print(f"   Block files: {total_blocks}")
    print(f"   Textures in database: {total_textures_in_db}")
    print()
    
    # Sign types information
    print("🚦 SIGN TYPES:")
    for category, info in sign_types.items():
        print(f"   Category {category.upper()}: {info['description']}")
        print(f"     Shape: {info['shape']}")
        print(f"     Back texture: {info['back_texture']}")
    print()
    
    # Category breakdown
    print("📁 CATEGORY BREAKDOWN:")
    for category in ['a', 'b', 'c', 'd']:
        png_count = len(png_files.get(category, []))
        block_count = len(block_files.get(category, []))
        info = sign_types[category]
        
        print(f"   Category {category.upper()}:")
        print(f"     PNG files: {png_count}")
        print(f"     Block files: {block_count}")
        print(f"     Shape: {info['shape']}")
        print(f"     Back texture: {info['back_texture']}")
    print()
    
    # Verification results
    print("🔍 VERIFICATION RESULTS:")
    
    # Check for missing blocks
    missing_blocks = []
    for category in ['a', 'b', 'c', 'd']:
        png_list = png_files.get(category, [])
        block_list = block_files.get(category, [])
        
        for png_name in png_list:
            if png_name not in block_list:
                missing_blocks.append(png_name)
    
    if missing_blocks:
        print(f"   ❌ Missing blocks for {len(missing_blocks)} PNG files:")
        for block in missing_blocks:
            print(f"      - {block}")
    else:
        print("   ✅ All PNG files have corresponding blocks")
    
    # Check for missing textures in database
    missing_textures = []
    for category in ['a', 'b', 'c', 'd']:
        png_list = png_files.get(category, [])
        
        for png_name in png_list:
            if png_name not in texture_db:
                missing_textures.append(png_name)
    
    if missing_textures:
        print(f"   ❌ Missing textures in database for {len(missing_textures)} files:")
        for texture in missing_textures:
            print(f"      - {texture}")
    else:
        print("   ✅ All PNG files have database entries")
    
    # Check for orphaned blocks
    orphaned_blocks = []
    for category in ['a', 'b', 'c', 'd']:
        png_list = png_files.get(category, [])
        block_list = block_files.get(category, [])
        
        for block_name in block_list:
            if block_name not in png_list:
                orphaned_blocks.append(block_name)
    
    if orphaned_blocks:
        print(f"   ⚠️  Orphaned blocks (no PNG): {len(orphaned_blocks)}")
        for block in orphaned_blocks:
            print(f"      - {block}")
    else:
        print("   ✅ No orphaned blocks found")
    
    # Check back textures
    print("\n🎨 BACK TEXTURES:")
    back_textures_needed = set()
    for category in ['a', 'b', 'c', 'd']:
        back_texture = sign_types[category]['back_texture']
        back_textures_needed.add(back_texture)
    
    for back_texture in back_textures_needed:
        if back_texture in texture_db:
            print(f"   ✅ {back_texture}")
        else:
            print(f"   ❌ {back_texture} (missing)")
    
    # Check special textures
    print("\n🔧 SPECIAL TEXTURES:")
    special_textures = ['gray_concrete', 'black_concrete']
    for texture in special_textures:
        if texture in texture_db:
            print(f"   ✅ {texture}")
        else:
            print(f"   ❌ {texture} (missing)")
    
    # File size analysis
    print("\n📏 FILE SIZE ANALYSIS:")
    if file_sizes:
        # Group by size ranges
        size_ranges = {
            'Small (< 5KB)': [],
            'Medium (5-10KB)': [],
            'Large (10-20KB)': [],
            'Very Large (> 20KB)': []
        }
        
        for texture_name, size in file_sizes.items():
            if size < 5000:
                size_ranges['Small (< 5KB)'].append(texture_name)
            elif size < 10000:
                size_ranges['Medium (5-10KB)'].append(texture_name)
            elif size < 20000:
                size_ranges['Large (10-20KB)'].append(texture_name)
            else:
                size_ranges['Very Large (> 20KB)'].append(texture_name)
        
        for range_name, textures in size_ranges.items():
            if textures:
                print(f"   {range_name}: {len(textures)} textures")
                if len(textures) <= 5:  # Show details for small groups
                    for texture in textures:
                        print(f"     - {texture}")
    
    # Summary
    print(f"\n📋 SUMMARY:")
    print(f"   Total PNG files: {total_png}")
    print(f"   Total block files: {total_blocks}")
    print(f"   Missing blocks: {len(missing_blocks)}")
    print(f"   Missing textures in DB: {len(missing_textures)}")
    print(f"   Orphaned blocks: {len(orphaned_blocks)}")
    
    if not missing_blocks and not missing_textures and not orphaned_blocks:
        print("   🎉 Project is consistent!")
    else:
        print("   ⚠️  Project has inconsistencies that need attention.")

if __name__ == "__main__":
    verify_project() 