###########
SSL and TLS
###########

You can use SSL basic authentication with the use_ssl parameter of the Server object, you can also specify a port (636 is the default for secure ldap)::

    s = Server('servername', port = 636, use_ssl = True)  # define a secure LDAP server

To start a TLS connection on an already created _clear connection::

    c.start_tls()



Some older versions (up to 2.7.9) of the Python interpreter lack the capability to check the server certificate against
the DNS name of the server. This is a potential breach of security because a server could present a certificate issued
for another host name. ldap3 includes a backport of this capability ported from the 3.4.3 version of the Python interpreter.
If you want to keep your application up to date with the hostname checking capability of the latest Python version
you can install the backports.ssl_match_hostname package from pypi. The ldap3 library will detect and use it instead of
the included static backport.

The Tls object
==============

You can customize the server Tls object with references to keys, certificates and CAs. It includes all attributes needed to securely connect over an ssl socket:

* local_private_key_file: the file with the private key of the client
* local_certificate_file: the certificate of the server
* validate: specifies if the server certificate must be validated, values can be: CERT_NONE (certificates are ignored), CERT_OPTIONAL (not required, but validated if provided) and CERT_REQUIRED (required and validated)
* version: SSL or TLS version to use, can be one of the following: SSLv2, SSLv3, SSLv23, TLSv1 (as per Python 3.3. The version list can be different in other Python versions)
* ca_certs_file: the file containing the certificates of the certification authorities

Tls object uses the ssl module of the Python standard library with additional checking functions that are missing from the Python 2 standard library.

The needed constants are defined in the ssl package.

IF you don't use a specific Tls object and set use_ssl=True in the Server definition, a default Tls object will be used, it has no certificate
files, uses the ssl.PROTOCOL_SSLv23 (if available in your Python interpreter) and performs no validation of the server certificate.
It's recommended to set validate=ssl.CERT_REQUIRED to verify the certificate server. Example::

    tls = Tls(local_private_key_file='client_private_key.pem', local_certificate_file='client_cert.pem', validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file='ca_certs.b64')


SSLContext
----------
You can use SSLContext if running in Python 3.4 or newer.

The use of ssl.SSLContext make TLS operation more flexible, It integrates with the system wide Certification Authorities and also ensure that there are "reasonable" security defaults when using the TLS
layer. It's also possible to specify a file system path containing
the CA file or even pass certificate data "on the fly".

When defining the Tls object you have the following additional parameters available:

* ca_cert_file: the usual link to the certification authority chain of certificates
* ca_cert_path: a link to a path containing the certification  authorities certificates (reashed, as expected by OpenSSL)
* ca_cert_data: CA certificate data stored in memory

if you leave all these parameter to None the SSLContext will use the
system wide certificate store (ssl path on linux, CA stores on
Windows)

If the SSLContext is not available the library will fall back to the
ssl wrapped socket mechanism.


SASL
----

Three SASL mechanisms are currently implemented in the ldap3 library: EXTERNAL, DIGEST-MD5 and GSSAPI (Kerberos, via the gssapi package). Even if DIGEST-MD5 is **deprecated** and moved to historic (RFC6331, July 2011)
because it is **insecure and unsuitable for use in protocols** (as stated by the RFC) I've developed the authentication phase of the protocol because it is still used in LDAP servers.

External
^^^^^^^^

You can use the EXTERNAL mechanism when you're on a secure (TLS) channel. You can provide an authorization identity string in sasl_credentials or let the
server trust the credential provided when establishing the secure channel::

     tls = Tls(local_private_key_file = 'key.pem', local_certificate_file = 'cert.pem', validate = ssl.CERT_REQUIRED, version = ssl.PROTOCOL_TLSv1,
               ca_certs_file = 'cacert.b64')
     server = Server(host = test_server, port = test_port_ssl, use_ssl = True, tls = tls)
     connection = Connection(server, auto_bind = True, version = 3, client_strategy = test_strategy, authentication = SASL,
                             sasl_mechanism = 'EXTERNAL', sasl_credentials = 'username')

Digest-MD5
^^^^^^^^^^

To use the DIGEST-MD5 you must pass a 4-value tuple as sasl_credentials: (realm, user, password, authz_id). You can pass None for 'realm' and 'authz_id' if not used. Quality of Protection is always 'auth'::

     server = Server(host = test_server, port = test_port)
     connection = Connection(server, auto_bind = True, version = 3, client_strategy = test_strategy, authentication = SASL,
                             sasl_mechanism = 'DIGEST-MD5', sasl_credentials = (None, 'username', 'password', None))

Username is not required to be an LDAP entry, but it can be any identifier recognized by the server (i.e. email, principal, ...). If
you pass None as 'realm' the default realm of the LDAP server will be used.

**Again, remember that DIGEST-MD5 is deprecated and should not be used.**
