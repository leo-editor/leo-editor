echo off
cd C:\Repos\leo-editor
call python -m leo.core.leoAst --orange --recursive leo\core
call python -m leo.core.leoAst --orange --recursive leo\commands
call python -m leo.core.leoAst --orange --recursive leo\plugins\importers
call python -m leo.core.leoAst --orange --recursive leo\plugins\writers
