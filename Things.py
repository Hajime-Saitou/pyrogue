from enum import IntEnum
import Pack
import Global
import Common
import Rooms
import Traps
import Player
from Rings import RingOf
import Move
import Scrolls
import Sticks
import Rings
import Potions
import Armor
import Io
from Rogue import CarryObject
import Daemons
import copy

class ThingTypes(IntEnum):
    Potion = 0
    Scroll = 1
    Food = 2
    Weapon = 3
    Armor = 4
    Ring = 5
    Stick = 6

# Stuff about magic items
class MagicItems(object):
    def __init__(self, name):
        self.name = name
        self.itemList = []
        self.tentativeName = []
        self.know = []
        self.guessName = []

    def append(self, name:str, prob:int, worth:int):
        nItems = len(self.itemList)
        if nItems > 0:
            self.itemList[nItems - 1]["prob"] += prob
        self.itemList.append({ "name": name, "prob": prob, "worth": worth })

    def getItemName(self, index):
        if self.know[index]:
            itemName = self.itemList[index]["name"]
        elif self.guessName[index] != "":
            itemName = self.guessName[index]
        else:
            itemName = self.tentativeName[index]

        return itemName

    def badCheck(self):
        if not self.itemList:
            return

        if self.itemList[-1]["prob"] == 100:
            return

        Global.logger.debug(f"\nBad percentages for {self.name}:\n")
        Global.logger.debug(self.itemList)

# isMagicItem:
# Returns true if an object radiates magic
def isMagicItem(item:CarryObject) -> bool:
    if item.type == Global.Armor:
        return item.armorClass != Global.armors[item.which]["ArmorClass"]
    elif item.type == Global.Weapon:
        return item.hitPlus != 0 or item.damagePlus != 0
    elif item.type in [ Global.Potion, Global.Scroll, Global.Stick, Global.Ring, Global.Amulet ]:
        return True
    else:
        return False

# putThings:
# put potions and scrolls on this level
def putThings(maxThings=9):
    # Throw away stuff left on the previous level (if anything)
    Global.levelObjectList.clear()

    # Once you have found the amulet, the only way to get new stuff is
    # go down into the dungeon.
    if Global.hasAmulet and Global.level < Global.maxLevel:
        return

    # Do MAXOBJ attempts to put things on a level
    for _ in range(maxThings):
        if Global.rnd(100) < 35:
            # Pick a new object and link it in the list
            item = newThing()
            Global.levelObjectList.append(item)

            # Put it somewhere
            room = Rooms.rndRoom()
            item.position = room.rndPosition()
            Global.stdscr.addch(item.position.y, item.position.x, item.type)

    # If he is really deep in the dungeon and he hasn't found the
    # amulet yet, put it somewhere on the ground
    if Global.level > 25 and not Global.hasAmulet:
        item = CarryObject()
        item.type = Global.Amulet
        Global.levelObjectList.append(item)

        # Put it somewhere
        room = Rooms.rndRoom()
        item.position = room.rndPosition()
        Global.stdscr.addch(item.position.y, item.position.x, item.type)

# putStair:
# Place the staircase down.
def putStair():
    room = Rooms.rndRoom()
    Global.stairPosition = room.rndPosition()
    Global.stdscr.addch(Global.stairPosition.y, Global.stairPosition.x, Global.Stairs)

# putTraps:
# Place the traps
def putTraps(maxTraps=10):
    if Global.rnd(10) < Global.level:
        ntraps = Global.rnd(Global.level // 4 + 1) + 1
        if ntraps > maxTraps:
            ntraps = maxTraps

        for i in range(ntraps):
            trap = Traps.TrapFactory.createRandom(Rooms.rndRoom().rndPosition())
            Global.traps.append(trap)
            Global.stdscr.addch(trap.position.y, trap.position.x, Global.Trap)

# putHero:
# player here come.
def putHero():
    room = Rooms.rndRoom()
    Player.player.position = room.rndPosition()
    Player.player.oldCh = Global.playerWindow.inch(Player.player.position.y, Player.player.position.x)
    Move.light(Player.player.position)
    Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)

# newThing:
def newThing():
    item = CarryObject()

    # Decide what kind of object it will be
    # If we haven't had food for a while, let it be food.
    kindOfItem = ThingTypes.Food if Player.noFood > 3 else pickOne(Global.things)
    Global.logger.debug(kindOfItem)
    if kindOfItem == ThingTypes.Potion:
        item.type = Global.Potion
        item.which = pickOne(Global.potionMagic)
    elif kindOfItem == ThingTypes.Scroll:
        item.type = Global.Scroll
        item.which = pickOne(Global.scrollMagic)
    elif kindOfItem == ThingTypes.Food:
        Player.noFood = 0
        item.type = Global.Food
        item.which = 0 if Global.rnd(100) > 10 else 1
    elif kindOfItem == ThingTypes.Weapon:
        item.type = Global.Weapon
        item.which = Global.rnd(Global.weapons.length())
        weapon = Global.weapons[item.which]
        Global.logger.debug(weapon)
        item.damage = weapon["Damage"]
        item.hurlDamage = weapon["HurlDamage"]
        item.launch = weapon["Launch"]

        if weapon["Flags"] & Global.Flags.IsMany:
            item.flags.isMany = True
        if weapon["Flags"] & Global.Flags.IsMisl:
            item.flags.isMisl = True

        if item.flags.isMany:
            item.count = Global.rnd(8) + 8
        else:
            item.count = 1

        r = Global.rnd(100)
        if r < 10:
            item.flags.isCursed = True
            item.hitPlus -= Global.rnd(3) + 1
        elif r < 15:
            item.hitPlus += Global.rnd(3) + 1
    elif kindOfItem == ThingTypes.Armor:
        item.type = Global.Armor
        for index in range(Global.armors.length()):
            r = Global.rnd(100)
            if r < Global.armors[index]["Chance"]:
                item.which = index
                item.armorClass = Global.armors[index]["ArmorClass"]
                break
        else:
            Global.logger.debug(f"Picked a bad armor")
            item.which = 0
            item.armorClass = Global.armors[0]["ArmorClass"]
        r = Global.rnd(100)
        if r < 20:
            item.flags.isCursed = True
            item.armorClass += Global.rnd(3) + 1
        elif r < 28:
            item.armorClass -= Global.rnd(3) + 1
    elif kindOfItem == ThingTypes.Ring:
        item.type = Global.Ring
        item.which = pickOne(Global.ringMagic)
        if item.which in [ RingOf.AddStrength, RingOf.Protection, RingOf.Dexterity, RingOf.IncreaseDamage ]:
            if Global.rnd(3) == 0:
                item.armorClass = -1
                item.flags.isCursed = True
        elif item.which in [ RingOf.AggravateMonster, RingOf.Teleportation ]:
            item.flags.isCursed = True
    elif kindOfItem == ThingTypes.Stick:
        item.type = Global.Stick
        item.which = pickOne(Global.stickMagic)
        Sticks.fix(item)
    else:
        raise ValueError(f"Picked a bad kind of object: {kindOfItem}")

    Global.logger.debug(f"type: {item.type}")
    Global.logger.debug(f"which: {item.which}")
    return item

# pickOne:
# pick an item out of a list of nitems possible magic items
def pickOne(magicItems):
    while True:
        for index, item in enumerate(magicItems.itemList):
            if Global.rnd(100) < item["prob"]:
                Global.logger.debug(f"pickOne: {index}")
                return index

# invName:
# return the name of something as it would appear in an inventory.
def invName(item, drop):
    Global.logger.debug(f"invName")
    Global.logger.debug(f"type: {item.type}")
    Global.logger.debug(f"which: {item.which}")
    type = item.type
    itemName = ""
    displayName = ""
    if type == Global.Scroll:
        if item.count == 1:
            displayName = "A scroll "
        else:
            displayName = f"{item.count} scrolls "

        itemName = Global.scrollMagic.getItemName(item.which)

        if Global.scrollMagic.know[item.which]:
            displayName += "of " + itemName
        elif Global.scrollMagic.guessName[item.which] != "":
            displayName += "called " + itemName
        else:
            displayName += "titled " + itemName

    elif type == Global.Potion:
        if item.count == 1:
            displayName = "A potion "
        else:
            displayName = f"{item.count} potions "

        itemName = Global.potionMagic.getItemName(item.which)
        vowel = Common.vowelStr(itemName)
        if Global.potionMagic.know[item.which]:
            displayName += "of " + itemName
        elif Global.potionMagic.guessName[item.which] != "":
            displayName += "called " + itemName
        else:
            if item.count == 1:
                displayName = f"A{vowel} {itemName} potion"
            else:
                displayName = f"{item.count} {itemName} potions"
    elif type == Global.Food:
        if item.which == 1:         # fruit
            if item.count == 1:
                vowel = Common.vowelStr(Player.fruitName)
                displayName = f"A{vowel} {Player.fruitName}"
            else:
                displayName = f"{item.count} {Player.fruitName}s"
        else:                       # food
            if item.count == 1:
                displayName = "Some food"
            else:
                displayName = f"{item.count} rations of food"
    elif type == Global.Weapon:
        if item.count > 1:
            displayName = f"{item.count} "
        else:
            displayName = "A "
        
        if item.flags & Global.Flags.IsKnow:
            displayName += f"{Common.num(item.hitPlus, item.damagePlus)} "
        
        displayName += Global.weapons.itemList[item.which]["Name"]
        if item.count > 1:
            displayName += "s"
    elif type == Global.Armor:
        if item.flags & Global.Flags.IsKnow:
            armorClass = Global.armors[item.which]["ArmorClass"] - item.armorClass
            displayName = f"{Common.num(armorClass, 0)} {itemName}"
        displayName += Global.armors.itemList[item.which]["Name"]
    elif type == Global.Amulet:
        displayName = "The Amulet of Yendor"
    elif type == Global.Stick:
        wsTypes = Sticks.wsTypes[item.which]
        wsMade = Sticks.wsMade[item.which]
        itemName = Global.stickMagic.getItemName(item.which)

        displayName = f"A {wSticks.wsTypes[item.which]} "
        if item.flags & Global.Flags.IsKnow:
            charge = Sticks.chargeStr(item)
            displayName += f"of {itemName} {charge}({Sticks.wsMade[item.which]})"
        elif Global.stickMagic.guessName[item.which] != "":
            displayName += f"called {itemName}({Sticks.wsMade[item.which]})"
        else:
            displayName = f"A {Sticks.wsMade[item.which]} {Sticks.wsTypes[item.which]}"
    elif type == Global.Ring:
        itemName = Global.ringMagic.itemList[item.which]["name"]
        stoneName = Global.ringMagic.tentativeName[item.which]
        if item.flags & Global.Flags.IsKnow:
            ringNum = Rings.ringNum(item)
            displayName = f"A {ringNum} ring of {itemName}({stoneName})"
        elif Global.ringMagic.guessName[item.which] != "":
            displayName = f"A ring called {itemName}({stoneName})"
        else:
            vowel = Common.vowelStr(stoneName)
            displayName = f"A{vowel} {stoneName} ring"
    else:
        displayName = f"Something bizarre {type}"

    if item == Player.curArmor:
        displayName += " (being worn)"
    if item == Player.curWeapon:
        displayName += " (weapon in hand)"
    if item == Player.curRings["Left"]:
        displayName += " (on left hand)"
    if item == Player.curRings["Right"]:
        displayName += " (on right hand)"

    firstCh = displayName[:1]
    if drop and firstCh.isupper():
        displayName = firstCh.lower() + displayName[1:]
    elif not drop and firstCh.islower():
        displayName = firstCh.upper() + displayName[1:]

    if not drop:
        displayName += "."

    return displayName

# money:
# Add to characters purse
def money():
    for room in Global.rooms:
        if not room.goldValue:
            continue

        if Player.player.position == room.goldPosition:
            if Global.notify:
                Io.msg(f"You found {room.goldValue} gold pieces.")

            Player.purse += room.goldValue
            room.goldValue = 0
            Global.stdscr.addch(room.goldPosition.y, room.goldPosition.x, Global.Floor)
            return

    Io.msg("That gold must have been counterfeit")

# dropCheck:
# Do special checks for dropping or unweilding|unwearing|unringing
def dropCheck(carryObject:CarryObject) -> bool:
    if carryObject is None:
        return True

    if carryObject not in [ Player.curArmor, Player.curWeapon, Player.curRings["Left"], Player.curRings["Right"] ]:
        return True

    if carryObject.flags & Global.Flags.IsCursed:
        Io.msg("You can't.  It appears to be cursed.")
        return False

    if carryObject == Player.curWeapon:
        Player.curWeapon = None
    elif carryObject == Player.curArmor:
        Armor.wasteTime()
        Player.curArmor = None
    elif carryObject in [ Player.curRings["Left"], Player.curRings["Right"] ]:
        if carryObject.which == RingOf.AddStrength:
            # saveMax = maxStats.s_str
            # Sticks.chargeStr(-carryObject.armorClass)
            # maxStats.s_str = saveMax
            pass
        elif carryObject.which == RingOf.SeeInvisible:
            Player.player.flags.canSee = False
            Global.daemonManager.kill(Daemons.unsee)
            Move.light(Player.player.position)
            Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)

        Player.curRings["Left" if carryObject == Player.curRings["Left"] else "Right"] = None

    return True

# drop:
# put something down
def drop() -> None:
    ch = chr(Global.stdscr.inch(Player.player.position.y, Player.player.position.x))
    if ch not in [ Global.Floor, Global.Passage ]:
        Io.msg("There is something there already")
        return

    item:CarryObject = Pack.getItem("drop", Global.InventryItemTypes.DisplayAll)
    if item == None:
        return 

    if not dropCheck(item):
        return

    # Take it out of the pack
    if item.count >= 2 and item.type != Global.Weapon:
        droppedItem = copy.deepcopy(item)
        droppedItem.count = 1
        item.count -= 1
    else:
        Player.pack.remove(item)
        droppedItem = item

    # Link it into the level object list
    Global.levelObjectList.append(item)
    Global.stdscr.addch(Player.player.position.y, Player.player.position.x, droppedItem.type)
    droppedItem.position = Player.player.position
    Io.msg(f"Dropped {invName(droppedItem, True)}")

# whatIs:
# What a certin object is
def whatIs() -> None:
    item = Pack.getItem("identify", Global.InventryItemTypes.DisplayAll)
    if item is None:
        return

    if item.which == Global.Scroll:
        Global.ringMagic.know.know[item.which] = True
        if Global.ringMagic.guessName[item.which]:
            Global.ringMagic.guessName = ""
    elif item.which == Global.Potion:
        Global.potionMagic.know[item.which] = True
        if Global.potionMagic.guessName[item.which]:
            Global.potionMagic.guessName[item.which] = ""
    elif item.which == Global.Stick:
        Global.stickMagic.know[item.which] = True
        item.flags.isKnow = True
        if Global.stickMagic.guessName[item.which]:
            Global.stickMagic.guessName[item.which] = ""
    elif item.which in [ Global.Weapon, Global.Armor ]:
        item.flags.isKnown = True
    elif item.which == Global.Ring:
        Global.ringMagic.know[item.which] = True
        item.flags.isKnown = True
        if Global.ringMagic.guessName[item.which]:
            Global.ringMagic.guessName[item.which] = ""

    Io.msg((item, False))
