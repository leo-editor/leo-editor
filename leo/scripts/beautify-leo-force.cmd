@echo off
cd %~dp0..\..

echo beautify-leo

call py -m leo.core.leoAst --orange --force --verbose leo\core
call py -m leo.core.leoAst --orange --force --verbose leo\commands

rem It's ok to beautify everything:

call py -m leo.core.leoAst --orange --verbose leo\plugins
call py -m leo.core.leoAst --orange --verbose leo\modes

rem call py -m leo.core.leoAst --orange --force --verbose leo\plugins\importers
rem call py -m leo.core.leoAst --orange --force --verbose leo\plugins\writers
