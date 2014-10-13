import ldap3

server = ldap3.Server('unknownhost')
try:
    connection = ldap3.Connection(server, auto_bind=True)
except ldap3.core.exceptions.LDAPSocketCloseError as err:
    print ("Exception: " + str(type(err)))
    print ("Caught: LDAPSocketOpenError")
except ldap3.core.exceptions.LDAPCommunicationError as err:
    print ("Exception: " + str(type(err)))
    print ("Caught: LDAPCommunicationError")