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

def GetBaseAddressModule(ProcessID, ModuleName, FirstOffSet):
    hModuleSnap = c_void_p(0)
    moduleEntry = MODULEENTRY32()
    moduleEntry.dwSize = sizeof(MODULEENTRY32)
    hModuleSnap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, ProcessID )

    ret = Module32First(hModuleSnap, byref(moduleEntry))
    if ret == 0 :
        print ('ListProcessModules() Error on Module32First[%d]' % GetLastError())
        CloseHandle( hModuleSnap )
        return False

    while ret :
        compare = ModuleName.encode()
        if moduleEntry.szModule == compare:
            print("   MODULE NAME:     %s"%             moduleEntry.szModule )
            print("   executable     = %s"%             moduleEntry.szExePath )
            print("   process ID     = 0x%08X"%         moduleEntry.th32ProcessID )
            print("   ref count (g)  =     0x%04X"%     moduleEntry.GlblcntUsage )
            print("   ref count (p)  =     0x%04X"%     moduleEntry.ProccntUsage )
            print("   base address   = {}".format(moduleEntry.modBaseAddr))
            print("   base size      = %d"%             moduleEntry.modBaseSize )

            process = OpenProcess(0x10, False, mypid)
            returnAddress = c_int32()
            bytesRead = c_int32()
            # int(0x01F9E3D8) is add value from baseAddress of "Engine.dll"
            ReadProcessMemory(process, addressof(moduleEntry.modBaseAddr.contents) + int(FirstOffSet), byref(returnAddress), sizeof(returnAddress), byref(bytesRead))
            # Return value int of modBaseAddr that using in ReadProcessMemory
            # Just add offset to get correct data value like HP/CP/MP ...
            return returnAddress.value 
        ret = Module32Next(hModuleSnap, byref(moduleEntry))


    CloseHandle(hModuleSnap)
    return False  

def ReadLineageOffsetValueInt32(Process, ModuleName, StartAddress, *OffSetList):
    #Viet ham doc phan cap offset, chu y la cu moi offset trong Cheat Engine tuong ung mot con tro
    retValue = 0
    offsetAddressNext = StartAddress
    for offsets in OffSetList:
        value = c_int32()
        # Address truyen cho ReadProcessMemory co the la so int, hex...
        ReadProcessMemory(Process, offsetAddressNext + offsets, byref(value), sizeof(value), None)
        retValue = value
        offsetAddressNext = value.value
    return retValue


# main
if __name__ == '__main__':
    print("")
    print("==================================================")
    print("VI DU CHO RA PROCESS ID TUONG UNG VOI PID 9476 va module 'Engine.dll' chua nhieu thong so game")
    print("--------------------------------------------------")
    mypid = 16884 #PID cua process
    process = OpenProcess(0x10, False, mypid)
    baseEngine = GetBaseAddressModule(mypid, "Engine.dll", 0x01F9E3D8)
    hp = ReadLineageOffsetValueInt32(process, "Engine.dll", baseEngine, int(0x5C)).value
    mp = ReadLineageOffsetValueInt32(process, "Engine.dll", baseEngine, int(0x60)).value
    cp = ReadLineageOffsetValueInt32(process, "Engine.dll", baseEngine, int(0x64)).value
    hppt = dict()
    baseNWindow = GetBaseAddressModule(mypid, "NWindow.DLL", 0x0134E620)
    for i in range(9):
        hppt[i] = ReadLineageOffsetValueInt32(process, "NWindow.DLL", baseNWindow, int(0x20), int(0x3E8), int(0x214), int(0x444 + i*0x4), int(0x34), int(0x21C)).value

    CloseHandle(process)
