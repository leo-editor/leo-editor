#@+leo-ver=5-thin
#@+node:ekr.20110605121601.17996: * @file ../plugins/qt_commands.py
'''Leo's Qt-related commands defined by @g.command.'''

import leo.core.leoGlobals as g
import datetime

#@+others
#@+node:ekr.20110605121601.18000: ** init
def init ():
    '''Top-level init function for qt_commands.py.'''
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
#@+node:tbrown.20140814090009.55874: ** style_reload command & helpers
@g.command('style-reload')
def style_reload(kwargs):
    """reload-styles command.
    
    Find the appropriate style sheet and re-apply it.

    The ReloadStyle clss replaces execution of the `stylesheet & source` node in settings files.
    """
    safe = True
    c = kwargs['c']
    if c:
        class ReloadStyle:
            #@+others
            #@+node:ekr.20140912110338.19371: *3* rs.__init__
            def __init__(self,c,safe):
                '''Ctor the ReloadStyle class.'''
                self.c = c
                self.safe = safe
                self.settings_p = g.findNodeAnywhere(c,'@settings')
                if not self.settings_p:
                    g.es("No '@settings' node found in outline.  See:")
                    g.es("http://leoeditor.com/tutorial-basics.html#configuring-leo")
            #@+node:ekr.20140912110338.19369: *3* check_stylesheet
            def check_stylesheet(self,stylesheet):
                '''check/trace the stylesheet.'''
                check = True
                trace = True and not g.unitTesting
                c = self.c
                if check:
                    sheet = g.expand_css_constants(c,stylesheet)
                    if self.safe:
                        from leo.core.leoQt import QtWidgets
                        w = QtWidgets.QFrame()
                        w.setStyleSheet(sheet)
                        used = str(w.styleSheet())
                    else:
                        c.frame.top.setStyleSheets()
                            # Calls g.expand_css_constants
                        used = str(g.app.gui.frameFactory.masterFrame.styleSheet())
                    sheet,used = self.munge(sheet),self.munge(used)
                    ok = len(sheet) == len(used)
                    if trace:
                        g.trace('match',ok,'len(sheet)',len(sheet),'len(used)',len(used))
                        if not ok:
                            g.trace('\n\n===== input stylesheet =====\n\n',sheet)
                            g.trace('\n\n===== output stylesheet =====\n\n',used)
                    return ok
                else:
                    return True
            #@+node:ekr.20140912110338.19368: *3* find_themes
            def find_themes(self):
                '''Find all theme-related nodes in the @settings tree.'''
                themes,theme_name = [],'unknown'
                for p in self.settings_p.subtree_iter():
                    if p.h.startswith('@string color_theme'):
                        theme_name = p.h.split()[-1]
                        themes.append((theme_name,p.copy()))
                    elif p.h == 'stylesheet & source':
                        theme_name = 'unknown'
                        themes.append((theme_name,p.copy()))
                return themes,theme_name
            #@+node:ekr.20140912110338.19367: *3* get_last_style_sheet
            def get_last_style_sheet(self):
                '''Return the body text of the *last* @data qt-gui-plugin-style-sheet node.'''
                sheets = [p.copy() for p in self.settings_p.subtree_iter()
                    if p.h == '@data qt-gui-plugin-style-sheet']
                if sheets:
                    if len(sheets) > 1:
                        g.es("WARNING: found multiple\n'@data qt-gui-plugin-style-sheet' nodes")
                        g.es("Using the *last* node found")
                    else:
                        g.es("Stylesheet found")
                    data_p = sheets[-1]
                    return data_p.b
                else:
                    g.es("No '@data qt-gui-plugin-style-sheet' node")
                    # g.es("Typically 'Reload Settings' is used in the Global or Personal "
                         # "settings files, 'leoSettings.leo and 'myLeoSettings.leo'")
                    return None
            #@+node:ekr.20140912110338.19366: *3* get_last_theme
            def get_last_theme(self,themes,theme_name):
                '''Return the stylesheet of the last theme.'''
                g.es("Found theme(s):")
                for name,p in themes:
                    g.es('found theme:',name)
                if len(themes) > 1:
                    g.es("WARNING: using the *last* theme found")
                theme_p = themes[-1][1]
                unl = theme_p.get_UNL()+'-->'
                seen = 0
                for i in theme_p.subtree_iter():
                    # Disable any @data qt-gui-plugin-style-sheet nodes in theme's tree.
                    if i.h == '@data qt-gui-plugin-style-sheet':
                        i.h = '@@data qt-gui-plugin-style-sheet'
                        seen += 1
                if seen == 0:
                    g.es("NOTE: Did not find compiled stylesheet for theme")
                elif seen > 1:
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
                stylesheet = '\n'.join(text)
                if self.safe:
                    g.trace('Stylesheet:\n' % stylesheet)
                else:
                    data_p = theme_p.insertAsLastChild()
                    data_p.h = '@data qt-gui-plugin-style-sheet'
                    data_p.b = stylesheet
                    g.es("Stylesheet compiled")
                return stylesheet
            #@+node:ekr.20140912110338.19365: *3* get_stylesheet
            def get_stylesheet(self):
                '''
                Scan for themes or @data qt-gui-plugin-style-sheet nodes.
                Return the text of the relevant node.
                '''
                themes,theme_name = self.find_themes()
                if themes:
                    return self.get_last_theme(themes,theme_name)
                else:
                    g.es("No theme found, assuming static stylesheet")
                    return self.get_last_style_sheet()
            #@+node:ekr.20140912110338.19372: *3* munge
            def munge(self,stylesheet):
                '''Return the stylesheet without extra whitespace.'''
                return ''.join([s.lstrip() #.replace('  ',' ')
                    for s in g.splitLines(stylesheet)])
            #@+node:ekr.20140912110338.19370: *3* run
            def run(self):
                '''The main line of the style-reload command.'''
                if not self.settings_p:
                    return
                c = self.c
                stylesheet = self.get_stylesheet()
                if not stylesheet:
                    return
                ok = self.check_stylesheet(stylesheet)
                if self.safe:
                    g.es('safe mode: no settings changed',color='blue')
                else:
                    # Reload the settings from this file.
                    g.es('reloading settings',color='blue')
                    shortcuts,settings = g.app.loadManager.createSettingsDicts(c,True)
                    c.config.settingsDict.update(settings)
                    c.redraw()
            #@-others
        ReloadStyle(c,safe).run()
#@-others
#@-leo
