####################
The MODIFY operation
####################

The **Modify** operation allows a client to request the modification of an entry already present in the LDAP directory.

To perform a Modify operation you must specify the dn of the entry and the kind of changes requested.

In the ldap3 library the signature for the Modify operation is::

    def modify(self,
               dn,
               changes,
               controls=None):


* dn: distinguished name of the object whose attributes must be modified

* changes: a dictionary of changes to be performed on the specified entry

* controls: additional controls to send in the request

* dn: distinguish name of the object to delete

* controls: additional controls to send with the request

For synchronous strategies the modify method returns True if the operation was successful, returns False in case of errors.
In this case you can inspect the result attribute of the connection object to get the error description.

For asynchronous strategies the modify method returns the message id of the operation. You can get the operation result with
the get_response(message_id) method of the connection object.

There are 4 different kinds of change:

* MODIFY_ADD: add values listed to the specified attribute, creating the attribute if necessary.

* MODIFY_DELETE: delete values listed from the attribute. If no values are listed, or if all current values of the attribute are listed,
  the entire attribute is removed.

* MODIFY_REPLACE: replace all existing values of the specified attribute with the new values listed, creating the attribute if it did not already exist.  A replace with no values will delete the entire attribute if it exists, and it is ignored if the attribute does not exist.

* MODIFY_INCREMENT: All existing values of the specified attribute are to be incremented by the listed value. The attribute must be appropriate for the request (e.g., it must have INTEGER or other increment-able values), and the modification must provide one and only one value. (RFC4525)

changes is a dictionary in the form {'attribute1': [(operation, [val1, val2, ...], (operation2, [val1, val2, ...]), ...], 'attribute2': [(operation, [val1, val2, ...])], ...}

operation is MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE, MODIFY_INCREMENT (import them from the ldap3 namespace)

The entire list of modifications is performed by the server in the order they are listed as a single atomic operation.
While individual modifications may violate certain aspects of the directory schema (such as the object class definition
and content rules), the resulting entry after the entire list of modifications is performed must conform to the requirements
of the directory model and the controlling schema.

The Modify operation cannot be used to remove from an entry any of its distinguished values (the values which form the
entry's relative distinguished name).

Due to the requirement for atomicity in applying the list of modifications in the Modify Request, the client may expect
that no modifications have been performed if the Modify Response received indicates any sort of error, and that all
requested modifications have been performed if the Modify Response indicates successful completion of the Modify operation.

You perform a Modify operation as in the following example (using the default synchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform the Modify operation
    c.modify('cn=user1,ou=users,o=company',
             {'givenName': [(MODIFY_REPLACE, ['givenname-1-replaced'])],
              'sn': [(MODIFY_REPLACE, ['sn-replaced'])]})
    print(c.result)

    # close the connection
    c.unbind()

Extended logging
----------------

To get an idea of what happens when you perform a Modify operation this is the extended log from a session to an OpenLdap
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
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]>
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]> with mode IP_V6_PREFERRED


    # Opening the connection (trying IPv6 then IPv4):

    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it.> for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <local: [::]:50396 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]
    DEBUG:ldap3:NETWORK:connection open for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>


    # Authenticating to the LDAP server with the Simple Bind method:

    DEBUG:ldap3:BASIC:start BIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:performing simple BIND for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:simple BIND request <{'version': 3, 'name': 'cn=admin,o=test', 'authentication': {'simple': '<stripped 8 characters of sensitive data>', 'sasl': None}}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=1
    >> protocolOp=ProtocolOp:
    >>  bindRequest=BindRequest:
    >>   version=3
    >>   name=b'cn=admin,o=test'
    >>   authentication=AuthenticationChoice:
    >>    simple=b'<stripped 8 characters of sensitive data>'
    DEBUG:ldap3:NETWORK:sent 37 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=1
    << protocolOp=ProtocolOp:
    <<  bindResponse=BindResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:BIND response <{'message': '', 'description': 'success', 'referrals': None, 'saslCreds': None, 'result': 0, 'dn': '', 'type': 'bindResponse'}> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done BIND operation, result <True>


    # Performing the Modify operation:

    DEBUG:ldap3:BASIC:start MODIFY operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:MODIFY request <{'entry': 'cn=user1,o=test', 'changes': [{'attribute': {'type': 'givenName', 'value': ['givenname-1-replaced']}, 'operation': 2}, {'attribute': {'type': 'sn', 'value': ['sn-replaced']}, 'operation': 2}]}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=2
    >> protocolOp=ProtocolOp:
    >>  modifyRequest=ModifyRequest:
    >>   object=b'cn=user1,o=test'
    >>   changes=Changes:
    >>    Change:
    >>     operation='replace'
    >>     modification=PartialAttribute:
    >>      type=b'givenName'
    >>      vals=Vals:
    >>       b'givenname-1-replaced'
    >>    Change:
    >>     operation='replace'
    >>     modification=PartialAttribute:
    >>      type=b'sn'
    >>      vals=Vals:
    >>       b'sn-replaced'
    DEBUG:ldap3:NETWORK:sent 94 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 14 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  modifyResponse=ModifyResponse:
    <<   resultCode='success'
    <<   matchedDN=b''
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:MODIFY response <[{'message': '', 'description': 'success', 'referrals': None, 'result': 0, 'dn': '', 'type': 'modifyResponse'}]> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done MODIFY operation, result <True>


    # Closing the connnection (via the Unbind operation):

    DEBUG:ldap3:BASIC:start UNBIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <3> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=3
    >> protocolOp=ProtocolOp:
    >>  unbindRequest=b''
    DEBUG:ldap3:NETWORK:sent 7 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:closing connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - open - <local: 192.168.137.1:52751 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection closed for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - bound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>


These are the usage metrics of this session::

    Connection Usage:
      Time: [elapsed:        0:00:01.243813]
        Initial start time:  2015-06-10T18:23:50.618075
        Open socket time:    2015-06-10T18:23:50.618075
        Close socket time:   2015-06-10T18:23:51.861888
      Server:
        Servers from pool:   0
        Sockets open:        1
        Sockets closed:      1
        Sockets wrapped:     0
      Bytes:                 166
        Transmitted:         138
        Received:            28
      Messages:              5
        Transmitted:         3
        Received:            2
      Operations:            3
        Abandon:             0
        Bind:                1
        Add:                 0
        Compare:             0
        Delete:              0
        Extended:            0
        Modify:              1
        ModifyDn:            0
        Search:              0
        Unbind:              1
      Referrals:
        Received:            0
        Followed:            0
      Restartable tries:     0
        Failed restarts:     0
        Successful restarts: 0
