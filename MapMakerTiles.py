import matplotlib.pyplot as plt
import random
import networkx
"""
This program generates random maps for TTRPG based on the Nintendo property Pokemon Mystery Dungeon
TODO List
Fix Hallways so they actually are attached
Decide if each class should have a list of tiles in it and add those for everything
Little things like dead ends need to exist to be more like the original game
Make random room locations less random
Add a hashing alg to convert string to seed (Probably something standard like SHA256 so pythonversions don't chenge the values) 
Might be a bug where two walls that are exactly touching will have a wall between them
"""

#Edit these if you want to change num of rooms or the size variance
#region
minRooms = 4 
maxRooms = 8
minRoomVariance = 6
maxRoomVariance = 12
#endregion



class Floor:
    def __init__(self, width=100, height=100):
        self.rooms = []

        #self.cornerX = [0, 100, 100, 0, 0]
        #self.cornerY = [0, 0, 100, 100, 0]
        self.width = width
        self.height = height
        self.numRooms = random.randint(minRooms, maxRooms) 
        self.hallways = []
        self.tiles = []
        #self.tiles = [Tile() for _ in range(width * height)]

    def CreateTiles(self):
        x, y = 0, 0
        while(x <= 100):
            y = 0
            while(y <= 100):
                newTile = Tile(x,y)
                self.tiles.append(newTile)
                y += 1
            x += 1
        return True
    
    def getTile(self, x, y):
        return self.tiles[y * self.width + x]

    def setTile(self, x, y, tileType):
        if(x <= self.width and y <= self.height):
            self.tiles[y * self.width + x].type = tileType
        else:
            return False

    def setTilesLine(self, x1, y1, x2, y2, tileType):
        if x1 == x2: #Vertical Line
            start_y = min(y1, y2)  
            end_y = max(y1, y2) 
            for y in range(start_y, end_y + 1):  
                self.tiles[y * self.width + x1].type = tileType
        
        elif y1 == y2: #Horizontal Line
            start_x = min(x1, x2)  
            end_x = max(x1, x2)  

            for x in range(start_x, end_x + 1):  
                self.tiles[y1 * self.width + x].type = tileType

    def setTileIf(self, x, y, typeToReplace, tileType):
        if(self.getTile(x, y).type == typeToReplace):
            self.setTile(x, y, tileType)
        else:
            print(f"Cannot make tile ({x}, {y}) a {tileType} because it is not {typeToReplace}")
            return False

    def AddRoom(self, *rooms):
        """Adds any amount of rooms 
        
        Args:
            *rooms: a single or list of rooms
        """
        for room in rooms:
            self.rooms.append(room)
            room.floor = self

    def MakeRooms(self):
        """Makes X rooms in random locations where X is a random number between minRooms & maxRooms
        """
        currNumRooms = len(self.rooms)
        while currNumRooms < self.numRooms:
            x = random.randint(1, 100)
            y = random.randint(1, 100)
            
            # Check if the coordinate is not used then create room
            if not any(room.x == x and room.y == y for room in self.rooms):
                self.AddRoom(Room(self, x,y))
                currNumRooms += 1

        return True
    

    def AddStairs(self):
        #Picks random rooms for stairs
        roomNumUp = random.randint(0, self.numRooms - 1) 
        while True:
            roomNumDown = random.randint(0, self.numRooms - 1)
            if roomNumUp != roomNumDown:
                break
        #Assignes each room a status for if it has stairs
        roomUp = self.rooms[roomNumUp]
        roomDown = self.rooms[roomNumDown]
        roomUp.stairs = 'Up'
        roomDown.stairs = 'Down'

        upX = random.randint(roomUp.botLeft[0] + 1, roomUp.topRight[0] - 1)
        upY = random.randint(roomUp.botLeft[1] + 1, roomUp.topRight[1] - 1)
        downX = random.randint(roomDown.botLeft[0] + 1, roomDown.topRight[0] - 1)
        downY = random.randint(roomDown.botLeft[1] + 1, roomDown.topRight[1] - 1)

        self.setTile(upX, upY, 'stairsUp')
        self.setTile(downX, downY, 'stairsDown')

        return (roomNumUp, roomNumDown)

    def AltDraw(self):
        x, y, count = 0, 0, 0
        line =  []
        for tiles in self.tiles:
            if tiles.type == 'wall':
                line.append('w')
            elif tiles.type == 'floor':
                line.append('f')
            elif tiles.type == 'stairsUp':
                line.append('u')
            elif tiles.type == 'stairsDown':
                line.append('d')
            elif tiles.type == 'door':
                line.append('0')
            else:
                line.append('?')
            count += 1
            if count >= 100:
                print(''.join(line))
                line.clear()
                count = 0
        return True
    
    def Draw(self):

        return 1

    def Draw(self):
        return 1

    def RemoveRoom(self, room):
        self.rooms.remove(room)
        for tile in room.tiles:
            self.setTile(tile.x, tile.y, 'wall')

    def AddHallways(self):
        for room in self.rooms:
            #Get closet room with no hall between
            closestRoom = room.FindClosest()
            if room is closestRoom:
                continue
            hallway = room.AddDoorBetween(closestRoom)
            room.ConnectHallway(closestRoom, hallway)
            #pick midpoint between rooms
            #Add hall straight from door to midpoint and midpoint to other door

        return -1
    

    
class Room:
    """
    Updating room class to a new implementation. I do not need the mid point so we will instead track an X,Y pair for the top left corner of each room
    Then just track width and height. This should simplify a ton of things 
    Room class allows for randomly generated rooms and combined rooms to be easily drawn
    Args:
        middle: list of 2 ints treated as X,Y coordinates
    """
    def __init__(self, floor, x, y):
        self.x = x
        self.y = y
        self.width = random.randint(minRoomVariance, maxRoomVariance)
        self.height = random.randint(minRoomVariance, maxRoomVariance)
        self.floor = floor
        self.tiles = []
        self.stairs = None
        self.connectedRooms = []
        self.numHalls = 0
        self.doors = []

        self.botLeft  = (self.x, self.y)
        self.topLeft  = (self.x, self.y + self.height)
        self.botRight = (self.x + self.width, self.y)
        self.topRight = (self.x + self.width, self.y + self.height)
        self.AssignTiles()

    def AssignTiles(self):
        for dx in range(self.width):
            for dy in range(self.height):
                x = self.x + dx
                y = self.y + dy
                # Ensure x, y are within floor bounds before setting the tile
                if 0 <= x < self.floor.width and 0 <= y < self.floor.height:
                    self.floor.setTile(x, y, 'floor')        

    def FindClosest(self):
        """
        Finds the closest room that is not already connected by a hallway

        returns:
            closestRoom - the room object with start points closest to that of the current room
        Limitations:
            Does not actually return the closest based on total size of the rooms, only returns the closest starting point
        """
        closestRoom = self
        closestDist = float('inf')
        currDist = 0
        for currroom in self.floor.rooms:
            #Ignore if same Room, already connected 
            if currroom == self or currroom in self.connectedRooms:
                continue
            currDist = ManDistance(self.x, self.y, currroom.x, currroom.y)
            if currDist < closestDist:
                closestDist = currDist
                closestRoom = currroom
        #print(f"The closest room to: {self.botLeft} is: {closestRoom.botLeft} and they are {closestDist} spaces apart")
        return closestRoom

    def AddDoorBetween(self, otherRoom):
        minDistance = float('inf')
        room1Doors = []
        room2Doors = []
        #Add door to each side of both rooms
        #Check which is closest. Add those to rooms
        #Then create hallway from those

        topDoor = (random.randint(self.topLeft[0], self.topRight[0]), self.topLeft[1])
        botDoor = (random.randint(self.botLeft[0], self.botRight[0]), self.botLeft[1])

        leftDoor  = (self.botLeft[0],  random.randint(self.botLeft[1], self.topLeft[1]))
        rightDoor = (self.botRight[0], random.randint(self.botRight[1], self.topRight[1]))
        
        OtopDoor = (random.randint(otherRoom.topLeft[0], otherRoom.topRight[0]), otherRoom.topLeft[1])
        ObotDoor = (random.randint(otherRoom.botLeft[0], otherRoom.botRight[0]), otherRoom.botLeft[1])
        OleftDoor  = (otherRoom.botLeft[0],  random.randint(otherRoom.botLeft[1], otherRoom.topLeft[1]))
        OrightDoor = (otherRoom.botRight[0], random.randint(otherRoom.botRight[1], otherRoom.topRight[1]))
        
        room1Doors.extend([topDoor,botDoor,leftDoor,rightDoor])
        room2Doors.extend([OtopDoor,ObotDoor,OleftDoor,OrightDoor])

        for door1 in room1Doors:
            for door2 in room2Doors:
                currDistance = ManDistance(door1[0], door1[1], door2[0], door2[1])
                if currDistance < minDistance:
                    minDistance = currDistance
                    selfDoor = door1
                    otherDoor = door2

        self.connectedRooms.append(otherRoom)
        otherRoom.connectedRooms.append(self)
        newHall = Hallway(self.floor, selfDoor[0], selfDoor[1], otherDoor[0], otherDoor[1])
        self.floor.hallways.append(newHall)
        return newHall

    def Intersect(self, otherRoom):
        """Finds if two rooms intersect. If so returns the coordinates for the intesecting rectangle 
        
        Args:
            otherRoom - Second room you are checking against
        """        
        interiorRectangle = []
        x_left = max(self.x, otherRoom.x)
        x_right = min(self.x + self.width, otherRoom.x + otherRoom.width)
        y_bottom = max(self.y - self.height, otherRoom.y - otherRoom.height)
        y_top = min(self.y, otherRoom.y)

        # Check if there is no overlap
        if x_right < x_left or y_bottom > y_top:
            return None

        interiorRectangle.append((x_left, y_top))
        interiorRectangle.append((x_right, y_top))
        interiorRectangle.append((x_right, y_bottom))
        interiorRectangle.append((x_left, y_bottom))
        # Returns overlapping rectangle corners
        return interiorRectangle

    
    def Delete(self):
        if (self.floor):
            self.floor.RemoveRoom(self)
        return 1    

    def ConnectHallway(self, otherRoom, hallway):
        midpoint = (0, 0)
        wall, otherWall = 'temp', 'temp'
        firstTileSelf, firstTileOther = 0, 0
        intersect1 = []
        intersect2 = []

        if(hallway.startX == self.botLeft[0]):
            wall = 'left'
            firstTileSelf = (hallway.startX - 1, hallway.startY)
            hallway.tiles.append(firstTileSelf)
        elif(hallway.startX == self.botRight[0]):
            wall = 'right'
            firstTileSelf = (hallway.startX + 1, hallway.startY)
            hallway.tiles.append(firstTileSelf)
        elif(hallway.startY == self.botLeft[1]):
            wall = 'bottom'
            firstTileSelf = (hallway.startX, hallway.startY - 1)
            hallway.tiles.append(firstTileSelf)
        elif(hallway.startY == self.topRight[1]):
            wall = 'top'
            firstTileSelf = (hallway.startX, hallway.startY + 1)
            hallway.tiles.append(firstTileSelf)

        if(hallway.endX == otherRoom.botLeft[0]):
            otherWall = 'left'
            firstTileOther = (hallway.endX - 1, hallway.endY)
            hallway.tiles.append(firstTileOther)
        elif(hallway.endX == otherRoom.botRight[0]):
            otherWall = 'right'
            firstTileOther = (hallway.endX + 1, hallway.endY)
            hallway.tiles.append(firstTileOther)
        elif(hallway.endY == otherRoom.botLeft[1]):
            otherWall = 'bottom'
            firstTileOther = (hallway.endX, hallway.endY - 1)
            hallway.tiles.append(firstTileOther)
        elif(hallway.endY == otherRoom.topRight[1]):
            otherWall = 'top'
            firstTileOther = (hallway.endX, hallway.endY + 1)
            hallway.tiles.append(firstTileOther)

        for tile in hallway.tiles:
            for nextTile in hallway.tiles:
                if tile == nextTile:
                    continue
                midX = Random(tile[0], nextTile[0])
                midY = Random(tile[1], nextTile[1])
                midpoint = (midX, midY)
        if(wall in {'left', 'right'}):
            intersect1 = (midpoint[0], firstTileSelf[1])
        elif(wall in {'top', 'bottom'}):
            intersect1 = (firstTileSelf[0], midpoint[1])

        if(otherWall in {'left', 'right'}):
            intersect2 = (midpoint[0], firstTileOther[1])
        elif(otherWall in {'top', 'bottom'}):
            intersect2 = (firstTileOther[0], midpoint[1])


        self.floor.setTilesLine(firstTileSelf[0], firstTileSelf[1], intersect1[0], intersect1[1], 'floor')
        self.floor.setTilesLine(firstTileOther[0], firstTileOther[1], intersect2[0], intersect2[1], 'floor')
        self.floor.setTilesLine(intersect1[0], intersect1[1], intersect2[0], intersect2[1], 'floor')

        return hallway

class Hallway:
    def __init__(self, floor, startX, startY, endX, endY):
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY
        self.tiles = []

        self.floor = floor
        self.tiles.append((startX, startY))
        self.tiles.append((endX, endY))
        self.AssignTiles()
    
    def AssignTiles(self):
        self.floor.setTileIf(self.startX, self.startY, 'wall', 'door')
        self.floor.setTileIf(self.endX, self.endY, 'wall', 'door')

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = 'wall'

#Manhattan Distance - count diagonals as 2 
def ManDistance(x1,y1,x2,y2):
    return abs(x2 - x1) + abs(y2 - y1)

def Random(x, y):
    if(x == y):
        return x
    if(x > y):
        return(random.randint(y,x))
    else:
        return(random.randint(x,y))

def main():

    floor = Floor()
    floor.CreateTiles()

#Testin purposes:
    #region
    #room1 = Room(floor, 20, 20)
    #room2 = Room(floor, 50, 50)
    #room3 = Room(floor, 10, 50)

   #floor.AddRoom(room1, room2, room3)
    floor.MakeRooms()
    floor.AddHallways()
    floor.AddStairs()
    floor.AltDraw()
    return 1

if __name__ == '__main__':
    main()