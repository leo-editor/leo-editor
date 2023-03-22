echo off
::cd c:\Repos\leo-editor
call set-repo-dir

echo reindent-leo leo/core
call reindent leo/core

echo reindent-leo leo/commands
call reindent leo/commands
