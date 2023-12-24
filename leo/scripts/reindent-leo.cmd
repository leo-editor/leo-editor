@echo off
cd %~dp0..\..

:: Save path to reindent.py to a file .leo\reindent-path.txt
call py %~dp0\find-reindent.py

set PATH_FILE=%USERPROFILE%\.leo\reindent-path.txt
set /P "REINDENT_PATH="< %PATH_FILE%

:: echo %REINDENT_PATH%

if "%REINDENT_PATH%"=="" goto no_reindent

echo reindent-leo

rem echo reindent leo/core
call py %REINDENT_PATH% -r leo\core
rem echo reindent leo/commands
call py %REINDENT_PATH% -r leo\commands
rem echo reindent leo/plugins/importers
call py %REINDENT_PATH% -r leo\plugins\importers
rem echo reindent leo/plugins/commands
call py %REINDENT_PATH% leo\plugins\qt_commands.py
call py %REINDENT_PATH% leo\plugins\qt_events.py
call py %REINDENT_PATH% leo\plugins\qt_frame.py
call py %REINDENT_PATH% leo\plugins\qt_gui.py
call py %REINDENT_PATH% leo\plugins\qt_idle_time.py
call py %REINDENT_PATH% leo\plugins\qt_text.py
call py %REINDENT_PATH% leo\plugins\qt_tree.py
rem echo reindent leo/plugins/writers
call py %REINDENT_PATH% -r leo\plugins\writers
rem echo reindent leo/unittests
call py %REINDENT_PATH% -r leo\unittests
rem echo reindent official plugins.
call py %REINDENT_PATH% leo\plugins\indented_languages.py
goto done

:no_reindent
echo Cannot find reindent.py, skipping reindentation

:done
