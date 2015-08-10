##############
LDAP3 Tutorial
##############

What LDAP is not?
=================

If you're reading this tutorial I assume that you already know what LDAP is, or have a rough idea of it. If you really
don't know it this is not a problem because after reading this tutorial you should be able to understand LDAP and access an
LDAP compliant server and use it. I'd rather like to be sure that you are aware of what LDAP is not:

- it's not a server
- it's not a database
- it's not a network service
- it's not an authentication procedure
- it's not a user/password repository
- it's not an open source neither a closed source product

I think is important to know what LDAP is not because people tend to call "LDAP" a peculiar part of what they use of the
Lightweight Directory Access Protocol. LDAP is just a "protocol", like many of the other 'trailing-P' words
in the Internet ecosystem (HTTP, FTP, IP, TCP...). It's a set of rules you have to use to "talk" to an external
server/database/service/procedure/repository/product (all things in the above list). All the talk you can do via LDAP is
about key/value(s) pairs grouped in a hierarchical structure. LDAP doesn't specify how the data is stored or how the user
is authorized to read and modify them. There are only a few types of data that each LDAP server must recognize (the
standard *schema* we'll meet later).

That's all, all the (sometime too complex) LDAP machinery you will interact with has this only purpose.

Being a standard protocol LDAP is not related to any specific product and it is described in a set of RFC (Request for
comments, the official rules of the Internet ecosystem). Its latest version is 3 and is documented in the RFC4510
released in June, 2006.


A very brief history of LDAP
============================

You may wonder why the "L" in LDAP? Well, its ancestor was called DAP (Directory Access Protocol)
and was developed in the 1980s by the CCITT (now ITU-T), the International Committee for Telephone and Telegraphy (a venerable
entity that gave us, among other, the fax and the modem protocols we used in the pre-Internet era). DAP was a very "heavy"
and hard to implement protocol (either for the client and the server components) and was not accessible via TCP/IP. In 1993
a lightweight access protocol was invented to act as a gateway to the DAP world. Afterwards followed server products
that could understand LDAP directly and the gateway to DAP was soon cut off. LDAP v3 was first documented in 1997 and its
documentation was revised in 2006.


The ldap3 package
=================

ldap3 is a fully compliant ldap v3 client and follows the latest (as per 2015) standard RFCs. It's written from scratch to be
compatible with Python 2 and Python 3 and can be used on any machine where the Python interpreter can access the network.

Chances are that you find the ldap3 package already installed on your machine, just try to **import ldap3** from your Python console.

If you get an ImportError you need to install the package from pypi via pip::

    pip install ldap3


.. note::

   If pip complains about certificates you should speficy the path to the pypi CA with the --cert parameter::

   pip install ldap3 --cert /etc/ssl/certs/DigiCert_High_Assurance_EV_Root_CA.pem


or from source::

    cd ldap3
    python setup.py install

ldap3 installs the pyasn1 package if not present. This package is used to communicate with the server over the network.

ldap3 usage is very simple and straightforward: you define a Server object, a Connection object tied to the Server and
issue commands to it. A server can have more than one connection and there are different communication strategies to choose
from. All the imports are done in the ldap3 namespace, that exposes all you need to interact with the LDAP server.
At least you need the Server and the Connection object, and any additional constant you will use in your LDAP conversation
(constants are defined in upper case)::

    from ldap3 import Server, Connection, ALL

Accessing an LDAP server
========================

In this tutorial we will access a free public test LDAP server available at "ldap.forumsys.com". We are allowed read only access,
so we can't modify any data on the server.

In the LDAP protocol the login operation is called **bind**. A bind can be performed in 3 different ways: anonymous bind,
simple password bind, and SASL (a Simple Authentication and Security Layer that allows multiple authentication methods)
bind. You can think of the Anonymous bind as a *public* access to the LDAP server where you don't provide any credentials
and the server apply some *default* access rules. Not all LDAP servers allow anonymous bind. With the simple password
binding and the SASL binding you provide credentials that the LDAP server uses to determine your authorizazion level.
Again, keep in mind that the LDAP v3 standard doesn't define any specific access level and that the authorization
mechanism is not specified at all. So each LDAP server can have a different method for authorizing the user to different
access levels.

Let's start accessing the server with an anonymous bind::

    >>> server = Server('ldap.forumsys.com')
    >>> conn = Connection(server)
    >>> conn.bind()
    >>>

or shorter::

    >>> conn = Connection('ldap3.forumsys.com', auto_bind=True)
    >>>

It hardly could be simpler than that! We already have a full working anonymous connection open and bound to the server
with a synchronous *communication strategy* (more on communication strategies later)::

    >>> print(conn)
    'ldap://ldap.forumsys.com:389 - cleartext - user: None - bound - open - <local: 192.168.1.101:51038 - remote: 23.20.46.132:389> \
    - tls not started - listening - SyncStrategy'
    >>>

With print(conn) [or str(conn)] we ask an overview of the connection. We already get back a lot of information:

+--------------------------------------------------------+-------------------------------------------------------------------+
|ldap://ldap.forumsys.com:389                            |the server name and the port we are connected to                   |
|cleartext                                               |the authentication method used                                     |
|user: None                                              |the credentials used, in this case None means an anonymous binding |
|bound                                                   |the status of the LDAP session                                     |
|open                                                    |the status of the underlying TCP/IP session                        |
|<local: 192.168.1.101:51038 - remote: 23.20.46.132:389> |the local and remote socket endpoints                              |
|tls not started                                         |the status of the TLS (Transport Layer Security) session           |
|listening                                               |the status of the communication strategy                           |
|SyncStrategy                                            |the communication strategy used                                    |
+--------------------------------------------------------+-------------------------------------------------------------------+

If you ask for the representation of the conn object you can get a view of all the object definition arguments::

    >>> conn
    Connection(server=Server(host='ldap.forumsys.com', port=389, use_ssl=False, get_info='NO_INFO'), auto_bind='NO_TLS', \
    version=3, authentication='ANONYMOUS', client_strategy='SYNC', auto_referrals=True, check_names=True, read_only=False,
    lazy=False, raise_exceptions=False)
    >>>

If you just copy and paste the object representation you can instantiate a new one. This is very helpful when experimenting
in the interactive console.

.. sidebar:: Object representation
    the ldap3 library uses the following object representation rule: when you use the str() representation you get all
    the information about the status of the object, when you use the repr() you get back a string you can use in the
    Python console to recreate the object.


... more to come ...


+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+---------------------+
| body row 3             | Cells may  | - Table cells       |
+------------------------+ span rows. | - contain           |
| body row 4             |            | - body elements.    |
+------------------------+------------+---------------------+



=====  =====  =======
  A      B    A and B
=====  =====  =======
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =======
