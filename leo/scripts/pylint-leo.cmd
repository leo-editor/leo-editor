echo off
time /T
call python -m pylint leo --extension-pkg-allow-list=PyQt6.QtCore,PyQt6.QtGui,PyQt6.QtWidgets %*
time /T
