#@+leo-ver=5-thin
#@+node:swot.20250715091430.1: * @file /Users/swot/app/leo-editor/leo/plugins/body_style_hook.py
"""
body_style_plugin.py
Provides consistent font, line height, and letter spacing settings for Leo's Body pane.
Fixes issues with line height reset on node switch and supports hot reloading.
"""

from leo.core import leoGlobals as g
from PyQt6.QtGui import QTextBlockFormat, QTextCursor, QFont, QTextCharFormat
from PyQt6.QtCore import QTimer

# Eliminate Pyflakes false positives during save
try:
    c
except NameError:
    c = None

# Configuration Area
STYLE_CONFIG = {
    "family": "JetBrains Mono",
    "size": 16,
    "line_height": 125,      # 125% = 1.25x line height
    "line_height_type": 1,   # 1 = ProportionalHeight
    "letter_spacing": 105    # 105% letter spacing
}

def init():
    """Plugin entry point"""
    # 1. For newly opened windows (Ctrl+O, Ctrl+N)
    g.registerHandler('open2', on_window_init)
    
    # 2. For the first window when Leo starts
    g.registerHandler('start2', on_window_init)
    
    # 3. [Key Fix] For existing windows during plugin reload
    # If the reload command is executed, this loop immediately fixes all open windows
    if g.app.commanders():
        for existing_c in g.app.commanders():
            on_window_init('reload', {'c': existing_c})

    g.es("Body Style Plugin loaded (New Window Fix).")
    return True

def on_window_init(tag, keywords):
    """Universal window initialization function, handles startup, new windows, and reloads"""
    c = keywords.get('c')
    if not c:
        return

    # Prevent duplicate mounting (Singleton pattern)
    if hasattr(c, '_body_styler'):
        # In case of plugin reload, force style refresh
        # No need to recreate Controller, just call apply
        c._body_styler.apply_style()
        return

    # First time mount
    c._body_styler = BodyStyleController(c)

class BodyStyleController:
    """
    Independent style controller for each Commander.
    """
    def __init__(self, c):
        self.c = c
        
        # Listen for node switching
        g.registerHandler('select1', self.on_select)
        
        # Delayed application on startup
        QTimer.singleShot(100, self.apply_style)

    def on_select(self, tag, keywords):
        """Apply style when switching nodes"""
        if keywords.get('c') != self.c:
            return
            
        # [Fix]: Use 0ms delay to ensure execution after Leo finishes loading text
        QTimer.singleShot(0, self.apply_style)

    def get_editor(self):
        """Safely get Qt editor widget"""
        try:
            return self.c.frame.body.wrapper.widget
        except AttributeError:
            return None

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
        if (current_font.family() != STYLE_CONFIG["family"] or 
            current_font.pointSize() != STYLE_CONFIG["size"]):
            
            font = QFont(STYLE_CONFIG["family"])
            font.setPointSize(STYLE_CONFIG["size"])
            font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, STYLE_CONFIG["letter_spacing"])
            
            editor.setFont(font)
            doc.setDefaultFont(font)

        # 2. Force apply Block and Char formats
        self._apply_formats(editor, doc)

    def _apply_formats(self, editor, doc):
        """Apply paragraph (line height) and character (letter spacing) formats simultaneously"""
        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.SelectionType.Document)

        # A. Set paragraph format (Line Height)
        block_fmt = QTextBlockFormat()
        block_fmt.setLineHeight(
            STYLE_CONFIG["line_height"], 
            STYLE_CONFIG["line_height_type"]
        )
        cursor.mergeBlockFormat(block_fmt)

        # B. Set character format (Letter Spacing)
        char_fmt = QTextCharFormat()
        char_fmt.setFontLetterSpacingType(QFont.SpacingType.PercentageSpacing)
        char_fmt.setFontLetterSpacing(STYLE_CONFIG["letter_spacing"])
        
        cursor.mergeCharFormat(char_fmt)
        
        # Clear selection
        cursor.clearSelection()
#@-leo
