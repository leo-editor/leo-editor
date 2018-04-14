#@+leo-ver=5-thin
#@+node:ekr.20170428084208.157: * @file ../external/npyscreen/wgmultilineeditable.py
import curses
from . import wgwidget
from . import wgmultiline
from . import wgtextbox as textbox
from . import wgboxwidget
import leo.core.leoGlobals as g
assert g
#pylint: disable=no-member
#@+others
#@+node:ekr.20170428084208.159: ** class MultiLineEditable (MultiLine)
class MultiLineEditable(wgmultiline.MultiLine):
    _contained_widgets      = textbox.Textfield
    CHECK_VALUE             = True
    ALLOW_CONTINUE_EDITING  = True
    CONTINUE_EDITING_AFTER_EDITING_ONE_LINE = True

    #@+others
    #@+node:ekr.20170428084208.160: *3* MultiLineEditable.get_new_value
    def get_new_value(self):
        return ''

    #@+node:ekr.20170428084208.161: *3* MultiLineEditable.check_line_value
    def check_line_value(self, vl):
        if not vl:
            return False
        else:
            return True

    #@+node:ekr.20170428084208.162: *3* MultiLineEditable.edit_cursor_line_value
    def edit_cursor_line_value(self):
        if not self.values:
            self.insert_line_value()
            return False
        try:
            active_line = self._my_widgets[(self.cursor_line-self.start_display_at)]
        except IndexError:
            self._my_widgets[0] # Huh?
            self.cursor_line = 0
            self.insert_line_value()
            return True
        active_line.highlight = False
        active_line.edit()
        try:
            self.values[self.cursor_line] = active_line.value
        except IndexError:
            self.values.append(active_line.value)
            if not self.cursor_line:
                self.cursor_line = 0
            self.cursor_line = len(self.values) - 1
        self.reset_display_cache()

        if self.CHECK_VALUE:
            if not self.check_line_value(self.values[self.cursor_line]):
                self.delete_line_value()
                return False

        self.display()
        return True

    #@+node:ekr.20170428084208.163: *3* MultiLineEditable.insert_line_value
    def insert_line_value(self):
        if self.cursor_line is None:
            self.cursor_line = 0
        self.values.insert(self.cursor_line, self.get_new_value())
        self.display()
        cont = self.edit_cursor_line_value()
        if cont and self.ALLOW_CONTINUE_EDITING:
            self._continue_editing()

    #@+node:ekr.20170428084208.164: *3* MultiLineEditable.delete_line_value
    def delete_line_value(self):
        if self.values:
            del self.values[self.cursor_line]
            self.display()
    #@+node:ekr.20170428084208.165: *3* MultiLineEditable._continue_editing
    def _continue_editing(self):

        g.trace('(MultiLineEditable)')
        active_line = self._my_widgets[(self.cursor_line-self.start_display_at)]
        continue_editing = self.ALLOW_CONTINUE_EDITING
        if hasattr(active_line, 'how_exited'):
            while active_line.how_exited == wgwidget.EXITED_DOWN and continue_editing:
                self.values.insert(self.cursor_line+1, self.get_new_value())
                self.cursor_line += 1
                self.display()
                continue_editing = self.edit_cursor_line_value()
                active_line = self._my_widgets[(self.cursor_line-self.start_display_at)]

    #@+node:ekr.20170506041638.1: *3* MultiLineEditable.Handlers
    #@+node:ekr.20170428084208.166: *4* MultiLineEditable.h_insert_next_line
    def h_insert_next_line(self, ch):

        # pylint: disable=len-as-condition
        if len(self.values) == self.cursor_line - 1 or len(self.values) == 0:
            self.values.append(self.get_new_value())
            self.cursor_line += 1
            self.display()
            cont = self.edit_cursor_line_value()
            if cont and self.ALLOW_CONTINUE_EDITING:
                self._continue_editing()

        else:
            self.cursor_line += 1
            self.insert_line_value()

    #@+node:ekr.20170428084208.167: *4* MultiLineEditable.h_edit_cursor_line_value
    def h_edit_cursor_line_value(self, ch):
        continue_line = self.edit_cursor_line_value()
        if continue_line and self.CONTINUE_EDITING_AFTER_EDITING_ONE_LINE:
            self._continue_editing()

    #@+node:ekr.20170428084208.168: *4* MultiLineEditable.h_insert_value
    def h_insert_value(self, ch):
        return self.insert_line_value()

    #@+node:ekr.20170428084208.169: *4* MultiLineEditable.h_delete_line_value
    def h_delete_line_value(self, ch):
        self.delete_line_value()
    #@+node:ekr.20170428084208.170: *4* set_up_handlers
    def set_up_handlers(self):
        '''MultiLineEditable.set_up_handlers.'''
        super(MultiLineEditable, self).set_up_handlers()
        self.handlers.update ( {
            ord('i'):               self.h_insert_value,
            ord('o'):               self.h_insert_next_line,
            curses.ascii.CR:        self.h_edit_cursor_line_value,
            curses.ascii.NL:        self.h_edit_cursor_line_value,
            curses.ascii.SP:        self.h_edit_cursor_line_value,
            curses.ascii.DEL:       self.h_delete_line_value,
            curses.ascii.BS:        self.h_delete_line_value,
            curses.KEY_BACKSPACE:   self.h_delete_line_value,
        })
    #@-others
#@+node:ekr.20170428084208.171: ** class MultiLineEditableTitle
class MultiLineEditableTitle(wgmultiline.TitleMultiLine):
    _entry_type = MultiLineEditable

#@+node:ekr.20170428084208.172: ** class MultiLineEditableBoxed
class MultiLineEditableBoxed(wgboxwidget.BoxTitle):
    _contained_widget = MultiLineEditable

#@-others
#@@language python
#@@tabwidth -4
#@-leo
