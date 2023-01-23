echo off
cls
cd c:\Repos\leo-editor

rem echo test-one-leo: TestPlugins.test_cursesGui2
rem call python -m unittest leo.unittests.test_plugins.TestPlugins.test_cursesGui2 %*

rem echo test-one-leo: test_leoAst.TestFstringify
rem call python -m unittest leo.unittests.core.test_leoAst.TestFstringify

rem echo test-one-leo: test_leoAst.TestOrange
rem call python -m unittest leo.unittests.core.test_leoAst.TestOrange

echo test-one-leo: test_importers.TestHtml.test_structure
call python -m unittest leo.unittests.test_importers.TestHtml.test_structure




