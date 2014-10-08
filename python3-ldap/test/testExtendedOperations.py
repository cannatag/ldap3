# Created on 2014.06.30
#
# @author: Giovanni Cannata
#
# Copyright 2013 Giovanni Cannata
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

import unittest
from ldap3 import Server, Connection, STRATEGY_REUSABLE_THREADED, GET_DSA_INFO, LDAPExtensionError
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_lazy_connection, test_server_context


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=GET_DSA_INFO)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_who_am_i_extension(self):
        try:
            self.connection.extend.standard.who_am_i()
            result = self.connection.result
            self.assertTrue(result['description'] in ['success', 'protocolError'])
        except LDAPExtensionError as e:
            if not e.args[0] == 'extension not in DSA list of supported extensions':
                raise

    def test_get_bind_dn_extension(self):
        result = self.connection.extend.novell.get_bind_dn()
        # result = self.connection.result
        self.assertTrue(test_user in result)

    def test_paged_search_accumulator(self):
        responses = self.connection.extend.standard.paged_search('o=test', '(&(cn=*)(!(cn=*move*)))', generator=False)
        self.assertGreater(len(responses), 20)

    def test_paged_search_generator(self):
        responses = []
        for response in self.connection.extend.standard.paged_search('o=test', '(&(cn=*)(!(cn=*move*)))'):
            responses.append(response)
        self.assertGreater(len(responses), 20)


    def test_novell_list_replicas(self):
        result = self.connection.extend.novell.list_replicas('cn=' + test_server + ',' + test_server_context)
        self.assertEquals(result, None)

    def test_novell_replica_info(self):
        result = self.connection.extend.novell.replica_info('cn=' + test_server + ',' + test_server_context, '')
        self.assertEquals(result, '')

    def test_novell_partition_entry_count(self):
        result = self.connection.extend.novell.partition_entry_count('o=test')
        self.assertTrue(result > 200)