"""
"""

# Created on 2016.04.30
#
# Author: Giovanni Cannata
#
# Copyright 2016 Giovanni Cannata
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

import json
import re

from threading import Lock

from .. import SEQUENCE_TYPES
from ..operation.bind import bind_request_to_dict
from ..operation.delete import delete_request_to_dict
from ..operation.add import add_request_to_dict
from ..operation.compare import compare_request_to_dict
from ..operation.modifyDn import modify_dn_request_to_dict
from ..operation.modify import modify_request_to_dict
from ..operation.search import search_request_to_dict, parse_filter, ROOT, AND, OR, NOT, MATCH_APPROX, \
    MATCH_GREATER_OR_EQUAL, MATCH_LESS_OR_EQUAL, MATCH_EXTENSIBLE, MATCH_PRESENT,\
    MATCH_SUBSTRING, MATCH_EQUAL
from ..utils.conv import json_hook, check_escape, to_unicode, to_raw
from ..core.exceptions import LDAPDefinitionError, LDAPPasswordIsMandatoryError
from ..utils.ciDict import CaseInsensitiveDict
from ..utils.dn import to_dn, safe_dn, safe_rdn
from ..protocol.sasl.sasl import validate_simple_password
from ..utils.log import log, log_enabled, ERROR, BASIC


# noinspection PyProtectedMember,PyUnresolvedReferences
class MockBaseStrategy(object):
    """
    Base class for connection strategy
    """

    def __init__(self):
        if not hasattr(self.connection.server, 'dit'):  # create entries dict if not already present
            self.connection.server.dit_lock = Lock()
            self.connection.server.dit = dict()
        self.entries = self.connection.server.dit  # for simpler reference
        self.no_real_dsa = True
        self.bound = None
        if log_enabled(BASIC):
            log(BASIC, 'instantiated <%s>: <%s>', self.__class__.__name__, self)

    def _start_listen(self):
        self.connection.listening = True
        self.connection.closed = False
        if self.connection.usage:
            self.connection._usage.open_sockets += 1

    def _stop_listen(self):
        self.connection.listening = False
        self.connection.closed = True
        if self.connection.usage:
            self.connection._usage.closed_sockets += 1

    def add_entry(self, dn, attributes):
        with self.connection.server.dit_lock:
            escaped_dn = safe_dn(dn)
            if escaped_dn not in self.connection.server.dit:
                self.connection.server.dit[escaped_dn] = CaseInsensitiveDict()
                for attribute in attributes:
                    if not isinstance(attributes[attribute], SEQUENCE_TYPES):  # entry attributes are always lists of bytes values
                        attributes[attribute] = [attributes[attribute]]
                    self.connection.server.dit[escaped_dn][attribute] = [to_raw(value) for value in attributes[attribute]]
                for rdn in safe_rdn(escaped_dn, decompose=True):  # adds rdns to entry attributes
                    if rdn[0] not in self.connection.server.dit[escaped_dn]:  # if rdn attribute is missing adds attribute and its value
                        self.connection.server.dit[escaped_dn][rdn[0]] = [to_raw(check_escape(rdn[1]))]
                    else:
                        if rdn[1] not in self.connection.server.dit[escaped_dn][rdn[0]]:  # add rdn value if rdn attribute is present but value is missing
                            self.connection.server.dit[escaped_dn][rdn[0]].append(to_raw(check_escape(rdn[1])))
                return True
            return False

    def remove_entry(self, dn):
        with self.connection.server.dit_lock:
            escaped_dn = safe_dn(dn)
            if escaped_dn in self.connection.server.dit:
                del self.connection.server.dit[escaped_dn]
                return True
            return False

    def entries_from_json(self, json_entry_file):
        target = open(json_entry_file, 'r')
        definition = json.load(target, object_hook=json_hook)
        if 'entries' not in definition:
            self.connection.last_error = 'invalid JSON definition, missing "entries" section'
            if log_enabled(ERROR):
                log(ERROR, '<%s> for <%s>', self.connection.last_error, self.connection)
            raise LDAPDefinitionError(self.connection.last_error)
        if not self.connection.server.dit:
            self.connection.server.dit = CaseInsensitiveDict()
        for entry in definition['entries']:
            if 'raw' not in entry:
                self.connection.last_error = 'invalid JSON definition, missing "raw" section'
                if log_enabled(ERROR):
                    log(ERROR, '<%s> for <%s>', self.connection.last_error, self.connection)
                raise LDAPDefinitionError(self.connection.last_error)
            if 'dn' not in entry:
                self.connection.last_error = 'invalid JSON definition, missing "dn" section'
                if log_enabled(ERROR):
                    log(ERROR, '<%s> for <%s>', self.connection.last_error, self.connection)
                raise LDAPDefinitionError(self.connection.last_error)
            self.add_entry(entry['dn'], entry['raw'])
        target.close()

    def mock_bind(self, request_message, controls):
        # BindRequest ::= [APPLICATION 0] SEQUENCE {
        #     version                 INTEGER (1 ..  127),
        #     name                    LDAPDN,
        #     authentication          AuthenticationChoice }
        #
        # BindResponse ::= [APPLICATION 1] SEQUENCE {
        #     COMPONENTS OF LDAPResult,
        #     serverSaslCreds    [7] OCTET STRING OPTIONAL }
        #
        # request: version, name, authentication
        # response: LDAPResult + serverSaslCreds
        request = bind_request_to_dict(request_message)
        identity = request['name']
        if 'simple' in request['authentication']:
            try:
                password = validate_simple_password(request['authentication']['simple'])
            except LDAPPasswordIsMandatoryError:
                password = ''
                identity = '<anonymous>'
        else:
            self.connection.last_error = 'only Simple Bind allowed in Mock strategy'
            if log_enabled(ERROR):
                log(ERROR, '<%s> for <%s>', self.connection.last_error, self.connection)
            raise LDAPDefinitionError(self.connection.last_error)
        # checks userPassword for password. userPassword must be a clear text string or a list of clear text strings
        if identity in self.connection.server.dit:
            if 'userPassword' in self.connection.server.dit[identity]:
                if self.connection.server.dit[identity]['userPassword'] == password or password in self.connection.server.dit[identity]['userPassword']:
                    result_code = 0
                    message = ''
                    self.bound = identity
                else:
                    result_code = 49
                    message = 'invalid credentials'
            else:  # no user found,  waits for 2 seconds returns invalidCredentials
                result_code = 49
                message = 'missing userPassword attribute'
        elif identity == '<anonymous>':
            result_code = 0
            message = ''
            self.bound = identity
        else:
            result_code = 49
            message = 'missing object'

        return {'resultCode': result_code,
                'matchedDN': to_unicode(''),
                'diagnosticMessage': to_unicode(message),
                'referral': None,
                'serverSaslCreds': None
                }

    def mock_delete(self, request_message, controls):
        # DelRequest ::= [APPLICATION 10] LDAPDN
        #
        # DelResponse ::= [APPLICATION 11] LDAPResult
        #
        # request: entry
        # response: LDAPResult
        request = delete_request_to_dict(request_message)
        dn = safe_dn(request['entry'])
        if dn in self.connection.server.dit:
            del self.connection.server.dit[dn]
            result_code = 0
            message = ''
        else:
            result_code = 32
            message = 'object not found'

        return {'resultCode': result_code,
                'matchedDN': to_unicode(''),
                'diagnosticMessage': to_unicode(message),
                'referral': None
                }

    def mock_add(self, request_message, controls):
        # AddRequest ::= [APPLICATION 8] SEQUENCE {
        #     entry           LDAPDN,
        #     attributes      AttributeList }
        #
        # AddResponse ::= [APPLICATION 9] LDAPResult
        #
        # request: entry, attributes
        # response: LDAPResult
        request = add_request_to_dict(request_message)
        dn = safe_dn(request['entry'])
        attributes = request['attributes']
        # converts attributes values to bytes

        if dn not in self.connection.server.dit:
            if self.add_entry(dn, attributes):
                result_code = 0
                message = ''
            else:
                result_code = 1
                message = 'error adding entry'
        else:
            result_code = 68
            message = 'entry already exist'

        return {'resultCode': result_code,
                'matchedDN': to_unicode(''),
                'diagnosticMessage': to_unicode(message),
                'referral': None
                }

    def mock_compare(self, request_message, controls):
        # CompareRequest ::= [APPLICATION 14] SEQUENCE {
        #     entry           LDAPDN,
        #     ava             AttributeValueAssertion }
        #
        # CompareResponse ::= [APPLICATION 15] LDAPResult
        #
        # request: entry, attribute, value
        # response: LDAPResult
        request = compare_request_to_dict(request_message)
        dn = safe_dn(request['entry'])
        attribute = request['attribute']
        value = to_raw(request['value'])
        if dn in self.connection.server.dit:
            if attribute in self.connection.server.dit[dn]:
                if value in self.connection.server.dit[dn][attribute]:
                    result_code = 6
                    message = ''
                else:
                    result_code = 5
                    message = ''
            else:
                result_code = 16
                message = 'attribute not found'
        else:
            result_code = 32
            message = 'object not found'

        return {'resultCode': result_code,
                'matchedDN': to_unicode(''),
                'diagnosticMessage': to_unicode(message),
                'referral': None
                }

    def mock_modify_dn(self, request_message, controls):
        # ModifyDNRequest ::= [APPLICATION 12] SEQUENCE {
        #     entry           LDAPDN,
        #     newrdn          RelativeLDAPDN,
        #     deleteoldrdn    BOOLEAN,
        #     newSuperior     [0] LDAPDN OPTIONAL }
        #
        # ModifyDNResponse ::= [APPLICATION 13] LDAPResult
        #
        # request: entry, newRdn, deleteOldRdn, newSuperior
        # response: LDAPResult
        request = modify_dn_request_to_dict(request_message)
        dn = safe_dn(request['entry'])
        new_rdn = request['newRdn']
        delete_old_rdn = request['deleteOldRdn']
        new_superior = safe_dn(request['newSuperior']) if request['newSuperior'] else ''
        dn_components = to_dn(dn)
        if dn in self.connection.server.dit:
            if new_superior and new_rdn:  # performs move in the DIT
                self.connection.server.dit[safe_dn(dn_components[0] + ',' + new_superior)] = self.connection.server.dit[dn].copy()
                if delete_old_rdn:
                    del self.connection.server.dit[dn]
                result_code = 0
                message = 'entry moved'
            elif new_rdn and not new_superior:  # performs rename
                self.connection.server.dit[safe_dn(new_rdn + ',' + safe_dn(dn_components[1:]))] = self.connection.server.dit[dn].copy()
                del self.connection.server.dit[dn]
                result_code = 0
                message = 'entry rdn renamed'
            else:
                result_code = 53
                message = 'newRdn or newSuperior missing'
        else:
            result_code = 32
            message = 'object not found'

        return {'resultCode': result_code,
                'matchedDN': to_unicode(''),
                'diagnosticMessage': to_unicode(message),
                'referral': None
                }

    def mock_modify(self, request_message, controls):
        # ModifyRequest ::= [APPLICATION 6] SEQUENCE {
        #     object          LDAPDN,
        #     changes         SEQUENCE OF change SEQUENCE {
        #         operation       ENUMERATED {
        #             add     (0),
        #             delete  (1),
        #             replace (2),
        #             ...  },
        #         modification    PartialAttribute } }
        #
        # ModifyResponse ::= [APPLICATION 7] LDAPResult
        #
        # request: entry, changes
        # response: LDAPResult
        #
        # changes is a dictionary in the form {'attribute': [(operation, [val1, ...]), ...], ...}
        # operation is 0 (add), 1 (delete), 2 (replace), 3 (increment)
        request = modify_request_to_dict(request_message)
        dn = safe_dn(request['entry'])
        changes = request['changes']
        result_code = 0
        message = ''
        rdns = [rdn[0] for rdn in safe_rdn(dn, decompose=True)]
        if dn in self.connection.server.dit:
            original_entry = self.connection.server.dit[dn].copy()  # to preserve atomicity of operation
            for modification in changes:
                operation = modification['operation']
                attribute = modification['attribute']['type']
                elements = modification['attribute']['value']
                if operation == 0:  # add
                    if attribute not in self.connection.server.dit[dn] and elements:  # attribute not present, creates the new attribute and add elements
                        self.connection.server.dit[dn][attribute] = [to_raw(element) for element in elements]
                    else:  # attribute present, adds elements to current values
                        self.connection.server.dit[dn][attribute].extend([to_raw(element) for element in elements])
                elif operation == 1:  # delete
                    if attribute not in self.connection.server.dit[dn]:  # attribute must exist
                        result_code = 16
                        message = 'attribute must exists for deleting its values'
                    elif attribute in rdns:  # attribute can't be used in dn
                        result_code = 67
                        message = 'cannot delete an rdn'
                    else:
                        if not elements:  # deletes whole attribute if element list is empty
                            del self.connection.server.dit[dn][attribute]
                        else:
                            for element in elements:
                                raw_element = to_raw(element)
                                if raw_element in self.connection.server.dit[dn][attribute]:  # removes single element
                                    self.connection.server.dit[dn][attribute].remove(raw_element)
                                else:
                                    result_code = 1
                                    message = 'value to delete not found'
                            if not self.connection.server.dit[dn][attribute]:  # removes the whole attribute if no elements remained
                                del self.connection.server.dit[dn][attribute]
                elif operation == 2:  # replace
                    if attribute not in self.connection.server.dit[dn] and elements:  # attribute not present, creates the new attribute and add elements
                        self.connection.server.dit[dn][attribute] = [to_raw(element) for element in elements]
                    elif not elements and attribute in rdns:  # attribute can't be used in dn
                        result_code = 67
                        message = 'cannot replace an rdn'
                    elif not elements:  # deletes whole attribute if element list is empty
                        if attribute in self.connection.server.dit[dn]:
                            del self.connection.server.dit[dn][attribute]
                    else:  # substitutes elements
                        self.connection.server.dit[dn][attribute] = [to_raw(element) for element in elements]

            if result_code:  # an error has happened, restores the original dn
                self.connection.server.dit[dn] = original_entry
        else:
            result_code = 32
            message = 'object not found'

        return {'resultCode': result_code,
                'matchedDN': to_unicode(''),
                'diagnosticMessage': to_unicode(message),
                'referral': None
                }

    def mock_search(self, request_message, controls):
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
        #
        # SearchResultEntry ::= [APPLICATION 4] SEQUENCE {
        #     objectName      LDAPDN,
        #     attributes      PartialAttributeList }
        #
        #
        # SearchResultReference ::= [APPLICATION 19] SEQUENCE
        #     SIZE (1..MAX) OF uri URI
        #
        # SearchResultDone ::= [APPLICATION 5] LDAPResult
        #
        # request: base, scope, dereferenceAlias, sizeLimit, timeLimit, typesOnly, filter, attributes
        # response_entry: object, attributes
        # response_done: LDAPResult
        request = search_request_to_dict(request_message)
        responses = []
        base = safe_dn(request['base'])
        scope = request['scope']
        attributes = request['attributes']
        filter_root = parse_filter(request['filter'], self.connection.server.schema)
        candidates = []
        if scope == 0:  # base object
            if base in self.connection.server.dit:
                candidates.append(base)
        elif scope == 1:  # single level
            for entry in self.connection.server.dit:
                if entry.endswith(base) and ',' not in entry[:-len(base) - 1]:  # only leafs without commas in the remaining dn
                    candidates.append(entry)
        elif scope == 2:  # whole subtree
            for entry in self.connection.server.dit:
                if entry.endswith(base):
                    candidates.append(entry)

        if not candidates:  # incorrect base
            result_code = 32
            message = 'incorrect base object'
        else:
            matched = self.evaluate_filter_node(filter_root, candidates)
            for match in matched:
                responses.append({
                    'object': match,
                    'attributes': [{'type': attribute,
                                    'vals': [] if request['typesOnly'] else self.connection.server.dit[match][attribute]}
                                   for attribute in self.connection.server.dit[match]
                                   if attribute in attributes]
                })

            result_code = 0
            message = ''

        result = {'resultCode': result_code,
                  'matchedDN': to_unicode(''),
                  'diagnosticMessage': to_unicode(message),
                  'referral': None
                  }

        return responses[:request['sizeLimit']] if request['sizeLimit'] > 0 else responses, result

    def evaluate_filter_node(self, node, candidates):
        """After evaluation each 2 sets are added to each MATCH node, one for the matched object and one for unmatched object.
        The unmatched object set is needed if a superior node is a NOT that reverts the evaluation. The BOOLEAN nodes mix the sets
        returned by the MATCH nodes"""
        node.matched = set()
        node.unmatched = set()

        if node.elements:
            for element in node.elements:
                self.evaluate_filter_node(element, candidates)

        if node.tag == ROOT:
            return node.elements[0].matched
        elif node.tag == AND:
            for element in node.elements:
                if not node.matched:
                    node.matched.update(element.matched)
                else:
                    node.matched.intersection_update(element.matched)
                if not node.unmatched:
                    node.unmatched.update(element.unmatched)
                else:
                    node.unmatched.intersection_update(element.unmatched)
        elif node.tag == OR:
            for element in node.elements:
                node.matched.update(element.matched)
                node.unmatched.update(element.unmatched)
        elif node.tag == NOT:
            node.matched = node.elements[0].unmatched
            node.unmatched = node.elements[0].matched
        elif node.tag == MATCH_GREATER_OR_EQUAL:
            attr_name = node.assertion['attr']
            attr_value = node.assertion['value']
            for candidate in candidates:
                if attr_name in self.connection.server.dit[candidate]:
                    for value in self.connection.server.dit[candidate][attr_name]:
                        if value.isdigit() and attr_value.isdigit():  # int comparison
                            if int(value) >= int(attr_value):
                                node.matched.add(candidate)
                            else:
                                node.unmatched.add(candidate)
                        else:
                            if to_unicode(value).lower() >= to_unicode(attr_value).lower():  # case insentive string comparison
                                node.matched.add(candidate)
                            else:
                                node.unmatched.add(candidate)
        elif node.tag == MATCH_LESS_OR_EQUAL:
            attr_name = node.assertion['attr']
            attr_value = node.assertion['value']
            for candidate in candidates:
                if attr_name in self.connection.server.dit[candidate]:
                    for value in self.connection.server.dit[candidate][attr_name]:
                        if value.isdigit() and attr_value.isdigit():  # int comparison
                            if int(value) <= int(attr_value):
                                node.matched.add(candidate)
                            else:
                                node.unmatched.add(candidate)
                        else:
                            if to_unicode(value).lower() <= to_unicode(attr_value).lower():  # case insentive string comparison
                                node.matched.add(candidate)
                            else:
                                node.unmatched.add(candidate)
        elif node.tag == MATCH_EXTENSIBLE:
            pass
        elif node.tag == MATCH_PRESENT:
            attr_name = node.assertion['attr']
            for candidate in candidates:
                if attr_name in self.connection.server.dit[candidate]:
                    node.matched.add(candidate)
                else:
                    node.unmatched.add(candidate)
        elif node.tag == MATCH_SUBSTRING:
            attr_name = node.assertion['attr']
            # rebuild the original substring filter
            if node.assertion['initial']:
                substring_filter = re.escape(to_unicode(node.assertion['initial']))
            else:
                substring_filter = ''

            if node.assertion['any']:
                for middle in node.assertion['any']:
                    substring_filter += '.*' + re.escape(to_unicode(middle))

            if node.assertion['final']:
                substring_filter += '.*' + re.escape(to_unicode(node.assertion['final']))

            if substring_filter and not node.assertion['any'] and not node.assertion['final']:  # onyly initial, adds .*
                substring_filter += '.*'

            regex_filter = re.compile(substring_filter, flags=re.UNICODE)
            for candidate in candidates:
                if attr_name in self.connection.server.dit[candidate]:
                    for value in self.connection.server.dit[candidate][attr_name]:
                        if regex_filter.match(to_unicode(value)):
                            node.matched.add(candidate)
                        else:
                            node.unmatched.add(candidate)
                else:
                    node.unmatched.add(candidate)
        elif node.tag == MATCH_EQUAL or node.tag == MATCH_APPROX:
            attr_name = node.assertion['attr']
            attr_value = node.assertion['value']
            for candidate in candidates:
                if attr_name in self.connection.server.dit[candidate] and attr_value in self.connection.server.dit[candidate][attr_name]:
                    node.matched.add(candidate)
                else:
                    node.unmatched.add(candidate)


