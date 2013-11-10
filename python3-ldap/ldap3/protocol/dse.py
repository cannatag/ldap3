"""
Created on 2013.09.11

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
from os import linesep
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
        self.supportedFeatures = decodeOids(attributes.pop('supportedFeatures', None)) + decodeOids(attributes.pop('supportedCapabilities', None))
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
        r += ('  Supported LDAP Versions: ' + ', '.join([s for s in self.supportedLdapVersions]) + linesep) if self.supportedLdapVersions else ''
        r += ('  Naming Contexts:' + linesep + linesep.join(['    ' + s for s in self.namingContexts]) + linesep) if self.namingContexts else ''
        r += ('  Alternative Servers:' + linesep + linesep.join(['    ' + s for s in self.altServers]) + linesep) if self.altServers else ''
        r += ('  Supported Controls:' + linesep + linesep.join(['    ' + str(s) for s in self.supportedControls]) + linesep) if self.supportedControls else ''
        r += (
            '  Supported Extensions:' + linesep + linesep.join(
                ['    ' + str(s) for s in self.supportedExtensions]) + linesep) if self.supportedExtensions else ''
        r += ('  Supported Features:' + linesep + linesep.join(['    ' + str(s) for s in self.supportedFeatures]) + linesep) if self.supportedFeatures else ''
        r += ('  Supported SASL Mechanisms:' + linesep + '    ' + ', '.join(
            [s for s in self.supportedSaslMechanisms]) + linesep) if self.supportedSaslMechanisms else ''
        r += ('  Schema Entry:' + linesep + linesep.join(['    ' + s for s in self.schemaEntry]) + linesep) if self.schemaEntry else ''

        r += 'Other:' + linesep
        for k, v in self.other.items():
            r += '  ' + k + ': ' + linesep
            if isinstance(v, list):
                r += linesep.join(['    ' + str(s) for s in v]) + linesep
            else:
                r += v + linesep
        return r
