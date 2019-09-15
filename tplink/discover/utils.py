from ..devices import Bulb, Plug
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