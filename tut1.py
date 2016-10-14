from ldap3 import Server, Connection
from ldap3.utils.dn import safe_rdn
server = Server('ipa.demo1.freeipa.org')
conn = Connection(server, 'uid=admin, cn=users, cn=accounts, dc=demo1, dc=freeipa, dc=org', 'Secret123', auto_bind=True)
print(conn.extend.standard.who_am_i())
print(server.schema)
print(server.info)
print(server.schema.object_classes['inetorgperson'])
print(server.schema.object_classes['organizationalperson'])
print(server.schema.object_classes['person'])
print(server.schema.object_classes['top'])

conn.search('dc=demo1, dc=freeipa, dc=org', '(&(objectclass=person)(uid=admin))', attributes=['sn', 'krbLastPwdChange', 'objectclass'])
entry = conn.entries[0]

print(entry)

conn.add('ou=ldap3-tutorial, dc=demo1, dc=freeipa, dc=org', 'organizationalUnit')
conn.add('cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Beatrix', 'sn': 'Young', 'departmentNumber': 'DEV', 'telephoneNumber': 1111})
conn.add('cn=j.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'John', 'sn': 'Smith', 'departmentNumber': 'DEV', 'telephoneNumber': 2222})
conn.add('cn=m.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Marianne', 'sn': 'Smith', 'departmentNumber': 'QA',  'telephoneNumber': 3333})
conn.add('cn=quentin.cat,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'inetOrgPerson', {'givenName': 'Quentin', 'sn': 'Cat', 'departmentNumber': 'CC', 'telephoneNumber': 4444})
conn.modify_dn('cn=b.young,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'cn=b.smith')
conn.search('ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=b.smith)', attributes=['objectclass', 'sn', 'cn', 'givenname'])
print(conn.entries)
conn.add('ou=moved, ou=ldap3-tutorial, dc=demo1, dc=freeipa, dc=org', 'organizationalUnit')
conn.modify_dn('cn=b.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', 'cn=b.smith', new_superior='ou=moved, ou=ldap3-tutorial, dc=demo1, dc=freeipa, dc=org')
print(safe_rdn('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org'))
from ldap3 import MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE
print(conn.modify('cn=b.smith,ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', {'sn': [(MODIFY_ADD, ['Smith'])]}))
print(conn.last_error)
conn.search('ou=moved,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', '(cn=b.smith)', attributes=['objectclass', 'sn', 'cn', 'givenname'])
print(conn.entries)
