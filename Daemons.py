# All the daemon and fuse functions are in here
from Rogue.Daemon import Daemon, DaemonManager, Fuse, DaemonExecuteTiming
import Global
import Common
import Player
import Rings
import Io
import Rogue
import Monsters
import Move

# doctor:
# A healing daemon that restors hit points after rest
def doctor() -> None:
    lv = Player.player.stats.level
    ohp = Player.player.stats.hitPoints
    Player.quiet += 1

    if lv < 8:
        if Player.quiet > 20 - lv * 2:
            Player.player.stats.hitPoints += 1
    else:
        if Player.quiet >= 3:
            Player.player.stats.hitPoints += Global.rnd(lv - 7) + 1

    if Player.ｗasWornRingOnHand("Left", Rings.RingOf.Regeneration):
        Player.player.stats.hitPoints += 1
    if Player.ｗasWornRingOnHand("Right", Rings.RingOf.Regeneration):
        Player.player.stats.hitPoints += 1

    if ohp != Player.player.stats.hitPoints:
        if Player.player.stats.hitPoints > Player.maxHp:
            Player.player.stats.hitPoints = Player.maxHp
        Player.quiet = 0

# Swander:
# Called when it is time to start rolling for wandering monsters
def swander() -> None:
    Global.daemonManager.append(Daemon(rollwand), DaemonExecuteTiming.Before)

# rollwand:
# Called to roll to see if a wandering monster starts up
between:int = 0
def rollwand() -> None:
    global between

    between += 1
    if between >= 4:
    	if Common.roll(1, 6) == 4:
            Monsters.wanderer()
            Global.daemonManager.kill(rollwand)
            Global.daemonManager.append(Fuse(swander, Global.WanderTime), executeTiming=DaemonExecuteTiming.Before)
    	between = 0

# unconfuse:
# Release the poor player from his confusion
def unconfuse():
    Player.player.flags.isHuh = False
    Io.msg("You feel less confused now")

# unsee:
# He lost his see invisible power
def unsee() -> None:
    Player.player.flags.canSee = False

# sight:
# He gets his sight back
def sight() -> None:
    if Player.player.flags.isBlind:
        Global.daemonManager.kill(sight)
        Player.player.flags.isBlind = False
        Move.light(Player.player.position)
        Io.msg("The veil of darkness lifts")

# nohaste:
# End the hasting
def nohaste() -> None:
    Player.player.flags.isHaste = False
    Io.msg("You feel yourself slowing down.")

# stomach
# digest the hero's food
def stomach():
    if Player.foodLeft <= 0:
        # the hero is fainting
        if Global.noCommand != 0 or Global.rnd(100) > 20:
            return
        Global.noCommand = Global.rnd(8) + 4
        Io.addMsg("You feel too weak from lack of food.  ")
        Io.msg("You faint")
        Player.running = False
        Global.count = 0
        Player.hungryState = 3
    else:
        oldFood = Player.foodLeft
        Player.foodLeft -= Rings.ringEat("Left") + Rings.ringEat("Right") + 1 - Global.hasAmulet

        if Player.foodLeft < Global.MoreTime and  oldFood >= Global.MoreTime:
            Io.msg("You are starting to feel weak")
            Player.hungryState = 2
        elif Player.foodLeft < 2 * Global.MoreTime and oldFood >= 2 * Global.MoreTime:
            Io.msg("Getting hungry")
            Player.hungryState = 1

