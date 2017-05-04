"""
"""

# Created on 2013.06.06
#
# Author: Giovanni Cannata
#
# Copyright 2013, 2014, 2015, 2016 Giovanni Cannata
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

from ldap3 import ANONYMOUS, SASL, NTLM, DIGEST_MD5
from test.config import test_sasl_user, test_sasl_password, random_id, get_connection, drop_connection, test_sasl_realm, \
    test_server_type, test_ntlm_user, test_ntlm_password, test_secondary_user, test_secondary_password, \
    test_sasl_secondary_user, test_sasl_secondary_password, test_sasl_secondary_user_dn, test_sasl_user_dn


class Test(unittest.TestCase):
    def test_bind_clear_text_to_secondary_user(self):
        connection = get_connection()
        self.assertTrue(connection.bound)
        connection.rebind(test_secondary_user, test_secondary_password)
        if test_server_type == 'EDIR':
            bound_dn = connection.extend.novell.get_bind_dn()
        else:
            bound_dn = connection.extend.standard.who_am_i()

        if bound_dn:
            if '\\' in bound_dn:  # for Active Directory
                domain, _, name = bound_dn.replace('u:', '').partition('\\')
                self.assertTrue(domain in test_secondary_user)
                self.assertTrue(name in test_secondary_user)
            else:
                self.assertTrue(test_secondary_user in bound_dn)
        else:
            self.fail('no user dn in extended response')

        drop_connection(connection)
        self.assertFalse(connection.bound)

    def test_bind_anonymous_to_secondary_user(self):
        connection = get_connection(bind=True, lazy_connection=False, authentication=ANONYMOUS)
        self.assertTrue(connection.bound)
        connection.rebind(test_secondary_user, test_secondary_password)
        if test_server_type == 'EDIR':
            bound_dn = connection.extend.novell.get_bind_dn()
        else:
            bound_dn = connection.extend.standard.who_am_i()

        if bound_dn:
            if '\\' in bound_dn:  # for Active Directory
                domain, _, name = bound_dn.replace('u:', '').partition('\\')
                self.assertTrue(domain in test_secondary_user)
                self.assertTrue(name in test_secondary_user)
            else:
                self.assertTrue(test_secondary_user in bound_dn)
        else:
            self.fail('no user dn in extended response')

        drop_connection(connection)
        self.assertFalse(connection.bound)

    def test_bind_sasl_digest_md5_to_secondary_sasl_user(self):
        if test_server_type not in ['AD', 'SLAPD']:
            connection = get_connection(bind=False, authentication=SASL, sasl_mechanism=DIGEST_MD5, sasl_credentials=(test_sasl_realm, test_sasl_user, test_sasl_password, None))
            connection.open()
            connection.bind()
            self.assertTrue(connection.bound)
            if test_server_type == 'EDIR':
                connected_user = connection.extend.novell.get_bind_dn()
            else:
                connected_user = str(connection.extend.standard.who_am_i())
            self.assertEqual(connected_user, test_sasl_user_dn)

            if connection.rebind(authentication=SASL, sasl_mechanism=DIGEST_MD5, sasl_credentials=(test_sasl_realm, test_sasl_secondary_user, test_sasl_secondary_password, None)):
                if test_server_type == 'EDIR':
                    connected_user = connection.extend.novell.get_bind_dn()
                else:
                    connected_user = connection.extend.standard.who_am_i()

                self.assertEqual(connected_user, test_sasl_secondary_user_dn)
            else:
                self.fail('secondary user sasl authentication failed')

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
