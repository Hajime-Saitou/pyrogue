# Dig and draw a new level
import Global
import Common
import Rooms
import Passages
import Things
import Io
import Player

# newLevel:
def newLevel():
    if Global.level > Global.maxLevel:
        Global.maxLevel = Global.level

    Global.playerWindow.clear()
    Global.monsterWindow.clear()
    Global.stdscr.clear()

    # Free up the monsters on the last level
    Global.levelMonsterList.clear()

    Rooms.doRooms(Global.cursesColumns, Global.cursesLines)    # Draw rooms
    Passages.doPassage()                        # Draw passages
    Player.noFood += 1
    Things.putThings(9)                         # Place objects (if any)
    Things.putStair()                           # Place the staircase down.
    Things.putTraps(10)                         # Place the traps
    Common.clearWindow(Global.playerWindow)
    Io.status()
    Things.putHero()
