# Created on 2013.07.11
#
# @author: Giovanni Cannata
#
# Copyright 2013 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from os import path

package_name = 'python3-ldap'
package_folder = path.join('.', package_name)
version_file = open(path.join(package_folder, 'ldap3', '_version.py'))
exec_local = dict()
exec(version_file.read(), dict(), exec_local)
__version__ = exec_local['__version__']
__author__ = exec_local['__author__']
__email__ = exec_local['__email__']
__license__ = exec_local['__license__']
__url__ = exec_local['__url__']
__description__ = exec_local['__description__']
version_file.close()

setup(name=package_name,
      version=__version__,
      packages=['ldap3',
                'ldap3.core',
                'ldap3.abstract',
                'ldap3.operation',
                'ldap3.protocol',
                'ldap3.protocol.sasl',
                'ldap3.protocol.schemas',
                'ldap3.protocol.formatters',
                'ldap3.strategy',
                'ldap3.compat',
                'ldap3.utils',
                'ldap3.extend',
                'ldap3.extend.novell',
                'ldap3.extend.microsoft',
                'ldap3.extend.standard'
               ],
      package_dir={ '': package_folder },
      install_requires=['pyasn1 == 0.1.7'],
      license=__license__,
      author=__author__,
      author_email=__email__,
      description=__description__,
      keywords='python3 python2 ldap',
      url=__url__,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX :: Linux',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP']
      )
