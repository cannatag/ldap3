###################
Exception Hierarchy
###################

LDAPException

--LDAPExceptionError

----LDAPAttributeError

----LDAPBindError

----LDAPCertificateError

----LDAPChangesError

----LDAPCommunicationError

------LDAPReferralError

------LDAPSessionTerminatedByServer

------LDAPSocketCloseError

------LDAPSocketOpenError

------LDAPSocketReceiveError

------LDAPSocketSendError

------LDAPUnknownRequestError

------LDAPUnknownResponseError

----LDAPConnectionIsReadOnlyError

----LDAPConnectionPoolNameIsMandatoryError

----LDAPConnectionPoolNotStartedError

----LDAPControlsError

----LDAPEntryError

----LDAPInvalidDereferenceAliasesError

----LDAPInvalidFilterError

----LDAPInvalidPort

----LDAPInvalidScopeError

----LDAPInvalidServerError

----LDAPKeyError

----LDAPLDIFError

----LDAPMetricsError

----LDAPObjectClassError

----LDAPObjectError

----LDAPPasswordIsMandatoryError

----LDAPReaderError

----LDAPSASLBindInProgressError

----LDAPSASLMechanismNotSupportedError

----LDAPSASLPrepError

----LDAPSchemaError

----LDAPServerPoolError

----LDAPServerPoolExhaustedError

----LDAPSSLConfigurationError

----LDAPSSLNotSupportedError

----LDAPStartTLSError

----LDAPTypeError

----LDAPUnknownAuthenticationMethodError

----LDAPUnknownStrategyError

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
