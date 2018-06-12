#!/bin/bash
set -e -x

# Remove python versions we won't build against
ls -al /opt/python/
#rm -rf /opt/python/cp26-*
#rm -rf /opt/python/cp27-*
rm -rf /opt/python/cp33-*
rm -rf /opt/python/cp34-*
ls -al /opt/python/

cd /io

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    "${PYBIN}/pip" install cython
    "${PYBIN}/pip" install -r requirements.txt
    #"${PYBIN}/pip" wheel /io/ -w wheelhouse/
    "${PYBIN}/python" setup-binary.py bdist_wheel --dist-dir=wheelhouse/$1
    # Remove the .c generated files
    "${PYBIN}/python" setup-binary.py clean -a
done

# Remove downloaded Cython wheel packages
rm -f wheelhouse/Cython*

# Bundle external shared libraries into the wheels
for whl in wheelhouse/$1/*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse
done

# Install packages and test
for PYBIN in /opt/python/*/bin/; do
    "${PYBIN}/pip" install ldap3-binary --no-index -f /io/wheelhouse || exit 1
    "${PYBIN}/pip" install nosetests
    "${PYBIN}/nosetests" -s test/
done

# Remove the pre wheel destination and the build directories
rm -rf wheelhouse/$1 build/

# Set the right ownership
chown -R $2:$3 wheelhouse/
