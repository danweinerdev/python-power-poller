#!/usr/bin/env python3

import os
import sys

pkgPath = os.path.realpath(os.path.join(__file__, os.pardir, os.pardir))
if os.path.exists(os.path.join(pkgPath, 'monitor-lib')):
    sys.path.insert(0, os.path.join(pkgPath, 'monitor-lib'))

from commands import Interactive, Poll, Status
from monitor.lib import Execute


def ConfigureParams(parser):
    """
    Add the default options for any command on this tool.

    :param parser: Command sub-parser
    :return: Updated parser object.
    """
    parser.add_argument('--device', '-d', action='append', dest='devices',
        help='List of known devices. If provided discovery is skipped.')
    return parser


def Setup(args):
    """
    Setup the argument parsers for the extra sub-commands for the CLI tool.
    This will configure the given callbacks and setup for bypassing the normal
    poll mode and triggering secondary callbacks.

    :param args: Callback registration tool.
    :return: None
    """
    ConfigureParams(args.Register('status', Status,
        help='Status command for polling the state of the configured devices'))
    # ConfigureParams(args.Register('interactive', Interactive,
    #    help='Run the interactive mode for the CLI tool.'))


if __name__ == '__main__':
    Execute(Poll, 'devices', command='run', commands=Setup)
