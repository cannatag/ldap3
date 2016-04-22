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
from ldap3.operation.bind import bind_response_to_dict
from ..strategy.sync import SyncStrategy
from ..utils.conv import to_unicode


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

    def send(self, message_type, request, controls=None):
        self.connection.request = None
        if self.connection.listening:
            return message_type, request, controls

        return None, None, None

    def _start_listen(self):
        self.connection.listening = True

    def _stop_listen(self):
        self.connection.listening = False

    def _open_socket(self, address, use_ssl=False, unix_socket=False):
        self.connection.socket = NotImplemented  # placeholder for a dummy socket
        if self.connection.usage:
            self.connection._usage.open_sockets += 1

        self.connection.closed = False

    def _close_socket(self):
        if self.connection.usage:
            self.connection._usage.closed_sockets += 1

        self.connection.socket = None
        self.connection.closed = True

    def post_send_search(self, message_type, request, controls=None):
        return None

    def post_send_single_response(self, (message_type, request, controls)):
        responses = []
        result = None
        if message_type == 'bindRequest':
            result = bind_response_to_dict(self.mock_bind_request(message_type, request, controls))

        self.connection.result = result
        responses.append(result)
        return responses

    def mock_bind_request(self, message_type, request, controls):
        # BindResponse ::= [APPLICATION 1] SEQUENCE {
        #     COMPONENTS OF LDAPResult,
        #     serverSaslCreds    [7] OCTET STRING OPTIONAL }
        result = {'resultCode': 0,
                  'matchedDN': to_unicode(''),
                  'diagnosticMessage': to_unicode(''),
                  'referral': None,
                  'serverSaslCreds': None
                 }

        return result
