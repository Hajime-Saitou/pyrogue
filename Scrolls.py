# Read a scroll and let it happen
from enum import IntEnum
from Rogue import Coordinate
import Global
import Player
import Pack
import Io
import Rooms
import Move
import Monsters
import Chase
import Things
import Options

class ScrollOf(IntEnum):
	MonsterConfusion = 0,
	MagicMapping = 1,
	Light = 2,
	HoldMonster = 3,
	Sleep = 4,
	EnchantArmor = 5,
	Identify = 6,
	ScareMonster = 7,
	GoldDetection = 8,
	Teleportation = 9,
	EnchantWeapon = 10,
	CreateMonster = 11,
	RemoveCurse = 12,
	AggravateMonsters = 13,
	BlankPaper = 14,
	Genocide = 15

# initTentativeNames:
# Generate the names of the various scrolls
def initTentativeNames(nofScrolls):
    syllables = [
        "a", "ab", "ag", "aks", "ala", "an", "ankh", "app", "arg", "arze",
        "ash", "ban", "bar", "bat", "bek", "bie", "bin", "bit", "bjor",
        "blu", "bot", "bu", "byt", "comp", "con", "cos", "cre", "dalf",
        "dan", "den", "do", "e", "eep", "el", "eng", "er", "ere", "erk",
        "esh", "evs", "fa", "fid", "for", "fri", "fu", "gan", "gar",
        "glen", "gop", "gre", "ha", "he", "hyd", "i", "ing", "ion", "ip",
        "ish", "it", "ite", "iv", "jo", "kho", "kli", "klis", "la", "lech",
        "man", "mar", "me", "mi", "mic", "mik", "mon", "mung", "mur",
        "nej", "nelg", "nep", "ner", "nes", "nes", "nih", "nin", "o", "od",
        "ood", "org", "orn", "ox", "oxy", "pay", "pet", "ple", "plu", "po",
        "pot", "prok", "re", "rea", "rhov", "ri", "ro", "rog", "rok", "rol",
        "sa", "san", "sat", "see", "sef", "seh", "shu", "ski", "sna",
        "sne", "snik", "sno", "so", "sol", "sri", "sta", "sun", "ta",
        "tab", "tem", "ther", "ti", "tox", "trol", "tue", "turs", "u",
        "ulk", "um", "un", "uni", "ur", "val", "viv", "vly", "vom", "wah",
        "wed", "werg", "wex", "whon", "wun", "xo", "y", "yot", "yu",
        "zant", "zap", "zeb", "zim", "zok", "zon", "zum",
    ]

    scrollNames = []
    for index in range(nofScrolls):
        scrollName = ""
        nwords = Global.rnd(4) + 2
        for word in range(nwords):
            nsyl = Global.rnd(3) + 1
            for syl in range(nsyl):
                spellIndex = Global.rnd(len(syllables))
                scrollName += syllables[spellIndex] + " "
        
        scrollNames.append(scrollName.strip())

    return scrollNames

# readScroll:
def readScroll() -> None:
    item = Pack.getItem("read", ord(Global.Scroll))
    if item is None:
        return

    if item.type != Global.Scroll:
        Io.msg("There is nothing on it to read")
        return

    Io.msg("As you read the scroll, it vanishes.")
    # Calculate the effect it has on the poor guy.
    if item == Player.curWeapon:
        Player.curWeapon = None

    if item.which == ScrollOf.MonsterConfusion:
        # Scroll of monster confusion. Give him that power.
        Io.msg("Your hands begin to glow red")
        Player.player.flags.canHuh = True
    elif item.which == ScrollOf.Light:
        room = Rooms.Rooms.roomIn(Player.Player.position)
        if room is None:
            Io.msg("The corridor glows and then fades")
        else:
            Io.addmsg("The room is lit by a shimmering blue light.")
            Io.endmsg()
            room.flags.isDark = False
            # Light the room and put the player back up
            Move.light(Player.Player.position)
            Global.playerWindow.addch(Player.Player.position.y, Player.Player.position.x, Global.Player)
        Global.scrollMagic.know[ScrollOf.Light] = True
    elif item.which == ScrollOf.EnchantArmor:
        if Player.curArmor:
            Io.msg("Your armor glows faintly for a moment")
            Player.curArmor.armorClass -= 1
            Player.curArmor.flags.isCursed = False
    elif item.which == ScrollOf.HoldMonster:
        # Hold monster scroll.
        # Stop all monsters within two spaces from chasing after the hero.
        pos = Player.player.position
        for x in range(max(pos.x - 2, 0), pos.x + 2 + 1):
            for y in range(max(pos.y - 2, 0), pos.y + 2 + 1):
                ch = Global.monsterWindow.inch(y, x)
                if str(ch).isupper():
                    monster = Monsters.findMonster(Coordinate(x, y))
                    if monster:
                        monster.flags.isRun = False
                        monster.flags.isHeld = True
    elif item.which == ScrollOf.Sleep:
        # Scroll which makes you fall asleep
        Io.msg("You fall asleep.");
        Global.noCommand += 4 + Global.rnd(Global.SleepTime)
        Global.scrollMagic.know[ScrollOf.Sleep] = True
    elif item.which == ScrollOf.CreateMonster:
        # Create a monster
        # First look in a circle around him, next try his room
        # otherwise give up
        appear:int = 0

        # Search for an open place
        monsterCreatePosition = None
        for y in range(Player.player.positon.y, Player.player.positon.y + 1 + 1):
            for x in range(Player.player.positon.x, Player.player.positon.x + 1 + 1):
                coord = Coordinate(x, y)
                # Don't put a monster in top of the player.
                if coord == Player.player.position:
                    continue

                # Or anything else nasty
                if Chase.stepOk(Io.winAt(coord)):
                    appear += 1
                    if Global.rnd(appear) == 0:
                        monsterCreatePosition = coord.clone()

        if appear:
            Monsters.newMonster(Monsters.randMonster(False), monsterCreatePosition)
        else:
            Io.msg("You hear a faint cry of anguish in the distance.")
    elif item.which == ScrollOf.Identify:
        # Identify, let the rogue figure something out
        Io.msg("This scroll is an identify scroll")
        Global.scrollMagic.know[ScrollOf.Identify] = True
        Things.whatIs()
    elif item.which == ScrollOf.MagicMapping:
        # Scroll of magic mapping.
        Global.scrollMagic.know[ScrollOf.MagicMapping] = True
        Io.msg("Oh, now this scroll has a map on it.")
        Global.stdscr.overwrite(Global.helpWindow)

        # Take all the things we want to keep hidden out of the window
        for y in range(Global.cursesLines):
            for x in range(Global.cursesColumns):
                ch = Global.helpWindow.inch(y, x)
                newCh = ch
                if ch == Global.SecretDoor:
                    newCh = Global.Door
                    Global.stdscr.addch(y, x, newCh)
                elif ch in [ "-", "|", " ", Global.Door, Global.Passage, Global.Stairs ]:
                    mch = Global.monsterWindow.inch(y, x)
                    if mch != " ":
                        monster = Monsters.findMonster(Coordinate(x, y))
                        if monster.oldCh == " ":
                            monster.oldCh = ch
                    break
                else:
                    newCh = " "

                if newCh != ch:
                    Global.helpWindow.addch(newCh)

        # Copy in what he has discovered
        Global.playerWindow.overlay(Global.helpWindow)
        # And set up for display
        Global.helpWindow.overwrite(Global.playerWindow)
    elif item.which == ScrollOf.GoldDetection:
        # Scroll of gold detection
        gtotal:int = 0

        Global.helpWindow.clear()

        for room in Global.rooms:
            gtotal += room.goldValue
            if room.goldValue:
                ch = Global.stdscr.inch(room.goldPosition.y, room.goldPosition.x)
                if ch == Global.Gold:
                    Global.stdscr.inch(room.goldPosition.y, room.goldPosition.x, Global.Gold)

        if gtotal:
            Global.scrollMagic.know[ScrollOf.GoldDetection] = True
            Io.showiwn(Global.helpWindow, "You begin to feel greedy and you sense gold.--More--")
        else:
            Io.msg("You begin to feel a pull downward")
    elif item.which == ScrollOf.Teleportation:
        # Scroll of teleportation:
        # Make him dissapear and reappear

        curRoom = Rooms.roomIn(Player.player.position)
        room = Move.teleport()
        if room != curRoom:
            Global.scrollMagic.know[ScrollOf.Teleportation] = True
    elif item.which == ScrollOf.EnchantWeapon:
        if Player.curArmor is None:
            Io.msg("You feel a strange sense of loss.")
            return

        Player.curWeapon.flags.isCursed = True
        if Global.rnd(100) > 50:
            Global.curWeapon.hitPlus += 1
        else:
            Global.curWeapon.damagePlus += 1
        Io.msg(f"Your {Player.curWeapon.name} glows blue for a moment.")
    elif item.which == ScrollOf.ScareMonster:
        # A monster will refuse to step on a scare monster scroll
        # if it is dropped.  Thus reading it is a mistake and produces
        # laughter at the poor rogue's boo boo.
        Io.msg("You hear maniacal laughter in the distance.")
    elif item.which == ScrollOf.RemoveCurse:
        if Player.curArmor:
            Player.curArmor.flags.isCursed = False
        if Player.curWeapon:
            Player.curWeapon.flags.isCursed = False
        if Player.curRings["Left"]:
            Player.curRings["Left"].flags.isCursed = False
        if Player.curRings["Right"]:
            Player.curRings["Right"].flags.isCursed = False

        Io.msg("You feel as if somebody is watching over you.")
    elif item.which == ScrollOf.AggravateMonsters:
        # This scroll aggravates all the monsters on the current
        # level and sets them running towards the hero
        Monsters.aggravate()
        Io.msg("You hear a high pitched humming noise.")
    elif item.which == ScrollOf.BlankPaper:
        Io.msg("This scroll seems to be blank.")
    elif item.which == ScrollOf.Genocide:
        Io.msg("You have been granted the boon of genocide")
        Monsters.genocide()
        Global.scrollMagic.know[ScrollOf.Genocide] = True
    else:
        Io.msg("What a puzzling scroll!")
        return

    Move.look(True)     # put the result of the scroll on the screen
    Io.status()
    if Global.scrollMagic.know[item.which] and Global.scrollMagic.guessName[item.whichi]:
        Global.scrollMagic.guessName[item.which] = ""
    elif Global.scrollMagic.know[item.which] == "" and Options.askMe and Global.scrollMagic.guessName[item.which] is None:
        Io.msg("What do you want to call it? ")
        ret, string = Io.getStr("", Global.playerWindow)
        if ret == Io.InputValueType.Norm:
            Global.scrollMagic.guessName[item.which] = string

    # Get rid of the thing
    if item.count > 1:
        item.count -= 1
    else:
        Player.pack.remove(item)
