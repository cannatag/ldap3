CALL venv\Scripts\activate.bat
rd dist build ldap3.egg-info /S /Q
python setup.py clean
python setup.py build sdist --format=gztar
python setup.py build bdist_wininst
python setup.py build bdist_wheel --universal
py -2.6 setup.py bdist_egg
py -2.7 setup.py bdist_egg
python setup.py bdist_egg
