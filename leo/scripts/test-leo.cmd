echo off
call set-repo-dir

echo test-leo
py -m unittest %*
