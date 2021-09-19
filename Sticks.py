from enum import IntEnum
import Monsters
import Global
from Rogue import Coordinate, CarryObject
import Pack
import Io
import Common
import Rooms
import Player
import Move
import Chase
import Rip
import Fight
import Weapon
import copy

wsTypes = None
wsMade = None

# Rod/Wand/Staff types
class StickOf(IntEnum):
    Light = 0
    Striking = 1
    Lightning = 2
    Fire = 3
    Cold = 4
    Polymorph = 5
    MagicMissile = 6
    HasteMonster = 7
    SlowMonster = 8
    DrainLife = 9
    Nothing = 10
    TeleportAway = 11
    TeleportTo = 12
    Cancellation = 13

# fix
def fix(item):
    Global.logger.debug(f"which: {item.which}")
    if wsTypes[item.which] == "staff":
        item.damage = "2d3"
    else:
        item.damage = "1d1"
        item.hurlDamage = "1d1"

    item.charges = 3 + Global.rnd(5)
    if item.which == StickOf.Striking:
        item.hitPlus = 3
        item.damagePlus = 3
        item.damage = "1d8"
    elif item.which == StickOf.Light:
	    item.charges = 10 + Global.rnd(10)

def initTentativeName(nofSticks):
    return [ "" ] * nofSticks

# Initialize the construction materials for wands and staffs
def initMaterials(nofSticks):
    wood = [
        "Avocado wood",
        "Balsa",
        "Banyan",
        "Birch",
        "Cedar",
        "Cherry",
        "Cinnibar",
        "Driftwood",
        "Ebony",
        "Eucalyptus",
        "Hemlock",
        "Ironwood",
        "Mahogany",
        "Manzanita",
        "Maple",
        "Oak",
        "Persimmon wood",
        "Redwood",
        "Rosewood",
        "Teak",
        "Walnut",
        "Zebra wood",
    ]

    metal = [
        "Aluminium",
        "Bone",
        "Brass",
        "Bronze",
        "Copper",
        "Iron",
        "Lead",
        "Pewter",
        "Steel",
        "Tin",
        "Zinc",
    ]

    wsMade = [ "" ] * nofSticks
    wsTypes = [ "" ] * nofSticks
    for index in range(nofSticks):
        if Global.rnd(100) > 50:
            wsTypes[index] = "wand"
            wsMade[index] = metal[Global.rnd(len(metal))]
        else:
            wsTypes[index] = "staff"
            wsMade[index] = wood[Global.rnd(len(wood))]

    return

# charge a wand for wizards.
def chargeStr(item):
    return f"[{item.charges} charges]" if item.flags & Global.Flags.IsKnow else ""

# doZap:
def doZap(delta:Coordinate) -> None:
    item = Pack.getItem("zap with", ord(Global.Stick))
    if item is None:
        return

    if item.type != Global.Stick:
        Io.msg("You can't zap with that!")
        Global.after = False
        return

    if item.charges == 0:
        Io.msg("Nothing happens.")
        return

    if delta is None:
        delta = Common.getRandomDir()

    if item.which == StickOf.Light:
        # Reddy Kilowat wand.  Light up the room
        Global.ringMagic.know[StickOf.Light] = True

        room = Rooms.roomIn(Player.player.position)
        if room is None:
            Io.msg("The corridor glows and then fades")
        else:
            Io.addMsg("The room is lit by a shimmering blue light.")
            Io.endMsg()
            room.flags.isDark = False

            # Light the room and put the player back up
            Move.light(Player.player.position)
            Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)
    elif item.which == StickOf.DrainLife:
        # Take away 1/2 of hero's hit points, then take it away
        # evenly from the monsters in the room (or next to hero
        # if he is in a passage)
        if Player.player.stats.hitPoints < 2:
            Io.msg("You are too weak to use it.")
            return

        room = Rooms.roomIn(Player.player.position)
        if room is None:
            drain(Player.player.position.y - 1, Player.player.position.y + 1, Player.player.position.x - 1, Player.player.position.x + 1)
        else:
            drain(room.rect.top, room.rect.bottom, room.rect.left, room.rect.right)
    elif item.which in [ StickOf.Polymorph, StickOf.TeleportAway, StickOf.TeleportTo, StickOf.Cancellation ]:
        coord = Player.player.position.clone()
        while Chase.stepOk(Io.winAt(coord)):
            coord += delta

        monsterCh = str(Global.monsterWindow.inch(coord.y, coord.x))
        if monsterCh.isUpper():
            oMonsterCh = monsterCh
            monster = Monsters.findMonster(coord)

            if monsterCh == "F":
                Player.player.flags.isHeld = False

            if item.which == StickOf.Polymorph:
                oldch = monster.oldCh
                Global.levelMonsterList.remove(monster)
                delta = coord
                monsterCh = Global.rnd(26) + ord("A")
                Monsters.newMonster(monsterCh, delta)
                if not monster.flags.isRun:
                    Chase.runTo(delta, Player.player.position)

                if str(Global.playerWindow.inch(coord.y, coord.x)).isupper():
                    Global.playerWindow.addch(coord.y, coord.x, monsterCh)
                monster.oldCh = oldch
                ws_know[StickOf.Polymorph] |= (monster != oMonsterCh)
            elif item.which == StickOf.Cancellation:
                monster.flags.isCanc = True
                monster.flags.isInvis = False
            else:
                if item.which == StickOf.TeleportAway:
                    monster.position = Rooms.rndRoom().rndPosition()
                else:
                    monster.position = Player.player.position + delta

                if str(Global.playerWindow.inch(coord.y, coord.x)).isupper():
                    Global.playerWindow.addch(coord.y, coord.x, monster.oldCh)

                Chase.runTo(monster, Player.player.position)
                Global.monsterWindow.addch(coord.y, coord.x, " ")
                Global.monsterWindow.addch(monster.position.y, monster.position.x, monsterCh)
                if monster.position != coord:
                    monster.oldCh = Global.playerWindow.inch(monster.positon.y, monster.position.x)
    elif item.which == StickOf.MagicMissile:
        bolt = CarryObject()
        bolt.type = "*"
        bolt.position = Coordinate(0, 0)
        bolt.text = ""
        bolt.launch = 0
        bolt.damage = ""
        bolt.hurlDamage = "1d4"
        bolt.count = 0
        bolt.which = 0
        bolt.hitPlus = 100
        bolt.damagePlus = 1

        Weapon.doMotion(bolt, delta)
        if str(Global.monsterWindow.inch(bolt.y, bolt.x)).isupper() and Fight.saveThrow(Fight.SaveAgainstThings.Magic, Monsters.findMonster(bolt.position)):
                Weapon.hitMonster(bolt.position, bolt)
        else:
            Io.msg("The missle vanishes with a puff of smoke")

        Global.ringMagic.know[StickOf.MagicMissile] = True
    elif item.which == StickOf.Striking:
        delta += Player.player.position
        ch = str(Io.winAt(delta))
        if ch.isupper():
            if Global.rnd(20) == 0:
                item.damage = "3d8"
                item.damagePlus = 9
            else:
                item.damage = "1d8"
                item.damagePlus = 3
            Fight.fight(delta, ch, item, False)
    elif item.which in [ StickOf.HasteMonster, StickOf.SlowMonster ]:
        coord = Player.player.position.clone()
        while Chase.stepOk(Io.winAt(coord)):
            coord += delta

        ch = str(Global.monsterWindow.inch(coord.y, coord.x))
        if ch.isupper():
            monster = Monsters.findMonster(coord)
            if item.which == StickOf.HasteMonster:
                if monster.flags.isSlow:
                    monster.flags.isSlow = False
                else:
                    monster.flags.isHaste = True
            else:
                if monster.flags.isHaste:
                    monster.flags.isHaste = False
                else:
                    monster.flags.isSlow = True
                monster.turn = True

            delta = coord.clone()
            Chase.runTo(delta, Player.player.position)
    elif item.which in [ StickOf.Lightning, StickOf.Fire, StickOf.Cold ]:
        bolt = CarryObject()
        bolt.type = "*"
        bolt.position = Coordinate(0, 0)
        bolt.text = ""
        bolt.launch = 0
        bolt.damage = ""
        bolt.hurlDamage = "6d6"
        bolt.count = 0
        bolt.which = 0
        bolt.hitPlus = 100
        bolt.damagePlus = 0

        xy = abs(delta.y + delta.x)
        if xy == 0:
            dirCh = "/"
        elif xy == 1:
            dirCh = "-" if delta.y == 0 else "|"
        else:
            dirCh = "\\"

        if item.which == StickOf.Lightning:
            name = "bolt"
        elif item.which == StickOf.Fire:
            name = "flame"
        else:
            name = "ice"

        pos = Player.player.position.clone()
        bounced = False
        used = False
        spotpos = [ Coordinate(0, 0) ] * Global.BoltLength
        for y in range(Global.BoltLength):
            if used:
                break

            ch = Io.winAt(pos)
            spotpos[y] = pos
            if ch in [ Global.Door, Global.Global.SecretDoor, "|", "-", " " ]:
                bounced = True
                delta.y = -delta.y
                delta.x = -delta.x
                y -= 1
                Io.msg("The bolt bounces")
                break
            else:
                if not bounced and ch.isupper():
                    if not Fight.saveThrow(Fight.SaveAgainstThings.Magic, Monsters.findMonser(pos)):
                        bolt.o_pos = pos
                        Weapon.hitMonster(pos, bolt)
                        used = True
                    elif ch != "M" or Move.show(pos) == "M":
                        Io.msg(f"The {name} whizzes past the {Monsters.Monsters.getMonsterName(ch)}")
                        Chase.runto(pos, Player.player.position)
                elif bounced and pos == Player.player.position:
                    bounced = False
                    if not Fight.save(Fight.SaveAgainstThings.Magic):
                        Io.msg(f"You are hit by the {name}")
                        Player.player.stats.hitPoints -= Common.roll(6, 6)
                        if Player.player.stats.hitPoints <= 0:
                            Rip.death("B")
                        used = True
                    else:
                        Io.msg(f"The {name} whizzes by you")
                
                Global.playerWindow.addch(pos.y, pos.x, dirCh)
                Global.playerWindow.refresh()

            pos += delta

        for x in range(y):
            Global.playerWindow.addch(spotpos[x].y, spotpos[x].x, Move.show(spotpos[x]))
        Global.ringMagic.know[item.which] = True
    else:
        Io.msg("What a bizarre schtick!")

    item.charges -= 1

# drain:
# Do drain hit points from player shtick
def drain(ymin:int, ymax:int, xmin:int, xmax:int):
    # First count how many things we need to spread the hit points among
    monsterCount = 0

    for y in range(ymin, ymax + 1):
       for x in range(xmin, xmax + 1):
           ch = str(Global.monsterWindow.inch(y, x))
           if ch.isupper():
                monsterCount += 1

    if monsterCount == 0:
        Io.msg("You have a tingling feeling")
        return
    else:
        monsterCount = Player.player.stats.hitPoints / monsterCount

    Player.player.stats.hitPoints /= 2

    # Now zot all of the monsters
    for y in range(ymin, ymax + 1):
        for x in range(xmin, xmax + 1):
            coord = Coordinate(x, y)

            ch = str(Global.monsterWindow.inch(y, x))
            if ch.isupper():
                item = Monsters.findMonster(coord)
                if item:
                    item.stats.hitPoints -= monsterCount
                    if item.stats.hitPoints < 1:
                        Rip.killed(item, Chase.cansee(coord) and not item.flags.isInvis)
