# Draw the nine rooms on the screen
import Global
import Common
import Monsters
import Things
from Rogue import Rect, Coordinate, Flags

class Room(object):
    def __init__(self) -> None:
        self.rect:Rect = None
        self.goldPosition:Coordinate = None
        self.goldValue:int = 0
        self.flags:Flags = Flags([ "isGone", "isDark" ])
        self.exitPosition:list = []

    def clearThings(self) -> None:
        self.rect = None
        self.goldValue = 0
        self.flags.clearAll()
        self.exitPosition.clear()

    # rndPosition
    # pick a random spot in a room
    def rndPosition(self) -> Coordinate:
        position = Coordinate()
        while True:
            position.x = int(self.rect.left + Global.rnd(self.rect.width - 2) + 1)
            position.y = int(self.rect.top + Global.rnd(self.rect.height - 2) + 1)
            break

            # TODO:
            # ch = Global.stdscr.inch(position.y, position.x)
            # if ch == Global.Floor:
            #     break

        return position

    # draw:
    # Draw a box around a room
    def draw(self) -> None:
        self.__vert()
        self.__horiz()

        # Put the floor down
        self.__drawFloor()

        # Put the gold there
        if (self.goldValue > 0):
            Global.stdscr.addch(int(self.goldPosition.y), int(self.goldPosition.x), Global.Gold)

    # __drawFloor:
    # Put the floor down
    def __drawFloor(self) -> None:
        for y in range(1, self.rect.height - 1):
            for x in range(self.rect.width - 1):
                Global.stdscr.addch(int(self.rect.top + y), int(self.rect.left + x), Global.Floor)

    # __horiz:
    # draw a horizontal line
    def __horiz(self) -> None:
        top = int(self.rect.top)
        bottom = int(self.rect.top + self.rect.height - 1)
        length = self.rect.width + 2 - 1
        Global.stdscr.hline(top, self.rect.left - 1, "-", length)
        Global.stdscr.hline(bottom, self.rect.left - 1, "-", length)

    # __vert:
    # draw a vertical line
    def __vert(self) -> None:
        left = int(self.rect.left - 1)
        right = int(self.rect.left + self.rect.width - 1)
        length = self.rect.height - 1
        Global.stdscr.vline(self.rect.top, left, "|", length)
        Global.stdscr.vline(self.rect.top, right, "|", length)

    def inRoom(self, coord:Coordinate) -> bool:
        return self.rect.left - 1 <= coord.x <= (self.rect.left + self.rect.width)\
            and self.rect.top <= coord.y <= (self.rect.top + self.rect.height)

# rndRoom:
# Pick a room that is really there
def rndRoom() -> Room:
    roomNo:int = Global.rnd(Global.MaxRooms)
    while True:
        if not Global.rooms[roomNo].flags.isGone:
            break
        roomNo = Global.rnd(Global.MaxRooms)
    return Global.rooms[roomNo]

# doRooms:
def doRooms(screenColumns, screenLines) -> None:
    # Clear things for a new level
    for room in Global.rooms:
        room.clearThings()

    # Put the gone rooms, if any, on the level
    for i in range(Global.rnd(4)):
        rndRoom().flags.isGone = True

    # dig and populate all the rooms on the level
    bsze = Coordinate(screenColumns // 3, (screenLines - 1) // 3)
    for i, room in enumerate(Global.rooms):
        # Find upper left corner of box that this room goes in
        top = Coordinate((i % 3) * (bsze.x + 1) + 1, i // 3 * bsze.y + 1)

        if room.flags.isGone:
            # Place a gone room. Make certain that there is a blank line for passage drawing.
            x = top.x + Global.rnd(bsze.x - 2)
            y = top.y + Global.rnd(bsze.y - 2)
            width = -1
            height = -1
            room.rect = Rect(x, y, width, height)
            Global.stdscr.addch(y, x, "#")
            continue

        # Create dark room
        if Global.rnd(10) < Global.level - 1:
            room.flags.isDark = True

        # Find a place and size for a random room
        width = Global.rnd(bsze.x - 4) + 4
        height = Global.rnd(bsze.y - 4) + 4
        x = top.x + Global.rnd(bsze.x - width)
        y = top.y + Global.rnd(bsze.y - height)
        room.rect = Rect(x, y, width, height)

        # Put the gold in
        if (Global.rnd(100) < 50 and not Global.hasAmulet) or Global.level >= Global.maxLevel:
            room.goldValue = Common.CalcGoldValue(Global.level)
            room.goldPosition = room.rndPosition()

        room.draw()

        # Put the monster in
        if Global.rnd(100) < 80 if room.goldValue > 0 else 25:
            monster = Monsters.newMonster(Monsters.randMonster(False), room.rndPosition())
            # See if we want to give it a treasure to carry around.
            if Global.rnd(100) < Global.monsterParameters[ord(monster.type) - ord("A")].carry:
                monster.pack = Things.newThing()

# roomIn:
# Find what room some coordinates are in.
# NULL means they aren't in any room.
def roomIn(coord:Coordinate) -> Room:
    for room in Global.rooms:
        if room.inRoom(coord):
            return room
    else:
        return None
