from ctypes import *
from ctypes.wintypes import *


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
## CloseHandle
CloseHandle = windll.kernel32.CloseHandle
## Module32First
Module32First = windll.kernel32.Module32First
## Module32Next
Module32Next = windll.kernel32.Module32Next
## GetLastError
GetLastError = windll.kernel32.GetLastError
## ReadProcessMemory
ReadProcessMemory = windll.kernel32.ReadProcessMemory

def GetBaseAddressModule(ProcessID, ModuleName):
    hModuleSnap = c_void_p(0)
    me32 = MODULEENTRY32()
    me32.dwSize = sizeof(MODULEENTRY32)
    hModuleSnap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, ProcessID )

    ret = Module32First(hModuleSnap, byref(me32))
    if ret == 0 :
        print ('ListProcessModules() Error on Module32First[%d]' % GetLastError())
        CloseHandle( hModuleSnap )
        return False

    while ret :
        compare = ModuleName.encode()
        if me32.szModule == compare:
            print("   MODULE NAME:     %s"%             me32.szModule )
            print("   executable     = %s"%             me32.szExePath )
            print("   process ID     = 0x%08X"%         me32.th32ProcessID )
            print("   ref count (g)  =     0x%04X"%     me32.GlblcntUsage )
            print("   ref count (p)  =     0x%04X"%     me32.ProccntUsage )
            print("   base address   = {}".format(me32.modBaseAddr))
            print("   base size      = %d"%             me32.modBaseSize )

            process = OpenProcess(0x10, False, mypid)
            returnAddress = c_int32()
            bytesRead = c_int32()
            # int(0x01F9E3D8) is add value from baseAddress of "Engine.dll"
            ReadProcessMemory(process, addressof(me32.modBaseAddr.contents) + int(0x01F9E3D8), byref(returnAddress), sizeof(returnAddress), byref(bytesRead))
            # Return value int of modBaseAddr that using in ReadProcessMemory
            # Just add offset to get correct data value like HP/CP/MP ...
            return returnAddress.value 
        ret = Module32Next(hModuleSnap, byref(me32))


    CloseHandle(hModuleSnap)
    return False  

def ReadLineageOffsetValue(ProcessID, ModuleName, *OffSetList):
    #Viet ham doc phan cap offset, chu y la cu moi offset trong Cheat Engine tuong ung mot con tro
    pass
# main
if __name__ == '__main__':
    print("")
    print("==================================================")
    print("VI DU CHO RA PROCESS ID TUONG UNG VOI PID 9476 va module 'Engine.dll' chua nhieu thong so game")
    print("--------------------------------------------------")
    mypid = 304 #PID cua process
    process = OpenProcess(0x10, False, mypid)
    BaseHexAddress = GetBaseAddressModule(mypid,"Engine.dll")
    while True:
    # Address truyen cho ReadProcessMemory co the la so int, hex...
        hp = c_int32()
        ReadProcessMemory(process, BaseHexAddress + int(0x5C), byref(hp), sizeof(hp), None)
        mp = c_int32()
        ReadProcessMemory(process, BaseHexAddress + int(0x60), byref(mp), sizeof(mp), None)
        cp = c_int32()
        ReadProcessMemory(process, BaseHexAddress + int(0x64), byref(cp), sizeof(cp), None)
        print("Info: HP: %s/MP: %s/CP: %s." % (hp.value, mp.value, cp.value))
    CloseHandle(process)
