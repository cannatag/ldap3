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

from .mockBase import MockBaseStrategy
from .async import AsyncStrategy

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


class MockAsyncStrategy(MockBaseStrategy, AsyncStrategy):  # class inheritance sequence is important, MockBaseStrategy must be the first one
    """
    This strategy create a mock LDAP server, with asynchronous access
    It can be useful to test LDAP without accessing a real Server
    """
    def __init__(self, ldap_connection):
        AsyncStrategy.__init__(self, ldap_connection)
        MockBaseStrategy.__init__(self)


