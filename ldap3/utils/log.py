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

from logging import getLogger, DEBUG, getLevelName

from .. import LIBRARY_LOGGING_LEVEL

logging_level = None

try:
    from logging import NullHandler
except ImportError:  # NullHandler not present in Python < 2.7
    from logging import Handler

    class NullHandler(Handler):
        def handle(self, record):
            """Stub."""

        def emit(self, record):
            """Stub."""

        def createLock(self):
            self.lock = None


def log(message):
    logger.log(logging_level, message)


def log_enabled():
    if logger.isEnabledFor(logging_level):
        return True
    return False


def set_logging_level(level):
    global logging_level
    logging_level = level


logger = getLogger('ldap3')
logger.addHandler(NullHandler())
set_logging_level(LIBRARY_LOGGING_LEVEL)
logger.info('ldap3 library intialized - logging emitted when loglevel is ' + getLevelName(logging_level))
