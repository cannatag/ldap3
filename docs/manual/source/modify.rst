####################
The MODIFY operation
####################

The **MOdify** operation allows a client to request the modification of an entry already present in the LDAP directory.

To perform a Modify operation you must specify the dn of the entry and the kind of changes requested.

In the ldap3 library the signature for the Modify operation is::

    def modify(self,
               dn,
               changes,
               controls=None):

* dn: distinguish name of the object to delete

* changes: a sequence of changes to be performed in the specified entry

* controls: additional controls to send with the request

There are different type of changes:

* MODIFY_ADD: add values listed to the specified attribute, creating the attribute if necessary.

* MODIFY_DELETE: delete values listed from the attribute. If no values are listed, or if all current values of the attribute are listed,
the entire attribute is removed.

* MODIFY_REPLACE: replace all existing values of the specified attribute with the new values listed, creating the attribute
           if it did not already exist.  A replace with no values will delete the entire attribute if it exists, and it
           is ignored if the attribute does not exist.

* MODIFY_INCREMENT: All existing values of the specified attribute are to be incremented by the listed value. The attribute
             must be appropriate for the request (e.g., it must have INTEGER or other increment-able values), and the
             modification must provide one and only one value. (RFC4525)

changes is a dictionary in the form {'attribute1': (operation, [val1, val2, ...]], 'attribute2': (operation, [val1, val2, ...]), ...}

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

    # perform the Delete operation
    c.delete('cn=user1,ou=uses,o=company')
    print(c.result)

    # close the connection
    c.unbind()
