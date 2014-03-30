"""
Created on 2013.05.23

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""

import unittest

from ldap3.protocol.rfc4511 import LDAPDN, AddRequest, AttributeList, Attribute, AttributeDescription, AttributeValue, AssertionValue, Substrings, Initial, Any, Final, SubstringFilter, And, Or, Not, Substring
from ldap3.protocol.rfc4511 import SearchRequest, ValsAtLeast1, Scope, Integer0ToMax, TypesOnly, Filter, AttributeSelection, Selector, EqualityMatch
from ldap3.core.connection import Connection
from ldap3.core.server import Server
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, test_dn_builder, test_lazy_connection


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(test_server, test_port, allowed_referral_hosts=('*', True))
        self.connection = Connection(server, auto_bind=True, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=False)

    def tearDown(self):
        self.connection.unbind()

    def test_search_equality(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('tost1')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('tust1')
        attribute2['type'] = AttributeDescription('givenName')
        attribute2['vals'] = vals2

        attribute3 = Attribute()
        vals3 = ValsAtLeast1()
        vals3[0] = AttributeValue('inetOrgPerson')
        attribute3['type'] = AttributeDescription('objectClass')
        attribute3['vals'] = vals3

        attributes = AttributeList()
        attributes[0] = attribute1
        attributes[1] = attribute2
        attributes[2] = attribute3

        add_req = AddRequest()
        add_req['entry'] = LDAPDN(test_dn_builder(test_base, 'test-search-1'))
        add_req['attributes'] = attributes

        self.connection.send('addRequest', add_req)

        assertion1 = EqualityMatch()
        assertion1['attributeDesc'] = AttributeDescription('cn')
        assertion1['assertionValue'] = AssertionValue('test-search-1')

        search_filter = Filter()
        search_filter['equalityMatch'] = assertion1

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        search_req = SearchRequest()
        search_req['baseObject'] = LDAPDN(test_base)
        search_req['scope'] = Scope('singleLevel')
        search_req['derefAliases'] = 'neverDerefAliases'
        search_req['sizeLimit'] = Integer0ToMax(0)
        search_req['timeLimit'] = Integer0ToMax(0)
        search_req['typesOnly'] = TypesOnly(False)
        search_req['filter'] = search_filter
        search_req['attributes'] = attributes

        self.connection.send('searchRequest', search_req)
        self.assertTrue(True)

    def test_search_substring(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('test2-1')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('test2-2')
        attribute2['type'] = AttributeDescription('givenName')
        attribute2['vals'] = vals2

        attribute3 = Attribute()
        vals3 = ValsAtLeast1()
        vals3[0] = AttributeValue('inetOrgPerson')
        attribute3['type'] = AttributeDescription('objectClass')
        attribute3['vals'] = vals3

        attributes = AttributeList()
        attributes[0] = attribute1
        attributes[1] = attribute2
        attributes[2] = attribute3

        add_req = AddRequest()
        add_req['entry'] = LDAPDN(test_dn_builder(test_base, 'test-search-2'))
        add_req['attributes'] = attributes
        self.connection.send('addRequest', add_req)

        substrings = Substrings()
        substring1 = Substring().setComponentByName('initial', Initial('test'))
        substring2 = Substring().setComponentByName('any', Any('se'))
        substring3 = Substring().setComponentByName('any', Any('ch'))
        substring4 = Substring().setComponentByName('final', Final('2'))

        substrings[0] = substring1
        substrings[1] = substring2
        substrings[2] = substring3
        substrings[3] = substring4

        substring_filter = SubstringFilter()
        substring_filter['type'] = 'cn'
        substring_filter['substrings'] = substrings
        search_filter = Filter()
        search_filter['substringFilter'] = substring_filter

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        search_req = SearchRequest()
        search_req['baseObject'] = LDAPDN(test_base)
        search_req['scope'] = Scope('singleLevel')
        search_req['derefAliases'] = 'neverDerefAliases'
        search_req['sizeLimit'] = Integer0ToMax(0)
        search_req['timeLimit'] = Integer0ToMax(0)
        search_req['typesOnly'] = TypesOnly(False)
        search_req['filter'] = search_filter
        search_req['attributes'] = attributes

        self.connection.send('searchRequest', search_req)
        self.assertTrue(True)

    def test_search_and(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('test3-1')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('test3-2')
        attribute2['type'] = AttributeDescription('givenName')
        attribute2['vals'] = vals2

        attribute3 = Attribute()
        vals3 = ValsAtLeast1()
        vals3[0] = AttributeValue('inetOrgPerson')
        attribute3['type'] = AttributeDescription('objectClass')
        attribute3['vals'] = vals3

        attributes = AttributeList()
        attributes[0] = attribute1
        attributes[1] = attribute2
        attributes[2] = attribute3

        add_req = AddRequest()
        add_req['entry'] = LDAPDN(test_dn_builder(test_base, 'test-search-3'))
        add_req['attributes'] = attributes

        self.connection.send('addRequest', add_req)

        assertion1 = EqualityMatch()
        assertion1['attributeDesc'] = AttributeDescription('cn')
        assertion1['assertionValue'] = AssertionValue('test-search-3')

        assertion2 = EqualityMatch()
        assertion2['attributeDesc'] = AttributeDescription('objectClass')
        assertion2['assertionValue'] = AssertionValue('inetOrgPerson')

        search_filter1 = Filter()
        search_filter1['equalityMatch'] = assertion1

        search_filter2 = Filter()
        search_filter2['equalityMatch'] = assertion2

        and_filter = And()
        and_filter[0] = search_filter1
        and_filter[1] = search_filter2

        search_filter = Filter()
        search_filter['and'] = and_filter

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        search_req = SearchRequest()
        search_req['baseObject'] = LDAPDN(test_base)
        search_req['scope'] = Scope('singleLevel')
        search_req['derefAliases'] = 'neverDerefAliases'
        search_req['sizeLimit'] = Integer0ToMax(0)
        search_req['timeLimit'] = Integer0ToMax(0)
        search_req['typesOnly'] = TypesOnly(False)
        search_req['filter'] = search_filter
        search_req['attributes'] = attributes

        self.connection.send('searchRequest', search_req)
        self.assertTrue(True)

    def test_search_or(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('test4-1')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('test4-2')
        attribute2['type'] = AttributeDescription('givenName')
        attribute2['vals'] = vals2

        attribute3 = Attribute()
        vals3 = ValsAtLeast1()
        vals3[0] = AttributeValue('inetOrgPerson')
        attribute3['type'] = AttributeDescription('objectClass')
        attribute3['vals'] = vals3

        attributes = AttributeList()
        attributes[0] = attribute1
        attributes[1] = attribute2
        attributes[2] = attribute3

        add_req1 = AddRequest()
        add_req1['entry'] = LDAPDN(test_dn_builder(test_base, 'test-search-4'))
        add_req1['attributes'] = attributes

        self.connection.send('addRequest', add_req1)

        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('test5-1')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('test5-2')
        attribute2['type'] = AttributeDescription('givenName')
        attribute2['vals'] = vals2

        attribute3 = Attribute()
        vals3 = ValsAtLeast1()
        vals3[0] = AttributeValue('inetOrgPerson')
        attribute3['type'] = AttributeDescription('objectClass')
        attribute3['vals'] = vals3

        attributes = AttributeList()
        attributes[0] = attribute1
        attributes[1] = attribute2
        attributes[2] = attribute3

        add_req2 = AddRequest()
        add_req2['entry'] = LDAPDN(test_dn_builder(test_base, 'test-search-5'))
        add_req2['attributes'] = attributes

        self.connection.send('addRequest', add_req2)

        assertion1 = EqualityMatch()
        assertion1['attributeDesc'] = AttributeDescription('cn')
        assertion1['assertionValue'] = AssertionValue('test-search-4')

        assertion2 = EqualityMatch()
        assertion2['attributeDesc'] = AttributeDescription('cn')
        assertion2['assertionValue'] = AssertionValue('test-search-5')

        search_filter1 = Filter()
        search_filter1['equalityMatch'] = assertion1

        search_filter2 = Filter()
        search_filter2['equalityMatch'] = assertion2

        or_filter = Or()
        or_filter[0] = search_filter1
        or_filter[1] = search_filter2

        search_filter = Filter()
        search_filter['or'] = or_filter

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        search_req = SearchRequest()
        search_req['baseObject'] = LDAPDN(test_base)
        search_req['scope'] = Scope('singleLevel')
        search_req['derefAliases'] = 'neverDerefAliases'
        search_req['sizeLimit'] = Integer0ToMax(0)
        search_req['timeLimit'] = Integer0ToMax(0)
        search_req['typesOnly'] = TypesOnly(False)
        search_req['filter'] = search_filter
        search_req['attributes'] = attributes

        self.connection.send('searchRequest', search_req)
        self.assertTrue(True)

    def test_search_not(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('test6-1')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('test6-2')
        attribute2['type'] = AttributeDescription('givenName')
        attribute2['vals'] = vals2

        attribute3 = Attribute()
        vals3 = ValsAtLeast1()
        vals3[0] = AttributeValue('inetOrgPerson')
        attribute3['type'] = AttributeDescription('objectClass')
        attribute3['vals'] = vals3

        attributes = AttributeList()
        attributes[0] = attribute1
        attributes[1] = attribute2
        attributes[2] = attribute3

        add_req = AddRequest()
        add_req['entry'] = LDAPDN(test_dn_builder(test_base, 'test-search-6'))
        add_req['attributes'] = attributes

        self.connection.send('addRequest', add_req)

        assertion1 = EqualityMatch()
        assertion1['attributeDesc'] = AttributeDescription('cn')
        assertion1['assertionValue'] = AssertionValue('test-search-6')

        search_filter = Filter()
        search_filter['equalityMatch'] = assertion1

        not_filter = Not()
        not_filter['innerNotFilter'] = search_filter

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        search_req = SearchRequest()
        search_req['baseObject'] = LDAPDN(test_base)
        search_req['scope'] = Scope('singleLevel')
        search_req['derefAliases'] = 'neverDerefAliases'
        search_req['sizeLimit'] = Integer0ToMax(0)
        search_req['timeLimit'] = Integer0ToMax(0)
        search_req['typesOnly'] = TypesOnly(False)
        search_req['filter'] = Filter().setComponentByName('notFilter', not_filter)
        search_req['attributes'] = attributes

        self.connection.send('searchRequest', search_req)
        self.assertTrue(True)
