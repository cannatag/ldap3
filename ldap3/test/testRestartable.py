# """
# Created on 2014.03.29
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
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

from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy,\
    generate_dn, test_base, test_lazy_connection, test_get_info, test_server_mode

from ldap3 import Server, Connection, ServerPool, SEARCH_SCOPE_WHOLE_SUBTREE, STRATEGY_SYNC_RESTARTABLE, POOLING_STRATEGY_ROUND_ROBIN,  SEARCH_SCOPE_SINGLE_LEVEL, ALL_ATTRIBUTES


class Test(unittest.TestCase):
    def test_restartable_invalid_server(self):
        if isinstance(test_server, (list, tuple)):
            hosts = list(test_server) + ['a.b.c.d']
        else:
            hosts = [test_server, 'a.b.c.d']
        search_results = []
        servers = [Server(host=host, port=636, use_ssl=True, get_info=test_get_info, mode=test_server_mode) for host in hosts]

        connection = Connection(ServerPool(servers, POOLING_STRATEGY_ROUND_ROBIN, active=True, exhaust=True), user=test_user, password=test_password, client_strategy=STRATEGY_SYNC_RESTARTABLE, lazy=test_lazy_connection, pool_name='pool1')

        with connection as c:
            c.search(search_base='o=test', search_filter='(cn=test*)', search_scope=SEARCH_SCOPE_WHOLE_SUBTREE, attributes='*')

            for resp in connection.response:
                if resp['type'] == 'searchResEntry':
                    search_results.append(resp['dn'])
        self.assertTrue(len(search_results) > 15)

    def test_restartable_invalid_server2(self):
        # hosts = ['sl08', 'sl09', 'sl10', 'idmprofiler', 'openldap', 'localhost', 'edir1', 'edir2', 'edir3']
        if isinstance(test_server, (list, tuple)):
            hosts = ['sl10', 'edir1', 'idmprofiler'] + list(test_server)
        else:
            hosts = ['sl10', 'edir1', 'idmprofiler', test_server]
        search_results = []
        servers = [Server(host=host, port=389, use_ssl=False) for host in hosts]
        server_pool = ServerPool(servers, POOLING_STRATEGY_ROUND_ROBIN, active=True, exhaust=True)
        connection = Connection(server_pool, user=test_user, password=test_password, client_strategy=STRATEGY_SYNC_RESTARTABLE, lazy=False)
        connection.open()
        connection.bind()
        connection.search(search_base='o=test', search_filter='(objectClass=*)', search_scope=SEARCH_SCOPE_SINGLE_LEVEL)
        if connection.response:
            for resp in connection.response:
                if resp['type'] == 'searchResEntry':
                    search_results.append(resp['dn'])
        connection.unbind()
        self.assertTrue(len(search_results) > 15)

    # def test_restartable_pool(self):
    #     hosts = ['edir', 'edir2', 'edir3']
    #     search_results = []
    #     servers = [Server(host=host, port=389, use_ssl=False) for host in hosts]
    #     server_pool = ServerPool(servers, POOLING_STRATEGY_ROUND_ROBIN, active=True, exhaust=True)
    #     connection = Connection(server_pool, user=test_user, password=test_password, client_strategy=STRATEGY_SYNC_RESTARTABLE, lazy=False)
    #     connection.open()
    #     connection.bind()
    #     for x in range(10000):
    #         connection.search(search_base='o=test', search_filter='(objectClass=*)', attributes=ALL_ATTRIBUTES, search_scope=SEARCH_SCOPE_SINGLE_LEVEL)
    #         sleep(1)
