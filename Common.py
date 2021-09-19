from Rogue import CarryObject
import Global
from enum import IntEnum
from Rogue import Coordinate, Flags

version = "0.1py"

# Rolls:
# roll manager for several attacks
class Rolls(object):
    def __init__(self, damageString:str) -> None:
        self.rolls:list = []
        self.parse(damageString)

    def parse(self, damageString:str) -> None:
        self.rolls.clear()

        for damage in damageString.split("/"):
            dice, sides = damage.split("d")
            self.rolls.append(( int(dice), int(sides) ))

# Structure for strength paramter
class Strength(object):
    def __init__(self, strength, addStrength):
        self.strength = strength
        self.addStrength = addStrength

# Structure describing a fighting being
class Stats(object):
    def __init__(self, strength:int, addStrength:int, experience:int, level:int, armorClass:int, hitPoints:int, damage:str):
        self.strength:Strength = Strength(strength, addStrength)
        self.experience:int = experience
        self.level:int = level
        self.armorClass:int = armorClass
        self.hitPoints:int = hitPoints
        self.damage:str = damage

# Structure for monsters and player
class Thing(object):
    def __init__(self):
        self.position:Coordinate = Coordinate()
        self.turn:bool = False                      # If slowed, is it a turn to move
        self.type:str = ""                          # What it is
        self.disguise:str = ""			            # What mimic looks like
        self.oldCh:str = ""                         # Character that was where it was
        self.destination:Coordinate = Coordinate()  # Where it is running to
        self.flags = Flags([                        # State word
            "isRun",
            "isHeld",
            "isHaste",
            "isHuh",
            "isBlind",
            "isSlow",
            "isCanc",

            "isInvis",
            "isMean",
            "isGreed",
            "isBlock",
            "isRegen",
            "isFound",

            "canHuh",
            "canSee"
        ])
        self.stats:Stats = None                     # Physical description
        self.pack:list = []                         # What the thing is carrying

# roll a number of dice
def roll(number:int, sides:int) -> int:
    dtotal = 0
    for _ in range(number):
    	dtotal += Global.rnd(sides) + 1

    return dtotal

# CalcGoldValue:
# Calculate gold value
def CalcGoldValue(level:int) -> int:
    return Global.rnd(50 + 10 * level) + 2

def getNewItemGroup() -> int:
    global itemGorup
    Global.itemGorup += 1
    return Global.itemGorup

def ctrl(ch) -> int:
    return ord(ch) & 0x37

def copyStdscr(destWindow) -> None:
    destWindow.clear()
    for y in range(Global.cursesLines - 1):
        for x in range(Global.cursesColumns):
            ch = Global.stdscr.inch(y, x)
            destWindow.addch(y, x, ch)

def clearWindow(window) -> None:
    window.clear()
    for y in range(Global.cursesLines - 2):
        for x in range(Global.cursesColumns):
            window.addch(y, x, " ")
    Global.stdscr.refresh()
    window.refresh()

# vowelStr:
# for printfs: if string starts with a vowel, return "n" for an "an"
def vowelStr(string) -> str:
    ch = string.lower()[:1]
    return "n" if ch in [ "a", "e", "i", "o", "u"] else ""

# num:
# Figure out the plus number for armor/weapons
def num(n1, n2) -> int:
    if n1 == 0 and n2 == 0:
        return "+0"

    if n2 == 0:
        return f"{'' if n1 < 0 else '+'}{n1}"

    return f"{'' if n1 < 0 else '+'}{n1},{'' if n2 < 0 else '+'}{n2}"

# findObject:
# find the unclaimed object at y, x
def findObject(coord):
    for item in Global.levelObjectList:
        if item.position == coord:
            return item

    return None

# getRandomDir:
def getRandomDir() -> Coordinate:
    delta = Coordinate(0, 0)

    while True:
        delta.y = Global.rnd(3) - 1
        delta.x = Global.rnd(3) - 1
        if delta.y != 0 and delta.x != 0:
            break

    return delta
