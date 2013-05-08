#@+leo-ver=5-thin
#@+node:maphew.20130505160115.1636: * @file leo-editor/build-leo.bat
python setup.py sdist
python setup.py bdist_wininst --user-access-control=auto --bitmap leo\Icons\SplashScreen-installer.bmp
start dist
#@-leo
