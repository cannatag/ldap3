# """
# Created on 2014.05.10
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

from ldap3 import Server, Connection, ServerPool
from ldap3.core.exceptions import LDAPException, LDAPOperationsErrorResult, LDAPOperationResult, LDAPNoSuchObjectResult
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_server_mode,\
    test_lazy_connection, test_get_info, test_check_names, test_pooling_strategy, test_pooling_active, test_pooling_exhaust, \
    test_name_attr


class Test(unittest.TestCase):
    def test_main_class_exception(self):
        e = LDAPException()
        self.assertTrue(isinstance(e, LDAPException))

    def test_subclassing_exception(self):
        e = LDAPOperationResult(1)
        self.assertTrue(isinstance(e, LDAPOperationsErrorResult))
