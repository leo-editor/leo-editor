
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
call python312 -m leo.core.leoTokens leo\modes %*

call python312 -m leo.core.leoTokens leo\unittests\core %*
call python312 -m leo.core.leoTokens leo\unittests\commands %*
call python312 -m leo.core.leoTokens leo\unittests\plugins %*
call python312 -m leo.core.leoTokens leo\unittests\misc_tests %*
goto done

:help:
call python312 -m leo.core.leoTokens  --help

:done:
