@:: Build source distribution and wheel
@:: typically used for deploying to PyPi.org and installing Leo with Pip
@set _p=%prompt%
@set prompt=$H
@echo This can take a 5 or more minutes, be patient with no screen output.
pushd %~dp0..\..\..
rem python setup.py --quiet sdist bdist_wheel
start dist
popd
@set prompt=%_p%
