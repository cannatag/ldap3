from ldap3 import Server, Connection
from ldap3.abstract import ObjectDef, AttrDef, Reader

person = ObjectDef('inetOrgPerson')
engineer = ObjectDef(['inetOrgPerson', 'auxEngineer'])
cnAttribute = AttrDef('cn')
person.add(cnAttribute)
# person += AttrDef('cn')  # same as above
# person += 'cn'  # same as above

person += [AttrDef('cn', key='Common Name'), AttrDef('sn', key='Surname')]
# person += ['cn', 'sn']  # as above, but keys are the attribute names
cnAttrDef = person['Common Name']
cnAttrDef = person['commonName']  # same as above
cnAttrDef = person.CommonName  # same as above

deps = {'A': 'Accounting', 'F': 'Finance', 'E': 'Engineering'}
# checks that the parameter in query is in a specific range
validDepartment = lambda attr, value: True if value in deps.values() else False
# person += AttrDef('employeeStatus', key = 'Department', validate = validDepartment)
# transform value to be search


def get_department_code(attr, value):
    for dep in deps.items():
        if dep[1] == value:
            return dep[0]
    return 'not a department'

# person += AttrDef('employeeStatus', key = 'Department', preQuery = getDepartmentCode)
getDepartmentName = lambda attr, value: deps.get(value, 'not a department') if attr == 'Department' else value
person += AttrDef('employeeStatus', key='Department', validate=validDepartment, pre_query=get_department_code, post_query=getDepartmentName)
department = ObjectDef('groupOfNames')
department += 'cn'
department += AttrDef('member', key='employeer', dereference_dn=person)  # values of 'employeer' will be the 'Person' entries members of the found department
s = Server('edir1')
c = Connection(s, user='cn=admin,o=resources', password='password')
query = 'Department: Accounting'  # explained in next paragraph
personReader = Reader(c, person, query, 'o=test')
personReader.search()
print(personReader)

personEntry = personReader.entries[0]
for attr in personEntry:
    print(attr)

personCommonName = personEntry.CommonName
for cn in personCommonName:
    print(cn)
    print(cn.rawValues)

myDepartment = personEntry.Department.value
