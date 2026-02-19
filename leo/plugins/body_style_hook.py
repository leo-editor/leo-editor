#@+leo-ver=5-thin
#@+node:swot.20250715091430.1: * @file /Users/swot/app/leo-editor/leo/plugins/body_style_hook.py
#@@language python
"""
body_style_hook.py
Set consistent font and spacing for Leo's body pane without visual jumps.
"""
from leo.core import leoGlobals as g
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QTextBlockFormat, QTextCursor

# Throttle timer
_apply_timer = None

# Target style
TARGET_FONT_FAMILY = "JetBrains Mono"
TARGET_FONT_SIZE = 16
TARGET_LINE_HEIGHT = 30  # Percentage - reasonable line height

# Track applied styles to avoid unnecessary updates
_applied_fonts = {}  # Track font applications
_applied_line_heights = {}  # Track line height applications

# Flag to prevent recursion
_applying_style = False

# Global editor key
editor_key = None
#@+others
#@+node:swot.20250715095600.1: ** get_editor_key
def get_editor_key(c):
    """Get unique key for editor to track applied styles"""
    try:
        editorId = id(c.frame.body.wrapper.widget)
    except:
        editorId = None
    print("Enter function: get_editor_key(c) - ", editorId)
    return editorId
#@+node:swot.20250715095555.1: ** get_content_hash
def get_content_hash(c):
    """Get a hash of the current content to detect changes"""
    try:
        editor = c.frame.body.wrapper.widget
        if not editor or not editor.document():
            return None
        doc = editor.document()
        return f"{doc.characterCount()}_{doc.lastModified()}"
    except:
        return None
#@+node:swot.20250715095543.1: ** is_line_height_applied
def is_line_height_applied(c):
    """Check if line height has been applied to current content"""
    global editor_key
    if not editor_key:
        return False
    current_hash = get_content_hash(c)
    if not current_hash:
        return False
    stored_hash = _applied_line_heights.get(editor_key)
    return stored_hash == current_hash
#@+node:swot.20250715095521.1: ** mark_line_height_applied
def mark_line_height_applied(c):
    """Mark that line height has been applied to current content"""
    global editor_key
    current_hash = get_content_hash(c)
    if editor_key and current_hash:
        _applied_line_heights[editor_key] = current_hash
#@+node:swot.20250715095322.1: ** apply_line_height_only
def apply_line_height_only(c):
    """Apply only line height without changing font"""
    global _applying_style
    global editor_key
    
    if _applying_style:
        return  # Prevent recursion
        
    try:
        _applying_style = True
        
        editor = c.frame.body.wrapper.widget
        if not editor or not editor.document():
            return

        # Use global editor_key
        if not editor_key:
            return
        # Only apply if not already applied to current content
        if is_line_height_applied(c):
            return

        doc = editor.document()
        if doc:
            # Apply line height using block format
            block_format = QTextBlockFormat()
            block_format.setLineHeight(TARGET_LINE_HEIGHT, 2)  # PercentageHeight
            
            # Apply to all blocks
            block = doc.begin()
            while block.isValid():
                block_cursor = QTextCursor(block)
                block_cursor.setBlockFormat(block_format)
                block = block.next()
            
            mark_line_height_applied(c)

    except Exception as e:
        g.es("Failed to apply line height:", e)
    finally:
        _applying_style = False
#@+node:swot.20250715091647.1: ** init
def init():
    # Core events for style application
    g.registerHandler('start2', on_start)                # Apply once on startup
    g.registerHandler('select1', on_content_loaded)      # When node is selected (content loaded)
    
    # Text change events for abbreviation support
    # g.registerHandler('body-text-changed', on_text_changed)  # After text changes
    
    g.es("Body style plugin loaded (no visual jumps, with minimal event monitoring).")
    return True
#@+node:swot.20250715091739.1: *3* on_start
def on_start(tag, keywords):
    """Called on startup"""
    print("on_start")
    c = keywords.get('c')
    global editor_key
    if c:
        # Set global editor_key only once
        if editor_key is None:
            editor_key = get_editor_key(c)
        # Apply to existing editor on startup
        schedule_apply_once(c, delay=100)
        # Connect to Qt text change signal
        connect_qt_text_changed(c)
#@+node:swot.20250715095455.1: *4* schedule_apply_once
def schedule_apply_once(c, delay=50):
    """Schedule one-time style application"""

    # Only print once after some test,
    # so this Throttle is not very important!
    # print("calling: schedule_apply_once")

    global _apply_timer
    if _apply_timer:
        _apply_timer.stop()
        _apply_timer = None

    def run():
        global _apply_timer
        _apply_timer = None
        apply_editor_style_once(c)

    _apply_timer = QTimer()
    _apply_timer.setSingleShot(True)
    _apply_timer.timeout.connect(run)
    _apply_timer.start(delay)
#@+node:swot.20250715095513.1: *5* apply_editor_style_once
def apply_editor_style_once(c):
    """Apply style only once when editor is first created"""
    global _applying_style
    global editor_key

    if _applying_style:
        return  # Prevent recursion

    try:
        _applying_style = True

        editor = c.frame.body.wrapper.widget
        if not editor or not editor.document():
            return

        # Use global editor_key
        if not editor_key:
            return

        # Apply font settings (only once per editor)
        if not is_font_applied(editor_key):
            font = editor.font()
            font.setFamily(TARGET_FONT_FAMILY)
            font.setPointSize(TARGET_FONT_SIZE)
            font.setLetterSpacing(font.SpacingType.PercentageSpacing, 102)
            editor.setFont(font)
            mark_font_applied(editor_key)

        # Apply line height using document default format
        if not is_line_height_applied(c):
            doc = editor.document()
            if doc:
                # Get the font for document default
                font = editor.font()

                # Set document default block format
                default_format = QTextBlockFormat()
                default_format.setLineHeight(TARGET_LINE_HEIGHT, 2)  # PercentageHeight
                doc.setDefaultFont(font)

                # Apply to all existing blocks
                block = doc.begin()
                while block.isValid():
                    block_cursor = QTextCursor(block)
                    block_cursor.setBlockFormat(default_format)
                    block = block.next()

                mark_line_height_applied(c)

        g.es(f"Applied style to editor {editor_key}")

    except Exception as e:
        g.es("Failed to apply style:", e)
    finally:
        _applying_style = False
#@+node:swot.20250715095550.1: *6* is_font_applied
def is_font_applied(editor_key):
    """Check if font has already been applied to this editor"""
    if not editor_key:
        return False
    return editor_key in _applied_fonts
#@+node:swot.20250715095538.1: *6* mark_font_applied
def mark_font_applied(editor_key):
    """Mark that font has been applied to this editor"""
    if editor_key:
        _applied_fonts[editor_key] = True
#@+node:swot.20250715095416.1: *4* connect_qt_text_changed
def connect_qt_text_changed(c):
    """Connect to Qt text change signal for more reliable detection"""
    try:
        editor = c.frame.body.wrapper.widget
        if editor and hasattr(editor, 'textChanged'):
            # Connect to Qt's textChanged signal
            editor.textChanged.connect(lambda: on_qt_text_changed(c))
            g.es("Connected to Qt textChanged signal")
    except Exception as e:
        g.es("Failed to connect to Qt textChanged signal:", e)
#@+node:swot.20250715095411.1: *5* on_qt_text_changed
def on_qt_text_changed(c):
    """Called when Qt text editor content changes"""
    try:
        # Force re-application of line height
        force_reapply_line_height(c)
    except Exception as e:
        g.es("Failed to handle Qt text change:", e)
#@+node:swot.20250715091834.1: *6* force_reapply_line_height
def force_reapply_line_height(c):
    """Force re-application of line height by clearing tracking and reapplying"""
    global editor_key
    try:
        if editor_key and editor_key in _applied_line_heights:
            del _applied_line_heights[editor_key]
        
        # Apply line height immediately
        apply_line_height_only(c)
        
    except Exception as e:
        g.es("Failed to force reapply line height:", e)
#@+node:swot.20250715095403.1: *3* on_content_loaded
def on_content_loaded(tag, keywords):
    """Called when content is loaded into editor"""
    # print("on_content_loaded")
    c = keywords.get('c')
    if c:
        # Apply only line height when content changes
        apply_line_height_only(c)
#@-others
#@-leo
