#@+leo-ver=5-thin
#@+node:ekr.20110605121601.17996: * @file ../plugins/qt_commands.py
'''Leo's Qt-related commands defined by @g.command.'''

import leo.core.leoGlobals as g

#@+others
#@+node:ekr.20110605121601.18000: ** init
def init ():
    '''Top-level init function for qtframecommands.py.'''
    ok = True
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

#@+node:tbrown.20140620095406.40066: ** gui-show/hide/toggle commands
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
            getattr(w, vis)()
        g.command("gui-%s-%s"%(name, vis))(dovis)
        
    def doall(event, vis=vis):
        c = event['c']
        for name, widget in widgets:
            w = widget(c)
            if vis == 'toggle':
                # note, this *intentionally* toggles all to on/off
                # based on the state of the first
                vis = 'hide' if w.isVisible() else 'show'
            getattr(w, vis)()
    g.command("gui-all-%s"%vis)(doall)
#@+node:tbrown.20140814090009.55874: ** style_reload command
@g.command('style-reload')
def style_reload(kwargs):
    """reload_styles - recompile, if necessary, the stylesheet, and re-apply
    
    This method, added 20140814, is intended to replace execution of the
    `stylesheet & source` node in (my)LeoSettings.leo, and the script in the
    `@button reload-styles` node, which should just become
    `c.k.simulateCommand('style-reload')`.

    :Parameters:
    - `kwargs`: kwargs from Leo command
    
    Returns True on success, otherwise False
    """
    
    c = kwargs['c']
    
    # first, rebuild the stylesheet template from the tree, if
    # the stylesheet source is in tree form, e.g. dark themes, currently the
    # default light theme uses a single @data qt-gui-plugin-style-sheet node
    settings_p = g.findNodeAnywhere(c, '@settings')
    if not settings_p:
        # pylint: disable=fixme
        g.es("No '@settings' node found in outline")
        g.es("Please see http://leoeditor.com/FIXME.html")
        return False
    themes = []
    theme_name = 'unknown'
    for i in settings_p.subtree_iter():
        if i.h.startswith('@string color_theme'):
            theme_name = i.h.split()[-1]
        if i.h == 'stylesheet & source':
            themes.append((theme_name, i.copy()))
            theme_name = 'unknown'
    if themes:
        g.es("Found theme(s):")
        for i in themes:
            g.es("   "+i[0])
        if len(themes) > 1:
            g.es("WARNING: using the *last* theme found")
        theme_p = themes[-1][1]
        unl = theme_p.get_UNL()+'-->'
        seen = 0
        for i in theme_p.subtree_iter():
            if i.h == '@data qt-gui-plugin-style-sheet':
                i.h = '@@data qt-gui-plugin-style-sheet'
                seen += 1
        if seen == 0:
            g.es("NOTE: Did not find compiled stylesheet for theme")
        if seen > 1:
            g.es("NOTE: Found multiple compiled stylesheets for theme")
        text = [
            "/*\n  DON'T EDIT THIS, EDIT THE OTHER NODES UNDER "
            "('stylesheet & source')\n  AND RECREATE THIS BY "
            "Alt-X style-reload"
            "\n\n  AUTOMATICALLY GENERATED FROM:\n  %s\n  %s\n*/\n\n"
            % (
                theme_p.get_UNL(with_proto=True),
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            )]
        for i in theme_p.subtree_iter():
            src = i.get_UNL().replace(unl, '')
            if i.h.startswith('@data '):
                i.h = '@'+i.h
            if ('@ignore' in src) or ('@data' in src):
                continue
            text.append("/*### %s %s*/\n%s\n\n" % (
                src, '#'*(70-len(src)),
                i.b.strip()
            ))
            
        data_p = theme_p.insertAsLastChild()
        data_p.h = '@data qt-gui-plugin-style-sheet'
        data_p.b = '\n'.join(text)
        g.es("Stylesheet compiled")
        
    else:
        g.es("No theme found, assuming static stylesheet")
        sheets = [i.copy() for i in settings_p.subtree_iter()
                  if i.h == '@data qt-gui-plugin-style-sheet']
        if not sheets:
            g.es("Didn't find '@data qt-gui-plugin-style-sheet' node")
            return False
        if len(sheets) > 1:
            g.es("WARNING: found multiple\n'@data qt-gui-plugin-style-sheet' nodes")
            g.es("Using the *last* node found")
        else:
            g.es("Stylesheet found")
        data_p = sheets[-1]

    # then, reload settings from this file
    shortcuts, settings = g.app.loadManager.createSettingsDicts(c, True)
    c.config.settingsDict.update(settings)
    
    # apply the stylesheet
    c.frame.top.setStyleSheets()
    # check that our styles were applied
    used = str(g.app.gui.frameFactory.masterFrame.styleSheet())
    sheet = g.expand_css_constants(c, data_p.b)
    # Qt normalizes whitespace, so we must too
    used = ' '.join(used.split())
    sheet = ' '.join(sheet.split())
    c.redraw()
    if used != sheet:
        g.es("WARNING: styles in use do not match applied styles")
        return False
    else:
        g.es("Styles reloaded")
        return True
#@+node:tbrown.20130411145310.18857: ** zoom_in & zoom_out
@g.command("zoom-in")
def zoom_in(event=None, delta=1):
    """increase body font size by one
    
    requires that @font-size-body is being used in stylesheet
    """
    c = event.get('c')
    if c:
        c._style_deltas['font-size-body'] += delta
        ss = g.expand_css_constants(c, c.active_stylesheet)
        c.frame.body.wrapper.widget.setStyleSheet(ss)
    
@g.command("zoom-out")
def zoom_out(event=None):
    """decrease body font size by one
    
    requires that @font-size-body is being used in stylesheet
    """
    zoom_in(event=event, delta=-1)
#@-others
#@-leo
