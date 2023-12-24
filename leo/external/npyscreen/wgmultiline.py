#@+leo-ver=5-thin
#@+node:ekr.20170428084208.68: * @file ../external/npyscreen/wgmultiline.py
#!/usr/bin/python
# pylint: disable=no-member
# type: ignore
import collections
import copy
import curses
import textwrap
import weakref
from . import wgwidget as widget
from . import wgtextbox as textbox
from . import wgtitlefield as titlefield
from . import fmPopup as Popup
from leo.core import leoGlobals as g
assert g
MORE_LABEL = "- more -"  # string to tell user there are more options
#@+others
#@+node:ekr.20170428084208.69: ** Declarations
#@+node:ekr.20170428084208.70: ** class FilterPopupHelper
class FilterPopupHelper(Popup.Popup):
    #@+others
    #@+node:ekr.20170428084208.71: *3* create
    def create(self):
        super(FilterPopupHelper, self).create()
        self.filterbox = self.add(titlefield.TitleText, name='Find:',)
        self.nextrely += 1
        self.statusline = self.add(textbox.Textfield, color='LABEL', editable=False)

    #@+node:ekr.20170428084208.72: *3* updatestatusline
    def updatestatusline(self):
        self.owner_widget._filter = self.filterbox.value
        filtered_lines = self.owner_widget.get_filtered_indexes()
        len_f = len(filtered_lines)
        if self.filterbox.value == None or self.filterbox.value == '':
            self.statusline.value = ''
        elif len_f == 0:
            self.statusline.value = '(No Matches)'
        elif len_f == 1:
            self.statusline.value = '(1 Match)'
        else:
            self.statusline.value = '(%s Matches)' % len_f

    #@+node:ekr.20170428084208.73: *3* adjust_widgets
    def adjust_widgets(self):
        self.updatestatusline()
        self.statusline.display()




    #@-others
#@+node:ekr.20170428084208.74: ** class MultiLine (Widget)
class MultiLine(widget.Widget):
    _safe_to_display_cache = True
    """
    Display a list of items to the user. By overloading the display_value
    method, this widget can be made to display different kinds of objects.
    Given the standard definition, the same effect can be achieved by
    altering the __str__() method of displayed objects
    """
    _MINIMUM_HEIGHT = 2  # Raise an error if not given this.
    _contained_widgets = textbox.Textfield
    _contained_widget_height = 1
    #@+others
    #@+node:ekr.20170428084208.75: *3* MultiLine.__init__
    def __init__(self, screen,
        values=None,
        value=None,
        slow_scroll=False,
        scroll_exit=False,
        return_exit=False,
        select_exit=False,
        exit_left=False,
        exit_right=False,
        widgets_inherit_color=False,
        always_show_cursor=False,
        allow_filtering=True,
        **keywords
    ):
        self.never_cache = False
        self.exit_left = exit_left
        self.exit_right = exit_right
        self.allow_filtering = allow_filtering
        self.widgets_inherit_color = widgets_inherit_color
        super(MultiLine, self).__init__(screen, **keywords)  # Call the base class.
        if self.height < self.__class__._MINIMUM_HEIGHT:
            raise widget.NotEnoughSpaceForWidget(
                "Height of %s allocated. Not enough space allowed for %s" % (
                    self.height, str(self)))
        self.make_contained_widgets()
        self.return_exit = return_exit
            # does pushing return select and then leave the widget?
        self.select_exit = select_exit
            # does any selection leave the widget?
        self.always_show_cursor = always_show_cursor
            # Show cursor even when not editing?
        self.slow_scroll = slow_scroll
        self.scroll_exit = scroll_exit
        # EKR: Cursor and value ivars.
        self.start_display_at = 0
        self.cursor_line = 0
        self.values = values or []
        self.value = value
        self._filter = None
        # For optimization...
        self._last_start_display_at = None
        self._last_cursor_line = None
        self._last_values = copy.copy(values)
        self._last_value = copy.copy(value)
        self._last_filter = None
        self._filtered_values_cache = []
        # override - it looks nicer.
        if self.scroll_exit:
            self.slow_scroll = True
    #@+node:ekr.20170428084208.76: *3* MultiLine.resize
    def resize(self):
        super(MultiLine, self).resize()
        self.make_contained_widgets()
        self.reset_display_cache()
        self.display()

    #@+node:ekr.20170428084208.77: *3* MultiLine.make_contained_widgets
    def make_contained_widgets(self):
        # The *only* make_contained_widgets (plural) in npyscreen.
        trace = False
        trace_widgets = True
        self._my_widgets = []
        height = self.height // self.__class__._contained_widget_height
        if trace: g.trace(self.__class__.__name__, height)  #, g.callers(2))
            # Called from BoxTitle.make_contained_widget.
        for h in range(height):
            # EKR: it's LeoMLTree._contained_widgets that we have to emulate.
            self._my_widgets.append(
                self._contained_widgets(
                    self.parent,
                    rely=(h * self._contained_widget_height) + self.rely,
                    relx=self.relx,
                    max_width=self.width,
                    max_height=self.__class__._contained_widget_height
            ))
        if trace and trace_widgets:
            g.printList(self._my_widgets)
            g.printList(['value: %r' % (z.value) for z in self._my_widgets])
    #@+node:ekr.20170428084208.78: *3* MultiLine.display_value
    def display_value(self, vl):
        """Overload this function to change how values are displayed.
        Should accept one argument (the object to be represented), and return a string or the
        object to be passed to the contained widget."""
        try:
            return self.safe_string(str(vl))
        except ReferenceError:
            return "**REFERENCE ERROR**"
        try:
            return "Error displaying " + self.safe_string(repr(vl))
        except Exception:
            return "**** Error ****"
    #@+node:ekr.20170428084208.79: *3* MultiLine.calculate_area_needed
    def calculate_area_needed(self):
        return 0, 0
    #@+node:ekr.20170428084208.80: *3* MultiLine.reset_cursor
    def reset_cursor(self):
        self.start_display_at = 0
        self.cursor_line = 0
    #@+node:ekr.20170428084208.81: *3* MultiLine.reset_display_cache
    def reset_display_cache(self):
        self._last_values = False
        self._last_value = False
    #@+node:ekr.20170428084208.82: *3* MultiLine.update (LeoMLTree overrides this)
    def update(self, clear=True):
        trace = False  # LeoMLTree.update overrides this.
        if trace and self.hidden:
            g.trace('hidden')
        if self.hidden and clear:
            self.clear()
            return False
        elif self.hidden:
            return False
        if self.values == None:
            self.values = []
        # clear = None is a good value for this widget
        display_length = len(self._my_widgets)
        #self._remake_filter_cache()
        self._filtered_values_cache = self.get_filtered_indexes()
        if self.editing or self.always_show_cursor:
            # EKR: Put cursor_line in range.
            if self.cursor_line < 0:
                self.cursor_line = 0
            if self.cursor_line > len(self.values) - 1:
                self.cursor_line = len(self.values) - 1
            if self.slow_scroll:
                # Scroll by lines.
                if self.cursor_line > self.start_display_at + display_length - 1:
                    self.start_display_at = self.cursor_line - (display_length - 1)
                if self.cursor_line < self.start_display_at:
                    self.start_display_at = self.cursor_line
            else:
                # Scroll by pages.
                if self.cursor_line > self.start_display_at + (display_length - 2):
                    self.start_display_at = self.cursor_line
                if self.cursor_line < self.start_display_at:
                    self.start_display_at = self.cursor_line - (display_length - 2)
                    if self.start_display_at < 0: self.start_display_at = 0
        # Don't update the screen if nothing has changed.
        # no_change = False
        try:
            no_change = (
                self._safe_to_display_cache and
                self._last_value is self.value and
                self.values == self._last_values and
                self.start_display_at == self._last_start_display_at and
                clear != True and
                self._last_cursor_line == self.cursor_line and
                self._last_filter == self._filter and
                self.editing
            )
        except Exception:
            no_change = False
        if clear:
            no_change = False
        if trace:
            from . import npysTree as npysTree
            val = self.values[self.cursor_line]
            # name = val.__class__.__name__
            if isinstance(val, npysTree.TreeData):
                val = val.get_content()
            g.trace('changed: %5s, cursor_line: %s %s' % (
                not no_change, self.cursor_line, val))
                # self.start_display_at,
        if not no_change or clear or self.never_cache:
            if clear is True:
                self.clear()
            if self._last_start_display_at != self.start_display_at and clear is None:
                self.clear()
            else:
                pass
            self._last_start_display_at = self.start_display_at
            self._before_print_lines()
            indexer = 0 + self.start_display_at
            for line in self._my_widgets[:-1]:
                self._print_line(line, indexer)
                line.task = "PRINTLINE"
                line.update(clear=True)
                indexer += 1
            # Now do the final line
            line = self._my_widgets[-1]
            if (len(self.values) <= indexer + 1):
                # or (len(self._my_widgets)*self._contained_widget_height)<self.height:
                self._print_line(line, indexer)
                line.task = "PRINTLINE"
                line.update(clear=False)
            elif len((self._my_widgets) * self._contained_widget_height) < self.height:
                self._print_line(line, indexer)
                line.task = "PRINTLINELASTOFSCREEN"
                line.update(clear=False)
                if self.do_colors():
                    self.parent.curses_pad.addstr(self.rely + self.height - 1, self.relx, MORE_LABEL, self.parent.theme_manager.findPair(self, 'CONTROL'))
                else:
                    self.parent.curses_pad.addstr(self.rely + self.height - 1, self.relx, MORE_LABEL)
            else:
                #line.value = MORE_LABEL
                line.name = MORE_LABEL
                line.task = MORE_LABEL
                #line.highlight = False
                #line.show_bold = False
                line.clear()
                if self.do_colors():
                    self.parent.curses_pad.addstr(
                        self.rely + self.height - 1,
                        self.relx, MORE_LABEL,
                        self.parent.theme_manager.findPair(self, 'CONTROL'),
                    )
                else:
                    self.parent.curses_pad.addstr(
                        self.rely + self.height - 1,
                        self.relx,
                        MORE_LABEL,
                    )
            if self.editing or self.always_show_cursor:
                self.set_is_line_cursor(self._my_widgets[(self.cursor_line - self.start_display_at)], True)
                self._my_widgets[(self.cursor_line - self.start_display_at)].update(clear=True)
            else:
                # There is a bug somewhere that affects the first line.  This cures it.
                # Without this line, the first line inherits the color of the form when not editing. Not clear why.
                self._my_widgets[0].update()
        # EKR: remember the previous values.
        self._last_start_display_at = self.start_display_at
        self._last_cursor_line = self.cursor_line
        self._last_values = copy.copy(self.values)
        self._last_value = copy.copy(self.value)
        # Prevent the program crashing if the user has changed values and
        # the cursor is now on the bottom line.
        if (self._my_widgets[self.cursor_line - self.start_display_at].task in
            (MORE_LABEL, "PRINTLINELASTOFSCREEN")
        ):
            if self.slow_scroll:
                self.start_display_at += 1
            else:
                self.start_display_at = self.cursor_line
            self.update(clear=clear)
    #@+node:ekr.20170428084208.83: *3* MultiLine._before_print_lines
    def _before_print_lines(self):
        # Provide a function for the Tree classes to override.
        pass
    #@+node:ekr.20170428084208.84: *3* MultiLine._print_line
    def _print_line(self, line, value_indexer):

        trace = False  # LeoMLTree.update overrides this.
        if self.widgets_inherit_color and self.do_colors():
            line.color = self.color
        self._set_line_values(line, value_indexer)
        # Sets line.value
        if trace: g.trace(value_indexer, line.value.get_content())
            # line.value is a weakref to a LeoTreeData.
        self._set_line_highlighting(line, value_indexer)
    #@+node:ekr.20170504211313.1: *3* MultiLine.setters
    #@+node:ekr.20170428084208.85: *4* MultiLine._set_line_values
    def _set_line_values(self, line, value_indexer):
        try:
            _vl = self.values[value_indexer]
        except IndexError:
            self._set_line_blank(line)
            return False
        except TypeError:
            self._set_line_blank(line)
            return False
        line.value = self.display_value(_vl)
        line.hidden = False
    #@+node:ekr.20170428084208.86: *4* MultiLine._set_line_blank
    def _set_line_blank(self, line):
        line.value = None
        line.show_bold = False
        line.name = None
        line.hidden = True
    #@+node:ekr.20170428084208.87: *4* MultiLine._set_line_highlighting
    def _set_line_highlighting(self, line, value_indexer):
        if value_indexer in self._filtered_values_cache:
            self.set_is_line_important(line, True)
        else:
            self.set_is_line_important(line, False)
        if (value_indexer == self.value) and \
            (self.value is not None):
            self.set_is_line_bold(line, True)
        else:
            self.set_is_line_bold(line, False)
        self.set_is_line_cursor(line, False)
    #@+node:ekr.20170428084208.88: *4* MultiLine.set_is_line_important
    def set_is_line_important(self, line, value):
        line.important = value
    #@+node:ekr.20170428084208.89: *4* MultiLine.set_is_line_bold
    def set_is_line_bold(self, line, value):
        line.show_bold = value
    #@+node:ekr.20170428084208.90: *4* MultiLine.set_is_line_cursor
    def set_is_line_cursor(self, line, value):

        # g.trace('Multiline')
        line.highlight = value
    #@+node:ekr.20170504211232.1: *3* MultiLine.filters
    #@+node:ekr.20170428084208.91: *4* MultiLine.get_filtered_indexes
    def get_filtered_indexes(self, force_remake_cache=False):
        if not force_remake_cache:
            try:
                if self._last_filter == self._filter and self._last_values == self.values:
                    return self._filtered_values_cache
            except ReferenceError:
                # Can happen if self.values was a list of weak references
                pass
        self._last_filter = self._filter
        self._last_values = copy.copy(self.values)
        if self._filter == None or self._filter == '':
            return []
        list_of_indexes = []
        for indexer in range(len(self.values)):
            if self.filter_value(indexer):
                list_of_indexes.append(indexer)
        return list_of_indexes
    #@+node:ekr.20170428084208.92: *4* MultiLine.get_filtered_values
    def get_filtered_values(self):
        fvls = []
        for vli in self.get_filtered_indexes():
            fvls.append(self.values[vli])
        return fvls

    #@+node:ekr.20170428084208.93: *4* MultiLine._remake_filter_cache
    def _remake_filter_cache(self):
        self._filtered_values_cache = self.get_filtered_indexes(force_remake_cache=True)
    #@+node:ekr.20170428084208.94: *4* MultiLine.filter_value
    def filter_value(self, index):
        if self._filter in self.display_value(self.values[index]):
            return True
        else:
            return False
    #@+node:ekr.20170428084208.95: *4* MultiLine.jump_to_first_filtered
    def jump_to_first_filtered(self,):
        self.h_cursor_beginning(None)
        self.move_next_filtered(include_this_line=True)
    #@+node:ekr.20170428084208.96: *4* MultiLine.clear_filter
    def clear_filter(self):
        self._filter = None
        self.cursor_line = 0
        self.start_display_at = 0
    #@+node:ekr.20170428084208.97: *4* MultiLine.move_next_filtered
    def move_next_filtered(self, include_this_line=False, *args):
        if self._filter == None:
            return False
        for possible in self._filtered_values_cache:
            if (possible == self.cursor_line and include_this_line == True):
                self.update()
                break
            elif possible > self.cursor_line:
                self.cursor_line = possible
                self.update()
                break
        try:
            if self.cursor_line - self.start_display_at > len(self._my_widgets) or \
            self._my_widgets[self.cursor_line - self.start_display_at].task == MORE_LABEL:
                if self.slow_scroll:
                    self.start_display_at += 1
                else:
                    self.start_display_at = self.cursor_line
        except IndexError:
            self.cursor_line = 0
            self.start_display_at = 0
    #@+node:ekr.20170428084208.98: *4* MultiLine.move_previous_filtered
    def move_previous_filtered(self, *args):
        if self._filter == None:
            return False
        # nextline = self.cursor_line
        _filtered_values_cache_reversed = copy.copy(self._filtered_values_cache)
        _filtered_values_cache_reversed.reverse()
        for possible in _filtered_values_cache_reversed:
            if possible < self.cursor_line:
                self.cursor_line = possible
                return True
    #@+node:ekr.20170428084208.99: *3* MultiLine.get_selected_objects
    def get_selected_objects(self):
        if self.value == None:
            return None
        else:
            return [self.values[x] for x in self.value]
    #@+node:ekr.20170504210158.1: *3* MultiLine.Handlers
    #@+node:ekr.20170428084208.100: *4* MultiLine.handle_mouse_event
    def handle_mouse_event(self, mouse_event):
        # unfinished
        #mouse_id, x, y, z, bstate = mouse_event
        #self.cursor_line = y - self.rely - self.parent.show_aty + self.start_display_at
        mouse_id, rel_x, rel_y, z, bstate = self.interpret_mouse_event(mouse_event)
        self.cursor_line = rel_y // self._contained_widget_height + self.start_display_at
        ##if self.cursor_line > len(self.values):
        ##    self.cursor_line = len(self.values)
        self.display()
    #@+node:ekr.20170428084208.101: *4* MultiLine.set_up_handlers
    def set_up_handlers(self):
        '''MultiLine.set_up_handlers.'''
        super(MultiLine, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_UP: self.h_cursor_line_up,
            ord('k'): self.h_cursor_line_up,
            curses.KEY_LEFT: self.h_cursor_line_up,
            curses.KEY_DOWN: self.h_cursor_line_down,
            ord('j'): self.h_cursor_line_down,
            curses.KEY_RIGHT: self.h_cursor_line_down,
            curses.KEY_NPAGE: self.h_cursor_page_down,
            curses.KEY_PPAGE: self.h_cursor_page_up,
            curses.ascii.TAB: self.h_exit_down,
            curses.ascii.NL: self.h_select_exit,
            curses.KEY_HOME: self.h_cursor_beginning,
            curses.KEY_END: self.h_cursor_end,
            ord('g'): self.h_cursor_beginning,
            ord('G'): self.h_cursor_end,
            ord('x'): self.h_select,
            # "^L":        self.h_set_filtered_to_selected,
            curses.ascii.SP: self.h_select,
            curses.ascii.ESC: self.h_exit_escape,
            curses.ascii.CR: self.h_select_exit,
        })
        if self.allow_filtering:
            self.handlers.update({
                ord('l'): self.h_set_filter,
                ord('L'): self.h_clear_filter,
                ord('n'): self.move_next_filtered,
                ord('N'): self.move_previous_filtered,
                ord('p'): self.move_previous_filtered,
                # "^L":        self.h_set_filtered_to_selected,
            })
        if self.exit_left:
            self.handlers.update({
                curses.KEY_LEFT: self.h_exit_left
            })
        if self.exit_right:
            self.handlers.update({
                curses.KEY_RIGHT: self.h_exit_right
            })
        self.complex_handlers = [
            # (self.t_input_isprint, self.h_find_char)
        ]
    #@+node:ekr.20170428084208.102: *4* MultiLine.h_find_char
    def h_find_char(self, input):
        # The following ought to work, but there is a curses keyname bug
        # searchingfor = curses.keyname(input).upper()
        # do this instead:
        searchingfor = chr(input).upper()
        for counter in range(len(self.values)):
            try:
                if self.values[counter].find(searchingfor) != -1:
                    self.cursor_line = counter
                    break
            except AttributeError:
                break
    #@+node:ekr.20170428084208.103: *4* MultiLine.t_input_isprint
    def t_input_isprint(self, input):
        if curses.ascii.isprint(input): return True
        else: return False
    #@+node:ekr.20170428084208.104: *4* MultiLine.h_set_filter
    def h_set_filter(self, ch):
        if not self.allow_filtering:
            return None
        P = FilterPopupHelper()
        P.owner_widget = weakref.proxy(self)
        P.display()
        P.filterbox.edit()
        self._remake_filter_cache()
        self.jump_to_first_filtered()
    #@+node:ekr.20170428084208.105: *4* MultiLine.h_clear_filter
    def h_clear_filter(self, ch):
        self.clear_filter()
        self.update()

    #@+node:ekr.20170428084208.106: *4* MultiLine.h_cursor_beginning
    def h_cursor_beginning(self, ch):

        self.cursor_line = 0
    #@+node:ekr.20170428084208.107: *4* MultiLine.h_cursor_end
    def h_cursor_end(self, ch):
        self.cursor_line = len(self.values) - 1
        if self.cursor_line < 0:
            self.cursor_line = 0
    #@+node:ekr.20170428084208.108: *4* MultiLine.h_cursor_page_down
    def h_cursor_page_down(self, ch):
        self.cursor_line += (len(self._my_widgets) - 1)  # -1 because of the -more-
        if self.cursor_line >= len(self.values) - 1:
            self.cursor_line = len(self.values) - 1
        if not (self.start_display_at + len(self._my_widgets) - 1) > len(self.values):
            self.start_display_at += (len(self._my_widgets) - 1)
            if self.start_display_at > len(self.values) - (len(self._my_widgets) - 1):
                self.start_display_at = len(self.values) - (len(self._my_widgets) - 1)

    #@+node:ekr.20170428084208.109: *4* MultiLine.h_cursor_page_up
    def h_cursor_page_up(self, ch):
        self.cursor_line -= (len(self._my_widgets) - 1)
        if self.cursor_line < 0:
            self.cursor_line = 0
        self.start_display_at -= (len(self._my_widgets) - 1)
        if self.start_display_at < 0: self.start_display_at = 0
    #@+node:ekr.20170428084208.110: *4* MultiLine.h_cursor_line_up
    def h_cursor_line_up(self, ch):
        self.cursor_line -= 1
        if self.cursor_line < 0:
            if self.scroll_exit:
                self.cursor_line = 0
                self.h_exit_up(ch)
            else:
                self.cursor_line = 0

    #@+node:ekr.20170428084208.111: *4* MultiLine.h_cursor_line_down
    def h_cursor_line_down(self, ch):
        self.cursor_line += 1
        if self.cursor_line >= len(self.values):
            if self.scroll_exit:
                self.cursor_line = len(self.values) - 1
                self.h_exit_down(ch)
                return True
            else:
                self.cursor_line -= 1
                return True
        if self._my_widgets[self.cursor_line - self.start_display_at].task == MORE_LABEL:
            if self.slow_scroll:
                self.start_display_at += 1
            else:
                self.start_display_at = self.cursor_line
    #@+node:ekr.20170428084208.112: *4* MultiLine.h_exit
    def h_exit(self, ch):

        # g.trace('MultiLine')
        self.editing = False
        self.how_exited = True

    #@+node:ekr.20170428084208.113: *4* MultiLine.h_set_filtered_to_selected
    def h_set_filtered_to_selected(self, ch):
        # This is broken on multiline
        if len(self._filtered_values_cache) < 2:
            self.value = self._filtered_values_cache
        else:
            # There is an error - trying to select too many things.
            curses.beep()
    #@+node:ekr.20170428084208.114: *4* MultiLine.h_select
    def h_select(self, ch):

        # g.trace('MultiLine')
        self.value = self.cursor_line
        if self.select_exit:
            self.editing = False
            self.how_exited = True
    #@+node:ekr.20170428084208.115: *4* MultiLine.h_select_exit
    def h_select_exit(self, ch):

        # g.trace('MultiLine')
        self.h_select(ch)
        if self.return_exit or self.select_exit:
            self.editing = False
            self.how_exited = True
    #@+node:ekr.20170428084208.116: *4* MultiLine.edit
    def edit(self):
        trace = False and not g.unitTesting
        if trace:
            g.trace('===== (MultiLine:%s)' % self.__class__.__name__)
        self.editing = True
        self.how_exited = None
        #if self.value: self.cursor_line = self.value
        self.display()
        while self.editing:
            if trace: g.trace('(MultiLine:%s) LOOP' % self.__class__.__name__)
            self.get_and_use_key_press()
            self.update(clear=None)
            ##  self.clear()
            ##  self.update(clear=False)
            self.parent.refresh()
            ##  curses.napms(10)
            ##  curses.flushinp()
        if trace: g.trace('(MultiLine:%s) DONE' % self.__class__.__name__)
    #@-others
#@+node:ekr.20170428084208.117: ** class MultiLineAction
class MultiLineAction(MultiLine):
    RAISE_ERROR_IF_EMPTY_ACTION = False
    #@+others
    #@+node:ekr.20170428084208.118: *3* MultiLineAction.__init__
    def __init__(self, *args, **keywords):
        self.allow_multi_action = False
        super(MultiLineAction, self).__init__(*args, **keywords)

    #@+node:ekr.20170428084208.119: *3* MultiLineAction.actionHighlighted
    def actionHighlighted(self, act_on_this, key_press):
        "Override this Method"
        pass

    #@+node:ekr.20170428084208.120: *3* MultiLineAction.h_act_on_highlighted
    def h_act_on_highlighted(self, ch):
        try:
            return self.actionHighlighted(self.values[self.cursor_line], ch)
        except IndexError:
            if self.RAISE_ERROR_IF_EMPTY_ACTION:
                raise
            else:
                pass

    #@+node:ekr.20170428084208.121: *3* MultiLineAction.set_up_handlers
    def set_up_handlers(self):
        '''MultiLineAction.set_up_handlers.'''
        super(MultiLineAction, self).set_up_handlers()
        self.handlers.update({
            curses.ascii.NL: self.h_act_on_highlighted,
            curses.ascii.CR: self.h_act_on_highlighted,
            ord('x'): self.h_act_on_highlighted,
            curses.ascii.SP: self.h_act_on_highlighted,
        })


    #@-others
#@+node:ekr.20170428084208.122: ** class MultiLineActionWithShortcuts
class MultiLineActionWithShortcuts(MultiLineAction):
    shortcut_attribute_name = 'shortcut'
    #@+others
    #@+node:ekr.20170428084208.123: *3* MultiLineActionWithShortcuts.set_up_handlers
    def set_up_handlers(self):
        '''MultiLineActionWithShortcuts.set_up_handlers.'''
        super(MultiLineActionWithShortcuts, self).set_up_handlers()
        self.add_complex_handlers(((self.h_find_shortcut_action, self.h_execute_shortcut_action),))


    #@+node:ekr.20170428084208.124: *3* MultiLineActionWithShortcuts.h_find_shortcut_action
    def h_find_shortcut_action(self, _input):
        _input_decoded = curses.ascii.unctrl(_input)
        for r in range(len(self.values)):
            if hasattr(self.values[r], self.shortcut_attribute_name):
                # from . import utilNotify
                if getattr(self.values[r], self.shortcut_attribute_name) == _input \
                or getattr(self.values[r], self.shortcut_attribute_name) == _input_decoded:
                    return r
        return False

    #@+node:ekr.20170428084208.125: *3* MultiLineActionWithShortcuts.h_execute_shortcut_action
    def h_execute_shortcut_action(self, _input):
        l = self.h_find_shortcut_action(_input)
        if l is False:
            return None
        self.cursor_line = l
        self.display()
        self.h_act_on_highlighted(_input)




    #@-others
#@+node:ekr.20170428084208.126: ** class Pager
class Pager(MultiLine):
    #@+others
    #@+node:ekr.20170428084208.127: *3* Pager.__init__
    def __init__(self, screen, autowrap=False, center=False, **keywords):
        super(Pager, self).__init__(screen, **keywords)
        self.autowrap = autowrap
        self.center = center
        self._values_cache_for_wrapping = []

    #@+node:ekr.20170428084208.128: *3* Pager.reset_display_cache
    def reset_display_cache(self):
        super(Pager, self).reset_display_cache()
        self._values_cache_for_wrapping = False

    #@+node:ekr.20170428084208.129: *3* Pager._wrap_message_lines
    def _wrap_message_lines(self, message_lines, line_length):
        lines = []
        for line in message_lines:
            if line.rstrip() == '':
                lines.append('')
            else:
                this_line_set = textwrap.wrap(line.rstrip(), line_length)
                if this_line_set:
                    lines.extend(this_line_set)
                else:
                    lines.append('')
        return lines

    #@+node:ekr.20170428084208.130: *3* Pager.resize
    def resize(self):
        super(Pager, self).resize()
        if self.autowrap:
            self.setValuesWrap(list(self.values))
        if self.center:
            self.centerValues()

    #@+node:ekr.20170428084208.131: *3* Pager.setValuesWrap
    def setValuesWrap(self, lines):
        if self.autowrap and (lines == self._values_cache_for_wrapping):
            return False
        try:
            lines = lines.split('\n')
        except AttributeError:
            pass
        self.values = self._wrap_message_lines(lines, self.width - 1)
        self._values_cache_for_wrapping = self.values

    #@+node:ekr.20170428084208.132: *3* Pager.centerValues
    def centerValues(self):
        self.values = [l.strip().center(self.width - 1) for l in self.values]

    #@+node:ekr.20170428084208.133: *3* Pager.update
    def update(self, clear=True):
        #we look this up a lot. Let's have it here.
        if self.autowrap:
            self.setValuesWrap(list(self.values))

        if self.center:
            self.centerValues()

        display_length = len(self._my_widgets)
        values_len = len(self.values)

        if self.start_display_at > values_len - display_length:
            self.start_display_at = values_len - display_length
        if self.start_display_at < 0: self.start_display_at = 0

        indexer = 0 + self.start_display_at
        for line in self._my_widgets[:-1]:
            self._print_line(line, indexer)
            indexer += 1

        # Now do the final line
        line = self._my_widgets[-1]

        if values_len <= indexer + 1:
            self._print_line(line, indexer)
        else:
            line.value = MORE_LABEL
            line.highlight = False
            line.show_bold = False

        for w in self._my_widgets:
            # call update to avoid needless refreshes
            w.update(clear=True)
        # There is a bug somewhere that affects the first line.  This cures it.
        # Without this line, the first line inherits the color of the form when not editing. Not clear why.
        self._my_widgets[0].update()



    #@+node:ekr.20170428084208.134: *3* Pager.edit
    def edit(self):
        # Make sure a value never gets set.
        value = self.value
        super(Pager, self).edit()
        self.value = value

    #@+node:ekr.20170428084208.135: *3* Pager.h_scroll_line_up
    def h_scroll_line_up(self, input):
        self.start_display_at -= 1
        if self.scroll_exit and self.start_display_at < 0:
            self.editing = False
            self.how_exited = widget.EXITED_UP

    #@+node:ekr.20170428084208.136: *3* Pager.h_scroll_line_down
    def h_scroll_line_down(self, input):
        self.start_display_at += 1
        if self.scroll_exit and self.start_display_at >= len(self.values) - self.start_display_at + 1:
            self.editing = False
            self.how_exited = widget.EXITED_DOWN

    #@+node:ekr.20170428084208.137: *3* Pager.h_scroll_page_down
    def h_scroll_page_down(self, input):
        self.start_display_at += len(self._my_widgets)

    #@+node:ekr.20170428084208.138: *3* Pager.h_scroll_page_up
    def h_scroll_page_up(self, input):
        self.start_display_at -= len(self._my_widgets)

    #@+node:ekr.20170428084208.139: *3* Pager.h_show_beginning
    def h_show_beginning(self, input):
        self.start_display_at = 0

    #@+node:ekr.20170428084208.140: *3* Pager.h_show_end
    def h_show_end(self, input):
        self.start_display_at = len(self.values) - len(self._my_widgets)

    #@+node:ekr.20170428084208.141: *3* Pager.h_select_exit
    def h_select_exit(self, _input):
        self.exit(self, _input)

    #@+node:ekr.20170428084208.142: *3* Pager.set_up_handlers
    def set_up_handlers(self):
        '''Pager.set_up_handlers.'''
        super(Pager, self).set_up_handlers()
        self.handlers = {
            curses.KEY_UP: self.h_scroll_line_up,
            curses.KEY_LEFT: self.h_scroll_line_up,
            curses.KEY_DOWN: self.h_scroll_line_down,
            curses.KEY_RIGHT: self.h_scroll_line_down,
            curses.KEY_NPAGE: self.h_scroll_page_down,
            curses.KEY_PPAGE: self.h_scroll_page_up,
            curses.KEY_HOME: self.h_show_beginning,
            curses.KEY_END: self.h_show_end,
            curses.ascii.NL: self.h_exit,
            curses.ascii.CR: self.h_exit,
            curses.ascii.SP: self.h_scroll_page_down,
            curses.ascii.TAB: self.h_exit,
            ord('j'): self.h_scroll_line_down,
            ord('k'): self.h_scroll_line_up,
            ord('x'): self.h_exit,
            ord('q'): self.h_exit,
            ord('g'): self.h_show_beginning,
            ord('G'): self.h_show_end,
            curses.ascii.ESC: self.h_exit_escape,
        }
        self.complex_handlers = []

    #@-others
#@+node:ekr.20170428084208.143: ** class TitleMultiLine
class TitleMultiLine(titlefield.TitleText):
    _entry_type = MultiLine

    #@+others
    #@+node:ekr.20170428084208.144: *3* get_selected_objects
    def get_selected_objects(self):
        return self.entry_widget.get_selected_objects()

    #@+node:ekr.20170428084208.145: *3* get_values
    def get_values(self):
        if hasattr(self, 'entry_widget'):
            return self.entry_widget.values
        elif hasattr(self, '__tmp_value'):
            return self.__tmp_values
        else:
            return None
    #@+node:ekr.20170428084208.146: *3* set_values
    def set_values(self, value):
        if hasattr(self, 'entry_widget'):
            self.entry_widget.values = value
        elif hasattr(self, '__tmp_value'):
            # probably trying to set the value before the textarea is initialized
            self.__tmp_values = value
    #@+node:ekr.20170428084208.147: *3* del_values
    def del_values(self):
        del self.entry_widget.value
    values = property(get_values, set_values, del_values)


    #@-others
#@+node:ekr.20170428084208.148: ** class TitlePager
class TitlePager(TitleMultiLine):
    _entry_type = Pager

#@+node:ekr.20170428084208.149: ** class BufferPager
class BufferPager(Pager):
    DEFAULT_MAXLEN = None

    #@+others
    #@+node:ekr.20170428084208.150: *3* BufferPager.__init__
    def __init__(self, screen, maxlen=False, *args, **keywords):
        super(BufferPager, self).__init__(screen, *args, **keywords)
        if maxlen is False:
            maxlen = self.DEFAULT_MAXLEN
        self.values = collections.deque(maxlen=maxlen)

    #@+node:ekr.20170428084208.151: *3* BufferPager.clearBuffer
    def clearBuffer(self):
        self.values.clear()

    #@+node:ekr.20170428084208.152: *3* BufferPager.setValuesWrap
    def setValuesWrap(self, lines):
        if self.autowrap and (lines == self._values_cache_for_wrapping):
            return False
        try:
            lines = lines.split('\n')
        except AttributeError:
            pass

        self.clearBuffer()
        self.buffer(self._wrap_message_lines(lines, self.width - 1))
        self._values_cache_for_wrapping = copy.deepcopy(self.values)

    #@+node:ekr.20170428084208.153: *3* BufferPager.buffer
    def buffer(self, lines, scroll_end=True, scroll_if_editing=False):
        "Add data to be displayed in the buffer."
        self.values.extend(lines)
        if scroll_end:
            if not self.editing:
                self.start_display_at = len(self.values) - len(self._my_widgets)
            elif scroll_if_editing:
                self.start_display_at = len(self.values) - len(self._my_widgets)

    #@-others
#@+node:ekr.20170428084208.154: ** class TitleBufferPager
class TitleBufferPager(TitleMultiLine):
    _entry_type = BufferPager

    #@+others
    #@+node:ekr.20170428084208.155: *3* clearBuffer
    def clearBuffer(self):
        return self.entry_widget.clearBuffer()

    #@+node:ekr.20170428084208.156: *3* buffer
    def buffer(self, *args, **values):
        return self.entry_widget.buffer(*args, **values)





    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
