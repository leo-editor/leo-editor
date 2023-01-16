echo off
cls
cd c:\Repos\leo-editor
rem echo test-one-leo: test_cursesGui2
rem call python -m unittest leo.unittests.test_plugins.TestPlugins.test_cursesGui2 %*

rem echo test-one-leo: TestFstringify
rem call python -m unittest leo.unittests.core.test_leoAst.TestFstringify

echo test-one-leo: TestOrange.test_annotations
call python -m unittest leo.unittests.core.test_leoAst.TestOrange.test_annotations

