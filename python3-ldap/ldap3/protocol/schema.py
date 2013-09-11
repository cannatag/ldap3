"""
Created on 2013.09.11

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
from collections import namedtuple
from os import linesep
import re


class ObjectClassInfo(namedtuple('ObjectClassInfo', 'oid, name, description, obsolete, superior, type, mustContains, mayContains, extensions')):
    # def __init__(self, oid, name = None, description = None, obsolete = None, superior = None, type = None, mustContains = None, mayContains = None, extensions = None):
    #     self.oid = oid
    #     self.name = name
    #     self.description = description
    #     self.obsolete = obsolete
    #     self.superior = superior
    #     self.type = type
    #     self.mustContains = mustContains
    #     self.mayContains = mayContains
    #     self.extensions = extensions

    @staticmethod
    def fromDefinition(objectClassDefinition):
        if [objectClassDefinition[0] == ')' and objectClassDefinition[:-1] == ')']:
            splitted = re.split('( NAME | DESC | OBSOLETE| SUP | ABSTRACT| STRUCTURAL| AUXILIARY| MUST | MAY | X-)', objectClassDefinition[1:-1])
            values = splitted[::2]
            separators = splitted[1::2]
            separators.insert(0, 'OID')

            #return d
        # return ObjectClassInfo(values[0], None, None, None, None, None, None, None, None)


class SchemaInfo():
    """
       This class contains info about the ldap server schema read from an entry (default to DSE)
       as defined in rfc 4512. Unkwnown attributes are stored in the "other" dict
    """

    def __init__(self, schemaEntry, attributes):
        self.schemaEntry = schemaEntry
        self.createTimeStamp = attributes.pop('createTimestamp', None)
        self.modifyTimeStamp = attributes.pop('modifyTimestamp', None)
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
