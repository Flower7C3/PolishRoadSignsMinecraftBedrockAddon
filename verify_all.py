#!/usr/bin/env python3
"""
Comprehensive verification script for Minecraft Bedrock Addon
Verifies project structure, files, textures, and build readiness
"""

from minecraft_check import MinecraftUtils

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from console_utils import ConsoleStyle, rsort

if not PIL_AVAILABLE:
    print(ConsoleStyle.warning("PIL not available - texture dimension checks will be skipped"))


def get_texture_dimensions(texture_path):
    """Pobierz wymiary tekstury"""
    if not PIL_AVAILABLE:
        return None, None
    try:
        with Image.open(texture_path) as img:
            return img.size[0], img.size[1]
    except Exception:
        return None, None


def verify_vertical_alignment():
    """Sprawdź wyrównanie pionowe znaków"""
    errors = []
    warnings = []

    data = MinecraftUtils.load_json_file('database.json')

    stats = {}
    total_signs = 0
    signs_with_alignment = 0
    signs_with_invalid_alignment = set()
    alignment_stats = {'bottom': 0, 'top': 0, 'center': 0}

    for category in data['categories']:
        for sign_id, sign_data in data['categories'][category]['blocks'].items():
            total_signs += 1
            alignment = sign_data.get('vertical_alignment', '')

            if alignment:
                signs_with_alignment += 1
                if alignment in alignment_stats:
                    alignment_stats[alignment] += 1
                else:
                    stats[ConsoleStyle.error(f"Invalid alignment [{alignment}] for sign [{sign_id}]")] = True
                    signs_with_invalid_alignment.add(sign_id)
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

    ConsoleStyle.print_stats(stats, f"VERTICAL ALIGNMENT ([{total_signs}])", icon='📐')

    return errors, warnings


def verify_database():
    """Sprawdź bazę danych"""

    errors = []
    warnings = []

    data = MinecraftUtils.load_json_file('database.json')

    stats = {}
    categories = list(data['categories'].keys())
    categories_with_wikipedia_category_page = 0
    categories_with_translations = 0

    for category in categories:
        category_data = data['categories'][category]
        # Sprawdź URL Wikipedia
        if 'wikipedia_category_page' in category_data and category_data['wikipedia_category_page']:
            categories_with_wikipedia_category_page += 1
        # Sprawdź tłumaczenia
        if 'translations' in category_data and category_data['translations']:
            categories_with_translations += 1

    stats[ConsoleStyle.success("Found")] = f"[{len(categories)}]"
    stats[ConsoleStyle.info("With Wikipedia URLs", 3)] = f"[{categories_with_wikipedia_category_page}]"
    stats[ConsoleStyle.info("With translations", 3)] = f"[{categories_with_translations}]"
    ConsoleStyle.print_stats(stats, "CATEGORIES", icon='🗄')

    stats = {}
    signs_with_shape = 0
    signs_without_shape = set()
    shape_types = {}

    for category in data['categories']:
        for sign_id, sign_data in data['categories'][category]['blocks'].items():
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
        = f"[{len(signs_without_shape)}] ({', '.join(sorted(signs_without_shape))})" if signs_without_shape else "0"
    if signs_without_shape:
        warnings.append(f"Missing [{len(signs_without_shape)}] signs without shape field")
    stats[ConsoleStyle.info("Shape types")] \
        = f"{', '.join([f'{shape}({count})' for shape, count in shape_types.items()])}"
    ConsoleStyle.print_stats(stats, "SHAPE FIELD VERIFICATION", icon='🔷')

    return errors, warnings


def verify_blocks_comprehensive():
    """Kompleksowa weryfikacja bloków: definicje, tekstury, modele i kompatybilność"""
    errors = []
    warnings = []

    # Wczytaj dane
    data = MinecraftUtils.load_json_file('database.json')

    # Zbierz statystyki
    sizes = {}
    shapes = {}
    shape_size_combinations = {}
    shape_size_examples = {}
    padding_examples = []
    no_padding_examples = []

    for category in data['categories']:
        for sign_id, sign_data in data['categories'][category]['blocks'].items():
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
            shapes_list[size] = ', '.join([f'{shape}({count})' for shape, count in shape_count.items()])

    paddings = {
        f"signs 'width < height' → adds padding": f"[{len(padding_examples)}] ({', '.join(padding_examples)})",
        f"signs 'width >= height' → no changes": f"[{len(no_padding_examples)}] ({', '.join(no_padding_examples)})",
    }

    ConsoleStyle.print_stats(rsort(sizes),
                             f"SIGN SIZES ([{len(sizes)}])", icon='📏')
    ConsoleStyle.print_stats(rsort(shapes),
                             f"SIGN SHAPES ([{len(shapes)}])", icon='🔷')
    ConsoleStyle.print_stats(rsort(shape_size_combinations),
                             f"SHAPE AND DIMENSION COMBINATIONS ([{len(shape_size_combinations)}])", icon='🔀')
    ConsoleStyle.print_stats(paddings,
                             f"PADDING ANALYSIS", icon='📐')
    ConsoleStyle.print_stats(shapes_list,
                             f"SHAPE DISTRIBUTION IN SIZES ([{len(shapes_list)}])", icon='📊')

    return errors, warnings


def main():
    """Main verification function"""
    from minecraft_check import MinecraftUtils
    MinecraftUtils.verification_summary([
        MinecraftUtils.verify_config,
        MinecraftUtils.verify_manifests,
        MinecraftUtils.verify_project_structure,
        MinecraftUtils.count_project_files,
        MinecraftUtils.verify_translations,
        MinecraftUtils.verify_blocks,
        MinecraftUtils.verify_models,
        MinecraftUtils.verify_textures,
        verify_database,
        verify_blocks_comprehensive,
        verify_vertical_alignment,
    ])


if __name__ == "__main__":
    main()
