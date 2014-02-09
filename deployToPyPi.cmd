\Python\Python33\python.exe setup.py clean
\Python\Python33\python.exe setup.py build sdist --format=gztar upload
\Python\Python33\python.exe setup.py build bdist_wininst upload
\Python\Python33\python.exe setup.py build bdist_egg upload
\Python\Python27\python.exe setup.py build bdist_egg upload