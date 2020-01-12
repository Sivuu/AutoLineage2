import time
import win32api
import win32gui
import win32con


class Color():
    def __init__(self):
        pass

    def GetPixelColor(self):
        """Get the color at mouse position"""
        x, y = win32gui.GetCursorPos()
        color = win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), x, y)
        ret = dict()
        ret["x"] = x
        ret["y"] = y
        ret["color"] = color
        return ret

    def CheckPixelColor(self, cdict):
        hwnd = win32gui.GetActiveWindow()
        hwndDC = win32gui.GetDC(hwnd)
        mColor = win32gui.GetPixel(hwndDC, cdict["x"], cdict["y"])
        cColor = cdict["color"]
        if mColor == cColor:
            win32gui.ReleaseDC(hwnd, hwndDC)
            return True
        else:
            win32gui.ReleaseDC(hwnd, hwndDC)
            return False