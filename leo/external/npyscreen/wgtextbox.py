#@+leo-ver=5-thin
#@+node:ekr.20170428084208.318: * @file ../external/npyscreen/wgtextbox.py
#!/usr/bin/python
import curses
import curses.ascii
import sys
import locale
from . import wgwidget as widget
from . import npysGlobalOptions as GlobalOptions
from leo.core import leoGlobals as g
assert g

# pylint: disable=no-member
#@+others
#@+node:ekr.20170428084208.320: ** class TextfieldBase (Widget)
class TextfieldBase(widget.Widget):
    ENSURE_STRING_VALUE = True
    #@+others
    #@+node:ekr.20170428084208.321: *3* TextfieldBase.__init__
    def __init__(self, screen,
        value='',
        highlight_color='CURSOR',
        highlight_whole_widget=False,
        invert_highlight_color=True,
        **keywords
    ):
        # For Leo, called from MultiLine.make_contained_widgets.
        # g.trace('TextfieldBase: value', repr(value), g.callers())
        try:
            self.value = value or ""
        except Exception:
            self.value = ""

        super(TextfieldBase, self).__init__(screen, **keywords)

        if GlobalOptions.ASCII_ONLY or locale.getpreferredencoding() == 'US-ASCII':
            self._force_ascii = True
        else:
            self._force_ascii = False

        self.cursor_position = False
        self.highlight_color = highlight_color
        self.highlight_whole_widget = highlight_whole_widget
        self.invert_highlight_color = invert_highlight_color
        self.show_bold = False
        self.highlight = False
        self.important = False

        self.syntax_highlighting = False
        self._highlightingdata = None
        self.left_margin = 0

        self.begin_at = 0  # Where does the display string begin?
        self.set_text_widths()
        self.update()

    #@+node:ekr.20170428084208.322: *3* set_text_widths
    def set_text_widths(self):
        if self.on_last_line:
            self.maximum_string_length = self.width - 2  # Leave room for the cursor
        else:
            self.maximum_string_length = self.width - 1  # Leave room for the cursor at the end of the string.
    #@+node:ekr.20170428084208.323: *3* resize
    def resize(self):
        self.set_text_widths()
    #@+node:ekr.20170428084208.324: *3* calculate_area_needed
    def calculate_area_needed(self):
        "Need one line of screen, and any width going"
        return 1, 0

    #@+node:ekr.20170428084208.325: *3* TextfieldBase.update (LeoTreeLine USED TO override this)
    update_count = 0

    def update(self, clear=True, cursor=True):
        """Update the contents of the textbox, without calling the final refresh to the screen"""
        # pylint: disable=arguments-differ

        # cursor not working. See later for a fake cursor
            #if self.editing: pmfuncs.show_cursor()
            #else: pmfuncs.hide_cursor()
        # Not needed here -- gets called too much!
            #pmfuncs.hide_cursor()

        self.update_count += 1
        # name = self.__class__.__name__
        # if name.startswith('LeoLogTextField'):
            # g.trace('=====', name, g.callers())
            # g.trace('(TextfieldBase) %3s %s TextfieldBase: cursor: %5r %s' % (
                # self.update_count, id(self), self.cursor_position, self.value))
        if clear: self.clear()
        if self.hidden:
            return True
        value_to_use_for_calculations = self.value
        if self.ENSURE_STRING_VALUE:
            if value_to_use_for_calculations in (None, False, True):
                value_to_use_for_calculations = ''
                self.value = ''
        if self.begin_at < 0: self.begin_at = 0
        if self.left_margin >= self.maximum_string_length:
            raise ValueError
        if self.editing:
            if isinstance(self.value, bytes):
                # use a unicode version of self.value to work out where the cursor is.
                # not always accurate, but better than the bytes
                value_to_use_for_calculations = self.display_value(self.value).decode(self.encoding, 'replace')
            if cursor:
                if self.cursor_position is False:
                    self.cursor_position = len(value_to_use_for_calculations)

                elif self.cursor_position > len(value_to_use_for_calculations):
                    self.cursor_position = len(value_to_use_for_calculations)

                elif self.cursor_position < 0:
                    self.cursor_position = 0

                if self.cursor_position < self.begin_at:
                    self.begin_at = self.cursor_position

                while self.cursor_position > self.begin_at + self.maximum_string_length - self.left_margin:  # -1:
                    self.begin_at += 1
            else:
                if self.do_colors():
                    self.parent.curses_pad.bkgdset(' ', self.parent.theme_manager.findPair(self, self.highlight_color) | curses.A_STANDOUT)
                else:
                    self.parent.curses_pad.bkgdset(' ', curses.A_STANDOUT)
        # Do this twice so that the _print method can ignore it if needed.
        if self.highlight:
            if self.do_colors():
                if self.invert_highlight_color:
                    attributes = self.parent.theme_manager.findPair(self, self.highlight_color) | curses.A_STANDOUT
                else:
                    attributes = self.parent.theme_manager.findPair(self, self.highlight_color)
                self.parent.curses_pad.bkgdset(' ', attributes)
            else:
                self.parent.curses_pad.bkgdset(' ', curses.A_STANDOUT)
        if self.show_bold:
            self.parent.curses_pad.attron(curses.A_BOLD)
        if self.important and not self.do_colors():
            self.parent.curses_pad.attron(curses.A_UNDERLINE)
        self._print()
        # reset everything to normal
        self.parent.curses_pad.attroff(curses.A_BOLD)
        self.parent.curses_pad.attroff(curses.A_UNDERLINE)
        self.parent.curses_pad.bkgdset(' ', curses.A_NORMAL)
        self.parent.curses_pad.attrset(0)
        if self.editing and cursor:
            self.print_cursor()
    #@+node:ekr.20170428084208.326: *3* TextfieldBase.print_cursor
    def print_cursor(self):
        # This needs fixing for Unicode multi-width chars.

        # Cursors do not seem to work on pads.
            #self.parent.curses_pad.move(self.rely, self.cursor_position - self.begin_at)
        # let's have a fake cursor
            # _cur_loc_x = self.cursor_position - self.begin_at + self.relx + self.left_margin
        # The following two lines work fine for ascii, but not for unicode
            #char_under_cur = self.parent.curses_pad.inch(self.rely, _cur_loc_x)
            #self.parent.curses_pad.addch(self.rely, self.cursor_position - self.begin_at + self.relx, char_under_cur, curses.A_STANDOUT)
        #The following appears to work for unicode as well.

        try:
            #char_under_cur = self.value[self.cursor_position] #use the real value
            char_under_cur = self._get_string_to_print()[self.cursor_position]
            char_under_cur = self.safe_string(char_under_cur)
        except IndexError:
            char_under_cur = ' '
        except TypeError:
            char_under_cur = ' '
        if self.do_colors():
            self.parent.curses_pad.addstr(
                self.rely,
                self.cursor_position - self.begin_at + self.relx + self.left_margin,
                char_under_cur,
                self.parent.theme_manager.findPair(self, 'CURSOR_INVERSE'))
        else:
            self.parent.curses_pad.addstr(
                self.rely,
                self.cursor_position - self.begin_at + self.relx + self.left_margin,
                char_under_cur,
                curses.A_STANDOUT)
    #@+node:ekr.20170428084208.327: *3* print_cursor_pre_unicode
    def print_cursor_pre_unicode(self):
        # Cursors do not seem to work on pads.
            #self.parent.curses_pad.move(self.rely, self.cursor_position - self.begin_at)
        # let's have a fake cursor
            # _cur_loc_x = self.cursor_position - self.begin_at + self.relx + self.left_margin
        # The following two lines work fine for ascii, but not for unicode
            #char_under_cur = self.parent.curses_pad.inch(self.rely, _cur_loc_x)
            #self.parent.curses_pad.addch(self.rely, self.cursor_position - self.begin_at + self.relx, char_under_cur, curses.A_STANDOUT)
        #The following appears to work for unicode as well.
        try:
            char_under_cur = self.display_value(self.value)[self.cursor_position]
        except Exception:
            char_under_cur = ' '

        self.parent.curses_pad.addstr(self.rely, self.cursor_position - self.begin_at + self.relx + self.left_margin, char_under_cur, curses.A_STANDOUT)
    #@+node:ekr.20170428084208.328: *3* display_value
    def display_value(self, value):
        if value == None:
            return ''
        else:
            try:
                str_value = str(value)
            except UnicodeEncodeError:
                str_value = self.safe_string(value)
                return str_value
            except ReferenceError:
                return ">*ERROR*ERROR*ERROR*<"
            return self.safe_string(str_value)
    #@+node:ekr.20170428084208.329: *3* TextFieldBase.find_width_of_char
    def find_width_of_char(self, ch):
        return 1
    #@+node:ekr.20170428084208.330: *3* _print_unicode_char
    def _print_unicode_char(self, ch):
        '''return the ch to print.  For python 3 this is just ch.'''
        # pylint: disable=arguments-differ
        if self._force_ascii:
            return ch.encode('ascii', 'replace')
        elif sys.version_info[0] >= 3:
            return ch
        else:
            return ch.encode('utf-8', 'strict')
    #@+node:ekr.20170428084208.331: *3* TextfieldBase._get_string_to_print
    def _get_string_to_print(self):
        string_to_print = self.display_value(self.value)
        if not string_to_print:
            return None
        string_to_print = string_to_print[
            self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin]

        if sys.version_info[0] >= 3:
            string_to_print = self.display_value(self.value)[
                self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin]
        else:
            # ensure unicode only here encoding here.
            dv = self.display_value(self.value)
            if isinstance(dv, bytes):
                dv = dv.decode(self.encoding, 'replace')
            string_to_print = dv[
                self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin]
        return string_to_print
    #@+node:ekr.20170428084208.332: *3* TextfieldBase._print
    def _print(self):
        string_to_print = self._get_string_to_print()
        if not string_to_print:
            return None
        string_to_print = string_to_print[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin]

        if sys.version_info[0] >= 3:
            string_to_print = self.display_value(self.value)[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin]
        else:
            # ensure unicode only here encoding here.
            dv = self.display_value(self.value)
            if isinstance(dv, bytes):
                dv = dv.decode(self.encoding, 'replace')
            string_to_print = dv[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin]

        column = 0
        place_in_string = 0
        if self.syntax_highlighting:
            self.update_highlighting(start=self.begin_at, end=self.maximum_string_length + self.begin_at - self.left_margin)
            while column <= (self.maximum_string_length - self.left_margin):
                if not string_to_print or place_in_string > len(string_to_print) - 1:
                    break
                width_of_char_to_print = self.find_width_of_char(string_to_print[place_in_string])
                if column - 1 + width_of_char_to_print > self.maximum_string_length:
                    break
                try:
                    highlight = self._highlightingdata[self.begin_at + place_in_string]
                except Exception:
                    highlight = curses.A_NORMAL
                self.parent.curses_pad.addstr(
                    self.rely,
                    self.relx + column + self.left_margin,
                    self._print_unicode_char(string_to_print[place_in_string]),
                    highlight
                )
                column += self.find_width_of_char(string_to_print[place_in_string])
                place_in_string += 1
        else:
            if self.do_colors():
                if self.show_bold and self.color == 'DEFAULT':
                    color = self.parent.theme_manager.findPair(self, 'BOLD') | curses.A_BOLD
                elif self.show_bold:
                    color = self.parent.theme_manager.findPair(self, self.color) | curses.A_BOLD
                elif self.important:
                    color = self.parent.theme_manager.findPair(self, 'IMPORTANT') | curses.A_BOLD
                else:
                    color = self.parent.theme_manager.findPair(self)
            else:
                if self.important or self.show_bold:
                    color = curses.A_BOLD
                else:
                    color = curses.A_NORMAL
            while column <= (self.maximum_string_length - self.left_margin):
                if not string_to_print or place_in_string > len(string_to_print) - 1:
                    if self.highlight_whole_widget:
                        self.parent.curses_pad.addstr(
                            self.rely,
                            self.relx + column + self.left_margin,
                            ' ',
                            color,
                        )
                        column += width_of_char_to_print
                        place_in_string += 1
                        continue
                    else:
                        break
                width_of_char_to_print = self.find_width_of_char(string_to_print[place_in_string])
                if column - 1 + width_of_char_to_print > self.maximum_string_length:
                    break
                self.parent.curses_pad.addstr(
                    self.rely,
                    self.relx + column + self.left_margin,
                    self._print_unicode_char(string_to_print[place_in_string]),
                    color,
                )
                column += width_of_char_to_print
                place_in_string += 1
    #@+node:ekr.20170428084208.333: *3* _print_pre_unicode
    def _print_pre_unicode(self):
        # This method was used to print the string before we became interested in unicode.

        string_to_print = self.display_value(self.value)
        if string_to_print == None: return

        if self.syntax_highlighting:
            self.update_highlighting(start=self.begin_at, end=self.maximum_string_length + self.begin_at - self.left_margin)
            for i in range(len(string_to_print[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin])):
                try:
                    highlight = self._highlightingdata[self.begin_at + i]
                except Exception:
                    highlight = curses.A_NORMAL
                self.parent.curses_pad.addstr(
                    self.rely, self.relx + i + self.left_margin,
                    string_to_print[self.begin_at + i],
                    highlight
                )
        elif self.do_colors():
            coltofind = 'DEFAULT'
            if self.show_bold and self.color == 'DEFAULT':
                coltofind = 'BOLD'
            if self.show_bold:
                self.parent.curses_pad.addstr(
                    self.rely,
                    self.relx + self.left_margin,
                    string_to_print[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin],
                    self.parent.theme_manager.findPair(self, coltofind) | curses.A_BOLD)
            elif self.important:
                coltofind = 'IMPORTANT'
                self.parent.curses_pad.addstr(
                    self.rely,
                    self.relx + self.left_margin,
                    string_to_print[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin],
                    self.parent.theme_manager.findPair(self, coltofind) | curses.A_BOLD)
            else:
                self.parent.curses_pad.addstr(
                    self.rely,
                    self.relx + self.left_margin,
                    string_to_print[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin],
                    self.parent.theme_manager.findPair(self))
        else:
            if self.important:
                self.parent.curses_pad.addstr(
                    self.rely,
                    self.relx + self.left_margin,
                    string_to_print[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin],
                    curses.A_BOLD)
            elif self.show_bold:
                self.parent.curses_pad.addstr(
                    self.rely,
                    self.relx + self.left_margin,
                    string_to_print[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin],
                    curses.A_BOLD)
            else:
                self.parent.curses_pad.addstr(
                    self.rely,
                    self.relx + self.left_margin,
                    string_to_print[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin])
    #@+node:ekr.20170428084208.334: *3* update_highlighting
    def update_highlighting(self, start=None, end=None, clear=False):
        if clear or (self._highlightingdata == None):
            self._highlightingdata = []

        # string_to_print = self.display_value(self.value)
        self.display_value(self.value)
    #@-others
#@+node:ekr.20170428084208.335: ** class Textfield (TextfieldBase)
class Textfield(TextfieldBase):
    #@+others
    #@+node:ekr.20170428084208.336: *3* Textfield.show_brief_message
    def show_brief_message(self, message):
        curses.beep()
        keep_for_a_moment = self.value
        self.value = message
        self.editing = False
        self.display()
        curses.napms(1200)
        self.editing = True
        self.value = keep_for_a_moment


    #@+node:ekr.20170428084208.337: *3* Textfield.edit
    def edit(self):

        # g.trace('===== (Textfield:%s)' % self.__class__.__name__)
        self.editing = 1
        if self.cursor_position is False:
            self.cursor_position = len(self.value or '')
        self.parent.curses_pad.keypad(1)

        self.old_value = self.value

        self.how_exited = False

        while self.editing:
            self.display()
            self.get_and_use_key_press()

        self.begin_at = 0
        self.display()
        self.cursor_position = False
        return self.how_exited, self.value
    #@+node:ekr.20170428084208.339: *3* Textfield.t_input_isprint
    def t_input_isprint(self, inp):
        if self._last_get_ch_was_unicode and inp not in '\n\t\r':
            return True
        # if curses.ascii.isprint(inp) and \
        # (chr(inp) not in '\n\t\r'):
            # return True
        # else:
            # return False
        return curses.ascii.isprint(inp) and chr(inp) not in '\n\t\r'


    #@+node:ekr.20170526065621.1: *3* Textfield handlers
    #@+node:ekr.20170428084208.340: *4* Textfield.h_addch
    def h_addch(self, inp):
        if self.editable:
            #self.value = self.value[:self.cursor_position] + curses.keyname(input) \
            #   + self.value[self.cursor_position:]
            #self.cursor_position += len(curses.keyname(input))

            # workaround for the metamode bug:
            if self._last_get_ch_was_unicode == True and isinstance(self.value, bytes):
                # probably dealing with python2.
                ch_adding = inp
                self.value = self.value.decode()
            elif self._last_get_ch_was_unicode == True:
                ch_adding = inp
            else:
                try:
                    ch_adding = chr(inp)
                except TypeError:
                    ch_adding = input
            self.value = self.value[:self.cursor_position] + ch_adding \
                + self.value[self.cursor_position:]
            self.cursor_position += len(ch_adding)

            # or avoid it entirely:
            #self.value = self.value[:self.cursor_position] + curses.ascii.unctrl(input) \
            #   + self.value[self.cursor_position:]
            #self.cursor_position += len(curses.ascii.unctrl(input))

    #@+node:ekr.20170428084208.341: *4* Textfield.h_cursor_left
    def h_cursor_left(self, input):
        self.cursor_position -= 1

    #@+node:ekr.20170428084208.342: *4* Textfield.h_cursor_right
    def h_cursor_right(self, input):
        self.cursor_position += 1

    #@+node:ekr.20170428084208.343: *4* Textfield.h_delete_left
    def h_delete_left(self, input):
        if self.editable and self.cursor_position > 0:
            self.value = self.value[: self.cursor_position - 1] + self.value[self.cursor_position:]

        self.cursor_position -= 1
        self.begin_at -= 1


    #@+node:ekr.20170428084208.344: *4* Textfield.h_delete_right
    def h_delete_right(self, input):
        if self.editable:
            self.value = self.value[:self.cursor_position] + self.value[self.cursor_position + 1 :]

    #@+node:ekr.20170428084208.345: *4* Textfield.h_erase_left
    def h_erase_left(self, input):
        if self.editable:
            self.value = self.value[self.cursor_position:]
            self.cursor_position = 0

    #@+node:ekr.20170428084208.346: *4* Textfield.h_erase_right
    def h_erase_right(self, input):
        if self.editable:
            self.value = self.value[:self.cursor_position]
            self.cursor_position = len(self.value)
            self.begin_at = 0

    #@+node:ekr.20170428084208.347: *4* Textfield.handle_mouse_event
    def handle_mouse_event(self, mouse_event):
        #mouse_id, x, y, z, bstate = mouse_event
        #rel_mouse_x = x - self.relx - self.parent.show_atx
        mouse_id, rel_x, rel_y, z, bstate = self.interpret_mouse_event(mouse_event)
        self.cursor_position = rel_x + self.begin_at
        self.display()


    #@+node:ekr.20170428084208.338: *4* Textfield.set_up_handlers
    def set_up_handlers(self):
        '''Textfield.set_up_handlers.'''
        super(Textfield, self).set_up_handlers()
        # For OS X
        # del_key = curses.ascii.alt('~')
        self.handlers.update({
            curses.KEY_LEFT: self.h_cursor_left,
            curses.KEY_RIGHT: self.h_cursor_right,
            curses.KEY_DC: self.h_delete_right,
            curses.ascii.DEL: self.h_delete_left,
            curses.ascii.BS: self.h_delete_left,
            curses.KEY_BACKSPACE: self.h_delete_left,
            # mac os x curses reports DEL as escape oddly
            # no solution yet
            "^K": self.h_erase_right,
            "^U": self.h_erase_left,
        })
        self.complex_handlers.extend((
            (self.t_input_isprint, self.h_addch),
            # (self.t_is_ck, self.h_erase_right),
            # (self.t_is_cu, self.h_erase_left),
        ))

    #@-others
#@+node:ekr.20170428084208.348: ** class FixedText (TextfieldBase)
class FixedText(TextfieldBase):
    #@+others
    #@+node:ekr.20170428084208.349: *3* FixedText.set_up_handlers
    def set_up_handlers(self):
        '''FixedText.set_up_handlers.'''
        super(FixedText, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_LEFT: self.h_cursor_left,
            curses.KEY_RIGHT: self.h_cursor_right,
            ord('k'): self.h_exit_up,
            ord('j'): self.h_exit_down,
        })


    #@+node:ekr.20170428084208.350: *3* FixedText.h_cursor_left
    def h_cursor_left(self, input):
        if self.begin_at > 0:
            self.begin_at -= 1

    #@+node:ekr.20170428084208.351: *3* FixedText.h_cursor_right
    def h_cursor_right(self, input):
        if len(self.value) - self.begin_at > self.maximum_string_length:
            self.begin_at += 1

    #@+node:ekr.20170428084208.352: *3* FixedText.update
    def update(self, clear=True,):
        # pylint: disable=arguments-differ
        super(FixedText, self).update(clear=clear, cursor=False)

    #@+node:ekr.20170428084208.353: *3* FixedText.edit
    def edit(self):
        self.editing = 1
        self.highlight = False
        self.cursor_position = 0
        self.parent.curses_pad.keypad(1)

        self.old_value = self.value

        self.how_exited = False

        while self.editing:
            self.display()
            self.get_and_use_key_press()

        self.begin_at = 0
        self.highlight = False
        self.display()

        return self.how_exited, self.value

    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@nobeautify
#@-leo
