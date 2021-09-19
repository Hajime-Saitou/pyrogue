#=============================================================================================
# pyrogue:
#     Rogue proting to the Python
#     Copyright (C) 2021 by Hajime Saito
#     All rights reserved
#=============================================================================================
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "Rogue"))
import argparse
import curses

from Rogue import Daemon, Fuse, DaemonExecuteTiming
import Global
import Rooms
import Init
import NewLevel
import Command
import Daemons
import Chase
import Player
import Weapon
import Armor
import Player
import Pack
from Rogue import CarryObject
import Options


def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--showScore", "--s", help="show the score ranking", action="store_true")

    return parser.parse_args(sys.argv[1:])

def main(stdscr):
    curses.curs_set(0)
    args = parseArguments()

    Init.initScore()

    # check for print-score option
    if args.showScore:
        curses.curs_set(1)
        curses.endwin()
        Global.scoreTable.print()
        exit(0)

    # parse environment declaration of options
    rogueOpts = os.getenv("ROGUEOPTS")
    if rogueOpts is not None:
        Options.parseOption(rogueOpts)

    # set seed of randomizer
    seed = os.getenv("SEED")
    if seed is not None:
        Global.randomizer.seed = int(seed)

    print(f"Hello {Options.whoami.value}, just a moment while I dig the dungeon...")

    # Set up windows
    Global.stdscr = stdscr
    Global.cursesLines = curses.LINES
    Global.cursesColumns = curses.COLS

    Global.playerWindow = curses.newwin(Global.cursesLines, Global.cursesColumns)
    Global.monsterWindow = curses.newwin(Global.cursesLines, Global.cursesColumns)
    Global.helpWindow = curses.newwin(Global.cursesLines, Global.cursesColumns)

    # Initialize game properties
    Init.initialize()

    NewLevel.newLevel()                 # Draw current level

    # Start up daemons and fuses
    Global.daemonManager.append(Daemon(Daemons.doctor), DaemonExecuteTiming.After)
    Global.daemonManager.append(Fuse(Daemons.swander, Global.WanderTime), DaemonExecuteTiming.After)
    Global.daemonManager.append(Daemon(Daemons.stomach), DaemonExecuteTiming.After)
    Global.daemonManager.append(Daemon(Chase.runners), DaemonExecuteTiming.After)

    # Give the rogue his weaponry.  First a mace.
    item = CarryObject.CarryObject()
    item.type = Global.Weapon
    item.which = Weapon.WeaponOf.Mace
    weapon = Global.weapons[item.which]
    item.damage = weapon["Damage"]
    item.hurlDamage = weapon["HurlDamage"]
    item.launch = weapon["Launch"]
    item.flags = weapon["Flags"]
    item.hitPlus = 1
    item.damagePlus = 1
    item.flags = Global.Flags.IsKnow
    Pack.addPack(item, True)
    Player.curWeapon = item

    # Now a +1 bow
    item = CarryObject.CarryObject()
    item.type = Global.Weapon
    item.which = Weapon.WeaponOf.ShortBow
    item.hitPlus = 1
    item.damagePlus = 0
    item.flags = Global.Flags.IsKnow
    Pack.addPack(item, True)

    # Now some arrows
    item = CarryObject.CarryObject()
    item.type = Global.Weapon
    item.which = Weapon.WeaponOf.Arrow
    item.count = 25 + Global.rnd(15)
    item.hitPlus = 0
    item.damagePlus = 0
    item.flags = Global.Flags.IsKnow
    Pack.addPack(item, True)

    # And his suit of armor
    item = CarryObject.CarryObject()
    item.type = Global.Armor
    item.which = Armor.ArmorOf.RingMail
    item.armorClass = -1
    item.flags = Global.Flags.IsKnow
    Pack.addPack(item, True)
    Player.curArmor = item

    # Give him some food too
    item = CarryObject.CarryObject()
    item.type = Global.Food
    item.which = 0
    item.count = 1
    Pack.addPack(item, True)

    item = CarryObject.CarryObject()
    item.type = Global.Ring
    item.which = 0
    item.flags = Global.Flags.IsKnow
    Pack.addPack(item, True)
    Player.curRings["Left"] = item

    # Now playing rogue
    playIt()

    return

# The main loop of the program.  Loop until the game is over,
# refreshing things and looking at the proper times.
def playIt():
    # save player position for Move.look() call
    Player.oldPosition = Player.player.position
    Player.oldRoom = Rooms.roomIn(Player.player.position)

    while Global.playingGame:
        Command.command()               # Command execution

    endIt()

# endIt:
# Exit the program abnormally.
def endIt():
    curses.curs_set(1)
    curses.endwin()
    exit(0)

if __name__ == '__main__':
    curses.wrapper(main)
    curses.endwin()
