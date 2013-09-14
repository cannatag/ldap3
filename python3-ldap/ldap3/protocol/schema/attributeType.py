"""
Created on 2013.09.14

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
import re
from ldap3.protocol.schema.oid import Oids
from ldap3.protocol.schema.schema import constantToAttributeUsage, listToString, quotedStringToList, oidsStringToList, attributeUsageToConstant, extensionToTuple


class AttributeTypeInfo():
    def __init__(self, oid = None, name = None, description = None, obsolete = False, superior = None, equality = None, ordering = None, substring = None, syntax = None, singleValue = False, collective = False, noUserModification = False, usage = None, extensions = None, experimental = None,
                 definition = None):
        self.oid = oid
        self.name = name
        self.description = description
        self.obsolete = obsolete
        self.superior = superior
        self.equality = equality
        self.ordering = ordering
        self.substring = substring
        self.syntax = syntax
        self.singleValue = singleValue
        self.collective = collective
        self.noUserModification = noUserModification
        self.usage = usage
        self.extensions = extensions
        self.experimental = experimental
        self.rawDefinition = definition
        self._oidInfo = None

    @property
    def oidInfo(self):
        if self._oidInfo is None and self.oid:
            self._oidInfo = Oids.get(self.oid, '')

        return self._oidInfo if self._oidInfo else None


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = 'AttributeType ' + self.oid
        r += (' [OBSOLETE]' + linesep) if self.obsolete else ''
        r += ' [SINGLE VALUE]' if self.singleValue else ''
        r += ' [COLLECTIVE]' if self.collective else ''
        r += ' [NO USER MODIFICATION]' if self.noUserModification else ''
        r += linesep
        r += ('  Usage: ' + constantToAttributeUsage(self.usage) + linesep) if self.usage else ''
        r += ('  Short name: ' + listToString(self.name) + linesep) if self.name else ''
        r += ('  Description: ' + self.description + linesep) if self.description else ''
        r += ('  Equality rule: ' + listToString(self.equality) + linesep) if self.equality else ''
        r += ('  Ordering rule: ' + listToString(self.ordering) + linesep) if self.ordering else ''
        r += ('  Substring rule: ' + listToString(self.substring) + linesep) if self.substring else ''
        r += ('  Syntax ' + listToString(self.syntax) + linesep) if self.syntax else ''
        r += ('  Extensions:' + linesep + linesep.join(['    ' + s[0] + ': ' + listToString(s[1]) for s in self.extensions]) + linesep) if self.extensions else ''
        r += ('  Experimental:' + linesep + linesep.join(['    ' + s[0] + ': ' + listToString(s[1]) for s in self.experimental]) + linesep) if self.experimental else ''
        r += ('  OidInfo: ' + str(self.oidInfo)) if self.oidInfo else ''
        return r

    @staticmethod
    def fromDefinition(attributeTypeDefinition):
        if not attributeTypeDefinition:
            return None

        if [attributeTypeDefinition[0] == ')' and attributeTypeDefinition[:-1] == ')']:
            splitted = re.split('( NAME | DESC | OBSOLETE| SUP | EQUALITY | ORDERING | SUBSTR | SYNTAX | SINGLE-VALUE| COLLECTIVE| NO-USER-MODIFICATION| USAGE | X-| E-)', attributeTypeDefinition[1:-1])
            values = splitted[::2]
            separators = splitted[1::2]
            separators.insert(0, 'OID')
            defs = list(zip(separators, values))
            attributeTypeDef = AttributeTypeInfo()
            for d in defs:
                key = d[0].strip()
                value = d[1].strip()
                if key == 'OID':
                    attributeTypeDef.oid = value
                elif key == 'NAME':
                    attributeTypeDef.name = quotedStringToList(value)
                elif key == 'DESC':
                    attributeTypeDef.description = value.strip("'")
                elif key == 'OBSOLETE':
                    attributeTypeDef.obsolete = True
                elif key == 'SUP':
                    attributeTypeDef.superior = oidsStringToList(value)
                elif key == 'EQUALITY':
                    attributeTypeDef.equality = oidsStringToList(value)
                elif key == 'ORDERING':
                    attributeTypeDef.ordering = oidsStringToList(value)
                elif key == 'SUBSTR':
                    attributeTypeDef.substr = oidsStringToList(value)
                elif key == 'SYNTAX':
                    attributeTypeDef.syntax = oidsStringToList(value)
                elif key == 'SINGLE-VALUE':
                    attributeTypeDef.singleValue = True
                elif key == 'COLLECTIVE':
                    attributeTypeDef.collective = True
                elif key == 'NO-USER-MODIFICATION':
                    attributeTypeDef.noUserModification = True
                elif key == 'USAGE':
                    attributeTypeDef.usage = attributeUsageToConstant(value)
                elif key == 'X-':
                    if not attributeTypeDef.extensions:
                        attributeTypeDef.extensions = list()
                    attributeTypeDef.extensions.append(extensionToTuple('X-' + value))
                elif key == 'E-':
                    if not attributeTypeDef.experimental:
                        attributeTypeDef.experimental = list()
                    attributeTypeDef.experimental.append(extensionToTuple('E-' + value))
                else:
                    raise Exception('malformed Attribute Type Definition key:' + key)
            attributeTypeDef.rawDefinition = attributeTypeDefinition
            return attributeTypeDef
        else:
            raise Exception('malformed Attribute Type Definition')

    @staticmethod
    def _returnKind(classKind):
        if classKind == 0:
            return 'STRUCTURAL'
        elif classKind == 1:
            return 'ABSTRACT'
        elif classKind == 2:
            return 'AUXILIARY'
        else:
            return 'unknown'
