from ldap3 import Server, Connection, ObjectDef, AttrDef, Reader, Writer, ALL
server = Server('ipa.demo1.freeipa.org', get_info=ALL)
conn = Connection(server, 'uid=admin,cn=users,cn=accounts,dc=demo1,dc=freeipa,dc=org', 'Secret123', auto_bind=True)
obj_person = ObjectDef('person', conn)
r = Reader(conn, obj_person, None, 'dc=demo1,dc=freeipa,dc=org')
r.search()
w = Writer.from_cursor(r)
print(w)