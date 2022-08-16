# Coordinate data type
class Coordinate(object):
    def __init__(self, x:int=0, y:int=0) -> None:
        self.x:int = int(x)
        self.y:int = int(y)

    def __eq__(self, other):
        return [ self.x, self.y ] == [ other.x, other.y ]

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __add__(self, other):
        return Coordinate(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"x: {self.x}, y: {self.y}"

    def distance(self, other) -> float:
        return (other.x - self.x) ** 2 + (other.y - self.y) ** 2

    def clone(self):
        return Coordinate(self.x, self.y)