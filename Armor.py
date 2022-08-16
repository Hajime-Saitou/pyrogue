import Global
from Rogue import DaemonExecuteTiming
import Player
import Things
import Io
import Pack

# Armor types
class ArmorOf(object):
    Leather = 0
    RingMail = 1
    StuddedLeather = 2
    ScaleMail = 3
    ChainMail = 4
    SplintMail = 5
    BandedMail = 6
    PlateMail = 7

class Armor(object):
    def __init__(self):
        self.itemList = []
     
    def append(self, name:str, armorClass:int, chance:int, worth:int):
        self.itemList.append({ "Name": name, "ArmorClass": armorClass, "Chance": chance, "Worth": worth })

    def __getitem__(self, index):
        return None if index < 0 or index >= len(self.itemList) else self.itemList[index]

    def length(self):
        return len(self.itemList)

# wear:
# The player wants to wear something, so let him/her put it on.
def wear() -> None:
    if Player.curArmor is not None:
        Io.addMsg("You are already wearing some. You'll have to take it off first")
        Io.endMsg()
        after = False
        return

    item = Pack.getItem("wear", ord(Global.Armor))
    if item is None:
        return

    if item.type != Global.Armor:
        Io.msg("You can't wear that.")
        return

    wasteTime()
    Io.msg(f"You are now wearing {Global.armors.itemList[item.which]['Name']}.")
    Player.curArmor = item
    item.flags |= Global.Flags.IsKnow

# takeOff:
# Get the armor off of the players back
def takeOff() -> None:
    if Player.curArmor is None:
        Io.msg("You aren't wearing any armor")
        return

    curArmor = Player.curArmor          # copy variable reference value for Pack.packChar
    if not Things.dropCheck(Player.curArmor):
        return

    Io.addMsg("You used to be ")
    Io.msg(f"wearing {Pack.packChar(curArmor)}) {Things.invName(curArmor, True)}")

# wasteTime:
# Do nothing but let other things happen
def wasteTime() -> None:
    Global.daemonManager.do(DaemonExecuteTiming.Before)
    Global.daemonManager.do(DaemonExecuteTiming.After)
