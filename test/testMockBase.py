# Created on 2016.04.17
#
# Author: Giovanni Cannata & signedbit
#
# Copyright 2016 - 2020 Giovanni Cannata & signedbit
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

from ldap3 import SchemaInfo, DsaInfo, Server, Connection, MOCK_SYNC
from ldap3.operation import search
from ldap3.core.exceptions import LDAPSizeLimitExceededResult
from ldap3.protocol.schemas.edir914 import edir_9_1_4_schema, edir_9_1_4_dsa_info


class Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = SchemaInfo.from_json(edir_9_1_4_schema)
        info = DsaInfo.from_json(edir_9_1_4_dsa_info, cls.schema)
        cls.server = Server.from_definition('MockSyncServer', info, cls.schema)
        cls.connection = Connection(cls.server, user='cn=user1,ou=test', password='test1', client_strategy=MOCK_SYNC)

        # create fixtures
        cls.connection.strategy.add_entry('cn=user1,ou=test', {'userPassword': 'test1', 'revision': 1})
        cls.connection.strategy.add_entry('cn=user2,ou=test', {'userPassword': 'test2', 'revision': 2})
        cls.connection.strategy.add_entry('cn=user3,ou=test', {'userPassword': 'test3', 'revision': 3})

    @classmethod
    def tearDownClass(cls):
        cls.connection.unbind()

    def test_and_evaluates_correctly_when_first_operand_doesnt_match(self):
        actual = len(self._evaluate_filter('(&(revision=1)(userPassword=notarealvalue))'))
        expected = 0

        self.assertEqual(actual, expected)

    def test_and_evaluates_correctly_when_second_operand_doesnt_match(self):
        actual = len(self._evaluate_filter('(&(userPassword=notarealvalue)(revision=1))'))
        expected = 0

        self.assertEqual(actual, expected)

    def test_and_evaluates_correctly_when_both_operands_match(self):
        actual = len(self._evaluate_filter('(&(revision=1)(userPassword=test1))'))
        expected = 1

        self.assertEqual(actual, expected)

    # def test_raises_size_limit_exceeded_exception(self):
    #     connection = Connection(self.server, user='cn=user1,ou=test', password='test1', client_strategy=MOCK_SYNC, raise_exceptions=True)
    #     # create fixtures
    #     connection.strategy.add_entry('cn=user1,ou=test', {'userPassword': 'test1', 'revision': 1})
    #     connection.strategy.add_entry('cn=user2,ou=test', {'userPassword': 'test2', 'revision': 2})
    #     connection.strategy.add_entry('cn=user3,ou=test', {'userPassword': 'test3', 'revision': 3})
    #     connection.bind()
    #     with self.assertRaises(LDAPSizeLimitExceededResult):
    #         connection.search('ou=test', '(cn=*)', size_limit=1)

    def _evaluate_filter(self, search_filter):
        filter_root = search.parse_filter(search_filter, self.schema, auto_escape=True, auto_encode=False, validator=None, check_names=False)
        candidates = self.server.dit
        return self.connection.strategy.evaluate_filter_node(filter_root, candidates)
