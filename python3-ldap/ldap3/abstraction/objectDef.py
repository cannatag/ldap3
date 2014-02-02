"""
Created on 2014.02.02

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

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

from . import AttrDef

class ObjectDef(object):
    """
    Ogni attributo e' definito da un dizionario che ha come chiave il
    nome con cui si accede all'attributo e come campi:
    attr -> il nome dell'attributo nell'ldap
    valida -> una funzione che valida il valore di ricerca prima di aggiungere l'attributo alla query di ricerca
    preQuery -> una funzione da eseguire sul valore di ricerca il cui risultato viene aggiunto alla query di ricerca
    postQuery -> una funzione da eseguire dopo la ricerca il cui risultato viene ritornato come valore del campo
    ritornaSempre -> un booleano che indica se il valore deve essere ritornato sempre oppure solo se richiesto esplicitamente
    default -> un valore di default da ritornare quando l'attributo non viene trovato
    Se ritornaSempre e' impostato a False viene ritornato il valore di default
    "2"
    """

    def __init__(self, objectClass = None):
        self.objectClass = objectClass
        self.__dict__['_attributes'] = dict()

    def add(self, definition = None):
        if isinstance(definition, str):
            element = AttrDef(definition)
            self.add(element)
        elif isinstance(definition, AttrDef):
            key = definition.key
            for attr in self._attributes:
                if key.lower() == attr.lower():
                    raise Exception('attribute already defined')
            self._attributes[key] = definition
        elif isinstance(definition, list):
            for element in definition:
                self.add(element)
        else:
            raise Exception('unable to add element to object definition')

    def remove(self, item):
        if isinstance(item, str):
            item = ''.join(item.split()).lower()
            for attr in self._attributes:
                if item == attr.lower():
                    del self._attributes[attr]
                    break

    def clear(self):
        self.objectClass = None
        self.__dict__['_attributes'] = dict()

    def __iter__(self):
        for attribute in self._attributes:
            yield self._attributes[attribute]

    def __len__(self):
        return len(self._attributes)

    def __contains__(self, item):
        return True if self.__getitem__(item) else False

    def __repr__(self):
        r = 'objectClass: ' + self.objectClass if self.objectClass else ''
        for attr in self._attributes:
            r += linesep + '    ' + self._attributes[attr].__repr__() + ', '

        return r[:-2] if r[-2] == ',' else r

    def __str__(self):
        return self.__repr__()


    def __getitem__(self, item):
        return self.__getattr__(item)

    def __getattr__(self, item):
        if isinstance(item, str):
            item = ''.join(item.split()).lower()
            for attr in self._attributes:
                if item == attr.lower():
                    return self._attributes[attr]

    def __iadd__(self, other):
        self.add(other)
        return self

    def __isub__(self, other):
        if isinstance(other, AttrDef):
            self.remove(other.key)
        elif isinstance(other, str):
            self.remove(other)

        return self
