# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170108162404.1: * @file ../external/pyzo/leo_test.py
#@@first
'''Prototype test code for integrating pyzo into Leo.'''
#@+<< pyzo copyright >>
#@+node:ekr.20170108171806.1: ** << pyzo copyright >>
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< pyzo copyright >>
#@+<< pyzo/leo_test.py imports >>
#@+node:ekr.20170108162537.1: ** << pyzo/leo_test.py imports >>
import leo.core.leoGlobals as g
import imp
import leo.external.pyzo.base as base
# import leo.external.pyzo.highlighter as highlighter
import leo.external.pyzo.python_parser as python_parser
imp.reload(base)
# imp.reload(highlighter)
imp.reload(python_parser)
#@-<< pyzo/leo_test.py imports >>
#@+others
#@+node:ekr.20170108162608.1: ** class LeoCodeEditor
class LeoCodeEditor(base.CodeEditorBase):

    def __init__(self):
        # Must set _parser ivar before initing the base class.
        self._parser = python_parser.Parser()
        base.CodeEditorBase.__init__(self)

    def parser(self):
        return self._parser
#@+node:ekr.20170108162637.1: ** main
def main(c):
    '''main test code.'''
    codeEditor = LeoCodeEditor()
    h = codeEditor.leo_highlighter
        # widget = c.frame.body.wrapper.widget
        # h = highlighter.Highlighter(codeEditor, widget)
    h.colorer = g.NullObject()
        # Disable code in Leo's core.
    c.frame.body.colorizer.highlighter = h
#@-others
#@@language python
#@@tabwidth -4
#@-leo
