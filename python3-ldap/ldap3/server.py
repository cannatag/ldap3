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
from ldap3.protocol.dse import DsaInfo
from ldap3.protocol.schema import SchemaInfo
from ldap3.tls import Tls
from ldap3 import GET_DSA_INFO, GET_SCHEMA_INFO, GET_ALL_INFO, \
    ALL_ATTRIBUTES, SEARCH_SCOPE_BASE_OBJECT


class Server(object):
    """
    LDAP Server definition class
    allowedReferralHosts can be None (which is the default)
    or a list of tuples of allowed servers ip address or names to contact while redirecting search to referrals.
    Second element of tuple is a boolean to indicate if authentication to that server is allowed,
    if False only anonymous bind will be used.
    as per RFC 4516. Use ('*', False) to allow any host with anonymous bind,
    use ('*', True) to allow any host with same authentication of Server.
    """
    _realServers = dict()   # dictionary of real servers currently active, the key is the host part of the server address
                            # and the value is the messageId counter for all connection to that host)
    def __init__(self, host, port = 389, useSsl = False, allowedReferralHosts = None, getInfo = None, tls = None):
        """
        Constructor
        """
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
            raise Exception('port must be an integer')
        if isinstance(allowedReferralHosts, list):
            self.allowedReferralHosts = []
            for refServer in allowedReferralHosts:
                if isinstance(refServer, tuple):
                    if isinstance(refServer[1], bool):
                        self.allowedReferralHosts.append(refServer)
        elif isinstance(allowedReferralHosts, tuple):
            if isinstance(allowedReferralHosts[1], bool):
                self.allowedReferralHosts = [allowedReferralHosts]
        else:
            self.allowedReferralHosts = []

        self.ssl = True if useSsl else False
        self.tls = Tls() if self.ssl and not tls else tls
        self.name = ('ldaps' if self.ssl else 'ldap') + '://' + self.host + ':' + str(self.port)
        self.getInfo = getInfo
        self._dsaInfo = None
        self._schemaInfo = None

    def __str__(self):
        if self.host:
            s = self.name + (' - ssl ' if self.ssl else ' - cleartext')
        else:
            s = super(Server, self).__str__()
        return s

    def __repr__(self):
        r = 'Server(host={0.host!r}, port={0.port!r}, ssl={0.ssl!r}'.format(self)
        r += '' if not self.allowedReferralHosts else ', allowedReferralHosts={0.allowedReferralHosts!r}'.format(self)
        r += '' if self.tls is None else ', tls={0.tls!r}'.format(self)
        r += '' if not self.getInfo else ', getInfo={0.getInfo!r}'.format(self)
        r += ')'

        return r

    def isValid(self):
        return True if self.address else False

    def nextMessageId(self):
        """
        messageId is unique in all connections to the server
        """
        if self.address and self.address in Server._realServers:
            Server._realServers[self.address] += 1
            if Server._realServers[
                self.address] > 2147483646:  # wrap as per MAXINT (2147483647) in rfc4511 specification
                Server._realServers[self.address] = 1  # 0 is reserved for Unsolicited messages
        else:
            Server._realServers[self.address] = 1

        return Server._realServers[self.address]

    def _getDsaInfo(self, connection):
        """
        retrieve DSE operational attribute as per rfc 4512 (5.1)
        """
        result = connection.search('', '(objectClass=*)', SEARCH_SCOPE_BASE_OBJECT, attributes = ALL_ATTRIBUTES, getOperationalAttributes = True)
        if isinstance(result, bool):  #sync request
            self._dsaInfo = DsaInfo(connection.response[0]['attributes'])
        elif result:
            self._dsaInfo = DsaInfo(connection.getResponse(result)[0]['attributes'])
        else:
            self._dsaInfo = None

    def _getSchemaInfo(self, connection, entry = ''):
        """
        retrive schema from subschemaSubentry DSE attribute as per rfc 4512 (4.4 and 5.1)
        entry = '' means DSE
        """
        self._schemaInfo = None
        schemaEntry = None

        if self._dsaInfo and entry == '':  # subschemaSubentry already present in dsaInfo
            schemaEntry = self._dsaInfo.schemaEntry[0] if self._dsaInfo.schemaEntry else None
        else:
            result = connection.search(schemaEntry, '(objectClass=*)', SEARCH_SCOPE_BASE_OBJECT, attributes = ['subschemaSubentry'], getOperationalAttributes = True)
            if isinstance(result, bool):
                schemaEntry = connection.response[0]['attributes']['subschemaSubentry'][0]
            else:
                schemaEntry = connection.getResponse(result)[0]['attributes']['subschemaSubentry'][0]

        if schemaEntry:
            print('GETTING SCHEMA FROM:', schemaEntry)
            result = connection.search(schemaEntry, searchFilter = '(objectClass=subschema)', searchScope = SEARCH_SCOPE_BASE_OBJECT, attributes = ALL_ATTRIBUTES, getOperationalAttributes = True)
            if isinstance(result, bool):
                self._schemaInfo = SchemaInfo(schemaEntry, connection.response[0]['attributes']) if result else None
            else:
                self._schemaInfo = SchemaInfo(schemaEntry, connection.getResponse(result)[0]['attributes'])

    def getInfoFromServer(self, connection):
        """
        read info from DSE and from subschema
        """
        if not connection.closed:
            if self.getInfo == GET_DSA_INFO or self.getInfo == GET_ALL_INFO:
                self._getDsaInfo(connection)

            if self.getInfo == GET_SCHEMA_INFO or self.getInfo == GET_ALL_INFO:
                self._getSchemaInfo(connection)

    @property
    def info(self):
        return self._dsaInfo

    @property
    def schema(self):
        return self._schemaInfo
