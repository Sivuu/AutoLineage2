class KeyCombine():

    def __init__(self, value):
        self.Key = "f%s" % value
        self.RepeatTime = "600"
        self.SleepTime = "2"
        self.DictColor = dict()
        self.ActiveColor = False
        self.ActiveRepeat = False
        self.ActiveHotKey = True