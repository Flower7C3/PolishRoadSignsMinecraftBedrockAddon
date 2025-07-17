from PIL import Image, ImageDraw
import math
import os

def draw_circle(path):
    im = Image.new('RGBA', (128,128), (0,0,0,0))
    draw = ImageDraw.Draw(im)
    draw.ellipse([1,1,126,126], outline='black', width=2)
    im.save(path)

def draw_square(path):
    im = Image.new('RGBA', (128,128), (0,0,0,0))
    draw = ImageDraw.Draw(im)
    draw.rectangle([1,1,126,126], outline='black', width=2)
    im.save(path)

def draw_triangle(path):
    im = Image.new('RGBA', (128,128), (0,0,0,0))
    draw = ImageDraw.Draw(im)
    points = [(64,3), (125,125), (3,125)]
    draw.polygon(points, outline='black', width=2)
    im.save(path)

def draw_octagon(path):
    im = Image.new('RGBA', (128,128), (0,0,0,0))
    draw = ImageDraw.Draw(im)
    r = 62
    cx, cy = 64, 64
    points = [(cx + r*math.cos(math.radians(22.5 + 45*i)), cy + r*math.sin(math.radians(22.5 + 45*i))) for i in range(8)]
    draw.polygon(points, outline='black', width=2)
    im.save(path)

def draw_diamond(path):
    im = Image.new('RGBA', (128,128), (0,0,0,0))
    draw = ImageDraw.Draw(im)
    points = [(64,3), (125,64), (64,125), (3,64)]
    draw.polygon(points, outline='black', width=2)
    im.save(path)

def main():
    os.makedirs('RP/textures/blocks/sign_sides', exist_ok=True)
    draw_circle('RP/textures/blocks/sign_sides/circle_side.png')
    draw_square('RP/textures/blocks/sign_sides/square_side.png')
    draw_triangle('RP/textures/blocks/sign_sides/triangle_side.png')
    draw_octagon('RP/textures/blocks/sign_sides/octagon_side.png')
    draw_diamond('RP/textures/blocks/sign_sides/diamond_side.png')
    print('Wygenerowano tekstury boczne znaków!')

if __name__ == '__main__':
    main() 