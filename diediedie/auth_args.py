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
from pathlib import Path

from diediedie import utils

home = str(Path.home())
DEFAULT_CONFIG_DIR = f"{home}/.config/diediedie/"
DEFAULT_CONFIG_FILE = f"{home}/.config/diediedie/brick.conf"

parser = argparse.ArgumentParser()
# The default OpenStack Authentication args
parser.add_argument("--config-file",
                    metavar="<config-file>",
                    default=None,
                    help="config file for logging. "
                         "Default={}".format(DEFAULT_CONFIG_FILE))

parser.add_argument("--os-auth-type",
                    metavar="<auth-url>",
                    default=utils.env("OS_AUTH_TYPE"),
                    help="URL for the authentication service. "
                         "Default=env[OS_AUTH_URL].")
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

parser.add_argument("--os-project-name",
                    metavar="<auth-project-name>",
                    default=utils.env("OS_PROJECT_NAME"),
                    help="Project name. "
                         "Default=env[OS_PROJECT_NAME].")
parser.add_argument("--os-project-id",
                    metavar="<auth-project-id>",
                    default=utils.env("OS_PROJECT_ID"),
                    help="Project ID"
                         "Default=env[OS_PROJECT_ID].")
parser.add_argument("--os-project-domain-id",
                    metavar="<auth-project-domain-id>",
                    default=utils.env("OS_PROJECT_DOMAIN_ID"),
                    help="Project DOMAIN ID"
                         "Default=env[OS_PROJECT_DOMAIN_ID].")
parser.add_argument("--os-project-domain-name",
                    metavar="<auth-project-domain-name>",
                    default=utils.env("OS_PROJECT_DOMAIN_NAME"),
                    help="Project DOMAIN Name"
                         "Default=env[OS_PROJECT_DOMAIN_NAME].")

parser.add_argument("--os-user-id",
                    metavar="<os-user-id>",
                    default=utils.env("OS_USER_ID"),
                    help="User ID. "
                         "Default=env[OS_USER_ID")
parser.add_argument("--os-user-domain-id",
                    metavar="<auth-user-domain-id>",
                    default=utils.env("OS_USER_DOMAIN_ID"),
                    help="user domain id. "
                         "Default=env[OS_USER_DOMAIN_ID].")
parser.add_argument("--os-user-domain-name",
                    metavar="<auth-user-domain-name>",
                    default=utils.env("OS_USER_DOMAIN_NAME"),
                    help="user domain name. "
                         "Default=env[OS_USER_DOMAIN_NAME].")

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

parser.add_argument("--os-token",
                    metavar="<auth-token>",
                    default=utils.env("OS_TOKEN"),
                    help="Openstack Token. "
                         "Default=env[OS_TOKEN].")

parser.add_argument("--os-region-name",
                    metavar="<auth-region-name>",
                    default=utils.env("OS_REGION_NAME"),
                    help="Openstack Region Name"
                         "Default=env[OS_REGION_NAME].")
