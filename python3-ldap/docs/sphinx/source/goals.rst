#############
Project goals
#############

1. Python3-ldap Conforms strictly to the current RFC for LDAP 3 (from rfc4510 to rfc4519)

    - Latest RFCs for LDAP v3 (dated 2006) obsolete the previous RFCs specified in rfc3377 (2251-2256, 2829, 2830, 3371) for LDAP v3 and amend and clarify the LDAP protocol.

    - All the asn1 definitions from the rfc4511 must be rewritten because those in the pyasn1_modules package are not current with the RFC.

2. Platform independent (tested on Linux and Windows) architecture

    - The library should run on Windows and Linux and (possibly) other Unixes with no differences.

3. Based only on pure Python code

    - I usually work on Linux and Windows boxes and each time I must install the current python-ldap library for Python2 from different sources.

    - python3-ldap should be directly installed from source of from pypi using pip or a similar package manager on different platforms.

    - Installation should be the same on any platform.

    - Socket and thread programming should be appropriate for the platform used, with no changes needed in the configuration.

    - python3-ldap library should depend on the standard library and the pyasn1 package only.

4. Compatible with python3 and python2

    - Development and testing is done in Python 3, but as the library should (hopefully) be compatible with Python 2.

    - Unicode strings are appropriately converted.

5. Multiple *connection strategies* to choose from, either synchronous or asynchronous

    - I'm planning to use different ways to connect to the LDAP server (no thread, single threaded, multithreaded, event...)

    - I'm not sure about which connection strategy is the best to use on LDAP  messages communication, so I'm writing a Connection object with a **pluggable** socket connection Strategy.

    - "SyncWaitStrategy", "AsyncThreadedStrategy" and "LdifProducerStrategy" are defined.

6. Semplified query construction language

    - For a different project I developed an "abstraction layer" for LDAP query. I'd like to have a generalized LDAP abstraction layer to semplify access to the DIT.

7. Compatibility mode for application using python-ldap

    - I have a number of projects using the python-ldap library. I'd like to move them to Python3 without changing what I've already done for LDAP.

    - It should be (ideally) enough just to change the import from python-ldap to python3-ldap to use them on Python3, at least for the LDAP part.
