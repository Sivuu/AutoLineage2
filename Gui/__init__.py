import time
import win32api
import win32gui
import win32con
import wx
import sys


class UserGui(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self,parent, title=title, size= wx.Size(460,350))
        mainpn = wx.Panel(self)
        mainnb = wx.Notebook(mainpn)
        self.tab = dict()
        self.tab["RunCheck"] = False

        # Tab Control ung dung
        self.tab["MainPage"] = wx.Panel(mainpn)
        sizerControl = wx.BoxSizer(wx.HORIZONTAL)

        self.btRun = wx.Button(self.tab["MainPage"], wx.ID_ANY, u"Start")
        self.Bind(wx.EVT_BUTTON, self.RunClick, self.btRun)

        self.btExit = wx.Button(self.tab["MainPage"], wx.ID_ANY, u"Exit")
        self.Bind(wx.EVT_BUTTON, self.ExitClick, self.btExit)

        sizerControl.AddStretchSpacer()
        sizerControl.Add(self.btRun, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizerControl.Add(self.btExit, 0,wx.ALIGN_CENTRE_HORIZONTAL, 0)
        sizerControl.AddStretchSpacer()
        self.tab["MainPage"].SetSizer(sizerControl)

        # Tab danh cho moi key
        for i in range(9):
            self.tab["Tab %s" % (i+1)] = dict()
            self.tab["Tab %s" % (i+1)]["Panel"] = wx.Panel(mainnb)
            # Key to send
            self.tab["Tab %s" % (i+1)]["LabelKey"] = wx.StaticText(self.tab["Tab %s" % (i+1)]["Panel"],  wx.ID_ANY, "Key Name %s" % (i+1), pos=(5, 10), size=(80, 30))
            self.tab["Tab %s" % (i+1)]["Key"] = wx.TextCtrl(self.tab["Tab %s" % (i+1)]["Panel"], wx.ID_ANY, "f%s" % (i+1), pos=( 95, 5), size=(80, 30))

            # Repeat time
            self.tab["Tab %s" % (i+1)]["LabelTime"] = wx.StaticText(self.tab["Tab %s" % (i+1)]["Panel"],  wx.ID_ANY, "Repeat Time %s" % (i+1), pos=(5, 50), size=(80, 30))
            self.tab["Tab %s" % (i+1)]["Time"] = wx.TextCtrl(self.tab["Tab %s" % (i+1)]["Panel"], wx.ID_ANY, "600", pos=( 95, 45), size=(80, 30))
            self.tab["Tab %s" % (i+1)]["LastHitTime"] = time.time()
            # Sleep time
            self.tab["Tab %s" % (i+1)]["LabelSleep"] = wx.StaticText(self.tab["Tab %s" % (i+1)]["Panel"],  wx.ID_ANY, "Sleep Time %s" % (i+1), pos=(5, 90), size=(80, 30))
            self.tab["Tab %s" % (i+1)]["Sleep"] = wx.TextCtrl(self.tab["Tab %s" % (i+1)]["Panel"], wx.ID_ANY, "2", pos=( 95, 85), size=(80, 30))

            # Check box to active
            self.tab["Tab %s" % (i+1)]["ColorCheckBox"] = wx.CheckBox(self.tab["Tab %s" % (i+1)]["Panel"], wx.ID_ANY, "Color Check", pos=(5, 125))
            self.tab["Tab %s" % (i+1)]["RepeatKeyBox"] = wx.CheckBox(self.tab["Tab %s" % (i+1)]["Panel"], wx.ID_ANY, "Repeat Key", pos=(165, 125))
            
            # Clear color
            self.tab["Tab %s" % (i+1)]["ButtonClear"] = wx.Button(self.tab["Tab %s" % (i+1)]["Panel"], wx.ID_ANY, u"Clear Color", pos=(5, 165))
            self.Bind(wx.EVT_BUTTON, lambda event,temp=i+1 : self.ClearColor(event,temp), self.tab["Tab %s" % (i+1)]["ButtonClear"])

            self.tab["Tab %s" % (i+1)]["Color"] = list()
            self.tab["Tab %s" % (i+1)]["Handle"] = list()

            tabSizer = wx.BoxSizer(wx.VERTICAL)
            tabSizer.Add(self.tab["Tab %s" % (i+1)]["LabelKey"], 0, wx.ALL, 5)
            tabSizer.Add(self.tab["Tab %s" % (i+1)]["Key"], 0, wx.ALL, 5)
            tabSizer.Add(self.tab["Tab %s" % (i+1)]["LabelTime"], 0, wx.ALL, 5)
            tabSizer.Add(self.tab["Tab %s" % (i+1)]["Time"], 0, wx.ALL, 5)
            tabSizer.Add(self.tab["Tab %s" % (i+1)]["LabelSleep"], 0, wx.ALL, 5)
            tabSizer.Add(self.tab["Tab %s" % (i+1)]["Sleep"], 0, wx.ALL, 5)
            tabSizer.Add(self.tab["Tab %s" % (i+1)]["ColorCheckBox"], 0, wx.ALL, 5 )
            tabSizer.Add(self.tab["Tab %s" % (i+1)]["ButtonClear"], 0, wx.ALL, 5 )

            mainnb.AddPage(self.tab["Tab %s" % (i+1)]["Panel"], 'Key {}'.format(i+1))
            
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(mainnb, 1, wx.EXPAND)
        sizer.Add(self.tab["MainPage"])
        mainpn.SetSizer(sizer)

        self.CreateStatusBar()
        self.Show(True)

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

    def RunClick(self, event):
        """Event for Run Check when its clicked"""
        if not self.tab["RunCheck"]:
            self.tab["Handler"] = self.GetHWND()
            self.tab["RunCheck"] = True
            self.btRun.SetLabel("Running")
        else:
            self.tab["Handler"] = self.GetHWND()
            self.tab["RunCheck"] = False
            self.btRun.SetLabel("Stop")

    def ExitClick(self, event):
        """Event for Exit Button when its clicked"""
        pass

    def ClearColor(self, event, value):
        self.tab["Tab %s" % value]["Color"] = list()