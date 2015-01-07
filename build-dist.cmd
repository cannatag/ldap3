rd dist build ldap3.egg-info /S /Q
\Python\Python34\python.exe setup.py clean
\Python\Python34\python.exe setup.py build sdist --format=gztar
\Python\Python34\python.exe setup.py build bdist_wininst
\Python\Python34\python.exe setup.py build bdist_wheel --universal
\Python\Python26\python.exe setup.py bdist_egg
\Python\Python27\python.exe setup.py bdist_egg
\Python\Python34\python.exe setup.py bdist_egg
