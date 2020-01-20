import os
import sys
import time
import win32api
import win32gui
import win32con
import wx
import threading
import base64
import ntplib
from datetime import datetime, timezone, timedelta

class UserGui(wx.Frame):
    def __init__(self, parent, title):
        # Khai bao tham so cua GUI
        self.encode = os.popen("wmic diskdrive get serialnumber").read().split()[-1]
        f = open(os.path.join(os.path.abspath(os.getcwd()),"key.txt"),"r")
        keytemp =  base64.b64decode(f.read().encode("utf-8")).decode("utf-8")
        self.keyCode = keytemp.split(";")[0]
        self.keyTime = keytemp.split(";")[1] + "+00:00"
        self.UIDict = dict()

        # Khoi tao cua so ung dung
        wx.Frame.__init__(self,parent, title=title, size= wx.Size(750,420), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.CreateStatusBar()
        sizerFrame = wx.GridBagSizer(0,0)
        sizerFrame.SetFlexibleDirection(wx.BOTH)
        sizerFrame.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        # Choice box de lua chon Handle setup cho tool
        self.UIDict["Handle"] = []
        self.UIDict["ChoiceHandle"] = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.UIDict["Handle"], 0 )
        self.UIDict["ChoiceHandle"].SetSelection( 0 )
        sizerFrame.Add(self.UIDict["ChoiceHandle"], wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        # Button Start/Run
        self.UIDict["btRun"] = wx.Button(self, wx.ID_ANY, label='Start')
        sizerFrame.Add(self.UIDict["btRun"] , wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        # Button Get Handle
        self.UIDict["btGetHandle"] = wx.Button(self, wx.ID_ANY, label='Get Handle')
        sizerFrame.Add(self.UIDict["btGetHandle"] , wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        # Button Save Key
        self.UIDict["btSaveKey"] = wx.Button(self, wx.ID_ANY, label='Save Key')
        sizerFrame.Add(self.UIDict["btSaveKey"] , wx.GBPosition( 4, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        # Button Save Profile
        self.UIDict["btSaveProfile"] = wx.Button(self, wx.ID_ANY, label='Save Profile')
        sizerFrame.Add(self.UIDict["btSaveProfile"] , wx.GBPosition( 6, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        # Button Load Profile
        self.UIDict["btLoadProfile"] = wx.Button(self, wx.ID_ANY, label='Load Profile')
        sizerFrame.Add(self.UIDict["btLoadProfile"] , wx.GBPosition( 7, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        # Button Exit
        self.UIDict["btExit"] = wx.Button(self, wx.ID_ANY, label='Exit')
        sizerFrame.Add(self.UIDict["btExit"] , wx.GBPosition( 9, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

        # Thiet lap Panel danh cho Handle Infomation --------------------
        self.UIDict["panelHandle"] = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        sizerFrame.Add(self.UIDict["panelHandle"], wx.GBPosition( 0, 1 ), wx.GBSpan( 19, 47 ), wx.ALL, 5 )
        
        sizerPanel = wx.GridBagSizer(0,0)
        sizerPanel.SetFlexibleDirection(wx.BOTH)
        sizerPanel.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        # Label Name cua Lineage II Tab
        self.UIDict["panelHandleName"] = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Lineage 2 Tab")

        # Nhom Label KeyCombine Information
        pnKeyName = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Key Combine")
        sizerPanel.Add(pnKeyName,wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5 )
        pnRepeat = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Repeat Time")
        sizerPanel.Add(pnRepeat,wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5 )
        pnSleep = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Sleep Time")
        sizerPanel.Add(pnSleep,wx.GBPosition(1, 2), wx.GBSpan(1, 1), wx.ALL, 5 )
        pnActiveRepeat = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Active Repeat")
        sizerPanel.Add(pnActiveRepeat,wx.GBPosition(1, 3), wx.GBSpan(1, 1), wx.ALL, 5 )
        pnActiveColor = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Active Color")
        sizerPanel.Add(pnActiveColor,wx.GBPosition(1, 4), wx.GBSpan(1, 1), wx.ALL, 5 )
        pnActiveHotKey = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Active HotKey")
        sizerPanel.Add(pnActiveHotKey,wx.GBPosition(1, 5), wx.GBSpan(1, 1), wx.ALL, 5 )

        self.UIDict["CombineKey"] = dict()
        for i in range(2,11):
            self.UIDict["CombineKey"]["Key%s" %(i-1)] = dict()

            self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnKeyName"] = wx.TextCtrl(self.UIDict["panelHandle"], id=wx.ID_ANY, value="f%s" %(i-1))
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnKeyName"] ,wx.GBPosition(i, 0), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5 )

            self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnRepeat"] = wx.TextCtrl(self.UIDict["panelHandle"], id=wx.ID_ANY, value="5")
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnRepeat"],wx.GBPosition(i, 1), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5 )

            self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnSleep"] = wx.TextCtrl(self.UIDict["panelHandle"], id=wx.ID_ANY, value="5")
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnSleep"],wx.GBPosition(i, 2), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5 )

            self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnActiveRepeat"] = wx.CheckBox(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Y/N")
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnActiveRepeat"],wx.GBPosition(i, 3), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5 )

            self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnActiveColor"] = wx.CheckBox(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Y/N")
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnActiveColor"],wx.GBPosition(i, 4), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5 )

            self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnActiveHotKey"] = wx.CheckBox(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Y/N")
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" %(i-1)]["pnActiveHotKey"],wx.GBPosition(i, 5), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5 )
        
        self.UIDict["panelHandle"].SetSizer(sizerPanel)
        self.UIDict["panelHandle"].Layout()
        # Thiet lap Sizer Main-------------------------------------------
        self.SetSizer(sizerFrame)
        self.Layout()
        self.Show(True)

    def TakeNTPTime(self):
        """ Function to get time from NTP with time zone is utc + 0"""
        c = ntplib.NTPClient()
        # Provide the respective ntp server ip in below function
        response = c.request('uk.pool.ntp.org', version=3)
        response.offset 
        # UTC timezone used here, for working with different timezones you can use [pytz library][1]
        return (datetime.fromtimestamp(response.tx_time, timezone.utc))

    def ConvertStringtoDateTime(self, strconvert):
        """ Function to convert string time to date time with time zone is utc + 0"""
        try:
            dateret = datetime.strptime(strconvert, '%Y-%m-%d %H:%M:%S.%f%z').astimezone(timezone.utc)
        except:
            return (self.TakeNTPTime() - timedelta(days=1))
        else:
            return dateret 

    def CheckKeyCode(self):
        """ Kiem tra KeyCode co hop le"""
        self.encode = os.popen("wmic diskdrive get serialnumber").read().split()[-1]
        f = open(os.path.join(os.path.abspath(os.getcwd()),"key.txt"),"r")
        keytemp =  base64.b64decode(f.read().encode("utf-8")).decode("utf-8")
        self.keyCode = keytemp.split(";")[0]
        self.keyTime = keytemp.split(";")[1] + "+00:00"
        if (self.encode == self.keyCode) and (self.TakeNTPTime() < self.ConvertStringtoDateTime(self.keyTime)):
            return True
        else:
            return False

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
        if self.CheckKeyCode():
        # if True:
            if not self.tab["RunCheck"]: 
                self.tab["RunCheck"] = True
                self.btRun.SetLabel("Stop")
            else:
                self.tab["RunCheck"] = False
                self.btRun.SetLabel("Run")
        else:
            wx.MessageBox("Incorrect key or Time is expired", "New Key Code Require", wx.OK)

    def HotKeyClick(self, event):
        """Event for Hot Key when its clicked"""
        if self.CheckKeyCode():
        # if True:
            if not self.tab["HotKey"]:
                self.tab["HotKey"] = True
                self.btHotKey.SetLabel("Stop Hot Key")
            else:
                self.tab["HotKey"] = False
                self.btHotKey.SetLabel("Run Hot Key")
        else:
            wx.MessageBox("Incorrect key or Time is expired", "New Key Code Require", wx.OK)

    def ColorClick(self):
        pass

    def ExitClick(self, event):
        """Event for Exit Button when its clicked"""
        self.Close()

    def ClearColor(self, event, value):
        """Event for Clear color in tab key"""
        self.tab["Tab %s" % value]["Color"] = list()

    def GetHandle(self, event, value):
        """Get Handle for per tab key"""
        self.tab["Handler"] = self.GetHWND()
        askFrame = wx.Frame(self, id=wx.ID_ANY,title="Select L2 Client to disable", size=(460,350))
        sizer = wx.BoxSizer(wx.VERTICAL)
        dictCheckBox = dict()

        def CloseFrame(event):
            for handle in self.tab["Handler"]:
                self.tab["Tab %s" % value][handle] = dictCheckBox[win32gui.GetWindowText(handle)].GetValue()
            askFrame.Close()

        for handle in self.tab["Handler"]:
            dictCheckBox[win32gui.GetWindowText(handle)] = wx.CheckBox(askFrame, id=wx.ID_ANY, label="%s" % win32gui.GetWindowText(handle))
            dictCheckBox[win32gui.GetWindowText(handle)].SetValue(False)
            sizer.Add(dictCheckBox[win32gui.GetWindowText(handle)])
            
        okBtn = wx.Button(askFrame, label="OK")
        okBtn.Bind(wx.EVT_BUTTON, CloseFrame)
        sizer.Add(okBtn)
        askFrame.SetSizer(sizer)
        askFrame.Show(True)

    def ColorCheckThread(self):
        try:
            while objGui:
                if objGui.tab["RunCheck"] :
                    for i in range(1,10):
                        if objGui.tab["Tab %s" % i]["ColorCheckBox"].GetValue() and objGui.tab["Tab %s" % i]["Color"]:
                            for color in objGui.tab["Tab %s" % i]["Color"]:
                                if (not objColor.CheckPixelColor(color)) and objGui.tab["Handler"]:
                                    for hwnd in objGui.tab["Handler"]:
                                        objKeyBoard.ControlSend(objGui.tab["Tab %s" % i], hwnd, objGui.tab["Tab %s" % i]["Key"].GetValue())
                                    time.sleep(1)
                else:
                    pass
        except NameError as er:
            print("Error in color check thread is: %s" % (er))

    def RepeatKeyThread(self):
        try:
            while objGui:
                if objGui.tab["RunCheck"]:
                    for i in range(1,10):
                        if objGui.tab["Tab %s" % i]["RepeatKeyBox"].GetValue():
                            try:
                                cdtime = int(float(objGui.tab["Tab %s" % i]["Time"].GetValue()))
                            except:
                                pass
                            if cdtime > 0:
                                lhtime = objGui.tab["Tab %s" % i]["LastHitTime"]
                                if (lhtime + cdtime) < time.time():
                                    lhtime = objGui.tab["Tab %s" % i]["LastHitTime"] = time.time()
                                    try:
                                        sltime = int(float(objGui.tab["Tab %s" % i]["Sleep"].GetValue()))
                                    except:
                                        pass
                                    for hwnd in objGui.tab["Handler"]:
                                        objKeyBoard.ControlSend(objGui.tab["Tab %s" % i], hwnd, objGui.tab["Tab %s" % i]["Key"].GetValue())
                                    time.sleep(sltime)
                else:
                    pass

        except NameError as er:
            print("Error in Repeat key thread is: %s" % (er))

    def HotKeyRegistry(self):
        for i in range(1,10):
            keyboard.add_hotkey('ctrl+%s' % i, AddColor, args=[i])
            keyboard.add_hotkey('f%s' % i, ControlSend, args=[i], suppress=True)
        keyboard.wait("ctrl+shift+end")

    def AddColor(self, value):
        if objGui:
            objGui.tab["Tab %s" % value]["Color"].append(   
                objColor.GetPixelColor()
            )
        else:
            pass

    def ControlSend(self, value):
        if objGui:
            if objGui.tab["HotKey"]:
                for hwnd in objGui.tab["Handler"]:
                    objKeyBoard.ControlSend(objGui.tab["Tab %s" % value], hwnd, objGui.tab["Tab %s" % value]["Key"].GetValue())
            else:
                pass

