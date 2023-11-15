@echo off
cd %~dp0..\..
--verbose 
echo beautify-leo
call py -m leo.core.leoAst --orange --force --verbose leo\core
call py -m leo.core.leoAst --orange --force --verbose leo\commands
call py -m leo.core.leoAst --orange --force --verbose leo\plugins\importers
call py -m leo.core.leoAst --orange --force --verbose leo\plugins\writers

rem Never force the following:
call py -m leo.core.leoAst --orange --verbose leo\plugins
call py -m leo.core.leoAst --orange --verbose leo\modes
