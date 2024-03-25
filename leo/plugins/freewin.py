#@+leo-ver=5-thin
#@+node:tom.20210613135525.1: * @file ../plugins/freewin.py
#@@language python
r"""
#@+<< docstring >>
#@+node:tom.20210603022210.1: ** << docstring >> (freewin.py)
Freewin - a plugin with a basic editor pane that tracks an
outline node.

Provides a free-floating window tied to one node in an outline.
The window functions as a plain text editor, and can also be
switched to render the node with Restructured Text.  A Freewin window
is node-locked - that is, it always shows a view of its original host node
no matter how the user navigates within or between outlines.

:By: T\. B\. Passin
:Version: 2.01
:Date: 6 Apr 2022

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
will only display that node.  It will remain synchronized even if
the node has been moved to a new position in its outline.

.. Note:: A Freewin window will close if the underlying node is removed.
          This will not change the body of the underlying node.

#@+node:tom.20210625220923.1: *3* Navigating
Navigating
~~~~~~~~~~~

#@@nocolor

A Freewin window only ever displays the content of the node it ws opened
on. However, the selected node in the outline in the host can be changed,
which will cause the host to navigate to the new selection. This navigation
can be done when a line in the visible text contains a `gnx` - a node
identifier. If the cursor is placed on a line with a gnx, or if that line
is selected, and then <CONTROL-F9> is pressed, the host outline will
navigate to the node having that gnx.

A gnx looks like this::

    tom.20210610132217.1

A line with a gnx might look like this::

    :event: tom.20210623002747.1 `John DeBoer Opens General Store`_

This capability is always available in the editor pane. It can be available
in the rendering pane (see below) if the setting::

    @string fw-render-pane = nav-view

is set in the @settings tree. The setting can be in the @settings tree of
an outline or in myLeoSettings.leo.
#@+node:tom.20210604181030.1: *3* Rendering with Restructured Text
Rendering with Restructured Text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pressing the ``Rendered <--> Plain`` button will switch between
text and RsT rendering.  In RsT mode, text cannot be edited but
changes to the node in the outline will be rendered as they are
made.

If RsT text in the focal node links to another node in the same
subtree, the Freewin window will not navigate to the
target.  This is because the window only represents a single,
unchangeable node. However, no RsT error will be shown, and the
link will be underlined even though it will not be active.

Two types of rendering views are available, and can be chosen by a setting in the @settings tree.

1. A well-rendered view with all the features of Restructured Text rendered
   in an appealing way (depending on the stylesheet used). This view can be
   zoomed in or out using the standard browser keys: CTRL-+ and CTRL--.
   A light or dark themed stylesheet is selected based on the dark or light
   character of your Leo theme. You can supply your own stylesheet to use
   instead of the built-in ones.

2. A less fully-rendered view that has the ability to cause the host
   outline to navigate to a node with a selected gnx - see the section on
   `Navigating` above. Because of limitations of the Qt widget used for
   this view, the size cannot be zoomed and some visual features of the
   rendered RsT can be less refined. The stylesheets for this view cannot
   be changed. Automatic switching between light and dark themes is still
   done.

View 1 is the default view. View2 is mainly used when the QtWebEngineView
library package is not available. To use View 2 instead, add the following
setting to the setting tree of an outline or to myLeoSettings.leo:

    @string fw-render-pane = nav-view

#@+node:tom.20210626134532.1: *3* Hotkeys
Hotkeys
~~~~~~~

Freewin uses two hotkeys:

<CNTL-F7> --  copy the gnx of this Freewin window to the clipboard.
<CNTL-F9> -- Select host node that has gnx under the selection point.

<CNTL-F9> is available in the editor view, and in the rendered view
with limitations discussed above discussed above.
#@+node:tom.20210712005103.1: *3* Commands
Commands
~~~~~~~~~

Freewin has one minibuffer command: ``z-open-freewin``. This opens a
Freewin window linked to the currently selected node.
#@+node:tom.20210712005441.1: *3* Settings
Settings
~~~~~~~~~

Freewin has two settings:

1. ``@string fw-render-pane = nav-view``

If present with this value, the rendered view will allow the <CNTL>-F7/F9
keys to work as they do in the Editor view. The rendered view will not be
able to display all the features that a full rendered view can.

2. ``@bool fw-copy-html = False``

   Change to `True` to copy the rendered RsT to the clipboard.
#@+node:tom.20210614171220.1: *3* Stylesheets and Dark-themed Appearance
Stylesheets and Dark-themed Appearance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The appearance of the editing and rendering view is determined
by stylesheets. Simple default stylesheets are built into the
plugin for the editing view.

For styling the Restructured Text rendering view (When the default "View 1"
is in use) and for customized editing view stylesheets, the plugin looks in
the user's `.leo/css directory`.

The plugin attempts to determine whether the Leo theme in use
is a dark theme or not.  If it is, a dark-themed stylesheet
will be used if it is found.  The "dark" determination is based
on the ``@color_theme_is_dark`` setting in the Leo theme file.
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

The following on applies when the default rendereing view,
called "View 1" above, is being used.

The RsT view can be styled by extending or replacing
the default css stylesheet provided by docutils.
Custom stylesheets must be in the user's `.leo/css` directory.

For information on creating a customized css stylesheet, see

`docutils stylesheets <https://docutils.sourceforge.io/docs/howto/html-stylesheets.html>`_

As a starting point, the light and dark RsT stylesheets used
by the Viewrendered3 plugin could be used.  They can be found
in the Leo install directory in the ``leo\plugins\viewrendered3``
directory.  There are also a number of docutil stylesheets to be
found with an Internet search.

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

If no stylesheet exists for the Restructured Text view, the
default Docutils stylesheet will be used for either light or dark
Leo themes.
#@-others

#@-<< docstring >>
"""
#@+<< imports >>
#@+node:tom.20210527153415.1: ** << imports >> (freewin.py)
from __future__ import annotations
from typing import TYPE_CHECKING, Any
from os.path import exists, join as osp_join
import re

from leo.core import leoColorizer
from leo.plugins import qt_text

from leo.core import leoGlobals as g

qt_imports_ok = False
try:
    from leo.core.leoQt import QtCore, QtWidgets, QtGui
    from leo.core.leoQt import KeyboardModifier
    from leo.core.leoQt import QtWebEngineWidgets
    qt_imports_ok = True
except ImportError as e:
    g.trace(e)

if not qt_imports_ok:
    print('Freewin plugin: Qt imports failed')
    raise ImportError('Qt Imports failed')

QWebView = QtWebEngineWidgets.QWebEngineView

#@+<<import docutils>>
#@+node:tom.20210529002833.1: *3* <<import docutils>>
got_docutils = False
try:
    from docutils.core import publish_string
    from docutils.utils import SystemMessage
    got_docutils = True
except ModuleNotFoundError as e:
    print('Freewin:', e)
except ImportError as e:
    print('Freewin:', e)
except SyntaxError as e:
    print('Freewin:', e)
except Exception as e:
    print('Freewin:', e)

if not got_docutils:
    print('Freewin: no docutils - rendered view is not available')

#@-<<import docutils>>

# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

# Aliases.
QApplication = QtWidgets.QApplication
QFont = QtGui.QFont
QFontInfo = QtGui.QFontInfo
QFontMetrics = QtGui.QFontMetrics
QPushButton = QtWidgets.QPushButton

QRect = QtCore.QRect
QStackedWidget = QtWidgets.QStackedWidget
QTextEdit = QtWidgets.QTextEdit
QVBoxLayout = QtWidgets.QVBoxLayout
QWidget = QtWidgets.QWidget
QColor = QtGui.QColor

WrapMode = QtGui.QTextOption.WrapMode

#@-<< imports >>
#@+<< annotations >>
#@+node:tom.20220919101426.1: ** << annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoQt import QtWidgets
    from leo.core.leoQt import QtGui
    from leo.plugins.qt_text import LeoQTextBrowser
#@-<< annotations >>
#@+<< declarations >>
#@+node:tom.20210527153422.1: ** << declarations >>
# pylint: disable=invalid-name
# Dimensions and placing of editor windows
W: int = 570
H: int = 350
X: int = 1200
Y: int = 100
DELTA_Y: int = 35

clipboard = QApplication.clipboard()

FG_COLOR_LIGHT: str = '#6B5B53'
BG_COLOR_LIGHT: str = '#ededed'
BG_COLOR_DARK: str = '#202020'
FG_COLOR_DARK: str = '#cbdedc'
FONT_FAMILY: str = 'Cousine, Consolas, Droid Sans Mono, DejaVu Sans Mono'

EDITOR_FONT_SIZE: str = '11pt'
EDITOR_STYLESHEET_LIGHT_FILE: str = 'freewin_editor_light.css'
EDITOR_STYLESHEET_DARK_FILE: str = 'freewin_editor_dark.css'
ENCODING: str = 'utf-8'
BROWSER: int = 1
EDITOR: int = 0
BROWSER_VIEW: str = 'browser_view'
NAV_VIEW: str = 'nav-view'

RST_NO_WARNINGS: int = 5
RST_CUSTOM_STYLESHEET_LIGHT_FILE: str = 'freewin_rst_light.css'
RST_CUSTOM_STYLESHEET_DARK_FILE: str = 'freewin_rst_dark.css'

instances: dict[str, ZEditorWin] = {}

#@+others
#@+node:tom.20210709130401.1: *3* Fonts and Text
ZOOM_FACTOR: float = 1.1

F7_KEY: int = 0x01000036  # See https://doc.qt.io/qt-5/qt.html#Key-enum (enum Qt::Key)
F9_KEY: int = 0x01000038
KEY_S: int = 0x53

GNXre: str = r'^(.+\.\d+\.\d+)'  # For gnx at start of line
GNX1re: str = r'.*[([\s](\w+\.\d+\.\d+)'  # For gnx not at start of line

GNX: re.Pattern = re.compile(GNXre)
GNX1: re.Pattern = re.compile(GNX1re)

fs: str = EDITOR_FONT_SIZE.split('pt', 1)[0]
qf: QtGui.QFont = QFont(FONT_FAMILY[0], int(fs))
qfont: QtGui.QFontInfo = QFontInfo(qf)  # Uses actual font if different
FM: QtGui.QFontMetrics = QFontMetrics(qf)

TABWIDTH: int = 36  # Best guess but may not alays be right.
TAB2SPACES: int = 4  # Tab replacement when writing back to host node
#@-others

#@-<< declarations >>
#@+<< Stylesheets >>
#@+node:tom.20210614172857.1: ** << Stylesheets >>

EDITOR_STYLESHEET_LIGHT: str = f'''QTextEdit {{
    color: {FG_COLOR_LIGHT};
    background: {BG_COLOR_LIGHT};
    font-family: {FONT_FAMILY};
    font-size: {EDITOR_FONT_SIZE};
    }}'''

EDITOR_STYLESHEET_DARK: str = f'''QTextEdit {{
    color: {FG_COLOR_DARK};
    background: {BG_COLOR_DARK};
    font-family: {FONT_FAMILY};
    font-size: {EDITOR_FONT_SIZE};
    }}'''

RENDER_BTN_STYLESHEET_LIGHT: str = f'''color: {FG_COLOR_LIGHT};
    background: {BG_COLOR_LIGHT};
    font-size: {EDITOR_FONT_SIZE};'''

RENDER_BTN_STYLESHEET_DARK: str = f'''color: {FG_COLOR_DARK};
    background: {BG_COLOR_DARK};
    font-size: {EDITOR_FONT_SIZE};'''

#@+others
#@+node:tom.20210625145324.1: *3* RsT Stylesheet Dark
RST_STYLESHEET_DARK: str = '''body {
  color: #cbdedc; /*#ededed;*/
  background: #202020;
  font-family: Verdana, Arial, "Bitstream Vera Sans", sans-serif;
  font-size: 10pt;
  line-height:120%;
  margin: 8px 0;
  margin-left: 7px;
  margin-right: 7px;
  }

  h1 {text-align: center; margin-top: 7px; margin-bottom: 12px;}
  a {color: lightblue; text-decoration: none}

  table {margin-top: 10px;}

  th {
    color: #ededed;
    background: #073642;
    vertical-align: top;
    border-bottom: thin solid #839496;
    text-align: center;
    padding-right: 6px; padding-left: 2px;
    padding: 2px;
  }

  th.docinfo-name {
    text-align: right;
  }

  td {
    padding-left: 10px;
  }

  div.admonition, div.note {
    margin: 2em;
    border: 2px solid;
    padding-right: 1em;
    padding-left: 1em;
    background-color: #073642;
    color: #ededed;
    border-color: #839496;
  }

  div.note p.admonition-title {
    color: #2aa198;
    font-weight: bold;
}

'''
#@+node:tom.20210625155534.1: *3* RsT Stylesheet Light
RST_STYLESHEET_LIGHT: str = '''body {
  color: #6B5B53;
  background: #ededed;
  font-family: Verdana, Arial, "Bitstream Vera Sans", sans-serif;
  font-size: 10pt;
  line-height: 120%;
  margin: 8px 0;
  margin-left: 7px;
  margin-right: 7px;
  }

  h1 {text-align: center; margin-top: 7px; margin-bottom: 12px;}
  a {color: darkblue; text-decoration: none}

  table {
    margin-top: 10px;
  }

  th {
    color: #093947;
    background: #b0ddee;
    vertical-align: top;
    border-bottom: thin solid #839496;
    text-align: center;
    padding-right: 6px; padding-left: 2px;
    padding: 2px;
  }

  td {
    padding-left: 10px;
  }

  th.docinfo-name {
    text-align: right;
  }

  div.admonition, div.system-message,
        div.warning, div.note {
    margin: 2em;
    border: 2px solid;
    padding-right: 1em;
    padding-left: 1em;
    background: #e0e0e0;
    color: #586e75;
    border-color: #657b83;
  }

  p.admonition-title {
    color: #2aa198;
    font-weight: bold;
  }

  div.caution p.admonition-title,
      div.attention p.admonition-title,
      div.warning p.admonition-title {
    color: #cb4b16;
  }

  div.note {
    border-radius: .5em;
  }
'''
#@-others
#@-<< Stylesheets >>

#@+others
#@+node:ekr.20210617074439.1: ** init
def init() -> bool:
    """Return True if the plugin has loaded successfully."""
    return True
#@+node:tom.20210527153848.1: ** z-commands
@g.command('z-open-freewin')
def open_z_window(event: LeoKeyEvent) -> None:
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
#@+node:tom.20210625145842.1: ** getGnx
def getGnx(line: str) -> str:
    """Find and return a gnx in a line of text, or None.

    The gnx may be enclosed in parens or brackets.
    """

    matched = GNX1.match(line) or GNX.match(line)
    target = matched[1] if matched else None
    return target
#@+node:tom.20210625145905.1: ** getLine
def getLine(text_edit: QtWidgets.QTextEdit) -> str:
    """Return line of text at cursor position.

    Cursor may not be visible, but its location
    will be at the last mouse click.  If a block
    is selected, then the last line of the block
    is returned.

    ARGUMENT
    text_edit -- a QTextEdit instance

    RETURNS
    a line of text, or ''
    """

    curs = text_edit.textCursor()
    text = text_edit.toPlainText()
    pos = curs.position()
    before = text[:pos]
    after = text[pos:]
    line = before.split('\n')[-1] + after.split('\n')[0]
    return line
#@+node:tom.20210625161018.1: ** gotoHostGnx
def gotoHostGnx(c: Cmdr, target: str) -> bool:
    """Change host node selection to target gnx.

    This will not change the node displayed by the
    invoking window.

    ARGUMENTS
    c -- the Leo commander of the outline hosting our window.
    target -- the gnx to be selected in the host, as a string.

    RETURNS
    True if target was found, else False
    """
    if c.p.gnx == target:
        return True
    for p in c.all_unique_positions():
        if p.v.gnx == target:
            c.selectPosition(p)
            return True
    return False
#@+node:tom.20210628002321.1: ** copy2clip
def copy2clip(text: str) -> None:
    clipboard.setText(text)
#@+node:tom.20220329145952.1: ** change_css_prop
def change_css_prop(css: str, prop: str, newval: str) -> str:
    """Change the value of a named property in a css stylesheet fragment.

    If there is more than one instance of prop, only
    the first one will be changed.

    The previous property value is replace with the new.
    """
    if prop not in css:
        return None
    start = css.find(prop)
    colon = css[start:].find(':')
    frag = css[start + colon + 1 :]
    end = frag.find(';')
    val = frag[:end].strip()

    return css.replace(val, newval, 1)

#@+node:tom.20220329150105.1: ** get_body_colors
# Get current colors from the body editor widget
def get_body_colors(c: Cmdr) -> tuple[str, str]:
    wrapper = c.frame.body.wrapper
    w: LeoQTextBrowser = wrapper.widget

    pallete: QtGui.QPalette = w.viewport().palette()
    fg_hex: int = pallete.text().color().rgb()
    bg_hex: int = pallete.window().color().rgb()
    fg: str = f'#{fg_hex:x}'
    bg: str = f'#{bg_hex:x}'

    return fg, bg
#@+node:tom.20220329231604.1: ** is_body_dark
def is_body_dark(c: Cmdr) -> bool:
    """Return True if host's body appears to have a dark theme."""
    fg, bg = get_body_colors(c)
    # hsv =  hue, saturation, value
    # We assess the background to be dark if its value is < 90
    bg_color = QColor(bg)
    h, s, vbg, a = bg_color.getHsv()
    return vbg < 90
#@+node:tom.20210527153906.1: ** class ZEditorWin
class ZEditorWin(QtWidgets.QMainWindow):
    """An editing window that echos the contents of an outline node."""
    #@+others
    #@+node:tom.20210527185804.1: *3* ctor
    def __init__(self, c: Cmdr, title: str = 'Z-editor') -> None:
        # pylint: disable=too-many-locals
        # pylint: disable = too-many-statements
        global TAB2SPACES
        super().__init__()

        self.c = c
        self.p = c.p
        self.v = c.p.v
        self.host_id = c.p.gnx
        w = c.frame.body.wrapper
        self.host_editor = w.widget
        self.switching = False
        self.closing = False

        self.reloadSettings()

        # The rendering pane can be either a QWebView or a QTextEdit
        # depending on the features desired
        if not QWebView:  # Until Qt6 has a QWebEngineView, force QTextEdit
            self.render_pane_type = NAV_VIEW
        if self.render_pane_type == NAV_VIEW:
            self.render_widget = QTextEdit
        else:
            self.render_widget = QWebView
            self.render_pane_type = BROWSER_VIEW
            QtWebEngineWidgets.QWebEngineView.__init__(self)

        self.editor = QTextEdit()
        wrapper = qt_text.QTextEditWrapper(self.editor, name='zwin', c=c)
        c.k.completeAllBindingsForWidget(wrapper)

        browser = self.browser = self.render_widget()

        #@+<<set stylesheet paths>>
        #@+node:tom.20210604170628.1: *4* <<set stylesheet paths>>
        self.editor_csspath = ''
        self.rst_csspath = ''

        home = g.app.loadManager.computeHomeDir()
        cssdir = osp_join(home, '.leo', 'css')

        is_dark = is_body_dark(self.c)
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
        # Check if editor stylesheet file exists. If so,
        # we cache its contents.
        if exists(self.editor_csspath):
            with open(self.editor_csspath, encoding=ENCODING) as f:
                self.editor_style = f.read()
        else:
            self.editor_style = EDITOR_STYLESHEET_DARK if is_dark else EDITOR_STYLESHEET_LIGHT

        # If a stylesheet exists for RsT, we cache its contents.
        self.rst_stylesheet = None
        if exists(self.rst_csspath):
            with open(self.rst_csspath, encoding=ENCODING) as f:
                self.rst_stylesheet = f.read()
        else:
            self.rst_stylesheet = RST_STYLESHEET_DARK if is_dark else RST_STYLESHEET_LIGHT
        #@-<<set stylesheets>>
        #@+<<set up editor>>
        #@+node:tom.20210602172856.1: *4* <<set up editor>>
        self.doc = self.editor.document()
        self.editor.setWordWrapMode(WrapMode.WrapAtWordBoundaryOrAnywhere)

        # Adjust editor stylesheet color to match body fg, bg
        fg, bg = get_body_colors(self.c)
        css = change_css_prop(self.editor_style, 'color', fg)
        css = change_css_prop(css, 'background', bg)
        self.editor_style = css
        self.editor.setStyleSheet(css)

        colorizer = leoColorizer.make_colorizer(c, self.editor)
        colorizer.highlighter.setDocument(self.doc)

        # Try to get tab width from the host's body
        # Used when writing edits back to host
        # "tabwidth" directive ought to be in first six lines
        lines = self.p.v.b.split('\n', 6)
        for line in lines:
            if line.startswith('@tabwidth') and line.find(' ') > 0:
                tabfield = line.split()[1]
                TAB2SPACES = abs(int(tabfield))
                break

        # Make tabs line up with 4 spaces (at least approximately)
        self.editor.setTabStopDistance(TABWIDTH)

        if self.render_pane_type == NAV_VIEW:
            # Different stylesheet mechanism if we are a QTextEdit
            stylesheet = RST_STYLESHEET_DARK if is_dark else RST_STYLESHEET_LIGHT
            browser.setReadOnly(True)
            browser_doc = browser.document()
            browser_doc.setDefaultStyleSheet(stylesheet)
        #@-<<set up editor>>
        #@+<<set up render button>>
        #@+node:tom.20210602173354.1: *4* <<set up render button>>
        self.render_button = QPushButton("Rendered <--> Plain")
        self.render_button.clicked.connect(self.switch_and_render)

        b_style = RENDER_BTN_STYLESHEET_DARK if is_dark else RENDER_BTN_STYLESHEET_LIGHT
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

        self.central_widget = central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

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
        if got_docutils:
            dummy = publish_string('dummy', writer_name='html').decode(ENCODING)
            self.browser.setHtml(dummy)
            central_widget.keyPressEvent = self.keyPressEvent
        QApplication.processEvents()
        self.show()

    #@+node:tom.20210625205847.1: *3* reload settings
    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        self.render_pane_type = c.config.getString('fw-render-pane') or ''  # type: ignore [attr-defined]
        self.copy_html = c.config.getBool('fw-copy-html', default=False)  # type: ignore [attr-defined]

    #@+node:tom.20210528090313.1: *3* update
    # Must have this signature: called by leoPlugins.callTagHandler.
    def update(self, tag: str, keywords: Any) -> None:
        """Update host node if this card's text has changed.

           Otherwise if the host node's text has changed, update
           the card's text with the host's changed text.
           Render as plain text or RsT.

           If the host node does not exist any more, delete ourself.
        """
        if self.closing:
            return

        # Make sure our host node still exists
        if not self.c.p.v == self.v:
            # Find our node
            found_us: bool = False
            for p1 in self.c.all_unique_positions():
                if p1.v == self.v:
                    self.p = p1
                    found_us = True
                    break
            if not found_us:
                self.teardown(tag)
                return

        if self.switching:
            return

        if self.doc.isModified():
            self.current_text = self.doc.toPlainText()
            self.current_text = self.current_text.replace('\t', ' ' * TAB2SPACES)
            self.p.b = self.current_text
            self.doc.setModified(False)

        # If the current position in the outline is our own node,
        # then synchronize the text if it's changed in
        # the host outline.
        elif self.c.p.v == self.v:
            doc = self.host_editor.document()
            if doc.isModified():
                scrollbar = self.editor.verticalScrollBar()
                old_scroll = scrollbar.value()
                self.current_text = doc.toPlainText()
                self.editor.setPlainText(self.current_text)
                self.set_and_render(False)
                doc.setModified(False)
                scrollbar.setValue(old_scroll)

            self.doc.setModified(False)

    #@+node:tom.20210703173219.1: *3* teardown
    def teardown(self, tag: str = '') -> None:
        # Close window and delete it when host node is deleted.
        if self.closing:
            return

        self.closing = True
        g.unregisterHandler(tag, self.update)
        self.central_widget.keyPressEvent = None
        id_ = self.host_id
        self.editor.deleteLater()
        self.browser.deleteLater()
        self.stacked_widget.deleteLater()
        self.central_widget.deleteLater()
        instances[id_] = None  # Not sure if we need this
        del instances[id_]
        self.deleteLater()
    #@+node:tom.20210619000302.1: *3* keyPressEvent
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:  # pylint:disable=method-hidden
        """Take action on keypresses.

        A method of this name receives keystrokes for most or all
        QObject-descended objects. Currently, checks only for
        <CONTROL-F7>, <CONTROL-F9>, <CONTROL-EQUALS> and
        <CONTROL-MINUS> events for zooming or unzooming the rendering
        pane.
        """
        w = self.browser if self.render_kind == BROWSER else self.editor
        modifiers = event.modifiers()
        bare_key = event.text()
        keyval = event.key()

        if modifiers == KeyboardModifier.ControlModifier:
            if keyval == KEY_S:
                self.c.executeMinibufferCommand('save')
            elif keyval == F7_KEY:
                # Copy our gnx to clipboard.
                copy2clip(self.p.v.gnx)
            elif self.render_pane_type == NAV_VIEW or self.render_kind == EDITOR:
                # change host's selected node to new target
                if keyval == F9_KEY:
                    gnx = getGnx(getLine(w))
                    found_gnx = gotoHostGnx(self.c, gnx)
                    if not found_gnx:
                        g.es(f'Could not find gnx "{gnx}"')
            elif (
                self.render_kind == BROWSER
                and self.render_pane_type == BROWSER_VIEW
            ):
                # Zoom/unzoom
                if bare_key == '=':
                    _zf = w.zoomFactor()
                    w.setZoomFactor(_zf * ZOOM_FACTOR)
                elif bare_key == '-':
                    _zf = w.zoomFactor()
                    w.setZoomFactor(_zf / ZOOM_FACTOR)

    #@+node:tom.20210527234644.1: *3* _register_handlers
    def _register_handlers(self):
        """_register_handlers - attach to Leo signals"""
        for hook, handler in self.handlers:
            g.registerHandler(hook, handler)

    #@+node:tom.20210529000221.1: *3* set_and_render
    def set_and_render(self, switch: bool = True):
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
            text = self.editor.document().toPlainText()
            if text[0] == '<':
                html = text
            else:
                html = self.render_rst(text)
            self.browser.setHtml(html)
            if self.copy_html:
                copy2clip(html)

        self.switching = False

    def switch_and_render(self):
        self.set_and_render(True)
    #@+node:tom.20210602174838.1: *3* render_rst
    def render_rst(self, text):
        """Render text of the editor widget as HTML and display it."""
        if not got_docutils:
            return "<h1>Can't find Docutils to Render This Node</h1>"

        # Call docutils to get the html rendering.
        _html = ''
        args = {'output_encoding': 'unicode',  # return a string, not a byte array
                'report_level': RST_NO_WARNINGS,
               }

        if self.rst_stylesheet:
            args['stylesheet_path'] = None  # omit stylesheet, we will insert one

        try:
            _html = publish_string(text, writer_name='html',
                                   settings_overrides=args)
        except SystemMessage as sm:
            msg = sm.args[0]
            if 'SEVERE' in msg or 'FATAL' in msg:
                _html = f'RsT error:\n{msg}\n\n{text}'

        # Insert stylesheet if our rendering view is a web browser widget
        if self.render_pane_type == BROWSER_VIEW:
            if self.rst_stylesheet:
                style_insert = ("<style type='text/css'>\n"
                        f'{self.rst_stylesheet}\n</style>\n</head>\n')
                _html = _html.replace('</head>', style_insert, 1)
        return _html
    #@-others
#@-others
#@-leo
