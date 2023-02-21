echo off
cls
cd c:\Repos\leo-editor

rem echo test-one-leo: TestHtml.test_brython
rem call python -m unittest leo.unittests.test_importers.TestHtml.test_brython

rem echo test-one-leo: test_leoFind.TestFind
rem call python -m unittest leo.unittests.core.test_leoFind.TestFind

echo test-one-leo: test_CheckerCommands.TestFind.test_check_nodes
call python -m unittest leo.unittests.commands.test_checkerCommands.TestChecker.test_check_nodes
