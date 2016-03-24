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
Sample script to dump out the initiator connector dictionary on the
current system.

"""
import sys

from oslo_config import cfg
from oslo_log import log

from diediedie import auth_args
from diediedie import utils
from os_brick.local_dev import lvm

parser = auth_args.parser
parser.add_argument("-g", "--group",
                    metavar="<lvm-volume-group>",
                    default=None,
                    help='LVM volume group')

CONF = cfg.CONF
log.register_options(CONF)
CONF([], project='brick', version='1.0')
log.setup(CONF, 'brick')
LOG = log.getLogger(__name__)


def main():
    """The main."""
    args = parser.parse_args()
    vg_name = args.group
    #vg = lvm.LVM(vg_name, 'sudo')
    root_helper = 'sudo'
    groups = lvm.LVM.get_all_volume_groups(root_helper, vg_name=vg_name)
    for group in groups:
        utils.print_dict(group, value_align='l', disable_unicode=True)
        vols = lvm.LVM.get_lv_info(root_helper, vg_name=group['name'])
        for vol in vols:
            utils.print_dict(vol)

if __name__ == "__main__":
    main()
