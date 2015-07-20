Installation and configuration
##############################

Installation is straightforward and can be done via a package manager or from the source.


Installation with a package manager
-----------------------------------

You need the *setuptools* and *pip* packages (or any other package manager that can download and install from pyPI) to
install ldap3. Then you can download and install the ldap3 library directly from pyPI::

    pip install ldap3

This library has only one dependence on the *pyasn1* module, You can install it or let the installer do it for you.

If you need to access a server with the Kerberos SASL authentication mechanism you must install the *gssapi* package.

ldap3 includes a backport (from Python 3.4.3) of ssl.check_hostnames to be used on older
(version < 2.7.10) Python version. If you want to use a more up to date version of the check_hostnames feature you can
install the backports.ssl_check_hostnames package that should be kept updated with the Standard Library of the latest
Python release.


Installation from the source
----------------------------

You can download the latest source from https://github.com/cannatag/ldap3 then you can install the library in with::

    python setup.py install


Global configuration
--------------------

in the *ldap3/__init__.py*  present in the site-packages ldap3 folder there are some configurable settings:

* RESPONSE_SLEEPTIME = 0.02  # seconds to wait while waiting for a response in asynchronous strategies.
* RESPONSE_WAITING_TIMEOUT = 1  # waiting timeout for receiving a response in asynchronous strategies (in seconds).
* SOCKET_SIZE = 4096  # socket byte size.
* RESTARTABLE_SLEEPTIME = 2  # time to wait in a restartable strategy before retrying the request.
* RESTARTABLE_TRIES = 50  # number of times to retry in a restartable strategy before giving up.
  Set to True for unlimited retries.

This parameters are library-wide and usually you should keep the default values.


Importing objects and constants
-------------------------------

All objects and constants needed to use the ldap3 library can be imported from the **ldap3** namespace::

    from ldap3 import Connection, Server, ANONYMOUS, SIMPLE, SYNC, ASYNC


Library errors
--------------

You can deal with errors in two different ways. By default in synchronous strategies each LDAP operation returns a
True/False value that specify if the operation has been successful or not. In case of failures you can check the
error description in the last_error attribute of the Connection object. In some cases an exception of the custom
hierarchy starting from the LDAPExceptionError class is raised with a description of the error condition in the *args*
attribute.

If you prefer to deal always with Exceptions you can set the **raise_exceptions** attribute to True in the Connection
object definition. From now on the Connection will raise exceptions for all operations that return a result codeù
different from RESULT_SUCCESS, RESULT_COMPARE_FALSE, RESULT_COMPARE_TRUE, RESULT_REFERRAL.

Communication exceptions have multiple inheritance either from LDAPCommunicationError and the specific socket exception.
The last exception message for a connection is stored in the last_error attribute of the Connection object when available.

Exceptions are defined in the **ldap3.core.exceptions** package.
