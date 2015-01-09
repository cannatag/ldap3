# Created on 2013.06.06
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

from ldap3 import ANONYMOUS, SASL
from test import test_sasl_user, test_sasl_password, random_id, get_connection, drop_connection, test_sasl_realm

testcase_id = random_id()


class Test(unittest.TestCase):
    def test_bind_clear_text(self):
        connection = get_connection(bind=False)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        drop_connection(connection)
        self.assertFalse(connection.bound)

    def test_bind_anonymous(self):
        connection = get_connection(bind=False, lazy_connection=False, authentication=ANONYMOUS)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        drop_connection(connection)
        self.assertFalse(connection.bound)

    def test_bind_sasl_digest_md5(self):
        connection = get_connection(bind=False, authentication=SASL, sasl_mechanism='DIGEST-MD5', sasl_credentials=(test_sasl_realm, test_sasl_user, test_sasl_password, None))
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        drop_connection(connection)
        self.assertFalse(connection.bound)
