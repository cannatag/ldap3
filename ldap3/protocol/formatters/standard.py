"""
"""

# Created on 2014.10.28
#
# Author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
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

from ... import SEQUENCE_TYPES
from ...protocol.formatters.formatters import format_ad_timestamp, format_binary, format_boolean, format_integer, format_sid, format_time, format_unicode, format_uuid, format_uuid_le

standard_formatter = {
    '1.2.840.113556.1.4.903': format_binary,  # Object (DN-binary) - Microsoft
    '1.2.840.113556.1.4.904': format_unicode,  # Object (DN-string) - Microsoft
    '1.2.840.113556.1.4.905': format_unicode,  # String (Teletex) - Microsoft
    '1.2.840.113556.1.4.906': format_integer,  # Large integer - Microsoft
    '1.2.840.113556.1.4.907': format_binary,  # String (NT-sec-desc) - Microsoft
    '1.2.840.113556.1.4.1221': format_binary,  # Object (OR-name) - Microsoft
    '1.2.840.113556.1.4.1362': format_unicode,  # String (Case) - Microsoft
    '1.3.6.1.4.1.1466.115.121.1.1': format_binary,  # ACI item [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.2': format_binary,  # Access point [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.3': format_unicode,  # Attribute type description
    '1.3.6.1.4.1.1466.115.121.1.4': format_binary,  # Audio [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.5': format_binary,  # Binary [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.6': format_unicode,  # Bit String
    '1.3.6.1.4.1.1466.115.121.1.7': format_boolean,  # Boolean
    '1.3.6.1.4.1.1466.115.121.1.8': format_binary,  # Certificate [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.9': format_binary,  # Certificate List [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.10': format_binary,  # Certificate Pair [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.11': format_unicode,  # Country String
    '1.3.6.1.4.1.1466.115.121.1.12': format_unicode,  # Distinguished name (DN)
    '1.3.6.1.4.1.1466.115.121.1.13': format_binary,  # Data Quality Syntax [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.14': format_unicode,  # Delivery method
    '1.3.6.1.4.1.1466.115.121.1.15': format_unicode,  # Directory string
    '1.3.6.1.4.1.1466.115.121.1.16': format_unicode,  # DIT Content Rule Description
    '1.3.6.1.4.1.1466.115.121.1.17': format_unicode,  # DIT Structure Rule Description
    '1.3.6.1.4.1.1466.115.121.1.18': format_binary,  # DL Submit Permission [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.19': format_binary,  # DSA Quality Syntax [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.20': format_binary,  # DSE Type [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.21': format_binary,  # Enhanced Guide
    '1.3.6.1.4.1.1466.115.121.1.22': format_unicode,  # Facsimile Telephone Number
    '1.3.6.1.4.1.1466.115.121.1.23': format_binary,  # Fax
    '1.3.6.1.4.1.1466.115.121.1.24': format_time,  # Generalized time
    '1.3.6.1.4.1.1466.115.121.1.25': format_binary,  # Guide [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.26': format_unicode,  # IA5 string
    '1.3.6.1.4.1.1466.115.121.1.27': format_integer,  # Integer
    '1.3.6.1.4.1.1466.115.121.1.28': format_binary,  # JPEG
    '1.3.6.1.4.1.1466.115.121.1.29': format_binary,  # Master and Shadow Access Points [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.30': format_unicode,  # Matching rule description
    '1.3.6.1.4.1.1466.115.121.1.31': format_unicode,  # Matching rule use description
    '1.3.6.1.4.1.1466.115.121.1.32': format_unicode,  # Mail Preference [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.33': format_unicode,  # MHS OR Address [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.34': format_unicode,  # Name and optional UID
    '1.3.6.1.4.1.1466.115.121.1.35': format_unicode,  # Name form description
    '1.3.6.1.4.1.1466.115.121.1.36': format_unicode,  # Numeric string
    '1.3.6.1.4.1.1466.115.121.1.37': format_unicode,  # Object class description
    '1.3.6.1.4.1.1466.115.121.1.38': format_unicode,  # OID
    '1.3.6.1.4.1.1466.115.121.1.39': format_unicode,  # Other mailbox
    '1.3.6.1.4.1.1466.115.121.1.40': format_binary,  # Octet string
    '1.3.6.1.4.1.1466.115.121.1.41': format_unicode,  # Postal address
    '1.3.6.1.4.1.1466.115.121.1.42': format_binary,  # Protocol Information [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.43': format_binary,  # Presentation Address [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.44': format_unicode,  # Printable string
    '1.3.6.1.4.1.1466.115.121.1.45': format_binary,  # Subtree specification [OBSOLETE
    '1.3.6.1.4.1.1466.115.121.1.46': format_binary,  # Supplier Information [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.47': format_binary,  # Supplier Or Consumer [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.48': format_binary,  # Supplier And Consumer [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.49': format_binary,  # Supported Algorithm [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.50': format_unicode,  # Telephone number
    '1.3.6.1.4.1.1466.115.121.1.51': format_unicode,  # Teletex terminal identifier
    '1.3.6.1.4.1.1466.115.121.1.52': format_unicode,  # Teletex number
    '1.3.6.1.4.1.1466.115.121.1.53': format_time,  # Utc time  (deprecated)
    '1.3.6.1.4.1.1466.115.121.1.54': format_unicode,  # LDAP syntax description
    '1.3.6.1.4.1.1466.115.121.1.55': format_binary,  # Modify rights [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.56': format_binary,  # LDAP Schema Definition [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.57': format_unicode,  # LDAP Schema Description [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.58': format_unicode,  # Substring assertion
    '1.3.6.1.1.16.1': format_unicode,  # UUID
    '2.16.840.1.113719.1.1.4.1.501': format_uuid,  # GUID (Novell)
    '2.16.840.1.113719.1.1.5.1.0': format_binary,  # Unknown (Novell)
    '2.16.840.1.113719.1.1.5.1.6': format_unicode,  # Case Ignore List (Novell)
    '2.16.840.1.113719.1.1.5.1.12': format_binary,  # Tagged Data (Novell)
    '2.16.840.1.113719.1.1.5.1.13': format_binary,  # Octet List (Novell)
    '2.16.840.1.113719.1.1.5.1.14': format_unicode,  # Tagged String (Novell)
    '2.16.840.1.113719.1.1.5.1.15': format_unicode,  # Tagged Name And String (Novell)
    '2.16.840.1.113719.1.1.5.1.16': format_binary,  # NDS Replica Pointer (Novell)
    '2.16.840.1.113719.1.1.5.1.17': format_unicode,  # NDS ACL (Novell)
    '2.16.840.1.113719.1.1.5.1.19': format_time,  # NDS Timestamp (Novell)
    '2.16.840.1.113719.1.1.5.1.22': format_integer,  # Counter (Novell)
    '2.16.840.1.113719.1.1.5.1.23': format_unicode,  # Tagged Name (Novell)
    '2.16.840.1.113719.1.1.5.1.25': format_unicode,  # Typed Name (Novell)
    'supportedldapversion': format_integer,  # supportedLdapVersion (Microsoft)
    'octetstring': format_binary,  # octect string (Microsoft)
    '1.2.840.113556.1.4.2': format_uuid_le,  # object guid (Microsoft)
    '1.2.840.113556.1.4.13': format_ad_timestamp,  # builtinCreationTime (Microsoft)
    '1.2.840.113556.1.4.26': format_ad_timestamp,  # creationTime (Microsoft)
    '1.2.840.113556.1.4.49': format_ad_timestamp,  # badPasswordTime (Microsoft)
    '1.2.840.113556.1.4.51': format_ad_timestamp,  # lastLogoff (Microsoft)
    '1.2.840.113556.1.4.52': format_ad_timestamp,  # lastLogon (Microsoft)
    '1.2.840.113556.1.4.96': format_ad_timestamp,  # pwdLastSet (Microsoft)
    '1.2.840.113556.1.4.146': format_sid,  # objectSid (Microsoft)
    '1.2.840.113556.1.4.159': format_ad_timestamp,  # accountExpires (Microsoft)
    '1.2.840.113556.1.4.662': format_ad_timestamp,  # lockoutTime (Microsoft)
    '1.2.840.113556.1.4.1696': format_ad_timestamp  # lastLogonTimestamp (Microsoft)
}


def format_attribute_values(schema, name, values, custom_formatter):
    """
    Tries to format following the OIDs info and format_helper specification.
    Search for attribute oid, then attribute name (can be multiple), then attribute syntax
    Precedence is:
    1. attribute name
    2. attribute oid(from schema)
    3. attribute names (from oid_info)
    4. attribute syntax (from schema)
    Custom formatters can be defined in Server object and have precedence over the standard_formatters
    If no formatter is found the raw_value is returned as bytes.
    Attributes defined as SINGLE_VALUE in schema are returned as a single object, otherwise are returned as a list of object
    Formatter functions can return any kind of object
    """
    formatter = None
    if schema and schema.attribute_types is not None and name in schema.attribute_types:
        attr_type = schema.attribute_types[name]
    else:
        attr_type = None

    if custom_formatter and isinstance(custom_formatter, dict):  # if custom formatters are defined they have precedence over the standard formatters
        if name in custom_formatter:  # search for attribute name, as returned by the search operation
            formatter = custom_formatter[name]

        if not formatter and attr_type and attr_type.oid in custom_formatter:  # search for attribute oid as returned by schema
            formatter = custom_formatter[attr_type.oid]

        if not formatter and attr_type and attr_type.oid_info:
            if isinstance(attr_type.oid_info.name, SEQUENCE_TYPES):  # search for multiple names defined in oid_info
                for attr_name in attr_type.oid_info.name:
                    if attr_name in custom_formatter:
                        formatter = custom_formatter[attr_name]
                        break
            elif attr_type.oid_info.name in custom_formatter:  # search for name defined in oid_info
                formatter = custom_formatter[attr_type.oid_info.name]

        if not formatter and attr_type and attr_type.syntax in custom_formatter:  # search for syntax defined in schema
            formatter = custom_formatter[attr_type.syntax]

    if not formatter and name in standard_formatter:  # search for attribute name, as returned by the search operation
        formatter = standard_formatter[name]

    if not formatter and attr_type and attr_type.oid in standard_formatter:  # search for attribute oid as returned by schema
        formatter = standard_formatter[attr_type.oid]

    if not formatter and attr_type and attr_type.oid_info:
        if isinstance(attr_type.oid_info.name, SEQUENCE_TYPES):  # search for multiple names defined in oid_info
            for attr_name in attr_type.oid_info.name:
                if attr_name in standard_formatter:
                    formatter = standard_formatter[attr_name]
                    break
        elif attr_type.oid_info.name in standard_formatter:  # search for name defined in oid_info
            formatter = standard_formatter[attr_type.oid_info.name]

    if not formatter and attr_type and attr_type.syntax in standard_formatter:  # search for syntax defined in schema
        formatter = standard_formatter[attr_type.syntax]

    if not formatter:
        formatter = format_unicode  # default formatter

    formatted_values = [formatter(raw_value) for raw_value in values]
    return formatted_values[0] if (attr_type and attr_type.single_value) else formatted_values
