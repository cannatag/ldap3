############
Installation
############

Installation is very straightforward, you need "setuptools" and "pip" to install python3-ldap (or any other package manager that can download and install from pypi).
Then you can download the python3-ldap library directly from pypi::

    pip install python3-ldap

This library has only one dependence on the pyasn1 module, you don't need the pyasn1_modules package, you can install it or let the installer do it for you.

If you have downloaded the source you can build the library running in the unzipped source directory with::

    python setup.py install
