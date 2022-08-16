# Hero movement commands
import Rings
from Rogue import CarryObject
import Global
import Common
import Rooms
import Player
import Chase
import Io
import Monsters
import Fight
import Scrolls
import Traps
import Rogue
import copy
import Traps
import NewLevel
import Rip
import Weapon
import Move

# doRun:
# Start the hero running
def doRun(ch:str) -> None:
    Player.running = True
    Global.after = False
    Player.runCh = ch

# doMove:
# Check to see that a move is legal.  If it is handle the
# consequences (fighting, picking up, etc.)
def doMove(dy:int, dx:int) -> None:
    Player.firstMove = False
    if Player.noMove:
        Player.noMove -= 1
        Io.msg("You are still stuck in the bear trap")
        return

    # Do a confused move (maybe)
    if Global.rnd(100) < 80 and Player.player.flags.isHuh:
        newPosition = rndMove(Player.player)
    else:
        newPosition = Player.player.position + Rogue.Coordinate(dx, dy)

    # Check if he tried to move off the screen or make an illegal
    # diagonal move, and stop him if he did.
    if newPosition.x < 0 or  newPosition.x > Global.cursesColumns - 1\
            or newPosition.y < 0 or newPosition.y > Global.cursesLines - 2\
            or not Chase.diagOk(Player.player.position, newPosition):
        Global.after = False
        Player.running = False
        return

    if Player.running and Player.player.position == newPosition:
        Global.after = False
        Player.running = False

    ch = Io.winAt(newPosition)
    if Player.player.flags.isHeld and ch != "F":
        Io.msg("You are being held")
        return

    if ch in [ " ", "|", "-", Global.SecretDoor ]:
        Global.after = False
        Player.running = False
        return

    if ch in [
            Global.Gold,\
            Global.Potion,\
            Global.Scroll,\
            Global.Food,\
            Global.Weapon,\
            Global.Armor,\
            Global.Ring,\
            Global.Amulet,\
            Global.Stick\
            ]:
        Player.running = False
        Player.take = ch
    elif ch == Global.Trap:
        ch = beTrapped(newPosition)
        if ch in [ Traps.TrapDoor, Traps.TeleportTrap ]:
            return

    # move stuff
    if ch == Global.Passage and Io.winAt(Player.player.position) == Global.Door:
        light(Player.player.position)       # player get out the room.
    elif ch == Global.Door:
        Player.running = False
        if Io.winAt(Player.player.position) == Global.Passage:
            light(newPosition)              # player enter the room.
    elif ch == Global.Stairs:
        Player.running = False
    elif str(ch).isupper():
        Player.running = False
        Fight.fight(newPosition, ch, Player.curWeapon, False)
        return

    ch = Io.winAt(Player.player.position)
    Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, ch)
    Player.player.position = newPosition
    Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)
    
# beTrapped:
# The guy stepped on a trap.... Make him pay.
def beTrapped(coord):
    trap = Traps.trapAt(coord)
    count:bool = False
    Player.running = False

    Global.playerWindow.addch(trap.position.y, trap.position.x, Global.Trap)
    trap.flags.isFound = True

    if trap.type == Traps.TrapOf.TrapDoor:
        Global.level += 1
        Player.deepestLevelReached = max(Global.level, Player.deepestLevelReached)
        NewLevel.newLevel()
        Io.msg("You fell into a trap!")
    elif trap.type == Traps.TrapOf.BearTrap:
        Player.noMove += Global.BearTime
        Io.msg("You are caught in a bear trap")
    elif trap.type == Traps.TrapOf.SleepingGasTrap:
        Global.noCommand += Global.SleepTime
        Io.msg("A strange white mist envelops you and you fall asleep")
    elif trap.type == Traps.TrapOf.ArrowTrap:
        if Fight.swing(Player.player.stats.level - 1, Player.player.stats.arm, 1):
            Io.msg("Oh no! An arrow shot you")
            Player.player.stats.hitPoints -= Common.roll(1, 6)
            if Player.player.stats.hitPoints <= 0:
                Io.msg("The arrow killed you.")
                Rip.death("a")
        else:
            Io.msg("An arrow shoots past you.")
            item = CarryObject()
            item.type = Global.Weapon
            item.which = Weapon.WeaponOf.Arrow
            weapon = Global.weapons[item.which]
            item.damage = weapon["Damage"]
            item.hurlDamage = weapon["HurlDamage"]
            item.launch = weapon["Launch"]
            item.flags = weapon["Flags"]
            item.count = 1
            item.position = Player.player.position.clone()

            # BUG FIX!  This fixes the infamous "arrow bug".
            item.hitPlus = 0
            item.damagePlus = 0
            if Global.rnd(100) < 15:
                item.hitPlus += Global.rnd(3) + 1
            # End of BUG FIX!

            Weapon.fall(item, False)
    elif trap.type == Traps.TrapOf.TeleportTrap:
        Move.teleport()
    elif trap.type == Traps.TrapOf.PoisonDartTrap:
        if Fight.swing(Player.player.stats.level + 1, Player.player.stats.armorClass, 1):
            Io.msg("A small dart just hit you in the shoulder")
            Player.player.stats.hitPoints -= Common.roll(1, 4)
            if Player.player.stats.hitPoints <= 0:
                Io.msg("The dart killed you.")
                Rip.death("d")

            if not Player.ｗasWornRing(Rings.RingOf.SustainStrength):
                Player.changeStrength(-1)
        else:
            Io.msg("A small dart whizzes by your ear and vanishes.")

    # raw();      /* flush typeahead */
    # noraw();

    return trap.type

# rndMove:
# move in a random direction if the monster/person is confused
def rndMove(monster):
    retPosition = monster.position          # what we will be returning
    nopen = 0

    # Now go through the spaces surrounding the player and
    # set that place in the array to true if the space can be moved into
    ex = retPosition.x + 1
    ey = retPosition.y + 1
    for y in range(retPosition.y - 1, ey):
        if not 0 <= y < Global.cursesLines:
            continue
        for x in range(retPosition.x - 1, ex):
            if not 0 <= x < Global.cursesColumns:
                continue

            newPosition = Rogue.Coordinate(x, y)
            ch = Io.winAt(newPosition)
            if Chase.stepOk(ch):
                dest = newPosition
                if not Chase.diagOk(monster.position, newPosition):
                    continue

                stepOnTheScareMonster = False
                if ch == Global.Scroll:
                    for item in Global.levelObjectList:
                        if item.which == Scrolls.ScrollOf.ScareMonster:
                            stepOnTheScareMonster = True
                            break

                    if stepOnTheScareMonster:
                        continue

                nopen += 1
                if Global.rnd(nopen) == 0:
                    retPosition = dest

    return retPosition

# light
# Called to illuminate a room.
# If it is dark, remove anything that might move.
def light(coord):
    room = Rooms.roomIn(coord)
    if room == None or Player.player.flags.isBlind:
        return

    left = room.rect.left - 1
    top = room.rect.top
    for y in range(room.rect.height):
        for x in range(room.rect.width + 1):
            checkCoord = Rogue.Coordinate(left + x, top + y)
            ch = show(checkCoord)

            # Figure out how to display a secret door
            if ch == Global.SecretDoor:
                ch = secretDoor(checkCoord)

            # If the room is a dark room, we might want to remove
            # monsters and the like from it (since they might move)
            if str(ch).isupper():
                monster = Monsters.wakeMonster(checkCoord)
                if monster.oldCh == " ":
                    if not room.flags.isDark:
                        monster.oldCh = chr(Global.stdscr.inch(checkCoord.y, checkCoord.x))

            if room.flags.isDark:
                rch = chr(Global.playerWindow.inch(checkCoord.y, checkCoord.x))
                if rch in [ Global.Door, Global.Stairs, Global.Trap, "|", "-", " " ]:
                    ch = rch
                elif rch == Global.Floor:
                    ch =  Global.Floor if Player.player.flags.isBlind else " "
                else:
                    ch = " "
            
            if ch != 4294967295:
                Global.playerWindow.addch(checkCoord.y, checkCoord.x, ch)

    Global.playerWindow.refresh()

# show:
# returns what a certain thing will display as to the un-initiated
def show(coord):
    ch = Io.winAt(coord)

    if ch == Global.Trap:
        return Traps.secretTrap(coord)

    if ch in [ "M", "I" ]:
        monster = Monsters.findMonster(coord)
        if monster is None:
            Io.msg("Can't find monster in show")
            return " "

        if ch == "M":
            ch = monster.disguise

        # Hide invisible monsters
        elif not Player.player.flags.canSee:
            ch = chr(Global.stdscr.inch(coord.y, coord.x))

    return ch

# look:
# A quick glance all around the player
def look(wakeup=False):
    ch = ""
    passageCount = 0

    oldY, oldX = Global.playerWindow.getyx()
    oldCoord = Rogue.Coordinate(oldX, oldY)
    if Player.oldRoom and Player.oldRoom.flags.isDark and not Player.player.flags.isBlind:
        for x in range(oldCoord.x - 1, oldCoord.x + 1):
            for y in range(oldCoord.y - 1, oldCoord.y + 1):
                workCoord = Rogue.Coordinate(x, y)
                if workCoord != Player.player.position and show(workCoord) == Global.Floor:
                    Global.playerWindow.addch(y, x, " ")

    room = Rooms.roomIn(Player.player.position)
    inpass = True if room == None else False

    ep = Player.player.position + Rogue.Coordinate(1, 1)
    for x in range(max(Player.player.position.x - 1, 0), min(ep.x, Global.cursesColumns) + 1):
        for y in range(max(Player.player.position.y - 1, 1), min(ep.y, Global.cursesLines - 1) + 1):
            checkPosition = Rogue.Coordinate(x, y)

            ch = chr(Global.monsterWindow.inch(y, x))
            if str(ch).isupper():
                Global.logger.debug(f"look: {checkPosition}, {wakeup}")
                if wakeup:
                    monster = Monsters.wakeMonster(checkPosition)
                else:
                    monster = Monsters.findMonster(checkPosition)

                if monster:
                    monster.oldCh = Global.stdscr.inch(y, x)
                    if monster.oldCh == Global.Trap:
                        monster.oldCh = Traps.secretTrap(checkPosition)
                        pass
                    if monster.oldCh == Global.Floor and room.flags.isDark and not Player.player.flags.isBlind:
                        monster.oldCh = " "

            # Secret doors show as walls
            ch = show(checkPosition)
            if ch == Global.SecretDoor:
                ch = secretDoor(checkPosition)

            # Don't show room walls if he is in a passage
            if not Player.player.flags.isBlind:
                if Player.player.position == checkPosition or (inpass and ch in [ "-", "|" ]):
                    continue
            elif Player.player.position != checkPosition:
                    continue

            # ch = "~"
            if ch != 4294967295:
                Global.playerWindow.addch(y, x, ch)

            if Player.doorStop and not Player.firstMove and Player.running:
                if Player.runch == 'h':
                    if x == ep.x:
                        continue
                elif Player.runCh == 'j':
                    if y == Player.player.position.y - 1:
                        continue
                elif Player.runCh == 'k':
                    if y == ep.y:
                        continue
                elif Player.runCh == 'l':
                    if x == Player.player.position.x - 1:
                        continue
                elif Player.runCh == 'y':
                    if (x + y) - (Player.player.position.x + Player.player.position.y) >= 1:
                        continue
                elif Player.runCh == 'u':
                    if (y - x) - (Player.player.position.y + Player.player.position.x) >= 1:
                        continue
                elif Player.runCh == 'n':
                    if (x + y) - (Player.player.position.x + Player.player.position.y) <= -1:
                        continue
                elif Player.runCh == 'b':
                    if (y - x) - (Player.player.position.y + Player.player.position.x) <= -1:
                        continue

                if ch == Global.Door:
                    if x == Player.player.position.x or y == Player.player.position.y:
                        running = False
                elif ch == Global.PASSAGE:
                    if x == Player.player.position.x or y == Player.player.position.y:
                        passageCount += 1
                    break
                elif ch in [ Global.Floor, "|", "-", " " ]:
                    break
                else:
                    running = False
                    break
            if Player.doorStop and not Player.firstMove and passageCount > 1:
                running = False

    Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)
    Player.oldPosition = Player.player.position
    Player.oldRoom = room

# secret_door:
# Figure out what a secret door looks like.
def secretDoor(position):
    room = Rooms.roomIn(position)
    if not room.inRoom(position):
        return "p"

    if position.y in [ room.rect.top, room.rect.top + room.rect.height - 1 ]:
        return "-"
    else:
        return "|"

# telport:
# Bamf the hero someplace else
def teleport():
    beforePosition = copy.deepcopy(Player.player.position)

    Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.stdscr.inch(Player.player.position.y, Player.player.position.x))

    room = None
    while(True):
        room = Rooms.rndRoom()
        Player.player.position = room.rndPosition()
        if Io.winAt(Player.player.position) == Global.Floor:
            break

    light(beforePosition)
    light(Player.player.position)
    Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)

    # turn off ISHELD in case teleportation was done while fighting a Fungi
    if Player.player.flags.isHeld:
        Player.player.flags.isHeld = False
        Global.fungHit = 0
        Global.monsterParameters[ord("F") - ord("A")].stats.damage = "0d0"

    Global.count = 0
    Player.running = False
    # raw()                   # flush typeahead
    # noraw()
    return room
