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
Sample script to exercize brick's extend_volume.

Sample script that finds an attached volume in Cinder, and then calls
brick to extend_volume.

"""
import sys

from oslo_config import cfg
from oslo_log import log

from diediedie import auth_args
from diediedie import utils
from os_brick.initiator import connector

parser = auth_args.parser
parser.add_argument("-l", "--list",
                    help="List available attached volumes",
                    default=False, action="store_true")
parser.add_argument("-v", "--volume",
                    metavar="<cinder-volume-id>",
                    help='Cinder volume id to test for resize')


CONF = cfg.CONF
log.register_options(CONF)
CONF([], project='brick', version='1.0')
log.setup(CONF, 'brick')
LOG = log.getLogger(__name__)


def main():
    """The main."""
    args = parser.parse_args()
    initiator = utils.get_initiator()
    client = utils.build_cinder(args)
    print(f"{client}")

    volumes = client.volumes.list(True)
    if args.list:
        for vol in volumes:
            if vol.status == 'in-use':
                print("Name: '%(name)s' %(id)s Size:%(size)sG Type:%(type)s " %
                      {'name': vol.name, 'id': vol.id, 'size': vol.size,
                       'type': vol.volume_type})

        sys.exit(0)

    info = dict()
    volume = client.volumes.get(args.volume)
    info['id'] = volume._info['id']
    info['encrypted'] = volume._info['encrypted']
    info['multiattach'] = volume._info['multiattach']
    info['status'] = volume._info['status']
    info['host'] = volume._info['os-vol-host-attr:host']
    info['size'] = volume._info['size']
    info['volume_type'] = volume._info['volume_type']
    info['attachments'] = volume._info['attachments']
    # info.update(volume._info)
    info.pop('links', None)

    # now fetch the volume paths
    if volume.status == 'in-use':
        conn = client.volumes.initialize_connection(volume, initiator)
        b = connector.InitiatorConnector.factory(
            conn['driver_volume_type'], 'sudo',
            use_multipath=initiator['multipath'])
        info['system-paths'] = b.get_volume_paths(conn['data'])

    utils.print_dict(info, value_align='l', disable_unicode=True)


if __name__ == "__main__":
    main()
