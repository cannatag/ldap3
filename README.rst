LDAP3
=====

.. image:: https://img.shields.io/pypi/v/ldap3.svg
    :target: https://pypi.python.org/pypi/ldap3/
    :alt: Latest Version

.. image:: https://img.shields.io/travis/cannatag/ldap3/master.svg
    :target: https://travis-ci.org/cannatag/ldap3
    :alt: TRAVIS-CI build status for master branch

.. image:: https://img.shields.io/pypi/l/ldap3.svg
    :target: https://pypi.python.org/pypi/ldap3/
    :alt: License


ldap3 is a strictly RFC 4510 conforming LDAP V3 pure Python **client** library. The same codebase works with Python 2, Python 3, PyPy and PyPy3.

[This project was previously named **python3-ldap**]

.. warning:: In version 2.x some default values (auto_range in Connection object, get_info in Server object) are changed and the the ldap3 namespace
    has been decluttered, removing redundant constants. The result code constants are moved to ldap3.core.results and the ldap3 custom exceptions
    are stored in ldap3.core.exceptions. If you experience errors in your existing code you should rearrange the import statements or explicitly
    set the defaults to their former values).

.. note:: **A more pythonic LDAP: LDAP operations are clumsy and hard-to-use because reflect the old-age idea that most time-consuming operations
    should be done on the client to not clutter and hog the server with unneeded elaboration. Starting from version 2.0.2 ldap3 includes
    brand-new fully functional **Abstraction Layer** that let you interact with the DIT in a modern and *pythonic* way. With the Abstraction
    Layer you can perform all CRUD (Create, Read, Update, Delete) operations in a simple way, with no need of using any LDAP specific operation.**

Home Page
---------

Project home page is https://github.com/cannatag/ldap3


Documentation
-------------

Documentation is available at http://ldap3.readthedocs.io


License
-------

The ldap3 project is open source software released under the **LGPL v3 license**.
Copyright 2013, 2014, 2015, 2016 Giovanni Cannata

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

For information and suggestions you can contact me at cannatag@gmail.com or you can also a support ticket on https://github.com/cannatag/ldap3/issues/new


Changelog
---------

You can read the current changelog at http://ldap3.readthedocs.io/changelog.html
