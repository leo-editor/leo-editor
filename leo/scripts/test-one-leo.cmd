echo off
cls
cd c:\Repos\leo-editor

rem echo test-one-leo: TestHtml.test_brython
rem call python -m unittest leo.unittests.test_importers.TestHtml.test_brython

echo test-one-leo: test_leoFind.TestFind.test_find_def and test_find_var
call python -m unittest leo.unittests.core.test_leoFind.TestFind.test_find_def
call python -m unittest leo.unittests.core.test_leoFind.TestFind.test_find_var
