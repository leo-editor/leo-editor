@setlocal
pushd %~dp0
@set prompt=$G$S
pushd ..\..
rd /s/q build dist
rd /s/q *.egg-info
pyinstaller leo\dist\leo.spec
@pushd dist
@rem 7z x *.whl > nul
@start .
@popd
