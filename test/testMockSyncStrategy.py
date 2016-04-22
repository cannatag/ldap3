# Created on 2015.02.3
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

from ldap3 import Server, Connection, MOCK_SYNC, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, OFFLINE_SLAPD_2_4
from ldap3.protocol.rfc4512 import SchemaInfo, DsaInfo
from ldap3.protocol.schemas.edir888 import edir_8_8_8_dsa_info, edir_8_8_8_schema
from test import test_base, generate_dn, test_name_attr, test_moved, random_id
testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        schema = SchemaInfo.from_json(edir_8_8_8_schema)
        info = DsaInfo.from_json(edir_8_8_8_dsa_info, schema)
        server_1 = Server.from_definition('MockSyncServer', info, schema)
        self.connection_1 = Connection(server_1, user='mock_user', password='mock_password', client_strategy=MOCK_SYNC)
        server_2 = Server('dummy', get_info=OFFLINE_SLAPD_2_4)
        self.connection_2 = Connection(server_2, user='mock_user', password='mock_password', client_strategy=MOCK_SYNC)

    def tearDown(self):
        self.connection_1.unbind()
        self.assertFalse(self.connection_1.bound)

    def test_open_1(self):
        self.connection_1.open()
        self.assertFalse(self.connection_1.closed)

    def test_open_2(self):
        self.connection_2.open()
        self.assertFalse(self.connection_2.closed)

    def test_bind_1(self):
        self.connection_1.open()
        self.connection_1.bind()
        self.assertTrue(self.connection_1.bound)

    def test_bind_2(self):
        self.connection_2.open()
        self.connection_2.bind()
        self.assertTrue(self.connection_2.bound)

    def test_unbind_1(self):
        self.connection_1.open()
        self.connection_1.bind()
        self.assertTrue(self.connection_1.bound)
        self.connection_1.unbind()
        self.assertFalse(self.connection_1.bound)

    def test_unbind_2(self):
        self.connection_2.open()
        self.connection_2.bind()
        self.assertTrue(self.connection_2.bound)
        self.connection_2.unbind()
        self.assertFalse(self.connection_2.bound)
