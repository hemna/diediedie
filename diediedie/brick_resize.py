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
    args = parser.parse_args()
    initiator = utils.get_initiator()
    client = utils.build_cinder(args)

    volumes = client.volumes.list(True)
    if args.list:
        for vol in volumes:
            if vol.status == 'in-use':
                print("Name: '%(name)s' %(id)s Size:%(size)sG Type:%(type)s " %
                      {'name': vol.name, 'id': vol.id, 'size': vol.size,
                       'type': vol.volume_type})

        sys.exit(0)

    for vol in volumes:
        if vol.status == 'in-use' and vol.id == args.volume:
            LOG.debug("id = %s", vol.id)
            conn = client.volumes.initialize_connection(vol, initiator)
            LOG.debug("conn = %s", conn)
            sys.exit(-1)
            b = connector.InitiatorConnector.factory(
                conn['driver_volume_type'], 'sudo',
                use_multipath=initiator['multipath'])
            LOG.debug("call resize for %s", conn)
            new_size = b.extend_volume(conn['data'])
            LOG.debug("New size for device = %s" %
                      new_size)


if __name__ == "__main__":
    main()
