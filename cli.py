#!/usr/bin/env python3

import argparse
import sys
from commands import Interactive, Status
from tplink.devices import Device
from tplink.discover import GetDeviceType
from tplink.utils import IsValidIPv4


def LoadDevices(addresses):
    devices = []
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


def Main(args):
    for address in args.devices:
        if not IsValidIPv4(address):
            print("Error: Invalid IPv4 address: {}".format(address))
            return False
    
    devices = LoadDevices(args.devices)
    if len(devices) == 0:
        print('Error: unable to load any devices')
        return False

    if args.command == 'status':
        return Status(devices, args)

    return Interactive(devices, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('cli')
    parser.add_argument('--device', '-d', action='append', dest='devices',
        help='List of known devices. If provided discovery is skipped.')
    
    commands = parser.add_subparsers(dest='command')
    status = commands.add_parser('status',
        help='Get devices current status')

    args = parser.parse_args()
    if not Main(args):
        sys.exit(1)
    