echo off
cd c:\Repos\leo-editor

rem See leo-editor/.mypy.ini for exclusions!
rem Always use the fast (official) version of mypy.

echo mypy-leo
python -m mypy --debug-cache leo %*
