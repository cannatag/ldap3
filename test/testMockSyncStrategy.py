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

from ldap3 import Server, Connection, MOCK_SYNC, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
from ldap3.protocol.rfc4512 import SchemaInfo, DsaInfo
from ldap3.protocol.schemas.edir888 import edir_8_8_8_dsa_info, edir_8_8_8_schema
from test import test_base, generate_dn, test_name_attr, test_moved, random_id


testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        schema = SchemaInfo.from_json(edir_8_8_8_schema)
        info = DsaInfo.from_json(edir_8_8_8_dsa_info, schema)
        server = Server.from_definition('MockSyncServer', info, schema)
        self.connection = Connection(server, client_strategy=MOCK_SYNC)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def test_open(self):
        self.connection.open()
        self.assertFalse(self.connection.closed)

    def test_bind(self):
        self.connection.open()
        self.connection.bind()
        self.assertTrue(self.connection.bound)
