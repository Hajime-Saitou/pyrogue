import Common
from Common import roll
from Rogue import DaemonExecuteTiming, Fuse
import random
import Pack
import Global
import Player
from enum import IntEnum
import Io
import Rings
import Daemons
import Move
import Options
import Fight
import Things

class PotionOf(IntEnum):
    Confusion = 0
    Paralysis = 1
    Poison = 2
    GainStrength = 3
    SeeInvisible = 4
    Healing = 5
    MonsterDetection = 6
    MagicDetection = 7
    RaiseLevel = 8
    ExtraHealing = 9
    HasteSelf = 10
    RestoreStrength = 11
    Blindness = 12
    ThirstQuenching = 13

def initTentativeNames(nofPotions):
    rainbow = [
        "Red",
        "Blue",
        "Green",
        "Yellow",
        "Black",
        "Brown",
        "Orange",
        "Pink",
        "Purple",
        "Grey",
        "White",
        "Silver",
        "Gold",
        "Violet",
        "Clear",
        "Vermilion",
        "Ecru",
        "Turquoise",
        "Magenta",
        "Amber",
        "Topaz",
        "Plaid",
        "Tan",
        "Tangerine",
    ]

    return random.sample(rainbow, nofPotions)

# quaff:
def quaff() -> None:
    item = Pack.getItem("quaff", ord(Global.Potion))

    # Make certain that it is somethings that we want to drink
    if item == None:
        return

    if item.type != Global.Potion:
        Io.msg("Yuk! Why would you want to drink that?")
        return

    if item == Player.curWeapon:
        Player.curWeapon = None

    # Calculate the effect it has on the poor guy.
    if item.which == PotionOf.Confusion:
        if not Player.player.flags.isHuh:
            Io.msg("Wait, what's going on here. Huh? What? Who?")
            Global.daemonManager.append(Fuse(Daemons.unconfuse, Global.rnd(8) + Global.HuhDuration), DaemonExecuteTiming.After)
        else:
            Global.daemonManager.lengthen(Daemons.unconfuse, Global.rnd(8) + Global.HuhDuration)
            Player.player.flags.isHuh = True
            Global.potionMagic.know[PotionOf.Confusion] = True
    elif item.which == PotionOf.Poison:
        if Player.ｗasWornRing(Rings.RingOf.SustainStrength):
            Player.changeStrength(-(Global.rnd(3) + 1))
            Io.msg("You feel very sick now.")
        else:
            Io.msg("You feel momentarily sick")
        Global.potionMagic.know[PotionOf.Poison] = True
    elif item.which == PotionOf.Healing:
        Player.player.stats.hitPoints += roll(Player.player.stats.level, 4)
        if Player.player.stats.hitPoints > Player.maxHp:
            Player.maxHp += 1
            Player.player.stats.hitPoints = Player.maxHp
        Io.msg("You begin to feel better.")
        Daemons.sight()
        Global.potionMagic.know[PotionOf.Healing] = True
    elif item.which == PotionOf.GainStrength:
        Io.msg("You feel stronger, now.  What bulging muscles!")
        Player.changeStrength(1)
        Global.potionMagic.know[PotionOf.GainStrength] = True
    elif item.which == PotionOf.MonsterDetection:
        # Potion of monster detection, if there are monters, detect them
        if len(Global.levelMonsterList) > 0:
            Global.helpWindow.clear()
            Global.helpWindow.overwrtite(Global.monsterWindow)
            # overwrite(mw, hw)
            Io.showWin(Global.helpWindow, "You begin to sense the presence of monsters.--More--")
            Global.potionMagic.know[PotionOf.MagicDetection] = True
        else:
            Io.msg("You have a strange feeling for a moment, then it passes.")
    elif item.which == PotionOf.MagicDetection:
        # Potion of magic detection.  Show the potions and scrolls
        if len(Global.levelObjectList) > 0:
            show:bool = False
            Global.helpWindow.clear()
            for item in Global.levelObjectList:
                if Things.isMagicItem(item):
                    show = True
                    Global.helpWindow.addch(item.position.y, item.position.x, Global.Magic)

                Global.potionMagic.know[PotionOf.MagicDetection] = True

                if show:
                    Io.showWin(Global.helpWindow, "You sense the presence of magic on this level.--More--")
                    break
        Io.msg("You have a strange feeling for a moment, then it passes.")
    elif item.which == PotionOf.Paralysis:
        Io.msg("You can't move.")
        no_command = Global.HoldTime
        Global.potionMagic.know[PotionOf.Paralysis] = True
    elif item.which == PotionOf.SeeInvisible:
        Io.msg(f"This potion tastes like {Player.fruitName} juice.")
        if not Player.player.flags.canSee:
            Player.player.flags.canSee = True
            Global.daemonManager.append(Fuse(Daemons.unsee, Global.SeeDuration), DaemonExecuteTiming.After)
            Move.light(Player.player.position)
        Daemons.sight()
        Global.potionMagic.know[PotionOf.SeeInvisible] = True
    elif item.which == PotionOf.RaiseLevel:
        Io.msg("You suddenly feel much more skillful")
        Fight.raiseLevel()
        Global.potionMagic.know[PotionOf.RaiseLevel] = True
    elif item.which == PotionOf.ExtraHealing:
        Player.player.stats.hitPoints += roll(Player.player.stats.level, 8)
        if Player.player.stats.hitPoints > Player.maxHp:
            Player.player.stats.hitPoints = Player.maxHp
        Io.msg("You begin to feel much better.")
        Daemons.sight()
        Global.potionMagic.know[PotionOf.ExtraHealing] = True
    elif item.which == PotionOf.HasteSelf:
        Player.addHaste(True)
        Io.msg("You feel yourself moving much faster.")
        Global.potionMagic.know[PotionOf.HasteSelf] = True
    elif item.which == PotionOf.RestoreStrength:
        Io.msg("Hey, this tastes great.  It make you feel warm all over.")
        if Player.player.stats.strength < Player.maxStats.strength or \
                (Player.player.stats.strength.strength == 18 and Player.player.stats.addStrength < Player.maxStats.addStrength):
            Player.player.stats.strength = Player.maxStats.strength
        Global.potionMagic.know[PotionOf.RestoreStrength] = True
    elif item.which == PotionOf.Blindness:
        Io.msg("A cloak of darkness falls around you.")
        if not Player.player.flags.isBlind:
            Player.player.flags.isBlind = True
            Global.daemonManager.append(Fuse(Daemons.sight, Global.seeDuration), DaemonExecuteTiming.After)
            Move.look(False)
        Global.potionMagic.know[PotionOf.Blindness] = True
    elif item.which == PotionOf.ThirstQuenching:
        Io.msg("This potion tastes extremely dull.")
        Global.potionMagic.know[PotionOf.ThirstQuenching] = True
    else:
        Io.msg("What an odd tasting potion!")
        return

    Io.status()
    if Global.potionMagic.know[item.which] and Global.potionMagic.guessName[item.which]:
        Global.potionMagic.guessName[item.which] = ""
    elif not Global.potionMagic.know[item.which] and Options.askMe and not Global.potionMagic.guessName[item.which]:
        Io.msg("What do you want to call it? ")
        inputType, string = Io.getStr("", Global.playerWindow)
        if inputType == Io.InputValueType.Norm:
            Global.potionMagic.guessName[item.which] = string

    # Throw the item away
    if item.count > 1:
        item.count -= 1
    else:
        Player.pack.remove(item)
