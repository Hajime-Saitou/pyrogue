import Pack
import Global
import Io
from Fight import checkLevel
from Rogue.CarryObject import CarryObject
import Daemons
import Common

#define MAXPACK 23
MaxPack = 23

player = None
curWeapon = None
curArmor = None
curRings = { "Left": None, "Right": None }
pack = []

# game parameters
deepestLevelReached:int = 0     # The deepest level reached by the player
purse:int = 0                   # How much gold the rogue has
noFood = 0                      # Number of levels without food
foodLeft:int = 0                # Amount of food in hero's stomach
hungryState:int = 0             # How hungry is he
quiet:int = 0                   # Number of quiet turns
maxHp:int = 0                   # Player's max hit points
maxStats = None                 # The maximum for the player
noMove:int = 0                  # Number of turns held in place
running:bool = False            # True if player is running
doorStop:bool = False           # Stop running when we pass a door
firstMove:bool = False          # First move after setting doorStop
jump:bool = False               # Show running as series of jumps
take:str = ""                   # Thing the rogue is taking
runCh:str = ""                  # Direction player is running
oldRoom = None                  # Roomin(oldRoom)
oldPosition = None              # Position before last look() call

# option parameter
whoami = "player"               # Name of player
fruitName = "slimemold"         # Favorite fruit

# isWearingArmor
def isWearingArmor() -> bool:
    return curArmor is not None

# ｗasWornRingOnHand
def ｗasWornRingOnHand(hand, ringType) -> bool:
    return curRings[hand] is not None and curRings[hand].which == ringType

# ｗasWornRing
def ｗasWornRing(ringType) -> bool:
    return ｗasWornRingOnHand("Left", ringType) and ｗasWornRingOnHand("Right", ringType)

# eat
# She wants to eat something, so let her try
def eat() -> None:
    global foodLeft, curWeapon, hungryState, pack

    item:CarryObject = Pack.getItem("eat", ord(Global.Food))
    if item is None:
        return

    if item.type != Global.Food:
        Io.msg("Ugh, you would get ill if you ate that.")
        return

    item.count -= 1
    if item.count < 1:
        if item in pack:
            pack.remove(item)

    if item.which == 1:
        Io.msg(f"My, that was a yummy {fruitName}")
    else:
        if Global.rnd(100) > 70:
            Io.msg("Yuk, this food tastes awful")
            player.stats.experience += 1
            checkLevel()
        else:
            Io.msg("Yum, that tasted good")

    foodLeft += Global.HungerTime + Global.rnd(400) - 200
    if foodLeft > Global.StomachSize:
        food_left = Global.StomachSize

    hungryState = 0

    if item == curWeapon:
        curWeapon = None

# isEquipmentItem:
# see if the object is one of the currently used items
def isEquipment(item:CarryObject) -> bool:
    global curArmor, curWeapon, curRings
    if item is None:
        return False

    if item in [ curArmor, curWeapon, curRings["Left"], curRings["Right"] ]:
        Io.msg("That's already in use.")
        return True

    return False

# changeStrength:
# Used to modify the playes strength
# it keeps track of the highest it has been, just in case
def changeStrength(amount:int) -> None:
    if amount == 0:
        return

    strength:Common.Strength = player.stats.strength
    if amount > 0:
        for _ in range(amount):
            if strength.strength < 18:
                strength.strength += 1
            elif strength.addStrength == 0:
                strength.addStrength = Global.rnd(50) + 1
            elif strength.addStrength <= 50:
                strength.addStrength = 51 + Global.rnd(24)
            elif strength.addStrength <= 75:
                strength.addStrength = 76 + Global.rnd(14)
            elif strength.addStrength <= 90:
                strength.addStrength = 91
            elif strength.addStrength < 100:
                strength.addStrength += 1
    else:
        for _ in range(abs(amount)):
            if strength.strength < 18 or strength.addStrength == 0:
                strength.strength -= 1
            elif strength.addStrength <= 51:
                strength.addStrength = 0
            elif strength.addStrength < 76:
                strength.addStrength = 1 + Global.rnd(50)
            elif strength.addStrength < 91:
                strength.addStrength = 51 + Global.rnd(25)
            elif strength.addStrength < 100:
                strength.addStrength = 76 + Global.rnd(14)
            else:
                strength.addStrength = 91 + Global.rnd(8)
        if strength.strength < 3:
            strength.strength = 3

# addHaste:
# add a haste to the player
def addHaste(potion:bool) -> None:
    if player.flags.isHaste:
        Io.msg("You faint from exhaustion.")
        Global.noCommand += Global.rnd(8)
        Global.daemonManager.remove(Daemons.nohaste)
    else:
        player.flags.isHaste = True
        if potion:
            Global.daemonManager.append(Daemons.nohaste, Global.rnd(4) + 4, Daemons.DaemonExecuteTiming.After)
