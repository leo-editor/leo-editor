#@+leo-ver=5-thin
#@+node:ekr.20110605121601.17996: * @file ../plugins/qt_commands.py
'''Leo's Qt-related commands defined by @g.command.'''
import leo.core.leoGlobals as g
#@+others
#@+node:ekr.20110605121601.18000: ** init
def init():
    '''Top-level init function for qt_commands.py.'''
    ok = True
    g.plugin_signon(__name__)
    g.registerHandler("select2", onSelect)
    return ok

def onSelect(tag, keywords):
    c = keywords.get('c') or keywords.get('new_c')
    wdg = c.frame.top.leo_body_frame
    wdg.setWindowTitle(c.p.h)
#@+node:ekr.20110605121601.18001: ** detach-editor-toggle (qt_commands.py)
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
    else:
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
    parent.insertWidget(0, wdg)
    wdg.show()
    parent.setSizes(sizes)
    c.frame.detached_body_info = None
#@+node:tbrown.20140620095406.40066: ** gui-show/hide/toggle (qt_commands.py)
# create the commands gui-<menu|iconbar|statusbar|minibuffer>-<hide|show>
widgets = [
    ('menu', lambda c: c.frame.top.menuBar()),
    ('iconbar', lambda c: c.frame.top.iconBar),
    ('statusbar', lambda c: c.frame.top.statusBar),
    ('minibuffer', lambda c: c.frame.miniBufferWidget.widget.parent()),
    ('tabbar', lambda c: g.app.gui.frameFactory.masterFrame.tabBar()),
]
for vis in 'hide', 'show', 'toggle':
    for name, widget in widgets:

        def dovis(event, widget=widget, vis=vis):
            c = event['c']
            w = widget(c)
            if vis == 'toggle':
                vis = 'hide' if w.isVisible() else 'show'
            # Executes either w.hide() or w.show()
            getattr(w, vis)()

        g.command("gui-%s-%s" % (name, vis))(dovis)

    def doall(event, vis=vis):
        c = event['c']
        for name, widget in widgets:
            w = widget(c)
            if vis == 'toggle':
                # note, this *intentionally* toggles all to on/off
                # based on the state of the first
                vis = 'hide' if w.isVisible() else 'show'
            getattr(w, vis)()

    g.command("gui-all-%s" % vis)(doall)
#@+node:tbrown.20140814090009.55874: ** style_sheet commands (qt_commands.py)
#@+node:ekr.20140918124632.17893: *3* print-style-sheet
@g.command('print-style-sheet')
def print_style_sheet(event):
    '''print-style-sheet command.'''
    c = event.get('c')
    if c:
        c.styleSheetManager.print_style_sheet()
#@+node:ekr.20140918124632.17891: *3* style-reload
@g.command('style-reload')
def style_reload(event):
    """reload-styles command.

    Find the appropriate style sheet and re-apply it.

    This replaces execution of the `stylesheet & source` node in settings files.
    """
    c = event.get('c')
    if c and c.styleSheetManager:
        c.reloadSettings()
            # Call ssm.reload_settings after reloading all settings.
#@+node:ekr.20140918124632.17892: *3* style-set-selected
@g.command('style-set-selected')
def style_set_selected(event):
    '''style-set-selected command. Set the global stylesheet to c.p.b. (For testing)'''
    c = event.get('c')
    if c:
        c.styleSheetManager.set_selected_style_sheet()
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
