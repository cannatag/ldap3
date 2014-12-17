# Created on 2013.08.11
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

import unittest
import ssl

from ldap3 import Server, Connection, ServerPool, Tls, AUTH_SASL, STRATEGY_REUSABLE_THREADED
from test import test_server, test_port, test_port_ssl, test_user, test_password, test_authentication, \
    test_strategy, test_base, test_lazy_connection, test_get_info, test_server_mode, \
    test_pooling_strategy, test_pooling_active, test_pooling_exhaust


class Test(unittest.TestCase):
    def test_start_tls(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, tls=Tls(validate=ssl.CERT_NONE), get_info=test_get_info, mode=test_server_mode)
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')
        connection.open()
        connection.start_tls()
        self.assertFalse(connection.closed)
        connection.unbind()
        if connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            connection.strategy.terminate()

    def test_open_ssl_with_defaults(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port_ssl, use_ssl=True)
        connection = Connection(server, user=test_user, password=test_password)
        connection.open()
        self.assertFalse(connection.closed)
        connection.unbind()
        if connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            connection.strategy.terminate()

    def test_search_with_tls_before_bind(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, tls=Tls())
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')
        connection.open()
        connection.start_tls()
        connection.bind()
        result = connection.search(test_base, '(objectClass=*)', attributes='sn')
        if not connection.strategy.sync:
            response, result = connection.get_response(result)
        else:
            response = connection.response
            result = connection.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(len(response) > 15)
        connection.unbind()
        if connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            connection.strategy.terminate()
        self.assertFalse(connection.bound)

    def test_search_with_tls_after_bind(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, tls=Tls())
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')
        connection.open()
        connection.bind()
        connection.start_tls()
        result = connection.search(test_base, '(objectClass=*)', attributes='sn')
        if not connection.strategy.sync:
            response, result = connection.get_response(result)
        else:
            response = connection.response
            result = connection.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(len(response) > 15)
        connection.unbind()
        if connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            connection.strategy.terminate()
        self.assertFalse(connection.bound)

    def test_bind_ssl_with_certificate(self):
        tls = Tls(local_private_key_file='admin-key.pem', local_certificate_file='admin-cert.pem', validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file='ca-cert.pem', valid_names=['EDIR-TEST', 'edir1.hyperv', 'edir1'])
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port_ssl, use_ssl=True, tls=tls)
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication)
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        connection.unbind()
        if connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            connection.strategy.terminate()
        self.assertFalse(connection.bound)

    def test_sasl_with_external_certificate(self):
        tls = Tls(local_private_key_file='admin-key.pem', local_certificate_file='admin-cert.pem', validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file='ca-cert.pem', valid_names=['EDIR-TEST', 'edir1.hyperv', 'edir2.hyperv', 'edir3.hyperv', 'edir1', 'edir2', 'edir3'])
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port_ssl, use_ssl=True, tls=tls)
        connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, authentication=AUTH_SASL, sasl_mechanism='EXTERNAL')
        connection.open()
        connection.bind()
        self.assertTrue(connection.bound)
        connection.unbind()
        if connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            connection.strategy.terminate()
        self.assertFalse(connection.bound)
