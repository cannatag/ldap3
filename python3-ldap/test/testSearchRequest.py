"""
Created on 2013.05.23

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

This file is part of Python3-ldap.

Python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
from ldap3.protocol.rfc4511 import LDAPDN, AddRequest, AttributeList, Attribute, AttributeDescription, AttributeValue, \
    AssertionValue, Substrings, Initial, Any, Final, SubstringFilter, And, Or, Not, \
    Substring
from ldap3.protocol.rfc4511 import SearchRequest, ValsAtLeast1, Scope, Integer0ToMax, TypesOnly, Filter, AttributeSelection, Selector, EqualityMatch
from ldap3.connection import Connection
from ldap3.server import Server
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy


class Test(unittest.TestCase):

    def setUp(self):
        server = Server(test_server, test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, clientStrategy = test_strategy, user = test_user, password = test_password, authentication = test_authentication)

    def tearDown(self):
        self.connection.unbind()

    def testSearchEquality(self):
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

        addReq = AddRequest()
        addReq['entry'] = LDAPDN('cn=test-search-1,o=test')
        addReq['attributes'] = attributes

        self.connection.send('addRequest', addReq)

        assertion1 = EqualityMatch()
        assertion1['attributeDesc'] = AttributeDescription('cn')
        assertion1['assertionValue'] = AssertionValue('test-search-1')

        searchFilter = Filter()
        searchFilter['equalityMatch'] = assertion1

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        searchReq = SearchRequest()
        searchReq['baseObject'] = LDAPDN('o=test')
        searchReq['scope'] = Scope('singleLevel')
        searchReq['derefAliases'] = 'neverDerefAliases'
        searchReq['sizeLimit'] = Integer0ToMax(0)
        searchReq['timeLimit'] = Integer0ToMax(0)
        searchReq['typesOnly'] = TypesOnly(False)
        searchReq['filter'] = searchFilter
        searchReq['attributes'] = attributes

        self.connection.send('searchRequest', searchReq)
        self.assertTrue(True)

    def testSearchSubstring(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('tost2')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('tust2')
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

        addReq = AddRequest()
        addReq['entry'] = LDAPDN('cn=test-search-2,o=test')
        addReq['attributes'] = attributes
        self.connection.send('addRequest', addReq)

        substrings = Substrings()
        substring1 = Substring().setComponentByName('initial', Initial('test'))
        substring2 = Substring().setComponentByName('any', Any('se'))
        substring3 = Substring().setComponentByName('any', Any('ch'))
        substring4 = Substring().setComponentByName('final', Final('2'))

        substrings[0] = substring1
        substrings[1] = substring2
        substrings[2] = substring3
        substrings[3] = substring4

        substringFilter = SubstringFilter()
        substringFilter['type'] = 'cn'
        substringFilter['substrings'] = substrings
        searchFilter = Filter()
        searchFilter['substringFilter'] = substringFilter

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        searchReq = SearchRequest()
        searchReq['baseObject'] = LDAPDN('o=test')
        searchReq['scope'] = Scope('singleLevel')
        searchReq['derefAliases'] = 'neverDerefAliases'
        searchReq['sizeLimit'] = Integer0ToMax(0)
        searchReq['timeLimit'] = Integer0ToMax(0)
        searchReq['typesOnly'] = TypesOnly(False)
        searchReq['filter'] = searchFilter
        searchReq['attributes'] = attributes

        self.connection.send('searchRequest', searchReq)
        self.assertTrue(True)

    def testSearchAnd(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('tost3')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('tust3')
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

        addReq = AddRequest()
        addReq['entry'] = LDAPDN('cn=test-search-3,o=test')
        addReq['attributes'] = attributes

        self.connection.send('addRequest', addReq)

        assertion1 = EqualityMatch()
        assertion1['attributeDesc'] = AttributeDescription('cn')
        assertion1['assertionValue'] = AssertionValue('test-search-3')

        assertion2 = EqualityMatch()
        assertion2['attributeDesc'] = AttributeDescription('objectClass')
        assertion2['assertionValue'] = AssertionValue('inetOrgPerson')

        searchFilter1 = Filter()
        searchFilter1['equalityMatch'] = assertion1

        searchFilter2 = Filter()
        searchFilter2['equalityMatch'] = assertion2

        andFilter = And()
        andFilter[0] = searchFilter1
        andFilter[1] = searchFilter2

        searchFilter = Filter()
        searchFilter['and'] = andFilter

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        searchReq = SearchRequest()
        searchReq['baseObject'] = LDAPDN('o=test')
        searchReq['scope'] = Scope('singleLevel')
        searchReq['derefAliases'] = 'neverDerefAliases'
        searchReq['sizeLimit'] = Integer0ToMax(0)
        searchReq['timeLimit'] = Integer0ToMax(0)
        searchReq['typesOnly'] = TypesOnly(False)
        searchReq['filter'] = searchFilter
        searchReq['attributes'] = attributes

        self.connection.send('searchRequest', searchReq)
        self.assertTrue(True)

    def testSearchOr(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('tost4')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('tust4')
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

        addReq1 = AddRequest()
        addReq1['entry'] = LDAPDN('cn=test-search-4,o=test')
        addReq1['attributes'] = attributes

        self.connection.send('addRequest', addReq1)

        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('tost5')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('tust5')
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

        addReq2 = AddRequest()
        addReq2['entry'] = LDAPDN('cn=test-search-5,o=test')
        addReq2['attributes'] = attributes

        self.connection.send('addRequest', addReq2)

        assertion1 = EqualityMatch()
        assertion1['attributeDesc'] = AttributeDescription('cn')
        assertion1['assertionValue'] = AssertionValue('test-search-4')

        assertion2 = EqualityMatch()
        assertion2['attributeDesc'] = AttributeDescription('cn')
        assertion2['assertionValue'] = AssertionValue('test-search-5')

        searchFilter1 = Filter()
        searchFilter1['equalityMatch'] = assertion1

        searchFilter2 = Filter()
        searchFilter2['equalityMatch'] = assertion2

        orFilter = Or()
        orFilter[0] = searchFilter1
        orFilter[1] = searchFilter2

        searchFilter = Filter()
        searchFilter['or'] = orFilter

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        searchReq = SearchRequest()
        searchReq['baseObject'] = LDAPDN('o=test')
        searchReq['scope'] = Scope('singleLevel')
        searchReq['derefAliases'] = 'neverDerefAliases'
        searchReq['sizeLimit'] = Integer0ToMax(0)
        searchReq['timeLimit'] = Integer0ToMax(0)
        searchReq['typesOnly'] = TypesOnly(False)
        searchReq['filter'] = searchFilter
        searchReq['attributes'] = attributes

        self.connection.send('searchRequest', searchReq)
        self.assertTrue(True)

    def testSearchNot(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('tost6')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('tust6')
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

        addReq = AddRequest()
        addReq['entry'] = LDAPDN('cn=test-search-6,o=test')
        addReq['attributes'] = attributes

        self.connection.send('addRequest', addReq)

        assertion1 = EqualityMatch()
        assertion1['attributeDesc'] = AttributeDescription('cn')
        assertion1['assertionValue'] = AssertionValue('test-search-6')

        searchFilter = Filter()
        searchFilter['equalityMatch'] = assertion1

        notFilter = Not()
        notFilter['innerNotFilter'] = searchFilter

        attributes = AttributeSelection()
        attributes[0] = Selector('cn')
        attributes[1] = Selector('givenName')
        attributes[2] = Selector('sn')

        searchReq = SearchRequest()
        searchReq['baseObject'] = LDAPDN('o=test')
        searchReq['scope'] = Scope('singleLevel')
        searchReq['derefAliases'] = 'neverDerefAliases'
        searchReq['sizeLimit'] = Integer0ToMax(0)
        searchReq['timeLimit'] = Integer0ToMax(0)
        searchReq['typesOnly'] = TypesOnly(False)
        searchReq['filter'] = Filter().setComponentByName('notFilter', notFilter)
        searchReq['attributes'] = attributes

        self.connection.send('searchRequest', searchReq)
        self.assertTrue(True)
