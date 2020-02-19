import time
from Color import Color

class KeyCombine():
    def __init__(self, value):
        self.Key = "n%s" % value
        self.RepeatTime = "600"
        self.SleepTime = "2"
        self.ActiveRepeat = False
        self.LastHit = 0
