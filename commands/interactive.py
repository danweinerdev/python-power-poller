commands = {
    'help': 'Display this help menu',
    'quit': 'Exit this interactive prompt',
    'list': 'List available devices'
}

def Interactive(devices, args):
    while True:
        try:
            command = input('Select interactive option (help for menu): ')
            if command is None or len(command) == 0:
                continue

            command = command.lower()
            if command == 'q' or command == 'quit':
                break
            elif command == 'h' or command == 'help':
                print('Available options:\n')
                for option, text in commands.items():
                    print('{}: {}'.format(option, text))
            elif command == 'l' or command == 'list':
                print('Available devices:\n')
                for i in range(len(devices)):
                    print('{}) {}'.format(i + 1, devices[i]))
            else:
                print('Error: unknown option: {}'.format(command))
            print()
        except KeyboardInterrupt:
            print("Type 'quit' to exit the interactive utility")
            print()
    return True