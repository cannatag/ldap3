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


class Reader(object):
    def __init__(self, connection, objectDef, query):
        self.connection = connection
        self.query = query
        self.definition = objectDef

    def _creaDict(self, text):
        '''
        crea un dizionario con le coppie chiave:valore di una query
        Il testo della query deve essere composto da coppie chiave:valore separate dalla virgola.
        '''
        queryDict = dict()
        for argValueStr in text.split(','):
            if ':' in argValueStr:
                argValueList = argValueStr.split(':')
                queryDict[argValueList[0].strip()] = argValueList[1].strip()

        return queryDict

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

        queryDict = self._creaDict(text)
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
