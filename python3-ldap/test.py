import socket
from ldap3 import (
    Connection,
    Server,
    ServerPool,
    SEARCH_SCOPE_WHOLE_SUBTREE,
    STRATEGY_SYNC_RESTARTABLE,
    POOLING_STRATEGY_ROUND_ROBIN_PASSIVE,
    POOLING_STRATEGY_ROUND_ROBIN_ACTIVE,
    LDAPException
)


# For Active Directory, quering the domain will return all all name servers.
# Yeah, that doesn't mean DC, but I was lazy to quickly post code.
# _, _, hosts = socket.gethostbyname_ex('xxx.xxx.xxx')
hosts = ['idmprofiler', '127.0.0.1']

servers = [Server(host=host, port=636, use_ssl=True) for host in hosts]

connection = Connection(
    ServerPool(servers, POOLING_STRATEGY_ROUND_ROBIN_PASSIVE),
    user='cn=admin,o=services',
    password='camera',
    client_strategy=STRATEGY_SYNC_RESTARTABLE,
    lazy=True
)

with connection as c:
    c.search(
        search_base='o=test',
        search_filter='(cn=test*)',
        search_scope=SEARCH_SCOPE_WHOLE_SUBTREE,
        attributes='*'
    )

    for resp in connection.response:
        if resp['type'] == 'searchResEntry':
            print(resp['dn'], resp['attributes'])

