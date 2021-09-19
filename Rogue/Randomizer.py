import os
import time

class LinearRandomizer(object):
   def __init__(self, seed:int, multiplier:int, addend:int, divisor:int) -> None:
       self.seed:int = int(seed)
       self.multiplier:int = int(multiplier)
       self.addend:int = int(addend)
       self.divisor:int = int(divisor)

   def next(self) -> int:
       self.seed = (self.seed * self.multiplier + self.addend) % self.divisor
       return self.seed
       
class RogueRandomizer(LinearRandomizer):
    def __init__(self) -> None:
        seed:int = int(time.time()) + int(os.getpid())
        super().__init__(seed, 11109, 13849, 0x7FFF)

    def next(self, range:int) -> int:
        self.seed = self.seed * self.multiplier + self.addend
        r =  self.seed & self.divisor >> 1
    
        return 0 if range == 0 else abs(r) % range
