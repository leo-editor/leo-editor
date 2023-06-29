@echo off
cd %~dp0..\..

echo black leo.core
call py -m black --skip-string-normalization leo\core

rem echo.
rem echo black leo.commands
rem call python -m black --skip-string-normalization leo\commands
