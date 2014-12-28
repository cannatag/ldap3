# Created on 2013.05.23
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of pureLDAP.
#
# pureLDAP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pureLDAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pureLDAP in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from ldap3 import AUTH_SIMPLE, STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, STRATEGY_SYNC_RESTARTABLE,\
    STRATEGY_REUSABLE_THREADED, POOLING_STRATEGY_ROUND_ROBIN, GET_ALL_INFO, IP_V4_PREFERRED, \
    IP_SYSTEM_DEFAULT, IP_V6_PREFERRED, IP_V4_ONLY, IP_V6_ONLY, GET_NO_INFO, GET_DSA_INFO
from sys import version

# test_server = ['server1', 'server2', 'server3']  # the ldap server where tests are executed, if a list is given a pool will be created

"""
# test in the cloud
test_server = 'labldap02.cloudapp.net'
test_server_context = 'o=resources'  # used in novell eDirectory extended operations
test_server_edir_name = 'SLES1'  # used in novell eDirectory extended operations
test_user = 'cn=testLAB,o=resources'  # the user that performs the tests
test_password = 'Rc1234pfop'  # user password
test_sasl_user = 'testLAB.resources'
test_sasl_password = 'Rc1234pfop'
test_ca_cert_file = 'ca-edir-lab.pem'
test_user_cert_file = 'testlab-cert.pem'
test_user_key_file = 'testlab-key.pem'
"""

# test elitebook
# test_server = 'edir1.hyperv'
test_server = ['edir1', 'edir2', 'edir3']  # the ldap server where tests are executed, if a list is given a pool will be created
test_server = 'edir1.hyperv'
test_server_context = 'o=services'  # used in novell eDirectory extended operations
test_server_edir_name = 'edir1'  # used in novell eDirectory extended operations
test_user = 'cn=admin,o=services'  # the user that performs the tests
test_password = 'password'  # user password
test_sasl_user = 'testsasl.test'
test_sasl_password = 'password'
test_ca_cert_file = 'ca-cert.pem'
test_user_cert_file = 'admin-cert.pem'
test_user_key_file = 'admin-key.pem'

"""
# test camera
test_server = 'sl10'
test_server_context = 'o=services'  # used in novell eDirectory extended operations
test_server_edir_name = 'sl10'  # used in novell eDirectory extended operations
test_user = 'cn=admin,o=services'  # the user that performs the tests
test_password = 'camera'  # user password
test_sasl_user = 'testsasl.services'
test_sasl_password = 'password'
test_ca_cert_file = 'ca-cert.pem'
test_user_cert_file = 'admin-cert.pem'
test_user_key_file = 'admin-key.pem'
"""

# test_server_mode = IP_SYSTEM_DEFAULT
test_server_mode = IP_V6_PREFERRED
test_base = 'o=test'  # base context where test objects are created
test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
test_name_attr = 'cn'  # naming attribute for test objects

test_pooling_strategy = POOLING_STRATEGY_ROUND_ROBIN
test_pooling_active = True
test_pooling_exhaust = False

test_port = 389  # ldap port
test_port_ssl = 636  # ldap secure port
test_authentication = AUTH_SIMPLE  # authentication type
test_check_names = False  # check attribute names in operations
test_get_info = GET_ALL_INFO  # get info from DSA
test_lazy_connection = False  # connection lazy
test_strategy = STRATEGY_SYNC  # sync strategy for executing tests
# test_strategy = STRATEGY_ASYNC_THREADED  # uncomment this line to test the async strategy
# test_strategy = STRATEGY_SYNC_RESTARTABLE  # uncomment this line to test the sync_restartable strategy
# test_strategy = STRATEGY_REUSABLE_THREADED  # uncomment this line to test the sync_reusable_threaded strategy

print('Strategy:', test_strategy, '- Lazy:', test_lazy_connection, '- Check names:' , test_check_names, '- Version:', version)


def dn_for_test(base, name):
    return test_name_attr + '=' + name + ',' + base
