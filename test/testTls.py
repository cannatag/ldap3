# Created on 2013.08.11
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
import ssl

from ldap3 import Server, Connection, ServerPool, Tls, SASL, EXTERNAL, MOCK_ASYNC, MOCK_SYNC
from test import test_server, test_port, test_port_ssl, test_user, test_password, test_authentication, \
    test_strategy, test_lazy_connection, test_get_info, test_server_mode, test_valid_names, \
    test_pooling_strategy, test_pooling_active, test_pooling_exhaust, test_ca_cert_file, test_user_cert_file, test_user_key_file


class Test(unittest.TestCase):
    def test_start_tls(self):
        if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
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
            if connection.strategy.pooled:
                connection.strategy.terminate()

    def test_open_ssl_with_defaults(self):
        if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
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
            if connection.strategy.pooled:
                connection.strategy.terminate()

    def test_open_with_tls_before_bind(self):
        if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
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
            self.assertTrue(connection.bound)
            connection.unbind()
            if connection.strategy.pooled:
                connection.strategy.terminate()
            self.assertFalse(connection.bound)

    def test_open_with_tls_after_bind(self):
        if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
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
            self.assertTrue(connection.bound)
            connection.unbind()
            if connection.strategy.pooled:
                connection.strategy.terminate()
            self.assertFalse(connection.bound)

    def test_bind_ssl_with_certificate(self):
        if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
            tls = Tls(local_private_key_file=test_user_key_file,
                      local_certificate_file=test_user_cert_file,
                      validate=ssl.CERT_REQUIRED,
                      version=ssl.PROTOCOL_TLSv1,
                      ca_certs_file=test_ca_cert_file,
                      valid_names=test_valid_names)
            if isinstance(test_server, (list, tuple)):
                server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
                for host in test_server:
                    server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
            else:
                server = Server(host=test_server, port=test_port_ssl, use_ssl=True, tls=tls)
            connection = Connection(server, auto_bind=False, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication)
            connection.open()
            connection.bind()
            self.assertTrue(connection.bound)
            connection.unbind()
            if connection.strategy.pooled:
                connection.strategy.terminate()
            self.assertFalse(connection.bound)

    def test_sasl_with_external_certificate(self):
        if test_strategy not in [MOCK_SYNC, MOCK_ASYNC]:
            tls = Tls(local_private_key_file=test_user_key_file, local_certificate_file=test_user_cert_file, validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file=test_ca_cert_file, valid_names=test_valid_names)
            if isinstance(test_server, (list, tuple)):
                server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
                for host in test_server:
                    server.add(Server(host=host, port=test_port_ssl, use_ssl=True, tls=tls, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
            else:
                server = Server(host=test_server, port=test_port_ssl, use_ssl=True, tls=tls)
            connection = Connection(server, auto_bind=False, version=3, client_strategy=test_strategy, authentication=SASL, sasl_mechanism=EXTERNAL)
            connection.open()
            connection.bind()
            self.assertTrue(connection.bound)
            connection.unbind()
            if connection.strategy.pooled:
                connection.strategy.terminate()
            self.assertFalse(connection.bound)
