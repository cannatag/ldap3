"""
Created on 2013.05.31

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

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

from ldap3.protocol.rfc4511 import Version, AuthenticationChoice, Simple, BindRequest, ResultCode, SaslCredentials
from ldap3 import AUTH_SIMPLE, AUTH_ANONYMOUS, AUTH_SASL
from ldap3.protocol.convert import authenticationChoiceToDict, referralsToList
from ldap3.protocol.sasl.sasl import validateSimplePassword

# BindRequest ::= [APPLICATION 0] SEQUENCE {
#     version                 INTEGER (1 ..  127),
#     name                    LDAPDN,
#     authentication          AuthenticationChoice }


def bindOperation(version, authentication, name = '', password = None, saslMechanism = None, saslCred = None):
    request = BindRequest()
    request['version'] = Version(version)
    if name is None:
        name = ''
    request['name'] = name
    if authentication == AUTH_SIMPLE:
        if password:
            request['authentication'] = AuthenticationChoice().setComponentByName('simple', Simple(validateSimplePassword(password)))
        else:
            raise Exception('password cannot be empty')
    elif authentication == AUTH_SASL:
        saslCredentials = SaslCredentials()
        saslCredentials['mechanism'] = saslMechanism
        if saslCred:
            saslCredentials['credentials'] = saslCred
        request['authentication'] = AuthenticationChoice().setComponentByName('sasl', saslCredentials)
    elif authentication == AUTH_ANONYMOUS:
        request['name'] = ''
        request['authentication'] = AuthenticationChoice().setComponentByName('simple', Simple(''))
    else:
        raise (Exception('Invalid authentication mechanism'))

    return request


def bindRequestToDict(request):
    return {'version': int(request['version']), 'name': str(request['name']), 'authentication': authenticationChoiceToDict(request['authentication'])}


def bindResponseToDict(response):
    return {'result': int(response['resultCode']), 'description': ResultCode().getNamedValues().getName(response['resultCode']),
            'dn': str(response['matchedDN']), 'message': str(response['diagnosticMessage']), 'referrals': referralsToList(response['referral']),
            'saslCreds': str(response['serverSaslCreds'])}
