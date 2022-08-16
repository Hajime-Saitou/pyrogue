# Flags:
# Create flag manager dynamically.
class Flags(object):
    def __init__(self, flagNameList:list) -> None:
        self.flagNameList:list = flagNameList
        self.clearAll()

    def clearAll(self) -> None:
        for flag in self.flagNameList:
            setattr(self, flag, False)
