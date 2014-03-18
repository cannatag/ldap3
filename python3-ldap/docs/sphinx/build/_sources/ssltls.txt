#########
SSL & TLS
#########

To use SSL basic authentication change the server definition to::

    s = server.Server('servername', port = 636, use_ssl = True)  # define a secure LDAP server

To start a TLS connection on an already created clear connection::

    c.tls = Tls()
    c.start_tls()

You can customize the Tls object with references to keys, certificates and CAs. See the Tls() constructor docstring for details

SASL
----

Two SASL mechanisms are implemented in the python3-ldap library: EXTERNAL and DIGEST-MD5. Even if DIGEST-MD5 is deprecated and moved to historic (RFC6331, July 2011)
because it is "insecure and unsuitable for use in protocols" (as stated by the RFC) I've developed the authentication phase of the protocol because it is still used in LDAP servers.


External
^^^^^^^^

You can use the EXTERNAL mechanism when you're on a secure (TLS) channel. You can provide an authorization identity string in sasl_credentials or let the
server trust the credential provided when establishing the secure channel::

     tls = Tls(local_private_key_file = 'key.pem', local_certificate_file = 'cert.pem', validate = ssl.CERT_REQUIRED, version = ssl.PROTOCOL_TLSv1,
               ca_certs_file = 'cacert.b64')
     server = Server(host = test_server, port = test_port_ssl, use_ssl = True, tls = tls)
     connection = Connection(server, auto_bind = True, version = 3, client_strategy = test_strategy, authentication = AUTH_SASL,
                             sasl_mechanism = 'EXTERNAL', sasl_credentials = 'username')

Digest-MD5
^^^^^^^^^^

To use the DIGEST-MD5 you must pass a 4-value tuple as sasl_credentials: (realm, user, password, authz_id). You can pass None for 'realm' and 'authz_id' if not used. Quality of Protection is always 'auth'::

     server = Server(host = test_server, port = test_port)
     connection = Connection(server, auto_bind = True, version = 3, client_strategy = test_strategy, authentication = AUTH_SASL,
                             sasl_mechanism = 'DIGEST-MD5', sasl_credentials = (None, 'username', 'password', None))

Username is not required to be an LDAP entry, but it can be any identifier recognized by the server (i.e. email, principal, ...). If
you pass None as 'realm' the default realm of the LDAP server will be used.

**Again, consider that DIGEST-MD5 is deprecated and should not be used.**
