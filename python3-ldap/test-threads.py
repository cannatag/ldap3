from ldap3 import Server, Connection, AUTH_SIMPLE, STRATEGY_ASYNC_THREADED
from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO
from multiprocessing.pool import ThreadPool as Pool

s = Server('edir1', port = 389, get_info = GET_ALL_INFO)
c = Connection(s, user='cn=admin,o=services',  password='password', auto_bind = True,
  client_strategy = STRATEGY_ASYNC_THREADED, check_names=True)

def f(uid):
  uid=uid.rstrip()
  msgid = c.search(
   'o=test', '(cn=%s)' % uid,
   SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['sn', 'objectClass'])
  response, result = c.get_response(msgid, timeout=5)
  print (msgid)
  if not result:
    print ("TIMEOUT",uid)
    return None
  for r in response:
    if uid not in r['dn']:
       print ("PROBLEM",uid, r['dn'])
    return(r['dn'])

if __name__ == '__main__':
    # uids=open('/tmp/uids','r').rseadlines()
    cns = ['test-search-1', 'test-search-2', 'test-search-3'] * 1000
    pool = Pool(processes=10)
    print (len(pool.map(f, cns)))
