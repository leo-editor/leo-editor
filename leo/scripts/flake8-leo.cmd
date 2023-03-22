@echo off
call %~dp0\set-repo-dir

rem: See leo-editor/setup.cfg for defaults.

echo flake8-leo
py -m flake8 %*
