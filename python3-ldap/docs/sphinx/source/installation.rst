##############################
Installation and configuration
##############################

Installation is very straightforward and can be done via a package manager or from source.


Installation with a package manager
-----------------------------------

You need "setuptools" and "pip" (or any other package manager that can download and install from pypi) to install python3-ldap. Then you can download and install the python3-ldap library directly from pypi::

    pip install python3-ldap

This library has only one dependence on the *pyasn1* module (you don't need the additional pyasn1_modules package), you can install it or let the installer do it for you.

Installation from the source
----------------------------

You can download the latest source in trunk from https://subversion.assembla.com/svn/python3-ldap using a svn client, then you can build the library in the source directory with::

    python setup.py install

Global configuration
--------------------

in the *ldap3/__init__.py* that should have been created in the site-packages folder there are some configurable settings:

* RESPONSE_SLEEPTIME = 0.02  # seconds to wait while waiting for a response in asynchronous strategies
* RESPONSE_WAITING_TIMEOUT = 1  # waiting timeout for receiving a response in asynchronous strategies (in seconds)
* SOCKET_SIZE = 4096  # socket byte size
* RESTARTABLE_SLEEPTIME = 2  # time to wait in a restartable strategy before retrying the request
* RESTARTABLE_TRIES = 50  # number of times to retry in a restartable strategy before giving up. Set to True for unlimited retries

This parameters are library-wide and Usually you can keep the default values.

Importing classes and constants
-------------------------------

All classes and constants needed to use the python3-ldap library can be imported from the **ldap3** namespace::

    from ldap3 import Connection, Server, AUTH_ANONYMOUS, AUTH_SIMPLE

Library errors
--------------

Errors are returned as exceptions of the LDAPExceptionError class, with a description of the error condition in the *args* attribute.

Communication exceptions have multiple inheritance either from LDAPCommunicationError and the specific socket exception.
The last exception message for a connection is stored in the last_error attribute of the Connection object when available.

When used in **raise_exceptions=True** mode the Connection object will raise exceptions for all operations that return a result code different from RESULT_SUCCESS, RESULT_COMPARE_FALSE, RESULT_COMPARE_TRUE, RESULT_REFERRAL.

Exceptions are defined in the **ldap3.core.exceptions** package.

PEP8 compliance
---------------
Starting from version 0.9.0 python3-ldap is PEP8 compliant. To use the previous signature for the Server, Connection and Tls object you can import them from the ldap3.compat package.
