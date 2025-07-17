#!/usr/bin/env python3
import json
import os
from pathlib import Path

def get_existing_blocks():
    """Get all existing block files from BP/blocks directory"""
    blocks = []
    for block_file in Path("BP/blocks").rglob("*.block.json"):
        # Convert path like "BP/blocks/a/a_1.block.json" to "a/a_1"
        relative_path = block_file.relative_to(Path("BP/blocks"))
        block_id = str(relative_path).replace(".block.json", "")
        blocks.append(block_id)
    return sorted(blocks)

def get_catalog_blocks():
    """Get all blocks currently in the crafting catalog"""
    with open("BP/item_catalog/crafting_item_catalog.json", "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    catalog_blocks = []
    for category in catalog["minecraft:crafting_items_catalog"]["categories"]:
        for group in category["groups"]:
            catalog_blocks.extend(group["items"])
    
    return catalog_blocks

def update_catalog():
    """Update the crafting catalog with missing blocks"""
    existing_blocks = get_existing_blocks()
    catalog_blocks = get_catalog_blocks()
    
    # Convert catalog blocks to match the format (remove polish_road_sign: prefix)
    catalog_block_ids = [block.replace("polish_road_sign:", "") for block in catalog_blocks]
    
    # Find missing blocks
    missing_blocks = []
    for block in existing_blocks:
        if block not in catalog_block_ids:
            missing_blocks.append(block)
    
    print(f"Found {len(missing_blocks)} missing blocks:")
    for block in missing_blocks:
        print(f"  - {block}")
    
    # Load current catalog
    with open("BP/item_catalog/crafting_item_catalog.json", "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    # Add missing blocks to appropriate groups
    for block in missing_blocks:
        category = block.split("/")[0]  # a, b, c, or d
        
        # Find the appropriate group
        for group in catalog["minecraft:crafting_items_catalog"]["categories"][0]["groups"]:
            group_name = group["group_identifier"]["name"]
            if category == "a" and "warning_signs" in group_name:
                group["items"].append(f"polish_road_sign:{block}")
                break
            elif category == "b" and "prohibition_signs" in group_name:
                group["items"].append(f"polish_road_sign:{block}")
                break
            elif category == "c" and "mandatory_signs" in group_name:
                group["items"].append(f"polish_road_sign:{block}")
                break
            elif category == "d" and "information_signs" in group_name:
                group["items"].append(f"polish_road_sign:{block}")
                break
    
    # Sort items in each group
    for group in catalog["minecraft:crafting_items_catalog"]["categories"][0]["groups"]:
        group["items"].sort()
    
    # Save updated catalog
    with open("BP/item_catalog/crafting_item_catalog.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpdated crafting_item_catalog.json with {len(missing_blocks)} missing blocks")

if __name__ == "__main__":
    update_catalog() 