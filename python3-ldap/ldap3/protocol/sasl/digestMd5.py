"""
"""

# Created on 2014.01.04
#
# Author: Giovanni Cannata
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

from binascii import hexlify
import hashlib
import hmac

from .sasl import abort_sasl_negotiation, send_sasl_negotiation, random_hex_string


def md5_h(value):
    if not isinstance(value, bytes):
        value = value.encode()

    return hashlib.md5(value).digest()


def md5_kd(k, s):
    if not isinstance(k, bytes):
        k = k.encode()

    if not isinstance(s, bytes):
        s = s.encode()

    return md5_h(k + b':' + s)


def md5_hex(value):
    if not isinstance(value, bytes):
        value = value.encode()

    return hexlify(value)


def md5_hmac(k, s):
    if not isinstance(k, bytes):
        k = k.encode()

    if not isinstance(s, bytes):
        s = s.encode()

    return hmac.new(k, s).hexdigest()


def sasl_digest_md5(connection, controls):
    # sasl_credential must be a tuple made up of the following elements: (realm, user, password, authorization_id)
    # if realm is None will be used the realm received from the server, if available
    if not isinstance(connection.sasl_credentials, tuple) or not len(connection.sasl_credentials) == 4:
        return None

    # step One of RFC2831
    result = send_sasl_negotiation(connection, controls, None)
    if 'saslCreds' in result and result['saslCreds'] != 'None':
        server_directives = dict((attr[0], attr[1].strip('"')) for attr in [line.split('=') for line in result['saslCreds'].split(',')])  # convert directives to dict, unquote values
    else:
        return None

    if 'realm' not in server_directives or 'nonce' not in server_directives or 'algorithm' not in server_directives:  # mandatory directives, as per RFC2831
        abort_sasl_negotiation(connection, controls)
        return None

    # step Two of RFC2831
    charset = server_directives['charset'] if 'charset' in server_directives and server_directives['charset'].lower() == 'utf-8' else 'iso8859-1'
    user = connection.sasl_credentials[1].encode(charset)
    realm = (connection.sasl_credentials[0] if connection.sasl_credentials[0] else (server_directives['realm'] if 'realm' in server_directives else '')).encode(charset)
    password = connection.sasl_credentials[2].encode(charset)
    authz_id = connection.sasl_credentials[3].encode(charset) if connection.sasl_credentials[3] else b''
    nonce = server_directives['nonce'].encode(charset)
    cnonce = random_hex_string(16).encode(charset)
    uri = b'ldap/'
    qop = b'auth'

    digest_response = b'username="' + user + b'",'
    digest_response += b'realm="' + realm + b'",'
    digest_response += b'nonce="' + nonce + b'",'
    digest_response += b'cnonce="' + cnonce + b'",'
    digest_response += b'digest-uri="' + uri + b'",'
    digest_response += b'qop=' + qop + b','
    digest_response += b'nc=00000001' + b','
    if charset == 'utf-8':
        digest_response += b'charset="utf-8",'

    a0 = md5_h(b':'.join([user, realm, password]))
    a1 = b':'.join([a0, nonce, cnonce, authz_id]) if authz_id else b':'.join([a0, nonce, cnonce])
    a2 = b'AUTHENTICATE:' + uri + (':00000000000000000000000000000000' if qop in [b'auth-int', b'auth-conf'] else b'')

    digest_response += b'response="' + md5_hex(md5_kd(md5_hex(md5_h(a1)), b':'.join([nonce, b'00000001', cnonce, qop, md5_hex(md5_h(a2))]))) + b'"'

    result = send_sasl_negotiation(connection, controls, digest_response)
    return result
