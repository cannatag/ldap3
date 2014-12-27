# Created on 2013.09.13
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

from ldap3 import Server, Connection, ServerPool, GET_ALL_INFO, STRATEGY_REUSABLE_THREADED, SchemaInfo, DsaInfo
from ldap3.protocol.rfc4512 import ObjectClassInfo, AttributeTypeInfo
from test import test_server, test_port, test_user, test_password, test_authentication,\
    test_strategy, test_lazy_connection, test_server_mode, test_pooling_strategy, test_pooling_active, test_pooling_exhaust


class Test(unittest.TestCase):
    def setUp(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=GET_ALL_INFO, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=GET_ALL_INFO, mode=test_server_mode)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_schema(self):
        self.assertTrue(type(self.connection.server.schema), SchemaInfo)

    def test_object_classes(self):
        if not self.connection.strategy.pooled:
            if not self.connection.server.info:
                self.connection.refresh_server_info()
            self.assertTrue(type(self.connection.server.schema.object_classes['iNetOrgPerson']), ObjectClassInfo)

    def test_attributes_types(self):
        if not self.connection.server.info:
            self.connection.refresh_server_info()
        if self.connection.server.schema:
            self.assertTrue(type(self.connection.server.schema.attribute_types['cn']), AttributeTypeInfo)

    def test_json_definition(self):
        if not self.connection.strategy.pooled:
            if not self.connection.server.info:
                self.connection.refresh_server_info()

            json_info = self.connection.server.info.to_json()
            json_schema = self.connection.server.schema.to_json()
            info = DsaInfo.from_json(json_info)
            schema = SchemaInfo.from_json(json_schema)
            server1 = Server.from_definition(test_server, info, schema)
            json_info1 = server1.info.to_json()
            json_schema1 = server1.schema.to_json()
            self.assertEqual(json_info, json_info1)
            self.assertEqual(json_schema, json_schema1)
