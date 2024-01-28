
@echo off
cls
-cd %~dp0..\..

rem leo/scripts/tbo.cmd.
rem This file runs Leo's token-based beautifier in leoTokens.py.
rem This file contains four sub-scripts. See the :start: label below.

rem --diff now prevents changes.

rem start1: one file, with diffs
rem start2: Production
rem start3: Performance tests
rem start4: See what files have changed

goto start2

:start1:

rem One file, with diffs
echo tbo.cmd --diff --force --verbose leoGlobals.py

call python312 -m leo.core.leoTokens --orange --diff --force --verbose leo\core\leoGlobals.py
goto done


:start2:

rem Production
echo tbo.cmd --force

call python312 -m leo.core.leoTokens --orange --force leo\core
call python312 -m leo.core.leoTokens --orange --force leo\commands

call python312 -m leo.core.leoTokens --orange --force leo\plugins\importers
call python312 -m leo.core.leoTokens --orange --force leo\plugins\writers
goto done

:start3:

rem Performance tests.
echo tbo.cmd --force --silent

call python312 -m leo.core.leoTokens --orange --force --silent leo\core
call python312 -m leo.core.leoTokens --orange --force --silent leo\commands

call python312 -m leo.core.leoTokens --orange --force --silent leo\plugins\importers
call python312 -m leo.core.leoTokens --orange --force --silent leo\plugins\writers
goto done

:start4:

rem --force  # See changed files
echo tbo.cmd --diff --force --verbose

call python312 -m leo.core.leoTokens --orange --force leo\core
call python312 -m leo.core.leoTokens --orange --force leo\commands

call python312 -m leo.core.leoTokens --orange --force leo\plugins\importers
call python312 -m leo.core.leoTokens --orange --force leo\plugins\writers
goto done

:done:

rem call python312 -m leo.core.leoTokens --orange --force --silent leo\plugins
rem call python312 -m leo.core.leoTokens --orange --force --silent leo\modes
