import time
import win32api
import win32gui
import win32con
from tkinter import *
from tkinter import ttk


class Gui(Tk):
    def __init__(self):
        super(Gui, self).__init__()
        self.title("Auto Lineage II - For Local User")
        self.minsize(640, 400)

        tabControl = ttk.Notebook(self)

        numPad1 = ttk.Frame(tabControl)
        tabControl.add(numPad1, text="Numpad 01")
        box11 = IntVar()
        b1_np1 = Checkbutton(numPad1, text="Box 1", variable=box11, onvalue=1, offvalue=0, height=5, width=20)
        b1_np1.pack()


        numPad2 = ttk.Frame(tabControl)
        tabControl.add(numPad2, text="Numpad 02")
        box12 = IntVar()
        b1_np1 = Checkbutton(numPad2, text="Box 1", variable=box12, onvalue=1, offvalue=0, height=5, width=20)
        b1_np1.pack()

        tabControl.pack(expan=1, fill="both")

    def CallBack(self, hwnd, hwnds):
        """Return a list of window handlers based on it class name"""
        if win32gui.GetClassName(hwnd) == "L2UnrealWWindowsViewportWindow":
            hwnds.append(hwnd)
        return True

    def GetHWND(self):
        """Get all handle that have class name equal Lineage 2 Classic"""
        hwnds = []
        win32gui.EnumWindows(self.CallBack, hwnds)
        return hwnds
