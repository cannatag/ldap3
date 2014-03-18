############
Installation
############

Installation is very straightforward, you need "setuptools" and "pip" to install python3-ldap (or any other package manager that can download and install from pypi).
Then you can download the python3-ldap library directly from pypi::

    pip install python3-ldap

This library has only one dependence on the pyasn1 module, you don't need the pyasn1_modules package, you can install it or let the installer do it for you.

If you have downloaded the source you can build the library running in the unzipped source directory with::

    python setup.py install


Global configuration
====================

in the *ldap3/__init__.py* that should have been created in the site-packages folder there are some configurable settings:

* RESPONSE_SLEEPTIME = 0.02  # seconds to wait while waiting for a response in asynchronous strategies
* RESPONSE_WAITING_TIMEOUT = 1  # waiting timeout for receiving a response in asynchronous strategies
* SOCKET_SIZE = 4096  # socket byte size
* RESTARTABLE_SLEEPTIME = 2  # time to wait in a restartable strategy before retrying the request
* RESTARTABLE_TRIES = 50  # number of times to retry in a restartable strategy before giving up. Set to True for unlimited retries

Usually you can keep the default values.
