import png
import os

class ImgProcessor:
    def __init__(self, pixel_byte_width, width, pixels):
        self.pixel_byte_width = pixel_byte_width
        self.width = width
        self.pixels = pixels

    def isTile(self, tileStart):
        midPoint = self.PixelAddition(tileStart, 12, 12)
        try:
            r, g, b = self.pixels[midPoint:midPoint + 3]
        except Exception as e:
            #print(f" An Error Occurred: {e}")
            return 0

        return [r, g, b] != [0, 128, 128] 

    def PixelAddition(self, currLocation, offsetX, offsetY):
        return (currLocation + (self.pixel_byte_width * offsetX) + (self.pixel_byte_width * offsetY * self.width))

    def CurrPixelLocation(self, currLocation):
        pixelIndex = currLocation // self.pixel_byte_width
        x = pixelIndex % self.width
        y = pixelIndex // self.width


        return x,y
    
    def WriteTile(self, currTile, output_filepath, tileCount):
        tile = []
        tempTile = self.PixelAddition(currTile, 1, 0) # Remove if you want the border
        
        
        for _ in range(24):
            tempTile = self.PixelAddition(tempTile, 0, 1)
            tile.extend(self.pixels[tempTile:tempTile + 24 * self.pixel_byte_width]) #adds 24 pixels to tile
            
        # Convert the list to bytearray
        tile_pixels_bytes = bytearray(tile)

        # Write to a new PNG file named in order
        output_filename = f'{output_filepath}\\{tileCount}.png'  # Example output filename with a unique count
                        
        with open(output_filename, 'wb') as f:
            writer = png.Writer(24,24, alpha=True, greyscale=False)
                
            new_image_rows = [tile_pixels_bytes[j:j + 24 * self.pixel_byte_width] for j in range(0, len(tile_pixels_bytes), 24 * self.pixel_byte_width)]
            writer.write(f, new_image_rows)
            tileCount = tileCount + 1

        return -1
    
def Parse():
    # Calls actual program for each file in the src folder also updates status to user
    src_path = 'src\\'
    dungeonsParsed = []
    numParsed = 0
    totalFiles = 0

    for filename in os.listdir(src_path):
        totalFiles = totalFiles + 1

    for filename in os.listdir(src_path):
        file_path = os.path.join(src_path, filename)
        filename = os.path.splitext(filename)[0] #Splits text into a list then takes only the first element
        dungeonsParsed.append(filename)

        output_folder_path = f'ParsedPNGs\\{filename}'

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
        numParsed = numParsed + 1
        print('Currently ripping: ', dungeonsParsed[numParsed - 1], ' ', numParsed, ' of ', totalFiles, ' Files')
        OpenFile(file_path, output_folder_path)

# Return 4 if RGBa 3 if RGB
def isAlpha(metadata):
    if metadata["alpha"]:
        return 4
    else:
        return 3

def OpenFile(input_filepath, output_filepath):
    # Open the file in 'rb' means read binary 
    with open(input_filepath, 'rb') as f:
        reader = png.Reader(file=f)
        width, h, pixels, metadata = reader.read_flat()
        pixel_byte_width = isAlpha(metadata)
        processor = ImgProcessor(pixel_byte_width, width, pixels)  
        checkedTiles = 0 #Tiles we've looked at already
        tileCount = 0 #output tiles
        tableStart = (width * 145 * pixel_byte_width) + (6 * pixel_byte_width) #iterator that tracks which pixel we're on 
        firstTile = processor.PixelAddition(tableStart, 2, 17)
        
        currTile = firstTile

        numColumns = 8
        j = 0

        for _ in range(numColumns):

            # Loops for each row 
            for _ in range(96): #Where the fuck did I get this number?
            
                if (checkedTiles % 3 == 0 and checkedTiles != 0):
                    currTile = processor.PixelAddition(currTile, -75, 25) #move  tiles left and 1 down
                
                if (processor.isTile(currTile)):
                    processor.WriteTile(currTile, output_filepath, tileCount)
                    tileCount += 1

                currTile = processor.PixelAddition(currTile, 25, 0)
                checkedTiles += 1
            j+= 1
            checkedTiles = 0
            currTile = processor.PixelAddition(firstTile, (75 * j), 0) #Sets currTile to the start of the next column

