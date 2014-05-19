from ldap3 import (
    Connection,
    Server,
    ServerPool,
    SEARCH_SCOPE_WHOLE_SUBTREE,
    STRATEGY_SYNC_RESTARTABLE,
    STRATEGY_SYNC,
    POOLING_STRATEGY_ROUND_ROBIN,
    POOLING_STRATEGY_FIRST,
    POOLING_STRATEGY_RANDOM,
    LDAPException
)


# For Active Directory, querying the domain will return all all name servers.
# Yeah, that doesn't mean DC, but I was lazy to quickly post code.
# _, _, hosts = socket.gethostbyname_ex('xxx.xxx.xxx')
hosts = ['127.0.0.1', 'edir', 'edir2']

servers = [Server(host=host, port=636, use_ssl=True) for host in hosts]

connection = Connection(
    ServerPool(servers, POOLING_STRATEGY_RANDOM, active=True, exhaust=True),
    user='cn=admin,o=risorse',
    password='password',
    client_strategy=STRATEGY_SYNC,
    lazy=True
)
print('ready')
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

