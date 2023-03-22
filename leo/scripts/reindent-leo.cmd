@echo off
:: Save path to reindent.py to a file .leo\reindent-path.txt
py %~dp0\find-reindent.py

set PATH_FILE=%USERPROFILE%\.leo\reindent-path.txt
set /P "REINDENT_PATH="< %PATH_FILE%

if "%REINDENT_PATH%"=="" goto no_reindent
echo re-indenting
py %REINDENT_PATH% -r leo
goto done

:no_reindent
echo Cannot find reindent.py, skipping reindentation

:done

