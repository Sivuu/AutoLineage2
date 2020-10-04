import os
import sys
import time
import wx
import threading
import base64
import ntplib
import json
from pykeyboard import keyboard as kb
from Memory import Memory
from pynput import keyboard
import mouse as ms
import win32gui
import win32con
import win32api
from datetime import datetime, timezone, timedelta
from L2Handle import L2Handle
from Keyboard import Keyboard
from Color import Color

class UserGui(wx.Frame):
    def __init__(self, parent, title):
        # Khai bao tham so cua GUI
        self.guiKB = Keyboard()
        self.memREAD = Memory()
        self.lockThread = threading.Lock()
        self.thdRepeat = threading.Thread(target=self.RepeatKeyThread, daemon=True)
        self.thdHeal = threading.Thread(target=self.HealCheckThread, daemon=True)
        self.thdHotKey = threading.Thread(target=self.HotKeyRegistry, daemon=True)
        self.thdMark = threading.Thread(target=self.MarkThread, daemon=True)
        self.encode = os.popen("wmic diskdrive get serialnumber").read().split()[-1]
        f = open(os.path.join(os.path.abspath(os.getcwd()), "key.txt"), "r")
        keytemp = base64.b64decode(f.read().encode("utf-8")).decode("utf-8")
        self.keyCode = keytemp.split(";")[0]
        self.keyTime = keytemp.split(";")[1] + "+00:00"
        self.UIDict = dict()
        self.UIDict["RepeatThread"] = False
        self.UIDict["HotKeyThread"] = False
        self.UIDict["HealThread"] = False
        self.UIDict["MarkThread"] = False

        # self.thdRepeat.start()
        # self.thdHeal.start()
        # self.thdHotKey.start()
        # self.thdMark.start()

        # Khoi tao cua so ung dung
        wx.Frame.__init__(self, parent, title=title, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.CreateStatusBar()
        sizerFrame = wx.GridBagSizer(0, 0)
        sizerFrame.SetFlexibleDirection(wx.BOTH)
        sizerFrame.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # Choice box de lua chon Handle setup cho tool
        self.UIDict["Handle"] = list()
        self.UIDict["L2Handle"] = dict()
        for hwnd in self.GetHWND():
            title = win32gui.GetWindowText(hwnd)
            self.UIDict["Handle"].append(title + ';Not Note')
            self.UIDict["L2Handle"][title] = L2Handle(hwnd, title)

        self.UIDict["ChoiceHandle"] = wx.Choice(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(250,30), choices=self.UIDict["Handle"], style=0)
        self.UIDict["ChoiceHandle"].SetSelection(0)
        self.UIDict["ChoiceHandle"].Bind(wx.EVT_CHOICE, self.ChoiceSelected)
        sizerFrame.Add(self.UIDict["ChoiceHandle"], wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        # Button Load Profile
        self.UIDict["btLoadProfile"] = wx.Button(self, wx.ID_ANY, label='Load Profile', size=(250,30))
        self.UIDict["btLoadProfile"].Bind(wx.EVT_BUTTON, self.LoadProfileClick)
        sizerFrame.Add(self.UIDict["btLoadProfile"], wx.GBPosition(2, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Save Profile
        self.UIDict["btSaveProfile"] = wx.Button(self, wx.ID_ANY, label='Save Profile', size=(250,30))
        self.UIDict["btSaveProfile"].Bind(wx.EVT_BUTTON, self.SaveProfileClick)
        sizerFrame.Add(self.UIDict["btSaveProfile"], wx.GBPosition(3, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Get Handle
        self.UIDict["btGetHandle"] = wx.Button(self, wx.ID_ANY, label='Get Windows', size=(250,30))
        self.UIDict["btGetHandle"].Bind(wx.EVT_BUTTON, self.GetHandleClick)
        sizerFrame.Add(self.UIDict["btGetHandle"], wx.GBPosition(4, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Repeat Key
        self.UIDict["btRun"] = wx.Button(self, wx.ID_ANY, label='Repeat Key', size=(250,30))
        self.UIDict["btRun"].Bind(wx.EVT_BUTTON, self.RepeatKeyClick)
        sizerFrame.Add(self.UIDict["btRun"], wx.GBPosition(5, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Hot Key
        self.UIDict["btHotKey"] = wx.Button(self, wx.ID_ANY, label='Hot Key', size=(250,30))
        self.UIDict["btHotKey"].Bind(wx.EVT_BUTTON, self.HotKeyClick)
        sizerFrame.Add(self.UIDict["btHotKey"], wx.GBPosition(6, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button HPMPCP
        self.UIDict["btHeal"] = wx.Button(self, wx.ID_ANY, label='Heal', size=(250,30))
        self.UIDict["btHeal"].Bind(wx.EVT_BUTTON, self.HealClick)
        sizerFrame.Add(self.UIDict["btHeal"], wx.GBPosition(7, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Mark
        self.UIDict["btMark"] = wx.Button(self, wx.ID_ANY, label='Mark Assit', size=(250,30))
        self.UIDict["btMark"].Bind(wx.EVT_BUTTON, self.MarkClick)
        sizerFrame.Add(self.UIDict["btMark"], wx.GBPosition(8, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Exit
        self.UIDict["btExit"] = wx.Button(self, wx.ID_ANY, label='Exit', size=(250,30))
        self.UIDict["btExit"].Bind(wx.EVT_BUTTON, self.ExitClick)
        sizerFrame.Add(self.UIDict["btExit"], wx.GBPosition(11, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Thiet lap Panel danh cho Handle Infomation --------------------
        self.UIDict["panelHandle"] = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        sizerFrame.Add(self.UIDict["panelHandle"], wx.GBPosition(0, 1), wx.GBSpan(19, 47), wx.ALL, 5)
        sizerPanel = wx.GridBagSizer(0, 0)
        sizerPanel.SetFlexibleDirection(wx.BOTH)
        sizerPanel.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # Label + Name cua Lineage II Tab------------------------
        self.UIDict["panelHandleName"] = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Lineage 2 Tab")
        sizerPanel.Add(self.UIDict["panelHandleName"], wx.GBPosition(0,0), wx.GBSpan(1,2), wx.ALL, 5)

        self.UIDict["panelHandleNote"] = wx.TextCtrl(self.UIDict["panelHandle"], id=wx.ID_ANY, value="Not Active")
        sizerPanel.Add(self.UIDict["panelHandleNote"], wx.GBPosition(0,2), wx.GBSpan(1,2), wx.ALL, 5)

        # Nhom Label KeyCombine Information
        pnKeyName = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Key Combine")
        sizerPanel.Add(pnKeyName, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5)
        pnRepeat = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Repeat Time")
        sizerPanel.Add(pnRepeat, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)
        pnSleep = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Sleep Time")
        sizerPanel.Add(pnSleep, wx.GBPosition(1, 2), wx.GBSpan(1, 1), wx.ALL, 5)
        pnActiveRepeat = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Repeat")
        sizerPanel.Add(pnActiveRepeat, wx.GBPosition(1, 3), wx.GBSpan(1, 1), wx.ALL, 5)

        # Form thiet lap thong tin moi key ung voi tung cua so------------------
        self.UIDict["CombineKey"] = dict()
        for i in range(2, 11):
            self.UIDict["CombineKey"]["Key%s" % (i-1)] = dict()

            self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnKeyName"] = wx.TextCtrl(self.UIDict["panelHandle"], id=wx.ID_ANY, value="n%s" % (i-1))
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnKeyName"], wx.GBPosition(i, 0), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

            self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnRepeat"] = wx.TextCtrl(self.UIDict["panelHandle"], id=wx.ID_ANY, value="600")
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnRepeat"], wx.GBPosition(i, 1), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

            self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnSleep"] = wx.TextCtrl(self.UIDict["panelHandle"], id=wx.ID_ANY, value="2")
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnSleep"], wx.GBPosition(i, 2), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

            self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveRepeat"] = wx.CheckBox(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Y/N")
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveRepeat"], wx.GBPosition(i, 3), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

        # Button Save Key
        self.UIDict["btSaveKey"] = wx.Button(self.UIDict["panelHandle"],id=wx.ID_ANY, label='Save Key')
        self.UIDict["btSaveKey"].Bind(wx.EVT_BUTTON, self.SaveKeyClick)
        sizerPanel.Add(self.UIDict["btSaveKey"], wx.GBPosition(12, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        # Button HP/MP/CP
        self.UIDict["btHPMPCP"] = wx.Button(self.UIDict["panelHandle"],id=wx.ID_ANY, label='HP/MP/CP')
        self.UIDict["btHPMPCP"].Bind(wx.EVT_BUTTON, self.HPCPMPClick)
        sizerPanel.Add(self.UIDict["btHPMPCP"], wx.GBPosition(12, 1), wx.GBSpan(1, 1), wx.ALL, 5)

        # Button HP/MP/CP
        self.UIDict["lbHPMPCP"] = wx.StaticText(self.UIDict["panelHandle"],id=wx.ID_ANY, label='HP--/MP--/CP--')
        sizerPanel.Add(self.UIDict["lbHPMPCP"], wx.GBPosition(12, 2), wx.GBSpan(1, 1), wx.ALL, 5)

        # Active Assist Key
        self.UIDict["cbMark"] = wx.CheckBox(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Mark Target by Key F12")
        sizerPanel.Add(self.UIDict["cbMark"], wx.GBPosition(13, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        self.UIDict["panelHandle"].SetSizer(sizerPanel)
        self.UIDict["panelHandle"].Layout()

        # Thiet lap Sizer Main-------------------------------------------
        self.SetSizer(sizerFrame)
        sizerFrame.Fit(self)
        self.SetClientSize(sizerFrame.GetSize() + (+5, -90))
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
            dateret = datetime.strptime(
                strconvert, '%Y-%m-%d %H:%M:%S.%f%z').astimezone(timezone.utc)
        except:
            return (self.TakeNTPTime() - timedelta(days=1))
        else:
            return dateret

    def CheckKeyCode(self):
        """ Kiem tra KeyCode co hop le"""
        self.encode = os.popen(
            "wmic diskdrive get serialnumber").read().split()[-1]
        f = open(os.path.join(os.path.abspath(os.getcwd()), "key.txt"), "r")
        keytemp = base64.b64decode(f.read().encode("utf-8")).decode("utf-8")
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

    def GetL2Handle(self, title):
        for key, l2handle in self.UIDict["L2Handle"].items():
            if l2handle.HandleName == title:
                return l2handle
                break

    def ChoiceSelected(self, event):    
        self.UpdatePanel()

    def UpdateHandle(self):
        self.UIDict["Handle"].clear()
        for items in self.UIDict["ChoiceHandle"].Items:
            self.UIDict["Handle"].append(items)

    def UpdateChoiceBox(self):
        self.UIDict["ChoiceHandle"].Clear()
        for hwnd in self.GetHWND():
            self.UIDict["ChoiceHandle"].Append(win32gui.GetWindowText(hwnd) + ';Not Note' )
        #clear choice roi append lai tung thanh phan voi modifi
        for st in range(self.UIDict["ChoiceHandle"].GetCount()):
            strfirst = self.UIDict["ChoiceHandle"].GetString(st)
            title = strfirst.split(';')[0]
            strlast = title + ';' + self.UIDict["L2Handle"][title].HandleNote
            self.UIDict["ChoiceHandle"].SetString(st, strlast)
        self.UIDict["ChoiceHandle"].SetSelection(0)

    def UpdatePanel(self):
        title = self.UIDict["ChoiceHandle"].GetString(self.UIDict["ChoiceHandle"].GetSelection()).split(';')[0]
        l2f = self.GetL2Handle(title)
        if l2f:
            self.lockThread.acquire()
            self.UIDict["panelHandleName"].SetLabel(l2f.HandleName)
            self.UIDict["panelHandleNote"].SetLabel(l2f.HandleNote)
            for i in range(2, 11):
                self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnKeyName"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].Key)
                self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnRepeat"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].RepeatTime)
                self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnSleep"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].SleepTime)
                self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveRepeat"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].ActiveRepeat)
            self.UIDict["cbMark"].SetValue(l2f.Mark)
            self.lockThread.release()

    def GetHandleClick(self, event):
        """Get new handle if new windows is open"""
        
        for hwnd in self.GetHWND():
            title = win32gui.GetWindowText(hwnd)      
            if self.UIDict["L2Handle"].get(title) == None:
                self.lockThread.acquire()
                self.UIDict["Handle"].append(title + ';Not Note')
                self.UIDict["L2Handle"][title] = L2Handle(hwnd, title)
                self.UIDict["ChoiceHandle"].Append(title)
                self.lockThread.release()
            elif self.UIDict["L2Handle"][title].HandleValue == 0:
                self.lockThread.acquire()
                self.UIDict["L2Handle"][title].HandleValue = hwnd
                self.lockThread.release()
        self.RemoveHandleNotUsed()
        self.UpdateChoiceBox()
        self.UpdatePanel()

    def RemoveHandleNotUsed(self):
        """Remove the handle that is not use from UIDict"""
        
        listH = list()
        for h in self.GetHWND():
            listH.append(win32gui.GetWindowText(h))

        dictTemp = list(self.UIDict["L2Handle"])
        for title in dictTemp:
            if not (title in listH) and (title in self.UIDict["Handle"]):
                self.lockThread.acquire()
                fullTitle = title + ';' + self.UIDict["L2Handle"][title].HandleNote
                self.UIDict["Handle"].remove(fullTitle)
                self.UIDict["ChoiceHandle"].Delete(self.UIDict["ChoiceHandle"].FindString(title))
                self.lockThread.release()     

    def SaveKeyClick(self, event):
        """Event for Save Key"""
        old = self.UIDict["ChoiceHandle"].GetString(self.UIDict["ChoiceHandle"].GetSelection())
        title = old.split(';')[0]
        l2f = self.GetL2Handle(title)
        self.UIDict["L2Handle"][str(l2f.HandleName)].HandleNote =  self.UIDict["panelHandleNote"].GetValue()
        newtitle = title + ';' + self.UIDict["panelHandleNote"].GetValue()
        for num in range(len(self.UIDict["Handle"])):
            if self.UIDict["Handle"][num] == old:
                self.UIDict["Handle"][num] = newtitle
        self.UIDict["ChoiceHandle"].SetString(self.UIDict["ChoiceHandle"].GetSelection(), newtitle)
                
        for i in range(2, 11):
            self.lockThread.acquire()
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (i-1)].Key = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnKeyName"].GetValue()
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (i-1)].RepeatTime = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnRepeat"].GetValue()
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (i-1)].SleepTime = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnSleep"].GetValue()
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (i-1)].ActiveRepeat = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveRepeat"].GetValue()
            self.UIDict["L2Handle"][str(l2f.HandleName)].Mark = self.UIDict["cbMark"].GetValue()
            self.lockThread.release()

    def SaveProfileClick(self, event):
        """Event for save profiles"""
        # Save File Dialog    
        with wx.FileDialog(self, "Select Profile", wildcard="Json file (*.json)|*.json",style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as SaveFile:
            if SaveFile.ShowModal() == wx.ID_CANCEL:
                return
            path = SaveFile.GetPath()
            # Processing
            self.lockThread.acquire()
            fileDict = dict()
            fileDict["Handle"] = self.UIDict["Handle"]
            for key, l2 in self.UIDict["L2Handle"].items():
                fileDict[key] = dict()
                fileDict[key]["HandleName"] = l2.HandleName
                # fileDict[key]["HandleValue"] = l2.HandleValue
                fileDict[key]["HandleNote"] = l2.HandleNote
                fileDict[key]["ActiveTime"] = l2.ActiveTime
                fileDict[key]["Active"] = l2.Active
                fileDict[key]["Condition"] = l2.Condition
                fileDict[key]["DictKeyCombine"]= dict()
                for i in range(1,10):
                    fileDict[key]["DictKeyCombine"]["Key%s" % i] = dict()
                    fileDict[key]["DictKeyCombine"]["Key%s" % i]["Key"] = l2.DictKeyCombine["Key%s" % i].Key
                    fileDict[key]["DictKeyCombine"]["Key%s" % i]["RepeatTime"] = l2.DictKeyCombine["Key%s" % i].RepeatTime
                    fileDict[key]["DictKeyCombine"]["Key%s" % i]["SleepTime"] = l2.DictKeyCombine["Key%s" % i].SleepTime
                    fileDict[key]["DictKeyCombine"]["Key%s" % i]["ActiveRepeat"] = l2.DictKeyCombine["Key%s" % i].ActiveRepeat
                    fileDict[key]["DictKeyCombine"]["Key%s" % i]["LastHit"] = 0 # l2.DictKeyCombine["Key%s" % i].LastHit
                fileDict[key]["Mark"] = l2.Mark
            self.lockThread.release()
            try:
                with open(path, "w") as l2config:
                    json.dump(fileDict, l2config)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % path)

    def LoadProfileClick(self, event): 
        """Event for load profiles"""
        # Open File Dialog
        with wx.FileDialog(self, "Select Profile", "", "", "Json file (*.json)|*.json", wx.FD_OPEN|wx.FD_FILE_MUST_EXIST) as OpenFile:
            if OpenFile.ShowModal() ==  wx.ID_CANCEL:
                return
            path = OpenFile.GetPath()
            # Processing
            tempDict = dict()
            with open(path, "r") as l2config:
                if os.stat(path).st_size != 0:
                    tempDict = json.load(l2config)
                    self.UIDict["Handle"] = tempDict["Handle"]
                    for key, l2 in tempDict.items():
                        if key != "Handle":
                            if self.UIDict["L2Handle"].get(key) == None:
                                self.UIDict["L2Handle"][key] = L2Handle(win32gui.FindWindowEx(None,None,None,key), key)
                                
                            self.UIDict["L2Handle"][key].HandleName = tempDict[key]["HandleName"]
                            # self.UIDict["L2Handle"][key].HandleValue = win32gui.FindWindowEx(None,None,None,key)
                            self.UIDict["L2Handle"][key].HandleNote = tempDict[key]["HandleNote"]
                            self.UIDict["L2Handle"][key].ActiveTime = tempDict[key]["ActiveTime"]
                            self.UIDict["L2Handle"][key].Active = tempDict[key]["Active"]
                            self.UIDict["L2Handle"][key].Condition = tempDict[key]["Condition"]
                            for k, kc in tempDict[key]["DictKeyCombine"].items():
                                self.UIDict["L2Handle"][key].DictKeyCombine[k].Key = kc["Key"]
                                self.UIDict["L2Handle"][key].DictKeyCombine[k].RepeatTime = kc["RepeatTime"]
                                self.UIDict["L2Handle"][key].DictKeyCombine[k].SleepTime = kc["SleepTime"]
                                self.UIDict["L2Handle"][key].DictKeyCombine[k].ActiveRepeat = kc["ActiveRepeat"]
                                self.UIDict["L2Handle"][key].DictKeyCombine[k].LastHit = 0 # kc["LastHit"]
                            self.UIDict["L2Handle"][key].Mark = tempDict[key]["Mark"]

        self.UpdateChoiceBox()
        self.UpdatePanel()

    def RepeatKeyClick(self, event):
        """Event for Run Check when its clicked"""
        if not self.UIDict["RepeatThread"]:
            if self.CheckKeyCode():
                self.UIDict["RepeatThread"] = True
                self.thdRepeat.start()
                self.UIDict["btRun"].SetLabel("Repeat Key: On")
            else:
                wx.MessageBox("Incorrect key or Time is expired", "New Key Code Require", wx.OK)
        else:
            self.UIDict["RepeatThread"] = False
            self.thdRepeat.join()
            self.UIDict["btRun"].SetLabel("Repeat Key: Off")

    def HotKeyClick(self, event):
        """Event for Hot Key when its clicked"""
        if not self.UIDict["HotKeyThread"]:
            if self.CheckKeyCode():
                self.UIDict["HotKeyThread"] = True
                self.thdHotKey.start()
                self.UIDict["btHotKey"].SetLabel("Hot Key: On")
            else:
                wx.MessageBox("Incorrect key or Time is expired", "New Key Code Require", wx.OK)
        else:
            self.UIDict["HotKeyThread"] = False
            self.thdHotKey.join()
            self.UIDict["btHotKey"].SetLabel("Hot Key: Off")

    def HealClick(self, event):
        """Event for HPMPCP when its clicked"""
        # if True:
        if not self.UIDict["HealThread"]:
            if self.CheckKeyCode():
                self.UIDict["HealThread"] = True
                self.thdHeal.start()
                self.UIDict["btHeal"].SetLabel("Heal: On")
            else:
                wx.MessageBox("Incorrect key or Time is expired", "New Key Code Require", wx.OK)
        else:
            self.UIDict["HealThread"] = False
            self.thdHeal.join()
            self.UIDict["btHeal"].SetLabel("Heal: Off")
    
    def MarkClick(self, event):
        """Event for Mark when its clicked"""
        # if True:
        if not self.UIDict["MarkThread"]:
            if self.CheckKeyCode():
                self.UIDict["MarkThread"] = True
                self.thdMark.start()
                self.UIDict["btMark"].SetLabel("Mark Assist: On")
            else:
                wx.MessageBox("Incorrect key or Time is expired", "New Key Code Require", wx.OK)
        else:
            self.UIDict["MarkThread"] = False
            self.thdMark.join()
            self.UIDict["btMark"].SetLabel("Mark Assist: Off")

    def HPCPMPClick(self, event):
        """Event for Info Button"""
        
        title = self.UIDict["ChoiceHandle"].GetString(self.UIDict["ChoiceHandle"].GetSelection()).split(';')[0]
        note = self.UIDict["ChoiceHandle"].GetString(self.UIDict["ChoiceHandle"].GetSelection())
        l2f = self.GetL2Handle(title)
        cFrame = wx.Frame(None, title="Setup for %s" % self.UIDict["ChoiceHandle"].GetString(self.UIDict["ChoiceHandle"].GetSelection()))
        sizerInfo = wx.GridBagSizer(0, 0)
        sizerInfo.SetFlexibleDirection(wx.BOTH)
        sizerInfo.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        self.UpdateHandle()
        cbCharName = wx.Choice(cFrame, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, choices=self.UIDict["Handle"], style=0)
        sizerInfo.Add(cbCharName, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)
        lbValue = wx.StaticText(cFrame, id=wx.ID_ANY, label="Value: ")
        sizerInfo.Add(lbValue, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)
        lbKey = wx.StaticText(cFrame, id=wx.ID_ANY, label="Key: ")
        sizerInfo.Add(lbKey, wx.GBPosition(0, 2), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

        # HP Select
        lbHP = wx.StaticText(cFrame, id=wx.ID_ANY, label="HP <= ")
        sizerInfo.Add(lbHP, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)
        tcHP = wx.TextCtrl(cFrame, id=wx.ID_ANY, value=str(l2f.Condition["HPHeal"]))
        sizerInfo.Add(tcHP, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)
        tcHPKey = wx.TextCtrl(cFrame, id=wx.ID_ANY, value=l2f.Condition["HPKey"])
        sizerInfo.Add(tcHPKey, wx.GBPosition(1, 2), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

        # MP Select
        lbMP = wx.StaticText(cFrame, id=wx.ID_ANY, label="MP <= ")
        sizerInfo.Add(lbMP, wx.GBPosition(2, 0), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)
        tcMP = wx.TextCtrl(cFrame, id=wx.ID_ANY, value=str(l2f.Condition["MPRecharge"]))
        sizerInfo.Add(tcMP, wx.GBPosition(2, 1), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)
        tcMPKey = wx.TextCtrl(cFrame, id=wx.ID_ANY, value=l2f.Condition["MPKey"])
        sizerInfo.Add(tcMPKey, wx.GBPosition(2, 2), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

        # CP Select
        lbCP = wx.StaticText(cFrame, id=wx.ID_ANY, label="CP <= ")
        sizerInfo.Add(lbCP, wx.GBPosition(3, 0), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)
        tcCP = wx.TextCtrl(cFrame, id=wx.ID_ANY, value=str(l2f.Condition["CPHeal"]))
        sizerInfo.Add(tcCP, wx.GBPosition(3, 1), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)
        tcCPKey = wx.TextCtrl(cFrame, id=wx.ID_ANY, value=l2f.Condition["CPKey"])
        sizerInfo.Add(tcCPKey, wx.GBPosition(3, 2), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

        def SaveHPMPCP(event):
            tit = cbCharName.GetString(cbCharName.GetSelection()).split(';')[0]
            self.lockThread.acquire()
            if tit != '':
                handle = self.GetL2Handle(tit)
                l2f.Condition["Char"] = handle.HandleName
            
            l2f.Condition["HPHeal"] = tcHP.GetValue()
            l2f.Condition["HPKey"] = tcHPKey.GetValue()
            l2f.Condition["MPRecharge"] = tcMP.GetValue()
            l2f.Condition["MPKey"] = tcMPKey.GetValue()
            l2f.Condition["CPHeal"] = tcCP.GetValue()
            l2f.Condition["CPKey"] = tcCPKey.GetValue()
            self.lockThread.release()
            cFrame.Close()

        # Button Save Info
        btSave = wx.Button(cFrame, id=wx.ID_ANY, label="Save", style=0)
        btSave.Bind(wx.EVT_BUTTON, SaveHPMPCP)
        sizerInfo.Add(btSave, wx.GBPosition(4, 1), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

        cFrame.SetSizer(sizerInfo)
        sizerInfo.Fit(cFrame)
        cFrame.SetClientSize(sizerInfo.GetSize() + (5, 5))
        cFrame.Show(True)
        
    def ExitClick(self, event):
        """Event for Exit Button when its clicked"""
        self.Close()

    def RepeatKeyThread(self):
        """Function to processing Repeat Key"""
        try:
            while self.UIDict["RepeatThread"]:
                if not self.guiKB.CheckModifierKey():
                    for nhwnd, hwnd in self.UIDict["L2Handle"].items():
                        for nkey, key in hwnd.DictKeyCombine.items():
                            if key.ActiveRepeat:
                                cdTime = int(float(key.RepeatTime))
                                lhTime = key.LastHit
                                # Kiem tra dieu kien cast lap theo so giay,
                                # Ngoai ra moi cua so cung can phai sleep 1 thoi gian nhat dinh, tranh chen key
                                if (cdTime + lhTime) < time.time() and hwnd.ActiveTime < time.time():
                                    key.LastHit = time.time()
                                    slTime = int(float(key.SleepTime))
                                    hwnd.ActiveTime = time.time() + slTime
                                    self.guiKB.ControlSend(hwnd, key.Key)     
                time.sleep(0.1)

        except NameError as er:
            print("Error in Repeat key thread is: %s" % (er))

    def HotKeyRegistry(self):
        """Hot key repeat"""
        kb.add_hotkey('ctrl+s', self.RunClick, args=[0], suppress=True)
        kb.add_hotkey((79), self.ControlSend, args=[1], suppress=True)
        kb.add_hotkey((80), self.ControlSend, args=[2], suppress=True)
        kb.add_hotkey((81), self.ControlSend, args=[3], suppress=True)
        kb.add_hotkey((75), self.ControlSend, args=[4], suppress=True)
        kb.add_hotkey((76), self.ControlSend, args=[5], suppress=True)
        kb.add_hotkey((77), self.ControlSend, args=[6], suppress=True)
        kb.add_hotkey((71), self.ControlSend, args=[7], suppress=True)
        kb.add_hotkey((72), self.ControlSend, args=[8], suppress=True)
        kb.add_hotkey((73), self.ControlSend, args=[9], suppress=True)
        kb.wait("ctrl+shift+end")

    def ControlSend(self, value):
        """Send key when hotkey is pressed"""
        if self.UIDict["HotKeyThread"]:
            for name, hwnd in self.UIDict["L2Handle"].items():
                self.lockThread.acquire()
                key = hwnd.DictKeyCombine["Key%s" % value].Key
                slTime = int(float(hwnd.DictKeyCombine["Key%s" % value].SleepTime))
                hwnd.ActiveTime = time.time() + slTime
                self.guiKB.ControlSend(hwnd, "n%s" % value)
                self.lockThread.release()

    def HealCheckThread(self):
        """Threading for healing/ recharging"""
        while self.UIDict["HealThread"]:
            if not self.guiKB.CheckModifierKey():
                for nhwnd, l2client in self.UIDict["L2Handle"].items():
                    if win32gui.IsWindowVisible(l2client.HandleValue):
                        baseAddress = self.memREAD.GetBaseAddressModule(l2client.PID, "NWindow.DLL", 0x01320C1C)
                        l2client.HP = self.memREAD.ReadLineageOffsetValueInt32(l2client.PID, baseAddress, 0xA4, 0x4, 0x1F0, 0x3C, 0x4C, 0x220).value
                        l2client.MP = self.memREAD.ReadLineageOffsetValueInt32(l2client.PID, baseAddress, 0xA4, 0x4, 0x1F0, 0x3C, 0x60, 0x220).value
                        l2client.CP = self.memREAD.ReadLineageOffsetValueInt32(l2client.PID, baseAddress, 0xA4, 0x4, 0x1F0, 0x3C, 0x38, 0x220).value

                for nhwnd, l2client in self.UIDict["L2Handle"].items():
                    if win32gui.IsWindowVisible(l2client.HandleValue):
                        for hwnd2, l2target in self.UIDict["L2Handle"].items():
                            if win32gui.IsWindowVisible(l2target.HandleValue):
                                if l2target.HP > 0 and l2target.HP < int(l2client.Condition["HPHeal"]) and l2client.Condition["HPKey"] != "Notset":
                                    self.guiKB.ControlSend(l2client, l2client.Condition["HPKey"])
                                if l2target.MP > 0 and l2target.MP < int(l2client.Condition["MPRecharge"]) and l2client.Condition["MPKey"] != "Notset":
                                    self.guiKB.ControlSend(l2client, l2client.Condition["MPKey"])
                                if l2target.CP > 0 and l2target.CP < int(l2client.Condition["CPHeal"]) and l2client.Condition["CPKey"] != "Notset":
                                    self.guiKB.ControlSend(l2client, l2client.Condition["CPKey"])
                
                                
                title = self.UIDict["ChoiceHandle"].GetString(self.UIDict["ChoiceHandle"].GetSelection()).split(';')[0]
                l2f = self.GetL2Handle(title)                                                                                                
                strLabel = "HP: " + str(l2f.HP) + "/MP: " + str(l2f.MP) + "/CP: " + str(l2f.CP)
                self.UIDict["lbHPMPCP"].SetLabel(strLabel)
            time.sleep(0.2)

    def MarkThread(self):
        """Thread for mark target and support assistance"""
        while self.UIDict["MarkThread"]:
            if not self.guiKB.CheckModifierKey():
                for key, l2client in self.UIDict["L2Handle"].items():
                    if self.UIDict["L2Handle"][key].Mark == True and self.CheckTargetIsMarking(l2client):
                        self.guiKB.ControlSend(l2client,"f12")
                        time.sleep(1)
    
    def CheckTargetIsMarking(self, l2client):
            baseAddress = self.memREAD.GetBaseAddressModule(l2client.PID, "NWindow.DLL", 0x01320C1C)
            checkvalue = self.memREAD.ReadLineageOffsetValueInt32(l2client.PID, baseAddress, 0xA4, 0x4, 0xE0, 0x224, 0x220, 0x34, 0xCD4).value
            if checkvalue == 37748744:
                return True
            else:
                return False