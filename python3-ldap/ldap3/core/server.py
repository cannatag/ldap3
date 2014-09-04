"""
"""

# Created on 2014.05.31
#
# Author: Giovanni Cannata
#
# Copyright 2014 Giovanni Cannata
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

import socket
from threading import Lock
from .. import GET_NO_INFO, GET_DSA_INFO, GET_SCHEMA_INFO, GET_ALL_INFO, ALL_ATTRIBUTES, SEARCH_SCOPE_BASE_OBJECT, LDAP_MAX_INT
from .exceptions import LDAPInvalidPort
from ..core.exceptions import LDAPInvalidServerError
from ..protocol.rfc4512 import SchemaInfo, DsaInfo
from .tls import Tls


class Server(object):
    """
    LDAP Server definition class

    Allowed_referral_hosts can be None (default), or a list of tuples of
    allowed servers ip address or names to contact while redirecting
    search to referrals.

    The second element of the tuple is a boolean to indicate if
    authentication to that server is allowed; if False only anonymous
    bind will be used.

    Per RFC 4516. Use ('*', False) to allow any host with anonymous
    bind, use ('*', True) to allow any host with same authentication of
    Server.
    """

    _message_counter = 0
    _message_id_lock = Lock()

    def __init__(self,
                 host,
                 port=None,
                 use_ssl=False,
                 allowed_referral_hosts=None,
                 get_info=GET_NO_INFO,
                 tls=None,
                 formatter=None):

        url_given = False
        if host.startswith('ldap://'):
            self.host = host[7:]
            use_ssl = False
            url_given = True
        elif host.startswith('ldaps://'):
            self.host = host[8:]
            use_ssl = True
            url_given = True
        else:
            self.host = host

        if ':' in self.host and self.host.count(':') == 1:
            hostname, _, hostport = self.host.partition(':')
            try:
                port = int(hostport) or port
                self.host = hostname
            except ValueError:
                raise LDAPInvalidPort('port must be an integer')
        elif url_given and self.host.startswith('['):
            hostname, sep, hostport = self.host[1:].partition(']')
            if sep != ']' or not self._is_ipv6(hostname):
                raise LDAPInvalidServerError()
            if len(hostport):
                if not hostport.startswith(':'):
                    raise LDAPInvalidServerError('invalid URL in server name')
                if not hostport[1:].isdecimal():
                    raise LDAPInvalidPort('port must be an integer')
                port = int(hostport[1:])
            self.host = hostname
        elif not url_given and self._is_ipv6(self.host):
            pass
        elif self.host.count(':') > 1:
            raise LDAPInvalidServerError()

        if not use_ssl and not port:
            port = 389
        elif use_ssl and not port:
            port = 636

        if isinstance(port, int):
            if port in range(0, 65535):
                self.port = port
            else:
                raise LDAPInvalidPort('port must in range from 0 to 65535')
        else:
            raise LDAPInvalidPort('port must be an integer')

        if isinstance(allowed_referral_hosts, (list, tuple)):
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

        if self._is_ipv6(self.host):
            self.name = ('ldaps' if self.ssl else 'ldap') + '://[' + self.host + ']:' + str(self.port)
        else:
            self.name = ('ldaps' if self.ssl else 'ldap') + '://' + self.host + ':' + str(self.port)

        self.get_info = get_info
        self._dsa_info = None
        self._schema_info = None
        self.lock = Lock()
        self.custom_formatter = formatter
        self._address_info = None  # property self.address_info resolved at open time (or when you call check_availability)

    @staticmethod
    def _is_ipv6(host):
        try:
            socket.inet_pton(socket.AF_INET6, host)
        except (socket.error, AttributeError):
            return False
        return True

    def __str__(self):
        if self.host:
            s = self.name + (' - ssl' if self.ssl else ' - cleartext')
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

    @property
    def address_info(self):
        if not self._address_info:
            self._address_info = socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM)

        return self._address_info

    def check_availability(self):
        """
        Tries to open, connect and close a socket to specified address
        and port to check availability.
        """
        available = True
        try:
            temp_socket = socket.socket(*self.address_info[0][:3])
            try:
                temp_socket.connect(self.address_info[0][4])
            except socket.error:
                available = False
            finally:
                try:
                    temp_socket.shutdown(socket.SHUT_RDWR)
                    temp_socket.close()
                except socket.error:
                    available = False
        except socket.gaierror:
            available = False

        return available

    @staticmethod
    def next_message_id():
        """
        messageId is unique for all connections
        """
        with Server._message_id_lock:
            Server._message_counter += 1
            if Server._message_counter >= LDAP_MAX_INT:
                Server._message_counter = 1

        return Server._message_counter

    def _get_dsa_info(self, connection):
        """
        Retrieve DSE operational attribute as per RFC4512 (5.1).
        """
        result = connection.search('', '(objectClass=*)', SEARCH_SCOPE_BASE_OBJECT, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
        self._dsa_info = None
        with self.lock:
            if isinstance(result, bool):  # sync request
                self._dsa_info = DsaInfo(connection.response[0]['attributes']) if result else None
            elif result:  # async request, must check if attributes in response
                results, _ = connection.get_response(result)
                if len(results) == 1 and 'attributes' in results[0]:
                    self._dsa_info = DsaInfo(results[0]['attributes'])

    def _get_schema_info(self, connection, entry=''):
        """
        Retrieve schema from subschemaSubentry DSE attribute, per RFC
        4512 (4.4 and 5.1); entry = '' means DSE.
        """
        schema_entry = None
        if self._dsa_info and entry == '':  # subschemaSubentry already present in dsaInfo
            schema_entry = self._dsa_info.schema_entry[0] if self._dsa_info.schema_entry else None
        else:
            result = connection.search(entry, '(objectClass=*)', SEARCH_SCOPE_BASE_OBJECT, attributes=['subschemaSubentry'], get_operational_attributes=True)
            if isinstance(result, bool):  # sync request
                schema_entry = connection.response[0]['attributes']['subschemaSubentry'][0] if result else None
            else:  # async request, must check if subschemaSubentry in attributes
                results, _ = connection.get_response(result)
                if len(results) == 1 and 'attributes' in results[0] and 'subschemaSubentry' in results[0]['attributes']:
                    schema_entry = results[0]['attributes']['subschemaSubentry'][0]

        result = None
        if schema_entry:
            result = connection.search(schema_entry,
                                       search_filter='(objectClass=subschema)',
                                       search_scope=SEARCH_SCOPE_BASE_OBJECT,
                                       attributes=['objectClasses',  # requests specific subschema attributes
                                                   'attributeTypes',
                                                   'ldapSyntaxes',
                                                   'matchingRules',
                                                   'matchingRuleUse',
                                                   'dITContentRules',
                                                   'dITStructureRules',
                                                   'nameForms',
                                                   'createTimestamp',
                                                   'modifyTimestamp',
                                                   '*'],  # requests all remaining attributes (other)
                                       get_operational_attributes=True
                                       )

        with self.lock:
            self._schema_info = None
            if result:
                if isinstance(result, bool):  # sync request
                    self._schema_info = SchemaInfo(schema_entry, connection.response[0]['attributes']) if result else None
                else:  # async request, must check if attributes in response
                    results, _ = connection.get_response(result)
                    if len(results) == 1 and 'attributes' in results[0]:
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
