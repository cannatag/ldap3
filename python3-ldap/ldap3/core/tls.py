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
from ldap3 import LDAPException

try:
    # noinspection PyUnresolvedReferences
    import ssl
except ImportError:
    raise LDAPException('ssl not supported in this Python interpreter')

try:
    # noinspection PyUnresolvedReferences
    from ssl import CertificateError
except ImportError:
    class CertificateError(ValueError):  # fix for Python 2, code from Python 3.3 standard library
        pass

from os import path


class Tls(object):
    """
    tls/ssl configuration for Server object
    """

    def __init__(self, local_private_key_file=None, local_certificate_file=None, validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1, ca_certs_file=None, valid_names=None):
        if validate in [ssl.CERT_NONE, ssl.CERT_OPTIONAL, ssl.CERT_REQUIRED]:
            self.validate = validate
        elif validate:
            raise LDAPException('invalid validate parameter')

        if ca_certs_file and path.exists(ca_certs_file):
            self.ca_certs_file = ca_certs_file
        elif ca_certs_file:
            raise LDAPException('invalid CA public key parameter')
        else:
            self.ca_certs_file = None

        self.version = version
        self.private_key_file = local_private_key_file
        self.certificate_file = local_certificate_file
        self.valid_names = valid_names

    def __str__(self):
        return 'version: ' + self.version + ' - local private key: ' + str(self.private_key_file) + ' - local public key:' + str(self.certificate_file) + ' - validate remote public key:' + self.validate + 'CA public key: ' + str(self.ca_certs_file)

    def __repr__(self):
        r = '' if self.private_key_file is None else ', localPrivateKeyFile={0.private_key_file!r}'.format(self)
        r += '' if self.certificate_file is None else ', localCertificateFile={0.certificate_file!r}'.format(self)
        r += '' if self.validate is None else ', validate={0.validate!r}'.format(self)
        r += '' if self.version is None else ', version={0.version!r}'.format(self)
        r += '' if self.ca_certs_file is None else ', ca_certs_file={0.ca_certs_file!r}'.format(self)
        r = 'Tls(' + r[2:] + ')'
        return r

    def wrap_socket(self, connection, do_handshake=False):
        """
        Adds TLS to a plain socket and returns the SSL socket
        """
        wrapped_socket = ssl.wrap_socket(connection.socket,
          keyfile=self.private_key_file, certfile=self.certificate_file,
          server_side=False, cert_reqs=self.validate,
          ssl_version=self.version, ca_certs=self.ca_certs_file,
          do_handshake_on_connect=do_handshake)

        if self.validate == ssl.CERT_REQUIRED 
          or self.validate == ssl.CERT_OPTIONAL:
            check_hostname(wrapped_socket, connection.server.host,
                             self.valid_names)

        return wrapped_socket

    @staticmethod
    def unwrap_socket(sock):
        """
        Removes TLS from an SSL socket and returns the plain socket
        """
        return sock.unwrap()

    def start_tls(self, connection):
        if connection.tls_started
          or connection.strategy._outstanding
          or connection.sasl_in_progress:
            # Per RFC 4513 (3.1.1)
            return False

        result = connection.extended('1.3.6.1.4.1.1466.20037')
        if not connection.strategy.sync:
            # async - start_tls must be executed by the strategy
            connection.get_response(result)
            return True
        else:
            if connection.result['description'] not in ['success']:
                # startTLS failed
                connection.last_error = 'startTLS failed'
                raise LDAPException(connection.last_error)
            return self._start_tls(connection)

    def _start_tls(self, connection):
        connection.socket = self.wrap_socket(connection, False)
        try:
            connection.socket.do_handshake()
        except:
            connection.last_error = 'Tls handshake error'
            raise LDAPException(connection.last_error)

        if self.validate == ssl.CERT_REQUIRED
          or self.validate == ssl.CERT_OPTIONAL:
            check_hostname(connection.socket, connection.server.host,
                             self.valid_names)

        if connection.usage:
            connection.usage.wrapped_socket += 1

        connection.tls_started = True
        return True


def _dnsname_to_pat_backport(dn):
    '''
    Fix for Python2; code from Python 3.3 standard library.
    '''
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


def match_hostname_backport(cert, hostname):
    """
    Fix for Python2; code from Python 3.3 standard library.

    Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 rules are
    mostly followed, but IP addresses are not accepted for *hostname*.

    CertificateError is raised on failure. On success, the function
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
                #  according to RFC 2818, the most specific Common Name
                # must be used.
                if key == 'commonName':
                    if _dnsname_to_pat_backport(value).match(hostname):
                        return
                    dnsnames.append(value)
    if len(dnsnames) > 1:
        raise CertificateError("hostname %r doesn't match either of %s" % (hostname, ', '.join(map(repr, dnsnames))))
    elif len(dnsnames) == 1:
        raise CertificateError("hostname %r doesn't match %r" % (hostname, dnsnames[0]))
    else:
        raise CertificateError("no appropriate commonName or subjectAltName fields were found")


def check_hostname(sock, server_name, additional_names):

    server_certificate = sock.getpeercert()
    host_names = [server_name] + (additional_names if isinstance(additional_names, list) else [additional_names])
    valid_found = False
    for host_name in host_names:
        if host_names == '*':
            return
        try:
            ssl.match_hostname(server_certificate, host_name)  # raise CertificateError if certificate doesn't match server name
            valid_found = True
        except AttributeError:
            match_hostname_backport(server_certificate, host_name)
            valid_found = True
        except CertificateError:
            pass

        if valid_found:
            return

    raise LDAPException("certificate error, name doesn't match")
