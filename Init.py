import os
import Global
import Common
import Rooms
import Passages
import Things
import Weapon
import Armor
import Sticks
import Monsters
import Player
import Scrolls
import Potions
import Rings
import Rogue
import Options

# possible to connect to room i
possibleToConnect = [
    [ 0, 1, 0, 1, 0, 0, 0, 0, 0 ],
    [ 1, 0, 1, 0, 1, 0, 0, 0, 0 ],
    [ 0, 1, 0, 0, 0, 1, 0, 0, 0 ],
    [ 1, 0, 0, 0, 1, 0, 1, 0, 0 ],
    [ 0, 1, 0, 1, 0, 1, 0, 1, 0 ],
    [ 0, 0, 1, 0, 1, 0, 0, 0, 1 ],
    [ 0, 0, 0, 1, 0, 0, 0, 1, 0 ],
    [ 0, 0, 0, 0, 1, 0, 1, 0, 1 ],
    [ 0, 0, 0, 0, 0, 1, 0, 1, 0 ]
]

# initialize:
def initialize():
    # initialized room descriptions
    for index in range(Global.MaxRooms):
        Global.rooms.append(Rooms.Room())
        Global.roomGraphDesc.append(Passages.RoomGraphDescription(possibleToConnect[index]))

    initPlayer()            # Roll up the rogue
    initThings()            # Set up probabilities of things
    initScroll()            # Set up names of scrolls
    initRing()              # Set up stone settings of rings
    initPotion()
    initStick()
    initWeapon()
    initArmor()
    initMonsters()

# initialize score table
def initScore():
    Global.scoreTable = Rogue.ScoreTable()
    if os.path.isfile(Global.scoreFilename):
        Global.scoreTable.load(Global.scoreFilename)

# roll up the rogue
def initPlayer():
    Player.player = Common.Thing()
    Player.maxHp = 12

    if Global.rnd(100) == 7:
        strength = 18
        addStrength = Global.rnd(100) + 1
    else:
        strength = 16
        addStrength = 0
    Player.player.stats = Common.Stats(strength=strength, addStrength=addStrength, experience=0, level=1, armorClass=10, hitPoints=12, damage="1d4")

    Player.maxStats = Player.player.stats
    Player.player.pack = []

    Player.foodLeft = Global.StomachSize
    #for debug
    # Player.foodLeft = Global.StomachSize * 1000

def initMonsters():
    ISMEAN = Global.Flags.IsMean
    ISGREED = Global.Flags.IsGreed
    ISINVIS = Global.Flags.IsInvis
    ISBLOCK = Global.Flags.IsBlock
    ISREGEN = Global.Flags.IsRegen
    monsterParams = [
        # Name                 CARRY FLAG               str/add  exp   lv  ac  hp  damage
        [ "giant ant",            0, ISMEAN,            1, 1,      10,  2,  3,  1, "1d6" ],
        [ "bat",                  0, 0,                 1, 1,       1,  1,  3,  1, "1d2" ],
        [ "centaur",             15, 0,                 1, 1,      15,  4,  4,  1, "1d6/1d6" ],
        [ "dragon",             100, ISGREED,           1, 1,    9000, 10, -1,  1, "1d8/1d8/3d10" ],
        [ "floating eye",         0, 0,                 1, 1,       5,  1,  9,  1, "0d0" ],
        [ "violet fungi",         0, ISMEAN,            1, 1,      85,  8,  3,  1, "0d0" ],
        [ "gnome",               10, 0,                 1, 1,       8,  1,  5,  1, "1d6" ],
        [ "hobgoblin",            0, ISMEAN,            1, 1,       3,  1,  5,  1, "1d8" ],
        [ "invisible stalker",    0, ISINVIS,           1, 1,     120,  8,  3,  1, "4d4" ],
        [ "jackal",               0, ISMEAN,            1, 1,       2,  1,  7,  1, "1d2" ],
        [ "kobold",               0, ISMEAN,            1, 1,       1,  1,  7,  1, "1d4" ],
        [ "leprechaun",           0, 0,                 1, 1,      10,  3,  8,  1, "1d1" ],
        [ "mimic",               30, 0,                 1, 1,     140,  7,  7,  1, "3d4" ],
        [ "nymph",              100, 0,                 1, 1,      40,  3,  9,  1, "0d0" ],
        [ "orc",                 15, ISBLOCK,           1, 1,       5,  1,  6,  1, "1d8" ],
        [ "purple worm",         70, 0,                 1, 1,    7000, 15,  6,  1, "2d12/2d4" ],
        [ "quasit",              30, ISMEAN,            1, 1,      35,  3,  2,  1, "1d2/1d2/1d4" ],
        [ "rust monster",         0, ISMEAN,            1, 1,      25,  5,  2,  1, "0d0/0d0" ],
        [ "snake",                0, ISMEAN,            1, 1,       3,  1,  5,  1, "1d3" ],
        [ "troll",               50, ISREGEN | ISMEAN,  1, 1,      55,  6,  4,  1, "1d8/1d8/2d6" ],
        [ "umber hulk",          40, ISMEAN,            1, 1,     130,  8,  2,  1, "3d4/3d4/2d5" ],
        [ "vampire",             20, ISREGEN | ISMEAN,  1, 1,     380,  8,  1,  1, "1d10" ],
        [ "wraith",               0, 0,                 1, 1,      55,  5,  4,  1, "1d6" ],
        [ "xorn",                 0, ISMEAN,            1, 1,     120,  7, -2,  1, "1d3/1d3/1d3/4d6" ],
        [ "yeti",                30, 0,                 1, 1,      50,  4,  6,  1, "1d6/1d6" ],
        [ "zombie",               0, ISMEAN,            1, 1,       7,  2,  8,  1, "1d8" ]
    ]

    for param in monsterParams:
        Global.monsterParameters.append(
            Monsters.Monster(
                name=param[0], carry=param[1], flags=param[2],
                stats=Common.Stats(strength=param[3], addStrength=param[4], experience=param[5],
                    level=param[6], armorClass=param[7], hitPoints=param[8], damage=param[9])
            )
        )

# Initialize the probabilities for types of things
def initThings():
    Global.things = Things.MagicItems("things")
    Global.things.append("potion", 27, 0)
    Global.things.append("scroll", 27, 0)
    Global.things.append("food",   18, 0)
    Global.things.append("weapon",  9, 0)
    Global.things.append("armor",   9, 0)
    Global.things.append("ring",    5, 0)
    Global.things.append("stick",   5, 0)
    Global.things.badCheck()

# initScroll:
def initScroll():
    Global.scrollMagic = Things.MagicItems("scroll")
    Global.scrollMagic.append("monster confusion",   8, 170)
    Global.scrollMagic.append("magic mapping",       5, 180)
    Global.scrollMagic.append("light",              10, 100)
    Global.scrollMagic.append("hold monster",        2, 200)
    Global.scrollMagic.append("sleep",               5,  50)
    Global.scrollMagic.append("enchant armor",       8, 130)
    Global.scrollMagic.append("identify",           21, 100)
    Global.scrollMagic.append("scare monster",       4, 180)
    Global.scrollMagic.append("gold detection",      4, 110)
    Global.scrollMagic.append("teleportation",       7, 175)
    Global.scrollMagic.append("enchant weapon",     10, 150)
    Global.scrollMagic.append("create monster",      5,  75)
    Global.scrollMagic.append("remove curse",        8, 105)
    Global.scrollMagic.append("aggravate monsters",  1,  60)
    Global.scrollMagic.append("blank paper",         1,  50)
    Global.scrollMagic.append("genocide",            1, 200)

    length = len(Global.scrollMagic.itemList)
    Global.scrollMagic.tentativeName = Scrolls.initTentativeNames(length)
    Global.scrollMagic.know = [ False ] * length
    Global.scrollMagic.guessName = [ "" ] * length

# initPotion:
def initPotion():
    Global.potionMagic = Things.MagicItems("potion")
    Global.potionMagic.append("confusion",           8,  50)
    Global.potionMagic.append("paralysis",          10,  50)
    Global.potionMagic.append("poison",              8,  50)
    Global.potionMagic.append("gain strength",      15, 150)
    Global.potionMagic.append("see invisible",       2, 170)
    Global.potionMagic.append("healing",            15, 130)
    Global.potionMagic.append("monster detection",   6, 120)
    Global.potionMagic.append("magic detection",     6, 105)
    Global.potionMagic.append("raise level",         2, 220)
    Global.potionMagic.append("extra healing",       5, 180)
    Global.potionMagic.append("haste self",          4, 200)
    Global.potionMagic.append("restore strength",   14, 120)
    Global.potionMagic.append("blindness",           4,  50)
    Global.potionMagic.append("thirst quenching",    1,  50)

    length = len(Global.potionMagic.itemList)
    Global.potionMagic.tentativeName = Potions.initTentativeNames(length)
    Global.potionMagic.know = [ False ] * length
    Global.potionMagic.guessName = [ "" ] * length

# initRing:
def initRing():
    Global.ringMagic = Things.MagicItems("ring")
    Global.ringMagic.append("protection",            9, 200)
    Global.ringMagic.append("add strength",          9, 200)
    Global.ringMagic.append("sustain strength",      5, 180)
    Global.ringMagic.append("searching",            10, 200)
    Global.ringMagic.append("see invisible",        10, 175)
    Global.ringMagic.append("adornment",             1, 100)
    Global.ringMagic.append("aggravate monster",    11, 100)
    Global.ringMagic.append("dexterity",             8, 220)
    Global.ringMagic.append("increase damage",       8, 220)
    Global.ringMagic.append("regeneration",          4, 260)
    Global.ringMagic.append("slow digestion",        9, 240)
    Global.ringMagic.append("telportation",          9, 100)
    Global.ringMagic.append("stealth",               7, 100)

    length = len(Global.ringMagic.itemList)
    Global.ringMagic.tentativeName = Rings.initTentativeNames(length)
    Global.ringMagic.know = [ False ] * length
    Global.ringMagic.guessName = [ "" ] * length

# initStick:
def initStick():
    Global.stickMagic = Things.MagicItems("stick")
    Global.stickMagic.append("light",               12, 120)
    Global.stickMagic.append("striking",             9, 115)
    Global.stickMagic.append("lightning",            3, 200)
    Global.stickMagic.append("fire",                 3, 200)
    Global.stickMagic.append("cold",                 3, 200)
    Global.stickMagic.append("polymorph",           15, 210)
    Global.stickMagic.append("magic missile",       10, 170)
    Global.stickMagic.append("haste monster",        9,  50)
    Global.stickMagic.append("slow monster",        11, 220)
    Global.stickMagic.append("drain life",           9, 210)
    Global.stickMagic.append("nothing",              1,  70)
    Global.stickMagic.append("teleport away",        5, 140)
    Global.stickMagic.append("teleport to",          5,  60)
    Global.stickMagic.append("cancellation",         5, 130)

    length = len(Global.stickMagic.itemList)
    Sticks.initMaterials(length)
    Global.stickMagic.tentativeName = Sticks.initTentativeName(length)
    Global.stickMagic.know = [ False ] * length
    Global.stickMagic.guessName = [ "" ] * length

# initWeapon:
def initWeapon():
    Global.weapons = Weapon.Weapon()
    Global.weapons.append("mace",                "2d4",  "1d3", None,                       0, 8)
    Global.weapons.append("long sword",         "1d10",  "1d2", None,                       0, 15)
    Global.weapons.append("short bow",           "1d1",  "1d1", None,	                    0, 75)
    Global.weapons.append("arrow",               "1d1",  "1d6", Weapon.WeaponOf.ShortBow,   Global.Flags.IsMany|Global.Flags.IsMisl, 1)
    Global.weapons.append("dagger",              "1d6",  "1d4", None,	                    Global.Flags.IsMisl, 2)
    Global.weapons.append("rock",                "1d2",  "1d4", Weapon.WeaponOf.Sling,      Global.Flags.IsMany|Global.Flags.IsMisl, 1)
    Global.weapons.append("two handed sword",    "3d6",  "1d2", None,	                    0, 30)
    Global.weapons.append("sling",               "0d0",  "0d0", None,                       0, 1)
    Global.weapons.append("dart",                "1d1",  "1d3", None,	                    Global.Flags.IsMany|Global.Flags.IsMisl, 1)
    Global.weapons.append("crossbow",            "1d1",  "1d1", None,                       0, 15)
    Global.weapons.append("crossbow bolt",       "1d2", "1d10", Weapon.WeaponOf.CrossBow,   Global.Flags.IsMany|Global.Flags.IsMisl, 1)
    Global.weapons.append("spear",               "1d8",  "1d6", None,                       Global.Flags.IsMisl, 2)

# initArmor:
def initArmor():
    Global.armors = Armor.Armor()
    Global.armors.append("leather armor",           8,  20, 5)
    Global.armors.append("ring mail",               7,  35, 30)
    Global.armors.append("studded leather armor",   7,  50, 15)
    Global.armors.append("scale mail",              6,  63, 3)
    Global.armors.append("chain mail",              5,  75, 75)
    Global.armors.append("splint mail",             4,  85, 80)
    Global.armors.append("banded mail",             4,  95, 90)
    Global.armors.append("plate mail",              3, 100, 400)
