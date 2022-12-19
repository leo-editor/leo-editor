echo off
cls
cd c:\Repos\leo-editor
echo leo/scripts/test-one-leo.cmd: test_cursesGui2
call python -m unittest leo.unittests.test_plugins.TestPlugins.test_cursesGui2 %*
