echo off
cls
cd c:\Repos\leo-editor

rem echo test-one-leo: test_leoFind.TestFind
rem call python -m unittest leo.unittests.core.test_leoFind.TestFind

echo test-one-leo: TestHtml.test_brython
call python -m unittest leo.unittests.test_importers.TestHtml.test_brython









