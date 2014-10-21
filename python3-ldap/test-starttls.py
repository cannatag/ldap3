from ldap3 import Server, Connection, AUTH_SIMPLE, Tls
from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO, LDAPStartTLSError
import ssl

tls = Tls(validate=ssl.CERT_REQUIRED)
s = Server('edir1', port = 389, get_info = GET_ALL_INFO, tls = tls)
c = Connection(s, user='cn=admin,o=services',  password='password', auto_bind = True,
  check_names=True)

c.open()
try:
    # STARTTLS not supported on connection
    c.start_tls()
except ssl.SSLError:
    # appears to be a SSL certificate verification error
    print(2)
except LDAPStartTLSError:
    # appears to be a STARTTLS issue
    print(1)

