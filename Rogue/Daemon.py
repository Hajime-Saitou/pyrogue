from enum import IntEnum

# Contains functions for dealing with things that happen in the future.
class DaemonExecuteTiming(IntEnum):
    NotSet = 0,
    Before = 1,
    After = 2,

# Daemon:
# Start a daemon, takes a function.
class Daemon(object):
    def __init__(self, func) -> None:
        self.func = func
        self.enabled:bool = True

    # do:
    # Run all the daemons/fuses that are active with the current flag,
    # passing the argument to the function.
    def do(self) -> None:
        # Executing each one, giving it the proper arguments
        if self.enabled:
            self.func()

# Fuse:
# Start a fuse to go off in a certain number of turns
class Fuse(Daemon):
    def __init__(self, func, delayTimer:int=0) -> None:
        super().__init__(func)
        self.delayTimer:int = delayTimer

    # do:
    # Run all the daemons/fuses that are active with the current flag,
    # passing the argument to the function.
    def do(self) -> None:
        if not self.enabled:
            return

        # Decrementing counters and starting things we want.  We also need
        # to remove the fuse from the list once it has gone off.
        if self.delayTimer > 0:
            self.delayTimer -= 1

        if self.delayTimer == 0:
            self.func()
            self.enabled = False

    # lengthen:
    # Increase the time until a fuse goes off
    def lengthen(self, extendTime:int) -> None:
        self.delayTimer += extendTime
        if self.delayTimer > 0:
            self.enabled = True

# DaemonManager:
# Execute daemons with various function at specific timing.
class DaemonManager(object):
    def __init__(self):
        self.slot:list = []

    def __str__(self) -> str:
        string = ""
        for daemon, executeTiming in self.slot:
            string += f"{daemon.func}, {executeTiming}"
            if type(daemon) == "Fuse":
                string += f"{daemon.existTimer}"
            string += "\n"
        
        return string

    def append(self, daemon:Daemon, executeTiming:DaemonExecuteTiming):
        self.slot.append(( daemon, executeTiming ))

    def do(self, executeTiming:DaemonExecuteTiming):
        # Loop through the devil list
        for daemon, _ in filter(lambda d: d[1] == executeTiming, self.slot):
            # Executing each one, giving it the proper arguments
            daemon.do()
            if not daemon.enabled:
                self.kill(daemon.func)

    # kill:
    # Remove a daemon from the list
    def kill(self, func) -> None:
        for daemon, executeTiming in filter(lambda d: d[0].func == func, self.slot):
            self.slot.remove(( daemon, executeTiming ))

    # lengthen:
    # Increase the time until a fuse goes off
    def lengthen(self, func, extendTime:int) -> None:
        for fuse, _ in filter(lambda d: d[0].func == func, self.slot):
            fuse.lengthen(extendTime)
