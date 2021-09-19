from Rogue import Coordinate, Flags

# Structure for a thing that the rogue can carry
class CarryObject(object):
    def __init__(self):
        self.name:str = ""
        self.type:str = None                # What kind of object it is
        self.position:Coordinate = None     # Where it lives on the screen
        self.text:str = ""                  # What it says if you read it
        self.launch = None                  # What you need to launch it
        self.damage:str = "0d0"             # Damage if used like sword
        self.hurlDamage:str = "0d0"         # Damage if thrown
        self.count:int = 1                  # Count for plural objects
        self.which:int = 0                  # Which object of a type it is
        self.hitPlus:int = 0                # Plusses to hit
        self.damagePlus:int = 0             # Plusses to damage
        self.armorClass:int = 0             # Armor class
        self.flags = Flags([ "isKnow" ])                  # Information about objects
        self.group:int = 0                  # Group number for this object
