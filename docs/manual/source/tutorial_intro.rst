Tutorial: Introduction to ldap3
###############################

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


Even if you really don't know anything about LDAP, after reading this tutorial you should be able to access an LDAP compliant server and use it without bothering with
the many glitches of the LDAP protocol.

What LDAP is not
================
I'd rather want to be sure that you are aware of what LDAP **is not**:

- LDAP is not a **server**
- LDAP is not a **database**
- LDAP is not a **network service**
- LDAP is not a **network device**
- LDAP is not an **authentication procedure**
- LDAP is not a **user/password repository**
- LDAP is not a specific **open or closed source product**

It's important to know what LDAP is not, because people usually call "LDAP" a peculiar part of what they use of the
**Lightweight Directory Access Protocol**. LDAP is a *protocol* and as other 'ending in P' words in the Internet
ecosystem (HTTP, FTP, TCP, IP, ...) it's a set of rules you must follow to talk to an external
server/database/service/device/procedure/repository/product (all things in the previous list).

Data managed via LDAP are key/value(s) pairs grouped in a hierarchical structure. This structure is called the **DIT** (*Directory
Information Tree*). LDAP doesn't specify how data is actually stored in the DIT neither how the user is authorized to
access it. There are only a few data types that every LDAP server must recognize (some of them being very old and not used anymore).
LDAP version 3 is also an extensible protocol, this means that a vendor can add features not in the LDAP specifications (using Controls and Extensions).
Any LDAP server relies on a **schema** to know which data types, attributes and object it understands. A portion of the schema is standard
(defined in the protocol itself), but each vendor can add attributes and object for specific purposes. The schema can also be extended by the
system administrator, the developer and the end user of the LDAP server.

Curiously "extending the schema" is something that is not defined in the LDAP protocol, so each vendor has developed
different methods for adding objects, attributes and additional rules to the schema.

Being a protocol, LDAP is not related to any specific product and it is described in a set of **RFCs** (*Request for
comments*, the official rules of the Internet ecosystem). Latest version of this rules is **version 3** documented
in the RFC4510 (and subsequents RFCs) released in June 2006.

A brief history of LDAP
=======================
You may wonder why the "lightweight" in LDAP. Its ancestor, called **DAP** (*Directory Access Protocol*), was developed
in the 1980s by the CCITT (now ITU-T), the *International Committee for Telephone and Telegraphy* (the venerable entity
that gave us, among others, the fax and the protocols we used on modems in the pre-Internet era). Even if its intended use
was to standardize access to directory services (i.e. phone directories) DAP was a very heavy and hard-to-implement protocol
(for client and server components) and was not accessible via TCP/IP. In 1993 a simpler access protocol was
invented at the University of Michigan to act as a gateway to the DAP world. Afterwards vendors developed
products that could understand LDAP directly and the gateway to DAP was soon removed. LDAP v3 was first documented
in 1997 and its specifications was revised in 2006. These later specifications are strictly followed by the ldap3 library.

Unicode everywhere
==================
The LDAP protocol specifies that attribute names and their string values (usually in the Directory String LDAP syntax) must
be stored in Unicode version 3.2 with the UTF-8 byte encoding. There are some limitations in defining the attribute names
that must use only ASCII letters (upper and lowercase), numbers and the hypen character (but not as a leading character).

**Unicode** is a standard to describe tens of thousands of printed (even if not visible) characters but what goes over the wire
when you interact with an LDAP server is only old plain bytes (with values ranging from 0 to 255 as usual), so the UTF-8
encoding is needed when talking to an LDAP server to convert the Unicode character to a valid byte (or multi-byte)
representation. For this reason when sending a string value in any LDAP operation it must be converted to
UTF-8 encoding. Your environment could have (and probably has) a different default encoding so the ldap3 library
will try to convert from your default encoding to UTF-8 for you, but you may set a different input encoding
with the ``set_config_parameter('DEFAULT_ENCODING', 'my_encoding')`` function of the ldap3 library. String values
returned by the LDAP search operation are always encoded in UTF-8. This doesn't apply to other binary formats, as
Octect String that can use a different encoding.

The ldap3 package
=================
ldap3 is a fully compliant LDAP v3 client library following the official RFCs released in June 2006. It's written from
scratch to be compatible with Python 2 and Python 3 and can be used on any machine where Python can gain access to the
network via its Standard Library.

Chances are that you find the ldap3 package already installed (or installable with your local package manager) on your machine, just try
to **import ldap3** from your Python console. If you get an ``ImportError`` you need to install the package from PyPI via
pip in the usual way::

    pip install ldap3

.. warning::
   If pip complains about certificates you should specify the path to the PyPI CA certificate with the --cert parameter::

      pip install ldap3 --cert /path/to/the/DigiCert_High_Assurance_EV_Root_CA.pem

You can also download the source code from https://github.com/cannatag/ldap3 and install it with::

    python setup.py install

ldap3 needs the **pyasn1** package (and will install it if not already present). This package is used to communicate with
the server over the network. By default ldap3 uses the pyasn1 package only when sending data to the server. Data received
from the server are decoded with an internal ASN1 decoder, much faster than the pyasn1 decoder.

Accessing an LDAP server
========================
ldap3 usage is straightforward: you define a Server object and a Connection object. Then you issue commands to the connection.
A server can have any number of active connections with the same or a different *communication strategy*.

All the importable objects are available in the ldap3 namespace. At least you need to import the Server and the Connection object,
and any additional constant you will use in your LDAP conversation (constants are defined in upper case)::

    >>> from ldap3 import Server, Connection, ALL

ldap3 specific exceptions are defined in the ``ldap3.core.exceptions`` package.

.. note:: **A more pythonic LDAP**: LDAP operations look clumsy and hard-to-use because they reflect the old-age idea
    that time-consuming operations should be done on the client to not clutter or hog the server with unneeded elaboration.
    ldap3 includes a fully functional **Abstraction Layer** that lets you interact with the DIT in a modern and *pythonic*
    way. With the Abstraction Layer you don't need to directly issue any LDAP operation at all.

In the LDAP protocol the authentication operation is called **Bind**. A bind can be performed in 3 different ways: Anonymous Bind,
Simple Password Bind, and SASL (*Simple Authentication and Security Layer*, allowing a larger set of authentication mechanisms)
Bind. You can think of the Anonymous Bind as of a *public* access to the LDAP server where no credentials are provided
and the server applies some *default* access rules. With the Simple Password Bind and the SASL Bind you provide credentials
that the LDAP server uses to determine your authorization level. Again, keep in mind that the LDAP standard doesn't define
specific access rules, so each LDAP server vendor has developed a different method for authorizing the user to access
data stored in the DIT.

ldap3 lets you choose the method that the client will use to connect to the server with the ``client_strategy`` parameter
of the Connection object. There are four strategies that can be used for establishing a connection: SYNC, ASYNC, RESTARTABLE
and REUSABLE. As a general rule, in synchronous strategies (**SYNC**, **RESTARTABLE**) all LDAP operations return a
boolean: ``True`` if they're successful, ``False`` if they fail; in asynchronous strategies (**ASYNC**, **REUSABLE**) all
LDAP operations (except Bind that always returns a boolean) return a number, the *message_id* of the request. With
asynchronous strategies you can send multiple requests without waiting for responses and then you get each response with
the ``get_response(message_id)`` method of the Connection object as you need it. ldap3 will raise an exception if
the response has not yet arrived after a specified time. In the ``get_response()`` method the timeout value can be set
with the ``timeout`` parameter to the number of seconds to wait for the response to appear (default is 10 seconds).
If you use the ``get_request=True`` in the ``get_response()`` parameter you also get the request dictionary back.

Asynchronous strategies are thread-safe and are useful with slow servers or when you have many requests with the same
Connection object in multiple threads. Usually you will use synchronous strategies only.

The **LDIF** strategy is used to create a stream of LDIF-CHANGEs. (LDIF stands for *LDAP Data Interchange Format*, a textual
standard used to describe the changes performed by LDAP operations). The MOCK_SYNC and MOCK_ASYNC strategies can be
used to emulate a fake LDAP server to test your application without the need of a real LDAP server.

.. note::
    In this tutorial you will use the default SYNC communication strategy. If you keep loosing connection to the server
    you can use the RESTARTABLE communication strategy that tries to reconnect and resend the operation when the link
    to the server fails.

Let's start accessing the server with an anonymous bind::

    >>> server = Server('ipa.demo1.freeipa.org')
    >>> conn = Connection(server)
    >>> conn.bind()
    True

or shorter::

    >>> conn = Connection('ipa.demo1.freeipa.org', auto_bind=True)

it could hardly be simpler than this. The ``auto_bind=True`` parameter forces the Bind operation to execute after creating the
Connection object. You have now a full working anonymous session open and bound to the server with a *synchronous*
communication strategy::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - cleartext - user: None - bound - open - <local: 192.168.1.101:49813 - remote: 209.132.178.99:389> -
    tls not started - listening - SyncStrategy - internal decoder

With ``print(conn)`` you ask the connection for its status and get back a lot of information:

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

.. note::
    Object representation: the ldap3 library uses the following object representation rule: when you use ``str()`` you get
    back information about the status of the object in a human readable format, when you use ``repr()`` you get back a
    string you can use in the Python console to recreate the object. ``print()`` always return the ``str()`` representation.
    Typing at the ``>>>`` prompt always return the ``repr`` representation that can be used to recreate the object in your code.

If you ask for the ``repr()`` representation of the conn object you can get a snippet of Python code::

    >>> conn
    Connection(server=Server(host='ipa.demo1.freeipa.org', port=389, use_ssl=False, get_info='NO_INFO'), auto_bind='NONE',
    version=3, authentication='ANONYMOUS', client_strategy='SYNC', auto_referrals=True, check_names=True, read_only=False,
    lazy=False, raise_exceptions=False, fast_decoder=True)

If you just copy and paste the object representation at the ``>>>`` prompt you can instantiate a new object similar to
the original one. This is helpful when experimenting in the interactive console and works for most of the ldap3 library
objects::

   >>> server
   Server(host='ipa.demo1.freeipa.org', port=389, use_ssl=False, get_info='NO_INFO')

.. note::
    The tutorial is intended to be used from the *REPL* (Read, Evaluate, Print, Loop), the interactive Python command
    line where you can directly type Python statements at the **>>>** prompt. The REPL implicitly use the ``repr()``
    representation for showing the output of a statement. If you instead want the ``str()`` representation you must
    explicitly ask for it using the ``print()`` function.

Getting information from the server
===================================
The LDAP protocol specifies that an LDAP server must return some information about itself. You can inspect them with
the ``.info`` attribute of the Server object::

    >>> server = Server('ipa.demo1.freeipa.org',  get_info=ALL)
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
Naming contexts           <...>                   Server stores information for 3 different DIT partitions
Alternative servers       None                    This is the only replica of the database
Supported Controls        <...>                   Optional controls that can be sent in a request operation
Supported Extentions      <...>                   Additional extended operations understood by the server
Supported SASL Mechanisms <...>                   Different additional SASL authentication mechanisms available
Schema Entry              cn=schema               The location of the schema in the DIT
Vendor name               389 Project             The brand/mark/name of this LDAP server
Vendor version            389-Directory/1.3.3 ... The version of this LDAP server
Other                     ...                     Additional information provided by the server
========================= ======================= =============================================================

From this response we know that this server is a stand-alone LDAP server that can hold entries in the dc=demo1,dc=freeipa,dc=org
portion of the DIT (usually called *context*), that supports various SASL access mechanisms and that is based on the
"389 Directory Service" server. Furthermore in the Supported Controls we can see it supports "paged searches", and the
"who am i" and "StartTLS" extended operations in Supported Extensions.

.. note:: Controls vs Extensions: in LDAP a *Control* is some additional information that can be attached to any LDAP
   request or response, while an *Extension* is a custom command that can be sent to the LDAP server in an **Extended
   Operation** Request. A Control usually modifies the behaviour of a standard LDAP operation, while an Extension is
   a completely new kind of operation that each vendor is free to include in its LDAP server implementation.
   An LDAP server declares which controls and which extendend operations it understands. The ldap3 library decodes the
   known supported controls and extended operation and includes a brief description and a reference to the relevant
   RFC in the ``.info`` attribute (when known). Not all controls or extensions are intended to be used by clients. Some controls and
   extensions are used by servers that hold a replica or a data partition. Unfortunately in the LDAP specifications
   there is no way to specify if such extensions are reserved for a server (**DSA**, *Directory Server Agent* in LDAP
   parlance) to server communication (for example in replicas or partitions management) or can be used
   by clients (**DUA**, *Directory User Agent*). Because the LDAP protocols doesn't provide a specific way for DSAs
   to communicate with each other, a DSA actually presents itself as a DUA to another DSA.

An LDAP server stores information about known *types* in its **schema**. The schema includes all information needed by
a client to correctly performs LDAP operations. Let's examine the LDAP server schema for the ipa.demo1.freeipa.org server::

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


The schema is a very long list that describes what type of data the server understands. It also specifies
what attributes can be stored in each class. Some classes are containers for other entries (either container or leaf)
and are used to build the hierarchy of the DIT. Container entries can have attributes too.
One important specification in the schema is if the attribute is *multi-valued* or not. A multi-valued attribute can
store one or more values. Every LDAP server must at least support the standard LDAP3 schema but can have additional
custom classes and attributes. The schema defines also the *syntaxes* and the *matching rules* of the different
data types stored in the DIT.

.. note::
   Object classes and attributes are independent objects. An attribute is not a "child" of a class neither a
   class is a "parent" of any attribute. Classes and attributes are linked in the schema with the ``MAY`` and ``MUST`` options
   of the object class definition that specifies what attributes an entry can contain and which of them are mandatory.

.. note::
   There are 3 different types of object classes: **ABSTRACT** (used only when defining the class hierarchy), **STRUCTURAL** (used to
   create concrete entries) and **AUXILIARY** (used to add additional attributes to an entry). Only one structural class can be used
   in an entry, while many auxiliary classes can be added to the same entry. Adding an object class to an entry simply means
   that the attribute types defined in that object class can be stored in that entry.

If the ldap3 library is aware of the schema used by the LDAP server it will try to automatically convert data retrieved by the Search
operation to their representation. An integer will be returned as an int, a generalizedDate as a datetime object and so on.
If you don't read the schema all the values are returned as bytes and unicode strings. You can control this behaviour with
the ``get_info`` parameter of the Server object and the ``check_names`` parameter of the Connection object.

Logging into the server
=======================
You haven't provided any credentials to the server yet, but you received a response anyway. This means that LDAP allows users to perform
operations anonymously without declaring their identity. Obviously what the server returns to an anonymous connection is someway limited.
This makes sense because originally the DAP protocol was intended for reading phone directories, as in a printed book, so its
content could be read by anyone.

If you want to establish an authenticated session you have two options: Simple Password and SASL. With Simple Password you provide
a **DN** (*Distinguished Name*) and a password. The server checks if your credentials are valid and permits or denies
access to the elements of the DIT. SASL provides additional methods to identify the user, as an external certificate or a Kerberos ticket.

.. note:: Distinguished Names: the DIT is a hierarchical structure, as a filesystem. To identify an entry you must specify
    its *path* in the DIT starting from the leaf that represents the entry up to the top of the Tree. This path is called the
    **Distinguished Name** (DN) of an entry and is constructed with key-value pairs, separated by a comma, of the names and the values
    of the entries that form the path from the leaf up to the top of the Tree. The DN of an entry is unique throughout the DIT
    and changes only if the entry is moved into another container within the DIT. The parts of the DN are called
    **Relative Distinguished Name** (RDN) because are unique only in the context where they are defined. So, for example,
    if you have a *inetOrgPerson* entry with RDN ``cn=Fred`` that is stored in an *organizationaUnit* with RDN ``ou=users`` that
    is stored in an *organization* with RDN ``o=company`` the DN of the entry will be ``cn=Fred,ou=users,o=company``.
    The RDN value must be unique in the context where the entry is stored. LDAP also support a (quite obscure) "multi-rdn"
    naming option where each part of the RDN is separated with the + character, as in ``cn=Fred+sn=Smith``.

.. warning:: Accessing Active Directory: with ldap3 you can also connect to an Active Directory server with the NTLM v2 protocol::

        >>> from ldap3 import Server, Connection, ALL, NTLM
        >>> server = Server('servername', get_info=ALL)
        >>> conn = Connection(server, user="Domain\\User", password="password", authentication=NTLM)

    This kind of authentication is not part of the LDAP 3 RFCs but uses a proprietary Microsoft authentication mechanism
    named SICILY. ldap3 implements it because it's much easier to use this method than Kerberos to access Active Directory.

Now try to ask to the server who you are::

    >>> conn.extend.standard.who_am_i()

We have used and Extended Operation, conveniently packaged in a function of the ``ldap3.extend.standard`` package, and get an empty response.
This means you have no authentication status on the server, so you are an **anonymous** user. This doesn't mean
that you are unknown to the server, actually you have a session open with it, so you can send additional operation requests. Even
if you don't send the anonymous bind operation the server will accept any operation requests as an anonymous user,
establishing a new session if needed.

.. note:: The ``extend`` namespace. The connection object has a special namespace called "extend" where more complex
    operations are defined. This namespace include a ``standard`` section and a number of specific vendor sections.
    In these sections you can find methods to perform tricky or hard-to-implement operations. For example in the
    ``microsoft`` section you can find a method to easily change the user password, and in the ``novell`` section
    a method to apply transactions to groups of LDAP operations. In the ``standard`` section you can also find an
    easy way to perform a paged search via generators.


.. warning:: Opening vs Binding: the LDAP protocol provides a Bind and an Unbind operation but, for historical reasons,
    they are not symmetrical. As any TCP connection the communication socket must be *open* before binding to the server.
    This is implicitly done by the ldap3 package when you issue a ``bind()`` or another operation or can be esplicity
    done with the ``open()`` method of the Connection object. The Unbind operation is actually used to *terminate* the
    connection, both ending the session and closing the socket. After the ``unbind()`` operation the connection
    cannot be used anymore. If you want to access as another user or change the current session to an anonymous one,
    you must issue ``bind()`` again. The ldap3 library includes the ``rebind()`` method to access the same connection
    as a different user. You must use ``unbind()`` only when you want to close the network socket.

Try to specify an identity to access the DIT::

    >>> conn = Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123', auto_bind=True)
    >>> conn.extend.standard.who_am_i()
    'dn: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org'

Now the server knows that you are a valid user and the ``who_am_i()`` extended operation returns your identity.

Establishing a secure connection
================================
If you check the connection info you can see that the Connection is using a cleartext (insecure) channel::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - **cleartext** - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - bound - open - <local: 192.168.1.101:50164 - remote: 209.132.178.99:**389**> - **tls not started** - listening - SyncStrategy - internal decoder'

This means that credentials pass unencrypted over the wire, so they can be easily captured by network eavesdroppers
(with unencrypted connections a network sniffer can capture passwords and other sensitive data). The LDAP protocol provides
two ways to secure a connection: **LDAP over TLS** and the **StartTLS** extended operation. Both methods establish a secure TLS
connection: the former secure with TLS the communication channel as soon as the connection is open, while the latter can
be used at any time on an already open unsecure connection to secure it issuing the StartTLS operation.

.. warning:: LDAP URL scheme: a cleartext connection to a server can be expressed in the URL with the **ldap://** scheme,
    while LDAP over TLS can be indicated with **ldaps://** even if this is not specified in any of the LDAP RFCs.
    If a scheme is included in the server name while creating the Server object, the ldap3 library opens the proper port,
    unencrypted or with the specified TLS options (or the default TLS options if none is specified).

.. note:: Default port numbers: the default port for cleartext (unsecure) communication is **389**, while the default port
   for LDAP over TLS (secure) communication is **636**. Note that because you can start a session on the 389 port and then
    raise the security level with the StartTLS operation, you can have a secure communication even on the 389 port (usually
    considered unsecure). Obviously the server can listen on different ports. When defining the Server object you can specify
    which port to use with the ``port`` parameter. Keep this in mind if you need to connect to a server behind a firewall.

Now try to use the StartTLS extended operation::

    >>> conn.start_tls()
    True

if you check the connection status you can see that the session is on a secure channel now, even if started on a cleartext connection::

    >>> print(conn)
    ldap://ipa.demo1.freeipa.org:389 - cleartext - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - bound - open - <local: 192.168.1.101:50910 - remote: 209.132.178.99:389> - tls started - listening - SyncStrategy - internal decoder


To start the connection on a SSL socket::

    >>> server = Server('ipa.demo1.freeipa.org', use_ssl=True, get_info=ALL)
    >>> conn = Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123', auto_bind=True)
    >>> print(conn)
    ldaps://ipa.demo1.freeipa.org:636 - ssl - user: uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org - bound - open - <local: 192.168.1.101:51438 - remote: 209.132.178.99:636> - tls not started - listening - SyncStrategy - internal decoder


Either with the former or the latter method the connection is now encrypted. We haven't specified any TLS option, so
there is no checking of certificate validity. You can customize the TLS behaviour providing a ``Tls`` object to the Server
object. The Tls object configures the security context::

    >>> from ldap3 import Tls
    >>> import ssl
    >>> tls_configuration = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1)
    >>> server = Server('ipa.demo1.freeipa.org', use_ssl=True, tls=tls_configuration)
    >>> conn = Connection(server)
    >>> conn.open()
    ...
    ldap3.core.exceptions.LDAPSocketOpenError: (LDAPSocketOpenError('socket ssl wrapping error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:600)',),)

In this case, using the FreeIPA demo server we get a LDAPSocketOpenError exception because the certificate cannot be verified.
You can configure the Tls object with a number of options. Look at :ref:`SSL and TLS <ssltls>` for more information.

The FreeIPA server doesn't return a valid certificate so to continue the tutorial let's revert the certificate validation to CERT_NONE::

    >>> tls_configuration.validate = ssl.CERT_NONE


Connection context manager
==========================
The Connection object responds to the context manager protocol, so you can perform LDAP operations with automatic open, bind and unbind as in the following example::

    >>> with Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123') as conn:
            conn.search('dc=demo1,dc=freeipa,dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn','krbLastPwdChange', 'objectclass'])
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

When the Connection object exits the context manager it retains the state it had before entering the context. The connection
is always open and bound while in context. If the connection was not bound to the server when entering the context the
Unbind operation will be tried when you leave the context even if the operations in the context raise an exception.
