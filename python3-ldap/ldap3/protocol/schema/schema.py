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

from os import linesep
import re
from ldap3 import CLASS_ABSTRACT, CLASS_STRUCTURAL, CLASS_AUXILIARY, ATTRIBUTE_USER_APPLICATION, ATTRIBUTE_DIRECTORY_OPERATION, ATTRIBUTE_DISTRIBUTED_OPERATION, ATTRIBUTE_DSA_OPERATION
from ldap3.protocol.schema.attributeType import AttributeTypeInfo
from ldap3.protocol.schema.objectClass import ObjectClassInfo
from ldap3.protocol.schema.oid import Oids


def constantToClassKind(value):
    if value == CLASS_STRUCTURAL:
        return 'STRUCTURAL CLASS'
    elif value == CLASS_ABSTRACT:
        return 'ABSTRACT CLASS'
    elif value == CLASS_AUXILIARY:
        return 'AUXILIARY CLASS'
    else:
        return 'unknown'


def constantToAttributeUsage(value):
    if value == ATTRIBUTE_USER_APPLICATION:
        return 'User Application'
    elif value == ATTRIBUTE_DIRECTORY_OPERATION:
        return "Directory operation"
    elif value == ATTRIBUTE_DISTRIBUTED_OPERATION:
        return 'Distributed operation'
    elif value == ATTRIBUTE_DSA_OPERATION:
        return 'DSA operation'
    else:
        return 'unknown'

def attributeUsageToConstant(value):
    if value == 'userApplications':
        return ATTRIBUTE_USER_APPLICATION
    elif value == 'directoryOperation':
        return ATTRIBUTE_DIRECTORY_OPERATION
    elif value == 'distributedOperation':
        return ATTRIBUTE_DISTRIBUTED_OPERATION
    elif value == 'dsaOperation':
        return ATTRIBUTE_DSA_OPERATION
    else:
        return 'unknown'

def quotedStringToList(quotedString):
        string = quotedString.strip()
        if string[0] == '(' and string[-1] == ')':
            string = string[1:-1]
        elements = string.split("'")
        return [element.strip("'").strip() for element in elements if element]

def oidsStringToList(oidString):
        string = oidString.strip()
        if string[0] == '(' and string[-1] == ')':
            string = string[1:-1]
        elements = string.split('$')
        return [element.strip() for element in elements if element]

def extensionToTuple(extensionString):
        string = extensionString.strip()
        name, _, values = string.partition(' ')
        return name, quotedStringToList(values)

def listToString(listObject):
    if isinstance(listObject, str):
        return listObject

    r = ''
    for element in listObject:
        r += (listToString(element) if isinstance(element, list) else str(element)) + ', '

    return r[:-2] if r else ''


class SchemaInfo():
    """
       This class contains info about the ldap server schema read from an entry (default entry is DSE)
       as defined in rfc 4512. Unkwnown attributes are stored in the "other" dict
    """

    def __init__(self, schemaEntry, attributes):
        self.schemaEntry = schemaEntry
        self.createTimeStamp = attributes.pop('createTimestamp', None)
        self.modifyTimeStamp = attributes.pop('modifyTimestamp', None)
        self.attributeTypes = [AttributeTypeInfo.fromDefinition(attributeTypeDef) for attributeTypeDef in attributes.pop('attributeTypes', [])]
        self.ldapSyntaxes = attributes.pop('ldapSyntaxes', None)
        self.objectClasses = [ObjectClassInfo.fromDefinition(objectClassDef) for objectClassDef in attributes.pop('objectClasses', [])]
        self.other = attributes

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = 'DSA Schema from: ' + self.schemaEntry + linesep
        r += ('  Attribute Types:' + linesep + '    ' + ', '.join([str(s) for s in self.attributeTypes]) + linesep) if self.attributeTypes else ''
        r += ('  Object Classes:' + linesep + '    ' + ', '.join([str(s) for s in self.objectClasses]) + linesep) if self.objectClasses else ''
        r += ('  LDAP Syntaxes:' + linesep + '    ' + ', '.join([str(s) for s in self.ldapSyntaxes]) + linesep) if self.ldapSyntaxes else ''
        r += 'Other:' + linesep

        for k, v in self.other.items():
            r += '  ' + k + ': ' + linesep
            r += v if isinstance(v, str) else (linesep.join(['    ' + str(s) for s in v])) + linesep
        return r


class BaseObjectInfo():
    def __init__(self, oid = None, name = None, description = None, obsolete = False, extensions = None, experimental = None, definition = None):
        self.oid = oid
        self.name = name
        self.description = description
        self.obsolete = obsolete
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
        r = 'Matching rule ' + self.oid
        r += (' [OBSOLETE]' + linesep) if self.obsolete else linesep
        r += ('  Short name: ' + listToString(self.name) + linesep) if self.name else ''
        r += ('  Description: ' + self.description + linesep) if self.description else ''
        r += ('  Syntax ' + listToString(self.syntax) + linesep) if self.syntax else ''
        r += '<OTHER-SCHEMA-DESC-HERE>'
        r += ('  Extensions:' + linesep + linesep.join(['    ' + s[0] + ': ' + listToString(s[1]) for s in self.extensions]) + linesep) if self.extensions else ''
        r += ('  Experimental:' + linesep + linesep.join(['    ' + s[0] + ': ' + listToString(s[1]) for s in self.experimental]) + linesep) if self.experimental else ''
        r += ('  OidInfo:' + str(self.oidInfo)) if self.oidInfo else ''
        return r

    @staticmethod
    def fromDefinition(objectDefinition, pattern, objectClass):
        if not objectDefinition:
            return None

        if [objectDefinition[0] == ')' and objectDefinition[:-1] == ')']:
            splitted = re.split('( NAME | DESC | OBSOLETE| | X-| E-|' + pattern + ')', objectDefinition[1:-1])
            values = splitted[::2]
            separators = splitted[1::2]
            separators.insert(0, 'OID')
            defs = list(zip(separators, values))
            objectDef = objectClass()
            for d in defs:
                key = d[0].strip()
                value = d[1].strip()
                if key == 'OID':
                    objectDef.oid = value
                elif key == 'NAME':
                    objectDef.name = quotedStringToList(value)
                elif key == 'DESC':
                    objectDef.description = value.strip("'")
                elif key == 'OBSOLETE':
                    objectDef.obsolete = True
                elif key == 'SYNTAX':
                    objectDef.syntax = oidsStringToList(value)
                elif key == 'SUP':
                    objectDef.superior = oidsStringToList(value)
                elif key == 'ABSTRACT':
                    objectDef.kind = CLASS_ABSTRACT
                elif key == 'STRUCTURAL':
                    objectDef.kind = CLASS_STRUCTURAL
                elif key == 'AUXILIARY':
                    objectDef.kind = CLASS_AUXILIARY
                elif key == 'MUST':
                    objectDef.mustContain = oidsStringToList(value)
                elif key == 'MAY':
                    objectDef.mayContain = oidsStringToList(value)
                elif key == 'X-':
                    if not objectDef.extensions:
                        objectDef.extensions = list()
                    objectDef.extensions.append(extensionToTuple('X-' + value))
                elif key == 'E-':
                    if not objectDef.experimental:
                        objectDef.experimental = list()
                    objectDef.experimental.append(extensionToTuple('E-' + value))
                else:
                    raise Exception('malformed schema definition key:' + key)
            objectDef.rawDefinition = objectDefinition
            return objectDef
        else:
            raise Exception('malformed schema definition')
