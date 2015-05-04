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

# logging
VERBOSITY_SEVERE = 10
VERBOSITY_SPARSE = 20
VERBOSITY_NORMAL = 30
VERBOSITY_CHATTY = 40
VERBOSITY_LEVELS = [VERBOSITY_SEVERE, VERBOSITY_SPARSE, VERBOSITY_NORMAL, VERBOSITY_CHATTY]
LIBRARY_VERBOSITY_LEVEL = VERBOSITY_NORMAL
LIBRARY_LOGGING_LEVEL = DEBUG

logging_level = None
verbosity_level = None

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


def get_verbosity_level_name(level):

    if level == VERBOSITY_SEVERE:
        return 'SEVERE'
    elif level == VERBOSITY_SPARSE:
        return 'SPARSE'
    elif level == VERBOSITY_NORMAL:
        return 'NORMAL'
    elif level == VERBOSITY_CHATTY:
        return 'CHATTY'

    raise ValueError('unknown verbosity level')


def log(verbosity, message, *args):
    if verbosity <= verbosity_level:
        logger.log(logging_level, '[' + get_verbosity_level_name(verbosity) + '] ' + message, *args)


def log_enabled(verbosity):
    return True if logger.isEnabledFor(logging_level) and verbosity <= verbosity_level else False


def set_library_logging_level(level):
    if isinstance(level, int):
        global logging_level
        logging_level = level


def set_library_verbosity_level(verbosity):
    if verbosity in VERBOSITY_LEVELS:
        global verbosity_level
        verbosity_level = verbosity

# set a logger for the library with NullHandler. It can be used by the application with its own logging configuration
logger = getLogger('ldap3')
logger.addHandler(NullHandler())
set_library_logging_level(LIBRARY_LOGGING_LEVEL)
set_library_verbosity_level(LIBRARY_VERBOSITY_LEVEL)

# emits a info message to let the application know that ldap3 logging is available when the log level is set to logging_level
logger.info('ldap3 library intialized - logging emitted when loglevel is ' + getLevelName(logging_level))
