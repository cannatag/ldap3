##############
ldap3 Tutorial
##############

.. note::
    In this tutorial we will access a public demo of `FreeIPA`_, available at https://ipa.demo1.freeipa.org (you must trust
    its certificate on first login). FreeIPA is a fully featured identity management solution, but for the purposes of this
    tutorial we're only interested in its LDAP server. Note that the demo server is periodically wiped, as described on the
    `FreeIPA demo wiki page`_.

    .. _FreeIPA: https://www.freeipa.org
    .. _FreeIPA demo wiki page: https://www.freeipa.org/page/Demo

.. warning::
    If you receive an ``LDAPSocketReceiveError: error receiving data`` exception the server could have
    closed the connection abruptly. You can easily reopen it with the ``conn.bind()`` method.

What LDAP is not
================

If you're reading this tutorial I assume that you already know what LDAP is, or at least have a rough idea of it. If you really
don't know anything about LDAP after reading this tutorial you should be able to access an LDAP compliant server and use it without bothering with
the many glitches of the LDAP protocol.

I'd rather want to be sure that you are aware of what LDAP **is not**:

- is not a server
- is not a database
- is not a network service
- is not an authentication procedure
- is not a user/password repository
- is not an open source neither a closed source product

It's important to know what LDAP is not because people usually call "LDAP" a peculiar part of what they use of the
*Lightweight Directory Access Protocol*. LDAP is a *protocol* and as other 'trailing-P' words in the Internet
ecosystem (HTTP, FTP, TCP, IP, ...) it is a set of rules you must use to communicate with an external
server/database/service/procedure/repository/product (all the things in the above list). Data managed via LDAP are
key/value(s) pairs grouped in a hierarchical structure. This hierarchical structure is called the *DIT* (Directory
Information Tree). LDAP doesn't specify how the data is actually stored on the server neither how the user is authorized to
read and modify them. There are only a few data types that every LDAP server must recognize (the standard *schema*
we'll meet later).

That's all, all the (sometime too complex) LDAP machinery you will interact with has this only purpose.

Being a protocol, LDAP is not related to any specific product and it is described in a set of *RFC* (Request for
comments, the official rules of the Internet ecosystem). Its latest version is 3 and is documented in the RFC4510 and subsequents RFCs
released in June 2006.


A very brief history of LDAP
============================

You may wonder why the "L" in LDAP? Its ancestor, called DAP (Directory Access Protocol), was developed in the 1980s
by the CCITT (now ITU-T), the *International Committee for Telephone and Telegraphy* (the venerable entity that gave us, among
others, the fax and the modem protocols we used in the pre-Internet era). DAP was a very heavy and hard to implement protocol
(either for the client and the server components) and was not accessible via TCP/IP. In 1993 a lighter access protocol
was invented at the University of Michigan to act as a gateway to the DAP world. Afterwards followed server products that
could understand LDAP directly and the gateway to DAP was soon cut off. LDAP v3 was first documented in 1997 and its
specifications was revised in 2006. THis specifications are strictly followed by the ldap3 library.


The ldap3 package
=================

ldap3 is a fully compliant LDAP v3 client library and follows the latest standard RFCs. It's written from scratch to be
compatible with Python 2 and Python 3 and can be used on any machine where the Python interpreter can access the network via the Python
standard library.

Chances are that you find the ldap3 package already installed (or installable with the local package manager) on your machine, just try
to **import ldap3** from your Python console.

If you get an ImportError you need to install the package from PyPI via pip::

    pip install ldap3


.. warning::
   If pip complains about certificates you should specify the path to the PyPI CA certificate with the --cert parameter::

   pip install ldap3 --cert /path/to/the/DigiCert_High_Assurance_EV_Root_CA.pem


or you can download the source from https://github.com/cannatag/ldap3 and install it with::

    python setup.py install

ldap3 installs the **pyasn1** package (if not already present). This package is used to communicate with the server over the network.

ldap3 usage is straightforward: you define a Server object, a Connection object tied to the Server and then you issue commands to it.
A server can have more than one connection and there are different *communication strategies* to choose from. All the imports
are available in the ldap3 namespace. At least you need to import the Server and the Connection object, and any additional constant you
will use in your LDAP conversation (constants are defined in upper case)::

    >>> from ldap3 import Server, Connection, ALL

Accessing an LDAP server
========================

In the LDAP protocol the login operation is called **bind**. A bind can be performed in 3 different ways: anonymous bind,
simple password bind, and SASL (*Simple Authentication and Security Layer*, allowing multiple authentication methods)
bind. You can think of the anonymous bind as a of *public* access to the LDAP server where you don't provide any credentials
and the server applies some *default* access rules. With the simple password bind and the SASL bind you provide credentials
that the LDAP server uses to determine your authorizazion level. Again, keep in mind that the LDAP v3 standard doesn't define
any specific access rules and that the authorization mechanism is not specified at all. So each LDAP server type can have a
different method for authorizing the user to access data stored in the DIT.

ldap3 let you choose the strategy that the client will use to connect to the server with the ``client_strategy`` parameter of the
Connection object. There are 5 strategies that can be used for establishing a connection: SYNC, ASYNC, LDIF, RESTARTABLE and REUSABLE.

With synchronous strategies (**SYNC**, **RESTARTABLE**) all LDAP operations return a boolean: ``True`` if they're successful, ``False``
if they fail.

With asynchronous strategies (**ASYNC**, **REUSABLE**) all LDAP operations (except Bind that always returns a boolean) return an
integer, the *message_id* of the request. You can send multiple requests without waiting for responses and then get each
response with the ``get_response(message_id)`` method of the Connection object as you need it. You will get an exception if
the response has not yet arrived after a specified time. In the get_response method this timeout value can be set
with the ``timeout`` attribute to the number of seconds to wait for the response to appear (defaults is 10 seconds).

The **LDIF** strategy is used to create a stream of LDIF-CHANGEs.

.. note::
    In this tutorial we will use the default SYNC communication strategy.

Let's start accessing the server with an anonymous bind::

    >>> server = Server('ipa.demo1.freeipa.org')
    >>> conn = Connection(server)
    >>> conn.bind()
    True

or shorter::

    >>> conn = Connection('ipa.demo1.freeipa.org', auto_bind=True)
    True

It hardly could be simpler than that. The ``auto_bind`` parameter forces the bind() operation while creating the Connection object.
We have now a full working anonymous connection open and bound to the server with a *synchronous* communication strategy (more on
communication strategies later)::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - cleartext - user: None - bound - open - <local: 192.168.1.101:49813 - remote: 209.132.178.99:389> -
    tls not started - listening - SyncStrategy - internal decoder

With print(conn) we ask to the connection its status and get back a lot of information:

======================================================= ==================================================================
ldap://ipa.demo1.freeipa.org:389                        the server URL (scheme, name and port we are connected to)
cleartext                                               the kind of connection the server is listening to
user: None                                              the credentials used, in this case None means an anonymous binding
bound                                                   the status of the LDAP session
open                                                    the status of the underlying TCP/IP session
<local: 192.168.1.101:51038 - remote: 23.20.46.132:389> the local and remote communication endpoints
tls not started                                         the status of the TLS (Transport Layer Security) session
listening                                               the status of the communication strategy
SyncStrategy                                            the communication strategy used
internal decoder                                        which BER decoder are we using (internal or pyasn1)
======================================================= ==================================================================


.. sidebar:: Object representation
    the ldap3 library uses the following object representation rule: when you use the str() representation you get all
    the information about the status of the object, when you use the repr() you get back a string you can use in the
    Python console to recreate the object.

If you ask for the representation of the ``conn`` object you can get a view of all the object definition arguments::

    >>> conn
    Connection(server=Server(host='ipa.demo1.freeipa.org', port=389, use_ssl=False, get_info='NO_INFO'), auto_bind='NONE',
    version=3, authentication='ANONYMOUS', client_strategy='SYNC', auto_referrals=True, check_names=True, read_only=False,
    lazy=False, raise_exceptions=False, fast_decoder=True)

If you just copy and paste the object representation you can instantiate a new one. This is very helpful when experimenting
in the interactive console and works for most of the ldap3 library objects::

   >>> server
   Server(host='ipa.demo1.freeipa.org', port=389, use_ssl=False, get_info='NO_INFO')


Getting information from the server
===================================

The LDAP protocol specifies that an LDAP server must return some information about itself. We can requeste them with the ``get_info=ALL``
parameter and access them with the ``.info`` attribute of the Server object::

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

This server (like most LDAP servers) lets an anonymous user to know a lot about it:

========================= ======================= =============================================================
Supported LDAP Versions   2, 3                    The server supports LDAP 2 and 3
Naming contexts           ...                     The server stores information for 3 different DIT portions
Alternative servers       None                    This is the only replica of the database
Supported Controls        ...                     Optional controls that can be sent in a request operation
Supported Extentions      ...                     Additional extended operations understood by the server
Supported SASL Mechanisms ...                     Different additional SASL authentication mechanisms available
Schema Entry              cn=schema               The location of the schema in the DIT
Vendor name               389 Project             The brand/mark/name of the LDAP server
Vendor version            389-Directory/1.3.3 ... The version of the LDAP server
Other                     ...                     Additional information provided by the server
========================= ======================= =============================================================

Now we know that this server is a stand-alone LDAP server that can hold entries in the dc=demo1,dc=freeipa,dc=org context,
that supports various SASL access mechanisms and that is based on the 389 Directory Service server. Furthermore in the
Supported Controls we can see it supports "paged searches", and the "who am i" and "StartTLS" extended operations in
Supported Extensions.

.. sidebar:: Controls vs Extensions
    In LDAP a *control* is some additional information that can be attached to any LDAP request or response while an
    *extension* is a custom request that can be sent to the LDAP server in an Extended Operation Request.
    A control usually modifies the behaviour of a standard LDAP operation, while an extension is a completely new
    kind of operation performed by the server.
    Each server declares which controls and which extendend operations it understand. The ldap3 library decodes the
    known supported controls and extended operation and includes a brief description and a reference to the relevant
    RFC in the ``server.info`` attribute. Not all controls or extensions must be used by clients. Sometimes controls and
    extensions are used by servers that hold a replica or a partition of the data. Unfortunately in the LDAP specifications
    there is no way to understand if such extensions are reserved for server (*DSA*, Directory Server Agent in LDAP
    parlance) to server communication (for example in replica or partitions management) or can be used
    by clients (*DUA*, Directory User Agent). Because the LDAP protocols doesn't provide a specific way for DSAs to communicate,
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

      <...list of descriptors...>


The schema is a very long list that describes what kind of data types the LDAP server understands. It also specifies
what attributes can be stored in each class. Some classes are containers for other entries (either containers or leaf)
and are used to build the hierarchy of the DIT. Container entries can have attributes too.
One important specification in the schema is if the attribute is *multi-valued*. A multi-valued attribute stores more than a value
and all values are returned when the attribute is requested in a search. Every LDAP server must at least support
the standard LDAP3 schema but can have additional custom classes and attributes. The schema defines also the *syntaxes* and the
*matching rules* of the different kind of data types stored in the LDAP.

.. note::
    Object classes and attributes are independent objects. An attribute is not a "child" of a class neither a
    class is a "parent" of any attribute. Classes and attributes are linked in the schema with the ``MAY`` and ``MUST`` options
    of the object class definition that specify what attributes an entry can contain and which of them are mandatory.

.. sidebar::
    There are 3 different types of object classes: ABSTRACT (used only for defining the class hiearchy), STRUCTURAL (used to
    create concrete entries) and AUXILIARY (used to add additional attributes to an entry). Only one structural class can be used
    in an entry, while many auxiliary classes can be added to the same entry. Adding an object class to an entry simply means
    that the attributes defined in that object class can be stored in that entry.

While reading the schema the ldap3 library will try to automatically convert data to their representation. So an integer
will be returned as an int, a generalizedDate as a datetime object and so on. If you don't read the schema all the values
are returned as bytes and unicode strings. You can control this behaviour with the ``get_info`` parameter of the Server object
and the ``check_names`` parameter of the Connection object.

Logging into the server
=======================

We have not provided any credentials to the server yet. LDAP allow users to perform operations anonymously without
declaring their identity! Obviously what the server returns to an anonymous connection is someway limited. This makes sense because
originally the DAP protocol was intended for reading phone directories, as in a printed book, so its content could be read by anyone.

If you want to establish an authenticated connection you have two options: Simple and SASL. With Simple authentication you provide
a Distinguished Name and a password. The server checks if your credentials are valid and will permit or deny access to the data.
SASL provides additional methods to identify the user, as an external certificate or a Kerberos ticket.

.. sidebar:: Distinguished Names
    The DIT is a hierarchical structure, as a filesystem. To identify an entry you must specify its *path* starting from the top
    of the Tree down to the last leaf that represents the entry. This path is called the **Distinguished Name** (DN) of an entry and is
    constructed with the names, separated by a comma, of all the entries that form the path from the leaf to the top of the Tree.
    The DN of an entry is unique in throughout the DIT and changes only if you move the entry to another container within the DIT.
    The parts of the DN are called **Relative Distinguished Name** (RDN) because are unique only in the context where they are defined. So,
    for example, if you have a *person* entry with RDN ``cn=Fred`` that is stored in an *organizational unit* with RDN ``ou=users``
    that is stored in an *organization* with RDN ``o=company`` the DN of the *person* entry will be ``cn=Fred, ou=users, o=company``.
    The RDN value must be unique in the context where the entry is stored, but there is no specification in the LDAP schema on which
    attribute to use as RDN for a specific class.

.. note::
    With ldap3 you can also connect to an Active Directory server with the NTLM v2 protocol::

        # import class and constants
        >>> from ldap3 import Server, Connection, SIMPLE, SYNC, ALL, NTLM

        # define the server and the connection
        >>> server = Server('servername', get_info=ALL)
        >>> conn = Connection(server, user="Domain\\User", password="password", authentication=NTLM)

    This kind of authentication is not part of the LDAP 3 RFCs but uses a proprietary Microsoft authentication mechanism (SICILY).

Let's ask the server who we are::

    >>> conn.extend.standard.who_am_i()

We get an empty response. This means we have no authentication status on the server, so we are an **anonymous** user. This doesn't mean
that we are unknown to the server, actually we have a session open with the server and we can send additional operation requests. Even
if we don't send the anonymous bind operation the server will accept our operation requests as an anonymous user.

.. note:: Opening vs Binding
    The LDAP protocol provides a Bind and an Unbind operation but, for historical reasons, they are not symmetric. In fact before binding
    to the server the connection must be *open*. This is implicitly done by the ldap3 package when you issue a Bind or another operation or
    can be esplicity done with the ``open()`` method of the Connection object. The Unbind operation is actually used to *terminate* the
    connection, both ending the session and closing the connection. so it cannot be used anymore. If you want to access as another user
    or change the current session to an anonymous one, just issue another Bind. You must Unbind the connection only when you wnat to
    close the network transport.

Let's try to specify a valid user::

    >>> conn = Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
    >>> conn.extend.standard.who_am_i()
    'dn: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org'

Now the server knows that we are a recognized user and the ``who_am_i()`` extended operation returns our identity.

Establishing a secure connection
================================

If we check the connection info we see that we are using a cleartext (insecure) channel::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - **cleartext** - user: uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:50164 - remote: 209.132.178.99:**389**> - **tls not started** - listening - SyncStrategy - internal decoder'

Our credentials pass unencrypted over the wire, so that they can be easily captured by a network sniffer. The LDAP protocol provides two ways
to secure a connection: **LDAP over TLS** (or over SSL) or the **StartTLS** extended operation. This two methods both establish a secure TLS
connection but with the former the communication channel is secured with TLS as soon as the connection is open, while with the latter the
connection is open as unsecure and then the channel is secured issuing the StartTLS operation. StartTLS be done once at any time after the
connection is established, but once issued there is no way to revert the socket to a cleartext state.

.. note:: LDAP URL scheme
    A cleartext connection to a server can be expressed in a URL with the **ldap://** scheme, while LDAP over TLS is indicated as **ldaps://** (even if
    this is not specified in any of the LDAP RFCs). If a scheme is included in the server name while creating the Server object, the ldap3 library
    opens the proper port, unencrypted or with the specified TLS options (or default options if none is specified).

.. sidebar:: Default port numbers
    The default port for cleartext (unsecure) communication is **389**, while the default for LDAP over TLS (secure) communication is **636**. Note
    that because you can start a session on the 389 port and then raise the security level with the StartTLS operation, you can have a secure
    communication even on the 389 port (usually considered unsecure). Obviously the server can listen on additional or different ports. When
    defining the Server object you can specify which port to use with the ``port`` parameter. Keep this in mind if you need to put your server
    behind a firewall.

Let's try to use the StartTLS extended operation::

    >>> conn.start_tls()
    True

if we check the conn status we see that the connection is on a secure channel now, even if started on a cleartext connection::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:50910 - remote: 209.132.178.99:389> - tls started - listening - SyncStrategy - internal decoder


To start the connection on a SSL socket::

    >>> server = Server('ipa.demo1.freeipa.org', use_ssl=True, get_info=ALL)
    >>> conn = Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
    >>> print(conn)
    ldaps://ipa.demo1.freeipa.org:636 - ssl - user: uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:51438 - remote: 209.132.178.99:636> - tls not started - listening - SyncStrategy - internal decoder

Either with the former or the latter method the connection is now encrypted. We haven't specified any TLS option, so there is no checking of
certificate validity. You can customize the TLS behaviour providing a Tls object to the Server object using the security context configuration::

    >>> from ldap3 import Server, Connection, Tls
    >>> import ssl
    >>> tls_configuration = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1)
    >>> server = Server('ipa.demo1.freeipa.org', use_ssl=True, tls=tls_configuration)
    >>> conn = Connection(server)
    >>> conn.open()
    ...
    ldap3.core.exceptions.LDAPSocketOpenError: (LDAPSocketOpenError('socket ssl wrapping error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:600)',),)

In this specific case, using the FreeIPA demo server we get a LDAPSocketOpenError exception because the certificate cannot be verified.
You can configure the Tls object with a number of options. Look at :ref:`the SSL and TLS documentation <ssltls>` for more information.

Database Operations
===================

As any system that stores data, LDAP lets you perform the standard CRUD (Create, Read, Update, Delete) operations, but their usage is someway rudimentary.
Again, if you think of the intended use of the original DAP protocol (storing key-values pairs related to an entry in a phone directory)
this makes sense: an entry is written once, seldom modified, and eventually deleted, so the create (**Add** in LDAP), update (**Modify** or **ModifyDn**)
and delete (**Delete**) operations have a very basic usage while the Read (**Search**) operation is richer of options, but lacks many capabilities
you would expect in a modern query language (as 1 to N relationship, joining views, or server data manipulation). Nonetheless almost everything you can do in a modern
database can be equally done in LDAP. Furthermore consider that even if an LDAP server can be accessed by multiple clients simultaneously, the LDAP
protocol itself has no notion of "transaction", so if you want to issue multiple Add or Modify operations in an atomic way (to keep your data consistent),
you must investigate the extended operations of the specific LDAP server you're connecting to to check if it supports transactions for multiple operations.

.. note:: Synchronous vs Asynchronous
    You can submit operations to the server in two different ways: **synchronous** mode and **asynchronous** mode. While in the former mode you send the request and
    wait for the response, in the latter mode the ldap3 library constantly listens to the server (one independent thread for each connection). When you send a request you must
    store its *message id* (a unique number that ldap3 stamps on every message of your LDAP session) in your code so you can later query the Connection object for the
    relevant response when it's ready. You'll probably stick with the synchronous mode, because nowadays LDAP servers are fast to respond, but the asynchronous mode is
    still useful if your program is event-driven (maybe using an asynchronous event loop).

    ldap3 supports both of this models with its different *communication strategies*.

LDAP also provides the **Compare** operation that returns True only if an attribute has the value you specify in the request. Even if this operation seems redundant
(you could read the attribute and perform the comparison using more powerful tools in your code) you need it to check for the presence
of a value (even in a multi-valued attribute) without having the permission to read it. This obviuosly relies upon some "access restriction" mechanism that must
be present on the server. LDAP doesn't specify how this mechanism works, so each LDAP server has its specific way of handle authorization. The Compare operation is also used to
check the validity of a password (that you can't read) without performing a Bind operation with the specific user.

After any synchronous operation, you'll find the following attributes populated in the Connection object:

* ``result``: the result of the last operation (as returned by the server)
* ``response``: the entries found (if the last operation is a Search)
* ``entries``: the entries found exposed via the abstraction layer (if the last operation is a Search)
* ``last_error``: the error occurred in the last operation, if any
* ``bound``: True if the connection is bound to the server
* ``listening``: True if the socket is listening to the server
* ``closed``: True if the socket is not open


Performing searches
===================

The Search operation in ldap3 has a number of parameters, but only two of them are mandatory:

* ``search_base``: the location in the DIT where the search will start
* ``search_filter``: what are you searching

Search filters are based on assertions and look odd when you're unfamiliar with their syntax. One *assertion* is a bracketed expression
that affirms something about an attribute and its value, as ``(givenName=John)`` or ``(maxRetries>=10)``. Each assertion resolves
to True, False or Undefined (that is treated as False) for one or more entries in the Tree. Assertions can be grouped in boolean groups
where all assertions (*and* group, specified with ``&``) or just one assertion (*or* group, specified with ``|``) must be True. A single
assertion can be negated (*not* group, specified with ``!``). Each group must be bracketed, allowing for recursive filters.
Operators allowed in an assertion are ``=`` (*equal*), ``<=`` (*less than or equal*), ``>=`` (*greater than or equal*), ``=*`` (*present*), ``~=``
(*aproximate*) and ``:=`` (*extensible*). Surprisingly the *less than* and the *greater than* operators don't exist in the filter syntax.
The *aproximate* and the *extensible* are someway obscure and seldom used. In an equality filter you can use the ``*`` (asterisk) as a wildcard in the usual way.

For example, to search for all users named John with an email ending with '@example.org' the filter will be ``(&(givenName=John)(mail=*@example.org))``,
to search for all users named John or Fred with an email ending in '@example.org' the filter will be
``(&(|(givenName=Fred)(givenName=John))(mail=*@example.org))``, while to search for all users that have a givenName different from Smith the filter
will be ``(&(givenName=*)(!(givenName=Smith)))`` (The first assertion in the *and* set is needed to ensure the presence of the value). Longer
search filters can easily become hard to understand so it may be useful to divide them on multple lines while writing/reading them::

    (&
        (|
            (givenName=Fred)
            (givenName=John)
        )
        (mail=*@example.org)
    )


Let's try to search all the users in the FreeIPA demo LDAP server::

    >>> from ldap3 import Server, Connection, ALL
    >>> server = Server('ipa.demo1.freeipa.org', get_info=ALL)
    >>> conn = Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
    >>> conn.search('dc=demo1, dc=freeipa, dc=org', '(objectclass=person)')
    True
    >>> conn.entries
    [DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    , DN: uid=manager,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    , DN: uid=employee,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    , DN: uid=helpdesk,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    ]

Here we are requesting all the entries of class *person*, starting from the *dc=demo1, dc=freeipa, dc=org* context with the default subtree scope.
We have not requested any attribute, so in the response we get only the Distinguished Name of the entries found.

Now let's try to request some attributes for the admin user::

    >>> conn.search('dc=demo1, dc=freeipa, dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn','krbLastPwdChange', 'objectclass'])
    True
    >>> conn.entries[0]
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
        krbLastPwdChange: 2015-09-30 04:06:59+00:00
        objectclass: top
                     person
                     posixaccount
                     krbprincipalaux
                     krbticketpolicyaux
                     inetuser
                     ipaobject
                     ipasshuser
                     ipaSshGroupOfPubKeys
        sn: Administrator


.. note::
    When using attributes in a search filter it's a good habit to always request for the class of the entries you expect to retrieve. You cannot be sure that the
    attribute you're serching for is not used is some other object classes, and even if you were sure that no other object class uses the attribute this could always change
    in the future when someone creates in the schema a new object class that uses that same attribute and your program suddenly breaks with no apparent reason.


As you can see the ``entries`` attribute of the Connection object is specially crafted to be used in interactive mode. It gives a visual
representation of the entry data structure where each value is, according to the schema, properly formatted (the date value in krbLastPwdChange is
actually stored as ``b'20150930040659Z'``). Attributes can be queried as if the entry were a class object or a dict, with some
additional features as case-insensitivity and blank-insensitivity. You can get the formatted value and the raw value (the value actually
returned by the server) in the ``values`` and ``raw_values`` attribute::

    >>> entry = entries[0]
    >>> entry.krbLastPwdChange
    krbLastPwdChange: 2015-09-30 04:06:59+00:00
    >>> entry.KRBLastPwdCHANGE
    krbLastPwdChange: 2015-09-30 04:06:59+00:00
    >>> entry['krbLastPwdChange']
    krbLastPwdChange: 2015-09-30 04:06:59+00:00
    >>> entry['KRB LAST PWD CHANGE']
    krbLastPwdChange: 2015-09-30 04:06:59+00:00

    >>> entry.krbLastPwdChange.values
    [datetime.datetime(2015, 9, 30, 4, 6, 59, tzinfo=OffsetTzInfo(offset=0, name='UTC'))]
    >>> entry.krbLastPwdChange.raw_values
    [b'20150930040659Z']


In the previous search operations we specified ``dc=demo1, dc=freeipa, dc=org`` as the base of our search, but the entries we got back were in the ``cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org``
context of the DIT. So the server has, for some unapparent reason, walked down in every context under the base and applied the filter to each of the entries in the sub-contexts.
It actually performed a *whole subtree* search. Other possible kinds of search are the *single level* (that searches only in the level specified in the base) and the *base object*
(that search only in the attributes of the entry specified in the base). What changes in this different kinds of search is the breath of the portion of
the LDAP database that is searched. This is called the **scope** of the search and can be specified with the ``search_scope`` attribute of the search
operation. It can assume three different values ``BASE``, ``LEVEL`` and ``SUBTREE``. The latter value is the default for the search opertion, so this clarifies why we
got back all the entries in the sub-contexts of the base in our previous searches.


You can have a LDIF representation of the response of a search with::

    >>> print(conn.entries[0].entry_to_ldif())
    version: 1
    dn: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    objectclass: top
    objectclass: person
    objectclass: posixaccount
    objectclass: krbprincipalaux
    objectclass: krbticketpolicyaux
    objectclass: inetuser
    objectclass: ipaobject
    objectclass: ipasshuser
    objectclass: ipaSshGroupOfPubKeys
    krbLastPwdChange: 20150930040659Z
    sn: Administrator
    # total number of entries: 1

.. sidebar:: LDIF
    LDIF stands for LDAP Data Interchange Format and is a textual standard used to describe two different aspects of LDAP: the content of an entry (**LDIF-CONTENT**)
    or the changes performed to an entry with an LDAP operation (**LDIF-CHANGE**). LDIF-CONTENT is used to describe LDAP entries in an ASCII stream (i.e. a file),
    while LDIF-CHANGE is used to describe the Add, Delete, Modify and ModifyDn operations.

    *These two formats have different purposes and cannot be mixed in the same stream.*

or you can save the response to a JSON string::

    >>> print(entry.entry_to_json())
    {
        "attributes": {
            "krbLastPwdChange": [
                "2015-09-30 04:06:59+00:00"
            ],
            "objectclass": [
                "top",
                "person",
                "posixaccount",
                "krbprincipalaux",
                "krbticketpolicyaux",
                "inetuser",
                "ipaobject",
                "ipasshuser",
                "ipaSshGroupOfPubKeys"
            ],
            "sn": [
                "Administrator"
            ]
        },
        "dn": "uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org"

Searching for binary values
===========================
To search for a binary value you must use the RFC4515 escape ASCII sequence for each byte in the search assertion. You
can use the function *escape_bytes()* in ldap3.utils.conv for properly escape a byte sequence::

    >>> from ldap3.utils.conv import escape_bytes
    >>> unique_id = b'\xca@\xf2k\x1d\x86\xcaL\xb7\xa2\xca@\xf2k\x1d\x86'
    >>> search_filter = '(nsUniqueID=' + escape_bytes(unique_id) + ')'
    >>> conn.search('dc=demo1, dc=freeipa, dc=org', search_filter, attributes=['nsUniqueId'])

search_filter will contain ``'(guid=\\ca\\40\\f2\\6b\\1d\\86\\ca\\4c\\b7\\a2\\ca\\40\\f2\\6b\\1d\\86)'``.

Connection context manager
==========================

Connections respond to the context manager protocol, so you can have automatic open, bind and unbind with the following syntax::

    >>> with Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123') as conn:
            conn.search('dc=demo1, dc=freeipa, dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn','krbLastPwdChange', 'objectclass'])
            entry = conn.entries[0]
    True
    >>> conn.bound
    False
    >>> entry
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    krbLastPwdChange: 2015-09-30 04:06:59+00:00
    objectclass: top
                 person
                 posixaccount
                 krbprincipalaux
                 krbticketpolicyaux
                 inetuser
                 ipaobject
                 ipasshuser
                 ipaSshGroupOfPubKeys
    sn: Administrator

When using context managers the Connection object retains its previous state after exiting the context. The connection is always open and bound while in context.
If the connection was not bound to the server when entering the context the Unbind operation will be tried when you leave the context even if the operations
in the context raise an exception.

The Add operation
=================

Let's try to add some data to the LDAP server::

... work in progress ...
