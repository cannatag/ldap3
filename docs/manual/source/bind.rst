##################
The BIND operation
##################

As specified in RFC4511 the Bind operation must be tought as the "authenticate" operation. It's name (and that of its
Unbind counterpart) is for historical reason.

When you open a connection to an LDAP server you're in an **anonymous** connection state. What this exactly means
is defined by the server implementation, not by the protocol. Think of this as of a default access to the server public
data (even if what public data means is still a server local matter).

The Bind operation allows authentication information to be exchanged between the client and server to establish a new
authorization state.

The Bind request typically specifies the desired authentication identity. Some Bind mechanisms also allow the client
to specify the authorization identity.  If the authorization identity is not specified, the server derives it from the
authentication identity in an implementation-specific manner.

If you want to provide authentication information you must use the Bind operation to specify an identity to be used to
access the data. Keep in mind that either the authentication details than the authorization details
are a local server matter. The LDAP protocol doesn't specify how the identity must be stored on the server nor how the
authorization ACLs are specified.

The bind operation specify 4 different methods to authenticate to the server:

* Simple bind: you provide user credentials by the means of a username (in a dn form) and a password.

* Anonymous simple Bind: the user and password are passed as empty strings

* Unauthenticated simple Bind: you pass a username without a password. This method, even if specified in the protocol,
should not be used because is higly insecure and should be forbidden by the server. It was used for tracing purpose.

* Sasl (Simple Authentication and Security Layer): this define multiple mechanisms that each server can provide to allow
access to the server. Before trying a mechanism you should check that the server supports it. The LDAP server publish
its allowed SASL mechanism in the DSE information that can be read anonymously.


Simple Bind
-----------

You perform a simple bind as in the following example (using the default synchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform the Bind operation
    if not c.bind():
        print('error in bind', c.result)


The server and connection are create with the default parameters::

    s = Server(host='servername', port=389, use_ssl=False, get_info='ALL')
    c = Connection(s, user='user_dn', password='user_password', auto_bind='NONE', version=3, authentication='SIMPLE', \
    client_strategy='SYNC', auto_referrals=True, check_names=True, read_only=False, lazy=False, raise_exceptions=False)


Refer to the Server and Connections docs for info about the default parameters.


Anonymous Bind
--------------

Anonymous bind performs a simple bind with the username and the user passwrod set to empty strings. The ldap3 library has
a specific authentication option to do that::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s)  # define an ANONYMOUS connection

    # perform the Bind operation
    if not c.bind():
        print('error in bind', c.result)


The server and connection are create with the default parameters::

    s = Server(host='servername', port=389, use_ssl=False, get_info='ALL')
    c = Connection(s, auto_bind='NONE', version=3, authentication='ANONYMOUS', client_strategy='SYNC', auto_referrals=True, \
    check_names=True, read_only=False, lazy=False, raise_exceptions=False)


To use SSL secure connection in the previous examples modify the server object:

To use SSL basic authentication change the server definition to::

    s = Server('servername', use_ssl=True, get_info=ALL)  # define a secure LDAP server on the default 636 port


StartTLS
--------

If you want to raise the transport layer security to an encrypted state you can perform the StartTLS operation. With this
mechanism you can wrap the plain socket in an ssl encrypted socket::

    c.start_tls()


From now on the communication transport is encrypted. You should properly configure the Server object addind a Tls object
with the relevant ssl configuration::


    t = Tls(local_private_key_file='client_private_key.pem', local_certificate_file='client_cert.pem', validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file='ca_certs.b64')
    s = Server('servername', tls=t, get_info=ALL)


Please refer to the SSLTLS section for more information.


SASL
----

Three SASL mechanisms are currently implemented in the ldap3 library: EXTERNAL, DIGEST-MD5 and GSSAPI (Kerberos, via the gssapi package). Even if DIGEST-MD5 is **deprecated** and moved to historic (RFC6331, July 2011)
because it is **"insecure and unsuitable for use in protocols"** (as stated by the RFC).

To query the SASL mechanism available on the server you must read the information published by the server. The ldap3 library
has a convenient way to do that::

    from ldap3 import Server, Connection, ALL
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema
    c = Connection(s)
    c.open()  # establish connection without performing any bind (equivalent to ANONYMOUS bind)
    print(s.info.supported_sasl_mechanisms)

Print out a list of the SASL mechanism supported by the server::

    ['EXTERNAL', 'DIGEST-MD5', 'GSSAPI']


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


Kerberos
^^^^^^^^

Kerberos authentication uses the python-gssapi package. You must install it and configure your Kerberos environment to use the GSSAPI mechanism::

    import ldap3
    import ssl

    tls = ldap3.Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)
    server = ldap3.Server('<servername>', use_ssl=True, tls=tls)
    connection = ldap3.Connection(
        server, authentication=ldap3.SASL, sasl_mechanism='GSSAPI')
    connection.bind()
    print(connection.extend.standard.who_am_i())



NTLM
----

The ldap3 library support an additional method to bind to Active Directory servers via the NTLM method::

    # import class and constants
    from ldap3 import Server, Connection, SIMPLE, SYNC, ALL, SASL, NTLM)

    # define the server and the connection
    s = Server('servername', get_info=ALL)
    c = Connection(s, user="AUTHTEST\\Administrator", password="password", authentication=NTLM)
    # perform the Bind operation
    if not c.bind():
        print('error in bind', c.result)

This authentication method is specific for Active Directory and uses a proprietary authentication protocol named SICILY
that break the LDAP RFC but can be used to access AD.
