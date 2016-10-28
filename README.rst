LDAP3
=====

.. image:: https://img.shields.io/pypi/v/ldap3.svg
    :target: https://pypi.python.org/pypi/ldap3/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/ldap3.svg
    :target: https://pypi.python.org/pypi/ldap3/
    :alt: License


ldap3 is a strictly RFC 4510 conforming **LDAP V3 pure Python client** library. The same codebase runs in Python 2, Python 3, PyPy and PyPy3.


Version 2 warning
-----------------

In version 2 of ldap3 some default values have been changed and the ldap3 namespace has been decluttered, removing redundant
constants (look at the changelog for details). Also, the result code constants were moved to ldap3.core.results and the ldap3 custom exceptions
were stored in ldap3.core.exceptions. If you experience errors in your existing code you should rearrange the import statements or explicitly
set the defaults to their former values.


A more pythonic LDAP
--------------------

LDAP operations look clumsy and hard-to-use because they reflect the old-age idea that time-consuming operations
should be done on the client to not clutter and hog the server with unneeded elaboration. ldap3 includes a fully functional **Abstraction
Layer** that lets you interact with the DIT in a modern and *pythonic* way. With the Abstraction Layer you don't need to directly issue any
LDAP operation at all.


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
You can submit pull request on the **dev** branch at https://github.com/cannatag/ldap3/tree/dev


Thanks to
---------

* **Ilya Etingof**, the author of the *pyasn1* package for his excellent work and support.

* **Mark Lutz** for his *Learning Python* and *Programming Python* excellent books series and **John Goerzen** and **Brandon Rhodes** for their book *Foundations of Python Network Programming*. These books are wonderful tools for learning Python and this project owes a lot to them.

* **JetBrains** for donating to this project the Open Source license of *PyCharm Professional*.

* **GitHub** for providing the *free source repository space and the tools* I use to develop this project.

* The **FreeIPA** team for letting me use their demo LDAP server in the ldap3 tutorial.


Contact me
----------

For information and suggestions you can contact me at cannatag@gmail.com. You can also a support ticket on https://github.com/cannatag/ldap3/issues/new


Changelog
---------

Updated changelog at https://ldap3.readthedocs.io/changelog.html

