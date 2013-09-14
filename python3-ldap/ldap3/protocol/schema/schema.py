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
from ldap3 import CLASS_ABSTRACT, CLASS_STRUCTURAL, CLASS_AUXILIARY, ATTRIBUTE_USER_APPLICATION, ATTRIBUTE_DIRECTORY_OPERATION, ATTRIBUTE_DISTRIBUTED_OPERATION, ATTRIBUTE_DSA_OPERATION
from ldap3.protocol.schema.attributeType import AttributeTypeInfo
from ldap3.protocol.schema.objectClass import ObjectClassInfo


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
