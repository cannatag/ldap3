The DELETE operation
####################

The **Delete** operation allows a client to request the removal of an entry from the LDAP directory.

To perform a Delete operation you must specify the dn of the entry.

In the ldap3 library the signature for the Delete operation is::

    def delete(self,
               dn,
               controls=None):

* dn: distinguished name of the object to delete

* controls: additional controls to send with the request

For synchronous strategies the delete method returns True if the operation was successful, returns False in case of errors.
In this case you can inspect the result attribute of the connection object to get the error description.

For asynchronous strategies the add method returns the message id of the operation. You can get the operation result with
the ``get_response(message_id)`` method of the connection object. If you use the ``get_request=True`` parameter you get the request dictionary back.

Only leaf entries (those with no subordinate entries) can be deleted with this operation.

You perform a Delete operation as in the following example (using the default synchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform the Delete operation
    c.delete('cn=user1,ou=users,o=company')
    print(c.result)

    # close the connection
    c.unbind()

Extended logging
----------------

To get an idea of what's happening when you perform a Delete operation this is the extended log from a session to an OpenLdap
server from a Windows client with dual stack IP::

    # Initialization:

    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED
    DEBUG:ldap3:ERROR:detail level set to EXTENDED
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO'), user='cn=admin,o=test', password='<stripped 8 characters of sensitive data>', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:NETWORK:opening connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
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
    DEBUG:ldap3:NETWORK:connection open for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>


    # Authenticating to the LDAP server with the Simple Bind method:

    DEBUG:ldap3:BASIC:start BIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'name': 'cn=admin,o=test', 'version': 3, 'authentication': {'sasl': None, 'simple': '<stripped 8 characters of sensitive data>'}}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=1
    >> protocolOp=ProtocolOp:
    >>  bindRequest=BindRequest:
    >>   version=3
    >>   name=b'cn=admin,o=test'
    >>   authentication=AuthenticationChoice:
    >>    simple=b'<stripped 8 characters of sensitive data>'
    DEBUG:ldap3:NETWORK:sent 37 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=1
    << protocolOp=ProtocolOp:
    <<  bindResponse=BindResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:BIND response <{'type': 'bindResponse', 'dn': '', 'saslCreds': None, 'result': 0, 'referrals': None, 'message': '', 'description': 'success'}> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <True>

    # Performing the Delete operation:

    DEBUG:ldap3:BASIC:start DELETE operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:DELETE request <{'entry': 'cn=user1,o=test'}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=2
    >> protocolOp=ProtocolOp:
    >>  delRequest=b'cn=user1,o=test'
    DEBUG:ldap3:NETWORK:sent 22 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  delResponse=DelResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:DELETE response <[{'type': 'delResponse', 'dn': '', 'result': 0, 'referrals': None, 'message': '', 'description': 'success'}]> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done DELETE operation, result <True>


    # Closing the connnection (via the Unbind operation):

    DEBUG:ldap3:BASIC:start UNBIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <3> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=3
    >> protocolOp=ProtocolOp:
    >>  unbindRequest=b''
    DEBUG:ldap3:NETWORK:sent 7 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:closing connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:50024 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection closed for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>


These are the usage metrics of this session::

    Connection Usage:
      Time: [elapsed:        0:00:01.387729]
        Initial start time:  2015-06-06T08:19:25.843569
        Open socket time:    2015-06-06T08:19:25.843569
        Close socket time:   2015-06-06T08:19:27.231298
      Server:
        Servers from pool:   0
        Sockets open:        1
        Sockets closed:      1
        Sockets wrapped:     0
      Bytes:                 94
        Transmitted:         66
        Received:            28
      Messages:              5
        Transmitted:         3
        Received:            2
      Operations:            3
        Abandon:             0
        Bind:                1
        Add:                 0
        Compare:             0
        Delete:              1
        Extended:            0
        Modify:              0
        ModifyDn:            0
        Search:              0
        Unbind:              1
      Referrals:
        Received:            0
        Followed:            0
      Restartable tries:     0
        Failed restarts:     0
        Successful restarts: 0
