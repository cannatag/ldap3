"""
"""

# Created on 2013.07.11
#
# Author: Giovanni Cannata
#
# Copyright 2013 - 2018 Giovanni Cannata
#
# This file is part of ldap3.
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

import os
import glob
from setuptools import setup
from distutils.command.clean import clean
from json import load

version_dict = load(open('_version.json', 'r'))
version = str(version_dict['version'])
author = str(version_dict['author'])
email = str(version_dict['email'])
license = str(version_dict['license'])
url = str(version_dict['url'])
description = str(version_dict['description'])
package_name = str(version_dict['package_name'])
package_folder = str(version_dict['package_folder'])
status = str(version_dict['status'])

long_description = str(open('README.rst').read())
packages=['ldap3',
          'ldap3.abstract',
          'ldap3.core',
          'ldap3.operation',
          'ldap3.protocol',
          'ldap3.protocol.sasl',
          'ldap3.protocol.schemas',
          'ldap3.protocol.formatters',
          'ldap3.strategy',
          'ldap3.utils',
          'ldap3.extend',
          'ldap3.extend.novell',
          'ldap3.extend.microsoft',
          'ldap3.extend.standard']

setup_kwargs = {'packages': packages,
                'package_dir': {'': package_folder}}

try:
    from Cython.Build import cythonize
    HAS_CYTHON = True
except ImportError:
    HAS_CYTHON = False

if 'LDAP3_CYTHON_COMPILE' in os.environ and HAS_CYTHON is True:
    import sys
    import multiprocessing
    import multiprocessing.pool
    from setuptools import Extension
    from distutils.command.build_py import build_py
    from distutils.command.build_ext import build_ext
    # Change to source's directory prior to running any command
    try:
        SETUP_DIRNAME = os.path.dirname(__file__)
    except NameError:
        # We're most likely being frozen and __file__ triggered this NameError
        # Let's work around that
        SETUP_DIRNAME = os.path.dirname(sys.argv[0])
    if SETUP_DIRNAME != '':
        os.chdir(SETUP_DIRNAME)

    SETUP_DIRNAME = os.path.abspath(SETUP_DIRNAME)

    def find_ext():
        for package in ('ldap3',):
            for root, _, files in os.walk(os.path.join(SETUP_DIRNAME, package)):
                commonprefix = os.path.commonprefix([SETUP_DIRNAME, root])
                for filename in files:
                    full = os.path.join(root, filename)
                    if not filename.endswith(('.py', '.c')):
                        continue
                    if filename in ('__init__.py',):
                        continue
                    relpath = os.path.join(root, filename).split(commonprefix)[-1][1:]
                    module = os.path.splitext(relpath)[0].replace(os.sep, '.')
                    yield Extension(module, [full])

    def discover_packages():
        modules = []
        pkg_data = {}
        pkg_dir = {}
        for package in ('ldap3',):
            for root, _, files in os.walk(os.path.join(SETUP_DIRNAME, package)):
                if '__init__.py' not in files:
                    continue
                pdir = os.path.relpath(root, SETUP_DIRNAME)
                modname = pdir.replace(os.sep, '.')
                modules.append(modname)
                pkg_data.setdefault(modname, []).append('*.so')
                pkg_dir[modname] = pdir
        return modules, pkg_dir, pkg_data

    ext_modules = cythonize(list(find_ext()), nthreads=multiprocessing.cpu_count())


    class BuildPy(build_py):

        def find_package_modules(self, package, package_dir):
            modules = build_py.find_package_modules(self, package, package_dir)
            for package, module, filename in modules:
                if module not in ('__init__',):
                    # We only want __init__ python files
                    # All others will be built as extensions
                    continue
                yield package, module, filename


    class BuildExt(build_ext):

        def run(self):
            self.extensions = ext_modules
            build_ext.run(self)

        def build_extensions(self):
            multiprocessing.pool.ThreadPool(
                processes=multiprocessing.cpu_count()).map(
                    self.build_extension, self.extensions)

    packages, package_dir, package_data = discover_packages()
    setup_kwargs['packages'] = packages
    setup_kwargs['package_dir'] = package_dir
    setup_kwargs['package_data'] = package_data
    setup_kwargs['cmdclass'] = {'build_py': BuildPy, 'build_ext': BuildExt}
    setup_kwargs['ext_modules'] = ext_modules
    setup_kwargs['zip_safe'] = False


class Clean(clean):
    def run(self):
        clean.run(self)
        # Let's clean compiled *.py[c,o] *.c *.so
        for subdir in ('ldap3',):
            root = os.path.join(os.path.dirname(__file__), subdir)
            for dirname, dirs, _ in os.walk(root):
                for to_remove_filename in glob.glob('{0}/*.py[ocx]'.format(dirname)):
                    os.remove(to_remove_filename)
                for to_remove_filename in glob.glob('{0}/*.c'.format(dirname)):
                    os.remove(to_remove_filename)
                for to_remove_filename in glob.glob('{0}/*.so'.format(dirname)):
                    os.remove(to_remove_filename)
                for dir_ in dirs:
                    if dir_ == '__pycache__':
                        shutil.rmtree(os.path.join(dirname, dir_))


setup_kwargs['cmdclass'] = {'clean': Clean}


setup(name=package_name,
      version=version,
      install_requires=[i.strip() for i in open('requirements.txt').readlines()],
      license=license,
      author=author,
      author_email=email,
      description=description,
      long_description=long_description,
      keywords='python3 python2 ldap',
      url=url,
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX :: Linux',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP'],
      **setup_kwargs
      )
