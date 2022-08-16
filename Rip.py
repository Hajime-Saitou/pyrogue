# File for the fun ends, Death or a total win
import Global
import Player
import Monsters
import Common
import time
import curses
from Rogue import *
import Io
import Rings
import Things

# death:
# Do something really fun when he dies
def death(monsterType:str):
    Global.stdscr.clear()
    Global.stdscr.move(8, 0)
    Global.stdscr.addstr(
"""
                       __________
                      /          \\
                     /    REST    \\
                    /      IN      \\
                   /     PEACE      \\
                  /                  \\
                  |                  |
                  |                  |
                  |   killed by a    |
                  |                  |
                  |       1980       |
                 *|     *  *  *      | *
         ________)/\\\\_//(\\/(/\\)/\\//\\/|_)_______
"""
    )

    killer = killname(monsterType)

    Global.stdscr.addstr(int(15), int(28 - centering(Player.whoami)), Player.whoami)
    buf = f"{int(Player.purse / 10)} Au"
    Global.stdscr.addstr(int(16), int(28 - centering(buf)), buf)
    Global.stdscr.addstr(int(18), int(28 - centering(killer)), killer)
    Global.stdscr.addstr(int(16), int(33), Common.vowelStr(killer))
    Global.stdscr.addstr(int(19), int(26), time.strftime("%Y"))
    Global.stdscr.move(Global.cursesLines - 1, 0)
    Global.stdscr.addstr("[Press return to continue]")
    Global.stdscr.refresh()
    Io.waitFor("\n")
    score(Player.purse, 0, monsterType)

    curses.curs_set(1)
    curses.endwin()
    exit(0)

# centering:
# calculate a string centring position
def centering(message:str) -> int:
    return int((len(message) + 1) / 2)

# killname:
# get killer or trap name
def killname(monsterType:str) -> str:
    if monsterType.isupper():
        return Monsters.getMonsterName(monsterType)

    if monsterType == "a":
        return "arrow"
    elif monsterType == "d":
        return "dart"
    elif monsterType == "b":
        return "bolt"

# score:
# figure score and post it.
def score(amount:int, reasonId:int, monsterType:str=""):
    newScore = Score()
    newScore.score = amount
    newScore.playerName = Player.whoami
    if reasonId == 0:       # killed by monster
        killer = killname(monsterType)
        newScore.reason = f"killed by a{Common.vowelStr(killer)} {killer}"
    elif reasonId == 1:
        newScore.reason = "quit"
    elif reasonId == 2:
        newScore.reason = "A total winner"
    newScore.level = Global.level if reasonId != 2 else Player.deepestLevelReached

    Global.scoreTable.entry(newScore)
    Global.scoreTable.print()
    Global.scoreTable.save(Global.scoreFilename)

# totalWinner:
# Now you brought the amulet of yendor.
def totalWinner():
    Global.stdscr.clear()
    Global.stdscr.standout()
    Global.stdscr.addstr("                                                               \n")
    Global.stdscr.addstr("  @   @               @   @           @          @@@  @     @  \n")
    Global.stdscr.addstr("  @   @               @@ @@           @           @   @     @  \n")
    Global.stdscr.addstr("  @   @  @@@  @   @   @ @ @  @@@   @@@@  @@@      @  @@@    @  \n")
    Global.stdscr.addstr("   @@@@ @   @ @   @   @   @     @ @   @ @   @     @   @     @  \n")
    Global.stdscr.addstr("      @ @   @ @   @   @   @  @@@@ @   @ @@@@@     @   @     @  \n")
    Global.stdscr.addstr("  @   @ @   @ @  @@   @   @ @   @ @   @ @         @   @  @     \n")
    Global.stdscr.addstr("   @@@   @@@   @@ @   @   @  @@@@  @@@@  @@@     @@@   @@   @  \n")
    Global.stdscr.addstr("                                                               \n")
    Global.stdscr.addstr("     Congratulations, you have made it to the light of day!    \n")
    Global.stdscr.standend()
    Global.stdscr.addstr("\nYou have joined the elite ranks of those who have escaped the\n");
    Global.stdscr.addstr("Dungeons of Doom alive.  You journey home and sell all your loot at\n");
    Global.stdscr.addstr("a great profit and are admitted to the fighters guild.\n")
    Global.stdscr.addstr(Global.cursesLines - 1, 0, "--Press space to continue--")
    Global.stdscr.refresh()
    Io.waitFor(" ")

    # calclate total amounts
    print("--- Total results ---")
    print("")
    print("   Worth Item")

    oldPurse = Player.purse

    itemIndex:int = 0
    for item in Player.pack:
        worth:int = 0

        if item.type == Global.Food:
            worth = 2 * item.count
        elif item.type == Global.Weapon:
            worth = Global.weapons.itemList[item.which]["Worth"]
            worth *= (item.hitPlus + item.damagePlus) * 10 + 1
            worth *= item.count
        elif item.type == Global.Armor:
            worth = Global.armors.itemList[item.which]["Worth"]
            worth *= (Global.armors[item.which]["ArmorClass"] - item.armorClass) * 10 + 1
        elif item.type == Global.Scroll:
            worth = Global.scrollMagic.itemList[item.which]["worth"]
            worth *= item.count
            Global.scrollMagic.know[item.which] = True
        elif item.type == Global.Potion:
            worth = Global.potionMagic.itemList[item.which]["worth"]
            worth *= item.count
            Global.potionMagic.know[item.which] = True
        elif item.type == Global.Ring:
            worth = Global.ringMagic.itemList[item.which]["worth"]
            worth *= item.count
            if item.which in [ Rings.RingOf.AddStrength, Rings.RingOf.IncreaseDamage, Rings.RingOf.Protection, Rings.RingOf.Dexterity ]:
                if item.armorClass > 0:
                    worth += item.armorClass * 20
                else:
                    worth = 50
            Global.ringMagic.know[item.which] = True
        elif item.type == Global.Stick:
            Global.stickMagic.know[item.which] = True
            worth = Global.stickMagic.itemList[item.which]["worth"]
            worth += item.charges * 20
        elif item.type == Global.Amulet:
            worth = 1000

        item.flags.isKnow = True            # print canonical name
        print(itemIndex + 1, 0, f"{chr(ord('a') + itemIndex)}) {worth:>5d} {Things.invName(item, False)}")
        itemIndex += 1
        Player.purse += worth

    print(itemIndex + 2, 0, f"   {oldPurse:>5d} Gold Peices")
    print("")
    score(Player.purse, 2)

    curses.curs_set(1)
    curses.endwin()
    exit(0)
