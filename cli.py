#!/usr/bin/env python3

# Copyright 2019-2024 Daniel Weiner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os.path import dirname, exists, join, realpath
import os
import sys


rootPath = realpath(join(__file__, os.pardir))
parentPath = dirname(rootPath)

if exists(join(parentPath, 'PyMonitorLib')):
    sys.path.insert(0, join(parentPath, 'PyMonitorLib'))

if exists(join(rootPath, 'commands')):
    sys.path.insert(0, rootPath)

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
    ConfigureParams(args.Register('interactive', Interactive,
        help='Run the interactive mode for the CLI tool.'))


if __name__ == '__main__':
    Execute(Poll, 'devices', command='run', commands=Setup)
