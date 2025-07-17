#!/bin/bash

# Lista tekstur 128x128 do przeskalowania
textures_128=(
    "RP/textures/blocks/d/d_47.png"
    "RP/textures/blocks/d/d_46.png"
    "RP/textures/blocks/d/d_44.png"
    "RP/textures/blocks/d/d_45.png"
    "RP/textures/blocks/d/d_41.png"
    "RP/textures/blocks/d/d_40.png"
    "RP/textures/blocks/d/d_30.png"
    "RP/textures/blocks/d/d_31.png"
    "RP/textures/blocks/d/d_33.png"
    "RP/textures/blocks/d/d_27.png"
    "RP/textures/blocks/d/d_32.png"
    "RP/textures/blocks/d/d_34.png"
    "RP/textures/blocks/d/d_28.png"
    "RP/textures/blocks/d/d_29.png"
)

echo "Przeskalowuję tekstury 128x128 do 64x64..."

for texture in "${textures_128[@]}"; do
    if [ -f "$texture" ]; then
        echo "Przeskalowuję: $texture"
        convert "$texture" -resize 64x64 "${texture}_temp"
        mv "${texture}_temp" "$texture"
    else
        echo "Plik nie istnieje: $texture"
    fi
done

echo "Zakończono przeskalowanie tekstur." 