.. ldap3 documentation master file, created by
   sphinx-quickstart on Tue Aug 26 12:24:10 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ldap3's documentation
================================

ldap3 is a pure Python LDAP 3 client library strictly conforming to RFC4510 and is released under the LGPL v3 open source license.
RFC4510 is the current LDAP specification (June 2006) from IETF and obsoletes the previous LDAP RFCs 2251, 2830, 3771 (December 1997).

ldap3 can be used with any Python version starting from 2.6, including all Python 3 versions. It also works with PyPy and PyPy3.


.. warning::
   ldap3 versioning follows `SemVer`_. In version 2 the public API has slightly changed from version 1: some default values have been changed
   and the ldap3 namespace has been decluttered, removing redundant constants (look at the changelog for details). Also, the result code
   constants were moved to ldap3.core.results and the ldap3 custom exceptions were stored in ldap3.core.exceptions. If you experience
   errors in your existing code you should rearrange the import statements or explicitly set the defaults to their former values.

   .. _SemVer: http://semver.org

Contents
--------

.. toctree::
   :maxdepth: 2

   welcome
   tutorial
   features
   installation
   servers
   connections
   ssltls
   metrics
   operations
   extend
   abstraction
   ldif
   exceptions
   utils
   logging
   mocking
   testing
   changelog
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
