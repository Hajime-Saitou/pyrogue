class AbstructEncoder(object):
    def encode(self):
        raise NotImplementedError
    
    def decode(self):
        raise NotImplementedError

class BinaryStringXorEncoder(AbstructEncoder):
    def __init__(self, xorBytes:bytes) -> None:
        self.xorBytes:list = list(xorBytes)

    def encode(self, bstring:bytes) -> bytes:
        encoderIndex:int = 0
        encodedBytes:list = []

        for ch in list(bstring):
            encodedBytes.append(ch ^ self.xorBytes[encoderIndex])
            encoderIndex += 1
            encoderIndex %= len(self.xorBytes)

        return bytes(encodedBytes)

    def decode(self, encodedBytes:bytes) -> bytes:
        return self.encode(encodedBytes)

class RogueEncoder(AbstructEncoder):
    encoder:BinaryStringXorEncoder = BinaryStringXorEncoder(b"\354\251\243\332A\201|\301\321p\210\251\327\"\257\365t\341%3\271^`~\203z{\341};\f\341\231\222e\234\351]\321")

    @staticmethod
    def encode(bstring:bytes) -> bytes:
        return RogueEncoder.encoder.encode(bstring)

    @staticmethod
    def decode(encodedBytes:bytes) -> bytes:
        return RogueEncoder.encoder.decode(encodedBytes)