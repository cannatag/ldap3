"""
Created on 2014.01.06

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

class attrDef(object):
    def __init__(self, name, friendlyName = None, multiValue = None, validate = None, preQuery = None, postQuery = None, default = None, always = False):
        self.name = name
        self.friendlyName = friendlyName or name
        self.multiValue = multiValue if multiValue else False
        self.validate = validate
        self.preQuery = preQuery
        self.postQuery = postQuery
        self.default = default
        self.always = always


class attrDefs(object):
    """
    Ogni attributo e' definito da un dizionario che ha come chiave il
    nome con cui si accede all'attributo e come campi:
    attr -> il nome dell'attributo nell'ldap
    multivalue -> un booleano che indica se l'attributo puo' avere piu' valori
    valida -> una funzione che valida il valore di ricerca prima di aggiungere l'attributo alla query di ricerca
    preQuery -> una funzione da eseguire sul valore di ricerca il cui risultato viene aggiunto alla query di ricerca
    postQuery -> una funzione da eseguire dopo la ricerca il cui risultato viene ritornato come valore del campo
    ritornaSempre -> un booleano che indica se il valore deve essere ritornato sempre oppure solo se richiesto esplicitamente
    default -> un valore di default da ritornare quando l'attributo non viene trovato
    Se ritornaSempre e' impostato a False viene ritornato il valore di default
    "2"
    """
    def __init__(self):
        self.attributes = dict()

    def add(self, name, friendlyName = None, multivalue = None, validate = None, preQuery = None, postQuery = None, default = None, always = False):
        if isinstance(name, attrDef):
            self.attributes[name.friendlyName] = name
        else:
            attr = attrDef()
            attr.name = name
            attr.friendlyName = friendlyName or name


        if name in self.attributes:
            raise Exception('attribute already defined')
        attr = dict()
        attr['attribute']
        self.attributes[name] = dict()



