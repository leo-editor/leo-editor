@echo off
cls
call %~dp0\set-repo-dir

echo test-one-leo
call py -m unittest leo.unittests.core.test_leoGlobals.TestGlobals.test_g_handleScriptException
