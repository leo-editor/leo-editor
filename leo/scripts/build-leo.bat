@:: Build source distribution and wheel
@:: typically used for deploying to PyPi.org and installing Leo with Pip
pushd %~dp0..\..
python setup.py sdist bdist_wheel |findstr /v "^creating ^adding ^copying ^creating ^byte-compiling"
start dist
popd
