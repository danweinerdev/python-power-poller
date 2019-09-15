import os


class DeviceError(Exception):
    message = 'Whoops! Something went wrong'

    def __init__(self, message=None, *args):
        self.message = message or self.message
        self.message = self.message.format(*args)


class ConnectionError(DeviceError):
    err = -1
    errstr = None
    message = 'Failed to connect to target device'

    def __init__(self, err, *args, **kwargs):
        self.err = err
        self.errstr = os.strerror(err)
        super(ConnectionError, self).__init__(*args, **kwargs)


class InputError(DeviceError):
    message = 'Invalid input given'