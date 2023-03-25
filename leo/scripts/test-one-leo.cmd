@echo off
cls
call %~dp0\set-repo-dir

echo test-one-leo: test_leoFind.test_g_findUnl
call py -m unittest leo.unittests.core.test_leoGlobals.TestGlobals.test_g_findUnl
