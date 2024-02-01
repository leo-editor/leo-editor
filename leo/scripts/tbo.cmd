
@echo off
cls
cd %~dp0..\..

rem Use leoTokens.py to beautify all files.

IF [%1]==[-h] goto help
IF [%1]==[--help] goto help

:tbo:
echo tbo [%*]
call python312 -m leo.core.leoTokens leo\core %*
call python312 -m leo.core.leoTokens leo\commands %*
call python312 -m leo.core.leoTokens leo\plugins\importers %*
call python312 -m leo.core.leoTokens leo\plugins\writers %*
goto done

:help:
call python312 -m leo.core.leoTokens  --help

:done:
