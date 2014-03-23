"""
Created on 2013.07.11

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup

setup(name='python3-ldap',
      version='0.9.1',
      packages=['ldap3',
                'ldap3.core',
                'ldap3.abstract',
                'ldap3.operation',
                'ldap3.protocol',
                'ldap3.protocol.sasl',
                'ldap3.strategy',
                'ldap3.compat'],
      package_dir={'': 'python3-ldap'},
      install_requires=['pyasn1 >= 0.1.7'],
      license='LGPL v3',
      author='Giovanni Cannata',
      author_email='python3ldap@gmail.com',
      description='A strictly RFC 4511 conforming LDAP V3 pure Python 3 client - Python 2 compatible',
      keywords='python3 python2 ldap',
      url='https://www.assembla.com/spaces/python3-ldap',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Operating System :: Microsoft :: Windows', 'Operating System :: POSIX :: Linux',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP']
      )

