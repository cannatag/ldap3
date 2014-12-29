# Created on 2014.06.30
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
from ldap3 import Server, Connection, ServerPool, STRATEGY_REUSABLE_THREADED, GET_DSA_INFO, LDAPExtensionError
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, \
    test_lazy_connection, test_server_context, test_server_mode, test_pooling_strategy, test_pooling_active, \
    test_pooling_exhaust, test_server_edir_name


class Test(unittest.TestCase):
    def setUp(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=GET_DSA_INFO, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=GET_DSA_INFO, mode=test_server_mode)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_who_am_i_extension(self):
        if not self.connection.strategy.pooled:
            try:
                if not self.connection.server.info:
                    self.connection.refresh_server_info()
                self.connection.extend.standard.who_am_i()
                result = self.connection.result
                self.assertTrue(result['description'] in ['success', 'protocolError'])
            except LDAPExtensionError as e:
                if not e.args[0] == 'extension not in DSA list of supported extensions':
                    raise

    def test_get_bind_dn_extension(self):
        if not self.connection.strategy.pooled:
            result = self.connection.extend.novell.get_bind_dn()
            self.assertTrue(test_user in result)

    def test_paged_search_accumulator(self):
        responses = self.connection.extend.standard.paged_search('o=test', '(&(cn=*)(!(cn=*move*)))', generator=False)
        self.assertTrue(len(responses) > 20)

    def test_paged_search_generator(self):
        responses = []
        for response in self.connection.extend.standard.paged_search('o=test', '(&(cn=*)(!(cn=*move*)))'):
            responses.append(response)
        self.assertTrue(len(responses) > 20)


    def test_novell_list_replicas(self):
        result = self.connection.extend.novell.list_replicas('cn=' + test_server_edir_name + ',' + test_server_context)

        self.assertEqual(result, None)

    def test_novell_replica_info(self):
        result = self.connection.extend.novell.replica_info('cn=' + test_server_edir_name + ',' + test_server_context, '')

        self.assertEqual(result, '')

    def test_novell_partition_entry_count(self):
        result = self.connection.extend.novell.partition_entry_count('o=test')
        self.assertTrue(result > 60)
