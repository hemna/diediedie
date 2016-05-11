#!/usr/bin/python
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""
Script that tries to attach an existing exported target.

"""
import sys
import os

from clint.textui import prompt, puts, colored, validators
from os_brick.initiator import connector

from diediedie import utils 

sys.path.insert(0, os.path.abspath('..'))


def iscsi_func():
    puts(colored.green("Enter iSCSI information"))
    iqn = prompt.query("Enter target IQN:")
    portal = prompt.query("Enter Target Portal ():")
    lun_id = prompt.query("Enter Target LUN ID:")
    conn_info = {'driver_volume_type': 'iscsi',
                 'data': {'encrypted': False,
                          'target_discovered': False,
                          'target_iqn': iqn,
                          'target_portal': portal,
                          'target_lun': int(lun_id)} }

    return conn_info


def fc_func():
    puts(colored.green("Enter Fibre Channel information"))
    wwn = prompt.query("Enter target WWN:")
    lun_id = prompt.query("Enter Target LUN ID:")
    conn_info = {'driver_volume_type': 'fibre_channel',
                 'data': {'encrypted': False,
                          'target_discovered': False,
                          'target_wwn': wwn,
                          'target_lun': int(lun_id)} }

    return conn_info


def do_attach(conn_info):
    """Try and attach a volume."""

    initiator = utils.get_initiator()
    conn = connector.InitiatorConnector.factory(
        conn_info['driver_volume_type'], 'sudo',
        use_multipath=initiator['multipath'])

    conn.connect_volume(conn_info['data'])


def main():
    # Standard non-empty input
    #name = prompt.query("What's your name?")

    # Set validators to an empty list for an optional input
    #language = prompt.query("Your favorite tool (optional)?", validators=[])

    # Shows a list of options to select from
    inst_options = [{'selector':'1','prompt':'iSCSI','return':connector.ISCSI},
                    {'selector':'2','prompt':'FibreChannel','return':connector.FIBRE_CHANNEL},
                   ]
    inst = prompt.options("Select Volume transport protocol", inst_options)

    if inst == connector.ISCSI:
        connection_info = iscsi_func()
    elif inst == connector.FIBRE_CHANNEL:
        connection_info = fc_func()

    # Use a default value and a validator
    #path = prompt.query('Installation Path', default='/usr/local/bin/', validators=[validators.PathValidator()])

    #puts(colored.blue('Hi {0}. Install {1} {2} to {3}'.format(name, inst, language or 'nothing', path)))   
    puts(colored.blue('Attempting to attach to  {0} volume'.format(inst)))
    puts(colored.blue('Using {0}'.format(connection_info)))

    do_attach(connection_info)


if __name__ == '__main__':
    main()
