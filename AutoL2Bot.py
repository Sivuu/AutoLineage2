import os
import sys
import time
import ctypes
import wx
import threading
import keyboard
import win32gui
from Color import Color
from Keyboard import Keyboard
from Gui import UserGui


def ColorCheckThread():
    try:
        while objGui:
            if objGui.tab["RunCheck"] :
                for i in range(1,10):
                    if objGui.tab["Tab %s" % i]["ColorCheckBox"].GetValue() and objGui.tab["Tab %s" % i]["Color"]:
                        for color in objGui.tab["Tab %s" % i]["Color"]:
                            if (not objColor.CheckPixelColor(color)) and objGui.tab["Handler"]:
                                for hwnd in objGui.tab["Handler"]:
                                    if objGui.tab[hwnd] and win32gui.IsWindowVisible(hwnd):
                                        objKeyBoard.ControlSend(hwnd, objGui.tab["Tab %s" % i]["Key"].GetValue())
                                    else:
                                        objGui.tab["Handler"] = objGui.GetHWND()
                                time.sleep(1)
    except NameError as er:
        print("Error is: %s" % (er))

def RepeatKeyThread():
    try:
        while objGui:
            if objGui.tab["RunCheck"] :
                for i in range(1,10):
                    if objGui.tab["Tab %s" % i]["RepeatKeyBox"].GetValue():
                        cdtime = int(float(objGui.tab["Tab %s" % i]["Time"].GetValue()))
                        if cdtime > 0:
                            lhtime = objGui.tab["Tab %s" % i]["LastHitTime"]
                            if (lhtime + cdtime) < time.time():
                                lhtime = objGui.tab["Tab %s" % i]["LastHitTime"] = time.time()
                                sltime = int(float(objGui.tab["Tab %s" % i]["Sleep"].GetValue()))
                                for hwnd in objGui.tab["Handler"]:
                                    if objGui.tab[hwnd] and win32gui.IsWindowVisible(hwnd):
                                        objKeyBoard.ControlSend(hwnd, objGui.tab["Tab %s" % i]["Key"].GetValue())
                                    else:
                                        objGui.tab["Handler"] = objGui.GetHWND()
                                time.sleep(sltime)
    except NameError as er:
        print("Error is: %s" % (er))

def HotKeyRegistry():
    for i in range(1,10):
        keyboard.add_hotkey('ctrl+%s' % i, AddColor, args=[i])
        shortkey = "f%s" % i
        keyboard.add_hotkey('f%s' % i, ControlSend, args=[shortkey])
    keyboard.wait("ctrl+esc")

def AddColor(value):
    if objGui:
        objGui.tab["Tab %s" % value]["Color"].append(   
            objColor.GetPixelColor()
        )
    else:
        pass

def ControlSend(value):
    if objGui:
        if objGui.tab["RunCheck"]:
            for hwnd in objGui.tab["Handler"]:
                if objGui.tab[hwnd] and win32gui.IsWindowVisible(hwnd):
                    objKeyBoard.ControlSend(hwnd, value)
                else:
                    objGui.tab["Handler"] = objGui.GetHWND()

if __name__ == '__main__' and ctypes.windll.shell32.IsUserAnAdmin():
    # Thuc hien threading o day
    global objColor, objGui, objKeyBoard, app
    objColor = Color()
    objKeyBoard = Keyboard()

    app = wx.App(False)
    objGui = UserGui(None, "AutoL2Python")
    # Khai bao cac threading tai day
    tcolor = threading.Thread(target= ColorCheckThread, daemon=True)
    tcolor.start()
    trepeat = threading.Thread(target= RepeatKeyThread, daemon=True)
    trepeat.start()
    thotkey = threading.Thread(target= HotKeyRegistry, daemon=True)
    thotkey.start()
    app.MainLoop()