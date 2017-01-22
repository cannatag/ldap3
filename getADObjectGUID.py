from ldap3 import Server, Connection
from ldap3.utils.conv import escape_bytes
from uuid import UUID

MY_SERVER = 'labldap01.cloudapp.net'
MY_BASE = 'cn=Users, dc=ad2012, dc=LAB'
MY_ADMIN = 'cn=Giovanni, cn=Users, dc=AD2012, dc=LAB'
MY_PASSWORD = 'Rc123456pfop'
MY_USER = 'Giovanni'

# establish a connection to the AD Server
print('Trying to connect to ' + MY_SERVER + ' with user ' + MY_ADMIN)
s = Server(MY_SERVER, use_ssl=True)
c = Connection(s, MY_ADMIN, MY_PASSWORD)
if c.bind():
    print('Searching for object GUID for user ' + MY_USER)
    if c.search(MY_BASE, '(cn=%s)' % MY_USER, attributes=['objectGuid']):
        print('Entry ' + c.response[0]['dn'] + ' found')
        if c.response[0]['attributes']['objectGuid']:
            guid = c.response[0]['attributes']['objectGuid']
            escaped_guid = escape_bytes(UUID(guid).bytes_le)
            print('Object GUID for %s is %s. Its escaped bytes value is %s' % (MY_USER, guid, escaped_guid))
            print('Searching for guid ' + guid)
            if c.search(MY_BASE, '(objectGuid=%s)' % escaped_guid, attributes=['samAccountName', 'objectGUID']):
                print('Found user %s with object GUID %s' % (c.response[0]['attributes']['samAccountName'], c.response[0]['attributes']['objectGuid']))
            else:
                print('ObjectGuid ' + guid + ' not found')
        else:
            print('objectGuid not found for ' + MY_USER)
    else:
        print(MY_USER + ' not found')
    print('Closing connectin to ' + MY_SERVER)
    c.unbind()
else:
    print('Unable to bind to ' + MY_SERVER + ' + with user ' + MY_USER)

print('Done')