#@+leo-ver=5-thin
#@+node:ekr.20170428084208.297: * @file ../external/npyscreen/wgslider.py
#!/usr/bin/python
#@+others
#@+node:ekr.20170428084208.298: ** Declarations
import curses
from . import wgwidget as widget
from . import wgtitlefield as titlefield

#@+node:ekr.20170428084208.299: ** class Slider
class Slider(widget.Widget):
    DEFAULT_BLOCK_COLOR = None
    #@+others
    #@+node:ekr.20170428084208.300: *3* Slider.__init__
    def __init__(self, screen, value=0,
                out_of=100, step=1, lowest=0,
                label=True,
                block_color=None,
                **keywords):
        self.out_of = out_of
        self.value = value
        self.step = step
        self.lowest = lowest
        self.block_color = block_color or self.__class__.DEFAULT_BLOCK_COLOR
        super(Slider, self).__init__(screen, **keywords)
        if self.parent.curses_pad.getmaxyx()[0] - 1 == self.rely: self.on_last_line = True
        else: self.on_last_line = False
        if self.on_last_line:
            self.maximum_string_length = self.width - 1
        else:
            self.maximum_string_length = self.width
        self.label = label

    #@+node:ekr.20170428084208.301: *3* Slider.calculate_area_needed
    def calculate_area_needed(self):
        return 1, 0

    #@+node:ekr.20170428084208.302: *3* Slider.translate_value
    def translate_value(self):
        """What do different values mean?  If you subclass this object, and override this
        method, you can change how the labels are displayed.  This method should return a
        unicode string, to be displayed to the user. You probably want to ensure this is a fixed width."""

        stri = "%s / %s" % (self.value, self.out_of)
        if isinstance(stri, bytes):
            stri = stri.decode(self.encoding, 'replace')
        l = (len(str(self.out_of))) * 2 + 4
        stri = stri.rjust(l)
        return stri

    #@+node:ekr.20170428084208.303: *3* Slider.update
    def update(self, clear=True):
        if clear: self.clear()
        if self.hidden:
            self.clear()
            return False
        length_of_display = self.width + 1
        blocks_on_screen = length_of_display

        if self.label:
            label_str = self.translate_value()
            if isinstance(label_str, bytes):
                label_str = label_str.decode(self.encoding, 'replace')
            blocks_on_screen -= len(label_str) + 3
            if self.do_colors():
                label_attributes = self.parent.theme_manager.findPair(self)
            else:
                label_attributes = curses.A_NORMAL
            self.add_line(
                self.rely, self.relx + blocks_on_screen + 2,
                label_str,
                self.make_attributes_list(label_str, label_attributes),
                len(label_str)
                )

            # If want to handle neg. numbers, this line would need changing.
        blocks_to_fill = (float(self.value) / float(self.out_of)) * int(blocks_on_screen)

        if self.editing:
            self.parent.curses_pad.attron(curses.A_BOLD)
            #self.parent.curses_pad.bkgdset(curses.ACS_HLINE)
            #self.parent.curses_pad.bkgdset(">")
            #self.parent.curses_pad.bkgdset(curses.A_NORMAL)
            BACKGROUND_CHAR = ">"
            BARCHAR = curses.ACS_HLINE
        else:
            self.parent.curses_pad.attroff(curses.A_BOLD)
            self.parent.curses_pad.bkgdset(curses.A_NORMAL)
            #self.parent.curses_pad.bkgdset(curses.ACS_HLINE)
            BACKGROUND_CHAR = curses.ACS_HLINE
            BARCHAR = " "


        for n in range(blocks_on_screen):
            xoffset = self.relx
            if self.do_colors():
                self.parent.curses_pad.addch(self.rely, n + xoffset, BACKGROUND_CHAR, curses.A_NORMAL | self.parent.theme_manager.findPair(self))
            else:
                self.parent.curses_pad.addch(self.rely, n + xoffset, BACKGROUND_CHAR, curses.A_NORMAL)

        for n in range(int(blocks_to_fill)):
            if self.do_colors():
                if self.block_color:
                    self.parent.curses_pad.addch(self.rely, n + xoffset, BARCHAR, self.parent.theme_manager.findPair(self, self.block_color))
                else:
                    self.parent.curses_pad.addch(self.rely, n + xoffset, BARCHAR, curses.A_STANDOUT | self.parent.theme_manager.findPair(self))
            else:
                self.parent.curses_pad.addch(self.rely, n + xoffset, BARCHAR, curses.A_STANDOUT)  #curses.ACS_BLOCK)

        self.parent.curses_pad.attroff(curses.A_BOLD)
        self.parent.curses_pad.bkgdset(curses.A_NORMAL)

    #@+node:ekr.20170428084208.304: *3* Slider.set_value
    def set_value(self, val):
        #"We can only represent ints or floats, and must be less than what we are out of..."
        if val is None: val = 0
        if not isinstance(val, int) and not isinstance(val, float):
            raise ValueError

        else:
            self.__value = val

        if self.__value > self.out_of: raise ValueError

    #@+node:ekr.20170428084208.305: *3* Slider.get_value
    def get_value(self):
        return float(self.__value)
    value = property(get_value, set_value)

    #@+node:ekr.20170428084208.306: *3* Slider.set_up_handlers
    def set_up_handlers(self):
        '''Slider.set_up_handlers.'''
        super(widget.Widget, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_LEFT: self.h_decrease,
            curses.KEY_RIGHT: self.h_increase,
            ord('+'): self.h_increase,
            ord('-'): self.h_decrease,
            ord('h'): self.h_decrease,
            ord('l'): self.h_increase,
            ord('j'): self.h_exit_down,
            ord('k'): self.h_exit_up,
        })

    #@+node:ekr.20170428084208.307: *3* Slider.h_increase
    def h_increase(self, ch):
        if (self.value + self.step <= self.out_of): self.value += self.step

    #@+node:ekr.20170428084208.308: *3* Slider.h_decrease
    def h_decrease(self, ch):
        if (self.value - self.step >= self.lowest): self.value -= self.step


    #@-others
#@+node:ekr.20170428084208.309: ** class TitleSlider
class TitleSlider(titlefield.TitleText):
    _entry_type = Slider

#@+node:ekr.20170428084208.310: ** class SliderNoLabel
class SliderNoLabel(Slider):
    #@+others
    #@+node:ekr.20170428084208.311: *3* __init__
    def __init__(self, screen, label=False, *args, **kwargs):
        super(SliderNoLabel, self).__init__(screen, label=label, *args, **kwargs)

    #@+node:ekr.20170428084208.312: *3* translate_value
    def translate_value(self):
        return ''

    #@-others
#@+node:ekr.20170428084208.313: ** class TitleSliderNoLabel
class TitleSliderNoLabel(TitleSlider):
    _entry_type = SliderNoLabel

#@+node:ekr.20170428084208.314: ** class SliderPercent
class SliderPercent(Slider):
    #@+others
    #@+node:ekr.20170428084208.315: *3* __init__
    def __init__(self, screen, accuracy=2, *args, **kwargs):
        super(SliderPercent, self).__init__(screen, *args, **kwargs)
        self.accuracy = accuracy

    #@+node:ekr.20170428084208.316: *3* translate_value
    def translate_value(self):
        pc = float(self.value) / float(self.out_of) * 100
        return '%.*f%%' % (int(self.accuracy), pc)

    #@-others
#@+node:ekr.20170428084208.317: ** class TitleSliderPercent
class TitleSliderPercent(TitleSlider):
    _entry_type = SliderPercent
#@-others
#@@language python
#@@tabwidth -4
#@@nobeautify
#@-leo
