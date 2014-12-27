"""
"""

# Created on 2013.05.31
#
# Author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of pureLDAP.
#
# pureLDAP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pureLDAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pureLDAP in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from .. import AUTH_SIMPLE, AUTH_ANONYMOUS, AUTH_SASL
from ..core.exceptions import LDAPPasswordIsMandatoryError, LDAPUnknownAuthenticationMethodError
from ..protocol.sasl.sasl import validate_simple_password
from ..protocol.rfc4511 import Version, AuthenticationChoice, Simple, BindRequest, ResultCode, SaslCredentials
from ..protocol.convert import authentication_choice_to_dict, referrals_to_list

# BindRequest ::= [APPLICATION 0] SEQUENCE {
#     version                 INTEGER (1 ..  127),
#     name                    LDAPDN,
#     authentication          AuthenticationChoice }


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
    if authentication == AUTH_SIMPLE:
        if password:
            request['authentication'] = AuthenticationChoice().setComponentByName('simple', Simple(validate_simple_password(password)))
        else:
            raise LDAPPasswordIsMandatoryError('password is mandatory')
    elif authentication == AUTH_SASL:
        sasl_creds = SaslCredentials()
        sasl_creds['mechanism'] = sasl_mechanism
        if sasl_credentials:
            sasl_creds['credentials'] = sasl_credentials
        request['authentication'] = AuthenticationChoice().setComponentByName('sasl', sasl_creds)
    elif authentication == AUTH_ANONYMOUS:
        request['name'] = ''
        request['authentication'] = AuthenticationChoice().setComponentByName('simple', Simple(''))
    else:
        raise LDAPUnknownAuthenticationMethodError('unknown authentication method')

    return request


def bind_request_to_dict(request):
    return {'version': int(request['version']),
            'name': str(request['name']),
            'authentication': authentication_choice_to_dict(request['authentication'])}


def bind_response_to_dict(response):
    return {'result': int(response['resultCode']),
            'description': ResultCode().getNamedValues().getName(response['resultCode']),
            'dn': str(response['matchedDN']),
            'message': str(response['diagnosticMessage']),
            'referrals': referrals_to_list(response['referral']),
            'saslCreds': str(response['serverSaslCreds'])}
