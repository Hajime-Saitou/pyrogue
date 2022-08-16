from Rogue import CarryObject, KeyMap
import Things
import Global
import curses
import Io
import Common
import Player
import Rooms
import Scrolls

# inventory:
# list what is in the pack
def inventory(itemList:list, type:int) -> bool:
    typeCh = chr(type) if type not in [ Global.InventryItemTypes.Callable, Global.InventryItemTypes.DisplayAll ] else ""

    n_objs = 0
    invTemp = ""
    for index, item in enumerate(itemList):
        if type and type != item.type and\
                not(type == Global.InventryItemTypes.Callable and typeCh in [ Global.Scroll, Global.Potion, Global.Ring, Global.Stick ]):
            continue

        ch = chr(ord("a") + index)

	    # For the first thing in the inventory, just save the string
	    # in case there is only one.
        if n_objs == 0:
            invTemp = f"{ch}) {Things.invName(item, False)}"
        elif n_objs == 1:
            # If there is more than one, clear the screen, print the
            # saved message and fall through to ...
            if Global.slowInvent:
                Io.msg(invTemp)
            else:
                Global.helpWindow.clear()
                Global.helpWindow.addstr(invTemp + "\n")
        else:
            # Print the line for this object
            if Global.slowInvent:
                Io.msg(f"{ch}) {Things.invName(item, False)}")
            else:
                Global.helpWindow.addstr(f"{ch}) {Things.invName(item, False)}\n")
        n_objs += 1

    if n_objs == 0:
        Io.msg("You are empty handed." if type else "You don't have anything appropriate.")
        return False
    elif n_objs == 1:
        Io.msg(invTemp)
        return True

    if not Global.slowInvent:
        Global.helpWindow.addstr(Global.cursesLines - 1, 0, "--Press space to continue--")
        Global.helpWindow.refresh()
        Io.waitFor(" ")
        Global.playerWindow.clearok(True)
        Global.playerWindow.touchwin()

    return True

# pickyInventory:
# Allow player to inventory a single item
def pickyInventory(itemList):
    length = len(itemList)
    if length == 0:
        Io.msg("You aren't carrying anything")
        return

    if length == 1:
        Io.msg("a) %s", Things.invName(itemList[0], False))
        return

    Io.msg("Which item do you wish to inventory: ")
    mpos = 0
    mch = Io.readChar()
    if mch == KeyMap.Escape:
        Io.msg("")
        return

    for index in range(length):
        ch = chr(ord("a") + index)

        if ch == mch:
            Io.msg(f"{ch}) {Things.invName(itemList[index], False)}")
            return

    Io.msg(f"'{mch}' not in pack")
    rangeTo = chr(ord("a") + length - 1)
    Io.msg(f"Range is 'a' to '{rangeTo}'")

# pickUp:
# Add something to characters pack.
def pickUp(ch):
    if ch == Global.Gold:
        Things.money()
        return

    if ch not in [ Global.Armor, Global.Potion, Global.Food, Global.Weapon, Global.Scroll, Global.Amulet, Global.Ring, Global.Stick ]:
        return

    addPack(None, False)
    
# addPack:
# Pick up an object and add it to the pack.  If the argument is non-null
# use it as the linked_list pointer instead of gettting it off the ground.
def addPack(item, silent):
    fromFloor = False

    if item == None:
        fromFloor = True
        item = Common.findObject(Player.player.position)
        if item == None:
            return
    else:
        fromFloor = False

    # Link it into the pack.  Search the pack for a object of similar type
    # if there isn't one, stuff it at the beginning, if there is, look for one
    # that is exactly the same and just increment the count if there is.
    # it  that.  Food is always put at the beginning for ease of access, but
    # is not ordered so that you can't tell good food from bad.  First check
    # to see if there is something in thr same group and if there is then
    # increment the count.
    if item.group != 0:
        for playerItem in Player.pack:
            if item.group == playerItem.group:
                # Put it in the pack and notify the user
                playerItem.count += 1
                if fromFloor:
                    removeLevelObject(item)

                pickedUp(item, silent)
                return

    # Check if there is room
    if len(Player.pack) == Player.MaxPack - 1:
        Io.msg("You can't carry anything else.")
        return

    # Check for and deal with scare monster scrolls
    if item.type == Global.Scroll and item.which == Scrolls.ScrollOf.ScareMonster:
        if item.flags & Global.Flags.isFound:
            Io.msg("The scroll turns to dust as you pick it up.")
            removeLevelObject(item)
            return
        else:
            item.flags |= Global.Flags.isFound

    if fromFloor:
        removeLevelObject(item)

    # Search for an object of the same type
    exact = False
    searchItem = None
    for playerItem in Player.pack:
        if playerItem.type == item.type:
            searchItem = playerItem
            break

    if searchItem == None:
        # Put it at the end of the pack since it is a new type
        for playerItem in Player.pack:
            if item.type != Global.Food:
                searchItem = playerItem
                break
    else:
        # Search for an object which is exactly the same
        itemIndex = Player.pack.index(searchItem)
        for index, playerItem in enumerate(Player.pack):
            if index < itemIndex:
                continue
            if playerItem.which == item.which:
                exact = True
                searchItem = playerItem
                break
        else:
            searachItem = None

    if searchItem == None:
        # Didn't find an exact match, just stick it here
        Player.pack.append(item)
    else:
        # If we found an exact match.  If it is a potion, food, or a 
        # scroll, increase the count, otherwise put it with its clones.
        if exact and item.type in [ Global.Potion, Global.Scroll, Global.Food ]:
            searchItem.count += 1
            pickedUp(item, silent)
            return
        else:
            Player.pack.append(item)

    pickedUp(item, silent)

# pickedUp:
def pickedUp(item, silent):
    if item.type == Global.Amulet:
        Global.hasAmulet = True

    # Notify the user
    if Global.notify and not silent:
        removeLevelObject(item)
        Io.msg(f"You found {Things.invName(item, True)} (?)")

# removeLevelObject:
# Remove item from level objects
def removeLevelObject(item):
    if item in Global.levelObjectList:
        Global.levelObjectList.remove(item)
    Global.stdscr.addch(item.position.y, item.position.x,\
        Global.Floor if Rooms.roomIn(item.position) else Global.Passage)


# getItem:
# Pick something out of a pack for a purpose
def getItem(purpose, type:int) -> CarryObject:
    if Player.pack is None:
        Io.msg("You aren't carrying anything.")
        return None

    while True:
        Io.msg(f"Which object do you want to {purpose} what? (* for list): ")

        ch = Io.readChar()
        Io.msgPos = 0

        # Give the poor player a chance to abort the command
        if ch in [ KeyMap.Escape, KeyMap.Bell ]:
                Global.after = False
                Io.msg("")
                return None

        if ch == "*":
            Io.msgPos = 0
            if not inventory(Player.pack, type):
                Global.after = False
                return None

            continue

        och = ord("a")
        for item in Player.pack:
            if ch == chr(och):
                return item
            och += 1
        else:
            Io.msg(f"Please specify a letter between 'a' and '{chr(och - 1)}'")

# packChar:
# get a pack item's letter
def packChar(carryObject:CarryObject) -> str:
    if carryObject not in Player.pack:
        return "z"
    else:
        return chr(Player.pack.index(carryObject) + ord("a"))
