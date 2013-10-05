"""
Created on 2013.06.02

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

from string import whitespace
from os import linesep

from ldap3 import SEARCH_NEVER_DEREFERENCE_ALIASES, SEARCH_SCOPE_BASE_OBJECT, SEARCH_SCOPE_SINGLE_LEVEL, SEARCH_SCOPE_WHOLE_SUBTREE, SEARCH_DEREFERENCE_IN_SEARCHING, SEARCH_DEREFERENCE_FINDING_BASE_OBJECT, SEARCH_DEREFERENCE_ALWAYS, NO_ATTRIBUTES
from ldap3.protocol.rfc4511 import SearchRequest, LDAPDN, Scope, DerefAliases, Integer0ToMax, TypesOnly, AttributeSelection, Selector, EqualityMatch, AttributeDescription, AssertionValue, Filter, Not, And, Or, ApproxMatch, GreaterOrEqual, LessOrEqual, ExtensibleMatch, Present, SubstringFilter, Substrings, Final, Initial, Any, ResultCode, Substring, MatchingRule, Type, MatchValue, DnAttributes
from ldap3.operation.bind import referralsToList
from ldap3.protocol.convert import avaToDict, attributesToList, searchRefsToList



# SearchRequest ::= [APPLICATION 3] SEQUENCE {
#     baseObject      LDAPDN,
#     scope           ENUMERATED {
#         baseObject              (0),
#         singleLevel             (1),
#         wholeSubtree            (2),
#     ...  },
#     derefAliases    ENUMERATED {
#         neverDerefAliases       (0),
#         derefInSearching        (1),
#         derefFindingBaseObj     (2),
#         derefAlways             (3) },
#     sizeLimit       INTEGER (0 ..  maxInt),
#     timeLimit       INTEGER (0 ..  maxInt),
#     typesOnly       BOOLEAN,
#     filter          Filter,
#     attributes      AttributeSelection }

ROOT = 0
AND = 1
OR = 2
NOT = 3
MATCH_APPROX = 4
MATCH_GREATER_OR_EQUAL = 5
MATCH_LESS_OR_EQUAL = 6
MATCH_EXTENSIBLE = 7
MATCH_PRESENT = 8
MATCH_SUBSTRING = 9
MATCH_EQUAL = 10

SEARCH_OPEN = 11
SEARCH_OPEN_OR_CLOSE = 12
SEARCH_MATCH_OR_CLOSE = 13
SEARCH_MATCH_OR_CONTROL = 14


class FilterNode():
    def __init__(self, tag = None, assertion = None):
        self.tag = tag
        self.parent = None
        self.assertion = assertion
        self.elements = []

    def append(self, filterNode):
        filterNode.parent = self
        self.elements.append(filterNode)
        return filterNode

    def __str__(self, pos = 0):
        self.__repr__(pos)

    def __repr__(self, pos = 0):
        nodetags = ['ROOT', 'AND', 'OR', 'NOT', 'MATCH_APPROX', 'MATCH_GREATER_OR_EQUAL', 'MATCH_LESS_OR_EQUAL', 'MATCH_EXTENSIBLE', 'MATCH_PRESENT',
                    'MATCH_SUBSTRING', 'MATCH_EQUAL']
        representation = ' ' * pos + 'tag: ' + nodetags[self.tag] + ' - assertion: ' + str(self.assertion)
        if self.elements:
            representation += ' - elements: ' + str(len(self.elements))
            for element in self.elements:
                representation += linesep
                representation += ' ' * pos + element.__repr__(pos + 2)

        return representation


def validateAssertionValue(value):
    value = value.strip()
    value.replace('\\2a', '*')
    value.replace('\\2A', '*')
    value.replace('\\28', '(')
    value.replace('\\29', ')')
    value.replace('\\5c', '\\')
    value.replace('\\5C', '\\')
    value.replace('\\00', chr(0))
    return value


def evaluateMatch(match):
    match = match.strip()
    if '~=' in match:
        tag = MATCH_APPROX
        leftPart, _, rightPart = match.split('~=')
        assertion = {'attr': leftPart.strip(), 'value': validateAssertionValue(rightPart)}
    elif '>=' in match:
        tag = MATCH_GREATER_OR_EQUAL
        leftPart, _, rightPart = match.partition('>=')
        assertion = {'attr': leftPart.strip(), 'value': validateAssertionValue(rightPart)}
    elif '<=' in match:
        tag = MATCH_LESS_OR_EQUAL
        leftPart, _, rightPart = match.partition('>=')

        assertion = {'attr': leftPart.strip(), 'value': validateAssertionValue(rightPart)}
    elif ':=' in match:
        tag = MATCH_EXTENSIBLE
        leftPart, _, rightPart = match.partition(':=')
        extendedFilterList = leftPart.split(':')
        matchingRule = None
        dnAttributes = None
        attributeName = None
        if extendedFilterList[0] == '':  # extensible filter format [:dn]:matchingRule:=assertionValue
            if len(extendedFilterList) == 2 and extendedFilterList[1].lower().strip() != 'dn':
                matchingRule = extendedFilterList[1].strip()
            elif len(extendedFilterList) == 3 and extendedFilterList[1].lower().strip() == 'dn':
                dnAttributes = True
                matchingRule = extendedFilterList[2].strip()
            else:
                raise Exception('invalid extensible filter')
        elif len(extendedFilterList) <= 3: # extensible filter format attr[:dn][:matchingRule]:=assertionValue
            if len(extendedFilterList) == 1:
                attributeName = extendedFilterList[0]
            elif len(extendedFilterList) == 2:
                attributeName = extendedFilterList[0]
                if extendedFilterList[1].lower().strip() == 'dn':
                    dnAttributes = True
                else:
                    matchingRule = extendedFilterList[1].strip()
            elif len(extendedFilterList) == 3 and extendedFilterList[1].lower().strip() == 'dn':
                attributeName = extendedFilterList[0]
                dnAttributes = True
                matchingRule = extendedFilterList[2].strip()
            else:
                raise Exception('invalid extensible filter')

        if not attributeName and not matchingRule:
            raise Exception('invalid extensible filter')

        assertion = {'attr': attributeName.strip() if attributeName else None, 'value': validateAssertionValue(rightPart),
                     'matchingRule': matchingRule.strip() if matchingRule else None, 'dnAttributes': dnAttributes}
    elif match.endswith('=*'):
        tag = MATCH_PRESENT
        assertion = {'attr': match[:-2]}
    elif '=' in match and '*' in match:
        tag = MATCH_SUBSTRING
        leftPart, _, rightPart = match.partition('=')
        substrings = rightPart.split('*')
        initial = substrings[0] if substrings[0] else None
        final = substrings[-1] if substrings[-1] else None
        anyString = [substring for substring in substrings[1:-1] if substring]
        assertion = {'attr': leftPart, 'initial': initial, 'any': anyString, 'final': final}
    elif '=' in match:
        tag = MATCH_EQUAL
        leftPart, _, rightPart = match.partition('=')
        assertion = {'attr': leftPart.strip(), 'value': validateAssertionValue(rightPart)}
    else:
        raise Exception('invalid matching assertion')

    return FilterNode(tag, assertion)


def parseFilter(searchFilter):
    searchFilter = searchFilter.strip()
    if searchFilter and searchFilter.count('(') == searchFilter.count(')') and searchFilter.startswith('(') and searchFilter.endswith(')'):
        state = SEARCH_OPEN_OR_CLOSE
        root = FilterNode(ROOT)
        currentNode = root
        startPos = None
        skipWhiteSpace = True
        justClosed = False
        for pos, c in enumerate(searchFilter):
            if skipWhiteSpace and c in whitespace:
                pass
            elif (state == SEARCH_OPEN or state == SEARCH_OPEN_OR_CLOSE) and c == '(':
                state = SEARCH_MATCH_OR_CONTROL
                justClosed = False
            elif state == SEARCH_MATCH_OR_CONTROL and c in '&!|':
                if c == '&':
                    currentNode = currentNode.append(FilterNode(AND))
                elif c == '|':
                    currentNode = currentNode.append(FilterNode(OR))
                elif c == '!':
                    currentNode = currentNode.append(FilterNode(NOT))
                state = SEARCH_OPEN
            elif (state == SEARCH_MATCH_OR_CLOSE or state == SEARCH_OPEN_OR_CLOSE) and c == ')':
                if justClosed:
                    currentNode = currentNode.parent
                else:
                    justClosed = True
                    skipWhiteSpace = True
                    endPos = pos
                    if startPos:
                        if currentNode.tag == NOT and len(currentNode.elements) > 0:
                            raise Exception('Not clause in filter cannot be multiple')
                        currentNode.append(evaluateMatch(searchFilter[startPos:endPos]))
                startPos = None
                state = SEARCH_OPEN_OR_CLOSE
            elif (state == SEARCH_MATCH_OR_CLOSE or state == SEARCH_MATCH_OR_CONTROL) and c not in '()':
                skipWhiteSpace = False
                if not startPos:
                    startPos = pos
                state = SEARCH_MATCH_OR_CLOSE
            else:
                raise Exception('malformed filter')
        if len(root.elements) != 1:
            raise Exception('missing boolean operator in filter')
        return root
    else:
        raise Exception('invalid filter')


def compileFilter(filterNode):
    compiledFilter = Filter()
    if filterNode.tag == AND:
        booleanFilter = And()
        pos = 0
        for element in filterNode.elements:
            booleanFilter[pos] = compileFilter(element)
            pos += 1
        compiledFilter['and'] = booleanFilter
    elif filterNode.tag == OR:
        booleanFilter = Or()
        pos = 0
        for element in filterNode.elements:
            booleanFilter[pos] = compileFilter(element)
            pos += 1
        compiledFilter['or'] = booleanFilter
    elif filterNode.tag == NOT:
        booleanFilter = Not()
        booleanFilter['innerNotFilter'] = compileFilter(filterNode.elements[0])
        compiledFilter['notFilter'] = booleanFilter
    elif filterNode.tag == MATCH_APPROX:
        matchingFilter = ApproxMatch()
        matchingFilter['attributeDesc'] = AttributeDescription(filterNode.assertion['attr'])
        matchingFilter['assertionValue'] = AssertionValue(filterNode.assertion['value'])
        compiledFilter['approxMatch'] = matchingFilter
    elif filterNode.tag == MATCH_GREATER_OR_EQUAL:
        matchingFilter = GreaterOrEqual()
        matchingFilter['attributeDesc'] = AttributeDescription(filterNode.assertion['attr'])
        matchingFilter['assertionValue'] = AssertionValue(filterNode.assertion['value'])
        compiledFilter['greaterOrEqual'] = matchingFilter
    elif filterNode.tag == MATCH_LESS_OR_EQUAL:
        matchingFilter = LessOrEqual()
        matchingFilter['attributeDesc'] = AttributeDescription(filterNode.assertion['attr'])
        matchingFilter['assertionValue'] = AssertionValue(filterNode.assertion['value'])
        compiledFilter['lessOrEqual'] = matchingFilter
    elif filterNode.tag == MATCH_EXTENSIBLE:
        matchingFilter = ExtensibleMatch()
        if filterNode.assertion['matchingRule']:
            matchingFilter['matchingRule'] = MatchingRule(filterNode.assertion['matchingRule'])
        if filterNode.assertion['attr']:
            matchingFilter['type'] = Type(filterNode.assertion['attr'])
        matchingFilter['matchValue'] = MatchValue(filterNode.assertion['value'])
        matchingFilter['dnAttributes'] = DnAttributes(filterNode.assertion['dnAttributes'])
        compiledFilter['extensibleMatch'] = matchingFilter
    elif filterNode.tag == MATCH_PRESENT:
        matchingFilter = Present(AttributeDescription(filterNode.assertion['attr']))
        compiledFilter['present'] = matchingFilter
    elif filterNode.tag == MATCH_SUBSTRING:
        matchingFilter = SubstringFilter()
        matchingFilter['type'] = AttributeDescription(filterNode.assertion['attr'])
        substrings = Substrings()
        pos = 0
        if filterNode.assertion['initial']:
            substrings[pos] = Substring().setComponentByName('initial', Initial(filterNode.assertion['initial']))
            pos += 1
        if filterNode.assertion['any']:
            for substring in filterNode.assertion['any']:
                substrings[pos] = Substring().setComponentByName('any', Any(substring))
                pos += 1
        if filterNode.assertion['final']:
            substrings[pos] = Substring().setComponentByName('final', Final(filterNode.assertion['final']))
        matchingFilter['substrings'] = substrings
        compiledFilter['substringFilter'] = matchingFilter
    elif filterNode.tag == MATCH_EQUAL:
        matchingFilter = EqualityMatch()
        matchingFilter['attributeDesc'] = AttributeDescription(filterNode.assertion['attr'])
        matchingFilter['assertionValue'] = AssertionValue(filterNode.assertion['value'])
        compiledFilter.setComponentByName('equalityMatch', matchingFilter)
    else:
        raise Exception('unknown filter')

    return compiledFilter


def buildFilter(searchFilter):
    parsedFilter = parseFilter(searchFilter)
    return compileFilter(parsedFilter.elements[0])


def buildAttributeSelection(attributeList):
    attributeSelection = AttributeSelection()
    for index, attribute in enumerate(attributeList):
        attributeSelection[index] = Selector(attribute)

    return attributeSelection


def searchOperation(searchBase, searchFilter, searchScope, dereferenceAliases, attributes, sizeLimit, timeLimit, typesOnly):
    request = SearchRequest()
    request['baseObject'] = LDAPDN(searchBase)

    if searchScope == SEARCH_SCOPE_BASE_OBJECT:
        request['scope'] = Scope('baseObject')
    elif searchScope == SEARCH_SCOPE_SINGLE_LEVEL:
        request['scope'] = Scope('singleLevel')
    elif searchScope == SEARCH_SCOPE_WHOLE_SUBTREE:
        request['scope'] = Scope('wholeSubtree')
    else:
        raise Exception('invalid scope type')

    if dereferenceAliases == SEARCH_NEVER_DEREFERENCE_ALIASES:
        request['derefAliases'] = DerefAliases('neverDerefAliases')
    elif dereferenceAliases == SEARCH_DEREFERENCE_IN_SEARCHING:
        request['derefAliases'] = DerefAliases('derefInSearching')
    elif dereferenceAliases == SEARCH_DEREFERENCE_FINDING_BASE_OBJECT:
        request['derefAliases'] = DerefAliases('derefFindingBaseObj')
    elif dereferenceAliases == SEARCH_DEREFERENCE_ALWAYS:
        request['derefAliases'] = DerefAliases('derefAlways')
    else:
        raise Exception('invalid dereference aliases type')

    request['sizeLimit'] = Integer0ToMax(sizeLimit)
    request['timeLimit'] = Integer0ToMax(timeLimit)
    request['typesOnly'] = TypesOnly(True) if typesOnly else TypesOnly(False)
    request['filter'] = buildFilter(searchFilter)

    if not isinstance(attributes, list):
        attributes = [NO_ATTRIBUTES]

    request['attributes'] = buildAttributeSelection(attributes)

    return request


def decodeVals(vals):
    if vals:
        return [str(val) for val in vals if val]
    else:
        return None


def attributesToDict(attributeList):
    attributes = dict()
    for attribute in attributeList:
        attributes[str(attribute['type'])] = decodeVals(attribute['vals'])

    return attributes


def decodeRawVals(vals):
    if vals:
        return [bytes(val) for val in vals if val]
    else:
        return None


def rawAttributesToDict(attributeList):
    attributes = dict()
    for attribute in attributeList:
        attributes[str(attribute['type'])] = decodeRawVals(attribute['vals'])

    return attributes


def matchingRuleAssertionToString(matchingRuleAssertion):
    return str(matchingRuleAssertion)


def filterToString(filterObject):
    filterType = filterObject.getName()
    filterString = '('
    if filterType == 'and':
        filterString += '&'
        for f in filterObject['and']:
            filterString += filterToString(f)
    elif filterType == 'or':
        filterString += '!'
        for f in filterObject['or']:
            filterString += filterToString(f)
    elif filterType == 'notFilter':
        filterString += '!' + filterToString(filterObject['notFilter']['innerNotFilter'])
    elif filterType == 'equalityMatch':
        ava = avaToDict(filterObject['equalityMatch'])
        filterString += ava['attribute'] + '=' + ava['value']
    elif filterType == 'substringFilter':
        attribute = filterObject['substringFilter']['type']
        filterString += str(attribute) + '='
        for substring in filterObject['substringFilter']['substrings']:
            if substring['initial']:
                filterString += str(substring['initial']) + '*'
            elif substring['any']:
                filterString += str(substring['any']) if filterString.endswith('*') else '*' + str(substring['any'])
                filterString += '*'
            elif substring['final']:
                filterString += '*' + str(substring['final'])
    elif filterType == 'greaterOrEqual':
        ava = avaToDict(filterObject['greaterOrEqual'])
        filterString += ava['attribute'] + '>=' + ava['value']
    elif filterType == 'lessOrEqual':
        ava = avaToDict(filterObject['lessOrEqual'])
        filterString += ava['attribute'] + '<=' + ava['value']
    elif filterType == 'present':
        filterString += str(filterObject['present']) + '=*'
    elif filterType == 'approxMatch':
        ava = avaToDict(filterObject['approxMatch'])
        filterString += ava['attribute'] + '~=' + ava['value']
    elif filterType == 'extensibleMatch':
        filterString += matchingRuleAssertionToString(filterObject['extensibleMatch'])
    else:
        raise Exception('error converting filter to string')

    filterString += ')'
    return filterString


def searchRequestToDict(request):
    return {'base': str(request['baseObject']), 'scope': int(request['scope']), 'dereferenceAlias': int(request['derefAliases']),
            'sizeLimit': int(request['sizeLimit']), 'timeLimit': int(request['timeLimit']), 'typeOnly': bool(request['typesOnly']),
            'filter': filterToString(request['filter']), 'attributes': attributesToList(request['attributes'])}


def searchResultEntryResponseToDict(response):
    return {'dn': str(response['object']), 'attributes': attributesToDict(response['attributes']), 'rawAttributes': rawAttributesToDict(response['attributes'])}


def searchResultDoneResponseToDict(response):
    return {'result': int(response[0]), 'description': ResultCode().getNamedValues().getName(response[0]), 'message': str(response['diagnosticMessage']),
            'dn': str(response['matchedDN']), 'referrals': referralsToList(response['referral'])}


def searchResultReferenceResponseToDict(response):
    return {'uri': searchRefsToList(response)}
