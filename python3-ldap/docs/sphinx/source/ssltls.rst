#########
SSL & TLS
#########

To use SSL basic authentication change the server definition to::

    s = server.Server('servername', port = 636, useSsl = True)  # define a secure LDAP server

To start a TLS connection on an already created clear connection::

    c.tls = Tls()
    c.start_tls()

You can customize the Tls object with references to key, certificate and CAs. See the Tls() constructor docstring for details


SASL
----

Two SASL mechanisms are implemented in the python3-ldap library: EXTERNAL and DIGEST-MD5. Even if DIGEST-MD5 is deprecated and moved to historic (RFC 6331, July 2011)
because it is "insecure and unsuitable for use in protocols" I've developed the authentication phase of the protocol because it is still used in LDAP servers.


External
^^^^^^^^

You can use the EXTERNAL mechanism when you're on a secure (TLS) channel. You can provide an authorization identity string in saslCredentials or let the
server trust the credential provided when establishing the secure channel::

     tls = Tls(localPrivateKeyFile = 'key.pem', localCertificateFile = 'cert.pem', validate = ssl.CERT_REQUIRED, version = ssl.PROTOCOL_TLSv1,
               caCertsFile = 'cacert.b64')
     server = Server(host = test_server, port = test_port_ssl, useSsl = True, tls = tls)
     connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, authentication = AUTH_SASL,
                             saslMechanism = 'EXTERNAL', saslCredentials = 'username')


Digest-MD5
^^^^^^^^^^

To use the DIGEST-MD5 you must pass a 4-value tuple as saslCredentials: (realm, user, password, authzId). You can pass None for 'realm' and 'authzId' if not used.

Quality of Protection is always 'auth'::

     server = Server(host = test_server, port = test_port)
     connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, authentication = AUTH_SASL,
                             saslMechanism = 'DIGEST-MD5', saslCredentials = (None, 'username', 'password', None))

UsernameId is not required to be an LDAP entry, but it can be any identifier recognized by the server (i.e. email, principal, ...). If
you pass None as 'realm' the default realm of the LDAP server will be used.

Again, consider that DIGEST-MD5 is deprecated and should not be used.
