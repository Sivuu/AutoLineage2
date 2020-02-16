import time
import win32api
import win32gui
import win32con


class Color():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.color = 0
    
    def Init(self):
        self.x, self.y = win32gui.GetCursorPos()
        self.color = win32gui.GetPixel(win32gui.GetWindowDC(win32gui.GetDesktopWindow()), self.x, self.y)
        
    def CheckPixelColor(self, x, y, color):
        try:
            if self.CheckActiveWindow():
                hwnd = win32gui.GetDesktopWindow()
                hwndDC = win32gui.GetWindowDC(hwnd)
                mColor = win32gui.GetPixel(hwndDC, x, y)
                win32gui.ReleaseDC(hwnd, hwndDC)
                if mColor == color:           
                    return True
                else:
                    return False
            else:
                return True

        except NameError as error:
            print("Error in CheckPixelColor %s" % error)

    def CheckActiveWindow(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                classHwnd = win32gui.GetClassName(hwnd)
                if classHwnd == "L2UnrealWWindowsViewportWindow" or classHwnd == "l2UnrealWWindowsViewportWindow":
                    return True
                else:
                    return False
            else:
                return False
        except NameError as er:
            print("Error in CheckActiveWindow: %s " % er)