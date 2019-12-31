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
        ret = (x,y,color)
        return ret

