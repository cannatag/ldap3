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
from datetime import datetime
from os import linesep

from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE, SEARCH_SCOPE_SINGLE_LEVEL, SEARCH_DEREFERENCE_ALWAYS, SEARCH_SCOPE_BASE_OBJECT
from .attribute import Attribute
from .entry import Entry


def _retSearchValue(value):
    return value[0] + '=' + value[1:] if value[0] in '<>~' and value[1] != '=' else value

def _createQueryDict(queryText):
    """
    Create a dictonary  with query key:value definitions
    QUeryText is a comma delimited key:value sequence
    """
    queryDict = dict()
    if queryText:
        for argValueStr in queryText.split(','):
            if ':' in argValueStr:
                argValueList = argValueStr.split(':')
                queryDict[argValueList[0].strip()] = argValueList[1].strip()

    return queryDict


class Reader(object):
    """
    Reader object perform the search with the requested parameters:
    'connection': the connection to use
    'objectDef': the definition of the LDAP object to be returned
    'query': the simplified query to be transformed in an LDAP filter
    'base': starting base of the DIT
    'componentInAnd': specify if components of query mus be all satisfied or not (AND/OR)
    'subTree': a boolean to specify if the search must be performed ad Single Level (False) or Whole SubTree (True)
    'getOperationalAttributes': a boolean to specify if operational attributes are returned or not
    'controls': controls to be used in search
    """
    def __init__(self, connection, objectDef, query, base, componentsInAnd = True, subTree = True, getOperationalAttributes = False,  noSingleValueList = True, controls = None):
        self.connection = connection
        self.query = query
        self.definition = objectDef
        self.base = base
        self.componentsInAnd = componentsInAnd
        self.attributes = sorted([attr.name for attr in self.definition])
        self.getOperationalAttributes = getOperationalAttributes
        self.controls = controls
        self.subTree = subTree
        self.noSingleValueList = noSingleValueList
        self.reset()

    def __repr__(self):
        r = 'CONN   : ' + str(self.connection) + linesep
        r += 'BASE   : ' + repr(self.base) + (' [SUB]' if self.subTree else ' [LEVEL]') + linesep
        r += 'DEFS   : ' + self.definition.objectClass + ' ['
        for attrDef in self.definition:
            r += (attrDef.key if attrDef.key == attrDef.name else (attrDef.key + ' <' + attrDef.name + '>')) + ', '
        if r[-2] == ',':
            r = r[:-2]
        r += ']' + linesep
        r += 'QUERY  : ' + repr(self.query) + (' [AND]' if self.componentsInAnd else ' [OR]') + linesep
        r += 'ATTRS  : ' + repr(self.attributes) + (' [OPERATIONAL]' if self.getOperationalAttributes else '') + linesep
        r += 'FILTER : ' + repr(self.queryFilter) + linesep
        if self.executionTime:
            r += 'ENTRIES: ' + str(len(self.entries))
            r += ' [SUB]' if self.lastSubTree else ' [level]'
            r += ' [SIZE LIMIT: ' + str(self.sizeLimit) + ']'if self.sizeLimit else ''
            r += ' [TIME LIMIT: ' + str(self.timeLimit) + ']' if self.sizeLimit else ''
            r += ' [no single value list]' if self.noSingleValueList else ''
            r += ' [executed at: ' + str(self.executionTime.ctime()) + ']' + linesep
        return r

    def __str__(self):
        return self.__repr__()

    def clear(self):
        self.dereferenceAliases = SEARCH_DEREFERENCE_ALWAYS
        self.sizeLimit = 0
        self.timeLimit = 0
        self.typesOnly = False
        self.pagedSize = None
        self.pagedCriticality = False

    def reset(self):
        self.clear()
        self.validatedQuery = None
        self._queryDict = dict()
        self._validatedQueryDict = dict()
        self.executionTime = None
        self.queryFilter = None
        self.entries = []
        self.pagedCookie = None
        self.lastSubTree = None
        self._createQueryFilter()

    def __iter__(self):
        return self.entries.__iter__()

    def __getitem__(self, item):
        return self.entries[item]

    def __len__(self):
        return len(self.entries)

    def _validateQuery(self):
        """
        Elabora il testo di una query e verifica che i campi richiesti siano presenti nel dizionario
        del reader relativo. Se non sono presenti il campo viene ignorato.
        Se l'attributo nel dizionario ha un campo 'valida' la relativa funzione viene eseguita per
        verificare se il valore da ricercare sia tra quelli possibili. In caso di
        valore non validato viene generata un'eccezione.
        Il testo della query deve essere composto da coppie chiave:valore separate dalla virgola.
        Sono riconosciute alcune chiavi speciali che modificano il funzionamento della query:
        'query_and_or' (con valore 'AND' oppure 'OR') -> indica che i campi di ricerca sono in AND oppure in OR
        'query_filtro' -> esegue un generico filtro LDAP
        'query_base' -> base su cui eseguire 'query_filtro', non puo' essere usato senza 'query_filtro'
        'query_livello' (con valore 'SUB' oppure 'LIVELLO') -> indica il livello di esecuzione della query
        Per eseguire un AND o un OR nello stesso attributo far precedere la chiave dal segno '&' oppure '|'
        e dividere i valori multipli con un ';'
        In 'query_filtro' e in 'query_base' eventuali ',' devono essere indicate con ';'
        Un valore preceduto da un '!' indica un NOT
        Il valore e' composto da un segno di ricerca (=, >, <, ~) e dalla chiave di ricerca
        Ritorna il testo della query validato che puo' essere trasformato in dizionario per essere utilizzato
        come chiave di ricerca delle funzioni _cerca dei reader di classe ldap.
        """

        if not self._queryDict:
            self._queryDict = _createQueryDict(self.query)

        query = ''
        for d in sorted(self._queryDict):
            attr = d[1:] if d[0] in '&|' else d
            for attrDef in self.definition:
                if ''.join(attr.split()).lower() == attrDef.key.lower():
                    attr = attrDef.key
                    break

            if attr in self.definition:
                vals = sorted(self._queryDict[d].split(';'))

                query += d[0] + attr if d[0] in '&|' else attr
                query += ': '
                for val in vals:
                    val = val.strip()
                    valNot = True if val[0] == '!' else False
                    valSearchOperator = '='  # default
                    if valNot:
                        if val[1:].lstrip()[0] not in '=<>~':
                            value = val[1:].lstrip()
                        else:
                            valSearchOperator = val[1:].lstrip()[0]
                            value = val[1:].lstrip()[1:]
                    else:
                        if val[0] not in '=<>~':
                            value = val.lstrip()
                        else:
                            valSearchOperator = val[0]
                            value = val[1:].lstrip()

                    if self.definition[attr].validate:
                        if not self.definition[attr].validate(value):
                            raise Exception('validation failed for attribute %s with value %s' % (val, self._queryDict[d]))

                    if valNot:
                        query += '!' + valSearchOperator + value
                    else:
                        query += valSearchOperator + value

                    query += ';'
                query = query[:-1]
                query += ', '

        self.validatedQuery = query[:-2]
        self._validatedQueryDict = _createQueryDict(self.validatedQuery)

    def _createQueryFilter(self):
        """
        Prepara la query ldap e verifica che gli attributi siano presenti in attrDefs
        La query e' composta di un dizionario contenente le chiavi di ricerca cosi'
        come sono definite nelle classi readers. Se e' presente una funzione di 'preQuery'
        questa viene eseguita passandogli il valore della chiave di ricerca e il suo risultato
        viene aggiunto alla query.
        Sono riconosciute alcune chiavi speciali che modificano il funzionamento della query:
        'query_and_or' (con valore 'AND' oppure 'OR') -> indica che i campi di ricerca sono in AND oppure in OR
        'query_filtro' -> esegue un generico filtro LDAP con base indicata in 'query_base'
        'query_base' -> indica la base su cui eseguire 'query_filtro'. Deve essere usata solo insieme a 'query_filtro'
        'query_livello' (con valore 'SUB' oppure 'LIVELLO') -> indica il livello di esecuziones della query
        Eventuali ',' presenti in 'query_base' o in 'query_filtro' devono essere sostituite con ';'
        I valori di default delle chiavi speciali sono:
        query_and_or: AND
        query_filtro: None
        query_livello: SUB
        query_base: la base definita nel reader del tipo di oggetto
        Per eseguire un AND o un OR nello stesso campo far precedere il campo dal segno '&' oppure '|' e
        dividere le chiavi multiple con ';'
        Il default dei campi con valori di ricerca combinati e' in OR
        Se e' presente un '!' prima di una chiave di ricerca questa viene eseguita in NOT.
        """

        if self.query and self.query.startswith('(') and self.query.stopswith(')'):
            self.queryFilter = self.query
            return

        self.queryFilter = ''

        if self.definition.objectClass:
            self.queryFilter += '(&(objectClass=' + self.definition.objectClass + ')'

        if not self.componentsInAnd:
            self.queryFilter += '(|'
        elif not self.definition.objectClass:
            self.queryFilter += '(&'

        if not self._validatedQueryDict:
            self._validateQuery()

        attrCounter = 0
        for attr in sorted(self._validatedQueryDict):
            attrCounter += 1
            multi = True if ';' in self._validatedQueryDict[attr] else False
            vals = sorted(self._validatedQueryDict[attr].split(';'))
            attrDef = self.definition[attr[1:]] if attr[0] in '&|' else self.definition[attr]
            if attrDef.preQuery:
                modvals = []
                for val in vals:
                    modvals.append(val[0] + attrDef.preQuery(attr, val[1:]))
                vals = modvals
            if multi:
                if attr[0] in '&|':
                    self.queryFilter += '(' + attr[0]
                else:
                    self.queryFilter += '(|'

            for val in vals:
                if val[0] == '!':
                    self.queryFilter += '(!(' + attrDef.name + _retSearchValue(val[1:]) + '))'
                else:
                    self.queryFilter += '(' + attrDef.name + _retSearchValue(val) + ')'
            if multi:
                self.queryFilter += ')'

        if not self.componentsInAnd:
            self.queryFilter += '))'
        else:
            self.queryFilter += ')'

        if not self.definition.objectClass and attrCounter == 1:  # remove unneeded starting filter
            self.queryFilter = self.queryFilter[2:-1]

    def _getAttributeValues(self, result, attrDefs):
        """
        Assegna il risultato della query LDAP al dizionario 'valori' dell'oggetto.
        Se e' presente una funzione di 'postQuery' questa viene eseguita sulla lista dei valori trovato e il risultato
        della funzione viene ritornato nell'attributo relativo.
        Fa in modo che se un attributo richiesto e' assente questo venga inserito nei valori con il valore di default
        Se dereferencedObjectDef != None tenta di recuperare da ldap l'oggetto di tipo dereferenceObjectDef memorizzato nel value
        """
        values = dict()
        for attrDef in attrDefs:
            name = None
            for attrName in result['attributes']:
                if attrDef.name.lower() == attrName.lower():
                    name = attrName
                    break

            if name:
                attribute = Attribute(attrDef.key, attrDef, self)
                if not attrDef.dereferencedObjectDef:
                    if attrDef.postQuery and attrDef.name in result['attributes']:
                        if attrDef.postQueryReturnsList:
                            attribute.__dict__['values'] = attrDef.postQuery(result['attributes'][name]) or attrDef.default
                        else:
                            attribute.__dict__['values'] = [attrDef.postQuery(value) for value in result['attributes'][name]]
                    else:
                        attribute.__dict__['values'] = result['attributes'][name] or attrDef.default
                else:  # try to get object referenced in value
                    attribute.__dict__['values'] = result['attributes'][name] or attrDef.default
                    if attribute.values:
                        tempReader = Reader(self.connection, attrDef.dereferencedObjectDef, query = None, base = None, getOperationalAttributes = self.getOperationalAttributes, controls = self.controls, noSingleValueList = self.noSingleValueList)
                        tempValues = []

                        for element in attribute.values:
                            tempReader.base = element
                            tempValues.append(tempReader.searchObject())
                        del tempReader
                        attribute.__dict__['values'] = tempValues

                values[attribute.key] = attribute

        return values

    def _getEntry(self, result):
        if not result['type'] == 'searchResEntry':
            return None

        entry = Entry(result['dn'], self)
        entry.__dict__['_attributes'] = self._getAttributeValues(result, self.definition)
        entry.__dict__['_rawAttributes'] = result['rawAttributes']
        for attr in entry:
            attrName = attr.key
            entry.__dict__[attrName] = attr.values

        return entry

    def _executeQuery(self, queryScope):
        if not self.connection:
            raise Exception('No connection available')

        self._createQueryFilter()

        result = self.connection.search(searchBase = self.base,
                                         searchFilter = self.queryFilter,
                                         searchScope = queryScope,
                                         dereferenceAliases = self.dereferenceAliases,
                                         attributes = self.attributes,
                                         sizeLimit = self.sizeLimit,
                                         timeLimit = self.timeLimit,
                                         typesOnly  = self.typesOnly,
                                         getOperationalAttributes = self.getOperationalAttributes,
                                         controls = self.controls,
                                         pagedSize = self.pagedSize,
                                         pagedCriticality = self.pagedCriticality,
                                         pagedCookie = self.pagedCookie)

        if not self.connection.strategy.sync:
            response = self.connection.getResponse(result)
            if len(response) > 1:
                response = response[:-1]
        else:
            response = self.connection.response

        self.entries = []
        for r in response:
            entry = self._getEntry(r)
            self.entries.append(entry)

        self.lastSubTree = self.subTree
        self.executionTime = datetime.now()

    def search(self):
        self.clear()
        queryScope = SEARCH_SCOPE_WHOLE_SUBTREE if self.subTree else SEARCH_SCOPE_SINGLE_LEVEL
        self._executeQuery(queryScope)

        return self.entries

    def searchLevel(self):
        self.clear()
        self._executeQuery(SEARCH_SCOPE_SINGLE_LEVEL)

        return self.entries

    def searchSubtree(self):
        self.clear()
        self._executeQuery(SEARCH_SCOPE_WHOLE_SUBTREE)

        return self.entries

    def searchObject(self):  # base must be a single dn
        self.clear()
        self._executeQuery(SEARCH_SCOPE_BASE_OBJECT)
        return self.entries[0]

    def searchSizeLimit(self, sizeLimit):
        self.clear()
        self.sizeLimit = sizeLimit
        queryScope = SEARCH_SCOPE_WHOLE_SUBTREE if self.subTree else SEARCH_SCOPE_SINGLE_LEVEL
        self._executeQuery(queryScope)

        return self.entries

    def searchTimeLimit(self, TimeLimit):
        self.clear()
        self.TimeLimit = TimeLimit
        queryScope = SEARCH_SCOPE_WHOLE_SUBTREE if self.subTree else SEARCH_SCOPE_SINGLE_LEVEL
        self._executeQuery(queryScope)

        return self.entries

    def searchTypesOnly(self):
        self.clear()
        self.typesOnly = True
        queryScope = SEARCH_SCOPE_WHOLE_SUBTREE if self.subTree else SEARCH_SCOPE_SINGLE_LEVEL
        self._executeQuery(queryScope)

        return self.entries

    def searchPaged(self, pagedSize, pagedCriticality = True):
        if not self.pagedCookie:
            self.clear()

        self.pagedSize = pagedSize
        self.pagedCriticality = pagedCriticality
        queryScope = SEARCH_SCOPE_WHOLE_SUBTREE if self.subTree else SEARCH_SCOPE_SINGLE_LEVEL

        self._executeQuery(queryScope)

        if self.entries:
            yield self.entries
        else:
            raise StopIteration
