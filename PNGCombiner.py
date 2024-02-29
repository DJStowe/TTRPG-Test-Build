import png
import os

import MapMaker as mm

wall_filepath = 'ParsedPNGs\\Wall\\'
alt_wall_filepath = 'ParsedPNGs\\AltWalls\\'
ground_filepath = 'ParsedPNGs\\Ground\\'
template_filepath = 'ParsedPNGs\\template\\'


def WriteFiles(input_filepath, output_filepath):
    # Open the file in 'rb' means read binary 
    #with open(input_filepath, 'rb') as f:
    return 1


def Combine(activeFloor, mapName):
    
    tileList = []
    tileList = activeFloor.tiles.copy()
    
    count = 0
    line =  []
    for tiles in tileList:
        match tiles.type:
            case 'wall':
                line.append('w')
                #AddTile('wall')
            case 'floor':
                line.append('f')
            case 'stairsUp':
                line.append('u')
            case 'stairsDown':
                line.append('d')
            case 'door':
                line.append('0')
            case _:
                line.append('?')
        count += 1
        if count >= 100:
            print(''.join(line))
            line.clear()
            count = 0
    line.clear()
    return 1
