#!/usr/bin/env python3
"""
Simple Road Sign Image Fetcher using curl
Fetches images from Wikipedia, scales them to 128px width while preserving aspect ratio,
and updates the database with image dimensions.
"""

import os
import json
import subprocess
import tempfile
import sys
import re
import time
from PIL import Image

class RoadSignFetcher:
    def __init__(self):
        self.errors = []
        self.success_count = 0
        self.total_count = 0
        
    def get_svg_url_from_wikipedia(self, wiki_page_url):
        """Extract SVG URL from Wikipedia page using curl and grep"""
        try:
            print(f"Fetching Wikipedia page: {wiki_page_url}")
            
            # Use curl to fetch the page
            cmd = [
                'curl', '-s', '-L',
                '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '--insecure',  # Disable SSL verification
                wiki_page_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Curl error: {result.stderr}")
                return None
            
            page_content = result.stdout
            
            # Look for .fullImageLink a element
            full_image_pattern = r'href="([^"]*\.svg)"[^>]*class="[^"]*fullImageLink[^"]*"'
            match = re.search(full_image_pattern, page_content)
            if match:
                svg_url = match.group(1)
                if svg_url.startswith('//'):
                    svg_url = 'https:' + svg_url
                elif svg_url.startswith('/'):
                    svg_url = 'https://pl.wikipedia.org' + svg_url
                print(f"Found SVG URL: {svg_url}")
                return svg_url
            
            # Fallback: look for any SVG link to upload.wikimedia.org
            upload_pattern = r'https://upload\.wikimedia\.org/[^"]*\.svg'
            match = re.search(upload_pattern, page_content)
            if match:
                svg_url = match.group(0)
                print(f"Found SVG URL (fallback): {svg_url}")
                return svg_url
            
            print("No SVG link found on page")
            return None
            
        except Exception as e:
            print(f"Error fetching Wikipedia page: {e}")
            return None
    
    def download_svg(self, svg_url, temp_path):
        """Download SVG file using curl"""
        try:
            print(f"Downloading SVG: {svg_url}")
            
            cmd = [
                'curl', '-s', '-L',
                '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '--insecure',
                '-o', temp_path,
                svg_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Curl download error: {result.stderr}")
                return False
            
            return True
        except Exception as e:
            print(f"Error downloading SVG: {e}")
            return False
    
    def convert_svg_to_png(self, svg_path, output_path, target_width=128):
        """Convert SVG to PNG with preserved aspect ratio"""
        try:
            print(f"Converting SVG to PNG: {output_path}")
            
            # Use Inkscape to convert SVG to PNG
            cmd = [
                'inkscape',
                svg_path,
                '--export-type=png',
                f'--export-width={target_width}',
                f'--export-filename={output_path}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Inkscape error: {result.stderr}")
                return False
            
            return True
        except Exception as e:
            print(f"Error converting SVG: {e}")
            return False
    
    def get_image_dimensions(self, image_path):
        """Get image dimensions"""
        try:
            with Image.open(image_path) as img:
                return img.size[0], img.size[1]
        except Exception as e:
            print(f"Error getting image dimensions: {e}")
            return None, None
    
    def update_database_dimensions(self, sign_id, category, width, height):
        """Update database with image dimensions"""
        try:
            with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update the sign's image dimensions
            if category in data['road_signs'] and sign_id in data['road_signs'][category]['signs']:
                data['road_signs'][category]['signs'][sign_id]['image_width'] = str(width)
                data['road_signs'][category]['signs'][sign_id]['image_height'] = str(height)
                
                # Also update image_dimensions field if it exists
                if 'image_dimensions' in data['road_signs'][category]['signs'][sign_id]:
                    data['road_signs'][category]['signs'][sign_id]['image_dimensions'] = f"{width}x{height}"
                
                # Write back to file
                with open('road_signs_full_database.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"Updated database with dimensions: {width}x{height}")
                return True
            else:
                print(f"Sign {sign_id} not found in database")
                return False
                
        except Exception as e:
            print(f"Error updating database: {e}")
            return False
    
    def get_category_from_sign_id(self, sign_id):
        """Extract category from sign ID (e.g., 'a_1' -> 'A')"""
        if sign_id.startswith('a_'):
            return 'A'
        elif sign_id.startswith('b_'):
            return 'B'
        elif sign_id.startswith('c_'):
            return 'C'
        elif sign_id.startswith('d_'):
            return 'D'
        else:
            return None
    
    def process_sign(self, sign_id):
        """Process a single sign"""
        category = self.get_category_from_sign_id(sign_id)
        if not category:
            self.errors.append(f"{sign_id}: Could not determine category from sign ID")
            return False
            
        print(f"\nProcessing sign: {sign_id} (category: {category})")
        
        # Load database
        try:
            with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.errors.append(f"{sign_id}: Database error - {e}")
            return False
        
        # Get Wikipedia page URL
        try:
            wiki_page_url = data['road_signs'][category]['signs'][sign_id]['wikipedia_file_page']
        except KeyError:
            self.errors.append(f"{sign_id}: No wikipedia_file_page URL found")
            return False
        
        # Get SVG URL
        svg_url = self.get_svg_url_from_wikipedia(wiki_page_url)
        if not svg_url:
            self.errors.append(f"{sign_id}: Could not extract SVG URL")
            return False
        
        # Create output directory
        output_dir = f"RP/textures/blocks/{category.lower()}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{sign_id}.png"
        
        # Download and convert
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as temp_file:
            temp_svg_path = temp_file.name
        
        try:
            # Download SVG
            if not self.download_svg(svg_url, temp_svg_path):
                self.errors.append(f"{sign_id}: Failed to download SVG")
                return False
            
            # Convert to PNG
            if not self.convert_svg_to_png(temp_svg_path, output_path):
                self.errors.append(f"{sign_id}: Failed to convert SVG to PNG")
                return False
            
            # Get dimensions
            width, height = self.get_image_dimensions(output_path)
            if width is None or height is None:
                self.errors.append(f"{sign_id}: Could not get image dimensions")
                return False
            
            # Update database
            if self.update_database_dimensions(sign_id, category, width, height):
                print(f"✅ Successfully processed {sign_id}: {width}x{height}")
                self.success_count += 1
                return True
            else:
                self.errors.append(f"{sign_id}: Failed to update database")
                return False
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_svg_path):
                os.unlink(temp_svg_path)
    
    def process_all_signs(self):
        """Process all signs from database"""
        print("Processing all signs from database...")
        
        # Load database
        try:
            with open('road_signs_full_database.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading database: {e}")
            return
        
        # Process each category
        for category in ['A', 'B', 'C', 'D']:
            if category in data['road_signs']:
                print(f"\nProcessing category {category}...")
                signs = data['road_signs'][category]['signs']
                
                for sign_id in signs:
                    self.total_count += 1
                    self.process_sign(sign_id)
                    
                    # Add delay to be respectful to servers
                    time.sleep(1)
    
    def print_summary(self):
        """Print summary of processing results"""
        print(f"\n{'='*50}")
        print("📊 PROCESSING SUMMARY")
        print(f"{'='*50}")
        print(f"Total signs processed: {self.total_count}")
        print(f"Successfully processed: {self.success_count}")
        print(f"Failed: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print(f"\n✅ All signs processed successfully!")

def main():
    """Main function"""
    print("🚦 Road Sign Image Fetcher (Simple Python)")
    print("=" * 50)
    
    fetcher = RoadSignFetcher()
    
    if len(sys.argv) == 2:
        # Process specific sign
        sign_id = sys.argv[1]
        
        fetcher.process_sign(sign_id)
        fetcher.total_count = 1
        
    elif len(sys.argv) == 1:
        # Process all signs
        fetcher.process_all_signs()
        
    else:
        print("Usage: python resize_simple.py [sign_id]")
        print("  If no arguments provided, processes all signs from database")
        print("  Example: python resize_simple.py a_1")
        sys.exit(1)
    
    fetcher.print_summary()

if __name__ == "__main__":
    main() 