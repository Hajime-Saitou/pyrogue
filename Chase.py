import Global
import Rooms
import Monsters
import Io
import Move
import Player
import Fight
import Rogue
from Rogue import Coordinate
import Chase

# Set a mosnter running after something
# or stop it from running (for when it dies)
def runTo(runner, spot):
    # If we couldn't find him, something is funny
    monster = Monsters.findMonster(runner)
    if not monster:
    	# msg("CHASER '%s'", unctrl(winat(runner->y, runner->x)))
        pass

    # Start the beastie running
    monster.destination = spot
    monster.flags.isRun = True
    monster.flags.isHeld = False

# Check to see if the move is legal if it is diagonal
def diagOk(sp, ep):
    if ep == sp:
        return True
    return stepOk(Global.stdscr.inch(ep.y, sp.x)) and stepOk(Global.stdscr.inch(sp.y, ep.x))

# returns true if it is ok to step on ch
def stepOk(ch):
    if ch == ord(" ") or ch == ord("|") or ch == ord("-") or ch == Global.SecretDoor:
        return False

    return not str(ch).isalpha()

# runners:
# Make all the running monsters move.
def runners():
    for monster in Global.levelMonsterList:
        if not monster.flags.isHeld and monster.flags.isRun:
            if not monster.flags.isSlow or monster.turn:
                doChase(monster)
            if monster.flags.isHaste:
                doChase(monster)

            monster.turn = not monster.turn

# doChase:
# Make one thing chase another.
def doChase(monster):
    minDist = 32767
    stopRun = False             # TRUE means we are there
    tempDestination = None      # Temporary destination for chaser

    roomOfChaser = Rooms.roomIn(monster.position)      # Find room of chaser
    roomOfChasee = Rooms.roomIn(monster.destination)   # Find room of chasee

    # We don't count doors as inside rooms for this routine
    if Global.stdscr.inch(monster.position.y, monster.position.x) == Global.Door:
        roomOfChaser = None
    tempDestination = Player.player.position

    # If the object of our desire is in a different room, 
    # than we are and we ar not in a corridor, run to the
    # door nearest to our goal.
    if roomOfChaser != None and roomOfChaser != roomOfChasee:
        for exitPosition in roomOfChaser.exitPosition:   # loop through doors
            if exitPosition is None:
                continue

            dist = monster.position.distance(exitPosition)
            if dist < minDist:                  # minimize distance
                tempDestination = exitPosition
                minDist = dist

    # this now contains what we want to run to this time
    # so we run to it.  If we hit it we either want to fight it
    # or stop running
    retDist, chasePosition = chase(monster, tempDestination)
    if not retDist:
        if tempDestination == Player.player.position:
            Fight.attack(monster)
            return
        elif monster.type != "F":
            stopRun = True
    elif monster.type == "F":
    	return

    if monster.oldCh != 4294967295:
        Global.playerWindow.addch(monster.position.y, monster.position.x, monster.oldCh)
    sch = Global.playerWindow.inch(chasePosition.y, chasePosition.x)
    if roomOfChaser != None and roomOfChaser.flags.isDark and sch == Global.Floor\
        	and chasePosition.distance(monster.position) < 3\
            and not Player.player.flags.isBlind:
	    monster.oldCh = " "
    else:
	    monster.oldCh = sch

    if Chase.cansee(monster.position) and monster.flags.isInvis:
        Global.playerWindow.addch(chasePosition.y, chasePosition.x, monster.type)

    Global.monsterWindow.addch(monster.position.y, monster.position.x, " ")
    Global.monsterWindow.addch(chasePosition.y, chasePosition.x, monster.type)
    monster.position = chasePosition

    # And stop running if need be
    if stopRun and monster.position == monster.destination:
    	monster.flags.isRun = False

# Find the spot for the chaser(er) to move closer to the
# chasee(ee).  Returns TRUE if we want to keep on chasing later
# FALSE if we reach the goal.
def chase(chaser, destination):
    # If the thing is confused, let it move randomly. Invisible
    # Stalkers are slightly confused all of the time, and bats are
    # quite confused all the time
    if chaser.flags.isHuh and Global.rnd(10) < 8\
            or chaser.type == "I" and Global.rnd(100) < 20\
            or chaser.type == "B" and Global.rnd(100) < 50:
        # get a valid random move
        chasePosition = Move.rndMove(chaser)
        dist = chasePosition.distance(destination)

        # Small chance that it will become un-confused 
        if Global.rnd(1000) < 50:
            chaser.flags.isHuh = False

    # Otherwise, find the empty spot next to the chaser that is
    # closest to the chasee.
    else:
        # This will eventually hold where we move to get closer
        # If we can't find an empty spot, we stay where we are.
        er = chaser.position
        dist = er.distance(destination)
        chasePosition = er.clone()

        ey = er.y + 1
        ex = er.x + 1
        for x in range(er.x - 1, ex + 1):
            for y in range(er.y - 1, ey + 1):
                tryp = Rogue.Coordinate(x, y)
                if not diagOk(er, tryp):
                    continue

                ch = Io.winAt(tryp)
                if (stepOk(ch)):
        	        # If it is a scroll, it might be a scare monster scroll
        	        # so we need to look it up to see what type it is.
                    stepOnTheScareMonster = False
                    if ch == Global.Scroll:
                        for item in Global.levelObjectList:
                            if item.position == tryp:
                                # if item.which == Scrolls.ScrollOf.ScareMonster:
                                #     stepOnTheScareMonster = True
                                break

                        if stepOnTheScareMonster:
                            continue

        	        # If we didn't find any scrolls at this place or it
        	        # wasn't a scare scroll, then this place counts
                    thisDist = tryp.distance(destination)
                    if thisDist < dist:
                        chasePosition = tryp
                        dist = thisDist

    return dist != 0, chasePosition

# cansee:
# returns true if the hero can see a certain coordinate.
def cansee(coord:Coordinate) -> bool:
    if Player.player.flags.isBlind:
        return False

    room = Rooms.roomIn(coord)
    if room is None:
        return False

    # We can only see if the hero in the same room as
    # the coordinate and the room is lit or if it is close.
    room = Rooms.roomIn(Player.player.position)
    if room is None:
        return False

    return not room.flags.isDark or coord.sidtance(Player.player.position) < 3
