echo off
cls
cd c:\Repos\leo-editor

rem echo test-one-leo: TestHtml.test_brython
rem call python -m unittest leo.unittests.test_importers.TestHtml.test_brython

rem echo test-one-leo: test_leoFind.TestFind
rem call python -m unittest leo.unittests.core.test_leoFind.TestFind

rem echo test-one-leo: test_CheckerCommands.TestFind.test_check_nodes
rem call python -m unittest leo.unittests.commands.test_checkerCommands.TestChecker.test_check_nodes

echo test-one-leo: test_leoFind.TestFind
call python -m unittest leo.unittests.core.test_leoGlobals.TestGlobals.test_g_handleScriptException
