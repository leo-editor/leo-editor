#@+leo-ver=5-thin
#@+node:swot.20250715091430.1: * @file /Users/swot/app/leo-editor/leo/plugins/body_style_hook.py
#@@language python
#@+others
#@+node:swot.20260219114240.1: ** import
from leo.core import leoGlobals as g
from PyQt6.QtGui import QTextBlockFormat, QTextCursor, QFont, QTextCharFormat
from PyQt6.QtCore import QTimer

#@+node:swot.20260219114210.1: ** var
# Eliminate Pyflakes false positives during save
try:
    c
except NameError:
    c = None

# Configuration Area
STYLE_CONFIG = {
    "family": "JetBrains Mono",
    "size": 16,
    "line_height": 125,  # 125% = 1.25x line height
    "line_height_type": 1,  # 1 = ProportionalHeight
    "letter_spacing": 105,  # 105% letter spacing
}


#@+node:swot.20260219114140.1: ** def init
def init():
    """Plugin entry point"""
    # 1. For newly opened windows (Ctrl+O, Ctrl+N)
    g.registerHandler("open2", on_window_init)

    # 2. For the first window when Leo starts
    g.registerHandler("start2", on_window_init)

    # 3. [Key Fix] For existing windows during plugin reload
    # If the reload command is executed, this loop immediately fixes all open windows
    if g.app.commanders():
        for existing_c in g.app.commanders():
            on_window_init("reload", {"c": existing_c})

    g.es("Body Style Plugin loaded (New Window Fix).")
    return True


#@+node:swot.20260219114126.1: ** def on_window_init
def on_window_init(tag, keywords):
    """Universal window initialization function, handles startup, new windows, and reloads"""
    c = keywords.get("c")
    if not c:
        return

    # Prevent duplicate mounting (Singleton pattern)
    if hasattr(c, "_body_styler"):
        # In case of plugin reload, force style refresh
        # No need to recreate Controller, just call apply
        c._body_styler.apply_style()
        return

    # First time mount
    c._body_styler = BodyStyleController(c)


#@+node:swot.20260219114059.1: ** class BodyStyleController
class BodyStyleController:
    """
    Independent style controller for each Commander.
    """

    #@+others
    #@+node:swot.20260219115900.1: *3* def __init__
    def __init__(self, c):
        self.c = c

        # 1. init Debouncer
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(50)  # delay 50ms
        self._debounce_timer.timeout.connect(self.apply_style)

        # 2. Listen for node switching
        g.registerHandler("select1", self.on_select)

        # 3. Listen Leo command
        g.registerHandler("command2", self.on_command)

        # Delayed application on startup
        QTimer.singleShot(100, self.setup_qt_signals)

    #@+node:swot.20260219115854.1: *3* def on_select
    def on_select(self, tag, keywords):
        """Apply style when switching nodes"""
        if keywords.get("c") != self.c:
            return
        self.trigger_refresh()

    #@+node:swot.20260222110100.1: *3* def on_command
    def on_command(self, tag, keywords):
        """catch not  trigger textChanged command"""
        if keywords.get("c") == self.c:
            self.trigger_refresh()

    #@+node:swot.20260222110233.1: *3* def setup_qt_signals
    def setup_qt_signals(self):
        """Bind Qt textChanged signal"""
        editor = self.get_editor()
        if editor:
            # confirm not bind again when reload
            try:
                editor.textChanged.disconnect(self.trigger_refresh)
            except TypeError:
                pass
            editor.textChanged.connect(self.trigger_refresh)
        self.apply_style()

    #@+node:swot.20260222110737.1: *3* def trigger_refresh
    def trigger_refresh(self):
        """restart timer to apply debouncer"""
        self._debounce_timer.start()

    #@+node:swot.20260219115843.1: *3* def get_editor
    def get_editor(self):
        """Safely get Qt editor widget"""
        try:
            return self.c.frame.body.wrapper.widget
        except AttributeError:
            return None

    #@+node:swot.20260219114043.1: *3* def apply_style
    def apply_style(self):
        """Entry point: Prepare font object and apply formats"""
        editor = self.get_editor()
        if not editor:
            return

        doc = editor.document()
        if not doc:
            return

        # 1. Set Widget-level base font
        current_font = editor.font()
        # Keeping the check for performance, but if hot reload config fails
        # (e.g. only changing line height), consider removing this if block.
        if (
            current_font.family() != STYLE_CONFIG["family"]
            or current_font.pointSize() != STYLE_CONFIG["size"]
        ):
            font = QFont(STYLE_CONFIG["family"])
            font.setPointSize(STYLE_CONFIG["size"])
            font.setLetterSpacing(
                QFont.SpacingType.PercentageSpacing, STYLE_CONFIG["letter_spacing"]
            )

            editor.setFont(font)
            doc.setDefaultFont(font)

        # 2. Force apply Block and Char formats
        self._apply_formats(editor, doc)

    #@+node:swot.20260219114021.1: *3* def _apply_formats
    def _apply_formats(self, editor, doc):
        """Apply paragraph (line height) and character (letter spacing) formats simultaneously"""
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.SelectionType.Document)

        # Disable Qt signals for now!
        # Since mergeBlockFormat changes the document, we must block signals to prevent textChanged from causing an infinite recursion.
        editor.blockSignals(True)

        try:
            # A. Set paragraph format (Line Height)
            block_fmt = QTextBlockFormat()
            block_fmt.setLineHeight(
                STYLE_CONFIG["line_height"], STYLE_CONFIG["line_height_type"]
            )
            cursor.mergeBlockFormat(block_fmt)

            # B. Set character format (Letter Spacing)
            char_fmt = QTextCharFormat()
            char_fmt.setFontLetterSpacingType(QFont.SpacingType.PercentageSpacing)
            char_fmt.setFontLetterSpacing(STYLE_CONFIG["letter_spacing"])
            cursor.mergeCharFormat(char_fmt)
        finally:
            editor.blockSignals(False)
            # Clear selection
            cursor.clearSelection()

    #@-others


#@-others

"""
body_style_plugin.py
Provides consistent font, line height, and letter spacing settings for Leo's Body pane.
Fixes issues with line height reset on node switch and supports hot reloading.
"""
#@-leo
