@echo off
call %~dp0\set-repo-dir

rem See leo-editor/.mypy.ini for exclusions!
rem Always use the fast (official) version of mypy.

echo mypy-leo
py -m mypy --debug-cache leo %*
