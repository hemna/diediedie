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
Helper for creating an argparse parser with standard OpenStack env auth vars.

Simply import this and use parser.
"""
import argparse

from hpe_os_tools import utils

parser = argparse.ArgumentParser()
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
