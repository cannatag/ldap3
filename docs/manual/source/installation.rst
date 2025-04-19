Installation and configuration
##############################

Installation is straightforward and can be done via a package manager or from the source.


Installation with a package manager
-----------------------------------

You need the **pip** package (or another package manager that can download and install from pyPI) to
install ldap3. Then you can download and install the ldap3 library directly from pyPI::

    pip install ldap3

This library has two dependencies (the *pyasn1* module and the *pycryptodomex* module), you can install it or let the installer do it for you.


If you need to access a server with the Kerberos SASL authentication mechanism you must install the *gssapi* or the *winkerberos* package with::

    pip install ldap3[gssapi]
    pip install ldap3[winkerberos]

ldap3 includes a backport (from Python 3.4.3) of ``ssl.check_hostnames`` to be used on older
(version < 2.7.10) Python version. If you want to use a more up to date version of the check_hostnames feature you can
install the *backports.ssl_check_hostnames* package that should be kept updated with the Standard Library of the latest
Python release by its maintainers.


Installation from the source
----------------------------

You can download the latest source from https://github.com/cannatag/ldap3 then you can install the library with::

    python -m build

Global configuration
--------------------

in the **ldap3.utils.config** package there are some configurable settings:

* POOLING_LOOP_TIMEOUT = 10  # number of seconds to wait before restarting a cycle to find an active server in the pool
* RESPONSE_SLEEPTIME = 0.05  # seconds to wait while waiting for a response in asynchronous strategies
* RESPONSE_WAITING_TIMEOUT = 3  # waiting timeout for receiving a response in asynchronous strategies
* SOCKET_SIZE = 4096  # socket byte size
* CHECK_AVAILABILITY_TIMEOUT = 2.5  # default timeout for socket connect when checking availability
* RESET_AVAILABILITY_TIMEOUT = 5  # default timeout for resetting the availability status when checking candidate addresses
* RESTARTABLE_SLEEPTIME = 2  # time to wait in a restartable strategy before retrying the request
* RESTARTABLE_TRIES = 3  # number of times to retry in a restartable strategy before giving up. Set to True for unlimited retries
* REUSABLE_THREADED_POOL_SIZE = 5
* REUSABLE_THREADED_LIFETIME = 3600  # 1 hour
* DEFAULT_THREADED_POOL_NAME = 'REUSABLE_DEFAULT_POOL'
* ADDRESS_INFO_REFRESH_TIME = 300  # seconds to wait before refreshing address info from dns
* ADDITIONAL_ENCODINGS = ['latin-1']  # some broken LDAP implementation may have different encoding than those expected by RFCs
* IGNORE_MALFORMED_SCHEMA = False  # some flaky LDAP servers returns malformed schema. If True no expection is raised and schema is thrown away


This parameters are library-wide and usually you should keep the default values.

You can use the ``get_config_parameter()`` and ``set_config_parameter()`` functions in the ldap3 namespace to get and set the configurable parameters at runtime.


Importing objects and constants
-------------------------------

All objects and constants needed to use the ldap3 library can be imported from the **ldap3** namespace::

    from ldap3 import Connection, Server, ANONYMOUS, SIMPLE, SYNC, ASYNC


Library errors
--------------

You can deal with errors in two different ways. By default in synchronous strategies each LDAP operation returns a
True/False value that specifies if the operation has been successful or not. In case of failures you can check the
error description in the ```last_error``` attribute of the Connection object. In some cases an exception of the custom
hierarchy starting from the ```LDAPExceptionError``` class is raised with a description of the error condition in the *args*
attribute.

If you prefer to deal always with Exceptions you can set the ``raise_exceptions`` attribute to ``True`` in the Connection
object definition. From now on the Connection will raise exceptions for all operations that return result codes
different from ``RESULT_SUCCESS``, ``RESULT_COMPARE_FALSE``, ``RESULT_COMPARE_TRUE``, ``RESULT_REFERRAL``.

Communication exceptions have multiple inheritance either from ```LDAPCommunicationError``` and the specific socket exception.

Exceptions are defined in the **ldap3.core.exceptions** package.
