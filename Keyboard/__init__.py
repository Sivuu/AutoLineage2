import time
import win32api
import win32gui
import win32con
from pynput.keyboard import Key, Listener


class Keyboard():
    def __init__(self):
        self.listKeyCode = {
            '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
            '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,
            'numpad0': 96, 'numpad1': 97, 'numpad2': 98, 'numpad3': 99,
            'numpad4': 100, 'numpad5': 101, 'numpad6': 102, 'numpad7': 103,
            'numpad8': 104, 'numpad9': 105,
            'multiply': 106, 'add': 107, 'subtract': 109,
            'dot': 110, 'divide': 111,
            'f1': 112, 'f2': 113, 'f3': 114, 'f4': 115,
            'f5': 116, 'f6': 117, 'f7': 118, 'f8': 119,
            'f9': 120, 'f10': 121, 'f11': 122, 'f12': 123
        }

    def ControlSend(self, hwnd, key):
        """ Send a key to windows, include it running on background"""
        if key in self.listKeyCode.keys():
            keyhex = self.listKeyCode[key]
            win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, keyhex, 0)
            return win32gui.PostMessage(hwnd, win32con.WM_KEYUP, keyhex, 0)
        else:
            print("The %s is not in list key (0-9,numpad, f1-f12)")
