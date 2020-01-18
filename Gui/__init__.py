import time
import os
import win32api
import win32gui
import win32con
import wx
import sys
import base64
#V0wxNVYyQzg=

class UserGui(wx.Frame):
    def __init__(self, parent, title, uuid):
        wx.Frame.__init__(self,parent, title=title, size= wx.Size(460,350))
        mainpn = wx.Panel(self)
        mainnb = wx.Notebook(mainpn)
        self.encode = base64.b64encode(uuid.encode('utf-8'))
        f = open(os.path.join(os.path.abspath(os.getcwd()),"key.txt"),"r")
        self.keyCode = f.read().encode("utf-8")
        self.tab = dict()
        self.tab["RunCheck"] = False
        self.tab["HotKey"] = False
        self.tab["Handler"] = self.GetHWND()

        # Tab Control ung dung
        self.tab["MainPage"] = wx.Panel(mainpn)
        sizerControl = wx.BoxSizer(wx.HORIZONTAL)

        self.btRun = wx.Button(self.tab["MainPage"], wx.ID_ANY, u"Start")
        self.Bind(wx.EVT_BUTTON, self.RunClick, self.btRun)

        self.btHotKey = wx.Button(self.tab["MainPage"], wx.ID_ANY, u"HotKey")
        self.Bind(wx.EVT_BUTTON, self.HotKeyClick, self.btHotKey)

        self.btExit = wx.Button(self.tab["MainPage"], wx.ID_ANY, u"Exit")
        self.Bind(wx.EVT_BUTTON, self.ExitClick, self.btExit)
    
        sizerControl.AddStretchSpacer()
        sizerControl.Add(self.btRun, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizerControl.Add(self.btHotKey, 0,wx.ALIGN_CENTRE_HORIZONTAL, 0)
        sizerControl.Add(self.btExit, 0,wx.ALIGN_CENTRE_HORIZONTAL, 0)
        sizerControl.AddStretchSpacer()
        self.tab["MainPage"].SetSizer(sizerControl)
        # Tab danh cho

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

            # Get client to send for key
            self.tab["Tab %s" % (i+1)]["ButtonHandle"] = wx.Button(self.tab["Tab %s" % (i+1)]["Panel"], wx.ID_ANY, u"Set Windows", pos=(105, 165))
            self.Bind(wx.EVT_BUTTON, lambda event,temp=i+1 : self.GetHandle(event,temp), self.tab["Tab %s" % (i+1)]["ButtonHandle"])

            self.tab["Tab %s" % (i+1)]["Color"] = list()

            for hwnd in self.tab["Handler"]:
                self.tab["Tab %s" % (i+1)][hwnd] = True

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
        if win32gui.GetClassName(hwnd) == "L2UnrealWWindowsViewportWindow"\
            or win32gui.GetClassName(hwnd) == "l2UnrealWWindowsViewportWindow":
            hwnds.append(hwnd)
        return True

    def GetHWND(self):
        """Get all handle that have class name equal Lineage 2 Classic"""
        hwnds = []
        win32gui.EnumWindows(self.CallBack, hwnds)
        return hwnds

    def RunClick(self, event):
        """Event for Run Check when its clicked"""
        if (self.encode == self.keyCode):
        # if True:
            if not self.tab["RunCheck"]: 
                self.tab["RunCheck"] = True
                self.btRun.SetLabel("Stop")
            else:
                self.tab["RunCheck"] = False
                self.btRun.SetLabel("Run")
        else:
            wx.MessageBox("Please put correct key to key.txt file in same folder with AutoL2Bot.exe", "Key Code Require", wx.OK)

    def HotKeyClick(self, event):
        """Event for Hot Key when its clicked"""
        if (self.encode == self.keyCode):
        # if True:
            if not self.tab["HotKey"]:
                self.tab["HotKey"] = True
                self.btHotKey.SetLabel("Stop Hot Key")
            else:
                self.tab["HotKey"] = False
                self.btHotKey.SetLabel("Run Hot Key")
        else:
            wx.MessageBox("Please put correct key to key.txt file in same folder with AutoL2Bot.exe", "Key Code Require", wx.OK)

    def ExitClick(self, event):
        """Event for Exit Button when its clicked"""
        self.Close()

    def ClearColor(self, event, value):
        """Event for Clear color in tab key"""
        self.tab["Tab %s" % value]["Color"] = list()

    def GetHandle(self, event, value):
        askFrame = wx.Frame(self, id=wx.ID_ANY,title="Select L2 Client to disable", size=(460,350))
        sizer = wx.BoxSizer(wx.VERTICAL)
        dictCheckBox = dict()

        def CloseFrame(event):
            for handle in self.tab["Handler"]:
                self.tab["Tab %s" % value][handle] = dictCheckBox[win32gui.GetWindowText(handle)].GetValue()
            askFrame.Close()

        for handle in self.tab["Handler"]:
            dictCheckBox[win32gui.GetWindowText(handle)] = wx.CheckBox(askFrame, id=wx.ID_ANY, label="%s" % win32gui.GetWindowText(handle))
            dictCheckBox[win32gui.GetWindowText(handle)].SetValue(True)
            sizer.Add(dictCheckBox[win32gui.GetWindowText(handle)])
            
        okBtn = wx.Button(askFrame, label="OK")
        okBtn.Bind(wx.EVT_BUTTON, CloseFrame)
        sizer.Add(okBtn)
        askFrame.SetSizer(sizer)
        askFrame.Show(True)
