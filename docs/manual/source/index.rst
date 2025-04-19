.. ldap3 documentation master file, created by
   sphinx-quickstart on Tue Aug 26 12:24:10 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ldap3's documentation
================================

ldap3 is a pure Python LDAP 3 client library strictly conforming to RFC4510 and is released under the LGPL v3 open source license.
RFC4510 is the current LDAP specification (June 2006) from IETF and obsoletes the previous LDAP RFCs 2251, 2830, 3771 (December 1997).

ldap3 can be used with any Python version starting from 2.6, including all Python 3 versions. It also works with PyPy and PyPy3.


.. note::
   ldap3 versioning follows `SemVer`_.
.. _SemVer: http://semver.org


.. warning::
   Thread safe strategies

   In multithreaded programs you must use one of **SAFE_SYNC** (synchronous connection strategy), **SAFE_RESTARTABLE** (restartable syncronous connection strategy) or **ASYNC** (asynchronous connection strategy).
   Each LDAP operation with SAFE_SYNC or SAFE_RESTARTABLE strategies returns a tuple of four elements: status, result, response and request.

   * status: states if the operation was successful

   * result: the LDAP result of the operation

   * response: the response of a LDAP Search Operation

   * request: the original request of the operation

   The SafeSync strategy can be used with the Abstract Layer, but the Abstract Layer currently is NOT thread safe.
   For example, to use *SAFE_SYNC*::

      from ldap3 import Server, Connection, SAFE_SYNC
      server = Server('my_server')
      conn = Connection(server, 'my_user', 'my_password', client_strategy=SAFE_SYNC, auto_bind=True)
      status, result, response, _ = conn.search('o=test', '(objectclass=*)')  # usually you don't need the original request (4th element of the returned tuple)


   With *ASYNC* you must request the response with the *get_response()* method.

Contents
--------

.. toctree::
   :maxdepth: 3

   welcome
   features
   tutorial
   installation
   server
   schema
   connection
   ssltls
   metrics
   operations
   extend
   encoding
   abstraction
   ldif
   exceptions
   utils
   logging
   mocking
   testing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
