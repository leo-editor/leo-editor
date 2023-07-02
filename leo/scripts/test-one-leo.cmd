@echo off
cls
cd %~dp0..\..

echo test-one-leo
call py -m unittest leo.unittests.core.test_leoGlobals.TestGlobals.test_g_handleScriptException
