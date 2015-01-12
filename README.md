LDAP3
=====

[![Build Status](https://travis-ci.org/cannatag/ldap3.svg?branch=master)](https://travis-ci.org/cannatag/ldap3)
    
    
ldap3 is a strictly RFC 4511 conforming LDAP V3 pure Python client. The same codebase works with Python, Python 3, PyPy and PyPy3.

This project was formerly named **python3-ldap**. The name has been changed to avoid confusion with the python-ldap library.

Home Page
---------

Project home page is https://github.com/cannatag/ldap3


Documentation
-------------

Documentation is available at http://ldap3.readthedocs.org


License
-------

The ldap3 project is open source software released under the **LGPL v3 license**.


PEP8 Compliance
---------------

ldap3 is PEP8 compliant, except for line length.


Download
--------

Package download is available at https://pypi.python.org/pypi/ldap3.


Install
-------

Install with **pip install ldap3**


Git repository
--------------

You can download the latest source at https://github.com/cannatag/ldap3


Continuous integration
----------------------

Continuous integration for testing is at https://travis-ci.org/cannatag/ldap3

Support
-------

You can submit support tickets on https://github.com/cannatag/ldap3/issues/new


Thanks to
---------

* **Ilya Etingof**, the author of the *pyasn1* package for his excellent work and support.
* **Mark Lutz** for his *Learning Python* and *Programming Python* excellent books series and **John Goerzen** and **Brandon Rhodes** for their book *Foundations of Python Network Programming*. These books are wonderful tools for learning Python and this project owes a lot to them.
* **JetBrains** for donating to this project the Open Source license of *PyCharm 3 Professional*.
* **GitHub** for providing the *free source repository space and the tools* I use to develop this project.
* The **Python Software Foundation** for providing support for the test lab infrastructure.


Contact me
----------

For information and suggestions you can contact me at cannatag@gmail.com or you can open a support ticket on https://github.com/cannatag/ldap3/issues/new

CHANGELOG
---------

* 0.9.7.2 2015.01.11
    - Fixed a bug when resolving IP address with getaddrinfo(). On OSX returned an UDP connection.

* 0.9.7.1 2015.01.05
    - Moved to Github
    - Moved to Travis-CI for continuous integration
    - Moved to ReadTheDocs for documentation
    - Moved testing servers in the cloud, to allow testing from Travis-CI
    - Project renamed from python3-ldap to ldap3 to avoid name clashing with the existing python-ldap library
    - Constant values in ldap3 are now strings. This is helpful in testing and debugging
    - Test suite fully refactored to be used in cloud lab and local development lab
    - Test suite includes options for testing against eDirectory, Active Directory and OpenLDAP

Previous versions changelog is available at http://pythonhosted.org//python3-ldap/changelog.html
