@setlocal
@set prompt=$G$S
rd /s/q build dist
rd /s/q *.egg-info
python setup.py bdist_wheel
@pushd dist
7z x *.whl > nul
@start .
@popd
