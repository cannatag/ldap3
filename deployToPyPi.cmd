\Python\Python34\python.exe setup.py clean
\Python\Python34\python.exe setup.py build sdist --format=gztar upload
\Python\Python34\python.exe setup.py build bdist_wininst upload
\Python\Python34\python.exe setup.py build bdist_wheel upload
\Python\Python34\python.exe setup.py build bdist_egg upload
\Python\Python27\python.exe setup.py build bdist_egg upload
\Python\Python26\python.exe setup.py build bdist_egg upload