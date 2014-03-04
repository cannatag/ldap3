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
from binascii import hexlify

import hashlib
import hmac
from .sasl import abortSaslNegotiation, sendSaslNegotiation, randomHexString


def MD5_H(value):
    if not isinstance(value, bytes):
        value = value.encode()

    return hashlib.md5(value).digest()


def MD5_KD(k, s):
    if not isinstance(k, bytes):
        k = k.encode()

    if not isinstance(s, bytes):
        s = s.encode()

    return MD5_H(k + b':' + s)


def MD5_HEX(value):
    if not isinstance(value, bytes):
        value = value.encode()

    return hexlify(value)


def MD5_HMAC(k, s):
    if not isinstance(k, bytes):
        k = k.encode()

    if not isinstance(s, bytes):
        s = s.encode()

    return hmac.new(k, s).hexdigest()


def saslDigestMd5(connection, controls):
    # saslCredential must be a tuple made up of the following elements: (realm, user, password, authorizationId)
    # if realm is None will be used the realm received from the server, if available
    if not isinstance(connection.saslCredentials, tuple) or not len(connection.saslCredentials) == 4:
        return None

    # step One of rfc 2831
    result = sendSaslNegotiation(connection, controls, None)
    serverDirectives = dict((attr[0], attr[1].strip('"')) for attr in [line.split('=') for line in result['saslCreds'].split(',')])  # convert directives to dict, unquote values

    if 'realm' not in serverDirectives or 'nonce' not in serverDirectives or 'algorithm' not in serverDirectives:  # mandatory directives, as per rfc 2831
        abortSaslNegotiation(connection, controls)
        return None

    # step Two of rfc 2831
    charset = serverDirectives['charset'] if 'charset' in serverDirectives and serverDirectives['charset'].lower() == 'utf-8' else 'iso8859-1'
    user = connection.saslCredentials[1].encode(charset)
    realm = (connection.saslCredentials[0] if connection.saslCredentials[0] else (serverDirectives['realm'] if 'realm' in serverDirectives else '')).encode(charset)
    password = connection.saslCredentials[2].encode(charset)
    authzId = connection.saslCredentials[3].encode(charset) if connection.saslCredentials[3] else b''
    nonce = serverDirectives['nonce'].encode(charset)
    cnonce = randomHexString(16).encode(charset)
    uri = b'ldap/'
    qop = b'auth'

    digestResponse = b'username="' + user + b'",'
    digestResponse += b'realm="' + realm + b'",'
    digestResponse += b'nonce="' + nonce + b'",'
    digestResponse += b'cnonce="' + cnonce + b'",'
    digestResponse += b'digest-uri="' + uri + b'",'
    digestResponse += b'qop=' + qop + b','
    digestResponse += b'nc=00000001' + b','
    if charset == 'utf-8':
        digestResponse += b'charset="utf-8",'

    A0 = MD5_H(b':'.join([user, realm, password]))
    A1 = b':'.join([A0, nonce, cnonce, authzId]) if authzId else b':'.join([A0, nonce, cnonce])
    A2 = b'AUTHENTICATE:' + uri + (':00000000000000000000000000000000' if qop in [b'auth-int', b'auth-conf'] else b'')

    digestResponse += b'response="' + MD5_HEX(MD5_KD(MD5_HEX(MD5_H(A1)), b':'.join([nonce, b'00000001', cnonce, qop, MD5_HEX(MD5_H(A2))]))) + b'"'

    result = sendSaslNegotiation(connection, controls, digestResponse)
    # pprint(result)
    return result
