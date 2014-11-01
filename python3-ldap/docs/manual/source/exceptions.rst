Exceptions
##########

The python3-ldap exceptions hierarchy includes a LDAPException root class with two main
branches: LDAPExceptionError and LDAPExceptionResult. The
LDAPExceptionError contains 42 different exceptions that should help
understanding what's going wrong when you have an error. A few of these
(including all the LDAPCommunicationError exceptions) have multiple
inheritance either from the LDAPExceptionError and from specific
Python exceptions. This let you choose between catching standard Python
errors or the more detailed python3-ldap errors. The
LDAPCommunicationError exceptions will be created at runtime and
inherit the specific socket exception raised by the interpreter, so
you can catch them with the specific socket.error or the more general
LDAPCommunicationError.

LDAPOperationResult (the other branch of LDAPException hierarchy)
includes 48 exceptions, one for each possible error result (except
RESULT_SUCCESS) specified in the LDAPv3 protocol. When you create a
connection object with the "raise_exceptions" parameter set to True
any unsuccesful LDAP operation will throw an exception of this class, subclassed
to the specific LDAP result code exception. For example if you get an
INVALID_DN_SYNTAX (result code 34) the connection will raise the
LDAPInvalidDNSyntaxResult exception, with the following parameter:
result, description, dn, message, response_type, and the whole
response filled with the values received in the response of the LDAP
operation. You can specify which result codes you don't want to raise
exceptions, the default is : RESULT_COMPARE_FALSE, RESULT_COMPARE_TRUE,
RESULT_REFERRAL (and of course RESULT_SUCCESS). You can change this
behaviour in the ldap3 __init__.py package or at runtime modifying the
ldap3.DO_NOT_RAISE_EXCEPTIONS list.

The "raise_exceptions" mode is helpful if you want exceptions to flow
up in the code and manage them at a upper level than the single
operation level. This mode works in every kind of strategy, even in
the ReusableStrategy (for connection pooling) where exceptions are
trapped in the "effective" connection thread and are sent back to the
calling connection object in the main (or another) thread.


LDAPException

--LDAPExceptionError

----LDAPAttributeError (inherits also from AttributeError)

----LDAPBindError

----LDAPCertificateError

----LDAPChangesError (inherits also from ValueError)

----LDAPCommunicationError (all may inherit from socket.error)

------LDAPReferralError

------LDAPSessionTerminatedByServer

------LDAPSocketCloseError

------LDAPSocketOpenError

------LDAPSocketReceiveError

------LDAPSocketSendError

------LDAPUnknownRequestError

------LDAPUnknownResponseError

----LDAPConfigurationError

------LDAPUnknownStrategyError

------LDAPUnknownAuthenticationMethodError

------LDAPSSLConfigurationError

------LDAPDefinitionError

----LDAPConnectionIsReadOnlyError

----LDAPConnectionPoolNameIsMandatoryError

----LDAPConnectionPoolNotStartedError

----LDAPControlsError (inherits also from ValueError)

----LDAPEntryError

----LDAPExtensionError

----LDAPInvalidDereferenceAliasesError (inherits also from ValueError)

----LDAPInvalidFilterError

----LDAPInvalidPort

----LDAPInvalidScopeError (inherits also from ValueError)

----LDAPInvalidServerError

----LDAPKeyError (inherits also from KeyError)

----LDAPLDIFError

----LDAPMaximumRetriesError

----LDAPMetricsError

----LDAPObjectClassError (inherits also from ValueError)

----LDAPObjectError

----LDAPPasswordIsMandatoryError

----LDAPReaderError

----LDAPMaximumRetriesError

----LDAPSASLBindInProgressError

----LDAPSASLMechanismNotSupportedError

----LDAPSASLPrepError

----LDAPSchemaError

----LDAPServerPoolError

----LDAPServerPoolExhaustedError

----LDAPSSLNotSupportedError (inherits also from ImportError)

----LDAPStartTLSError

----LDAPTypeError

--LDAPOperationResult

----LDAPAdminLimitExceededResult

----LDAPAffectMultipleDSASResult

----LDAPAliasDereferencingProblemResult

----LDAPAliasProblemResult

----LDAPAssertionFailedResult

----LDAPAttributeOrValueExistsResult

----LDAPAuthMethodNotSupportedResult

----LDAPAuthorizationDeniedResult

----LDAPBusyResult

----LDAPCanceledResult

----LDAPCannotCancelResult

----LDAPConfidentialityRequiredResult

----LDAPConstraintViolationResult

----LDAPEntryAlreadyExistsResult

----LDAPESyncRefreshRequiredResult

----LDAPInappropriateAuthenticationResult

----LDAPInappropriateMatchingResult

----LDAPInsufficientAccessRightsResult

----LDAPInvalidAttributeSyntaxResult

----LDAPInvalidCredentialsResult

----LDAPInvalidDNSyntaxResult

----LDAPLCUPInvalidDataResult

----LDAPLCUPReloadRequiredResult

----LDAPLCUPResourcesExhaustedResult

----LDAPLCUPSecurityViolationResult

----LDAPLCUPUnsupportedSchemeResult

----LDAPLoopDetectedResult

----LDAPNamingViolationResult

----LDAPNoSuchAttributeResult

----LDAPNoSuchObjectResult

----LDAPNoSuchOperationResult

----LDAPNotAllowedOnNotLeafResult

----LDAPNotAllowedOnRDNResult

----LDAPObjectClassModsProhibitedResult

----LDAPObjectClassViolationResult

----LDAPOperationsErrorResult

----LDAPOtherResult

----LDAPProtocolErrorResult

----LDAPReferralResult

----LDAPSASLBindInProgressResult

----LDAPSizeLimitExceededResult

----LDAPStrongerAuthRequiredResult

----LDAPTimeLimitExceededResult

----LDAPTooLateResult

----LDAPUnavailableCriticalExtensionResult

----LDAPUnavailableResult

----LDAPUndefinedAttributeTypeResult

----LDAPUnwillingToPerformResult
