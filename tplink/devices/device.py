import json
import socket
import struct
import sys
from .emeter import EmeterHandler
from ..exceptions import ConnectionError, DeviceError, InputError
from ..utils import Cache, IsValidMacAddress


class DeviceType(object):
    NONE = 0
    BULB = 1
    PLUG = 2


class Device(object):

    DEFAULT_PORT = 9999
    ENCRYPTION_KEY = 0xAB

    def __init__(self, address, type=DeviceType.NONE, info=None, key=None,
            port=DEFAULT_PORT):
        self.address = address
        self.port = int(port)
        self.key = key or self.ENCRYPTION_KEY
        self.type = type or DeviceType.NONE
        self.emeter = None
        self.cache = Cache()

    @staticmethod
    def Decrypt(message, key):
        buffer = []
        for cipherbyte in message:
            plainbyte = key ^ cipherbyte
            key = cipherbyte
            buffer.append(plainbyte)

        plaintext = bytes(buffer)
        return plaintext.decode()

    @staticmethod
    def Encrypt(message, key):
        plainbytes = message.encode()
        buffer = bytearray(struct.pack(">I", len(plainbytes)))

        for plainbyte in plainbytes:
            cipherbyte = key ^ plainbyte
            key = cipherbyte
            buffer.append(cipherbyte)

        return bytes(buffer)

    def GetAlias(self):
        return self.GetSysInfo('alias')

    def GetDescription(self):
        return self.GetSysInfo('description')

    def GetDeviceIdentifier(self):
        return self.GetSysInfo('deviceId')

    def GetDeviceState(self):
        return self.GetSysInfo('dev_state')

    def GetEmeter(self):
        if not self.HasEmeter():
            raise DeviceError('Device does not support the emeter')
        if self.emeter is None:
            self.emeter = EmeterHandler(self)
        return self.emeter

    def GetEmeterType(self):
        raise NotImplementedError

    def GetFeatures(self):
        value = self.GetSysInfo('feature')
        return value.split(':') if value is not None else []

    def GetFirmwareIdentifier(self):
        return self.GetSysInfo('fwId')

    def GetInfo(self, key=None):
        info = self.cache.Get('system')
        if info is None:
            info = self.Send(
                self.QueryHelper('system', 'get_sysinfo'))
        if info is not None:
            self.cache.Insert('system', info)
        if key is not None:
            return info[key]
        return info

    def GetHardwareVersion(self):
        return self.GetSysInfo('hw_ver')

    def GetHardwareIdentifier(self):
        return self.GetSysInfo('hwId')

    def GetMacAddress(self):
        value = self.GetSysInfo('mac')
        if value is not None:
            return str(value)
        value = self.GetSysInfo('mic_mac')
        if value is not None:
            return ':'.join(format(s, '02x')
                for s in bytes.fromhex(value))
        return None

    def GetManufacturerIdentifier(self):
        return self.GetSysInfo('oemId')

    def GetModel(self):
        return self.GetSysInfo('model')

    def GetSignalStrength(self):
        value = self.GetSysInfo('rssi')
        if value is not None:
            return int(value)
        return -1 * sys.maxint

    def GetSoftwareVersion(self):
        return self.GetSysInfo('sw_ver')

    def GetSysInfo(self, key=None):
        if key is not None:
            return self.GetInfo('system')['get_sysinfo'].get(key)
        return self.GetInfo('system')['get_sysinfo']

    def GetType(self):
        if self.type == DeviceType.BULB:
            return 'Bulb'
        elif self.type == DeviceType.PLUG:
            return 'Plug'
        return 'Unknown'

    def GetTypeString(self):
        return (self.GetSysInfo('type') or self.GetSysInfo('mic_type')).lower()

    def GetUptime(self):
        value = self.GetSysInfo('on_time')
        if value is not None:
            return int(value)
        return int(-1)

    def HasEmeter(self):
        raise NotImplementedError

    def IsBrightnessSupported(self):
        # Device Specific Implementation
        return False

    def IsBulb(self):
        return self.type == DeviceType.BULB

    def IsOff(self):
        # Device Specific Implementation
        raise NotImplementedError

    def IsOn(self):
        # Device Specific Implementation
        raise NotImplementedError

    def IsPlug(self):
        return self.type == DeviceType.PLUG

    def Off(self):
        # Device Specific Implementation
        raise NotImplementedError

    def On(self):
        # Device Specific Implementation
        raise NotImplementedError

    def Reboot(self, delay=0):
        return self.Send(
            self.QueryHelper('system', 'reboot', {'delay': delay}))

    def Send(self, message):
        encrypted = self.Encrypt(message, self.key)

        sock = None
        try:
            sock = socket.create_connection((self.address, self.port), 3)
            sock.send(encrypted)

            buffer = bytes()
            length = -1
            while True:
                chunk = sock.recv(4096)
                if length == -1:
                    length = struct.unpack(">I", chunk[0:4])[0]
                buffer += chunk
                if (length > 0 and len(buffer) >= length + 4) or not chunk:
                    break
        except socket.error as e:
            raise ConnectionError(e.errno, 'Error connecting to bulb: {}:{}'.format(
                self.address, self.port))
        finally:
            try:
                sock.close()
            except:
                pass

        response = self.Decrypt(buffer[4:], self.key)
        return json.loads(response)

    def Set(self, category, option, value):
        result = self.Send(self.QueryHelper(category, option, value))
        if result is None or len(result) == 0:
            print("Error: unable to set '{}::{}': invalid response from device"\
                .format(category, option))
            return False
        if category not in result:
            print('Error: invalid response from device')
            return False
        if option not in result[category]:
            print('Error: invalid response from device')
            return False
        response = result[category][option]
        if 'err_code' not in response or response['err_code'] != 0:
            return False
        self.cache.Clear()
        return True

    def SetAlias(self, alias):
        return self.Set('system', 'set_dev_alias', {'alias': alias})

    def SetMacAddress(self, address):
        if not IsValidMacAddress(address):
            raise InputError('Invalid MAC address: {}'.format(address))
        return self.Send(
            self.QueryHelper('system', 'set_mac_addr', {'mac': address}))

    @staticmethod
    def QueryHelper(target, command, argument=None):
        message = {target: {command: argument or {}}}
        return json.dumps(message)
