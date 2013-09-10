"""
Created on 2013.05.31

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

This file is part of Python3-ldap.

Python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""

from os import linesep
from socket import getaddrinfo, gaierror
from ldap3.tls import Tls
from ldap3 import GET_DSA_INFO, GET_SCHEMA_INFO, GET_ALL_INFO, \
    ALL_ATTRIBUTES, SEARCH_SCOPE_BASE_OBJECT

from ldap3.protocol.oid import decodeOids


class DsaInfo():
    """
    This class contains info about the ldap server (DSA) read from DSE
    as defined in rfc 4512 and rfc 3045. Unkwnown attributes are stored in the "other" dict
    """

    def __init__(self, attributes):
        self.altServers = attributes.pop('altServer', None)
        self.namingContexts = attributes.pop('namingContexts', None)
        self.supportedControls = decodeOids(attributes.pop('supportedControl', None))
        self.supportedExtensions = decodeOids(attributes.pop('supportedExtension', None))
        self.supportedFeatures = decodeOids(attributes.pop('supportedFeatures', None)) + decodeOids(
            attributes.pop('supportedCapabilities', None))
        self.supportedLdapVersions = attributes.pop('supportedLDAPVersion', None)
        self.supportedSaslMechanisms = attributes.pop('supportedSASLMechanisms', None)
        self.vendorName = attributes.pop('vendorName', None)
        self.vendorVersion = attributes.pop('vendorVersion', None)
        self.schemaEntry = attributes.pop('subschemaSubentry', None)
        self.other = attributes

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = 'DSA info (from DSE):' + linesep
        r += ('  Supported LDAP Versions:' + linesep + '    ' + ', '.join([s for s in self.supportedLdapVersions]) + linesep) if self.supportedLdapVersions else ''
        r += ('  Naming Contexts:' + linesep + linesep.join(['    ' + s for s in self.namingContexts]) + linesep) if self.namingContexts else ''
        r += ('  Alternative Servers:' + linesep + linesep.join(['    ' + s for s in self.altServers]) + linesep) if self.altServers else ''
        r += ('  Supported Controls:' + linesep + linesep.join(['    ' + str(s) for s in self.supportedControls]) + linesep) if self.supportedControls else ''
        r += ('  Supported Extensions:' + linesep + linesep.join(['    ' + str(s) for s in self.supportedExtensions]) + linesep) if self.supportedExtensions else ''
        r += ('  Supported Features:' + linesep + linesep.join(['    ' + str(s) for s in self.supportedFeatures]) + linesep) if self.supportedFeatures else ''
        r += ('  Supported SASL Mechanisms:' + linesep + '    ' + ', '.join([s for s in self.supportedSaslMechanisms]) + linesep) if self.supportedSaslMechanisms else ''
        r += ('  Schema Entry:' + linesep + linesep.join(['    ' + s for s in self.schemaEntry]) + linesep) if self.schemaEntry else ''

        r += 'Other:' + linesep
        for k, v in self.other.items():
            r += '  ' + k + ': ' + linesep
            if isinstance(v, str):
                r += v + linesep
            else:
                r += linesep.join(['    ' + str(s) for s in v]) + linesep
        return r


class SchemaInfo():
    """
       This class contains info about the ldap server schema read from DSE
       as defined in rfc 4512. Unkwnown attributes are stored in the "other" dict
    """

    def __init__(self, schemaEntry, attributes):
        self.schemaEntry = schemaEntry
        self.attributeTypes = attributes.pop('attributeTypes', None)
        self.ldapSyntaxes = attributes.pop('ldapSyntaxes', None)
        self.objectClasses = attributes.pop('objectClasses', None)
        self.other = attributes

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = 'DSA Schema from: ' + self.schemaEntry + linesep
        r += ('  Attribute Types:' + linesep + '    ' + ', '.join([s for s in self.attributeTypes]) + linesep) if self.attributeTypes else ''
        r += ('  Object Classes:' + linesep + '    ' + ', '.join([s for s in self.objectClasses]) + linesep) if self.objectClasses else ''
        r += ('  LDAP Syntaxes:' + linesep + '    ' + ', '.join([s for s in self.ldapSyntaxes]) + linesep) if self.ldapSyntaxes else ''
        r += 'Other:' + linesep

        for k, v in self.other.items():
            r += '  ' + k + ': ' + linesep
            if isinstance(v, str):
                r += v + linesep
            else:
                r += linesep.join(['    ' + str(s) for s in v]) + linesep
        return r


class Server():
    """
    LDAP Server definition class
    allowedReferralHosts can be None (which is the default)
    or a list of tuples of allowed servers ip address or names to contact while redirecting search to referrals.
    Second element of tuple is a boolean to indicate if authentication to that server is allowed,
    if False only anonymous bind will be used.
    as per RFC 4516. Use ('*', False) to allow any host with anonymous bind,
    use ('*', True) to allow any host with same authentication of Server.
    """
    _realServers = dict()  # dictionary of real servers currently active, the key is the host part of the server address
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
        if result > 1:  #async request
            self._dsaInfo = DsaInfo(connection.getResponse(result).response[0]['attributes'])
        elif result:
            self._dsaInfo = DsaInfo(connection.response[0]['attributes'])
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
            schemaEntry = connection.getResponse(result).response[0]['attributes']['subschemaSubentry'][0] if result > 1 else connection.response[0]['attributes']['subschemaSubentry'][0]

        if schemaEntry and connection.search(schemaEntry, searchFilter = '(objectClass=subschema)', searchScope = SEARCH_SCOPE_BASE_OBJECT, attributes = ALL_ATTRIBUTES, getOperationalAttributes = True):
                self._schemaInfo = SchemaInfo(schemaEntry, connection.response[0]['attributes'])

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
