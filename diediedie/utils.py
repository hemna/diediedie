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
"""Utilities and helper functions."""

import os
import pprint
import sys

from cinderclient import client as cinder
from os_brick.initiator import connector
from oslo_log import log as logging
from oslo_utils import encodeutils
from oslo_utils import netutils
import prettytable
import six


LOG = logging.getLogger(__name__)


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


def env(*vars, **kwargs):
    """This returns the first environment variable set.

    if none are non-empty, defaults to '' or keyword arg default

    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def _print(pt, order):
    if sys.version_info >= (3, 0):
        print(pt.get_string(sortby=order))
    else:
        print(encodeutils.safe_encode(pt.get_string(sortby=order)))


def print_list(objs, fields, exclude_unavailable=False, formatters=None,
               sortby_index=0):
    '''Prints a list of objects.

    @param objs: Objects to print
    @param fields: Fields on each object to be printed
    @param exclude_unavailable: Boolean to decide if unavailable fields are
                                removed
    @param formatters: Custom field formatters
    @param sortby_index: Results sorted against the key in the fields list at
                         this index; if None then the object order is not
                         altered
    '''
    formatters = formatters or {}
    mixed_case_fields = ['serverId']
    removed_fields = []
    rows = []

    for o in objs:
        row = []
        for field in fields:
            if field in removed_fields:
                continue
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                if type(o) == dict and field in o:
                    data = o[field]
                else:
                    if not hasattr(o, field_name) and exclude_unavailable:
                        removed_fields.append(field)
                        continue
                    else:
                        data = getattr(o, field_name, '')
                if data is None:
                    data = '-'
                if isinstance(data, six.string_types) and "\r" in data:
                    data = data.replace("\r", " ")
                row.append(data)
        rows.append(row)

    for f in removed_fields:
        fields.remove(f)

    pt = prettytable.PrettyTable((f for f in fields), caching=False)
    pt.aligns = ['l' for f in fields]
    for row in rows:
        pt.add_row(row)

    if sortby_index is None:
        order_by = None
    else:
        order_by = fields[sortby_index]
    _print(pt, order_by)


def no_unicode(object, context, maxlevels, level):
    """ change unicode u'foo' to string 'foo' when pretty printing"""
    if pprint._type(object) is unicode:
        object = str(object)
    return pprint._safe_repr(object, context, maxlevels, level)


def print_dict(d, property="Property", value_align="c",
               disable_unicode=False):
    """Print out a dict."""
    pp = pprint.PrettyPrinter(indent=2)
    # disable the annoying leading 'u'
    if disable_unicode:
        pp.format = no_unicode
    pt = prettytable.PrettyTable([property, 'Value'], caching=False)
    # pt.aligns = ['l', 'l']
    pt.align['Value'] = value_align
    for r in six.iteritems(d):
        r = list(r)

        if isinstance(r[1], list):
            if isinstance(r[1][0], six.string_types):
                r[1] = '\n'.join(r[1])
            else:
                tmp = []
                for item in r[1]:
                    item_str = pp.pformat(item)
                    tmp.append(item_str)

                r[1] = '\n'.join(tmp)
        if isinstance(r[1], six.string_types) and "\r" in r[1]:
            r[1] = r[1].replace("\r", " ")
        pt.add_row(r)
    _print(pt, property)
