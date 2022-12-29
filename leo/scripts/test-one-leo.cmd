echo off
cls
cd c:\Repos\leo-editor
echo test-one-leo: test_cursesGui2
call python -m unittest leo.unittests.test_plugins.TestPlugins.test_cursesGui2 %*
