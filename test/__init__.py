# Created on 2013.05.23
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
from time import sleep
from sys import version
from os import environ
from random import SystemRandom

from ldap3 import SIMPLE, SYNC, ROUND_ROBIN, IP_V6_PREFERRED, Server, Connection, ServerPool, SASL, \
    NONE, ASYNC, REUSABLE, RESTARTABLE, NTLM, AUTO_BIND_TLS_BEFORE_BIND


# test_server = ['server1', 'server2', 'server3']  # the ldap server where tests are executed, if a list is given a pool will be created

# test_server_mode = IP_SYSTEM_DEFAULT
test_server_mode = IP_V6_PREFERRED

test_pooling_strategy = ROUND_ROBIN
test_pooling_active = True
test_pooling_exhaust = False

test_port = 389  # ldap port
test_port_ssl = 636  # ldap secure port
test_authentication = SIMPLE  # authentication type
test_check_names = False  # check attribute names in operations
test_get_info = NONE  # get info from DSA


try:
    location = environ['USERDOMAIN']
except KeyError:
    location = 'UNKNOWN'

if location.startswith('TRAVIS'):
    # test in the cloud
    test_server = 'labldap02.cloudapp.net'
    test_server_context = 'o=resources'  # used in novell eDirectory extended operations
    test_server_edir_name = 'SLES1'  # used in novell eDirectory extended operations
    test_server_type = 'EDIR'
    test_base = 'o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'loginGraceLimit'
    test_user = 'cn=testLAB,o=resources'  # the user that performs the tests
    test_password = 'Rc1234pfop'  # user password
    test_sasl_user = 'testLAB.resources'
    test_sasl_password = 'Rc1234pfop'
    test_sasl_realm = None
    test_ca_cert_file = 'test/lab-edir-ca-cert.pem'
    test_user_cert_file = 'test/lab-edir-testlab-cert.pem'
    test_user_key_file = 'test/lab-edir-testlab-key.pem'
    test_ntlm_user = 'xxx\\yyy'
    test_ntlm_password = 'zzz'
elif location == 'GCNBHPW8-EDIR':
    # test elitebook - eDirectory (EDIR)
    # test_server = 'edir1.hyperv'
    test_server = ['edir1',
                   'edir2',
                   'edir3']  # the ldap server where tests are executed, if a list is given a pool will be created
    test_server = 'edir1.hyperv'
    test_server_type = 'EDIR'
    test_base = 'o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'loginGraceLimit'
    test_server_context = 'o=services'  # used in novell eDirectory extended operations
    test_server_edir_name = 'edir1'  # used in novell eDirectory extended operations
    test_user = 'cn=admin,o=services'  # the user that performs the tests
    test_password = 'password'  # user password
    test_sasl_user = 'testSASL.resources'
    test_sasl_password = 'password'
    test_sasl_realm = None
    test_ca_cert_file = 'local-edir-ca-cert.pem'
    test_user_cert_file = 'local-edir-admin-cert.pem'
    test_user_key_file = 'local-edir-admin-key.pem'
    test_ntlm_user = 'xxx\\yyy'
    test_ntlm_password = 'zzz'
elif location == 'GCNBHPW8':
    # test elitebook - Active Directory (AD)
    # test_server = ['win1',
    #                'win2']
    test_server = 'win1.hyperv'
    test_server_type = 'AD'
    test_base = 'OU=test,DC=FOREST,DC=LAB'  # base context where test objects are created
    test_moved = 'ou=moved,OU=test,DC=FOREST,DC=LAB'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'logonCount'
    test_server_context = ''  # used in novell eDirectory extended operations
    test_server_edir_name = ''  # used in novell eDirectory extended operations
    test_user = 'CN=Administrator,CN=Users,DC=FOREST,DC=LAB'  # the user that performs the tests
    test_password = 'Rc1234pfop'  # user password
    test_sasl_user = 'CN=testLAB,CN=Users,DC=FOREST,DC=LAB'
    test_sasl_password = 'Rc1234pfop'
    test_sasl_realm = None
    test_ca_cert_file = 'local-forest-lab-ca.pem'
    test_user_cert_file = ''  # 'local-forest-lab-administrator-cert.pem'
    test_user_key_file = ''  # 'local-forest-lab-administrator-key.pem'
    test_ntlm_user = 'FOREST\\Administrator'
    test_ntlm_password = 'Rc1234pfop'
elif location == 'GCNBHPW8-SLAPD':
    # test elitebook - OpenLDAP (SLAPD)
    # test_server = 'edir1.hyperv'
    test_server = 'openldap.hyperv'
    test_server_type = 'SLAPD'
    test_base = 'o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'gidNumber'
    test_server_context = ''  # used in novell eDirectory extended operations
    test_server_edir_name = ''  # used in novell eDirectory extended operations
    test_user = 'cn=admin,o=test'  # the user that performs the tests
    test_password = 'password'  # user password
    test_sasl_user = 'cn=testSASL,o=test'
    test_sasl_password = 'password'
    test_sasl_realm = 'openldap.hyperv'
    test_ca_cert_file = 'local-openldap-ca-cert.pem'
    test_user_cert_file = ''
    test_user_key_file = ''
    test_ntlm_user = 'xxx\\yyy'
    test_ntlm_password = 'zzz'
elif location == 'GCW89227':
    # test camera
    # test_server = ['sl08',
    #               'sl09',
    #               'sl10']  # the ldap server where tests are executed, if a list is given a pool will be created
    # test_server = 'sl10'
    # test_server_type = 'EDIR'
    test_server = 'nova01.amm.intra.camera.it'
    test_server_type = 'AD'
    test_base = 'o=test'  # base context where test objects are created
    test_moved = 'ou=moved,o=test'  # base context where objects are moved in ModifyDN operations
    test_name_attr = 'cn'  # naming attribute for test objects
    test_int_attr = 'loginGraceLimit'
    test_server_context = 'o=risorse'  # used in novell eDirectory extended operations
    test_server_edir_name = 'sl10'  # used in novell eDirectory extended operations
    test_user = 'cn=admin,o=services'  # the user that performs the tests
    test_password = 'camera'  # user password
    test_sasl_user = 'testSASL.services'
    test_sasl_password = 'password'
    test_sasl_realm = None
    test_ca_cert_file = 'local-edir-.pem'
    test_user_cert_file = 'admin-cert.pem'
    test_user_key_file = 'admin-key.pem'
    test_ntlm_user = 'AMM\\Administrator'
    test_ntlm_password = 'xxx'
else:
    raise Exception('testing location ' + location + ' is not valid')

if location.startswith('TRAVIS,'):
    _, strategy, lazy = location.split(',')
    test_strategy = strategy
    test_lazy_connection = bool(int(lazy))
else:
    test_strategy = SYNC  # sync strategy for executing tests
    # test_strategy = ASYNC  # uncomment this line to test the async strategy
    # test_strategy = RESTARTABLE  # uncomment this line to test the sync_restartable strategy
    # test_strategy = REUSABLE  # uncomment this line to test the sync_reusable_threaded strategy
    test_lazy_connection = False  # connection lazy

print('Testing location:', location)
print('Test server:', test_server)
print('Python version:', version)
print('Strategy:', test_strategy, '- Lazy:', test_lazy_connection, '- Check names:', test_check_names)


def random_id():
    return '[' + str(SystemRandom().random())[-8:] + ']'


def generate_dn(base, batch_id, name):
    return test_name_attr + '=' + batch_id + name + ',' + base


def get_connection(bind=None,
                   check_names=None,
                   lazy_connection=None,
                   authentication=None,
                   sasl_mechanism=None,
                   sasl_credentials=None,
                   ntlm_credentials=None,
                   get_info=None):
    if bind is None:
        if test_server_type == 'AD':
            bind = AUTO_BIND_TLS_BEFORE_BIND
        else:
            bind = True
    if check_names is None:
        check_names = test_check_names
    if lazy_connection is None:
        lazy_connection = test_lazy_connection
    if authentication is None:
        authentication = test_authentication
    if get_info is None:
        get_info = test_get_info

    if isinstance(test_server, (list, tuple)):
        server = ServerPool(pool_strategy=test_pooling_strategy,
                            active=test_pooling_active,
                            exhaust=test_pooling_exhaust)
        for host in test_server:
            server.add(Server(host=host,
                              port=test_port,
                              allowed_referral_hosts=('*', True),
                              get_info=get_info,
                              mode=test_server_mode))
    else:
        server = Server(host=test_server,
                        port=test_port,
                        allowed_referral_hosts=('*', True),
                        get_info=get_info,
                        mode=test_server_mode)

    if authentication == SASL:
        return Connection(server,
                          auto_bind=bind,
                          version=3,
                          client_strategy=test_strategy,
                          authentication=SASL,
                          sasl_mechanism=sasl_mechanism,
                          sasl_credentials=sasl_credentials,
                          lazy=lazy_connection,
                          pool_name='pool1',
                          check_names=check_names)
    elif authentication == NTLM:
        return Connection(server,
                          auto_bind=bind,
                          version=3,
                          client_strategy=test_strategy,
                          user=ntlm_credentials[0],
                          password=ntlm_credentials[1],
                          authentication=NTLM,
                          lazy=lazy_connection,
                          pool_name='pool1',
                          check_names=check_names)
    else:
        return Connection(server,
                          auto_bind=bind,
                          version=3,
                          client_strategy=test_strategy,
                          user=test_user,
                          password=test_password,
                          authentication=authentication,
                          lazy=lazy_connection,
                          pool_name='pool1',
                          check_names=check_names)


def drop_connection(connection, dn_to_delete=None):
    if dn_to_delete:
        for dn in dn_to_delete:
            done = False
            counter = 30
            while not done:  # wait at maximum for 120 seconds
                operation_result = connection.delete(dn[0])
                result = get_operation_result(connection, operation_result)
                if result['description'] == 'success':
                    done = True
                elif result['description'] == 'busy':
                    counter -= 1
                    if counter >= 0:
                        sleep(4)  # wait and retry
                    else:
                        print('unable to delete object ' + dn[0] + ': ' + str(result))
                        done = True
                else:
                    print('unable to delete object ' + dn[0] + ': ' + str(result))
                    break
    connection.unbind()
    if connection.strategy.pooled:
        connection.strategy.terminate()


def get_operation_result(connection, operation_result):
    if not connection.strategy.sync:
        _, result = connection.get_response(operation_result)
    else:
        result = connection.result

    return result


def add_user(connection, batch_id, username, attributes=None):
    if attributes is None:
        attributes = dict()

    if test_server_type == 'EDIR':
        attributes.update({'objectClass': 'iNetOrgPerson', 'sn': username})
    elif test_server_type == 'AD':
        attributes.update({'objectClass': 'iNetOrgPerson', 'sn': username, 'unicodePwd': '"Rc1234abcd"'.encode('utf-16-le'), 'userAccountControl': 512})
    elif test_server_type == 'SLAPD':
        attributes.update({'objectClass': ['iNetOrgPerson', 'posixGroup', 'top'], 'sn': username, 'gidNumber': 0})
    else:
        attributes.update({'objectClass': 'iNetOrgPerson', 'sn': username})
    dn = generate_dn(test_base, batch_id, username)
    operation_result = connection.add(dn, 'iNetOrgPerson', attributes)
    result = get_operation_result(connection, operation_result)
    if not result['description'] == 'success':
        raise Exception('unable to create user ' + username + ': ' + str(result))

    return dn, result


def add_group(connection, batch_id, groupname, members=None):
    if members is None:
        members = list()
    dn = generate_dn(test_base, batch_id, groupname)
    operation_result = connection.add(dn, [], {'objectClass': 'groupOfNames', 'member': [member[0] for member in members]})
    result = get_operation_result(connection, operation_result)
    if not result['description'] == 'success':
        raise Exception('unable to create group ' + groupname + ': ' + str(result))

    return dn, result

