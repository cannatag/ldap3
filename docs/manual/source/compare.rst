#####################
The COMPARE operation
#####################

The **Compare** operation allows a client to request the comparison of an entry attribute against a specific value.

To perform a Compare operation you must specify the dn of the entry, the name of the attribute and the value to compare.

In the ldap3 library the signature for the Compare operation is::

        def compare(self,
                dn,
                attribute,
                value,
                controls=None):

    * dn: distinguished name of the entry whose attribute is to compare

    * attribute: name of the attribute to compare

    * value: value to be compared

    * controls: additional controls to send in the request


For synchronous strategies the compare method returns True if the attribute value equals the value sent in the operation,
returns False in case it's different.

For asynchronous strategies the compare method returns the message id of the operation. You can get the operation result
with the get_response(message_id) method of the connection object.

False value is returned even if the entry is not found in the LDAP server. You can check the description of the connection
result attribute to know the reason of the missed match. The dessription is set to compareTrue, compareFalse, or an appropriate error.

compareTrue indicates that the specified value matches a value of the attribute according to the attribute's EQUALITY matching rule.
compareFalse indicates that the specified value and the value (or values) of the attribute does not match.

Note that some LDAP servers may establish access controls that permit the values of certain attributes 0to be compared
but not read by other means (as for the userPassword attribute).


You perform a Compare operation as in the following example (using the default synchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform the Compare operation
    comparison = c.compare('cn=user1,ou=users,o=company', 'sn', 'surname')
    print(comparison)

    # close the connection
    c.unbind()


Extended logging
----------------

To get an idea of what happens when you perform a Compare operation this is the extended log from a session to an OpenLdap
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


    # Performing the Compare operation:

    DEBUG:ldap3:BASIC:start COMPARE operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:COMPARE request <{'entry': 'cn=user1,o=test', 'attribute': 'sn', 'value': 'surname'}> sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <2> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=2
    >> protocolOp=ProtocolOp:
    >>  compareRequest=CompareRequest:
    >>   entry=b'cn=user1,o=test'
    >>   ava=AttributeValueAssertion:
    >>    attributeDesc=b'sn'
    >>    assertionValue=b'surname'
    DEBUG:ldap3:NETWORK:sent 39 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 20 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:received 1 ldap messages via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    <<LDAPMessage:
    << messageID=2
    << protocolOp=ProtocolOp:
    <<  compareResponse=CompareResponse:
    <<   resultCode='noSuchObject'
    <<   matchedDN=b'o=test'
    <<   diagnosticMessage=b''
    DEBUG:ldap3:PROTOCOL:COMPARE response <[{'description': 'noSuchObject', 'message': '', 'type': 'compareResponse', 'result': 32, 'dn': 'o=test', 'referrals': None}]> received via <ldap://openldap:389 - cleartext - user: cn=admin,o=services - unbound - open - <local: 192.168.137.1:51287 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:done COMPARE operation, result <False>


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

    Connection Usage:
      Time: [elapsed:        0:00:01.040277]
        Initial start time:  2015-07-16T07:38:39.883408
        Open socket time:    2015-07-16T07:38:39.883408
        Close socket time:   2015-07-16T07:38:40.923685
      Server:
        Servers from pool:   0
        Sockets open:        1
        Sockets closed:      1
        Sockets wrapped:     0
      Bytes:                 121
        Transmitted:         87
        Received:            34
      Messages:              5
        Transmitted:         3
        Received:            2
      Operations:            3
        Abandon:             0
        Bind:                1
        Add:                 0
        Compare:             1
        Delete:              0
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

