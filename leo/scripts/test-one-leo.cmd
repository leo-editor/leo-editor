echo off
cls
cd c:\Repos\leo-editor

echo test-one-leo: test_leoFind.TestFind
call python -m unittest leo.unittests.core.test_leoGlobals.TestGlobals.test_g_handleScriptException
