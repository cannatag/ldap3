#####################
The ABANDON operation
#####################

The use of the **Abandon** operation is very limited. Its function is to allow a client to request that the server
gives up an uncompleted operation. Since there is no response from the server the client cannot tell the difference
between a successfully abandoned operation and a completed operation. The Bind, Unbind and the Abandon operations
cannot be abandoned.

Clients should not send multiple Abandon requests for the same message ID and must be prepared to receive a response to
the original operation, in case the server has already completed the request before receiving the Abandon request.

The only (and indirect) way to know if the operation has been abandoned is to wait for a reasonable time to see if you
get the response to the original operation (the one that has to be abandoned).

The Abandon operation can be used with asynchronous strategies only because you need the message ID that is returned
by the operation method of the connection object.

The Abandon Request is defined as follows::

    def abandon(self,
                message_id,
                controls=None):


    * message_id: id of the previously sent request to be abandoned

    * controls: additional controls to send in the request


The abandon method returns True if the abandon request was sent, returns False if the request cannot
be sent (for Bind, Unbind and Abandon requests).

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
