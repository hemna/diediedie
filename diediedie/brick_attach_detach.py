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

from cinder import context as cinder_ctxt
from cinder import keymgr as key_manager
from cinder import utils as cinder_utils

from oslo_config import cfg
from oslo_log import log

from diediedie import auth_args
from diediedie import utils
from os_brick import encryptors
from os_brick.initiator import connector as con


parser = auth_args.parser
parser.add_argument("-l", "--list",
                    help="List available encrypted volumes",
                    default=False, action="store_true")
parser.add_argument("-v", "--volume",
                    metavar="<cinder-volume-id>",
                    help='Cinder volume id to test for encryptor')
parser.add_argument("-o", "--oper",
                    metavar="r|w",
                    help="read/write data from first 512 bytes")
parser.add_argument("-d", "--data",
                    metavar="<data to write>",
                    help="write data to volume")

other_opts = [
    cfg.StrOpt('rootwrap_config',
               default='/etc/cinder/rootwrap.conf',
               help='Path to the rootwrap configuration file to use for '
                    'running commands as root'),
]


LOG = None
CONF = cfg.CONF
CONF.register_opts(other_opts)


def setup_logging():
    global LOG
    log.register_options(CONF)
    log.setup(CONF, __name__)
    LOG = log.getLogger(__name__)


def attach_volume(context, client, vol, initiator):
    print("Attach volume %s" % vol.id)
    conn = client.volumes.initialize_connection(vol, initiator)
    connector = con.InitiatorConnector.factory(
        conn['driver_volume_type'], 'sudo',
        use_multipath=initiator['multipath'])
    vol_handle = connector.connect_volume(conn['data'])
    if not connector.check_valid_device(vol_handle['path'], True):
        print("check_valid_device %s fails" % vol_handle['path'])
        sys.exit(-1)

    try:
        encryption = client.volumes.get_encryption_metadata(vol.id)
        if encryption['encryption_key_id']:
            # This is an encrypted volume
            keymgr = key_manager.API()
            conn_info = {'data': {'device_path': vol_handle['path']}}
            encryptor = encryptors.get_volume_encryptor(
                root_helper="sudo",
                connection_info=conn_info,
                keymgr=keymgr,
                **encryption)
            encryptor.attach_volume(context, **encryption)
    except Exception as e:
        connector.disconnect_volume(conn['data'], vol_handle)
        client.volumes.terminate_connection(vol, initiator)
        print("Failed to attach volume: %s." % e)
        sys.exit(-1)

    print("vol path/handle = %s" % vol_handle)

    print("Succeed to attach volume.")
    return vol_handle


def detach_volume(context, client, vol, device, initiator):
    conn = client.volumes.initialize_connection(vol, initiator)
    connector = con.InitiatorConnector.factory(
        conn['driver_volume_type'], 'sudo',
        use_multipath=initiator['multipath'])

    encryption = client.volumes.get_encryption_metadata(vol.id)
    if encryption['encryption_key_id']:
        # Detach encryptor at first
        keymgr = key_manager.API(CONF)
        conn_info = {'data': {'device_path': device}}
        encryptor = encryptors.get_volume_encryptor(root_helper="sudo",
                                                    connection_info=conn_info,
                                                    keymgr=keymgr,
                                                    **encryption)
        encryptor.detach_volume()

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
        with cinder_utils.temporary_chown(device):
            with open(device, 'r') as device_file:
                data = device_file.read(512)
                print("data is %s." % data_convert(data))

    else:
        data = device.read(512)
        print("data is %s." % data_convert(data))


def write_data(device, data):
    print("Write data to volume.")
    if isinstance(device, six.string_types):
        with cinder_utils.temporary_chown(device):
            with open(device, 'w') as device_file:
                device_file.write(data)
    else:
        device.write(data)
    print("data is written to volume.")


def main():
    setup_logging()
    args = parser.parse_args()
    CONF([], project='brick_volume',
         default_config_files=['/etc/cinder/cinder.conf'])
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
            context = cinder_ctxt.get_admin_context()
            vol_handle = attach_volume(context, client, vol, initiator)
            try:
                if args.oper == 'w':
                    write_data(vol_handle['path'], args.data)
                else:
                    read_data(vol_handle['path'])
            finally:
                detach_volume(context, client, vol,
                              vol_handle['path'], initiator)


if __name__ == "__main__":
    main()
