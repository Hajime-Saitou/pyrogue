# Draw the connecting passages
import Global
import copy
import random
import Rogue

class RoomGraphDescription(object):
    def __init__(self, possibleToConnect:list):
        self.possibleToConnect:list = possibleToConnect                 # possible to connect to room i?
        self.isConnectionBeenMade:list = [ False ] * Global.MaxRooms    # connection been made to room i?
        self.inGraphAlready:bool = False                                # this room in graph already?
        self.inputValency:int = 0                                       # graph valency(input)
        self.outputValency:int = 0                                      # graph valency(output)

    # initialize room graph description
    def initialize(self) -> None:
        for index in range(len(self.isConnectionBeenMade)):
            self.isConnectionBeenMade[index] = False

        self.inGraphAlready = False
        self.inputValency = 0
        self.outputValency = 0

# doPassages:
# Draw all the passages on a level.
def doPassage() -> None:
    # reinitialize room graph description
    for index in range(Global.MaxRooms):
        Global.roomGraphDesc[index].initialize()
    
    # starting with one room, connect it to a random adjacent room and
    # then pick a new room to start with.
    roomCount:int = 0

    while True:
        roomList = list(range(Global.MaxRooms - 2))
        random.shuffle(roomList)
        for roomNoFrom in roomList:
            if Global.rnd(100) < 50:
                continue
            roomGraphDescFrom = Global.roomGraphDesc[roomNoFrom]

            if roomNoFrom % 3 == 2:
                roomNoTo = 3
                roomIsEdge = True
            elif roomNoFrom // 3 == 2:
                roomNoTo = 1
                roomIsEdge = True
            else:
                roomNoTo = 3 if Global.rnd(100) < 50 else 1
                roomIsEdge = False

            if roomGraphDescFrom.isConnectionBeenMade[roomNoFrom + roomNoTo]:
                # can not create other passage.
                if roomIsEdge:
                    continue
                else:
                    roomNoTo = 3 if roomNoTo == 1 else 1
                    # already created.
                    if roomGraphDescFrom.isConnectionBeenMade[roomNoFrom + roomNoTo]:
                        continue

            roomNoTo += roomNoFrom
            roomGraphDescTo = Global.roomGraphDesc[roomNoTo]

            connectRoom(roomNoFrom, roomNoTo)
            Global.logger.debug(f"roomCount: {roomCount}")

            roomGraphDescFrom.inGraphAlready = True
            roomGraphDescFrom.isConnectionBeenMade[roomNoTo] = True
            roomGraphDescFrom.outputValency += 1

            roomGraphDescTo.inGraphAlready = True
            roomGraphDescTo.isConnectionBeenMade[roomNoFrom] = True
            roomGraphDescTo.inputValency += 1
            roomCount += 1

            if allPathsIsConnected(roomCount):
                break

        if allPathsIsConnected(roomCount):
            break

# doVisit:
def doVisit(roomNo, visitRooms):
    if visitRooms[roomNo]:
        return

    visitRooms[roomNo] = True
    Global.logger.debug(f"visited: {roomNo}")

    roomX = roomNo % 3
    roomY = roomNo // 3
    if roomX > 1 and Global.roomGraphDesc[roomNo].isConnectionBeenMade[roomNo - 1]:
        Global.logger.debug(f"visit from {roomNo} to {roomNo - 1}")
        doVisit(roomNo - 1, visitRooms)
    if roomX < 2 and Global.roomGraphDesc[roomNo].isConnectionBeenMade[roomNo + 1]:
        Global.logger.debug(f"visit from {roomNo} to {roomNo + 1}")
        doVisit(roomNo + 1, visitRooms)

    if roomY > 1 and Global.roomGraphDesc[roomNo].isConnectionBeenMade[roomNo - 3]:
        Global.logger.debug(f"visit from {roomNo} to {roomNo - 3}")
        doVisit(roomNo - 3, visitRooms)
    if roomY < 2 and Global.roomGraphDesc[roomNo].isConnectionBeenMade[roomNo + 3]:
        Global.logger.debug(f"visit from {roomNo} to {roomNo + 3}")
        doVisit(roomNo + 3, visitRooms)
    
    return

# allPathsIsConnected:
# can we walking through all rooms
def allPathsIsConnected(roomCount:int) -> bool:
    visitRooms = [ False ] * Global.MaxRooms
    doVisit(0, visitRooms)

    return len([ trueCount for trueCount in visitRooms if trueCount == True ]) == Global.MaxRooms

# connectRoom:
# Draw a corridor from a room in a certain direction.
def connectRoom(roomNoFrom, roomNoTo):
    Global.logger.debug(f"start: {roomNoFrom}")
    Global.logger.debug(f"end: {roomNoTo}")

    # swap room number by number order
    passageDirection = ""
    if roomNoTo < roomNoFrom:
        roomNoFrom, roomNoTo = roomNoTo, roomNoFrom

    if roomNoFrom + 1 == roomNoTo:
        passageDirection = "r"
    else:
        passageDirection = "d"

    roomFrom = Global.rooms[roomNoFrom]
    Global.logger.debug(f"Direction: {passageDirection}")

    # Set up the movement variables, in two cases:
    # first drawing one down.
    startPosition = None
    endPosition = None
    delta = None
    turnDelta = None
    roomNoTo = 0
    roomTo = None
    distance = 0
    if passageDirection == "d":
        roomNoTo = roomNoFrom + 3               # room # of dest
        roomTo = Global.rooms[roomNoTo]         # room pointer of dest

        delta = Rogue.Coordinate(0, 1)          # direction of move
        startPosition = Rogue.Coordinate(roomFrom.rect.left, roomFrom.rect.top) # start of move
        endPosition = Rogue.Coordinate(roomTo.rect.left, roomTo.rect.top)       # end of move

        if not roomFrom.flags.isGone:           # if not gone pick door pos
            startPosition.x += Global.rnd(roomFrom.rect.width - 2) + 1
            startPosition.y += roomFrom.rect.height - 1

        if not roomTo.flags.isGone:             # if not gone pick door pos
            endPosition.x += Global.rnd(roomTo.rect.width - 2) + 1

        distance = abs(startPosition.y - endPosition.y) - 1     # distance to move

        turnDelta = Rogue.Coordinate(1 if startPosition.x < endPosition.x else -1, 0)       # direction to turn
        turnDistance = abs(startPosition.x - endPosition.x)                 # how far to turn
        turnSpot = (Global.rnd(distance - 1) + 1) if distance >= 2 else 1     # where turn starts
    elif passageDirection == "r":                    # setup for moving right
        roomNoTo = roomNoFrom + 1
        roomTo = Global.rooms[roomNoTo]

        delta = Rogue.Coordinate(1, 0)
        startPosition = Rogue.Coordinate(roomFrom.rect.left, roomFrom.rect.top) # start of move
        endPosition = Rogue.Coordinate(roomTo.rect.left - 1, roomTo.rect.top)   # end of move

        if not roomFrom.flags.isGone:           # if not gone pick door pos
            startPosition.x += roomFrom.rect.width - 1
            startPosition.y += Global.rnd(roomFrom.rect.height - 2) + 1

        if not roomTo.flags.isGone:             # if not gone pick door pos
            endPosition.y += Global.rnd(roomTo.rect.height - 2) + 1

        distance = abs(startPosition.x - endPosition.x) - 1     # distane to move

        turnDelta = Rogue.Coordinate(0, 1 if startPosition.y < endPosition.y else -1)       # direction to turn
        turnDistance = abs(startPosition.y - endPosition.y)     # how far to turn
        turnSpot = (Global.rnd(distance - 1) + 1) if distance >= 2 else 1     # where turn starts

    # Draw in the doors on either side of the passage or just put #'s if the rooms are gone.
    if not roomFrom.flags.isGone:
        door(roomFrom, startPosition)
    else:
        Global.stdscr.addch(startPosition.y, startPosition.x, Global.Passage)

    if not roomTo.flags.isGone:
        door(roomTo, endPosition)
    else:
        Global.stdscr.addch(endPosition.y, endPosition.x, Global.Passage)

    # Get ready to move...
    currentPosition = copy.deepcopy(startPosition)
    Global.logger.debug(f"start: {roomNoFrom}, {str(startPosition)}")
    Global.logger.debug(f"end: {roomNoTo}, {str(endPosition)}")
    Global.logger.debug("distance: " + str(distance))
    while True:
        if distance == 0:
            break

        # Move to new position
        currentPosition += delta
        Global.logger.debug("add delta: " + str(currentPosition))

        # Check if we are at the turn place, if so do the turn
        if distance == turnSpot and turnDistance > 0:
            while True:
                if turnDistance == 0:
                    break

                Global.stdscr.addch(currentPosition.y, currentPosition.x, Global.Passage)
                currentPosition += turnDelta
                Global.logger.debug("add turn delta: " + str(currentPosition))
                turnDistance -= 1

        # Continue digging along
        Global.stdscr.addch(currentPosition.y, currentPosition.x, Global.Passage)
        distance -= 1

# door:
# Add a door or possibly a secret door
# also enters the door in the exits array of the room.
def door(room, coordinate):
    Global.stdscr.addch(coordinate.y, coordinate.x, Global.SecretDoor if Global.rnd(10) < Global.level - 1 and Global.rnd(100) < 20 else Global.Door)
    room.exitPosition.append(copy.deepcopy(coordinate))
    return