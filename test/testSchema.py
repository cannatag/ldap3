# Created on 2013.09.13
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

from ldap3 import Server, ALL, SchemaInfo, DsaInfo
from ldap3.protocol.rfc4512 import ObjectClassInfo, AttributeTypeInfo
from test import test_server, get_connection, drop_connection


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection(get_info=ALL, lazy_connection=False)
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection)
        self.assertFalse(self.connection.bound)

    def test_schema(self):
        if not self.connection.strategy.pooled:
            self.assertEqual(type(self.connection.server.schema), SchemaInfo)

    def test_object_classes(self):
        if not self.connection.strategy.pooled:
            self.assertEqual(type(self.connection.server.schema.object_classes['iNetOrgPerson']), ObjectClassInfo)

    def test_attributes_types(self):
        if self.connection.server.schema:
            self.assertEqual(type(self.connection.server.schema.attribute_types['cn']), AttributeTypeInfo)

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
