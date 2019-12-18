from ..devices import Bulb, Device, Plug
from ..exceptions import DeviceError


def GetDeviceType(info):
    deviceType = None
    if 'system' in info and 'get_sysinfo' in info['system']:
        sysinfo = info['system']['get_sysinfo']
        if 'type' in sysinfo:
            deviceType = sysinfo['type']
        elif 'mic_type' in sysinfo:
            deviceType = sysinfo['mic_type']
        else:
            print('DEBUG: {}'.format(sysinfo))

    if deviceType is None:
        raise DeviceError('Unable to detect device type')
    if 'smartplug' in deviceType.lower():
        return Plug
    elif 'smartbulb' in deviceType.lower():
        return Bulb

    return None

def LoadDevices(addresses):
    devices = []
    if not addresses or len(addresses) == 0:
        return []
    for address in addresses:
        device = Device(address)
        info = device.GetInfo()
        if info is None:
            print('Error: Unable to reach address: {}'.format(address))
            continue
        DeviceType = GetDeviceType(info)
        if DeviceType is not None:
            devices.append(DeviceType(address, info=info))
        else:
            print('Error: Unable to determine device type for: {}'.format(address))

    return devices
