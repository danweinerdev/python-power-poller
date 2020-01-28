from .device import Device, DeviceType
from ..exceptions import DeviceError


class Plug(Device):

    def __init__(self, *args, **kwargs):
        super(Plug, self).__init__(type=DeviceType.PLUG, *args, **kwargs)

    def __repr__(self):
        return '<{}: {}>'.format(self.GetType(), self.address)

    def GetEmeterType(self):
        if not self.HasEmeter():
            raise DeviceError('Device does not support the emeter')
        return 'emeter'

    def GetType(self):
        return 'Plug'

    def HasEmeter(self):
        return 'ENE' in self.GetFeatures()

    def IsOff(self):
        return not self.IsOn()

    def IsOn(self):
        return bool(self.GetSysInfo('relay_state'))

    def IsLedOff(self):
        return not self.IsLedOn()

    def IsLedOn(self):
        return bool(self.GetSysInfo('led_off') == 0)

    def Off(self):
        return self.Send(
            self.QueryHelper('system', 'set_relay_state', {'state': 0}))

    def On(self):
        return self.Send(
            self.QueryHelper('system', 'set_relay_state', {'state': 1}))
