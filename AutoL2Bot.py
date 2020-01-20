import os
import sys
import time
import wx
import ctypes
from Gui import UserGui

if __name__ == '__main__' and ctypes.windll.shell32.IsUserAnAdmin():
    app = wx.App(False)
    objGui = UserGui(None, "Loop Macro Lineage 2 - %s" % os.popen("wmic diskdrive get serialnumber").read().split()[-1])
    # Khai bao cac threading tai day
    app.MainLoop()