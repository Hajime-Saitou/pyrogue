import random
import string
import struct
from Rogue.Encoder import RogueEncoder

class Score(object):
    packFormat:str = "I16s32sI"
    packSize:int = struct.calcsize(packFormat)

    def __init__(self) -> None:
        self.score:int = 0
        self.playerName:str = self.__randomString__(16)
        self.reason:str = self.__randomString__(32)
        self.level:int = random.randint(0, 255)

    def __randomString__(self, length:int) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def __str__(self) -> str:
        if self.score == 0:
            return ""

        return f"{self.score:>5} {self.playerName:<16}: {self.reason:<32} on level {self.level:>3}"

    def pack(self) -> bytes:
        return struct.pack(Score.packFormat, self.score, self.playerName.encode(), self.reason.encode(), self.level)

    def unpack(self, binaryData:bytes) -> None:
        if len(binaryData) != Score.packSize:
            raise ValueError("data size incorrect.")

        self.score, self.playerName, self.reason, self.level = struct.unpack(Score.packFormat, binaryData)
        self.playerName = (self.playerName).decode()
        self.reason = (self.reason).decode()

class ScoreTable(object):
    def __init__(self, sizeOfTable:int=10) -> None:
        self.size:int = sizeOfTable
        self.scoreTable:list = []

        self.resetScoreTable()

    def resetScoreTable(self) -> None:
        self.scoreTable:list = []

        for _ in range(self.size):
            self.scoreTable.append(Score())

    def entry(self, score:Score) -> None:
        self.scoreTable.append(score)
        self.scoreTable = sorted(self.scoreTable, key=lambda s: s.score, reverse=True)[:self.size]

    def load(self, filename:str) -> None:
        self.resetScoreTable()

        with open(filename, "rb") as f:
            for score in self.scoreTable:
                score.unpack(RogueEncoder.decode(f.read(Score.packSize)))

    def save(self, filename:str) -> None:
        with open(filename, "wb") as f:
            for score in self.scoreTable:
                f.write(RogueEncoder.encode(score.pack()))

    # Print the list
    def print(self):
        print("")
        print(f"Top {self.size} Adventurers:")
        print("Rank Score Name")

        for rank, score in enumerate(self.scoreTable):
            print(f"{rank + 1:>4} {score}")
