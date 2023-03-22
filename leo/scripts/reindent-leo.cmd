@echo off
call %~dp0\set-repo-dir

:: Save path to reindent.py to a file .leo\reindent-path.txt
call py %~dp0\find-reindent.py

set PATH_FILE=%USERPROFILE%\.leo\reindent-path.txt
set /P "REINDENT_PATH="< %PATH_FILE%

:: echo %REINDENT_PATH%

if "%REINDENT_PATH%"=="" goto no_reindent

echo reindent leo\core
call py %REINDENT_PATH% -r leo\core
echo reindent leo\commands
call py %REINDENT_PATH% -r leo\commands
goto done

:no_reindent
echo Cannot find reindent.py, skipping reindentation

:done
