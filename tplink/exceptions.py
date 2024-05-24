import os
from monitor.lib.utils import GetErrorMessage


class DeviceError(Exception):
    def __init__(self, message=None, *args):
        self.message = message or 'Whoops! Something went wrong'
        self.message = self.message.format(*args)


class ConnectionError(DeviceError):

    def __init__(self, err, *args, **kwargs):
        self.err = err or -1
        self.errstr = GetErrorMessage(err) if err else ''
        super(ConnectionError, self).__init__(*args, **kwargs)


class InputError(DeviceError):
    message = 'Invalid input given'
