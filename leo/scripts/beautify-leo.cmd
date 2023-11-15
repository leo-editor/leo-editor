@echo off
cd %~dp0..\..

echo beautify-leo

call py -m leo.core.leoAst --orange --verbose leo\core
call py -m leo.core.leoAst --orange --verbose leo\commands
call py -m leo.core.leoAst --orange --verbose leo\plugins
call py -m leo.core.leoAst --orange --verbose leo\modes
