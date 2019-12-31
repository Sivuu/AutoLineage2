import os
import sys
import time
import ctypes
import keyboard
from Color import *
from Keyboard import *
from Gui import *

listKeyboard = list()
objColor = Color()
objGui = Gui()

def add_window(value):
    listKeyboard[value].handleBox = objGui.GetHWND()

def add_color(value):
    listKeyboard[value].colorActive.append(objColor.GetPixelColor())

keyboard.add_hotkey("ctrl+1",add_color,args=[0])
if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin():
        for i in range(9):
            name = "f" + str(i + 1)
            listKeyboard.append(Keyboard(name))
            add_window(i)

keyboard.wait('shift+esc')