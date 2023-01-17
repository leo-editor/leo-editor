echo off
cls
cd c:\Repos\leo-editor
rem echo test-one-leo: test_cursesGui2
rem call python -m unittest leo.unittests.test_plugins.TestPlugins.test_cursesGui2 %*

rem echo test-one-leo: TestFstringify
rem call python -m unittest leo.unittests.core.test_leoAst.TestFstringify

rem echo test-one-leo: TestOrange.test_annotations
rem call python -m unittest leo.unittests.core.test_leoAst.TestOrange.test_annotations

rem echo test-one-leo: TestOrange.test_bug_1429
rem call python -m unittest leo.unittests.core.test_leoAst.TestOrange.test_bug_1429

rem echo test-one-leo: TestOrange.test_one_line_pet_peeves
rem call python -m unittest leo.unittests.core.test_leoAst.TestOrange.test_one_line_pet_peeves

rem echo test-one-leo: TestIterative.test_one_line_pet_peeves
rem call python -m unittest leo.unittests.core.test_leoAst.TestIterative.test_one_line_pet_peeves

echo test-one-leo: TestOrange
call python -m unittest leo.unittests.core.test_leoAst.TestOrange


