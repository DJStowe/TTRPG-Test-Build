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
        self.rectangles = []
        self.cornerX = [0, 100, 100, 0, 0]
        self.cornerY = [0, 0, 100, 100, 0]
        self.numRooms = random.randint(minRooms, maxRooms) #TODO Temp numbers for how many rooms there are
        self.arrX = []
        self.arrY = []

    def AddRoom(self, *rooms):
        """Adds any amount of rooms 
        
        Args:
            *rooms: a single or list of rooms
        """
        for room in rooms:
            self.rooms.append(room)

    def MakeRooms(self):
        """Makes X rooms in random locations where X is a random number between minRooms & maxRooms
        """
        while len(self.arrX) < self.numRooms:
            x = random.randint(1, 100)
            y = random.randint(1, 100)

            # Check if the coordinate is already used
            if (x, y) not in zip(self.arrX, self.arrY):
                self.arrX.append(x)
                self.arrY.append(y)

        #Create a room obj for each coordinate
        for i in range(len(self.arrX)):
            self.AddRoom(Room([self.arrX[i], self.arrY[i]]))
        self.rectangles = self.rooms.copy()
        return 1
    
    #TODO This needs to add all corners of intersection then remove any corners inside of the combined boxes or any other unneeded corners

    def CombineRooms(self):
       
                   
       return -1
      

    def isOverlaped(self):
        """ Checks all room objects to see which overlap eachother

        Returns:
            A list of rooms that overlap as X,Y pairs representing each room's midpoint
        """
        overlappingCorners = []
        # Function to check if two rooms overlap
        #Returns list of corners from intersection
        def RoomsOverlap(room1, room2):
            # Calculate edges for room1
            room1_left = min([corner[0] for corner in room1.corners])
            room1_right = max([corner[0] for corner in room1.corners])
            room1_up = max([corner[1] for corner in room1.corners])
            room1_down = min([corner[1] for corner in room1.corners])

            # Calculate edges for room2
            room2_left = min([corner[0] for corner in room2.corners])
            room2_right = max([corner[0] for corner in room2.corners])
            room2_up = max([corner[1] for corner in room2.corners])
            room2_down = min([corner[1] for corner in room2.corners])

        # Check for overlap and calculate intersection points
            if room1_right >= room2_left and room1_left <= room2_right and room1_down <= room2_up and room1_up >= room2_down:
                # Calculate the edges of the overlapping region
                overlap_left = max(room1_left, room2_left)
                overlap_right = min(room1_right, room2_right)
                overlap_up = min(room1_up, room2_up)
                overlap_down = max(room1_down, room2_down)

                # Define the corners of the overlapping region
                overlappingCorners = [
                    (overlap_left, overlap_down),
                    (overlap_left, overlap_up),
                    (overlap_right, overlap_up),
                    (overlap_right, overlap_down)
                ]
                room1.corners.extend(overlappingCorners)
                #print(f"Here is room1 corners list: {room1.corners}")
                return True
            else:
                # Return an empty list if there is no overlap
                return False
        
        # Iterate through each pair of rooms
        for i, room1 in enumerate(self.rectangles):
            for room2 in self.rectangles[i+1:]:
                overlappingCorners.append(RoomsOverlap(room1, room2))
                
        return overlappingCorners
    
    def Draw(self):
        figure = plt.figure(figsize=(6,6))
        plt.plot(self.cornerX, self.cornerY, color='black')
        #This shit is about to get ugly
        for room in self.rooms:
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
        print(f"self Corners are: {self.corners}")
        print(f"other Room Corners are: {otherRoom.corners}")
        print(f"Interior Rectangle is: {interiorRectangle}")
        
        temp = []
        if interiorRectangle is not None:
            self.corners.extend(otherRoom.corners) #Add room2 corners to room1 corners list
            for intCorners in interiorRectangle: #Loops through interior Rect and removes anything that's in both lists from room1 corners
                if(intCorners in self.corners):
                    self.corners.remove(intCorners)
                else: #If not in both lists then add to self.corners
                    self.corners.append(intCorners)
            print(f"Before Sorting Corners List: {self.corners}")
            self.SortCorners()
        return -1
    
    def SortCorners(self):
        """This method sorts all corners starting at the first in the corner list. Each pair is the closest to the previous pair       
        Args:
            none
        Returns:
            bool: True when no errors occur
        """
        excludedPoints = []
        tempList = []
        currX = self.x
        currY = self.y
        tempList.append((currX, currY))
        excludedPoints.append((currX, currY))
        
        while len(tempList) < len(self.corners):
            nextDistance = float('inf')
            nextPoint = None

            for corner in self.corners:
                if corner in excludedPoints:
                    continue #Reserved skip to next corner

                distance = (corner[0] - currX)**2 + (corner[1] - currY)**2 #ΔX^2 + ΔY^2 
                if (distance < nextDistance):
                    nextDistance = distance
                    nextPoint = corner

            if nextPoint:
                excludedPoints.append(nextPoint)
                tempList.append(nextPoint)
                currX = nextPoint[0]
                currY = nextPoint[1]

        self.corners = tempList.copy()
        print(f"After sorting the list is: {self.corners}")
        return 1
    
    def RemoveWalls(self, otherRoom, interiorRectangle):
        
        return -1
    
    #TODO    
    def Delete(self):

        return -1    



def main():

    i = 0

    floor = Floor()
    #floor.MakeRooms() #Creates randomly generated rooms
    
#Testin purposes:
    #region
    room1 = Room(0,20)
    room2 = Room(58, 43)
    room3 = Room(2, 15)
    room4 = Room(53,28)
    
    floor.AddRoom(room1, room2, room3, room4)
    # Iterate through each pair of rooms
    for i, room1 in enumerate(floor.rooms):
        for room2 in floor.rooms[i+1:]:
            room1.Combine(room2)

  
    #floor.rectangles = floor.rooms.copy()

    #floor.CombineRooms()
    #floor.isOverlaped()
    #for rooms in overlaps:
        #print(f"These rooms overlap: {rooms[0].middle}, {rooms[1].middle}")
    #room1.SortCorners()
    #endregion
    floor.Draw()

    return 1

if __name__ == '__main__':
    main()