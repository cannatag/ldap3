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

def _retSearchValue(value):
    return value[0] + '=' + value[1:] if value[0] in '<>~' and value[1] != '=' else value


def _createQueryDict(self, text):
    """
    crea un dizionario con le coppie chiave:valore di una query
    Il testo della query deve essere composto da coppie chiave:valore separate dalla virgola.
    """
    queryDict = dict()
    for argValueStr in text.split(','):
        if ':' in argValueStr:
            argValueList = argValueStr.split(':')
            queryDict[argValueList[0].strip()] = argValueList[1].strip()

    return queryDict


class Reader(object):
    def __init__(self, connection, objectDef, query, queryBase, queryScope = SCOP):
        self.connection = connection
        self.query = query
        self.definition = objectDef
        self.base = queryBase
        self.scope

    def _validateQueryText(self, text):
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

        queryDict = _createQueryDict(text)
        query = ''
        for d in sorted(queryDict):
            attr = d[1:] if d[0] in '&|' else d

            if attr.lower() not in ['query_and_or', 'query_filter', 'query_base', 'query_scope']:
                for attrDef in self.definition:
                    if attr.lower() == attrDef.lower():
                        attr = attrDef
                        break

                if attr in self.definition:
                    vals = queryDict[d].split(';')

                    query += d[0] + attr if d[0] in '&|' else attr
                    query += ': '
                    for val in vals:
                        val = val.strip()
                        valNot = True if val[0] == '!' else False
                        if valNot:
                            valSearchOperator = val[1:].lstrip()[0]
                            value = val[1:].lstrip()[1:]
                        else:
                            valSearchOperator = val[0]
                            value = val[1:].lstrip()

                        if valSearchOperator not in '=<>~':
                            raise Exception('invalid operator, must be one of =, <, > or ~')

                        if self.definition[attr].validate:
                            if not self.definition[attr].validate(value):
                                raise Exception('validation failed for attribute %s with value %s' % (val, queryDict[d]))

                        if valNot:
                            query += '!' + valSearchOperator + value
                        else:
                            query += valSearchOperator + value

                        query += ';'
                    query = query[:-1]
                    query += ', '
            else:
                if attr.lower() == 'query_and_or':
                    if queryDict[d].lower() in ['and', 'or']:
                        query += 'query_and_or: ' + queryDict[d].lower() + ', '
                elif attr.lower() == 'query_filter':
                    query += 'query_filter: ' + queryDict[d] + ', '
                elif attr.lower() == 'query_base':
                    query += 'query_base: ' + queryDict[d] + ', '
                elif attr.lower() == 'query_scope':
                    if queryDict[d].lower() in ['sub', 'level']:
                        query += 'query_scope: ' + queryDict[d].lower() + ', '

        return query[:-2]

    def _createQueryFilter(self, queryDict):
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
        if self.definition.objectClass:
            ldapFilter = '(&(objectClass=' + self.definition.objectClass + ')'

        if 'query_and_or' in queryDict and queryDict['query_and_or'] == 'or':
            ldapFilter += '(|'
        elif not self.definition.objectClass:
            ldapFilter = '(&'

        attrCounter = 0
        for attr in queryDict:
            if attr not in ['query_and_or', 'query_filter', 'query_scope', 'query_base']:
                attrCounter += 1
                multi = True if ';' in queryDict[attr] else False
                vals = queryDict[attr].split(';')
                attrDef = self.definition.attributes[attr[1:]] if attr[0] in '&|' else self.definition.attributes[attr]
                if multi:
                    if attr[0] in '&|':
                        ldapFilter += '(' + attr[0]
                    else:
                        ldapFilter += '(|'
                if attrDef.preQuery:
                    if multi:
                        for val in vals:
                            ldapFilter += '(' + attrDef.preQuery(attr, val) + ')'
                    else:
                        ldapFilter += '(' + attrDef.preQuery(attr, queryDict[attr]) + ')'
                else:
                    for val in vals:
                        if val[0] == '!':
                            ldapFilter += '(!(' + attrDef.name + _retSearchValue(val[1:]) + '))'
                        else:
                            ldapFilter += '(' + attrDef.name + _retSearchValue(val) + ')'
                if multi:
                    ldapFilter += ')'
            elif attr == 'query_filter':
                ldapFilter += queryDict['query_filter'].replace(';', ',')

        if 'query_and_or' in queryDict and queryDict['query_and_or'] == 'or':
            ldapFilter += '))'
        else:
            ldapFilter += ')'

        if not self.definition.objectClass and attrCounter == 1:  # remove unneeded starting filter
            ldapFilter = ldapFilter[2:-1]
        return ldapFilter
