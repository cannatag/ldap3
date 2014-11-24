from ldap3 import Server, Connection

s = Server('win1', get_info=3)
c = Connection(s, 'cn=Administrator,cn=Users,dc=forest,dc=lab', 'Rc66pfop', auto_bind=True, auto_range=True)
c.search('ou=range,ou=test,dc=forest,dc=lab', '(cn=*)', attributes=['member'], paged_size=999)
q = c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
r = c.response
while q:
    c.search('ou=range,ou=test,dc=forest,dc=lab', '(cn=*)', attributes=['member'], paged_cookie=q, paged_size=123)
    r += c.response
    if 'controls' in c.result:
        q = c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    else:
        print('NONE', c.result)
        q = None
    #print(len(c.response), q)
print('FINE', c.result)
print(len(r))