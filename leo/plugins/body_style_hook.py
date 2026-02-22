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


#@+node:swot.20260219114140.1: ** def init
def init():
    """Plugin entry point"""
    # 1. For newly opened windows (Ctrl+O, Ctrl+N)
    g.registerHandler("open2", on_window_init)

    # 2. For the first window when Leo starts
    g.registerHandler("start2", on_window_init)

    # 3. [Key Fix] For existing windows during plugin reload
    if g.app.commanders():
        for existing_c in g.app.commanders():
            on_window_init("reload", {"c": existing_c})

    g.es("Body Style Plugin loaded (Config Enabled).")
    return True


#@+node:swot.20260219114126.1: ** def on_window_init
def on_window_init(tag, keywords):
    """Universal window initialization function, handles startup, new windows, and reloads"""
    c = keywords.get("c")
    if not c:
        return

    # Prevent duplicate mounting (Singleton pattern)
    if hasattr(c, "_body_styler"):
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

    #@+node:swot.20260222181121.1: *3* def get_config
    def get_config(self):
        """Load settings from Leo's @data body-style-settings node"""
        # Default configuration fallback
        conf = {
            "family": "JetBrains Mono",
            "size": 16,
            "line_height": 125,
            "line_height_type": 1,
            "letter_spacing": 105,
        }

        # Fetch data from myLeoSettings.leo
        data = self.c.config.getData("body-style-settings")
        if data:
            for line in data:
                line = line.strip()
                # Skip empty lines or comments
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, val = [x.strip() for x in line.split("=", 1)]
                    if key in conf:
                        if key == "family":
                            conf[key] = val
                        else:
                            try:
                                conf[key] = int(val)
                            except ValueError:
                                g.es(f"BodyStyle Warning: Invalid number for {key}")
        return conf

    #@+node:swot.20260219115854.1: *3* def on_select
    def on_select(self, tag, keywords):
        """Apply style when switching nodes"""
        if keywords.get("c") != self.c:
            return
        QTimer.singleShot(0, self.apply_style)

    #@+node:swot.20260222110100.1: *3* def on_command
    def on_command(self, tag, keywords):
        """catch not trigger textChanged command"""
        if keywords.get("c") == self.c:
            QTimer.singleShot(0, self.apply_style)

    #@+node:swot.20260222110233.1: *3* def setup_qt_signals
    def setup_qt_signals(self):
        """Bind Qt document contentsChange signal"""
        editor = self.get_editor()
        if not editor:
            return

        doc = editor.document()
        if not doc:
            return

        try:
            doc.contentsChange.disconnect(self.on_contents_change)
        except Exception:
            pass

        doc.contentsChange.connect(self.on_contents_change)
        self.apply_style()

    #@+node:swot.20260222164552.1: *3* def on_contents_change
    def on_contents_change(self, position, charsRemoved, charsAdded):
        """Differentiate normal typing from abbrev expansion/paste"""
        if charsRemoved > 1 or charsAdded > 1:
            QTimer.singleShot(0, self.apply_style)
        else:
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

        config = self.get_config()

        current_font = editor.font()
        if (
            current_font.family() != config["family"]
            or current_font.pointSize() != config["size"]
        ):
            font = QFont(config["family"])
            font.setPointSize(config["size"])
            font.setLetterSpacing(
                QFont.SpacingType.PercentageSpacing, config["letter_spacing"]
            )

            editor.setFont(font)
            doc.setDefaultFont(font)

        self._apply_formats(editor, doc, config)

    #@+node:swot.20260219114021.1: *3* def _apply_formats
    def _apply_formats(self, editor, doc, config):
        """Apply paragraph (line height) and character (letter spacing) formats simultaneously"""
        v_scrollbar = editor.verticalScrollBar()
        current_scroll_value = v_scrollbar.value() if v_scrollbar else 0

        cursor = QTextCursor(doc)
        cursor.select(QTextCursor.SelectionType.Document)

        editor.blockSignals(True)
        doc.blockSignals(True)

        try:
            # A. Set paragraph format using dynamic config
            block_fmt = QTextBlockFormat()
            block_fmt.setLineHeight(config["line_height"], config["line_height_type"])
            cursor.mergeBlockFormat(block_fmt)

            # B. Set character format using dynamic config
            char_fmt = QTextCharFormat()
            
            char_fmt.setFontFamily(config["family"])
            char_fmt.setFontPointSize(config["size"])
            
            char_fmt.setFontLetterSpacingType(QFont.SpacingType.PercentageSpacing)
            char_fmt.setFontLetterSpacing(config["letter_spacing"])
            cursor.mergeCharFormat(char_fmt)
        finally:
            doc.blockSignals(False)
            editor.blockSignals(False)

            cursor.clearSelection()

            if v_scrollbar:
                v_scrollbar.setValue(current_scroll_value)

    #@-others


#@-others
#@-leo
