The ldap3 project
#################

ldap3 is a strictly RFC 4510 conforming LDAP v3 pure Python client library. The whole ldap3 library has been **written from scratch**
and the **same codebase works with Python 2, Python 3, PyPy, PyPy3 and Nuikta** on any system where it can gain access to
the network via a Python interpreter and the Python Standard Library.


License
-------

The ldap3 library is open source software released under the **LGPL v3 license** (http://www.gnu.org/licenses/lgpl-3.0.html).
This means that you can use the ldap3 library in any application (either open or proprietary). You can also copy, distribute and modify
the ldap3 library provided that modifications are described and licensed for free under LGPL.
Derivatives works of ldap3 can only be redistributed under LGPL, but applications that use the library don't have to be.


RFCs Compliance
---------------

The ldap3 library strictly follows the latest (as of 2015) RFCs describing the LDAP v3 protocol:

* The **latest RFCs for LDAP v3** (dated 2006) obsolete the previous RFCs specified in RFC3377 (2251-2256, 2829, 2830, 3371) for LDAP v3 and amend and clarify the LDAP protocol.
* All the ASN1 definitions are written from scratch to be current with RFC 4511.

To avoid unnecessary server and network load caused by poor formed searches The ldap3 library deliberately doesn't
follow the specification in RFC4511 (4.5.1.8.1) that states that in a Search operation "an empty list with no attributes requests
the return of all user attributes.". Instead you must explicitly request the attributes you need or use the ldap3.ALL_ATTRIBUTES
value in the Search operation.

The library allows to send an empty member list while creating a GroupOfNames object, even if this is not allowed in the
official LDAP v3 schema.

ldap3 allows communication over Unix sockets (ldapi:// scheme, LDAP over IPC) even if this is not required by any official LDAP RFCs.


PEP8 Compliance
---------------

ldap3 is PEP8 compliant, except for line length. PEP8 (https://www.python.org/dev/peps/pep-0008/) is the standard coding style
guide for the Python Standard Library and for many other Python projects. It provides a consistent way of writing code for maintainability
and readability following the principle that "software is more read then written".


Home Page
---------

The home page of the ldap3 project is https://github.com/cannatag/ldap3


Documentation
-------------

Documentation is available at http://ldap3.readthedocs.io. You can download a PDF copy of the manual at https://media.readthedocs.org/pdf/ldap3/stable/ldap3.pdf


Download
--------

The ldap3 package can be downloaded at https://pypi.python.org/pypi/ldap3. If you use a package manager that support the *wheel* format
you can get the universal wheel package, and install it on any supported Python environment.


Install
-------

Install with **pip install ldap3**. If needed the library installs the ``pyasn1`` package. If you need Kerberos support you must
install the ``gssapi`` package. ldap3 includes a backport (from Python 3.4.3) of ssl.check_hostnames to use on older
(< 2.7.10) Python version. If you want to use a newer version of the check_hostnames feature you can
install the ``backports.ssl_check_hostnames`` package that should be kept updated by its author with the latest Python release.


GIT repository
--------------

You can download the latest released source code at https://github.com/cannatag/ldap3/tree/master


Contribuiting to this project
-----------------------------

ldap3 source is hosted on github. You can contribute to the ldap3 project on https://github.com/cannatag/ldap3
forking the project and submitting a *pull request+ with your modifications.


Continuous integration
----------------------

Continuous integration for testing is at https://travis-ci.org/cannatag/ldap3


Support
-------

You can submit support tickets on https://github.com/cannatag/ldap3/issues/new


Contact me
----------

For information and suggestions you can contact me at cannatag@gmail.com. You can also open a support ticket on
https://github.com/cannatag/ldap3/issues/new


Thanks to
---------

* **Ilya Etingof**, the author of the *pyasn1* package for his excellent work and support.

* **Mark Lutz** for his *Learning Python* and *Programming Python* excellent books series and **John Goerzen** and
  **Brandon Rhodes** for their books *Foundations of Python Network Programming* (Second and Third edition).
  These books are wonderful tools for learning Python and this project owes a lot to them.

* **JetBrains** for donating to this project the Open Source license of *PyCharm 4 Professional*.

* **GitHub** for providing the *free source repository space and tools* used to develop this project.

* The **Python Software Foundation** for supporting the cloud lab infrastructure used for testing the library.
