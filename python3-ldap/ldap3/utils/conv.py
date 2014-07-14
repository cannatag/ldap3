"""
Created on 2014.04.26

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""


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
