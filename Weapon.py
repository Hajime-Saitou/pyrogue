from enum import IntEnum
from Rogue import Coordinate, CarryObject
import Player
import Global
import Things
import Pack
import Io
import Fight
import Chase
import copy
import Rooms
import Move

# Weapon types
class WeaponOf(IntEnum):
    Mace = 0
    LongSword = 1
    ShortBow = 2
    Arrow = 3
    Dagger = 4
    Rock = 5
    TwoHandedSword = 6
    Sling = 7
    Dart = 8
    CrossBow = 9
    CrossBowBolt = 10
    Spear = 11

class WeaponLaunchTypes(IntEnum):
    CanNotLaunch = 0
    Bow = 1
    Sling = 2
    CrossBow = 3

class Weapon(object):
    def __init__(self):
        self.itemList:list = []

    def append(self, name:str, damage:str, hurlDamage:str, launchType:WeaponLaunchTypes, flags:int, worth:int):
        self.itemList.append({ "Name": name, "Damage": damage, "HurlDamage": hurlDamage, "Launch": launchType, "Flags": flags, "Worth": worth })

    def __getitem__(self, index):
        return None if index < 0 or index >= len(self.itemList) else self.itemList[index]

    def length(self):
        return len(self.itemList)
    
# wield:
# Pull out a certain weapon
def wield() -> None:
    oweapon = Player.curWeapon
    if not Things.dropCheck(Player.curWeapon):
        Player.curWeapon = oweapon
        return

    curWeapon = oweapon
    item = Pack.getItem("wield", ord(Global.Weapon))
    if item == None:
        Global.after = False
        return

    if item.type == Global.Armor:
        Io.msg("You can't wield armor")
        Global.after = False
        return

    if Player.isEquipment(item):
        Global.after = False
        return

    Io.addMsg(f"You are now wielding {Things.invName(item, True)}")
    Player.curWeapon = item

# missile:
# Fire a missile in a given direction
def missile(delta:Coordinate):
    # Get which thing we are hurling
    item = Pack.getItem("throw", Global.Weapon)
    if item is None:
        return

    if not Things.dropCheck(item) or Player.isEquipment(item):
        return

    # Get rid of the thing.  If it is a non-multiple item object, or
    # if it is the last thing, just drop it.  Otherwise, create a new
    # item with a count of one.
    if item.count < 2:
        Player.pack.remove(item)
    else:
        item.count -= 1
        # if item.group == 0:
        #     inpack--;

        newItem = copy.deepcopy(item)
        newItem.count = 1
        item = newItem

    doMotion(item, delta)

    # AHA! Here it has hit something.  If it is a wall or a door,
    # or if it misses (combat) the mosnter, put it on the floor
    ch = str(Global.monsterWindow.inch(item.posiotn.y, item.position.x))
    if not ch.isupper() or not hitMonster(item.position, item): 
        fall(item, True)

    Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)

# doMotion:
# do the actual motion on the screen done by an object traveling across the room
def doMotion(obj:CarryObject, delta:Coordinate):
    # Come fly with us ...
    obj.position = copy.deepcopy(Player.player.position)

    while True:
        # Erase the old one
        ch = str(Global.playerWindow.inch(obj.position.y, obj.position.x))
        if obj != Player.player.position and Chase.cansee(obj.position) and ch != " ":
            Global.playerWindow.addch(obj.position.y, obj.position.x, Move.show(obj.position))

        # Get the new position
        obj.position += delta
        ch = Io.winAt(obj.position)
        if Chase.stepOk(ch) and ch != Global.Door:
            # It hasn't hit anything yet, so display it If it alright.
            if Chase.cansee(obj.position) and Global.playerWindow.inch(obj.position.y, obj.position.x) != " ":
                Global.playerWindow.addch(obj.position.y, obj.position.x, obj.type)
                Global.playerWindow.refresh()
            continue

        break

# hitMonster:
# Does the missile hit the monster
def hitMonster(pos, obj):
    mp = pos.clone()
    return Fight.fight(mp, Io.winAt(mp), obj, True)

# fall:
# Drop an item someplace around here.
def fall(item, printMessage:bool) -> None:
    fallPos = Coordinate(0, 0)
    if fallpos(item.position, fallPos, True):
        Global.stdscr.addch(fallPos.y, fallPos.x, item.type)
        item.position = fallPos

        room = Rooms.roomIn(Player.player.position)
        if room and not room.flags.isDark:
            Move.light(Player.player.position)
            Global.playerWindow.addch(Player.player.position.y, Player.player.position.x, Global.Player)

        Global.levelObjectList.append(item)
        return

    if printMessage:
        Io.msg(f"Your {item.name} vanishes as it hits the ground.")

# fallPos:
# pick a random position around the give (y, x) coordinates
def fallpos(pos:Coordinate, newPos:Coordinate, passages:bool) -> bool:
    count = 0

    for y in range(pos.y - 1, pos.y + 1 + 1):
        for x in range(pos.x - 1, pos.x + 1 + 1):
            # check to make certain the spot is empty, if it is,
            # put the object there, set it in the level list
            # and re-draw the room if he can see it
            coord = Coordinate(x, y)
            if coord == Player.player.position:
                continue

            ch = Io.winAt(coord)
            count += 1
            if (ch == Global.Floor or (passages and ch == Global.Global.Passage)) and Global.rnd(count) == 0:
                newPos = coord.clone()

    return count != 0
