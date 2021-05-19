from tplink.discover import LoadDevices

commands = {
    'toggle': 'Disable the devices',
    'help': 'Display this help menu',
    'quit': 'Exit this interactive prompt',
    'list': 'List available devices',
    'use': 'Target a specific device ID or name for commands'
}

def IsNumber(value):
    try:
        int(value)
    except ValueError:
        return False
    return True


def Interactive(config, args):
    target = None
    devices = LoadDevices(args.devices)
    if len(devices) == 1:
        target = devices[0]

    while True:
        try:
            if target is not None:
                print('Using device: {}'.format(target.GetAlias()))

            command = input('Select interactive option (help for menu): ')
            if command is None or len(command) == 0:
                continue

            args = command.split(' ')
            command = args.pop(0).lower()
            if command == 'q' or command == 'quit':
                break
            elif command == 'h' or command == 'help':
                print('Available options:\n')
                for option, text in commands.items():
                    print('{}: {}'.format(option, text))
            elif command == 'l' or command == 'list':
                print('Available devices:\n')
                for i in range(len(devices)):
                    print('{}) {} ({})'.format(i + 1, devices[i].GetAlias(), devices[i].address))
            elif command == 'reboot':
                for i in range(len(devices)):
                    print("Rebooting device '{}' ...".format(devices[i].GetAlias()))
                    result = devices[i].Set('system', 'reboot', {'delay': 1})
                    print("device='{}' result={}".format(devices[i].GetAlias(), result))
            elif command == 'toggle':
                for i in range(len(devices)):
                    if devices[i].IsOn():
                        devices[i].Off()
                        print("Changing active state for '{}' to 'Off'".format(
                            devices[i].GetAlias()))
                    elif devices[i].IsOff():
                        devices[i].On()
                        print("Changing active state for '{}' to 'On'".format(
                            devices[i].GetAlias()))
            elif command == 'use':
                if len(args) == 0:
                    if target is not None:
                        target = None
                    else:
                        print('Error: specify a device ID or name to select')
                elif IsNumber(args[0]):
                    index = int(args[0])
                    if index > 0 and index <= len(devices):
                        target = devices[index - 1]
                    else:
                        print("Error: invalid device id '{}'".format(args[0]))
                else:
                    name = ' '.join(args)
                    for device in devices:
                        if device.GetAlias() == name:
                            target = device
                            break
                    if target is None:
                        print("Error: Unknown device '{}'".format(name))
            elif command == 'set':
                if len(args) < 2:
                    print('Error: invalid set parameters')
                else:
                    option = args[0]
                    value = ' '.join(args[1:])
                    result = False
                    if option == 'alias':
                        result = target.SetAlias(value)
                    else:
                        print("Error: invalid set-option '{}'".fomrat(option))
                        continue
                    if result:
                        print('Success')
                    else:
                        print('Failed')

            else:
                print('Error: unknown option: {}'.format(command))
            print()
        except KeyboardInterrupt:
            print("Type 'quit' to exit the interactive utility")
            print()
        except EOFError:
            return False
    return True
