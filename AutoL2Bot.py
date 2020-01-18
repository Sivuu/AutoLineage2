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
                                    objKeyBoard.ControlSend(objGui.tab["Tab %s" % i], hwnd, objGui.tab["Tab %s" % i]["Key"].GetValue())
                                time.sleep(1)
            else:
                pass
    except NameError as er:
        print("Error in color check thread is: %s" % (er))

def RepeatKeyThread():
    try:
        while objGui:
            if objGui.tab["RunCheck"]:
                for i in range(1,10):
                    if objGui.tab["Tab %s" % i]["RepeatKeyBox"].GetValue():
                        try:
                            cdtime = int(float(objGui.tab["Tab %s" % i]["Time"].GetValue()))
                        except:
                            pass
                        if cdtime > 0:
                            lhtime = objGui.tab["Tab %s" % i]["LastHitTime"]
                            if (lhtime + cdtime) < time.time():
                                lhtime = objGui.tab["Tab %s" % i]["LastHitTime"] = time.time()
                                try:
                                    sltime = int(float(objGui.tab["Tab %s" % i]["Sleep"].GetValue()))
                                except:
                                    pass
                                for hwnd in objGui.tab["Handler"]:
                                    objKeyBoard.ControlSend(objGui.tab["Tab %s" % i], hwnd, objGui.tab["Tab %s" % i]["Key"].GetValue())
                                time.sleep(sltime)
            else:
                pass

    except NameError as er:
        print("Error in Repeat key thread is: %s" % (er))

def HotKeyRegistry():
    for i in range(1,10):
        keyboard.add_hotkey('ctrl+%s' % i, AddColor, args=[i])
        keyboard.add_hotkey('f%s' % i, ControlSend, args=[i], suppress=True)
    keyboard.wait("ctrl+shift+end")

def AddColor(value):
    if objGui:
        objGui.tab["Tab %s" % value]["Color"].append(   
            objColor.GetPixelColor()
        )
    else:
        pass

def ControlSend(value):
    if objGui:
        if objGui.tab["HotKey"]:
            for hwnd in objGui.tab["Handler"]:
                objKeyBoard.ControlSend(objGui.tab["Tab %s" % value], hwnd, objGui.tab["Tab %s" % value]["Key"].GetValue())
        else:
            pass

if __name__ == '__main__' and ctypes.windll.shell32.IsUserAnAdmin():
    # Check HDD -----
    myuuid = os.popen("wmic diskdrive get serialnumber").read().split()[-1]
    #myuuid = '2H4520037435'
    # Thuc hien threading o day
    global objColor, objGui, objKeyBoard, app
    objColor = Color()
    objKeyBoard = Keyboard()

    app = wx.App(False)
    objGui = UserGui(None, "AutoL2 - %s" % myuuid, myuuid)
    # Khai bao cac threading tai day
    thotkey = threading.Thread(target= HotKeyRegistry, daemon=True)
    thotkey.start()
    tcolor = threading.Thread(target= ColorCheckThread, daemon=True)
    tcolor.start()
    trepeat = threading.Thread(target= RepeatKeyThread, daemon=True)
    trepeat.start() 
    app.MainLoop()