"""
"""

# Created on 2013.07.24
#
# Author: Giovanni Cannata
#
# Copyright 2013, 2014, 2015, 2016, 2017 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from .. import SEQUENCE_TYPES, STRING_TYPES, get_config_parameter
from ..core.exceptions import LDAPControlError, LDAPAttributeError, LDAPObjectClassError
from ..protocol.rfc4511 import Controls, Control
from ..utils.conv import to_raw, to_unicode, escape_filter_chars, is_filter_escaped


def attribute_to_dict(attribute):
    return {'type': str(attribute['type']), 'values': [str(val) for val in attribute['vals']]}


def attributes_to_dict(attributes):
    attributes_dict = dict()
    for attribute in attributes:
        attribute_dict = attribute_to_dict(attribute)
        attributes_dict[attribute_dict['type']] = attribute_dict['values']
    return attributes_dict


def referrals_to_list(referrals):
    return [str(referral) for referral in referrals if referral] if referrals else None


def search_refs_to_list(search_refs):
    return [str(search_ref) for search_ref in search_refs if search_ref] if search_refs else None


def sasl_to_dict(sasl):
    return {'mechanism': str(sasl['mechanism']), 'credentials': str(sasl['credentials'])}


def authentication_choice_to_dict(authentication_choice):
    return {'simple': str(authentication_choice['simple']) if authentication_choice.getName() == 'simple' else None, 'sasl': sasl_to_dict(authentication_choice['sasl']) if authentication_choice.getName() == 'sasl' else None}


def decode_referrals(referrals):
    return [str(referral) for referral in referrals if referral] if referrals else None


def partial_attribute_to_dict(modification):
    return {'type': str(modification['type']), 'value': [str(value) for value in modification['vals']]}


def change_to_dict(change):
    return {'operation': int(change['operation']), 'attribute': partial_attribute_to_dict(change['modification'])}


def changes_to_list(changes):
    return [change_to_dict(change) for change in changes]


def attributes_to_list(attributes):
    return [str(attribute) for attribute in attributes]


def ava_to_dict(ava):
    return {'attribute': str(ava['attributeDesc']), 'value': str(ava['assertionValue'])}


def substring_to_dict(substring):
    return {'initial': substring['initial'] if substring['initial'] else '', 'any': [middle for middle in substring['any']] if substring['any'] else '', 'final': substring['final'] if substring['final'] else ''}


def prepare_changes_for_request(changes):
    prepared = dict()
    for change in changes:
        prepared[change['attribute']['type']] = (change['operation'], change['attribute']['value'])
    return prepared


def build_controls_list(controls):
    """
    controls is a list of Control() or tuples
    each tuple must have 3 elements: the control OID, the criticality, the value
    criticality must be a boolean
    """
    if not controls:
        return None

    if not isinstance(controls, SEQUENCE_TYPES):
        raise LDAPControlError('controls must be a sequence')

    built_controls = Controls()
    for idx, control in enumerate(controls):
        if isinstance(control, Control):
            built_controls.setComponentByPosition(idx, control)
        elif len(control) == 3 and isinstance(control[1], bool):
            built_control = Control()
            built_control['controlType'] = control[0]
            built_control['criticality'] = control[1]
            if control[2] is not None:
                built_control['controlValue'] = control[2]
            built_controls.setComponentByPosition(idx, built_control)
        else:
            raise LDAPControlError('control must be a tuple of 3 elements: controlType, criticality (boolean) and controlValue (None if not provided)')

    return built_controls


def validate_assertion_value(schema, name, value, auto_escape, auto_encode):
    value = to_unicode(value)
    if auto_escape:
        if '\\' in value and not is_filter_escaped(value):
            value = escape_filter_chars(value)
    value = validate_attribute_value(schema, name, value, auto_encode)
    return value


def validate_attribute_value(schema, name, value, auto_encode):
    if schema:
        if ';' in name:
            name = name.split(';')[0]

        if schema.object_classes is not None and name == 'objectClass':
            if value not in get_config_parameter('CLASSES_EXCLUDED_FROM_CHECK') and value not in schema.object_classes:
                raise LDAPObjectClassError('invalid class in objectClass attribute: ' + value)

        if schema.attribute_types is not None:
            if name not in schema.attribute_types and name not in get_config_parameter('ATTRIBUTES_EXCLUDED_FROM_CHECK'):
                raise LDAPAttributeError('invalid attribute ' + name)

            # encodes to utf-8 for well known Unicode LDAP syntaxes
            if auto_encode and (schema.attribute_types[name].syntax in get_config_parameter('UTF8_ENCODED_SYNTAXES') or name in get_config_parameter('UTF8_ENCODED_TYPES')):
                value = to_unicode(value)  # tries to convert from local encoding to Unicode

    return to_raw(value)


def prepare_filter_for_sending(raw_string):
    i = 0
    ints = []
    raw_string = to_raw(raw_string)
    while i < len(raw_string):
        if (raw_string[i] == 92 or raw_string[i] == '\\') and i < len(raw_string) - 2:  # 92 is backslash
            try:
                ints.append(int(raw_string[i + 1: i + 3], 16))
                i += 2
            except ValueError:  # not an ldap escaped value, sends as is
                ints.append(92)  # adds backslash
        else:
            if str is not bytes:  # Python 3
                ints.append(raw_string[i])
            else:  # Python 2
                ints.append(ord(raw_string[i]))
        i += 1

    if str is not bytes:  # Python 3
        return bytes(ints)
    else:  # Python 2
        return ''.join(chr(x) for x in ints)


def prepare_for_sending(raw_string):
    return to_raw(raw_string) if isinstance(raw_string, STRING_TYPES) else raw_string
