#@+leo-ver=5-thin
#@+node:ekr.20110605121601.17996: * @file ../plugins/qt_commands.py
"""Leo's Qt-related commands defined by @g.command."""
from leo.core import leoGlobals as g
from leo.core import leoColor
from leo.core import leoConfig
from leo.core.leoQt import QtGui, QtWidgets
#@+others
#@+node:ekr.20110605121601.18000: ** init
def init():
    """Top-level init function for qt_commands.py."""
    ok = True
    g.plugin_signon(__name__)
    g.registerHandler("select2", onSelect)
    return ok

def onSelect(tag, keywords):
    c = keywords.get('c') or keywords.get('new_c')
    wdg = c.frame.top.leo_body_frame
    wdg.setWindowTitle(c.p.h)
#@+node:ekr.20110605121601.18001: ** qt: detach-editor-toggle & helpers
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

@g.command('detach-editor-toggle-max')
def detach_editor_toggle_max(event):
    """ Detach editor, maximize """
    c = event['c']
    detach_editor_toggle(event)
    if c.frame.detached_body_info is not None:
        wdg = c.frame.top.leo_body_frame
        wdg.showMaximized()
#@+node:ekr.20170324145714.1: *3* qt: detach_editor
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
#@+node:ekr.20170324145716.1: *3* qt: undetach_editor
def undetach_editor(c):
    wdg = c.frame.top.leo_body_frame
    parent, sizes = c.frame.detached_body_info
    parent.insertWidget(0, wdg)
    wdg.show()
    parent.setSizes(sizes)
    c.frame.detached_body_info = None
#@+node:ekr.20170324143944.2: ** qt: show-color-names
@g.command('show-color-names')
def showColorNames(event=None):
    """Put up a dialog showing color names."""
    c = event.get('c')
    template = '''
        QComboBox {
            background-color: %s;
            selection-background-color: %s;
            selection-color: black;
        }'''
    ivar = 'leo_settings_color_picker'
    if getattr(c, ivar, None):
        g.es('The color picker already exists in the icon bar.')
    else:
        color_list: list[str] = []
        box = QtWidgets.QComboBox()

        def onActivated(n, *args, **keys):
            color = color_list[n]
            sheet = template % (color, color)
            box.setStyleSheet(sheet)
            g.es("copied to clipboard:", color)
            QtWidgets.QApplication.clipboard().setText(color)

        box.activated.connect(onActivated)
        color_db = leoColor.leo_color_database
        for key in sorted(color_db):
            if not key.startswith('grey'):  # Use gray, not grey.
                val = color_db.get(key)
                color = QtGui.QColor(val)
                color_list.append(val)
                pixmap = QtGui.QPixmap(40, 40)
                pixmap.fill(color)
                icon = QtGui.QIcon(pixmap)
                box.addItem(icon, key)

        c.frame.iconBar.addWidget(box)
        setattr(c, ivar, True)
        # Do this last, so errors don't prevent re-execution.
        g.es('created color picker in icon area')
#@+node:ekr.20170324142416.1: ** qt: show-color-wheel
@g.command('show-color-wheel')
def showColorWheel(self, event=None):
    """Show a Qt color dialog."""
    c, p = self.c, self.c.p
    picker = QtWidgets.QColorDialog()
    in_color_setting = p.h.startswith('@color ')
    try:
        text = QtWidgets.QApplication.clipboard().text()
        if in_color_setting:
            text = p.h.split('=', 1)[1].strip()
        color = QtGui.QColor(text)
        picker.setCurrentColor(color)
    except(ValueError, IndexError) as e:
        g.trace('error caught', e)

    result = picker.exec_()
    if not result:
        g.es("No color selected")
    elif in_color_setting:
        udata = c.undoer.beforeChangeNodeContents(p)
        p.h = f"{p.h.split('=', 1)[0].strip()} = {picker.selectedColor().name()}"
        c.undoer.afterChangeNodeContents(p, 'change-color', udata)
    else:
        text = picker.selectedColor().name()
        g.es("copied to clipboard:", text)
        QtWidgets.QApplication.clipboard().setText(text)
#@+node:ekr.20170324143944.3: ** qt: show-fonts
@g.command('show-fonts')
def showFonts(self, event=None):
    """Open a tab in the log pane showing a font picker."""
    c, p = self.c, self.c.p
    picker = QtWidgets.QFontDialog()
    if p.h.startswith('@font'):
        (name, family, weight, slant, size) = leoConfig.parseFont(p.b)
    else:
        name, family, weight, slant, size = None, None, False, False, 12
    try:
        font = QtGui.QFont()
        if family:
            font.setFamily(family)
        font.setBold(weight)
        font.setItalic(slant)
        font.setPointSize(size)
        picker.setCurrentFont(font)
    except ValueError:
        pass
    result = picker.exec_()
    if not result:
        g.es("No font selected")
    else:
        font = picker.selectedFont()
        udata = c.undoer.beforeChangeNodeContents(p)
        comments = [x for x in g.splitLines(p.b) if x.strip().startswith('#')]
        defs = [
            '\n' if comments else '',
            f"{name}_family = {font.family()}\n",
            f"{name}_weight = {'bold' if font.bold() else 'normal'}\n",
            f"{name}_slant = {'italic' if font.italic() else 'roman'}\n",
            f"{name}_size = {font.pointSizeF()}\n"
        ]
        p.b = ''.join(comments + defs)
        c.undoer.afterChangeNodeContents(p, 'change-font', udata)
#@+node:ekr.20140918124632.17893: ** qt: show-style-sheet
@g.command('show-style-sheet')
def print_style_sheet(event):
    """show-style-sheet command."""
    c = event.get('c')
    if c:
        c.styleSheetManager.print_style_sheet()
#@+node:ekr.20140918124632.17891: ** qt: style-reload
@g.command('style-reload')
@g.command('reload-style-sheets')
def style_reload(event):
    """reload-styles command.

    Find the appropriate style sheet and re-apply it.

    This replaces execution of the `stylesheet & source` node in settings files.
    """
    c = event.get('c')
    if c and c.styleSheetManager:
        # Call ssm.reload_settings after reloading all settings.
        c.reloadSettings()
#@+node:ekr.20140918124632.17892: ** qt: style-set-selected
@g.command('style-set-selected')
def style_set_selected(event):
    """style-set-selected command. Set the global stylesheet to c.p.b. (For testing)"""
    c = event.get('c')
    if c:
        c.styleSheetManager.set_selected_style_sheet()
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
