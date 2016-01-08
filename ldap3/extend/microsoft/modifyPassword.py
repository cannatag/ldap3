from ... import MODIFY_REPLACE, RESULT_SUCCESS, MODIFY_DELETE, MODIFY_ADD
from ...utils.log import log, log_enabled, PROTOCOL


def modify_ad_password(connection, user_dn, old_password, new_password, controls=None):
    # old password must be None to reset password with sufficient privileges
    encoded_new_password = ('"%s"' % new_password).encode('utf-16-le')
    if old_password:  # normal users must specify old and new password
        encoded_old_password = ('"%s"' % old_password).encode('utf-16-le')
        result = connection.modify(user_dn,
                                   {'unicodePwd': [(MODIFY_DELETE, [encoded_old_password]),
                                                   (MODIFY_ADD, [encoded_new_password])]},
                                   controls)
    else:  # admin users can reset password without sending the old one
        result = connection.modify(user_dn,
                                   {'unicodePwd': [(MODIFY_REPLACE, [encoded_new_password])]},
                                   controls)

    if not connection.strategy.sync:
        _, result = connection.get_response(result)
    else:
        result = connection.result

    # change successful, returns True
    if result['result'] == RESULT_SUCCESS:
        return True

    # change was not successful, raises exception if raise_exception = True in connection or returns the operation result, error code is in result['result']
    if connection.raise_exceptions:
        from ... import LDAPOperationResult
        if log_enabled(PROTOCOL):
            log(PROTOCOL, 'operation result <%s> for <%s>', result, connection)
        raise LDAPOperationResult(result=result['result'], description=result['description'], dn=result['dn'], message=result['message'], response_type=result['type'])

    return result
