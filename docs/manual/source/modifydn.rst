#######################
The MODIFY-DN operation
#######################

The **ModifyDN** operation allows a client to change the Relative Distinguished Name (RDN) or to move an entry in the LDAP directory.

ModifyDN is really a two-flavours operation: you can rename the last part of the dn *or* you move the entry
in another container but you cannot perform both operations at the same time.

To perform a ModifyDN operation you must specify the dn of the entry and the new relative dn requested.

In the ldap3 library the signature for the Delete operation is::

    def modify_dn(self,
                  dn,
                  relative_dn,
                  delete_old_dn=True,
                  new_superior=None,
                  controls=None)


* dn: distinguished name of the entry whose relative name must be modified

* relative_dn: new relative dn of the entry

* delete_old_dn: remove the previous dn (defaults to True)

* new_superior: the new container of the entry

* controls: additional controls to send in the request


For synchronous strategies the modify_dn method returns True if the operation was successful, returns False in case of errors.
In this case you can inspect the result attribute of the connection object to get the error description.

For asynchronous strategies the modify_dn method returns the message id of the operation. You can get the operation result with
the get_response(message_id) method of the connection object.

You can rename an entry with a ModifyDN operation as in the following example (using the default synchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform the ModifyDN operation to rename an entry
    c.modify_dn('cn=user1,ou=users,o=company', 'cn=user2')
    print(c.result)

    # perform the ModifyDN operation to move an entry
    c.modify_dn('cn=user2,ou=users,o=company', 'cn=user2', new_superior='ou=admins,o=company')

    print(c.result)

    # close the connection
    c.unbind()



Extended logging
----------------

To get an idea of what's happening when you perform a ModifyDn operation this is the extended log from a session to an OpenLdap
server from a Windows client with dual stack IP. AFter binding a rename is performed and then the entry is moved::

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
    DEBUG:ldap3:NETWORK:connection open for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:start BIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>


    # Authenticating to the LDAP server with the Simple Bind method:

    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'authentication': {'sasl': None, 'simple': '<stripped 8 characters of sensitive data>'}, 'version': 3, 'name': 'cn=admin,o=test'}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=1
    >> protocolOp=ProtocolOp:
    >>  bindRequest=BindRequest:
    >>   version=3
    >>   name=b'cn=admin,o=test'
    >>   authentication=AuthenticationChoice:
    >>    simple=b'<stripped 8 characters of sensitive data>'
    DEBUG:ldap3:NETWORK:sent 37 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=1
    << protocolOp=ProtocolOp:
    <<  bindResponse=BindResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:BIND response <{'type': 'bindResponse', 'dn': '', 'referrals': None, 'saslCreds': None, 'message': '', 'result': 0, 'description': 'success'}> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <True>


    # Starting the ModifyDN operation to perform a rename

    DEBUG:ldap3:BASIC:start MODIFY DN operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:MODIFY DN request <{'newRdn': 'cn=user2', 'deleteOldRdn': True, 'entry': 'cn=user1,o=test', 'newSuperior': None}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=2
    >> protocolOp=ProtocolOp:
    >>  modDNRequest=ModifyDNRequest:
    >>   entry=b'cn=user1,o=test'
    >>   newrdn=b'cn=user2'
    >>   deleteoldrdn='True'
    DEBUG:ldap3:NETWORK:sent 37 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  modDNResponse=ModifyDNResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:MODIFY DN response <[{'type': 'modDNResponse', 'dn': '', 'referrals': None, 'message': '', 'result': 0, 'description': 'success'}]> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done MODIFY DN operation, result <True>


    # Starting the ModifyDN operation to perform a move

    DEBUG:ldap3:BASIC:start MODIFY DN operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:MODIFY DN request <{'newRdn': 'cn=user2', 'deleteOldRdn': True, 'entry': 'cn=user2,o=test', 'newSuperior': 'ou=moved,o=test'}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <3> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=3
    >> protocolOp=ProtocolOp:
    >>  modDNRequest=ModifyDNRequest:
    >>   entry=b'cn=user2,o=test'
    >>   newrdn=b'cn=user2'
    >>   deleteoldrdn='True'
    >>   newSuperior=b'ou=moved,o=test'
    DEBUG:ldap3:NETWORK:sent 54 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=3
    << protocolOp=ProtocolOp:
    <<  modDNResponse=ModifyDNResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:MODIFY DN response <[{'type': 'modDNResponse', 'dn': '', 'referrals': None, 'message': '', 'result': 0, 'description': 'success'}]> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done MODIFY DN operation, result <True>


    # Closing the connnection (via the Unbind operation):

    DEBUG:ldap3:BASIC:start UNBIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <4> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=4
    >> protocolOp=ProtocolOp:
    >>  unbindRequest=b''
    DEBUG:ldap3:NETWORK:sent 7 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:closing connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:53484 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection closed for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>


These are the usage metrics of this session::

    Connection Usage:
      Time: [elapsed:        0:00:18.903383]
        Initial start time:  2015-06-11T22:03:36.180931
        Open socket time:    2015-06-11T22:03:36.180931
        Close socket time:   2015-06-11T22:03:55.084314
      Server:
        Servers from pool:   0
        Sockets open:        1
        Sockets closed:      1
        Sockets wrapped:     0
      Bytes:                 177
        Transmitted:         135
        Received:            42
      Messages:              7
        Transmitted:         4
        Received:            3
      Operations:            4
        Abandon:             0
        Bind:                1
        Add:                 0
        Compare:             0
        Delete:              0
        Extended:            0
        Modify:              0
        ModifyDn:            2
        Search:              0
        Unbind:              1
      Referrals:
        Received:            0
        Followed:            0
      Restartable tries:     0
        Failed restarts:     0
