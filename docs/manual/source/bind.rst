##################
The BIND operation
##################

As specified in RFC4511 the **Bind** operation is the "authenticate" operation. It (and the Unbind operation as well) has
this name for historical reason.

When you open a connection to an LDAP server you're in an **anonymous** connection state. What this exactly means
is defined by the server implementation, not by the protocol. Think of this as a public access to the server data
(even if what public data mean is still a server matter). In ldap3 you establish the connection to the server
with the ``open()`` method of the Connection object. The ``bind()`` method will open the connection if not already open.

The Bind operation allows creadentials to be exchanged between the client and server to establish a new
authorization state.

The Bind request typically specifies the desired authentication identity. Some Bind mechanisms also allow the client
to specify the authorization identity. If the authorization identity is not specified, the server derives it from the
authentication identity in an implementation-specific manner.

If you want to provide authentication information you must use the Bind operation to specify an identity to use to
access the data. Keep in mind that either the authentication details than the authorization details
are a local server matter. The LDAP protocol doesn't specify how the identity must be stored on the server nor how the
authorization ACLs are specified.

The Bind operation specify 4 different methods to authenticate to the server, as specified in RFC4513:

* Simple Bind: you provide user credentials by the means of a username (in a dn form) and a password.

* Anonymous Bind: the user and password are passed as empty strings.

* Unauthenticated simple Bind: you pass a username without a password. This method, even if specified in the protocol,
  should not be used because is higly insecure and should be forbidden by the server. It was used in the past for tracing purpose.

* SASL (Simple Authentication and Security Layer): this defines multiple mechanisms that each server can provide to allow access to the server.
  Before trying a mechanism you should check that the server supports it. The LDAP server publish its allowed SASL mechanism in the DSE 
  information that can be read anonymously with the ``get_info=ALL`` parameter of the Server object.

The Bind method returns True if the bind is successful, False if something goes wrong while binding. In this case you
can inspect the ``result`` attribute of the Connection object to get the error description.

Simple Bind
-----------

You perform a Simple Bind operation as in the following example (using the default synchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform the Bind operation
    if not c.bind():
        print('error in bind', c.result)


The server and the connection are created with the default parameters::

    s = Server(host='servername', port=389, use_ssl=False, get_info='ALL')
    c = Connection(s, user='user_dn', password='user_password', auto_bind='NONE', version=3, authentication='SIMPLE', \
    client_strategy='SYNC', auto_referrals=True, check_names=True, read_only=False, lazy=False, raise_exceptions=False)


Refer to the Server and Connection docs for info about the default parameters.


Anonymous Bind
--------------

Anonymous bind performs a simple bind with the user name and the user password set to empty strings. The ldap3 library has
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


The server and the connection are created with the default parameters::

    s = Server(host='servername', port=389, use_ssl=False, get_info='ALL')
    c = Connection(s, auto_bind='NONE', version=3, authentication='ANONYMOUS', client_strategy='SYNC', auto_referrals=True, \
    check_names=True, read_only=False, lazy=False, raise_exceptions=False)

To use SSL basic authentication change the server definition to::

    s = Server('servername', use_ssl=True, get_info=ALL)  # define a secure LDAP server on the default 636 port


StartTLS
--------

If you want to raise the transport layer security to an encrypted state you can perform the *StartTLS* extended operation. With this
mechanism you can wrap the plain socket in an SSL encrypted socket::

    c.start_tls()


From now on the communication transport is encrypted. You should properly configure the Server object addind a Tls object
with the relevant ssl configuration::


    t = Tls(local_private_key_file='client_private_key.pem', local_certificate_file='client_cert.pem', validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1, ca_certs_file='ca_certs.b64')
    s = Server('servername', tls=t, get_info=ALL)


Please refer to the SSLTLS section for more information.


SASL
----

Three SASL mechanisms are currently implemented in the ldap3 library: EXTERNAL, DIGEST-MD5 and GSSAPI (Kerberos, via the gssapi package). DIGEST-MD5 is
implemented even if it is **deprecated** and moved to historic (RFC6331, July 2011) because it is **"insecure and unsuitable for use in protocols"**
(as stated by the RFC).

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

You can use the EXTERNAL mechanism when you're on a secure (TLS) channel. You can provide an authorization identity string in ``sasl_credentials`` or let the
server trust the credential provided when establishing the secure channel::

     tls = Tls(local_private_key_file = 'key.pem', local_certificate_file = 'cert.pem', validate = ssl.CERT_REQUIRED, version = ssl.PROTOCOL_TLSv1,
               ca_certs_file = 'cacert.b64')
     server = Server(host = test_server, port = test_port_ssl, use_ssl = True, tls = tls)
     connection = Connection(server, auto_bind = True, version = 3, client_strategy = test_strategy, authentication = SASL,
                             sasl_mechanism = 'EXTERNAL', sasl_credentials = 'username')

Digest-MD5
^^^^^^^^^^

To use the DIGEST-MD5 you must pass a 4-value tuple as sasl_credentials: (realm, user, password, authz_id). You can pass None
for 'realm' and 'authz_id' if not used. Quality of Protection is always 'auth'::

     server = Server(host = test_server, port = test_port)
     connection = Connection(server, auto_bind = True, version = 3, client_strategy = test_strategy, authentication = SASL,
                             sasl_mechanism = 'DIGEST-MD5', sasl_credentials = (None, 'username', 'password', None))

Username is not required to be an LDAP entry, but it can be any identifier recognized by the server (i.e. email, principal, ...). If
you pass None as 'realm' the default realm of the LDAP server will be used.

**Again, remember that DIGEST-MD5 is deprecated and should not be used.**


.. _sasl-kerberos:

Kerberos
^^^^^^^^

Kerberos authentication uses the ``gssapi`` package. You must install it and configure your Kerberos environment to use the GSSAPI mechanism::

    import ldap3
    import ssl

    tls = ldap3.Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)
    server = ldap3.Server('<servername>', use_ssl=True, tls=tls)
    connection = ldap3.Connection(
        server, authentication=ldap3.SASL, sasl_mechanism='GSSAPI')
    connection.bind()
    print(connection.extend.standard.who_am_i())

You can specify which Kerberos client principal should be used with the ``user`` parameter when declaring the ``connection``::

    connection = ldap3.Connection(
        server, user='ldap-client/client.example.com',
        authentication=ldap3.SASL, sasl_mechanism='GSSAPI')

By default the library attempts to bind against the service principal for the domain you attempted to connect to.
If your target LDAP service uses a round-robin DNS, it's likely that the hostname you connect to won't match. In this case,
you can either specify a hostname explicitly as the first element of the ``sasl_credentials`` connection parameter,
or pass ``True`` as the first element to do a reverse DNS lookup::

    # Override server hostname for authentication
    connection = ldap3.Connection(
        server, sasl_credentials=('ldap-3.example.com',),
        authentication=ldap3.SASL, sasl_mechanism='GSSAPI')

    # Perform a reverse DNS lookup to determine the hostname to authenticate against.
    connection = ldap3.Connection(
        server, sasl_credentials=(True,),
        authentication=ldap3.SASL, sasl_mechanism='GSSAPI')

NTLM
----

The ldap3 library supports an additional method to bind to Active Directory servers via the NTLM method::

    # import class and constants
    from ldap3 import Server, Connection, SIMPLE, SYNC, ALL, SASL, NTLM

    # define the server and the connection
    s = Server('servername', get_info=ALL)
    c = Connection(s, user="AUTHTEST\\Administrator", password="password", authentication=NTLM)
    # perform the Bind operation
    if not c.bind():
        print('error in bind', c.result)

This authentication method is specific for Active Directory and uses a proprietary authentication protocol named SICILY
that breaks the LDAP RFC but can be used to access AD.

When binding via NTLM, it is also possible to authenticate with an LM:NTLM hash rather than a password::

    c = Connection(s, user="AUTHTEST\\Administrator", password="E52CAC67419A9A224A3B108F3FA6CB6D:8846F7EAEE8FB117AD06BDD830B7586C", authentication=NTLM)

LDAPI (LDAP over IPC)
---------------------

If your LDAP server provides a UNIX socket connection you can use the **ldapi:** (*Interprocess Communication*) scheme to access it from the
same machine::

    >>> # accessing OpenLDAP server in a root user session
    >>> s = Server('ldapi:///var/run/slapd/ldapi')
    >>> c = Connection(s, authentication=SASL, sasl_mechanism=EXTERNAL, sasl_credentials='')
    >>> c.bind()
    >>> True
    >>> c.extend.standard.who_am_i()
    >>> dn:cn=config

Using the SASL *EXTERNAL* mechanism allows you to provide to the server the credentials of the logged user.

While accessing your LDAP server via a UNIX socket you can perform any usual LDAP operation. This should be faster than using a TCP connection.
You don't need to use SSL when connecting via a socket because all the communication is in the server memory and is not exposed on the wire.


Bind as a different user while the Connection is open
-----------------------------------------------------

LDAP protocol allows to bind as a different user while the connection is open. In this case you can use the **rebind()** method
that let you change the user and the authentication method while the connection is open::

    # import class and constants
    from ldap3 import Server, Connection, ALL, LDAPBindError

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform the Bind operation
    if not c.bind():
        print('error in bind', c.result)

    try:
        c.rebind(user='different_user_dn', password='different_user_password')
    except LDAPBindError:
       print('error in rebind', c.result)

In case the credentials are invalid or if the server doesn't allow you to rebind the server *could* abruptly close the connection.
This condition is checked by the ``rebind()`` method and an LDAPBindError exception will be raised if caught.

Extended logging
----------------
To get an idea of what's happening when you perform a Simple Bind operation using the StartTLS security feature this is
the extended log from a session to an OpenLdap server from a Windows client with dual stack IP::

    # Initialization:

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED
    DEBUG:ldap3:ERROR:detail level set to EXTENDED
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO'), user='cn=admin,o=test', password='<stripped 8 characters of sensitive data>', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:NETWORK:opening connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:reset usage metrics
    DEBUG:ldap3:BASIC:start collecting usage metrics
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]>
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]> with mode IP_V6_PREFERRED


    # Opening the connection (trying IPv6 then IPv4):

    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it.> for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <local: [::]:49610 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]
    DEBUG:ldap3:NETWORK:connection open for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:start START TLS operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:instantiated Tls: <Tls(validate=0)>


    # Starting TLS - wrapping the socket in an ssl socket:

    DEBUG:ldap3:BASIC:starting tls for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:start EXTENDED operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:EXTENDED request <{'name': '1.3.6.1.4.1.1466.20037', 'value': None}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=1
    >> protocolOp=ProtocolOp:
    >>  extendedReq=ExtendedRequest:
    >>   requestName=b'1.3.6.1.4.1.1466.20037'
    DEBUG:ldap3:NETWORK:sent 31 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=1
    << protocolOp=ProtocolOp:
    <<  extendedResp=ExtendedResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:EXTENDED response <[{'referrals': None, 'dn': '', 'type': 'extendedResp', 'result': 0, 'description': 'success', 'responseName': None, 'responseValue': b'', 'message': ''}]> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done EXTENDED operation, result <True>
    DEBUG:ldap3:BASIC:tls started for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:socket wrapped with SSL using SSLContext for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: [None]:None - remote: [None]:None> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done START TLS operation, result <True>


    # Performing Bind operation with Simple Bind method:

    DEBUG:ldap3:BASIC:start BIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'name': 'cn=admin,o=test', 'authentication': {'sasl': None, 'simple': '<stripped 8 characters of sensitive data>'}, 'version': 3}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=2
    >> protocolOp=ProtocolOp:
    >>  bindRequest=BindRequest:
    >>   version=3
    >>   name=b'cn=admin,o=test'
    >>   authentication=AuthenticationChoice:
    >>    simple=b'<stripped 8 characters of sensitive data>'
    DEBUG:ldap3:NETWORK:sent 37 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  bindResponse=BindResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:BIND response <{'referrals': None, 'dn': '', 'type': 'bindResponse', 'result': 0, 'description': 'success', 'saslCreds': None, 'message': ''}> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:49611 - remote: 192.168.137.104:389> - tls started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <True>


These are the usage metrics of this session::

    Connection Usage:
     Time: [elapsed:        0:00:01.908938]
       Initial start time:  2015-06-02T09:37:49.451263
       Open socket time:    2015-06-02T09:37:49.451263
       Close socket time:
     Server:
       Servers from pool:   0
       Sockets open:        1
       Sockets closed:      0
       Sockets wrapped:     1
     Bytes:                 96
       Transmitted:         68
       Received:            28
     Messages:              4
       Transmitted:         2
       Received:            2
     Operations:            2
       Abandon:             0
       Bind:                1
       Add:                 0
       Compare:             0
       Delete:              0
       Extended:            1
       Modify:              0
       ModifyDn:            0
       Search:              0
       Unbind:              0
     Referrals:
       Received:            0
       Followed:            0
     Restartable tries:     0
       Failed restarts:     0
       Successful restarts: 0

As you can see there have been two operation, one for the bind and one for the startTLS (an extendend operation). One socket
has been open and has been wrapped in SSL. All the communication stream took 96 bytes in 4 LDAP messages.
