import curses
from Rogue.Daemon import DaemonExecuteTiming, Fuse
import Global
import Common
import copy
import Player
import Rings
import Chase
import Io
import Rooms
import Daemons
from Rogue import Coordinate, KeyMap
import Fight
import Monsters

# Array containing information on all the various types of mosnters
class Monster(object):
    def __init__(self, name, carry, flags, stats):
        self.name = name            # What to call the monster
        self.carry = carry          # Probability of carrying something
        self.flags = flags          # Things about the monster
        self.stats = stats          # Initial stats

# List of monsters in rough order of vorpalness
lvl_mons =  "KJBSHEAOZGLCRQNYTWFIXUMVDP"
wand_mons = "KJBSH AOZG CRQ Y W IXU V  "

# randMonster:
# Pick a monster to show up. The lower the level,
# the meaner the monster.
def randMonster(wander):
    global lvl_mons, wand_mons

    mons = wand_mons if wander else lvl_mons
    index = 0
    while True:
        index = Global.level + (Global.rnd(10) - 5)
        if index < 0:
            index = Global.rnd(5) + 1
        elif index >= 26:
            index = Global.rnd(5) + 21

        if mons[index] != " ":
            break

    return mons[index]

# findMonster:
# Find the level monster from his coordinates
def findMonster(coord):
    for monster in Global.levelMonsterList:
        if coord == monster.position:
            return monster

    return None

# newMonster:
# Pick a new monster and add it to the list
def newMonster(typeOfMonster, position:Coordinate):
    monster = Common.Thing()
    Global.levelMonsterList.append(monster)

    monster.type = typeOfMonster
    monster.position = position
    Global.monsterWindow.addch(position.y, position.x, typeOfMonster)
    monster.oldCh = Global.Floor

    monsterParameter = Global.monsterParameters[ord(typeOfMonster) - ord("A")]
    monster.stats = copy.deepcopy(monsterParameter.stats)
    monster.stats.hitPoints = Common.roll(monsterParameter.stats.level, 8)

    # set flags
    if monsterParameter.flags & Global.Flags.IsMean:
        monster.flags.isMean = True
    if monsterParameter.flags & Global.Flags.IsRegen:
        monster.flags.isRegen = True
    if monsterParameter.flags & Global.Flags.IsInvis:
        monster.flags.isInvis = True
    if monsterParameter.flags & Global.Flags.IsGreed:
        monster.flags.isGreed = True
    if monsterParameter.flags & Global.Flags.IsBlock:
        monster.flags.isBlock = True

    monster.turn = True
    monster.pack = []
    if Player.ｗasWornRing(Rings.RingOf.AggravateMonster):
    	Chase.runTo(position, Player.player.position)

    # mimic disguised.
    if typeOfMonster == "M":
        monster.disguise = disguise()

    return monster

# disguise:
# Mimic disguise to carry object.
def disguise():
    disguiseTable = [
        Global.Gold,
        Global.Potion,
        Global.Scroll,
        Global.Stairs,
        Global.Weapon,
        Global.Armor,
        Global.Ring,
        Global.Stick,
        Global.Amulet
    ]

    isLevelWhereAmuletExists = Global.level > Global.LevelWhereAmuletExists
    return disguiseTable[Global.rnd(9 if isLevelWhereAmuletExists else 8)]

# getMonsterName:
# Get the monster name by monster types.
def getMonsterName(monsterType:str):
    return Global.monsterParameters[ord(monsterType) - ord("A")].name

# wanderer:
# A wandering monster has awakened and is headed for the player
def wanderer():
    hr = Rooms.roomIn(Player.player.position)
    position  = None
    while(True):
        room = Rooms.rndRoom()
        if room == hr:
            continue

        position  = room.rndPosition()
        ch = Global.stdscr.inch(position.y, position.x)
        if ch == curses.ERR:
            # debug("Routine wanderer: mvwinch failed to %d,%d", cp.y, cp.x);
            Io.waitFor("\n")
        elif Chase.stepOk(ch):
            break

    monster = newMonster(randMonster(wander=True), position)
    monster.flags.isRun = True
    monster.destination = Player.player.position

    if Global.wasWizard:
        Io.msg(f"Started a wandering {Monsters.getMonsterName(monster.type)}")

# wakeMonster:
# what to do when the hero steps next to a monster
def wakeMonster(coord):
    Global.logger.debug(f"wake: {coord}")

    monster:Common.Thing = findMonster(coord)
    if monster == None:
	    Io.msg("Can't find monster in show")

    ch = monster.type
    # Every time he sees mean monster, it might start chasing him
    if Global.rnd(100) > 33 and monster.flags.isMean and not monster.flags.isHeld and Player.ｗasWornRing(Rings.RingOf.Stealth):
    # if True:
        monster.destination = Player.player.position
        monster.flags.isRun = True
        Global.logger.debug(f"monster {ch} wake")

    room:Rooms.Room = Rooms.roomIn(Player.player.position)

    # The umber hulk's gaze has confused you.
    if ch == "U" and not Player.player.flags.isBlind:
        if (room and room.flags.isDark) or monster.distance(Player.player.position) < 3:
            if not monster.flags.isFound and not Fight.saveThrow(Fight.SaveAgainstThings.Magic):
                Io.msg("The umber hulk's gaze has confused you.")
                if Player.player.flags.isHuh:
                    Global.daemonManager.lengthen(Daemons.unconfuse, Global.rnd(20) + Global.HuhDuration)
                else:
                    Global.daemonManager.append(Fuse(Daemons.unconfuse, Global.rnd(20) + Global.HuhDuration), DaemonExecuteTiming.After)
                Player.player.flags.isHuh = True

            monster.flags.isFound = True

    # Hide invisible monsters
    if monster.flags.isInvis and not Player.player.flags.canSee:
        ch = Global.stdscr.inch(coord.y, coord.x)
        # Let greedy ones guard gold
        if monster.flags.isGreed and not monster.flags.isRun:
            if room and room.goldValue:
                monster.destination = room.goldPosition
                monster.flags.isRun = True

    return monster

# genocide:
# Genocide the specific monster-races permanently.
def genocide() -> None:
    global lvl_mons, wand_mons

    Io.addMsg("Which monser")
    Io.addMsg(" do you wish to wipe out")
    Io.msg("? ")

    while True:
        ch = Io.readChar()
        if not str(ch).isalpha():
            continue
        if ch == KeyMap.Escape:      # cancel
            return

        Io.msgPos = 0
        Io.msg("Please specifiy a letter between 'A' and 'Z'")

        ch = str(ch).upper()[0]

        # kill specific monster in level.
        for monster in filter(lambda m: m.type == ch, Global.levelMonsterList):
            Fight.remove(monster)

        # delete monster race from monster list.
        lvl_mons = lvl_mons.replace(ch, " ")
        wand_mons = wand_mons.replace(ch, " ")

# aggravate:
# aggravate all the monsters on this level
def aggravate() -> None:
    for monster in Global.levelMonsterList:
        Chase.runTo(monster, Player.playerposition)

