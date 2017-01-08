# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20170107214315.1: * @file ../external/pyzo/style.py
#@@first
#@+<< pyzo copyright >>
#@+node:ekr.20170108171955.1: ** << pyzo copyright >>
# Copyright (C) 2016, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#@-<< pyzo copyright >>
from leo.core.leoQt import QtCore, QtGui
Qt = QtCore.Qt
#@+others
#@+node:ekr.20170107214321.3: ** class StyleElementDescription
class StyleElementDescription:
    """ StyleElementDescription(name, defaultFormat, description)
    
    Describes a style element by its name, default format, and description.
    
    A style description is a simple placeholder for something
    that can be styled.
    
    """
    
    #@+others
    #@+node:ekr.20170107214321.4: *3* __init__
    def __init__(self, name, description, defaultFormat):
        self._name = name
        self._description = description
        self._defaultFormat = StyleFormat(defaultFormat)
    #@+node:ekr.20170107214321.5: *3* __repr__
    def __repr__(self):
        return '<"%s": "%s">' % (self.name, self.defaultFormat)
    #@+node:ekr.20170107214321.6: *3* name
    @property
    def name(self):
        return self._name
    #@+node:ekr.20170107214321.7: *3* key
    @property
    def key(self):
        return self._name.replace(' ', '').lower()
    #@+node:ekr.20170107214321.8: *3* description
    @property
    def description(self):
        return self._description
    #@+node:ekr.20170107214321.9: *3* defaultFormat
    @property
    def defaultFormat(self):
        return self._defaultFormat
    #@-others
#@+node:ekr.20170107214321.10: ** class StyleFormat
class StyleFormat:
    """ StyleFormat(format='')
    
    Represents the style format for a specific style element.
    A "style" is a dictionary that maps names (of style elements) 
    to StyleFormat instances.
    
    The given format can be a string or another StyleFormat instance.
    Style formats can be combined using their update() method. 
    
    A style format consists of multiple parts, where each "part" consists
    of a key and a value. The keys can be anything, depending
    on what kind of thing is being styled. The value can be obtained using
    the index operator (e.g. styleFomat['fore'])
    
    For a few special keys, properties are defined that return the Qt object
    corresponding to the value. These values are also buffered to enable
    fast access. These keys are:
      * fore: (QColor) the foreground color
      * back: (QColor) the background color
      * bold: (bool) whether the text should be bold
      * italic: (bool) whether the text should be in italic
      * underline: (int) whether an underline should be used (and which one)
      * linestyle: (int) what line style to use (e.g. for indent guides)
      * textCharFOrmat: (QTextCharFormat) for the syntax styles
    
    The format neglects spaces and case. Parts are separated by commas 
    or semicolons. If only a key is given it's value is interpreted
    as 'yes'. If only a color is given, its key is interpreted as 'fore' 
    and back. Colors should be given using the '#' hex formatting.
    
    An example format string: 'fore:#334, bold, underline:dotLine'
    
    By calling str(styleFormatInstance) the string representing of the 
    format can be obtained. By iterating over the instance, a series 
    of key-value pairs is obtained.
    
    """
    
    #@+others
    #@+node:ekr.20170107214321.11: *3* __init__
    def __init__(self, format=''):
        self._parts = {}
        self.update(format)
    #@+node:ekr.20170107214321.12: *3* _resetProperties
    def _resetProperties(self):
        self._fore = None
        self._back = None
        self._bold = None
        self._italic = None
        self._underline = None
        self._linestyle = None
        self._textCharFormat = None
    #@+node:ekr.20170107214321.13: *3* __str__
    def __str__(self):
        """ Get a (cleaned up) string representation of this style format. 
        """
        parts = []
        for key in self._parts:
            parts.append('%s:%s' % (key, self._parts[key]))
        return ', '.join(parts)
    #@+node:ekr.20170107214321.14: *3* __repr__
    def __repr__(self):
        return '<StyleFormat "%s">' % str(self)
    #@+node:ekr.20170107214321.15: *3* __getitem__
    def __getitem__(self, key):
        try:
            return self._parts[key]
        except KeyError:
            raise KeyError('Invalid part key for style format.')
    #@+node:ekr.20170107214321.16: *3* __iter__
    def __iter__(self):
        """ Yields a series of tuples (key, val).
        """
        parts = []
        for key in self._parts:
            parts.append( (key, self._parts[key]) )
        return parts.__iter__()
    #@+node:ekr.20170107214321.17: *3* update
    def update(self, format):
        """ update(format)
        
        Update this style format with the given format.
        
        """
        # Reset buffered values
        self._resetProperties()
        # Make a string, so we update the format with the given one
        if isinstance(format, StyleFormat):
            format = str(format)
        # Split on ',' and ',', ignore spaces
        styleParts = [p for p in
            format.replace('=',':').replace(';',',').split(',')]
        for stylePart in styleParts:
            # Make sure it consists of identifier and value pair
            # e.g. fore:#xxx, bold:yes, underline:no
            if not ':' in stylePart:
                if stylePart.startswith('#'):
                    stylePart = 'foreandback:' + stylePart
                else:
                    stylePart += ':yes'
            # Get key value and strip and make lowecase
            key, _, val = [i.strip().lower() for i in stylePart.partition(':')]
            # Store in parts
            if key == 'foreandback':
                self._parts['fore'] = val
                self._parts['back'] = val
            elif key:
                self._parts[key] = val

    #@+node:ekr.20170108171245.1: *3* properties & helper
    #@+node:ekr.20170107214321.18: *4* _getValueSafe
    def _getValueSafe(self, key):
        try:
            return self._parts[key]
        except KeyError:
            return 'no'
    #@+node:ekr.20170107214321.20: *4* back
    @property
    def back(self):
        if self._back is None:
            self._back = QtGui.QColor(self._parts['back'])
        return self._back
    #@+node:ekr.20170107214321.21: *4* bold
    @property
    def bold(self):
        if self._bold is None:
            if self._getValueSafe('bold') in ['yes', 'true']:
                self._bold = True
            else:
                self._bold = False
        return self._bold
    #@+node:ekr.20170107214321.19: *4* fore
    @property
    def fore(self):
        if self._fore is None:
            self._fore = QtGui.QColor(self._parts['fore'])
        return self._fore
    #@+node:ekr.20170107214321.22: *4* italic
    @property
    def italic(self):
        if self._italic is None:
            if self._getValueSafe('italic') in ['yes', 'true']:
                self._italic = True
            else:
                self._italic = False
        return self._italic
    #@+node:ekr.20170107214321.24: *4* linestyle
    @property
    def linestyle(self):
        if self._linestyle is None:
            val = self._getValueSafe('linestyle')
            if val in ['yes', 'true']:
                self._linestyle = Qt.SolidLine
            elif val in ['dotted', 'dot', 'dots', 'dotline']: 
                self._linestyle = Qt.DotLine
            elif val in ['dashed', 'dash', 'dashes', 'dashline']: 
                self._linestyle = Qt.DashLine
            else:
                self._linestyle = Qt.SolidLine # default to solid
        return self._linestyle
    #@+node:ekr.20170107214321.25: *4* textCharFormat
    @property
    def textCharFormat(self):
        if self._textCharFormat is None:
            self._textCharFormat = tcf = QtGui.QTextCharFormat()
            self._textCharFormat.setForeground(self.fore)
            self._textCharFormat.setUnderlineStyle(self.underline)
            if self.bold:
                self._textCharFormat.setFontWeight(QtGui.QFont.Bold)
            if self.italic:
                self._textCharFormat.setFontItalic(True)
        return self._textCharFormat
    #@+node:ekr.20170107214321.23: *4* underline
    @property
    def underline(self):
        if self._underline is None:
            val = self._getValueSafe('underline')
            if val in ['yes', 'true']:
                self._underline = QtGui.QTextCharFormat.SingleUnderline
            elif val in ['dotted', 'dots', 'dotline']: 
                self._underline = QtGui.QTextCharFormat.DotLine
            elif val in ['wave']: 
                self._underline = QtGui.QTextCharFormat.WaveUnderline
            else:
                self._underline = QtGui.QTextCharFormat.NoUnderline
        return self._underline
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
