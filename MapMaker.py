import matplotlib.pyplot as plt
import random

"""
This program generates random maps for TTRPG based on the Nintendo property Pokemon Mystery Dungeon
TODO List
Write CombineRooms Function
    This should also make new rooms if there aren't enough
Add start and end stairs. TODO Grab the sprites for those before I delete them
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
            
        for i, room1 in enumerate(self.rooms):
            for room2 in self.rooms[i+1:]:
                room1.Combine(room2)   
        return True
    
    def Draw(self):
        figure = plt.figure(figsize=(6,6))
        plt.plot(self.cornerX, self.cornerY, color='black')

        for room in self.rooms:
            if (len(room.corners) > 0): 
                #seperate lists for x and y coordinates
                x_coords = [corner[0] for corner in room.corners]
                y_coords = [corner[1] for corner in room.corners]

                # Add the first corner to close shape
                x_coords.append(room.corners[0][0])
                y_coords.append(room.corners[0][1])
                
                plt.plot(x_coords, y_coords, color='blue')

        xlim = plt.xlim(-10, 110)            # Set x-axis limits
        ylim = plt.ylim(-10, 110)            # Set y-axis limits
        plt.show

    def RemoveRoom(self, room):
        self.rooms.remove(room)


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
        self.corners = []
        self.floor = None

        self.corners.append((self.x, self.y))
        self.corners.append((self.x + self.width, self.y))
        self.corners.append((self.x + self.width,self.y - self.height)) 
        self.corners.append((self.x , self.y - self.height))
        
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
            #print(f"Intersect returns None")
            return None

        interiorRectangle.append((x_left, y_top))
        interiorRectangle.append((x_right, y_top))
        interiorRectangle.append((x_right, y_bottom))
        interiorRectangle.append((x_left, y_bottom))
        # Returns overlapping rectangle corners
        return interiorRectangle
    
    """
    Logic looks funny here but basically 
    if intersect combine lists check if in interior rectangle and if it is remove it from the lists
    This removes the inside corners while adding the corners on the edges
    """
    def Combine(self, otherRoom):
        interiorRectangle = self.Intersect(otherRoom)
        
        cornersToAdd = []
        #print(f"Interior Rect is: {interiorRectangle}")
        if interiorRectangle is not None:
            self.corners.extend(otherRoom.corners) #Add room2 corners to room1 corners list
            for intCorners in interiorRectangle: #Loops through interior rect and removes duplicates
                if(intCorners in self.corners):
                    self.corners.remove(intCorners)
                    
                else: #If not duplicate add
                    cornersToAdd.append(intCorners)
            
            for intCorner in cornersToAdd:
                for i, corner in enumerate(self.corners):
                    if i + 1 < len(self.corners):
                        nextCorner = self.corners[i+1]
                        if((intCorner[0] == corner[0]) and (intCorner[1] == nextCorner[1])):
                            #Insert into this location then break?
                            print(f"Adding corner {intCorner} from list: {cornersToAdd} to index {i + 1} in list {self.corners}")
                            self.corners.insert(i+1, intCorner)
                            print(f"New list is: {self.corners}")
                            #cornersToAdd.remove(intCorner)
                            break
                        
                #If not in place adds at end
                if (intCorner not in self.corners):
                    self.corners.append(intCorner)

            #print(f"List of corners is: {self.corners} otherRoom was: {otherRoom.corners}")
            #print(f"List of intersects is: {cornersToAdd}")

            otherRoom.Delete()
            self.SortCorners()
            return True
        return False
    
    def SortCorners(self):
        """This method sorts all corners starting at the first in the corner list. Each pair is the closest to the previous pair
        sort-corners-fix update: Adds a check to make sure next point is in line with current point (X or Y is same)       
        Args:
            none
        Returns:
            bool: True when no errors occur
        """
        tempCorners = self.corners.copy()
        inOrderList = []
        pointsAdded = 0
        minX = min(corner[0] for corner in self.corners)
        maxY = max(corner[1] for corner in self.corners)
        topLeft = (minX, maxY)
        #TODO Idk if this fixes anything
        if topLeft not in tempCorners:
            topLeft = tempCorners[0]

        currPoint = topLeft
        pointToAdd = topLeft
        inOrderList.append(pointToAdd)
        pointsAdded += 1
        try:
            tempCorners.remove(pointToAdd)
        except:
            #print(f"Unexpected error: {pointToAdd} is not in the list {self.corners}")
            #print(f"tempCorners is: {tempCorners} and inOrderList is: {inOrderList}")
            SystemExit
        #pointToAdd = None
        directionPointToAdd = 'up'
        direction = None

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

        while pointsAdded < len(self.corners):
            for corner in tempCorners:
                direction = FindDirection(currPoint, corner, directionPointToAdd, pointToAdd)
                match direction:
                    case None:
                        pointToAdd = pointToAdd
                    case 'right':
                        pointToAdd = corner
                        directionPointToAdd = 'right'
                    case 'down':
                        if (directionPointToAdd not in {'right'}):
                            pointToAdd = corner
                            directionPointToAdd = 'down'
                    case 'left':
                        if (directionPointToAdd not in {'right', 'down'}):
                            pointToAdd = corner
                            directionPointToAdd = 'left'

                    case 'up':
                        if (directionPointToAdd not in {'right', 'down', 'left'}):
                            pointToAdd = corner
                            directionPointToAdd = 'up'    

            #TODO Fix bug that writes the same number over and over here
            inOrderList.append(pointToAdd)
            pointsAdded += 1
            
            try:
                tempCorners.remove(pointToAdd)
            except:
                print(f"Unexpected error: {pointToAdd} is not in the list {self.corners}")
                print(f"tempCorners is: {tempCorners}")
                #SystemExit
            currPoint = pointToAdd
            directionPointToAdd = 'temp'
            #pointToAdd = None
        self.corners = inOrderList.copy()
        print(f"Ordered list: {self.corners}")

        return 1
    
    def RemoveWalls(self, otherRoom, interiorRectangle):
        
        return -1
    
    #TODO    
    def Delete(self):
        if (self.floor and self.corners is not None):
            self.floor.RemoveRoom(self)
        self.corners = None
        return 1    



def main():

    i = 0
    while i < 10:
        floor = Floor()
            #print(f"This floor should have: {floor.numRooms} rooms")
        floor.MakeRooms() #Creates randomly generated rooms
        floor.Draw()
    
        #print(f"Floor has: {len(floor.rooms)} Rooms")
        #input(f"Press Enter...")
        i+= 1
    
#Testin purposes:
    #region
    #room1 = Room(0,20)
    #room2 = Room(58, 43)
    #room3 = Room(2, 15)
    #room4 = Room(53,28)
    
    #floor.AddRoom(room1, room2, room3)
    # Iterate through each pair of rooms
    #for i, room1 in enumerate(floor.rooms):
        #for room2 in floor.rooms[i+1:]:
            #room1.Combine(room2)

  
    #floor.rectangles = floor.rooms.copy()

    #floor.CombineRooms()
    #for rooms in overlaps:
        #print(f"These rooms overlap: {rooms[0].middle}, {rooms[1].middle}")
    #room1.SortCorners()
    #endregion
    #floor.Draw()

    return 1

if __name__ == '__main__':
    main()