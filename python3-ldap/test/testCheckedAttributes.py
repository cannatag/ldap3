# """
# Created on 2014.07.14
#
# @author: Giovanni Cannata
#
# Copyright 2013 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

import unittest

from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base,\
    dn_for_test, test_name_attr, test_lazy_connection, test_get_info, test_pooling_strategy, test_pooling_active,\
    test_pooling_exhaust, test_server_mode
from ldap3 import Server, Connection, ServerPool, SEARCH_SCOPE_WHOLE_SUBTREE, STRATEGY_REUSABLE_THREADED


class Test(unittest.TestCase):
    def setUp(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1', check_names=True)
        result = self.connection.add(dn_for_test(test_base, 'test-checked-attributes'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-checked-attributes', 'loginGraceLimit': 10})
        if not self.connection.strategy.sync:
            self.connection.get_response(result)

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_search_checked_attributes(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=test-checked-attributes)', attributes=[test_name_attr, 'sn', 'jpegPhoto', 'loginGraceLimit'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['attributes']['sn'][0], 'test-checked-attributes')
        self.assertEqual(response[0]['attributes']['loginGraceLimit'], 10)
        if str != bytes:  # python3
            self.assertTrue(isinstance(response[0]['attributes']['sn'][0], str))
        else:  # python2
            self.assertTrue(isinstance(response[0]['attributes']['sn'][0], unicode))
        self.assertTrue(isinstance(response[0]['attributes']['loginGraceLimit'], int))

    def test_custom_formatter(self):
        def to_upper(byte_value):
            if str != bytes:
                return str(byte_value, encoding='UTF-8').upper()
            else:
                return unicode(byte_value, encoding='UTF-8').upper()
        if str != bytes:  # python3
            formatter = {'cn': to_upper,  # name to upper
                         '2.5.4.4': lambda v: str(v, encoding='UTF-8')[::-1],  # sn reversed
                         '1.3.6.1.4.1.1466.115.121.1.27': lambda v: int(v) + 1000  # integer syntax incremented by 1000
            }
        else:
            formatter = {'cn': to_upper,  # name to upper
                         '2.5.4.4': lambda v: unicode(v, encoding='UTF-8')[::-1],  # sn reversed
                         '1.3.6.1.4.1.1466.115.121.1.27': lambda v: int(v) + 1000  # integer syntax incremented by 1000
            }
        self.connection.server.custom_formatter = formatter
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=test-checked-attributes)', attributes=[test_name_attr, 'sn', 'jpegPhoto', 'loginGraceLimit'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['attributes']['cn'][0], 'TEST-CHECKED-ATTRIBUTES')
        self.assertEqual(response[0]['attributes']['sn'][0], 'setubirtta-dekcehc-tset')
        self.assertEqual(response[0]['attributes']['loginGraceLimit'], 1010)