Installation and configuration
##############################

Installation is straightforward and can be done via a package manager or from source.


Installation with a package manager
-----------------------------------

You need "setuptools" and "pip" (or any other package manager that can download and install from pypi) to install ldap3.
Then you can download and install the ldap3 library directly from pypi::

    pip install ldap3

This library has only one dependence on the *pyasn1* module, You can install it or let the installer do it for you.


Installation from the source
----------------------------

You can download the latest source in trunk from https://github.com/cannatag/ldap3 then you can build the library in
the source directory with::

    python setup.py install

Global configuration
--------------------

in the *ldap3/__init__.py* that should have been created in the site-packages folder there are some configurable settings:

* RESPONSE_SLEEPTIME = 0.02  # seconds to wait while waiting for a response in asynchronous strategies
* RESPONSE_WAITING_TIMEOUT = 1  # waiting timeout for receiving a response in asynchronous strategies (in seconds)
* SOCKET_SIZE = 4096  # socket byte size
* RESTARTABLE_SLEEPTIME = 2  # time to wait in a restartable strategy before retrying the request
* RESTARTABLE_TRIES = 50  # number of times to retry in a restartable strategy before giving up. Set to True for unlimited retries

This parameters are library-wide and usually you can keep the default values.

Importing classes and constants
-------------------------------

All classes and constants needed to use the ldap3 library can be imported from the **ldap3** namespace::

    from ldap3 import Connection, Server, AUTH_ANONYMOUS, AUTH_SIMPLE

Library errors
--------------

Errors are returned as exceptions of the LDAPExceptionError class, with a description of the error condition in the *args* attribute.

Communication exceptions have multiple inheritance either from LDAPCommunicationError and the specific socket exception.
The last exception message for a connection is stored in the last_error attribute of the Connection object when available.

When **raise_exceptions=True** the Connection object will raise exceptions for all operations that return a result code different
from RESULT_SUCCESS, RESULT_COMPARE_FALSE, RESULT_COMPARE_TRUE, RESULT_REFERRAL.

Exceptions are defined in the **ldap3.core.exceptions** package.

PEP8 compliance
---------------
ldap3 is PEP8 compliant, except for line length.
