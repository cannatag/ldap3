# encoding: utf-8
"""
"""

# Created on 2013.06.06
#
# Author: Giovanni Cannata
#
# Copyright 2013 - 2018 Giovanni Cannata
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
from time import sleep

from ldap3 import MODIFY_REPLACE, MODIFY_ADD, LEVEL, BASE, SEQUENCE_TYPES
from test.config import random_id, get_connection, add_user, drop_connection, test_singlevalued_attribute, test_multivalued_attribute, test_base, test_name_attr

testcase_id = ''


def make_bytes(value, encoding=None):
    if str is bytes:  # python 2
        if isinstance(value, unicode):
            return value.encode(encoding)
        else:
            return bytes(value)
    else:
        if isinstance(value, SEQUENCE_TYPES):
            return bytes(value)
        else:
            return bytes(value, encoding)


def make_bytearray(value, encoding=None):
    if str is bytes:  # python 2
        if isinstance(value, unicode):
            return value.encode(encoding)
        else:
            return bytearray(value)
    else:
        if isinstance(value, SEQUENCE_TYPES):
            return bytearray(value)
        else:
            return bytearray(value, encoding)


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection()
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_add_operation_from_bytes_literal(self):
        single = b'abc'
        multi = [b'abc', b'def']
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-1', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_add_operation_from_bytes(self):
        single = make_bytes('àèìòù', 'utf-8')
        multi = [make_bytes('àèì', 'utf-8'), make_bytes('òù', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-2', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])

    def test_add_operation_from_byte_values(self):
        if str is not bytes:  # integer list to bytes works only in Python 3
            single = make_bytes([195, 160, 195, 168, 195, 172, 195, 178, 195, 185])
            multi = [make_bytes([195, 160, 195, 168, 195, 172]), make_bytes([195, 178, 195, 185])]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-3', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_add_operation_from_unicode_literal(self):
        single = make_bytes(u'\u00e0\u00e8\u00ec\u00f2\u00f9', 'utf-8')
        multi = [make_bytes(u'\u00e0\u00e8\u00ec', 'utf-8'), make_bytes('\u00f2\u00f9', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-4', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_add_operation_from_unicode_name(self):
        if str is not bytes:  # works only in Python 3
            single = make_bytes('\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')
            multi = [make_bytes('\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}', 'utf-8'), make_bytes('\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-5', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_add_operation_from_bytearray(self):
        single = make_bytearray('àèìòù', 'utf-8')
        multi = [make_bytearray('àèì', 'utf-8'), make_bytearray('òù', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-6', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_add_operation_from_bytearray_values(self):
        single = make_bytearray([195, 160, 195, 168, 195, 172, 195, 178, 195, 185])
        multi = [make_bytearray([195, 160, 195, 168, 195, 172]), make_bytearray([195, 178, 195, 185])]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-7', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_add_operation_from_bytearray_unicode_literal(self):
        single = make_bytearray(u'\u00e0\u00e8\u00ec\u00f2\u00f9', 'utf-8')
        multi = [make_bytearray(u'\u00e0\u00e8\u00ec', 'utf-8'), make_bytearray(u'\u00f2\u00f9', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-8', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_add_operation_from_bytearray_unicode_name(self):
        if str is not bytes:  # works only in python 3
            single = make_bytearray(u'\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')
            multi = [make_bytearray(u'\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}', 'utf-8'), make_bytearray('\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-9', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_compare_true_operation_with_bytes(self):
        single = make_bytes('àèìòù', 'utf-8')
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-10', attributes={test_singlevalued_attribute: single}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.compare(self.delete_at_teardown[0][0], test_singlevalued_attribute, single)
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result

        self.assertEqual(result['description'], 'compareTrue')

    def test_compare_false_operation_with_bytes(self):
        single = make_bytes('àèìòù', 'utf-8')
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-11', attributes={test_singlevalued_attribute: single}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.compare(self.delete_at_teardown[0][0], test_singlevalued_attribute, 'invalid')
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result

        self.assertEqual(result['description'], 'compareFalse')

    def test_modify_operation_from_bytes_literal(self):
        single = b'abc'
        multi = [b'abc', b'def']
        single_mod = b'cba'
        multi_mod = [b'cba', b'fed']
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-12', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
        self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
        if not self.connection.strategy.sync:
            sleep(2)
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_modify_operation_from_bytes(self):
        single = make_bytes('àèìòù', 'utf-8')
        multi = [make_bytes('àèì', 'utf-8'), make_bytes('òù', 'utf-8')]
        single_mod = make_bytes('ùòìèà', 'utf-8')
        multi_mod = [make_bytes('ìèà', 'utf-8'), make_bytes('ùò', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-12', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
        self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
        if not self.connection.strategy.sync:
            sleep(2)
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_modify_operation_from_byte_values(self):
        if str is not bytes:  # integer list to bytes works only in Python 3
            single = make_bytes([195, 160, 195, 168, 195, 172, 195, 178, 195, 185])
            multi = [make_bytes([195, 160, 195, 168, 195, 172]), make_bytes([195, 178, 195, 185])]
            single_mod = make_bytes([195, 185, 195, 178, 195, 172, 195, 168, 195, 160])
            multi_mod = [make_bytes([195, 172, 195, 168, 195, 160]), make_bytes([195, 185, 195, 178])]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-13', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
            self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
            if not self.connection.strategy.sync:
                sleep(2)
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_modify_operation_from_unicode_literal(self):
        single = make_bytes(u'\u00e0\u00e8\u00ec\u00f2\u00f9', 'utf-8')
        multi = [make_bytes(u'\u00e0\u00e8\u00ec', 'utf-8'), make_bytes('\u00f2\u00f9', 'utf-8')]
        single_mod = make_bytes(u'\u00f9\u00f2\u00ec\u00e8\u00e0', 'utf-8')
        multi_mod = [make_bytes(u'\u00ec\u00e8\u00e0', 'utf-8'), make_bytes('\u00f9\u00f2', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-14', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
        self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
        if not self.connection.strategy.sync:
            sleep(2)
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_modify_operation_from_unicode_name(self):
        if str is not bytes:  # works only in Python 3
            single = make_bytes('\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')
            multi = [make_bytes('\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}', 'utf-8'), make_bytes('\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')]
            single_mod = make_bytes('\N{LATIN SMALL LETTER U WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER A WITH GRAVE}', 'utf-8')
            multi_mod = [make_bytes('\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER A WITH GRAVE}', 'utf-8'), make_bytes('\N{LATIN SMALL LETTER U WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}', 'utf-8')]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-15', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
            self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
            if not self.connection.strategy.sync:
                sleep(2)
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_modify_operation_from_bytearray(self):
        single = make_bytearray('àèìòù', 'utf-8')
        multi = [make_bytearray('àèì', 'utf-8'), make_bytearray('òù', 'utf-8')]
        single_mod = make_bytearray('ùòìèà', 'utf-8')
        multi_mod = [make_bytearray('ìèà', 'utf-8'), make_bytearray('ùò', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-16', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
        self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
        if not self.connection.strategy.sync:
            sleep(2)
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_modify_operation_from_bytearray_values(self):
        single = make_bytearray([195, 160, 195, 168, 195, 172, 195, 178, 195, 185])
        multi = [make_bytearray([195, 160, 195, 168, 195, 172]), make_bytearray([195, 178, 195, 185])]
        single_mod = make_bytearray([195, 185, 195, 178, 195, 172, 195, 168, 195, 160])
        multi_mod = [make_bytearray([195, 172, 195, 168, 195, 160]), make_bytearray([195, 185, 195, 178])]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-17', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
        self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
        if not self.connection.strategy.sync:
            sleep(2)
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_modify_operation_from_bytearray_unicode_literal(self):
        single = make_bytearray(u'\u00e0\u00e8\u00ec\u00f2\u00f9', 'utf-8')
        multi = [make_bytearray(u'\u00e0\u00e8\u00ec', 'utf-8'), make_bytearray(u'\u00f2\u00f9', 'utf-8')]
        single_mod = make_bytearray(u'\u00f9\u00f2\u00ec\u00e8\u00e0', 'utf-8')
        multi_mod = [make_bytearray(u'\u00ec\u00e8\u00e0', 'utf-8'), make_bytearray('\u00f9\u00f2', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-18', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
        self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
        if not self.connection.strategy.sync:
            sleep(2)
        result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_modify_operation_from_bytearray_unicode_name(self):
        if str is not bytes:  # works only in python 3
            single = make_bytearray(u'\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')
            multi = [make_bytearray(u'\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}', 'utf-8'), make_bytearray('\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')]
            single_mod = make_bytearray('\N{LATIN SMALL LETTER U WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER A WITH GRAVE}', 'utf-8')
            multi_mod = [make_bytearray('\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER A WITH GRAVE}', 'utf-8'), make_bytearray('\N{LATIN SMALL LETTER U WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}', 'utf-8')]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-19', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))
            self.connection.modify(self.delete_at_teardown[0][0], {test_singlevalued_attribute: (MODIFY_REPLACE, single_mod), test_multivalued_attribute: (MODIFY_ADD, multi_mod)})
            if not self.connection.strategy.sync:
                sleep(2)
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', BASE, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single_mod])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi + multi_mod))

    def test_search_operation_from_bytes_literal(self):
        single = b'abc'
        multi = [b'abc', b'def']
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-20', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        if str is bytes:  # python 2
            byte_filter = b'(&(%s=*%s*)(%s=%s))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
        else:
            # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'

        result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_search_operation_from_bytes(self):
        single = make_bytes('àèìòù', 'utf-8')
        multi = [make_bytes('àèì', 'utf-8'), make_bytes('òù', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-21', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        if str is bytes:  # python 2
            byte_filter = b'(&(%s=*%s*)(%s=%s))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
        else:
            # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'
        result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_search_operation_from_byte_values(self):
        if str is not bytes:  # integer list to bytes works only in Python 3
            single = make_bytes([195, 160, 195, 168, 195, 172, 195, 178, 195, 185])
            multi = [make_bytes([195, 160, 195, 168, 195, 172]), make_bytes([195, 178, 195, 185])]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-22', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'
            result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_search_operation_from_unicode_literal(self):
        single = make_bytes(u'\u00e0\u00e8\u00ec\u00f2\u00f9', 'utf-8')
        multi = [make_bytes(u'\u00e0\u00e8\u00ec', 'utf-8'), make_bytes('\u00f2\u00f9', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-23', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        if str is bytes:  # python 2
            byte_filter = b'(&(%s=*%s*)(%s=%s))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
        else:
            # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'
        result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_search_operation_from_unicode_name(self):
        if str is not bytes:  # works only in Python 3
            single = make_bytes('\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')
            multi = [make_bytes('\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}', 'utf-8'), make_bytes('\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-24', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            if str is bytes:  # python 2
                byte_filter = b'(&(%s=*%s*)(%s=%s))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            else:
                # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
                byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'
            result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_search_operation_from_bytearray(self):
        single = make_bytearray('àèìòù', 'utf-8')
        multi = [make_bytearray('àèì', 'utf-8'), make_bytearray('òù', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-25', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        if str is bytes:  # python 2
            byte_filter = b'(&(%s=*%s*)(%s=%s))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
        else:
            # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'
        result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_search_operation_from_bytearray_values(self):
        single = make_bytearray([195, 160, 195, 168, 195, 172, 195, 178, 195, 185])
        multi = [make_bytearray([195, 160, 195, 168, 195, 172]), make_bytearray([195, 178, 195, 185])]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-26', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        if str is bytes:  # python 2
            byte_filter = b'(&(%s=*%s*)(%s=%s))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
        else:
            # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'
        result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_search_operation_from_bytearray_unicode_literal(self):
        single = make_bytearray(u'\u00e0\u00e8\u00ec\u00f2\u00f9', 'utf-8')
        multi = [make_bytearray(u'\u00e0\u00e8\u00ec', 'utf-8'), make_bytearray(u'\u00f2\u00f9', 'utf-8')]
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-27', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        if str is bytes:  # python 2
            byte_filter = b'(&(%s=*%s*)(%s=%s))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
        else:
            # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'
        result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
        self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_search_operation_from_bytearray_unicode_name(self):
        if str is not bytes:  # works only in python 3
            single = make_bytearray(u'\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')
            multi = [make_bytearray(u'\N{LATIN SMALL LETTER A WITH GRAVE}\N{LATIN SMALL LETTER E WITH GRAVE}\N{LATIN SMALL LETTER I WITH GRAVE}', 'utf-8'), make_bytearray('\N{LATIN SMALL LETTER O WITH GRAVE}\N{LATIN SMALL LETTER U WITH GRAVE}', 'utf-8')]
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-28', attributes={test_singlevalued_attribute: single, test_multivalued_attribute: multi}, test_bytes=True))
            self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
            # byte_filter = b'(&(%b=*%b*)(%b=%b))' % (make_bytes(test_name_attr, 'utf-8'), make_bytes(testcase_id, 'utf-8'), make_bytes(test_singlevalued_attribute, 'utf-8'), single)
            byte_filter = b'(&(' + make_bytes(test_name_attr, 'utf-8') + b'=*' + make_bytes(testcase_id, 'utf-8') + b'*)(' + make_bytes(test_singlevalued_attribute, 'utf-8') + b'=' + single + b'))'
            result = self.connection.search(test_base, byte_filter, attributes=[test_singlevalued_attribute, test_multivalued_attribute])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
            self.assertEqual(len(response), 1)
            self.assertEqual(response[0]['raw_attributes'][test_singlevalued_attribute], [single])
            self.assertEqual(sorted(response[0]['raw_attributes'][test_multivalued_attribute]), sorted(multi))

    def test_modify_operation_from_bytes_for_objectclass(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'byt-29', test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])
        result = self.connection.modify(self.delete_at_teardown[0][0], {'objectClass': (MODIFY_REPLACE, [b'top', b'organizationalunit'])})
        if not self.connection.strategy.sync:
            sleep(2)
            response, result = self.connection.get_response(result)
        else:
            result = self.connection.result

        self.assertTrue(result['description'], ['objectClassViolation', 'objectClassModsProhibited'])

