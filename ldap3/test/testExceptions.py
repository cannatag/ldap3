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
    test_lazy_connection, test_get_info, test_check_names, test_pooling_strategy, test_pooling_active, test_pooling_exhaust


class Test(unittest.TestCase):
    def test_main_class_exception(self):
        e = LDAPException()
        self.assertTrue(isinstance(e, LDAPException))

    def test_subclassing_exception(self):
        e = LDAPOperationResult(1)
        self.assertTrue(isinstance(e, LDAPOperationsErrorResult))

    def test_raise_exceptions(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode)
        connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1', check_names=test_check_names, raise_exceptions=True)
        ok = False
        try:
            result = connection.search('xxx=xxx', '(cn=*)')
            if not connection.strategy.sync:
                connection.get_response(result)
        except LDAPNoSuchObjectResult:
            ok = True

        self.assertTrue(ok)
