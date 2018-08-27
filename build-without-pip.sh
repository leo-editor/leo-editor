# Issue #968 - make `python setup.py install` work again
# https://github.com/leo-editor/leo-editor/issues/968
clear
export PKG=/tmp/packages
cp leo/dist/setup_5.6.py setup.py
cp leo/dist/setup_5.6.cfg setup.cfg
cp leo/dist/leo-install.py ./

python setup.py install --root=$PKG

