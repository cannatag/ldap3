"""
"""

# Created on 2014.04.26
#
# Author: Giovanni Cannata
#
# Copyright 2014 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from base64 import b64encode, b64decode
import datetime
from ..utils.ciDict import CaseInsensitiveDict
from ..core.exceptions import LDAPDefinitionError


def escape_bytes(bytes_value):
    if str != bytes:  # Python 3
        if isinstance(bytes_value, str):
            bytes_value = bytearray(bytes_value, encoding='utf-8')
        escaped = '\\'.join([('%02x' % int(b)) for b in bytes_value])
    else:  # Python 2
        if isinstance(bytes_value, unicode):
            bytes_value = bytes_value.encode('utf-8')
        escaped = '\\'.join([('%02x' % ord(b)) for b in bytes_value])

    return ('\\' + escaped) if escaped else ''


def prepare_for_stream(value):
    if str != bytes:  # Python 3
        return value
    else:  # Python 2
        return value.decode()


def json_encode_b64(obj):
    try:
        return dict(encoding='base64', encoded=b64encode(obj))
    except:
        raise LDAPDefinitionError('unable to encode ' + str(obj))


def check_json_dict(json_dict):
    """
    # needed only for python 2
    for k, v in json_dict.items():
        if isinstance(v, (CaseInsensitiveDict)):
            json_dict[k] = v._store
            check_json_dict(json_dict['k'])
        else:
            if isinstance(v, (list, tuple)):
                for index, element in enumerate(v):
                    if isinstance(element, (CaseInsensitiveDict)):
                        json_dict[k][v] = element._store
                        check_json_dict(json_dict[k][v])
                    else:
                        v[index] = format_json(element)
            else:
                json_dict[k] == format_json(v)
    """

def json_hook(obj):
    if hasattr(obj, 'keys') and len(obj.keys()) == 2 and 'encoding' in obj.keys() and 'encoded' in obj.keys():
        return b64decode(obj['encoded'])

    return obj


def format_json(obj):
    print(type(obj), obj)
    if isinstance(obj, CaseInsensitiveDict):
        return obj._store

    if isinstance(obj, datetime.datetime):
        return str(obj)

    try:
        if str != bytes:  # python3
            return str(obj, 'utf-8', errors='strict')
        else:
            if isinstance(obj, unicode):
                return obj
            else:
                return unicode(obj, 'utf-8', errors='strict')
    except (TypeError, UnicodeDecodeError):
        pass

    try:
        return json_encode_b64(bytes(obj))
    except:
        pass

    print('unable', type(obj), obj)

    return 'unable to convert'