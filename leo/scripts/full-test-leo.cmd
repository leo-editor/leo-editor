@echo off
cls
cd %~dp0..\..

rem Run all of Leo's pre-commit tests.

call tbo.cmd --all --beautified --report --write
call python312 -m unittest
call ruff-leo.cmd
call mypy-leo.cmd
echo Done!
