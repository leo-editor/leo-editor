#@+leo-ver=5-thin
#@+node:tom.20210613135525.1: * @file ../plugins/freewin.py
"""
#@+<< docstring >>
#@+node:tom.20210603022210.1: ** << docstring >>
Freewin - a plugin with a basic editor pane that tracks an outline node.

Provides a free-floating window tied to one node in an outline.
The window functions as a plain text editor, and can also be
switched to render the node with Restructured Text.

:By: T\. B\. Passin
:Date: 19 June 2021
:Version: 1.1

#@+others
#@+node:tom.20210604174603.1: *3* Opening a Window
Opening a Window
~~~~~~~~~~~~~~~~~
To open a Freewin window, select a node in your outline and issue
the minibuffer command ``z-open-freewin``.

The window that opens will display an editor pane that contains the
text of the node.  The text can be edited in the window.  If the 
text is edited in the outline instead, the changes will show in the
Freewin pane.

Editing changes made in the Freewin window will be echoed in the
underlying outline node even if a different node has been selected.
They will be visible in the outline when the original node is
selected again.

A given Freewin window will be synchronized with the node
that was selected when the Freewin window was opened, and 
will only display that node.

#@+node:tom.20210604181030.1: *3* Rendering with Restructured Text
Rendering with Restructured Text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pressing the ``Rendered <--> Plain`` button will switch between
text and RsT rendering.  In RsT mode, text cannot be edited but
changes to the node in the outline will be rendered as they are made.

If RsT text in the focal node links to another node in the same
subtree, the Freewin window will not be able to navigate to the
target.  This is because the window only represents a single,
unchangeable node. However, no RsT error will be shown, and the
link will be underlined even though it will not be active.

The size of the rendered view can be increased or decreased with
the standard browser keys: CTRL-+ and CTRL--. Currently this feature
does not work with Qt6.
#@+node:tom.20210614171220.1: *3* Stylesheets and Dark-themed Appearance
Stylesheets and Dark-themed Appearance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The appearance of the editing and rendering view is determined
by stylesheets. Simple default stylesheets are built into the plugin
for the editing view.

For styling the Restructured Text rendering view and for customized
editing view stylesheets, the plugin looks in the user's `.leo/css
directory`.

The plugin attempts to determine whether the Leo theme in use
is a dark theme or not.  If it is, a dark-themed stylesheet will be
used if it is found.  The "dark" determination is based on the ``@color_theme_is_dark`` setting in the Leo theme file.
#@+node:tom.20210604181134.1: *4* Styling the Editor View
Styling the Editor View
~~~~~~~~~~~~~~~~~~~~~~~~
The editor panel styles will be set by a
css stylesheet file in the same directory as the
the RsT stylesheet above: the user's `.leo/css`
directory. There can be two stylesheets, one for light
and one for dark themes.

Light Stylesheet
-----------------
The light-themed stylesheet must be named `freewin_editor_light.css`.
The default Freewin values are::

    QTextEdit {
        color: #202020;
        background: #fdfdfd;
        font-family: Cousine, Consolas, Droid Sans Mono, DejaVu Sans Mono;
        font-size: 11pt;
}

Dark Stylesheet
-----------------
The dark-themed stylesheet must be named `freewin_editor_dark.css`.
The default Freewin values are::

    QTextEdit {
        color: #cbdedc;
        background: #202020;
        font-family: Cousine, Consolas, Droid Sans Mono, DejaVu Sans Mono;
        font-size: 11pt;
    }


No Stylesheet
--------------

If the correctly-named stylesheet is not present in the
user's ``.leo/css`` directory then the plugin will use the default values given above.
#@+node:tom.20210604181109.1: *4* Styling the RsT View
Styling the RsT View
~~~~~~~~~~~~~~~~~~~~~

The RsT view can be styled by extending or replacing
the default css stylesheet provided by docutils.
Custom stylesheets must be in the user's `.leo/css` directory.

For information on creating a customized css stylesheet, see

`docutils stylesheets <https://docutils.sourceforge.io/docs/howto/html-stylesheets.html>`_

As a starting point, the light and dark RsT stylesheets used
by the Viewrendered3 plugin could be used.  They can be found
in the Leo install directory in the ``leo\plugins\viewrendered3``
directory.  There are also a number of docutil stylesheets to be found with an Internet search.

The VR3 stylesheets must be renamed for the Freewin plugin to
be able to use them.

Light Stylesheet
-----------------

The light-themed stylesheet must be named ``freewin_rst_light.css``.

Dark Stylesheet
-----------------

The dark-themed stylesheet must be named ``freewin_rst_dark.css``.

No Stylesheet
--------------

If no stylesheet exists for the Restructured Text view, the default Docutils stylesheet will be used for either light or dark Leo themes.
#@-others

#@-<< docstring >>
"""

#@+<< imports >>
#@+node:tom.20210527153415.1: ** << imports >>
from os.path import exists, join as osp_join

try:
    # pylint: disable=import-error
    # this can fix an issue with Qt Web views in Ubuntu
    from OpenGL import GL
    assert GL  # To keep pyflakes happy.
except Exception:
    # but not need to stop if it doesn't work
    pass

from leo.core import leoGlobals as g

qt_imports_ok = False
try:
    from leo.core.leoQt import isQt5, QtCore, QtWidgets
    qt_imports_ok = True
except ImportError as e:
    g.trace(e)

if not qt_imports_ok:
    g.trace('Freewin plugin: Qt imports failed')
    raise ImportError('Qt Imports failed')

#@+<<import  QWebView>>
#@+node:tom.20210603000519.1: *3* <<import QWebView>>
QWebView = None
if isQt5:
    try:
        from leo.core.leoQt import QtWebKitWidgets
        QWebView = QtWebKitWidgets.QWebView
    except ImportError:
        g.trace("Can't import QtWebKitWidgets")
    except Exception as e:
        g.trace(e)
else:
    try:
        QWebView = QtWidgets.QTextBrowser
    except Exception as e:
        g.trace(e)
#@-<<import  QWebView>>
#@+<<import docutils>>
#@+node:tom.20210529002833.1: *3* <<import docutils>>
try:
    import docutils
    import docutils.core
except ImportError:
    docutils = None
if docutils:
    try:
        from docutils.core import publish_string
        from docutils.utils import SystemMessage
        got_docutils = True
    except ImportError:
        got_docutils = False
        g.es_exception()
    except SyntaxError:
        got_docutils = False
        g.es_exception()
else:
    got_docutils = False
    print('ZEditorWin: *** no docutils')

#@-<<import docutils>>
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

# Aliases.
QWidget = QtWidgets.QWidget
QTextEdit = QtWidgets.QTextEdit
QVBoxLayout = QtWidgets.QVBoxLayout
QPushButton = QtWidgets.QPushButton
QStackedWidget = QtWidgets.QStackedWidget
QRect = QtCore.QRect
#@-<< imports >>
#@+<< declarations >>
#@+node:tom.20210527153422.1: ** << declarations >>
# pylint: disable=invalid-name
# Dimensions and placing of editor windows
W = 570
H = 350
X = 1200
Y = 100
DELTA_Y = 35

BG_COLOR = '#fdfdfd'
BG_COLOR_DARK = '#202020'
FG_COLOR = '#202020'
FG_COLOR_DARK = '#cbdedc'
FONT_FAMILY = 'Cousine, Consolas, Droid Sans Mono, DejaVu Sans Mono'

BROWSER = 1
EDITOR = 0
EDITOR_FONT_SIZE = '11pt'
EDITOR_STYLESHEET_LIGHT_FILE = 'freewin_editor_light.css'
EDITOR_STYLESHEET_DARK_FILE = 'freewin_editor_dark.css'
ENCODING = 'utf-8'

RST_NO_WARNINGS = 5
RST_CUSTOM_STYLESHEET_LIGHT_FILE = 'freewin_rst_light.css'
RST_CUSTOM_STYLESHEET_DARK_FILE = 'freewin_rst_dark.css'

ENCODING='utf-8'
instances = {}

ZOOM_FACTOR = 1.1
#@-<< declarations >>
#@+<< Stylesheets >>
#@+node:tom.20210614172857.1: ** << Stylesheets >>

EDITOR_STYLESHEET_LIGHT = f'''QTextEdit {{
    color: {FG_COLOR};
    background: {BG_COLOR};
    font-family: {FONT_FAMILY};
    font-size: {EDITOR_FONT_SIZE};
    }}'''

EDITOR_STYLESHEET_DARK = f'''QTextEdit {{
    color: {FG_COLOR_DARK};
    background: {BG_COLOR_DARK};
    font-family: {FONT_FAMILY};
    font-size: 11pt;
    }}'''

RENDER_BTN_STYLESHEET_LIGHT = f'''color: {FG_COLOR}; 
    background: {BG_COLOR};
    font-size: {EDITOR_FONT_SIZE};'''

RENDER_BTN_STYLESHEET_DARK = f'''color: {FG_COLOR_DARK}; 
    background: {BG_COLOR_DARK};
    font-size: {EDITOR_FONT_SIZE};'''
#@-<< Stylesheets >>

#@+others
#@+node:ekr.20210617074439.1: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    return True
#@+node:tom.20210527153848.1: ** z-commands
@g.command('z-open-freewin')
def open_z_window(event):
    """Open or show editing window for the selected node."""
    if g.app.gui.guiName() != 'qt':
        return
    c = event.get('c')
    if not c:
        return
    id_ = c.p.gnx[:]

    zwin = instances.get(id_)
    if not zwin:
        zwin = instances[id_] = ZEditorWin(c)

    zwin.show()
    zwin.activateWindow()
#@+node:tom.20210614120921.1: ** get_at_setting_value()
def get_at_setting_value(name:str, lines:list)->str:
    """Retrieve value of a named setting as a string.

       The input lines are assumed to be from a Leo outline.
       Thus they are in XML.  We are not doing proper 
       XML parsing here, just brute force string operations.

       ARGUMENTS
       name -- the name of the setting, not including the
               "@type " introducer.
       lines -- a list of lines from a Leo theme file.

       RETURNS
       a string.
    """
    val = ''
    for line in lines:
        if name in line.split():
            fields = line.split('=')
            val = fields[-1].strip()
            val = val.replace('</vh></v>', '')
            break
    return val
#@+node:tom.20210527153906.1: ** class ZEditorWin
class ZEditorWin(QtWidgets.QMainWindow):
    """An basic editing window that echos the contents of an outline node."""
    #@+others
    #@+node:tom.20210527185804.1: *3* ctor
    def __init__(self, c, title='Z-editor'):
        super().__init__()
        QWidget().__init__()

        self.c = c
        self.p = c.p
        w = self.c.frame.body.wrapper
        self.host_editor = w.widget
        self.switching = False

        self.editor = QTextEdit()
        self.browser = QWebView()

        #@+<<set stylesheet paths>>
        #@+node:tom.20210604170628.1: *4* <<set stylesheet paths>>
        self.editor_csspath = ''
        self.rst_csspath = ''

        home = g.app.loadManager.computeHomeDir()
        cssdir = osp_join(home, '.leo', 'css')

        is_dark = False
        theme_path = g.app.loadManager.computeThemeFilePath()
        if theme_path:
            with open(theme_path, encoding=ENCODING) as f:
                lines = [l.strip() for l in f.readlines()]
            is_dark = get_at_setting_value('color_theme_is_dark', lines) == 'True'

        if is_dark:
            self.editor_csspath = osp_join(cssdir, EDITOR_STYLESHEET_DARK_FILE)
            self.rst_csspath = osp_join(cssdir, RST_CUSTOM_STYLESHEET_DARK_FILE)
        else:
            self.editor_csspath = osp_join(cssdir, EDITOR_STYLESHEET_LIGHT_FILE)
            self.rst_csspath = osp_join(cssdir, RST_CUSTOM_STYLESHEET_LIGHT_FILE)

        if g.isWindows:
            self.editor_csspath = self.editor_csspath.replace('/', '\\')
            self.rst_csspath = self.rst_csspath.replace('/', '\\')
        else:
            self.editor_csspath = self.editor_csspath.replace('\\', '/')
            self.rst_csspath = self.rst_csspath.replace('\\', '/')

        #@-<<set stylesheet paths>>
        #@+<<set stylesheets>>
        #@+node:tom.20210615101103.1: *4* <<set stylesheets>>
        # Check if editor stylesheet file exists.   If so,
        # we cache its contents.
        if exists(self.editor_csspath):
            with open(self.editor_csspath, encoding=ENCODING) as f:
                self.editor_style = f.read()
        else:
            self.editor_style = EDITOR_STYLESHEET_DARK if is_dark \
                                else EDITOR_STYLESHEET_LIGHT

        # If a stylesheet exists for RsT, we cache its contents.
        self.rst_stylesheet = None
        if exists(self.rst_csspath):
            with open(self.rst_csspath, encoding=ENCODING) as f:
                self.rst_stylesheet = f.read()
        #@-<<set stylesheets>>
        #@+<<set up editor>>
        #@+node:tom.20210602172856.1: *4* <<set up editor>>
        self.doc = self.editor.document()
        self.editor.setStyleSheet(self.editor_style)
        #@-<<set up editor>>
        #@+<<set up render button>>
        #@+node:tom.20210602173354.1: *4* <<set up render button>>
        self.render_button  = QPushButton("Rendered <--> Plain")
        self.render_button.clicked.connect(self.switch_and_render)

        b_style = RENDER_BTN_STYLESHEET_DARK if is_dark \
                  else RENDER_BTN_STYLESHEET_LIGHT
        self.render_button.setStyleSheet(b_style)
        #@-<<set up render button>>

        #@+<<build central widget>>
        #@+node:tom.20210528235126.1: *4* <<build central widget>>
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.insertWidget(EDITOR, self.editor)
        self.stacked_widget.insertWidget(BROWSER, self.browser)

        layout = QVBoxLayout()
        layout.addWidget(self.render_button)
        layout.addWidget(self.stacked_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        central_widget.keyPressEvent = self.keyPressEvent
        #@-<<build central widget>>
        #@+<<set geometry>>
        #@+node:tom.20210528235451.1: *4* <<set geometry>>
        Y_ = Y + (len(instances) % 10) * DELTA_Y
        self.setGeometry(QtCore.QRect(X, Y_, W, H))
        #@-<<set geometry>>
        #@+<<set window title>>
        #@+node:tom.20210531235412.1: *4* <<set window title>>
        # Show parent's title-->our title, our gnx
        ph = ''
        parents_ = list(c.p.parents())
        if parents_:
            ph = parents_[0].h + '-->'
        self.setWindowTitle(f'{ph}{c.p.h}   {c.p.gnx}')
        #@-<<set window title>>

        self.render_kind = EDITOR

        self.handlers = [('idle', self.update)]
        self._register_handlers()

        self.current_text = c.p.b
        self.editor.setPlainText(self.current_text)

        # Load docutils without rendering anything real
        # Avoids initial delay when switching to RsT the first time.
        dummy = publish_string('dummy', writer_name='html').decode(ENCODING)
        self.browser.setHtml(dummy)

        self.show()
    #@+node:tom.20210528090313.1: *3* update
    # Must have this signature: called by leoPlugins.callTagHandler.
    def update(self, tag, keywords):
        """Update host node if this card's text has changed.  Otherwise
           if the host node's text has changed, update the card's text 
           with the host's changed text. Render as plain text or RsT.
        """
        if self.switching: return

        if self.doc.isModified():
            self.current_text = self.doc.toRawText()
            self.p.b = self.current_text
            self.doc.setModified(False)

        # if the current position in the outline is our own node, 
        # then synchronize the text if it's changed in the host outline.
        elif self.c.p == self.p:
            doc = self.host_editor.document()
            if doc.isModified():
                scrollbar = self.editor.verticalScrollBar()
                old_scroll = scrollbar.value()
                self.current_text = doc.toRawText()
                self.editor.setPlainText(self.current_text)
                self.set_and_render(False)
                doc.setModified(False)
                scrollbar.setValue(old_scroll)

            self.doc.setModified(False)
    #@+node:tom.20210619000302.1: *3* keyPressEvent
    def keyPressEvent(self, event):
        """Take actions on keypresses when the render pane has focus and a
        key is pressed.

        A method of this name receives keystrokes for most or all
        QObject-descended objects. Currently, check only for <CNTRL-=> and
        <CONTROL-MINUS> events for zooming or unzooming the VR3 browser pane.
        """

        if self.render_kind != BROWSER or not isQt5:
            return

        w = self.browser

        mod = ''
        modifiers = event.modifiers()
        bare_key = event.text()

        KeyboardModifiers = QtCore.Qt if isQt5 else QtCore.Qt.KeyboardModifiers
        if modifiers and modifiers == KeyboardModifiers.ControlModifier:
            mod = 'cntrl'

        if bare_key == '=' and mod == 'cntrl':
            _zf = w.zoomFactor()
            w.setZoomFactor(_zf * ZOOM_FACTOR)
        elif bare_key == '-' and mod == 'cntrl':
            _zf = w.zoomFactor()
            w.setZoomFactor(_zf / ZOOM_FACTOR)

    #@+node:tom.20210527234644.1: *3* _register_handlers (floating_pane.py)
    def _register_handlers(self):
        """_register_handlers - attach to Leo signals"""
        for hook, handler in self.handlers:
            g.registerHandler(hook, handler)

    #@+node:tom.20210529000221.1: *3* set_and_render
    def set_and_render(self, switch=True):
        """Switch between the editor and RsT viewer, and render text."""
        self.switching = True
        if not got_docutils:
            self.render_kind = EDITOR
        elif switch:
            if self.render_kind == BROWSER:
                self.render_kind = EDITOR
            else:
                self.render_kind = BROWSER

            self.stacked_widget.setCurrentIndex(self.render_kind)

        if self.render_kind == BROWSER:
            text = self.editor.document().toRawText()
            html = self.render_rst(text)
            self.browser.setHtml(html)

        self.switching = False

    def switch_and_render(self):
        self.set_and_render(True)
    #@+node:tom.20210602174838.1: *3* render_rst
    def render_rst(self, text):
        """Render text of the editor widget as HTML and display it."""
        if not got_docutils:
            return("<h1>Can't find Docutils to Render This Node</h1>")

        # Call docutils to get the html rendering.
        _html = ''
        args = {'output_encoding': 'unicode', # return a string, not a byte array
                'report_level' : RST_NO_WARNINGS,
               }

        if self.rst_stylesheet:
            args['stylesheet_path'] = None # omit stylesheet, we will insert one

        try:
            _html = publish_string(text, writer_name='html',
                                   settings_overrides=args)
        except SystemMessage as sm:
            msg = sm.args[0]
            if 'SEVERE' in msg or 'FATAL' in msg:
                _html = f'RsT error:\n{msg}\n\n{text}'


        if self.rst_stylesheet:
            style_insert = f'''<style type='text/css'>
            {self.rst_stylesheet}
            </style>
            </head>'''
            _html = _html.replace('</head>', style_insert, 1)

        return _html
    #@-others
#@-others
#@-leo
