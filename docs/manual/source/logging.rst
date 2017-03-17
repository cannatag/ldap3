Logging
#######

ldap3 has an extended logging capability that uses the standard Python logging libray and integrates with the logging
facility of the client application.

To enable logging the application must have a working logging configuration that emits logging at the DEBUG level::

    import logging
    logging.basicConfig(filename='client_application.log', level=logging.DEBUG)

This is intended to avoid the mix of ldap3 logging records in the application logging. Only one record is emitted at
INFO level regardless of the library log activation level::

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK

This is to inform that the logging facility is enabled and record will be emitted only when the loglevel and the detail
level are properly set. Only when you set the log level to DEBUG ldap3 starts to emit its log records.

Logging activation level
========================

You can change the ldap3 logging activation level to a different one if you need not to mix logging from ldap3 with DEBUG
level for your application::

    import logging
    logging.basicConfig(filename='client_application.log', level=logging.CRITICAL)
    from ldap3.utils.log import set_library_log_activation_level
    set_library_log_activation_level(logging.CRITICAL)  # ldap3 will emit its log only when you set level=logging.CRITICAL in your log configuration

ldap3 logging has its own level of log detail: OFF, ERROR, BASIC, PROTOCOL, NETWORK and EXTENDED. You can set the level
of detail with ldap3.utils.log.set_library_log_detail_level().

Detail level defaults to OFF. You must change it at runtime as needed to have anything logged::

    from ldap3.utils.log import set_library_log_detail_level, OFF, BASIC, NETWORK, EXTENDED
    # ... unlogged ldap3 operation
    set_library_log_detail_level(BASIC)
    # ... ldap3 operation with few details
    set_library_log_detail_level(EXTENDED)
    # ... other ldap3 operation with most details
    set_library_log_detail_level(OFF)
    # nothing else is logged

Logging detail level
====================

Each detail level details a specific feature of the library and includes the previous level details, as for standard
logging:

* NONE: nothing is logged

* ERROR: only exceptions are logged

* BASIC: library activity is logged, only operation result is shown

* PROTOCOL: LDAPv3 operations are logged, sent requests and received responses are shown

* NETWORK: socket activity is logged

* EXTENDED: ldap messages are decoded and properly printed

At EXTENDED level every LDAP message is logged and printed in a proper way (thanks to pyasn1 prettyPrint feature).
The flow of the network conversation can be easily guessed by the prefix of the message lines: >> for outgoing messages
(to the LDAP server) and << for incoming messages (from the LDAP server). To get a full descriptive logging of outgoing
messages you must set ``fast_decoder=False`` in the connection object.

Each log record contains the detail level and when available information on the active connection used. So the log size grows very easily.
ldap3 performance degrades when logging is active, especially at level greater than ERROR, so it's better to use it only when needed.

logging text is encoded to ASCII.


Hiding sensitive data
=====================

Sensitive data (as user password and SASL credentials) are stripped by default from the log and substituted with a string
of '*' (with the same length of the original value) or by a "<stripped xxx characters of sensitive data>" message (where xxx is the
number of characters stripped). You can change the default behaviour and let the log record all the data with the
set_library_log_hide_sensitive_data(False) function of the utils.log package::

    import logging
    logging.basicConfig(filename=log_file, level=logging.DEBUG)
    from ldap3.utils.log import set_library_log_detail_level, get_detail_level_name, set_library_log_hide_sensitive_data, EXTENDED

    set_library_log_detail_level(EXTENDED)
    set_library_log_hide_sensitive_data(False)

You can use the get_library_log_hide_sensitive_data() function of the utils.log module to check if sensitive data will
be hidden or not.


Maximum log line length
=======================
When logging LDAP responses at the EXTENDED detail level is possible to receive very long lines. This usually happens
when the schema is read with get_info=SCHEMA or get_info=ALL in the Server object. A tipical response while reading the
schema can be 300 KB (or more) long.

To avoid the creation of huge and usually useless logs the ldap3 library log system set the maximum length of the log lines
to a default value of 4096 characters. This should be a reasonable value for logging search operation responses, without
cluttering the log. If you want to change the maximum log line length to another value you can use the
set_library_log_max_line_length(length) function to set the desired length. You can use the get_library_log_max_line_length()
function to read the current value.


Examples
========

Opening an SSL connection to an LDAP server listening on IPv4 only on a IPv6/IPv4 box. The connection mode is set to IP_V6_PREFERRED, the connection is bound and a search operation is performed

a search operation at basic level::

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED - sensitive data will be hidden
    DEBUG:ldap3:ERROR:detail level set to BASIC
    DEBUG:ldap3:BASIC:instantiated Tls: <Tls(validate=0)>
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=636, use_ssl=True, tls=Tls(validate=0), get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=636, use_ssl=True, tls=Tls(validate=0), get_info='NO_INFO'), user='cn=admin,o=test', password='********', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:BASIC:start BIND operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:reset usage metrics
    DEBUG:ldap3:BASIC:start collecting usage metrics
    DEBUG:ldap3:BASIC:address for <ldaps://openldap:636 - ssl> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]>
    DEBUG:ldap3:BASIC:address for <ldaps://openldap:636 - ssl> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldaps://openldap:636 - ssl>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldaps://openldap:636 - ssl>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it> for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <local: [::]:50122 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]
    DEBUG:ldap3:BASIC:refreshing server info for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50123 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <True>
    DEBUG:ldap3:BASIC:start SEARCH operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50123 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done SEARCH operation, result <True>
    DEBUG:ldap3:BASIC:start UNBIND operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50123 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>


the same operation at PROTOCOL detail level::

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED - sensitive data will be hidden
    DEBUG:ldap3:ERROR:detail level set to PROTOCOL
    DEBUG:ldap3:BASIC:instantiated Tls: <Tls(validate=0)>
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=636, use_ssl=True, tls=Tls(validate=0), get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=636, use_ssl=True, tls=Tls(validate=0), get_info='NO_INFO'), user='cn=admin,o=test', password='********', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:BASIC:start BIND operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:reset usage metrics
    DEBUG:ldap3:BASIC:start collecting usage metrics
    DEBUG:ldap3:BASIC:address for <ldaps://openldap:636 - ssl> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]>
    DEBUG:ldap3:BASIC:address for <ldaps://openldap:636 - ssl> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldaps://openldap:636 - ssl>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldaps://openldap:636 - ssl>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it.> for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <local: [::]:50127 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]
    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'version': 3, 'authentication': {'sasl': None, 'simple': '<stripped 8 characters of sensitive data>'}, 'name': 'cn=admin,o=test'}> sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:PROTOCOL:BIND response <{'result': 0, 'saslCreds': None, 'type': 'bindResponse', 'message': '', 'referrals': None, 'dn': '', 'description': 'success'}> received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <True>
    DEBUG:ldap3:BASIC:start SEARCH operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:SEARCH request <{'sizeLimit': 0, 'scope': 2, 'timeLimit': 0, 'typesOnly': False, 'filter': '(cn=test*)', 'attributes': ['objectClass', 'sn'], 'base': 'o=test', 'dereferenceAlias': 3}> sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:PROTOCOL:SEARCH response entry <{'type': 'searchResEntry', 'dn': 'cn=testSASL,o=test', 'attributes': {'objectClass': ['inetOrgPerson', 'organizationalPerson', 'person', 'top'], 'sn': ['testSASL']}, 'raw_attributes': {'objectClass': [b'inetOrgPerson', b'organizationalPerson', b'person', b'top'], 'sn': [b'testSASL']}}> received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done SEARCH operation, result <True>
    DEBUG:ldap3:BASIC:start UNBIND operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50128 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <3> generated
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>


the same opeaton at NETWORK detail level::

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED - sensitive data will be hidden
    DEBUG:ldap3:ERROR:detail level set to NETWORK
    DEBUG:ldap3:BASIC:instantiated Tls: <Tls(validate=0)>
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=636, use_ssl=True, tls=Tls(validate=0), get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=636, use_ssl=True, tls=Tls(validate=0), get_info='NO_INFO'), user='cn=admin,o=test', password='********', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:BASIC:start BIND operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:opening connection for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:reset usage metrics
    DEBUG:ldap3:BASIC:start collecting usage metrics
    DEBUG:ldap3:BASIC:address for <ldaps://openldap:636 - ssl> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]>
    DEBUG:ldap3:BASIC:address for <ldaps://openldap:636 - ssl> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldaps://openldap:636 - ssl>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldaps://openldap:636 - ssl>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it> for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <local: [::]:50130 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]
    DEBUG:ldap3:NETWORK:socket wrapped with SSL using SSLContext for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <local: [None]:None - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection open for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'version': 3, 'authentication': {'sasl': None, 'simple': '<stripped 8 characters of sensitive data>'}, 'name': 'cn=admin,o=test'}> sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:sent 37 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:BIND response <{'description': 'success', 'referrals': None, 'result': 0, 'type': 'bindResponse', 'message': '', 'saslCreds': None, 'dn': ''}> received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <True>
    DEBUG:ldap3:BASIC:start SEARCH operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:SEARCH request <{'attributes': ['objectClass', 'sn'], 'base': 'o=test', 'scope': 2, 'dereferenceAlias': 3, 'filter': '(cn=test*)', 'typesOnly': False, 'sizeLimit': 0, 'timeLimit': 0}> sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:sent 63 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 114 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:SEARCH response entry <{'raw_attributes': {'sn': [b'testSASL'], 'objectClass': [b'inetOrgPerson', b'organizationalPerson', b'person', b'top']}, 'attributes': {'sn': ['testSASL'], 'objectClass': ['inetOrgPerson', 'organizationalPerson', 'person', 'top']}, 'type': 'searchResEntry', 'dn': 'cn=testSASL,o=test'}> received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done SEARCH operation, result <True>
    DEBUG:ldap3:BASIC:start UNBIND operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <3> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:sent 7 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:closing connection for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50131 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection closed for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>


the same operation at EXTENDED detail level::

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED - sensitive data will be hidden
    DEBUG:ldap3:ERROR:detail level set to EXTENDED
    DEBUG:ldap3:BASIC:instantiated Tls: <Tls(validate=0)>
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=636, use_ssl=True, tls=Tls(validate=0), get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=636, use_ssl=True, tls=Tls(validate=0), get_info='NO_INFO'), user='cn=admin,o=test', password='********', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:BASIC:start BIND operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:opening connection for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:reset usage metrics
    DEBUG:ldap3:BASIC:start collecting usage metrics
    DEBUG:ldap3:BASIC:address for <ldaps://openldap:636 - ssl> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]>
    DEBUG:ldap3:BASIC:address for <ldaps://openldap:636 - ssl> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldaps://openldap:636 - ssl>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldaps://openldap:636 - ssl>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 636, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] Impossibile stabilire la connessione. Rifiuto persistente del computer di destinazione> for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <local: [::]:50132 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 636)]
    DEBUG:ldap3:NETWORK:socket wrapped with SSL using SSLContext for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <local: [None]:None - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection open for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'authentication': {'sasl': None, 'simple': '<stripped 8 characters of sensitive data>'}, 'name': 'cn=admin,o=test', 'version': 3}> sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=1
    >> protocolOp=ProtocolOp:
    >>  bindRequest=BindRequest:
    >>   version=3
    >>   name=b'cn=admin,o=test'
    >>   authentication=AuthenticationChoice:
    >>    simple=<stripped 8 characters of sensitive data>
    DEBUG:ldap3:NETWORK:sent 37 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=1
    << protocolOp=ProtocolOp:
    <<  bindResponse=BindResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:BIND response <{'dn': '', 'description': 'success', 'type': 'bindResponse', 'message': '', 'result': 0, 'saslCreds': None, 'referrals': None}> received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <True>
    DEBUG:ldap3:BASIC:start SEARCH operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:SEARCH request <{'scope': 2, 'base': 'o=test', 'timeLimit': 0, 'filter': '(cn=test*)', 'typesOnly': False, 'attributes': ['objectClass', 'sn'], 'dereferenceAlias': 3, 'sizeLimit': 0}> sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=2
    >> protocolOp=ProtocolOp:
    >>  searchRequest=SearchRequest:
    >>   baseObject=b'o=test'
    >>   scope='wholeSubtree'
    >>   derefAliases='derefAlways'
    >>   sizeLimit=0
    >>   timeLimit=0
    >>   typesOnly='False'
    >>   filter=Filter:
    >>    substringFilter=SubstringFilter:
    >>     type=b'cn'
    >>     substrings=Substrings:
    >>      Substring:
    >>       initial=b'test'
    >>   attributes=AttributeSelection:
    >>    b'objectClass'    b'sn'
    DEBUG:ldap3:NETWORK:sent 63 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 114 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  searchResEntry=SearchResultEntry:
    <<   object=b'cn=testSASL,o=test'
    <<   attributes=PartialAttributeList:
    <<    PartialAttribute:
    <<     type=b'sn'
    <<     vals=Vals:
    <<      b'testSASL'
    <<    PartialAttribute:
    <<     type=b'objectClass'
    <<     vals=Vals:
    <<      b'inetOrgPerson'      b'organizationalPerson'      b'person'      b'top'
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  searchResDone=SearchResultDone:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:SEARCH response entry <{'attributes': {'sn': ['testSASL'], 'objectClass': ['inetOrgPerson', 'organizationalPerson', 'person', 'top']}, 'dn': 'cn=testSASL,o=test', 'type': 'searchResEntry', 'raw_attributes': {'sn': [b'testSASL'], 'objectClass': [b'inetOrgPerson', b'organizationalPerson', b'person', b'top']}}> received via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done SEARCH operation, result <True>
    DEBUG:ldap3:BASIC:start UNBIND operation via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <3> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sending via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=3
    >> protocolOp=ProtocolOp:
    >>  unbindRequest=b''
    DEBUG:ldap3:NETWORK:sent 7 bytes via <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:closing connection for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50133 - remote: 192.168.137.104:636> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection closed for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - bound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>

At the ERROR detail level you get only the library errors:

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED - sensitive data will be hidden
    DEBUG:ldap3:ERROR:detail level set to ERROR
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it.> for <ldaps://openldap:636 - ssl - user: cn=admin,o=test - unbound - closed - <local: [::]:50321 - remote: [None]:None> - tls not started - not listening - SyncStrategy>

The usage metrics are the same at every detail:

    Connection Usage:
      Time: [elapsed:        0:00:01.949587]
        Initial start time:  2015-05-18T19:27:17.057422
        Open socket time:    2015-05-18T19:27:17.057422
        Close socket time:   2015-05-18T19:27:19.007009
      Server:
        Servers from pool:   0
        Sockets open:        1
        Sockets closed:      1
        Sockets wrapped:     1
      Bytes:                 249
        Transmitted:         107
        Received:            142
      Messages:              6
        Transmitted:         3
        Received:            3
      Operations:            3
        Abandon:             0
        Bind:                1
        Add                  0
        Compare:             0
        Delete:              0
        Extended:            0
        Modify:              0
        ModifyDn:            0
        Search:              1
        Unbind:              1
      Referrals:
        Received:            0
        Followed:            0
      Restartable tries:     0
        Failed restarts:     0
        Successful restarts: 0
