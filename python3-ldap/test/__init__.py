"""
@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

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

# noinspection PyUnresolvedReferences
from ldap3 import AUTH_SIMPLE, STRATEGY_SYNC, STRATEGY_ASYNC_THREADED

test_server = 'edir'
test_user = 'cn=admin,o=risorse'
test_password = 'password'

test_port = 389
test_port_ssl = 636
test_authentication = AUTH_SIMPLE
test_strategy = STRATEGY_SYNC
test_strategy = STRATEGY_ASYNC_THREADED
