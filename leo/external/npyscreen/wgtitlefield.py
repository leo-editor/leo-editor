#@+leo-ver=5-thin
#@+node:ekr.20170428084208.381: * @file ../external/npyscreen/wgtitlefield.py
#!/usr/bin/python
from leo.core import leoGlobals as g
assert g
#@+others
#@+node:ekr.20170428084208.382: ** Declarations
# import curses
import weakref
from . import wgtextbox as textbox
from . import wgwidget as widget

#@+node:ekr.20170428084208.383: ** class TitleText
class TitleText(widget.Widget):
    _entry_type = textbox.Textfield

    #@+others
    #@+node:ekr.20170428084208.384: *3* TitleText.__init__
    def __init__(self, screen,
        begin_entry_at=16,
        field_width=None,
        value=None,
        use_two_lines=None,
        hidden=False,
        labelColor='LABEL',
        allow_override_begin_entry_at=True,
        **keywords):

        self.text_field_begin_at = begin_entry_at
        self.field_width_request = field_width
        self.labelColor = labelColor
        self.allow_override_begin_entry_at = allow_override_begin_entry_at
        super(TitleText, self).__init__(screen, **keywords)

        if self.name is None: self.name = 'NoName'

        if use_two_lines is None:
            if len(self.name) + 2 >= begin_entry_at:
                self.use_two_lines = True
            else:
                self.use_two_lines = False
        else:
            self.use_two_lines = use_two_lines

        self._passon = keywords.copy()
        for dangerous in ('relx', 'rely', 'value',):  # 'width','max_width'):
            try:
                self._passon.pop(dangerous)
            except Exception:
                pass

        if self.field_width_request:
            self._passon['width'] = self.field_width_request
        else:
            if 'max_width' in self._passon.keys():
                if self._passon['max_width'] > 0:
                    if self._passon['max_width'] < self.text_field_begin_at:
                        raise ValueError("The maximum width specified is less than the text_field_begin_at value.")
                    else:
                        self._passon['max_width'] -= self.text_field_begin_at + 1

        if 'width' in self._passon:
            #if 0 < self._passon['width'] < self.text_field_begin_at:
            #    raise ValueError("The maximum width specified %s is less than the text_field_begin_at value %s." % (self._passon['width'], self.text_field_begin_at))
            if self._passon['width'] > 0:
                self._passon['width'] -= self.text_field_begin_at + 1

        if self.use_two_lines:
            if 'max_height' in self._passon and self._passon['max_height']:
                if self._passon['max_height'] == 1:
                    raise ValueError("I don't know how to resolve this: max_height == 1 but widget using 2 lines.")
                self._passon['max_height'] -= 1
            if 'height' in self._passon and self._passon['height']:
                raise ValueError("I don't know how to resolve this: height == 1 but widget using 2 lines.")
                self._passon['height'] -= 1


        self.make_contained_widgets()
        self.set_value(value)
        self.hidden = hidden



    #@+node:ekr.20170428084208.385: *3* TitleText.resize
    def resize(self):
        super(TitleText, self).resize()
        self.label_widget.relx = self.relx
        self.label_widget.rely = self.rely
        self.entry_widget.relx = self.relx + self.text_field_begin_at
        self.entry_widget.rely = self.rely + self._contained_rely_offset
        self.label_widget._resize()
        self.entry_widget._resize()
        self.recalculate_size()

    #@+node:ekr.20170428084208.386: *3* TitleText.make_contained_widgets
    def make_contained_widgets(self):
        self.label_widget = textbox.Textfield(self.parent, relx=self.relx, rely=self.rely, width=len(self.name) + 1, value=self.name, color=self.labelColor)
        if self.label_widget.on_last_line and self.use_two_lines:
            # we're in trouble here.
            if len(self.name) > 12:
                ab_label = 12
            else:
                ab_label = len(self.name)
            self.use_two_lines = False
            self.label_widget = textbox.Textfield(self.parent, relx=self.relx, rely=self.rely, width=ab_label + 1, value=self.name)
            if self.allow_override_begin_entry_at:
                self.text_field_begin_at = ab_label + 1
        if self.use_two_lines:
            self._contained_rely_offset = 1
        else:
            self._contained_rely_offset = 0

        self.entry_widget = self.__class__._entry_type(self.parent,
                                relx=(self.relx + self.text_field_begin_at),
                                rely=(self.rely + self._contained_rely_offset), value=self.value,
                                ** self._passon)
        self.entry_widget.parent_widget = weakref.proxy(self)
        self.recalculate_size()


    #@+node:ekr.20170428084208.387: *3* TitleText.recalculate_size
    def recalculate_size(self):
        self.height = self.entry_widget.height
        if self.use_two_lines: self.height += 1
        else: pass
        self.width = self.entry_widget.width + self.text_field_begin_at

    #@+node:ekr.20170428084208.388: *3* TitleText.edit
    def edit(self):

        # g.trace('===== (TitleText)')
        self.editing = True
        self.display()
        self.entry_widget.edit()
        #self.value = self.textarea.value
        self.how_exited = self.entry_widget.how_exited
        self.editing = False
        self.display()

    #@+node:ekr.20170428084208.389: *3* TitleText.update
    def update(self, clear=True):
        if clear: self.clear()
        if self.hidden: return False
        if self.editing:
            self.label_widget.show_bold = True
            self.label_widget.color = 'LABELBOLD'
        else:
            self.label_widget.show_bold = False
            self.label_widget.color = self.labelColor
        self.label_widget.update()
        self.entry_widget.update()

    #@+node:ekr.20170428084208.390: *3* TitleText.handle_mouse_event
    def handle_mouse_event(self, mouse_event):
        if self.entry_widget.intersted_in_mouse_event(mouse_event):
            self.entry_widget.handle_mouse_event(mouse_event)

    #@+node:ekr.20170428084208.391: *3* TitleText.get_value
    def get_value(self):
        if hasattr(self, 'entry_widget'):
            return self.entry_widget.value
        elif hasattr(self, '__tmp_value'):
            return self.__tmp_value
        else:
            return None
    #@+node:ekr.20170428084208.392: *3* TitleText.set_value
    def set_value(self, value):
        if hasattr(self, 'entry_widget'):
            self.entry_widget.value = value
        else:
            # probably trying to set the value before the textarea is initialized
            self.__tmp_value = value
    #@+node:ekr.20170428084208.393: *3* TitleText.del_value
    def del_value(self):
        del self.entry_widget.value
    value = property(get_value, set_value, del_value)

    #@+node:ekr.20170428084208.394: *3* TitleText.editable
    @property
    def editable(self):
        try:
            return self.entry_widget.editable
        except AttributeError:
            return self._editable

    #@+node:ekr.20170428084208.395: *3* TitleText.editable
    @editable.setter
    def editable(self, value):
        self._editable = value
        try:
            self.entry_widget.editable = value
        except AttributeError:
            self._editable = value

    #@+node:ekr.20170428084208.396: *3* TitleText.add_handlers
    def add_handlers(self, handler_dictionary):
        """
        Pass handlers to entry_widget
        """
        self.entry_widget.add_handlers(handler_dictionary)

    #@-others
#@+node:ekr.20170428084208.397: ** class TitleFixedText
class TitleFixedText(TitleText):
    _entry_type = textbox.FixedText
#@-others
#@@language python
#@@tabwidth -4
#@-leo
