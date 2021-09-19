# All the fighting gets done here
import Global
import Monsters
import Chase
import Player
import Io
import Common
import Rooms
import Move
import Weapon
import Rings
import Sticks
import Things
import Rip
from Rogue import CarryObject
from enum import IntEnum
import Fight

# Save against things
class SaveAgainstThings(IntEnum):
    Poison = 0,             # VS_POISON 00
    Paralyzation = 0,       # VS_PARALYZATION 00
    Death = 0,              # VS_DEATH 00
    Petrification = 1,      # VS_PETRIFICATION 01
    Breath = 2,             # VS_BREATH 02
    Magic = 3,              # VS_MAGIC  03

eLevels = [
    10,20,40,80, 160, 320, 640,1280,2560,5120,10240,20480,
    40920, 81920, 163840, 327680, 655360, 1310720, 2621440, 0
]

# fight
# The player attacks the monster.
def fight(newPosition, monsterType, weapon, thrown):
    did_hit = True

    # Find the monster we want to fight
    monster = Monsters.findMonster(newPosition)
    if monster == None:
        Global.logger.debug(f"Fight what @ {newPosition}")

    # Since we are fighting, things are not quiet so no healing takes place.
    Player.quiet = 0
    Chase.runTo(newPosition, Player.player.position)

    # Let him know it was really a mimic (if it was one).
    if monster.type == "M" and monster.disguise != "M" and not Player.player.flags.isBlind:
        Io.msg("Wait! That's a mimic!")
        monster.disguise = "M"
        did_hit = thrown

    if did_hit:
        did_hit = False
        if Player.player.flags.isBlind:
            monsterName = "it"
        else:
            monsterName = Monsters.getMonsterName(monsterType)

        if roll_em(Player.player, monster, weapon, thrown):
            did_hit = True
            if thrown:
                thunk(weapon, monsterName)
            else:
                hit(None, monsterName)

            if Player.player.flags.canHuh:
                Io.msg("Your hands stop glowing red")
                Io.msg(f"The {monsterName} appears confused.")
                monster.flags.isHuh = True
                Player.player.flags.isHuh = False

            if (monster.stats.hitPoints <= 0):
                killed(monster, True)
        else:
            if thrown:
                bounce(weapon, monsterName)
            else:
                miss(None, monsterName)

    count = 0

    return did_hit

# hit:
# Print a message to indicate a succesful hit
def hit(er, ee):
    Io.addMsg(printName(er, True))
    s = [
        " scored an excellent hit on ",
        " hit ",
        f" {'have' if er == None else 'has'} injured ",
        " swing{0} and hit{0} ".format('s' if er == None else '')
    ]
    Io.addMsg(s[Global.rnd(len(s))])
    Io.addMsg(printName(ee, False))
    Io.endMsg()

# miss:
# Print a message to indicate a poor swing
def miss(er, ee):
    Io.addMsg(printName(er, True))
    s = [
        " miss " if er == None else " misses ",
        " swing and miss " if er == None else " swings and misses ",
        " barely miss " if er == None else " barely misses ",
        " don't hit " if er == None else " doesn't hit ",
    ]
    Io.addMsg(s[Global.rnd(len(s))])
    Io.addMsg(printName(ee, False))
    Io.endMsg()

# printName:
# The print name of a combatant
def printName(who, toUpper):
    tbuf = ""

    if who == None:
        tbuf = "you"
    elif Player.player.flags.isBlind:
        tbuf = "it"
    else:
        tbuf = f"the {who}"

    return tbuf.upper() if toUpper else tbuf

# thunk:
# A missile hits a monster
def thunk(weapon, monsterName):
    if weapon.type == Global.types.Weapon:
        weaponName = Global.weapons.itemList[weapon.which]["Name"]
        Io.msg(f"The {weaponName} hits the {monsterName}.")
    else:
        Io.msg("You hit the {monsterName}.")

# bounce:
# A missile misses a monster
def bounce(weapon, monsterName):
    if weapon.type == Global.types.Weapon:
        weaponName = Global.weapons.itemList[weapon.which]["Name"]
        Io.msg(f"The {weaponName} misses the {monsterName}.")
    else:
        Io.msg(f"You missed the {monsterName}.")

# killed:
# Called to put a monster to death
def killed(monster, printMessage:bool):
    if printMessage:
        if Player.player.flags.isBlind:
            monsterName = "it"
        else:
            monsterName = f"the {Monsters.getMonsterName(monster.type)}"
        Io.msg(f"You have defeated {monsterName}.")

    Player.player.stats.experience += monster.stats.experience

    # Do adjustments if he went up a level
    checkLevel()
    # If the monster was a violet fungi, un-hold him
    if monster.type == "F":
        Player.player.flags.isHeld = False
        Global.fungHit = 0
        monster.stats.damage = f"0d0"
    elif monster.type == "L":
        room = Rooms.roomIn(monster.position)
        if room:
            if room.goldValue or Weapon.fallpos(monster.position, room.goldValue, False):
                room.goldValue += Common.CalcGoldValue(Global.level)
                if save(Fight.SaveAgainstThings.Magic):
                    for _ in range(4):
                        room.goldValue += Common.CalcGoldValue(Global.level)

                Global.stdscr.addch(room.goldPosition.y, room.goldPosition.x, Global.Gold)

                if not room.flags.isDark:
                    Move.light(Player.player.position)
                    Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)

    # Empty the monsters pack
    for item in monster.pack:
        Weapon.fall(item, False)
        pass
    
    monster.pack.clear()

    # Get rid of the monster.
    remove(monster)

# checkLevel:
# Check to see if the guy has gone up a level.
def checkLevel():
    global eLevels

    for newLevel, eLevel in enumerate(eLevels):
        if Player.player.stats.experience < eLevel:
            break
    else:
        return

    newLevel += 1
    if newLevel > Player.player.stats.level:
        add = Common.roll(newLevel - Player.player.stats.level, 10)
        Player.maxHp = add
        Player.player.stats.hitPoints += add
        if Player.player.stats.hitPoints > Player.maxHp:
            Player.player.stats.hitPoints = Player.maxHp

        Io.msg("")
        Io.msg(f"Welcome to level {newLevel}!")

    Player.player.stats.level = newLevel

# raiseLevel:
# The guy just magically went up a level.
def raiseLevel():
    global eLevels
    Player.player.stats.experience = eLevels[Player.player.stats.level - 1] + 1
    checkLevel()

# remove:
# remove a monster from the screen
def remove(monster):
    Global.monsterWindow.addch(monster.position.y, monster.position.x, " ")
    Global.playerWindow.addch(monster.position.y, monster.position.x, monster.oldCh)

    if monster in Global.levelMonsterList:
        Global.levelMonsterList.remove(monster)

# swing:
# returns true if the swing hits
def swing(at_lvl, op_arm, wplus):
    res = Global.rnd(20) + 1
    need = (21 - at_lvl) - op_arm
    results = (res + wplus) >= need
    Global.logger.debug(f"swing: {results}, {res}, {wplus}, {need}")
    return results

# strPlus:
# compute bonus/penalties for strength on the "to hit" roll
def strPlus(str):
    if str.strength == 18:
        if str.addStrength == 100:
            return 3
        if str.addStrength > 50:
            return 2

    if str.strength >= 17:
        return 1

    if str.strength > 6:
        return 0

    return str.strength - 7

# addDamage:
# compute additional damage done for exceptionally high or low strength
def addDamage(str):
    if str.strength == 18:
        if str.addStrength == 100:
            return 6
        if str.addStrength > 90:
            return 5
        if str.addStrength > 75:
            return 4
        if str.addStrength != 0:
            return 3

        return 2

    if str.strength > 15:
        return 1

    if str.strength > 6:
        return 0

    return str.strength - 7

# attack:
# The monster attacks the player
def attack(monster):
    # Since this is an attack, stop running and any healing that was going on at the time.
    Player.running = False
    Player.quiet = 0

    if monster.type == "M" and not Player.player.flags.isBlind:
        monster.disguise = "M"

    if Player.player.flags.isBlind:
        monsterName = "it"
    else:
        monsterName = Monsters.getMonsterName(monster.type)

    if roll_em(monster, Player.player, None, False):
        if monster.type != "E":
            hit(monsterName, False)
        if Player.player.stats.hitPoints <= 0:
            Rip.death(monster.type)         # Bye bye life ...
        if not monster.flags.isCanc:
            if monster.type == "R":
                # If a rust monster hits, you lose armor
                if Player.curArmor != None and Player.curArmor.armorCalss < 9:
                    Io.msg("Your armor appears to be weaker now. Oh my!")
                    Player.curArmor.armorCalss += 1
            elif monster.type == "E":
                # The gaze of the floating eye hypnotizes you
                if not Player.player.flags.isBlind:
                    if not Global.noCommand:
                        Io.addMsg("You are transfixed")
                        Io.addMsg(" by the gaze of the floating eye.")
                        Io.endMsg()
                    Global.noCommand += Global.rnd(2) + 2
            elif monster.type == "A":
                # Ants have poisonous bites
                if not save(Fight.SaveAgainstThings.Poison):
                    if not Player.Player.ｗasWornRing(Rings.RingOf.SustainStrength):
                        Player.changeStrength(-1)
                        Io.msg("You feel a sting in your arm and now feel weaker")
                    else:
                        Io.msg("A sting momentarily weakens you")
            elif monster.type == "W":
                # Wraiths might drain energy levels
                if Global.rnd(100) < 15:
                    if Player.player.stats.experience == 0:
                        Rip.death('W')          #  All levels gone

                    Io.msg("You suddenly feel weaker.")
                    Player.player.stats.level -= 1
                    if Player.player.stats.level == 0:
                        Player.player.stats.experience = 0
                        Player.player.stats.level = 1
                    else:
                        global eLevels
                        Player.player.stats.experience = eLevels[Player.player.stats.level - 1] + 1

                    fewer = Common.roll(1, 10)
                    Player.player.stats.hitPoints -= fewer
                    if Player.player.stats.hitPoints < 1:
                        Player.player.stats.hitPoints = 1

                    Player.maxHp -= fewer
                    if Player.maxHp < 1:
                        Rip.death('W')
            elif monster.type == "F":
                # Violet fungi stops the poor guy from moving
                Player.player.flags.isHeld = True
                Global.fungHit += 1
                monster.stats.damage = f"{Global.fungHitd1}"
            elif monster.type == "L":
                # Leperachaun steals some gold
                lastPurse = Player.purse
                Player.purse -= Common.CalcGoldValue(Global.level)

                if not save(Fight.SaveAgainstThings.Magic):
                    for _ in range(4):
                        Player.purse -= Common.CalcGoldValue(Global.level)

                if Player.purse < 0:
                    Player.purse = 0

                if Player.purse != lastPurse:
                    Io.msg("Your purse feels lighter")

                remove(monster)
            elif monster.type == "N":
                # Nymph's steal a magic item, look through the pack and pick out one we like.
                stolenItem:CarryObject = None
                nofObject = 0 
                for item in Player.player.pack:
                    if item not in [ Player.curArmor, Player.curWeapon ] and Things.isMagicItem(stolenItem) and Global.rnd(nofObject) == 0:
                        stolenItem = item

                if stolenItem:
                    remove(monster)
                    if stolenItem.count > 1 and stolenItem.group == 0:
                        stolenItem.count -= 1
                        oc = stolenItem.count
                        stolenItem.count = 1
                        Io.msg(f"She stole {Things.invName(stolenItem, True)}!")
                        stolenItem.count = oc
                    else:
                        Io.msg(f"She stole {Things.invName(stolenItem, True)}!")
                        Player.pack.remove(stolenItem)
    elif monster.type != "E":
        if monster.type == "F":
            Player.player.stats.hitPoints -= Global.fungHit
            if Player.player.stats.hitPoints <= 0:
                Rip.death(monster.type)         # Bye bye life ...

        miss(monsterName, None)

    # Check to see if this is a regenerating monster and let it heal if it is.
    if monster.flags.isRegen and Global.rnd(100) < 33:
        monster.stats.hitPoints += 1

    if Global.fightFlush:
        # raw()           # flush typeahead
        # noraw()
        pass

    Global.count = 0
    Io.status()


# roll_em:
# Roll several attacks
def roll_em(attacker, defender, weapon, hurl):
    did_hit = False

    if weapon == None:
        damageString = attacker.stats.damage
    elif hurl:
        if weapon.flags.isMisl and Global.cur_weapon != None and\
                Global.cur_weapon.which == weapon.launch:
            damageString = weapon.hurlDamage
            prop_hplus = Global.cur_weapon.hitPlus
            prop_dplus = Global.cur_weapon.damagePlus
        else:
            damageString = weapon.flags.isMisl if weapon.damage else weapon.hurlDamage
    else:
        damageString = weapon.damage

    # # Drain a staff of striking
    if weapon != None and weapon.type == Global.Stick and weapon.which == Sticks.StickOf.Striking and weapon.charges == 0:
        weapon.damage = "0d0"
        weapon.hplus = 0
        weapon.dplus = 0
        damageString = weapon.damage

    rolls = Common.Rolls(damageString)
    Global.logger.debug(f"damageString: {damageString}")
    Global.logger.debug(f"rolls: {rolls.rolls}")

    for roll in rolls.rolls:
        hplus = weapon.hitPlus if weapon != None else 0
        dplus = weapon.damagePlus if weapon != None else 0

        if weapon == Player.curWeapon:
            if Player.ｗasWornRingOnHand("Left", Rings.RingOf.IncreaseDamage):
                dplus += Player.curRings["Left"].armorClass
            elif Player.ｗasWornRingOnHand("Left", Rings.RingOf.Dexterity):
                hplus += Player.curRings["Left"].armorClass

            if Player.ｗasWornRingOnHand("Right", Rings.RingOf.IncreaseDamage):
                dplus += Player.curRings["Right"].armorClass
            elif Player.ｗasWornRingOnHand("Right", Rings.RingOf.Dexterity):
                hplus += Player.curRings["Right"].armorClass

        if defender.stats == Player.player.stats:
            if Player.curArmor != None:
                defArmorClass = Player.curArmor.armorClass
            else:
                defArmorClass = defender.stats.armorClass
            if Player.ｗasWornRingOnHand("Left", Rings.RingOf.Protection):
                defArmorClass -= Player.curRings["Left"].armorClass
            if Player.ｗasWornRingOnHand("Right", Rings.RingOf.Protection):
                defArmorClass -= Player.curRings["Right"].armorClass
        else:
            defArmorClass = defender.stats.armorClass

        ndice, nsides = int(roll[0]), int(roll[1])
        if swing(attacker.stats.level, defArmorClass, hplus + strPlus(attacker.stats.strength)):
            proll = Common.roll(ndice, nsides)
            if (ndice + nsides) > 0 and proll < 1:
                Io.msg(f"Damage for {ndice}d{nsides} came out {proll}.")
            damage = dplus + proll + addDamage(attacker.stats.strength)
            defender.stats.hitPoints -= max(0, damage)
            did_hit = True

    return did_hit

# saveThrow:
# See if a creature save against something
def saveThrow(self, which:SaveAgainstThings) -> bool:
    need = 14 + which - self.stats.level / 2
    return Common.roll(1, 20) >= need

# save:
# See if he saves against various nasty things
def save(which:int) -> bool:
    return saveThrow(which, Player.player)
