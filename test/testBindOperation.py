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

from ldap3 import ANONYMOUS, SASL, NTLM, Server, Connection, EXTERNAL, DIGEST_MD5, MOCK_SYNC, MOCK_ASYNC
from ldap3.core.exceptions import LDAPSocketOpenError
from test.config import test_sasl_user, test_sasl_password, random_id, get_connection, drop_connection, test_sasl_realm, test_server_type, \
    test_ntlm_user, test_ntlm_password, test_sasl_user_dn, test_strategy


class Test(unittest.TestCase):
    def test_bind_cleartext(self):
        connection = get_connection(bind=False)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        drop_connection(connection)
        self.assertFalse(connection.bound)

    def test_bind_ssl_cert_none(self):
        connection = get_connection(bind=False, use_ssl=True)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        drop_connection(connection)
        self.assertFalse(connection.bound)

    def test_bind_anonymous(self):
        connection = get_connection(bind=True, lazy_connection=False, authentication=ANONYMOUS)
        self.assertTrue(connection.bound)
        drop_connection(connection)
        self.assertFalse(connection.bound)

    def test_bind_sasl_digest_md5(self):
        if test_server_type not in ['AD', 'SLAPD'] and test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
            connection = get_connection(bind=False, authentication=SASL, sasl_mechanism=DIGEST_MD5, sasl_credentials=(test_sasl_realm, test_sasl_user, test_sasl_password, None))
            connection.open()
            connection.bind()
            self.assertTrue(connection.bound)
            if not connection.strategy.pooled:
                if test_server_type == 'EDIR':
                    connected_user = connection.extend.novell.get_bind_dn()
                else:
                    connected_user = str(connection.extend.standard.who_am_i())
                self.assertEqual(connected_user, test_sasl_user_dn)
            drop_connection(connection)
            self.assertFalse(connection.bound)

    def test_ntlm(self):
        if test_server_type == 'AD':
            connection = get_connection(bind=False, authentication=NTLM, ntlm_credentials=(test_ntlm_user, test_ntlm_password))
            connection.open()
            connection.bind()
            self.assertTrue(connection.bound)
            connected_user = str(connection.extend.standard.who_am_i())[2:]
            self.assertEqual(connected_user, test_ntlm_user)
            drop_connection(connection)
            self.assertFalse(connection.bound)

    def test_ldapi(self):
        if test_server_type == 'SLAPD':
            try:
                server = Server('ldapi:///var/run/slapd/ldapi')
                connection = Connection(server, authentication=SASL, sasl_mechanism=EXTERNAL, sasl_credentials=('',))
                connection.open()
                connection.bind()
                self.assertTrue(connection.bound)
            except LDAPSocketOpenError:
                return

            self.assertTrue(False)

    def test_ldapi_encoded_url(self):
        if test_server_type == 'SLAPD':
            try:
                server = Server('ldapi://%2Fvar%2Frun%2Fslapd%2Fldapi')
                connection = Connection(server, authentication=SASL, sasl_mechanism=EXTERNAL, sasl_credentials=('',))
                connection.open()
                connection.bind()
                self.assertTrue(connection.bound)
            except LDAPSocketOpenError:
                return

            self.assertTrue(False)
