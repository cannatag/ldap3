"""
Created on 2014.02.02

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

from ldap3.server import Server
from ldap3.connection import Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True))
        self.connection = Connection(server, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testOpenConnection(self):
        self.connection.open()
        self.assertEquals(self.connection.closed, False)
        self.connection.unbind()
        self.assertEquals(self.connection.closed, True)
        self.assertEquals(self.connection.bound, False)

    def testBindConnection(self):
        self.connection.open()
        self.assertEquals(self.connection.closed, False)
        self.connection.bind()
        self.assertEquals(self.connection.bound, True)
        self.connection.unbind()
        self.assertEquals(self.connection.closed, True)
        self.assertEquals(self.connection.bound, False)

    def testConnectionInContext(self):
        with self.connection:
            self.assertEquals(self.connection.closed, False)
            self.assertEquals(self.connection.bound, True)

        self.assertEquals(self.connection.closed, True)
        self.assertEquals(self.connection.bound, False)

    def testConnectionInContextWithAs(self):
        with self.connection as c:
            self.assertEquals(c.closed, False)
            self.assertEquals(c.bound, True)

        self.assertEquals(self.connection.closed, True)
        self.assertEquals(self.connection.bound, False)
