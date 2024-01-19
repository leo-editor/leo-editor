
rem leo/scripts/tbo.cmd.
rem This file runs Leo's token-based beautifier in leoTokens.py.
rem This file contains four sub-scripts. See the :start: label below.

@echo off
cls
cd %~dp0..\..

:start:

rem Execute one of the four sub-scripts:
rem start1: one file
rem start2: diffs
rem start3: Performance tests
rem start4: See what files have changed

goto start3

:start1:

rem One file, with diffs
echo tbo.cmd --diff --force --verbose leoColorizer

call python312 -m leo.core.leoTokens --orange --diff --force --verbose leo\core\leoColorizer.py
goto done

:start2:

rem diffs
echo tbo.cmd --diff --force --verbose

call python312 -m leo.core.leoTokens --orange --diff --force --verbose leo\core
call python312 -m leo.core.leoTokens --orange --diff --force --verbose leo\commands

call python312 -m leo.core.leoTokens --orange --diff --force --verbose leo\plugins\importers
call python312 -m leo.core.leoTokens --orange --diff --force --verbose leo\plugins\writers
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

echo tbo.cmd --diff --force --verbose

call python312 -m leo.core.leoTokens --orange --force leo\core
call python312 -m leo.core.leoTokens --orange --force leo\commands

call python312 -m leo.core.leoTokens --orange --force leo\plugins\importers
call python312 -m leo.core.leoTokens --orange --force leo\plugins\writers
goto done

:done:
