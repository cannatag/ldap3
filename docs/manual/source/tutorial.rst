##############
LDAP3 Tutorial
##############

.. tip:: Disclaimer
In this tutorial we will access a public demo of `link FreeIPA <https://www.freeipa.org>`, available at
https://ipa.demo1.freeipa.org. FreeIPA is a fully featured identity management solution, but for the purposes
of this tutorial we're only interested in its LDAP server. Note that the demo server is periodically wiped, as described on the
`link FreeIPA demo wiki page <https://www.freeipa.org/page/Demo>`.


What LDAP is not
================

If you're reading this tutorial I assume that you already know what LDAP is, or have a rough idea of it. If you really
don't know this is not a problem because after reading this tutorial you should be to access an LDAP compliant server
and use it. I'd rather like to be sure that you are aware of what LDAP **is not**:

- it isn't a server
- it isn't a database
- it isn't a network service
- it isn't an authentication procedure
- it isn't a user/password repository
- it isn't an open source neither a closed source product

It's important to know what LDAP is not because people tend to call "LDAP" a peculiar part of what they use of the
*Lightweight Directory Access Protocol*. LDAP is a *protocol*, like many of the other 'trailing-P' words in the Internet
ecosystem (HTTP, FTP, IP, TCP...). It is a set of rules you have to use to communicate with an external
server/database/service/procedure/repository/product (all things in the above list). Data managed via LDAP are
key/value(s) pairs grouped in a hierarchical structure. This hierarchical structure is called the DIT (Directory
Information Tree) but LDAP doesn't specify how the data is stored on the server neither how the user is authorized to
read and modify them. There are only a few data types that every LDAP server must recognize (the standard *schema*
we'll meet later).

That's all, all the (sometime too complex) LDAP machinery you will interact with has this only purpose.

Being a standard protocol, LDAP is not related to any specific product and it's described in a set of RFC (Request for
comments, the official rules of the Internet ecosystem). Its latest version is 3 and is documented in the RFC4510
released in June 2006.


A very brief history of LDAP
============================

You may wonder why the "L" in LDAP? Its ancestor, called DAP (Directory Access Protocol), was developed in the 1980s
by the CCITT (now ITU-T), the International Committee for Telephone and Telegraphy (the venerable entity that gave us, among
others, the fax and the modem protocols we used in the pre-Internet era). DAP was a very heavy and hard to implement protocol
(either for the client and the server components) and was not accessible via TCP/IP. In 1993 a lighter access protocol
was invented to act as a gateway to the DAP world. Afterwards followed server products that could understand LDAP directly
and the gateway to DAP was soon cut off. LDAP v3 was first documented in 1997 and its documentation was revised in 2006.


The ldap3 package
=================

ldap3 is a fully compliant LDAP v3 client library and follows the latest (as per 2015) standard RFCs. It's written from scratch to be
compatible with Python 2 and Python 3 and can be used on any machine where the Python interpreter can access the network via the
standard library.

Chances are that you find the ldap3 package already installed (or installable with the local package manager) on your machine, just try
to **import ldap3** from your Python console.

If you get an ImportError you need to install the package from PyPI via pip::

    pip install ldap3


.. warning::

   If pip complains about certificates you should specify the path to the PyPI CA with the --cert parameter::

   pip install ldap3 --cert /path/to/the/DigiCert_High_Assurance_EV_Root_CA.pem


or you can download the source from `link github https://github.com/cannatag/ldap3`::

    python setup.py install

ldap3 installs the pyasn1 package if not present. This package is used to communicate with the server over the network.

ldap3 usage is straightforward: you define a Server object, a Connection object tied to the Server and then issue commands to it.
A server can have more than one connection and there are different communication strategies to choose from. All the imports
are available in the ldap3 namespace that exposes all you need to interact with the LDAP server. At least you need to import
the Server and the Connection object, and any additional constant you will use in your LDAP conversation (constants are defined
in upper case)::

    from ldap3 import Server, Connection, ALL

Accessing an LDAP server
========================

In the LDAP protocol the login operation is called **bind**. A bind can be performed in 3 different ways: anonymous bind,
simple password bind, and SASL (*Simple Authentication and Security Layer*, allowing multiple authentication methods)
bind. You can think of the anonymous bind as a of *public* access to the LDAP server where you don't provide any credentials
and the server apply some *default* access rules. Not all LDAP servers allow anonymous bind. With the simple password
bind and the SASL bind you provide credentials that the LDAP server uses to determine your authorizazion level.
Again, keep in mind that the LDAP v3 standard doesn't define any specific access level and that the authorization
mechanism is not specified at all. So each LDAP server type can have a different method for authorizing the user to different
access levels.

Let's start accessing the server with an anonymous bind::

    >>> server = Server('ipa.demo1.freeipa.org')
    >>> conn = Connection(server)
    >>> conn.bind()
    True

or shorter::

    >>> conn = Connection('ipa.demo1.freeipa.org', auto_bind=True)
    True

It hardly could be simpler than that! The auto_bind parameter force the bind() operation while creating the Connection object.
We have a full working anonymous connection open and bound to the server with a *synchronous* communication strategy (more on
communication strategies later)::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - cleartext - user: None - bound - open - <local: 192.168.1.101:49813 - remote: 209.132.178.99:389> -
    tls not started - listening - SyncStrategy - internal decoder

With print(conn) we ask the connection for its status and get back a lot of information:

======================================================= ==================================================================
ldap://ipa.demo1.freeipa.org:389                        the server URL (scheme, name and port we are connected to)
cleartext                                               the kind of connection the server is listening to
user: None                                              the credentials used, in this case None means an anonymous binding
bound                                                   the status of the LDAP session
open                                                    the status of the underlying TCP/IP session
<local: 192.168.1.101:51038 - remote: 23.20.46.132:389> the local and remote socket endpoints
tls not started                                         the status of the TLS (Transport Layer Security) session
listening                                               the status of the communication strategy
SyncStrategy                                            the communication strategy used
internal decoder                                        which BER decoder are we using (internal or pyasn1)
======================================================= ==================================================================


.. sidebar:: Object representation

    the ldap3 library uses the following object representation rule: when you use the str() representation you get all
    the information about the status of the object, when you use the repr() you get back a string you can use in the
    Python console to recreate the object.

If you ask for the representation of the conn object you can get a view of all the object definition arguments::

    >>> conn
    Connection(server=Server(host='ipa.demo1.freeipa.org', port=389, use_ssl=False, get_info='NO_INFO'), auto_bind='NONE',
    version=3, authentication='ANONYMOUS', client_strategy='SYNC', auto_referrals=True, check_names=True, read_only=False,
    lazy=False, raise_exceptions=False, fast_decoder=True)

If you just copy and paste the object representation you can instantiate a new one. This is very helpful when experimenting
in the interactive console and works for most of the ldap3 library objects::

   >>> server
   Server(host='ipa.demo1.freeipa.org', port=389, use_ssl=False, get_info='NO_INFO')



Getting info from the server
============================

Now let's try to request more information to the LDAP server::

    >>> server = Server('ipa.demo1.freeipa.org', get_info=ALL)
    >>> conn = Connection(server, auto_bind=True)
    >>> server.info
    DSA info (from DSE):
      Supported LDAP Versions: 2, 3
      Naming Contexts:
        cn=changelog
        dc=demo1,dc=freeipa,dc=org
        o=ipaca
      Alternative Servers: None
      Supported Controls:
        1.2.840.113556.1.4.319 - LDAP Simple Paged Results - Control - RFC2696
        1.2.840.113556.1.4.473 - Sort Request - Control - RFC2891
        1.3.6.1.1.13.1 - LDAP Pre-read - Control - RFC4527
        1.3.6.1.1.13.2 - LDAP Post-read - Control - RFC4527
        1.3.6.1.4.1.1466.29539.12 - Chaining loop detect - Control - SUN microsystems
        1.3.6.1.4.1.42.2.27.8.5.1 - Password policy - Control - IETF DRAFT behera-ldap-password-policy
        1.3.6.1.4.1.42.2.27.9.5.2 - Get effective rights - Control - IETF DRAFT draft-ietf-ldapext-acl-model
        1.3.6.1.4.1.42.2.27.9.5.8 - Account usability - Control - SUN microsystems
        1.3.6.1.4.1.4203.1.9.1.1 - LDAP content synchronization - Control - RFC4533
        1.3.6.1.4.1.4203.666.5.16 - LDAP Dereference - Control - IETF DRAFT draft-masarati-ldap-deref
        2.16.840.1.113730.3.4.12 - Proxied Authorization (old) - Control - Netscape
        2.16.840.1.113730.3.4.13 - iPlanet Directory Server Replication Update Information - Control - Netscape
        2.16.840.1.113730.3.4.14 - Search on specific database - Control - Netscape
        2.16.840.1.113730.3.4.15 - Authorization Identity Response Control - Control - RFC3829
        2.16.840.1.113730.3.4.16 - Authorization Identity Request Control - Control - RFC3829
        2.16.840.1.113730.3.4.17 - Real attribute only request - Control - Netscape
        2.16.840.1.113730.3.4.18 - Proxy Authorization Control - Control - RFC6171
        2.16.840.1.113730.3.4.19 - Chaining loop detection - Control - Netscape
        2.16.840.1.113730.3.4.2 - ManageDsaIT - Control - RFC3296
        2.16.840.1.113730.3.4.20 - Mapping Tree Node - Use one backend [extended] - Control - openLDAP
        2.16.840.1.113730.3.4.3 - Persistent Search - Control - IETF
        2.16.840.1.113730.3.4.4 - Netscape Password Expired - Control - Netscape
        2.16.840.1.113730.3.4.5 - Netscape Password Expiring - Control - Netscape
        2.16.840.1.113730.3.4.9 - Virtual List View Request - Control - IETF
        2.16.840.1.113730.3.8.10.6 - OTP Sync Request - Control - freeIPA
      Supported Extensions:
        1.3.6.1.4.1.1466.20037 - StartTLS - Extension - RFC4511-RFC4513
        1.3.6.1.4.1.4203.1.11.1 - Modify Password - Extension - RFC3062
        1.3.6.1.4.1.4203.1.11.3 - Who am I - Extension - RFC4532
        2.16.840.1.113730.3.5.10 - Distributed Numeric Assignment Extended Request - Extension - Netscape
        2.16.840.1.113730.3.5.12 - Start replication request - Extension - Netscape
        2.16.840.1.113730.3.5.3 - Transaction Response Extended Operation - Extension - Netscape
        2.16.840.1.113730.3.5.4 - iPlanet Replication Response Extended Operation - Extension - Netscape
        2.16.840.1.113730.3.5.5 - iPlanet End Replication Request Extended Operation - Extension - Netscape
        2.16.840.1.113730.3.5.6 - iPlanet Replication Entry Request Extended Operation - Extension - Netscape
        2.16.840.1.113730.3.5.7 - iPlanet Bulk Import Start Extended Operation - Extension - Netscape
        2.16.840.1.113730.3.5.8 - iPlanet Bulk Import Finished Extended Operation - Extension - Netscape
        2.16.840.1.113730.3.5.9 - iPlanet Digest Authentication Calculation Extended Operation - Extension - Netscape
        2.16.840.1.113730.3.6.5 - Replication CleanAllRUV - Extension - Netscape
        2.16.840.1.113730.3.6.6 - Replication Abort CleanAllRUV - Extension - Netscape
        2.16.840.1.113730.3.6.7 - Replication CleanAllRUV Retrieve MaxCSN - Extension - Netscape
        2.16.840.1.113730.3.6.8 - Replication CleanAllRUV Check Status - Extension - Netscape
        2.16.840.1.113730.3.8.10.1 - KeyTab set - Extension - FreeIPA
        2.16.840.1.113730.3.8.10.3 - Enrollment join - Extension - FreeIPA
        2.16.840.1.113730.3.8.10.5 - KeyTab get - Extension - FreeIPA
      Supported SASL Mechanisms:
        EXTERNAL, GSS-SPNEGO, GSSAPI, DIGEST-MD5, CRAM-MD5, PLAIN, LOGIN, ANONYMOUS
      Schema Entry:
        cn=schema
    Vendor name: 389 Project
    Vendor version: 389-Directory/1.3.3.8 B2015.036.047
    Other:
      dataversion:
        020150912040104020150912040104020150912040104
      changeLog:
        cn=changelog
      lastchangenumber:
        3033
      firstchangenumber:
        1713
      lastusn:
        8284
      defaultnamingcontext:
        dc=demo1,dc=freeipa,dc=org
      netscapemdsuffix:
        cn=ldap://dc=ipa,dc=demo1,dc=freeipa,dc=org:389
      objectClass:
        top

This server let an anonymous user to know a lot about it:

========================= ================= =======================================================================
Supported LDAP Versions   2, 3                    The server supports LDAP 2 and 3
Naming contexts           ...                     The server store information for 3 different contexts
Alternative servers       None                    This is the only replica of the database
Supported Controls        ...                     Optional controls that can be sent in a
                                                  request operation
Supported Extentions      ...                     Additional extended operations understood
                                                  by the server
Supported SASL Mechanisms ...                     Different additional SASL authentication mechanisms are available
Schema Entry              cn=schema               The location of the schema in the DIT
Vendor name               389 Project             The brand/mark/name of the LDAP server
Vendor version            389-Directory/1.3.3 ... The version of the LDAP server
Other                     ...                     Additional information provided by the server
                                                  but not requested by the LDAP standard
===================================================================================================================

Now we know that this server is a stand-alone LDAP server that holds objects in the dc=demo1,dc=freeipa,dc=org context,
that supports various SASL access mechanisms and that is based on the 389 Directory Service server. Furthermore in the
Supported Controls we can see it supports "paged searches", and the "who am i" and "StartTLS" extended operation in
Supported Extensions.

.. sidebar:: Controls vs Extensions
    In LDAP a *control* is some additional information that can be attached to any LDAP request or response while an
    *extension* is a completely custom request that can be sent to the LDAP server in an Extended Operation Request.
    A control usually modifies the behaviour of a standard LDAP operation, while an Extension is a completely new
    kind of operation performed by the server.
    Each server declares which controls and which extendend operation it understand. The ldap3 library decodes the
    known supported controls and extended operation and includes a brief description and a reference to the relevant
    RFC in the server.info attribute. Not all controls or extension must be used by clients. Sometimes controls and
    extensions are used by servers that hold a replica or a partition of the data. Unfortunately in the LDAP specifications
    there is no way to understand if such extensions are reserved for server (DSA, Directory Server Agent in LDAP
    parlance) to server communication (for example in replica or partitions management) or can be used
    by clients (DUA, Directory User Agent) because the LDAP protocols doesn't provide a way for DSA to communicate,
    a DSA actually presents itself as a DUA to another DSA.

Let's examine the LDAP server schema::

    >>> server.schema
    DSA Schema from: cn=schema
      Attribute types:{'ipaNTTrustForestTrustInfo': Attribute type: 2.16.840.1.113730.3.8.11.17
      Short name: ipaNTTrustForestTrustInfo
      Description: Forest trust information for a trusted domain object
      Equality rule: octetStringMatch
      Syntax: 1.3.6.1.4.1.1466.115.121.1.40 [('1.3.6.1.4.1.1466.115.121.1.40', 'LDAP_SYNTAX', 'Octet String', 'RFC4517')]
      'ntUserCreateNewAccount': Attribute type: 2.16.840.1.113730.3.1.42
      Short name: ntUserCreateNewAccount
      Description: Netscape defined attribute type
      Single Value: True
      Syntax: 1.3.6.1.4.1.1466.115.121.1.15 [('1.3.6.1.4.1.1466.115.121.1.15', 'LDAP_SYNTAX', 'Directory String', 'RFC4517')]
      Extensions:
        X-ORIGIN: Netscape NT Synchronization
      'passwordGraceUserTime': Attribute type: 2.16.840.1.113730.3.1.998
      Short name: passwordGraceUserTime, pwdGraceUserTime
      Description: Netscape defined password policy attribute type
      Single Value: True
      Usage: Directory operation
      Syntax: 1.3.6.1.4.1.1466.115.121.1.15 [('1.3.6.1.4.1.1466.115.121.1.15', 'LDAP_SYNTAX', 'Directory String', 'RFC4517')]
      Extensions:
        X-ORIGIN: Netscape Directory Server
      'nsslapd-ldapilisten': Attribute type: 2.16.840.1.113730.3.1.2229
      Short name: nsslapd-ldapilisten
      Description: Netscape defined attribute type
      Single Value: True
      Syntax: 1.3.6.1.4.1.1466.115.121.1.15 [('1.3.6.1.4.1.1466.115.121.1.15', 'LDAP_SYNTAX', 'Directory String', 'RFC4517')]
      Extensions:
        X-ORIGIN: Netscape Directory Server
      'bootParameter': Attribute type: 1.3.6.1.1.1.1.23
      Short name: bootParameter
      Description: Standard LDAP attribute type
      Syntax: 1.3.6.1.4.1.1466.115.121.1.26 [('1.3.6.1.4.1.1466.115.121.1.26', 'LDAP_SYNTAX', 'IA5 String', 'RFC4517')]
      Extensions:
        X-ORIGIN: RFC 2307

      < a very long list of descriptors follows...>


The schema is a very long list that describes what kind of data types the LDAP server understands. It also specifies
what attributes can be stored in each class.
Some classes are container for other objects (either containers or leaf objects) and are used to build the hierarchy of
the Directory Information Tree. Container objects can have attributes too. Every LDAP server must at least support the
standard LDAP3 schema but can have additional custom classes and attributes. The schema defines also the syntaxes and the
matching rules of the different kind of data types stored in the LDAP.

.. note::
    Object classes and attributes are independent objects in LDAP, an attribute is not a "child" of a class neither a
    class is a "parent" of any attribute. Classes and attributes are linked in the schema with the MAY and MUST options
    of the object class that specify what attributes an entry of a specified class can contain and which of them are mandatory.

.. sidebar::
    There are 3 different types of object classes: ABSTRACT (used only for defining the class hiearchy), STRUCTURAL (used to
    create concrete entries) and AUXILIARY (used to add additional attributes to an entry. Only one structural class can be used
    in an entry, while many auxiliary classes can be added to the same entry. Adding an object class to an entry simply means
    that the attributes defined in that object class can be stored in the entry.

When reading the schema the ldap3 library will try to automatically convert data to their representation. So an integer
will be returned as an int, a generalizedDate as a datetime object and so on. If you don't read the schema all the values
are returned as bytes and unicode strings. You can control this behaviour with the get_info parameter of the Server object
and the check_names parameter of the Connection object.

Did you note that we still didn't give any credentials to the server? LDAP allow users to perform operation anonymously without declaring their
identity! Obviously what the server returns to an anonymous connection is someway limited. This makes sense because originally the DAP
protocol was intended for reading phone directories, as a printed book, so its content could be read by anyone. If you want to establish
a logged connection you have a two options: Simple and SASL. With Simple authentication you provide a distinguished name and a password.
The server will check if your credentials are valid and will permit or deny access to the data. SASL provides additional methods to identify
the user as external certificate or Kerberos.

.. note::
    With ldap3 you can also connect to an Active Directory server with the NTLM v2 protocol::

        # import class and constants
        from ldap3 import Server, Connection, SIMPLE, SYNC, ALL, SASL, NTLM)

        # define the server and the connection
        s = Server('servername', get_info=ALL)
        c = Connection(s, user="Domain\\User", password="password", authentication=NTLM)

    This kind of authentication is not specified in the LDAP 3 RFCs but it's a proprietary Microsoft method called SICILY

Let's ask the server who we are::

    >>> conn.extend.standard.who_am_i()

We get an empty response. This means we have no authentication status on the server, we are an **anonymous** user. This doesn't mean
that we are unknown to the server, actually we have a session open with the server and we can send additional operation requests without
binding again. Even if we don't send the anonymous bind operation the server will accept our operation requests as an anonymous user.

.. note:: Opening vs Binding
    The LDAP protocol provides a Bind and an Unbind operation but, for historical reasons, they are not symmetric. In fact before binding
    to the server the connection must be open. This is implicitly done by the ldap3 package when you issue a Bind or another operation or
    can be esplicity done with the **open()** method of the Connection object. The Unbind operation is actually used to *terminate* the
    connection, both ending the session and closing the connection. so it cannot be used anymore. If you want to access as another user or change the
    current session to an anonymous, just issue another Bind without Unbinding the connection.

Let's try to specify a valid user::

    >>> conn = Connection(server, 'uid=manager, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
    >>> conn.extend.standard.who_am_i()
    'dn: uid=manager,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org'

Now the server knows that we are a valid user and the who_am_i() extended operation returns our identity.

Establishing a secure connection
================================

If we check the connection info we see that we are using a cleartext (insecure) channel::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - **cleartext** - user: uid=manager, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:50164 - remote: 209.132.178.99:**389**> - **tls not started** - listening - SyncStrategy - internal decoder'

Our credentials pass unencrypted over the wire, so they an be easily captured with a network sniffer. The LDAP protocol provides two ways
to secure a connection: LDAP over TLS (or SSL) or the StartTLS extended operation. This two method both ending in establishing a secure TLS connection
but with the former the communication channel is secured with TLS as soon as the connection is open, while with the latter the connection is open as
unsecure and then the channel is secured when we issue the StartTLS operation.

.. note:: LDAP URL scheme
    A cleartext connection to a server can be expressed in a URL with schema **ldap://**. Usually the LDAP over TLS is indicated as **ldaps://** even if
    this is not indicated in the lDAP specifications. If a URL is indicated while creating the Server object the ldap3 library recognize the URL schema and
    open the proper port in clear or with the specified (or default, if none is specified) TLS options.

.. sidebar:: Default port numbers
   The default ports for *cleartext* (unsecure) communication is 389, while the default for *LDAP over TLS* (secure) communication is 636. Note
   that because you can start a session on the 389 port and then increase the security level with the StartTLS operation, you can have a secure
   communication even on the 389 port (usually considered unsecure). Obviously the server can listen on additional or different ports. When
   defining the Server object you can specify which port to use with the *port* parameter.


Let's try to use the StartTLS extended operation::

    >>> conn.start_tls()
    True

if we check the conn status we see that the connection is on a secure channel, even if started on a cleartext connection::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - **cleartext** - user: uid=manager, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:50910 - remote: 209.132.178.99:**389**> - **tls started** - listening - SyncStrategy - internal decoder


THere is no way to return to an unencrypted connection once a StartTLS operation is issued.

To start the connection on a SSL socket::

    >>> server = Server('ipa.demo1.freeipa.org', use_ssl=True, get_info=ALL)
    >>> conn = Connection(server, 'uid=manager, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
    >>> print(conn)
    ldaps://ipa.demo1.freeipa.org:636 - **ssl** - user: uid=manager, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:51438 - remote: 209.132.178.99:**636**> - **tls not started** - listening - SyncStrategy - internal decoder


Either with the former or the latter method the connection is now encrypted. We haven't specified any TLS option, so there is no check of
certificate validity. You can customize the SSL behaviour providing a Tls object to the Server object with the SSL context configuration::

    >>> from ldap3 import Server, Connection, Tls
    >>> import ssl
    >>> tls_configuration = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1)
    >>> server = Server('ipa.demo1.freeipa.org', use_ssl=True, tls=tls_configuration)
    >>> conn = Connection(server)
    >>> conn.open()
    ...
    ldap3.core.exceptions.LDAPSocketOpenError: (LDAPSocketOpenError('socket ssl wrapping error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:600)',),)

Here we get a LDAPSocketOpenError exception because the certificate cannot be verified. You can configure the Tls object with a number of options. Look at :ref:`the SSL and TLS documentation <ssltls>`


Performing searches
===================


... more to come ...
