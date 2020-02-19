import time
import win32gui, win32process
from ctypes import *

from KeyCombine import KeyCombine


class L2Handle():

    def __init__(self, handle, title):
        self.HandleName = title
        self.HandleValue = handle
        self.PID = win32process.GetWindowThreadProcessId(handle)[1]

        self.HandleNote = "Not Note"
        self.ActiveTime = time.time()
        self.Active = False
        self.DictKeyCombine = dict()
        self.HP = 0
        self.MP = 0
        self.CP = 0
        self.Condition = dict()
        self.Condition["Char"] = None
        self.Condition["HPHeal"] = 0
        self.Condition["HPKey"] = "Notset"
        self.Condition["MPRecharge"] = 0
        self.Condition["MPKey"] = "Notset"
        self.Condition["CPHeal"] = 0
        self.Condition["CPKey"] = "Notset"
        for i in range(1, 10):
            self.DictKeyCombine["Key%s" % i] = KeyCombine(i)
