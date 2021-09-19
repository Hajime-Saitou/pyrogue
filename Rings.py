# routines dealing specifically with rings
from enum import IntEnum
from Rogue import KeyMap
import Global
import Common
import Player
import random
import Io
import Pack
import Move
import Monsters
import Options
import Things

# Ring types
class RingOf(IntEnum):
    Protection = 0
    AddStrength = 1
    SustainStrength = 2
    Searching = 3
    SeeInvisible = 4
    Adornment = 5
    AggravateMonster = 6
    Dexterity = 7
    IncreaseDamage = 8
    Regeneration = 9
    SlowDigestion = 10
    Teleportation = 11
    Stealth = 12

# ringEat:
# how much food does this ring use up?
def ringEat(hand):
    ring = Player.curRings[hand]
    if ring == None:
        return 0

    if ring.which == RingOf.Regeneration:
        return 2
    elif ring.which == RingOf.SustainStrength:
        return 1
    elif ring.which == RingOf.Searching:
        return 1 if Global.rnd(100) < 33 else 0
    elif ring.which == RingOf.SlowDigestion:
        return -1 if Global.rnd(100) < 50 else 0
    else:
        return 0

def initTentativeNames(nofRings):
    stones = [
        "Agate",
        "Alexandrite",
        "Amethyst",
        "Carnelian",
        "Diamond",
        "Emerald",
        "Granite",
        "Jade",
        "Kryptonite",
        "Lapus lazuli",
        "Moonstone",
        "Obsidian",
        "Onyx",
        "Opal",
        "Pearl",
        "Ruby",
        "Saphire",
        "Tiger eye",
        "Topaz",
        "Turquoise",
    ]

    return random.sample(stones, nofRings)

# ringNum:
# print ring bonuses
def ringNum(item):
    if item.flags & Global.Flags.IsKnow\
            and item.which in [\
                RingOf.Protection, RingOf.AddStrength,
                RingOf.IncreaseDamage, RingOf.Dexterity ]:
        return Common.num(item.armorClass, 0)
    else:
        return ""

# ringOn:
def ringOn():
    item = Pack.getItem("put on", ord(Global.Ring))

    # Make certain that it is somethings that we want to wear
    if item is None:
        return
    if item.type != Global.Ring:
        Io.msg("It would be difficult to wrap that around a finger")

    # find out which hand to put it on
    if (Player.isEquipment(item)):
        return

    if Player.curRings["Left"] is None and Player.curRings["Right"] is None:
        hand = getHand()
        if hand  == "":
            return
    elif Player.curRings["Left"] is None:
        hand = "Left"
    elif Player.curRings["Right"] is None:
        hand = "Right"
    else:
        Io.msg("You already have a ring on each hand")
        return

    Player.curRings[hand] = item
    Io.msg(f"You have a ring on {hand.lower()} hand")

    # Calculate the effect it has on the poor guy.
    if item.which == RingOf.AddStrength:
        saveMax:Common.Strength = Player.maxStats.strength
        Player.changeStrength(item.armorClass)
        Player.maxStats.strength = saveMax
        pass
    elif item.which == RingOf.SeeInvisible:
        Player.player.flags.canSee = True
        Move.light(Player.player.position)
        Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)
    elif item.which == RingOf.AggravateMonster:
            Monsters.aggravate()

    Io.status()
    if Global.ringMagic.know[item.which] and Global.ringMagic.guessName[item.which]:
        Global.r_guess = ""
    elif not Global.ringMagic.know[item.which] and Options.askMe and Global.ringMagic.guessName[item.which] == "":
        Io.msgPos = 0
        Io.msg("What do you want to call it? ")
        ret, string = Global.playerWindow.get_str()
        if ret == Io.InputValueType.Norm:
            Global.ringMagic.guessName[item] = string
        Io.msg("")

# ringOff:
def ringOff():
    if Player.curRings["Left"] is None and Player.curRings["Right"] is None:
        Io.msg("You aren't wearing any rings")
        return

    hand = ""
    if Player.curRings["Left"] is None:
        hand = "Right"
    elif Player.curRings["Right"] is None:
        hand = "Left"
    else:
        hand = getHand()
        if hand not in [ "Left", "Right" ]:
            return

    Io.msgPos = 0
    item = Player.curRings[hand]
    if item is None:
        Io.msg("Not wearing such a ring")
        return

    if Things.dropCheck(item):
        Io.msg(f"Was wearing {Things.invName(item, True)}")

# getHand:
def getHand() -> str:
    while True:
        Io.msg("Left hand or right hand? ")
        ch = str(Io.readChar()).upper()
        if ch == "L":
            return "Left"
        elif ch == "R":
            return "Right"
        elif ch == KeyMap.Escape:
            return ""
        else:
            Io.msgPos = 0
            Io.msg("Please type L or R")
