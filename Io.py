# Various input/output functions
import Global
import Player
from Rogue import Coordinate, KeyMap
import curses
from enum import IntEnum
import os
import struct

# return values for get functions
class InputValueType(IntEnum):
    Norm = 0        # normal exit
    Quit = 1        # quit option setting
    Minus = 2       # back up one option

# global variables
msgPos:int = 0              # Where cursor is on top line
newPos:int = 0              # Buffered message length
bufferedMessage:str = ""

# msg:
# Display a message at the top of the screen.
def msg(formattedString:str) -> None:
    global msgPos

    # if the string is "", just clear the line
    if formattedString == "":
        Global.playerWindow.move(0, 0)
        Global.playerWindow.clrtoeol()
        msgPos = 0
        return

    # otherwise add to the message and flush it out
    doAdd(formattedString)
    endMsg()

# addMsg:
# add things to the current message
def addMsg(formattedString:str) -> None:
    doAdd(formattedString)

# endMsg:
# Display a new msg (giving him a chance to see the previous one if it
# is up there with the --More--)
def endMsg() -> None:
    global bufferedMessage, newPos, msgPos

    if msgPos > 0:
        Global.playerWindow.addstr(0, msgPos, "--More--")
        Global.playerWindow.refresh()
        waitFor(" ")

    Global.playerWindow.addstr(0, 0, bufferedMessage)
    Global.playerWindow.clrtoeol()
    Global.playerWindow.refresh()
    msgPos = newPos
    newPos = 0
    bufferedMessage = ""

# doAdd:
# add message buffer to string
def doAdd(formattedString:str) -> None:
    global bufferedMessage, newPos

    bufferedMessage += formattedString
    newPos = len(bufferedMessage)

# waitFor:
# Sit around until the guy types the right key
def waitFor(ch:str) -> None:
    if ch == "\n":
        while True:
            if readChar() in [ "\n", "\r" ]:
                break
    else:
        while True:
            if ch == readChar():
                break

# status:
# Display the important stats line.  Keep the cursor where it was.
def status():
    dispArmorClass = Player.curArmor.armorClass if Player.curArmor else Player.player.stats.armorClass
    stat = [
        f"Level: {Global.level:>2d}",
        f"Gold: {Player.purse:>4d}",
        f"Hp: {Player.player.stats.hitPoints:>3d}({Player.maxHp:>3d})",
        f"Str: {Player.player.stats.strength.strength:>2}/{Player.player.stats.strength.addStrength:>2d}",
        f"Ac: {dispArmorClass:>2d}",
        f"Exp {Player.player.stats.level}/{Player.player.stats.experience}",
        f"{getHungrySrting(Player.hungryState)}",
        # f"s {Player.foodLeft}"                # for debug
    ]
    Global.playerWindow.move(Global.cursesLines - 1, 0)
    Global.playerWindow.clrtoeol()
    Global.playerWindow.addstr(Global.cursesLines - 1, 0, ("  ").join(stat))

# getHungrySrting:
def getHungrySrting(state:int) -> str:
    return [ "", "Hungry", "Weak", "Fainting" ][state]

# winAt:
def winAt(coord:Coordinate) -> str:
    ch = Global.monsterWindow.inch(coord.y, coord.x)
    if ch != 4294967295:
        ch = chr(ch)
    
    if ch == " ":
        ch = Global.stdscr.inch(coord.y, coord.x)
        if ch != 4294967295:
            ch = chr(ch)
    
    return ch

# readChar:
# read character from curses.stdscr
def readChar() -> None:
    return chr(Global.stdscr.getch())

# getStr:
# Set a string to buffer with curses window
def getStr(defaultString:str, window:curses.window) -> tuple:
    global msgPos

    window.refresh()
    oy, ox = window.getyx()

    # loop reading in the string, and put it in a temporary buffer
    string:str = defaultString
    while True:
        ch = readChar()
        if ch in [ KeyMap.CarriageReturn, KeyMap.LineFeed, KeyMap.Escape, KeyMap.Bell ]:
            break
        window.clrtoeol()
        window.refresh()
        if ch == -1:
            continue
        elif ch == KeyMap.Backspace:   # process erase character
            if len(string) > 0:
                string = string[0:-1]
                window.addch(KeyMap.Backspace)
                window.clrtoeol()
            continue
        elif ch == KeyMap.Control_C:   # process kill character
            string = ""
            window.move(oy, ox)
            window.clrtoeol()
            continue
        elif len(string) == 0:
            if ch == "-":
                break
            elif ch == "~":
                string = os.getenv("HOMEPATH")
                window.addstr(string)
                continue

        string += str(ch)
        window.addstr(curses.unctrl(ch))

    if len(string) > 0:         # only change option if something has been typed
        string = strucpy(string)

    window.addstr(oy, ox, f"{string}\n")
    window.refresh()

    if window == Global.playerWindow:
        msgPos += len(string)

    if ch == "-":
        return ( InputValueType.Minus, string )
    elif ch in [ KeyMap.Escape, KeyMap.Bell ]:
        return ( InputValueType.Quit, string )
    else:
        return ( InputValueType.Norm, string )

# getBool:
# allow changing a boolean option and print it out
def getBool(value:bool, window:curses.window) ->tuple:
    oy, ox = window.getyx()
    window.addstr(str(value))

    while True:
        window.move(oy, ox)
        window.refresh()

        ch = str(readChar()).upper()
        if ch == "T":
            value = True
            break
        elif ch == "F":
            value = False
            break
        elif ch in [ "\n", "\r" ]:
            break
        elif ch in [ KeyMap.Escape, KeyMap.Bell ]:
            return ( InputValueType.Quit, value )
        elif ch == "-":
            return ( InputValueType.Minus, value )
        else:
            window.addstr(oy, ox + 10, "(T or F)")

    window.move(oy, ox)
    window.addstr(f"{value}\n")
    return ( InputValueType.Norm, value )

# strucpy:
# copy string using unctrl for things
def strucpy(src:str) -> str:
    string:str = ""
    for ch in list(src):
        string += str(curses.unctrl(ch))

    return string

# showWin:
# function used to display a window and wait before returning
def showWin(window:curses.window, message:str) -> None:
    Global.stdscr.addstr(0, 0, message)
    Global.stdscr.touchwin()
    Global.stdscr.move(Player.player.position.y, Player.player.position.x)
    Global.stdscr.draw()
    waitFor(" ")

    Global.playerWindow.clearok(True)
    Global.playerWindow.touchwin()
