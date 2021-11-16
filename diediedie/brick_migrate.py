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


CONF = cfg.CONF
DOMAIN = "brick"
LOG = log.getLogger(DOMAIN)
log.register_options(CONF)


def main():
    """The main."""
    args = parser.parse_args()
    config_file = args.config_file
    if not config_file:
        config_file = ['--config-file', utils.DEFAULT_CONFIG_FILE]
    CONF(config_file, project="brick", version='1.0')

    utils.prepare_log()

    client = utils.build_cinder(args)
    LOG.info(f"{client}")
    LOG.info("{}".format(dir(client)))

    connector = {"connection_capabilities": ['vmware_service_instance_uuid:dfd3fd7e-3645-410e-b0e7-ce9fae84025a']}
    # connector = {}
    body = {"connector": connector}

    vol_id = '0a103a19-ad01-4131-9ff2-ade3b59832c2'
    volume = client.volumes.get(vol_id)

    print(f"{volume}")
    res, resp = client.volumes._action('os-migrate_volume_by_connector', volume, body)
    LOG.info(f"{res},   {resp}")
    sys.exit(0)

    volumes = client.volumes.list(True)
    for vol in volumes:
        LOG.info(f"{vol}")
        LOG.info("Name: '%(name)s' %(id)s Size:%(size)sG Type:%(type)s " %
                  {'name': vol.name, 'id': vol.id, 'size': vol.size,
                   'type': vol.volume_type})
        #res, resp = client.volumes._action('os-migrate_volume_by_connector', vol, body)
        #LOG.warning(f"{res}")
        #LOG.warning(f"{resp}")
        volume = client.volumes.get(vol.id)
        print(f"{volume}")
        sys.exit(0)


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
