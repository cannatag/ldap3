LDAP3
=====

.. image:: https://img.shields.io/pypi/v/ldap3.svg
    :target: https://pypi.python.org/pypi/ldap3/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/l/ldap3.svg
    :target: https://pypi.python.org/pypi/ldap3/
    :alt: License

.. image:: https://img.shields.io/travis/cannatag/ldap3/master.svg
    :target: https://travis-ci.org/cannatag/ldap3
    :alt: TRAVIS-CI build status for master branch


ldap3 is a strictly RFC 4510 conforming **LDAP V3 pure Python client** library. The same codebase runs in Python 2, Python 3, PyPy and PyPy3.


A more pythonic LDAP
--------------------

LDAP operations look clumsy and hard-to-use because they reflect the old-age idea that time-consuming operations should be performed client-side
to not hog the server with heavy elaborations. To alleviate this ldap3 includes a fully functional **Abstraction Layer** that lets you
interact with the LDAP server in a modern and *pythonic* way. With the Abstraction Layer you don't need to directly issue any LDAP operation at all.


Thread safe strategies
----------------------

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

Home Page
---------

The home page of the ldap3 project is https://github.com/cannatag/ldap3


Documentation
-------------

Documentation is available at http://ldap3.readthedocs.io


License
-------

The ldap3 project is open source software released under the **LGPL v3 license**.
Copyright 2013 - 2025 Giovanni Cannata


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


Support & Development
---------------------

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

For information and suggestions you can contact me at cannatag@gmail.com. You can also open a support ticket on https://github.com/cannatag/ldap3/issues/new


Donate
------

If you want to keep this project up and running you can send me an Amazon gift card. I will use it to improve my skills in Information and Communication technologies.


Changelog
---------

Updated changelog at https://ldap3.readthedocs.io/changelog.html

