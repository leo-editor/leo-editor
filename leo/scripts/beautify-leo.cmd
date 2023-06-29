@echo off
cd %~dp0..\..

echo beautify-leo
call py -m leo.core.leoAst --orange --recursive leo\core
call py -m leo.core.leoAst --orange --recursive leo\commands
call py -m leo.core.leoAst --orange --recursive leo\plugins\importers
call py -m leo.core.leoAst --orange --recursive leo\plugins\writers
rem call py -m leo.core.leoAst --orange --recursive leo\modes

