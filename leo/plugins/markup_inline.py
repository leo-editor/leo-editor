#@+leo-ver=5-thin
#@+node:tbrown.20130930160706.23451: * @file markup_inline.py
#@@language python
"""
Commands to go with keybindings in @settings-->@keys-->@shortcuts
to implement Ctrl-B,I,U Bold Italic Underline markup in plain text.
RST flavored, could be made language aware.

Key bindings would be something like::

    markup-inline-bold ! body = Ctrl-B
    markup-inline-italic ! body = Ctrl-I
    markup-inline-underline ! body = Ctrl-U

"""

import leo.core.leoGlobals as g

def init():
    g.plugin_signon(__name__)
    return True

def markup_inline(c, kind='unknown'):

    # find out if last action was open or close, creates entry if needed
    last_type = c.user_dict.setdefault(
        'markup_inline', {'last': 'close'})['last']

    p = c.p

    delim = {
        'bold': ('**','**'),
        'italic': ('*','*'),
        'underline': (':ul:`','`'),
    }[kind]

    if c.frame.body.bodyCtrl.hasSelection():
        c.user_dict['markup_inline']['last'] = 'close'
        i,j = c.frame.body.bodyCtrl.getSelectionRange()
        txt = c.frame.body.bodyCtrl.getAllText()
        p.b = "".join([
            txt[:i],
            delim[0],
            txt[i:j],
            delim[1],
            txt[j:],
        ])
        c.frame.body.bodyCtrl.setAllText(p.b)
        c.frame.body.bodyCtrl.setInsertPoint(j+len(delim[0])+len(delim[1]))
    else:
        i = c.frame.body.bodyCtrl.getInsertPoint()
        txt = c.frame.body.bodyCtrl.getAllText()
        if last_type == 'close':
            delim = delim[0]
            c.user_dict['markup_inline']['last'] = 'open'
        else:
            delim = delim[1]
            c.user_dict['markup_inline']['last'] = 'close'
        p.b = "".join([
            txt[:i],
            delim,
            txt[i:]
        ])
        c.frame.body.bodyCtrl.setAllText(p.b)
        c.frame.body.bodyCtrl.setInsertPoint(i+len(delim))
    c.setChanged()
    p.setDirty(True)
    c.redraw()
    c.bodyWantsFocusNow()

def cmd_bold(c):
    markup_inline(c, kind='bold')

def cmd_italic(c):
    markup_inline(c, kind='italic')

def cmd_underline(c):
    markup_inline(c, kind='underline')
#@-leo
