rd dist build pureLDAP\python3_ldap.egg-info /S /Q
\Python\Python34\python.exe setup.py clean
\Python\Python34\python.exe setup.py build sdist --format=gztar
\Python\Python34\python.exe setup.py build bdist_wininst
\Python\Python34\python.exe setup.py build bdist_wheel --universal
