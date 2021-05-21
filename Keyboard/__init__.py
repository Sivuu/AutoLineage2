import time
import wx
from pykeyboard import keyboard
import win32gui
import win32con
import win32api

class Keyboard():
    def __init__(self):
        self.listKeyCode = {
            '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
            '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,
            'n0': 96, 'n1': 97, 'n2': 98, 'n3': 99,
            'n4': 100, 'n5': 101, 'n6': 102, 'n7': 103,
            'n8': 104, 'n9': 105, 'esc': 27,
            '*': 106, '+': 107, '-': 109,
            '.': 110, '/': 111, '=' : 187,
            'f1': 112, 'f2': 113, 'f3': 114, 'f4': 115,
            'f5': 116, 'f6': 117, 'f7': 118, 'f8': 119,
            'f9': 120, 'f10': 121, 'f11': 122, 'f12': 123
        }

    def CheckModifierKey(self):
        if keyboard.is_pressed('alt')\
            or keyboard.is_pressed('ctrl')\
            or keyboard.is_pressed('shift'):
            return True
        else:
            return False

    def ControlSend(self, hwnd, key):
        """ Send a key to windows, include it running on background"""
        listkey = key.split(';')
        if hwnd and win32gui.IsWindowVisible(hwnd.HandleValue) and not self.CheckModifierKey():
            for k in listkey:
                if k in self.listKeyCode.keys():
                    win32gui.PostMessage(hwnd.HandleValue, win32con.WM_KEYDOWN, 27, 0)
                    keyhex = self.listKeyCode[k]
                    win32gui.PostMessage(hwnd.HandleValue, win32con.WM_KEYDOWN, keyhex, 0)
                else:
                    return False
        else:
            return False
        return True
