#!/usr/bin/env python3
import json
import os
import subprocess
import re
import sys
import time
import tempfile
import argparse
from natsort import natsorted
from console_utils import ConsoleStyle, print_if_not_quiet


def scale_size_from_mm_to_px(value):
    return value // 5


def scale_size_from_mm_to_msu(value):
    return round(value * 16 / 1000, 3)


def normalize_sign_id(sign_code):
    """Normalizuj kod znaku do formatu używanych w bazie danych"""
    # Usuń spacje i zamień na podkreślenie
    normalized = sign_code.strip().replace(' ', '_')

    # Zamień myślniki na podkreślenia
    normalized = normalized.replace('-', '_')

    # Zamień na małe litery
    normalized = normalized.lower()

    # Jeśli kod nie ma podkreślnika, dodaj go przed liczbą
    # Przykład: "a1" -> "a_1", "b5" -> "b_5", "c10" -> "c_10"
    if '_' not in normalized and len(normalized) > 1:
        # Znajdź pierwszą cyfrę
        for i, char in enumerate(normalized):
            if char.isdigit():
                # Wstaw podkreślnik przed pierwszą cyfrą
                normalized = normalized[:i] + '_' + normalized[i:]
                break

    return normalized


def find_sign_in_database(sign_id, data):
    """Znajdź znak w bazie danych"""
    categories = list(data['categories'].keys())
    for category in categories:
        if sign_id in data['categories'][category]['blocks']:
            return data['categories'][category]['blocks'][sign_id]
    return None


def get_category_for_sign(sign_id, data):
    """Pobierz kategorię dla znaku"""
    categories = list(data['categories'].keys())
    for category in categories:
        if sign_id in data['categories'][category]['blocks']:
            return category
    return None


def get_reverse_texture_for_shape(sign_shape, sign_width, sign_height):
    """Pobierz nazwę tekstury tła na podstawie kształtu znaku"""
    shape_to_background = {
        'triangle': f'triangle_{sign_width}x{sign_height}',
        'inverted_triangle': f'inverted_triangle_{sign_width}x{sign_height}',
        'circle': f'circle_{sign_width}x{sign_height}',
        'square': f'square_{sign_width}x{sign_height}',
        'diamond': f'diamond_{sign_width}x{sign_height}',
        'octagon': f'octagon_{sign_width}x{sign_height}',
        'rectangle': f'rectangle_{sign_width}x{sign_height}'
    }

    return shape_to_background.get(sign_shape, f'rectangle_{sign_width}x{sign_height}')


def get_image_dimensions(png_path):
    """Pobierz wymiary obrazka PNG — ulepszona wersja"""
    # Najpierw spróbuj z identify (szybsze)
    result = subprocess.run(['identify', '-format', '%wx%h', png_path],
                            capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        dimensions = result.stdout.strip()
        model_width, model_height = map(int, dimensions.split('x'))
        return model_width, model_height

    # Fallback: użyj PIL, jeśli identify nie działa
    try:
        from PIL import Image
        with Image.open(png_path) as img:
            return img.size[0], img.size[1]
    except Exception as e:
        print_if_not_quiet(ConsoleStyle.warning(f"Błąd pobierania wymiarów: {e}"))
    return None, None


def calculate_vertical_position(alignment, model_height):
    """Oblicz pozycję Y na podstawie wyrównania"""
    if alignment == "top":
        return 16 - model_height  # Wyrównanie do góry
    elif alignment == "center":
        return (16 - model_height) / 2  # Wyrównanie do środka
    else:  # "bottom" lub domyślne
        return 0  # Wyrównanie do dołu


def create_model_template(model_name, sign_width, sign_height, target_width, target_height, vertical_alignment="bottom"):
    """Twórz szablon modelu 3D"""
    cube_width = scale_size_from_mm_to_msu(sign_width)
    cube_height = scale_size_from_mm_to_msu(sign_height)
    
    # Oblicz pozycję Y na podstawie wyrównania
    origin_y = calculate_vertical_position(vertical_alignment, cube_height)
    
    return {
        "format_version": "1.21.90",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": f"geometry.{model_name}",
                    "texture_width": target_height if target_width < target_height else target_width,
                    "texture_height": target_height,
                    "visible_bounds_width": 0,
                    "visible_bounds_height": 0,
                    "visible_bounds_offset": [0, 0, 0]
                },
                "item_display_transforms": {
                    "firstperson_righthand": {
                        "rotation": [0, 180, 0],
                        "scale": [0.3, 0.3, 0.3],
                        "translation": [0, 4, 0]
                    },
                    "firstperson_lefthand": {
                        "rotation": [0, 180, 0],
                        "scale": [0.3, 0.3, 0.3],
                        "translation": [0, 4, 0]
                    },
                    "fixed": {
                        "scale": [1.5, 1.5, 1.5]
                    },
                    "gui": {
                        "rotation": [0, 180, 0]
                    }
                },
                "bones": [
                    {
                        "name": "block",
                        "cubes": [
                            {
                                "origin": [
                                    round((cube_height if cube_width < cube_height else cube_width) / -2, 3),
                                    origin_y,
                                    6.9
                                ],
                                "size": [
                                    cube_height if cube_width < cube_height else cube_width,
                                    cube_height,
                                    0],
                                "uv": {
                                    "north": {"uv": [0, 0], "uv_size": [
                                        target_height if target_width < target_height else target_width,
                                        target_height
                                    ]},
                                    "south": {"uv": [0, 0], "uv_size": [
                                        target_height if target_width < target_height else target_width,
                                        target_height
                                    ]}
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }


def create_model_if_needed(sign_shape, sign_width, sign_height, target_width, target_height, vertical_alignment="bottom"):
    """Twórz model 3D, jeśli nie istnieje"""
    model_name = f"road_sign_{sign_shape}_{sign_width}x{sign_height}_{vertical_alignment}"
    model_path = f"RP/models/blocks/{model_name}.geo.json"

    if os.path.exists(model_path):
        print_if_not_quiet(ConsoleStyle.success(f"Model [{model_name}] już istnieje!"))
        return model_name

    # Twórz model na podstawie szablonu
    template = create_model_template(model_name, sign_width, sign_height, target_width, target_height, vertical_alignment)

    with open(model_path, 'w') as f:
        json.dump(template, f, indent=2)

    print_if_not_quiet(ConsoleStyle.success(f"Utworzono model [{model_name}]"))
    return model_name


def update_model_if_needed(sign_shape, sign_width, sign_height, target_width, target_height, vertical_alignment="bottom"):
    """Zaktualizuj model 3D, jeśli wymiary się zmieniły"""
    print_if_not_quiet(ConsoleStyle.section("TWORZENIE MODELU"))

    model_name = f"road_sign_{sign_shape}_{sign_width}x{sign_height}_{vertical_alignment}"
    model_path = f"RP/models/blocks/{model_name}.geo.json"

    if not os.path.exists(model_path):
        print_if_not_quiet(ConsoleStyle.info(f"Model nie istnieje, tworzę nowy [{model_name}]"))
        return create_model_if_needed(sign_shape, sign_width, sign_height, target_width, target_height, vertical_alignment)

    # Sprawdź, czy wymiary modelu są aktualne
    try:
        with open(model_path, 'r') as f:
            model_data = json.load(f)

        # Pobierz aktualne wymiary z modelu
        if (model_data.get("minecraft:geometry") and
                len(model_data["minecraft:geometry"]) > 0 and
                model_data["minecraft:geometry"][0].get("description") and
                "texture_width" in model_data["minecraft:geometry"][0]["description"] and
                "texture_height" in model_data["minecraft:geometry"][0]["description"]):

            current_width = model_data["minecraft:geometry"][0]["description"]["texture_width"]
            current_height = model_data["minecraft:geometry"][0]["description"]["texture_height"]

            # Sprawdź, czy wymiary się zmieniły
            if current_width == target_width and current_height == target_height:
                print_if_not_quiet(ConsoleStyle.success(f"Model ma aktualne wymiary [{model_name}]"))
                return model_name
            else:
                print_if_not_quiet(ConsoleStyle.info(f"Aktualizuję model [{model_name}] z wymiarów [{current_width}x{current_height}] na [{target_width}x{target_height}]"))
        else:
            print_if_not_quiet(ConsoleStyle.warning(f"Nieprawidłowa struktura modelu, tworzę nowy [{model_name}]"))
            return create_model_if_needed(sign_shape, sign_width, sign_height, target_width, target_height, vertical_alignment)

    except Exception as e:
        print_if_not_quiet(ConsoleStyle.warning(f"Błąd odczytu modelu [{model_name}]: {e}"))
        return create_model_if_needed(sign_shape, sign_width, sign_height, target_width, target_height, vertical_alignment)

    # Aktualizuj model z nowymi wymiarami
    template = create_model_template(model_name, sign_width, sign_height, target_width, target_height, vertical_alignment)

    with open(model_path, 'w') as f:
        json.dump(template, f, indent=2)

    print_if_not_quiet(ConsoleStyle.success(f"Zaktualizowano model [{model_name}]"))
    return model_name


def create_reverse_texture_if_needed(sign_shape, sign_width, sign_height, texture_width, texture_height,
                                        force_rebuild=False):
    """Twórz teksturę tła, jeśli nie istnieje"""
    print_if_not_quiet(ConsoleStyle.section("TWORZENIE TEKSTURY REWERSU"))

    # Pobierz odpowiednią teksturę tła na podstawie kształtu
    reverse_texture_name = get_reverse_texture_for_shape(sign_shape, sign_width, sign_height)
    reverse_texture_dir = f"RP/textures/blocks/reverse/"
    reverse_texture_path = f"{reverse_texture_dir}{reverse_texture_name}.png"

    if os.path.exists(reverse_texture_path) and not force_rebuild:
        print_if_not_quiet(ConsoleStyle.success(f"Tekstura tła już istnieje [{reverse_texture_name}]"))
        return reverse_texture_name

    # Utwórz katalog, jeśli nie istnieje
    os.makedirs(os.path.dirname(reverse_texture_dir), exist_ok=True)

    # Sprawdź, czy trzeba zrobić kwadrat (width < height)
    if texture_width < texture_height:
        # Użyj większego wymiaru jako kwadrat
        square_size = texture_height
        print_if_not_quiet(
            f"  📐 Tworzę kwadratową teksturę tła [{square_size}x{square_size}] z wycentrowanym kształtem [{texture_width}x{texture_height}]")

        # Twórz neutralną białą teksturę tła w formacie sRGB z kanałem alpha zgodnie z kształtem
        try:
            if sign_shape == 'triangle':
                # Trójkąt — szary kolor w kształcie trójkąta wycentrowany w kwadracie
                subprocess.run(['magick', '-size', f'{square_size}x{square_size}', 'xc:transparent',
                                '-fill', '#808080', '-gravity', 'center',
                                '-draw',
                                f'polygon {square_size // 2},{square_size // 2 - texture_height // 2} {square_size // 2 - texture_width // 2},{square_size // 2 + texture_height // 2} {square_size // 2 + texture_width // 2},{square_size // 2 + texture_height // 2}',
                                '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'inverted_triangle':
                # Odwrócony trójkąt — szary kolor w kształcie odwróconego trójkąta wycentrowany w kwadracie
                subprocess.run(['magick', '-size', f'{square_size}x{square_size}', 'xc:transparent',
                                '-fill', '#808080', '-gravity', 'center',
                                '-draw',
                                f'polygon {square_size // 2 - texture_width // 2},{square_size // 2 - texture_height // 2} {square_size // 2 + texture_width // 2},{square_size // 2 - texture_height // 2} {square_size // 2},{square_size // 2 + texture_height // 2}',
                                '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'circle':
                # Koło — szary kolor w kształcie koła wycentrowany w kwadracie
                subprocess.run(['magick', '-size', f'{square_size}x{square_size}', 'xc:transparent',
                                '-fill', '#808080', '-gravity', 'center',
                                '-draw',
                                f'circle {square_size // 2},{square_size // 2} {square_size // 2},{square_size // 2 - min(texture_width, texture_height) // 2}',
                                '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'square':
                # Kwadrat — szary kolor w kształcie kwadratu wycentrowany w kwadracie
                subprocess.run(['magick', '-size', f'{square_size}x{square_size}', 'xc:transparent',
                                '-fill', '#808080', '-gravity', 'center',
                                '-draw',
                                f'rectangle {square_size // 2 - texture_width // 2},{square_size // 2 - texture_height // 2} {square_size // 2 + texture_width // 2},{square_size // 2 + texture_height // 2}',
                                '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'diamond':
                # Romb — szary kolor w kształcie rombu wycentrowany w kwadracie
                subprocess.run(['magick', '-size', f'{square_size}x{square_size}', 'xc:transparent',
                                '-fill', '#808080', '-gravity', 'center',
                                '-draw',
                                f'polygon {square_size // 2},{square_size // 2 - texture_height // 2} {square_size // 2 + texture_width // 2},{square_size // 2} {square_size // 2},{square_size // 2 + texture_height // 2} {square_size // 2 - texture_width // 2},{square_size // 2}',
                                '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'octagon':
                # Ośmiokąt — szary kolor w kształcie ośmiokąta wycentrowany w kwadracie
                margin = min(texture_width, texture_height) // 4
                subprocess.run(['magick', '-size', f'{square_size}x{square_size}', 'xc:transparent',
                                '-fill', '#808080', '-gravity', 'center',
                                '-draw',
                                f'polygon {square_size // 2 - texture_width // 2 + margin},{square_size // 2 - texture_height // 2} {square_size // 2 + texture_width // 2 - margin},{square_size // 2 - texture_height // 2} {square_size // 2 + texture_width // 2},{square_size // 2 - texture_height // 2 + margin} {square_size // 2 + texture_width // 2},{square_size // 2 + texture_height // 2 - margin} {square_size // 2 + texture_width // 2 - margin},{square_size // 2 + texture_height // 2} {square_size // 2 - texture_width // 2 + margin},{square_size // 2 + texture_height // 2} {square_size // 2 - texture_width // 2},{square_size // 2 + texture_height // 2 - margin} {square_size // 2 - texture_width // 2},{square_size // 2 - texture_height // 2 + margin}',
                                '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            else:
                # Domyślnie prostokąt wycentrowany w kwadracie
                subprocess.run(['magick', '-size', f'{square_size}x{square_size}', 'xc:transparent',
                                '-fill', '#808080', '-gravity', 'center',
                                '-draw',
                                f'rectangle {square_size // 2 - texture_width // 2},{square_size // 2 - texture_height // 2} {square_size // 2 + texture_width // 2},{square_size // 2 + texture_height // 2}',
                                '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)

            print_if_not_quiet(ConsoleStyle.success(f"Utworzono kwadratową teksturę tła [{reverse_texture_name}] (kształt: {sign_shape})"))
        except subprocess.CalledProcessError as e:
            print_if_not_quiet(ConsoleStyle.warning(f"Błąd tworzenia tekstury tła [{reverse_texture_name}]: {e}"))
            return None
    else:
        # Użyj oryginalnych wymiarów
        print_if_not_quiet(ConsoleStyle.info(f"Używam oryginalnych wymiarów tekstury tła [{texture_width}x{texture_height}]"))

        # Twórz neutralną szarą teksturę tła w formacie sRGB z kanałem alpha zgodnie z kształtem
        try:
            if sign_shape == 'triangle':
                # Trójkąt — szary kolor w kształcie trójkąta
                subprocess.run(
                    ['magick', '-size', f'{texture_width}x{texture_height}', 'xc:transparent', '-fill', '#808080',
                     '-draw', f'polygon {texture_width // 2},0 0,{texture_height} {texture_width},{texture_height}',
                     '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'inverted_triangle':
                # Odwrócony trójkąt — szary kolor w kształcie odwróconego trójkąta
                subprocess.run(
                    ['magick', '-size', f'{texture_width}x{texture_height}', 'xc:transparent', '-fill', '#808080',
                     '-draw', f'polygon 0,0 {texture_width},0 {texture_width // 2},{texture_height}', '-alpha', 'on',
                     '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'circle':
                # Koło — szary kolor w kształcie koła
                subprocess.run(
                    ['magick', '-size', f'{texture_width}x{texture_height}', 'xc:transparent', '-fill', '#808080',
                     '-draw', f'circle {texture_width // 2},{texture_height // 2} {texture_width // 2},0', '-alpha',
                     'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'square':
                # Kwadrat — szary kolor w kształcie kwadratu
                subprocess.run(
                    ['magick', '-size', f'{texture_width}x{texture_height}', 'xc:transparent', '-fill', '#808080',
                     '-draw', f'rectangle 0,0 {texture_width - 1},{texture_height - 1}', '-alpha', 'on', '-define',
                     'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'diamond':
                # Romb — szary kolor w kształcie rombu
                subprocess.run(
                    ['magick', '-size', f'{texture_width}x{texture_height}', 'xc:transparent', '-fill', '#808080',
                     '-draw',
                     f'polygon {texture_width // 2},0 {texture_width},{texture_height // 2} {texture_width // 2},{texture_height} 0,{texture_height // 2}',
                     '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            elif sign_shape == 'octagon':
                # Ośmiokąt — szary kolor w kształcie ośmiokąta
                margin = min(texture_width, texture_height) // 4
                subprocess.run(
                    ['magick', '-size', f'{texture_width}x{texture_height}', 'xc:transparent', '-fill', '#808080',
                     '-draw',
                     f'polygon {margin},0 {texture_width - margin},0 {texture_width},{margin} {texture_width},{texture_height - margin} {texture_width - margin},{texture_height} {margin},{texture_height} 0,{texture_height - margin} 0,{margin}',
                     '-alpha', 'on', '-define', 'png:color-type=6', reverse_texture_path], check=True)
            else:
                # Domyślnie prostokąt
                subprocess.run(
                    ['magick', '-size', f'{texture_width}x{texture_height}', 'xc:transparent', '-fill', '#808080',
                     '-draw', f'rectangle 0,0 {texture_width - 1},{texture_height - 1}', '-alpha', 'on', '-define',
                     'png:color-type=6', reverse_texture_path], check=True)

            print_if_not_quiet(ConsoleStyle.success(f"Utworzono teksturę tła [{reverse_texture_name}] (kształt: {sign_shape})"))
        except subprocess.CalledProcessError as e:
            print_if_not_quiet(ConsoleStyle.warning(f"Błąd tworzenia tekstury tła [{reverse_texture_name}]: {e}"))
            return None

    terrain_path = "RP/textures/terrain_texture.json"

    with open(terrain_path, 'r') as f:
        terrain = json.load(f)

    # Sprawdź, czy już istnieje
    if f"polish_road_sign_back:{reverse_texture_name}" in terrain["texture_data"]:
        print_if_not_quiet(ConsoleStyle.success(f"Tekstura tła [{reverse_texture_name}] już istnieje w terrain_texture.json"))
        return reverse_texture_name

    # Dodaj wpis tekstury tła
    terrain["texture_data"][f"polish_road_sign_back:{reverse_texture_name}"] = {
        "textures": f"textures/blocks/reverse/{reverse_texture_name}.png"
    }

    with open(terrain_path, 'w') as f:
        json.dump(terrain, f, indent=2)

    print_if_not_quiet(ConsoleStyle.success(f"Dodano teksturę tła [{reverse_texture_name}] do terrain_texture.json"))

    return reverse_texture_name


def add_averse_texture_to_terrain(sign_id):
    """Dodaj teksturę znaku do terrain_texture.json"""
    terrain_path = "RP/textures/terrain_texture.json"
    category = sign_id.split('_')[0]

    with open(terrain_path, 'r') as f:
        terrain = json.load(f)

    # Sprawdź, czy już istnieje
    if f"polish_road_sign:{sign_id}" in terrain["texture_data"]:
        print_if_not_quiet(ConsoleStyle.success(f"Tekstura znaku [{sign_id}] już istnieje w terrain_texture.json"))
        return

    # Dodaj wpis tekstury znaku
    terrain["texture_data"][f"polish_road_sign:{sign_id}"] = {
        "textures": f"textures/blocks/averse/{category.lower()}/{sign_id}.png"
    }

    with open(terrain_path, 'w') as f:
        json.dump(terrain, f, indent=2)

    print_if_not_quiet(ConsoleStyle.success(f"Dodano teksturę znaku [{sign_id}] do terrain_texture.json"))


def get_model_dimensions(model_name):
    """Pobierz wymiary modelu z pliku geometry"""
    model_path = f"RP/models/blocks/{model_name}.geo.json"

    if not os.path.exists(model_path):
        print_if_not_quiet(ConsoleStyle.warning(f"Nie znaleziono modelu [{model_path}]"))
        return None, None

    try:
        with open(model_path, 'r') as f:
            model_data = json.load(f)

        # Pobierz wymiary z pierwszego cuba
        if (model_data.get("minecraft:geometry") and
                len(model_data["minecraft:geometry"]) > 0 and
                model_data["minecraft:geometry"][0].get("bones") and
                len(model_data["minecraft:geometry"][0]["bones"]) > 0 and
                model_data["minecraft:geometry"][0]["bones"][0].get("cubes") and
                len(model_data["minecraft:geometry"][0]["bones"][0]["cubes"]) > 0):

            cube = model_data["minecraft:geometry"][0]["bones"][0]["cubes"][0]
            size = cube["size"]

            # Oblicz wymiary
            model_width = size[0]
            model_height = size[1]

            return model_width, model_height
        else:
            print_if_not_quiet(ConsoleStyle.warning(f"Nieprawidłowa struktura modelu [{model_path}]"))
            return None, None

    except Exception as e:
        print_if_not_quiet(ConsoleStyle.warning(f"Błąd odczytu modelu [{model_name}]: {e}"))
        return None, None


def create_block_template(sign_id, model_name, reverse_texture_name, model_width, model_height, vertical_alignment="bottom"):
    """Twórz szablon bloku"""
    # Oblicz origin (środek modelu)
    origin_x = round(-model_width / 2, 3)
    origin_y = calculate_vertical_position(vertical_alignment, model_height)
    origin_z = 6.9

    return {
        "format_version": "1.20.60",
        "minecraft:block": {
            "description": {
                "identifier": f"polish_road_sign:{sign_id}",
                "menu_category": {
                    "category": "construction"
                },
                "traits": {
                    "minecraft:placement_direction": {
                        "enabled_states": [
                            "minecraft:cardinal_direction"
                        ]
                    }
                }
            },
            "components": {
                "minecraft:collision_box": {
                    "origin": [origin_x, origin_y, origin_z],
                    "size": [
                        model_width,
                        model_height,
                        0.1
                    ]
                },
                "minecraft:selection_box": {
                    "origin": [origin_x, origin_y, origin_z],
                    "size": [
                        model_width,
                        model_height,
                        0.1
                    ]
                },
                "minecraft:destructible_by_mining": {
                    "seconds_to_destroy": 1
                },
                "minecraft:destructible_by_explosion": {
                    "explosion_resistance": 30
                },
                "minecraft:geometry": f"geometry.{model_name}",
                "minecraft:material_instances": {
                    "north": {
                        "texture": f"polish_road_sign:{sign_id}",
                        "render_method": "alpha_test_single_sided"
                    },
                    "south": {
                        "texture": f"polish_road_sign_back:{reverse_texture_name}",
                        "render_method": "alpha_test_single_sided"
                    }
                }
            },
            "permutations": [
                {
                    "condition": "q.block_state('minecraft:cardinal_direction') == 'north' ",
                    "components": {
                        "minecraft:transformation": {
                            "rotation": [0, 180, 0]
                        }
                    }
                },
                {
                    "condition": "q.block_state('minecraft:cardinal_direction') == 'south' ",
                    "components": {
                        "minecraft:transformation": {
                            "rotation": [0, 0, 0]
                        }
                    }
                },
                {
                    "condition": "q.block_state('minecraft:cardinal_direction') == 'east' ",
                    "components": {
                        "minecraft:transformation": {
                            "rotation": [0, 90, 0]
                        }
                    }
                },
                {
                    "condition": "q.block_state('minecraft:cardinal_direction') == 'west' ",
                    "components": {
                        "minecraft:transformation": {
                            "rotation": [0, 270, 0]
                        }
                    }
                }
            ]
        }
    }


def process_sign(sign_id, wikipedia_file_page, sign_width, sign_height, database_path, skip_download=False,
                 force_rebuild=False):
    """Przetwórz pojedynczy znak z automatycznym tworzeniem modeli i tekstur"""

    # Pobierz dane znaku z bazy danych
    with open(database_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sign_data = find_sign_in_database(sign_id, data)
    if not sign_data:
        print_if_not_quiet(ConsoleStyle.error(f"Nie znaleziono znaku [{sign_id}] w bazie danych"))
        return False

    # Pobierz kategorię
    category = get_category_for_sign(sign_id, data)
    if not category:
        print_if_not_quiet(ConsoleStyle.error(f"Nie znaleziono kategorii dla znaku [{sign_id}]"))
        return False

    # Pobierz kształt znaku z bazy danych
    sign_shape = sign_data.get('sign_shape', 'rectangle')
    # Pobierz wyrównanie w pionie (domyślnie "bottom")
    vertical_alignment = sign_data.get('vertical_alignment', 'bottom')
    target_width = scale_size_from_mm_to_px(sign_width)
    target_height = scale_size_from_mm_to_px(sign_height)
    print_if_not_quiet(ConsoleStyle.section(f"Przetwarzanie znaku [{sign_id}]"))
    print_if_not_quiet(ConsoleStyle.info(f"Kształt: {sign_shape}, Wymiary: {sign_width}x{sign_height}, Wyrównanie: {vertical_alignment}"))

    if not create_averse_texture_if_needed(sign_id, target_width, target_height, wikipedia_file_page, skip_download, force_rebuild):
        return False

    # Utwórz teksturę tła, jeśli nie istnieje
    reverse_texture_name = create_reverse_texture_if_needed(sign_shape, sign_width, sign_height, target_width,
                                                               target_height, force_rebuild)

    # Automatycznie twórz lub aktualizuj model i teksturę tła
    model_name = update_model_if_needed(sign_shape, sign_width, sign_height, target_width, target_height, vertical_alignment)

    return update_block_if_needed(sign_id, model_name, reverse_texture_name, sign_width, sign_height, vertical_alignment)


def create_averse_texture_if_needed(sign_id, target_width, target_height, wikipedia_file_page, skip_download=False, force_rebuild=False):
    print_if_not_quiet(ConsoleStyle.section("TWORZENIE TEKSTURY AWERSU"))
    category = sign_id.split('_')[0]

    # Przygotuj katalogi
    target_dir = f"RP/textures/blocks/averse/{category.lower()}"
    os.makedirs(target_dir, exist_ok=True)

    # Konwertuj na PNG w tym samym katalogu
    png_path = f"{target_dir}/{sign_id}.png"
    svg_path = get_svg(target_dir, sign_id, wikipedia_file_page, skip_download)
    if not svg_path:
        return False

    # Usuń istniejącą teksturę, jeśli force_rebuild = True
    if os.path.exists(png_path):
        if force_rebuild:
            os.remove(png_path)
            print_if_not_quiet(ConsoleStyle.warning(f"Usunięto istniejącą teksturę [{png_path}]"))
        else:
            print_if_not_quiet(ConsoleStyle.success(f"Tekstura znaku już istnieje [{png_path}]"))
            return True

    if not convert_svg_to_png(svg_path, png_path, target_width, target_height):
        print_if_not_quiet(ConsoleStyle.error(f"Nie udało się skonwertować SVG dla {sign_id}"))
        return False
    print_if_not_quiet(ConsoleStyle.success(f"Utworzono teksturę znaku [{png_path}] ({target_width}x{target_height})"))

    # Dodaj teksturę znaku do terrain_texture.json
    add_averse_texture_to_terrain(sign_id)

    return True


def get_svg(target_dir, sign_id, wikipedia_file_page, skip_download=False):
    # Ścieżka do lokalnego pliku SVG
    svg_path = f"{target_dir}/{sign_id}.svg"

    if skip_download:
        # Sprawdź, czy lokalny plik SVG istnieje
        if not os.path.exists(svg_path):
            print_if_not_quiet(ConsoleStyle.error(f"Nie znaleziono lokalnego pliku SVG [{svg_path}]"))
            return False
        print_if_not_quiet(ConsoleStyle.info(f"Używam lokalnego SVG [{svg_path}]"))
    else:
        # Pobierz stronę Wikipedii (użyj bezpośredniego linku do pliku)
        html_content = download_wikipedia_page(wikipedia_file_page)
        if not html_content:
            print_if_not_quiet(ConsoleStyle.error(f"Nie udało się pobrać strony dla [{sign_id}]"))
            return False

        # Wyciągnij link do SVG z pliku
        svg_url = extract_svg_url(html_content)
        if not svg_url:
            print_if_not_quiet(ConsoleStyle.error(f"Nie znaleziono linku SVG dla [{sign_id}]"))
            return False

        # Pobierz SVG do katalogu cache obok PNG
        if not download_svg(svg_url, svg_path):
            print_if_not_quiet(ConsoleStyle.error(f"Nie udało się pobrać SVG dla [{sign_id}]"))
            return False

        print_if_not_quiet(ConsoleStyle.success(f"Pobrano SVG [{svg_path}]"))
    return svg_path


def download_wikipedia_page(url):
    """Pobierz stronę Wikipedii"""
    try:
        result = subprocess.run(['curl', '-A', 'Mozilla/5.0', '-L', '--insecure', url],
                                capture_output=True, text=True, timeout=30)
        return result.stdout
    except Exception as e:
        print_if_not_quiet(ConsoleStyle.warning(f"Błąd pobierania strony: {e}"))
        return None


def extract_svg_url(html_content):
    """Wyciągnij link do pliku SVG z HTML — ulepszona wersja"""
    # Najpierw szukaj w "fullImageLink" (lepsze parsowanie)
    full_image_pattern = r'href="([^"]*\.svg)"[^>]*class="[^"]*fullImageLink[^"]*"'
    match = re.search(full_image_pattern, html_content)
    if match:
        svg_url = match.group(1)
        if svg_url.startswith('//'):
            svg_url = 'https:' + svg_url
        elif svg_url.startswith('/'):
            svg_url = 'https://pl.wikipedia.org' + svg_url
        print_if_not_quiet(ConsoleStyle.info(f"Znaleziono SVG (fullImageLink): {svg_url}"))
        return svg_url

    # Fallback: szukaj linku do pliku SVG w upload.wikimedia.org
    upload_pattern = r'href="//upload\.wikimedia\.org/wikipedia/commons/[^"]*\.svg"'
    match = re.search(upload_pattern, html_content)
    if match:
        svg_url = "https:" + match.group().replace('href="', '').replace('"', '')
        print_if_not_quiet(ConsoleStyle.info(f"Znaleziono SVG (fallback): {svg_url}"))
        return svg_url

    # Dodatkowy fallback: szukaj bezpośrednich linków
    direct_pattern = r'https://upload\.wikimedia\.org/[^"]*\.svg'
    match = re.search(direct_pattern, html_content)
    if match:
        svg_url = match.group(0)
        print_if_not_quiet(ConsoleStyle.info(f"Znaleziono SVG (direct): {svg_url}"))
        return svg_url

    return None


def download_svg(svg_url, output_path):
    """Pobierz plik SVG"""
    try:
        result = subprocess.run(['curl', '-A', 'Mozilla/5.0', '-L', '--insecure', svg_url, '-o', output_path],
                                capture_output=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print_if_not_quiet(ConsoleStyle.warning(f"Błąd pobierania SVG: {e}"))
        return False


def convert_svg_to_png(svg_path, png_path, target_width, target_height):
    """Konwertuj SVG na PNG z określoną szerokością"""
    try:
        # Sprawdź, czy trzeba dodać padding (width < height)
        if target_width < target_height:
            # Dodaj padding wokół obrazka
            padding = (target_height - target_width) // 2
            new_width = target_height
            new_height = target_height
            print_if_not_quiet(ConsoleStyle.info(f"Dodaję padding wokół obrazka [{new_width}x{new_height}] (padding: {padding}px)"))

            # Najpierw konwertuj SVG do oryginalnych wymiarów
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_png = temp_file.name

            result = subprocess.run([
                'inkscape', '--export-type=png',
                '--export-filename=' + temp_png,
                '--export-width=' + str(target_width),
                '--export-height=' + str(target_height),
                '--export-background-opacity=0',
                '--export-background=transparent',
                '--export-png-color-mode=RGBA_8', svg_path
            ], capture_output=True, text=True)

            if result.returncode == 0:
                # Dodaj padding z jawnie ustawioną przeroczystością
                subprocess.run([
                    'magick', temp_png, '-gravity', 'center', '-background', 'none',
                    '-extent', f'{new_width}x{new_height}',
                    '-alpha', 'on', png_path
                ], check=True)

                # Usuń plik tymczasowy
                os.remove(temp_png)

                return True
            else:
                print_if_not_quiet(ConsoleStyle.error(f"Błąd konwersji SVG: {result.stderr}"))
                return False
        else:
            # Użyj oryginalnych wymiarów
            print_if_not_quiet(ConsoleStyle.info(f"Używam oryginalnych wymiarów [{target_width}x{target_height}]"))
            result = subprocess.run([
                'inkscape', '--export-type=png',
                '--export-filename=' + png_path,
                '--export-width=' + str(target_width),
                '--export-height=' + str(target_height),
                '--export-background-opacity=0',
                '--export-background=transparent',
                '--export-png-color-mode=RGBA_8', svg_path
            ], capture_output=True, text=True)

            if result.returncode == 0:
                return True
            else:
                print_if_not_quiet(ConsoleStyle.error(f"Błąd konwersji SVG: {result.stderr}"))
                return False

    except subprocess.CalledProcessError as e:
        print_if_not_quiet(ConsoleStyle.error(f"Błąd konwersji SVG: {e}"))
        return False


def update_block_if_needed(sign_id, model_name, reverse_texture_name, sign_width, sign_height, vertical_alignment="bottom"):
    print_if_not_quiet(ConsoleStyle.section("TWORZENIE BLOKU"))
    category = sign_id.split('_')[0]
    category_lower = category.lower()
    block_path = f"BP/blocks/{category_lower}/{sign_id}.block.json"
    new_block = False
    # Utwórz lub zaktualizuj definicję bloku
    if not os.path.exists(block_path):
        new_block = True

    # Utwórz katalog, jeśli nie istnieje
    os.makedirs(os.path.dirname(block_path), exist_ok=True)

    # Pobierz wymiary modelu
    cube_width = scale_size_from_mm_to_msu(sign_width)
    cube_height = scale_size_from_mm_to_msu(sign_height)

    # Twórz blok na podstawie szablonu
    block_template = create_block_template(sign_id, model_name, reverse_texture_name, cube_width, cube_height, vertical_alignment)

    # Zapisz blok
    with open(block_path, 'w') as f:
        json.dump(block_template, f, indent=2)

    if new_block:
        print_if_not_quiet(ConsoleStyle.success(f"Utworzono blok [{sign_id}] ({cube_width}x{cube_height})"))
    else:
        print_if_not_quiet(ConsoleStyle.success(f"Zaktualizowano blok [{sign_id}] ({cube_width}x{cube_height})"))
    return True


def cleanup_category_files(data, category):
    """Usuń pliki dla konkretnej kategorii"""
    ConsoleStyle.print_section(f"CZYSZCZENIE KATEGORII {category}")

    category_lower = category.lower()
    removed_count = 0

    # Usuń bloki dla kategorii
    block_dir = f"BP/blocks/{category_lower}"
    if os.path.exists(block_dir):
        for file in os.listdir(block_dir):
            if file.endswith('.block.json'):
                os.remove(os.path.join(block_dir, file))
                print_if_not_quiet(ConsoleStyle.warning(f"Usunięto blok [{category_lower}/{file}]"))
                removed_count += 1

    # Usuń tekstury PNG dla kategorii (zachowaj SVG)
    texture_dir = f"RP/textures/blocks/averse/{category_lower}"
    if os.path.exists(texture_dir):
        for file in os.listdir(texture_dir):
            if file.endswith('.png'):
                os.remove(os.path.join(texture_dir, file))
                print_if_not_quiet(ConsoleStyle.warning(f"Usunięto teksturę [{category_lower}/{file}]"))
                removed_count += 1

    # Usuń wpisy z terrain_texture.json dla znaków z tej kategorii
    terrain_path = "RP/textures/terrain_texture.json"
    if os.path.exists(terrain_path):
        with open(terrain_path, 'r') as f:
            terrain_data = json.load(f)

        # Usuń wpisy dla znaków z tej kategorii
        keys_to_remove = []
        for key in terrain_data['texture_data']:
            if key.startswith(f'polish_road_sign:{category_lower}_'):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del terrain_data['texture_data'][key]
            print_if_not_quiet(ConsoleStyle.warning(f"Usunięto [{key}] z terrain_texture.json"))
            removed_count += 1

        with open(terrain_path, 'w') as f:
            json.dump(terrain_data, f, indent=2)

    if removed_count > 0:
        print_if_not_quiet(ConsoleStyle.success(f"Czyszczenie kategorii [{category}] zakończone - usunięto {removed_count} plików"))
    else:
        print_if_not_quiet(ConsoleStyle.info(f"Brak plików do usunięcia w kategorii [{category}]"))
    print_if_not_quiet(ConsoleStyle.divider())


def cleanup_orphaned_files(data):
    """Usuń pliki dla znaków, które nie istnieją w bazie danych"""
    ConsoleStyle.print_section("CZYSZCZENIE OSIEROCONYCH PLIKÓW")

    # Zbierz wszystkie znaki z bazy danych
    database_blocks = set()
    for category in data['categories'].values():
        database_blocks.update(category['blocks'].keys())
    
    print_if_not_quiet(ConsoleStyle.info(f"Znaki w bazie danych: {len(database_blocks)}"))
    
    removed_count = 0
    
    # Sprawdź i usuń bloki dla nieistniejących znaków
    for category in data['categories'].keys():
        category_lower = category.lower()
        block_dir = f"BP/blocks/{category_lower}"
        if os.path.exists(block_dir):
            for file in os.listdir(block_dir):
                if file.endswith('.block.json'):
                    sign_id = file.replace('.block.json', '')
                    if sign_id not in database_blocks:
                        os.remove(os.path.join(block_dir, file))
                        print_if_not_quiet(ConsoleStyle.warning(f"Usunięto blok [{category_lower}/{file}] (nie istnieje w bazie)"))
                        removed_count += 1

    # Sprawdź i usuń tekstury dla nieistniejących znaków
    for category in data['categories'].keys():
        category_lower = category.lower()
        texture_dir = f"RP/textures/blocks/averse/{category_lower}"
        if os.path.exists(texture_dir):
            for file in os.listdir(texture_dir):
                if file.endswith('.png'):
                    sign_id = file.replace('.png', '')
                    if sign_id not in database_blocks:
                        os.remove(os.path.join(texture_dir, file))
                        print_if_not_quiet(ConsoleStyle.warning(f"Usunięto teksturę [{category_lower}/{file}] (nie istnieje w bazie)"))
                        removed_count += 1

    # Usuń wpisy z terrain_texture.json dla nieistniejących znaków
    terrain_path = "RP/textures/terrain_texture.json"
    if os.path.exists(terrain_path):
        with open(terrain_path, 'r') as f:
            terrain_data = json.load(f)

        keys_to_remove = []
        for key in terrain_data['texture_data']:
            if key.startswith('polish_road_sign:'):
                sign_id = key.replace('polish_road_sign:', '')
                if sign_id not in database_blocks:
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del terrain_data['texture_data'][key]
            print_if_not_quiet(ConsoleStyle.warning(f"Usunięto [{key}] z terrain_texture.json (nie istnieje w bazie)"))
            removed_count += 1

        with open(terrain_path, 'w') as f:
            json.dump(terrain_data, f, indent=2)

    if removed_count > 0:
        print_if_not_quiet(ConsoleStyle.success(f"Czyszczenie zakończone - usunięto {removed_count} plików"))
    else:
        print_if_not_quiet(ConsoleStyle.info("Brak plików do usunięcia"))
    print_if_not_quiet(ConsoleStyle.divider())

def cleanup_all_files(data):
    """Usuń wszystkie istniejące bloki, modele, tekstury PNG i ich definicje"""
    ConsoleStyle.print_section("CZYSZCZENIE WSZYSTKICH PLIKÓW")

    # Pobierz kategorie z bazy danych
    categories = list(data['categories'].keys())
    print_if_not_quiet(ConsoleStyle.info(f"Znalezione kategorie: {', '.join(categories)}"))

    removed_count = 0

    # Usuń wszystkie bloki
    for category in categories:
        category_lower = category.lower()
        block_dir = f"BP/blocks/{category_lower}"
        if os.path.exists(block_dir):
            for file in os.listdir(block_dir):
                if file.endswith('.block.json'):
                    os.remove(os.path.join(block_dir, file))
                    print_if_not_quiet(ConsoleStyle.warning(f"Usunięto blok [{category_lower}/{file}]"))
                    removed_count += 1

    # Usuń wszystkie modele 3D
    models_dir = "RP/models/blocks"
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.startswith('road_sign_') and file.endswith('.geo.json'):
                os.remove(os.path.join(models_dir, file))
                print_if_not_quiet(ConsoleStyle.warning(f"Usunięto model [{file}]"))
                removed_count += 1

    # Usuń wszystkie tekstury PNG (zachowaj SVG)
    for category in categories:
        category_lower = category.lower()
        texture_dir = f"RP/textures/blocks/averse/{category_lower}"
        if os.path.exists(texture_dir):
            for file in os.listdir(texture_dir):
                if file.endswith('.png'):
                    os.remove(os.path.join(texture_dir, file))
                    print_if_not_quiet(ConsoleStyle.warning(f"Usunięto teksturę [{category_lower}/{file}]"))
                    removed_count += 1

    # Usuń tekstury tła
    sign_backs_dir = "RP/textures/blocks/reverse"
    if os.path.exists(sign_backs_dir):
        for file in os.listdir(sign_backs_dir):
            if file.endswith('.png'):
                os.remove(os.path.join(sign_backs_dir, file))
                print_if_not_quiet(ConsoleStyle.warning(f"Usunięto teksturę tła [{file}]"))
                removed_count += 1

    # Wyczyść terrain_texture.json (zachowaj tylko nie-polish_road_sign wpisy)
    terrain_path = "RP/textures/terrain_texture.json"
    if os.path.exists(terrain_path):
        with open(terrain_path, 'r') as f:
            terrain_data = json.load(f)

        # Usuń wszystkie polish_road_sign wpisy
        keys_to_remove = []
        for key in terrain_data['texture_data']:
            if key.startswith('polish_road_sign'):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del terrain_data['texture_data'][key]
            print_if_not_quiet(ConsoleStyle.warning(f"Usunięto [{key}] z terrain_texture.json"))
            removed_count += 1

        with open(terrain_path, 'w') as f:
            json.dump(terrain_data, f, indent=2)

    if removed_count > 0:
        print_if_not_quiet(ConsoleStyle.success(f"Czyszczenie zakończone - usunięto {removed_count} plików"))
    else:
        print_if_not_quiet(ConsoleStyle.info("Brak plików do usunięcia"))
    print_if_not_quiet(ConsoleStyle.divider())


def get_all_languages(data):
    """Dynamicznie wykryj wszystkie języki z bazy danych"""
    langs = set()
    for cat in data['categories'].values():
        if 'translations' in cat:
            langs.update(cat['translations'].keys())
        for sign in cat['blocks'].values():
            if 'translations' in sign:
                langs.update(sign['translations'].keys())
    return sorted(langs)

def update_language_files(data):
    """Aktualizuj pliki językowych na podstawie bazy danych"""
    ConsoleStyle.print_section("AKTUALIZACJA PLIKÓW JĘZYKOWYCH")
    
    languages = get_all_languages(data)
    lang_map = {lang: {} for lang in languages}
    total_translations = 0
    # Kategorie
    for cat_key, cat in data['categories'].items():
        if 'translations' in cat:
            for lang in cat['translations']:
                group_key = cat.get('crafting_group', cat_key)
                lang_map[lang][f'polish_road_sign:{group_key}'] = cat['translations'][lang]
    # Znaki
    for cat in data['categories'].values():
        for sign_id, sign in cat['blocks'].items():
            if 'translations' in sign:
                for lang in sign['translations']:
                    lang_map[lang][f'tile.polish_road_sign:{sign_id}.name'] = sign['translations'][lang]
    # Zapisz pliki
    for lang in lang_map:
        lang_file = f"RP/texts/{lang}.lang"
        existing_content = {}
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        existing_content[key] = value
        existing_content.update(lang_map[lang])
        # Naturalne sortowanie
        sorted_keys = natsorted(existing_content.keys())
        with open(lang_file, 'w', encoding='utf-8') as f:
            for key in sorted_keys:
                f.write(f"{key}={existing_content[key]}\n")
            print_if_not_quiet(ConsoleStyle.success(f"Zaktualizowano [{lang_file}] ({len(lang_map[lang])} tłumaczeń)"))
        total_translations += len(lang_map[lang])
    
    print_if_not_quiet(ConsoleStyle.info(f"Łącznie zaktualizowano {len(languages)} języków i {total_translations} tłumaczeń"))

def update_crafting_catalog(data):
    ConsoleStyle.print_section("AKTUALIZACJA KATALOGU CRAFTING")
    
    catalog_path = "BP/item_catalog/crafting_item_catalog.json"
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Przygotuj grupy na podstawie bazy
    groups = []
    total_items = 0
    for cat_key, cat in data['categories'].items():
        group = {
            "group_identifier": {
                "icon": f"polish_road_sign:{cat.get('icon', next(iter(cat['blocks'])))}",
                "name": f"polish_road_sign:{cat.get('crafting_group', cat_key)}"
            },
            "items": natsorted([f"polish_road_sign:{sign_id}" for sign_id in cat['blocks']])
        }
        groups.append(group)
        total_items += len(cat['blocks'])
    
    # Zastąp grupy w katalogu
    for category in catalog["minecraft:crafting_items_catalog"]["categories"]:
        category["groups"] = groups
    
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print_if_not_quiet(ConsoleStyle.success(f"Zaktualizowano [{catalog_path}]"))
    print_if_not_quiet(ConsoleStyle.info(f"Łącznie {len(groups)} kategorii i {total_items} znaków"))

def update_all_related_files(data):
    update_language_files(data)
    update_crafting_catalog(data)


def main():
    """Główna funkcja"""
    parser = argparse.ArgumentParser(
        description="Przetwarza znaki drogowe z bazy danych",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python3 road_sign_processor.py a-1
  python3 road_sign_processor.py B_5 c-10 d_25
  python3 road_sign_processor.py A1 B2 C3 D4
  python3 road_sign_processor.py all  # przetwórz wszystkie znaki
  python3 road_sign_processor.py category:A  # przetwórz kategorię A
  python3 road_sign_processor.py category:B --skip-download  # przetwórz kategorię B offline
  python3 road_sign_processor.py category:B -s  # przetwórz kategorię B offline (skrót)
  python3 road_sign_processor.py a_1 --skip-download  # użyj lokalnych plików SVG
  python3 road_sign_processor.py a_1 -s  # użyj lokalnych plików SVG (skrót)
  python3 road_sign_processor.py a_1 --force-rebuild  # wymuś przebudowanie tekstur
  python3 road_sign_processor.py a_1 -f  # wymuś przebudowanie tekstur (skrót)
  python3 road_sign_processor.py all --force-rebuild  # wymuś przebudowanie wszystkich tekstur
  python3 road_sign_processor.py all -f  # wymuś przebudowanie wszystkich tekstur (skrót)
  python3 road_sign_processor.py a_1 --quiet  # tryb cichy (tylko błędy)
  python3 road_sign_processor.py a_1 -q  # tryb cichy (tylko błędy) (skrót)

Skrypt automatycznie usuwa pliki dla znaków, które nie istnieją w bazie danych
        """
    )

    parser.add_argument('blocks', nargs='+', help='Kody znaków do przetworzenia (np. a_1, b_5) lub "all" dla wszystkich znaków, lub "category:X" dla kategorii')
    parser.add_argument('--skip-download', '-s', action='store_true', help='Tryb offline - użyj lokalnych plików SVG')
    parser.add_argument('--force-rebuild', '-f', action='store_true', help='Wymuś przebudowanie tekstur')
    parser.add_argument('--quiet', '-q', action='store_true', help='Tryb cichy (tylko błędy)')
    
    args = parser.parse_args()

    database_path = "database.json"

    if not os.path.exists(database_path):
        print_if_not_quiet(ConsoleStyle.error(f"Nie znaleziono bazy danych [{database_path}]"))
        return

    # Sprawdź flagę --skip-download / -s
    skip_download = args.skip_download
    if skip_download:
        print_if_not_quiet(ConsoleStyle.info("Tryb offline: pomijam pobieranie plików SVG z internetu"))
        print_if_not_quiet(ConsoleStyle.info("Używam lokalnych plików SVG"))

    # Sprawdź flagę --force-rebuild / -f
    force_rebuild = args.force_rebuild
    if force_rebuild:
        print_if_not_quiet(ConsoleStyle.process("Tryb wymuszenia przebudowania: usuwam istniejące tekstury przed przetwarzaniem"))

    # Sprawdź flagę --quiet / -q
    quiet_mode = args.quiet
    if quiet_mode:
        ConsoleStyle.set_quiet_mode(True)

    # Wczytaj bazę danych
    with open(database_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ConsoleStyle.print_section("PRZETWARZANIE ZNAKÓW DROGOWYCH")

    success_count = 0
    total_count = 0
    errors = []

    # Sprawdź, czy przetwarzamy wszystkie znaki
    if len(args.blocks) == 1 and args.blocks[0].lower() == 'all':
        print_if_not_quiet(ConsoleStyle.info("Przetwarzanie wszystkich znaków z bazy danych..."))

        # Wyczyść wszystkie pliki przed przetwarzaniem
        cleanup_all_files(data)

        # Pobierz kategorie z bazy danych
        categories = list(data['categories'].keys())
        for category in categories:
            if category in data['categories']:
                print_if_not_quiet(ConsoleStyle.section(f"Kategoria [{category}]"))
                blocks = data['categories'][category]['blocks']

                for sign_id in blocks:
                    total_count += 1

                    # Sprawdź, czy znak ma link do pliku Wikipedii
                    if 'wikipedia_file_page' not in blocks[sign_id]:
                        print_if_not_quiet(ConsoleStyle.warning(f"{sign_id}: brak linku do pliku Wikipedii"))
                        continue

                    wikipedia_file_page = blocks[sign_id]['wikipedia_file_page']
                    sign_width = int(blocks[sign_id].get('sign_width', 900))
                    sign_height = int(blocks[sign_id].get('sign_height', 900))

                    if process_sign(sign_id, wikipedia_file_page, sign_width, sign_height, database_path, skip_download,
                                    force_rebuild):
                        success_count += 1
                    else:
                        errors.append(f"{sign_id}: błąd przetwarzania")

                    # Dodaj delay między requestami (tylko jeśli nie pomijamy pobierania)
                    if not skip_download:
                        time.sleep(1)

    # Sprawdź, czy przetwarzamy konkretną kategorię
    elif len(args.blocks) == 1 and args.blocks[0].lower().startswith('category:'):
        category_param = args.blocks[0].lower().replace('category:', '')
        category = category_param.upper()

        if category not in data['categories']:
            print_if_not_quiet(ConsoleStyle.error(f"Nie znaleziono kategorii [{category}] w bazie danych"))
            print_if_not_quiet(ConsoleStyle.info(f"Dostępne kategorie: {', '.join(list(data['categories'].keys()))}"))
            return

        print_if_not_quiet(ConsoleStyle.info(f"Przetwarzanie kategorii [{category}]..."))

        # Wyczyść pliki dla tej kategorii przed przetwarzaniem
        cleanup_category_files(data, category)

        blocks = data['categories'][category]['blocks']
        print_if_not_quiet(ConsoleStyle.info(f"Znaleziono [{len(blocks)}] znaków w kategorii [{category}]"))

        for sign_id in blocks:
            total_count += 1

            # Sprawdź, czy znak ma link do pliku Wikipedii
            if 'wikipedia_file_page' not in blocks[sign_id]:
                print_if_not_quiet(ConsoleStyle.warning(f"{sign_id}: brak linku do pliku Wikipedii"))
                continue

            wikipedia_file_page = blocks[sign_id]['wikipedia_file_page']
            sign_width = int(blocks[sign_id].get('sign_width', 900))
            sign_height = int(blocks[sign_id].get('sign_height', 900))

            if process_sign(sign_id, wikipedia_file_page, sign_width, sign_height, database_path, skip_download,
                            force_rebuild):
                success_count += 1
            else:
                errors.append(f"{sign_id}: błąd przetwarzania")

            # Dodaj delay między requestami (tylko jeśli nie pomijamy pobierania)
            if not skip_download:
                time.sleep(1)
    else:
        # Przetwórz podane znaki
        for sign_code in args.blocks:
            total_count += 1

            # Normalizuj kod znaku
            sign_id = normalize_sign_id(sign_code)
            print_if_not_quiet(ConsoleStyle.info(f"Kod: {sign_code} → {sign_id}"))

            # Znajdź znak w bazie
            sign_data = find_sign_in_database(sign_id, data)
            if not sign_data:
                print_if_not_quiet(ConsoleStyle.error(f"Nie znaleziono znaku [{sign_id}] w bazie danych"))
                errors.append(f"{sign_id}: nie znaleziono w bazie")
                continue

            # Sprawdź, czy znak ma link do pliku Wikipedii
            if 'wikipedia_file_page' not in sign_data:
                print_if_not_quiet(ConsoleStyle.warning(f"{sign_id}: brak linku do pliku Wikipedii"))
                errors.append(f"{sign_id}: brak linku do pliku Wikipedii")
                continue

            wikipedia_file_page = sign_data['wikipedia_file_page']
            sign_width = int(sign_data.get('sign_width', 900))
            sign_height = int(sign_data.get('sign_height', 900))

            print_if_not_quiet(ConsoleStyle.info(f"Docelowe wymiary: {sign_width}x{sign_height}"))

            if process_sign(sign_id, wikipedia_file_page, sign_width, sign_height, database_path, skip_download,
                            force_rebuild):
                success_count += 1
            else:
                errors.append(f"{sign_id}: błąd przetwarzania")

    # Wyświetl podsumowanie
    ConsoleStyle.print_summary(success_count, total_count, errors)

    # Wyczyść pliki dla znaków, które nie istnieją w bazie danych
    cleanup_orphaned_files(data)

    # Aktualizuj pliki językowe i katalog crafting
    if success_count > 0:
        update_all_related_files(data)

    print_if_not_quiet(ConsoleStyle.divider())
    print_if_not_quiet(ConsoleStyle.success("Wszystkie operacje zakończone pomyślnie!"))
    print_if_not_quiet(ConsoleStyle.divider())


if __name__ == "__main__":
    main()
