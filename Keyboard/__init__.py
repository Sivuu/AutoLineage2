import time
import win32api
import win32gui
import win32con
import wx


class Keyboard():
    def __init__(self):
        self.listKeyCode = {
            '0': 48, '1': 49, '2': 50, '3': 51, '4': 52,
            '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,
            'n0': 96, 'n1': 97, 'n2': 98, 'n3': 99,
            'n4': 100, 'n5': 101, 'n6': 102, 'n7': 103,
            'n8': 104, 'n9': 105,
            '*': 106, '+': 107, '-': 109,
            '.': 110, '/': 111,
            'f1': 112, 'f2': 113, 'f3': 114, 'f4': 115,
            'f5': 116, 'f6': 117, 'f7': 118, 'f8': 119,
            'f9': 120, 'f10': 121, 'f11': 122, 'f12': 123
        }

    def ControlSend(self, obj, hwnd, key):
        """ Send a key to windows, include it running on background"""
        listkey = key.split(';')
        if obj[hwnd] and win32gui.IsWindowVisible(hwnd):
            for k in listkey:
                if k in self.listKeyCode.keys():
                    keyhex = self.listKeyCode[k]
                    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, keyhex, 0)
                    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, keyhex, 0)
                else:
                    return False
            time.sleep(0.2)
        else:
            return False
        return True

