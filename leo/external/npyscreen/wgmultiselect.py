#@+leo-ver=5-thin
#@+node:ekr.20170428084208.225: * @file ../external/npyscreen/wgmultiselect.py
#!/usr/bin/python
#@+others
#@+node:ekr.20170428084208.226: ** Declarations
from . import wgmultiline    as multiline
from . import wgselectone    as selectone
from . import wgcheckbox     as checkbox
import curses

#@+node:ekr.20170428084208.227: ** class MultiSelect
class MultiSelect(selectone.SelectOne):
    _contained_widgets = checkbox.Checkbox

    #@+others
    #@+node:ekr.20170428084208.228: *3* MultiSelect.set_up_handlers
    def set_up_handlers(self):
        '''MultiSelect.set_up_handlers.'''
        super(MultiSelect, self).set_up_handlers()
        self.handlers.update({
            ord("x"):           self.h_select_toggle,
            curses.ascii.SP:    self.h_select_toggle,
            ord("X"):           self.h_select,
            "^U":               self.h_select_none,
        })

    #@+node:ekr.20170428084208.229: *3* MultiSelect.h_select_none
    def h_select_none(self, input):
        self.value = []

    #@+node:ekr.20170428084208.230: *3* MultiSelect.h_select_toggle
    def h_select_toggle(self, input):
        if self.cursor_line in self.value:
            self.value.remove(self.cursor_line)
        else:
            self.value.append(self.cursor_line)

    #@+node:ekr.20170428084208.231: *3* MultiSelect.h_set_filtered_to_selected
    def h_set_filtered_to_selected(self, ch):
        self.value = self._filtered_values_cache

    #@+node:ekr.20170428084208.232: *3* MultiSelect.h_select_exit
    def h_select_exit(self, ch):
        if not self.cursor_line in self.value:
            self.value.append(self.cursor_line)
        if self.return_exit:
            self.editing = False
            self.how_exited=True

    #@+node:ekr.20170428084208.233: *3* MultiSelect.get_selected_objects
    def get_selected_objects(self):
        if self.value == [] or self.value == None:
            return None
        else:
            return [self.values[x] for x in self.value]

    #@-others
#@+node:ekr.20170428084208.234: ** class MultiSelectAction
class MultiSelectAction(MultiSelect):
    always_act_on_many = False
    #@+others
    #@+node:ekr.20170428084208.235: *3* MultiSelectAction.actionHighlighted
    def actionHighlighted(self, act_on_this, key_press):
        "Override this Method"
        pass

    #@+node:ekr.20170428084208.236: *3* MultiSelectAction.actionSelected
    def actionSelected(self, act_on_these, keypress):
        "Override this Method"
        pass

    #@+node:ekr.20170428084208.237: *3* MultiSelectAction.set_up_handlers
    def set_up_handlers(self):
        '''MultiSelectAction.set_up_handlers.'''
        super(MultiSelectAction, self).set_up_handlers()
        self.handlers.update ( {
            curses.ascii.NL:    self.h_act_on_highlighted,
            curses.ascii.CR:    self.h_act_on_highlighted,
            ord(';'):           self.h_act_on_selected,
            # "^L":             self.h_set_filtered_to_selected,
            curses.ascii.SP:    self.h_act_on_highlighted,
        })

    #@+node:ekr.20170428084208.238: *3* MultiSelectAction.h_act_on_highlighted
    def h_act_on_highlighted(self, ch):
        if self.always_act_on_many:
            return self.h_act_on_selected(ch)
        else:
            return self.actionHighlighted(self.values[self.cursor_line], ch)

    #@+node:ekr.20170428084208.239: *3* MultiSelectAction.h_act_on_selected
    def h_act_on_selected(self, ch):
        if self.vale:
            return self.actionSelected(self.get_selected_objects(), ch)


    #@-others
#@+node:ekr.20170428084208.240: ** class MultiSelectFixed
class MultiSelectFixed(MultiSelect):
    # This does not allow the user to change Values, but does allow the user to move around.
    # Useful for displaying Data.
    #@+others
    #@+node:ekr.20170428084208.241: *3* user_set_value
    def user_set_value(self, input):
        pass

    #@+node:ekr.20170428084208.242: *3* set_up_handlers
    def set_up_handlers(self):
        '''MultiSelectFixed.set_up_handlers.'''
        super(MultiSelectFixed, self).set_up_handlers()
        self.handlers.update({
            ord("x"):           self.user_set_value,
            ord("X"):           self.user_set_value,
            curses.ascii.SP:    self.user_set_value,
            "^U":               self.user_set_value,
            curses.ascii.NL:    self.h_exit_down,
            curses.ascii.CR:    self.h_exit_down,
        })
    #@-others
#@+node:ekr.20170428084208.243: ** class TitleMultiSelect
class TitleMultiSelect(multiline.TitleMultiLine):
    _entry_type = MultiSelect



#@+node:ekr.20170428084208.244: ** class TitleMultiSelectFixed
class TitleMultiSelectFixed(multiline.TitleMultiLine):
    _entry_type = MultiSelectFixed


#@-others
#@@language python
#@@tabwidth -4
#@-leo
