from .bulb import Bulb
from .device import DeviceType
from ..exceptions import DeviceError


class LightStrip(Bulb):
    LIGHT_STATE = 'smartlife.iot.lightStrip'
    SET_LIGHT_METHOD = 'set_light_state'

    def __init__(self, type=DeviceType.LIGHTSTRIP, **kwargs):
        super(LightStrip, self).__init__(type=type, **kwargs)

    def __repr__(self):
        return '<LightStrip: {}>'.format(self.address)
