"""
Created on 2014.03.10

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
from ..core.exceptions import LDAPSSLNotSupportedError
from ..core.tls import Tls as newTls


try:
    # noinspection PyUnresolvedReferences
    import ssl
except ImportError:
    raise LDAPSSLNotSupportedError('SSL not supported in this Python interpreter')


# noinspection PyPep8Naming
class Tls(newTls):
    """
    tls/ssl configuration for Server object
    """

    def __init__(self, localPrivateKeyFile=None, localCertificateFile=None, validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1, caCertsFile=None):
        newTls.__init__(self, localPrivateKeyFile, localCertificateFile, validate, version, caCertsFile)

    def startTls(self, connection):
        return newTls.start_tls(self, connection)
