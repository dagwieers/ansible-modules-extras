#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2016, Dag Wieers <dag@wieers.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: wakeonlan
version_added: 2.2
short_description: Send magic Wake-on-LAN (WoL) broadcast packet
description:
   - The M(wakeonlan) module sends magic Wake-on-LAN (WoL) broadcast packets.
options:
  mac:
    description:
      - MAC address to send wake-on-lan broadcast packet for
    required: true
    default: null
  broadcast:
    description:
      - Network broadcast address to use for broadcasting
    required: false
    default: 255.255.255.255
  port:
    description:
      - UDP port to use for magic packet
    required: false
    default: 7
author: "Dag Wieers (@dagwieers)"
todo:
  - Add arping support to check whether the system is up (before and after)
  - Enable check-mode support (when we have arping support)
  - Does not have SecureOn password support
notes:
  - This module sends a magic packet, without knowing whether it worked
  - Only works if the target system was properly configured for Wake-on-LAN (in the BIOS and/or the OS)
  - Some BIOSes have a different (configurable) Wake-on-LAN boot order (i.e. PXE first) when turned off
'''

EXAMPLES = '''
# Send a magic wake-on-lan packet to 00:CA:FE:BA:BE:00
- local_action: wakeonlan mac=00:CA:FE:BA:BE:00 broadcast=192.168.1.255

- wakeonlan: mac=00:CA:FE:BA:BE:00 port=9
  delegate_to: localhost
'''

import socket
import struct

def wakeonlan(macaddress, broadcast, port):
    """ Send a magic wake-on-lan packet. """

    mac = macaddress

    # Remove possible seperator from MAC address
    if len(mac) == 12 + 5:
        mac = mac.replace(mac[2], '')

    # If we don't end up with 12 hexadecimal characters, fail
    try:
        int(mac, 16)
    except ValueError:
        raise ValueError('Incorrect MAC address format %s' % macaddress)
 
    # Create payload for magic packet
    data = ''
    padding = ''.join(['FFFFFFFFFFFF', mac * 20])
    for i in range(0, len(padding), 2):
        data = ''.join([data, struct.pack('B', int(padding[i: i + 2], 16))])

    # Broadcast payload to network
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(data, (broadcast, port))

def main():
    module = AnsibleModule(
        argument_spec = dict(
            mac = dict(required=True, type='str'),
            broadcast = dict(required=False, default='255.255.255.255'),
            port = dict(required=False, type='int', default=7),
        ),
    )

    mac = module.params.get('mac')
    broadcast = module.params.get('broadcast')
    port = module.params.get('port')

    wakeonlan(mac, broadcast, port)

    module.exit_json(changed=True)


# import module snippets
from ansible.module_utils.basic import *

main()