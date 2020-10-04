from ctypes import *
from ctypes.wintypes import *
from ctypes import wintypes as w



# const variable
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010

class MODULEENTRY32(Structure):
    _fields_ = [('dwSize', DWORD ),
                ('th32ModuleID', DWORD ),
                ('th32ProcessID', DWORD ),
                ('GlblcntUsage', DWORD ),
                ('ProccntUsage', DWORD ),
                ('modBaseAddr', POINTER(BYTE)),
                ('modBaseSize', DWORD ),
                ('hModule', HMODULE ),
                ('szModule', c_char * 256 ),
                ('szExePath', c_char * 260 )]

# forigen function
## CreateToolhelp32Snapshot
CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
## OpenProcess
OpenProcess = windll.kernel32.OpenProcess
OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
OpenProcess.restype = w.HANDLE
## CloseHandle
CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = [w.HANDLE]
CloseHandle.restype = w.BOOL
## Module32First
Module32First = windll.kernel32.Module32First
## Module32Next
Module32Next = windll.kernel32.Module32Next
## GetLastError
GetLastError = windll.kernel32.GetLastError
GetLastError.argtypes = None
GetLastError.restype = w.DWORD
## ReadProcessMemory
ReadProcessMemory = windll.kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [w.HANDLE,w.LPCVOID,w.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = w.BOOL

class Memory():
    def __init__(self):
        pass

    def GetBaseAddressModule(self, ProcessID, ModuleName, FirstOffSet):
        returnAddress = c_int32() #CUC KY LUU Y DOAN KHAI BAO VALUE
        bytesRead = c_ulonglong() #CUC KY LUU Y DOAN KHAI BAO VALUE
        try:
            hModuleSnap = c_void_p(0)
            moduleEntry = MODULEENTRY32()
            moduleEntry.dwSize = sizeof(MODULEENTRY32)

            hModuleSnap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, ProcessID)

            ret = Module32First(hModuleSnap, byref(moduleEntry))
            if ret == 0:
                # print('ListProcessModules() Error on Module32First[%d]' % GetLastError())
                CloseHandle(hModuleSnap)
                return returnAddress.value 
            while ret:
                compare = ModuleName.encode()
                if moduleEntry.szModule == compare:
                    process = OpenProcess(0x10, False, ProcessID) 
                    # int(0x01F9E3D8) is add value from baseAddress of "Engine.dll"
                    ReadProcessMemory(process, addressof(moduleEntry.modBaseAddr.contents) + int(FirstOffSet), byref(returnAddress), sizeof(returnAddress), byref(bytesRead)) # byref(bytesRead)
                    # Return value int of modBaseAddr that using in ReadProcessMemory
                    # Just add offset to get correct data value like HP/CP/MP ...
                ret = Module32Next(hModuleSnap, byref(moduleEntry))
            CloseHandle(hModuleSnap)
            return returnAddress.value  
        except ValueError as ver:
            print("Error: %s." % ver)
            return returnAddress.value 

    def ReadLineageOffsetValueInt32(self, ProcessID, StartAddress, *OffSetList):
        #Viet ham doc phan cap offset, chu y la cu moi offset trong Cheat Engine tuong ung mot con tro
        retValue = 0
        offsetAddressNext = StartAddress
        try:
            process = OpenProcess(0x10, False, ProcessID)
            for offsets in OffSetList:
                value = c_int32()
                bytesRead = c_ulonglong()
                # Address truyen cho ReadProcessMemory co the la so int, hex...
                ReadProcessMemory(process, offsetAddressNext + offsets, byref(value), sizeof(value), byref(bytesRead))
                retValue = value
                offsetAddressNext = value.value
            CloseHandle(process)  # Close Handle phai nam ngoai vong lap vi neu ko se ko su dung offset dc  
            return retValue
        except NameError as er:
            print("Error %s" % er)
            return retValue
