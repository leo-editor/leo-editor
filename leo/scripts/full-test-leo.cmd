echo off
cls
cd C:\Repos\leo-editor
echo reindent
call reindent leo
echo beautify
call beautify-leo.cmd
echo unittests
call python -m unittest
echo.
echo mp
call mp-leo.cmd
echo.
echo flake8
call python -m flake8
echo pylint
call pylint-leo.cmd
echo.
echo Done!
