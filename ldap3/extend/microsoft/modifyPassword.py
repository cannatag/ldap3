from ... import MODIFY_REPLACE, RESULT_SUCCESS, LDAPOperationResult
from ...utils.log import log, log_enabled, PROTOCOL


def modify_password(connection, user_dn, new_password):
    encoded_password = '"%s"' % (new_password.encode('utf-16-le'))
    result = connection.modify(user_dn, {'unicodePwd': [(MODIFY_REPLACE, [encoded_password])]})
    if not connection.strategy.sync:
        _, result = connection.get_response(result)
    else:
        result = connection.result

    # change successful, returns True
    if result['result'] == RESULT_SUCCESS:
        return True

    # change unsuccessful, raises exception if raise_exception = True in connection or returns the operation result, error code is in result['result']
    if connection.raise_exceptions:
        if log_enabled(PROTOCOL):
            log(PROTOCOL, 'operation result <%s> for <%s>', result, connection)
        raise LDAPOperationResult(result=result['result'], description=result['description'], dn=result['dn'], message=result['message'], response_type=result['type'])

    return result
