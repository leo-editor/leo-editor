#@+leo-ver=5-thin
#@+node:ekr.20110605121601.17996: * @file ../plugins/qtframecommands.py
#@+<< docstring >>
#@+node:ekr.20110605121601.17997: ** << docstring >>
''' Various commands to manipulate GUI under qt
'''
#@-<< docstring >>

__version__ = '0.0'
#@+<< version history >>
#@+node:ekr.20110605121601.17998: ** << version history >>
#@@killcolor
#@+at
# 
# Put notes about each version here.
#@-<< version history >>

#@+<< imports >>
#@+node:ekr.20110605121601.17999: ** << imports >> (qtframecommands.py)
import leo.core.leoGlobals as g

# Whatever other imports your plugins uses.
#@-<< imports >>

#@+others
#@+node:ekr.20110605121601.18000: ** init
def init ():

    ok = True

    if ok:
        # g.registerHandler('start2',onStart2)
        g.plugin_signon(__name__)

    g.registerHandler("select2", onSelect)
    return ok

def onSelect(tag,keywords):
    c = keywords.get('c') or keywords.get('new_c')    
    wdg = c.frame.top.leo_body_frame
    wdg.setWindowTitle(c.p.h)

#@+node:ekr.20110605121601.18001: ** detach-editor-toggle
@g.command('detach-editor-toggle-max')
def detach_editor_toggle_max(event):
    """ Detach editor, maximize """
    c = event['c']
    detach_editor_toggle(event)
    if c.frame.detached_body_info is not None:
        wdg = c.frame.top.leo_body_frame
        wdg.showMaximized()


@g.command('detach-editor-toggle')
def detach_editor_toggle(event):
    """ Detach or undetach body editor """
    c = event['c']    
    detach = True
    try:
        if c.frame.detached_body_info is not None:
            detach = False
    except AttributeError:
        pass

    if detach:
        detach_editor(c)
    else:
        undetach_editor(c)

def detach_editor(c):
    wdg = c.frame.top.leo_body_frame
    parent = wdg.parent()
    if parent is None:
        # just show if already detached
        wdg.show()
        return

    c.frame.detached_body_info = parent, parent.sizes()
    wdg.setParent(None)

    sheet = c.config.getData('qt-gui-plugin-style-sheet')
    if sheet:
        sheet = '\n'.join(sheet)
        wdg.setStyleSheet(sheet)

    wdg.show()

def undetach_editor(c):
    wdg = c.frame.top.leo_body_frame
    parent, sizes = c.frame.detached_body_info
    parent.insertWidget(0,wdg)
    wdg.show()
    parent.setSizes(sizes)
    c.frame.detached_body_info = None

#@-others
#@-leo
