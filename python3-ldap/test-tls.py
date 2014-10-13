import ldap3
import ssl
host = 'edir1'
port = 389

tls = ldap3.Tls(validate=ssl.CERT_REQUIRED)
server = ldap3.Server(host, port=port, use_ssl=False, tls=tls)
conn1 = ldap3.Connection(server, raise_exceptions=False)
conn2 = ldap3.Connection(server, raise_exceptions=True)

try:
    conn1.open()
    conn1.start_tls()
except Exception as e:
    # ldap3.LDAPStartTLSError is raised
    print (type(e), e)
    e1 = e

try:
    conn2.open()
    conn2.start_tls()
except Exception as e:
    # ldap3.LDAPProtocolErrorResult is raised
    print (type(e), e)
    e2 = e
