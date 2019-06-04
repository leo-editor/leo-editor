#@+leo-ver=5-thin
#@+node:ekr.20170428084207.50: * @file ../external/npyscreen/apOptions.py
#@+others
#@+node:ekr.20170428084207.51: ** Declarations
import weakref
# import textwrap
import datetime

from . import fmForm
from . import fmPopup
from . import wgtitlefield
from . import wgannotatetextbox
from . import wgmultiline
from . import wgselectone
from . import wgmultiselect
from . import wgeditmultiline
from . import wgcheckbox
from . import wgfilenamecombo
from . import wgdatecombo

#@+node:ekr.20170428084207.52: ** class SimpleOptionForm
class SimpleOptionForm(fmForm.Form):
    #@+others
    #@+node:ekr.20170428084207.53: *3* create
    def create(self,):
        self.wOptionList = self.add(OptionListDisplay, )

    #@+node:ekr.20170428084207.54: *3* beforeEditing
    def beforeEditing(self, ):
        try:
            self.wOptionList.values = self.value.options
        except AttributeError:
            pass

    #@+node:ekr.20170428084207.55: *3* afterEditing
    def afterEditing(self):
        if self.value.filename:
            self.value.write_to_file()
        self.parentApp.switchFormPrevious()

    #@-others
#@+node:ekr.20170428084207.56: ** class OptionListDisplayLine
class OptionListDisplayLine(wgannotatetextbox.AnnotateTextboxBase):
    ANNOTATE_WIDTH = 25
    #@+others
    #@+node:ekr.20170428084207.57: *3* getAnnotationAndColor
    def getAnnotationAndColor(self):
        return (self.value.get_name_user(), 'LABEL')

    #@+node:ekr.20170428084207.58: *3* display_value
    def display_value(self, vl):
        return vl.get_for_single_line_display()

    #@-others
#@+node:ekr.20170428084207.59: ** class OptionListDisplay
class OptionListDisplay(wgmultiline.MultiLineAction):
    _contained_widgets = OptionListDisplayLine
    #@+others
    #@+node:ekr.20170428084207.60: *3* actionHighlighted
    def actionHighlighted(self, act_on_this, key_press):
        rtn = act_on_this.change_option()
        self.display()
        return rtn

    #@+node:ekr.20170428084207.61: *3* display_value
    def display_value(self, vl):
        return vl

    #@-others
#@+node:ekr.20170428084207.62: ** class OptionChanger
class OptionChanger(fmPopup.ActionPopupWide):
    #@+others
    #@+node:ekr.20170428084207.63: *3* on_ok
    def on_ok(self,):
        self.OPTION_TO_CHANGE.set_from_widget_value(self.OPTION_WIDGET.value)

    #@-others
#@+node:ekr.20170428084207.64: ** class OptionList
class OptionList:
    #@+others
    #@+node:ekr.20170428084207.65: *3* __init__
    def __init__(self, filename=None):
        self.options  = []
        self.filename = filename
        self.define_serialize_functions()

    #@+node:ekr.20170428084207.66: *3* define_serialize_functions
    def define_serialize_functions(self):
        self.SERIALIZE_FUNCTIONS = {
            OptionFreeText:         self.save_text,
            OptionSingleChoice:     self.save_text,
            OptionMultiChoice:      self.save_multi_text,
            OptionMultiFreeText:    self.save_text,
            OptionBoolean:          self.save_bool,
            OptionFilename:         self.save_text,
            OptionDate:             self.save_date,
            OptionMultiFreeList:    self.save_list,
        }

        self.UNSERIALIZE_FUNCTIONS = {
            OptionFreeText:         self.reload_text,
            OptionSingleChoice:     self.reload_text,
            OptionMultiChoice:      self.load_multi_text,
            OptionMultiFreeText:    self.reload_text,
            OptionBoolean:          self.load_bool,
            OptionFilename:         self.reload_text,
            OptionDate:             self.load_date,
            OptionMultiFreeList:    self.load_list,
        }

    #@+node:ekr.20170428084207.67: *3* get
    def get(self, name):
        for o in self.options:
            if o.get_real_name() == name:
                return o



    #@+node:ekr.20170428084207.68: *3* write_to_file
    def write_to_file(self, fn=None, exclude_defaults=True):
        fn = fn or self.filename
        if not fn:
            raise ValueError("Must specify a filename.")
        with open(fn, 'w', encoding="utf-8") as f:
            for opt in self.options:
                if opt.default != opt.get():
                    f.write('%s=%s\n' % (opt.get_real_name(), self.serialize_option_value(opt)))

    #@+node:ekr.20170428084207.69: *3* reload_from_file
    def reload_from_file(self, fn=None):
        fn = fn or self.filename
        with open(fn, 'r', encoding="utf-8") as f:
            for line in f.readlines():
                 line = line.strip()
                 name, value = line.split("=", maxsplit=1)
                 for option in self.options:
                     if option.get_real_name() == name:
                         option.set(self.deserialize_option_value(option, value.encode('ascii')))

    #@+node:ekr.20170428084207.70: *3* serialize_option_value
    def serialize_option_value(self, option):
        return self.SERIALIZE_FUNCTIONS[option.__class__](option)

    #@+node:ekr.20170428084207.71: *3* deserialize_option_value
    def deserialize_option_value(self, option, serialized):
        return self.UNSERIALIZE_FUNCTIONS[option.__class__](serialized)

    #@+node:ekr.20170428084207.72: *3* _encode_text_for_saving
    def _encode_text_for_saving(self, txt):
        return txt.encode('unicode-escape').decode('ascii')

    #@+node:ekr.20170428084207.73: *3* _decode_text_from_saved
    def _decode_text_from_saved(self, txt):
        return txt.decode('unicode-escape')

    #@+node:ekr.20170428084207.74: *3* save_text
    def save_text(self, option):
        s = option.get()
        if not s:
            s = ''
        return self._encode_text_for_saving(s)

    #@+node:ekr.20170428084207.75: *3* reload_text
    def reload_text(self, txt):
        return self._decode_text_from_saved(txt)

    #@+node:ekr.20170428084207.76: *3* save_bool
    def save_bool(self, option):
        if option.get():
            return 'True'
        else:
            return 'False'

    #@+node:ekr.20170428084207.77: *3* load_bool
    def load_bool(self, txt):
        txt = txt.decode()
        if txt in ('True', ):
            return True
        elif txt in ('False', ):
            return False
        else:
            raise ValueError("Could not decode %s" % txt)

    #@+node:ekr.20170428084207.78: *3* save_multi_text
    def save_multi_text(self, option):
        line = []
        opt = option.get()
        if not opt:
            return ''
        for text_part in opt:
            line.append(text_part.encode('unicode-escape').decode('ascii'))
        return "\t".join(line)

    #@+node:ekr.20170428084207.79: *3* load_multi_text
    def load_multi_text(self, text):
        parts = text.decode('ascii').split("\t")
        rtn = []
        for p in parts:
            rtn.append(p.encode('ascii').decode('unicode-escape'))
        return rtn

    #@+node:ekr.20170428084207.80: *3* save_list
    def save_list(self, lst):
        pts_to_save = []
        for p in lst.get():
            pts_to_save.append(self._encode_text_for_saving(p))
        return "\t".join(pts_to_save)

    #@+node:ekr.20170428084207.81: *3* load_list
    def load_list(self, text):
        parts = text.decode('ascii').split("\t")
        parts_to_return = []
        for p in parts:
            parts_to_return.append(self._decode_text_from_saved(p.encode('ascii')))
        return parts_to_return

    #@+node:ekr.20170428084207.82: *3* save_date
    def save_date(self, option):
        if option.get():
            return option.get().ctime()
        else:
            return None

    #@+node:ekr.20170428084207.83: *3* load_date
    def load_date(self, txt):
        if txt:
            return datetime.datetime.strptime(txt.decode(), "%a %b %d %H:%M:%S %Y")
        else:
            return None



    #@-others
#@+node:ekr.20170428084207.84: ** class Option
class Option:
    DEFAULT = ''
    #@+others
    #@+node:ekr.20170428084207.85: *3* __init__
    def __init__(self, name,
                    value=None,
                    documentation=None,
                    short_explanation=None,
                    option_widget_keywords = None,
                    default = None,
                    ):
        self.name = name
        self.default = default or self.DEFAULT
        self.set(value or self.default)
        self.documentation = documentation
        self.short_explanation = short_explanation
        self.option_widget_keywords = option_widget_keywords or {}
        self.default = default or self.DEFAULT

    #@+node:ekr.20170428084207.86: *3* when_set
    def when_set(self):
        pass

    #@+node:ekr.20170428084207.87: *3* get
    def get(self,):
        return self.value

    #@+node:ekr.20170428084207.88: *3* get_for_single_line_display
    def get_for_single_line_display(self):
        return repr(self.value)

    #@+node:ekr.20170428084207.89: *3* set_from_widget_value
    def set_from_widget_value(self, vl):
        self.set(vl)

    #@+node:ekr.20170428084207.90: *3* set
    def set(self, value):
        self.value = value
        self.when_set()

    #@+node:ekr.20170428084207.91: *3* get_real_name
    def get_real_name(self):
        # This might be for internal use
        return self.name

    #@+node:ekr.20170428084207.92: *3* get_name_user
    def get_name_user(self):
        # You could do translation here.
        return self.name

    #@+node:ekr.20170428084207.93: *3* _set_up_widget_values
    def _set_up_widget_values(self, option_form, main_option_widget):
        main_option_widget.value = self.value

    #@+node:ekr.20170428084207.94: *3* change_option
    def change_option(self):
        option_changing_form = OptionChanger()
        option_changing_form.OPTION_TO_CHANGE = weakref.proxy(self)
        if self.documentation:
            explanation_widget = option_changing_form.add(wgmultiline.Pager,
                                                        editable=False, value=None,
                                                        max_height=(option_changing_form.lines - 3) // 2,
                                                        autowrap=True,
                                                        )
            option_changing_form.nextrely += 1
            explanation_widget.values = self.documentation


        option_widget = option_changing_form.add(self.WIDGET_TO_USE,
                                                    name=self.get_name_user(),
                                                    **self.option_widget_keywords
                                                )
        option_changing_form.OPTION_WIDGET = option_widget
        self._set_up_widget_values(option_changing_form, option_widget)
        option_changing_form.edit()


    #@-others
#@+node:ekr.20170428084207.95: ** class OptionLimitedChoices
class OptionLimitedChoices(Option):
    #@+others
    #@+node:ekr.20170428084207.96: *3* __init__
    def __init__(self, name, choices=None, *args, **keywords):
        super(OptionLimitedChoices, self).__init__(name, *args, **keywords)
        choices = choices or []
        self.setChoices(choices)

    #@+node:ekr.20170428084207.97: *3* setChoices
    def setChoices(self, choices):
        self.choices = choices

    #@+node:ekr.20170428084207.98: *3* getChoices
    def getChoices(self,):
        return self.choices

    #@+node:ekr.20170428084207.99: *3* _set_up_widget_values
    def _set_up_widget_values(self, option_form, main_option_widget):
        main_option_widget.value  = []
        main_option_widget.values = self.getChoices()
        for x in range(len(main_option_widget.values)):
            if self.value and main_option_widget.values[x] in self.value:
                main_option_widget.value.append(x)

    #@+node:ekr.20170428084207.100: *3* set_from_widget_value
    def set_from_widget_value(self, vl):
        value = []
        for v in vl:
            value.append(self.choices[v])
        self.set(value)

    #@-others
#@+node:ekr.20170428084207.101: ** class OptionFreeText
class OptionFreeText(Option):
    WIDGET_TO_USE = wgtitlefield.TitleText

#@+node:ekr.20170428084207.102: ** class OptionSingleChoice
class OptionSingleChoice(OptionLimitedChoices):
    WIDGET_TO_USE = wgselectone.TitleSelectOne

#@+node:ekr.20170428084207.103: ** class OptionMultiChoice
class OptionMultiChoice(OptionLimitedChoices):
    DEFAULT = []
    WIDGET_TO_USE = wgmultiselect.TitleMultiSelect

#@+node:ekr.20170428084207.104: ** class OptionMultiFreeText
class OptionMultiFreeText(Option):
    WIDGET_TO_USE = wgeditmultiline.MultiLineEdit

#@+node:ekr.20170428084207.105: ** class OptionMultiFreeList
class OptionMultiFreeList(Option):
    WIDGET_TO_USE = wgeditmultiline.MultiLineEdit
    DEFAULT = []
    #@+others
    #@+node:ekr.20170428084207.106: *3* _set_up_widget_values
    def _set_up_widget_values(self, option_form, main_option_widget):
        main_option_widget.value = "\n".join(self.get())

    #@+node:ekr.20170428084207.107: *3* set_from_widget_value
    def set_from_widget_value(self, vl):
        self.set(vl.split("\n"))

    #@-others
#@+node:ekr.20170428084207.108: ** class OptionBoolean
class OptionBoolean(Option):
    WIDGET_TO_USE = wgcheckbox.Checkbox

#@+node:ekr.20170428084207.109: ** class OptionFilename
class OptionFilename(Option):
    DEFAULT = ''
    WIDGET_TO_USE = wgfilenamecombo.FilenameCombo

#@+node:ekr.20170428084207.110: ** class OptionDate
class OptionDate(Option):
    DEFAULT = None
    WIDGET_TO_USE = wgdatecombo.DateCombo
#@-others
#@@language python
#@@tabwidth -4
#@-leo
