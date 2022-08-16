from Rogue import DaemonManager, RogueRandomizer
from enum import IntEnum, IntFlag

wasWizard:bool = True

# for debug
import logging
logging.basicConfig(filename=".\\data\\rogue.log",level=logging.DEBUG)
logger = logging.getLogger()

# score filename
scoreFilename = ".\\data\\score.dat"
scoreTable = None

# Constant value
MaxRooms:int = 9
LevelWhereAmuletExists:int = 25

# System Variables
cursesLines:int = 0
cursesColumns:int=0

# managers
randomizer = RogueRandomizer()
rnd = randomizer.next
daemonManager:DaemonManager = DaemonManager()

# Things that appear on the screens
Passage = "#"
Door = "+"
Floor = "."
Player = "@"
Trap = "^"
SecretDoor = "&"
Stairs = "%"
Gold = "*"
Potion = "!"
Scroll = "?"
Magic = "$"
Food = ":"
Weapon = ")"
Armor = "]"
Amulet = ","
Ring = "="
Stick = "/"

class InventryItemTypes(IntEnum):
    DisplayAll = 0
    Callable = -1

# Various flag bits
class Flags(IntFlag):
    IsCursed = 2 ** 1
    IsKnow = 2 ** 2
    IsMisl = 2 ** 3
    IsMany = 2 ** 4

    IsFound = 2 ** 5

    IsBlock = 2 ** 6
    IsRegen = 2 ** 7
    IsMean = 2 ** 8
    IsGreed = 2 ** 9
    IsInvis = 2 ** 10

# Various constants
BearTime:int = 3
SleepTime:int = 5
HoldTime:int = 2
WanderTime:int = 70
HuhDuration:int = 20
SeeDuration:int = 850
HungerTime:int = 1300
MoreTime:int = 150
StomachSize:int = 2000
BoltLength:int = 6



rooms = []
roomGraphDesc = []
startPosition = None

stdscr = None
playerWindow = None
helpWindow = None
monsterWindow = None

# initialParameter of magic items
things = None
potionMagic = None
scrollMagic = None
ringMagic = None
stickMagic = None
weapons = None
armors = None

# monster parameters
monsterParameters = []

# things in level of dungeon
levelObjectList = []                    # List of objects on this level
levelMonsterList = []                   # List of monsters on the level
traps = []

# playing status
level = 1               # What level rogue is on
ntraps = 0              # Number of traps on this level
noMove = 0              # Number of turns held in place
noCommand = 0           # Number of turns asleep
inpack = 0              # Number of things in pack
lastscore = 0           # Score before this turn
seed = 0                # Random number seed
count = 0               # Number of times to repeat command
dnum = 0                # Dungeon number
fungHit = 0             # Number of time fungi has hit
maxLevel = 25           # Deepest player has gone
group = 0               # Current group number

# Game status
playingGame = True      # True until he quits
after = False           # True if we want after daemons
notify = False          # True if player wants to know
fightFlush = False      # True if toilet input
slowInvent = False      # Inventory one line at a time
askMe = False           # Ask about unidentified things
hasAmulet = False

helpList = [
    ( '?',  "       prints help" ),
    ( '/',  "       identify object" ),
    ( 'h',  "       left" ),
    ( 'j',  "       down" ),
    ( 'k',  "       up" ),
    ( 'l',  "       right" ),
    ( 'y',  "       up & left" ),
    ( 'u',  "       up & right" ),
    ( 'b',  "       down & left" ),
    ( 'n',  "       down & right" ),
    ( 'H',  "       run left" ),
    ( 'J',  "       run down" ),
    ( 'K',  "       run up" ),
    ( 'L',  "       run right" ),
    ( 'Y',  "       run up & left" ),
    ( 'U',  "       run up & right" ),
    ( 'B',  "       run down & left" ),
    ( 'N',  "       run down & right" ),
    ( 't',  "<dir>  throw something" ),
    ( 'f',  "<dir>  forward until find something" ),
    ( 'p',  "<dir>  zap a wand in a direction" ),
    ( 'z',  "       zap a wand or staff" ),
    ( '>',  "       go down a staircase" ),
    ( 's',  "       search for trap/secret door" ),
    ( ' ',  "       (space) rest for a while" ),
    ( 'i',  "       inventory" ),
    ( 'I',  "       inventory single item" ),
    ( 'q',  "       quaff potion" ),
    ( 'r',  "       read paper" ),
    ( 'e',  "       eat food" ),
    ( 'w',  "       wield a weapon" ),
    ( 'W',  "       wear armor" ),
    ( 'T',  "       take armor off" ),
    ( 'P',  "       put on ring" ),
    ( 'R',  "       remove ring" ),
    ( 'd',  "       drop object" ),
    ( 'c',  "       call object" ),
    ( 'o',  "       examine/set options" ),
    ( "^L", "       redraw screen" ),
    ( "^R", "       repeat last message" ),
    ( "^[", "       cancel command" ),
    ( 'v',  "       print program version number" ),
    ( '!',  "       shell escape" ),
    ( 'S',  "       save game" ),
    ( 'Q',  "       quit" )  
]