# """
# Created on 2013.08.05
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of pureLDAP.
#
# pureLDAP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pureLDAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pureLDAP in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import unittest

from ldap3 import Server, Connection, ServerPool, Tls, STRATEGY_REUSABLE_THREADED
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, \
    test_lazy_connection, test_server_context, test_get_info, test_server_mode, test_pooling_strategy, \
    test_pooling_active, test_pooling_exhaust


class Test(unittest.TestCase):
    def setUp(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_get_replica_list_extension(self):
        if isinstance(test_server, (list, tuple)):
            result = self.connection.extended('2.16.840.1.113719.1.27.100.19', ('cn=' + test_server[0] + ',' + test_server_context))
        else:
            result = self.connection.extended('2.16.840.1.113719.1.27.100.19', ('cn=' + test_server + ',' + test_server_context))

        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'noSuchObject'])

    def test_who_am_i_extension(self):
        result = self.connection.extended('1.3.6.1.4.1.4203.1.11.3')
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'protocolError'])

    def test_get_bind_dn_extension(self):
        result = self.connection.extended('2.16.840.1.113719.1.27.100.31')
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success'])

    def test_start_tls_extension(self):
        self.connection.server.tls = Tls()
        result = self.connection.extended('1.3.6.1.4.1.1466.20037')
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success'])
