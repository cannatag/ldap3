from ldap3 import Server, Connection, ALL_ATTRIBUTES, MODIFY_ADD
from pprint import pprint

s = Server('win1', get_info=3)
c = Connection(s, 'cn=Administrator,cn=Users,dc=forest,dc=lab', 'Rc66pfop', auto_range=True)
#s = Server('edir1', get_info=3)
#c = Connection(s, 'cn=admin,o=services', 'password')
c.bind()

for x in range(0, 10000):
    nome = 'utente' + str(x).zfill(5)

    if not c.add('cn=' + nome + ',ou=range,ou=test,dc=forest,dc=lab', ['top', 'person', 'organizationalperson', 'user'], attributes={'displayname': nome, 'sn': nome, 'samaccountname': nome, 'userprincipalname': nome}):
        print('A', x, c.result)
    if not c.modify('cn=gruppo1,ou=range,ou=test,dc=forest,dc=lab', {"nonSecurityMember": (MODIFY_ADD, ['cn=' + nome + ',ou=range,ou=test,dc=forest,dc=lab'])}):
        print('B', x, c.result)
    if not c.modify('cn=gruppo2,ou=range,ou=test,dc=forest,dc=lab', {"member": (MODIFY_ADD, ['cn=' + nome + ',ou=range,ou=test,dc=forest,dc=lab'])}):
            print('C', x, c.result)

    # if not c.add('cn=' + nome + ',ou=range,o=test', ['inetorgperson'], attributes={'sn': nome, 'givenname': nome, }):
    #     print(x, c.result)
    #
    # if not c.modify('cn=gruppo,ou=range,o=test', {"member": (MODIFY_ADD, ['cn=' + nome + ',ou=range,o=test'])}):
    #     print(x, c.result)

#c.search('ou=range,o=test','(cn=gruppo)',attributes=ALL_ATTRIBUTES)
c.search('ou=range,ou=test,dc=forest,dc=lab', '(cn=gruppo*)', attributes=['member'])
for resp in c.response:
    print(resp['dn'], len(resp['attributes']['member']))
c.unbind()