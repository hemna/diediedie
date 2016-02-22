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
Sample script to exercize brick's attach/detach volume.

Sample script that finds an available volume in Cinder, and then calls
brick to attach/detach volume.

"""
import six
import sys

from oslo_config import cfg
from oslo_log import log

from diediedie import auth_args
from diediedie import utils
from os_brick.initiator import connector as con

parser = auth_args.parser
parser.add_argument("-l", "--list",
                    help="List available encrypted volumes",
                    default=False, action="store_true")
parser.add_argument("-v", "--volume",
                    metavar="<cinder-volume-id>",
                    help='Cinder volume id to test for encryptor')

CONF = cfg.CONF
log.register_options(CONF)
CONF([], project='brick', version='1.0')
log.setup(CONF, 'brick')
LOG = log.getLogger(__name__)

def attach_volume(client, vol, initiator):
    LOG.info("Attach volume")
    conn = client.volumes.initialize_connection(vol, initiator)
    connector = con.InitiatorConnector.factory(
        conn['driver_volume_type'], 'sudo',
        use_multipath=initiator['multipath'])
    vol_handle = connector.connect_volume(conn['data'])
    if not connector.check_valid_device(vol_handle['path'], True):
        LOG.debug("check_valid_device %s fails" % vol_handle['path'])
        sys.exit(-1)
    print("Connection infor is %s." % conn)
    print("vol path/handle = %s" % vol_handle)

    print("Succeed to attach volume.")
    return vol_handle


def detach_volume(client, vol, device, initiator):
    conn = client.volumes.initialize_connection(vol, initiator)
    connector = con.InitiatorConnector.factory(
                    conn['driver_volume_type'], 'sudo',
                    use_multipath=initiator['multipath'])

    connector.disconnect_volume(conn['data'],
                                device)
    client.volumes.terminate_connection(vol, initiator)
    print("Succeed to detach volume.")


def data_convert(data):
    new_data = ":".join("{:02x}".format(ord(c)) for c in data)
    return new_data


def read_data(device):
    print("Read 512 bytes from device.")
    if isinstance(device, six.string_types):
        with open(device_path, 'r') as device_file:
            # reada
            data = device_file.read(512)
            print("data is %s." % data_convert(data))

    else:
        data = device.read(512)
        print("data is %s." % data_convert(data))


def main():
    args = parser.parse_args()
    client = utils.build_cinder(args)
    initiator = utils.get_initiator()

    volumes = client.volumes.list(True)
    if args.list:
        for vol in volumes:
            if (vol.status == 'available'):
                print("Name: '%(name)s' %(id)s Size:%(size)sG Type:%(type)s " %
                      {'name': vol.name, 'id': vol.id, 'size': vol.size,
                       'type': vol.volume_type})

        sys.exit(0)

    for vol in volumes:
        if (vol.status == 'available' and
                vol.id == args.volume):
            vol_handle = attach_volume(client, vol, initiator)
            read_data(vol_handle['path'])
            detach_volume(client, vol, vol_handle, initiator)


if __name__ == "__main__":
    main()
