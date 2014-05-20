"""
Created on 2013.09.11

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

from os import linesep
import re

from .. import CLASS_ABSTRACT, CLASS_STRUCTURAL, CLASS_AUXILIARY, ATTRIBUTE_USER_APPLICATION, ATTRIBUTE_DIRECTORY_OPERATION, ATTRIBUTE_DISTRIBUTED_OPERATION, ATTRIBUTE_DSA_OPERATION
from .oid import Oids, decode_oids, decode_syntax
from ..core.exceptions import LDAPSchemaError


def constant_to_class_kind(value):
    if value == CLASS_STRUCTURAL:
        return 'Structural'
    elif value == CLASS_ABSTRACT:
        return 'Abstract'
    elif value == CLASS_AUXILIARY:
        return 'Auxiliary'
    else:
        return 'unknown'


def constant_to_attribute_usage(value):
    if value == ATTRIBUTE_USER_APPLICATION:
        return 'User Application'
    elif value == ATTRIBUTE_DIRECTORY_OPERATION:
        return "Directory operation"
    elif value == ATTRIBUTE_DISTRIBUTED_OPERATION:
        return 'Distributed operation'
    elif value == ATTRIBUTE_DSA_OPERATION:
        return 'DSA operation'
    else:
        return 'unknown'


def attribute_usage_to_constant(value):
    if value == 'userApplications':
        return ATTRIBUTE_USER_APPLICATION
    elif value == 'directoryOperation':
        return ATTRIBUTE_DIRECTORY_OPERATION
    elif value == 'distributedOperation':
        return ATTRIBUTE_DISTRIBUTED_OPERATION
    elif value == 'dsaOperation':
        return ATTRIBUTE_DSA_OPERATION
    else:
        return 'unknown'


def quoted_string_to_list(quoted_string):
    string = quoted_string.strip()
    if string[0] == '(' and string[-1] == ')':
        string = string[1:-1]
    elements = string.split("'")
    return [element.strip("'").strip() for element in elements if element.strip()]


def oids_string_to_list(oid_string):
    string = oid_string.strip()
    if string[0] == '(' and string[-1] == ')':
        string = string[1:-1]
    elements = string.split('$')
    return [element.strip() for element in elements if element.strip()]


def extension_to_tuple(extension_string):
    string = extension_string.strip()
    name, _, values = string.partition(' ')
    return name, quoted_string_to_list(values)


def list_to_string(list_object):
    if not isinstance(list_object, list):
        return list_object

    r = ''
    for element in list_object:
        r += (list_to_string(element) if isinstance(element, list) else str(element)) + ', '

    return r[:-2] if r else ''


class DsaInfo(object):
    """
    This class contains info about the ldap server (DSA) read from DSE
    as defined in RFC4512 and RFC3045. Unknown attributes are stored in the "other" dict
    """

    def __init__(self, attributes):
        self.alt_servers = attributes.pop('altServer', None)
        self.naming_contexts = attributes.pop('namingContexts', None)
        self.supported_controls = decode_oids(attributes.pop('supportedControl', None))
        self.supported_extensions = decode_oids(attributes.pop('supportedExtension', None))
        self.supported_features = decode_oids(attributes.pop('supportedFeatures', None)) + decode_oids(attributes.pop('supportedCapabilities', None))
        self.supported_ldap_versions = attributes.pop('supportedLDAPVersion', None)
        self.supported_sasl_mechanisms = attributes.pop('supportedSASLMechanisms', None)
        self.vendor_name = attributes.pop('vendorName', None)
        self.vendor_version = attributes.pop('vendorVersion', None)
        self.schema_entry = attributes.pop('subschemaSubentry', None)
        self.other = attributes

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = 'DSA info (from DSE):' + linesep
        r += ('  Supported LDAP Versions: ' + ', '.join([s for s in self.supported_ldap_versions]) + linesep) if self.supported_ldap_versions else ''
        r += ('  Naming Contexts:' + linesep + linesep.join(['    ' + s for s in self.naming_contexts]) + linesep) if self.naming_contexts else ''
        r += ('  Alternative Servers:' + linesep + linesep.join(['    ' + s for s in self.alt_servers]) + linesep) if self.alt_servers else ''
        r += ('  Supported Controls:' + linesep + linesep.join(['    ' + str(s) for s in self.supported_controls]) + linesep) if self.supported_controls else ''
        r += ('  Supported Extensions:' + linesep + linesep.join(['    ' + str(s) for s in self.supported_extensions]) + linesep) if self.supported_extensions else ''
        r += ('  Supported Features:' + linesep + linesep.join(['    ' + str(s) for s in self.supported_features]) + linesep) if self.supported_features else ''
        r += ('  Supported SASL Mechanisms:' + linesep + '    ' + ', '.join([s for s in self.supported_sasl_mechanisms]) + linesep) if self.supported_sasl_mechanisms else ''
        r += ('  Schema Entry:' + linesep + linesep.join(['    ' + s for s in self.schema_entry]) + linesep) if self.schema_entry else ''
        r += 'Other:' + linesep
        for k, v in self.other.items():
            r += '  ' + k + ': ' + linesep
            if isinstance(v, list):
                r += linesep.join(['    ' + str(s) for s in v]) + linesep
            else:
                r += v + linesep
        return r


class SchemaInfo(object):
    """
    This class contains info about the ldap server schema read from an entry (default entry is DSE)
    as defined in RFC4512. Unknown attributes are stored in the "other" dict
    """

    def __init__(self, schema_entry, attributes):
        self.schema_entry = schema_entry
        self.create_time_stamp = attributes.pop('createTimestamp', None)
        self.modify_time_stamp = attributes.pop('modifyTimestamp', None)
        self.attribute_types = AttributeTypeInfo.from_definition(attributes.pop('attributeTypes', []))
        self.object_classes = ObjectClassInfo.from_definition(attributes.pop('objectClasses', []))
        self.matching_rules = MatchingRuleInfo.from_definition(attributes.pop('matchingRules', []))
        self.matching_rule_uses = MatchingRuleUseInfo.from_definition(attributes.pop('matchingRuleUse', []))
        self.dit_content_rules = DitContentRuleInfo.from_definition(attributes.pop('dITContentRules', []))
        self.dit_structure_rules = DitStructureRuleInfo.from_definition(attributes.pop('dITStructureRules', []))
        self.name_forms = NameFormInfo.from_definition(attributes.pop('nameForms', []))
        self.ldap_syntaxes = LdapSyntaxInfo.from_definition(attributes.pop('ldapSyntaxes', []))
        self.other = attributes  # remaining attributes not in RFC4512

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = 'DSA Schema from: ' + self.schema_entry + linesep
        r += ('  Attribute types:' + linesep + '    ' + ', '.join([str(self.attribute_types[s]) for s in self.attribute_types]) + linesep) if self.attribute_types else ''
        r += ('  Object classes:' + linesep + '    ' + ', '.join([str(self.object_classes[s]) for s in self.object_classes]) + linesep) if self.object_classes else ''
        r += ('  Matching rules:' + linesep + '    ' + ', '.join([str(self.matching_rules[s]) for s in self.matching_rules]) + linesep) if self.matching_rules else ''
        r += ('  Matching rule uses:' + linesep + '    ' + ', '.join([str(self.matching_rule_uses[s]) for s in self.matching_rule_uses]) + linesep) if self.matching_rule_uses else ''
        r += ('  DIT content rule:' + linesep + '    ' + ', '.join([str(self.dit_content_rules[s]) for s in self.dit_content_rules]) + linesep) if self.dit_content_rules else ''
        r += ('  DIT structure rule:' + linesep + '    ' + ', '.join([str(self.dit_structure_rules[s]) for s in self.dit_structure_rules]) + linesep) if self.dit_structure_rules else ''
        r += ('  Name forms:' + linesep + '    ' + ', '.join([str(self.name_forms[s]) for s in self.name_forms]) + linesep) if self.name_forms else ''
        r += ('  LDAP syntaxes:' + linesep + '    ' + ', '.join([str(self.ldap_syntaxes[s]) for s in self.ldap_syntaxes]) + linesep) if self.ldap_syntaxes else ''
        r += 'Other:' + linesep

        for k, v in self.other.items():
            r += '  ' + k + ': ' + linesep
            r += (linesep.join(['    ' + str(s) for s in v])) if isinstance(v, list) else v + linesep
        return r


class BaseObjectInfo(object):
    """
    Base class for objects defined in the schema as per RFC4512
    """

    def __init__(self,
                 oid=None,
                 name=None,
                 description=None,
                 obsolete=False,
                 extensions=None,
                 experimental=None,
                 definition=None):

        self.oid = oid
        self.name = name
        self.description = description
        self.obsolete = obsolete
        self.extensions = extensions
        self.experimental = experimental
        self.raw_definition = definition
        self._oid_info = None

    @property
    def oid_info(self):
        if self._oid_info is None and self.oid:
            self._oid_info = Oids.get(self.oid, '')

        return self._oid_info if self._oid_info else None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        r = ': ' + self.oid
        r += ' [OBSOLETE]' if self.obsolete else ''
        r += (linesep + '  Short name: ' + list_to_string(self.name)) if self.name else ''
        r += (linesep + '  Description: ' + self.description) if self.description else ''
        r += '<__desc__>'
        r += (linesep + '  Extensions:' + linesep + linesep.join(['    ' + s[0] + ': ' + list_to_string(s[1]) for s in self.extensions])) if self.extensions else ''
        r += (linesep + '  Experimental:' + linesep + linesep.join(['    ' + s[0] + ': ' + list_to_string(s[1]) for s in self.experimental])) if self.experimental else ''
        r += (linesep + '  OidInfo: ' + str(self.oid_info)) if self.oid_info else ''
        r += linesep
        return r

    @classmethod
    def from_definition(cls, definitions):
        if not definitions:
            return None

        ret_dict = dict()
        for object_definition in definitions:
            if [object_definition[0] == ')' and object_definition[:-1] == ')']:
                if cls is MatchingRuleInfo:
                    pattern = '| SYNTAX '
                elif cls is ObjectClassInfo:
                    pattern = '| SUP | ABSTRACT| STRUCTURAL| AUXILIARY| MUST | MAY '
                elif cls is AttributeTypeInfo:
                    pattern = '| SUP | EQUALITY | ORDERING | SUBSTR | SYNTAX | SINGLE-VALUE| COLLECTIVE| NO-USER-MODIFICATION| USAGE '
                elif cls is MatchingRuleUseInfo:
                    pattern = '| APPLIES '
                elif cls is DitContentRuleInfo:
                    pattern = '| AUX '
                elif cls is LdapSyntaxInfo:
                    pattern = ''
                elif cls is DitContentRuleInfo:
                    pattern = '| AUX | MUST | MAY | NOT '
                elif cls is DitStructureRuleInfo:
                    pattern = '| FORM | SUP '
                elif cls is NameFormInfo:
                    pattern = '| OC | MUST | MAY  '
                else:
                    raise LDAPSchemaError('unknown schema definition class')

                splitted = re.split('( NAME | DESC | OBSOLETE| X-| E-' + pattern + ')', object_definition[1:-1])
                values = splitted[::2]
                separators = splitted[1::2]
                separators.insert(0, 'OID')
                defs = list(zip(separators, values))
                object_def = cls()
                for d in defs:
                    key = d[0].strip()
                    value = d[1].strip()
                    if key == 'OID':
                        object_def.oid = value
                    elif key == 'NAME':
                        object_def.name = quoted_string_to_list(value)
                    elif key == 'DESC':
                        object_def.description = value.strip("'")
                    elif key == 'OBSOLETE':
                        object_def.obsolete = True
                    elif key == 'SYNTAX':
                        object_def.syntax = oids_string_to_list(value)
                    elif key == 'SUP':
                        object_def.superior = oids_string_to_list(value)
                    elif key == 'ABSTRACT':
                        object_def.kind = CLASS_ABSTRACT
                    elif key == 'STRUCTURAL':
                        object_def.kind = CLASS_STRUCTURAL
                    elif key == 'AUXILIARY':
                        object_def.kind = CLASS_AUXILIARY
                    elif key == 'MUST':
                        object_def.must_contain = oids_string_to_list(value)
                    elif key == 'MAY':
                        object_def.may_contain = oids_string_to_list(value)
                    elif key == 'EQUALITY':
                        object_def.equality = oids_string_to_list(value)
                    elif key == 'ORDERING':
                        object_def.ordering = oids_string_to_list(value)
                    elif key == 'SUBSTR':
                        object_def.substr = oids_string_to_list(value)
                    elif key == 'SYNTAX':
                        object_def.syntax = oids_string_to_list(value)
                    elif key == 'SINGLE-VALUE':
                        object_def.single_value = True
                    elif key == 'COLLECTIVE':
                        object_def.collective = True
                    elif key == 'NO-USER-MODIFICATION':
                        object_def.no_user_modification = True
                    elif key == 'USAGE':
                        object_def.usage = attribute_usage_to_constant(value)
                    elif key == 'APPLIES':
                        object_def.apply_to = oids_string_to_list(value)
                    elif key == 'AUX':
                        object_def.auxiliary_classes = oids_string_to_list(value)
                    elif key == 'FORM':
                        object_def.name_form = oids_string_to_list(value)
                    elif key == 'OC':
                        object_def.object_class = oids_string_to_list(value)
                    elif key == 'X-':
                        if not object_def.extensions:
                            object_def.extensions = []
                        object_def.extensions.append(extension_to_tuple('X-' + value))
                    elif key == 'E-':
                        if not object_def.experimental:
                            object_def.experimental = []
                        object_def.experimental.append(extension_to_tuple('E-' + value))
                    else:
                        raise LDAPSchemaError('malformed schema definition key:' + key)
                object_def.raw_definition = object_definition
                if hasattr(object_def, 'syntax') and len(object_def.syntax) == 1:
                    object_def.syntax = object_def.syntax[0]
                if object_def.name:
                    for name in object_def.name:
                        ret_dict[name.lower()] = object_def
                else:
                    ret_dict[object_def.oid] = object_def
            else:
                raise LDAPSchemaError('malformed schema definition')
        return ret_dict


class MatchingRuleInfo(BaseObjectInfo):
    """
    As per RFC 4512 (4.1.3)
    """

    def __init__(self,
                 oid=None,
                 name=None,
                 description=None,
                 obsolete=False,
                 syntax=None,
                 extensions=None,
                 experimental=None,
                 definition=None):

        BaseObjectInfo.__init__(self,
                                oid=oid,
                                name=name,
                                description=description,
                                obsolete=obsolete,
                                extensions=extensions,
                                experimental=experimental,
                                definition=definition)
        self.syntax = syntax

    def __repr__(self):
        r = (linesep + '  Syntax: ' + list_to_string(self.syntax)) if self.syntax else ''
        return 'Matching rule' + BaseObjectInfo.__repr__(self).replace('<__desc__>', r)


class MatchingRuleUseInfo(BaseObjectInfo):
    """
    As per RFC 4512 (4.1.4)
    """

    def __init__(self,
                 oid=None,
                 name=None,
                 description=None,
                 obsolete=False,
                 apply_to=None,
                 extensions=None,
                 experimental=None,
                 definition=None):
        BaseObjectInfo.__init__(self,
                                oid=oid,
                                name=name,
                                description=description,
                                obsolete=obsolete,
                                extensions=extensions,
                                experimental=experimental,
                                definition=definition)
        self.apply_to = apply_to

    def __repr__(self):
        r = (linesep + '  Apply to: ' + list_to_string(self.apply_to)) if self.apply_to else ''
        return 'Matching rule use' + BaseObjectInfo.__repr__(self).replace('<__desc__>', r)


class ObjectClassInfo(BaseObjectInfo):
    """
    As per RFC 4512 (4.1.1)
    """

    def __init__(self,
                 oid=None,
                 name=None,
                 description=None,
                 obsolete=False,
                 superior=None,
                 kind=None,
                 must_contain=None,
                 may_contain=None,
                 extensions=None,
                 experimental=None,
                 definition=None):

        BaseObjectInfo.__init__(self,
                                oid=oid,
                                name=name,
                                description=description,
                                obsolete=obsolete,
                                extensions=extensions,
                                experimental=experimental,
                                definition=definition)
        self.superior = superior
        self.kind = kind
        self.must_contain = must_contain
        self.may_contain = may_contain

    def __repr__(self):
        r = ''
        r += (linesep + '  Type: ' + constant_to_class_kind(self.kind)) if isinstance(self.kind, int) else ''
        r += (linesep + '  Must contain attributes: ' + list_to_string(self.must_contain)) if self.must_contain else ''
        r += (linesep + '  May contain attributes: ' + list_to_string(self.may_contain)) if self.may_contain else ''
        return 'Object Class' + BaseObjectInfo.__repr__(self).replace('<__desc__>', r)


class AttributeTypeInfo(BaseObjectInfo):
    """
    As per RFC 4512 (4.1.2)
    """

    def __init__(self,
                 oid=None,
                 name=None,
                 description=None,
                 obsolete=False,
                 superior=None,
                 equality=None,
                 ordering=None,
                 substring=None,
                 syntax=None,
                 single_value=False,
                 collective=False,
                 no_user_modification=False,
                 usage=None,
                 extensions=None,
                 experimental=None,
                 definition=None):

        BaseObjectInfo.__init__(self,
                                oid=oid,
                                name=name,
                                description=description,
                                obsolete=obsolete,
                                extensions=extensions,
                                experimental=experimental,
                                definition=definition)
        self.superior = superior
        self.equality = equality
        self.ordering = ordering
        self.substring = substring
        self.syntax = syntax
        self.single_value = single_value
        self.collective = collective
        self.no_user_modification = no_user_modification
        self.usage = usage

    def __repr__(self):
        r = ''
        r += linesep + '  Single Value: True' if self.single_value else ''
        r += linesep + '  Collective: True' if self.collective else ''
        r += linesep + '  No user modification: True' if self.no_user_modification else ''
        r += (linesep + '  Usage: ' + constant_to_attribute_usage(self.usage)) if self.usage else ''
        r += (linesep + '  Equality rule: ' + list_to_string(self.equality)) if self.equality else ''
        r += (linesep + '  Ordering rule: ' + list_to_string(self.ordering)) if self.ordering else ''
        r += (linesep + '  Substring rule: ' + list_to_string(self.substring)) if self.substring else ''
        r += (linesep + '  Syntax: ' + (self.syntax + ' - ' + str(decode_syntax(self.syntax)))) if self.syntax else ''
        return 'Attribute type' + BaseObjectInfo.__repr__(self).replace('<__desc__>', r)


class LdapSyntaxInfo(BaseObjectInfo):
    """
    As per RFC 4512 (4.1.5)
    """

    def __init__(self,
                 oid=None,
                 description=None,
                 extensions=None,
                 experimental=None,
                 definition=None):

        BaseObjectInfo.__init__(self,
                                oid=oid, name=None,
                                description=description,
                                obsolete=False,
                                extensions=extensions,
                                experimental=experimental,
                                definition=definition)

    def __repr__(self):
        return 'LDAP syntax' + BaseObjectInfo.__repr__(self).replace('<__desc__>', '')


class DitContentRuleInfo(BaseObjectInfo):
    """
    As per RFC 4512 (4.1.6)
    """

    def __init__(self,
                 oid=None,
                 name=None,
                 description=None,
                 obsolete=False,
                 auxiliary_classes=None,
                 must_contain=None,
                 may_contain=None,
                 not_contains=None,
                 extensions=None,
                 experimental=None,
                 definition=None):

        BaseObjectInfo.__init__(self,
                                oid=oid,
                                name=name,
                                description=description,
                                obsolete=obsolete,
                                extensions=extensions,
                                experimental=experimental,
                                definition=definition)

        self.auxiliary_classes = auxiliary_classes
        self.must_contain = must_contain
        self.may_contain = may_contain
        self.not_contains = not_contains

    def __repr__(self):
        r = (linesep + '  Auxiliary classes: ' + list_to_string(self.auxiliary_classes)) if self.auxiliary_classes else ''
        r += (linesep + '  Must contain: ' + list_to_string(self.must_contain)) if self.must_contain else ''
        r += (linesep + '  May contain: ' + list_to_string(self.may_contain)) if self.may_contain else ''
        r += (linesep + '  Not contains: ' + list_to_string(self.not_contains)) if self.not_contains else ''
        return 'DIT content rule' + BaseObjectInfo.__repr__(self).replace('<__desc__>', r)


class DitStructureRuleInfo(BaseObjectInfo):
    """
    As per RFC 4512 (4.1.7.1)
    """

    def __init__(self,
                 oid=None,
                 name=None,
                 description=None,
                 obsolete=False,
                 name_form=None,
                 superior=None,
                 extensions=None,
                 experimental=None,
                 definition=None):

        BaseObjectInfo.__init__(self,
                                oid=oid,
                                name=name,
                                description=description,
                                obsolete=obsolete,
                                extensions=extensions,
                                experimental=experimental,
                                definition=definition)
        self.superior = superior
        self.name_form = name_form

    def __repr__(self):
        r = (linesep + '  Superior rules: ' + list_to_string(self.superior)) if self.superior else ''
        r += (linesep + '  Name form: ' + list_to_string(self.name_form)) if self.name_form else ''
        return 'DIT content rule' + BaseObjectInfo.__repr__(self).replace('<__desc__>', r)


class NameFormInfo(BaseObjectInfo):
    """
    As per RFC 4512 (4.1.7.2)
    """

    def __init__(self,
                 oid=None,
                 name=None,
                 description=None,
                 obsolete=False,
                 object_class=None,
                 must_contain=None,
                 may_contain=None,
                 extensions=None,
                 experimental=None,
                 definition=None):

        BaseObjectInfo.__init__(self,
                                oid=oid,
                                name=name,
                                description=description,
                                obsolete=obsolete,
                                extensions=extensions,
                                experimental=experimental,
                                definition=definition)
        self.object_class = object_class
        self.must_contain = must_contain
        self.may_contain = may_contain

    def __repr__(self):
        r = (linesep + '  Object class: ' + self.object_class) if self.object_class else ''
        r += (linesep + '  Must contain: ' + list_to_string(self.must_contain)) if self.must_contain else ''
        r += (linesep + '  May contain: ' + list_to_string(self.may_contain)) if self.may_contain else ''
        return 'DIT content rule' + BaseObjectInfo.__repr__(self).replace('<__desc__>', r)
