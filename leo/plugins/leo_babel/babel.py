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
#@+<< imports >>
#@+node:bob.20170311140940.1: ** << imports >>
try:
    import os.path
    import six

    import leo.core.leoGlobals as leoG

    from leo.plugins.leo_babel import babel_api
    from leo.plugins.leo_babel import babel_lib

except ImportError as err:
    raise ImportError(f'Python Package required by Leo-Babel is missing\n{err}')
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
def init():
    leoG.registerHandler('after-create-leo-frame', onCreate)
    leoG.plugin_signon(__name__)
    return True
#@+node:bob.20170720150504.1: ** onCreate()
def onCreate(tag, keys):

    cmdr = keys.get('c')
    if not cmdr: return

    if six.PY2:
        raise babel_api.BABEL_ERROR('Leo-Babel requires Python 3')

    if not leoG.app.gui.guiName() in ('qt', 'nullGui'):
        raise babel_api.BABEL_ERROR('Leo-Babel requires PyQt as the Leo-Editor Graphical User Interface.  '
            'But Leo-Babel runs automated tests with Leo-Bridge.')

    babelG = babel_api.BabelGlobals()
    leoG.user_dict['leo_babel'] = babelG
    cmdr.k.registerCommand('babel-menu-p', babel_lib.babelMenu)
    cmdr.k.registerCommand('babel-exec-p', babel_lib.babelExec)

#@-others
#@-leo
