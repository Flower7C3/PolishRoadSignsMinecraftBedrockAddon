#!/usr/bin/env python3
import os
import json
import re
from collections import defaultdict

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - texture dimension checks will be skipped")

def get_categories_from_blocks():
    """Pobierz kategorie dynamicznie z katalogów bloków"""
    categories = []
    blocks_dir = 'BP/blocks'
    if os.path.exists(blocks_dir):
        for item in os.listdir(blocks_dir):
            item_path = os.path.join(blocks_dir, item)
            if os.path.isdir(item_path):
                categories.append(item)
    return sorted(categories)

def get_categories_from_textures():
    """Pobierz kategorie dynamicznie z katalogów tekstur"""
    categories = []
    textures_dir = 'RP/textures/blocks'
    if os.path.exists(textures_dir):
        for item in os.listdir(textures_dir):
            item_path = os.path.join(textures_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                categories.append(item)
    return sorted(categories)

def get_all_categories():
    """Pobierz wszystkie kategorie (duże litery z bazy + małe litery z katalogów)"""
    # Pobierz z bazy danych (duże litery)
    try:
        with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        db_categories = list(data['road_signs'].keys())
    except:
        db_categories = []
    
    # Pobierz z katalogów bloków (małe litery)
    block_categories = get_categories_from_blocks()
    
    # Pobierz z katalogów tekstur (małe litery)
    texture_categories = get_categories_from_textures()
    
    # Połącz wszystkie i usuń duplikaty
    all_categories = list(set(db_categories + block_categories + texture_categories))
    return sorted(all_categories)

def get_db_categories():
    """Pobierz kategorie z bazy danych (duże litery)"""
    try:
        with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return sorted(list(data['road_signs'].keys()))
    except:
        return []

def get_file_categories():
    """Pobierz kategorie z katalogów plików (małe litery) - wykluczając sign_backs"""
    # Pobierz z katalogów bloków
    block_categories = get_categories_from_blocks()
    
    # Pobierz z katalogów tekstur
    texture_categories = get_categories_from_textures()
    
    # Połącz wszystkie i usuń duplikaty, ale wyklucz sign_backs
    all_categories = list(set(block_categories + texture_categories))
    # Usuń sign_backs z listy kategorii
    if 'sign_backs' in all_categories:
        all_categories.remove('sign_backs')
    return sorted(all_categories)

def get_texture_dimensions(texture_path):
    """Pobierz wymiary tekstury"""
    if not PIL_AVAILABLE:
        return None, None
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

    print(f"📐 Models loaded: {len(model_dimensions)}")
    print(f"  Model dimensions: {', '.join([f'{name}({w}x{h})' for name, (w, h) in model_dimensions.items()])}")

    # Sprawdź wszystkie bloki
    compatibility_issues = []
    texture_model_mismatches = []
    missing_models = []
    missing_textures = []

    for category in get_all_categories():
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
    print(f"📋 Blocks checked: {len([f for f in os.listdir('BP/blocks/a') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/b') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/c') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/d') if f.endswith('.block.json')])}")

    if texture_model_mismatches:
        print(f"  ⚠️  Texture-model mismatches: {len(texture_model_mismatches)}")
        for mismatch in texture_model_mismatches[:10]:  # Pokaż pierwsze 10
            print(f"    {mismatch['sign_id']}: texture {mismatch['texture']} vs model {mismatch['model']} ({mismatch['model_name']})")
        if len(texture_model_mismatches) > 10:
            print(f"    ... and {len(texture_model_mismatches) - 10} more")

    if missing_models:
        print(f"  ❌ Missing {len(missing_models)} models:")
        for missing in missing_models[:5]:
            print(f"    {missing}")
        if len(missing_models) > 5:
            print(f"    ... and {len(missing_models) - 5} more")

    if missing_textures:
        print(f"  ❌ Missing {len(missing_textures)} textures:")
        for missing in missing_textures[:5]:
            print(f"    {missing}")
        if len(missing_textures) > 5:
            print(f"    ... and {len(missing_textures) - 5} more")

    if compatibility_issues:
        print(f"  ❌ Compatibility issues {len(compatibility_issues)}:")
        for issue in compatibility_issues[:5]:
            print(f"    {issue}")
        if len(compatibility_issues) > 5:
            print(f"    ... and {len(compatibility_issues) - 5} more")

    if not texture_model_mismatches and not missing_models and not missing_textures and not compatibility_issues:
        print(f"  ✅ All blocks have compatible geometries and textures!")

    return len(texture_model_mismatches), len(missing_models), len(missing_textures), len(compatibility_issues)


def verify_block_definitions():
    """Weryfikuj definicje bloków"""
    print("\n🔍 BLOCK DEFINITIONS")
    print("=" * 30)

    # Wczytaj bazę danych
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    categories = get_db_categories()
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

    print(f"📋 Found: {total_found}, Missing: {total_missing}")

    return total_found, total_missing

def verify_database():
    """Weryfikuj kategorie w bazie danych"""
    print("\n🔍 CATEGORIES")
    print("=" * 30)

    # Wczytaj bazę danych
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    categories = get_db_categories()
    total_signs = 0
    signs_with_dimensions = 0
    signs_with_wikipedia_file = 0
    signs_with_translations = 0
    categories_with_wikipedia_url = 0
    categories_with_translations = 0

    for category in categories:
        signs = data['road_signs'][category]['signs']
        total_signs += len(signs)

        # Sprawdź wymiary dla każdego znaku
        for sign_id, sign_data in signs.items():
            if 'dimensions' in sign_data:
                signs_with_dimensions += 1
            if 'wikipedia_file_page' in sign_data:
                signs_with_wikipedia_file += 1
            if 'translations' in sign_data:
                signs_with_translations += 1

        # Sprawdź kategorie
        if 'wikipedia_category_page' in data['road_signs'][category]:
            categories_with_wikipedia_url += 1
        if 'translations' in data['road_signs'][category]:
            categories_with_translations += 1

    print(f"📊 Total: {total_signs}")
    print(f"  Categories with Wikipedia URLs: {categories_with_wikipedia_url}/{len(categories)}")
    print(f"  Categories with translations: {categories_with_translations}/{len(categories)}")

    return total_signs, signs_with_dimensions, signs_with_wikipedia_file, signs_with_translations

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

    print(f"📋 Found: {found_dirs}, Missing: {len(missing_dirs)}")

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
    database_signs = set()
    for category in get_db_categories():
        database_signs.update(data['road_signs'][category]['signs'].keys())

    # Znajdź tłumaczenia w plikach języków
    file_pl_translations = set()
    file_en_translations = set()

    for match in re.finditer(r'tile\.polish_road_sign:([^.]+)\.name=', pl_content):
        file_pl_translations.add(match.group(1))

    for match in re.finditer(r'tile\.polish_road_sign:([^.]+)\.name=', en_content):
        file_en_translations.add(match.group(1))

    # Porównaj bezpośrednio, ponieważ pliki tłumaczeń używają już podkreślników
    database_missing_pl = database_signs - file_pl_translations
    database_missing_en = database_signs - file_en_translations
    file_extra_pl = file_pl_translations - database_signs
    file_extra_en = file_en_translations - database_signs

    # Dodaj zmienne dla bazy danych
    missing_db_pl = database_signs - file_pl_translations
    missing_db_en = database_signs - file_en_translations

    print(f"🇵🇱 Polish: {len(file_pl_translations)}/{len(database_signs)}")
    if missing_db_pl:
        print(f"  ✗ Missing in database: {len(missing_db_pl)}")
    if database_missing_pl:
        print(f"  ✗ Missing in lang file {len(database_missing_pl)}:")
        for name in database_missing_pl: print(f"    - {name}")
    if file_extra_pl :
        print(f"  ✗ Extra in lang file {len(file_extra_pl)}:")
        for name in file_extra_pl: print(f"    - {name}")
    print(f"🇬🇧 English: {len(file_en_translations)}/{len(database_signs)}")
    if missing_db_en:
        print(f"  ✗ Missing in database: {len(missing_db_en)}")
    if database_missing_en:
        print(f"  ✗ Missing in lang file {len(database_missing_en)}:")
        for name in database_missing_en: print(f"    - {name}")
    if file_extra_en:
        print(f"✗ Extra {len(file_extra_en)}:")
        for name in file_extra_en: print(f"    - {name}")

    return len(file_pl_translations), len(file_en_translations), len(database_missing_pl), len(database_missing_en)

def verify_blocks_comprehensive():
    """Kompleksowa weryfikacja bloków: definicje, tekstury, modele i kompatybilność"""
    print("🔍 BLOCKS COMPREHENSIVE VERIFICATION")
    print("=" * 30)

    # Wczytaj dane
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open('RP/textures/terrain_texture.json', 'r', encoding='utf-8') as f:
        terrain_data = json.load(f)

    # 1. SPRAWDŹ DEFINICJE BLOKÓW
    print("\n📋 BLOCK DEFINITIONS")
    print("-" * 30)

    categories = get_db_categories()
    database_signs = set()
    database_missing_blocks = set()
    file_blocks_found = 0
    file_blocks_missing = 0

    # Zbierz wszystkie znaki z bazy danych
    for category in categories:
        signs = data['road_signs'][category]['signs']
        for sign_id in signs.keys():
            database_signs.add(sign_id)
            block_path = f"BP/blocks/{category.lower()}/{sign_id}.block.json"
            if os.path.exists(block_path):
                file_blocks_found += 1
            else:
                file_blocks_missing += 1
                database_missing_blocks.add(sign_id)

    # Znajdź wszystkie bloki w plikach
    file_block_signs = set()
    for category in get_file_categories():
        block_dir = f'BP/blocks/{category}'
        if os.path.exists(block_dir):
            for filename in os.listdir(block_dir):
                if filename.endswith('.block.json'):
                    sign_id = filename.replace('.block.json', '')
                    file_block_signs.add(sign_id)

    file_extra_blocks = file_block_signs - database_signs
    database_extra_blocks = database_signs - file_block_signs

    print(f"✓ Loaded: {file_blocks_found}")
    if file_blocks_missing > 0:
        print(f"  ✗ Missing: {file_blocks_missing}")
    if file_extra_blocks:
        print(f"  ✗ Extra blocks: {len(file_extra_blocks)}")
        for name in sorted(file_extra_blocks): print(f"  - {name}")
    if len(database_missing_blocks) > 0:
        print(f"  ✗ Missing in database: {len(database_missing_blocks)}")
        for name in sorted(database_missing_blocks): print(f"    - {name}")
    if len(database_extra_blocks) > 0:
        print(f"  ✗ Extra in database: {len(database_extra_blocks)}")
        for name in sorted(database_extra_blocks): print(f"    - {name}")

    # 2. SPRAWDŹ TEKSTURY I PLIKI PNG
    print("\n🎨 TEXTURES & PNG FILES")
    print("-" * 30)

    # Sprawdź czy wszystkie tekstury z terrain_texture.json istnieją
    terrain_textures_found = 0
    terrain_textures_missing = 0
    missing_png_textures = []

    for texture_id, texture_info in terrain_data['texture_data'].items():
        texture_path = texture_info['textures']
        full_path = f"RP/{texture_path}"

        if os.path.exists(full_path):
            terrain_textures_found += 1
        else:
            terrain_textures_missing += 1
            missing_png_textures.append(texture_id)

    # Test 1: Sprawdź czy wszystkie zdefiniowane tekstury mają pliki PNG
    print(f"✓ Textures from blocks: {len(terrain_data['texture_data'])}")
    print(f"✓ Textures by terrain_texture.json (with existing PNG files): {terrain_textures_found}")
    if terrain_textures_missing > 0:
        print(f"✗ Missing {terrain_textures_missing} files:")
        for name in sorted(missing_png_textures): print(f"  - {name}")

    # Test 2: Sprawdź czy są pliki PNG bez definicji
    all_png_files = set()

    for category in get_file_categories():
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

    print(f"✓ Textures by PNG files (with definition in terrain_texture.json): {len(all_png_files)}")
    if len(extra_png_files) > 0:
        print(f"  ✗ Missing {len(extra_png_files)} defintions terrain_texture.json:")
        for name in sorted(extra_png_files): print(f"    - {name}")

    # Sprawdź PNG w bazie danych vs pliki
    # Znajdź wszystkie tekstury PNG w plikach
    file_png_signs = set()
    for category in get_file_categories():
        texture_dir = f'RP/textures/blocks/{category}'
        if os.path.exists(texture_dir):
            for filename in os.listdir(texture_dir):
                if filename.endswith('.png'):
                    sign_id = filename.replace('.png', '')
                    file_png_signs.add(sign_id)

    database_missing_pngs = database_signs - file_png_signs
    file_extra_pngs = file_png_signs - database_signs

    print(f"✓ In database: {len(database_signs)}")
    if len(database_missing_pngs) > 0:
        print(f"  ✗ Missing db PNGs: {len(database_missing_pngs)}")
        for name in sorted(database_missing_pngs): print(f"    - {name}")
    if len(file_extra_pngs) > 0:
        print(f"  ✗ Extra file PNGs: {len(file_extra_pngs)}")
        for name in sorted(file_extra_pngs): print(f"    - {name}")

    # Test 3: Sprawdź czy wszystkie używane tekstury z bloków są zdefiniowane
    print("\n🔗 BLOCK TEXTURES IN TERRAIN")
    print("-" * 30)

    block_textures = set()
    for category in get_file_categories():
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

    terrain_texture_keys = set(terrain_data['texture_data'].keys())
    missing_in_terrain = block_textures - terrain_texture_keys
    unused_textures = terrain_texture_keys - block_textures

    print(f"✓ Block textures referenced in block definitions: {len(block_textures)}")
    print(f"✓ Found in terrain_texture.json: {len(block_textures - missing_in_terrain)}")

    if len(missing_in_terrain) > 0:
        print(f"  ✗ Missing {len(missing_in_terrain)} items from terrain_texture.json:")
        for name in sorted(missing_in_terrain): print(f"    - {name}")
    
    if len(unused_textures) > 0:
        print(f"  ✗ Unused {len(unused_textures)} items in terrain_texture.json:")
        for name in sorted(unused_textures): print(f"    - {name}")

  # 2. SPRAWDŹ POLE SHAPE W BAZIE DANYCH
    print("\n📐 SHAPE FIELD VERIFICATION")
    print("-" * 30)

    signs_with_shape = 0
    signs_without_shape = set()
    shape_types = {}

    for category in get_db_categories():
        signs = data['road_signs'][category]['signs']
        for sign_id, sign_data in signs.items():
            if 'shape' in sign_data:
                signs_with_shape += 1
                shape_type = sign_data['shape']
                if shape_type not in shape_types:
                    shape_types[shape_type] = 0
                shape_types[shape_type] += 1
            else:
                signs_without_shape.add(sign_id)

    print(f"✓ Signs with shape field: {signs_with_shape}")
    if len(signs_without_shape) > 0:
        print(f"  ✗ Signs without shape field: {len(signs_without_shape)}")
        for name in sorted(signs_without_shape): print(f"    - {name}")

    print(f"➤ Shape types: {', '.join([f'{shape}({count})' for shape, count in shape_types.items()])}")

    # 4. SPRAWDŹ MODELE 3D
    print("\n📐 3D MODELS")
    print("-" * 30)


    models_dir = "RP/models/blocks"
    used_models = set()
    unused_models = set()
    model_dimensions = {}

    for filename in os.listdir(models_dir):
        if filename.endswith('.geo.json'):
            model_name = filename.replace('.geo.json', '')
            geometry_name = f"geometry.{model_name}"
            model_name = filename.replace('.geo.json', '')
            model_path = os.path.join(models_dir, filename)
            width, height = get_model_dimensions(model_path)
            if width and height:
                model_dimensions[model_name] = (width, height)

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
                unused_models.add(filename)

    print(f"✓ Loaded: {len(model_dimensions)}")
    print(f"✓︎ Used: {len(used_models)}")
    if len(unused_models):
        print(f"  ✗ Unused: {len(unused_models)}")
        for name in sorted(unused_models): print(f"    - {name}")

    print(f"➤ Model dimensions: {', '.join([f'{name}({w}x{h})' for name, (w, h) in model_dimensions.items()])}")

    # Sprawdź kompatybilność
    print("\n📐 MODELS COMPATIBILITY")
    print("-" * 30)

    compatibility_issues = []
    texture_model_mismatches = []
    missing_models = []
    missing_textures = []

    for category in get_file_categories():
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
        print(f"✗ Texture-model mismatches: {len(texture_model_mismatches)}")
        for mismatch in texture_model_mismatches[:5]:
            print(f"    {mismatch['sign_id']}: texture {mismatch['texture']} vs model {mismatch['model']} ({mismatch['model_name']})")
        if len(texture_model_mismatches) > 5:
            print(f"    ... and {len(texture_model_mismatches) - 5} more")

    if missing_models:
        print(f"✗ Missing {len(missing_models)} models:")
        for missing in missing_models[:3]:
            print(f"    {missing}")
        if len(missing_models) > 3:
            print(f"    ... and {len(missing_models) - 3} more")

    if missing_textures:
        print(f"✗ Missing {len(missing_textures)} textures:")
        for missing in missing_textures[:3]:
            print(f"    {missing}")
        if len(missing_textures) > 3:
            print(f"    ... and {len(missing_textures) - 3} more")

    if compatibility_issues:
        print(f"✗ Compatibility issues {len(compatibility_issues)}:")
        for issue in compatibility_issues[:3]:
            print(f"    {issue}")
        if len(compatibility_issues) > 3:
            print(f"    ... and {len(compatibility_issues) - 3} more")

    return (file_blocks_found, file_blocks_missing, terrain_textures_found, terrain_textures_missing,
            all_png_files, extra_png_files, block_textures, missing_in_terrain,
            len(used_models), len(unused_models), texture_model_mismatches,
            len(missing_models), len(missing_textures), len(compatibility_issues),
            signs_with_shape, len(signs_without_shape), unused_textures)

def main():
    """Główna funkcja weryfikacji"""

    # 1. KOMPLEKSOWA WERYFIKACJA BLOKÓW (definicje, tekstury, modele, kompatybilność)
    (file_blocks_found, file_blocks_missing, terrain_textures_found, terrain_textures_missing,
     all_png_files, extra_png_files, block_textures, missing_in_terrain,
     models_used, models_unused, texture_model_mismatches,
     missing_models, missing_textures, compatibility_issues,
     signs_with_shape, signs_without_shape, unused_textures) = verify_blocks_comprehensive()

    # 2. WERYFIKACJA TŁUMACZEŃ
    pl_trans, en_trans, pl_missing, en_missing = verify_translations()

    # 3. WERYFIKACJA BAZY DANYCH
    db_total, db_dim, db_wiki, db_trans = verify_database()

    # 4. WERYFIKACJA STRUKTURY PROJEKTU
    structure_found, structure_missing = verify_project_structure()

    # Sprawdź czy wszystko jest w porządku
    all_good = True

    if terrain_textures_missing > 0:
        all_good = False
    if len(extra_png_files) > 0:
        all_good = False
    if len(missing_in_terrain) > 0:
        all_good = False
    if len(unused_textures) > 0:
        all_good = False
    if models_unused > 0:
        all_good = False
    if file_blocks_missing > 0:
        all_good = False
    if structure_missing > 0:
        all_good = False

    if all_good:
        print("\n" + "=" * 50)
        print(f"🎉 ALL VERIFICATIONS PASSED!")
        print("=" * 50)
        print(f"  ✅ Project is complete and consistent")
    else:
        print("\n" + "=" * 50)
        print(f"⚠️ ISSUES DETECTED")
        print("=" * 50)
        if terrain_textures_missing > 0:
            print(f"  ❌ Missing terrain textures: {terrain_textures_missing}")
        if models_unused > 0:
            print(f"  ❌ Unused models: {models_unused}")
        if file_blocks_missing > 0:
            print(f"  ❌ Missing block definitions: {file_blocks_missing}")
        if structure_missing > 0:
            print(f"  ❌ Missing directories: {structure_missing}")
        if pl_missing > 0 or en_missing > 0:
            print(f"  ❌ Missing translations: PL {pl_missing}, EN {en_missing}")
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
        if signs_without_shape > 0:
            print(f"  ❌ Signs without shape field: {signs_without_shape}")
        if len(unused_textures) > 0:
            print(f"  ❌ Unused textures in terrain_texture.json: {len(unused_textures)}")

if __name__ == "__main__":
    main()