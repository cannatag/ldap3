"""
"""

# Created on 2013.05.31
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

from .. import SIMPLE, ANONYMOUS, SASL
from ..core.exceptions import LDAPPasswordIsMandatoryError, LDAPUnknownAuthenticationMethodError
from ..protocol.sasl.sasl import validate_simple_password
from ..protocol.rfc4511 import Version, AuthenticationChoice, Simple, BindRequest, ResultCode, SaslCredentials, BindResponse, \
    LDAPDN, LDAPString, Referral, ServerSaslCreds, SicilyPackageDiscovery, SicilyNegotiate, SicilyResponse
from ..protocol.convert import authentication_choice_to_dict, referrals_to_list


# BindRequest ::= [APPLICATION 0] SEQUENCE {
#                                           version        INTEGER (1 ..  127),
#                                           name           LDAPDN,
#                                           authentication AuthenticationChoice }


def bind_operation(version,
                   authentication,
                   name='',
                   password=None,
                   sasl_mechanism=None,
                   sasl_credentials=None):
    request = BindRequest()
    request['version'] = Version(version)
    if name is None:
        name = ''
    request['name'] = name
    if authentication == SIMPLE:
        if password:
            request['authentication'] = AuthenticationChoice().setComponentByName('simple', Simple(validate_simple_password(password)))
        else:
            raise LDAPPasswordIsMandatoryError('password is mandatory')
    elif authentication == SASL:
        sasl_creds = SaslCredentials()
        sasl_creds['mechanism'] = sasl_mechanism
        if sasl_credentials:
            sasl_creds['credentials'] = sasl_credentials
        request['authentication'] = AuthenticationChoice().setComponentByName('sasl', sasl_creds)
    elif authentication == ANONYMOUS:
        request['name'] = ''
        request['authentication'] = AuthenticationChoice().setComponentByName('simple', Simple(''))
    elif authentication == 'SICILY_PACKAGE_DISCOVERY':  # https://msdn.microsoft.com/en-us/library/cc223501.aspx
        request['name'] = ''
        request['authentication'] = AuthenticationChoice().setComponentByName('sicilyPackageDiscovery', SicilyPackageDiscovery(''))
    elif authentication == 'SICILY_NEGOTIATE_NTLM':  # https://msdn.microsoft.com/en-us/library/cc223501.aspx
        request['name'] = 'NTLM'
        request['authentication'] = AuthenticationChoice().setComponentByName('sicilyNegotiate', SicilyNegotiate(name.create_negotiate_message()))  # ntlm client in self.name
    elif authentication == 'SICILY_RESPONSE_NTLM':  # https://msdn.microsoft.com/en-us/library/cc223501.aspx
        name.parse_challenge_message(password)  # server_creds returned by server in password
        server_creds = name.create_authenticate_message()
        if server_creds:
            request['name'] = ''
            request['authentication'] = AuthenticationChoice().setComponentByName('sicilyResponse', SicilyResponse(server_creds))
        else:
            request = None
    else:
        raise LDAPUnknownAuthenticationMethodError('unknown authentication method')

    return request


def bind_request_to_dict(request):
    return {'version': int(request['version']),
            'name': str(request['name']),
            'authentication': authentication_choice_to_dict(request['authentication'])}

# BindResponse ::= [APPLICATION 1] SEQUENCE {
#                                            COMPONENTS OF LDAPResult,
#                                            serverSaslCreds    [7] OCTET STRING OPTIONAL }


def bind_response_operation(result_code,
                            matched_dn='',
                            diagnostic_message='',
                            referral=None,
                            server_sasl_credentials=None):

    response = BindResponse()
    response['resultCode'] = ResultCode(result_code)
    response['matchedDN'] = LDAPDN(matched_dn)
    response['diagnosticMessage'] = LDAPString(diagnostic_message)
    if referral:
        response['referral'] = Referral(referral)

    if server_sasl_credentials:
        response['serverSaslCreds'] = ServerSaslCreds(server_sasl_credentials)

    return response


def bind_response_to_dict(response):
    return {'result': int(response['resultCode']),
            'description': ResultCode().getNamedValues().getName(response['resultCode']),
            'dn': str(response['matchedDN']),
            'message': str(response['diagnosticMessage']),
            'referrals': referrals_to_list(response['referral']),
            'saslCreds': bytes(response['serverSaslCreds']) if response['serverSaslCreds'] is not None else None}


def sicily_bind_response_to_dict(response):
    return {'result': int(response['resultCode']),
            'description': ResultCode().getNamedValues().getName(response['resultCode']),
            'server_creds': bytes(response['matchedDN']),
            'error_message': str(response['diagnosticMessage'])}

