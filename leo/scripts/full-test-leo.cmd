echo off
cls
cd C:\Repos\leo-editor

echo full-test-leo
call reindent-leo.cmd
call beautify-leo.cmd
call test-leo.cmd
echo.
call mypy-leo.cmd
echo.
call flake8-leo.cmd
call pylint-leo.cmd
echo.
echo Done!
