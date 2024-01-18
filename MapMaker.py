import matplotlib.pyplot as plt
import random

"""
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
minRoomVariance = 3
maxRoomVariance = 6
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
    
    def AddIntersects(self, overlappingRooms):
        intersections = []
        
        for i, currRoom in enumerate(overlappingRooms):
            #Look a tthe list of rooms that overlap. For each pair add the corners of 1 into the other
            if i+1 < len(overlappingRooms):
                nextRoom = overlappingRooms[i + 1]
                #Put code that actually does shit here 

                #Copies 2nd room corners list to first room and all new intersections
                currRoom.corners.append(intersections)
                currRoom.corners.append(nextRoom.corners) 


        return -1

    def isOverlaped(self):
        """ Checks all room objects to see which overlap eachother

        Returns:
            A list of rooms that overlap as X,Y pairs representing each room's midpoint
        """
        overlappingRooms = []
        # Function to check if two rooms overlap
        def rooms_overlap(room1, room2):
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

            # Check for no overlap conditions
            if room1_right < room2_left or room1_left > room2_right or room1_down > room2_up or room1_up < room2_down:
                return False
            return True
        
        # Iterate through each pair of rooms
        for i, room1 in enumerate(self.rectangles):
            for room2 in self.rectangles[i+1:]:

                # Check for overlap
                if rooms_overlap(room1, room2):
                    #TODO Check if this combinations of rooms have already been added to overlapping rooms
                    # Add tuple of overlapping rooms to the list
                    overlappingRooms.append((room1, room2))
        return overlappingRooms
    
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
    """Room class allows for randomly generated rooms and combined rooms to be easily drawn
    Args:
        middle: list of 2 ints treated as X,Y coordinates
    """
    def __init__(self, middle):
        self.middle = middle
        self.corners = [] #List of Tuples representing X,y coordinates always starts topLeft then goes clockwise
        self.orderedCorners = []
        #region
        x = self.middle[0]
        y = self.middle[1]
        left = -1 * random.randint(minRoomVariance, maxRoomVariance)
        right = random.randint(minRoomVariance, maxRoomVariance)
        up = random.randint(minRoomVariance, maxRoomVariance)
        down = -1 * random.randint(minRoomVariance, maxRoomVariance)
        #endregion

        self.corners.append([x + left, y + up]) #TopLeft
        self.corners.append([x + right, y + up]) #TopRight        
        self.corners.append([x + right, y + down]) #botRight
        self.corners.append([x + left, y + down]) #BotLeft
        print(f"List of corners for midpoint {self.middle} is: {self.corners}")
        
    def SortCorners(self):
        """This method sorts all corners starting at the first in the corner list. Each pair is the closest to the previous pair       
        Args:
            none
        Returns:
            bool: True when no errors occur
        """
        excludedPoints = []
        tempList = []
        currPoint = self.corners[0]
        tempList.append(currPoint)
        excludedPoints.append(currPoint)
        
        while len(tempList) < len(self.corners):
            nextDistance = float('inf')
            nextPoint = None

            for corner in self.corners:
                if corner in excludedPoints:
                    continue #Reserved skip to next corner

                distance = (corner[0] - currPoint[0])**2 + (corner[1] - currPoint[1])**2 #The internet told me to do this
                if (distance < nextDistance):
                    nextDistance = distance
                    nextPoint = corner

            if nextPoint:
                excludedPoints.append(nextPoint)
                tempList.append(nextPoint)
                currPoint = nextPoint
        self.corners = tempList.copy()
        print(f"After sorting the list is: {self.corners}")
        return 1
    

def main():

    i = 0

    floor = Floor()
    #floor.MakeRooms() #Creates randomly generated rooms
    
#Testin purposes:
    #region
    room1 = Room([15,15])
    room2 = Room([17, 10])
    room3 = Room([37, 18])
    room4 = Room([13,18])
    
    floor.AddRoom(room1, room2, room3, room4)
    floor.rectangles = floor.rooms.copy()

    floor.CombineRooms()
    overlaps = floor.isOverlaped()
    for rooms in overlaps:
        print(f"These rooms overlap: {rooms[0].middle}, {rooms[1].middle}")
    room1.SortCorners()
    #endregion
    floor.Draw()

    return 1

if __name__ == '__main__':
    main()