from ctypes import *
from ctypes.wintypes import *
import win32process
import win32ui
import win32gui
import win32api

stamina_threshold = 200
stamina_max = 270

found_core_address = None
found_stamina_address = None

def find_coreclr_address():

    global found_core_address
    if found_core_address is not None:
        return found_core_address

    modules = win32process.EnumProcessModules(process_handle)

    for address in modules:
        module_name = str(win32process.GetModuleFileNameEx(process_handle, address))
        if "coreclr.dll" in module_name:
            found_core_address = address
            print(f"[!] found coreclr.dll [{hex(found_core_address)}]")

    return found_core_address

def get_stamina_address(base_address, offsets):

    global found_stamina_address
    if found_stamina_address is not None:
        return found_stamina_address

    buffer = c_uint64()
    address_buffer = c_uint64()

    windll.kernel32.ReadProcessMemory(process_handle, c_uint64(base_address + 0x004AC108), byref(buffer), sizeof(buffer), None)
    address_buffer = buffer.value
    windll.kernel32.ReadProcessMemory(process_handle, c_uint64(address_buffer + offsets[0]), byref(buffer), sizeof(buffer), None)
    
    for i in range(1, 4):
        windll.kernel32.ReadProcessMemory(process_handle, c_uint64(buffer.value + offsets[i]), byref(buffer), sizeof(buffer), None)

    found_stamina_address = buffer.value + offsets[4]

    print(f"[!] stamina found [{hex(found_stamina_address)}]")

    return found_stamina_address


def get_stamina():

    stamina_buffer = c_float()
    windll.kernel32.ReadProcessMemory(process_handle, c_uint64(stamina_address), byref(stamina_buffer), sizeof(stamina_buffer), None)

    return stamina_buffer.value

if not win32gui.FindWindow(None, "Stardew Valley") != 0:
    
    win32api.MessageBox(0, "stardew valley not found", "error")
    exit()

pid = win32process.GetWindowThreadProcessId(win32ui.FindWindow(None, "Stardew Valley").GetSafeHwnd())[1]
process_handle = windll.kernel32.OpenProcess(0x1F0FFF, False, int(pid))
stamina_address = get_stamina_address(find_coreclr_address(), [0xB0, 0x1CC, 0x18, 0x360, 0xA8C])

while True:

    current_stamina = get_stamina()

    if 0 < current_stamina < stamina_threshold:
        print(f"[!] recharging [{int(current_stamina)}] -> [{stamina_max}]")

        buffer = c_float()
        windll.kernel32.WriteProcessMemory(process_handle, c_uint64(stamina_address), byref(c_float(stamina_max)), sizeof(c_float(stamina_max)), byref(buffer))