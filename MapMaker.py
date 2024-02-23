import matplotlib.pyplot as plt
import random
import networkx
"""
This program generates random maps for TTRPG based on the Nintendo property Pokemon Mystery Dungeon
TODO List
Maybe I should create everything as single rectangular rooms then at the end just have a check for if there's overlap 
    Simplifies everything a bunch. Still keep random width and height 
Combine rooms sometimes makes weird shapes
Make Hallways that connect rooms (Maybe reuse closest point code)
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
    def __init__(self):
        self.rooms = []
        self.rectangles = [] #TODO decide if we need this. It can allow us to track combined rooms as two smaller rooms
        self.cornerX = [0, 100, 100, 0, 0]
        self.cornerY = [0, 0, 100, 100, 0]
        self.numRooms = random.randint(minRooms, maxRooms) 
        self.hallways = []

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
                self.AddRoom(Room(x,y))
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


        roomUp.stairsXY = (upX,upY)
        roomDown.stairsXY = (downX, downY)

        return (roomNumUp, roomNumDown)

    def Draw(self):
        figure = plt.figure(figsize=(6,6))
        plt.plot(self.cornerX, self.cornerY, color='black')
        hallNumber = 0
        for room in self.rooms:
            if (room.stairs == "Up"):
                stairUp = room.stairsXY
                plt.scatter(stairUp[0], stairUp[1], color='red', s=20)
            if (room.stairs == "Down"):
                stairDown = room.stairsXY
                plt.scatter(stairDown[0], stairDown[1], color='black', s=20)

            x_coords = room.botLeft[0], room.topLeft[0], room.topRight[0], room.botRight[0], room.botLeft[0]
            y_coords = room.botLeft[1], room.topLeft[1], room.topRight[1], room.botRight[1], room.botLeft[1]
            

            plt.plot(x_coords, y_coords, color='blue')
       
        # Draw hallways
        if hasattr(self, 'hallways'):  # Check if the 'hallways' attribute exists
            for hall in self.hallways:
                startX, startY, endX, endY = hall.startX, hall.startY, hall.endX, hall.endY 
                #plt.plot([startX, endX], [startY, endY], color='green')  # Draw the hallway line
                
                # Draw the hallNumber near the start and end points
                plt.text(startX, startY, str(hallNumber), color='green', fontsize=12)
                plt.text(endX, endY, str(hallNumber), color='green', fontsize=12)
                hallNumber += 1  # Increment the hall number for the next hallway

        xlim = plt.xlim(-10, 110)            # Set x-axis limits
        ylim = plt.ylim(-10, 110)            # Set y-axis limits
        plt.show

    def RemoveRoom(self, room):
        self.rooms.remove(room)

    def AddHallways(self):
        #closestRoom = self

        for room in self.rooms:
            #Get closet room with no hall between
            closestRoom = room.FindClosest()
            if room is closestRoom or closestRoom in room.overlap:
                continue
            #pick proper wall
            #Call AddDoor on each wall
            room.AddDoorBetween(closestRoom)
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
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = random.randint(minRoomVariance, maxRoomVariance)
        self.height = random.randint(minRoomVariance, maxRoomVariance)
        self.floor = None
        self.overlap = []
        self.stairs = None
        self.stairsXY = None
        self.connectedRooms = []
        self.numHalls = 0
        self.doors = []

        self.botLeft  = (self.x, self.y)
        self.topLeft  = (self.x, self.y + self.height)
        self.botRight = (self.x + self.width, self.y)
        self.topRight = (self.x + self.width, self.y + self.height)
        
        
    """
    Finds the closest room that is not already connected by a hallway

    returns:
        closestRoom - the room object with start points closest to that of the current room
    Limitations:
        Does not actually return the closest based on total size of the rooms, only returns the closest starting point
    """
    def FindClosest(self):
        closestRoom = self
        closestDist = float('inf')
        currDist = 0
        for currroom in self.floor.rooms:
            #Ignore if same Room, already connected or overlapping
            if currroom == self or currroom in self.connectedRooms or currroom in self.overlap:
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
        #Add door to each side of each room. 
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
        
#This is to find midpoint if I want that 
        if(selfDoor[0] == self.botLeft[0]):
            selfWall = 'left'
        if (selfDoor[0] == self.botRight[0]):
            selfWall = 'right'
        if (selfDoor[1] == self.topLeft[1]):
            selfWall = 'top'
        if (selfDoor[1] == self.botLeft[1]):
            selfWall = 'bottom'

        if(otherDoor[0] == otherRoom.botLeft[0]):
            endWall = 'left'
        if (otherDoor[0] == otherRoom.botRight[0]):
            endWall = 'right'
        if (otherDoor[1] == otherRoom.topLeft[1]):
            endWall = 'top'
        if (otherDoor[1] == otherRoom.botLeft[1]):
            endWall = 'bottom'



        
        
        #midpoint = [midX, midY]
        
        print(f"Created a new hallway from {selfDoor} to {otherDoor}")
        #print(f"Midpoint is: {midpoint}")
        self.connectedRooms.append(otherRoom)
        otherRoom.connectedRooms.append(self)
        #Create new Hallway obj start, mid, end
        newHall = Hallway(selfDoor[0], selfDoor[1], otherDoor[0], otherDoor[1])
        self.floor.hallways.append(newHall)
        #newHall.joints.append(midpoint)
        #Decide what to return
        return True    


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
    
    def RemoveWalls(self, otherRoom, interiorRectangle):
        
        return -1
    
    #TODO    
    def Delete(self):
        if (self.floor):
            self.floor.RemoveRoom(self)
        return 1    


class Hallway:
    def __init__(self, startX, startY, endX, endY):
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY
        self.joints = []

        self.floor = None


#Manhattan Distance - count diagonals as 2 
def ManDistance(x1,y1,x2,y2):
    return abs(x2 - x1) + abs(y2 - y1)

def Random(x, y):
    if(x > y):
        return(random.randint(y,x))
    else:
        return(random.randint(x,y))

#Returns direction or None if directionPointToAdd is higher priority
        #Also returns None if the pointToAdd is in the same direction and closer to the currPoint
def FindDirection(currPoint, nextPoint, directionPointToAdd, pointToAdd):
    direction = None
    sameY = currPoint[1] == nextPoint[1]
    sameX = currPoint[0] == nextPoint[0]

    if ((nextPoint[0] - currPoint[0] > 0) and sameY):
        direction = 'right'
    elif((nextPoint[0] - currPoint[0] < 0) and sameY):
        direction = 'left'
    elif((nextPoint[1] - currPoint[1] > 0) and sameX):
        direction = 'up'
    elif((nextPoint[1] - currPoint[1] < 0) and sameX):
        direction = 'down'
    else:
        direction = None
        return None

    if (pointToAdd is not None and directionPointToAdd is not None):
    # Check if the direction is the same but the next_point is further than point_to_add
        if direction == directionPointToAdd:
            if direction in ['right', 'left']:
                if abs(pointToAdd[0] - currPoint[0]) < abs(nextPoint[0] - currPoint[0]):
                    return None
            elif direction in ['up', 'down']:
                if (pointToAdd[1] - currPoint[1]) < abs(nextPoint[1] - currPoint[1]):
                    return None
    return direction

def main():

    floor = Floor()
        #print(f"This floor should have: {floor.numRooms} rooms")
    #floor.MakeRooms() #Creates randomly generated rooms
    #floor.AddStairs()
    #floor.AddHallways()
    #floor.Draw()
    #print("Done")

#Testin purposes:
    #region
    room1 = Room(20, 20)
    room2 = Room(50, 50)
    room3 = Room(10, 50)
    
    floor.AddRoom(room1, room2, room3)
    floor.AddHallways()
    floor.Draw()
    return 1

if __name__ == '__main__':
    main()