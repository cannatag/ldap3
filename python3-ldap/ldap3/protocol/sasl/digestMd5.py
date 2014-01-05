"""
Created on 2014.01.04

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

import hashlib
import hmac
from .sasl import abortSaslNegotiation, sendSaslNegotiation, randomHexString
from pprint import pprint


def MD5_H(value):
    if not isinstance(value, bytes):
        value = value.encode()

    return hashlib.md5(value).hexdigest()


def MD5_KD(k, s):
    return MD5_H(k + ':' + s)


def MD5_HMAC(k, s):
    if not isinstance(k, bytes):
        k = k.encode()

    if not isinstance(s, bytes):
        s = s.encode()

    return hmac.new(k, s).hexdigest()


def MD5_A1():
    pass

def saslDigestMd5(connection, controls):
    # saslCredential must be a tuple made up of the following elements: (realm, user, password)
    # if realm is None will be used the realm received from the server, if available
    if not isinstance(connection.saslCredentials, tuple) or not len(connection.saslCredentials) == 3:
        return None

    # step One of rfc 2831
    result = sendSaslNegotiation(connection, controls, None)
    serverDirectives = {attr[0]: attr[1].strip('"') for attr in [line.split('=') for line in result['saslCreds'].split(',')]}  # convert directives to dict, unquote values
    print(result['saslCreds'])
    pprint(serverDirectives)
    if 'realm' not in serverDirectives or 'nonce' not in serverDirectives or 'algorithm' not in serverDirectives:  # mandatory directives, as per rfc 2831
        abortSaslNegotiation(connection, controls)
        return None

    # step Two of rfc 2831
    digestResponse = 'username="' + connection.saslCredentials[1] + '",'
    digestResponse += 'realm="' + (connection.saslCredentials[0] if connection.saslCredentials[0] else (serverDirectives['realm'] if 'realm' in serverDirectives else '')) + '",'
    digestResponse += 'nonce="' + serverDirectives['nonce'] + '",'
    digestResponse += 'cnonce="' + randomHexString(16) + '",'
    digestResponse += 'nc=00000001' + ','
    if 'charset' in serverDirectives and (serverDirectives['charset'].lower() == 'utf-8' or serverDirectives['charset'].lower() == 'utf8'):
        digestResponse += 'charset="' + serverDirectives['charset'] + '",'

    digestResponse += 'response="' + 'abc' + '"'

    result = sendSaslNegotiation(connection, controls, digestResponse

    return result
