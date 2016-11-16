"""
"""

# Created on 2016.08.31
#
# Author: Giovanni Cannata
#
# Copyright 2013, 2014, 2015, 2016 Giovanni Cannata
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

from sys import stdin, getdefaultencoding
from ..core.exceptions import LDAPConfigurationParameterError

CASE_INSENSITIVE_ATTRIBUTE_NAMES = True
CASE_INSENSITIVE_SCHEMA_NAMES = True

# abstraction layer
ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX = 'OA_'

POOLING_LOOP_TIMEOUT = 10  # number of seconds to wait before restarting a cycle to find an active server in the pool

RESPONSE_SLEEPTIME = 0.05  # seconds to wait while waiting for a response in asynchronous strategies
RESPONSE_WAITING_TIMEOUT = 20  # waiting timeout for receiving a response in asynchronous strategies
SOCKET_SIZE = 4096  # socket byte size
CHECK_AVAILABILITY_TIMEOUT = 2.5  # default timeout for socket connect when checking availability
RESET_AVAILABILITY_TIMEOUT = 5  # default timeout for resetting the availability status when checking candidate addresses

# restartable strategy
RESTARTABLE_SLEEPTIME = 2  # time to wait in a restartable strategy before retrying the request
RESTARTABLE_TRIES = 30  # number of times to retry in a restartable strategy before giving up. Set to True for unlimited retries

# reusable strategies (Threaded)
REUSABLE_THREADED_POOL_SIZE = 10
REUSABLE_THREADED_LIFETIME = 3600  # 1 hour
DEFAULT_THREADED_POOL_NAME = 'REUSABLE_DEFAULT_POOL'

ADDRESS_INFO_REFRESH_TIME = 300  # seconds to wait before refreshing address info from dns
if stdin and stdin.encoding:
    DEFAULT_ENCODING = stdin.encoding
elif getdefaultencoding():
    DEFAULT_ENCODING = getdefaultencoding()
else:
    DEFAULT_ENCODING = 'utf-8'


def get_config_parameter(parameter):
    if parameter == 'CASE_INSENSITIVE_ATTRIBUTE_NAMES':
        return CASE_INSENSITIVE_ATTRIBUTE_NAMES
    elif parameter == 'CASE_INSENSITIVE_SCHEMA_NAMES':
        return CASE_INSENSITIVE_SCHEMA_NAMES
    elif parameter == 'ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX':
        return ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX
    elif parameter == 'POOLING_LOOP_TIMEOUT':
        return POOLING_LOOP_TIMEOUT
    elif parameter == 'RESPONSE_SLEEPTIME':
        return RESPONSE_SLEEPTIME
    elif parameter == 'RESPONSE_WAITING_TIMEOUT':
        return RESPONSE_WAITING_TIMEOUT
    elif parameter == 'SOCKET_SIZE':
        return SOCKET_SIZE
    elif parameter == 'CHECK_AVAILABILITY_TIMEOUT':
        return CHECK_AVAILABILITY_TIMEOUT
    elif parameter == 'RESTARTABLE_SLEEPTIME':
        return RESTARTABLE_SLEEPTIME
    elif parameter == 'RESTARTABLE_TRIES':
        return RESTARTABLE_TRIES
    elif parameter == 'REUSABLE_THREADED_POOL_SIZE':
        return REUSABLE_THREADED_POOL_SIZE
    elif parameter == 'REUSABLE_THREADED_LIFETIME':
        return REUSABLE_THREADED_LIFETIME
    elif parameter == 'DEFAULT_THREADED_POOL_NAME':
        return DEFAULT_THREADED_POOL_NAME
    elif parameter == 'ADDRESS_INFO_REFRESH_TIME':
        return ADDRESS_INFO_REFRESH_TIME
    elif parameter == 'RESET_AVAILABILITY_TIMEOUT':
        return RESET_AVAILABILITY_TIMEOUT
    elif parameter == 'DEFAULT_ENCODING':
        return DEFAULT_ENCODING

    raise LDAPConfigurationParameterError('configuration parameter %s not valid' % parameter)


def set_config_parameter(parameter, value):
    if parameter == 'CASE_INSENSITIVE_ATTRIBUTE_NAMES':
        global CASE_INSENSITIVE_ATTRIBUTE_NAMES
        CASE_INSENSITIVE_ATTRIBUTE_NAMES = value
    elif parameter == 'CASE_INSENSITIVE_SCHEMA_NAMES':
        global CASE_INSENSITIVE_SCHEMA_NAMES
        CASE_INSENSITIVE_SCHEMA_NAMES = value
    elif parameter == 'ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX':
        global ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX
        ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX = value
    elif parameter == 'POOLING_LOOP_TIMEOUT':
        global POOLING_LOOP_TIMEOUT
        POOLING_LOOP_TIMEOUT = value
    elif parameter == 'RESPONSE_SLEEPTIME':
        global RESPONSE_SLEEPTIME
        RESPONSE_SLEEPTIME = value
    elif parameter == 'RESPONSE_WAITING_TIMEOUT':
        global RESPONSE_WAITING_TIMEOUT
        RESPONSE_WAITING_TIMEOUT = value
    elif parameter == 'SOCKET_SIZE':
        global SOCKET_SIZE
        SOCKET_SIZE = value
    elif parameter == 'CHECK_AVAILABILITY_TIMEOUT':
        global CHECK_AVAILABILITY_TIMEOUT
        CHECK_AVAILABILITY_TIMEOUT = value
    elif parameter == 'RESTARTABLE_SLEEPTIME':
        global RESTARTABLE_SLEEPTIME
        RESTARTABLE_SLEEPTIME = value
    elif parameter == 'RESTARTABLE_TRIES':
        global RESTARTABLE_TRIES
        RESTARTABLE_TRIES = value
    elif parameter == 'REUSABLE_THREADED_POOL_SIZE':
        global REUSABLE_THREADED_POOL_SIZE
        REUSABLE_THREADED_POOL_SIZE = value
    elif parameter == 'REUSABLE_THREADED_LIFETIME':
        global REUSABLE_THREADED_LIFETIME
        REUSABLE_THREADED_LIFETIME = value
    elif parameter == 'DEFAULT_THREADED_POOL_NAME':
        global DEFAULT_THREADED_POOL_NAME
        DEFAULT_THREADED_POOL_NAME = value
    elif parameter == 'ADDRESS_INFO_REFRESH_TIME':
        global ADDRESS_INFO_REFRESH_TIME
        ADDRESS_INFO_REFRESH_TIME = value
    elif parameter == 'RESET_AVAILABILITY_TIMEOUT':
        global RESET_AVAILABILITY_TIMEOUT
        RESET_AVAILABILITY_TIMEOUT = value
    elif parameter == 'DEFAULT_ENCODING':
        global DEFAULT_ENCODING
        DEFAULT_ENCODING = value
    else:
        raise LDAPConfigurationParameterError('unable to set configuration parameter %s' % parameter)
