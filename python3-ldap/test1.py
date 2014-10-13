from ldap3 import Server, Connection, SEARCH_SCOPE_WHOLE_SUBTREE, AUTO_BIND_NO_TLS #For title queires into LDAP

def GetTitle(u):
    print(u)
    t=[]

    server = Server('edir1')
    c = Connection(server,
                   auto_bind=AUTO_BIND_NO_TLS,
                   read_only=True,
                   check_names=True,
                   user = 'cn=admin,o=services',
                   password= 'password')

    c.search(search_base = 'o=test',
             search_filter = '(&(cn=' + u + '))',
             search_scope = SEARCH_SCOPE_WHOLE_SUBTREE,
             attributes = ['cn'],
             paged_size = 5)

    for entry in c.response:
        print(entry['attributes']['cn'])
        t = entry['attributes']['cn']
        print(u, " : ", t)

users = ['test-add', 'notAuser', 'test-search-1']

for u in users:
    GetTitle(u)
