from os import path
from datetime import datetime
from platform import uname, python_version, python_build, python_compiler
from json import load

# reads _version.json

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

# creates version.py from _version.json

with open(path.join(package_name, 'version.py'), 'w+') as project_version_file:
    project_version_file.write('\n'.join([
        '# THIS FILE IS AUTO-GENERATED. PLEASE DO NOT MODIFY'
        '# version file for ' + package_name,
        '# generated on ' + datetime.now().__str__(),
        '# on system ' + str(uname()),
        '# with Python ' + python_version() + ' - ' + str(python_build()) + ' - ' + python_compiler(),
        '#',
        '__version__ = ' + "'" + version + "'",
        '__author__ = ' + "'" + author + "'",
        '__email__ = ' + "'" + email + "'",
        '__url__ = ' + "'" + url + "'",
        '__description__ = ' + "'" + description + "'",
        '__status__ = ' + "'" + status + "'",
        '__license__ = ' + "'" + license + "'"]))

# update README.rst from _changelog.txt

with open(path.join('README.rst'), 'r+') as project_readme_file, \
        open(path.join('_changelog.txt'), 'r') as project_changelog_file:
    readme = project_readme_file.read()
    changelog_identifier = '\nChangelog\n---------\n\n'
    changelog_position = readme.find(changelog_identifier)
    if changelog_position > 0:
        updated_readme = readme[0: changelog_position + len(changelog_identifier)] + project_changelog_file.read()
        project_readme_file.write(updated_readme)
