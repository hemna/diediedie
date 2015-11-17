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
import argparse
import sys

from cinderclient import client as cinder
from oslo_config import cfg
from oslo_log import log
from oslo_utils import netutils

from hpe_os_tools import utils
from os_brick.initiator import connector

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--list",
                    help="List available attached volumes",
                    default=False, action="store_true")
parser.add_argument("-v", "--volume",
                    metavar="<cinder-volume-id>",
                    help='Cinder volume id to test for resize')

# The default OpenStack Authentication args
parser.add_argument("--os-auth-url",
                    metavar="<auth-url>",
                    default=utils.env("OS_AUTH_URL"),
                    help="URL for the authentication service. "
                         "Default=env[OS_AUTH_URL].")
parser.add_argument("--os-username",
                    metavar='<auth-user-name>',
                    default=utils.env("OS_USERNAME"),
                    help="OpenStack user name. "
                         "Default=env[OS_USERNAME].")
parser.add_argument("--os-password",
                    metavar='<auth-password>',
                    default=utils.env("OS_PASSWORD"),
                    help="Password for OpenStack user. "
                         "Default=env[OS_PASSWORD].")
parser.add_argument("--os-tenant-name",
                    metavar="<auth-tenant-name>",
                    default=utils.env("OS_TENANT_NAME"),
                    help="Tenant name. "
                         "Default=env[OS_TENANT_NAME].")
parser.add_argument("--os-tenant-id",
                    metavar="<auth-tenant-id>",
                    default=utils.env("OS_TENANT_ID"),
                    help="ID for the tenant. "
                         "Default=env[OS_TENANT_ID].")


CONF = cfg.CONF
log.register_options(CONF)
CONF([], project='brick', version='1.0')
log.setup(CONF, 'brick')
LOG = log.getLogger(__name__)


def get_initiator():
    """Get the initiator connector dict."""
    # Get the intiator side connector properties
    my_ip = netutils.get_my_ipv4()
    initiator = connector.get_connector_properties('sudo', my_ip, True, False)
    LOG.debug("initiator = %s", initiator)
    return initiator


def build_cinder(args):
    """Build the cinder client object."""
    (os_username, os_password, os_tenant_name,
     os_auth_url, os_tenant_id) = (
        args.os_username, args.os_password, args.os_tenant_name,
        args.os_auth_url, args.os_tenant_id)

    # force this to version 2.0 of Cinder API
    api_version = 2

    c = cinder.Client(api_version,
                      os_username, os_password,
                      os_tenant_name,
                      os_auth_url,
                      tenant_id=os_tenant_id)
    return c


def main():
    args = parser.parse_args()
    initiator = get_initiator()
    client = build_cinder(args)

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
