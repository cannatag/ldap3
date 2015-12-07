ldap3 Features
##############

1. ldap3 strictly conforms to the current RFCs for the version 3 of the LDAP protocol (from 4510 to 4519):

    * RFC4510: Technical Specification Road Map
    * RFC4511: The Protocol
    * RFC4512: Directory Information Models
    * RFC4513: Authentication Methods and Security Mechanisms
    * RFC4514: String Representation of Distinguished Names
    * RFC4515: String Representation of Search Filters
    * RFC4516: Uniform Resource Locator
    * RFC4517: Syntaxes and Matching Rules
    * RFC4518: Internationalized String Preparation
    * RFC4519: Schema for User Applications

    The following RFCs, describing additional functionalities of the LDAP3 protocol, are also followed:

    * RFC2696: LDAP Control Extension for Simple Paged Results Manipulation
    * RFC2849: The LDAP Data Interchange Format (LDIF) - Technical Specification
    * RFC3045: Storing Vendor Information in the LDAP root DSE
    * RFC3062: LDAP Password Modify Extended Operation
    * RFC4525: Modify-Increment Extension
    * RFC4530: entryUUID Operational Attribute
    * RFC4532: "Who am I?" Operation
    * RFC5020: entryDN Operational Attribute


2. Platform independent (tested on Linux and Windows) architecture:

    * The library **runs on Windows, Linux, FreeBSD, OpenBSD, and Mac OSX** and (possibly) on other systems where it can
      gain access to the network via a Python interpreter and its Standard Library.

3. Based on **pure Python code**:

    * No need to install binaries or non Python code. The very same code works on Windows, Linux, Mac OS X, FreeBSD,
      OpenBSD and other systems, either in Python 2 or Python 3.

    * ldap3 **doesn't need a C compiler neither the OpenLDAP library**.

    * The library is self-contained and its installation is the same on any platform.

    * Socket and thread programming is appropriate for the platform used, with no changes needed in the configuration
      and in the exposed API.

    * The ldap3 library depends on the standard Python library and the pyasn1 package only. If you need Kerberos support
      you must install the *gssapi* package. ldap3 includes a backport (from Python 3.4.3) of ```ssl.check_hostnames``` to be
      used on older (version < 2.7.10) Python versions. If you want to use a more up to date version of the check_hostnames
      feature you can install the *backports.ssl_check_hostnames* package that should be kept updated with the Standard
      Library of the latest Python release by its maintainers.

4. Compatible with Python 2 and Python 3:

    * A **single codebase** for Python 2 and Python 3

    * Developed in **Python 3 native code** that works in Python 2 too.

    * The library is **compatible with Python 2** (2.6 and 2.7) without the need of any code compatibility parser/converter.

    * Testing is done in Python 3 (3.4, 3.5) Python 2 (2.6, 2.7), PyPy and PyPy3

    * Unicode strings are properly managed in each Python version.

5. Multiple *connection strategies* to choose from, either synchronous or asynchronous:

    * The library has different ways to connect to the LDAP server (no-thread, single-threaded, multi-threaded).
      This is achieved with **pluggable communication strategies** that can be changed on a per-connection basis.

    * SYNC, ASYNC, LDIF, RESTARTABLE (fault-tolerant), REUSABLE (fault-tolerant and pooled), are currently defined.

6. Simplified query construction language:

    * The library includes an  optional **abstraction layer** for performing LDAP queries.

7. Clear or secured access

    * ldap3 allows plaintext (**ldap:**), secure (**ldaps:**) and UNIX socket (**ldapi:**) access to the LDAP server.

    * The NTLM access method is available to connect to Active Directory servers
