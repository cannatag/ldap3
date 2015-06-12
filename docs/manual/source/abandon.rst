#####################
The ABANDON operation
#####################


   The function of the Abandon operation is to allow a client to request
   that the server abandon an uncompleted operation.  The Abandon
   Request is defined as follows:

        AbandonRequest ::= [APPLICATION 16] MessageID

   The MessageID is that of an operation that was requested earlier at
   this LDAP message layer.  The Abandon request itself has its own
   MessageID.  This is distinct from the MessageID of the earlier
   operation being abandoned.



Sermersheim                 Standards Track                    [Page 36]

RFC 4511                         LDAPv3                        June 2006


   There is no response defined in the Abandon operation.  Upon receipt
   of an AbandonRequest, the server MAY abandon the operation identified
   by the MessageID.  Since the client cannot tell the difference
   between a successfully abandoned operation and an uncompleted
   operation, the application of the Abandon operation is limited to
   uses where the client does not require an indication of its outcome.

   Abandon, Bind, Unbind, and StartTLS operations cannot be abandoned.

   In the event that a server receives an Abandon Request on a Search
   operation in the midst of transmitting responses to the Search, that
   server MUST cease transmitting entry responses to the abandoned
   request immediately, and it MUST NOT send the SearchResultDone.  Of
   course, the server MUST ensure that only properly encoded LDAPMessage
   PDUs are transmitted.

   The ability to abandon other (particularly update) operations is at
   the discretion of the server.

   Clients should not send Abandon requests for the same operation
   multiple times, and they MUST also be prepared to receive results
   from operations they have abandoned (since these might have been in
   transit when the Abandon was requested or might not be able to be
   abandoned).

   Servers MUST discard Abandon requests for messageIDs they do not
   recognize, for operations that cannot be abandoned, and for
   operations that have already been abandoned.


The use of the **Abandon** operation is quite limited. Its function is to allow a client to request that the server
gives up an uncompleted operation. Since there is no response from the server the client cannot tell the difference
between a successfully abandoned operation and a completed operation. The Bind, Unbind, StartTLS and Abandon operations
cannot be abandoned.

Clients should not send multiple Abandon requests for the same message ID and must be prepared to receive a response to
the original operation, in case the server has already completed the request before receiving the Abandon request.

The Abandon operation can be used with asynchronous strategies only because you need the message ID that is returned
by the operation method of the connection object.

The Abandon Request is defined as follows::

    def abandon(self,
                message_id,
                controls=None):

To perform an Abandon operation you must specify the id of the operation to be abandoned.


You perform an Abandon operation as in the following example (using the asynchronous strategy)::

    # import class and constants
    from ldap3 import Server, Connection, ALL, ASYNC

    # define the server
    s = Server('servername', get_info=ALL)  # define an unsecure LDAP server, requesting info on DSE and schema

    # define the connection
    c = Connection(s, user='user_dn', password='user_password', client_strategy=ASYNC)

    # perform a Delete operation
    message_id = c.delete('cn=user1,ou=users,o=company')

    # perform the Abandon operation
    c.abandon(message_id)

    # check if the operation to be abandoned has been already executed
    result = connection.get_response(message_id)
    if not result:
        print('Abandon successful')
    else:
        print('Too late... Cannot abandon')

    # close the connection
    c.unbind()
