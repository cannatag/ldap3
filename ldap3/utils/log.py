"""
"""

# Created on 2015.05.01
#
# Author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from logging import getLogger, getLevelName, DEBUG
from os import linesep
from copy import deepcopy

# logging
OFF = 0
ERROR = 10
BASIC = 20
PROTOCOL = 30
NETWORK = 40
EXTENDED = 50

_sensitive_lines = ('simple', 'credentials', 'serversaslcreds')  # must be a tuple, not a list
_sensitive_args = ('simple', 'password', 'sasl_credentials', 'saslcreds', 'server_creds')
_hide_sensitive_data = None

DETAIL_LEVELS = [OFF, ERROR, BASIC, PROTOCOL, NETWORK, EXTENDED]

_max_line_length = 4096
_logging_level = None
_detail_level = None
_logging_encoding = 'ascii'

try:
    from logging import NullHandler
except ImportError:  # NullHandler not present in Python < 2.7
    from logging import Handler

    class NullHandler(Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None


def _strip_sensitive_data_from_dict(d):
    if not isinstance(d, dict):
        return d

    try:
        d = deepcopy(d)
    except Exception:  # if deepcopy goes wrong gives up and return the dict unchanged
        return d
    for k in d.keys():
        if isinstance(d[k], dict):
            d[k] = _strip_sensitive_data_from_dict(d[k])
        elif k.lower() in _sensitive_args and d[k]:
            d[k] = '<stripped %d characters of sensitive data>' % len(d[k])

    return d


def get_detail_level_name(level_name):
    if level_name == OFF:
        return 'OFF'
    elif level_name == ERROR:
        return 'ERROR'
    elif level_name == BASIC:
        return 'BASIC'
    elif level_name == PROTOCOL:
        return 'PROTOCOL'
    elif level_name == NETWORK:
        return 'NETWORK'
    elif level_name == EXTENDED:
        return 'EXTENDED'
    raise ValueError('unknown detail level')


def log(detail, message, *args):
    if detail <= _detail_level:
        if _hide_sensitive_data:
            args = tuple([_strip_sensitive_data_from_dict(arg) if isinstance(arg, dict) else arg for arg in args])

        encoded_message = (get_detail_level_name(detail) + ':' + message % args).encode(_logging_encoding, 'backslashreplace')
        if str != bytes:  # Python 3
            encoded_message = encoded_message.decode()

        if len(encoded_message) > _max_line_length:
            logger.log(_logging_level, encoded_message[:_max_line_length] + ' <removed %d remaining bytes in this log line>' % (len(encoded_message) - _max_line_length, ))
        else:
            logger.log(_logging_level, encoded_message)


def log_enabled(detail):
    if detail <= _detail_level:
        if logger.isEnabledFor(_logging_level):
            return True

    return False


def set_library_log_hide_sensitive_data(hide=True):
    global _hide_sensitive_data
    if hide:
        _hide_sensitive_data = True
    else:
        _hide_sensitive_data = False
    if log_enabled(ERROR):
        log(ERROR, 'hide sensitive data set to ' + str(_hide_sensitive_data))


def get_library_log_hide_sensitive_data():
    return True if _hide_sensitive_data else False


def set_library_log_activation_level(logging_level):
    if isinstance(logging_level, int):
        global _logging_level
        _logging_level = logging_level
    else:
        if log_enabled(ERROR):
            log(ERROR, 'invalid library log activation level <%s> ', logging_level)
        raise ValueError('invalid library log activation level')


def get_library_log_activation_lavel():
    return _logging_level


def set_library_log_max_line_length(length):
    if isinstance(length, int):
        global _max_line_length
        _max_line_length = length
    else:
        if log_enabled(ERROR):
            log(ERROR, 'invalid log max line length <%s> ', length)
        raise ValueError('invalid library log max line length')


def get_library_log_max_line_length():
    return _max_line_length


def set_library_log_detail_level(detail):
    if detail in DETAIL_LEVELS:
        global _detail_level
        _detail_level = detail
        if log_enabled(ERROR):
            log(ERROR, 'detail level set to ' + get_detail_level_name(_detail_level))
    else:
        if log_enabled(ERROR):
            log(ERROR, 'unable to set log detail level to <%s>', detail)
        raise ValueError('invalid library log detail level')


def get_library_log_detail_level():
    return _detail_level


def format_ldap_message(message, prefix):
    prefixed = ''
    for line in message.prettyPrint().split('\n'):  # uses pyasn1 LDAP message prettyPrint() method
        if line:
            if _hide_sensitive_data and line.strip().lower().startswith(_sensitive_lines):  # _sensitive_lines is a tuple. startswith() method check each tuple element
                tag, _, data = line.partition('=')
                if data.startswith("b'") and data.endswith("'") or data.startswith('b"') and data.endswith('"'):
                    prefixed += linesep + prefix + tag + '=<stripped %d characters of sensitive data>' % (len(data) - 3, )
                else:
                    prefixed += linesep + prefix + tag + '=<stripped %d characters of sensitive data>' % len(data)
            else:
                prefixed += linesep + prefix + line
    return prefixed

# sets a logger for the library with NullHandler. It can be used by the application with its own logging configuration
logger = getLogger('ldap3')
logger.addHandler(NullHandler())

# set defaults for the library logging
set_library_log_activation_level(DEBUG)
set_library_log_detail_level(OFF)
set_library_log_hide_sensitive_data(True)

# emits a info message to let the application know that ldap3 logging is available when the log level is set to _logging_level
logger.info('ldap3 library initialized - logging emitted with loglevel set to ' + getLevelName(_logging_level) + ' - available detail levels are: ' + ', '.join([get_detail_level_name(level) for level in DETAIL_LEVELS]) + ' - sensitive data will ' + ('' if _hide_sensitive_data else 'not ') + 'be hidden')
