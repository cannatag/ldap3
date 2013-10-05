"""
Created on 2013.08.05

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

try:
    # noinspection PyUnresolvedReferences
    import ssl
except ImportError:
    raise Exception('ssl not supported in this Python interpreter')
from os import path


class Tls(object):
    """
    tls/ssl configuration for Server object
    """

    def __init__(self, localPrivateKeyFile = None, localCertificateFile = None, validate = ssl.CERT_NONE, version = ssl.PROTOCOL_TLSv1, caCertsFile = None):
        if validate in [ssl.CERT_NONE, ssl.CERT_OPTIONAL, ssl.CERT_REQUIRED]:
            self.validate = validate
        elif validate:
            raise Exception('invalid validate parameter')

        if version in [ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv23, ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_TLSv1]:
            self.version = version
        elif version:
            raise Exception('invalid version parameter')

        if caCertsFile and path.exists(caCertsFile):
            self.caCertsFile = caCertsFile
        elif caCertsFile:
            raise Exception('invalid CA public key parameter')
        else:
            self.caCertsFile = None

        self.privateKeyFile = localPrivateKeyFile
        self.certificateFile = localCertificateFile

    def __str__(self):
        return 'version: ' + self.version + ' - local private key: ' + str(self.privateKeyFile) + ' - local public key:' + str(
            self.certificateFile) + ' - validate remote public key:' + self.validate + 'CA public key: ' + str(self.caCertsFile)

    def __repr__(self):
        r = '' if self.privateKeyFile is None else ', localPrivateKeyFile={0.privateKeyFile!r}'.format(self)
        r += '' if self.certificateFile is None else ', localCertificateFile={0.certificateFile!r}'.format(self)
        r += '' if self.validate is None else ', validate={0.validate!r}'.format(self)
        r += '' if self.version is None else ', version={0.version!r}'.format(self)
        r += '' if self.caCertsFile is None else ', caCertsFile={0.caCertsFile!r}'.format(self)
        r = 'Tls(' + r[2:] + ')'
        return r

    def wrapSocket(self, sock, doHandshake = False):
        """
        Add TLS to a plain socket and return the SSL socket
        """
        return ssl.wrap_socket(sock, keyfile = self.privateKeyFile, certfile = self.certificateFile, server_side = False, cert_reqs = self.validate,
                               ssl_version = self.version, ca_certs = self.caCertsFile, do_handshake_on_connect = doHandshake)

    @staticmethod
    def unwrapSocket(sock):
        """
        Remove TLS from an SSL socket and return the plain socket
        """
        return sock.unwrap()

    def startTls(self, connection):
        if connection.tlsStarted or connection.strategy._outstanding or connection.saslInProgress:  # as per rfc 4513 (3.1.1)
            return False

        result = connection.extended('1.3.6.1.4.1.1466.20037')
        if not isinstance(result, bool):  # async - startTls must be executed by strategy
            connection.getResponse(result)
            return True
        else:
            if connection.result['description'] not in ['success']:  # startTLS failed
                connection.lastError = 'startTLS failed'
                raise Exception(connection.lastError)
            return self._startTls(connection)

    def _startTls(self, connection):
        connection.socket = self.wrapSocket(connection.socket, False)
        try:
            connection.socket.do_handshake()
        except:
            connection.lastError = 'Tls handshake error'
            raise Exception(connection.lastError)

        if self.validate == ssl.CERT_REQUIRED or self.validate == ssl.CERT_OPTIONAL:
            serverCertificate = connection.socket.getpeercert()
            try:
                ssl.match_hostname(serverCertificate, connection.server.host)  # raise exception if certificate doesn't match server name
            except AttributeError:
                match_hostname_backport(serverCertificate, connection.server.host)
            except:
                raise

        connection.tlsStarted = True
        return True


class CertificateError_backport(ValueError): # fix for Python2, code from python 3.3 standard library
    pass


def _dnsname_to_pat_backport(dn): # fix for Python2, code from python 3.3 standard library
    import re

    pats = []
    for frag in dn.split(r'.'):
        if frag == '*':
            # When '*' is a fragment by itself, it matches a non-empty dotless
            # fragment.
            pats.append('[^.]+')
        else:
            # Otherwise, '*' matches any dotless fragment.
            frag = re.escape(frag)
            pats.append(frag.replace(r'\*', '[^.]*'))
    return re.compile(r'\A' + r'\.'.join(pats) + r'\Z', re.IGNORECASE)


def match_hostname_backport(cert, hostname): # fix for Python2, code from python 3.3 standard library
    """Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 rules
    are mostly followed, but IP addresses are not accepted for *hostname*.

    CertificateError is raised on failure. On success, the function
    returns nothing.
    """
    if not cert:
        raise ValueError("empty or no certificate")
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        if key == 'DNS':
            if _dnsname_to_pat_backport(value).match(hostname):
                return
            dnsnames.append(value)
    if not dnsnames:
        # The subject is only checked when there is no dNSName entry
        # in subjectAltName
        for sub in cert.get('subject', ()):
            for key, value in sub:
                # XXX according to RFC 2818, the most specific Common Name
                # must be used.
                if key == 'commonName':
                    if _dnsname_to_pat_backport(value).match(hostname):
                        return
                    dnsnames.append(value)
    if len(dnsnames) > 1:
        raise CertificateError_backport("hostname %r "
                                        "doesn't match either of %s" % (hostname, ', '.join(map(repr, dnsnames))))
    elif len(dnsnames) == 1:
        raise CertificateError_backport("hostname %r "
                                        "doesn't match %r" % (hostname, dnsnames[0]))
    else:
        raise CertificateError_backport("no appropriate commonName or "
                                        "subjectAltName fields were found")
