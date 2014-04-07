"""
Created on 2013.05.31

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""

from socket import getaddrinfo, gaierror

from ldap3 import GET_NO_INFO, GET_DSA_INFO, GET_SCHEMA_INFO, GET_ALL_INFO, ALL_ATTRIBUTES, SEARCH_SCOPE_BASE_OBJECT, LDAPException, LDAP_MAX_INT
from ..protocol.dse import DsaInfo
from ..protocol.schema import SchemaInfo
from .tls import Tls
import socket


class Server(object):
    """
    LDAP Server definition class
    allowed_referral_hosts can be None (which is the default)
    or a list of tuples of allowed servers ip address or names to contact while redirecting search to referrals.
    Second element of tuple is a boolean to indicate if authentication to that server is allowed,
    if False only anonymous bind will be used.
    as per RFC 4516. Use ('*', False) to allow any host with anonymous bind,
    use ('*', True) to allow any host with same authentication of Server.
    """
    _real_servers = dict()  # dictionary of real servers currently active, the key is the host part of the server address
    # and the value is the messageId counter for all connection to that host)

    def __init__(self, host, port=389, use_ssl=False, allowed_referral_hosts=None, get_info=GET_NO_INFO, tls=None):
        try:
            self.address = getaddrinfo(host, port)[0][4][0]
        except gaierror:
            self.address = host

        if host.startswith('ldap://'):
            self.host = host[7:]
        elif host.startswith('ldaps://'):
            self.host = host[8:]
        else:
            self.host = host
        if isinstance(port, int):
            self.port = port
        else:
            raise LDAPException('port must be an integer')
        if isinstance(allowed_referral_hosts, list):
            self.allowed_referral_hosts = []
            for refServer in allowed_referral_hosts:
                if isinstance(refServer, tuple):
                    if isinstance(refServer[1], bool):
                        self.allowed_referral_hosts.append(refServer)
        elif isinstance(allowed_referral_hosts, tuple):
            if isinstance(allowed_referral_hosts[1], bool):
                self.allowed_referral_hosts = [allowed_referral_hosts]
        else:
            self.allowed_referral_hosts = []

        self.ssl = True if use_ssl else False
        self.tls = Tls() if self.ssl and not tls else tls
        self.name = ('ldaps' if self.ssl else 'ldap') + '://' + self.host + ':' + str(self.port)
        self.get_info = get_info
        self._dsa_info = None
        self._schema_info = None

    def __str__(self):
        if self.host:
            s = self.name + (' - ssl ' if self.ssl else ' - cleartext')
        else:
            s = object.__str__(self)
        return s

    def __repr__(self):
        r = 'Server(host={0.host!r}, port={0.port!r}, use_ssl={0.ssl!r}'.format(self)
        r += '' if not self.allowed_referral_hosts else ', allowed_referral_hosts={0.allowed_referral_hosts!r}'.format(self)
        r += '' if self.tls is None else ', tls={0.tls!r}'.format(self)
        r += '' if not self.get_info else ', get_info={0.get_info!r}'.format(self)
        r += ')'

        return r

    def is_valid(self):
        return True if self.address else False

    def check_availability(self):
        """
        Tries to open, connect and close a socket to specified address and port to check availability
        """
        available = True
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            temp_socket.connect((self.host, self.port))
        except socket.error:
            available = False
        finally:
            try:
                temp_socket.shutdown(socket.SHUT_RDWR)
                temp_socket.close()
            except socket.error:
                available = False

        return available

    def next_message_id(self):
        """
        messageId is unique in all connections to the server
        """
        if self.address and self.address in Server._real_servers:
            Server._real_servers[self.address] += 1
            if Server._real_servers[self.address] >= LDAP_MAX_INT:  # wrap as per MAXINT (2147483647) in rfc4511 specification
                Server._real_servers[self.address] = 1  # 0 is reserved for Unsolicited messages
        else:
            Server._real_servers[self.address] = 1

        return Server._real_servers[self.address]

    def _get_dsa_info(self, connection):
        """
        retrieve DSE operational attribute as per rfc 4512 (5.1)
        """
        self._dsa_info = None

        result = connection.search('', '(objectClass=*)', SEARCH_SCOPE_BASE_OBJECT, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
        if isinstance(result, bool):  # sync request
            self._dsa_info = DsaInfo(connection.response[0]['attributes']) if result else None
        elif result:  # async request, must check if attributes in response
            results, _ = connection.get_response(result)
            if len(results) == 2 and 'attributes' in results[0]:
                self._dsa_info = DsaInfo(results[0]['attributes'])

    def _get_schema_info(self, connection, entry=''):
        """
        retrive schema from subschemaSubentry DSE attribute as per rfc 4512 (4.4 and 5.1)
        entry = '' means DSE
        """
        self._schema_info = None
        schema_entry = None
        if self._dsa_info and entry == '':  # subschemaSubentry already present in dsaInfo
            schema_entry = self._dsa_info.schema_entry[0] if self._dsa_info.schema_entry else None
        else:
            result = connection.search(entry, '(objectClass=*)', SEARCH_SCOPE_BASE_OBJECT, attributes=['subschemaSubentry'], get_operational_attributes=True)
            if isinstance(result, bool):  # sync request
                schema_entry = connection.response[0]['attributes']['subschemaSubentry'][0] if result else None
            else:  # async request, must check if subschemaSubentry in attributes
                results, _ = connection.get_response(result)
                if len(results) == 2 and 'attributes' in results[0] and 'subschemaSubentry' in results[0]['attributes']:
                    schema_entry = results[0]['attributes']['subschemaSubentry'][0]

        if schema_entry:
            result = connection.search(schema_entry, search_filter='(objectClass=subschema)', search_scope=SEARCH_SCOPE_BASE_OBJECT, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
            if isinstance(result, bool):  # sync request
                self._schema_info = SchemaInfo(schema_entry, connection.response[0]['attributes']) if result else None
            else:  # async request, must check if attributes in response
                results, _ = connection.get_response(result)
                if len(results) == 2 and 'attributes' in results[0]:
                    self._schema_info = SchemaInfo(schema_entry, results[0]['attributes'])

    def get_info_from_server(self, connection):
        """
        read info from DSE and from subschema
        """
        if not connection.closed:
            if self.get_info in [GET_DSA_INFO, GET_ALL_INFO]:
                self._get_dsa_info(connection)

            if self.get_info in [GET_SCHEMA_INFO, GET_ALL_INFO]:
                self._get_schema_info(connection)

    @property
    def info(self):
        return self._dsa_info

    @property
    def schema(self):
        return self._schema_info
