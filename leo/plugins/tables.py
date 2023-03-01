#@+leo-ver=5-thin
#@+node:ekr.20170217164004.1: * @file ../plugins/tables.py
"""
A plugin that inserts tables, inspired by org mode tables:

Written by Edward K. Ream, February 17, 2017.
"""
from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20170217164709.1: ** top level
#@+node:ekr.20170217164759.1: *3* tables.py:commands
# Note: importing this plugin creates the commands.

@g.command('table-align')
def table_align(self, event=None):
    c = event.get('c')
    controller = c and getattr(c, 'tableController')
    if controller:
        controller.align()

@g.command('table-toggle-enabled')
def table_toggle_enabled(self, event=None):
    c = event.get('c')
    controller = c and getattr(c, 'tableController')
    if controller:
        controller.toggle()
#@+node:ekr.20170217164730.1: *3* tables.py:init
def init():
    """Return True if the plugin has loaded successfully."""
    ok = g.app.gui.guiName() in ('qt', 'qttabs')
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.plugin_signon(__name__)
    return ok
#@+node:ekr.20170217165001.1: *3* tables.py:onCreate
def onCreate(tag, keys):
    """Create a Tables instance for the outline."""
    c = keys.get('c')
    if c:
        c.tableController = TableController(c)
    else:
        g.trace('can not create TableController')
#@+node:ekr.20170217164903.1: ** class TableController
class TableController:
    """A class to create and align tables."""

    def __init__(self, c):
        """Ctor for TableController class."""
        self.c = c
        self.ec = c.editCommands
        self.enabled = True
        # Monkey-patch k.handleDefaultChar
        self.old_handleDefaultChar = c.k.handleDefaultChar
        c.k.handleDefaultChar = self.default_key_handler
        # Monkey-patch c.editCommands.insertNewLine
        self.old_insert_newline = c.editCommands.insertNewlineBase
        c.editCommands.insertNewlineBase = self.insert_newline

    #@+others
    #@+node:ekr.20170218142054.1: *3* table.abort
    def abort(self):
        """undo all monkey-patches."""
        g.es_print('exiting table.py plugin')
        c, ec = self.c, self.ec
        c.tableController = None
        c.k.handleDefaultChar = self.old_handleDefaultChar
        ec.insertNewlineBase = self.old_insert_newline
    #@+node:ekr.20170218073117.1: *3* table.default_key_handler
    def default_key_handler(self, event, stroke):
        """
        TableController: Override k.old_handleDefaultChar.

        Important: the code must use event.ch, not stroke.
        """
        w = self.ec.editWidget(event)
        ch = event.char
        i, s, lines = self.get_table(ch, w)
        if lines:
            self.put(ch, event)
            # Not yet: self.update()
        else:
            self.put(ch, event)

    #@+node:ekr.20170218130241.1: *3* table.get_table
    def get_table(self, ch, w):
        """Return i, lines, if w's insert point is inside a table."""
        s = w.getAllText()
        lines = g.splitLines(s)
        ins = w.getInsertPoint()
        i_row1, i_col1 = g.convertPythonIndexToRowCol(s, ins)
        s1 = lines[i_row1] if i_row1 < len(lines) else ''
        starts_row1 = ch in ('|', 'return') and not s1[:i_col1].strip()
        if self.enabled and g.isTextWrapper(w):
            i1, i2 = None, None
            for i, s in enumerate(lines):
                is_row = s.strip().startswith('|')
                if i == i_row1:
                    if is_row or starts_row1:
                        if i1 is None:
                            i1 = i2 = i  # Selected line starts the table.
                        else:
                            pass  # Table head already found.
                    elif i1 is None:
                        return -1, s1, []
                    # Selected line ends the table.
                    return i_row1, s1, lines[i1:i]
                if is_row:
                    if i1 is None:
                        i1 = i2 = i  # Row i starts the head.
                    elif i > i_row1:
                        i2 = i  # Row i extends the tail
                    else:
                        pass  # Table head already found.
                else:
                    if i1 is None:
                        pass  # Table head not yet found.
                    elif i < i_row1:
                        i1 = None  # Forget previous tables.
                        i2 = None
                    else:
                        # Selected line ends the table.
                        return i_row1, s1, lines[i1:i]
            # The end of the enumeration.
            if i_row1 == len(lines) and starts_row1 and not i1:
                g.trace('FOUND-end', i1)
                return i_row1, s1, [s1]
            if i1 is None or i2 is None:
                return -1, s1, []
            # Last line ends the table.
            return i_row1, s1, lines[i1 : len(lines)]
        return -1, s1, []
    #@+node:ekr.20170218075243.1: *3* table.insert_newline
    def insert_newline(self, event):
        """TableController: override c.editCommands.insertNewLine."""
        w = self.ec.editWidget(event)
        i, s, lines = self.get_table('return', w)
        if lines:
            self.put('\n', event)
            self.put('|', event)
        else:
            self.put('\n', event)
    #@+node:ekr.20170218135553.1: *3* table.put
    def put(self, ch, event):
        """
        Insert the given ch into w.
        ch must be valid as stroke.s
        """
        try:
            # Patch the event.
            event.char = ch
            event.stroke = g.KeyStroke(ch)
            self.old_handleDefaultChar(event, stroke=None)
        except Exception:
            g.es_exception()
            self.abort()
    #@+node:ekr.20170218125521.1: *3* table.toggle
    def toggle(self, event=None):
        """Toggle enabling."""
        self.enabled = not self.enabled
    #@+node:ekr.20170218134104.1: *3* table.update (not used)
    # def update(self, event, i, lines, stroke):

        # # self.old_handleDefaultChar(event, stroke)
        # self.put(ch, w)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
