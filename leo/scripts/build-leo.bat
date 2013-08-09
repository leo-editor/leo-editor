REM @+leo-ver=5-thin
REM @+node:maphew.20130809155103.2863: * @file build-leo.bat
REM @+at Create a ~Setuptools~ Windows binary installer package
REM @@c
pushd ..\..
python setup.py sdist
python setup.py bdist_wininst --user-access-control=auto --bitmap leo\Icons\SplashScreen-installer.bmp
start dist
REM @-leo
