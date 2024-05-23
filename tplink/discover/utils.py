from ..devices import Bulb, Device, LightStrip, Plug
from ..exceptions import DeviceError


def GetDeviceType(info):
    deviceType = None
    sysinfo = None
    if 'system' in info and 'get_sysinfo' in info['system']:
        sysinfo = info['system']['get_sysinfo']
        if 'type' in sysinfo:
            deviceType = sysinfo['type']
        elif 'mic_type' in sysinfo:
            deviceType = sysinfo['mic_type']

    if deviceType is None:
        raise DeviceError('Unable to detect device type')
    if 'smartplug' in deviceType.lower():
        return Plug
    elif 'smartbulb' in deviceType.lower():
        if 'length' in sysinfo:
            return LightStrip
        return Bulb

    return None


def LoadDevice(address, logger=None):
    device = Device(address, logger=logger)
    info = device.GetInfo()
    if info is not None:
        DeviceType = GetDeviceType(info)
        if DeviceType is not None:
            return DeviceType(address=address, info=info)
    return None


def LoadDevices(addresses, logger=None):
    devices = []
    if not addresses or len(addresses) == 0:
        return []
    for address in addresses:
        device = LoadDevice(address, logger=logger)
        if not device:
            if logger:
                logger.error('Error: Unable to determine device type for: {}', address)
            continue
        devices.append(device)

    return devices
