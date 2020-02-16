import time
import win32gui

from KeyCombine import KeyCombine


class L2Handle():

    def __init__(self, handle, title):
        self.HandleName = title
        self.HandleValue = handle
        self.HandleNote = "Not Note"
        self.ActiveTime = time.time()
        self.Active = False
        self.DictKeyCombine = dict()
        for i in range(1, 10):
            self.DictKeyCombine["Key%s" % i] = KeyCombine(i)
