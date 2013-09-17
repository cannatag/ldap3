"""
Created on 2013.07.24

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

from ldap3.protocol.rfc4511 import Controls, Control


def attributeToDict(attribute):
    return {'type': str(attribute['type']),
            'values': [str(val) for val in attribute['vals']]
    }


def attributesToDict(attributes):
    attributesDict = dict()
    for attribute in attributes:
        attributeDict = attributeToDict(attribute)
        attributesDict[attributeDict['type']] = attributeDict['values']

    return attributesDict


def referralsToList(referrals):
    if referrals:
        return [str(referral) for referral in referrals if referral]
    else:
        return None


def searchRefsToList(searchRefs):
    if searchRefs:
        return [str(searchRef) for searchRef in searchRefs if searchRef]
    else:
        return None


def saslToDict(sasl):
    return {'mechanism': str(sasl['mechanism']),
            'credentials': str(sasl['credentials'])
    }


def authenticationChoiceToDict(authenticationChoice):
    return {'simple': str(authenticationChoice['simple']) if authenticationChoice.getName() == 'simple' else None,
            'sasl': saslToDict(authenticationChoice['sasl']) if authenticationChoice.getName() == 'sasl' else None
    }


def decodeReferrals(referrals):
    if referrals:
        return [str(referral) for referral in referrals if referral]
    else:
        return None


def partialAttributeToDict(modification):
    return {
        'type': str(modification['type']),
        'value': [str(value) for value in modification['vals']]
    }


def changeToDict(change):
    return {
        'operation': int(change['operation']),
        'attribute': partialAttributeToDict(change['modification'])
    }


def changesToList(changes):
    return [changeToDict(change) for change in changes]


def attributesToList(attributes):
    return [str(attribute) for attribute in attributes]


def avaToDict(ava):
    return {
        'attribute': str(ava['attributeDesc']),
        'value': str(ava['assertionValue'])
    }


def substringToDict(substring):
    return {
        'initial': substring['initial'] if substring['initial'] else '',
        'any': [middle for middle in substring['any']] if substring['any'] else '',
        'final': substring['final'] if substring['final'] else ''
    }


def prepareChangesForRequest(changes):
    prepared = {}
    for change in changes:
        prepared[change['attribute']['type']] = (change['operation'], change['attribute']['value'])

    return prepared


def buildControlsList(controls):
    """
    controls is a list of tuple
    each tuple must have 3 elements: the control OID, the criticality, the value
    criticality must be a boolean
    """
    if not controls:
        return None

    if not isinstance(controls, list):
        raise Exception('controls must be a list')

    builtControls = Controls()
    for idx, control in enumerate(controls):
        if len(control) == 3 and isinstance(control[1], bool):
            builtControl = Control()
            builtControl['controlType'] = control[0]
            builtControl['criticality'] = control[1]
            builtControl['controlValue'] = control[2]
            builtControls.setComponentByPosition(idx, builtControl)
        else:
            raise Exception('control must be a list of 3 elements: controlType, criticality (boolean) and controlValue')

    return builtControls
