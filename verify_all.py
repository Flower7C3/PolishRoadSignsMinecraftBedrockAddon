#!/usr/bin/env python3
import os
import json
from PIL import Image
import re
from collections import defaultdict

def get_texture_dimensions(texture_path):
    """Pobierz wymiary tekstury"""
    try:
        with Image.open(texture_path) as img:
            return img.size[0], img.size[1]
    except Exception as e:
        return None, None

def get_model_dimensions(model_path):
    """Pobierz wymiary modelu z pliku .geo.json"""
    try:
        with open(model_path, 'r', encoding='utf-8') as f:
            model_data = json.load(f)
        
        # Sprawdź wymiary UV w modelu
        if 'minecraft:geometry' in model_data and isinstance(model_data['minecraft:geometry'], list) and len(model_data['minecraft:geometry']) > 0:
            geometry = model_data['minecraft:geometry'][0]
            if 'description' in geometry:
                description = geometry['description']
                if 'texture_width' in description and 'texture_height' in description:
                    return description['texture_width'], description['texture_height']
        
        return None, None
    except Exception as e:
        return None, None

def find_similar_model(model_name, available_models):
    """Znajdź podobny model jeśli dokładny nie istnieje"""
    if model_name in available_models:
        return model_name
    
    # Próbuj znaleźć podobny model
    base_name = model_name.split('_')[0]  # np. "road_sign_rectangle"
    for available_model in available_models:
        if available_model.startswith(base_name):
            return available_model
    
    return None

def verify_geometry_texture_compatibility():
    """Weryfikuj kompatybilność geometrii z wymiarami tekstur"""
    print("\n🔍 GEOMETRY-TEXTURE COMPATIBILITY")
    print("=" * 40)
    
    # Wczytaj terrain_texture.json
    with open('RP/textures/terrain_texture.json', 'r', encoding='utf-8') as f:
        terrain_data = json.load(f)
    
    # Wczytaj wszystkie modele
    models_dir = "RP/models/blocks"
    model_dimensions = {}
    
    for filename in os.listdir(models_dir):
        if filename.endswith('.geo.json'):
            model_name = filename.replace('.geo.json', '')
            model_path = os.path.join(models_dir, filename)
            width, height = get_model_dimensions(model_path)
            if width and height:
                model_dimensions[model_name] = (width, height)
    
    print(f"✓ Models loaded: {len(model_dimensions)}")
    print(f"  Model dimensions: {', '.join([f'{name}({w}x{h})' for name, (w, h) in model_dimensions.items()])}")
    
    # Sprawdź wszystkie bloki
    compatibility_issues = []
    texture_model_mismatches = []
    missing_models = []
    missing_textures = []
    
    for category in ['a', 'b', 'c', 'd']:
        block_dir = f'BP/blocks/{category}'
        if os.path.exists(block_dir):
            for filename in os.listdir(block_dir):
                if filename.endswith('.block.json'):
                    block_path = os.path.join(block_dir, filename)
                    sign_id = filename.replace('.block.json', '')
                    
                    try:
                        with open(block_path, 'r', encoding='utf-8') as f:
                            block_data = json.load(f)
                        
                        # Sprawdź geometrię
                        geometry_name = None
                        if 'minecraft:geometry' in block_data['minecraft:block']['components']:
                            geometry_name = block_data['minecraft:block']['components']['minecraft:geometry']
                            # Usuń prefix "geometry."
                            model_name = geometry_name.replace('geometry.', '')
                        
                        # Sprawdź teksturę (ignoruj tekstury tła)
                        texture_name = None
                        if 'minecraft:material_instances' in block_data['minecraft:block']['components']:
                            material_instances = block_data['minecraft:block']['components']['minecraft:material_instances']
                            for face, material in material_instances.items():
                                if 'texture' in material:
                                    texture_name = material['texture']
                                    break
                        
                        # Sprawdź wymiary tekstury
                        texture_width, texture_height = None, None
                        if texture_name and texture_name in terrain_data['texture_data']:
                            texture_path = terrain_data['texture_data'][texture_name]['textures']
                            full_texture_path = f"RP/{texture_path}"
                            if os.path.exists(full_texture_path):
                                texture_width, texture_height = get_texture_dimensions(full_texture_path)
                            else:
                                missing_textures.append(f"{sign_id} (texture: {texture_name})")
                        
                        # Sprawdź wymiary modelu
                        model_width, model_height = None, None
                        if model_name:
                            # Sprawdź czy model istnieje lub znajdź podobny
                            actual_model_name = find_similar_model(model_name, model_dimensions.keys())
                            if actual_model_name:
                                model_width, model_height = model_dimensions[actual_model_name]
                                if actual_model_name != model_name:
                                    print(f"    Note: {sign_id} using {actual_model_name} instead of {model_name}")
                            else:
                                missing_models.append(f"{sign_id} (model: {model_name})")
                        
                        # Sprawdź kompatybilność
                        if (texture_width and texture_height and 
                            model_width and model_height and
                            (texture_width != model_width or texture_height != model_height)):
                            texture_model_mismatches.append({
                                'sign_id': sign_id,
                                'texture': f"{texture_width}x{texture_height}",
                                'model': f"{model_width}x{model_height}",
                                'model_name': model_name
                            })
                        
                        # Sprawdź czy blok ma geometrię
                        if not geometry_name:
                            compatibility_issues.append(f"{sign_id} (no geometry)")
                        
                    except Exception as e:
                        compatibility_issues.append(f"{sign_id} (error: {str(e)})")
    
    # Wyświetl wyniki
    print(f"✓ Blocks checked: {len([f for f in os.listdir('BP/blocks/a') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/b') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/c') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/d') if f.endswith('.block.json')])}")
    
    if texture_model_mismatches:
        print(f"  ⚠️  Texture-model mismatches: {len(texture_model_mismatches)}")
        for mismatch in texture_model_mismatches[:10]:  # Pokaż pierwsze 10
            print(f"    {mismatch['sign_id']}: texture {mismatch['texture']} vs model {mismatch['model']} ({mismatch['model_name']})")
        if len(texture_model_mismatches) > 10:
            print(f"    ... and {len(texture_model_mismatches) - 10} more")
    
    if missing_models:
        print(f"  ❌ Missing models: {len(missing_models)}")
        for missing in missing_models[:5]:
            print(f"    {missing}")
        if len(missing_models) > 5:
            print(f"    ... and {len(missing_models) - 5} more")
    
    if missing_textures:
        print(f"  ❌ Missing textures: {len(missing_textures)}")
        for missing in missing_textures[:5]:
            print(f"    {missing}")
        if len(missing_textures) > 5:
            print(f"    ... and {len(missing_textures) - 5} more")
    
    if compatibility_issues:
        print(f"  ❌ Compatibility issues: {len(compatibility_issues)}")
        for issue in compatibility_issues[:5]:
            print(f"    {issue}")
        if len(compatibility_issues) > 5:
            print(f"    ... and {len(compatibility_issues) - 5} more")
    
    if not texture_model_mismatches and not missing_models and not missing_textures and not compatibility_issues:
        print(f"  ✅ All blocks have compatible geometries and textures!")
    
    return len(texture_model_mismatches), len(missing_models), len(missing_textures), len(compatibility_issues)

def verify_textures():
    """Weryfikuj tekstury"""
    print("🔍 TEXTURES")
    print("=" * 30)
    
    # Wczytaj bazę danych
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Wczytaj terrain_texture.json
    with open('RP/textures/terrain_texture.json', 'r', encoding='utf-8') as f:
        terrain_data = json.load(f)
    
    categories = ['A', 'B', 'C', 'D']
    total_found = 0
    total_missing = 0
    dimension_stats = defaultdict(int)
    
    for category in categories:
        signs = data['road_signs'][category]['signs']
        
        for sign_id, sign_data in signs.items():
            # Sprawdź czy tekstura jest w terrain_texture.json
            if sign_id in terrain_data['texture_data']:
                texture_path = terrain_data['texture_data'][sign_id]['textures']
                full_path = f"RP/{texture_path}"
                
                if os.path.exists(full_path):
                    width, height = get_texture_dimensions(full_path)
                    if width and height:
                        total_found += 1
                        dimension_stats[f"{width}x{height}"] += 1
                    else:
                        total_missing += 1
                else:
                    total_missing += 1
            else:
                total_missing += 1
    
    print(f"✓ Found: {total_found}, Missing: {total_missing}")
    print(f"  Dimensions: {', '.join([f'{dim}({count})' for dim, count in sorted(dimension_stats.items())])}")
    
    # Sprawdź wszystkie tekstury w terrain_texture.json i nadmiarowe pliki PNG
    print("\n🔍 TEXTURE FILES VERIFICATION")
    print("=" * 40)
    
    # Sprawdź czy wszystkie tekstury z terrain_texture.json istnieją
    terrain_textures_found = 0
    terrain_textures_missing = 0
    missing_textures = []
    
    for texture_id, texture_info in terrain_data['texture_data'].items():
        texture_path = texture_info['textures']
        full_path = f"RP/{texture_path}"
        
        if os.path.exists(full_path):
            terrain_textures_found += 1
        else:
            terrain_textures_missing += 1
            missing_textures.append(texture_id)
    
    print(f"✓ Terrain textures: {terrain_textures_found}/{terrain_textures_found + terrain_textures_missing}")
    
    if missing_textures:
        print(f"  Missing: {', '.join(missing_textures)}")
    
    # Zbierz wszystkie pliki PNG z ich ścieżkami
    all_png_files = set()
    
    # Sprawdź katalogi kategorii
    for category in ['a', 'b', 'c', 'd']:
        texture_dir = f'RP/textures/blocks/{category}'
        if os.path.exists(texture_dir):
            for filename in os.listdir(texture_dir):
                if filename.endswith('.png'):
                    # Dodaj ścieżkę względną do RP/textures/
                    relative_path = f"textures/blocks/{category}/{filename}"
                    all_png_files.add(relative_path)
    
    # Sprawdź pliki PNG w sign_backs
    sign_backs_dir = 'RP/textures/blocks/sign_backs'
    if os.path.exists(sign_backs_dir):
        for filename in os.listdir(sign_backs_dir):
            if filename.endswith('.png'):
                # Dodaj ścieżkę względną do RP/textures/
                relative_path = f"textures/blocks/sign_backs/{filename}"
                all_png_files.add(relative_path)
    
    # Sprawdź pliki PNG w głównym katalogu textures/blocks
    main_texture_dir = 'RP/textures/blocks'
    if os.path.exists(main_texture_dir):
        for filename in os.listdir(main_texture_dir):
            if filename.endswith('.png'):
                # Dodaj ścieżkę względną do RP/textures/
                relative_path = f"textures/blocks/{filename}"
                all_png_files.add(relative_path)
    
    # Znajdź ścieżki tekstur zdefiniowane w terrain_texture.json
    terrain_texture_paths = set()
    for texture_id, texture_info in terrain_data['texture_data'].items():
        terrain_texture_paths.add(texture_info['textures'])
    
    # Znajdź nadmiarowe pliki PNG
    extra_png_files = all_png_files - terrain_texture_paths
    
    print(f"✓ PNG files: {len(all_png_files)}")
    print(f"  Terrain textures: {len(terrain_texture_paths)}")
    print(f"  Extra PNG files: {len(extra_png_files)}")
    
    if extra_png_files:
        print("  Details:")
        for extra_file in sorted(extra_png_files):
            print(f"    - {extra_file}")
        print("  Note: These are unused background textures that were replaced by size-specific ones.")
        print("  Action: These can be safely removed to clean up the project.")
    
    # Sprawdź czy wszystkie tekstury z bloków są w terrain_texture.json
    print("\n🔍 BLOCK TEXTURES IN TERRAIN")
    print("=" * 35)
    
    block_textures = set()
    for category in ['a', 'b', 'c', 'd']:
        block_dir = f'BP/blocks/{category}'
        if os.path.exists(block_dir):
            for filename in os.listdir(block_dir):
                if filename.endswith('.block.json'):
                    try:
                        with open(os.path.join(block_dir, filename), 'r', encoding='utf-8') as f:
                            block_data = json.load(f)
                        
                        # Sprawdź wszystkie tekstury w material_instances
                        if 'minecraft:material_instances' in block_data['minecraft:block']['components']:
                            material_instances = block_data['minecraft:block']['components']['minecraft:material_instances']
                            for face, material in material_instances.items():
                                if 'texture' in material:
                                    block_textures.add(material['texture'])
                    except Exception:
                        continue
    
    # Sprawdź które tekstury z bloków nie są w terrain_texture.json
    # block_textures zawiera nazwy tekstur (klucze), więc porównujemy z kluczami z terrain_texture.json
    terrain_texture_keys = set(terrain_data['texture_data'].keys())
    missing_in_terrain = block_textures - terrain_texture_keys
    
    print(f"✓ Block textures: {len(block_textures)}")
    print(f"  In terrain: {len(block_textures - missing_in_terrain)}")
    print(f"  Missing in terrain: {len(missing_in_terrain)}")
    
    if missing_in_terrain:
        print(f"  Missing: {', '.join(sorted(missing_in_terrain))}")
        print("  Details:")
        for missing_texture in sorted(missing_in_terrain):
            print(f"    - {missing_texture}")
    
    return total_found, total_missing, terrain_textures_found, terrain_textures_missing, all_png_files, extra_png_files, block_textures, missing_in_terrain

def verify_models():
    """Weryfikuj modele 3D"""
    print("\n🔍 3D MODELS")
    print("=" * 30)
    
    models_dir = "RP/models/blocks"
    used_models = set()
    unused_models = []
    
    # Sprawdź wszystkie pliki .geo.json
    for filename in os.listdir(models_dir):
        if filename.endswith('.geo.json'):
            model_name = filename.replace('.geo.json', '')
            geometry_name = f"geometry.{model_name}"
            
            # Sprawdź czy model jest używany w blokach
            is_used = False
            for root, dirs, files in os.walk('BP/blocks'):
                for file in files:
                    if file.endswith('.block.json'):
                        block_path = os.path.join(root, file)
                        try:
                            with open(block_path, 'r', encoding='utf-8') as f:
                                block_data = json.load(f)
                            
                            if 'minecraft:geometry' in block_data['minecraft:block']['components']:
                                if block_data['minecraft:block']['components']['minecraft:geometry'] == geometry_name:
                                    is_used = True
                                    used_models.add(geometry_name)
                                    break
                        except Exception:
                            continue
                
                if is_used:
                    break
            
            if not is_used:
                unused_models.append(filename)
    
    print(f"✓ Used: {len(used_models)}, Unused: {len(unused_models)}")
    
    if unused_models:
        print("  Details:")
        for model in unused_models:
            print(f"    - {model}")
        print("  Note: These are base models that were replaced by size-specific models.")
        print("  Action: These can be safely removed if not needed for future reference.")
    
    return len(used_models), len(unused_models)

def verify_block_definitions():
    """Weryfikuj definicje bloków"""
    print("\n🔍 BLOCK DEFINITIONS")
    print("=" * 30)
    
    # Wczytaj bazę danych
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = ['A', 'B', 'C', 'D']
    total_found = 0
    total_missing = 0
    
    for category in categories:
        signs = data['road_signs'][category]['signs']
        
        for sign_id in signs.keys():
            # Sprawdź czy plik bloku istnieje
            block_path = f"BP/blocks/{category.lower()}/{sign_id}.block.json"
            if os.path.exists(block_path):
                total_found += 1
            else:
                total_missing += 1
    
    print(f"✓ Found: {total_found}, Missing: {total_missing}")
    
    return total_found, total_missing

def verify_database():
    """Weryfikuj bazę danych"""
    print("\n🔍 DATABASE")
    print("=" * 30)
    
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = ['A', 'B', 'C', 'D']
    total_signs = 0
    signs_with_dimensions = 0
    signs_with_wikipedia = 0
    signs_with_translations = 0
    
    for category in categories:
        signs = data['road_signs'][category]['signs']
        category_count = len(signs)
        total_signs += category_count
        
        for sign_id, sign_data in signs.items():
            if 'image_width' in sign_data and 'image_height' in sign_data:
                signs_with_dimensions += 1
            if 'wikipedia_url' in sign_data:
                signs_with_wikipedia += 1
            if 'translation_pl' in sign_data and 'translation_en' in sign_data:
                signs_with_translations += 1
    
    print(f"✓ Total: {total_signs}")
    print(f"  With dimensions: {signs_with_dimensions}")
    print(f"  With Wikipedia links: {signs_with_wikipedia}")
    print(f"  With translations: {signs_with_translations}")
    
    return total_signs, signs_with_dimensions, signs_with_wikipedia, signs_with_translations

def verify_project_structure():
    """Weryfikuj strukturę projektu"""
    print("\n🔍 PROJECT STRUCTURE")
    print("=" * 30)
    
    required_dirs = [
        'RP/textures/blocks/a', 'RP/textures/blocks/b', 'RP/textures/blocks/c', 'RP/textures/blocks/d',
        'RP/models/blocks', 'BP/blocks/a', 'BP/blocks/b', 'BP/blocks/c', 'BP/blocks/d'
    ]
    
    found_dirs = 0
    missing_dirs = []
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            found_dirs += 1
        else:
            missing_dirs.append(dir_path)
    
    print(f"✓ Found: {found_dirs}, Missing: {len(missing_dirs)}")
    
    if missing_dirs:
        print(f"  Missing: {', '.join(missing_dirs)}")
    
    return found_dirs, len(missing_dirs)

def verify_translations():
    """Weryfikuj tłumaczenia"""
    print("\n🔍 TRANSLATIONS")
    print("=" * 30)
    
    # Wczytaj bazę danych
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Wczytaj pliki języków
    with open('RP/texts/pl_PL.lang', 'r', encoding='utf-8') as f:
        pl_content = f.read()
    
    with open('RP/texts/en_US.lang', 'r', encoding='utf-8') as f:
        en_content = f.read()
    
    # Zbierz wszystkie znaki z bazy danych
    all_signs = set()
    for category in ['A', 'B', 'C', 'D']:
        all_signs.update(data['road_signs'][category]['signs'].keys())
    
    # Znajdź tłumaczenia w plikach języków
    pl_translations = set()
    en_translations = set()
    
    for match in re.finditer(r'tile\.polish_road_sign:([^.]+)\.name=', pl_content):
        pl_translations.add(match.group(1))
    
    for match in re.finditer(r'tile\.polish_road_sign:([^.]+)\.name=', en_content):
        en_translations.add(match.group(1))
    
    # Porównaj bezpośrednio, ponieważ pliki tłumaczeń używają już podkreślników
    missing_pl = all_signs - pl_translations
    missing_en = all_signs - en_translations
    extra_pl = pl_translations - all_signs
    extra_en = en_translations - all_signs
    
    print(f"✓ Polish: {len(pl_translations)}/{len(all_signs)}")
    if missing_pl:
        print(f"    Missing {len(missing_pl)}:")
        for name in missing_pl:
            print(f"      {name}")
    if extra_pl :
        print(f"    Extra {len(extra_pl)}:")
        for name in extra_pl:
            print(f"      {name}")
    print(f"✓ English: {len(en_translations)}/{len(all_signs)}")
    if missing_en:
        print(f"    Missing {len(missing_en)}:")
        for name in missing_en:
            print(f"      {name}")
    if extra_en:
        print(f"    Extra {len(extra_en)}:")
        for name in extra_en:
            print(f"      {name}")

    return len(pl_translations), len(en_translations), len(missing_pl), len(missing_en)

def verify_signs_completeness():
    """Sprawdź kompletność znaków"""
    print("\n🔍 SIGNS COMPLETENESS")
    print("=" * 30)
    
    # Wczytaj bazę danych
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Zbierz wszystkie znaki z bazy danych
    database_signs = set()
    for category in ['A', 'B', 'C', 'D']:
        database_signs.update(data['road_signs'][category]['signs'].keys())
    
    # Znajdź wszystkie bloki
    block_signs = set()
    for category in ['a', 'b', 'c', 'd']:
        block_dir = f'BP/blocks/{category}'
        if os.path.exists(block_dir):
            for filename in os.listdir(block_dir):
                if filename.endswith('.block.json'):
                    sign_id = filename.replace('.block.json', '')
                    block_signs.add(sign_id)
    
    # Znajdź wszystkie tekstury PNG
    png_signs = set()
    for category in ['a', 'b', 'c', 'd']:
        texture_dir = f'RP/textures/blocks/{category}'
        if os.path.exists(texture_dir):
            for filename in os.listdir(texture_dir):
                if filename.endswith('.png'):
                    sign_id = filename.replace('.png', '')
                    png_signs.add(sign_id)
    
    # Znajdź wszystkie tłumaczenia
    with open('RP/texts/pl_PL.lang', 'r', encoding='utf-8') as f:
        pl_content = f.read()
    
    with open('RP/texts/en_US.lang', 'r', encoding='utf-8') as f:
        en_content = f.read()
    
    pl_translations = set()
    en_translations = set()
    
    for match in re.finditer(r'tile\.polish_road_sign:([^.]+)\.name=', pl_content):
        pl_translations.add(match.group(1))
    
    for match in re.finditer(r'tile\.polish_road_sign:([^.]+)\.name=', en_content):
        en_translations.add(match.group(1))
    
    # Oblicz statystyki
    missing_blocks = database_signs - block_signs
    missing_pngs = database_signs - png_signs
    missing_pl = database_signs - pl_translations
    missing_en = database_signs - en_translations
    
    extra_blocks = block_signs - database_signs
    extra_pngs = png_signs - database_signs
    extra_pl = pl_translations - database_signs
    extra_en = en_translations - database_signs
    
    print(f"✓ Database: {len(database_signs)} signs")
    print(f"  Missing blocks: {len(missing_blocks)}")
    print(f"  Missing PNGs: {len(missing_pngs)}")
    print(f"  Missing PL: {len(missing_pl)}")
    print(f"  Missing EN: {len(missing_en)}")
    
    if extra_blocks or extra_pngs:
        print(f"  Extra blocks: {len(extra_blocks)}")
        print(f"  Extra PNGs: {len(extra_pngs)}")
    
    return len(database_signs), len(missing_blocks), len(missing_pngs), len(missing_pl), len(missing_en)

def verify_blocks_comprehensive():
    """Kompleksowa weryfikacja bloków: definicje, tekstury, modele i kompatybilność"""
    print("\n🔍 BLOCKS COMPREHENSIVE VERIFICATION")
    print("=" * 50)
    
    # Wczytaj dane
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open('RP/textures/terrain_texture.json', 'r', encoding='utf-8') as f:
        terrain_data = json.load(f)
    
    # 1. SPRAWDŹ DEFINICJE BLOKÓW
    print("📋 BLOCK DEFINITIONS")
    print("-" * 30)
    
    categories = ['A', 'B', 'C', 'D']
    total_found = 0
    total_missing = 0
    
    for category in categories:
        signs = data['road_signs'][category]['signs']
        
        for sign_id in signs.keys():
            block_path = f"BP/blocks/{category.lower()}/{sign_id}.block.json"
            if os.path.exists(block_path):
                total_found += 1
            else:
                total_missing += 1
    
    print(f"✓ Found: {total_found}, Missing: {total_missing}")
    
    # 2. SPRAWDŹ TEKSTURY I PLIKI PNG
    print("\n🎨 TEXTURES & PNG FILES")
    print("-" * 30)
    
    # Sprawdź czy wszystkie tekstury z terrain_texture.json istnieją
    terrain_textures_found = 0
    terrain_textures_missing = 0
    missing_textures = []
    
    for texture_id, texture_info in terrain_data['texture_data'].items():
        texture_path = texture_info['textures']
        full_path = f"RP/{texture_path}"
        
        if os.path.exists(full_path):
            terrain_textures_found += 1
        else:
            terrain_textures_missing += 1
            missing_textures.append(texture_id)
    
    print(f"✓ Terrain textures from blocks: {terrain_textures_found}")
    
    if missing_textures:
        print(f"✖ Missing {terrain_textures_missing}: {', '.join(missing_textures)}")
    
    # Zbierz wszystkie pliki PNG
    all_png_files = set()
    
    for category in ['a', 'b', 'c', 'd']:
        texture_dir = f'RP/textures/blocks/{category}'
        if os.path.exists(texture_dir):
            for filename in os.listdir(texture_dir):
                if filename.endswith('.png'):
                    relative_path = f"textures/blocks/{category}/{filename}"
                    all_png_files.add(relative_path)
    
    sign_backs_dir = 'RP/textures/blocks/sign_backs'
    if os.path.exists(sign_backs_dir):
        for filename in os.listdir(sign_backs_dir):
            if filename.endswith('.png'):
                relative_path = f"textures/blocks/sign_backs/{filename}"
                all_png_files.add(relative_path)
    
    main_texture_dir = 'RP/textures/blocks'
    if os.path.exists(main_texture_dir):
        for filename in os.listdir(main_texture_dir):
            if filename.endswith('.png'):
                relative_path = f"textures/blocks/{filename}"
                all_png_files.add(relative_path)
    
    # Znajdź ścieżki tekstur z terrain_texture.json
    terrain_texture_paths = set()
    for texture_id, texture_info in terrain_data['texture_data'].items():
        terrain_texture_paths.add(texture_info['textures'])
    
    # Znajdź nadmiarowe pliki PNG
    extra_png_files = all_png_files - terrain_texture_paths
    
    print(f"✓  Terrain textures from definition: {len(terrain_texture_paths)}")
    print(f" PNG files: {len(all_png_files)}")
    print(f"  ✖  Extra PNG files: {len(extra_png_files)}")
    
    if extra_png_files:
        print("  Details:")
        for extra_file in sorted(extra_png_files):
            print(f"    - {extra_file}")
    
    # 3. SPRAWDŹ TEKSTURY Z BLOKÓW
    print("\n🔗 BLOCK TEXTURES IN TERRAIN")
    print("-" * 30)
    
    block_textures = set()
    for category in ['a', 'b', 'c', 'd']:
        block_dir = f'BP/blocks/{category}'
        if os.path.exists(block_dir):
            for filename in os.listdir(block_dir):
                if filename.endswith('.block.json'):
                    try:
                        with open(os.path.join(block_dir, filename), 'r', encoding='utf-8') as f:
                            block_data = json.load(f)
                        
                        if 'minecraft:material_instances' in block_data['minecraft:block']['components']:
                            material_instances = block_data['minecraft:block']['components']['minecraft:material_instances']
                            for face, material in material_instances.items():
                                if 'texture' in material:
                                    block_textures.add(material['texture'])
                    except Exception:
                        continue
    
    terrain_texture_keys = set(terrain_data['texture_data'].keys())
    missing_in_terrain = block_textures - terrain_texture_keys
    
    print(f"✓ Block textures: {len(block_textures)}")
    print(f"  In terrain: {len(block_textures - missing_in_terrain)}")
    print(f"  Missing in terrain: {len(missing_in_terrain)}")
    
    if missing_in_terrain:
        print(f"  Missing: {', '.join(sorted(missing_in_terrain))}")
    
    # 4. SPRAWDŹ MODELE 3D
    print("\n📐 3D MODELS")
    print("-" * 30)
    
    models_dir = "RP/models/blocks"
    used_models = set()
    unused_models = []
    
    for filename in os.listdir(models_dir):
        if filename.endswith('.geo.json'):
            model_name = filename.replace('.geo.json', '')
            geometry_name = f"geometry.{model_name}"
            
            is_used = False
            for root, dirs, files in os.walk('BP/blocks'):
                for file in files:
                    if file.endswith('.block.json'):
                        block_path = os.path.join(root, file)
                        try:
                            with open(block_path, 'r', encoding='utf-8') as f:
                                block_data = json.load(f)
                            
                            if 'minecraft:geometry' in block_data['minecraft:block']['components']:
                                if block_data['minecraft:block']['components']['minecraft:geometry'] == geometry_name:
                                    is_used = True
                                    used_models.add(geometry_name)
                                    break
                        except Exception:
                            continue
                
                if is_used:
                    break
            
            if not is_used:
                unused_models.append(filename)
    
    print(f"✓ Used: {len(used_models)}, Unused: {len(unused_models)}")
    
    if unused_models:
        print("  Details:")
        for model in unused_models:
            print(f"    - {model}")
    
    # 5. SPRAWDŹ KOMPATYBILNOŚĆ TEKSTUR Z MODELAMI
    print("\n⚙️  TEXTURE-MODEL COMPATIBILITY")
    print("-" * 30)
    
    # Wczytaj wymiary modeli
    model_dimensions = {}
    for filename in os.listdir(models_dir):
        if filename.endswith('.geo.json'):
            model_name = filename.replace('.geo.json', '')
            model_path = os.path.join(models_dir, filename)
            width, height = get_model_dimensions(model_path)
            if width and height:
                model_dimensions[model_name] = (width, height)
    
    print(f"✓ Models loaded: {len(model_dimensions)}")
    print(f"  Model dimensions: {', '.join([f'{name}({w}x{h})' for name, (w, h) in model_dimensions.items()])}")
    
    # Sprawdź kompatybilność
    compatibility_issues = []
    texture_model_mismatches = []
    missing_models = []
    missing_textures = []
    
    for category in ['a', 'b', 'c', 'd']:
        block_dir = f'BP/blocks/{category}'
        if os.path.exists(block_dir):
            for filename in os.listdir(block_dir):
                if filename.endswith('.block.json'):
                    block_path = os.path.join(block_dir, filename)
                    sign_id = filename.replace('.block.json', '')
                    
                    try:
                        with open(block_path, 'r', encoding='utf-8') as f:
                            block_data = json.load(f)
                        
                        # Sprawdź geometrię
                        geometry_name = None
                        if 'minecraft:geometry' in block_data['minecraft:block']['components']:
                            geometry_name = block_data['minecraft:block']['components']['minecraft:geometry']
                            model_name = geometry_name.replace('geometry.', '')
                        
                        # Sprawdź teksturę
                        texture_name = None
                        if 'minecraft:material_instances' in block_data['minecraft:block']['components']:
                            material_instances = block_data['minecraft:block']['components']['minecraft:material_instances']
                            for face, material in material_instances.items():
                                if 'texture' in material:
                                    texture_name = material['texture']
                                    break
                        
                        # Sprawdź wymiary tekstury
                        texture_width, texture_height = None, None
                        if texture_name and texture_name in terrain_data['texture_data']:
                            texture_path = terrain_data['texture_data'][texture_name]['textures']
                            full_texture_path = f"RP/{texture_path}"
                            if os.path.exists(full_texture_path):
                                texture_width, texture_height = get_texture_dimensions(full_texture_path)
                            else:
                                missing_textures.append(f"{sign_id} (texture: {texture_name})")
                        
                        # Sprawdź wymiary modelu
                        model_width, model_height = None, None
                        if model_name:
                            # Sprawdź czy model istnieje lub znajdź podobny
                            actual_model_name = find_similar_model(model_name, model_dimensions.keys())
                            if actual_model_name:
                                model_width, model_height = model_dimensions[actual_model_name]
                                if actual_model_name != model_name:
                                    print(f"    Note: {sign_id} using {actual_model_name} instead of {model_name}")
                            else:
                                missing_models.append(f"{sign_id} (model: {model_name})")
                        
                        # Sprawdź kompatybilność
                        if (texture_width and texture_height and 
                            model_width and model_height and
                            (texture_width != model_width or texture_height != model_height)):
                            texture_model_mismatches.append({
                                'sign_id': sign_id,
                                'texture': f"{texture_width}x{texture_height}",
                                'model': f"{model_width}x{model_height}",
                                'model_name': model_name
                            })
                        
                        # Sprawdź czy blok ma geometrię
                        if not geometry_name:
                            compatibility_issues.append(f"{sign_id} (no geometry)")
                        
                    except Exception as e:
                        compatibility_issues.append(f"{sign_id} (error: {str(e)})")
    
    print(f"✓ Blocks checked: {len([f for f in os.listdir('BP/blocks/a') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/b') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/c') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/d') if f.endswith('.block.json')])}")
    
    if texture_model_mismatches:
        print(f"  ⚠️  Texture-model mismatches: {len(texture_model_mismatches)}")
        for mismatch in texture_model_mismatches[:5]:
            print(f"    {mismatch['sign_id']}: texture {mismatch['texture']} vs model {mismatch['model']} ({mismatch['model_name']})")
        if len(texture_model_mismatches) > 5:
            print(f"    ... and {len(texture_model_mismatches) - 5} more")
    
    if missing_models:
        print(f"  ❌ Missing models: {len(missing_models)}")
        for missing in missing_models[:3]:
            print(f"    {missing}")
        if len(missing_models) > 3:
            print(f"    ... and {len(missing_models) - 3} more")
    
    if missing_textures:
        print(f"  ❌ Missing textures: {len(missing_textures)}")
        for missing in missing_textures[:3]:
            print(f"    {missing}")
        if len(missing_textures) > 3:
            print(f"    ... and {len(missing_textures) - 3} more")
    
    if compatibility_issues:
        print(f"  ❌ Compatibility issues: {len(compatibility_issues)}")
        for issue in compatibility_issues[:3]:
            print(f"    {issue}")
        if len(compatibility_issues) > 3:
            print(f"    ... and {len(compatibility_issues) - 3} more")
    
    if not texture_model_mismatches and not missing_models and not missing_textures and not compatibility_issues:
        print(f"  ✅ All blocks have compatible geometries and textures!")
    
    # Podsumowanie sekcji bloków
    print(f"\n📊 BLOCKS SUMMARY:")
    print(f"  ✓ Block definitions: {total_found}/{total_found + total_missing}")
    print(f"  ✓ Terrain textures: {terrain_textures_found}/{terrain_textures_found + terrain_textures_missing}")
    print(f"  ✓ PNG files: {len(all_png_files)} total, {len(extra_png_files)} extra")
    print(f"  ✓ Block textures: {len(block_textures)} total, {len(missing_in_terrain)} missing in terrain")
    print(f"  ✓ 3D models: {len(used_models)} used, {len(unused_models)} unused")
    print(f"  ✓ Compatibility: {len(texture_model_mismatches)} mismatches, {len(missing_models)} missing models")
    
    return (total_found, total_missing, terrain_textures_found, terrain_textures_missing, 
            all_png_files, extra_png_files, block_textures, missing_in_terrain,
            len(used_models), len(unused_models), texture_model_mismatches, 
            len(missing_models), len(missing_textures), len(compatibility_issues))

def main():
    """Główna funkcja weryfikacji"""
    print("🔍 VERIFICATION SUMMARY")
    print("=" * 50)
    
    # 1. KOMPLEKSOWA WERYFIKACJA BLOKÓW (definicje, tekstury, modele, kompatybilność)
    (blocks_found, blocks_missing, terrain_textures_found, terrain_textures_missing, 
     all_png_files, extra_png_files, block_textures, missing_in_terrain,
     models_used, models_unused, texture_model_mismatches, 
     missing_models, missing_textures, compatibility_issues) = verify_blocks_comprehensive()
    
    # 2. MENU I TŁUMACZENIA
    pl_trans, en_trans, pl_missing, en_missing = verify_translations()
    
    # 3. DODATKOWE INFORMACJE
    db_total, db_dim, db_wiki, db_trans = verify_database()
    structure_found, structure_missing = verify_project_structure()
    signs_total, signs_missing_blocks, signs_missing_pngs, signs_missing_pl, signs_missing_en = verify_signs_completeness()
    
    # Podsumowanie
    print("\n" + "=" * 50)
    print("📊 OVERALL SUMMARY")
    print("=" * 50)
    
    # Oblicz sukces tekstur na podstawie terrain_textures
    texture_success_rate = 100.0 if (terrain_textures_found + terrain_textures_missing) > 0 else 0
    if terrain_textures_found + terrain_textures_missing > 0:
        texture_success_rate = (terrain_textures_found / (terrain_textures_found + terrain_textures_missing)) * 100
    
    print(f"Textures: {terrain_textures_found}/{terrain_textures_found + terrain_textures_missing} ({texture_success_rate:.1f}%)")
    print(f"Models: {models_used}/{models_used + models_unused} (Used: {models_used}, Unused: {models_unused})")
    print(f"Block Definitions: {blocks_found}/{blocks_found + blocks_missing} ({blocks_found / (blocks_found + blocks_missing) * 100:.1f}%)")
    print(f"Database: {db_total} signs with dimensions")
    print(f"Structure: {structure_found}/{structure_found + structure_missing} directories found")
    print(f"Translations: PL {pl_trans}/{signs_total}, EN {en_trans}/{signs_total}")
    print(f"Signs completeness: missing blocks: {signs_missing_blocks}, missing PNGs: {signs_missing_pngs}, missing PL: {signs_missing_pl}, missing EN: {signs_missing_en}")
    print(f"Geometry-Texture Compatibility: mismatches: {len(texture_model_mismatches)}, missing models: {missing_models}, missing textures: {missing_textures}, compatibility issues: {compatibility_issues}")
    
    # Dodaj podsumowanie wszystkich weryfikacji
    print(f"\n🔍 COMPREHENSIVE VERIFICATION:")
    print(f"  ✓ Terrain textures: {terrain_textures_found}/{terrain_textures_found + terrain_textures_missing}")
    print(f"  ✓ PNG files: {len(all_png_files)} total, {len(extra_png_files)} extra")
    print(f"  ✓ Block textures: {len(block_textures)} total, {len(missing_in_terrain)} missing in terrain")
    
    # Sprawdź czy wszystko jest w porządku
    all_good = (
        terrain_textures_missing == 0 and
        models_unused == 0 and
        blocks_missing == 0 and
        structure_missing == 0 and
        pl_missing == 0 and
        en_missing == 0 and
        signs_missing_blocks == 0 and
        signs_missing_pngs == 0 and
        signs_missing_pl == 0 and
        signs_missing_en == 0 and
        len(extra_png_files) == 0 and
        len(missing_in_terrain) == 0 and
        len(texture_model_mismatches) == 0 and
        missing_models == 0 and
        missing_textures == 0 and
        compatibility_issues == 0
    )
    
    if all_good:
        print(f"\n🎉 ALL VERIFICATIONS PASSED!")
        print(f"  ✅ Project is complete and consistent")
    else:
        print(f"\n⚠️  SOME ISSUES DETECTED:")
        if terrain_textures_missing > 0:
            print(f"  ❌ Missing terrain textures: {terrain_textures_missing}")
        if models_unused > 0:
            print(f"  ❌ Unused models: {models_unused}")
        if blocks_missing > 0:
            print(f"  ❌ Missing block definitions: {blocks_missing}")
        if structure_missing > 0:
            print(f"  ❌ Missing directories: {structure_missing}")
        if pl_missing > 0 or en_missing > 0:
            print(f"  ❌ Missing translations: PL {pl_missing}, EN {en_missing}")
        if terrain_textures_missing > 0:
            print(f"  ❌ Missing terrain textures: {terrain_textures_missing}")
        if len(extra_png_files) > 0:
            print(f"  ❌ Extra PNG files: {len(extra_png_files)}")
        if len(missing_in_terrain) > 0:
            print(f"  ❌ Block textures missing in terrain: {len(missing_in_terrain)}")
        if len(texture_model_mismatches) > 0:
            print(f"  ❌ Texture-model mismatches: {len(texture_model_mismatches)}")
        if missing_models > 0:
            print(f"  ❌ Missing models: {missing_models}")
        if missing_textures > 0:
            print(f"  ❌ Missing textures: {missing_textures}")
        if compatibility_issues > 0:
            print(f"  ❌ Compatibility issues: {compatibility_issues}")
    
    print("\n✅ Verification completed!")

if __name__ == "__main__":
    main() 