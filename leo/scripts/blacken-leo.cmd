@echo off
cd %~dp0..\..

rem not recommended!
echo black leo.core
call py -m black --skip-string-normalization leo\core
