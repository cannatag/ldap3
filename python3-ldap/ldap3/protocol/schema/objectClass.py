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
from ldap3 import CLASS_ABSTRACT, CLASS_STRUCTURAL, CLASS_AUXILIARY
from ldap3.protocol.schema.oid import Oids
from ldap3.protocol.schema.schema import constantToClassKind, listToString, quotedStringToList, oidsStringToList, extensionToTuple


class ObjectClassInfo():
    def __init__(self, oid = None, name = None, description = None, obsolete = False, superior = None, kind = None, mustContain = None, mayContain = None, extensions = None, experimental = None,
                 definition = None):
        self.oid = oid
        self.name = name
        self.description = description
        self.obsolete = obsolete
        self.superior = superior
        self.kind = kind
        self.mustContain = mustContain
        self.mayContain = mayContain
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
        r = 'ObjectClass ' + self.oid
        r += (' [' + constantToClassKind(self.kind) + '] ') if isinstance(self.kind, int) else ''
        r += (' [OBSOLETE]' + linesep) if self.obsolete else linesep
        r += ('  Short name: ' + listToString(self.name) + linesep) if self.name else ''
        r += ('  Description: ' + self.description + linesep) if self.description else ''
        r += ('  Must contain attributes: ' + listToString(self.mustContain) + linesep) if self.mustContain else ''
        r += ('  May contain attributes: ' + listToString(self.mayContain) + linesep) if self.mayContain else ''
        r += ('  Extensions:' + linesep + linesep.join(['    ' + s[0] + ': ' + listToString(s[1]) for s in self.extensions]) + linesep) if self.extensions else ''
        r += ('  Experimental:' + linesep + linesep.join(['    ' + s[0] + ': ' + listToString(s[1]) for s in self.experimental]) + linesep) if self.experimental else ''
        r += ('  OidInfo:' + str(self.oidInfo)) if self.oidInfo else ''
        return r

    @staticmethod
    def fromDefinition(objectClassDefinition):
        if not objectClassDefinition:
            return None

        if [objectClassDefinition[0] == ')' and objectClassDefinition[:-1] == ')']:
            splitted = re.split('( NAME | DESC | OBSOLETE| SUP | ABSTRACT| STRUCTURAL| AUXILIARY| MUST | MAY | X-| E-)', objectClassDefinition[1:-1])
            values = splitted[::2]
            separators = splitted[1::2]
            separators.insert(0, 'OID')
            defs = list(zip(separators, values))
            objectClassDef = ObjectClassInfo()
            for d in defs:
                key = d[0].strip()
                value = d[1].strip()
                if key == 'OID':
                    objectClassDef.oid = value
                elif key == 'NAME':
                    objectClassDef.name = quotedStringToList(value)
                elif key == 'DESC':
                    objectClassDef.description = value.strip("'")
                elif key == 'OBSOLETE':
                    objectClassDef.obsolete = True
                elif key == 'SUP':
                    objectClassDef.superior = oidsStringToList(value)
                elif key == 'ABSTRACT':
                    objectClassDef.kind = CLASS_ABSTRACT
                elif key == 'STRUCTURAL':
                    objectClassDef.kind = CLASS_STRUCTURAL
                elif key == 'AUXILIARY':
                    objectClassDef.kind = CLASS_AUXILIARY
                elif key == 'MUST':
                    objectClassDef.mustContain = oidsStringToList(value)
                elif key == 'MAY':
                    objectClassDef.mayContain = oidsStringToList(value)
                elif key == 'X-':
                    if not objectClassDef.extensions:
                        objectClassDef.extensions = list()
                    objectClassDef.extensions.append(extensionToTuple('X-' + value))
                elif key == 'E-':
                    if not objectClassDef.experimental:
                        objectClassDef.experimental = list()
                    objectClassDef.experimental.append(extensionToTuple('E-' + value))
                else:
                    raise Exception('malformed Object Class Definition key:' + key)
            objectClassDef.rawDefinition = objectClassDefinition
            return objectClassDef
        else:
            raise Exception('malformed Object Class Definition')
