"""
Created on 2013.08.17

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

from .saslPrep import saslPrep

def validateSimplePassword(password):
    """
    validate simple password as per RFC4013 using saslPrep:
    """

    if password == '' or password is None:
        raise Exception("simple password can't be empty")

    if not isinstance(password, bytes):  # bytes are returned raw, as per rfc (4.2)
        password = saslPrep(password)

    return password


def saslExternal(connection, initialRequest, controls):
    response = connection.postSendSingleResponse(connection.send('bindRequest', initialRequest, controls))
    if isinstance(response, int):  # get response if async
        connection.getResponse(response)

    return connection.result


def saslDigestMd5(connection, initialRequest, controls):
    response = connection.postSendSingleResponse(connection.send('bindRequest', initialRequest, controls))
    if isinstance(response, int):  # get response if async
        connection.getResponse(response)

    return connection.result
