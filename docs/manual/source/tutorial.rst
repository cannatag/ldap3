##############
ldap3 Tutorial
##############

.. note::
    In this tutorial you will access a public demo of `FreeIPA`_, available at https://ipa.demo1.freeipa.org (you must trust
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

If you're reading this tutorial I assume that you already know what LDAP is, or at least have a rough idea of it. Even if you really
don't know anything about LDAP, after reading this tutorial you should be able to access an LDAP compliant server and use it without bothering with
the many glitches of the LDAP protocol.

I'd rather want to be sure that you are aware of what LDAP **is not**:

- LDAP is not a server
- LDAP is not a database
- LDAP is not a network service
- LDAP is not an authentication procedure
- LDAP is not a user/password repository
- LDAP is not an open source neither a closed source product

It's important to know what LDAP is not because people usually call "LDAP" a peculiar part of what they use of the
**Lightweight Directory Access Protocol**. LDAP is a *protocol* and as other 'trailing-P' words in the Internet
ecosystem (HTTP, FTP, TCP, IP, ...) it is a set of rules you must follow to talk to an external
server/database/service/procedure/repository/product (all the things in the above list). Data managed via LDAP are
key/value(s) pairs grouped in a hierarchical structure. This structure is called the **DIT** (*Directory
Information Tree*). LDAP doesn't specify how data is actually stored in the DIT neither how the user is authorized to
access it. There are only a few data types that every LDAP server must recognize (some of them are very old and are not used anymore).
LDAP version 3 is also an extensible protocol, this means that a vendor can add features not in the LDAP specifications (using Controls and Extensions).
The LDAP server relies on a **schema** to know which data types, attributes and object it understand. A portion of the schema is standard
(defined in the protocol itself), but each vendor can add attributes and object for specific purpose. Also the schema can be extended by the user.
Keep in mind that "extending the schema" is something that is not defined in the LDAP protocol, so each vendor has developed different methods.

All the (sometime too complex) LDAP machinery you will interact with has this only purpose.

Being a protocol, LDAP is not related to any specific product and it is described in a set of **RFC** (*Request for
comments*, the official rules of the Internet ecosystem). Its latest version of this rules is **version 3** documented
in the RFC4510 and subsequents RFCs released in June 2006.

A very brief history of LDAP
============================

You may wonder why the "lightweight" in LDAP. Its ancestor, called **DAP** (*Directory Access Protocol*), was developed in the 1980s
by the CCITT (now ITU-T), the *International Committee for Telephone and Telegraphy* (the venerable entity that gave us, among
others, faxes and modem protocols we used in the pre-Internet era). DAP was a very heavy and hard-to-implement protocol
(either for the client and the server components) and was not accessible via TCP/IP. In 1993 a simpler access protocol
was invented at the University of Michigan to act as a gateway to the DAP world. Afterwards vendors developed server products that
could understand LDAP directly and the gateway to DAP was soon forgotten. LDAP v3 was first documented in 1997 and its
specifications was revised in 2006. These later specifications are strictly followed by the ldap3 library.

The ldap3 package
=================

ldap3 is a fully compliant LDAP v3 client library and follows the latest standard RFCs released in June 2006. It's written from scratch to be
compatible with Python 2 and Python 3 and can be used on any machine where the Python interpreter can gain access to the network via the Python
standard library.

Chances are that you find the ldap3 package already installed (or installable with your local package manager) on your machine, just try
to **import ldap3** from your Python console. If you get an ImportError you need to install the package from PyPI via pip in the standard way::

    pip install ldap3


.. warning::
   If pip complains about certificates you should specify the path to the PyPI CA certificate with the --cert parameter::

   pip install ldap3 --cert /path/to/the/DigiCert_High_Assurance_EV_Root_CA.pem


You can also download the source code from https://github.com/cannatag/ldap3 and install it with::

    python setup.py install

ldap3 needs the **pyasn1** package (and will install it if not already present). This package is used to communicate with the server over the network.

ldap3 usage is straightforward: you just define a Server object and a Connection object. Then you issue commands to the connection.
A server can have more than one connection and there are different *communication strategies* to choose from. All the importable objects
are available in the ldap3 namespace. At least you need to import the Server and the Connection object, and any additional constant you
will use in your LDAP conversation (constants are defined in upper case)::

    >>> from ldap3 import Server, Connection, ALL

ldap3 specific exceptions are defined in the ``ldap3.core.exceptions○`` package.

Accessing an LDAP server
========================

In the LDAP protocol the login operation is called **Bind**. A bind can be performed in 3 different ways: Anonymous Bind,
Simple Password Bind, and SASL (*Simple Authentication and Security Layer*, allowing a larger set of authentication methods)
Bind. You can think of the Anonymous Bind as of a *public* access to the LDAP server where no credentials are provided
and the server applies some *default* access rules. With the Simple Password Bind and the SASL Bind you provide credentials
that the LDAP server uses to determine your authorizazion level. Again, keep in mind that the LDAP standard doesn't define
specific access rules and that the authorization mechanism is not specified at all. So each LDAP server vendor can have a
different method for authorizing the user to access data stored in the DIT.

ldap3 let you choose the method that the client will use to connect to the server with the ``client_strategy`` parameter of the
Connection object. There are 5 strategies that can be used for establishing a connection: SYNC, ASYNC, LDIF, RESTARTABLE and REUSABLE.
The MOCK_SYNC strategy can be used to emulate a fake LDAP server and it's useful while testing your application without the need of a real server.

As a general rule in synchronous strategies (**SYNC**, **RESTARTABLE**) all LDAP operations return a boolean: ``True`` if they're successful, ``False``
if they fail. In asynchronous strategies (**ASYNC**, **REUSABLE**) all LDAP operations (except Bind that always returns a boolean) return a
number, the *message_id* of the request. With asynchronous strategies you can send multiple requests without waiting for responses, you get each
response with the ``get_response(message_id)`` method of the Connection object as you need it. ldap3 will raise an exception if
the response has not yet arrived after a specified time. In the ``get_response()`` method this timeout value can be set
with the ``timeout`` parameter to the number of seconds to wait for the response to appear (default is 10 seconds).
Asynchronous strategies are useful with slow servers or when you have many requests with the same connection object in multiple threads.
Usually you will use synchronous strategies only.

The **LDIF** strategy is used to create a stream of LDIF-CHANGEs.

.. note::
    In this tutorial you will use the default SYNC communication strategy.

Let's start accessing the server with an anonymous bind::

    >>> server = Server('ipa.demo1.freeipa.org')
    >>> conn = Connection(server)
    >>> conn.bind()
    True

or shorter::

    >>> conn = Connection('ipa.demo1.freeipa.org', auto_bind=True)
    True

Hardly it could be simpler than that. The ``auto_bind=True`` parameter forces the bind operation while creating the Connection object.
You have now a full working anonymous session open and bound to the server with a *synchronous* communication strategy::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - cleartext - user: None - bound - open - <local: 192.168.1.101:49813 - remote: 209.132.178.99:389> -
    tls not started - listening - SyncStrategy - internal decoder

With ``print(conn)`` you ask to the connection its status and get back a lot of information:

======================================================= =================================================================================
ldap://ipa.demo1.freeipa.org:389                        the server URL (scheme, name and port we are connected to)
cleartext                                               the kind of connection the server is listening to
user: None                                              the credentials used, in this case None means an anonymous binding
bound                                                   the status of the LDAP session
open                                                    the status of the underlying TCP/IP session
<local: 192.168.1.101:51038 - remote: 23.20.46.132:389> the local and remote communication endpoints
tls not started                                         the status of the TLS (Transport Layer Security) session
listening                                               the status of the communication strategy
SyncStrategy                                            the communication strategy used
internal decoder                                        which BER decoder the connection is using (pyasn1 or the faster internal decoder)
======================================================= =================================================================================


.. sidebar::
    Object representation: the ldap3 library uses the following object representation rule: when you use ``str()`` you get back information
    about the status of the object in a human readable format, when you use ``repr()`` you get back a string you can use in the
    Python console to recreate the object. ``print`` always return the str representation. Typing a variable at the ``>>>`` prompt always
    return the repr representation.

If you ask for the ``repr()`` representation of the conn object you can get a string to recreate the object::

    >>> conn
    Connection(server=Server(host='ipa.demo1.freeipa.org', port=389, use_ssl=False, get_info='NO_INFO'), auto_bind='NONE',
    version=3, authentication='ANONYMOUS', client_strategy='SYNC', auto_referrals=True, check_names=True, read_only=False,
    lazy=False, raise_exceptions=False, fast_decoder=True)

If you just copy and paste the object representation at the ``>>>`` prompt you can instantiate a new object similar to the original one.
This is helpful when experimenting in the interactive console and works for most of the ldap3 library objects::

   >>> server
   Server(host='ipa.demo1.freeipa.org', port=389, use_ssl=False, get_info='NO_INFO')


Getting information from the server
===================================

The LDAP protocol specifies that an LDAP server must return some information about itself. You can request them with the ``get_info=ALL``
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
Supported LDAP Versions   2, 3                    Server supports LDAP 2 and 3
Naming contexts           <...>                   Server stores information for 3 different DIT portions
Alternative servers       None                    This is the only replica of the database
Supported Controls        <...>                   Optional controls that can be sent in a request operation
Supported Extentions      <...>                   Additional extended operations understood by the server
Supported SASL Mechanisms <...>                   Different additional SASL authentication mechanisms available
Schema Entry              cn=schema               The location of the schema in the DIT
Vendor name               389 Project             The brand/mark/name of this LDAP server
Vendor version            389-Directory/1.3.3 ... The version of this LDAP server
Other                     ...                     Additional information provided by the server
========================= ======================= =============================================================

From this response we know that this server is a stand-alone LDAP server that can hold entries in the dc=demo1,dc=freeipa,dc=org context,
that supports various SASL access mechanisms and that is based on the 389 Directory Service server. Furthermore in the
Supported Controls we can see it supports "paged searches", and the "who am i" and "StartTLS" extended operations in
Supported Extensions.

.. sidebar:: Controls vs Extensions: in LDAP a *Control* is some additional information that can be attached to any LDAP request or response, while an
    *Extension* is a custom request that can be sent to the LDAP server in an **Extended Operation** Request.
    A Control usually modifies the behaviour of a standard LDAP operation, while an Extension is a completely new
    kind of operation that each vendor decides to include in its LDAP server implementation.
    An LDAP server declares which controls and which extendend operations it understand. The ldap3 library decodes the
    known supported controls and extended operation and includes a brief description and a reference to the relevant
    RFC in the ``.info`` attribute when known. Not all controls or extensions are intended to be used by clients. Sometimes controls and
    extensions are used by servers that hold a replica or a data partition. Unfortunately in the LDAP specifications
    there is no way to specify if such extensions are reserved for a server (**DSA**, *Directory Server Agent* in LDAP
    parlance) to server communication (for example in replicas or partitions management) or can be used
    by clients (**DUA**, *Directory User Agent*). Because the LDAP protocols doesn't provide a specific way for DSAs to communicate
    with each other, a DSA actually presents itself as a DUA to another DSA.

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

      <...long list of descriptors...>


The schema is a very long list that describes what kind of data types the LDAP server understands. It also specifies
what attributes can be stored in each class. Some classes are containers for other entries (either container or leaf)
and are used to build the hierarchy of the DIT. Container entries can have attributes too.
One important specification in the schema is if the attribute is *multi-valued* or not. A multi-valued attribute can store one or more values.
Every LDAP server must at least support the standard LDAP3 schema but can have additional custom classes and attributes.
The schema defines also the *syntaxes* and the *matching rules* of the different kind of data types stored in the LDAP.

.. note::
    Object classes and attributes are independent objects. An attribute is not a "child" of a class neither a
    class is a "parent" of any attribute. Classes and attributes are linked in the schema with the ``MAY`` and ``MUST`` options
    of the object class definition that specify what attributes an entry can contain and which of them are mandatory.

.. sidebar::
    There are 3 different types of object classes: **ABSTRACT** (used only when defining the class hiearchy), **STRUCTURAL** (used to
    create concrete entries) and **AUXILIARY** (used to add additional attributes to an entry). Only one structural class can be used
    in an entry, while many auxiliary classes can be added to the same entry. Adding an object class to an entry simply means
    that the attributes defined in that object class can be stored in that entry.

If the ldap3 library is aware of the schema used by the LDAP server it will try to automatically convert data retrieved by the Search
operation to their representation. So an integer will be returned as an int, a generalizedDate as a datetime object and so on.
If you don't read the schema all the values are returned as bytes and unicode strings. You can control this behaviour with
the ``get_info`` parameter of the Server object and the ``check_names`` parameter of the Connection object.

Logging into the server
=======================

You haven't provided any credentials to the server yet, but you received a response anyway. This means that LDAP allow users to perform
operations anonymously without declaring their identity. Obviously what the server returns to an anonymous connection is someway limited.
This makes sense because originally the DAP protocol was intended for reading phone directories, as in a printed book, so its
content could be read by anyone.

If you want to establish an authenticated session you have two options: Simple Password and SASL. With Simple Password you provide
a **DN** (*Distinguished Name*) and a password. The server checks if your credentials are valid and permits or denies access to the elements of the DIT.
SASL provides additional methods to identify the user, as an external certificate or a Kerberos ticket.

.. sidebar:: Distinguished Names: the DIT is a hierarchical structure, as a filesystem. To identify an entry you must specify its *path*
    in the DIT starting from the top of the Tree down to the last leaf that actually represents the entry. This path is called the
    **Distinguished Name** (DN) of an entry and is constructed with key-value pairs, separated by a comma, of all the entries that form
    the path from the leaf up to the top of the Tree. The DN of an entry is unique throughout the DIT and changes only if you move the
    entry to another container within the DIT. The parts of the DN are called **Relative Distinguished Name** (RDN) because are unique only
    in the context where they are defined. So, for example, if you have a *inetOrgperson* entry with RDN ``cn=Fred`` that is stored in an *organizational
    unit* with RDN ``ou=users`` that is stored in an *organization* with RDN ``o=company`` the DN of the *inetOrgperson* entry will
    be ``cn=Fred, ou=users, o=company``. The RDN value must be unique in the context where the entry is stored, but there is no specification
    in the LDAP schema on which attribute to use as RDN for a specific class.

.. note:: Accessing Active Directory: with ldap3 you can also connect to an Active Directory server with the NTLM v2 protocol::

        >>> from ldap3 import Server, Connection, ALL, NTLM
        >>> server = Server('servername', get_info=ALL)
        >>> conn = Connection(server, user="Domain\\User", password="password", authentication=NTLM)

    This kind of authentication is not part of the LDAP 3 RFCs but uses a proprietary Microsoft authentication mechanism named SICILY. ldap3 implements
    it because it's much easier to use this method than Kerberos to access Active Directory.

Now try to ask to the server who you are::

    >>> conn.extend.standard.who_am_i()

We get an empty response. This means you have no authentication status on the server, so you are an **anonymous** user. This doesn't mean
that you are unknown to the server, actually you have a session open with the server and you can send additional operation requests. Even
if you don't send the anonymous bind operation the server will accept any operation requests as an anonymous user.

.. note:: The ``extend`` namespace. The connection object has a special namespace called "extend" where more complex operations are defined
    This namespace include a ``standard`` section and a number of specific vendor sections. In these sections you can find methods to perform
    tricky or hard-to-implement operation. For example in the ``microsoft`` section you can find a method to easily change the user password, and
    in the ``novell`` section a method to apply transaction to groups of LDAP operations. In the ``standard`` section you can also find a very
    easy way to perform a paged search via generators.


.. note:: Opening vs Binding: the LDAP protocol provides a Bind and an Unbind operation but, for historical reasons, they are not symmetric.
    As any TCP connection the socket must be *open* before binding to the server . This is implicitly done by the ldap3 package when you
    issue a ``bind()`` or another operation or can be esplicity done with the ``open()`` method of the Connection object. The Unbind operation
    is actually used to *terminate* the connection, both ending the session and closing the socket. After the ``unbind()`` operation the connection
    cannot be used anymore. If you want to access as another user or change the current session to an anonymous one, you must issue ``bind()`` again.
    The ldap3 library allows you to use the ``rebind()`` method to access the same connection as a different user. You must use ``unbind()`` only when
    you want to close the network socket.

Try to specify a valid user::

    >>> conn = Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
    >>> conn.extend.standard.who_am_i()
    'dn: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org'

Now the server knows that you are a recognized user and the ``who_am_i()`` extended operation returns your identity.

Establishing a secure connection
================================

If you check the connection info you can see that the Connection is using a cleartext (insecure) channel::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - **cleartext** - user: uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:50164 - remote: 209.132.178.99:**389**> - **tls not started** - listening - SyncStrategy - internal decoder'

Credentials pass unencrypted over the wire, so they can be easily captured by a network eavesdropper. The LDAP protocol provides two ways
to secure a connection: **LDAP over TLS** (or over SSL) and the **StartTLS** extended operation. Both methods establish a secure TLS
connection: the former secure with TLS the communication channel as soon as the connection is open, while the latter can be used at any time on
an already open unsecure connection to secure it issuing the StartTLS operation.

.. note:: LDAP URL scheme: a cleartext connection to a server can be expressed in the URL with the **ldap://** scheme, while LDAP over TLS can be
    indicated with **ldaps://** even if this is not specified in any of the LDAP RFCs. If a scheme is included in the server name while creating
    the Server object, the ldap3 library opens the proper port, unencrypted or with the specified TLS options (or default options if none is specified).

.. sidebar:: Default port numbers: the default port for cleartext (unsecure) communication is **389**, while the default for LDAP over TLS (secure)
    communication is **636**. Note that because you can start a session on the 389 port and then raise the security level with the StartTLS operation,
    you can have a secure communication even on the 389 port (usually considered unsecure). Obviously the server can listen on additional or different
    ports. When defining the Server object you can specify which port to use with the ``port`` parameter. Keep this in mind if you need to connect to
    a server behind a firewall.

Now try to use the StartTLS extended operation::

    >>> conn.start_tls()
    True

if you check the connection status you can see that the session is on a secure channel now, even if started on a cleartext connection::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:50910 - remote: 209.132.178.99:389> - tls started - listening - SyncStrategy - internal decoder


To start the connection on a SSL socket::

    >>> server = Server('ipa.demo1.freeipa.org', use_ssl=True, get_info=ALL)
    >>> conn = Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
    >>> print(conn)
    ldaps://ipa.demo1.freeipa.org:636 - ssl - user: uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org - bound - open - <local: 192.168.1.101:51438 - remote: 209.132.178.99:636> - tls not started - listening - SyncStrategy - internal decoder

Either with the former or the latter method the connection is now encrypted. We haven't specified any TLS option, so there is no checking of
certificate validity. You can customize the TLS behaviour providing a Tls object to the Server object using the security context configuration::

    >>> from ldap3 import Tls
    >>> import ssl
    >>> tls_configuration = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1)
    >>> server = Server('ipa.demo1.freeipa.org', use_ssl=True, tls=tls_configuration)
    >>> conn = Connection(server)
    >>> conn.open()
    ...
    ldap3.core.exceptions.LDAPSocketOpenError: (LDAPSocketOpenError('socket ssl wrapping error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:600)',),)

In this case, using the FreeIPA demo server we get a LDAPSocketOpenError exception because the certificate cannot be verified.
You can configure the Tls object with a number of options. Look at :ref:`the SSL and TLS documentation <ssltls>` for more information.

Database Operations
===================

.. warning:: Abstraction Layer: the LDAP operation are clumsy and hard-to-use because reflect the old-age idea that most expensive operations
    should be done on the client to not cluttering and hogging the server with unneeded elaborations. ldap3 includes a full-functional **Abstraction
    Layer** that let you interact with the DIT in a modern and pythonic way. With the Abstraction Layer you shouldn't need to issue any
    LDAP operation at all.

As any system that stores data, LDAP lets you perform the standard CRUD (Create, Read, Update, Delete) operations, but their usage is someway rudimentary.
Again, if you think of the intended use of the original DAP protocol (storing key-values pairs related to an entry in a phone directory)
this makes sense: an entry is written once, seldom modified, and eventually deleted, so the create (**Add** in LDAP), update (**Modify** or **ModifyDn**)
and delete (**Delete**) operations have a very basic usage while the Read (**Search**) operation is richer in options, but lacks many capabilities
you would expect in a modern query language (as 1 to N relationship, joining views, or server data manipulation). Nonetheless almost everything you can do
in a modern database can be equally done with LDAP. Furthermore consider that even if an LDAP server can be accessed by multiple clients simultaneously,
the LDAP protocol itself has no notion of "transaction", so if you want to issue multiple Add or Modify operations in an atomic way (to keep data
consistent), you must investigate the extended operations of the specific LDAP server you're connecting to to check if it provides transactions for
multiple operations via Controls or Extended operations.

.. note:: Synchronous vs Asynchronous: you can submit operations to the server in two different ways: **synchronous** mode and **asynchronous**
    mode. While with the former you send the request and immediately get the response, in the latter the ldap3 library constantly listens to the
    server (it uses one independent thread for each connection). When you send a request you must store its *message id* (a unique number that
    ldap3 stamps on every message of your LDAP session) in your code so you can later query the Connection object for the relevant response when
    it's ready. You'll probably stick with the synchronous mode, because nowadays LDAP servers are fast to respond, but the asynchronous mode is
    still useful if your program is event-driven (maybe using an asynchronous event loop).

    ldap3 supports both of this models with its different *communication strategies*.

LDAP also provides the **Compare** operation that returns True only if an attribute has the value you specify in the request. Even if this operation seems
redundant (you could read the attribute and perform the comparison using more powerful tools in your code) you need it to check for the presence
of a value (even in a multi-valued attribute) without having the permission to read it. This obviuosly relies upon some "access restriction" mechanism
that must be present on the server. LDAP doesn't specify how this mechanism works, so each LDAP server has its specific way of handling authorization.
The Compare operation is also used to check the validity of a password (that you can't read) without performing a Bind operation with the specific user.

After any synchronous operation, you'll find the following attributes populated in the Connection object:

* ``result``: the result of the last operation (as returned by the server)
* ``response``: the entries found (if the last operation is a Search)
* ``entries``: the entries found exposed via the ldap3 Abstraction Layer (if the last operation is a Search)
* ``last_error``: the error, if any,  occurred in the last operation
* ``bound``: True if the connection is bound to the server
* ``listening``: True if the socket is listening to the server
* ``closed``: True if the socket is not open

Performing searches
===================

The **Search** operation in ldap3 has a number of parameters, but only two of them are mandatory:

* ``search_base``: the location in the DIT where the search will start
* ``search_filter``: a string that describes what are you searching

Search filters are based on assertions and look odd when you're unfamiliar with their syntax. One *assertion* is a bracketed expression
that affirms something about an attribute and its value, as ``(givenName=John)`` or ``(maxRetries>=10)``. Each assertion resolves
to True, False or Undefined (that is treated as False) for one or more entries in the DIT. Assertions can be grouped in boolean groups
where all assertions (**and** group, specified with ``&``) or just one assertion (**or** group, specified with ``|``) must be True. A single
assertion can be negated (**not** group, specified with ``!``). Each group must be bracketed, allowing for recursive filters.
Operators allowed in an assertion are ``=`` (**equal**), ``<=`` (**less than or equal**), ``>=`` (**greater than or equal**), ``=*`` (**present**), ``~=``
(**aproximate**) and ``:=`` (**extensible**). Surprisingly the *less than* and the *greater than* operators don't exist in the filter syntax.
The *aproximate* and the *extensible* are someway obscure and seldom used. In an equality filter you can use the ``*`` character as a wildcard.

For example, to search for all users named John with an email ending with '@example.org' the filter will be ``(&(givenName=John)(mail=*@example.org))``,
to search for all users named John or Fred with an email ending in '@example.org' the filter will be
``(&(|(givenName=Fred)(givenName=John))(mail=*@example.org))``, while to search for all users that have a givenName different from Smith the filter
will be ``(!(givenName=Smith))`` Long search filters can easily become hard to understand so it may be useful to divide the text on multiple lines while
writing/reading them::

    (&
        (|
            (givenName=Fred)
            (givenName=John)
        )
        (mail=*@example.org)
    )


Try now to search all users in the FreeIPA demo LDAP server::

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

Here you request all the entries of class *person*, starting from the *dc=demo1, dc=freeipa, dc=org* context with the default subtree scope.
You have not requested any attribute, so in the response we get only the Distinguished Name of the entries found.

Now let's try to request some attributes for the admin user::

    >>> conn.search('dc=demo1, dc=freeipa, dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn', 'krbLastPwdChange', 'objectclass'])
    True
    >>> conn.entries[0]
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-09T20:39:32.711000
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
    objectclass: top
                 person
                 posixaccount
                 krbprincipalaux
                 krbticketpolicyaux
                 inetuser
                 ipaobject
                 ipasshuser
                 ipaSshGroupOfPubKeys
                 ipaNTUserAttrs
    sn: Administrator

.. note::
    When using attributes in a search filter it's a good habit to always request for the structuraL class of the entries you expect to retrieve.
    You cannot be sure that the attribute you're serching for is not used is some other object classes, and even if you were sure that no other
    object class uses the attribute this could always change in the future when someone creates in the schema a new object class that uses that
    same attribute. Then your program suddenly breaks with no apparent reason.


The ``entries`` attribute of the Connection object is derived from the Abstraction Layer and it's specially crafted to be used in interactive mode
at the ``>>>`` prompt. It gives a visual representation of the entry data structure where each value is, according to the schema, properly formatted
(the date value in krbLastPwdChange is actually stored as ``b'20161009010118Z'``). Attributes can be queried as if the entry were a class object or
a dict, with some additional features as case-insensitivity and blank-insensitivity. You can get the formatted value and the raw value (the value
actually returned by the server) in the ``values`` and ``raw_values`` attribute::

    >>> entry = entries[0]
    >>> entry.krbLastPwdChange
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
    >>> entry.KRBLastPwdCHANGE
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
    >>> entry['krbLastPwdChange']
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
    >>> entry['KRB LAST PWD CHANGE']
    krbLastPwdChange 2016-10-09 10:01:18+00:00

    >>> entry.krbLastPwdChange.values
    [datetime.datetime(2016, 10, 9, 10, 1, 18, tzinfo=OffsetTzInfo(offset=0, name='UTC'))]
    >>> entry.krbLastPwdChange.raw_values
    [b'20161009010118Z']


Note that the entry status is "Read". This is not relevant in this example but the entry can be converted to a "writable" entry and used in the Abstraction
Layer to change or delete its content.

In the previous search operations you specified ``dc=demo1, dc=freeipa, dc=org`` as the base of our search, but the entries we got back were in the ``cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org``
context of the DIT. So the server has, for some unapparent reason, walked down in every context under the base and applied the filter to each of the entries in the sub-contexts.
It actually performed a *whole subtree* search. Other possible kinds of search are the *single level* (that searches only in the level specified in the base) and the *base object*
(that search only in the attributes of the entry specified in the base). What changes in this different kinds of search is the 'breath' of the portion of
the DIT that is searched. This breath is called the **scope** of the search and can be specified with the ``search_scope`` attribute of the search
operation. It can assume three different values ``BASE``, ``LEVEL`` and ``SUBTREE``. The latter value is the default for the search opertion, so this
clarifies why you got back all the entries in the sub-contexts of the base in previous searches.

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
    krbLastPwdChange: 20161009010118Z
    sn: Administrator
    # total number of entries: 1

.. sidebar:: LDIF
    LDIF stands for LDAP Data Interchange Format and is a textual standard used to describe two different aspects of LDAP: the content of an entry (**LDIF-CONTENT**)
    or the changes performed on an entry with an LDAP operation (**LDIF-CHANGE**). LDIF-CONTENT is used to describe LDAP entries in an ASCII stream (i.e. a file),
    while LDIF-CHANGE is used to describe the Add, Delete, Modify and ModifyDn operations.

    *These two formats have different purposes and cannot be mixed in the same stream.*

or you can save the response to a JSON string::

    >>> print(entry.entry_to_json())
    {
        "attributes": {
            "krbLastPwdChange": [
                "2016-10-09 10:01:18+00:00"
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

The Connection object responds to the context manager protocol, so you can have automatic open, bind and unbind with the following syntax::

    >>> with Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123') as conn:
            conn.search('dc=demo1, dc=freeipa, dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn','krbLastPwdChange', 'objectclass'])
            entry = conn.entries[0]
    True
    >>> conn.bound
    False
    >>> entry
    DN: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org
    krbLastPwdChange: 2016-10-09 10:01:18+00:00
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

When using context managers the Connection object retains its previous state after exiting the context. The connection is open and bound while in context.
If the connection was not bound to the server when entering the context the Unbind operation will be tried when you leave the context even if the operations
in the context raise an exception.

The Add operation
=================

Let's try to add some data to the LDAP server::

    >>> # Create a container for our new entries
    >>> conn.add('ou=ldap3-tutorial, dc=demo1, dc=freeipa, dc=org', 'organizationalUnit')
    >>> True
    >>> # Add some users
    >>> conn.add('cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Beatrix', 'sn': 'Young', 'departmentNumber': 'DEV', 'telephoneNumber': 1111})
    >>> True
    >>> conn.add('cn=j.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'John', 'sn': 'Smith', 'departmentNumber': 'DEV',  'telephoneNumber': 2222})
    >>> True
    >>> conn.add('cn=m.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Marianne', 'sn': 'Smith', 'departmentNumber': 'QA',  'telephoneNumber': 3333})
    >>> True
    >>> conn.add('cn=quentin.cat,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Quentin', 'sn': 'Cat', 'departmentNumber': 'CC',  'telephoneNumber': 4444})

As you can see we have added some users. You passed the full DN as the first parameter, the objectClass (or objectClasses) as second parameter and a dictonary of attributes as the third parameter.
Some attributes are mandatory when adding a new object. You can check which are the mandatories one in the schema.

If we look at the schema for the *inetOrgPerson* object class::

    >>> server.schema.object_classes['inetorgperson']
    Object class: 2.16.840.1.113730.3.2.2
      Short name: inetOrgPerson
      Superior: organizationalPerson
      May contain attributes: audio, businessCategory, carLicense, departmentNumber, displayName, employeeNumber, employeeType, givenName, homePhone, homePostalAddress, initials, jpegPhoto, labeledURI, mail, manager, mobile, o, pager, photo, roomNumber, secretary, uid, userCertificate, x500UniqueIdentifier, preferredLanguage, userSMIMECertificate, userPKCS12
      Extensions:
        X-ORIGIN: RFC 2798

We can see that it has no mandatory attributes and that is a subclass of the *organizationalPerson* object::

    Object class: 2.5.6.7
      Short name: organizationalPerson
      Superior: person
      May contain attributes: title, x121Address, registeredAddress, destinationIndicator, preferredDeliveryMethod, telexNumber, teletexTerminalIdentifier, internationalISDNNumber, facsimileTelephoneNumber, street, postOfficeBox, postalCode, postalAddress, physicalDeliveryOfficeName, ou, st, l
      Extensions:
        X-ORIGIN: RFC 4519
      OidInfo: ('2.5.6.7', 'OBJECT_CLASS', 'organizationalPerson', 'RFC4519')

The *organizationalPerson* object class has no mandatory attribute and is a subclass of the *person* object::

    Object class: 2.5.6.6
      Short name: person
      Superior: top
      Must contain attributes: sn, cn
      May contain attributes: userPassword, telephoneNumber, seeAlso, description
      Extensions:
        X-ORIGIN: RFC 4519
      OidInfo: ('2.5.6.6', 'OBJECT_CLASS', 'person', 'RFC4519')

We have found two mandatory attributes: *sn* and *cn*. Also the *person* object class is a subclass of the *top* object. Let's walk up the hineritance chain::

    Object class: 2.5.6.0
      Short name: top
      Must contain attributes: objectClass
      Extensions:
        X-ORIGIN: RFC 4512
      OidInfo: ('2.5.6.0', 'OBJECT_CLASS', 'top', 'RFC4512')

*top* is the root of all LDAP classes and defines a single mandatory attributes, objectClass. So every object class defined in the LDAP schema must have its own objectclass.
Let's read the objectClass of the first user we created::

    >>> conn.search('ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=*)', attributes=['objectclass'])
    >>> print(conn.entries[0])
    DN: cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org - STATUS: Read - READ TIME: 2016-10-09T17:36:44.100248
    objectclass: inetOrgPerson
                 organizationalPerson
                 person
                 top

You can see that the objectclass is composed of all the hierarchical tree from top to inetOrgPerson. This means that you can add any of the optional
attribute defined in each class of the hierarchy.

The Modify operation
====================

To change attributes of an object you must use the Modify operation. There are three kinds of modifications in LDAP: add, delete and replace.
**Add** is used to add values listed to the modification attribute, creating the attribute if necessary. **Delet** deletes values listed from the modification
attribute. If no values are listed, or if all current values of the attribute are listed, the entire attribute is removed. **Replace** replaces all existing
values of the modification attribute with the new values listed, creating the attribute if it did not already exist.  A replace with no value will delete the entire
attribute if it exists, and it is ignored if the attribute does not exist.

... work in progress ...
