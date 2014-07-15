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
from datetime import datetime
from uuid import UUID
from ..core.exceptions import LDAPControlsError, LDAPAttributeError, LDAPObjectClassError
from .. import FORMAT_UNICODE, FORMAT_INT, FORMAT_BINARY, FORMAT_UUID, FORMAT_UUID_LE, FORMAT_BOOLEAN, FORMAT_TIME
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
            return str(raw_value, 'utf-8')
        else:
            return unicode(raw_value, 'utf-8')
    except TypeError:
        pass

    return raw_value


def format_integer(raw_value):
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


def format_time(raw_value):
    try:
        return datetime(raw_value)  # tbd
    except TypeError:
        pass

    return raw_value


def format_attribute_values(schema, name, values):
    """
    Tries to format following the OIDs info and format_helper specification.
    Search for attribute oid, then attribute name (can be multiple), then attrubte syntax
    Precedence is: 1. attribute name
                   2. attribute oid(from schema)
                   3. attribute names (from oid_info)
                   4. attribute syntax (from schema)
    If no formatter is found the raw_value is returned as bytes.
    Attributes defined as SINGLE_VALUE in schema are returned as a single object, otherwise are returned as a list of object
    Formatter functions can return any kind of object
    """
    formatter = None
    if schema and schema.attribute_types is not None and name.lower() in schema.attribute_types:
        attr_type = schema.attribute_types[name.lower()]
    else:
        attr_type = None

    if name.lower() in format_helper:  # search for attribute name, as returned by the search operation
        formatter = format_helper[name.lower()]

    if not formatter and attr_type and attr_type.oid in format_helper:  # search for attribute oid as returned by schema
        formatter = format_helper[attr_type.oid]

    if not formatter and attr_type and attr_type.oid_info:
        if isinstance(attr_type.oid_info.name, list):  # search for multiple names defined in oid_info
            for attr_name in attr_type.oid_info.name:
                if attr_name.lower() in format_helper:
                    formatter = format_helper[attr_name.lower()]
                    break
        elif attr_type.oid_info.name in format_helper:  # search for name defined in oid_info
            formatter = format_helper[attr_type.oid_info.name]

    if not formatter and attr_type and attr_type.syntax in format_helper:  # search for syntax defined in schema
        formatter = format_helper[attr_type.syntax]

    if not formatter:
        print('UNKNOWN NAME:', name)
        if attr_type:
            print('UNKNOWN SYNTAX:', attr_type.syntax)
        else:
            print('NO ATTR_TYPE')
        formatter = bytes  # default formatter

    formatted_values = [formatter(raw_value) for raw_value in values]
    return formatted_values[0] if (attr_type and attr_type.single_value) else formatted_values


format_helper = {
    '1.3.6.1.4.1.1466.115.121.1.3': format_unicode,  # Attribute type description
    '1.3.6.1.4.1.1466.115.121.1.6': format_unicode,  # Bit String
    '1.3.6.1.4.1.1466.115.121.1.11': format_unicode,  # Country String
    '1.3.6.1.4.1.1466.115.121.1.12': format_unicode,  # Distinguished name (DN)
    '1.3.6.1.4.1.1466.115.121.1.14': format_unicode,  # Delivery method
    '1.3.6.1.4.1.1466.115.121.1.15': format_unicode,  # Directory string
    '1.3.6.1.4.1.1466.115.121.1.16': format_unicode,  # DIT Content Rule Description
    '1.3.6.1.4.1.1466.115.121.1.17': format_unicode,  # DIT Structure Rule Description
    '1.3.6.1.4.1.1466.115.121.1.21': format_unicode,  # Enhanced Guide
    '1.3.6.1.4.1.1466.115.121.1.22': format_unicode,  # Facsimile Telephone Number
    '1.3.6.1.4.1.1466.115.121.1.25': format_unicode,  # Guide (obsolete)
    '1.3.6.1.4.1.1466.115.121.1.26': format_unicode,  # IA5 string
    '1.3.6.1.4.1.1466.115.121.1.30': format_unicode,  # Matching rule description
    '1.3.6.1.4.1.1466.115.121.1.31': format_unicode,  # Matching ruledescription
    '1.3.6.1.4.1.1466.115.121.1.34': format_unicode,  # Name and optional UID
    '1.3.6.1.4.1.1466.115.121.1.35': format_unicode,  # Name form description
    '1.3.6.1.4.1.1466.115.121.1.36': format_unicode,  # Mumeric string
    '1.3.6.1.4.1.1466.115.121.1.37': format_unicode,  # Object class description
    '1.3.6.1.4.1.1466.115.121.1.38': format_unicode,  # OID
    '1.3.6.1.4.1.1466.115.121.1.39': format_unicode,  # Other mailbox
    '1.3.6.1.4.1.1466.115.121.1.41': format_unicode,  # Postal address
    '1.3.6.1.4.1.1466.115.121.1.44': format_unicode,  # Printable string
    '1.3.6.1.4.1.1466.115.121.1.50': format_unicode,  # Telephone number
    '1.3.6.1.4.1.1466.115.121.1.51': format_unicode,  # Teletex terminal identifier
    '1.3.6.1.4.1.1466.115.121.1.52': format_unicode,  # Teletex number
    '1.3.6.1.4.1.1466.115.121.1.54': format_unicode,  # LDAP syntax description
    '1.3.6.1.4.1.1466.115.121.1.58': format_unicode,  # Substring assertion
    '1.3.6.1.4.1.1466.115.121.1.27': format_integer,  # Integer
    '2.16.840.1.113719.1.1.5.1.22': format_integer,  # Counter (Novell)
    '1.3.6.1.4.1.1466.115.121.1.23': format_binary,  # Fax
    '1.3.6.1.4.1.1466.115.121.1.28': format_binary,  # JPEG
    '1.3.6.1.4.1.1466.115.121.1.40': format_binary,  # Octet string
    '1.3.6.1.1.16.1': format_uuid,  # UUID
    '2.16.840.1.113719.1.1.4.1.501': format_uuid,  # GUID (Novell)
    '1.3.6.1.4.1.1466.115.121.1.7': format_boolean,  # Boolean
    '1.3.6.1.4.1.1466.115.121.1.24': format_time,  # Generalized time
    '1.3.6.1.4.1.1466.115.121.1.53': format_time  # Utc time  (deprecated)
}