#@+leo-ver=5-thin
#@+node:ekr.20170428084207.377: * @file ../external/npyscreen/npysThemeManagers.py
#!/usr/bin/env python
# encoding: utf-8
#@+others
#@+node:ekr.20170428084207.378: ** Declarations
import curses
from . import npysGlobalOptions

#@+node:ekr.20170428084207.379: ** disableColor
def disableColor():
    npysGlobalOptions.DISABLE_ALL_COLORS = True

#@+node:ekr.20170428084207.380: ** enableColor
def enableColor():
    npysGlobalOptions.DISABLE_ALL_COLORS = False

#@+node:ekr.20170428084207.381: ** class ThemeManager
class ThemeManager:
    # a tuple with (color_number, (r, g, b))
    # you can use this to redefine colour values.
    # This will only work on compatible terminals.
    # Beware that effects will last beyond the end of the
    # application.
    _color_values = (
        #(curses.COLOR_GREEN, (150,250,100)),
    )


    _colors_to_define = (
     # DO NOT DEFINE THE WHITE_BLACK COLOR - THINGS BREAK
     #('WHITE_BLACK',      DO_NOT_DO_THIS,      DO_NOT_DO_THIS),
     ('BLACK_WHITE', curses.COLOR_BLACK, curses.COLOR_WHITE),
     #('BLACK_ON_DEFAULT', curses.COLOR_BLACK,      -1),
     #('WHITE_ON_DEFAULT', curses.COLOR_WHITE,      -1),
     ('BLUE_BLACK', curses.COLOR_BLUE, curses.COLOR_BLACK),
     ('CYAN_BLACK', curses.COLOR_CYAN, curses.COLOR_BLACK),
     ('GREEN_BLACK', curses.COLOR_GREEN, curses.COLOR_BLACK),
     ('MAGENTA_BLACK', curses.COLOR_MAGENTA, curses.COLOR_BLACK),
     ('RED_BLACK', curses.COLOR_RED, curses.COLOR_BLACK),
     ('YELLOW_BLACK', curses.COLOR_YELLOW, curses.COLOR_BLACK),
     ('BLACK_RED', curses.COLOR_BLACK, curses.COLOR_RED),
     ('BLACK_GREEN', curses.COLOR_BLACK, curses.COLOR_GREEN),
     ('BLACK_YELLOW', curses.COLOR_BLACK, curses.COLOR_YELLOW),
     ('BLACK_CYAN', curses.COLOR_BLACK, curses.COLOR_CYAN),
     ('BLUE_WHITE', curses.COLOR_BLUE, curses.COLOR_WHITE),
     ('CYAN_WHITE', curses.COLOR_CYAN, curses.COLOR_WHITE),
     ('GREEN_WHITE', curses.COLOR_GREEN, curses.COLOR_WHITE),
     ('MAGENTA_WHITE', curses.COLOR_MAGENTA, curses.COLOR_WHITE),
     ('RED_WHITE', curses.COLOR_RED, curses.COLOR_WHITE),
     ('YELLOW_WHITE', curses.COLOR_YELLOW, curses.COLOR_WHITE),
    )

    default_colors = {
        'DEFAULT': 'WHITE_BLACK',
        'FORMDEFAULT': 'WHITE_BLACK',
        'NO_EDIT': 'BLUE_BLACK',
        'STANDOUT': 'CYAN_BLACK',
        'CURSOR': 'WHITE_BLACK',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL': 'GREEN_BLACK',
        'LABELBOLD': 'WHITE_BLACK',
        'CONTROL': 'YELLOW_BLACK',
        'IMPORTANT': 'GREEN_BLACK',
        'SAFE': 'GREEN_BLACK',
        'WARNING': 'YELLOW_BLACK',
        'DANGER': 'RED_BLACK',
        'CRITICAL': 'BLACK_RED',
        'GOOD': 'GREEN_BLACK',
        'GOODHL': 'GREEN_BLACK',
        'VERYGOOD': 'BLACK_GREEN',
        'CAUTION': 'YELLOW_BLACK',
        'CAUTIONHL': 'BLACK_YELLOW',
    }
    #@+others
    #@+node:ekr.20170428084207.382: *3* __init__
    def __init__(self):
        #curses.use_default_colors()
        self.define_colour_numbers()
        self._defined_pairs = {}
        self._names = {}
        try:
            self._max_pairs = curses.COLOR_PAIRS - 1
            do_color = True
        except AttributeError:
            # curses.start_color has failed or has not been called
            do_color = False
            # Disable all color use across the application
            disableColor()
        if do_color and curses.has_colors():
            self.initialize_pairs()
            self.initialize_names()

    #@+node:ekr.20170428084207.383: *3* define_colour_numbers
    def define_colour_numbers(self):
        if curses.can_change_color():
            for c in self._color_values:
                curses.init_color(c[0], *c[1])


    #@+node:ekr.20170428084207.384: *3* findPair
    def findPair(self, caller, request='DEFAULT'):
        if not curses.has_colors() or npysGlobalOptions.DISABLE_ALL_COLORS:
            return False

        if request == 'DEFAULT':
            request = caller.color
        # Locate the requested colour pair.  Default to default if not found.
        try:
            pair = self._defined_pairs[self._names[request]]
        except Exception:
            pair = self._defined_pairs[self._names['DEFAULT']]

        # now make the actual attribute
        color_attribute = curses.color_pair(pair[0])

        return color_attribute

    #@+node:ekr.20170428084207.385: *3* setDefault
    def setDefault(self, caller):
        return False

    #@+node:ekr.20170428084207.386: *3* initialize_pairs
    def initialize_pairs(self):
        # White on Black is fixed as color_pair 0
        self._defined_pairs['WHITE_BLACK'] = (0, curses.COLOR_WHITE, curses.COLOR_BLACK)
        for cp in self.__class__._colors_to_define:
            if cp[0] == 'WHITE_BLACK':
                # silently protect the user from breaking things.
                continue
            self.initalize_pair(cp[0], cp[1], cp[2])

    #@+node:ekr.20170428084207.387: *3* initialize_names
    def initialize_names(self):
        self._names.update(self.__class__.default_colors)

    #@+node:ekr.20170428084207.388: *3* initalize_pair
    def initalize_pair(self, name, fg, bg):
        # Initialize a color_pair for the required colour and return the number. Raise an exception if this is not possible.
        if (len(list(self._defined_pairs.keys())) + 1) == self._max_pairs:
            raise Exception("Too many colours")

        _this_pair_number = len(list(self._defined_pairs.keys())) + 1

        curses.init_pair(_this_pair_number, fg, bg)

        self._defined_pairs[name] = (_this_pair_number, fg, bg)

        return _this_pair_number

    #@+node:ekr.20170428084207.389: *3* get_pair_number
    def get_pair_number(self, name):
        return self._defined_pairs[name][0]
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
