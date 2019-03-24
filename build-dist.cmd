rd dist build ldap3.egg-info /S /Q
py -3 setup.py clean
py -3 setup.py build sdist --format=gztar
py -3 setup.py build bdist_wininst
py -3 setup.py build bdist_wheel --universal
py -2.6 setup.py bdist_egg
py -2.7 setup.py bdist_egg
py -3 setup.py bdist_egg
