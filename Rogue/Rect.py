class Rect(object):
    def __init__(self, left:int=0, top:int=0, width:int=0, height:int=0) -> None:
        self.left:int = int(left)
        self.top:int = int(top)
        self.width:int = int(width)
        self.height:int = int(height)

        self.right:int = self.left + self.width - 1
        self.bottom:int = self.top + self.height - 1
        