ldap3 Features
##############

1. ldap3 strictly conforms to the current RFCs for the version 3 of the LDAP protocol (from 4510 to 4519):

    * The **Latest RFCs for LDAP v3** (dated 2006) obsolete the previous RFCs specified in RFC3377 (2251-2256, 2829, 2830, 3371) for LDAP v3 and amend and clarify the LDAP protocol.

    * All the ASN1 definitions are written from scratch to be current with RFC 4511.

2. Platform independent (tested on Linux and Windows) architecture:

    * The library **runs on Windows, Linux and Mac OSX** and (possibly) on other systems where it can gain access to the network via a Python
      interpreter without any difference.

3. Based on **pure Python code**:

    * No need to install binaries or non Python code. The very same code works on Windows, Linux, Mac OS X, FreeBSD,
      OpenBSD and other systems, either in Python 2 or Python 3.

    * ldap3 **doesn't need a C compiler neither the openldap client library**

    * The library is self-contained and its installation is the same on any platform.

    * Socket and thread programming is appropriate for the platform used, with no changes needed in the configuration and in the exposed API.

    * The ldap3 library depends on the standard Python library and the pyasn1 package only. If you need kerberos support you must install the gssapi package

4. Compatible with Python 3 and Python 2:

    * A **single codebase** for Python 2 and Python 3

    * Development is done in **Python 3 native code**

    * The library is **compatible with Python 2** (2.6 and 2.7)

    * Testing is done in Python 3 (3.4) Python 2 (2.6, 2.7), PyPy and PyPy3

    * Unicode strings are properly managed.

5. Multiple *connection strategies* to choose from, either synchronous or asynchronous:

    * The library has different ways to connect to the LDAP server (no-thread, single-threaded, multithreaded).
      This is achieved with **pluggable communication strategies** that can be changed on a per-connection basis.

    * SYNC, ASYNC, LDIF, REUSABLE, RESTARTABLE are currently defined.

6. Simplified query construction language:

    * The library includes an  **abstraction layer** for performing LDAP queries.
