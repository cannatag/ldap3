"""
"""

# Created on 2014.11.17
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
import json

from ..operation.bind import bind_request_to_dict, bind_response_to_dict
from ..operation.delete import delete_request_to_dict, delete_response_to_dict
from ..operation.add import add_request_to_dict, add_response_to_dict
from ..operation.compare import compare_request_to_dict, compare_response_to_dict
from ..operation.modifyDn import modify_dn_request_to_dict, modify_dn_response_to_dict
from ..operation.modify import modify_request_to_dict, modify_response_to_dict
from ..operation.search import search_request_to_dict, search_result_done_response_to_dict, search_result_entry_response_to_dict
from ..strategy.sync import SyncStrategy
from ..utils.conv import to_unicode
from ..utils.conv import json_hook, check_escape
from ..core.exceptions import LDAPDefinitionError
from ..utils.ciDict import CaseInsensitiveDict
from ..utils.dn import to_dn, safe_dn, safe_rdn


# LDAPResult ::= SEQUENCE {
#     resultCode         ENUMERATED {
#         success                      (0),
#         operationsError              (1),
#         protocolError                (2),
#         timeLimitExceeded            (3),
#         sizeLimitExceeded            (4),
#         compareFalse                 (5),
#         compareTrue                  (6),
#         authMethodNotSupported       (7),
#         strongerAuthRequired         (8),
#              -- 9 reserved --
#         referral                     (10),
#         adminLimitExceeded           (11),
#         unavailableCriticalExtension (12),
#         confidentialityRequired      (13),
#         saslBindInProgress           (14),
#         noSuchAttribute              (16),
#         undefinedAttributeType       (17),
#         inappropriateMatching        (18),
#         constraintViolation          (19),
#         attributeOrValueExists       (20),
#         invalidAttributeSyntax       (21),
#              -- 22-31 unused --
#         noSuchObject                 (32),
#         aliasProblem                 (33),
#         invalidDNSyntax              (34),
#              -- 35 reserved for undefined isLeaf --
#         aliasDereferencingProblem    (36),
#              -- 37-47 unused --
#         inappropriateAuthentication  (48),
#         invalidCredentials           (49),
#         insufficientAccessRights     (50),
#         busy                         (51),
#         unavailable                  (52),
#         unwillingToPerform           (53),
#         loopDetect                   (54),
#              -- 55-63 unused --
#         namingViolation              (64),
#         objectClassViolation         (65),
#         notAllowedOnNonLeaf          (66),
#         notAllowedOnRDN              (67),
#         entryAlreadyExists           (68),
#         objectClassModsProhibited    (69),
#              -- 70 reserved for CLDAP --
#         affectsMultipleDSAs          (71),
#              -- 72-79 unused --
#         other                        (80),
#         ...  },
#     matchedDN          LDAPDN,
#     diagnosticMessage  LDAPString,
#     referral           [3] Referral OPTIONAL }


# noinspection PyProtectedMember
class MockSyncStrategy(SyncStrategy):
    """
    This strategy create a mock LDAP server, with synchronous access
    It can be useful to test LDAP without a real Server
    """
    def __init__(self, ldap_connection):
        SyncStrategy.__init__(self, ldap_connection)
        self.sync = True
        self.no_real_dsa = True
        self.pooled = False
        self.can_stream = False
        self.entries = dict()
        self.bound = None

    def send(self, message_type, request, controls=None):
        self.connection.request = None
        if self.connection.listening:
            return message_type, request, controls

        return None, None, None

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

    def add_user(self, identity, password):
        if identity not in self.entries:
            self.add_entry(identity, {'userPassword': password})
            return True
        return False

    def remove_user(self, identity):
        if identity in self.entries:
            del self.entries[identity]
            return True
        return False

    def add_entry(self, dn, attributes):
        escaped_dn = safe_dn(dn)
        if escaped_dn not in self.entries:
            self.entries[escaped_dn] = attributes
            for rdn in safe_rdn(escaped_dn, decompose=True):  # adds rdns to entry attributes
                if rdn[0] not in self.entries[escaped_dn]:  # if rdn attribute is missing adds attribute and its value
                    self.entries[escaped_dn][rdn[0]] = rdn[1]
                else:
                    if rdn[1] not in self.entries[escaped_dn][rdn[0]]:  # add rdn value if rdn attribute is present but value is missing
                        self.entries[escaped_dn][rdn[0]].append(rdn[1])
            return True
        return False

    def remove_entry(self, dn):
        escaped_dn = safe_dn(dn)
        if escaped_dn in self.entries:
            del self.entries[escaped_dn]
            return True
        return False

    def users_from_json(self, json_user_file):
        target = open(json_user_file, 'r')
        definition = json.load(target, object_hook=json_hook)
        if 'users' not in definition:
            raise LDAPDefinitionError('invalid JSON definition, missing "users" section')

        if not self.entries:
            self.entries = CaseInsensitiveDict()
        for user in definition['users']:
            if 'identity' not in user:
                raise LDAPDefinitionError('invalid JSON definition, missing "identity" section')
            if 'password' not in user:
                raise LDAPDefinitionError('invalid JSON definition, missing "password" section')
            self.add_entry(user['identity'], {'userPassword': user['password']})
        target.close()

    def entries_from_json(self, json_entry_file):
        target = open(json_entry_file, 'r')
        definition = json.load(target, object_hook=json_hook)
        if 'entries' not in definition:
            raise LDAPDefinitionError('invalid JSON definition, missing "entries" section')

        if not self.entries:
            self.entries = CaseInsensitiveDict()

        for entry in definition['entries']:
            if 'raw' not in entry:
                raise LDAPDefinitionError('invalid JSON definition, missing "raw" section')
            attributes = CaseInsensitiveDict()

            for attribute in entry['raw']:
                attributes[attribute] = check_escape(entry['raw'][attribute])

            if 'dn' not in entry:
                raise LDAPDefinitionError('invalid JSON definition, missing "raw" section')
            self.entries[safe_dn(entry['dn'])] = attributes
        target.close()

    def post_send_search(self, payload):
        message_type, request, controls = payload
        responses = []
        self.connection.response = []
        self.connection.result = dict()
        if message_type == 'searchRequest':
            responses, result = self.mock_search(request, controls)
            result['type'] = 'searchResDone'

        for entry in responses:
            response = search_result_entry_response_to_dict(entry, self.connection.server.schema, self.connection.server.custom_formatter, self.connection.check_names)
            response['type'] = 'searchResEntry'
            self.connection.response.append(response)
        result = search_result_done_response_to_dict(result)
        result['type'] = 'searchResDone'
        self.connection.result = result
        return responses

    def post_send_single_response(self, payload):  # payload is a tuple sent by self.send() made of message_type, request, controls
        message_type, request, controls = payload
        responses = []
        result = None
        if message_type == 'bindRequest':
            result = bind_response_to_dict(self.mock_bind(request, controls))
            result['type'] = 'bindResponse'
        elif message_type == 'unbindRequest':
            self.bound = None
        elif message_type == 'abandonRequest':
            pass
        elif message_type == 'delRequest':
            result = delete_response_to_dict(self.mock_delete(request, controls))
            result['type'] = 'delResponse'
        elif message_type == 'addRequest':
            result = add_response_to_dict(self.mock_add(request, controls))
            result['type'] = 'addResponse'
        elif message_type == 'compareRequest':
            result = compare_response_to_dict(self.mock_compare(request, controls))
            result['type'] = 'compareResponse'
        elif message_type == 'modDNRequest':
            result = modify_dn_response_to_dict(self.mock_modify_dn(request, controls))
            result['type'] = 'modDNResponse'
        elif message_type == 'modifyRequest':
            result = modify_response_to_dict(self.mock_modify(request, controls))
            result['type'] = 'modifyResponse'
        self.connection.result = result
        responses.append(result)
        return responses

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
            password = request['authentication']['simple']
        else:
            raise LDAPDefinitionError('only Simple bind allowed in Mock strategy')
        # checks userPassword for password. userPassword must be a clear text string or a list of clear text strings
        if identity in self.entries and 'userPassword' in self.entries[identity] and (self.entries[identity]['userPassword'] == password or password in self.entries[identity]['userPassword']):
            result_code = 0
            message = ''
            self.bound = identity
        else:  # no user found,  waits for 2 seconds returns invalidCredentials
            result_code = 49
            message = 'invalid credentials'

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
        if dn in self.entries:
            del self.entries[dn]
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
        if dn not in self.entries:
            self.entries[dn] = CaseInsensitiveDict(attributes)
            result_code = 0
            message = ''
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
        value = request['value']
        if dn in self.entries:
            if attribute in self.entries[dn]:
                if self.entries[dn][attribute] == value:
                    result_code = 6
                    message = ''
                else:
                    result_code = 5
                    message = ''
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
        if dn in self.entries:
            if new_superior and new_rdn:  # performs move in the DIT
                self.entries[safe_dn(dn_components[0] + ',' + new_superior)] = self.entries[dn].copy()
                if delete_old_rdn:
                    del self.entries[dn]
                result_code = 0
                message = 'entry moved'
            elif new_rdn and not new_superior:  # performs rename
                self.entries[safe_dn(new_rdn + ',' + safe_dn(dn_components[1:]))] = self.entries[dn].copy()
                del self.entries[dn]
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
        if dn in self.entries:
            original_entry = self.entries[dn].copy()  # to preserve atomicity of operation
            for modification in changes:
                operation = modification['operation']
                attribute = modification['attribute']['type']
                elements = modification['attribute']['value']
                if operation == 0:  # add
                    if attribute not in self.entries[dn] and elements:  # attribute not present, creates the new attribute and add elements
                        self.entries[dn][attribute] = elements
                    else:  # attribute present, adds elements to current values
                        self.entries[dn][attribute].extend(elements)
                elif operation == 1:  # delete
                    if attribute not in self.entries[dn]:  # attribute must exist
                        result_code = 16
                        message = 'attribute must exists for deleting its values'
                    elif attribute in rdns:  # attribute can't be used in dn
                        result_code = 67
                        message = 'cannot delete an rdn'
                    else:
                        if not elements:  # deletes whole attribute if element list is empty
                            del self.entries[dn][attribute]
                        else:
                            for element in elements:
                                if element in self.entries[dn][attribute]:  # removes single element
                                    self.entries[dn][attribute].remove(element)
                                else:
                                    result_code = 1
                                    message = 'value to delete not found'
                            if not self.entries[dn][attribute]:  # removes the whole attribute if no elements remained
                                del self.entries[dn][attribute]
                elif operation == 2:  # replace
                    if attribute not in self.entries[dn] and elements:  # attribute not present, creates the new attribute and add elements
                        self.entries[dn][attribute] = elements
                    elif not elements and attribute in rdns:  # attribute can't be used in dn
                        result_code = 67
                        message = 'cannot replace an rdn'
                    elif not elements:  # deletes whole attribute if element list is empty
                        if attribute in self.entries[dn]:
                            del self.entries[dn][attribute]
                    else:  # substitutes elements
                        self.entries[dn][attribute] = elements

            if result_code:  # an error has happened, restores the original dn
                self.entries[dn] = original_entry
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
        print(request)
        responses = [{'object': 'cn=test100,ou=test,o=lab',
                      'attributes': [{'type': 'sn', 'vals': [b'a0', b'b0']},
                                     {'type': 'cn', 'vals': [b'test100']}]},
                     {'object': 'cn=test101,ou=test,o=lab',
                      'attributes': [{'type': 'sn', 'vals': [b'a1', b'b1']},
                                     {'type': 'cn', 'vals': [b'test101']}]}
                    ]
        result_code = 0
        message = ''
        result = {'resultCode': result_code,
                  'matchedDN': to_unicode(''),
                  'diagnosticMessage': to_unicode(message),
                  'referral': None
                  }

        return responses, result
