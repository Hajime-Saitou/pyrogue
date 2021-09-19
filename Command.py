from Rogue import Coordinate
import Global
import Move
import NewLevel
import Io
import Player
import Common
import Rings
import curses
import Monsters
import Pack
import Traps
import Rip
import Rogue
from Rogue import DaemonExecuteTiming, KeyMap
import Weapon
import Armor
import Things
import Potions
import Options
import Scrolls
import Sticks

countCh = 0

# Process the user commands
def command():
    global countCh
    ntimes:int = 1          # Number of player moves
    count:int = 0           # Number of times to repeat command
    newCount:bool = False
    ch:str = ""

    if Player.player.flags.isHaste:
        ntimes += 1

    # Let the daemons start up
    Global.daemonManager.do(DaemonExecuteTiming.Before)

    for _ in range(ntimes):
        Move.look(True)
        if Player.running:
            Global.doorStop = False

        Io.status()

        lastscore = Player.purse
        # wmove(cw, hero.y, hero.x)
        if not ((Player.running or count) and Player.jump):
            Global.playerWindow.refresh()

        Player.take = ""
        Global.after = True

        # Read command or continue run
        Global.logger.debug(f"noCommand: {Global.noCommand}")
        if Global.noCommand == 0:
            if Player.running:
                ch = Player.runCh
            elif count:
                ch = countCh
            else:
                ch = Io.readChar()
                if Io.newPos != 0 and not Player.running:
                    #Erase message if its there
                    Io.msg("")
        else:
            ch = " "
        Global.logger.debug(f"Command Char: {ch}")

        if Global.noCommand != 0:
            Global.noCommand -= 1
            if Global.noCommand == 0:
                Io.msg("You can move again.")
        else:
            # check for prefixes
            if ch.isdigit():
                newCount = True
                count = 0
                while ch.isdigit():
                    count = count * 10 + (ord(ch) - ord("0"))
                    ch = Io.readChar()
                countCh = ch

                # turn off count for commands which don't make sense to repeat
                repeatChars = [
                    "h", "j", "k", "l",
                    "y", "u", "b", "n",
                    "H", "J", "K", "L",
                    "Y", "U", "B", "N",
                    "q", "r", "s", "f",
                    "t", "C", "I", " ",
                    "z", "p"
                ]
                if ch not in repeatChars:
                    count = 0

            if ch == "f":
                if not Player.player.flags.isBlind:
                    Global.doorStop = True
                    Global.firstMove = True

                if count and not newCount:
                    ch = direction
                else:
                    ch = Io.readChar()
                    directChars = [
                        "h", "j", "k", "l",
                        "y", "u", "b", "n"
                    ]
                    if ch in directChars:
                        ch = str(ch).toupper()
                    direction = ch
                Global.newCount = False

            # execute a command
            if count and not Player.running:
                count -= 1

            if   ch == "h": Move.doMove( 0, -1)
            elif ch == "j": Move.doMove( 1,  0)
            elif ch == "k": Move.doMove(-1,  0)
            elif ch == "l": Move.doMove( 0,  1)
            elif ch == "y": Move.doMove(-1, -1)
            elif ch == "u": Move.doMove(-1,  1)
            elif ch == "b": Move.doMove( 1, -1)
            elif ch == "n": Move.doMove( 1,  1)
            elif ch == "H": Move.doRun("h")
            elif ch == "J": Move.doRun("j")
            elif ch == "K": Move.doRun("k")
            elif ch == "L": Move.doRun("l")
            elif ch == "Y": Move.doRun("y")
            elif ch == "U": Move.doRun("u")
            elif ch == "B": Move.doRun("b")
            elif ch == "N": Move.doRun("n")
            elif ch == "t":
                delta = getDir()
                if not delta:
                    Global.after = False
                else:
                    Weapon.missile(delta)
            elif ch == "Q":
                Global.after = False
                quit()
            elif ch == "i":
                Global.after = False
                Pack.inventory(Player.pack, Global.InventryItemTypes.DisplayAll)
            elif ch == "I":
                Global.after = False
                Pack.pickyInventory(Player.pack)
            elif ch == "d":
                Things.drop()
            elif ch == "q":
                Potions.quaff()
            elif ch == "r":
                Scrolls.readScroll()
            elif ch == "e":
                Player.eat()
            elif ch == "w":
                Weapon.wield()
            elif ch == "W":
                Armor.wear()
            elif ch == "T":
                Armor.takeOff()
            elif ch == "P":
                Rings.ringOn()
            elif ch == "R":
                Rings.ringOff()
            elif ch == "o":
                Options.option()
            elif ch == "c":
                call()
            elif ch == ">":
                Global.after = False
                goDownLevel()
            elif ch == "<":
                Global.after = False
                goUpLevel()
            elif ch == "?":
                help()
            elif ch == "/":
                Global.after = False
                identify()
            elif ch == "s":
                search()
            elif ch == "z":
                Sticks.doZap(None)
            elif ch == "p":
                delta = getDir()
                if delta:
                    Sticks.do_zap(delta)
                else:
                    Global.after = False
            elif ch == "v":
                Io.msg(f"Pyrogue version {Common.version}. (mctesq was here)")
            elif ch == KeyMap.Control_L:
                Global.after = False
                curses.curscr.ClearOk(True)
                curses.curscr.refresh()
            elif ch == KeyMap.Control_R:
                Global.after = False
                Io.msg(Io.bufferedMessage)
            elif ch == " ":         # Rest command
                pass
            elif ch == KeyMap.Escape:
                Player.doorStop = False
                count = 0
                Global.after = False
            else:
                if Global.wasWizard:
                    if ch == "@":
                        Io.msg(f"@ y:{Player.player.position.y}, x:{Player.player.position.x}")
                    elif ch == "x":
                        Common.copyStdscr(Global.playerWindow)
                        Global.stdscr.refresh()
                        Global.playerWindow.refresh()
                        Io.status()
                        Global.after = False
                    elif ch == KeyMap.Control_D:
                        Global.level += 1
                        Player.deepestLevelReached = max(Global.level, Player.deepestLevelReached)
                        NewLevel.newLevel()
                        Global.after = False
                    elif ch == KeyMap.Control_U:
                        Global.level -= 1
                        if Global.level == 0:
                            Rip.totalWinner()
                        else:
                            NewLevel.newLevel()
                            Global.after = False
                    else:
                        Io.msg(f"Illegal command '{curses.unctrl(ch)}'.")
                        count = 0
                    pass
                else:
                    Io.msg(f"Illegal command '{curses.unctrl(ch)}'.")
                    count = 0

            # turn off flags if no longer needed
            if not Player.running:
                Global.doorStop = False

        # If he ran into something to take, let him pick it up.
        if Player.take:
            Pack.pickUp(Player.take)

        if not Player.running:
            Global.doorStop = False

    # Kick off the rest if the daemons and fuses
    if Global.after:
        Move.look(False)
        Global.daemonManager.do(DaemonExecuteTiming.After)
        if Player.ｗasWornRingOnHand("Left", Rings.RingOf.Searching):
            search()
            pass
        elif Player.ｗasWornRingOnHand("Left", Rings.RingOf.Teleportation) and Global.rnd(100) < 2:
            Move.teleport()
            pass
        if Player.ｗasWornRingOnHand("Right", Rings.RingOf.Searching):
            search()
            pass
        elif Player.ｗasWornRingOnHand("Right", Rings.RingOf.Teleportation) and Global.rnd(100) < 2:
            Move.teleport()
            pass

    return

# goDownLevel:
# He wants to go down a level
def goDownLevel():
    if Io.winAt(Player.player.position) != Global.Stairs:
        Io.msg("I see no way down.")
    else:
        Global.level += 1
        Player.deepestLevelReached = max(Global.level, Player.deepestLevelReached)
        NewLevel.newLevel()

    return

# goUpLevel:
# He wants to go up a level
def goUpLevel():
    if Io.winAt(Player.player.position) == Global.Stairs:
        if Global.hasAmulet:
            Global.level -= 1
            if Global.level == 0:
                Rip.totalWinner()
            else:
                NewLevel.newLevel()
                Io.msg("You feel a wrenching sensation in your gut.")
    else:
        Io.msg("I see no way up.")

    return

# search:
# Player gropes about him to find hidden things.
def search():
    # Look all around the hero, if there is something hidden there,
    # give him a chance to find it.  If its found, display it.
    if Player.player.flags.isBlind:
        return

    for x in range(Player.player.position.x - 1, Player.player.position.x + 2):
        for y in range(Player.player.position.y - 1, Player.player.position.y + 2):
            checkPosition = Rogue.Coordinate(x, y)
            ch = Io.winAt(checkPosition)
            if ch == Global.SecretDoor:
                if Global.rnd(100) < 20:
                    Global.stdscr.addch(y, x, Global.Door)
                    Global.count = 0
                break
            elif ch == Global.Trap:
                if Global.playerWindow.inch(y, x) == Global.Trap:
                    break
                if Global.rnd(100) > 50:
                    break
                trap = Traps.trapAt(checkPosition)
                trap.flags.isFound = True
                Global.playerWindow.addch(y, x, Global.Trap)
                Global.count = 0
                Player.running = False
                Io.msg(f"You found a{Common.vowelStr(trap.name)} {trap.name}.")

# help:
# Give single character help, or the whole mess if he wants it
def help():
    Io.msg("Character you want help for (* for all): ")
    helpCh = Io.readChar()
    Io.msg("")
    # If its not a *, print the right help string
    # or an error if he typed a funny character.
    if helpCh != "*":
        Global.playerWindow.move(0, 0)
        for ch, description in Global.helpList:
            if ch == helpCh:
                Io.msg(f"{ch}{description}")
                break
        else:
            Io.msg(f"Unknown character '{helpCh}'")

        return

    # Here we print help for everything.
    # Then wait before we return to command mode
    Global.helpWindow.clear()
    for index, ( ch, description ) in enumerate(Global.helpList):
        Global.helpWindow.addstr(index % 23, 40 if index > 22 else 0, f"{ch}{description}")

    Global.helpWindow.addstr(Global.cursesLines - 1, 0, "--Press space to continue--")
    Global.helpWindow.refresh()
    Io.waitFor(" ")

    Global.helpWindow.clear()
    Global.helpWindow.refresh()
    Global.playerWindow.clearok(True)
    Global.playerWindow.touchwin()
    Global.playerWindow.move(0, 0)
    Global.playerWindow.clrtoeol()
    Io.status()

# identify:
# Tell the player what a certain thing is.
def identify():
    Io.msg("What do you want identified? ")
    ch = Io.readChar()
    if ch == KeyMap.Escape:
        Io.msg("")
        return

    if ch.isupper():
        string = Monsters.getMonsterName(ch)
    else:
        if ch in [ "|", "-" ]:
            string = "wall of a room"
        elif ch == Global.Gold: 
            string = "gold"
        elif ch == Global.Stairs:
            string = "passage leading down"
        elif ch == Global.Gold:
            string = "door"
        elif ch == Global.Floor:
            string = "room floor"
        elif ch == Global.Player:
            string = "you"
        elif ch == Global.Passage:
            string = "passage"
        elif ch == Global.Trap:
            string = "trap"
        elif ch == Global.Potion:
            string = "potion"
        elif ch == Global.Scroll:
            string = "scroll"
        elif ch == Global.Food:
            string = "food"
        elif ch == Global.Weapon:
            string = "weapon"
        elif ch == " ":
            string = "solid rock"
        elif ch == Global.Armor:
            string = "armor"
        elif ch == Global.Amulet:
            string = "The Amulet of Yendor"
        elif ch == Global.Ring:
            string = "ring"
        elif ch == Global.Stick:
            string = "wand or staff"
        else:
            string = "unknown character"

    Io.msg(f"'{ch}' : {string}")

# quit:
#Have player make certain, then exit.
def quit():
    # Reset the signal in case we got here via an interrupt
    Io.msg("Really quit?")
    ch = Io.readChar()
    if ch == "y":
        Global.stdscr.clear()
        Global.stdscr.move(Global.cursesLines - 1, 0)
        Global.stdscr.refresh()
        Rip.score(Player.purse, 1)

        curses.curs_set(1)
        curses.endwin()
        exit(0)
    else:
        Io.msg("")
        Io.status()
        Io.status()
        Global.playerWindow.refresh()
        Global.count = 0

# call:
# allow a user to call a potion, scroll, or ring something
def call() -> None:
    item = Pack.getItem("call", Global.InventryItemTypes.Callable)
    #  Make certain that it is somethings that we want to wear
    if item is None:
        return

    if item.type == Global.Ring:
        guess = Global.ringMagic.guessName
        know = Global.ringMagic.know
        elsewise = Global.ringMagic.guessName[item.which] if Global.ringMagic.guessName[item.which] else Global.ringMagic.tentativeName[item.which]
    elif item.type == Global.Potion:
        guess = Global.potionMagic.guessName
        know = Global.potionMagic.know
        elsewise = Global.potionMagic.guessName[item.which] if Global.potionMagic.guessName[item.which] else Global.potionMagic.tentativeName[item.which]
    elif item.type == Global.Scroll:
        guess = Global.scrollMagic.guessName
        know = Global.scrollMagic.know
        elsewise = Global.scrollMagic.guessName[item.which] if Global.scrollMagic.guessName[item.which] else Global.scrollMagic.tentativeName[item.which]
    elif item.type == Global.Stick:
        guess = Global.stickMagic.guessName
        know = Global.stickMagic.know
        elsewise = Global.stickMagic.guessName[item.which] if Global.stickMagic.guessName[item.which] else Global.stickMagic.tentativeName[item.which]
    else:
        Io.msg("You can't call that anything")
        return

    if know[item.which]:
        Io.msg("That has already been identified")
        return

    Io.msg(f"Was called \"{elsewise}\"")
    Io.msg("What do you want to call it? ")

    if guess[item.which]:
        guess[item.which] = ""

    type, string = Io.getStr(elsewise, Global.playerWindow)
    if type == Io.InputValueType.Norm:
        guess[item.which] = string

# getDir:
# set up the direction co_ordinate for use in varios "prefix" commands
def getDir() -> Coordinate:
    prompt:str = "Which direction? "
    Io.msg(prompt)
    delta = Coordinate(0, 0)

    while True:
        gotIt = True
        ch = str(Io.readChar()).lower()
        if ch == "h":
            delta.y =  0
            delta.x = -1
        elif ch == "j":
            delta.y =  1
            delta.x =  0
        elif ch == "k":
            delta.y = -1
            delta.x =  0
        elif ch == "l":
            delta.y =  0
            delta.x =  1
        elif ch == "y":
            delta.y = -1
            delta.x = -1
        elif ch == "u":
            delta.y = -1
            delta.x =  1
        elif ch == "b":
            delta.y =  1
            delta.x = -1
        elif ch == "n":
            delta.y =  1
            delta.x =  1
        elif ch == KeyMap.Escape:
            return None
        else:
            Io.msgPos = 0
            Io.msg(prompt)
            break

    if Player.player.flags.isHuh and Global.rnd(100) > 80:
        delta = Common.getRandomDir()

    Io.msgPos = 0
    return delta
