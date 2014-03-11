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

from ..protocol.oid import decode_oids


class DsaInfo():
    """
    This class contains info about the ldap server (DSA) read from DSE
    as defined in rfc 4512 and rfc 3045. Unkwnown attributes are stored in the "other" dict
    """

    def __init__(self, attributes):
        self.alt_servers = attributes.pop('altServer', None)
        self.naming_contexts = attributes.pop('namingContexts', None)
        self.supported_controls = decode_oids(attributes.pop('supportedControl', None))
        self.supported_extensions = decode_oids(attributes.pop('supportedExtension', None))
        self.supported_features = decode_oids(attributes.pop('supportedFeatures', None)) + decode_oids(attributes.pop('supportedCapabilities', None))
        self.supported_ldap_versions = attributes.pop('supportedLDAPVersion', None)
        self.supported_sasl_mechanisms = attributes.pop('supportedSASLMechanisms', None)
        self.vendor_name = attributes.pop('vendorName', None)
        self.vendor_version = attributes.pop('vendorVersion', None)
        self.schema_entry = attributes.pop('subschemaSubentry', None)
        self.other = attributes

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = 'DSA info (from DSE):' + linesep
        r += ('  Supported LDAP Versions: ' + ', '.join([s for s in self.supported_ldap_versions]) + linesep) if self.supported_ldap_versions else ''
        r += ('  Naming Contexts:' + linesep + linesep.join(['    ' + s for s in self.naming_contexts]) + linesep) if self.naming_contexts else ''
        r += ('  Alternative Servers:' + linesep + linesep.join(['    ' + s for s in self.alt_servers]) + linesep) if self.alt_servers else ''
        r += ('  Supported Controls:' + linesep + linesep.join(['    ' + str(s) for s in self.supported_controls]) + linesep) if self.supported_controls else ''
        r += ('  Supported Extensions:' + linesep + linesep.join(['    ' + str(s) for s in self.supported_extensions]) + linesep) if self.supported_extensions else ''
        r += ('  Supported Features:' + linesep + linesep.join(['    ' + str(s) for s in self.supported_features]) + linesep) if self.supported_features else ''
        r += ('  Supported SASL Mechanisms:' + linesep + '    ' + ', '.join([s for s in self.supported_sasl_mechanisms]) + linesep) if self.supported_sasl_mechanisms else ''
        r += ('  Schema Entry:' + linesep + linesep.join(['    ' + s for s in self.schema_entry]) + linesep) if self.schema_entry else ''
        r += 'Other:' + linesep
        for k, v in self.other.items():
            r += '  ' + k + ': ' + linesep
            if isinstance(v, list):
                r += linesep.join(['    ' + str(s) for s in v]) + linesep
            else:
                r += v + linesep
        return r
