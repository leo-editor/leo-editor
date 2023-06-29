@echo off
cd %~dp0..\..

echo black leo.core
call py -m black --skip-string-normalization leo\core
