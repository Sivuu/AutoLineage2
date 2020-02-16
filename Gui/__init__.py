import os
import sys
import time
import wx
import threading
import base64
import ntplib
import json
from pykeyboard import keyboard as kb
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
        self.lockThread = threading.Lock()
        self.thdRepeat = threading.Thread(target=self.RepeatKeyThread, daemon=True)
        self.thdColor = threading.Thread(target=self.ColorCheckThread, daemon=True)
        self.thdHotKey = threading.Thread(target=self.HotKeyRegistry, daemon=True)
        self.encode = os.popen(
            "wmic diskdrive get serialnumber").read().split()[-1]
        f = open(os.path.join(os.path.abspath(os.getcwd()), "key.txt"), "r")
        keytemp = base64.b64decode(f.read().encode("utf-8")).decode("utf-8")
        self.keyCode = keytemp.split(";")[0]
        self.keyTime = keytemp.split(";")[1] + "+00:00"
        self.UIDict = dict()
        self.UIDict["ToolRun"] = False
        self.UIDict["ColorRegistry"] = dict()
        self.UIDict["ColorRegistry"]['None'] = dict()
        self.UIDict["ListColor"] = ['None','C1','C2','C3','C4','C5','C6','C7','C8','C9']

        self.thdRepeat.start()
        self.thdColor.start()
        self.thdHotKey.start()
        # self.HotKey()

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

        self.UIDict["ChoiceHandle"] = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.UIDict["Handle"], 0)
        self.UIDict["ChoiceHandle"].SetSelection(0)
        self.UIDict["ChoiceHandle"].Bind(wx.EVT_CHOICE, self.ChoiceSelected)
        sizerFrame.Add(self.UIDict["ChoiceHandle"], wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL, 5)

        # Button Start/Run
        self.UIDict["btRun"] = wx.Button(self, wx.ID_ANY, label='Run', size=(150,30))
        self.UIDict["btRun"].Bind(wx.EVT_BUTTON, self.RunClick)
        sizerFrame.Add(self.UIDict["btRun"], wx.GBPosition(2, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Get Handle
        self.UIDict["btGetHandle"] = wx.Button(
            self, wx.ID_ANY, label='Get Windows', size=(150,30))
        self.UIDict["btGetHandle"].Bind(wx.EVT_BUTTON, self.GetHandleClick)
        sizerFrame.Add(self.UIDict["btGetHandle"], wx.GBPosition(3, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Save Profile
        self.UIDict["btSaveProfile"] = wx.Button(self, wx.ID_ANY, label='Save Profile', size=(150,30))
        self.UIDict["btSaveProfile"].Bind(wx.EVT_BUTTON, self.SaveProfileClick)
        sizerFrame.Add(self.UIDict["btSaveProfile"], wx.GBPosition(4, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Load Profile
        self.UIDict["btLoadProfile"] = wx.Button(self, wx.ID_ANY, label='Load Profile', size=(150,30))
        self.UIDict["btLoadProfile"].Bind(wx.EVT_BUTTON, self.LoadProfileClick)
        sizerFrame.Add(self.UIDict["btLoadProfile"], wx.GBPosition(5, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Exit
        self.UIDict["btListColor"] = wx.Button(self, wx.ID_ANY, label='List Color', size=(150,30))
        self.UIDict["btListColor"].Bind(wx.EVT_BUTTON, self.ListColorClick)
        sizerFrame.Add(self.UIDict["btListColor"], wx.GBPosition(6, 0), wx.GBSpan(1, 1), wx.CENTER|wx.ALL, 5)

        # Button Exit
        self.UIDict["btExit"] = wx.Button(self, wx.ID_ANY, label='Exit', size=(150,30))
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
        # Button Save Key
        self.UIDict["btSaveKey"] = wx.Button(self.UIDict["panelHandle"],id=wx.ID_ANY, label='Save Key')
        self.UIDict["btSaveKey"].Bind(wx.EVT_BUTTON, self.SaveKeyClick)
        sizerPanel.Add(self.UIDict["btSaveKey"], wx.GBPosition(0, 4), wx.GBSpan(1, 2), wx.ALL, 5)

        pnKeyName = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Key Combine")
        sizerPanel.Add(pnKeyName, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALL, 5)
        pnRepeat = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Repeat Time")
        sizerPanel.Add(pnRepeat, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALL, 5)
        pnSleep = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Sleep Time")
        sizerPanel.Add(pnSleep, wx.GBPosition(1, 2), wx.GBSpan(1, 1), wx.ALL, 5)
        pnActiveRepeat = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Repeat")
        sizerPanel.Add(pnActiveRepeat, wx.GBPosition(1, 3), wx.GBSpan(1, 1), wx.ALL, 5)
        pnActiveColor = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Color")
        sizerPanel.Add(pnActiveColor, wx.GBPosition(1, 4), wx.GBSpan(1, 1), wx.ALL, 5)
        pnActiveHotKey = wx.StaticText(self.UIDict["panelHandle"], id=wx.ID_ANY, label="HotKey")
        sizerPanel.Add(pnActiveHotKey, wx.GBPosition(1, 5), wx.GBSpan(1, 1), wx.ALL, 5)

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

            self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveColor"] = wx.Choice(self.UIDict["panelHandle"], id=wx.ID_ANY, choices=self.UIDict["ListColor"], style=0)
            self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveColor"].SetSelection(0)
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveColor"], wx.GBPosition(i, 4), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

            self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveHotKey"] = wx.CheckBox(self.UIDict["panelHandle"], id=wx.ID_ANY, label="Y/N")
            self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveHotKey"].SetValue(True)
            sizerPanel.Add(self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveHotKey"], wx.GBPosition(i, 5), wx.GBSpan(1, 1), wx.ALL | wx.CENTER, 5)

        self.UIDict["panelHandle"].SetSizer(sizerPanel)
        self.UIDict["panelHandle"].Layout()

        # Thiet lap Sizer Main-------------------------------------------
        self.SetSizer(sizerFrame)
        sizerFrame.Fit(self)
        self.SetClientSize(sizerFrame.GetSize() + (5, -100))
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
            self.UIDict["panelHandleName"].SetLabel(l2f.HandleName)
            self.UIDict["panelHandleNote"].SetLabel(l2f.HandleNote)
            for i in range(2, 11):
                self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnKeyName"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].Key)
                self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnRepeat"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].RepeatTime)
                self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnSleep"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].SleepTime)
                self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnActiveRepeat"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].ActiveRepeat)
                self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnActiveColor"].Clear()
                self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnActiveColor"].AppendItems(self.UIDict["ListColor"])
                posColorChoice = self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnActiveColor"].FindString(l2f.DictKeyCombine["Key%s" % (i-1)].ActiveColor)
                self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnActiveColor"].SetSelection(posColorChoice)
                self.UIDict["CombineKey"]["Key%s" % (
                    i-1)]["pnActiveHotKey"].SetValue(l2f.DictKeyCombine["Key%s" % (i-1)].ActiveHotKey)

    def RunClick(self, event):
        """Event for Run Check when its clicked"""
        if self.CheckKeyCode():
            # if True:
            if not self.UIDict["ToolRun"]:
                self.UIDict["ToolRun"] = True
                self.UIDict["btRun"].SetLabel("Stop")
            else:
                self.UIDict["ToolRun"] = False
                self.UIDict["btRun"].SetLabel("Run")
        else:
            wx.MessageBox("Incorrect key or Time is expired", "New Key Code Require", wx.OK)

    def GetHandleClick(self, event):
        self.lockThread.acquire()
        for hwnd in self.GetHWND():
            title = win32gui.GetWindowText(hwnd)      
            if self.UIDict["L2Handle"].get(title) == None:
                self.UIDict["Handle"].append(title + ';Not Note')
                self.UIDict["L2Handle"][title] = L2Handle(hwnd, title)
                self.UIDict["ChoiceHandle"].Append(title)
            elif self.UIDict["L2Handle"][title].HandleValue == 0:
                self.UIDict["L2Handle"][title].HandleValue = hwnd
        self.RemoveHandleNotUsed()
        self.UpdateChoiceBox()
        self.UpdatePanel()
        self.lockThread.release()

    def RemoveHandleNotUsed(self):
        listH = list()
        for h in self.GetHWND():
            listH.append(win32gui.GetWindowText(h))

        dictTemp = list(self.UIDict["L2Handle"])
        for title in dictTemp:
            if not (title in listH) and (title in self.UIDict["Handle"]):
                fullTitle = title + ';' + self.UIDict["L2Handle"][title].HandleNote
                self.UIDict["Handle"].remove(fullTitle)
                self.UIDict["ChoiceHandle"].Delete(self.UIDict["ChoiceHandle"].FindString(title))

    def SaveKeyClick(self, event):
        self.lockThread.acquire()
        title = self.UIDict["ChoiceHandle"].GetString(self.UIDict["ChoiceHandle"].GetSelection()).split(';')[0]
        l2f = self.GetL2Handle(title)
        self.UIDict["L2Handle"][str(l2f.HandleName)].HandleNote =  self.UIDict["panelHandleNote"].GetValue()
        newtitle = title + ';' + self.UIDict["panelHandleNote"].GetValue()
        self.UIDict["ChoiceHandle"].SetString(self.UIDict["ChoiceHandle"].GetSelection(), newtitle)
        for i in range(2, 11):
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (
                i-1)].Key = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnKeyName"].GetValue()
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (
                i-1)].RepeatTime = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnRepeat"].GetValue()
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (
                i-1)].SleepTime = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnSleep"].GetValue()
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (
                i-1)].ActiveRepeat = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveRepeat"].GetValue()
            # Nhan ve gia tri Active Color dang dict
            tempStr = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveColor"].GetStringSelection()
            if tempStr != 'None' and tempStr:
                self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (
                    i-1)].ActiveColor = tempStr
            else:
                self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (
                    i-1)].ActiveColor = "None"
            self.UIDict["L2Handle"][str(l2f.HandleName)].DictKeyCombine["Key%s" % (
                i-1)].ActiveHotKey = self.UIDict["CombineKey"]["Key%s" % (i-1)]["pnActiveHotKey"].GetValue()  
        self.lockThread.release()

    def SaveProfileClick(self, event):
        fileDict = dict()
        fileDict["ColorRegistry"] = self.UIDict["ColorRegistry"]
        for key, l2 in self.UIDict["L2Handle"].items():
            fileDict[key] = dict()
            fileDict[key]["HandleName"] = l2.HandleName
            fileDict[key]["HandleValue"] = l2.HandleValue
            fileDict[key]["HandleNote"] = l2.HandleNote
            fileDict[key]["ActiveTime"] = l2.ActiveTime
            fileDict[key]["Active"] = l2.Active
            fileDict[key]["DictKeyCombine"]= dict()
            for i in range(1,10):
                fileDict[key]["DictKeyCombine"]["Key%s" % i] = dict()
                fileDict[key]["DictKeyCombine"]["Key%s" % i]["Key"] = l2.DictKeyCombine["Key%s" % i].Key
                fileDict[key]["DictKeyCombine"]["Key%s" % i]["RepeatTime"] = l2.DictKeyCombine["Key%s" % i].RepeatTime
                fileDict[key]["DictKeyCombine"]["Key%s" % i]["SleepTime"] = l2.DictKeyCombine["Key%s" % i].SleepTime
                fileDict[key]["DictKeyCombine"]["Key%s" % i]["ActiveColor"] = l2.DictKeyCombine["Key%s" % i].ActiveColor
                fileDict[key]["DictKeyCombine"]["Key%s" % i]["ActiveRepeat"] = l2.DictKeyCombine["Key%s" % i].ActiveRepeat
                fileDict[key]["DictKeyCombine"]["Key%s" % i]["ActiveHotKey"] = l2.DictKeyCombine["Key%s" % i].ActiveHotKey
                fileDict[key]["DictKeyCombine"]["Key%s" % i]["LastHit"] = 0 # l2.DictKeyCombine["Key%s" % i].LastHit

        with open("l2config.json", "w") as l2config:
            json.dump(fileDict, l2config)

    def LoadProfileClick(self, event): 
        tempDict = dict()
        with open(os.path.join(os.path.abspath(os.getcwd()), "l2config.json"), "r") as l2config:
            if os.stat(os.path.join(os.path.abspath(os.getcwd()), "l2config.json")).st_size != 0:
                tempDict = json.load(l2config)
                self.UIDict["ColorRegistry"] = tempDict["ColorRegistry"]
                for key, l2 in tempDict.items():
                    if key != "ColorRegistry":
                        if self.UIDict["L2Handle"].get(key) == None:
                            self.UIDict["L2Handle"][key] = L2Handle(win32gui.FindWindowEx(None,None,None,key), key)
                            
                        self.UIDict["L2Handle"][key].HandleName = tempDict[key]["HandleName"]
                        self.UIDict["L2Handle"][key].HandleValue = win32gui.FindWindowEx(None,None,None,key)
                        self.UIDict["L2Handle"][key].HandleNote = tempDict[key]["HandleNote"]
                        self.UIDict["L2Handle"][key].ActiveTime = tempDict[key]["ActiveTime"]
                        self.UIDict["L2Handle"][key].Active = tempDict[key]["Active"]
                        for k, kc in tempDict[key]["DictKeyCombine"].items():
                            self.UIDict["L2Handle"][key].DictKeyCombine[k].Key = kc["Key"]
                            self.UIDict["L2Handle"][key].DictKeyCombine[k].RepeatTime = kc["RepeatTime"]
                            self.UIDict["L2Handle"][key].DictKeyCombine[k].SleepTime = kc["SleepTime"]
                            self.UIDict["L2Handle"][key].DictKeyCombine[k].ActiveColor = kc["ActiveColor"]
                            self.UIDict["L2Handle"][key].DictKeyCombine[k].ActiveRepeat = kc["ActiveRepeat"]
                            self.UIDict["L2Handle"][key].DictKeyCombine[k].LastHit = 0 # kc["LastHit"]

        self.UpdateChoiceBox()
        self.UpdatePanel()

    def ListColorClick(self, event):
        cFrame = wx.Frame(None, title="List Color")
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        for key, item in self.UIDict["ColorRegistry"].items():
            if item:
                label = wx.StaticText(cFrame, id=wx.ID_ANY, label= key +' : ('+ str(item["x"]) + ',' + str(item["y"]) + '): ' + str(item["color"]))
                sizer.Add(label)

        def okClick(event):
            cFrame.Close()

        def clearClick(event):
            self.UIDict["ColorRegistry"] = dict()
            cFrame.Close()

        okBtn = wx.Button(cFrame, id=wx.ID_ANY, label="OK")
        okBtn.Bind(wx.EVT_BUTTON, okClick)
        sizer.Add(okBtn)

        clearBtn = wx.Button(cFrame, id=wx.ID_ANY, label="Clear")
        clearBtn.Bind(wx.EVT_BUTTON, clearClick)
        sizer.Add(clearBtn)

        cFrame.SetSizer(sizer)
        cFrame.Show(True)

    def ExitClick(self, event):
        """Event for Exit Button when its clicked"""
        self.Close()

    def RepeatKeyThread(self):
        try:
            while True:
                if self.UIDict["ToolRun"]:
                    self.lockThread.acquire()
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
                    self.lockThread.release()
                time.sleep(0.1)

        except NameError as er:
            print("Error in Repeat key thread is: %s" % (er))

    def HotKeyRegistry(self):
        kb.add_hotkey('ctrl+s', self.RunClick, args=[0])
        for i in range(1, 10):
            kb.add_hotkey('ctrl+%s' % i, self.AddColor, args=[i])
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

    # def HotKey(self):
    #     ls = keyboard.Listener(on_press = self.onPress, daemon=True)
    #     ls.start()

    # def onPress(self, key):
    #     if hasattr(key, 'vk'):
    #         if key.vk == 97:
    #             self.ControlSend(1)
    #         elif key.vk == 98:
    #             self.ControlSend(2)
    #         elif key.vk == 99:
    #             self.ControlSend(3)
    #         elif key.vk == 100:
    #             self.ControlSend(4)
    #         elif key.vk == 101:
    #             self.ControlSend(5)
    #         elif key.vk == 102:
    #             self.ControlSend(6)
    #         elif key.vk == 103:
    #             self.ControlSend(7)
    #         elif key.vk == 104:
    #             self.ControlSend(8)
    #         elif key.vk == 105:
    #             self.ControlSend(9)

    def ControlSend(self, value):
        self.lockThread.acquire()
        for name, hwnd in self.UIDict["L2Handle"].items():
            if hwnd.DictKeyCombine["Key%s" % value].ActiveHotKey:
                key = hwnd.DictKeyCombine["Key%s" % value].Key
                slTime = int(float(hwnd.DictKeyCombine["Key%s" % value].SleepTime))
                hwnd.ActiveTime = time.time() + slTime
                self.guiKB.ControlSend(hwnd, "n%s" % value)
        self.lockThread.release()

    # Tam thoi khoa tinh nang color check de remake-----------------------
    def AddColor(self, value):
        self.lockThread.acquire()
        newColor = Color()
        newColor.Init()
        self.UIDict["ColorRegistry"]["C%s" % value] = dict()
        self.UIDict["ColorRegistry"]["C%s" % value]["x"] = newColor.x
        self.UIDict["ColorRegistry"]["C%s" % value]["y"] = newColor.y
        self.UIDict["ColorRegistry"]["C%s" % value]["color"] = newColor.color
        self.lockThread.release()


    def ClearColor(self, event, value):
        """Event for Clear color in tab key"""
        self.UIDict["ColorRegistry"] = dict()

    def ColorCheckThread(self):
        checkColor = Color()
        try:
            while True: # Tam thoi khoa tinh nang color check de remake
                if self.UIDict["ToolRun"]:
                    self.lockThread.acquire()
                    for nhwnd, hwnd in self.UIDict["L2Handle"].items():
                        for nkey, key in hwnd.DictKeyCombine.items():
                            if key.ActiveColor != 'None' and self.UIDict["ColorRegistry"].get(key.ActiveColor) != None:
                                x = self.UIDict["ColorRegistry"][key.ActiveColor]["x"]
                                y = self.UIDict["ColorRegistry"][key.ActiveColor]["y"]
                                color = self.UIDict["ColorRegistry"][key.ActiveColor]["color"]
                                if not checkColor.CheckPixelColor(x, y, color):
                                    self.guiKB.ControlSend(hwnd, key.Key)
                    self.lockThread.release()
                time.sleep(0.1)
        except NameError as er:
            print("Error in color check thread is: %s" % (er))
