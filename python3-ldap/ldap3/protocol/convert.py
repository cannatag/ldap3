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
from uuid import UUID
from ..core.exceptions import LDAPControlsError, LDAPAttributeError, LDAPObjectClassError
from .. import FORMAT_UNICODE, FORMAT_INT, FORMAT_BINARY, FORMAT_UUID, FORMAT_UUID_LE, FORMAT_BOOLEAN
from .rfc4511 import Controls, Control


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
    prepared = {}
    for change in changes:
        prepared[change['attribute']['type']] = (change['operation'], change['attribute']['value'])
    return prepared


def build_controls_list(controls):
    """
    controls is a list of tuple
    each tuple must have 3 elements: the control OID, the criticality, the value
    criticality must be a boolean
    """
    if not controls:
        return None

    if not isinstance(controls, (list, tuple)):
        raise LDAPControlsError('controls must be a list')

    built_controls = Controls()
    for idx, control in enumerate(controls):
        if len(control) == 3 and isinstance(control[1], bool):
            built_control = Control()
            built_control['controlType'] = control[0]
            built_control['criticality'] = control[1]
            built_control['controlValue'] = control[2]
            built_controls.setComponentByPosition(idx, built_control)
        else:
            raise LDAPControlsError('control must be a tuple of 3 elements: controlType, criticality (boolean) and controlValue')

    return built_controls


def validate_assertion_value(schema, name, value):
    if schema and schema.attribute_types is not None:
        if not name.lower() in schema.attribute_types:
            raise LDAPAttributeError('invalid attribute type in assertion: ' + name)
    if not '\\' in value:
        return value.encode('utf-8')
    validated_value = bytearray()
    pos = 0
    while pos < len(value):
        if value[pos] == '\\':
            byte = value[pos + 1: pos + 3]
            if len(byte) == 2:
                try:
                    validated_value.append(int(value[pos + 1: pos + 3], 16))
                    pos += 3
                    continue
                except ValueError:
                    pass
        validated_value += value[pos].encode('utf-8')
        pos += 1

    return bytes(validated_value)


def validate_attribute_value(schema, name, value):
    if schema:
        if schema.attribute_types is not None and not name.lower() in schema.attribute_types:
            raise LDAPAttributeError('invalid attribute type in attribute')
        if schema.object_classes is not None and name.lower() == 'objectclass':
            if value.lower() not in schema.object_classes:
                raise LDAPObjectClassError('invalid class in ObjectClass attribute: ' + value)

    if isinstance(value, str):
        return validate_assertion_value(None, name, value)  # schema already checked, no need to check again

    return value


def format_unicode(raw_value):
    try:
        if str != bytes:  # python3
            return str(raw_value)
        else:
            return unicode(raw_value, 'utf-8')
    except TypeError:
        pass

    return raw_value

def format_int(raw_value):
    try:
        return int(raw_value)
    except TypeError:
        pass
    return raw_value

def format_binary(raw_value):
    try:
        return bytes(raw_value)
    except TypeError:
        pass
    return raw_value


def format_uuid(raw_value):
    try:
        return str(UUID(bytes=raw_value))
    except TypeError:
        pass
    return raw_value


def format_uuid_le(raw_value):
    try:
        return str(UUID(bytes_le=raw_value))
    except TypeError:
        pass
    return raw_value


def format_boolean(raw_value):
    if raw_value in [b'TRUE', b'true', b'True']:
        return True
    if raw_value in [b'FALSE', b'false', b'False']:
        return False
    return raw_value


def format_attribute_values(schema, name, values):
    if schema and schema.attribute_types is not None and name.lower() in schema.attribute_types:
        attr_type = schema.attribute_types[name.lower()]
        formatted_values = []
        for raw_value in values:
            # tries to format following the SYNTAX_xxx specification. Attribute OIDs have precedence over Syntax OIDs
            # the attribute oid or the attribute name can be used
            if attr_type.oid in FORMAT_UNICODE or (any(name.lower() in FORMAT_UNICODE for name in attr_type.name)):
                formatted_value = format_unicode(raw_value)
            elif attr_type.oid in FORMAT_INT or (any(name.lower() in FORMAT_INT for name in attr_type.name)):
                formatted_value = format_int(raw_value)
            elif attr_type.oid in FORMAT_BINARY or (any(name.lower() in FORMAT_BINARY for name in attr_type.name)):
                formatted_value = format_binary(raw_value)
            elif attr_type.oid in FORMAT_UUID or (any(name.lower() in FORMAT_UUID for name in attr_type.name)):
                formatted_value = format_uuid(raw_value)
            elif attr_type.oid in FORMAT_UUID_LE or (any(name.lower() in FORMAT_UUID_LE for name in attr_type.name)):
                formatted_value = format_uuid_le(raw_value)
            elif attr_type.oid in FORMAT_BOOLEAN or (any(name.lower() in FORMAT_BOOLEAN for name in attr_type.name)):
                formatted_value = format_boolean(raw_value)
            elif attr_type.syntax in FORMAT_UNICODE:
                formatted_value = format_unicode(raw_value)
            elif attr_type.syntax in FORMAT_INT:
                formatted_value = format_int(raw_value)
            elif attr_type.syntax in FORMAT_BINARY:
                formatted_value = format_binary(raw_value)
            elif attr_type.syntax in FORMAT_UUID:
                formatted_value = format_uuid(raw_value)
            elif attr_type.syntax in FORMAT_UUID_LE:
                formatted_value = format_uuid_le(raw_value)
            elif attr_type.syntax in FORMAT_BOOLEAN:
                formatted_value = format_boolean(raw_value)
            else:
                formatted_value = raw_value

            formatted_values.append(formatted_value)
        if attr_type.single_value:
            formatted_values = formatted_values[0]
    else:
        formatted_values = values

    return formatted_values
