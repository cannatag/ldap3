"""
"""

# Created on 2013.05.15
#
# @author: Giovanni Cannata
#
# Copyright 2013 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

__version__ = '0.9.5.4'
__author__ = 'Giovanni Cannata'

# authentication
AUTH_ANONYMOUS = 0
AUTH_SIMPLE = 1
AUTH_SASL = 2
SASL_AVAILABLE_MECHANISMS = ['EXTERNAL', 'DIGEST-MD5']

AUTO_BIND_NONE = 0
AUTO_BIND_NO_TLS = 1
AUTO_BIND_TLS_BEFORE_BIND = 2
AUTO_BIND_TLS_AFTER_BIND = 3

AUTHZ_STATE_CLOSED = 0
AUTHZ_STATE_ANONYMOUS = 1
AUTHZ_STATE_UNAUTHENTICATED = 2

# search scope
SEARCH_SCOPE_BASE_OBJECT = 0
SEARCH_SCOPE_SINGLE_LEVEL = 1
SEARCH_SCOPE_WHOLE_SUBTREE = 2

# search alias
SEARCH_NEVER_DEREFERENCE_ALIASES = 0
SEARCH_DEREFERENCE_IN_SEARCHING = 1
SEARCH_DEREFERENCE_FINDING_BASE_OBJECT = 2
SEARCH_DEREFERENCE_ALWAYS = 3

# search attributes
ALL_ATTRIBUTES = '*'
NO_ATTRIBUTES = '1.1'  # as per RFC 4511
ALL_OPERATIONAL_ATTRIBUTES = '+'  # as per RFC 3673

#checks
ATTRIBUTES_EXCLUDED_FROM_CHECK = [ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, NO_ATTRIBUTES, 'ldapSyntaxes', 'matchingRules', 'matchingRuleUse', 'dITContentRules', 'dITStructureRules', 'nameForms']
CASE_INSENSITIVE_ATTRIBUTE_NAMES = True
CASE_INSENSITIVE_SCHEMA_NAMES = True

# modify type
MODIFY_ADD = 0
MODIFY_DELETE = 1
MODIFY_REPLACE = 2
MODIFY_INCREMENT = 3

# client strategies
STRATEGY_SYNC = 0
STRATEGY_ASYNC_THREADED = 1
STRATEGY_LDIF_PRODUCER = 2
STRATEGY_SYNC_RESTARTABLE = 3
STRATEGY_REUSABLE_THREADED = 4

CLIENT_STRATEGIES = [STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, STRATEGY_LDIF_PRODUCER, STRATEGY_SYNC_RESTARTABLE, STRATEGY_REUSABLE_THREADED]

# communication
SESSION_TERMINATED_BY_SERVER = 0
RESPONSE_COMPLETE = -1
RESPONSE_SLEEPTIME = 0.02  # seconds to wait while waiting for a response in asynchronous strategies
RESPONSE_WAITING_TIMEOUT = 10  # waiting timeout for receiving a response in asynchronous strategies
SOCKET_SIZE = 4096  # socket byte size

# restartable strategy
RESTARTABLE_SLEEPTIME = 2  # time to wait in a restartable strategy before retrying the request
RESTARTABLE_TRIES = 50  # number of times to retry in a restartable strategy before giving up. Set to True for unlimited retries

# reusable strategies (Threaded)
TERMINATE_REUSABLE = -1
REUSABLE_THREADED_POOL_SIZE = 10
REUSABLE_THREADED_LIFETIME = 3600  # 1 hour
DEFAULT_THREADED_POOL_NAME = 'connection_threaded_pool'


# LDAP protocol
LDAP_MAX_INT = 2147483647

# LDIF
LDIF_LINE_LENGTH = 78

# result codes
RESULT_SUCCESS = 0
RESULT_OPERATIONS_ERROR = 1
RESULT_PROTOCOL_ERROR = 2
RESULT_TIME_LIMIT_EXCEEDED = 3
RESULT_SIZE_LIMIT_EXCEEDED = 4
RESULT_COMPARE_FALSE = 5
RESULT_COMPARE_TRUE = 6
RESULT_AUTH_METHOD_NOT_SUPPORTED = 7
RESULT_STRONGER_AUTH_REQUIRED = 8
RESULT_REFERRAL = 10
RESULT_ADMIN_LIMIT_EXCEEDED = 11
RESULT_UNAVAILABLE_CRITICAL_EXTENSION = 12
RESULT_CONFIDENTIALITY_REQUIRED = 13
RESULT_SASL_BIND_IN_PROGRESS = 14
RESULT_NO_SUCH_ATTRIBUTE = 16
RESULT_UNDEFINED_ATTRIBUTE_TYPE = 17
RESULT_INAPPROPRIATE_MATCHING = 18
RESULT_CONSTRAINT_VIOLATION = 19
RESULT_ATTRIBUTE_OR_VALUE_EXISTS = 20
RESULT_INVALID_ATTRIBUTE_SYNTAX = 21
RESULT_NO_SUCH_OBJECT = 32
RESULT_ALIAS_PROBLEM = 33
RESULT_INVALID_DN_SYNTAX = 34
RESULT_ALIAS_DEREFERENCING_PROBLEM = 36
RESULT_INAPPROPRIATE_AUTHENTICATION = 48
RESULT_INVALID_CREDENTIALS = 49
RESULT_INSUFFICIENT_ACCESS_RIGHTS = 50
RESULT_BUSY = 51
RESULT_UNAVAILABLE = 52
RESULT_UNWILLING_TO_PERFORM = 53
RESULT_LOOP_DETECTED = 54
RESULT_NAMING_VIOLATION = 64
RESULT_OBJECT_CLASS_VIOLATION = 65
RESULT_NOT_ALLOWED_ON_NON_LEAF = 66
RESULT_NOT_ALLOWED_ON_RDN = 67
RESULT_ENTRY_ALREADY_EXISTS = 68
RESULT_OBJECT_CLASS_MODS_PROHIBITED = 69
RESULT_AFFECT_MULTIPLE_DSAS = 71
RESULT_OTHER = 80
RESULT_LCUP_RESOURCES_EXHAUSTED = 113
RESULT_LCUP_SECURITY_VIOLATION = 114
RESULT_LCUP_INVALID_DATA = 115
RESULT_LCUP_UNSUPPORTED_SCHEME = 116
RESULT_LCUP_RELOAD_REQUIRED = 117
RESULT_CANCELED = 118
RESULT_NO_SUCH_OPERATION = 119
RESULT_TOO_LATE = 120
RESULT_CANNOT_CANCEL = 121
RESULT_ASSERTION_FAILED = 122
RESULT_AUTHORIZATION_DENIED = 123
RESULT_E_SYNC_REFRESH_REQUIRED = 4096

# do not raise exception for (in raise_exceptions connection mode)
DO_NOT_RAISE_EXCEPTIONS = [RESULT_SUCCESS, RESULT_COMPARE_FALSE, RESULT_COMPARE_TRUE, RESULT_REFERRAL]

# get rootDSE info
GET_NO_INFO = 0
GET_DSA_INFO = 1
GET_SCHEMA_INFO = 2
GET_ALL_INFO = 3

# OID database definition
OID_CONTROL = 0
OID_EXTENSION = 1
OID_FEATURE = 2
OID_UNSOLICITED_NOTICE = 3
OID_ATTRIBUTE_TYPE = 4
OID_DIT_CONTENT_RULE = 5
OID_LDAP_URL_EXTENSION = 6
OID_FAMILY = 7
OID_MATCHING_RULE = 8
OID_NAME_FORM = 9
OID_OBJECT_CLASS = 10
OID_ADMINISTRATIVE_ROLE = 11
OID_LDAP_SYNTAX = 12

# class kind
CLASS_STRUCTURAL = 0
CLASS_ABSTRACT = 1
CLASS_AUXILIARY = 2

# attribute kind
ATTRIBUTE_USER_APPLICATION = 0
ATTRIBUTE_DIRECTORY_OPERATION = 1
ATTRIBUTE_DISTRIBUTED_OPERATION = 2
ATTRIBUTE_DSA_OPERATION = 3

# abstraction layer
ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX = 'OP_'

# server pooling
POOLING_STRATEGY_FIRST = 0
POOLING_STRATEGY_ROUND_ROBIN = 1
POOLING_STRATEGY_RANDOM = 2
POOLING_STRATEGIES = [POOLING_STRATEGY_FIRST, POOLING_STRATEGY_ROUND_ROBIN, POOLING_STRATEGY_RANDOM]


# ldap format conversion for syntaxes and attribute types
FORMAT_UNICODE = ['1.3.6.1.4.1.1466.115.121.1.3',  # Attribute type description
                  '1.3.6.1.4.1.1466.115.121.1.6',  # Bit String
                  '1.3.6.1.4.1.1466.115.121.1.11',  # Country String
                  '1.3.6.1.4.1.1466.115.121.1.12',  # Distinguished name (DN)
                  '1.3.6.1.4.1.1466.115.121.1.14',  # Delivery method
                  '1.3.6.1.4.1.1466.115.121.1.15',  # Directory string
                  '1.3.6.1.4.1.1466.115.121.1.16',  # DIT Content Rule Description
                  '1.3.6.1.4.1.1466.115.121.1.17',  # DIT Structure Rule Description
                  '1.3.6.1.4.1.1466.115.121.1.21',  # Enhanced Guide
                  '1.3.6.1.4.1.1466.115.121.1.22',  # Facsimile Telephone Number
                  '1.3.6.1.4.1.1466.115.121.1.25',  # Guide (obsolete)
                  '1.3.6.1.4.1.1466.115.121.1.26',  # IA5 string
                  '1.3.6.1.4.1.1466.115.121.1.30',  # Matching rule description
                  '1.3.6.1.4.1.1466.115.121.1.31',  # Matching ruledescription
                  '1.3.6.1.4.1.1466.115.121.1.34',  # Name and optional UID
                  '1.3.6.1.4.1.1466.115.121.1.35',  # Name form description
                  '1.3.6.1.4.1.1466.115.121.1.36',  # Mumeric string
                  '1.3.6.1.4.1.1466.115.121.1.37',  # Object class description
                  '1.3.6.1.4.1.1466.115.121.1.38',  # OID
                  '1.3.6.1.4.1.1466.115.121.1.39',  # Other mailbox
                  '1.3.6.1.4.1.1466.115.121.1.41',  # Postal address
                  '1.3.6.1.4.1.1466.115.121.1.44',  # Printable string
                  '1.3.6.1.4.1.1466.115.121.1.50',  # Telephone number
                  '1.3.6.1.4.1.1466.115.121.1.51',  # Teletex terminal identifier
                  '1.3.6.1.4.1.1466.115.121.1.52',  # Teletex number
                  '1.3.6.1.4.1.1466.115.121.1.54',  # LDAP syntax description
                  '1.3.6.1.4.1.1466.115.121.1.58'  # Substring assertion
                  ]
FORMAT_INT = ['1.3.6.1.4.1.1466.115.121.1.27',  # Integer
              '2.16.840.1.113719.1.1.5.1.22'  # Counter (Novell)
              ]
FORMAT_BINARY = ['1.3.6.1.4.1.1466.115.121.1.23',  # Fax
                 '1.3.6.1.4.1.1466.115.121.1.28',  # JPEG
                 '1.3.6.1.4.1.1466.115.121.1.40'  # Octet string
                 ]
FORMAT_UUID = ['1.3.6.1.1.16.1',  # UUID
               '2.16.840.1.113719.1.1.4.1.501',  # GUID (Novell)
               ]
FORMAT_UUID_LE = []
FORMAT_BOOLEAN = ['1.3.6.1.4.1.1466.115.121.1.7'  # Boolean
                  ]
FORMAT_TIME = ['1.3.6.1.4.1.1466.115.121.1.24',  # Generalized time
               '1.3.6.1.4.1.1466.115.121.1.53'  # Utc time  (deprecated)
               ]

# centralized imports
from .core.server import Server
from .core.connection import Connection
from .core.tls import Tls
from .core.pooling import ServerPool
from .abstract import ObjectDef, AttrDef, Attribute, Entry, Reader, OperationalAttribute
from .core.exceptions import LDAPException, LDAPExceptionError, LDAPSocketCloseError, LDAPReferralError, LDAPAttributeError, LDAPBindError, LDAPCertificateError, LDAPChangesError, LDAPCommunicationError, LDAPConnectionIsReadOnlyError, \
    LDAPConnectionPoolNameIsMandatoryError, LDAPConnectionPoolNotStartedError, LDAPControlsError, LDAPEntryError, LDAPInvalidDereferenceAliasesError, LDAPInvalidFilterError, LDAPInvalidScopeError, LDAPInvalidServerError, LDAPKeyError, LDAPLDIFError, \
    LDAPMetricsError, LDAPObjectClassError, LDAPObjectError, LDAPPasswordIsMandatoryError, LDAPReaderError, LDAPSASLBindInProgressError, LDAPSASLMechanismNotSupportedError, LDAPSASLPrepError, LDAPSchemaError, LDAPServerPoolError, \
    LDAPServerPoolExhaustedError, LDAPSocketOpenError, LDAPSocketReceiveError, LDAPSocketSendError, LDAPSSLConfigurationError, LDAPSSLNotSupportedError, LDAPStartTLSError, LDAPTypeError, LDAPUnknownAuthenticationMethodError, LDAPUnknownRequestError, \
    LDAPUnknownResponseError, LDAPUnknownStrategyError

from .core.exceptions import LDAPAdminLimitExceededResult, LDAPAffectMultipleDSASResult, LDAPAliasDereferencingProblemResult, LDAPAliasProblemResult, LDAPAssertionFailedResult, LDAPAttributeOrValueExistsResult, LDAPAuthMethodNotSupportedResult, \
    LDAPAuthorizationDeniedResult, LDAPBusyResult, LDAPCanceledResult, LDAPCannotCancelResult, LDAPConfidentialityRequiredResult, LDAPConstraintViolationResult, LDAPEntryAlreadyExistsResult, LDAPESyncRefreshRequiredResult, \
    LDAPInappropriateAuthenticationResult, LDAPInappropriateMatchingResult, LDAPInsufficientAccessRightsResult, LDAPInvalidAttributeSyntaxResult, LDAPInvalidCredentialsResult, LDAPInvalidDNSyntaxResult, LDAPLCUPInvalidDataResult, \
    LDAPLCUPReloadRequiredResult, LDAPLCUPResourcesExhaustedResult, LDAPLCUPSecurityViolationResult, LDAPLCUPUnsupportedSchemeResult, LDAPLoopDetectedResult, LDAPNamingViolationResult, LDAPNoSuchAttributeResult, LDAPNoSuchObjectResult, \
    LDAPNoSuchOperationResult, LDAPNotAllowedOnNotLeafResult, LDAPNotAllowedOnRDNResult, LDAPObjectClassModsProhibitedResult, LDAPObjectClassViolationResult, LDAPOperationResult, LDAPOperationsErrorResult, LDAPOtherResult, LDAPProtocolErrorResult, \
    LDAPReferralResult, LDAPSASLBindInProgressResult, LDAPSizeLimitExceededResult, LDAPStrongerAuthRequiredResult, LDAPTimeLimitExceededResult, LDAPTooLateResult, LDAPUnavailableCriticalExtensionResult, LDAPUnavailableResult, \
    LDAPUndefinedAttributeTypeResult, LDAPUnwillingToPerformResult, LDAPMaximumRetriesError, LDAPExtensionError
