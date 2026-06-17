import ctypes
from enum import Enum

class Arch(Enum):
    x86 = 0
    x64 = 1
    auto = 2

def detect_arch(pid):
    h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
    if not h:
        raise RuntimeError("The process doesn't exist or couldn't be accessed by process")
    try:
        is_wow64 = ctypes.c_bool(False)
        ctypes.windll.kernel32.IsWow64Process(h, ctypes.byref(is_wow64))
    finally:
        ctypes.windll.kernel32.CloseHandle(h)
    
    return Arch.x86 if is_wow64.value == True else Arch.x64