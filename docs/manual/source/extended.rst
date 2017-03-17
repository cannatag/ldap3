The EXTENDED operation
######################

The **Extended** operation allows a client to request an operation that may not be defined in the current RFCs but is available on the server.

To perform a Compare operation you must specify the *name* of the extended operation (defined with an OID) and the value to be sent.

In the ldap3 library the signature for the Extended operation is::

    def extended(self,
                 request_name,
                 request_value=None,
                 controls=None,
                 no_encode=None)

    * request_name: name of the extended operation

    * request_value: optional value sent in the request (defaults to None)

    * controls: additional controls to send in the request

    * no_encode: when True the value is passed without any encoding (defaults to False)


Some common extended operation are defined in the Connection.extend namespace.

You perform an Extended operation as in the following example (using the default synchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform the Extended operation
    result = c.extended('0.1.2.3', 'my_value')
    print(result)

    # close the connection
    c.unbind()


Extended logging
----------------

To get an idea of what happens when you perform an Extended operation this is the extended log from a session to an OpenLdap
server from a Windows client with dual stack IP::

    # Initialization:

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED - sensitive data will be hidden
    DEBUG:ldap3:ERROR:detail level set to EXTENDED
    DEBUG:ldap3:ERROR:hide sensitive data set to True
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO'), user='cn=admin,o=services', password='<stripped 8 characters of sensitive data>', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:NETWORK:opening connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:reset usage metrics
    DEBUG:ldap3:BASIC:start collecting usage metrics
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]>
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]> with mode IP_V6_PREFERRED


    # Opening the connection (trying IPv6 then IPv4):

    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it.> for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <local: [::]:50396 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]
    DEBUG:ldap3:NETWORK:connection open for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>


    # Authenticating to the LDAP server with the Simple Bind method:

    DEBUG:ldap3:BASIC:start BIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'name': 'cn=admin,o=services', 'authentication': {'sasl': None, 'simple': '<stripped 8 characters of sensitive data>'}, 'version': 3}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=1
    >> protocolOp=ProtocolOp:
    >>  bindRequest=BindRequest:
    >>   version=3
    >>   name=b'cn=admin,o=services'
    >>   authentication=AuthenticationChoice:
    >>    simple=<stripped 8 characters of sensitive data>
    DEBUG:ldap3:NETWORK:sent 41 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=1
    << protocolOp=ProtocolOp:
    <<  bindResponse=BindResponse:
    <<   resultCode='invalidCredentials'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:BIND response <{'description': 'invalidCredentials', 'message': '', 'type': 'bindResponse', 'saslCreds': None, 'result': 49, 'dn': '', 'referrals': None}> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <False>


    # Performing the Extended operation:

    TODO

    # Closing the connnection (via the Unbind operation):

    DEBUG:ldap3:BASIC:start UNBIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <3> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=3
    >> protocolOp=ProtocolOp:
    >>  unbindRequest=b''
    DEBUG:ldap3:NETWORK:sent 7 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:closing connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection closed for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>



These are the usage metrics of this session::

    TODO
