"""
"""

# Created on 2014.03.29
#
# Author: Giovanni Cannata
#
# Copyright 2014 - 2020 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import unittest

from test.config import test_server, test_user, test_password, test_lazy_connection, test_get_info, test_server_mode, test_base, test_strategy, test_server_type
from ldap3 import Server, Connection, ServerPool, RESTARTABLE, ROUND_ROBIN, BASE, MOCK_SYNC, MOCK_ASYNC
from ldap3.utils.config import set_config_parameter
import socket

class Test(unittest.TestCase):

    def setUp(self):
        # these settings will speeed up the test execution 
        set_config_parameter("RESTARTABLE_SLEEPTIME", 0.01)
        set_config_parameter("RESTARTABLE_TRIES", 1)
        set_config_parameter("POOLING_LOOP_TIMEOUT", 0)

    def test_restartable_invalid_server(self):
        if test_server_type != 'NONE' and test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
            if isinstance(test_server, (list, tuple)):
                hosts = ['a.b.c.d'] + list(test_server)
            else:
                hosts = ['a.b.c.d', test_server]
            search_results = []
            servers = [Server(host=host, port=636, use_ssl=True, get_info=test_get_info, mode=test_server_mode) for host in hosts]
            connection = Connection(ServerPool(servers, ROUND_ROBIN, active=True, exhaust=True), user=test_user, password=test_password, client_strategy=RESTARTABLE, lazy=test_lazy_connection, pool_name='pool1')
                
            with connection as c:
                c.search(search_base=test_base, search_filter='(' + test_base.split(',')[0] + ')', search_scope=BASE, attributes='*')
                for resp in connection.response:
                    if resp['type'] == 'searchResEntry':
                        search_results.append(resp['dn'])
            self.assertEqual(len(search_results), 1)

    def test_restartable_invalid_server2(self):
        if test_server_type not in  ['NONE', 'AD']:
            if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
                if isinstance(test_server, (list, tuple)):
                    hosts = ['a.b.c.d'] + list(test_server)
                else:
                    hosts = ['a.b.c.d', test_server]
                search_results = []
                servers = [Server(host=host, port=389, use_ssl=False) for host in hosts]
                server_pool = ServerPool(servers, ROUND_ROBIN, active=True, exhaust=True)
                connection = Connection(server_pool, user=test_user, password=test_password, client_strategy=RESTARTABLE, lazy=False)
                connection.open()
                connection.bind()
                connection.search(search_base=test_base, search_filter='(' + test_base.split(',')[0] + ')', search_scope=BASE)
                if connection.response:
                    for resp in connection.response:
                        if resp['type'] == 'searchResEntry':
                            search_results.append(resp['dn'])
                connection.unbind()
                self.assertEqual(len(search_results), 1)

    def test_restartable_reconnect(self):
        if test_server_type not in  ['NONE', 'AD']:
            if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
                if isinstance(test_server, (list, tuple)):
                    hosts = ['a.b.c.d'] + list(test_server)
                else:
                    hosts = ['a.b.c.d', test_server]
                search_results = []
                servers = [Server(host=host, port=389, use_ssl=False) for host in hosts]
                server_pool = ServerPool(servers, ROUND_ROBIN, active=True, exhaust=True)
                connection = Connection(server_pool, user=test_user, password=test_password, client_strategy=RESTARTABLE, lazy=False)
                connection.open()
                connection.bind()
                #simulate broken connection
                connection.socket.shutdown(socket.SHUT_RDWR)
                #make sure we reconnect automatically
                connection.search(search_base=test_base, search_filter='(' + test_base.split(',')[0] + ')', search_scope=BASE)
                if connection.response:
                    for resp in connection.response:
                        if resp['type'] == 'searchResEntry':
                            search_results.append(resp['dn'])
                connection.unbind()
                self.assertEqual(len(search_results), 1)
