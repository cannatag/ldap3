The ldap3 project
#################

ldap3 is a strictly RFC 4511 conforming LDAP V3 pure Python client. The whole ldap3 library has been written from scratch
and the same identical codebase works with Python 2, Python 3, PyPy and PyPy3 on any system where it can gain access to
the network via a Python interpreter and its Standard Library.


License
-------

The ldap3 library and is open source software released under the **LGPL v3 license**.


RFCs Compliance
---------------

The ldap3 library strictly follows the latest (as of 2015) RFCs describing the LDAP v3 protocol:

* RFC4510: Technical Specification Road Map
* RFC4511: The Protocol
* RFC4512: Directory Information Models
* RFC4513: Authentication Methods and Security Mechanisms
* RFC4514: String Representation of Distinguished Names
* RFC4515: String Representation of Search Filters
* RFC4516: Uniform Resource Locator
* RFC4517: Syntaxes and Matching Rules
* RFC4518: Internationalized String Preparation
* RFC4519: Schema for User Applications

The following RFCs, describing additional functionality of the LDAP3 protocol are also followed:

* RFC2696: LDAP Control Extension for Simple Paged Results Manipulation
* RFC2849: The LDAP Data Interchange Format (LDIF) - Technical Specification
* RFC3045: Storing Vendor Information in the LDAP root DSE
* RFC3062: LDAP Password Modify Extended Operation
* RFC4525: Modify-Increment Extension
* RFC4530: entryUUID Operational Attribute
* RFC4532: Who am I?" Operation
* RFC5020: entryDN Operational Attribute

The ldap3 library deliberately doesn't follow the specification in RFC4511 (4.5.1.8.1) that states that in a Search
operation "an empty list with no attributes requests the return of all user attributes.". Instead you have to request
each attribute explicitly or use the ldap3.ALL_ATTRIBUTES value in the attributes requested list in the Search operation.
This is to avoid pollution from bad formed search operation where alle attributes are returned back from the server when,
probably, only a few of them, if not only one, are really required by the application.


PEP8 Compliance
---------------

ldap3 is PEP8 compliant, except for line length.


Home Page
---------

Project home page is https://github.com/cannatag/ldap3


Documentation
-------------

Documentation is available at http://ldap3.readthedocs.org


Download
--------

Package download is available at https://pypi.python.org/pypi/ldap3


Install
-------

Install with **pip install ldap3**. The library auto install the pyasn1 package. If you need Kerberos support you must
install the gssapi package. ldap3 includes a backport (from Python 3.4.3) of ssl.check_hostnames to be used on older
(version < 2.7.10) Python version. If you want to use a more up to date version of the check_hostnames feature you can
install the backports.ssl_check_hostnames package that should be kept updated with the Standard Library of the latest
Python release.


GIT repository
--------------

You can download the latest source at https://github.com/cannatag/ldap3/master


Contribute to the project
-------------------------

You can contribute to the ldap3 project on https://github.com/cannatag/ldap3/dev


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

* **JetBrains** for donating to this project the Open Source license of *PyCharm 3 Professional*.

* **GitHub** for providing the *free source repository space and tools* I use to develop this project.

* The **Python Software Foundation** for providing support for building the test lab infrastructure.
