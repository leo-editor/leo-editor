@echo off
cd %~dp0..\..

rem: See leo-editor/setup.cfg for defaults.

echo flake8-leo
py -m flake8 %*
