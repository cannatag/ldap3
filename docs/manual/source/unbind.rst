####################
The UNBIND operation
####################

As specified in RFC4511 the **Unbind** operation must be tought as the "disconnect" operation. It's name (and that of its
Bind counterpart) is for historical reason.

Bind and Unbind are not symmetrical operations. In fact when you open a connection to an LDAP server you're already bounded
in an **anonymous** connection state. What this exactly means is defined by the server implementation, not by the protocol.
When you perform an Unbind operation you're actually requesting the server to end the user's sessione and close the
communication socket. The Bind operation instead has nothing to do with the socket, but performs the user's authentication.

So it's perfectly legal to open a connession to the ldap server, perform some operation in the anonymous state and then Unbind
to close the session.

In the ldap3 library the signature for the Delete operation is::

    def unbind(self,
               controls=None):

* controls: additional controls to send in the request

The unbind method always returns True.

You perform an Unbind operation as in the following example (using the default synchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password')

    # perform some LDAP operation
    ...

    # perform the Unbind operation
    c.unbind()

The Unbind request is quite peculiar in the LDAPv3 protocol. There is no acknowledgement from thet server, that doesn't respond at all.
It just ends the user's session and close the socket. The ldap3 library checks the success of this operation shutting down the socket
on both communication directions and then closes the socket.

You can check if the socket has been closed querying the *closed* attribute of the connection object.

Notice of Disconnection
-----------------------

Usually all communications between the client and the server are started by the client. There is only one case where the
LDAP server send an unsolicited message: the Notice of Disconnection. This message is issued by the server as an alert
when the server is about to stop. Once the message is sent, the server doesn't wait for any response, closes the socket
and quits. Note that this notification is not used as a response to an Unbind requested by the client.

When the ldap3 library receive a Notice of Disconnection it tries to gracefully close the socket and then raise the
LDAPSessionTerminatedByServer Exception. With asynchronous strategies the Exception is raised immediately, while with
synchronous strategies the Exception is raised as you try to send data over the socket.

Extended logging
----------------
To get an idea of what's happening when you perform an Unbind operation this is the extended log from an unbounded
session to an OpenLdap server from a Windows client::

    # Initialization:
    INFO:ldap3:ldap3 library initialized - logging emitted with loglevel set to DEBUG - available detail levels are: OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED
    DEBUG:ldap3:ERROR:detail level set to EXTENDED
    DEBUG:ldap3:BASIC:instantiated Server: <Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO')>
    DEBUG:ldap3:BASIC:instantiated Usage object
    DEBUG:ldap3:BASIC:instantiated <SyncStrategy>: <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - No strategy - async - real DSA - not pooled - cannot stream output>
    DEBUG:ldap3:BASIC:instantiated Connection: <Connection(server=Server(host='openldap', port=389, use_ssl=False, get_info='NO_INFO'), user='cn=admin,o=test', password='password', auto_bind='NONE', version=3, authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True, check_names=True, collect_usage=True, read_only=False, lazy=False, raise_exceptions=False)>
    DEBUG:ldap3:NETWORK:opening connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:reset usage metrics
    DEBUG:ldap3:BASIC:start collecting usage metrics
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]>
    DEBUG:ldap3:BASIC:address for <ldap://openldap:389 - cleartext> resolved as <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]>
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]> with mode IP_V6_PREFERRED
    DEBUG:ldap3:BASIC:obtained candidate address for <ldap://openldap:389 - cleartext>: <[<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]> with mode IP_V6_PREFERRED


    # Opening the connection (trying IPv6 then IPv4):

    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET6: 23>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('fe80::215:5dff:fe8f:2f0d%20', 389, 0, 20)]
    DEBUG:ldap3:ERROR:<socket connection error: [WinError 10061] No connection could be made because the target machine actively refused it.> for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <local: [::]:49610 - remote: [None]:None> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:try to open candidate address [<AddressFamily.AF_INET: 2>, <SocketKind.SOCK_STREAM: 1>, 6, '', ('192.168.137.104', 389)]
    DEBUG:ldap3:NETWORK:connection open for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49291 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:BASIC:refreshing server info for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49291 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>


    # Performing the Unbind operation:

    DEBUG:ldap3:BASIC:start UNBIND operation via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49291 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:UNBIND request sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49291 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:PROTOCOL:new message id <1> generated
    DEBUG:ldap3:NETWORK:sending 1 ldap message for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49291 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:EXTENDED:ldap message sent via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49291 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>:
    >>LDAPMessage:
    >> messageID=1
    >> protocolOp=ProtocolOp:
    >>  unbindRequest=b''
    DEBUG:ldap3:NETWORK:sent 7 bytes via <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49291 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:closing connection for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - open - <local: 192.168.137.1:49291 - remote: 192.168.137.104:389> - tls not started - listening - SyncStrategy>
    DEBUG:ldap3:NETWORK:connection closed for <ldap://openldap:389 - cleartext - user: cn=admin,o=test - unbound - closed - <no socket> - tls not started - not listening - SyncStrategy>
    DEBUG:ldap3:BASIC:stop collecting usage metrics
    DEBUG:ldap3:BASIC:done UNBIND operation, result <True>


These are the usage metrics of this session::

    Connection Usage:
      Time: [elapsed:        0:00:01.030738]
        Initial start time:  2015-06-04T17:01:43.431465
        Open socket time:    2015-06-04T17:01:43.431465
        Close socket time:   2015-06-04T17:01:44.462203
      Server:
        Servers from pool:   0
        Sockets open:        1
        Sockets closed:      1
        Sockets wrapped:     0
      Bytes:                 7
        Transmitted:         7
        Received:            0
      Messages:              1
        Transmitted:         1
        Received:            0
      Operations:            1
        Abandon:             0
        Bind:                0
        Add:                 0
        Compare:             0
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

As you can see there is been one operation only, the Unbind operation. 1 socket
has been open and then has been closed. All the communication stream took 7 bytes in 1 LDAP messages and the server never
sent anything back.
