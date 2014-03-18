#############
Project goals
#############

1. python3-ldap strictly conforms to the current RFCs for LDAP version 3 (from 4510 to 4519)

    - Latest RFCs for LDAP v3 (dated 2006) obsolete the previous RFCs specified in RFC3377 (2251-2256, 2829, 2830, 3371) for LDAP v3 and amend and clarify the LDAP protocol.

    - All the asn1 definitions from the RFC4511 have been rewritten because those in the pyasn1_modules package are not current with the RFC.

2. Platform independent (tested on Linux and Windows) architecture

    - The library should run on Windows and Linux and (possibly) other Unixes with any difference.

3. Based on pure Python code

    - I usually work on Linux and Windows boxes and each time I must install the current python-ldap library for Python 2 from different sources.

    - python3-ldap should be easily installed from source of from pypi using pip or a similar package manager on different platforms.

    - Installation should be the same on any platform.

    - Socket and thread programming should be appropriate for the platform used, with no changes needed in the configuration and in the exposed API..

    - python3-ldap library should depend on the standard library and the pyasn1 package only.

4. Compatible with Python 3 and Python 2

    - Development is done in Python 3, but the library should (hopefully) be compatible with Python 2.

    - Testing is done on Python3 and Python 2 (2.6, 2.7)

    - Unicode strings are appropriately managed in Python3. In Python 2 bytes (str object) are used

5. Multiple *connection strategies* to choose from, either synchronous or asynchronous

    - I'm planning to use different ways to connect to the LDAP server (no-thread, single-threaded, multithreaded, event...)

    - The socket connection strategy is **pluggable** and can be changed on a per-connection basis.

    - "SyncWaitStrategy", "AsyncThreadedStrategy", "LdifProducerStrategy" and "SyncRestartableStrategy" are currently defined.

6. Semplified query construction language

    - I previuosly developed an *abstraction layer* for LDAP query. I'd like to have a generalized LDAP abstraction layer to semplify access to the LDAP data..

7. Compatibility mode for application using python-ldap

    - I have a number of projects using the python-ldap library. I'd like to move them to Python 3 without changing what I've already done for LDAP.

    - It should be (possibly) enough just to change the import from python-ldap to python3-ldap to use them on Python 3, at least for the LDAP part.
