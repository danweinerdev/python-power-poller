from configparser import ConfigParser
from datetime import datetime
import errno
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import select
import signal
import sys
import time
import threading
from influxdb import InfluxDBClient
from tplink.discover import LoadDevices
from tplink.utils import IsValidIPv4


logger = logging.getLogger('power.monitor')

class PollError(Exception):

    def __init__(self, message=None, *args):
        self.message = message or self.message
        self.message = self.message.format(*args)


class ConfigError(PollError):
    message = 'Configuration failure'


class ConversionFailure(PollError):
    message = 'Invalid type conversion requested'


def ConvertBoolean(value):
    if value.lower() in ['yes', '1', 'true']:
        return True
    if value.lower() in ['no', '0', 'false']:
        return False
    return None


def ConvertValue(value, hint=None):
    value = value.strip()
    try:
        if hint is not None:
            if hint == 'int':
                if '.' in value:
                    return int(float(value))
                return int(value)
            if hint == 'float':
                return float(value)
            if hint == 'string':
                return value
            raise ConversionFailure
        else:
            v = float(value)
            if '.' in value:
                return v
            return int(v)
    except (TypeError, ValueError):
        if hint is not None:
            raise ConversionFailure('Failed to convert the given value to the requested type')
        else:
            if ConvertBoolean(value) is None:
                return value
            return ConvertBoolean(value)


def DropDescriptors():
    for fd in range(1, 3):
        try:
            os.close(fd)
        except (IOError, OSError):
            pass


def LoadConfiguration(configFile):
    parser = ConfigParser()
    parser.read(configFile)

    if not parser.has_section('influx'):
        raise ConfigError('Invalid config file: {}'.format(configFile))

    config = {'influx': {}, 'devices': {}}

    influxRequiredFields = ['database', 'devices', 'server']
    for field in influxRequiredFields:
        if not parser.has_option('influx', field):
            raise ConfigError(
                'Invalid influx configuration: Missing required field: {}'.format(field))

    allowedInfluxFields = ['database', 'port', 'server', 'ssl', 'verify']
    for field in allowedInfluxFields:
        if parser.has_option('influx', field):
            config['influx'][field] = ConvertValue(parser.get('influx', field))

    config['influx']['devices'] = parser.get('influx', 'devices').split()
    if len(config['influx']['devices']) == 0:
        raise ConfigError("No devices configured")

    deviceRequiredFields = ['address', 'deviceId', 'fields', 'tags']

    for value in config['influx']['devices']:
        if not parser.has_section(value):
            raise ConfigError('No configuration for device: {}'.format(value))
        for field in deviceRequiredFields:
            if not parser.has_option(value, field):
                raise ConfigError("Invalid device configuration for '{}': Missing required field: {}".format(
                    value, field))

        fields = parser.get(value, 'fields')
        tags = parser.get(value, 'tags')
        address = parser.get(value, 'address')
        device = parser.get(value, 'deviceId')

        if not IsValidIPv4(address):
            raise ConfigError("Invalid IP address '{}' for device '{}'".format(address, value))

        config['devices'][value] = {
            'address': address,
            'deviceId': device,
            'tags': {},
            'fields': {}
        }

        for tag in tags.split():
            try:
                k, v = tag.split('=')
            except ValueError:
                raise ConfigError("Invalid tag '{}' for device: {}".format(tag, value))
            config['devices'][value]['tags'][k] = v.strip()

        for field in fields.split():
            if not parser.has_section(field):
                raise ConfigError("Invalid field set '{}' for device: {}".format(field, value))
            if not parser.has_option(field, 'fields'):
                raise ConfigError('Malformed field configuration: {}'.format(field))
            sectionFields = parser.get(field, 'fields')
            if len(sectionFields) == 0:
                raise ConfigError('No fields specified for field set: {}'.format(field))
            for name in sectionFields.split():
                try:
                    name, _type = name.split(':')
                except (TypeError, ValueError):
                    _type = None
                if _type not in [None, 'int', 'float', 'string']:
                    raise ConfigError("Invalid type conversion to field: {}:{}".format(
                        value, name))
                config['devices'][value]['fields'][name] = _type
    return config


def Poll(devices, args):
    event = threading.Event()
    interval = (args.interval > 0)
    SetupLogging(args)

    if interval:
        def ShutdownHandler(sig, sigframe):
            logger.info('Signal received: %d', sig)
            if sig in [signal.SIGINT, signal.SIGTERM]:
                event.set()

        signal.signal(signal.SIGINT, ShutdownHandler)
        signal.signal(signal.SIGTERM, ShutdownHandler)
        if args.logfile is not None:
            DropDescriptors()

    if not os.path.isfile(args.config):
        logger.error('config file does not exist: {}', args.config)
        return False

    try:
        config = LoadConfiguration(args.config)
    except ConfigError as e:
        print('Error: {}'.format(e.message))
        return False

    if len(config['devices']) == 0:
        logger.warning('no devices specified')
        return False

    influx = InfluxDBClient(
        host=config['influx']['server'],
        port=config['influx']['port'],
        ssl=config['influx']['ssl'],
        verify_ssl=config['influx']['verify'],
        database=config['influx']['database'])

    logger.info('Successfully connected to InfluxDB: %s://%s:%d/%s',
        'https' if config['influx']['ssl'] else 'http',
        config['influx']['server'],
        config['influx']['port'],
        config['influx']['database'])

    addresses = {}
    for n, device in config['devices'].items():
        addresses[device['address']] = device

    print('addresses={}'.format(addresses))
    devices = LoadDevices(addresses.keys())

    try:
        while True:
            if not ProcessDevices(config, influx, addresses, devices):
                return False
            if event.is_set():
                break
            if not args.interval:
                break

            # TODO Update this sleep to a select-notify
            time.sleep(float(args.interval))
    finally:
        try:
            influx.close()
        except:
            pass

    return True

def ProcessDevices(config, influx, addresses, devices):
    failure = False
    points = []
    timeStamp = TimeStamp()

    for device in devices:
        if not device.HasEmeter():
            logger.warning("Device '{}' does not support electronic metering",
                device.GetAlias())
            failure = True
            continue

        emeter = device.GetEmeter()
        result = emeter.GetRealtime(cache=False)
        if 'err_code' not in result or result['err_code'] != 0:
            logger.error("Failed to load device '{}' emeter data",
                device.GetAlias())
            failure = True
            continue

        fields = addresses[device.address]['fields']
        for key, value in result.items():
            if key not in fields:
                continue

            points.append({
                'measurement': key.replace('.', '_'),
                'tags': addresses[device.address]['tags'],
                'time': timeStamp,
                'fields': {'value': value}})

    start = time.time()
    influx.write_points(points, time_precision='ms')
    stop = time.time()

    logger.debug("Uploaded '%d' metrics in %dms",
        len(points), stop - start)

    return (not failure)

def TimeStamp(now=None):
    now = now or datetime.utcnow()
    return now.strftime('%Y-%m-%dT%H:%M:%SZ')

def Select(rds, wrts, timeout):
    if not isinstance(rds, list):
        rds = [rds]
    if not isinstance(wrts, list):
        wrts = [wrts]

    try:
        res = select.select(rds, wrts, [], timeout)
    except select.error as e:
        pass
    except os.error as e:
        pass
    except KeyboardInterrupt:
        pass

def SetupLogging(args):
    if args.logfile is not None:
        handler = TimedRotatingFileHandler(
            args.logfile,
            backupCount=3,
            when='midnight')
    else:
        handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
