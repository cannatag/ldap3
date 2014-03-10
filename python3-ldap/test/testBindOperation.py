"""
Created on 2013.06.06

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

from ldap3.connection import Connection
from ldap3.server import Server
from ldap3 import AUTH_ANONYMOUS, AUTH_SASL
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_port_ssl


class Test(unittest.TestCase):
    def testBindClearText(self):
        server = Server(host=test_server, port=test_port)
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        connection.unbind()
        self.assertFalse(connection.bound)

    def testBindSsl(self):
        server = Server(host=test_server, port=test_port_ssl, use_ssl=True)
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        connection.unbind()
        self.assertFalse(connection.bound)

    def testBindAnonymous(self):
        server = Server(host=test_server, port=test_port)
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, authentication=AUTH_ANONYMOUS)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        connection.unbind()
        self.assertFalse(connection.bound)

    def testBindSaslDigestMd5(self):
        server = Server(host=test_server, port=test_port)
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, authentication=AUTH_SASL, sasl_mechanism='DIGEST-MD5', sasl_credentials=(None, 'testSasl.risorse', 'password', None))
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        connection.unbind()
        self.assertFalse(connection.bound)
