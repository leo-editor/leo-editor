#!/usr/bin/python
#coding=utf-8
#@+leo-ver=5-thin
#@+node:bob.20170311140807.1: * @file babel.py
#@@first
#@@first
#@@language python
#@@tabwidth -4

#@+<< version >>
#@+node:bob.20170311140807.2: ** << version >>
__version__ = '1.0.0'
#@-<< version >>
#@+<< errorList >>
#@+node:bob.20170819121708.1: ** << errorList >>
errorList = list()
#@-<< errorList >>
#@+<< imports >>
#@+node:bob.20170311140940.1: ** << imports >>
try:
    import os.path
    import six

    import leo.core.leoGlobals as leoG

    from leo.plugins.leo_babel import babel_api
    from leo.plugins.leo_babel import babel_lib

except ImportError as err:
    errMsg = ('Python Packages required by Leo-Babel are missing.\n'
        'Importing Python module {0} failed.'.format(err.name))
    print(errMsg)
    errorList.append(errMsg)
    raise ImportError(errMsg)
#@-<< imports >>
#@+<< documentation >>
#@+node:bob.20170502131205.1: ** << documentation >>
with open(os.path.join(os.path.dirname(__file__), 'doc', 'Leo-Babel.rst'), 'r') as fd_doc:
    __doc__ = """
    {0}
    """.format(fd_doc.read())
#@-<< documentation >>

#@+others
#@+node:bob.20170720150451.1: ** init()
def init ():
    leoG.registerHandler('after-create-leo-frame', onCreate)
    leoG.plugin_signon(__name__)
    return True
#@+node:bob.20170720150504.1: ** onCreate()
def onCreate (tag, keys):

    cmdr = keys.get('c')
    if not cmdr: return

    if six.PY2:
        errorList.append('Leo-Babel requires Python 3')

    if not leoG.app.gui.guiName() in ('qt', 'nullGui'):
        errorList.append('Leo-Babel requires PyQt as the Leo-Editor Graphical User Interface.  '
            'But Leo-Babel runs automated tests with Leo-Bridge.')

    if errorList:
        errorList.reverse()
        while errorList:
            errMsg = errorList.pop()
            leoG.es_print_error(errMsg)
        raise babel_api.BABEL_ERROR

    babelG = babel_api.BabelGlobals()
    leoG.user_dict['leo_babel'] = babelG
    cmdr.k.registerCommand('babel-menu-p', babel_lib.babelMenu)
    cmdr.k.registerCommand('babel-exec-p', babel_lib.babelExec)

#@-others
#@-leo
