# Created on 2013.05.23
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

from ldap3 import AUTH_SIMPLE, STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, STRATEGY_SYNC_RESTARTABLE, STRATEGY_REUSABLE_THREADED,\
    POOLING_STRATEGY_ROUND_ROBIN, GET_ALL_INFO, IP_V4_PREFERRED, IP_SYSTEM_DEFAULT, IP_V6_PREFERRED, IP_V4_ONLY, IP_V6_ONLY

test_server = ['edir1', 'edir2', 'edir3']  # the ldap server where tests executed, if a list is given a pool will be created
test_server = 'edir1'
# test_server = 'sl10'
# test_server_mode = IP_SYSTEM_DEFAULT
test_server_mode = IP_V6_PREFERRED
test_user = 'cn=admin,o=services'  # the user that performs the tests
test_password = 'password'  # user password
test_server_context = 'o=services'  # used in novell eDirectory extended operations

test_base = 'o=test'  # base context where test objects are created
test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
test_name_attr = 'cn'  # naming attribute for test objects

test_pooling_strategy = POOLING_STRATEGY_ROUND_ROBIN
test_pooling_active = True
test_pooling_exhaust = False

test_port = 389  # ldap port
test_port_ssl = 636  # ldap secure port
test_authentication = AUTH_SIMPLE  # authentication type
test_check_names = True  # check attribute names in operations
test_get_info = GET_ALL_INFO  # get info from DSA
test_lazy_connection = False  # connection lazy
test_strategy = STRATEGY_SYNC  # strategy for executing tests
test_strategy = STRATEGY_ASYNC_THREADED  # uncomment this line to test the async strategy
test_strategy = STRATEGY_SYNC_RESTARTABLE  # uncomment this line to test the sync_restartable strategy
test_strategy = STRATEGY_REUSABLE_THREADED  # uncomment this line to test the sync_reusable_threaded strategy


def dn_for_test(base, name):
    return test_name_attr + '=' + name + ',' + base
