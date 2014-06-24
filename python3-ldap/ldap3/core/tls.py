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
from .exceptions import LDAPSSLNotSupportedError, LDAPSSLConfigurationError, LDAPStartTLSError, LDAPCertificateError


try:
    # noinspection PyUnresolvedReferences
    import ssl
except ImportError:
    raise LDAPSSLNotSupportedError('SSL not supported in this Python interpreter')

try:
    # noinspection PyUnresolvedReferences
    from ssl import CertificateError
except ImportError:
    class CertificateError(ValueError):  # fix for Python 2, code from Python 3.3 standard library
        pass

try:
    from ssl import create_default_context, Purpose  # defined in Python 3.4
    use_ssl_context = True
except ImportError:
    use_ssl_context = False

from os import path


# noinspection PyProtectedMember
class Tls(object):
    """
    tls/ssl configuration for Server object
    Starting from python 3-4 it uses the SSLContext object
    that tries to read the CAs defined at system level
    ca_certs_path and ca_certs_data are valid only when using SSLContext
    local_private_key_password is valid only when using SSLContext
    """

    def __init__(self,
                 local_private_key_file=None,
                 local_certificate_file=None,
                 validate=ssl.CERT_NONE,
                 version=None,
                 ca_certs_file=None,
                 valid_names=None,
                 ca_certs_path=None,
                 ca_certs_data=None,
                 local_private_key_password=None
                 ):

        if validate in [ssl.CERT_NONE, ssl.CERT_OPTIONAL, ssl.CERT_REQUIRED]:
            self.validate = validate
        elif validate:
            raise LDAPSSLConfigurationError('invalid validate parameter')

        if ca_certs_file and path.exists(ca_certs_file):
            self.ca_certs_file = ca_certs_file
        elif ca_certs_file:
            raise LDAPSSLConfigurationError('invalid CA public key file')
        else:
            self.ca_certs_file = None

        if ca_certs_path and use_ssl_context and path.exists(ca_certs_path):
            self.ca_certs_path = ca_certs_path
        elif ca_certs_path and not use_ssl_context:
            raise LDAPSSLNotSupportedError('cannot use CA public keys path, SSLContext not available')
        elif ca_certs_path:
            raise LDAPSSLConfigurationError('invalid CA public keys path')
        else:
            self.ca_certs_path = None

        if ca_certs_data and use_ssl_context:
            self.ca_certs_data = ca_certs_data
        elif ca_certs_data:
            raise LDAPSSLNotSupportedError('cannot use CA data, SSLContext not available')
        else:
            self.ca_certs_data = None

        if local_private_key_password and use_ssl_context:
            self.private_key_password = local_private_key_password
        elif local_private_key_password:
            raise LDAPSSLNotSupportedError('cannot use local private key password, SSLContext is not available')
        else:
            self.private_key_password = None

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
        r += '' if self.ca_certs_path is None else ', ca_certs_path={0.ca_certs_path!r}'.format(self)
        r += '' if self.ca_certs_data is None else ', ca_certs_data={0.ca_certs_data!r}'.format(self)
        r = 'Tls(' + r[2:] + ')'
        return r

    def wrap_socket(self, connection, do_handshake=False):
        """
        Adds TLS to a plain socket and returns the SSL socket
        """

        if use_ssl_context:
            ssl_context = create_default_context(purpose=Purpose.SERVER_AUTH, cafile=self.ca_certs_file, capath=self.ca_certs_path, cadata=self.ca_certs_data)
            if self.private_key_file:
                ssl_context.load_cert_chain(self.certificate_file, keyfile=self.private_key_file, password=self.private_key_password)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = self.validate
            if self.version:  # if version is not present keep the default context version
                ssl_context.protocol = self.version
            wrapped_socket = ssl_context.wrap_socket(connection.socket, server_side=False, do_handshake_on_connect=do_handshake)
        else:
            wrapped_socket = ssl.wrap_socket(connection.socket, keyfile=self.private_key_file, certfile=self.certificate_file, server_side=False, cert_reqs=self.validate, ssl_version=self.version, ca_certs=self.ca_certs_file, do_handshake_on_connect=do_handshake)

        if do_handshake and (self.validate == ssl.CERT_REQUIRED or self.validate == ssl.CERT_OPTIONAL):
            check_hostname(wrapped_socket, connection.server.host, self.valid_names)

        return wrapped_socket

    def start_tls(self, connection):
        if connection.server.ssl:  # ssl already established at server level
            return False

        if (connection.tls_started and not connection._executing_deferred) or connection.strategy._outstanding or connection.sasl_in_progress:
            # Per RFC 4513 (3.1.1)
            return False
        connection.starting_tls = True
        result = connection.extended('1.3.6.1.4.1.1466.20037')
        if not connection.strategy.sync:
            # async - _start_tls must be executed by the strategy
            connection.get_response(result)
            return True
        else:
            if connection.result['description'] not in ['success']:
                # startTLS failed
                connection.last_error = 'startTLS failed - ' + str(connection.result['description'])
                raise LDAPStartTLSError(connection.last_error)
            return self._start_tls(connection)

    def _start_tls(self, connection):
        connection.socket = self.wrap_socket(connection, do_handshake=True)

        if connection.usage:
            connection._usage.wrapped_sockets += 1

        connection.starting_tls = False
        connection.tls_started = True
        return True


def _dnsname_match_backport(dn, hostname, max_wildcards=1):
    """Matching according to RFC 6125, section 6.4.3

    http://tools.ietf.org/html/rfc6125#section-6.4.3
    """
    pats = []
    if not dn:
        return False

    dn_array = dn.split(r'.')

    leftmost = dn_array[0]
    remainder = dn_array[1:]

    wildcards = leftmost.count('*')
    if wildcards > max_wildcards:
        # Issue #17980: avoid denials of service by refusing more
        # than one wildcard per fragment.  A survery of established
        # policy among SSL implementations showed it to be a
        # reasonable choice.
        raise CertificateError(
            "too many wildcards in certificate DNS name: " + repr(dn))

    # speed up common case w/o wildcards
    if not wildcards:
        return dn.lower() == hostname.lower()

    # RFC 6125, section 6.4.3, subitem 1.
    # The client SHOULD NOT attempt to match a presented identifier in which
    # the wildcard character comprises a label other than the left-most label.
    if leftmost == '*':
        # When '*' is a fragment by itself, it matches a non-empty dotless
        # fragment.
        pats.append('[^.]+')
    elif leftmost.startswith('xn--') or hostname.startswith('xn--'):
        # RFC 6125, section 6.4.3, subitem 3.
        # The client SHOULD NOT attempt to match a presented identifier
        # where the wildcard character is embedded within an A-label or
        # U-label of an internationalized domain name.
        pats.append(re.escape(leftmost))
    else:
        # Otherwise, '*' matches any dotless string, e.g. www*
        pats.append(re.escape(leftmost).replace(r'\*', '[^.]*'))

    # add the remaining fragments, ignore any wildcards
    for frag in remainder:
        pats.append(re.escape(frag))

    pat = re.compile(r'\A' + r'\.'.join(pats) + r'\Z', re.IGNORECASE)
    return pat.match(hostname)


def match_hostname_backport(cert, hostname):
    """
    Fix for Python2; code from Python 3.4.1 standard library.

    Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 and RFC 6125
    rules are followed, but IP addresses are not accepted for *hostname*.

    CertificateError is raised on failure. On success, the function
    returns nothing.
    """
    if not cert:
        raise ValueError("empty or no certificate, match_hostname needs a "
                         "SSL socket or SSL context with either "
                         "CERT_OPTIONAL or CERT_REQUIRED")
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        if key == 'DNS':
            if _dnsname_match_backport(value, hostname):
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
                    if _dnsname_match(value, hostname):
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
    for host_name in host_names:
        if host_name == '*':
            return
        try:
            ssl.match_hostname(server_certificate, host_name)  # raise CertificateError if certificate doesn't match server name
            return
        except AttributeError:
            match_hostname_backport(server_certificate, host_name)
            return
        except CertificateError:
            pass

    raise LDAPCertificateError("hostname doesn't match")
