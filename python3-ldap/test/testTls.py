"""
Created on 2013.08.11

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
import ssl

from ldap3 import Server, Connection, Tls, AUTH_SASL
from test import test_server, test_port, test_port_ssl, test_user, test_password, test_authentication, test_strategy, test_base


class Test(unittest.TestCase):
    def testStartTls(self):
        server = Server(host = test_server, port = test_port, tls = Tls())
        connection = Connection(server, autoBind = False, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                authentication = test_authentication)
        connection.open()
        connection.startTls()
        self.assertFalse(connection.closed)
        connection.unbind()

    def testSearchWithTlsBeforeBind(self):
        server = Server(host = test_server, port = test_port, tls = Tls())
        connection = Connection(server, autoBind = False, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                authentication = test_authentication)
        connection.open()
        connection.startTls()
        connection.bind()
        result = connection.search(test_base, '(objectClass=*)', attributes = 'sn')
        if not isinstance(result, bool):
            connection.getResponse(result)
        self.assertEqual(connection.result['description'], 'success')
        self.assertGreater(len(connection.response), 15)
        connection.unbind()

    def testSearchWithTlsAfterBind(self):
        server = Server(host = test_server, port = test_port, tls = Tls())
        connection = Connection(server, autoBind = False, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                authentication = test_authentication)
        connection.open()
        connection.bind()
        connection.startTls()
        result = connection.search(test_base, '(objectClass=*)', attributes = 'sn')
        if not isinstance(result, bool):
            connection.getResponse(result)
        self.assertEqual(connection.result['description'], 'success')
        self.assertGreater(len(connection.response), 15)

    def testBindSslWithCertificate(self):
        tls = Tls(localPrivateKeyFile = 'c:/admin2524KeyPlain.pem', localCertificateFile = 'c:/admin2524Cert.pem', validate = ssl.CERT_REQUIRED,
                  version = ssl.PROTOCOL_TLSv1, caCertsFile = 'c:/idmprofiler2524CA.b64')
        server = Server(host = test_server, port = test_port_ssl, useSsl = True, tls = tls)
        connection = Connection(server, autoBind = False, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                authentication = test_authentication)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        connection.unbind()
        self.assertFalse(connection.bound)

    def testSaslWithExternalCertificate(self):
        tls = Tls(localPrivateKeyFile = 'c:/admin2524KeyPlain.pem', localCertificateFile = 'c:/admin2524Cert.pem', validate = ssl.CERT_REQUIRED,
                  version = ssl.PROTOCOL_TLSv1, caCertsFile = 'c:/idmprofiler2524CA.b64')
        server = Server(host = test_server, port = test_port_ssl, useSsl = True, tls = tls)
        connection = Connection(server, autoBind = False, version = 3, clientStrategy = test_strategy, authentication = AUTH_SASL, saslMechanism = 'EXTERNAL')
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        connection.unbind()
        self.assertFalse(connection.bound)

    #===============================================================================
    # removal os TLS layer is defined as MAY in rfc4511. It can't be implemented againsta a generic LDAP server
    #     def testStopTls(self):
    #         server = Server(host = test_server, port = test_port, tls = Tls())
    #         connection = Connection(server, autoBind = False, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password, authentication = test_authentication)
    #         connection.open()
    #         connection.startTls()
    #         self.assertFalse(connection.closed)
    #         connection.stopTls()
    #         connection.unbind()
    #===============================================================================

    #===========================================================================
    # def testSaslWithDigestMD5(self):
    #     # tls = Tls(localPrivateKeyFile = 'c:/admin2524KeyPlain.pem', localCertificateFile = 'c:/admin2524Cert.pem', validate = ssl.CERT_REQUIRED, version = ssl.PROTOCOL_TLSv1, caCertsFile = 'c:/idmprofiler2524CA.b64')
    #     server = Server(host = test_server, port = test_port_ssl, useSsl = True, tls = Tls())
    #     connection = Connection(server, autoBind = False, version = 3, clientStrategy = test_strategy, authentication = AUTH_SASL, user = test_user, saslMechanism = 'DIGEST-MD5', saslCredentials = test_password)
    #     connection.open()
    #     connection.bind()
    #     self.assertTrue(connection.bound)
    #     connection.unbind()
    #     self.assertFalse(connection.bound)
    #===========================================================================
