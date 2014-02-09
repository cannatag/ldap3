from ldap3 import Server, Connection
from ldap3.abstraction import ObjectDef, AttrDef, Reader

reverse = lambda a, e: e[::-1]
valid = lambda a, e: True if e.startswith('t') else False

change = lambda attr, key: 'tost*'

def raiseParenthesesRank(attr, l):
    up = {'(': '[',
          ')': ']',
          '[': '{',
          ']':'}',
          '{':'<',
          '}':'>'
        }
    r = []
    for e in l:
        s = ''
        for c in e:
            s += up[c] if c in up else c
        r.append(s)

    return r

s = Server('edir')
c = Connection(s, user='cn=admin,o=risorse', password='password')
b = 'o=test'
print(c)
with c:
    print(c)
    result = c.search(b, '(&(objectClass=iNetOrgPerson)(cn=test-add*)(sn=test*))', attributes=['cn'])
    print (len(c.response))

ou = ObjectDef(['iNetOrgPerson', 'person'])
ou += AttrDef('cn', 'Common Name')
ou += AttrDef('sn', 'Surname', postQuery=reverse, preQuery=change)
ou += AttrDef('givenName', 'Given Name', validate=valid, postQuery=raiseParenthesesRank)
ou += 'ACL'
ou += AttrDef('employeeType', 'Department', default = 'not employeed')
qu = 'Common Name :test-add*, surname:=bug'
ru = Reader(c, ou, qu, b, getOperationalAttributes=True)
lu = ru.search()
eu = lu[0]

og = ObjectDef('groupOfNames')
og += AttrDef('member', dereferenceDN = ou)
og += 'cn'
qg = 'cn := test*'
rg = Reader(c, og, qg, b)
lg = rg.search()
eg = lg[0]
mg = lg[0].member
ug = lg[0].member[0]
