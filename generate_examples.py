#!/usr/bin/env python3
import json
import sys
from collections import Counter
from console_utils import ConsoleStyle, print_header, print_usage


def get_example_combinations():
    """Generate example combinations for different shape/size combinations"""
    with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Collect all shape and size combinations
    shape_size_combinations = Counter()
    shape_size_examples = {}

    for category in data['road_signs'].values():
        for sign_id, sign in category['signs'].items():
            width = sign.get('sign_width', 900)
            height = sign.get('sign_height', 900)
            shape = sign.get('sign_shape', 'rectangle')
            
            combination_key = f"{shape}_{width}x{height}"
            shape_size_combinations[combination_key] += 1
            
            if combination_key not in shape_size_examples:
                shape_size_examples[combination_key] = sign_id

    return shape_size_combinations, shape_size_examples


def generate_test_commands():
    """Generate test commands for different combinations"""
    shape_size_combinations, shape_size_examples = get_example_combinations()
    
    print(ConsoleStyle.section("GENEROWANIE PRZYKŁADOWYCH KOMEND TESTOWYCH"))
    print(ConsoleStyle.divider())

    # Show combinations
    print(f"🔗 KOMBINACJE KSZTAŁTÓW I WYMIARÓW ({len(shape_size_combinations)})")
    example_combinations = set()
    for combination, count in shape_size_combinations.items():
        shape, size = combination.split('_', 1)
        example_combinations.add(shape_size_examples[combination])
        print(f"  - {shape} {size}: {count} znaków (przykład: {shape_size_examples[combination]})")

    # Generate test commands
    print(f"\n🖥️ KOMENDY TESTOWE")
    print(ConsoleStyle.divider())
    
    # Basic test command
    basic_command = f"python3 road_sign_processor.py {' '.join([f'{code}' for code in example_combinations])} -s -f"
    print(f"📋 Test wszystkich kombinacji:")
    print(f"  {basic_command}")
    
    # Build and test command
    build_test_command = f"{basic_command} && python3 build.py -m -t"
    print(f"\n🚀 Test z budowaniem i instalacją:")
    print(f"  {build_test_command}")
    
    # Individual category tests
    print(f"\n📂 Testy pojedynczych kategorii:")
    categories = ['A', 'B', 'C', 'D', 'F', 'G', 'T', 'U']
    for category in categories:
        category_command = f"python3 road_sign_processor.py category:{category} -s -f && python3 build.py -m -t"
        print(f"  Kategoria {category}: {category_command}")
    
    # Quick test with few examples
    quick_examples = list(example_combinations)[:5]  # First 5 examples
    quick_command = f"python3 road_sign_processor.py {' '.join(quick_examples)} -s -f && python3 build.py -m -t"
    print(f"\n⚡ Szybki test (5 przykładów):")
    print(f"  {quick_command}")
    
    return example_combinations


def generate_development_commands():
    """Generate development workflow commands"""
    print(ConsoleStyle.section("KOMENDY PRACY DEWELOPERSKIEJ"))
    print(ConsoleStyle.divider())
    
    commands = [
        ("🔍 Weryfikacja projektu", "python3 verify_all.py"),
        ("📦 Budowanie wszystkich formatów", "python3 build.py -a"),
        ("🧪 Test lokalny", "python3 build.py -m -t"),
        ("🔄 Pełny cykl testowy", "python3 road_sign_processor.py all -s -f && python3 build.py -a -t"),
        ("📊 Analiza statystyk", "python3 verify_all.py | grep -E '(STATYSTYKI|PROBLEMY)'"),
        ("🧹 Czyszczenie", "rm -rf dist/ && python3 road_sign_processor.py all -s -f"),
    ]
    
    for description, command in commands:
        print(f"{description}:")
        print(f"  {command}")
        print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generuje przykładowe komendy testowe i deweloperskie",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python3 generate_examples.py              # Generuje wszystkie komendy
  python3 generate_examples.py --test       # Tylko komendy testowe
  python3 generate_examples.py -t           # Tylko komendy testowe (skrót)
  python3 generate_examples.py --dev        # Tylko komendy deweloperskie
  python3 generate_examples.py -d           # Tylko komendy deweloperskie (skrót)
  python3 generate_examples.py --help       # Wyświetla pomoc
  python3 generate_examples.py -h           # Wyświetla pomoc (skrót)
        """
    )
    
    parser.add_argument('--test', '-t', action='store_true', 
                       help='Generuj tylko komendy testowe')
    parser.add_argument('--dev', '-d', action='store_true', 
                       help='Generuj tylko komendy deweloperskie')
    
    args = parser.parse_args()
    
    # If no specific option, show all
    if not any([args.test, args.dev]):
        args.test = True
        args.dev = True
    
    print_header("GENEROWANIE PRZYKŁADOWYCH KOMEND")
    
    if args.test:
        generate_test_commands()
        print(ConsoleStyle.divider())
    
    if args.dev:
        generate_development_commands()
    
    print(ConsoleStyle.success("✅ Generowanie komend zakończone!"))


if __name__ == "__main__":
    import argparse
    main() 