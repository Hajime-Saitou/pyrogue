import Global
from Rogue import Coordinate, Flags

class TrapOf(object):
    TrapDoor = ">"
    ArrowTrap = "{"
    SleepingGasTrap = "$"
    BearTrap = "}"
    TeleportTrap = "~"
    PoisonDartTrap = "`"

# Array of all traps on this level
class TrapBase(object):
    type:str = "^"
    name:str = "trap"

    def __init__(self, position:Coordinate) -> None:
        self.position:Coordinate = position
        self.flags = Flags([ "isFound" ])

    @classmethod
    def __str__(cls):
        return cls.type

class TrapDoor(TrapBase):
    type:str = TrapOf.TrapDoor
    name:str = "trapdoor"

    def __init__(self, position:Coordinate) -> None:
        super().__init__(position)

class ArrowTrap(TrapBase):
    type:str = TrapOf.ArrowTrap
    name:str = "arrow trap"

    def __init__(self, position:Coordinate) -> None:
        super().__init__(position)

class SleepingGasTrap(TrapBase):
    type:str = "$"
    name:str = "sleeping gas trap"

    def __init__(self, position:Coordinate) -> None:
        super().__init__(position)

class BearTrap(TrapBase):
    type:str = "}"
    name:str = "beartrap"

    def __init__(self, position:Coordinate) -> None:
        super().__init__(position)

class TeleportTrap(TrapBase):
    type:str = "~"
    name:str = "teleport trap"

    def __init__(self, position:Coordinate) -> None:
        super().__init__(position)

class PoisonDartTrap(TrapBase):
    type:str = "`"
    name:str = "poison dart trap"

    def __init__(self, position:Coordinate) -> None:
        super().__init__(position)

class TrapFactory(object):
    traps:list = [
        TrapDoor,
        ArrowTrap,
        SleepingGasTrap,
        BearTrap,
        TeleportTrap,
        PoisonDartTrap,
    ]

    @classmethod
    def createRandom(cls, position:Coordinate) -> TrapBase:
        return cls.traps[Global.rnd(len(cls.traps))](position)

# trapAt:
# find the trap at (y,x) on screen.
def trapAt(coord:Coordinate) -> TrapBase:
    for trap in Global.traps:
        if trap.position == coord:
            return trap
    else:
        Global.logger.debug(f"Trap at {coord} not in array.")
        return None

# secretTrap:
# Figure out what a secret door looks like.
def secretTrap(coord):
    return Global.Trap if trapAt(coord).flags.isFound else Global.Floor
