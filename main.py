import png
import os

import MapMaker as mm
import pngParser as pp
from PNGCombiner import Combine

def main():
    print("Thank you for using my Map Making tool. \n Press 1 to parse a Sprite Sheet \n Press 2 to create a random map based on the files already loaded into the ParsedPNGs folder")
    function = input()
    match function:
        case '1':
            parse = pp.Parse()
            print("You chose Parse")
        case '2':
            activeFloor = mm.Floor()
            print("You chose to create a new Floor")
            src_path = 'ParsedPNGs\\'
            mapOptions = []
            for files in os.listdir(src_path):
                mapOptions.append(files)
            print(f"Select the index of one of the following map locations: ")
            for (i, maps) in enumerate(mapOptions):
                print(i, maps)
            mapChoice = int(input())
            if(mapChoice < len(mapOptions)):
                Combine(activeFloor, mapOptions[mapChoice])
            else:
                print(f"Directory {mapChoice} not found")
            #Combine(activeFloor)

if __name__ == '__main__':
    main()