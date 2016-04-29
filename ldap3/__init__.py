"""
"""

# Created on 2013.05.15
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

# authentication
ANONYMOUS = 'ANONYMOUS'
SIMPLE = 'SIMPLE'
SASL = 'SASL'
NTLM = 'NTLM'

# SASL MECHANISMS
EXTERNAL = 'EXTERNAL'
DIGEST_MD5 = 'DIGEST-MD5'
KERBEROS = GSSAPI = 'GSSAPI'

SASL_AVAILABLE_MECHANISMS = [EXTERNAL, DIGEST_MD5, GSSAPI]

AUTO_BIND_NONE = 'NONE'  # same as False
AUTO_BIND_NO_TLS = 'NO_TLS'  # same as True
AUTO_BIND_TLS_BEFORE_BIND = 'TLS_BEFORE_BIND'
AUTO_BIND_TLS_AFTER_BIND = 'TLS_AFTER_BIND'

# server IP dual stack mode
IP_SYSTEM_DEFAULT = 'IP_SYSTEM_DEFAULT'
IP_V4_ONLY = 'IP_V4_ONLY'
IP_V6_ONLY = 'IP_V6_ONLY'
IP_V4_PREFERRED = 'IP_V4_PREFERRED'
IP_V6_PREFERRED = 'IP_V6_PREFERRED'
ADDRESS_INFO_REFRESH_TIME = 300  # seconds to wait before refreshing address info from dns

# search scope
BASE = 'BASE'
LEVEL = 'LEVEL'
SUBTREE = 'SUBTREE'

# search alias
DEREF_NEVER = 'NEVER'
DEREF_SEARCH = 'SEARCH'
DEREF_BASE = 'FINDING_BASE'
DEREF_ALWAYS = 'ALWAYS'

# search attributes
ALL_ATTRIBUTES = '*'
NO_ATTRIBUTES = '1.1'  # as per RFC 4511
ALL_OPERATIONAL_ATTRIBUTES = '+'  # as per RFC 3673

CASE_INSENSITIVE_ATTRIBUTE_NAMES = True  # configurable parameter
CASE_INSENSITIVE_SCHEMA_NAMES = True  # configurable parameter

# checks
ATTRIBUTES_EXCLUDED_FROM_CHECK = [ALL_ATTRIBUTES,
                                  ALL_OPERATIONAL_ATTRIBUTES,
                                  NO_ATTRIBUTES,
                                  'ldapSyntaxes',
                                  'matchingRules',
                                  'matchingRuleUse',
                                  'dITContentRules',
                                  'dITStructureRules',
                                  'nameForms',
                                  'altServer',
                                  'namingContexts',
                                  'supportedControl',
                                  'supportedExtension',
                                  'supportedFeatures',
                                  'supportedCapabilities',
                                  'supportedLdapVersion',
                                  'supportedSASLMechanisms',
                                  'vendorName',
                                  'vendorVersion',
                                  'subschemaSubentry',
                                  'ACL']

# modify type
MODIFY_ADD = 'MODIFY_ADD'
MODIFY_DELETE = 'MODIFY_DELETE'
MODIFY_REPLACE = 'MODIFY_REPLACE'
MODIFY_INCREMENT = 'MODIFY_INCREMENT'

# client strategies
SYNC = 'SYNC'
ASYNC = 'ASYNC'
LDIF = 'LDIF'
RESTARTABLE = 'RESTARTABLE'
REUSABLE = 'REUSABLE'
MOCK_SYNC = 'MOCK_SYNC'
MOCK_ASYNC = 'MOCK_ASYNC'

CLIENT_STRATEGIES = [SYNC,
                     ASYNC,
                     LDIF,
                     RESTARTABLE,
                     REUSABLE,
                     MOCK_SYNC]

# get rootDSE info
NONE = 'NO_INFO'
DSA = 'DSA'
SCHEMA = 'SCHEMA'
ALL = 'ALL'

OFFLINE_EDIR_8_8_8 = 'EDIR_8_8_8'
OFFLINE_AD_2012_R2 = 'AD_2012_R2'
OFFLINE_SLAPD_2_4 = 'SLAPD_2_4'
OFFLINE_DS389_1_3_3 = 'DS389_1_3_3'

# abstraction layer
ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX = 'OPER_'  # configurable parameter

# server pooling
FIRST = 'FIRST'
ROUND_ROBIN = 'ROUND_ROBIN'
RANDOM = 'RANDOM'

POOLING_STRATEGIES = [FIRST, ROUND_ROBIN, RANDOM]
POOLING_LOOP_TIMEOUT = 10  # number of seconds to wait before restarting a cycle to find an active server in the pool - configurable parameter

# communication
SESSION_TERMINATED_BY_SERVER = 'TERMINATED_BY_SERVER'
TRANSACTION_ERROR = 'TRANSACTION_ERROR'
RESPONSE_COMPLETE = 'RESPONSE_FROM_SERVER_COMPLETE'
RESPONSE_SLEEPTIME = 0.05  # seconds to wait while waiting for a response in asynchronous strategies - configurable parameter
RESPONSE_WAITING_TIMEOUT = 20  # waiting timeout for receiving a response in asynchronous strategies - configurable parameter
SOCKET_SIZE = 4096  # socket byte size - configurable parameter
CHECK_AVAILABILITY_TIMEOUT = 2.5  # default timeout for socket connect when checking availability - configurable parameter

# restartable strategy
RESTARTABLE_SLEEPTIME = 2  # time to wait in a restartable strategy before retrying the request - configurable parameter
RESTARTABLE_TRIES = 30  # number of times to retry in a restartable strategy before giving up. Set to True for unlimited retries - configurable parameter

# reusable strategies (Threaded)
REUSABLE_THREADED_POOL_SIZE = 10  # configurable parameter
REUSABLE_THREADED_LIFETIME = 3600  # 1 hour - configurable parameter
DEFAULT_THREADED_POOL_NAME = 'reusable_default_pool'

# LDAP protocol
LDAP_MAX_INT = 2147483647

# LDIF
LDIF_LINE_LENGTH = 78

# Hashed password
HASHED_NONE = 'PLAIN'
HASHED_SHA = 'SHA'
HASHED_SHA256 = 'SHA256'
HASHED_SHA384 = 'SHA384'
HASHED_SHA512 = 'SHA512'
HASHED_MD5 = 'MD5'
HASHED_SALTED_SHA = 'SALTED_SHA'
HASHED_SALTED_SHA256 = 'SALTED_SHA256'
HASHED_SALTED_SHA384 = 'SALTED_SHA384'
HASHED_SALTED_SHA512 = 'SALTED_SHA512'
HASHED_SALTED_MD5 = 'SALTED_MD5'

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

RESULT_CODES = {
    RESULT_SUCCESS: 'success',
    RESULT_OPERATIONS_ERROR: 'operationsError',
    RESULT_PROTOCOL_ERROR: 'protocolError',
    RESULT_TIME_LIMIT_EXCEEDED: 'timeLimitExceeded',
    RESULT_SIZE_LIMIT_EXCEEDED: 'sizeLimitExceeded',
    RESULT_COMPARE_FALSE: 'compareFalse',
    RESULT_COMPARE_TRUE: 'compareTrue',
    RESULT_AUTH_METHOD_NOT_SUPPORTED: 'authMethodNotSupported',
    RESULT_STRONGER_AUTH_REQUIRED: 'strongerAuthRequired',
    RESULT_REFERRAL: 'referral',
    RESULT_ADMIN_LIMIT_EXCEEDED: 'adminLimitExceeded',
    RESULT_UNAVAILABLE_CRITICAL_EXTENSION: 'unavailableCriticalExtension',
    RESULT_CONFIDENTIALITY_REQUIRED: 'confidentialityRequired',
    RESULT_SASL_BIND_IN_PROGRESS: 'saslBindInProgress',
    RESULT_NO_SUCH_ATTRIBUTE: 'noSuchAttribute',
    RESULT_UNDEFINED_ATTRIBUTE_TYPE: 'undefinedAttributeType',
    RESULT_INAPPROPRIATE_MATCHING: 'inappropriateMatching',
    RESULT_CONSTRAINT_VIOLATION: 'constraintViolation',
    RESULT_ATTRIBUTE_OR_VALUE_EXISTS: 'attributeOrValueExists',
    RESULT_INVALID_ATTRIBUTE_SYNTAX: 'invalidAttributeSyntax',
    RESULT_NO_SUCH_OBJECT: 'noSuchObject',
    RESULT_ALIAS_PROBLEM: 'aliasProblem',
    RESULT_INVALID_DN_SYNTAX: 'invalidDNSyntax',
    RESULT_ALIAS_DEREFERENCING_PROBLEM: 'aliasDereferencingProblem',
    RESULT_INAPPROPRIATE_AUTHENTICATION: 'inappropriateAuthentication',
    RESULT_INVALID_CREDENTIALS: 'invalidCredentials',
    RESULT_INSUFFICIENT_ACCESS_RIGHTS: 'insufficientAccessRights',
    RESULT_BUSY: 'busy',
    RESULT_UNAVAILABLE: 'unavailable',
    RESULT_UNWILLING_TO_PERFORM: 'unwillingToPerform',
    RESULT_LOOP_DETECTED: 'loopDetected',
    RESULT_NAMING_VIOLATION: 'namingViolation',
    RESULT_OBJECT_CLASS_VIOLATION: 'objectClassViolation',
    RESULT_NOT_ALLOWED_ON_NON_LEAF: 'notAllowedOnNonLeaf',
    RESULT_NOT_ALLOWED_ON_RDN: 'notAllowedOnRDN',
    RESULT_ENTRY_ALREADY_EXISTS: 'entryAlreadyExists',
    RESULT_OBJECT_CLASS_MODS_PROHIBITED: 'objectClassModsProhibited',
    RESULT_AFFECT_MULTIPLE_DSAS: 'affectMultipleDSAs',
    RESULT_OTHER: 'other',
    RESULT_LCUP_RESOURCES_EXHAUSTED: 'lcupResourcesExhausted',
    RESULT_LCUP_SECURITY_VIOLATION: 'lcupSecurityViolation',
    RESULT_LCUP_INVALID_DATA: 'lcupInvalidData',
    RESULT_LCUP_UNSUPPORTED_SCHEME: 'lcupUnsupportedScheme',
    RESULT_LCUP_RELOAD_REQUIRED: 'lcupReloadRequired',
    RESULT_CANCELED: 'canceled',
    RESULT_NO_SUCH_OPERATION: 'noSuchOperation',
    RESULT_TOO_LATE: 'tooLate',
    RESULT_CANNOT_CANCEL: 'cannotCancel',
    RESULT_ASSERTION_FAILED: 'assertionFailed',
    RESULT_AUTHORIZATION_DENIED: 'authorizationDenied',
    RESULT_E_SYNC_REFRESH_REQUIRED: 'e-syncRefreshRequired'
}

# do not raise exception for (in raise_exceptions connection mode)
DO_NOT_RAISE_EXCEPTIONS = [RESULT_SUCCESS, RESULT_COMPARE_FALSE, RESULT_COMPARE_TRUE, RESULT_REFERRAL]

# types for string and sequence
if str != bytes:  # python 3
    STRING_TYPES = (str, )
else:  # python 2
    STRING_TYPES = (str, unicode)

from types import GeneratorType
SEQUENCE_TYPES = (list, tuple, GeneratorType)

# older and longer constants
AUTH_ANONYMOUS = ANONYMOUS
AUTH_SIMPLE = SIMPLE
AUTH_SASL = SASL

SEARCH_SCOPE_BASE_OBJECT = BASE
SEARCH_SCOPE_SINGLE_LEVEL = LEVEL
SEARCH_SCOPE_WHOLE_SUBTREE = SUBTREE

SEARCH_NEVER_DEREFERENCE_ALIASES = DEREF_NEVER
SEARCH_DEREFERENCE_IN_SEARCHING = DEREF_SEARCH
SEARCH_DEREFERENCE_FINDING_BASE_OBJECT = DEREF_BASE
SEARCH_DEREFERENCE_ALWAYS = DEREF_ALWAYS

STRATEGY_SYNC = SYNC
STRATEGY_ASYNC_THREADED = ASYNC
STRATEGY_LDIF_PRODUCER = LDIF
STRATEGY_SYNC_RESTARTABLE = RESTARTABLE
STRATEGY_REUSABLE_THREADED = REUSABLE
STRATEGY_MOCK_SYNC = MOCK_SYNC
STRATEGY_MOCK_ASYNC = MOCK_SYNC

POOLING_STRATEGY_FIRST = FIRST
POOLING_STRATEGY_ROUND_ROBIN = ROUND_ROBIN
POOLING_STRATEGY_RANDOM = RANDOM

GET_NO_INFO = NONE
GET_DSA_INFO = DSA
GET_SCHEMA_INFO = SCHEMA
GET_ALL_INFO = ALL


def get_config_parameter(parameter):
    if parameter == 'CASE_INSENSITIVE_ATTRIBUTE_NAMES':
        return CASE_INSENSITIVE_ATTRIBUTE_NAMES
    elif parameter == 'CASE_INSENSITIVE_SCHEMA_NAMES':
        return CASE_INSENSITIVE_SCHEMA_NAMES
    elif parameter == 'ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX':
        return ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX
    elif parameter == 'POOLING_LOOP_TIMEOUT':
        return POOLING_LOOP_TIMEOUT
    elif parameter == 'RESPONSE_SLEEPTIME':
        return RESPONSE_SLEEPTIME
    elif parameter == 'RESPONSE_WAITING_TIMEOUT':
        return RESPONSE_WAITING_TIMEOUT
    elif parameter == 'SOCKET_SIZE':
        return SOCKET_SIZE
    elif parameter == 'CHECK_AVAILABILITY_TIMEOUT':
        return CHECK_AVAILABILITY_TIMEOUT
    elif parameter == 'RESTARTABLE_SLEEPTIME':
        return RESTARTABLE_SLEEPTIME
    elif parameter == 'RESTARTABLE_TRIES':
        return RESTARTABLE_TRIES
    elif parameter == 'REUSABLE_THREADED_POOL_SIZE':
        return REUSABLE_THREADED_POOL_SIZE
    elif parameter == 'REUSABLE_THREADED_LIFETIME':
        return REUSABLE_THREADED_LIFETIME
    elif parameter == 'DEFAULT_THREADED_POOL_NAME':
        return DEFAULT_THREADED_POOL_NAME

    raise LDAPConfigurationParameterError('configuration parameter %s not valid' % parameter)


def set_config_parameter(parameter, value):
    if parameter == 'CASE_INSENSITIVE_ATTRIBUTE_NAMES':
        global CASE_INSENSITIVE_ATTRIBUTE_NAMES
        CASE_INSENSITIVE_ATTRIBUTE_NAMES = value
    elif parameter == 'CASE_INSENSITIVE_SCHEMA_NAMES':
        global CASE_INSENSITIVE_SCHEMA_NAMES
        CASE_INSENSITIVE_SCHEMA_NAMES = value
    elif parameter == 'ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX':
        global ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX
        ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX = value
    elif parameter == 'POOLING_LOOP_TIMEOUT':
        global POOLING_LOOP_TIMEOUT
        POOLING_LOOP_TIMEOUT = value
    elif parameter == 'RESPONSE_SLEEPTIME':
        global RESPONSE_SLEEPTIME
        RESPONSE_SLEEPTIME = value
    elif parameter == 'RESPONSE_WAITING_TIMEOUT':
        global RESPONSE_WAITING_TIMEOUT
        RESPONSE_WAITING_TIMEOUT = value
    elif parameter == 'SOCKET_SIZE':
        global SOCKET_SIZE
        SOCKET_SIZE = value
    elif parameter == 'CHECK_AVAILABILITY_TIMEOUT':
        global CHECK_AVAILABILITY_TIMEOUT
        CHECK_AVAILABILITY_TIMEOUT = value
    elif parameter == 'RESTARTABLE_SLEEPTIME':
        global RESTARTABLE_SLEEPTIME
        RESTARTABLE_SLEEPTIME = value
    elif parameter == 'RESTARTABLE_TRIES':
        global RESTARTABLE_TRIES
        RESTARTABLE_TRIES = value
    elif parameter == 'REUSABLE_THREADED_POOL_SIZE':
        global REUSABLE_THREADED_POOL_SIZE
        REUSABLE_THREADED_POOL_SIZE = value
    elif parameter == 'REUSABLE_THREADED_LIFETIME':
        global REUSABLE_THREADED_LIFETIME
        REUSABLE_THREADED_LIFETIME = value
    elif parameter == 'DEFAULT_THREADED_POOL_NAME':
        global DEFAULT_THREADED_POOL_NAME
        DEFAULT_THREADED_POOL_NAME = value
    else:
        raise LDAPConfigurationParameterError('unable to set configuration parameter %s' % parameter)

# centralized imports
from .version import __author__, __version__, __email__, __description__, __status__, __license__, __url__
from .core.server import Server
from .core.connection import Connection
from .core.tls import Tls
from .core.pooling import ServerPool
from .abstract import ObjectDef, AttrDef, Attribute, Entry, Reader, OperationalAttribute
from .protocol.rfc4512 import DsaInfo, SchemaInfo

# imports error Exceptions
from .core.exceptions import LDAPException, LDAPExceptionError, LDAPConfigurationError, LDAPSocketCloseError, LDAPReferralError, \
    LDAPAttributeError, LDAPBindError, LDAPCertificateError, LDAPChangesError, LDAPCommunicationError, LDAPConnectionIsReadOnlyError, \
    LDAPConnectionPoolNameIsMandatoryError, LDAPConnectionPoolNotStartedError, LDAPControlsError, LDAPEntryError, \
    LDAPInvalidDereferenceAliasesError, LDAPInvalidFilterError, LDAPInvalidScopeError, LDAPInvalidServerError, LDAPKeyError,\
    LDAPLDIFError, LDAPMetricsError, LDAPObjectClassError, LDAPObjectError, LDAPPasswordIsMandatoryError, LDAPReaderError,\
    LDAPSASLBindInProgressError, LDAPSASLMechanismNotSupportedError, LDAPSASLPrepError, LDAPSchemaError, LDAPServerPoolError, \
    LDAPServerPoolExhaustedError, LDAPSocketOpenError, LDAPSocketReceiveError, LDAPSocketSendError, LDAPSSLConfigurationError,\
    LDAPSSLNotSupportedError, LDAPStartTLSError, LDAPTypeError, LDAPUnknownAuthenticationMethodError, LDAPUnknownRequestError, \
    LDAPUnknownResponseError, LDAPUnknownStrategyError, LDAPDefinitionError, LDAPResponseTimeoutError, LDAPInvalidHashAlgorithmError, \
    LDAPSessionTerminatedByServerError, LDAPMaximumRetriesError, LDAPExtensionError, LDAPInvalidDnError, LDAPInvalidPortError, \
    LDAPPackageUnavailableError, LDAPConfigurationParameterError, LDAPInvalidTlsSpecificationError, LDAPUserNameNotAllowedError, \
    LDAPUserNameIsMandatoryError, LDAPTransactionError

# imports result code Exceptions
from .core.exceptions import LDAPAdminLimitExceededResult, LDAPAffectMultipleDSASResult, LDAPAliasDereferencingProblemResult,\
    LDAPAliasProblemResult, LDAPAssertionFailedResult, LDAPAttributeOrValueExistsResult, LDAPAuthMethodNotSupportedResult, \
    LDAPAuthorizationDeniedResult, LDAPBusyResult, LDAPCanceledResult, LDAPCannotCancelResult, LDAPConfidentialityRequiredResult,\
    LDAPConstraintViolationResult, LDAPEntryAlreadyExistsResult, LDAPESyncRefreshRequiredResult, \
    LDAPInappropriateAuthenticationResult, LDAPInappropriateMatchingResult, LDAPInsufficientAccessRightsResult, \
    LDAPInvalidAttributeSyntaxResult, LDAPInvalidCredentialsResult, LDAPInvalidDNSyntaxResult, LDAPLCUPInvalidDataResult, \
    LDAPLCUPReloadRequiredResult, LDAPLCUPResourcesExhaustedResult, LDAPLCUPSecurityViolationResult, LDAPLCUPUnsupportedSchemeResult, \
    LDAPLoopDetectedResult, LDAPNamingViolationResult, LDAPNoSuchAttributeResult, LDAPNoSuchObjectResult, \
    LDAPNoSuchOperationResult, LDAPNotAllowedOnNotLeafResult, LDAPNotAllowedOnRDNResult, LDAPObjectClassModsProhibitedResult, \
    LDAPObjectClassViolationResult, LDAPOperationResult, LDAPOperationsErrorResult, LDAPOtherResult, LDAPProtocolErrorResult, \
    LDAPReferralResult, LDAPSASLBindInProgressResult, LDAPSizeLimitExceededResult, LDAPStrongerAuthRequiredResult, \
    LDAPTimeLimitExceededResult, LDAPTooLateResult, LDAPUnavailableCriticalExtensionResult, LDAPUnavailableResult, \
    LDAPUndefinedAttributeTypeResult, LDAPUnwillingToPerformResult


