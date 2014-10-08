# Created on 2013.09.13
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

from ldap3 import Server, Connection, GET_ALL_INFO, STRATEGY_REUSABLE_THREADED
from ldap3.protocol.rfc4512 import SchemaServerInfo, ObjectClassInfo, AttributeTypeInfo
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_lazy_connection, test_get_info


class Test(unittest.TestCase):
    def setUp(self):
        self.server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=3)
        self.connection = Connection(self.server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_schema(self):
        self.assertTrue(type(self.server.schema), SchemaServerInfo)

    def test_object_classes(self):
        self.assertTrue(type(self.server.schema.object_classes['inetorgperson']), ObjectClassInfo)

    def test_attributes_types(self):
        self.assertTrue(type(self.server.schema.attribute_types['cn']), AttributeTypeInfo)
