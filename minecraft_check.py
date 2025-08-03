#!/usr/bin/env python3
"""
Biblioteka z funkcjami weryfikacji strukturę paczki Minecraft
"""
import json
import os
import sys
from typing import Any, Dict, List, Callable, Tuple

from console_utils import ConsoleStyle, print_if_not_quiet


class MinecraftUtils:
    """Klasa z funkcjami weryfikacji struktury paczki Minecraft"""

    namespace = None
    DATABASE_FILE_NAME = 'database.json'

    # Lista wbudowanych tekstur Minecraft Bedrock Edition
    BUILTIN_TEXTURES_FILE = 'minecraft_textures.json'

    @staticmethod
    def _load_builtin_textures():
        """Załaduj wbudowane tekstury z zewnętrznego pliku"""
        try:
            data = MinecraftUtils.load_json_file(MinecraftUtils.BUILTIN_TEXTURES_FILE)
            if data and 'builtin_textures' in data:
                return set(data['builtin_textures'])
            else:
                print(ConsoleStyle.warning(f"Nieprawidłowa struktura pliku [{MinecraftUtils.BUILTIN_TEXTURES_FILE}]"))
                return set()
        except Exception as e:
            print(ConsoleStyle.error(f"Błąd podczas ładowania [{MinecraftUtils.BUILTIN_TEXTURES_FILE}]: {e}"))
            return set()

    @staticmethod
    def get_builtin_textures():
        """Pobierz wbudowane tekstury (singleton pattern)"""
        if not hasattr(MinecraftUtils, '_builtin_textures_cache'):
            MinecraftUtils._builtin_textures_cache = MinecraftUtils._load_builtin_textures()
        return MinecraftUtils._builtin_textures_cache

    @staticmethod
    def load_json_file(file_path: str):
        """Load a JSON file and return its content"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ===== FUNKCJE POMOCNICZE =====

    @staticmethod
    def _get_bp_blocks():
        """Pobierz wszystkie bloki z BP"""
        blocks = {}
        for root, dirs, files in os.walk("BP/blocks"):
            for file in files:
                if file.endswith('.block.json'):
                    file_path = os.path.join(root, file)
                    data = MinecraftUtils.load_json_file(file_path)
                    if data:
                        blocks[file.replace('.block.json', '')] = data
        return blocks

    @staticmethod
    def _get_bp_items():
        """Pobierz wszystkie itemy z BP"""
        items = {}
        for root, dirs, files in os.walk("BP/items"):
            for file in files:
                if file.endswith('.item.json'):
                    file_path = os.path.join(root, file)
                    data = MinecraftUtils.load_json_file(file_path)
                    if data:
                        items[file.replace('.item.json', '')] = data
        return items

    @staticmethod
    def _get_rp_block_model_dimensions():
        model_dimensions = {}
        for root, dirs, files in os.walk("RP/models/blocks"):
            for file in files:
                if file.endswith('.geo.json'):
                    model_name = file.replace('.geo.json', '')
                    model_path = os.path.join(root, file)
                    width, height = MinecraftUtils._get_model_dimensions(model_path)
                    if width and height:
                        model_dimensions[model_name] = (width, height)
        return model_dimensions

    @staticmethod
    def _get_model_dimensions(model_path):
        """Pobierz wymiary modelu z pliku .geo.json"""
        model_data = MinecraftUtils.load_json_file(model_path)
        if 'minecraft:geometry' in model_data and isinstance(model_data['minecraft:geometry'], list) and len(
                model_data['minecraft:geometry']) > 0:
            geometry = model_data['minecraft:geometry'][0]
            if 'description' in geometry:
                description = geometry['description']
                if 'texture_width' in description and 'texture_height' in description:
                    return description['texture_width'], description['texture_height']

        return None, None

    @staticmethod
    def _find_category_for_block_id(block_id):
        """Znajdź kategorię dla znaku w bazie danych"""
        if not os.path.exists(MinecraftUtils.DATABASE_FILE_NAME):
            return None
        data = MinecraftUtils.load_json_file('database.json')
        if not data:
            return None

        for category in data['categories']:
            if block_id in data['categories'][category]['blocks']:
                return category

        return None

    @staticmethod
    def _find_similar_model(model_name, available_models):
        """Znajdź podobny model, jeśli dokładny nie istnieje"""
        if model_name in available_models:
            return model_name

        # Próbuj znaleźć podobny model
        base_name = model_name.split('_')[0]  # np. "road_sign_rectangle"
        for available_model in available_models:
            if available_model.startswith(base_name):
                return available_model

        return None

    # ===== WSPÓLNE FUNKCJE POMOCNICZE =====

    @staticmethod
    def _verify_texture_mappings():
        """Wspólna weryfikacja mapowań terrain_texture.json"""
        try:
            terrain_data = MinecraftUtils.load_json_file('RP/textures/terrain_texture.json')
        except FileNotFoundError:
            terrain_data = []
        try:
            item_data = MinecraftUtils.load_json_file('RP/textures/item_texture.json')
        except FileNotFoundError:
            item_data = {}
        if not terrain_data and not item_data:
            return [], [], [], []

        missing_textures = []
        valid_textures = []

        groups = {
            'blocks': terrain_data.get('texture_data', {}),
            'items': item_data.get('texture_data', {})
        }

        for key, data in groups.items():
            for texture_id, texture_info in data.items():
                if texture_id.startswith("minecraft:") or texture_id in MinecraftUtils.get_builtin_textures():
                    continue
                texture_path = texture_info.get('textures')
                if texture_path:
                    full_path = os.path.join("RP/", texture_path)
                    if os.path.exists(full_path):
                        valid_textures.append(texture_id)
                    elif os.path.exists(full_path + '.png'):
                        valid_textures.append(texture_id)
                        groups[key][texture_id]['textures'] = texture_path + '.png'
                    else:
                        missing_textures.append((texture_id, texture_path))

        return valid_textures, missing_textures, groups['blocks'], groups['items']

    @staticmethod
    def _verify_png_files():
        """Wspólna weryfikacja plików PNG"""
        all_png_files = set()

        for root, dirs, files in os.walk("RP/textures/"):
            for file in files:
                if file.endswith('.png'):
                    full_path = os.path.join(root, file).replace('RP/', '')
                    all_png_files.add(full_path)

        return all_png_files

    @staticmethod
    def _verify_material_instances(block_data):
        """Wspólna weryfikacja material_instances w bloku"""
        textures = []

        # Sprawdź główne material_instances w components
        material_instances = block_data.get('minecraft:block', {}).get('components', {}).get(
            'minecraft:material_instances', {})
        for face, material in material_instances.items():
            if 'texture' in material:
                texture_name = material['texture']
                textures.append((face, texture_name))

        # Sprawdź material_instances w permutations (lista)
        permutations = block_data.get('minecraft:block', {}).get('permutations', [])
        for permutation in permutations:
            permutation_material_instances = permutation.get('components', {}).get('minecraft:material_instances', {})
            for face, material in permutation_material_instances.items():
                if 'texture' in material:
                    texture_name = material['texture']
                    textures.append((face, texture_name))

        return textures

    @staticmethod
    def _verify_icon(item_data):
        """Wspólna weryfikacja material_instances w bloku"""
        return item_data.get('minecraft:item', {}).get('components', {}).get(
            'minecraft:icon', {})

    @staticmethod
    def _verify_block_structure(block_id: str, block_data):
        """Wspólna weryfikacja struktury bloku"""
        errors = []
        warnings = []

        # Check required structure
        if 'minecraft:block' not in block_data:
            errors.append(f"Missing [minecraft:block] section in [{block_id}] block")
            return errors, warnings

        block_data_section = block_data['minecraft:block']

        # Check description
        if 'description' not in block_data_section:
            errors.append(f"Missing [description] section in [{block_id}] block")
            return errors, warnings

        description = block_data_section['description']

        # Check identifier
        if 'identifier' not in description:
            errors.append(f"Missing [identifier] field in [{block_id}] block")
        else:
            identifier = description['identifier']
            if ':' not in identifier:
                errors.append(f"Invalid identifier format (should be [namespace:name]) in [{block_id}] block")

        # Check components
        if 'components' not in block_data_section:
            errors.append(f"Missing [components] section in [{block_id}] block")
        else:
            components = block_data_section['components']
            if 'minecraft:material_instances' not in components:
                errors.append(f"Missing [minecraft:material_instances] section in [{block_id}] block")

        return errors, warnings

    @staticmethod
    def _get_database_block_ids():
        """Pobierz wszystkie bloki z bazy danych"""

        data = MinecraftUtils.load_json_file(MinecraftUtils.DATABASE_FILE_NAME)
        if not data:
            return set()

        database_block_ids = set()
        for category in data['categories']:
            signs = data['categories'][category]['blocks']
            for block_id in signs.keys():
                database_block_ids.add(block_id)

        return database_block_ids

    # ===== SPECJALIZOWANE FUNKCJE WERYFIKACJI =====

    @staticmethod
    def _verify_block_structure_integrity():
        """1. Weryfikacja struktury bloków i modeli"""
        errors = []
        warnings = []

        blocks_loaded = []
        blocks_with_errors = []

        for block_id, block_data in MinecraftUtils._get_bp_blocks().items():
            blocks_loaded.append(block_id)
            structure_errors, structure_warnings = MinecraftUtils._verify_block_structure(block_id, block_data)
            errors.extend(structure_errors)
            warnings.extend(structure_warnings)

            if structure_errors:
                blocks_with_errors.append(block_id)

        ConsoleStyle.print_stats({
            ConsoleStyle.info("Blocks loaded"): f"[{len(blocks_loaded)}]",
            ConsoleStyle.error("Blocks with errors") if blocks_with_errors else ConsoleStyle.info("Blocks with errors"):
                f"[{len(blocks_with_errors)}] ({', '.join(blocks_with_errors)})" if blocks_with_errors else "0",
        }, "BLOCK STRUCTURE INTEGRITY", icon='🔳')

        return errors, warnings

    @staticmethod
    def _verify_database_block_coverage(database_block_ids):
        """2. Weryfikacja czy zdefiniowane w bazie bloki istnieją"""
        errors = []
        warnings = []
        stats = {}

        file_blocks_missing = set()
        file_blocks_found = 0

        for block_id in database_block_ids:
            category = MinecraftUtils._find_category_for_block_id(block_id)
            if category:
                block_path = f"BP/blocks/{category.lower()}/{block_id}.block.json"
                if os.path.exists(block_path):
                    file_blocks_found += 1
                else:
                    file_blocks_missing.add(block_id)

        stats[ConsoleStyle.info("Found blocks")] = f"[{file_blocks_found}]"
        stats[ConsoleStyle.info("Total in database")] = f"[{len(database_block_ids)}]"
        stats[ConsoleStyle.error("Missing blocks") if file_blocks_missing else ConsoleStyle.info("Missing blocks")] = \
            f"[{len(file_blocks_missing)}] ({', '.join(sorted(file_blocks_missing))})" if file_blocks_missing else "0"
        if file_blocks_missing:
            errors.append(
                f"Missing [{len(file_blocks_missing)}] file blocks: {', '.join(sorted(file_blocks_missing))}")

        ConsoleStyle.print_stats(stats, "DATABASE BLOCK COVERAGE", icon="📄")

        return errors, warnings

    @staticmethod
    def _verify_extra_block_files(database_block_ids):
        """3. Weryfikacja czy są bloki niezdefiniowane w bazie"""
        errors = []
        warnings = []
        stats = {}

        file_block_ids = MinecraftUtils._get_bp_blocks().keys()
        file_extra_blocks = file_block_ids - database_block_ids

        stats[ConsoleStyle.info("Total file blocks")] = f"[{len(file_block_ids)}]"
        stats[ConsoleStyle.info("Total database blocks")] = f"[{len(database_block_ids)}]"
        if database_block_ids:
            stats[ConsoleStyle.warning("Extra blocks") if file_extra_blocks else ConsoleStyle.info("Extra blocks")] \
                = f"[{len(file_extra_blocks)}] ({', '.join(sorted(file_extra_blocks))})" if file_extra_blocks else "0"
            if file_extra_blocks:
                warnings.append(f"Extra [{len(file_extra_blocks)}] file blocks: {', '.join(sorted(file_extra_blocks))}")

        ConsoleStyle.print_stats(stats, "EXTRA BLOCK FILES", icon="📁")

        return errors, warnings

    @staticmethod
    def _verify_model_existence():
        """4. Weryfikacja czy zdefiniowane w blokach modele istnieją"""
        errors = []
        warnings = []
        stats = {}

        model_dimensions = MinecraftUtils._get_rp_block_model_dimensions()
        missing_models = []

        # Sprawdź modele używane w blokach
        for block_id, block_data in MinecraftUtils._get_bp_blocks().items():
            geometry = block_data.get('minecraft:block', {}).get('components', {}).get(
                'minecraft:geometry', '')
            if geometry:
                model_name = geometry.replace('geometry.', '')

                # Sprawdź, czy model istnieje
                actual_model_name = MinecraftUtils._find_similar_model(model_name,
                                                                       model_dimensions.keys())
                if not actual_model_name:
                    missing_models.append(f"{block_id} (model: {model_name})")

        stats[ConsoleStyle.info("Available models")] = f"[{len(model_dimensions)}]"
        stats[ConsoleStyle.error("Missing models") if missing_models else ConsoleStyle.info("Missing models")] \
            = f"[{len(missing_models)}] {', '.join(sorted(missing_models))}" if missing_models else "0"
        if missing_models:
            errors.append(f"Missing models: {len(missing_models)}")
        stats[ConsoleStyle.info(
            "Model dimensions")] = f"{', '.join([f'{name}({w}x{h})' for name, (w, h) in model_dimensions.items()])}"

        ConsoleStyle.print_stats(stats, "MODEL EXISTENCE", icon="🎲")

        return errors, warnings

    @staticmethod
    def _verify_model_usage():
        """5. Weryfikacja czy zdefiniowane modele są używane przez bloki"""
        errors = []
        warnings = []
        stats = {}

        model_dimensions = MinecraftUtils._get_rp_block_model_dimensions()
        used_models = set()
        unused_models = set()

        # Sprawdź, które modele są używane
        for block_id, block_data in MinecraftUtils._get_bp_blocks().items():

            geometry = block_data.get('minecraft:block', {}).get('components', {}).get(
                'minecraft:geometry', '')
            if geometry:
                model_name = geometry.replace('geometry.', '')
                used_models.add(model_name)

        # Znajdź nieużywane modele
        for model_name in model_dimensions.keys():
            if model_name not in used_models:
                unused_models.add(model_name)

        stats[ConsoleStyle.info("Total models")] = f"[{len(model_dimensions)}]"
        stats[ConsoleStyle.info("Used models")] = f"[{len(used_models)}]"
        stats[ConsoleStyle.warning("Unused models") if unused_models else ConsoleStyle.info("Unused models")] \
            = f"[{len(unused_models)}] {', '.join(sorted(unused_models))}" if unused_models else "0"
        if unused_models:
            warnings.append(f"Unused [{len(unused_models)}] models: {', '.join(sorted(unused_models))}")

        ConsoleStyle.print_stats(stats, "MODEL USAGE", icon="🎲")

        return errors, warnings

    @staticmethod
    def _verify_texture_png_existence():
        """6. Weryfikacja czy zdefiniowane tekstury mają pliki PNG"""
        errors = []
        warnings = []
        stats = {}

        # Użyj wspólnej funkcji do weryfikacji terrain_texture.json
        valid_textures, missing_textures, terrain_texture_mappings, item_texture_mappings = MinecraftUtils._verify_texture_mappings()

        stats[ConsoleStyle.info(
            "Total defined terrain textures")] = f"[{len(terrain_texture_mappings)}]" if terrain_texture_mappings else "0"
        stats[ConsoleStyle.info(
            "Total defined item textures")] = f"[{len(item_texture_mappings)}]" if item_texture_mappings else "0"
        stats[ConsoleStyle.success("Valid textures")] = f"[{len(valid_textures)}]" if valid_textures else "0"
        stats[ConsoleStyle.error("Missing PNG files") if missing_textures else ConsoleStyle.info("Missing PNG files")] \
            = f"[{len(missing_textures)}] ({', '.join([f'{texture_id} -> {texture_name}' for texture_id, texture_name in missing_textures])})" if missing_textures else "0"
        if missing_textures:
            errors.append(
                f"Missing [{len(missing_textures)}] PNG files: {', '.join([f'{texture_id} -> {texture_name}' for texture_id, texture_name in missing_textures])}")

        ConsoleStyle.print_stats(stats, "TEXTURE PNG EXISTENCE", icon="🎨")

        return errors, warnings

    @staticmethod
    def _verify_png_definitions():
        """7. Weryfikacja czy pliki PNG mają definicje"""
        errors = []
        warnings = []
        stats = {}

        all_png_files = MinecraftUtils._verify_png_files()
        valid_textures, missing_textures, terrain_texture_mappings, item_texture_mappings = MinecraftUtils._verify_texture_mappings()

        texture_paths = set()
        for texture_id, texture_info in terrain_texture_mappings.items():
            texture_paths.add(texture_info['textures'])
        for texture_id, texture_info in item_texture_mappings.items():
            texture_paths.add(texture_info['textures'])

        # Znajdź nadmiarowe pliki PNG
        extra_png_files = all_png_files - texture_paths

        stats[ConsoleStyle.info("Total PNG files")] = f"[{len(all_png_files)}]"
        stats[ConsoleStyle.success("PNG files with definitions")] = f"[{len(all_png_files - extra_png_files)}]"
        stats[ConsoleStyle.error("PNG files without definitions") if extra_png_files else ConsoleStyle.info(
            "PNG files without definitions")] \
            = f"[{len(extra_png_files)}] {', '.join(sorted(extra_png_files))}" if extra_png_files else "0"
        if extra_png_files:
            errors.append(
                f"Missing [{len(extra_png_files)}] definitions for PNG files: {', '.join(sorted(extra_png_files))}")

        ConsoleStyle.print_stats(stats, "PNG DEFINITIONS", icon="🎨")

        return errors, warnings

    @staticmethod
    def _verify_block_texture_definitions():
        """8. Weryfikacja czy użyte w blokach tekstury są zdefiniowane"""
        errors = []
        warnings = []
        stats = {}

        block_textures = set()
        build_in_textures = set()
        valid_textures, missing_textures, terrain_texture_mappings, item_texture_mappings = MinecraftUtils._verify_texture_mappings()

        # Sprawdź tekstury używane w blokach
        for block_id, block_data in MinecraftUtils._get_bp_blocks().items():
            # Użyj wspólnej funkcji do weryfikacji material_instances
            textures = MinecraftUtils._verify_material_instances(block_data)
            for face, texture_name in textures:
                if texture_name.startswith("minecraft:") or texture_name in MinecraftUtils.get_builtin_textures():
                    build_in_textures.add(texture_name)
                else:
                    block_textures.add(texture_name)

        terrain_texture_keys = set(terrain_texture_mappings.keys())
        missing_in_terrain = block_textures - terrain_texture_keys
        unused_textures = terrain_texture_keys - block_textures

        stats[ConsoleStyle.info(
            "Build in block textures referenced")] = f"[{len(build_in_textures)}] {', '.join(sorted(build_in_textures))}" if build_in_textures else '0'
        stats[ConsoleStyle.info(
            "Custom block textures referenced")] = f"[{len(block_textures)}]" if block_textures else '0'
        stats[ConsoleStyle.error("Missing from terrain_texture.json") if missing_in_terrain else ConsoleStyle.info(
            "Missing from terrain_texture.json")] \
            = f"[{len(missing_in_terrain)}] {', '.join(sorted(missing_in_terrain))}" if missing_in_terrain else "0"
        if missing_in_terrain:
            errors.append(
                f"Missing [{len(missing_in_terrain)}] textures in terrain_texture.json: {', '.join(sorted(missing_in_terrain))}")

        stats[ConsoleStyle.warning("Unused in terrain_texture.json") if unused_textures else ConsoleStyle.info(
            "Unused in terrain_texture.json")] \
            = f"[{len(unused_textures)}] {', '.join(sorted(unused_textures))}" if unused_textures else "0"
        if unused_textures:
            warnings.append(
                f"Unused [{len(unused_textures)}] textures in terrain_texture.json: {', '.join(sorted(unused_textures))}")

        ConsoleStyle.print_stats(stats, "BLOCK TEXTURE DEFINITIONS", icon="🔗")

        return errors, warnings

    @staticmethod
    def _verify_item_texture_definitions():
        """8. Weryfikacja czy użyte w itemach tekstury są zdefiniowane"""
        errors = []
        warnings = []
        stats = {}

        item_textures = set()
        build_in_textures = set()
        valid_textures, missing_textures, terrain_texture_mappings, item_texture_mappings = MinecraftUtils._verify_texture_mappings()

        # Sprawdź tekstury używane w blokach
        for item_id, item_data in MinecraftUtils._get_bp_items().items():
            texture_name = MinecraftUtils._verify_icon(item_data)
            if texture_name.startswith("minecraft:") or texture_name in MinecraftUtils.get_builtin_textures():
                build_in_textures.add(texture_name)
            else:
                item_textures.add(texture_name)

        item_texture_keys = set(item_texture_mappings.keys())
        missing_in_item = item_textures - item_texture_keys
        unused_textures = item_texture_keys - item_textures

        stats[ConsoleStyle.info(
            "Build in textures referenced")] = f"[{len(build_in_textures)}] {', '.join(sorted(build_in_textures))}" if build_in_textures else '0'
        stats[
            ConsoleStyle.info("Custom item textures referenced")] = f"[{len(item_textures)}]" if item_textures else '0'
        stats[ConsoleStyle.error("Missing from item_texture.json") if missing_in_item else ConsoleStyle.info(
            "Missing from item_texture.json")] \
            = f"[{len(missing_in_item)}] {', '.join(sorted(missing_in_item))}" if missing_in_item else "0"
        if missing_in_item:
            errors.append(
                f"Missing [{len(missing_in_item)}] textures in item_texture.json: {', '.join(sorted(missing_in_item))}")

        stats[ConsoleStyle.warning("Unused in item_texture.json") if unused_textures else ConsoleStyle.info(
            "Unused in item_texture.json")] \
            = f"[{len(unused_textures)}] {', '.join(sorted(unused_textures))}" if unused_textures else "0"
        if unused_textures:
            warnings.append(
                f"Unused [{len(unused_textures)}] textures in item_texture.json: {', '.join(sorted(unused_textures))}")

        ConsoleStyle.print_stats(stats, "ITEM TEXTURE DEFINITIONS", icon="🔗")

        return errors, warnings

    # ===== GŁÓWNE FUNKCJE WERYFIKACJI =====

    @staticmethod
    def verify_blocks():
        """Verify all block files are valid and have required fields"""
        errors = []
        warnings = []

        # Uruchom wszystkie weryfikacje bloków
        structure_errors, structure_warnings = MinecraftUtils._verify_block_structure_integrity()
        errors.extend(structure_errors)
        warnings.extend(structure_warnings)

        try:
            database_block_ids = MinecraftUtils._get_database_block_ids()
        except FileNotFoundError:
            database_block_ids = {}

        if isinstance(database_block_ids, list):
            coverage_errors, coverage_warnings = MinecraftUtils._verify_database_block_coverage(database_block_ids)
            errors.extend(coverage_errors)
            warnings.extend(coverage_warnings)

            extra_errors, extra_warnings = MinecraftUtils._verify_extra_block_files(database_block_ids)
            errors.extend(extra_errors)
            warnings.extend(extra_warnings)

        return errors, warnings

    @staticmethod
    def verify_models():
        """Verify models and their compatibility with blocks"""
        errors = []
        warnings = []

        # Uruchom wszystkie weryfikacje modeli
        existence_errors, existence_warnings = MinecraftUtils._verify_model_existence()
        errors.extend(existence_errors)
        warnings.extend(existence_warnings)

        usage_errors, usage_warnings = MinecraftUtils._verify_model_usage()
        errors.extend(usage_errors)
        warnings.extend(usage_warnings)

        return errors, warnings

    @staticmethod
    def verify_textures():
        """Verify texture files and mappings with detailed analysis"""
        errors = []
        warnings = []

        # Uruchom wszystkie weryfikacje tekstur
        texture_errors, texture_warnings = MinecraftUtils._verify_block_texture_definitions()
        errors.extend(texture_errors)
        warnings.extend(texture_warnings)

        texture_errors, texture_warnings = MinecraftUtils._verify_item_texture_definitions()
        errors.extend(texture_errors)
        warnings.extend(texture_warnings)

        png_existence_errors, png_existence_warnings = MinecraftUtils._verify_texture_png_existence()
        errors.extend(png_existence_errors)
        warnings.extend(png_existence_warnings)

        png_def_errors, png_def_warnings = MinecraftUtils._verify_png_definitions()
        errors.extend(png_def_errors)
        warnings.extend(png_def_warnings)

        return errors, warnings

    @staticmethod
    def verify_manifests():
        """Weryfikuj pliki manifestów"""
        errors = []
        warnings = []

        manifest_files = [
            ("BP/manifest.json", "Behavior Pack"),
            ("RP/manifest.json", "Resource Pack")
        ]

        manifest_stats = {}

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
                        manifest_stats[ConsoleStyle.success(pack_type)] = f"Version {'.'.join(map(str, version))}"

                manifest_stats[ConsoleStyle.success(f"{pack_type} JSON")] = "Valid"

            except json.JSONDecodeError as e:
                errors.append(f"{pack_type} manifest is invalid JSON: {e}")
                manifest_stats[ConsoleStyle.error(pack_type)] = f"Invalid JSON: {e}"
            except Exception as e:
                errors.append(f"Error reading {pack_type} manifest: {e}")
                manifest_stats[ConsoleStyle.error(pack_type)] = f"Error: {e}"

        # Print statistics
        ConsoleStyle.print_stats(manifest_stats, "MANIFESTS VERIFICATION", icon="📋")

        return errors, warnings

    @staticmethod
    def verify_config():
        """Weryfikuj plik config.json"""

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
            config_stats = {}

            for field in required_fields:
                if field in data:
                    config_stats[ConsoleStyle.success(field)] = data[field]
                else:
                    config_stats[ConsoleStyle.error(field)] = "Missing"
                    errors.append(f"config.json missing required field: {field}")

            # Check namespace consistency
            if 'namespace' in data:
                MinecraftUtils.namespace = data['namespace']

                # Check if a namespace is used in block files
                namespace_used = False
                for block_id, block_data in MinecraftUtils._get_bp_blocks().items():
                    if 'minecraft:block' in block_data:
                        identifier = block_data['minecraft:block']['description'].get('identifier', '')
                        if identifier.startswith(f"{MinecraftUtils.namespace}:"):
                            namespace_used = True
                            break

                if namespace_used:
                    config_stats[ConsoleStyle.success("Namespace usage")] = "Found in blocks"
                else:
                    config_stats[ConsoleStyle.warning("Namespace usage")] = "Not found in blocks"
                    warnings.append(f"Namespace '{MinecraftUtils.namespace}' not found in block identifiers")

            config_stats[ConsoleStyle.success("JSON format")] = "Valid"

            # Print statistics
            ConsoleStyle.print_stats(config_stats, "CONFIG VERIFICATION", icon="⚙️")

        except json.JSONDecodeError as e:
            errors.append(f"config.json is invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading [config.json]: {e}")

        return errors, warnings

    @staticmethod
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

            stats[ConsoleStyle.info(f"/{rel_path}", icon='📁')] = f"[{len(files)}] files"
            total_files += len(files)

        ConsoleStyle.print_stats(stats, f"PROJECT FILES ([{total_files}])", icon="📦")

        return [], []

    @staticmethod
    def verify_project_structure():
        """Verify basic project structure"""
        state_required: int = 1
        state_optional: int = 2

        state_name = {
            state_required: 'required',
            state_optional: 'optional',
        }

        locations = {
            'config.json': state_required,
            'BP/': state_required,
            'BP/manifest.json': state_required,
            'BP/pack_icon.png': state_required,
            'RP/': state_required,
            'RP/manifest.json': state_required,
            'RP/pack_icon.png': state_required,
            'database.json': state_optional,
            'BP/item_catalog/crafting_item_catalog.json': state_optional,
            'RP/blocks.json': state_optional,
            'BP/blocks/': state_optional,
            'BP/items/': state_optional,
            'RP/models/': state_optional,
            'RP/models/blocks/': state_optional,
            'RP/models/items/': state_optional,
            'RP/sounds/': state_optional,
            'RP/sounds/sound_definitions.json': state_optional,
            'RP/sounds/blocks/': state_optional,
            'RP/sounds/items/': state_optional,
            'RP/textures/': state_optional,
            'RP/textures/terrain_texture.json': state_optional,
            'RP/textures/item_texture.json': state_optional,
            'RP/textures/blocks/': state_optional,
            'RP/textures/items/': state_optional,
            'RP/texts/': state_optional,
            'RP/texts/languages.json': state_optional,
        }

        errors = []
        warnings = []

        item_stats = {}
        for file_path, state in sorted(locations.items(), key=lambda item: item[0]):
            if os.path.exists(file_path):
                item_stats[ConsoleStyle.success(file_path, icon=f'📁' if file_path.endswith(
                    '/') else '📄')] = f"Found {state_name[state]}"
            else:
                item_stats[ConsoleStyle.error(file_path)] = f"Missing {state_name[state]}"
                if state == state_required:
                    errors.append(
                        f"Missing {state_name[state]} {'directory' if file_path.endswith('/') else 'file'}: {file_path}")
                else:
                    warnings.append(f"Missing {'directory' if file_path.endswith('/') else 'file'}: {file_path}")

        ConsoleStyle.print_stats(item_stats, "REQUIRED FILES & DIRECTORIES", icon="🗂️")

        return errors, warnings

    @staticmethod
    def verify_translations():
        """Verify localization files"""

        errors = []
        warnings = []

        # Check languages.json
        try:
            try:
                languages_list = MinecraftUtils.load_json_file('RP/texts/languages.json')
            except FileNotFoundError:
                languages_list = {}

            # languages.json is a list, not an object
            if isinstance(languages_list, list):
                ConsoleStyle.print_section(f"TRANSLATIONS ([{len(languages_list)}])", icon="🌐")

                # Wczytaj bloki
                project_block_translations = set()
                for block_id, block_data in MinecraftUtils._get_bp_blocks().items():
                    block_name = block_data['minecraft:block']['description']['identifier']
                    project_block_translations.add(block_name.replace(f'{MinecraftUtils.namespace}:', ''))

                # Wczytaj bazę danych
                database_block_ids = set()
                database_categories = set()
                if os.path.exists(MinecraftUtils.DATABASE_FILE_NAME):
                    database_file_content = MinecraftUtils.load_json_file(MinecraftUtils.DATABASE_FILE_NAME)
                    for category in database_file_content['categories']:
                        group_name = database_file_content['categories'][category]['crafting_group']
                        database_categories.add(f"{group_name}")
                        for block_id in database_file_content['categories'][category]['blocks']:
                            database_block_ids.add(block_id)

                # Check if language files exist
                for lang_name in languages_list:
                    lang_path = f"RP/texts/{lang_name}.lang"
                    lang_file_block_translations = set()
                    lang_file_category_translations = set()
                    stats = {}
                    with open(lang_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and '=' in line:
                                key = line.split('=', 1)[0].strip()
                                if key.startswith(f'tile.{MinecraftUtils.namespace}:') and key.endswith(
                                        '.name'):
                                    block_name = key.replace(f'tile.{MinecraftUtils.namespace}:',
                                                             '').replace('.name', '')
                                    lang_file_block_translations.add(block_name)
                                elif key.startswith(f'{MinecraftUtils.namespace}:'):
                                    # Kategorie mają format `namespace:category_name`
                                    category_name = key.replace(f'{MinecraftUtils.namespace}:', '')
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
                                        if name.startswith(f'{MinecraftUtils.namespace}:'):
                                            category_name = name.replace(f'{MinecraftUtils.namespace}:', '')
                                            project_category_translations.add(category_name)
                    except Exception as e:
                        print_if_not_quiet(ConsoleStyle.error(f"Error reading crafting catalog: {e}"))
                        warnings.append(f"Error reading crafting catalog: {e}")

                    stats[ConsoleStyle.info("Items in lang file")] \
                        = f"[{len(lang_file_category_translations) + len(lang_file_block_translations)}]"

                    stats[ConsoleStyle.info("Categories in lang file", 3)] \
                        = f"[{len(lang_file_category_translations)}]" if lang_file_category_translations else "0"
                    stats[ConsoleStyle.info("Blocks in lang file", 3)] \
                        = f"[{len(lang_file_block_translations)}]" if lang_file_block_translations else "0"

                    stats[ConsoleStyle.info("Items in project")] \
                        = f"[{len(project_category_translations) + len(project_block_translations)}]" if project_category_translations and project_block_translations else "0"
                    stats[ConsoleStyle.info("Categories in project", 3)] \
                        = f"[{len(project_category_translations)}]" if project_category_translations else "0"
                    stats[ConsoleStyle.info("Blocks in project", 3)] \
                        = f"[{len(project_block_translations)}]" if project_block_translations else "0"

                    lang_file_extra_categories = lang_file_category_translations - project_category_translations
                    stats[ConsoleStyle.warning(
                        "Extra categories in lang file") if lang_file_extra_categories else ConsoleStyle.info(
                        "Extra categories in lang file")] \
                        = f"[{len(lang_file_extra_categories)}] ({', '.join(sorted(lang_file_extra_categories))})" if lang_file_extra_categories else 0
                    if lang_file_extra_categories:
                        warnings.append(
                            f"Extra [{len(lang_file_extra_categories)}] categories in [{lang_name}] lang file")

                    lang_file_extra_blocks = lang_file_block_translations - project_block_translations
                    stats[ConsoleStyle.warning(
                        "Extra blocks in lang file") if lang_file_extra_blocks else ConsoleStyle.info(
                        "Extra blocks in lang file")] \
                        = f"[{len(lang_file_extra_blocks)}] ({', '.join(sorted(lang_file_extra_blocks))})" if lang_file_extra_blocks else 0
                    if lang_file_extra_blocks:
                        warnings.append(
                            f"Extra [{len(lang_file_extra_blocks)}] blocks in [{lang_name}] lang file")

                    lang_file_missing_categories = project_category_translations - lang_file_category_translations
                    stats[ConsoleStyle.error(
                        "Missing categories defined in lang file") if lang_file_missing_categories else ConsoleStyle.info(
                        "Missing categories defined in lang file")] \
                        = f"[{len(lang_file_missing_categories)}] ({', '.join(sorted(lang_file_missing_categories))})" if lang_file_missing_categories else 0
                    if lang_file_missing_categories:
                        errors.append(
                            f"Missing [{len(lang_file_missing_categories)}] categories defined in [{lang_name}] lang file")

                    lang_file_missing_blocks = project_block_translations - lang_file_block_translations
                    stats[ConsoleStyle.error(
                        "Missing blocks defined in lang file") if lang_file_missing_blocks else ConsoleStyle.info(
                        "Missing blocks defined in lang file")] \
                        = f"[{len(lang_file_missing_blocks)}] ({', '.join(sorted(lang_file_missing_blocks))})" if lang_file_missing_blocks else 0
                    if lang_file_missing_blocks:
                        errors.append(
                            f"Missing [{len(lang_file_missing_blocks)}] blocks defined in [{lang_name}] lang file")

                    if os.path.exists(MinecraftUtils.DATABASE_FILE_NAME):
                        stats[ConsoleStyle.info("In database")] = len(database_categories) + len(
                            database_block_ids)
                        stats[ConsoleStyle.info("Categories in database", 3)] = len(database_categories)
                        stats[ConsoleStyle.info("Blocks in database", 3)] = len(database_block_ids)
                        database_missing_categories = database_categories - lang_file_category_translations
                        stats[ConsoleStyle.error(
                            "Missing categories from database") if database_missing_categories else ConsoleStyle.info(
                            "Missing categories from database")] \
                            = f"[{len(database_missing_categories)}] ({', '.join(sorted(database_missing_categories))})" if database_missing_categories else 0
                        if database_missing_categories:
                            errors.append(
                                f"Missing [{len(database_missing_categories)}] from database in [{lang_name}]")
                        database_missing_blocks = database_block_ids - project_block_translations
                        stats[ConsoleStyle.error(
                            "Missing blocks from database") if database_missing_blocks else ConsoleStyle.info(
                            "Missing blocks from database")] \
                            = f"[{len(database_missing_blocks)}] ({', '.join(sorted(database_missing_blocks))})" if database_missing_blocks else 0
                        if database_missing_blocks:
                            errors.append(
                                f"Missing [{len(database_missing_blocks)}] from database in [{lang_name}]")

                    ConsoleStyle.print_stats(stats, f"{lang_name}", '-')
        except FileNotFoundError as e:
            errors.append(e)

        return errors, warnings

    @staticmethod
    def verification_summary(verifications: List[Callable[[], Tuple[List[str], List[str]]]]):
        verification_results = {
            'success': [],
            'warning': {},
            'error': {},
        }
        for verify_func in verifications:
            try:
                errors, warnings = verify_func()
                if errors or warnings:
                    if errors:
                        verification_results['error'][verify_func.__name__] = errors
                    if warnings:
                        verification_results['warning'][verify_func.__name__] = warnings
                else:
                    verification_results['success'].append(verify_func.__name__)

            except Exception as e:
                verification_results['error'][{verify_func.__name__}].append(e)

        # Print summary statistics
        success_details = ''.join([f'\n   • {name}' for name in verification_results['success']])
        warning_details = ''.join(
            [f'\n   • {name} ({len(details)})' + ''.join([f'\n      • {det}' for det in details]) for name, details in
             verification_results['warning'].items()])
        error_details = ''.join(
            [f'\n   • {name} ({len(details)})' + ''.join([f'\n      • {det}' for det in details]) for name, details in
             verification_results['error'].items()])

        ConsoleStyle.print_stats({
            ConsoleStyle.success("Passed checks"): f"[{len(verification_results['success'])}]{success_details}",
            ConsoleStyle.warning("Checks with warnings"): f"[{len(verification_results['warning'])}]{warning_details}",
            ConsoleStyle.error("Checks with errors"): f"[{len(verification_results['error'])}]{error_details}",
        }, f"VERIFICATION SUMMARY ([{len(verifications)}])", icon='📊')

        # Exit with the appropriate code
        print_if_not_quiet(ConsoleStyle.divider('-'))
        if verification_results['error']:
            print_if_not_quiet(
                ConsoleStyle.error(f"Verification failed with [{len(verification_results['error'])}] errors."))
            status = 1
        else:
            print_if_not_quiet(ConsoleStyle.success("Verification passed! Project is ready for building.", icon="🎉"))
            status = 0
        print_if_not_quiet(ConsoleStyle.divider('-'))
        sys.exit(status)
