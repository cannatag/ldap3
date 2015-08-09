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
Lightweight Directory Access Protocol (ops.. I revealed it!). LDAP is just a "protocol", like many of the other '*P' words
in the Internet ecosystem (HTTP, FTP, IP, TCP...). It's a set of rules you have to use to "talk" to an external
server/database/service/procedure/repository/product (all things in the above list). All the talk you can do via LDAP is
about key/value(s) pairs grouped in a hierarchical structure. That's all, all the (sometime too complex) LDAP machinery
you will interact with has this only purpose.

Being a standard protocol LDAP is not related to any specific product and it is described in a set of RFC (Request for
comments, the official rules of the Internet ecosystem). Its latest version is 3 and is documented in the RFC4510
released in June, 2006.


A very brief history of LDAP
============================

You may wonder why the "L" in LDAP? Well, its ancestor was called DAP (Directory Access Protocol)
and was developed in the 1980s by the CCITT (now ITU-T), the International Committee for Telephone and Telegraphy (a venerable
entity that gave us, among other, the fax and the modem protocols we used in the pre-Internet era). DAP was a very "heavy"
and hard to implement protocol (either for the client and the server components) and was not accessible via TCP/IP. In 1993
a lightweight access protocol was invented in 1993 to act as a gateway to the DAP world. Afterwards followed server products
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


... more to come ...
