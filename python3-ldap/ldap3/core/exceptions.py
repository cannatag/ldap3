"""
Created on 2014.05.14

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

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

from .. import RESULT_OPERATIONS_ERROR, RESULT_PROTOCOL_ERROR, RESULT_TIME_LIMIT_EXCEEDED, RESULT_SIZE_LIMIT_EXCEEDED, RESULT_STRONGER_AUTH_REQUIRED, RESULT_REFERRAL, RESULT_ADMIN_LIMIT_EXCEEDED, RESULT_UNAVAILABLE_CRITICAL_EXTENSION, \
    RESULT_AUTH_METHOD_NOT_SUPPORTED, RESULT_UNDEFINED_ATTRIBUTE_TYPE, RESULT_NO_SUCH_ATTRIBUTE, RESULT_SASL_BIND_IN_PROGRESS, RESULT_CONFIDENTIALITY_REQUIRED, RESULT_INAPPROPRIATE_MATCHING, RESULT_CONSTRAINT_VIOLATION, \
    RESULT_ATTRIBUTE_OR_VALUE_EXISTS, RESULT_INVALID_ATTRIBUTE_SYNTAX, RESULT_NO_SUCH_OBJECT, RESULT_ALIAS_PROBLEM, RESULT_INVALID_DN_SYNTAX, RESULT_ALIAS_DEREFERENCING_PROBLEM, RESULT_INVALID_CREDENTIALS, RESULT_LOOP_DETECTED, \
    RESULT_ENTRY_ALREADY_EXISTS, RESULT_LCUP_SECURITY_VIOLATION, RESULT_CANCELED, RESULT_E_SYNC_REFRESH_REQUIRED, RESULT_NO_SUCH_OPERATION, RESULT_LCUP_INVALID_DATA, RESULT_OBJECT_CLASS_MODS_PROHIBITED, RESULT_NAMING_VIOLATION, \
    RESULT_INSUFFICIENT_ACCESS_RIGHTS, RESULT_OBJECT_CLASS_VIOLATION, RESULT_TOO_LATE, RESULT_CANNOT_CANCEL, RESULT_LCUP_UNSUPPORTED_SCHEME, RESULT_BUSY, RESULT_AFFECT_MULTIPLE_DSAS, RESULT_UNAVAILABLE, RESULT_NOT_ALLOWED_ON_NON_LEAF, \
    RESULT_UNWILLING_TO_PERFORM, RESULT_OTHER, RESULT_LCUP_RELOAD_REQUIRED, RESULT_ASSERTION_FAILED, RESULT_AUTHORIZATION_DENIED, RESULT_LCUP_RESOURCES_EXHAUSTED, RESULT_NOT_ALLOWED_ON_RDN, RESULT_INAPPROPRIATE_AUTHENTICATION


# LDAPException hierarchy
class LDAPException(Exception):
    pass


class LDAPOperationResult(LDAPException):
    def __new__(cls, result=None, description=None, dn=None, message=None, response_type=None, response=None):
        if cls is LDAPOperationResult and result and result in exception_table:
            exc = super(LDAPOperationResult, exception_table[result]).__new__(exception_table[result])  # create an exception of the required result error
            exc.result = result
            exc.description = description
            exc.dn = dn
            exc.message = message
            exc.type = response_type
            exc.response = response
        else:
            exc = super(LDAPOperationResult, cls).__new__(cls)
        return exc

    def __init__(self, result=None, description=None, dn=None, message=None, response_type=None, response=None):
        self.result = result
        self.description = description
        self.dn = dn
        self.message = message
        self.type = response_type
        self.response = response

    def __str__(self):
        s = [self.__class__.__name__, str(self.result) if self.result else None, self.description if self.description else None, self.dn if self.dn else None, self.message if self.message else None, self.type if self.type else None, self.response if self.response else None]

        return ' - '.join(filter(None, s))

    def __repr__(self):
        return self.__str__()


class LDAPOperationsError(LDAPOperationResult):
    pass


class LDAPProtocolError(LDAPOperationResult):
    pass


class LDAPTimeLimitExceeded(LDAPOperationResult):
    pass


class LDAPSizeLimitExceeded(LDAPOperationResult):
    pass


class LDAPAuthMethodNotSupported(LDAPOperationResult):
    pass


class LDAPStrongerAuthRequired(LDAPOperationResult):
    pass


class LDAPReferral(LDAPOperationResult):
    pass


class LDAPAdminLimitExceeded(LDAPOperationResult):
    pass


class LDAPUnavailableCriticalExtension(LDAPOperationResult):
    pass


class LDAPConfidentialityRequired(LDAPOperationResult):
    pass


class LDAPSASLBindInProgress(LDAPOperationResult):
    pass


class LDAPNoSuchAttribute(LDAPOperationResult):
    pass


class LDAPUndefinedAttributeType(LDAPOperationResult):
    pass


class LDAPInappropriateMatching(LDAPOperationResult):
    pass


class LDAPConstraintViolation(LDAPOperationResult):
    pass


class LDAPAttributeOrValueExists(LDAPOperationResult):
    pass


class LDAPInvalidAttributeSyntax(LDAPOperationResult):
    pass


class LDAPNoSuchObject(LDAPOperationResult):
    pass


class LDAPAliasProblem(LDAPOperationResult):
    pass


class LDAPInvalidDNSyntax(LDAPOperationResult):
    pass


class LDAPAliasDereferencingProblem(LDAPOperationResult):
    pass


class LDAPInappropriateAuthentication(LDAPOperationResult):
    pass


class LDAPInvalidCredentials(LDAPOperationResult):
    pass


class LDAPInsufficientAccessRights(LDAPOperationResult):
    pass


class LDAPBusy(LDAPOperationResult):
    pass


class LDAPUnavailable(LDAPOperationResult):
    pass


class LDAPUnwillingToPerform(LDAPOperationResult):
    pass


class LDAPLoopDetected(LDAPOperationResult):
    pass


class LDAPNamingViolation(LDAPOperationResult):
    pass


class LDAPObjectClassViolation(LDAPOperationResult):
    pass


class LDAPNotAllowedOnNotLeaf(LDAPOperationResult):
    pass


class LDAPNotAllowedOnRDN(LDAPOperationResult):
    pass


class LDAPEntryAlreadyExists(LDAPOperationResult):
    pass


class LDAPObjectClassModsProhibited(LDAPOperationResult):
    pass


class LDAPAffectMultipleDSAS(LDAPOperationResult):
    pass


class LDAPOther(LDAPOperationResult):
    pass


class LDAPLCUPResourcesExhausted(LDAPOperationResult):
    pass


class LDAPLCUPSecurityViolation(LDAPOperationResult):
    pass


class LDAPLCUPInvalidData(LDAPOperationResult):
    pass


class LDAPLCUPUnsupportedScheme(LDAPOperationResult):
    pass


class LDAPLCUPReloadRequired(LDAPOperationResult):
    pass


class LDAPCanceled(LDAPOperationResult):
    pass


class LDAPNoSuchOperation(LDAPOperationResult):
    pass


class LDAPTooLate(LDAPOperationResult):
    pass


class LDAPCannotCancel(LDAPOperationResult):
    pass


class LDAPAssertionFailed(LDAPOperationResult):
    pass


class LDAPAuthorizationDenied(LDAPOperationResult):
    pass


class LDAPESyncRefreshRequired(LDAPOperationResult):
    pass


exception_table = {RESULT_OPERATIONS_ERROR: LDAPOperationsError,
                   RESULT_PROTOCOL_ERROR: LDAPProtocolError,
                   RESULT_TIME_LIMIT_EXCEEDED: LDAPTimeLimitExceeded,
                   RESULT_SIZE_LIMIT_EXCEEDED: LDAPSizeLimitExceeded,
                   RESULT_AUTH_METHOD_NOT_SUPPORTED: LDAPAuthMethodNotSupported,
                   RESULT_STRONGER_AUTH_REQUIRED: LDAPStrongerAuthRequired,
                   RESULT_REFERRAL: LDAPReferral,
                   RESULT_ADMIN_LIMIT_EXCEEDED: LDAPAdminLimitExceeded,
                   RESULT_UNAVAILABLE_CRITICAL_EXTENSION: LDAPUnavailableCriticalExtension,
                   RESULT_CONFIDENTIALITY_REQUIRED: LDAPConfidentialityRequired,
                   RESULT_SASL_BIND_IN_PROGRESS: LDAPSASLBindInProgress,
                   RESULT_NO_SUCH_ATTRIBUTE: LDAPNoSuchAttribute,
                   RESULT_UNDEFINED_ATTRIBUTE_TYPE: LDAPUndefinedAttributeType,
                   RESULT_INAPPROPRIATE_MATCHING: LDAPInappropriateMatching,
                   RESULT_CONSTRAINT_VIOLATION: LDAPConstraintViolation,
                   RESULT_ATTRIBUTE_OR_VALUE_EXISTS: LDAPAttributeOrValueExists,
                   RESULT_INVALID_ATTRIBUTE_SYNTAX: LDAPInvalidAttributeSyntax,
                   RESULT_NO_SUCH_OBJECT: LDAPNoSuchObject,
                   RESULT_ALIAS_PROBLEM: LDAPAliasProblem,
                   RESULT_INVALID_DN_SYNTAX: LDAPInvalidDNSyntax,
                   RESULT_ALIAS_DEREFERENCING_PROBLEM: LDAPAliasDereferencingProblem,
                   RESULT_INAPPROPRIATE_AUTHENTICATION: LDAPInappropriateAuthentication,
                   RESULT_INVALID_CREDENTIALS: LDAPInvalidCredentials,
                   RESULT_INSUFFICIENT_ACCESS_RIGHTS: LDAPInsufficientAccessRights,
                   RESULT_BUSY: LDAPBusy,
                   RESULT_UNAVAILABLE: LDAPUnavailable,
                   RESULT_UNWILLING_TO_PERFORM: LDAPUnwillingToPerform,
                   RESULT_LOOP_DETECTED: LDAPLoopDetected,
                   RESULT_NAMING_VIOLATION: LDAPNamingViolation,
                   RESULT_OBJECT_CLASS_VIOLATION: LDAPObjectClassViolation,
                   RESULT_NOT_ALLOWED_ON_NON_LEAF: LDAPNotAllowedOnNotLeaf,
                   RESULT_NOT_ALLOWED_ON_RDN: LDAPNotAllowedOnRDN,
                   RESULT_ENTRY_ALREADY_EXISTS: LDAPEntryAlreadyExists,
                   RESULT_OBJECT_CLASS_MODS_PROHIBITED: LDAPObjectClassModsProhibited,
                   RESULT_AFFECT_MULTIPLE_DSAS: LDAPAffectMultipleDSAS,
                   RESULT_OTHER: LDAPOther,
                   RESULT_LCUP_RESOURCES_EXHAUSTED: LDAPLCUPResourcesExhausted,
                   RESULT_LCUP_SECURITY_VIOLATION: LDAPLCUPSecurityViolation,
                   RESULT_LCUP_INVALID_DATA: LDAPLCUPInvalidData,
                   RESULT_LCUP_UNSUPPORTED_SCHEME: LDAPLCUPUnsupportedScheme,
                   RESULT_LCUP_RELOAD_REQUIRED: LDAPLCUPReloadRequired,
                   RESULT_CANCELED: LDAPCanceled,
                   RESULT_NO_SUCH_OPERATION: LDAPNoSuchOperation,
                   RESULT_TOO_LATE: LDAPTooLate,
                   RESULT_CANNOT_CANCEL: LDAPCannotCancel,
                   RESULT_ASSERTION_FAILED: LDAPAssertionFailed,
                   RESULT_AUTHORIZATION_DENIED: LDAPAuthorizationDenied,
                   RESULT_E_SYNC_REFRESH_REQUIRED: LDAPESyncRefreshRequired
                   }


class LDAPExceptionError(LDAPException):
    pass


# abstract layer exceptions
class LDAPKeyError(LDAPExceptionError, KeyError):
    pass


class LDAPAttributeError(LDAPExceptionError, AttributeError):
    pass


class LDAPEntryError(LDAPExceptionError):
    pass


class LDAPObjectError(LDAPExceptionError, ValueError):
    pass


class LDAPTypeError(LDAPExceptionError, TypeError):
    pass


class LDAPReaderError(LDAPExceptionError):
    pass


#tls exceptions
class LDAPSSLNotSupportedError(LDAPExceptionError, ImportError):
    pass


# connection exceptions
class LDAPUnknownStrategyError(LDAPExceptionError):
    pass


class LDAPUnknownAuthenticationMethodError(LDAPExceptionError):
    pass


class LDAPBindError(LDAPExceptionError):
    pass


class LDAPInvalidServerError(LDAPExceptionError):
    pass


class LDAPSASLMechanismNotSupportedError(LDAPExceptionError):
    pass


class LDAPObjectClassIsMandatoryError(LDAPExceptionError):
    pass


class LDAPConnectionIsReadOnlyError(LDAPExceptionError):
    pass


class LDAPInvalidChangesError(LDAPExceptionError, ValueError):
    pass


class LDAPServerPoolError(LDAPExceptionError):
    pass


class LDAPServerPoolExhaustedError(LDAPExceptionError):
    pass


class LDAPPortMustBeAnInteger(LDAPExceptionError):
    pass


class LDAPSSLConfigurationError(LDAPExceptionError):
    pass


class LDAPStartTLSError(LDAPExceptionError):
    pass


class LDAPCertificateError(LDAPExceptionError):
    pass


class LDAPPasswordIsMandatoryError(LDAPExceptionError):
    pass


class LDAPInvalidFilterError(LDAPExceptionError):
    pass


class LDAPInvalidScopeError(LDAPExceptionError, ValueError):
    pass


class LDAPInvalidDereferenceAliasesError(LDAPExceptionError, ValueError):
    pass
