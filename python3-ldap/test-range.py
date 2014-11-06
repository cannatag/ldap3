from ldap3 import Server, Connection, ALL_ATTRIBUTES, MODIFY_ADD
from pprint import pprint

s = Server('win1', get_info=3)
c = Connection(s, 'cn=Administrator,cn=Users,dc=forest,dc=lab', 'Rc66pfop')
c.bind()

for x in range(5, 5000):
    print(x)
    nome = 'utente' + str(x).zfill(4)
    #c.add('cn=' + nome + ',ou=test,dc=forest,dc=lab', ['top', 'person', 'organizationalperson', 'user'], attributes={'displayname': nome, 'sn': nome, 'samaccountname': nome, 'userprincipalname': nome})
    #c.modify('cn=gruppo,ou=test,dc=forest,dc=lab', {"member": (MODIFY_ADD, ['cn=' + nome + ',ou=test,dc=forest,dc=lab'])})

c.search('ou=test,dc=forest,dc=lab','(cn=gruppo)',attributes=ALL_ATTRIBUTES)
pprint(dict(c.response[0]['attributes']))
c.unbind()