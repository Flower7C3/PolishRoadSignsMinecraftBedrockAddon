#!/usr/bin/env python3
"""
Comprehensive verification script for Minecraft Bedrock Addon
Verifies project structure, files, textures, and build readiness
"""

import os
import json
import sys
from typing import Dict, Any

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from console_utils import ConsoleStyle, print_if_not_quiet, rsort


def verify_project_structure():
    """Verify basic project structure"""
    ConsoleStyle.print_section("🔍 VERIFYING PROJECT STRUCTURE")

    required_files = [
        'config.json',
        'BP/manifest.json',
        'RP/manifest.json',
        'build.py'
    ]

    required_dirs = [
        'BP',
        'BP/blocks',
        'RP',
        'RP/textures',
        'RP/textures/blocks',
        'RP/textures/blocks/averse',
        'RP/textures/blocks/reverse',
        'RP/models',
        'RP/models/blocks',
        'RP/texts'
    ]

    errors = []
    warnings = []

    # Check required files
    for file_path in required_files:
        if os.path.exists(file_path):
            print_if_not_quiet(ConsoleStyle.success(f"Found: {file_path}"))
        else:
            print_if_not_quiet(ConsoleStyle.error(f"Missing: {file_path}"))
            errors.append(f"Missing required file: {file_path}")

    # Check required directories
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print_if_not_quiet(ConsoleStyle.success(f"Found: {dir_path}/"))
        else:
            print_if_not_quiet(ConsoleStyle.error(f"Missing: {dir_path}/"))
            errors.append(f"Missing required directory: {dir_path}")

    return errors, warnings


def verify_manifests():
    """Weryfikuj pliki manifestów"""
    ConsoleStyle.print_section("📋 MANIFESTS VERIFICATION")

    errors = []
    warnings = []

    manifest_files = [
        ("BP/manifest.json", "Behavior Pack"),
        ("RP/manifest.json", "Resource Pack")
    ]

    for file_path, pack_type in manifest_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check required fields
            required_fields = ['format_version', 'header']
            for field in required_fields:
                if field not in data:
                    errors.append(f"{pack_type} missing required field: {field}")
                    continue

            if 'header' in data:
                header = data['header']
                header_fields = ['name', 'description', 'uuid', 'version', 'min_engine_version']
                for field in header_fields:
                    if field not in header:
                        errors.append(f"{pack_type} header missing required field: {field}")

            # Check a version format
            if 'header' in data and 'version' in data['header']:
                version = data['header']['version']
                if not isinstance(version, list) or len(version) != 3:
                    errors.append(f"{pack_type} version must be [major, minor, patch]")
                else:
                    print_if_not_quiet(ConsoleStyle.success(f"{pack_type} version: {'.'.join(map(str, version))}"))

            print_if_not_quiet(ConsoleStyle.success(f"{pack_type} manifest is valid JSON"))

        except json.JSONDecodeError as e:
            errors.append(f"{pack_type} manifest is invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading {pack_type} manifest: {e}")

    if errors:
        print_if_not_quiet(ConsoleStyle.error(f"Found [{len(errors)}] manifest errors: {',,,,, '.join(errors)}"))
    else:
        print_if_not_quiet(ConsoleStyle.success("All manifests are valid!"))

    if warnings:
        print_if_not_quiet(ConsoleStyle.warning(f"Found [{len(warnings)}] manifest warnings: {', '.join(warnings)}"))

    return errors, warnings


def verify_config():
    """Weryfikuj plik config.json"""
    ConsoleStyle.print_section("⚙️ CONFIG VERIFICATION")

    errors = []
    warnings = []

    config_path = "config.json"
    if not os.path.exists(config_path):
        print_if_not_quiet(ConsoleStyle.info("config.json not found - skipping config verification"))
        return errors, warnings

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check required fields
        required_fields = ['type', 'name', 'namespace', 'targetVersion']
        for field in required_fields:
            if field not in data:
                errors.append(f"config.json missing required field: {field}")

        # Check namespace consistency
        if 'namespace' in data:
            namespace = data['namespace']
            print_if_not_quiet(ConsoleStyle.success(f"Namespace: {namespace}"))

            # Check if namespace is used in block files
            namespace_used = False
            for root, dirs, files in os.walk("BP/blocks"):
                for file in files:
                    if file.endswith('.block.json'):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            block_data = json.load(f)
                            if 'minecraft:block' in block_data:
                                identifier = block_data['minecraft:block']['description'].get('identifier', '')
                                if identifier.startswith(f"{namespace}:"):
                                    namespace_used = True
                                    break
                if namespace_used:
                    break

            if not namespace_used:
                warnings.append(f"Namespace '{namespace}' not found in block identifiers")

        print_if_not_quiet(ConsoleStyle.success("config.json is valid JSON"))

    except json.JSONDecodeError as e:
        errors.append(f"config.json is invalid JSON: {e}")
    except Exception as e:
        errors.append(f"Error reading config.json: {e}")

    if errors:
        print_if_not_quiet(ConsoleStyle.error(f"Found [{len(errors)}] config errors: {', '.join(errors)}"))
    else:
        print_if_not_quiet(ConsoleStyle.success("Config is valid!"))

    if warnings:
        print_if_not_quiet(ConsoleStyle.warning(f"Found [{len(warnings)}] config warnings: {', '.join(warnings)}"))

    return errors, warnings


def count_project_files():
    """Count files in the project"""
    stats: Dict[str, Any] = {}

    total_files = 0
    # Count files by directory
    for root, dirs, files in os.walk("."):
        # Skip git and cache directories
        if any(skip in root for skip in ['.git', '.idea', '__pycache__', 'venv', 'dist']):
            continue

        rel_path = os.path.relpath(root, ".")
        if rel_path == ".":
            rel_path = ""

        stats[f"📁 /{rel_path}"] = f"[{len(files)}] files"
        total_files += len(files)

    ConsoleStyle.print_stats(stats, f"📦 PROJECT FILES ([{total_files}])")

    return [], []


def verify_translations():
    """Verify localization files"""
    ConsoleStyle.print_section("🌐 TRANSLATIONS")

    errors = []
    warnings = []

    # Check languages.json
    languages_path = "RP/texts/languages.json"
    if os.path.exists(languages_path):
        try:
            with open(languages_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # languages.json is a list, not an object
            if isinstance(data, list):
                language_files = data
                print_if_not_quiet(ConsoleStyle.success(f"Found {len(language_files)} language files"))

                # Wczytaj bloki
                project_block_translations = set()
                for root, dirs, files in os.walk("BP/blocks"):
                    for file in files:
                        if file.endswith('.block.json'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    block_data = json.load(f)
                                    block_name = block_data['minecraft:block']['description']['identifier']
                                    project_block_translations.add(
                                        block_name.replace('polish_road_sign:', ''))
                            except Exception as e:
                                print_if_not_quiet(
                                    ConsoleStyle.error(f"Error reading block data file [{file}]: {e}"))
                                warnings.append(f"Error reading block data file [{file}]: {e}")
                # Wczytaj bazę danych
                with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Pobierz wszystkie znaki z bazy danych
                database_blocks = set()
                database_categories = set()
                for category in data['road_signs']:
                    group_name = data['road_signs'][category]['crafting_group']
                    database_categories.add(f'{group_name}')
                    for sign_id in data['road_signs'][category]['signs']:
                        database_blocks.add(sign_id)

                # Check if language files exist
                for lang_name in language_files:
                    lang_path = f"RP/texts/{lang_name}.lang"
                    if os.path.exists(lang_path):
                        # Wczytaj plik językowy
                        lang_file_block_translations = set()
                        lang_file_category_translations = set()
                        stats = {}
                        try:
                            with open(lang_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    line = line.strip()
                                    if line and '=' in line:
                                        key = line.split('=', 1)[0].strip()
                                        if key.startswith('tile.polish_road_sign:') and key.endswith('.name'):
                                            block_name = key.replace('tile.polish_road_sign:', '').replace('.name', '')
                                            lang_file_block_translations.add(block_name)
                                        elif key.startswith('polish_road_sign:'):
                                            # Kategorie mają format polish_road_sign:category_name
                                            category_name = key.replace('polish_road_sign:', '')
                                            lang_file_category_translations.add(category_name)

                            # Wczytaj crafting catalog
                            project_category_translations = set()
                            try:
                                with open('BP/item_catalog/crafting_item_catalog.json', 'r', encoding='utf-8') as f:
                                    catalog_data = json.load(f)
                                    for category in catalog_data['minecraft:crafting_items_catalog']['categories']:
                                        for group in category.get('groups', []):
                                            if 'group_identifier' in group and 'name' in group['group_identifier']:
                                                name = group['group_identifier']['name']
                                                if name.startswith('polish_road_sign:'):
                                                    category_name = name.replace('polish_road_sign:', '')
                                                    project_category_translations.add(category_name)
                            except Exception as e:
                                print_if_not_quiet(ConsoleStyle.error(f"Error reading crafting catalog: {e}"))
                                warnings.append(f"Error reading crafting catalog: {e}")

                            stats[ConsoleStyle.info("Items in lang file")] \
                                = f'{len(lang_file_category_translations) + len(lang_file_block_translations)}'

                            stats[ConsoleStyle.info("   Categories in lang file")] \
                                = len(lang_file_category_translations)
                            stats[ConsoleStyle.info("   Blocks in lang file")] \
                                = len(lang_file_block_translations)

                            stats[ConsoleStyle.info("Items in project")] = len(project_category_translations) + len(
                                project_block_translations)
                            stats[ConsoleStyle.info("   Categories in project")] \
                                = len(project_category_translations)
                            stats[ConsoleStyle.info("   Blocks in project")] \
                                = len(project_block_translations)

                            lang_file_extra_categories = lang_file_category_translations - project_category_translations
                            stats[ConsoleStyle.info("Extra categories in lang file") if lang_file_extra_categories else ConsoleStyle.info("Extra categories in lang file") ] \
                                = f'[{len(lang_file_extra_categories)}] ({', '.join([f'{name}' for name in sorted(lang_file_extra_categories)])})' if lang_file_extra_categories else 0
                            if lang_file_extra_categories:
                                warnings.append(f"Extra [{len(lang_file_extra_categories)}] categories in [{lang_name}] lang file")

                            lang_file_extra_blocks = lang_file_block_translations - project_block_translations
                            stats[ConsoleStyle.error("Extra blocks in lang file") if lang_file_extra_blocks else ConsoleStyle.info("Extra blocks in lang file") ] \
                                = f'[{len(lang_file_extra_blocks)}] ({', '.join([f'{name}' for name in sorted(lang_file_extra_blocks)])})' if lang_file_extra_blocks else 0
                            if lang_file_extra_blocks:
                                warnings.append(f"Extra [{len(lang_file_extra_blocks)}] blocks in [{lang_name}] lang file")

                            lang_file_missing_categories = project_category_translations - lang_file_category_translations
                            stats[ConsoleStyle.error("Missing categories defined in lang file") if lang_file_missing_categories else ConsoleStyle.info("Missing categories defined in lang file") ] \
                                = f'[{len(lang_file_missing_categories)}] ({', '.join([f'{name}' for name in sorted(lang_file_missing_categories)])})' if lang_file_missing_categories else 0
                            if lang_file_missing_categories:
                                warnings.append(
                                    f"Missing [{len(lang_file_missing_categories)}] categories defined in [{lang_name}] lang file")

                            lang_file_missing_blocks = project_block_translations - lang_file_block_translations
                            stats[ConsoleStyle.error("Missing blocks defined in lang file") if lang_file_missing_blocks else ConsoleStyle.info("Missing blocks defined in lang file") ] \
                                = f'[{len(lang_file_missing_blocks)}] ({', '.join([f'{name}' for name in sorted(lang_file_missing_blocks)])})' if lang_file_missing_blocks else 0
                            if lang_file_missing_blocks:
                                warnings.append(
                                    f"Missing [{len(lang_file_missing_blocks)}] blocks from defined in [{lang_name}] lang file")

                            stats[ConsoleStyle.info("In database")] = len(database_categories) + len(database_blocks)
                            stats[ConsoleStyle.info("   Categories in database")] = len(database_categories)
                            stats[ConsoleStyle.info("   Blocks in database")] = len(database_blocks)
                            database_missing_categories = database_categories - lang_file_category_translations
                            stats[ConsoleStyle.error("Missing categories from database") if database_missing_categories else ConsoleStyle.info("Missing categories from database") ] \
                                = f'[{len(database_missing_categories)}] ({', '.join([f'{name}' for name in sorted(database_missing_categories)])})' if database_missing_categories else 0
                            if database_missing_categories:
                                warnings.append(
                                    f"Missing [{len(database_missing_categories)}] from database in [{lang_name}]")
                            database_missing_blocks = database_blocks - project_block_translations
                            stats[ConsoleStyle.error("Missing blocks from database") if database_missing_blocks else ConsoleStyle.info("Missing blocks from database") ] \
                                = f'[{len(database_missing_blocks)}] ({', '.join([f'{name}' for name in sorted(database_missing_blocks)])})' if database_missing_blocks else 0
                            if database_missing_blocks:
                                warnings.append(
                                    f"Missing [{len(database_missing_blocks)}] from database in [{lang_name}]")

                            ConsoleStyle.print_stats(stats, f"{lang_name}", '-')

                        except Exception as e:
                            print_if_not_quiet(ConsoleStyle.error(f"Error reading [{lang_path}]: {e}"))
                            errors.append(f"Error reading [{lang_path}]")

                            continue
                    else:
                        errors.append(f"Missing language file [{lang_name}.lang]")
            else:
                errors.append("languages.json should be a list of language codes")

        except json.JSONDecodeError as e:
            errors.append(f"languages.json is invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading languages.json: {e}")
    else:
        errors.append("Missing languages.json")

    return errors, warnings


if not PIL_AVAILABLE:
    print(ConsoleStyle.warning("PIL not available - texture dimension checks will be skipped"))


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
        # Sprawdź podkatalogi averse i reverse
        for subdir in ['averse', 'reverse']:
            subdir_path = os.path.join(textures_dir, subdir)
            if os.path.exists(subdir_path):
                for item in os.listdir(subdir_path):
                    item_path = os.path.join(subdir_path, item)
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
        if 'minecraft:geometry' in model_data and isinstance(model_data['minecraft:geometry'], list) and len(
                model_data['minecraft:geometry']) > 0:
            geometry = model_data['minecraft:geometry'][0]
            if 'description' in geometry:
                description = geometry['description']
                if 'texture_width' in description and 'texture_height' in description:
                    return description['texture_width'], description['texture_height']

        return None, None
    except Exception as e:
        return None, None


def find_similar_model(model_name, available_models):
    """Znajdź podobny model, jeśli dokładny nie istnieje"""
    if model_name in available_models:
        return model_name

    # Próbuj znaleźć podobny model
    base_name = model_name.split('_')[0]  # np. "road_sign_rectangle"
    for available_model in available_models:
        if available_model.startswith(base_name):
            return available_model

    return None


def verify_vertical_alignment():
    """Sprawdź wyrównanie pionowe znaków"""
    errors = []
    warnings = []

    try:
        with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        stats = {}
        total_signs = 0
        signs_with_alignment = 0
        signs_with_invalid_alignment = set()
        alignment_stats = {'bottom': 0, 'top': 0, 'center': 0}

        for category in data['road_signs']:
            for sign_id, sign_data in data['road_signs'][category]['signs'].items():
                total_signs += 1
                alignment = sign_data.get('vertical_alignment', '')

                if alignment:
                    signs_with_alignment += 1
                    if alignment in alignment_stats:
                        alignment_stats[alignment] += 1
                    else:
                        stats[ConsoleStyle.error(f"Invalid alignment [{alignment}] for sign [{sign_id}]")] = True
                        signs_with_invalid_alignment.add(sign_id)
        stats[ConsoleStyle.info("Total signs")] = f"[{total_signs}]"
        stats[ConsoleStyle.info("Signs with alignment")] = f"[{signs_with_alignment}]"
        stats[ConsoleStyle.info("Signs without alignment")] = f"[{total_signs - signs_with_alignment}]"
        if signs_with_invalid_alignment:
            warnings.append(
                f"{len(signs_with_invalid_alignment)} sign{'s' if len(signs_with_invalid_alignment) == 1 else 's'} without alignment")
            stats[ConsoleStyle.warning(
                "Invalid alignments")] = f"[{len(signs_with_invalid_alignment)}] ({', '.join(sorted(signs_with_invalid_alignment))})"
        if alignment_stats['bottom'] > 0:
            stats[ConsoleStyle.info("Bottom alignment")] = f"[{alignment_stats['bottom']}]"
        if alignment_stats['top'] > 0:
            stats[ConsoleStyle.info("Top alignment")] = f"[{alignment_stats['top']}]"
        if alignment_stats['center'] > 0:
            stats[ConsoleStyle.info("Center alignment")] = f"[{alignment_stats['center']}]"

        ConsoleStyle.print_stats(stats, "📐 VERTICAL ALIGNMENT")

    except FileNotFoundError as e:
        ConsoleStyle.print_section("📐 VERTICAL ALIGNMENT")
        print_if_not_quiet(ConsoleStyle.error("Database file not found"))
        errors.append(e)

    return errors, warnings


def verify_database():
    """Sprawdź bazę danych"""

    errors = []
    warnings = []

    try:
        with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        stats = {}
        categories = list(data['road_signs'].keys())
        categories_with_wikipedia_category_page = 0
        categories_with_translations = 0

        for category in categories:
            category_data = data['road_signs'][category]
            # Sprawdź URL Wikipedia
            if 'wikipedia_category_page' in category_data and category_data['wikipedia_category_page']:
                categories_with_wikipedia_category_page += 1
            # Sprawdź tłumaczenia
            if 'translations' in category_data and category_data['translations']:
                categories_with_translations += 1

        stats[ConsoleStyle.success("Found")] = f"[{len(categories)}]"
        stats[ConsoleStyle.info("   With Wikipedia URLs")] = f"[{categories_with_wikipedia_category_page}]"
        stats[ConsoleStyle.info("   With translations")] = f"[{categories_with_translations}]"

        ConsoleStyle.print_stats(stats, "🗄️ CATEGORIES")

    except FileNotFoundError as e:
        ConsoleStyle.print_section("🗄️ CATEGORIES")
        print_if_not_quiet(ConsoleStyle.error("Database file not found"))
        errors.append(e)

    return errors, warnings


def verify_blocks_comprehensive():
    """Kompleksowa weryfikacja bloków: definicje, tekstury, modele i kompatybilność"""
    ConsoleStyle.print_section("⏹️ BLOCKS COMPREHENSIVE VERIFICATION")

    errors = []
    warnings = []

    try:

        # Wczytaj dane
        with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        with open('RP/textures/terrain_texture.json', 'r', encoding='utf-8') as f:
            terrain_data = json.load(f)

        # Zbierz statystyki
        sizes = {}
        shapes = {}
        shape_size_combinations = {}
        shape_size_examples = {}
        padding_examples = []
        no_padding_examples = []

        for category in data['road_signs']:
            for sign_id, sign_data in data['road_signs'][category]['signs'].items():
                # Wymiary
                width = sign_data.get('sign_width', 0)
                height = sign_data.get('sign_height', 0)
                size_key = f"{width}x{height}"

                if size_key not in sizes:
                    sizes[size_key] = 0
                    shape_size_examples[size_key] = sign_id
                sizes[size_key] += 1

                # Kształty
                shape = sign_data.get('sign_shape', 'unknown')
                if shape not in shapes:
                    shapes[shape] = 0
                shapes[shape] += 1

                # Kombinacje kształt-wymiar
                combination = f"{shape}_{size_key}"
                if combination not in shape_size_combinations:
                    shape_size_combinations[combination] = 0
                    shape_size_examples[combination] = sign_id
                shape_size_combinations[combination] += 1

                # Analiza padding
                if width < height:
                    padding_examples.append(sign_id)
                else:
                    no_padding_examples.append(sign_id)

        shapes_list = {}
        for size in sorted(sizes.keys()):
            shape_count = {}
            for combination, count in shape_size_combinations.items():
                if combination.endswith(f"_{size}"):
                    shape = combination.split('_', 1)[0]
                    shape_count[shape] = count
            if shape_count:
                shapes_list[size] = ', '.join([f"{shape}({count})" for shape, count in shape_count.items()])

        ConsoleStyle.print_stats(rsort(sizes),
                                 f"📏 SIGN SIZES ([{len(sizes)}])")
        ConsoleStyle.print_stats(rsort(shapes),
                                 f"🔷 SIGN SHAPES ([{len(shapes)}])")
        ConsoleStyle.print_stats(rsort(shape_size_combinations),
                                 f"🔀 SHAPE AND DIMENSION COMBINATIONS ([{len(shape_size_combinations)}])")
        ConsoleStyle.print_stats({
            f"signs 'width < height' → adds padding": f"[{len(padding_examples)}] ({', '.join(padding_examples)})",
            f"signs 'width >= height' → no changes": f"[{len(no_padding_examples)}] ({', '.join(no_padding_examples)})",
        }, f" 📐 PADDING ANALYSIS")
        ConsoleStyle.print_stats(shapes_list, f"📊 SHAPE DISTRIBUTION IN SIZES ([{len(shapes_list)}])")

        # 1. SPRAWDŹ DEFINICJE BLOKÓW
        categories = get_db_categories()
        database_blocks = set()
        database_missing_blocks = set()
        file_blocks_found = 0
        file_blocks_missing = set()

        # Zbierz wszystkie znaki z bazy danych
        for category in categories:
            signs = data['road_signs'][category]['signs']
            for sign_id in signs.keys():
                database_blocks.add(sign_id)
                block_path = f"BP/blocks/{category.lower()}/{sign_id}.block.json"
                if os.path.exists(block_path):
                    file_blocks_found += 1
                else:
                    file_blocks_missing.add(sign_id)
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

        file_extra_blocks = file_block_signs - database_blocks
        database_extra_blocks = database_blocks - file_block_signs

        stats = {ConsoleStyle.success("Loaded"): f"[{file_blocks_found}]"}
        stats[ConsoleStyle.error(f"Missing blocks") if file_blocks_missing else ConsoleStyle.info(
            f"Missing blocks")] \
            = f"[{len(file_blocks_missing)}] ({', '.join([f'{name}' for name in sorted(file_blocks_missing)])})" if file_blocks_missing else "0"
        if file_blocks_missing:
            warnings.append(f"Missing [{len(file_blocks_missing)}] file blocks")
        stats[ConsoleStyle.error("Extra blocks") if file_extra_blocks else ConsoleStyle.info(
            "Extra blocks")] \
            = f"[{len(file_extra_blocks)}] ({', '.join([f'{name}' for name in sorted(file_extra_blocks)])})" if file_extra_blocks else "0"
        if file_extra_blocks:
            warnings.append(f'Extra [{len(file_extra_blocks)}] file blocks')
        stats[ConsoleStyle.error("Missing blocks in database") if database_missing_blocks else ConsoleStyle.info(
            "Missing blocks in database")] \
            = f"[{len(database_missing_blocks)}] ({', '.join([f'{name}' for name in sorted(database_missing_blocks)])})" if database_missing_blocks else "0"
        if database_missing_blocks:
            warnings.append(f"Missing [{len(database_missing_blocks)}] database blocks")
        stats[ConsoleStyle.error("Extra blocks in database") if database_extra_blocks else ConsoleStyle.info(
            "Extra blocks in database")] \
            = f"[{len(database_extra_blocks)}] ({', '.join([f'{name}' for name in sorted(database_extra_blocks)])})" if database_extra_blocks else "0"
        if database_extra_blocks:
            warnings.append(f'Extra [{len(database_extra_blocks)}] database blocks')
        terrain_textures_found = 0
        missing_png_textures = set()
        for texture_id, texture_info in terrain_data['texture_data'].items():
            texture_path = texture_info['textures']
            full_path = f"RP/{texture_path}"
            if os.path.exists(full_path):
                terrain_textures_found += 1
            else:
                missing_png_textures.add(texture_id)
        stats[ConsoleStyle.info("Textures from blocks")] = f"[{len(terrain_data['texture_data'])}]"
        stats[ConsoleStyle.info(
            "Textures by terrain_texture.json (with existing PNG files)")] = f"[{terrain_textures_found}]"
        stats[ConsoleStyle.error("Missing files") if missing_png_textures else ConsoleStyle.info("Missing files")] \
            = f"[{len(missing_png_textures)}] ({', '.join([f'{name}' for name in sorted(missing_png_textures)])})" if missing_png_textures else "0"
        if missing_png_textures:
            warnings.append(f'Missing [{len(missing_png_textures)}] PNG textures')
        ConsoleStyle.print_stats(stats, "📄 BLOCK DEFINITIONS")

        # Test 2: Sprawdź, czy są pliki PNG bez definicji
        stats = {}
        all_png_files = set()

        # Sprawdź tekstury znaków w katalogu averse
        for category in get_file_categories():
            texture_dir = f'RP/textures/blocks/averse/{category}'
            if os.path.exists(texture_dir):
                for filename in os.listdir(texture_dir):
                    if filename.endswith('.png'):
                        relative_path = f"textures/blocks/averse/{category}/{filename}"
                        all_png_files.add(relative_path)

        # Sprawdź tekstury tła w katalogu reverse
        reverse_dir = 'RP/textures/blocks/reverse'
        if os.path.exists(reverse_dir):
            for filename in os.listdir(reverse_dir):
                if filename.endswith('.png'):
                    relative_path = f"textures/blocks/reverse/{filename}"
                    all_png_files.add(relative_path)

        # Znajdź ścieżki tekstur z terrain_texture.json
        terrain_texture_paths = set()
        for texture_id, texture_info in terrain_data['texture_data'].items():
            terrain_texture_paths.add(texture_info['textures'])

        # Znajdź nadmiarowe pliki PNG
        extra_png_files = all_png_files - terrain_texture_paths

        stats[ConsoleStyle.success(
            "Textures by PNG files (with definition in terrain_texture.json)")] = f'[{len(all_png_files)}]'
        if extra_png_files:
            warnings.append(f'Missing [{len(extra_png_files)}] definitions terrain_texture.json')
            stats[ConsoleStyle.error(
                "  Missing definitions terrain_texture.json")] = f'[{len(extra_png_files)}] {', '.join([f'{name}' for name in sorted(extra_png_files)])}'

        # Sprawdź PNG w bazie danych kontra pliki
        database_blocks = set()
        for category in data['road_signs']:
            for sign_id in data['road_signs'][category]['signs']:
                database_blocks.add(sign_id)

        file_png_signs = set()
        for category in get_file_categories():
            texture_dir = f'RP/textures/blocks/averse/{category}'
            if os.path.exists(texture_dir):
                for filename in os.listdir(texture_dir):
                    if filename.endswith('.png'):
                        sign_id = filename.replace('.png', '')
                        file_png_signs.add(sign_id)

        database_missing_pngs = database_blocks - file_png_signs
        file_extra_pngs = file_png_signs - database_blocks

        stats[ConsoleStyle.info("In database")] = f'[{len(database_blocks)}]'
        stats[ConsoleStyle.error("Missing db PNGs") if database_missing_pngs else ConsoleStyle.info("Missing db PNGs")] \
            = f"[{len(database_missing_pngs)}] {', '.join([f'{name}' for name in sorted(database_missing_pngs)])}" if database_missing_pngs else "0"
        if database_missing_pngs:
            warnings.append(f"Missing [{len(database_missing_pngs)}] PNG files in database")
        stats[ConsoleStyle.error("Extra file PNGs") if file_extra_pngs else ConsoleStyle.info("Extra file PNGs")] \
            = f"[{len(file_extra_pngs)}] {', '.join([f'{name}' for name in sorted(file_extra_pngs)])}" if file_extra_pngs else "0"
        if file_extra_pngs:
            warnings.append(f"Extra [{len(file_extra_pngs)}] PNG files in database")

        ConsoleStyle.print_stats(stats, "🎨 TEXTURES & PNG FILES")

        # Test 3: Sprawdź, czy wszystkie używane tekstury z bloków są zdefiniowane
        stats = {}
        block_textures = set()
        for category in get_file_categories():
            block_dir = f'BP/blocks/{category}'
            if os.path.exists(block_dir):
                for filename in os.listdir(block_dir):
                    if filename.endswith('.block.json'):
                        block_path = os.path.join(block_dir, filename)
                        try:
                            with open(block_path, 'r') as f:
                                block_data = json.load(f)

                            material_instances = block_data.get('minecraft:block', {}).get('components', {}).get(
                                'minecraft:material_instances', {})
                            for face, material in material_instances.items():
                                if 'texture' in material:
                                    texture_name = material['texture']
                                    # Nie usuwaj prefiksu – porównuj z pełnymi nazwami z terrain_texture.json
                                    block_textures.add(texture_name)
                        except:
                            pass

        terrain_texture_keys = set(terrain_data['texture_data'].keys())
        missing_in_terrain = block_textures - terrain_texture_keys
        unused_textures = terrain_texture_keys - block_textures

        stats[ConsoleStyle.info("Block textures referenced in block definitions")] = f"[{len(block_textures)}]"
        stats[ConsoleStyle.info("Found in terrain_texture.json")] = f"[{len(block_textures - missing_in_terrain)}]"

        if missing_in_terrain:
            warnings.append(f"Missing [{len(missing_in_terrain)}] items textures in terrain_texture.json")
            stats[ConsoleStyle.error("Missing from terrain_texture.json") if missing_in_terrain else ConsoleStyle.info(
                "Missing from terrain_texture.json")] \
                = f"[{len(missing_in_terrain)}] {', '.join([f'{name}' for name in sorted(missing_in_terrain)])}" if missing_in_terrain else "0"

        stats[ConsoleStyle.error("Unused in terrain_texture.json") if unused_textures else ConsoleStyle.info(
            "Unused in terrain_texture.json")] \
            = f"[{len(unused_textures)}] {', '.join([f'{name}' for name in sorted(unused_textures)])}" if unused_textures else "0"
        if unused_textures:
            warnings.append(f"Unused [{len(unused_textures)}] items textures in terrain_texture.json")

        ConsoleStyle.print_stats(stats, "🔗 BLOCK TEXTURES IN TERRAIN")

        # 2. SPRAWDŹ POLE SHAPE W BAZIE DANYCH

        stats = {}
        signs_with_shape = 0
        signs_without_shape = set()
        shape_types = {}

        for category in data['road_signs']:
            for sign_id, sign_data in data['road_signs'][category]['signs'].items():
                if 'sign_shape' in sign_data:
                    signs_with_shape += 1
                    shape = sign_data['sign_shape']
                    if shape not in shape_types:
                        shape_types[shape] = 0
                    shape_types[shape] += 1
                else:
                    signs_without_shape.add(sign_id)
        stats[ConsoleStyle.info(f"Signs with shape field")] = f"[{signs_with_shape}]"
        stats[ConsoleStyle.error("Signs without shape field") if signs_without_shape else ConsoleStyle.info(
            "Signs without shape field")] \
            = f"[{len(signs_without_shape)}] ({', '.join([f'{name}' for name in sorted(signs_without_shape)])})" if signs_without_shape else "0"
        if signs_without_shape:
            warnings.append(f"Missing [{len(signs_without_shape)}] signs without shape field")
        stats[ConsoleStyle.info("Shape types")] \
            = f"{', '.join([f'{shape}({count})' for shape, count in shape_types.items()])}"
        ConsoleStyle.print_stats(stats, "🔷 SHAPE FIELD VERIFICATION")

        # 4. SPRAWDŹ MODELE 3D
        models_dir = "RP/models/blocks"
        model_dimensions = {}
        used_models = set()
        unused_models = set()

        if os.path.exists(models_dir):
            for filename in os.listdir(models_dir):
                if filename.endswith('.geo.json'):
                    model_name = filename.replace('.geo.json', '')
                    model_path = os.path.join(models_dir, filename)
                    width, height = get_model_dimensions(model_path)
                    if width and height:
                        model_dimensions[model_name] = (width, height)

        # Sprawdź, które modele są używane
        for category in get_file_categories():
            block_dir = f'BP/blocks/{category}'
            if os.path.exists(block_dir):
                for filename in os.listdir(block_dir):
                    if filename.endswith('.block.json'):
                        block_path = os.path.join(block_dir, filename)
                        try:
                            with open(block_path, 'r') as f:
                                block_data = json.load(f)

                            geometry = block_data.get('minecraft:block', {}).get('components', {}).get(
                                'minecraft:geometry',
                                '')
                            if geometry:
                                model_name = geometry.replace('geometry.', '')
                                used_models.add(model_name)
                        except:
                            pass

        # Znajdź nieużywane modele
        for model_name in model_dimensions:
            if model_name not in used_models:
                unused_models.add(model_name)

        stats = {
            ConsoleStyle.info(f"Loaded"): f"[{len(model_dimensions)}]",
            ConsoleStyle.info(f"Used"): f"[{len(used_models)}]",
        }

        if unused_models:
            warnings.append(f'Unused [{len(unused_models)}] models')
            stats[ConsoleStyle.error(
                "Unused")] = f"[{len(unused_models)}] {', '.join([f'{name}' for name in sorted(unused_models)])}"

        stats[ConsoleStyle.info(
            "Model dimensions")] = f"{', '.join([f'{name}({w}x{h})' for name, (w, h) in model_dimensions.items()])}"
        ConsoleStyle.print_stats(stats, "🎲 3D MODELS")

        # Sprawdź kompatybilność
        stats = {}
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
                            with open(block_path, 'r') as f:
                                block_data = json.load(f)

                            # Sprawdź geometrię
                            geometry = block_data.get('minecraft:block', {}).get('components', {}).get(
                                'minecraft:geometry',
                                '')
                            if geometry:
                                model_name = geometry.replace('geometry.', '')

                                # Sprawdź, czy model istnieje lub znajdź podobny
                                actual_model_name = find_similar_model(model_name, model_dimensions.keys())
                                if actual_model_name:
                                    model_width, model_height = model_dimensions[actual_model_name]
                                    if actual_model_name != model_name:
                                        print_if_not_quiet(ConsoleStyle.warning(
                                            f"    Note: {sign_id} using {actual_model_name} instead of {model_name}"))
                                else:
                                    missing_models.append(f"{sign_id} (model: {model_name})")

                            # Sprawdź tekstury
                            material_instances = block_data.get('minecraft:block', {}).get('components', {}).get(
                                'minecraft:material_instances', {})
                            for face, material in material_instances.items():
                                if 'texture' in material:
                                    texture_name = material['texture']
                                    # Nie usuwaj prefiksu – porównuj z pełnymi nazwami z terrain_texture.json

                                    if texture_name not in terrain_data['texture_data']:
                                        missing_textures.append(f"{sign_id} (texture: {texture_name})")

                        except Exception as e:
                            compatibility_issues.append(f"{sign_id} (error: {str(e)})")

        stats[ConsoleStyle.info(
            "Blocks checked")] = f"[{len([f for f in os.listdir('BP/blocks/a') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/b') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/c') if f.endswith('.block.json')]) + len([f for f in os.listdir('BP/blocks/d') if f.endswith('.block.json')])}]"

        if texture_model_mismatches:
            warnings.append(f'Texture-model mismatch: {len(texture_model_mismatches)}')
            stats[ConsoleStyle.error("Texture-model mismatches") if texture_model_mismatches else ConsoleStyle.info(
                "Texture-model mismatches")] \
                = f"[{len(texture_model_mismatches)}] {', '.join([f'{name}' for name in sorted(texture_model_mismatches)])}" if texture_model_mismatches else "0"

        stats[ConsoleStyle.error("Missing models") if missing_models else ConsoleStyle.info("Missing models")] \
            = f"[{len(missing_models)}] {', '.join([f'{name}' for name in sorted(missing_models)])}" if missing_models else "0"
        if missing_models:
            warnings.append(f'Missing models: {len(missing_models)}')

        stats[ConsoleStyle.error("Missing textures") if missing_textures else ConsoleStyle.info("Missing textures")] \
            = f"[{len(missing_textures)}] {', '.join([f'{name}' for name in sorted(missing_textures)])}" if missing_textures else "0"
        if missing_textures:
            warnings.append(f'Missing textures: {len(missing_textures)}')

        stats[ConsoleStyle.error("Compatibility issues") if compatibility_issues else ConsoleStyle.info(
            "Compatibility issues")] \
            = f"[{len(compatibility_issues)}] {', '.join([f'{name}' for name in sorted(compatibility_issues)])}" if compatibility_issues else "0"
        if compatibility_issues:
            warnings.append(f'Compatibility issues: {len(compatibility_issues)}')

        ConsoleStyle.print_stats(stats, "🔧 BLOCKS COMPATIBILITY")

    except FileNotFoundError as e:
        ConsoleStyle.print_section("⏹️ BLOCKS COMPREHENSIVE VERIFICATION")
        print_if_not_quiet(ConsoleStyle.error("Database file not found"))
        errors.append(e)

    return errors, warnings


def main():
    """Main verification function"""
    ConsoleStyle.print_section("🔍 COMPREHENSIVE PROJECT VERIFICATION")

    all_errors = []
    all_warnings = []

    # Run all verification functions
    verifications = [
        verify_manifests,
        verify_config,
        verify_project_structure,
        verify_database,
        verify_translations,
        verify_blocks_comprehensive,
        verify_vertical_alignment,
        count_project_files
    ]

    for verify_func in verifications:
        try:
            errors, warnings = verify_func()
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        except Exception as e:
            all_errors.append(f"Error in {verify_func.__name__}: {e}")

    # Print summary
    ConsoleStyle.print_section("📋 VERIFICATION SUMMARY")

    if all_errors:
        print_if_not_quiet(ConsoleStyle.error(f"Found [{len(all_errors)}] errors: {', '.join(all_errors)}"))
    else:
        print_if_not_quiet(ConsoleStyle.success("No errors found!"))

    if all_warnings:
        print_if_not_quiet(ConsoleStyle.warning(f"Found [{len(all_warnings)}] warnings: {', '.join(all_warnings)}"))
    else:
        print_if_not_quiet(ConsoleStyle.success("No warnings found!"))

    # Exit with appropriate code
    if all_errors:
        print_if_not_quiet(ConsoleStyle.error(f"Verification failed with [{len(all_errors)}] errors"))
        sys.exit(1)
    else:
        print_if_not_quiet(ConsoleStyle.success("Verification passed! Project is ready for building."))
        sys.exit(0)


if __name__ == "__main__":
    main()
