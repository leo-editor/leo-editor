@echo off
call %~dp0\set-repo-dir

echo pylint-leo
time /T
call py -m pylint leo --extension-pkg-allow-list=PyQt6.QtCore,PyQt6.QtGui,PyQt6.QtWidgets %*
time /T
