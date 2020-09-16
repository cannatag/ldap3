"""
"""

# Created on 2015.04.08
#
# Author: Giovanni Cannata
#
# Copyright 2015 - 2020 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

# original code by Hugh Cole-Baker, modified by Peter Foley
# it needs the gssapi package
import socket

from ...core.exceptions import LDAPPackageUnavailableError, LDAPCommunicationError
from ...core.rdns import ReverseDnsSetting, get_hostname_by_addr, is_ip_addr

try:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import gssapi
    from gssapi.raw import ChannelBindings
except ImportError:
    raise LDAPPackageUnavailableError('package gssapi missing')

from .sasl import send_sasl_negotiation, abort_sasl_negotiation


NO_SECURITY_LAYER = 1
INTEGRITY_PROTECTION = 2
CONFIDENTIALITY_PROTECTION = 4


def get_channel_bindings(ssl_socket):
    try:
        server_certificate = ssl_socket.getpeercert(True)
    except:
        # it is not SSL socket
        return None
    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes
    except ImportError:
        raise LDAPPackageUnavailableError('package cryptography missing')
    cert = x509.load_der_x509_certificate(server_certificate, default_backend())
    hash_algorithm = cert.signature_hash_algorithm
    # According to https://tools.ietf.org/html/rfc5929#section-4.1, we have to convert the the hash function for md5 and sha1
    if hash_algorithm.name in ('md5', 'sha1'):
        digest = hashes.Hash(hashes.SHA256(), default_backend())
    else:
        digest = hashes.Hash(hash_algorithm, default_backend())
    digest.update(server_certificate)
    application_data = b'tls-server-end-point:' + digest.finalize()
    return ChannelBindings(application_data=application_data)


def sasl_gssapi(connection, controls):
    """
    Performs a bind using the Kerberos v5 ("GSSAPI") SASL mechanism
    from RFC 4752. Does not support any security layers, only authentication!

    sasl_credentials can be empty or a tuple with one or two elements.
    The first element determines which service principal to request a ticket for and can be one of the following:
    
    - None or False, to use the hostname from the Server object
    - True to perform a reverse DNS lookup to retrieve the canonical hostname for the hosts IP address
    - A string containing the hostname
    
    The optional second element is what authorization ID to request.
    
    - If omitted or None, the authentication ID is used as the authorization ID
    - If a string, the authorization ID to use. Should start with "dn:" or "user:".

    The optional third element is a raw gssapi credentials structure which can be used over
    the implicit use of a krb ccache.
    """
    target_name = None
    authz_id = b""
    raw_creds = None
    creds = None
    if connection.sasl_credentials:
        if len(connection.sasl_credentials) >= 1 and connection.sasl_credentials[0]:
            # older code will still be using a boolean True for the equivalent of
            # ReverseDnsSetting.REQUIRE_RESOLVE_ALL_ADDRESSES
            if connection.sasl_credentials[0] is True:
                hostname = get_hostname_by_addr(connection.socket.getpeername()[0])
                target_name = gssapi.Name('ldap@' + hostname, gssapi.NameType.hostbased_service)
            elif isinstance(connection.sasl_credentials[0], ReverseDnsSetting):
                rdns_setting = connection.sasl_credentials[0]
                # if the rdns_setting is OFF then we won't enter any branch here and will leave hostname as server host,
                # so we'll just use the server host, whatever it is
                peer_ip = connection.socket.getpeername()[0]
                hostname = connection.server.host
                if rdns_setting == ReverseDnsSetting.REQUIRE_RESOLVE_ALL_ADDRESSES:
                    # resolve our peer ip and use it as our target name
                    hostname = get_hostname_by_addr(peer_ip)
                elif rdns_setting == ReverseDnsSetting.REQUIRE_RESOLVE_IP_ADDRESSES_ONLY:
                    # resolve our peer ip (if the server host is an ip address) and use it as our target name
                    if is_ip_addr(target_name):
                        hostname = get_hostname_by_addr(peer_ip)
                elif rdns_setting == ReverseDnsSetting.OPTIONAL_RESOLVE_ALL_ADDRESSES:
                    # try to resolve our peer ip in dns and if we can, use it as our target name.
                    # if not, just use the server host
                    resolved_hostname = get_hostname_by_addr(peer_ip, success_required=False)
                    if resolved_hostname is not None:
                        hostname = resolved_hostname
                elif rdns_setting == ReverseDnsSetting.OPTIONAL_RESOLVE_IP_ADDRESSES_ONLY:
                    # try to resolve our peer ip in dns if our server host is an ip. if we can, use it as our target
                    #  name. if not, just use the server host
                    if is_ip_addr(target_name):
                        resolved_hostname = get_hostname_by_addr(peer_ip, success_required=False)
                        if resolved_hostname is not None:
                            hostname = resolved_hostname
                # construct our target name
                target_name = gssapi.Name('ldap@' + hostname, gssapi.NameType.hostbased_service)
            else:  # string hostname directly provided
                target_name = gssapi.Name('ldap@' + connection.sasl_credentials[0], gssapi.NameType.hostbased_service)
        if len(connection.sasl_credentials) >= 2 and connection.sasl_credentials[1]:
            authz_id = connection.sasl_credentials[1].encode("utf-8")
        if len(connection.sasl_credentials) >= 3 and connection.sasl_credentials[2]:
            raw_creds = connection.sasl_credentials[2]
    if target_name is None:
        target_name = gssapi.Name('ldap@' + connection.server.host, gssapi.NameType.hostbased_service)

    if raw_creds is not None:
        creds = gssapi.Credentials(base=raw_creds, usage='initiate', store=connection.cred_store)
    else:
        creds = gssapi.Credentials(name=gssapi.Name(connection.user), usage='initiate', store=connection.cred_store) if connection.user else None

    ctx = gssapi.SecurityContext(name=target_name, mech=gssapi.MechType.kerberos, creds=creds, channel_bindings=get_channel_bindings(connection.socket))
    in_token = None
    try:
        while True:
            out_token = ctx.step(in_token)
            if out_token is None:
                out_token = ''
            result = send_sasl_negotiation(connection, controls, out_token)
            in_token = result['saslCreds']
            try:
                # This raised an exception in gssapi<1.1.2 if the context was
                # incomplete, but was fixed in
                # https://github.com/pythongssapi/python-gssapi/pull/70
                if ctx.complete:
                    break
            except gssapi.exceptions.MissingContextError:
                pass

        unwrapped_token = ctx.unwrap(in_token)
        if len(unwrapped_token.message) != 4:
            raise LDAPCommunicationError("Incorrect response from server")

        server_security_layers = unwrapped_token.message[0]
        if not isinstance(server_security_layers, int):
            server_security_layers = ord(server_security_layers)
        if server_security_layers in (0, NO_SECURITY_LAYER):
            if unwrapped_token.message[1:] != '\x00\x00\x00':
                raise LDAPCommunicationError("Server max buffer size must be 0 if no security layer")
        if not (server_security_layers & NO_SECURITY_LAYER):
            raise LDAPCommunicationError("Server requires a security layer, but this is not implemented")

        client_security_layers = bytearray([NO_SECURITY_LAYER, 0, 0, 0])
        out_token = ctx.wrap(bytes(client_security_layers)+authz_id, False)
        return send_sasl_negotiation(connection, controls, out_token.message)
    except (gssapi.exceptions.GSSError, LDAPCommunicationError):
        abort_sasl_negotiation(connection, controls)
        raise
