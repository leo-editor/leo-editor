#@+leo-ver=5-thin
#@+node:ekr.20140827092102.18574: * @file leoColorizer.py
"""Classes that syntax color body text."""

# Indicated code are copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

#@+<< leoColorizer imports >>
#@+node:ekr.20140827092102.18575: ** << leoColorizer imports >>
from __future__ import annotations
from collections.abc import Callable
import re
import string
import time
from typing import Any, Generator, Sequence, Optional, Union, TYPE_CHECKING
from types import ModuleType
import warnings

# Third-party tools.
try:
    import pygments
    from pygments.lexer import DelegatingLexer, RegexLexer, _TokenType, Text, Error
except ImportError:
    pygments = None

# Leo imports...
from leo.core import leoGlobals as g
from leo.core.leoColor import leo_color_database

# Qt imports. May fail from the bridge.
try:  # #1973
    from leo.core.leoQt import Qsci, QtGui, QtWidgets
    from leo.core.leoQt import UnderlineStyle, Weight  # #2330
except Exception:
    Qsci = QtGui = QtWidgets = None
    UnderlineStyle = Weight = None
#@-<< leoColorizer imports >>
#@+<< leoColorizer annotations >>
#@+node:ekr.20220901164936.1: ** << leoColorizer annotations >>
if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position, VNode
    from leo.core.leoGlobals import GeneralSetting
    try:
        from typing import Self
    except Exception:
        Self = Any
    KWargs = Any
    Lexer = Callable
    QWidget = QtWidgets.QWidget
    RuleSet = list[Callable]
#@-<< leoColorizer annotations >>
#@+others
#@+node:ekr.20190323044524.1: ** function: make_colorizer
def make_colorizer(c: Cmdr, widget: QWidget) -> Union[JEditColorizer, PygmentsColorizer]:
    """Return an instance of JEditColorizer or PygmentsColorizer."""
    use_pygments = pygments and c.config.getBool('use-pygments', default=False)
    if use_pygments:
        return PygmentsColorizer(c, widget)
    return JEditColorizer(c, widget)
#@+node:ekr.20170127141855.1: ** class BaseColorizer
class BaseColorizer:
    """
    The base class for all Leo colorizers.

    c.frame.body.colorizer is the actual colorizer.
    """
    #@+others
    #@+node:ekr.20220317050513.1: *3*  BaseColorizer: birth
    #@+node:ekr.20190324044744.1: *4* BaseColorizer.__init__
    def __init__(self, c: Cmdr, widget: QWidget = None) -> None:
        """ctor for BaseColorizer class."""
        # Copy args...
        self.c = c
        self.widget: QWidget = widget
        if widget:  # #503: widget may be None during unit tests.
            widget.leo_colorizer = self
        # Configuration dicts...
        self.configDict: dict[str, str] = {}  # Keys are tags, values are colors (names or values).
        self.configUnderlineDict: dict[str, bool] = {}  # Keys are tags, values are bools.
        # Common state ivars...
        self.enabled = False  # Per-node enable/disable flag set by updateSyntaxColorer.
        self.highlighter: object = g.NullObject()  # May be overridden in subclass...
        self.language = 'python'  # set by scanLanguageDirectives.
        self.showInvisibles = False
        # Statistics....
        self.count = 0
        self.full_recolor_count = 0  # For unit tests.
        self.recolorCount = 0
        # For traces...
        self.matcher_name: str = ''
        self.rulesetName: str = ''
        self.delegate_name: str = ''
    #@+node:ekr.20190324045134.1: *4* BaseColorizer.init
    def init(self) -> None:
        """May be over-ridden in subclasses."""
        pass
    #@+node:ekr.20110605121601.18578: *4* BaseColorizer.configureTags & helpers
    def configureTags(self) -> None:
        """Configure all tags."""
        self.configure_fonts()
        self.configure_colors()
        self.configure_variable_tags()
    #@+node:ekr.20190324172632.1: *5* BaseColorizer.configure_colors & helper
    def configure_colors(self) -> None:
        """Configure all colors in the default colors dict."""
        c = self.c

        # getColor puts the color name in standard form:
        # color = color.replace(' ', '').lower().strip()

        #@+<< function: resolve_color_key >>
        #@+node:ekr.20230314052558.1: *6* << function: resolve_color_key >>
        def resolve_color_key(key: str) -> str:
            """
            Resolve the given color name to a *valid* color.
            """
            option_name, default_color = self.default_colors_dict[key]
            colors = (
                c.config.getColor(f"{self.language}.{option_name}"),  # Preferred.
                c.config.getColor(f"{self.language}{option_name}"),  # Legacy.
                c.config.getColor(option_name),
                default_color,
            )
            for color in colors:
                color1 = color
                while color:
                    color = self.normalize(color)
                    if color in leo_color_database:
                        color = leo_color_database.get(color)
                    qt_color = QtGui.QColor(color)
                    if qt_color.isValid():
                        return color
                    if color.startswith('@'):
                        color = color[1:]
                    else:
                        g.trace('Invalid @color setting:', key, color1)
                        break
            return None  # Reasonable default.
        #@-<< function: resolve_color_key >>

        # Compute *all* color keys, not just those in default_colors_dict.
        all_color_keys = list(self.default_colors_dict.keys())
        if c.config.settingsDict:
            gs: GeneralSetting
            for key, gs in c.config.settingsDict.items():
                if gs and gs.kind == 'color' and gs.val:
                    all_color_keys.append(key)
                    self.default_colors_dict[key] = (key, self.normalize(gs.val))
        for key in sorted(all_color_keys):
            self.configDict[key] = resolve_color_key(key)
    #@+node:ekr.20190324172242.1: *5* BaseColorizer.configure_fonts & helpers
    def configure_fonts(self) -> None:
        """
        Configure:
        - All fonts in the the default fonts dict.
        - All fonts mentioned in any @font setting.
        """
        c = self.c
        self.font_selectors = ('family', 'size', 'slant', 'weight')
        # Keys are font names. Values are Dicts[selector, value]
        self.new_fonts: dict[str, dict] = {}

        # Get the default body font.
        defaultBodyfont = self.fonts.get('default_body_font')
        if not defaultBodyfont:
            defaultBodyfont = c.config.getFontFromParams(
                "body_text_font_family", "body_text_font_size",
                "body_text_font_slant", "body_text_font_weight",
                c.config.defaultBodyFontSize)
            self.fonts['default_body_font'] = defaultBodyfont

        # Handle syntax-coloring fonts.
        if c.config.settingsDict:
            gs: GeneralSetting
            setting_pat = re.compile(r'@font\s+(\w+)\.(\w+)')
            valid_languages = list(g.app.language_delims_dict.keys())
            valid_languages.append('rest_comments')
            valid_tags = self.default_font_dict.keys()
            for setting in sorted(c.config.settingsDict):
                gs = c.config.settingsDict.get(setting)
                if gs and gs.source:  # An @font setting.
                    if m := setting_pat.match(gs.source):
                        language, tag = m.group(1), m.group(2)
                        if language in valid_languages and tag in valid_tags:
                            self.resolve_font(setting, language, tag, gs.val)
                        else:
                            g.trace('Ignoring', gs.source)

        # Create all new syntax-coloring fonts.
        for font_name in self.new_fonts:
            d = self.new_fonts[font_name]
            font = g.app.gui.getFontFromParams(
                family=d.get('family'),
                size=self.zoomed_size(font_name, d.get('size')),
                slant=d.get('slant'),
                weight=d.get('weight'),
                tag=font_name,
            )
            # #1919: This really isn't correct.
            self.configure_hard_tab_width(font)
            self.fonts[font_name] = font

        # Set default fonts.
        for key in self.default_font_dict.keys():
            self.fonts[key] = None  # Default
            option_name = self.default_font_dict[key]
            for name in (
                f"{self.language}_{option_name}",
                option_name,
            ):
                font = self.fonts.get(name)
                if font:
                    break
                font = self.create_font(key, name)
                if font:
                    self.fonts[name] = font
                    if key == 'url':
                        try:  # Special case for Qt.
                            font.setUnderline(True)
                        except Exception:
                            pass
                    # #1919: This really isn't correct.
                    self.configure_hard_tab_width(font)
                    break
    #@+node:ekr.20230314052820.1: *6* BaseColorizer.resolve_font
    def resolve_font(self, setting: str, language: str, tag: str, val: str) -> None:
        """
        Resolve the arguments to a selector and font name.

        Add the selector to the font's entry in self.new_fonts.
        """
        for selector in self.font_selectors:
            if selector in setting:
                font_name = f"{language}.{tag}".lower()
                font_info = self.new_fonts.get(font_name, {})
                font_info[selector] = val
                self.new_fonts[font_name] = font_info
    #@+node:ekr.20190326034006.1: *6* BaseColorizer.create_font
    # Keys are key::settings_names. Values are cumulative font size.
    zoom_dict: dict[str, int] = {}

    def create_font(self, key: str, setting_name: str) -> QtGui.QFont:
        """
        Return the font for the given setting name.

        Return None if no font setting with the given name exists.
        """
        trace = 'coloring' in g.app.debug
        c = self.c
        get = c.config.get
        for name in (setting_name, setting_name.rstrip('_font')):
            family = get(name + '_family', 'family')
            size = get(name + '_size', 'size')
            slant = get(name + '_slant', 'slant')
            weight = get(name + '_weight', 'weight')
            if family or slant or weight or size:
                slant = slant or 'roman'
                weight = weight or 'normal'
                size = self.zoomed_size(f"{key}::{setting_name}", size)
                font = g.app.gui.getFontFromParams(family, size, slant, weight, tag=setting_name)
                if font:
                    if trace:
                        # A good trace: the key shows what is happening.
                        g.trace(
                            f"Create font: {id(font)} "
                            f"setting: {setting_name} "
                            f"key: {key} family: {family or 'None'} "
                            f"size: {size or 'None'} {slant} {weight}")
                    return font
        return None
    #@+node:ekr.20230317072911.1: *6* BaseColorizer.zoomed_size
    def zoomed_size(self, key: str, size: str) -> str:
        """
        Return the effect size (as a string) of the font after zooming.

        `key`: key for the zoom_dict.
        """
        c = self.c
        default_size = str(c.config.defaultBodyFontSize)
        # Compute i_size.
        i_size: int
        if key in self.zoom_dict:
            i_size = self.zoom_dict.get(key)
        else:
            s_size: str = size or default_size
            if s_size.endswith(('pt', 'px'),):
                s_size = s_size[:-2]
            try:
                i_size = int(s_size)
            except ValueError:
                # Don't zoom.
                return s_size

        # Bump i_size by the zoom_delta.
        zoom_delta: int = getattr(c, 'zoom_delta', 0)
        if zoom_delta:
            i_size += zoom_delta
            self.zoom_dict[key] = i_size
        return str(i_size)
    #@+node:ekr.20111024091133.16702: *5* BaseColorizer.configure_hard_tab_width
    def configure_hard_tab_width(self, font: QtGui.QFont) -> None:
        """
        Set the width of a hard tab.

        Qt does not appear to have the required methods. Indeed,
        https://stackoverflow.com/questions/13027091/how-to-override-tab-width-in-qt
        assumes that QTextEdit's have only a single font(!).

        This method probably only works probably if the body text contains
        a single @language directive, and it may not work properly even then.
        """
        c, widget = self.c, self.widget
        if isinstance(widget, QtWidgets.QTextEdit):
            # #1919: https://forum.qt.io/topic/99371/how-to-set-tab-stop-width-and-space-width
            fm = QtGui.QFontMetrics(font)
            try:  # fm.horizontalAdvance
                width = fm.horizontalAdvance(' ') * abs(c.tab_width)
                widget.setTabStopDistance(width)
            except Exception:
                width = fm.width(' ') * abs(c.tab_width)
                widget.setTabStopWidth(width)  # Obsolete.
        else:
            # To do: configure the QScintilla widget.
            pass
    #@+node:ekr.20110605121601.18579: *5* BaseColorizer.configure_variable_tags
    def configure_variable_tags(self) -> None:
        c = self.c
        use_pygments = pygments and c.config.getBool('use-pygments', default=False)
        name = 'name.other' if use_pygments else 'name'
        self.configUnderlineDict[name] = self.underline_undefined
        for name, option_name, default_color in (
            # ("blank", "show_invisibles_space_background_color", "Gray90"),
            # ("tab", "show_invisibles_tab_background_color", "Gray80"),
            ("elide", None, "yellow"),
        ):
            if self.showInvisibles:
                color = c.config.getColor(option_name) if option_name else default_color
            else:
                option_name, default_color = self.default_colors_dict.get(name, (None, None))
                color = c.config.getColor(option_name) if option_name else ''
            self.configDict[name] = color  # 2022/05/20: Discovered by pyflakes.
    #@+node:ekr.20110605121601.18574: *4* BaseColorizer.defineDefaultColorsDict
    #@@nobeautify

    def defineDefaultColorsDict(self) -> None:

        # These defaults are sure to exist.
        self.default_colors_dict = {

            # Used in Leo rules...
            # tag name      : ( option name,                   default color),
            'blank'         : ('show_invisibles_space_color',  '#E5E5E5'),  # gray90
            'docpart'       : ('doc_part_color',               'red'),
            'leokeyword'    : ('leo_keyword_color',            'blue'),
            'link'          : ('section_name_color',           'red'),
            'name'          : ('undefined_section_name_color', 'red'),
            'namebrackets'  : ('section_name_brackets_color',  'blue'),
            'tab'           : ('show_invisibles_tab_color',    '#CCCCCC'),  # gray80
            'url'           : ('url_color',                    'purple'),

            # Pygments tags.  Non-default values are taken from 'default' style.

            # Top-level...
            # tag name          : ( option name,         default color),
            'error'             : ('error',              '#FF0000'),  # border
            'other'             : ('other',              'white'),
            'punctuation'       : ('punctuation',        'white'),
            'whitespace'        : ('whitespace',         '#bbbbbb'),
            'xt'                : ('xt',                 '#bbbbbb'),

            # Comment...
            # tag name          : ( option name,         default color),
            'comment'           : ('comment',            '#408080'),  # italic
            'comment.hashbang'  : ('comment.hashbang',   '#408080'),
            'comment.multiline' : ('comment.multiline',  '#408080'),
            'comment.special'   : ('comment.special',    '#408080'),
            'comment.preproc'   : ('comment.preproc',    '#BC7A00'),  # noitalic
            'comment.single'    : ('comment.single',     '#BC7A00'),  # italic

            # Generic...
            # tag name          : ( option name,         default color),
            'generic'           : ('generic',            '#A00000'),
            'generic.deleted'   : ('generic.deleted',    '#A00000'),
            'generic.emph'      : ('generic.emph',       '#000080'),  # italic
            'generic.error'     : ('generic.error',      '#FF0000'),
            'generic.heading'   : ('generic.heading',    '#000080'),  # bold
            'generic.inserted'  : ('generic.inserted',   '#00A000'),
            'generic.output'    : ('generic.output',     '#888'),
            'generic.prompt'    : ('generic.prompt',     '#000080'),  # bold
            'generic.strong'    : ('generic.strong',     '#000080'),  # bold
            'generic.subheading': ('generic.subheading', '#800080'),  # bold
            'generic.traceback' : ('generic.traceback',  '#04D'),
            #
            # Keyword...
            # tag name              : ( option name,             default color),
            'keyword'               : ('keyword',                '#008000'),  # bold
            'keyword.constant'      : ('keyword.constant',       '#008000'),
            'keyword.declaration'   : ('keyword.declaration',    '#008000'),
            'keyword.namespace'     : ('keyword.namespace',      '#008000'),
            'keyword.pseudo'        : ('keyword.pseudo',         '#008000'),  # nobold
            'keyword.reserved'      : ('keyword.reserved',       '#008000'),
            'keyword.type'          : ('keyword.type',           '#B00040'),

            # Literal...
            # tag name              : ( option name,         default color),
            'literal'               : ('literal',            'white'),
            'literal.date'          : ('literal.date',       'white'),

            # Name...
            # tag name              : ( option name,          default color
            # 'name' defined below.
            'name.attribute'        : ('name.attribute',      '#7D9029'),  # bold
            'name.builtin'          : ('name.builtin',        '#008000'),
            'name.builtin.pseudo'   : ('name.builtin.pseudo', '#008000'),
            'name.class'            : ('name.class',          '#0000FF'),  # bold
            'name.constant'         : ('name.constant',       '#880000'),
            'name.decorator'        : ('name.decorator',      '#AA22FF'),
            'name.entity'           : ('name.entity',         '#999999'),  # bold
            'name.exception'        : ('name.exception',      '#D2413A'),  # bold
            'name.function'         : ('name.function',       '#0000FF'),
            'name.function.magic'   : ('name.function.magic', '#0000FF'),
            'name.label'            : ('name.label',          '#A0A000'),
            'name.namespace'        : ('name.namespace',      '#0000FF'),  # bold
            'name.other'            : ('name.other',          'red'),
            # A hack: getLegacyFormat returns name.pygments instead of name.
            'name.pygments'         : ('name.pygments',          'white'),
            'name.tag'              : ('name.tag',               '#008000'),  # bold
            'name.variable'         : ('name.variable',          '#19177C'),
            'name.variable.class'   : ('name.variable.class',    '#19177C'),
            'name.variable.global'  : ('name.variable.global',   '#19177C'),
            'name.variable.instance': ('name.variable.instance', '#19177C'),
            'name.variable.magic'   : ('name.variable.magic',    '#19177C'),

            # Number...
            # tag name              : ( option name,          default color
            'number'                : ('number',              '#666666'),
            'number.bin'            : ('number.bin',          '#666666'),
            'number.float'          : ('number.float',        '#666666'),
            'number.hex'            : ('number.hex',          '#666666'),
            'number.integer'        : ('number.integer',      '#666666'),
            'number.integer.long'   : ('number.integer.long', '#666666'),
            'number.oct'            : ('number.oct',          '#666666'),

            # Operator...
            # tag name          : ( option name,         default color
            # 'operator' defined below.
            'operator.word'     : ('operator.Word',      '#AA22FF'),  # bold

            # String...
            # tag name          : ( option name,         default color
            'string'            : ('string',             '#BA2121'),
            'string.affix'      : ('string.affix',       '#BA2121'),
            'string.backtick'   : ('string.backtick',    '#BA2121'),
            'string.char'       : ('string.char',        '#BA2121'),
            'string.delimiter'  : ('string.delimiter',   '#BA2121'),
            'string.doc'        : ('string.doc',         '#BA2121'),  # italic
            'string.double'     : ('string.double',      '#BA2121'),
            'string.escape'     : ('string.escape',      '#BB6622'),  # bold
            'string.heredoc'    : ('string.heredoc',     '#BA2121'),
            'string.interpol'   : ('string.interpol',    '#BB6688'),  # bold
            'string.other'      : ('string.other',       '#008000'),
            'string.regex'      : ('string.regex',       '#BB6688'),
            'string.single'     : ('string.single',      '#BA2121'),
            'string.symbol'     : ('string.symbol',      '#19177C'),
            #
            # jEdit tags.
            # tag name  : ( option name,     default color),
            'comment1'  : ('comment1_color', 'red'),
            'comment2'  : ('comment2_color', 'red'),
            'comment3'  : ('comment3_color', 'red'),
            'comment4'  : ('comment4_color', 'red'),
            'function'  : ('function_color', 'black'),
            'keyword1'  : ('keyword1_color', 'blue'),
            'keyword2'  : ('keyword2_color', 'blue'),
            'keyword3'  : ('keyword3_color', 'blue'),
            'keyword4'  : ('keyword4_color', 'blue'),
            'keyword5'  : ('keyword5_color', 'blue'),
            'label'     : ('label_color',    'black'),
            'literal1'  : ('literal1_color', '#00aa00'),
            'literal2'  : ('literal2_color', '#00aa00'),
            'literal3'  : ('literal3_color', '#00aa00'),
            'literal4'  : ('literal4_color', '#00aa00'),
            'markup'    : ('markup_color',   'red'),
            'null'      : ('null_color',     None),  # 'black'
            'operator'  : ('operator_color', 'black'),
            'trailing_whitespace':  ('trailing_whitespace_color', '#808080'),
        }
    #@+node:ekr.20110605121601.18575: *4* BaseColorizer.defineDefaultFontDict
    #@@nobeautify

    def defineDefaultFontDict(self) -> None:

        self.default_font_dict = {

            # Used in Leo rules...
            # tag name      :  option name
            'blank'         : 'show_invisibles_space_font',  # 2011/10/24.
            'docpart'       : 'doc_part_font',
            'leokeyword'    : 'leo_keyword_font',
            'link'          : 'section_name_font',
            'name'          : 'undefined_section_name_font',
            'namebrackets'  : 'section_name_brackets_font',
            'tab'           : 'show_invisibles_tab_font',  # 2011/10/24.
            'url'           : 'url_font',

            # Pygments tags (lower case)...
            # tag name          :  option name
            "comment"           : 'comment1_font',
            "comment.preproc"   : 'comment2_font',
            "comment.single"    : 'comment1_font',
            "error"             : 'null_font',
            "generic.deleted"   : 'literal4_font',
            "generic.emph"      : 'literal4_font',
            "generic.error"     : 'literal4_font',
            "generic.heading"   : 'literal4_font',
            "generic.inserted"  : 'literal4_font',
            "generic.output"    : 'literal4_font',
            "generic.prompt"    : 'literal4_font',
            "generic.strong"    : 'literal4_font',
            "generic.subheading": 'literal4_font',
            "generic.traceback" : 'literal4_font',
            "keyword"           : 'keyword1_font',
            "keyword.pseudo"    : 'keyword2_font',
            "keyword.type"      : 'keyword3_font',
            "name.attribute"    : 'null_font',
            "name.builtin"      : 'null_font',
            "name.class"        : 'null_font',
            "name.constant"     : 'null_font',
            "name.decorator"    : 'null_font',
            "name.entity"       : 'null_font',
            "name.exception"    : 'null_font',
            "name.function"     : 'null_font',
            "name.label"        : 'null_font',
            "name.namespace"    : 'null_font',
            "name.tag"          : 'null_font',
            "name.variable"     : 'null_font',
            "number"            : 'null_font',
            "operator.word"     : 'keyword4_font',
            "string"            : 'literal1_font',
            "string.doc"        : 'literal1_font',
            "string.escape"     : 'literal1_font',
            "string.interpol"   : 'literal1_font',
            "string.other"      : 'literal1_font',
            "string.regex"      : 'literal1_font',
            "string.single"     : 'literal1_font',
            "string.symbol"     : 'literal1_font',
            'xt'                : 'text_font',
            "whitespace"        : 'text_font',

            # jEdit tags.
            # tag name      :  option name
            'comment1'      : 'comment1_font',
            'comment2'      : 'comment2_font',
            'comment3'      : 'comment3_font',
            'comment4'      : 'comment4_font',
            # 'default'     : 'default_font',
            'function'      : 'function_font',
            'keyword1'      : 'keyword1_font',
            'keyword2'      : 'keyword2_font',
            'keyword3'      : 'keyword3_font',
            'keyword4'      : 'keyword4_font',
            'keyword5'      : 'keyword5_font',
            'label'         : 'label_font',
            'literal1'      : 'literal1_font',
            'literal2'      : 'literal2_font',
            'literal3'      : 'literal3_font',
            'literal4'      : 'literal4_font',
            'markup'        : 'markup_font',
            # 'nocolor' This tag is used, but never generates code.
            'null'          : 'null_font',
            'operator'      : 'operator_font',
            'trailing_whitespace' : 'trailing_whitespace_font',
        }
    #@+node:ekr.20110605121601.18573: *4* BaseColorizer.defineLeoKeywordsDict
    def defineLeoKeywordsDict(self) -> None:
        self.leoKeywordsDict = {}
        for key in g.globalDirectiveList:
            self.leoKeywordsDict[key] = 'leokeyword'
    #@+node:ekr.20230313051116.1: *3* BaseColorizer.normalize
    def normalize(self, s: str) -> str:
        """Return the normalized value of s."""
        if s.startswith('@'):
            s = s[1:]
        return s.replace(' ', '').replace('-', '').replace('_', '').lower().strip()
    #@+node:ekr.20171114041307.1: *3* BaseColorizer.reloadSettings
    #@@nobeautify
    def reloadSettings(self) -> None:
        c, getBool = self.c, self.c.config.getBool
        #
        # Init all settings ivars.
        self.color_tags_list: list[str] = []
        self.showInvisibles      = getBool("show-invisibles-by-default")
        self.underline_undefined = getBool("underline-undefined-section-names")
        self.use_hyperlinks      = getBool("use-hyperlinks")
        self.use_pygments        = None  # Set in report_changes.
        self.use_pygments_styles = getBool('use-pygments-styles', default=True)
        #
        # Report changes to pygments settings.
        self.report_changes()
        #
        # Init the default fonts.
        self.bold_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant", "body_text_font_weight",
            c.config.defaultBodyFontSize)
        self.italic_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant", "body_text_font_weight",
            c.config.defaultBodyFontSize)
        self.bolditalic_font = c.config.getFontFromParams(
            "body_text_font_family", "body_text_font_size",
            "body_text_font_slant", "body_text_font_weight",
            c.config.defaultBodyFontSize)
        # Init everything else.
        self.init_style_ivars()
        self.defineLeoKeywordsDict()
        self.defineDefaultColorsDict()
        self.defineDefaultFontDict()
        self.configureTags()
        self.init()
    #@+node:ekr.20190327053604.1: *4* BaseColorizer.report_changes
    prev_use_pygments: bool = None
    prev_use_styles: bool = None
    prev_style: str = None

    def report_changes(self) -> None:
        """Report changes to pygments settings"""
        c = self.c
        use_pygments = c.config.getBool('use-pygments', default=False)
        if not use_pygments:  # 1696.
            return
        trace = 'coloring' in g.app.debug and not g.unitTesting
        if trace:
            g.es_print('\nreport changes...')

        def show(setting: str, val: object) -> None:
            if trace:
                g.es_print(f"{setting:35}: {val}")

        # Set self.use_pygments only once: it can't be changed later.
        # There is no easy way to re-instantiate classes created by make_colorizer.
        if self.prev_use_pygments is None:
            self.use_pygments = self.prev_use_pygments = use_pygments
            show('@bool use-pygments', use_pygments)
        elif use_pygments == self.prev_use_pygments:
            show('@bool use-pygments', use_pygments)
        else:
            g.es_print(
                f"{'Can not change @bool use-pygments':35}: "
                f"{self.prev_use_pygments}",
                color='red')
        # This setting is used only in the LeoHighlighter class
        style_name = c.config.getString('pygments-style-name') or 'default'
        # Report everything if we are tracing.
        show('@bool use-pygments-styles', self.use_pygments_styles)
        show('@string pygments-style-name', style_name)
        # Report changes to @bool use-pygments-style
        if self.prev_use_styles is None:
            self.prev_use_styles = self.use_pygments_styles
        elif self.use_pygments_styles != self.prev_use_styles:
            g.es_print(f"using pygments styles: {self.use_pygments_styles}")
        # Report @string pygments-style-name only if we are using styles.
        if not self.use_pygments_styles:
            return
        # Report changes to @string pygments-style-name
        if self.prev_style is None:
            self.prev_style = style_name
        elif style_name != self.prev_style:
            g.es_print(f"New pygments style: {style_name}")
            self.prev_style = style_name
    #@+node:ekr.20110605121601.18641: *3* BaseColorizer.setTag
    def setTag(self, tag: str, s: str, i: int, j: int) -> None:
        """Set the tag in the highlighter."""
        trace = 'coloring' in g.app.debug and not g.unitTesting

        default_tag = f"{tag}_font"  # See default_font_dict.
        full_tag = f"{self.language}.{tag}"
        font: QtGui.QFont = None  # Set below. Define here for report().

        def report(color: QtGui.QColor) -> None:
            """A superb trace. Don't remove it."""
            i_j_s = f"{i:>3}:{j:<3}"
            matcher_name = g.caller(3)
            rule_name = g.caller(4)
            matcher_s = f"{self.rulesetName}::{rule_name}:{matcher_name}"
            s2 = s[i:j]  # Show only the colored string.
            print(
                f"setTag: {self.recolorCount:4} "
                f"{matcher_s:<50} "
                f"color: {colorName:7} "
                f"tag: {full_tag:<20} "
                f"{i_j_s:7} {s2}"
            )

        self.n_setTag += 1
        if i == j:
            return
        if not tag or not tag.strip():
            return
        tag = tag.lower().strip()
        # A hack to allow continuation dots on any tag.
        dots = tag.startswith('dots')
        if dots:
            tag = tag[len('dots') :]
        # This color name should already be valid.
        d = self.configDict
        color_key = self.language.replace('_', '')
        colorName: str = (
            d.get(f"{self.language}.{tag}") or  # Legacy.
            d.get(f"{color_key}.{tag}") or  # Leo 6.8.4.
            d.get(tag)  # Legacy default.
        )
        if not colorName:
            return
        # New in Leo 5.8.1: allow symbolic color names here.
        #                   (All keys in leo_color_database are normalized.)
        colorName = self.normalize(colorName)
        colorName = leo_color_database.get(colorName, colorName)
        # Get the actual color.
        color: QtGui.QColor = self.actualColorDict.get(colorName)
        if not color:
            color = QtGui.QColor(colorName)
            if color.isValid():
                self.actualColorDict[colorName] = color
            else:
                # Leo 6.7.2: This should never happen: configure_colors does a pre-check.
                message = (
                    "jedit.setTag: can not happen: "
                    f"full_tag: {full_tag} = {d.get(full_tag)!r} "
                    f"tag: {tag} = {d.get(tag)!r}"
                )
                g.print_unique_message(message)
                return
        underline = self.configUnderlineDict.get(tag)
        format = QtGui.QTextCharFormat()
        for font_name in (full_tag, tag, default_tag):
            font = self.fonts.get(font_name)
            if font:
                format.setFont(font)
                self.configure_hard_tab_width(font)  # #1919.
                break
        if tag in ('blank', 'tab'):
            if tag == 'tab' or colorName == 'black':
                format.setFontUnderline(True)
            if colorName != 'black':
                format.setBackground(color)
        elif underline:
            format.setForeground(color)
            format.setUnderlineStyle(UnderlineStyle.SingleUnderline)
            format.setFontUnderline(True)
        elif dots or tag == 'trailing_whitespace':
            format.setForeground(color)
            format.setUnderlineStyle(UnderlineStyle.DotLine)
        else:
            format.setForeground(color)
            format.setUnderlineStyle(UnderlineStyle.NoUnderline)
        self.tagCount += 1
        if trace:
            report(color)  # A superb trace.
        self.highlighter.setFormat(i, j - i, format)
    #@+node:ekr.20190324050727.1: *3* BaseColorizer.init_style_ivars
    def init_style_ivars(self) -> None:
        """Init Style data common to JEdit and Pygments colorizers."""
        # init() properly sets these for each language.
        self.actualColorDict: dict[str, QtGui.QColor] = {}  # Used only by setTag.
        self.hyperCount = 0
        # Attributes dict ivars: defaults are as shown...
        self.default = 'null'
        self.digit_re = ''
        self.escape = ''
        self.highlight_digits = True
        self.ignore_case = True
        self.no_word_sep = ''
        # Debugging...
        self.allow_mark_prev = True
        self.n_setTag = 0
        self.tagCount = 0
        # Profiling...
        self.recolorCount = 0  # Total calls to recolor
        self.stateCount = 0  # Total calls to setCurrentState
        self.totalStates = 0
        self.maxStateNumber = 0
        self.totalKeywordsCalls = 0
        self.totalLeoKeywordsCalls = 0
        # Mode data...
        self.importedRulesets: dict[str, bool] = {}
        self.fonts: dict[str, QtGui.QFont] = {}  # Keys are config names.  Values are actual fonts.
        self.keywords: dict[str, int] = {}  # Keys are keywords, values are 0..5.
        self.modes: dict[str, JEditModeDescriptor] = {}  # Keys are languages, values are modes.
        self.mode: JEditModeDescriptor = None  # The mode descriptor for the present language.
        self.modeStack: list[JEditModeDescriptor] = []
        self.rulesDict: dict[str, RuleSet] = {}
        # self.defineAndExtendForthWords()
        self.word_chars: dict[str, str] = {}  # Inited by init_keywords().
        self.tags = [
            # 8 Leo-specific tags.
            "blank",  # show_invisibles_space_color
            "docpart",
            "leokeyword",
            "link",  # section reference.
            "name",
            "namebrackets",
            "tab",  # show_invisibles_space_color
            "url",
            # jEdit tags.
            'comment1', 'comment2', 'comment3', 'comment4',
            # default, # exists, but never generated.
            'function',
            'keyword1', 'keyword2', 'keyword3', 'keyword4',
            'label', 'literal1', 'literal2', 'literal3', 'literal4',
            'markup', 'operator',
            'trailing_whitespace',
        ]
    #@+node:ekr.20170127142001.1: *3* BaseColorizer.updateSyntaxColorer & helpers
    # Note: these are used by unit tests.

    def updateSyntaxColorer(self, p: Position) -> None:
        """
        Scan for color directives in p and its ancestors.
        Return True unless an coloring is unambiguously disabled.
        Called from Leo's node-selection logic and from the colorizer.
        """
        if not p:  # This guard is required.
            return

        try:
            self.enabled = self.useSyntaxColoring(p)
            self.language = self.scanLanguageDirectives(p)
        except Exception:
            g.es_print('unexpected exception in updateSyntaxColorer')
            g.es_exception()
    #@+node:ekr.20170127142001.2: *4* BaseColorizer.scanLanguageDirectives
    def scanLanguageDirectives(self, p: Position) -> str:
        """Return language based on the directives in p's ancestors."""
        c = self.c
        language = c.getLanguage(p)
        return language or c.target_language
    #@+node:ekr.20170127142001.7: *4* BaseColorizer.useSyntaxColoring & helper
    def useSyntaxColoring(self, p: Position) -> bool:
        """True if syntax coloring is enabled in p."""
        #@verbatim
        # @nocolor-node only applies to p.
        d = self.findColorDirectives(p)
        if 'nocolor-node' in d:
            return False
        # Bug fix 2024/07/15: Examine p, then its parents.
        for p in p.self_and_parents():
            d = self.findColorDirectives(p)
            if 'killcolor' in d:
                #@verbatim
                # @killcolor anywhere disables coloring.
                return False
            # unambiguous @color enables coloring.
            if 'color' in d and 'nocolor' not in d:
                return True
            # Unambiguous @nocolor disables coloring.
            if 'nocolor' in d and 'color' not in d:
                return False
        return True
    #@+node:ekr.20170127142001.8: *5* BaseColorizer.findColorDirectives
    # Order is important: put longest matches first.
    color_directives_pat = re.compile(
        r'(^@color|^@killcolor|^@nocolor-node|^@nocolor)'
        , re.MULTILINE)

    def findColorDirectives(self, p: Position) -> dict[str, str]:
        """Return a dict with each color directive in p.b, without the leading '@'."""
        d: dict[str, str] = {}
        for m in self.color_directives_pat.finditer(p.b):
            word = m.group(0)[1:]
            d[word] = word
            if word == 'killcolor':
                break
        return d
    #@-others
#@+node:ekr.20110605121601.18569: ** class JEditColorizer(BaseColorizer)
class JEditColorizer(BaseColorizer):
    """
    This class colorizes p.b using Qt's QSyntaxHighlighter (qsh) class:
    https://doc.qt.io/qt-6/qsyntaxhighlighter.html

    Each commander creates a single instance of this class: c.frame.body.colorizer.

    Use Leo's `--tracing=coloring` command-line option to see this class in action.

    Issue #4158 links to the Theory of Operation for this class:
    https://github.com/leo-editor/leo-editor/issues/4158

    Do not *ever* change this class! Change mode files instead!
    """

    #@+others
    #@+node:ekr.20220317050804.1: *3*  jedit: Birth
    #@+node:ekr.20110605121601.18572: *4* jedit.__init__ & helpers
    def __init__(self, c: Cmdr, widget: QWidget) -> None:
        """Ctor for JEditColorizer class."""
        super().__init__(c, widget)

        # Create the highlighter. The default is NullObject.
        if isinstance(widget, QtWidgets.QTextEdit):
            self.highlighter = LeoHighlighter(c,
                colorizer=self,
                document=widget.document(),
            )

        # *Global* state data. This is not entirely correct, but it's not worth fixing.
        self.after_doc_language: str = None
        self.in_killcolor: bool = False

        # *Local* state data. Such state is harmless.
        self.delegate_stack: list[str] = []
        self.initialStateNumber = -1
        self.n2languageDict: dict[int, str] = {-1: c.target_language}
        self.mode: JEditModeDescriptor = None
        self.nested = False  # True: allow nested comments, etc.
        self.nested_level = 0  # Nesting level if self.nested is True.
        self.nextState = 1  # Don't use 0.
        self.restartDict: dict[int, Callable] = {}  # Keys are state numbers, values are restart functions.
        self.stateDict: dict[int, str] = {}  # Keys are state numbers, values state names.
        self.stateNameDict: dict[str, int] = {}  # Keys are state names, values are state numbers.

        # #2276: Set by init_section_delims.
        self.section_delim1 = '<<'
        self.section_delim2 = '>>'

        # Init common data...
        self.reloadSettings()
    #@+node:ekr.20110605121601.18580: *5* jedit.init
    def init(self) -> None:
        """
        Init the colorizer to match self.language.

        The caller must set or clear state after calling this method.
        """
        # Init the *per-language* initial state number.
        self.initialStateNumber = self.setInitialStateNumber()

        # Init mode-related ivars.
        self.init_mode(self.language)

        # Support per-language @font/@color settings.
        self.init_section_delims()  # #2276
    #@+node:ekr.20170201082248.1: *5* jedit.init_all_state
    def init_all_state(self) -> None:
        """Completely init all state data."""
        assert self.language, g.callers(8)

        # Only jedit.recolor shouuld ever call this method.
        # However, one unit test calls this method.
        if g.callers(1) != 'recolor' and not g.unitTesting:
            message = f"jedit.init_all_state: invalid caller: {g.callers()}"
            g.print_unique_message(message)

        self.n2languageDict = {-1: self.language}
        self.nextState = 1  # Don't use 0.
        self.restartDict = {}
        self.stateDict = {}
        self.stateNameDict = {}
        self.in_killcolor = False
    #@+node:ekr.20211029073553.1: *5* jedit.init_section_delims
    def init_section_delims(self) -> None:

        p = self.c.p

        def find_delims(v: VNode) -> Optional[re.Match]:
            for s in g.splitLines(v.b):
                if m := g.g_section_delims_pat.match(s):
                    return m
            return None

        v = g.findAncestorVnodeByPredicate(p, v_predicate=find_delims)
        if v:
            m = find_delims(v)
            self.section_delim1 = m.group(1)
            self.section_delim2 = m.group(2)
        else:
            self.section_delim1 = '<<'
            self.section_delim2 = '>>'
    #@+node:ekr.20110605121601.18576: *4* jedit.addImportedRules
    def addImportedRules(self, mode: JEditModeDescriptor, rulesDict: dict[str, RuleSet], rulesetName: str) -> None:
        """Append any imported rules at the end of the rulesets specified in mode.importDict"""
        if self.importedRulesets.get(rulesetName):
            return
        self.importedRulesets[rulesetName] = True
        names = mode.importDict.get(rulesetName, []) if hasattr(mode, 'importDict') else []
        for name in names:
            savedModeDescriptor = self.mode
            ok = self.init_mode(name)
            if ok:
                rulesDict2 = self.rulesDict
                for key in rulesDict2.keys():
                    aList = self.rulesDict.get(key, [])
                    aList2 = rulesDict2.get(key)
                    if aList2:
                        # Don't add the standard rules again.
                        rules = [z for z in aList2 if z not in aList]
                        if rules:
                            aList.extend(rules)
                            self.rulesDict[key] = aList
            self.initModeFromModeDescriptor(savedModeDescriptor)
    #@+node:ekr.20110605121601.18577: *4* jedit.addLeoRules
    def addLeoRules(self, theDict: dict[str, RuleSet]) -> None:
        """Put Leo-specific rules to theList."""
        table = [
            # Rules added at front are added in **reverse** order.
            # Debatable: Leo keywords override langauge keywords.
            ('@', self.match_leo_keywords, True),  # Called after all other Leo matchers.
            ('@', self.match_at_color, True),
            ('@', self.match_at_language, True),  # 2011/01/17
            ('@', self.match_at_nocolor, True),
            ('@', self.match_at_nocolor_node, True),
            ('@', self.match_at_killcolor, True),  # 2025/01/05: Match this *first*
            ('@', self.match_at_wrap, True),  # 2015/06/22
            ('@', self.match_doc_part, True),
            ('f', self.match_any_url, True),
            ('g', self.match_gnx, True),  # Leo 6.6.3.
            ('g', self.match_any_url, True),
            ('h', self.match_any_url, True),
            ('m', self.match_any_url, True),
            ('n', self.match_any_url, True),
            ('p', self.match_any_url, True),
            ('t', self.match_any_url, True),
            ('u', self.match_unl, True),
            ('w', self.match_any_url, True),
            ('<', self.match_section_ref, True),  # Called **first**.
            # Rules added at back are added in normal order.
            (' ', self.match_blanks, False),
            ('\t', self.match_tabs, False),
        ]
        if self.c.config.getBool("color-trailing-whitespace"):
            table += [
                (' ', self.match_trailing_ws, True),
                ('\t', self.match_trailing_ws, True),
            ]
        # Replace the bound method by an unbound method.
        for ch, rule, atFront, in table:
            rule = rule.__func__
            theList = theDict.get(ch, [])
            if rule not in theList:
                if atFront:
                    theList.insert(0, rule)
                else:
                    theList.append(rule)
                theDict[ch] = theList
    #@+node:ekr.20110605121601.18581: *4* jedit.init_mode & helpers
    def init_mode(self, name: str) -> bool:
        """Name may be a language name or a delegate name."""
        if not name:
            return False
        if name == 'latex':
            name = 'tex'  # #1088: use tex mode for both tex and latex.
        language, rulesetName = self.nameToRulesetName(name)
        mode_descriptor = self.modes.get(rulesetName)
        if mode_descriptor:
            if mode_descriptor.language == 'unknown-language':
                return False
            self.initModeFromModeDescriptor(mode_descriptor)
            self.language = language  # 2011/05/30
            return True
        # Don't try to import a non-existent language.
        path = g.os_path_join(g.app.loadDir, '..', 'modes')
        fn = g.os_path_join(path, f"{language}.py")
        if g.os_path_exists(fn):
            module = g.import_module(name=f"leo.modes.{language}")
            if module is None and g.unitTesting:  # Too intrusive otherwise.
                g.print_unique_message(f"Import failed! leo.modes.{language}")
        else:
            module = None
        return self.init_mode_from_module(name, module)
    #@+node:btheado.20131124162237.16303: *5* jedit.init_mode_from_module
    def init_mode_from_module(self, name: str, module: ModuleType) -> bool:
        """
        Name may be a language name or a delegate name.
        The mode file is a python module containing all
        coloring rule attributes for the mode.
        """
        language, rulesetName = self.nameToRulesetName(name)
        if not module:
            # Create a dummy mode descriptor to limit recursion.
            mode_descriptor = JEditModeDescriptor(
                attributesDict={},
                defaultColor=None,
                keywordsDict={},
                language='unknown-language',
                module=module,
                properties={},
                rulesDict={},
                rulesetName=rulesetName,
                word_chars=self.word_chars,  # 2011/05/21
            )
            self.mode = self.modes[language] = mode_descriptor
            self.rulesetName = rulesetName
            self.language = 'unknown-language'
            if g.unitTesting:  # Too intrusive otherwise.
                g.print_unique_message(
                    "{'\n'}jedit.init_mode_from_module: "
                    f"no mode file for {language!r}! {g.callers(8)}"
                )
            return False

        # A hack to give modes access to c.
        if hasattr(module, 'pre_init_mode'):
            module.pre_init_mode(self.c)
        self.language = language
        self.rulesetName = rulesetName
        self.properties = getattr(module, 'properties', None) or {}

        # #1334: Careful: getattr(module, ivar, {}) might be None!
        d: dict[object, dict] = getattr(module, 'keywordsDictDict', {}) or {}
        self.keywordsDict = d.get(rulesetName, {})
        self.setKeywords()
        d = getattr(module, 'attributesDictDict', {}) or {}
        self.attributesDict: dict[str, RuleSet] = d.get(rulesetName, {})
        self.setModeAttributes()
        d = getattr(module, 'rulesDictDict', {}) or {}
        self.rulesDict: dict[str, RuleSet] = d.get(rulesetName, {})
        self.addLeoRules(self.rulesDict)
        self.defaultColor = 'null'
        mode_descriptor = JEditModeDescriptor(
            attributesDict=self.attributesDict,
            defaultColor=self.defaultColor,
            keywordsDict=self.keywordsDict,
            language=self.language,
            module=module,
            properties=self.properties,
            rulesDict=self.rulesDict,
            rulesetName=self.rulesetName,
            word_chars=self.word_chars,  # 2011/05/21
        )
        self.mode = self.modes[rulesetName] = mode_descriptor

        # Do this after 'officially' initing the module, to limit recursion.
        self.addImportedRules(self.mode, self.rulesDict, rulesetName)
        self.updateDelimsTables()
        initialDelegate = self.properties.get('initialModeDelegate')
        if initialDelegate:
            # Replace the original mode by the delegate mode.
            self.init_mode(initialDelegate)
            language2, rulesetName2 = self.nameToRulesetName(initialDelegate)
            self.modes[rulesetName] = self.modes.get(rulesetName2)
            self.language = language2
        else:
            self.language = language
        return True
    #@+node:ekr.20110605121601.18582: *5* jedit.nameToRulesetName
    def nameToRulesetName(self, name: str) -> tuple[str, str]:
        """
        Compute language and rulesetName from name, which is either a language
        name or a delegate name.
        """
        if not name:
            return 'unknown-language', None
        # #1334. Lower-case the name, regardless of the spelling in @language.
        name = name.lower()
        i = name.find('::')
        if i == -1:
            # New in Leo 5.0: allow delegated language names.
            language = g.app.delegate_language_dict.get(name, name)
            rulesetName = f"{language}_main"
        else:
            language = name[:i]
            delegate_language = name[i + 2 :]
            rulesetName = self.munge(f"{language}_{delegate_language}")
        return language, rulesetName
    #@+node:ekr.20110605121601.18583: *5* jedit.setKeywords
    def setKeywords(self) -> None:
        """
        Initialize the keywords for the present language.

         Set self.word_chars ivar to string.letters + string.digits + '_'
         plus any other character appearing in any keyword.
         """
        # Add any new user keywords to leoKeywordsDict.
        d = self.keywordsDict
        keys = list(d.keys())
        for s in g.globalDirectiveList:
            key = '@' + s
            if key not in keys:
                d[key] = 'leokeyword'
        # Create a temporary chars list.  It will be converted to a dict later.
        chars = [z for z in string.ascii_letters + string.digits]
        chars.append('_')  # #2933.
        for key in list(d.keys()):
            for ch in key:
                if ch not in chars:
                    chars.append(g.checkUnicode(ch))
        # jEdit2Py now does this check, so this isn't really needed.
        # But it is needed for forth.py.
        for ch in (' ', '\t'):
            if ch in chars:
                # g.es_print('removing %s from word_chars' % (repr(ch)))
                chars.remove(ch)
        # Convert chars to a dict for faster access.
        self.word_chars: dict[str, str] = {}
        for z in chars:
            self.word_chars[z] = z
    #@+node:ekr.20110605121601.18584: *5* jedit.setModeAttributes
    def setModeAttributes(self) -> None:
        """
        Set the ivars from self.attributesDict,
        converting 'true'/'false' to True and False.
        """
        d = self.attributesDict
        aList = (
            ('default', 'null'),
            ('digit_re', ''),
            ('escape', ''),  # New in Leo 4.4.2.
            ('highlight_digits', True),
            ('ignore_case', True),
            ('no_word_sep', ''),
        )
        for key, default in aList:
            val = d.get(key, default)
            if val in ('true', 'True'):
                val = True
            if val in ('false', 'False'):
                val = False
            setattr(self, key, val)
    #@+node:ekr.20110605121601.18585: *5* jedit.initModeFromModeDescriptor
    def initModeFromModeDescriptor(self, mode_descriptor: JEditModeDescriptor) -> None:

        self.mode = mode_descriptor
        # Set the ivars.
        self.attributesDict = mode_descriptor.attributesDict
        self.setModeAttributes()
        self.defaultColor = mode_descriptor.defaultColor
        self.keywordsDict = mode_descriptor.keywordsDict
        self.language = mode_descriptor.language
        self.properties = mode_descriptor.properties
        self.rulesDict = mode_descriptor.rulesDict
        self.rulesetName = mode_descriptor.rulesetName
        self.word_chars = mode_descriptor.word_chars

    initModeFromBunch = initModeFromModeDescriptor
    #@+node:ekr.20110605121601.18586: *5* jedit.updateDelimsTables
    def updateDelimsTables(self) -> None:
        """Update g.app.language_delims_dict if no entry for the language exists."""
        d = self.properties
        lineComment = d.get('lineComment')
        startComment = d.get('commentStart')
        endComment = d.get('commentEnd')
        if lineComment and startComment and endComment:
            delims = f"{lineComment} {startComment} {endComment}"
        elif startComment and endComment:
            delims = f"{startComment} {endComment}"
        elif lineComment:
            delims = f"{lineComment}"
        else:
            delims = None
        if delims:
            d = g.app.language_delims_dict
            if not d.get(self.language):
                d[self.language] = delims
    #@+node:ekr.20110605121601.18587: *4* jedit.munge
    def munge(self, s: str) -> str:
        """Munge a mode name so that it is a valid python id."""
        valid = string.ascii_letters + string.digits + '_'
        return ''.join([ch.lower() if ch in valid else '_' for ch in s])
    #@+node:ekr.20170205055743.1: *4* jedit.set_wikiview_patterns
    def set_wikiview_patterns(self, leadins: list[str], patterns: list[re.Pattern]) -> None:
        """
        Init the colorizer so it will *skip* all patterns.
        The wikiview plugin calls this method.
        """
        d = self.rulesDict
        for leadins_list, pattern in zip(leadins, patterns):
            for ch in leadins_list:

                def wiki_rule(self: Self, s: str, i: int, pattern: re.Pattern = pattern) -> int:
                    """Bind pattern and leadin for jedit.match_wiki_pattern."""
                    return self.match_wiki_pattern(s, i, pattern)

                aList = d.get(ch, [])
                if wiki_rule not in aList:
                    aList.insert(0, wiki_rule)
                    d[ch] = aList
        self.rulesDict = d
    #@+node:ekr.20241116071343.1: *3* jedit.force_recolor
    def force_recolor(self) -> None:
        """jedit.force_recolor: A helper for Leo's 'recolor' command."""
        c = self.c
        p = c.p
        if not p:  # This guard is required.
            return

        # Only the 'recolor' command should call this method!
        if g.callers(1) != 'recolorCommand':
            message = f"jedit.force_recolor: invalid caller: {g.callers()}"
            g.print_unique_message(message)

        # Tell QSyntaxHighlighter to do a full recolor.
        g.es_print(f"recolor: `{p.h}`", color='blue')
        self.highlighter.rehighlight()
    #@+node:ekr.20110605121601.18638: *3* jedit.mainLoop
    tot_time = 0.0

    def mainLoop(self, state: int, s: str, i0: int, j: int) -> None:
        """
        Colorize a *single* line s[i:j] starting in state n.

        Except for traces, do not change this method in any way!

        Any substantial change would break all the pattern matchers!
        """
        # Do not remove this unit test!
        if not g.unitTesting and g.callers(1) not in ('recolor', 'colorRangeWithTag'):
            message = f"jedit.mainLoop: unexpected callers: {g.callers(6)}"
            g.print_unique_message(message)
        t1 = time.process_time()
        f = self.restartDict.get(state)
        i = f(s) if f else i0
        j = min(j, len(s))  # Required.
        while i < j:
            progress = i
            functions = self.rulesDict.get(s[i], [])
            for f in functions:
                n = f(self, s, i)
                if False and not g.unitTesting:
                    g.trace(f"i: {i} {f.__name__} => {n:2} {s!r}")
                if n is None:
                    g.trace('Can not happen: n is None', repr(f))
                    break
                elif n > 0:  # Success. The match has already been colored.
                    i += n
                    break
                elif n < 0:  # Total failure.
                    i += -n
                    break
                else:  # Partial failure: Do not break or change i!
                    pass
            else:
                i += 1
            assert i > progress
        # Don't even *think* about changing state here.
        self.tot_time += time.process_time() - t1
    #@+node:ekr.20110605121601.18640: *3* jedit.recolor & helpers
    def recolor(self, s: str) -> None:
        """
        jEdit.recolor: Recolor a *single* line, s.
        QSyntaxHighligher calls this method repeatedly and automatically.

        Don't even *think* about changing this method unless you
        understand *every word* of the Theory of Operation:
        https://github.com/leo-editor/leo-editor/issues/4158
        """
        trace = (False or 'coloring' in g.app.debug) and not g.unitTesting
        c = self.c
        p = self.c.p if c else None
        if not p:
            return

        # Do not remove this unit test!
        if g.callers(1) != 'highlightBlock':
            message = f"jedit.recolor: invalid caller: {g.callers()}"
            g.print_unique_message(message)

        self.recolorCount += 1
        prev_state = self.prevState()
        if prev_state == -1:
            self.updateSyntaxColorer(p)
            self.delegate_stack = []
            self.init_all_state()  # The only call to this method.
            self.init()
            self.state_number_cache_dict = {}
            state = self.initBlock0()
        else:
            state = prev_state  # Continue the previous state by default.

        self.setState(state)
        if self.in_killcolor:
            return

        # #4146: Update self.language from the *previous* state.
        self.language = self.stateNumberToLanguage(state)

        # #4146: Update the state, *without* disrupting restarters.
        self.init_mode(self.language)

        # Do not delete these traces!
        if trace:
            if prev_state == -1:
                print('')
                g.trace(f"New node: prev_state: {prev_state} p.h: {p.h}")
            if 0:  # Distracting.
                g.trace(
                    f"recolorCount: {self.recolorCount:<4} "
                    f"line: {self.currentBlockNumber():<4} "
                    f"state: {state}: {self.stateNumberToStateString(state):<10} "
                    f"s: {s!r}"
                )

        # mainLoop will do nothing if s is empty.
        if s:
            # Color the line even if colorizing is disabled.
            self.mainLoop(state, s, 0, len(s))
    #@+node:ekr.20170126100139.1: *4* jedit.initBlock0
    def initBlock0(self) -> int:
        """
        Init *local* ivars when handling block 0.
        This prevents endless recalculation of the proper default state.
        """
        if self.enabled:
            n = self.setInitialStateNumber()
        else:
            n = self.setRestart(self.restartNoColor)
        return n
    #@+node:ekr.20170126101049.1: *4* jedit.setInitialStateNumber
    def setInitialStateNumber(self) -> int:
        """
        Init the initialStateNumber ivar for clearState()
        This saves a lot of work.

        Called from init() and initBlock0.
        """
        state = self.languageToMode(self.language)
        n = self.stateNameToStateNumber(None, state)
        self.initialStateNumber = n
        self.blankStateNumber = self.stateNameToStateNumber(None, state + ';blank')
        return n
    #@+node:ekr.20170126103925.1: *4* jedit.languageToMode
    def languageToMode(self, name: str) -> str:
        """Return name of the mode file for the given language name."""
        if name:
            table = (
                ('markdown', 'md'),
                ('python', 'py'),
            )
            for pattern, s in table:
                name = name.replace(pattern, s)
            return name
        g.print_unique_message(f"jedit.languageToMode. Should not happen: {name!r} {g.callers()}")
        return 'no-language'
    #@+node:ekr.20241106195155.1: *4* jedit.traceRulesDict
    def traceRulesDict(self) -> None:
        """Trace jedit.rulesDict in a more readable form."""
        for key, value in self.rulesDict.items():
            names = [z.__name__ for z in value]
            len_names = sum(len(z) for z in names)
            if len_names > 50:
                print(f"{key!r:>4}: [")
                for name in names:
                    print(f"        {name}")
                print('      ]')
            else:
                print(f"{key!r:>4}: {[z.__name__ for z in value]}")
    #@+node:ekr.20110605121601.18589: *3* jedit:Pattern matchers
    #@+node:ekr.20110605121601.18590: *4*  About the pattern matchers
    #@@language rest
    #@+at
    # The following jEdit matcher methods return the length of the matched text if the
    # match succeeds, and zero otherwise. In most cases, these methods colorize all
    # the matched text.
    #
    # The following arguments affect matching:
    #
    # - at_line_start         True: sequence must start the line.
    # - at_whitespace_end     True: sequence must be first non-whitespace text of the line.
    # - at_word_start         True: sequence must start a word.
    # - hash_char             The first character that must match in a regular expression.
    # - no_escape:            True: ignore an 'end' string if it is preceded by
    #                         the ruleset's escape character.
    # - no_line_break         True: the match will not succeed across line breaks.
    # - no_word_break:        True: the match will not cross word breaks.
    #
    # The following arguments affect coloring when a match succeeds:
    #
    # - delegate              A ruleset name. The matched text will be colored recursively
    #                         by the indicated ruleset.
    # - exclude_match         If True, the actual text that matched will not be colored.
    # - kind                  The color tag to be applied to colored text.
    #@+node:ekr.20110605121601.18637: *4* jedit.colorRangeWithTag
    def colorRangeWithTag(self,
        s: str, i: int, j: int, tag: str, *, delegate: str = '', exclude_match: bool = False,
    ) -> None:
        """
        Pattern matchers call this helper to colorize the selected range.

        Mode files should not call this helper directly!
        """
        # setTag does most tracing.
        trace = 'coloring' in g.app.debug and not g.unitTesting
        if not self.inColorState():
            # Do *not* check x.flag here. It won't work.
            if trace:
                g.trace('not in color state')
            return
        self.delegate_name = delegate
        if delegate:
            self.push_delegate(delegate)
            state = self.currentState()
            self.mainLoop(state, s, i, j)
            self.pop_delegate()
        elif not exclude_match:
            self.setTag(tag, s, i, j)

        # Colorize UNL's, URL's, and GNX's *everywhere*.
        if tag != 'url':
            j = min(j, len(s))
            while i < j:
                ch = s[i].lower()
                if ch == 'g':
                    n = self.match_gnx(s, i)
                    if n > 0:
                        i += n
                        continue
                if ch == 'u':
                    n = self.match_unl(s, i)
                    if n > 0:
                        i += n
                        continue
                if ch in g.url_leadins:
                    n = self.match_any_url(s, i)
                    if n > 0:
                        i += n
                        continue
                i += 1
    #@+node:ekr.20110605121601.18591: *4* jedit.dump
    def dump(self, s: str) -> str:
        if s.find('\n') == -1:
            return s
        return '\n' + s + '\n'
    #@+node:ekr.20110605121601.18592: *4* jedit.Leo rule functions
    #@+node:ekr.20110605121601.18608: *5* jedit.match_any_url
    def match_any_url(self, s: str, i: int) -> int:
        """Like match_compiled_regexp, but with special case for trailing ')'"""
        # Called by the main colorizer loop and colorRangeWithTag.
        n = self.match_compiled_regexp_helper(s, i, g.url_regex)
        if n <= 0:
            return 0
        # Special case for trailing period.
        s2 = s[i : i + n]
        if s2.endswith('.'):
            n -= 1
            s2 = s[i : i + n]
        # Special case for trailing ')'
        if s2.endswith(')') and '(' not in s2:
            n -= 1
        j = i + n
        kind = 'url'
        self.colorRangeWithTag(s, i, j, kind)
        return n
    #@+node:ekr.20110605121601.18593: *5* jedit.match_at_color
    def match_at_color(self, s: str, i: int) -> int:

        # Only matches at start of line.
        if i == 0 and g.match_word(s, 0, '@color'):
            n = self.setRestart(self.restartColor)
            self.setState(n)  # Enable coloring of *this* line.
            # Now required. Sets state.
            self.colorRangeWithTag(s, 0, len('@color'), 'leokeyword')
            return len('@color')
        return 0
    #@+node:ekr.20170125140113.1: *6* jedit.restartColor
    def restartColor(self, s: str) -> int:
        """Change all lines up to the next color directive."""
        if g.match_word(s, 0, '@killcolor'):
            self.in_killcolor = True
            return -len(s)  # Continue to suppress coloring.
        if g.match_word(s, 0, '@nocolor-node'):
            self.setRestart(self.restartNoColorNode)
            return -len(s)  # Continue to suppress coloring.
        if g.match_word(s, 0, '@nocolor'):
            self.setRestart(self.restartNoColor)
            return -len(s)  # Continue to suppress coloring.
        n = self.setRestart(self.restartColor)
        self.setState(n)  # Enables coloring of *this* line.
        return 0  # Allow colorizing!
    #@+node:ekr.20110605121601.18597: *5* jedit.match_at_killcolor & restarter
    def match_at_killcolor(self, s: str, i: int) -> int:

        # Only matches at start of line.
        if i == 0 and g.match_word(s, i, '@killcolor'):
            self.in_killcolor = True
            return len(s) + 1  # Match everything.
        return 0
    #@+node:ekr.20110605121601.18594: *5* jedit.match_at_language
    def match_at_language(self, s: str, i: int) -> int:
        """Match Leo's @language directive."""
        trace = 'coloring' in g.app.debug and not g.unitTesting
        # Only matches at start of line.
        if i != 0:
            return 0
        if not g.match_word(s, i, '@language'):
            return 0
        old_name = self.language
        j = g.skip_ws(s, i + len('@language'))
        k = g.skip_c_id(s, j)
        name = s[j:k]
        ok = self.init_mode(name)
        if ok:
            self.language = name
            self.colorRangeWithTag(s, i, k, 'leokeyword')
            if name != old_name:
                # Init the stack.
                self.delegate_stack.append(self.language)
                # Solves the recoloring problem!
                n = self.setInitialStateNumber()
                self.setState(n)
        if trace:
            language_s = '???' if self.language == 'unknown-language' else self.language
            g.trace(f"{language_s:10} stack: {self.delegate_stack!r:15} {s}")
        return k - i

    #@+node:ekr.20110605121601.18595: *5* jedit.match_at_nocolor & restarter
    def match_at_nocolor(self, s: str, i: int) -> int:

        # Only matches at start of line.
        if i == 0 and not g.match(s, i, '@nocolor-') and g.match_word(s, i, '@nocolor'):
            self.setRestart(self.restartNoColor)
            return len(s)  # Match everything.
        return 0
    #@+node:ekr.20110605121601.18596: *6* jedit.restartNoColor
    def restartNoColor(self, s: str) -> int:

        if self.in_killcolor:
            return len(s) + 1  # Defensive
        if g.match_word(s, 0, '@color'):
            n = self.setRestart(self.restartColor)
            self.setState(n)  # Enables coloring of *this* line.
            self.colorRangeWithTag(s, 0, len('@color'), 'leokeyword')
            return len('@color')
        if g.match_word(s, 0, '@killcolor'):
            self.in_killcolor = True
            return len(s) + 1
        self.setRestart(self.restartNoColor)
        return len(s) + 1  # Match everything.
    #@+node:ekr.20110605121601.18599: *5* jedit.match_at_nocolor_node & restarter
    def match_at_nocolor_node(self, s: str, i: int) -> int:

        # Only matches at start of line.
        if i == 0 and g.match_word(s, i, '@nocolor-node'):
            self.setRestart(self.restartNoColorNode)
            return len(s)  # Match everything.
        return 0
    #@+node:ekr.20110605121601.18600: *6* jedit.restartNoColorNode
    def restartNoColorNode(self, s: str) -> int:
        self.setRestart(self.restartNoColorNode)
        return len(s) + 1
    #@+node:ekr.20150622072456.1: *5* jedit.match_at_wrap
    def match_at_wrap(self, s: str, i: int) -> int:
        """Match Leo's @wrap directive."""
        c = self.c
        # Only matches at start of line.
        seq = '@wrap'
        if i == 0 and g.match_word(s, i, seq):
            j = i + len(seq)
            k = g.skip_ws(s, j)
            self.colorRangeWithTag(s, i, k, 'leokeyword')
            c.frame.forceWrap(c.p)
            return k - i
        return 0
    #@+node:ekr.20110605121601.18601: *5* jedit.match_blanks
    def match_blanks(self, s: str, i: int) -> int:
        # Use Qt code to show invisibles.
        return 0
    #@+node:ekr.20110605121601.18602: *5* jedit.match_doc_part & restarter
    def match_doc_part(self, s: str, i: int) -> int:
        """
        Colorize Leo's @ and @ doc constructs.
        Matches only at the start of the line.
        """
        if self.language == 'cweb':
            # Let the cweb colorizer handle everything.
            return 0
        if i != 0:
            return 0
        if g.match_word(s, i, '@doc'):
            j = i + 4
        elif g.match(s, i, '@') and (i + 1 >= len(s) or s[i + 1] in (' ', '\t', '\n')):
            j = i + 1
        else:
            return 0
        c = self.c
        self.colorRangeWithTag(s, 0, j, 'leokeyword')
        # #4382: Always set after_doc_language.
        self.after_doc_language = self.language
        # New in Leo 5.5: optionally colorize doc parts using reStructuredText
        if c.config.getBool('color-doc-parts-as-rest'):
            # Switch languages.
            self.language = 'rest'
            self.init()
            self.clearState()
            # Restart.
            self.setRestart(self.restartDocPart)
            # Do *not* color the text here!
            return j
        self.clearState()
        self.setRestart(self.restartDocPart)
        self.colorRangeWithTag(s, j, len(s), 'docpart')
        return len(s)
    #@+node:ekr.20110605121601.18603: *6* jedit.restartDocPart
    def restartDocPart(self, s: str) -> int:
        """
        Restarter for @ and @ constructs.
        Continue until an @c, @code or @language at the start of the line.
        """
        for tag in ('@c', '@code', '@language'):
            if g.match_word(s, 0, tag):
                if tag == '@language':
                    return self.match_at_language(s, 0)
                j = len(tag)
                #@verbatim
                # @c or @code.
                self.colorRangeWithTag(s, 0, j, 'leokeyword')
                # Switch languages.
                self.language = self.after_doc_language
                if not self.language:
                    g.print_unique_message('no after_doc_language')
                    self.language = 'python'
                self.init()
                self.clearState()
                # Do not change after_doc_language.
                return j
        # Color the next line.
        self.setRestart(self.restartDocPart)
        if self.c.config.getBool('color-doc-parts-as-rest'):
            # Do *not* colorize the text here.
            return 0
        self.colorRangeWithTag(s, 0, len(s), 'docpart')
        return len(s)
    #@+node:ekr.20220704215504.1: *5* jedit.match_gnx
    def match_gnx(self, s: str, i: int) -> int:
        # Called by the main colorizer loop and colorRangeWithTag.
        return self.match_compiled_regexp(s, i, kind='url', regexp=g.gnx_regex)
    #@+node:ekr.20170204072452.1: *5* jedit.match_image
    image_url = re.compile(r'^\s*<\s*img\s+.*src=\"(.*)\".*>\s*$')

    def match_image(self, s: str, i: int) -> int:
        """Matcher for <img...>"""
        if m := self.image_url.match(s, i):
            self.image_src = src = m.group(1)
            j = len(src)
            doc = self.highlighter.document()
            block_n = self.currentBlockNumber()
            text_block = doc.findBlockByNumber(block_n)
            g.trace(f"block_n: {block_n:2} {s!r}")
            # How to get the cursor of the colorized line.
                # body = self.c.frame.body
                # s = body.wrapper.getAllText()
                # wrapper.delete(0, j)
                # cursor.insertHtml(src)
            g.trace(f"block text: {repr(text_block.text())}")
            return j
        return 0
    #@+node:ekr.20110605121601.18604: *5* jedit.match_leo_keywords
    def match_leo_keywords(self, s: str, i: int) -> int:
        """Succeed if s[i:] is a Leo keyword."""
        self.totalLeoKeywordsCalls += 1
        if s[i] != '@':
            return 0
        # fail if something besides whitespace precedes the word on the line.
        i2 = i - 1
        while i2 >= 0:
            ch = s[i2]
            if ch == '\n':
                break
            elif ch in (' ', '\t'):
                i2 -= 1
            else:
                return 0
        # Get the word as quickly as possible.
        j = i + 1
        while j < len(s) and s[j] in self.word_chars:
            j += 1
        word = s[i + 1 : j]  # entries in leoKeywordsDict do not start with '@'.
        if j < len(s) and s[j] not in (' ', '\t', '\n'):
            return 0  # Fail, but allow a rescan, as in objective_c.
        if self.leoKeywordsDict.get(word):
            kind = 'leokeyword'
            self.colorRangeWithTag(s, i, j, kind)
            result = j - i + 1  # Bug fix: skip the last character.
            return result
        # 2010/10/20: also check the keywords dict here.
        # This allows for objective_c keywords starting with '@'
        # This will not slow down Leo, because it is called
        # for things that look like Leo directives.
        word = '@' + word
        kind = self.keywordsDict.get(word)
        if kind:
            self.colorRangeWithTag(s, i, j, kind)
            return j - i
        # Bug fix: allow rescan.  Affects @language patch.
        return 0
    #@+node:ekr.20110605121601.18605: *5* jedit.match_section_ref
    def match_section_ref(self, s: str, i: int) -> int:
        p = self.c.p

        # Special case for @language patch: section references are not honored.
        if self.language == 'patch':
            return 0
        n1, n2 = len(self.section_delim1), len(self.section_delim2)
        if not g.match(s, i, self.section_delim1):
            return 0
        k = g.find_on_line(s, i + n1, self.section_delim2)
        if k == -1:
            return 0
        j = k + n2

        # Special case for @section-delims.
        if s.startswith('@section-delims'):
            self.colorRangeWithTag(s, i, i + n1, 'namebrackets')
            self.colorRangeWithTag(s, k, j, 'namebrackets')
            return j - i
        # An actual section reference.
        self.colorRangeWithTag(s, i, i + n1, 'namebrackets')
        ref = g.findReference(s[i:j], p)
        if ref:
            if self.use_hyperlinks:
                #@+<< set the hyperlink >>
                #@+node:ekr.20110605121601.18606: *6* << set the hyperlink >> (jedit)
                # Set the bindings to VNode callbacks.
                tagName = "hyper" + str(self.hyperCount)
                self.hyperCount += 1
                ref.tagName = tagName
                #@-<< set the hyperlink >>
            else:
                self.colorRangeWithTag(s, i + n1, k, 'link')
        else:
            self.colorRangeWithTag(s, i + n1, k, 'name')
        self.colorRangeWithTag(s, k, j, 'namebrackets')
        return j - i
    #@+node:ekr.20110605121601.18607: *5* jedit.match_tabs
    def match_tabs(self, s: str, i: int) -> int:
        # Use Qt code to show invisibles.
        return 0
    #@+node:tbrown.20170707150713.1: *5* jedit.match_trailing_ws
    def match_trailing_ws(self, s: str, i: int) -> int:
        """match trailing whitespace"""
        j = i
        n = len(s)
        while j < n and s[j] in ' \t':
            j += 1
        if j > i and j == n:
            self.colorRangeWithTag(s, i, j, 'trailing_whitespace')
            return j - i
        return 0
    #@+node:ekr.20170225103140.1: *5* jedit.match_unl
    def match_unl(self, s: str, i: int) -> int:
        # Called by the main colorizer loop and colorRangeWithTag.
        return self.match_compiled_regexp(s, i, kind='url', regexp=g.unl_regex)
    #@+node:ekr.20110605121601.18609: *4* jedit.match_compiled_regexp
    def match_compiled_regexp(self, s: str, i: int,
        *, kind: str,
        regexp: re.Pattern,
        delegate: str = '',
    ) -> int:
        """Succeed if the compiled regular expression regexp matches at s[i:]."""
        n = self.match_compiled_regexp_helper(s, i, regexp)
        if n > 0:
            j = i + n
            self.colorRangeWithTag(s, i, j, kind, delegate=delegate)
            return n
        return 0
    #@+node:ekr.20110605121601.18610: *5* jedit.match_compiled_regexp_helper
    def match_compiled_regexp_helper(self, s: str, i: int, regex: re.Pattern) -> int:
        """
        Return the length of the matching text if
        seq (a regular expression) matches the present position.
        """
        # Match succeeds or fails more quickly than search.
        self.match_obj = mo = regex.match(s, i)  # re_obj.search(s,i)
        if mo is None:
            return 0
        start, end = mo.start(), mo.end()
        if start != i:
            return 0
        return end - start
    #@+node:ekr.20110605121601.18611: *4* jedit.match_eol_span
    def match_eol_span(self, s: str, i: int,
        *,
        kind: str = None,
        seq: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
        exclude_match: bool = False,
    ) -> int:
        """Succeed if seq matches s[i:]"""
        if at_line_start and i != 0 and s[i - 1] != '\n':
            return 0
        if at_whitespace_end and i != g.skip_ws(s, 0):
            return 0
        if at_word_start and i > 0 and s[i - 1] in self.word_chars:
            return 0
        if (
            at_word_start
            and i + len(seq) + 1 < len(s)
            and s[i + len(seq)] in self.word_chars
        ):
            return 0
        # if g.match(s, i, seq):
        j = len(s)
        self.colorRangeWithTag(s, i, j, kind,
            delegate=delegate, exclude_match=exclude_match)
        return j  # (was j-1) With a delegate, this could clear state.
    #@+node:ekr.20110605121601.18612: *4* jedit.match_eol_span_regexp
    def match_eol_span_regexp(self, s: str, i: int,
        *,
        kind: str = '',
        regexp: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        delegate: str = '',
    ) -> int:
        """Succeed if the regular expression regex matches s[i:]."""
        if at_line_start and i != 0 and s[i - 1] != '\n':
            return 0
        if at_whitespace_end and i != g.skip_ws(s, 0):
            return 0
        n = self.match_regexp_helper(s, i, regexp)
        if n > 0:
            j = len(s)
            self.colorRangeWithTag(s, i, j, kind, delegate=delegate)
            return j - i
        return 0
    #@+node:ekr.20110605121601.18613: *4* jedit.match_everything
    # def match_everything (self,s,i,kind=None,delegate='',exclude_match=False):
        # """Match the entire rest of the string."""
        # j = len(s)
        # self.colorRangeWithTag(s,i,j,kind,delegate=delegate)
        # return j
    #@+node:ekr.20231209010844.1: *4* jedit.match_fstring & helper
    f_string_nesting_level = 0

    def match_fstring(self, s: str, i: int) -> int:
        """
        Match a python 3.12 f-string.

        Called only for python 3.12+.
        """
        # Fail quickly if possible.
        if i + 1 >= len(s):
            return 0

        # Make sure this is an f-string.
        if 'f' not in s[i : i + 2].lower():
            return 0

        # Find the opening string delim.
        j = 1 if s[i + 1] in 'rfRF' else 0
        delim_offset = i + j + 1
        if delim_offset >= len(s):
            return 0
        delim = s[delim_offset]
        if delim not in ('"', '"'):
            return 0

        # Init.
        self.f_string_nesting_level = 0
        if g.match(s, delim_offset, delim * 3):
            delim = delim * 3

        # print(f"  match_fstring i: {i:2} delim: {delim} s: {s}")

        # Similar to code for docstrings (match_span).
        start = delim_offset
        end = self.match_fstring_helper(s, start + len(delim), delim)
        if end == -1:
            return 0  # A real failure.

        # Color this line.
        self.colorRangeWithTag(s, start, end, tag='literal1')

        # Continue the f-string if necessary.
        if end > len(s):
            end = len(s) + 1

            def fstring_restarter(s: str) -> int:
                """Freeze the binding of delim"""
                return self.restart_fstring(s, delim)

            self.setRestart(fstring_restarter)

        return end - i  # Correct, whatever end is.
    #@+node:ekr.20231209015334.1: *5* jedit.match_fstring_helper
    def match_fstring_helper(self, s: str, i: int, delim: str) -> int:
        """
        s is an fstring (or its continuation) *without* the leadin characters and the opening delim.

        Return n >= 0 if s[i:] contains with a non-escaped delim at fstring-level 0.

        Return len(s) + 1 if the fstring should continue.
        """
        escape, escapes = '\\', 0
        level = self.f_string_nesting_level
        alt_delim = '"' if delim == "'" else "'"  # Works for triple delims.
        in_alt_delim, in_comment = False, False

        # Scan, incrementing escape count and f-string level.
        while i < len(s):
            progress = i
            if g.match(s, i, delim):
                if (escapes % 2) == 0 and level == 0 and not in_alt_delim:
                    return i + len(delim)
                i += len(delim)
                continue
            if g.match(s, i, alt_delim):
                in_alt_delim = not in_alt_delim
                i += 1
                continue
            if in_comment:
                i += 1
                continue
            ch = s[i]
            i += 1
            if ch == '#' and (escapes % 2) == 0 and not in_alt_delim:
                in_comment = True
            elif ch == escape:
                escapes += 1
            elif ch == '{':
                level += 1
            elif ch == '}':
                level -= 1
            else:
                escapes = 0
            assert progress < i, (i, s)

        # Continue scanning.
        self.f_string_nesting_level = level
        return len(s) + 1
    #@+node:ekr.20231209082830.1: *5* jedit.restart_fstring
    def restart_fstring(self, s: str, delim: str) -> int:
        """Remain in this state until 'delim' is seen."""
        i = 0
        j = self.match_fstring_helper(s, i, delim)
        j2 = len(s) + 1 if j == -1 else j
        self.colorRangeWithTag(s, i, j2, tag='literal1')

        # Restart if necessary.
        if j > len(s):

            def fstring_restarter(s: str) -> int:
                """Freeze the binding of delim."""
                return self.restart_fstring(s, delim)

            self.setRestart(fstring_restarter)

        else:
            self.clearState()
        return j  # Return the new i, *not* the length of the match.
    #@+node:ekr.20110605121601.18614: *4* jedit.match_keywords
    # This is a time-critical method.

    def match_keywords(self, s: str, i: int) -> int:
        """
        Succeed if s[i:] is a keyword.
        Returning -len(word) for failure greatly reduces the number of times this
        method is called.
        """
        self.totalKeywordsCalls += 1
        # We must be at the start of a word.
        if i > 0 and s[i - 1] in self.word_chars:
            return 0
        # Get the word as quickly as possible.
        j = i
        n = len(s)
        chars = self.word_chars
        # Special cases...
        if self.language in ('haskell', 'clojure'):
            chars["'"] = "'"
        if self.language == 'c':
            chars['_'] = '_'
        while j < n and s[j] in chars:
            j += 1
        word = s[i:j]
        # Fix part of #585: A kludge for css.
        if self.language == 'css' and word.endswith(':'):
            j -= 1
            word = word[:-1]
        if not word:
            g.trace(
                'can not happen',
                repr(s[i : max(j, i + 1)]),
                repr(s[i : i + 10]),
                g.callers(),
            )
            return 0
        if self.ignore_case:
            word = word.lower()
        kind = self.keywordsDict.get(word)
        if kind:
            self.colorRangeWithTag(s, i, j, kind)
            result = j - i
            return result
        return -len(word)  # An important new optimization.
    #@+node:ekr.20110605121601.18615: *4* jedit.match_line
    def match_line(self, s: str, i: int, *, kind: str = None) -> int:
        """Match the rest of the line."""
        j = g.skip_to_end_of_line(s, i)
        self.colorRangeWithTag(s, i, j, kind)
        return j - i
    #@+node:ekr.20190606201152.1: *4* jedit.match_lua_literal
    def match_lua_literal(self, s: str, i: int, *, kind: str) -> int:
        """Succeed if s[i:] is a lua literal. See #1175"""
        k = self.match_span(s, i, kind=kind, begin="[[", end="]]")
        if k not in (None, 0):
            return k
        if not g.match(s, i, '[='):
            return 0
        # Calculate begin and end, then just call match_span
        j = i + 2
        while g.match(s, j, '='):
            j += 1
        if not g.match(s, j, '['):
            return 0
        return self.match_span(s, i, kind=kind, begin=s[i:j], end=s[i + 1 : j] + ']')
    #@+node:ekr.20110605121601.18616: *4* jedit.match_mark_following & getNextToken
    def match_mark_following(self, s: str, i: int,
        *,
        kind: str = '',
        pattern: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        exclude_match: bool = False,
    ) -> int:
        """Succeed if s[i:] matches pattern."""
        if not self.allow_mark_prev:
            return 0
        if at_line_start and i != 0 and s[i - 1] != '\n':
            return 0
        if at_whitespace_end and i != g.skip_ws(s, 0):
            return 0
        if at_word_start and i > 0 and s[i - 1] in self.word_chars:
            return 0  # 7/5/2008
        if (
            at_word_start
            and i + len(pattern) + 1 < len(s)
            and s[i + len(pattern)] in self.word_chars
        ):
            return 0
        if g.match(s, i, pattern):
            j = i + len(pattern)
            # self.colorRangeWithTag(s,i,j,kind,exclude_match=exclude_match)
            k = self.getNextToken(s, j)
            # 2011/05/31: Do not match *anything* unless there is a token following.
            if k > j:
                self.colorRangeWithTag(s, i, j, kind, exclude_match=exclude_match)
                self.colorRangeWithTag(s, j, k, kind, exclude_match=False)
                j = k
                return j - i
        return 0
    #@+node:ekr.20110605121601.18617: *5* jedit.getNextToken
    def getNextToken(self, s: str, i: int) -> int:
        """
        Return the index of the end of the next token for match_mark_following.

        The jEdit docs are not clear about what a 'token' is, but experiments with jEdit
        show that token means a word, as defined by word_chars.
        """
        # 2011/05/31: Might we extend the concept of token?
        # If s[i] is not a word char, should we return just it?
        i0 = i
        while i < len(s) and s[i].isspace():
            i += 1
        i1 = i
        while i < len(s) and s[i] in self.word_chars:
            i += 1
        if i == i1:
            return i0
        return min(len(s), i)
    #@+node:ekr.20110605121601.18618: *4* jedit.match_mark_previous
    def match_mark_previous(self, s: str, i: int,
        *,
        kind: str = '',
        pattern: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        exclude_match: bool = False,
    ) -> int:
        """
        Return the length of a matched SEQ or 0 if no match.

        'at_line_start':    True: sequence must start the line.
        'at_whitespace_end':True: sequence must be first non-whitespace text of the line.
        'at_word_start':    True: sequence must start a word.
        """
        # This match was causing most of the syntax-color problems.
        return 0  # 2009/6/23
    #@+node:ekr.20230420052804.1: *4* jedit.match_plain_seq
    def match_plain_seq(self, s: str, i: int, *, kind: str, seq: str) -> int:
        """Matcher for plain sequence match at at s[i:]."""
        if not g.match(s, i, seq):
            return 0
        j = i + len(seq)
        self.colorRangeWithTag(s, i, j, kind)
        return len(seq)
    #@+node:ekr.20230420052841.1: *4* jedit.match_plain_span
    def match_plain_span(self, s: str, i: int,
        *,
        kind: str,
        begin: str,
        end: str,
    ) -> int:
        """Matcher for simple span at s[i:] with no delegate."""
        if not g.match(s, i, begin):
            return 0
        j = self.match_plain_span_helper(s, i + len(begin), end)
        if j == -1:
            return 0  # A real failure.

        # A hack to handle continued strings. Should work for most languages.
        # Prepend "dots" to the kind, as a flag to setTag.
        quotes = "'\""
        dots = (
            j > len(s)
            and begin in quotes
            and end in quotes
            and kind.startswith('literal')
            and self.language not in ('lisp', 'elisp', 'rust')
        )
        if dots:
            kind = 'dots' + kind
        j2 = j + len(end)
        self.colorRangeWithTag(s, i, j2, kind)
        j = j2

        # Don't recolor everything after continued strings.
        if j > len(s) and not dots:
            j = len(s) + 1

            def span(s: str) -> int:
                # Freeze all bindings.
                return self.restart_match_span(s, kind, begin=begin, end=end)

            self.setRestart(span,
                # These must be keyword args.
                delegate='',
                end=end,
                exclude_match=False,
                kind=kind,
                no_escape=False,
                no_line_break=False,
                no_word_break=False)
        return j - i  # Correct, whatever j is.
    #@+node:ekr.20230420055058.1: *5* jedit.match_plain_span_helper
    def match_plain_span_helper(self, s: str, i: int, pattern: str,
    ) -> int:
        """
        Return n >= 0 if s[i] ends with the 'end' string.
        """
        esc = self.escape
        while 1:
            j = s.find(pattern, i)
            if j == -1:
                # Match to end of text if not found and no_line_break is False
                return len(s) + 1
            if esc:
                # Only an odd number of escapes is a 'real' escape.
                escapes = 0
                k = 1
                while j - k >= 0 and s[j - k] == esc:
                    escapes += 1
                    k += 1
                if (escapes % 2) == 1:
                    assert s[j - 1] == esc
                    i += 1  # Advance past *one* escaped character.
                else:
                    return j
            else:
                return j
        # For pylint.
        return -1
    #@+node:ekr.20250109134131.1: *4* jedit.match_plain_eol_span
    def match_plain_eol_span(self, s: str, i: int, kind: str) -> int:
        """Colorizer s[i:]"""
        j = len(s)
        self.colorRangeWithTag(s, i, j, kind)
        return j
    #@+node:ekr.20110605121601.18619: *4* jedit.match_regexp_helper
    def match_regexp_helper(self, s: str, i: int, pattern: Union[str, re.Pattern]) -> int:
        """
        Return the length of the matching text if
        seq (a regular expression) matches the present position.
        """
        # Leo 6.7.6: Allow compiled regexes.
        if isinstance(pattern, str):
            try:
                flags = re.MULTILINE
                if self.ignore_case:
                    flags |= re.IGNORECASE
                # Suppress a FutureWarning: possible nested set.
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=FutureWarning)
                    re_obj = re.compile(pattern, flags)
            except Exception:
                # Do not call g.es here!
                g.trace(f"Invalid regular expression: {pattern:<30} {g.callers(2)}")
                return 0
        else:
            re_obj = pattern
        # Match succeeds or fails more quickly than search.
        self.match_obj = mo = re_obj.match(s, i)  # re_obj.search(s,i)
        if mo is None:
            return 0
        start, end = mo.start(), mo.end()
        if start != i:  # Bug fix 2007-12-18: no match at i
            return 0
        return end - start
    #@+node:ekr.20110605121601.18620: *4* jedit.match_seq
    def match_seq(self, s: str, i: int,
        *,
        kind: str = '',
        seq: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
    ) -> int:
        """Succeed if s[:] matches seq."""
        if at_line_start and i != 0 and s[i - 1] != '\n':
            j = i
        elif at_whitespace_end and i != g.skip_ws(s, 0):
            j = i
        elif at_word_start and i > 0 and s[i - 1] in self.word_chars:  # 7/5/2008
            j = i
        if at_word_start and i + len(
            seq) + 1 < len(s) and s[i + len(seq)] in self.word_chars:
            j = i  # 7/5/2008
        elif g.match(s, i, seq):
            j = i + len(seq)
            self.colorRangeWithTag(s, i, j, kind, delegate=delegate)
        else:
            j = i
        return j - i
    #@+node:ekr.20110605121601.18621: *4* jedit.match_seq_regexp
    def match_seq_regexp(self, s: str, i: int,
        *,
        kind: str = '',
        regexp: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
    ) -> int:
        """Succeed if the regular expression regexp matches at s[i:]."""
        if at_line_start and i != 0 and s[i - 1] != '\n':
            return 0
        if at_whitespace_end and i != g.skip_ws(s, 0):
            return 0
        if at_word_start and i > 0 and s[i - 1] in self.word_chars:
            return 0
        n = self.match_regexp_helper(s, i, regexp)
        j = i + n
        assert j - i == n
        self.colorRangeWithTag(s, i, j, kind, delegate=delegate)
        return j - i
    #@+node:ekr.20110605121601.18622: *4* jedit.match_span & helpers
    def match_span(self, s: str, i: int,
        *,
        kind: str,
        begin: str,
        end: str,
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
        exclude_match: bool = False,
        nested: bool = False,  # New in Leo 6.7.8.
        no_escape: bool = False,
        no_line_break: bool = False,
        no_word_break: bool = False,
    ) -> int:
        """Succeed if s[i:] starts with 'begin' and contains a following 'end'."""
        self.nested = nested
        self.nesting_level = -1
        if i >= len(s):
            return 0
        if at_line_start and i != 0 and s[i - 1] != '\n':
            return 0
        if at_whitespace_end and i != g.skip_ws(s, 0):
            return 0
        if at_word_start and i > 0 and s[i - 1] in self.word_chars:
            return 0
        if at_word_start and i + len(begin) + 1 < len(s) and s[i + len(begin)] in self.word_chars:
            return 0
        if not g.match(s, i, begin):
            return 0

        # We have matched the start of the span.
        j = self.match_span_helper(s, i + len(begin), begin, end,
            no_escape=no_escape,
            no_line_break=no_line_break,
            no_word_break=no_word_break,
        )
        if j == -1:
            return 0  # A real failure.

        # A hack to handle continued strings. Should work for most languages.
        # Prepend "dots" to the kind, as a flag to setTag.
        dots = (
            j > len(s)
            and begin in "'\""
            and end in "'\""
            and kind.startswith('literal')
        )

        # These language can continue strings over multiple lines.
        dots = dots and self.language not in ('lisp', 'elisp', 'rust', 'scheme')
        if dots:
            kind = 'dots' + kind
        # A match
        i2 = i + len(begin)
        j2 = j + len(end)
        if delegate:
            self.colorRangeWithTag(
                s, i, i2, kind, delegate=None, exclude_match=exclude_match)
            self.colorRangeWithTag(
                s, i2, j, kind, delegate=delegate, exclude_match=exclude_match)
            self.colorRangeWithTag(
                s, j, j2, kind, delegate=None, exclude_match=exclude_match)
        else:
            self.colorRangeWithTag(
                s, i, j2, kind, delegate=None, exclude_match=exclude_match)
        j = j2
        # New in Leo 5.5: don't recolor everything after continued strings.
        if j > len(s) and not dots:
            j = len(s) + 1

            def span(s: str) -> int:
                # Freeze all bindings.
                return self.restart_match_span(s, kind,
                    # Keyword args...
                    delegate=delegate,
                    begin=begin,
                    end=end,
                    exclude_match=exclude_match,
                    no_escape=no_escape,
                    no_line_break=no_line_break,
                    no_word_break=no_word_break,
                )

            self.setRestart(span,
                # These must be keyword args.
                delegate=delegate,
                end=end,
                exclude_match=exclude_match,
                kind=kind,
                no_escape=no_escape,
                no_line_break=no_line_break,
                no_word_break=no_word_break)
        return j - i  # Correct, whatever j is.
    #@+node:ekr.20110605121601.18623: *5* jedit.match_span_helper
    def match_span_helper(self,
        s: str,
        i: int,
        begin_pattern: str,
        end_pattern: str,
        *,
        no_escape: bool,
        no_line_break: bool,
        no_word_break: bool,
    ) -> int:
        """
        Return n >= 0 if s[i] ends with a non-escaped 'end' string.
        """
        esc = self.escape
        while 1:
            if self.nested:
                j = s.find(begin_pattern, i)
                if j > -1:
                    self.nesting_level += 1
                    i += len(begin_pattern)
                    continue
            j = s.find(end_pattern, i)
            if j == -1:
                # Match to end of text if not found and no_line_break is False
                if no_line_break:
                    return -1
                return len(s) + 1
            if self.nested:
                self.nesting_level -= 1
                if self.nesting_level > 0:
                    return -1
            if no_word_break and j > 0 and s[j - 1] in self.word_chars:
                return -1  # New in Leo 4.5.
            if no_line_break and '\n' in s[i:j]:
                return -1
            if esc and not no_escape:
                # Only an odd number of escapes is a 'real' escape.
                escapes = 0
                k = 1
                while j - k >= 0 and s[j - k] == esc:
                    escapes += 1
                    k += 1
                if (escapes % 2) == 1:
                    assert s[j - 1] == esc
                    # Advance past *one* escaped character.
                    i += 1
                else:
                    return j
            else:
                return j
        # For pylint.
        return -1
    #@+node:ekr.20110605121601.18624: *5* jedit.restart_match_span
    def restart_match_span(self, s: str, kind: str,
        *,
        begin: str,
        end: str,
        delegate: str = '',
        exclude_match: bool = False,
        no_escape: bool = False,
        no_line_break: bool = False,
        no_word_break: bool = False,
    ) -> int:
        """Remain in this state until 'end' is seen."""
        i = 0
        j = self.match_span_helper(s, i, begin, end,
            # Must be keyword arguments.
            no_escape=no_escape,
            no_line_break=no_line_break,
            no_word_break=no_word_break,
        )
        if j == -1:
            j2 = len(s) + 1
        elif j > len(s):
            j2 = j
        else:
            j2 = j + len(end)
        if delegate:
            self.colorRangeWithTag(s, i, j, kind,
                delegate=delegate, exclude_match=exclude_match)
            self.colorRangeWithTag(s, j, j2, kind,
                delegate=None, exclude_match=exclude_match)
        else:  # avoid having to merge ranges in addTagsToList.
            self.colorRangeWithTag(s, i, j2, kind,
                delegate=None, exclude_match=exclude_match)
        j = j2
        if j > len(s):

            def span(s: str) -> int:
                return self.restart_match_span(s, kind,
                    # Must be keyword arguments.
                    delegate=delegate,
                    begin=begin,
                    end=end,
                    exclude_match=exclude_match,
                    no_escape=no_escape,
                    no_line_break=no_line_break,
                    no_word_break=no_word_break,
                )

            self.setRestart(span,
                # Must be keyword arguments.
                delegate=delegate,
                end=end,
                kind=kind,
                no_escape=no_escape,
                no_line_break=no_line_break,
                no_word_break=no_word_break,
            )
        else:
            self.clearState()
        return j  # Return the new i, *not* the length of the match.
    #@+node:ekr.20110605121601.18625: *4* jedit.match_span_regexp
    def match_span_regexp(self, s: str, i: int,
        *,
        kind: str = '',
        begin: Union[re.Pattern, str] = '',
        end: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
        no_line_break: bool = False,
    ) -> int:
        """
        Succeed if s[i:] matches 'begin' a regex string or compiled regex.

        Callers should use regex features to limit the search.

        New in Leo 6.7.6:
        - The 'begin' arg may be compiled pattern (re.Pattern).
        - The 'end' arg is optional.
        """
        if at_line_start and i != 0 and s[i - 1] != '\n':
            return 0
        if at_whitespace_end and i != g.skip_ws(s, 0):
            return 0
        if at_word_start and i > 0 and s[i - 1] in self.word_chars:
            return 0
        if (
            isinstance(begin, str)
            and at_word_start
            and i + len(begin) + 1 < len(s)
            and s[i + len(begin)] in self.word_chars
        ):
            return 0  # 7/5/2008
        n = self.match_regexp_helper(s, i, begin)
        # We may have to allow $n here, in which case we must use a regex object?
        if n > 0:
            j = j2 = i + n
            if end:  # Leo 6.7.6.
                j2 = s.find(end, j)
                if j2 == -1:
                    return 0
            if self.escape:
                # Only an odd number of escapes is a 'real' escape.
                escapes = 0
                k = 1
                while j - k >= 0 and s[j - k] == self.escape:
                    escapes += 1
                    k += 1
                if (escapes % 2) == 1:
                    # An escaped end **aborts the entire match**:
                    # there is no way to 'restart' the regex.
                    return 0
            i2 = j2 - len(end)
            if delegate:
                self.colorRangeWithTag(s, i, j, kind)
                self.colorRangeWithTag(s, j, i2, kind, delegate=delegate)
                self.colorRangeWithTag(s, i2, j2, kind)
            else:  # avoid having to merge ranges in addTagsToList.
                self.colorRangeWithTag(s, i, j2, kind)
            return j2 - i
        return 0
    #@+node:ekr.20190623132338.1: *4* jedit.match_tex_backslash
    ascii_letters = re.compile(r'[a-zA-Z]+')

    def match_tex_backslash(self, s: str, i: int, *, kind: str) -> int:
        """
        Match the tex s[i:].

        (Conventional) macro names are a backslash followed by either:
        1. One or more ascii letters, or
        2. Exactly one character, of any kind.
        """
        if not g.unitTesting:
            assert s[i] == '\\'  # TestSyntax.slow_test_all_mode_files only tests signatures.
        if m := self.ascii_letters.match(s, i + 1):
            n = len(m.group(0))
            j = i + n + 1
        else:
            # Colorize the backslash plus exactly one more character.
            j = i + 2
        self.colorRangeWithTag(s, i, j, kind, delegate='')
        return j - i
    #@+node:ekr.20170205074106.1: *4* jedit.match_wiki_pattern
    def match_wiki_pattern(self, s: str, i: int, pattern: re.Pattern) -> int:
        """Show or hide a regex pattern managed by the wikiview plugin."""
        if m := pattern.match(s, i):
            n = len(m.group(0))
            self.colorRangeWithTag(s, i, i + n, 'url')
            return n
        return 0
    #@+node:ekr.20110605121601.18626: *4* jedit.match_word_and_regexp
    def match_word_and_regexp(self, s: str, i: int,
        *, kind1: str = '', word: str = '', kind2: str = '', pattern: str = '',
    ) -> int:
        """Succeed if s[i:] matches pattern."""
        # Only forth mode uses this matcher, so g.match is probably correct.
        if not g.match(s, i, word):
            return 0
        j = i + len(word)
        n = self.match_regexp_helper(s, j, pattern)
        if n == 0:
            return 0
        self.colorRangeWithTag(s, i, j, kind1)
        k = j + n
        self.colorRangeWithTag(s, j, k, kind2)
        return k - i
    #@+node:ekr.20241121030605.1: *4* jedit.pop_delegate
    def pop_delegate(self) -> None:
        """Pop the delegate stack amd restart the previous delegate."""
        trace = False  # 'coloring' in g.app.debug and not g.unitTesting

        if trace:
            print('')
            g.trace(repr(self.delegate_stack))
            print('')

        if not self.delegate_stack:
            # This is not an error.
            return

        # Switch to the previous language.
        old_language = self.delegate_stack.pop()
        self.init_mode(old_language)
        state_i = self.setInitialStateNumber()
        self.setState(state_i)
    #@+node:ekr.20241121024111.1: *4* jedit.push_delegate
    def push_delegate(self, new_language: str) -> None:
        """
        Push the old language on the delegate stack and switch to the new language.
        """
        trace = False  # 'coloring' in g.app.debug and not g.unitTesting

        if self.language == 'unknown-language':  # Defensive.
            old_language = new_language
        else:
            old_language = self.language
        self.language = new_language

        if not new_language:
            g.trace(f"Oops: no new language: {self.language} {g.callers()}")
            return

        if trace:
            print('')
            g.trace(f"{old_language} ==> {new_language} {self.delegate_stack}")
            print('')

        # Ignore redundant <style> or <script> elements.
        if not self.delegate_stack or self.delegate_stack[-1] != old_language:
            self.delegate_stack.append(old_language)

        # Switch to the new language.
        self.init_mode(new_language)
        state_i = self.setInitialStateNumber()
        self.setState(state_i)
    #@+node:ekr.20110605121601.18627: *4* jedit.skip_line
    def skip_line(self, s: str, i: int) -> int:
        if self.escape:
            escape = self.escape + '\n'
            n = len(escape)
            while i < len(s):
                j = g.skip_line(s, i)
                if not g.match(s, j - n, escape):
                    return j
                i = j
            return i
        # Include the newline so we don't get a flash at the end of the line.
        return g.skip_line(s, i)
    #@+node:ekr.20110605121601.18629: *3* jedit:State methods
    #@+node:ekr.20110605121601.18630: *4* jedit.clearState
    def clearState(self) -> int:
        """
        Create a *language-specific* default state.
        This properly forces a full recoloring when @language changes.
        """
        n = self.initialStateNumber
        self.setState(n)
        return n
    #@+node:ekr.20110605121601.18631: *4* jedit.computeState (uses self.language)
    def computeState(self, f: Callable, keys: KWargs) -> int:
        """
        Compute the state name associated with f and all the keys.
        Return a unique int n representing that state.
        """
        # Abbreviate arg names.
        d = {
            'delegate': '=>',
            'end': 'end',
            'at_line_start': 'start',
            'at_whitespace_end': 'ws-end',
            'exclude_match': '!match',
            'no_escape': '!esc',
            'no_line_break': '!lbrk',
            'no_word_break': '!wbrk',
        }
        result = [self.languageToMode(self.language)]
        if not self.rulesetName.endswith('_main'):
            result.append(self.rulesetName)
        if f:
            result.append(f.__name__)
        for key in sorted(keys):
            keyVal = keys.get(key)
            val = d.get(key)
            if val is None:
                val = keys.get(key)
                result.append(f"{key}={val}")
            elif keyVal is True:
                result.append(f"{val}")
            elif keyVal is False:
                pass
            elif keyVal not in (None, ''):
                result.append(f"{key}={keyVal}")
        state = ';'.join(result)
        table = (
            ('kind=', ''),
            ('literal', 'lit'),
        )
        for pattern, s in table:
            state = state.replace(pattern, s)
        n = self.stateNameToStateNumber(f, state)
        return n
    #@+node:ekr.20110605121601.18632: *4* jedit.getters & setters
    def currentBlockNumber(self) -> int:
        block = self.highlighter.currentBlock()
        return block.blockNumber() if block and block.isValid() else -1

    def currentState(self) -> int:
        return self.highlighter.currentBlockState()

    def prevState(self) -> int:
        return self.highlighter.previousBlockState()

    def setState(self, n: int) -> None:
        self.highlighter.setCurrentBlockState(n)
    #@+node:ekr.20170125141148.1: *4* jedit.inColorState
    def inColorState(self) -> bool:
        """True if the *current* state is enabled."""
        n = self.currentState()
        state = self.stateDict.get(n, 'no-state')
        enabled = (
            self.enabled  # 2024/11/12
            and not state.endswith('@nocolor')
            and not state.endswith('@nocolor-node')
            and not state.endswith('@killcolor'))
        return enabled
    #@+node:ekr.20110605121601.18633: *4* jedit.setRestart
    def setRestart(self, f: Callable, **keys: KWargs) -> int:

        n = self.computeState(f, keys)
        self.setState(n)
        return n
    #@+node:ekr.20110605121601.18635: *4* jedit.show...
    def showState(self, n: int) -> str:
        state = self.stateDict.get(n, 'no-state')
        return f"{n:2}:{state}"

    def showCurrentState(self) -> str:
        n = self.currentState()
        return self.showState(n)

    def showPrevState(self) -> str:
        n = self.prevState()
        return self.showState(n)
    #@+node:ekr.20110605121601.18636: *4* jedit.stateNameToStateNumber
    def stateNameToStateNumber(self, f: Callable, stateName: str) -> int:
        """
        Update the following ivars when seeing stateName for the first time:

        stateDict:     Keys are state numbers, values state names.
        stateNameDict: Keys are state names, values are state numbers.
        restartDict:   Keys are state numbers, values are restart functions
        """
        # Make sure nobody calls this method by accident.
        if g.callers(1) not in ('computeState', 'setInitialStateNumber'):
            message = f"jedit.stateNameToStateNumber: invalid caller: {g.callers()}"
            g.print_unique_message(message)

        n = self.stateNameDict.get(stateName)
        if n is None:
            n = self.nextState
            self.stateNameDict[stateName] = n
            self.stateDict[n] = stateName
            self.restartDict[n] = f
            self.nextState += 1
            self.n2languageDict[n] = self.language
        return n
    #@+node:ekr.20241106082615.1: *4* jedit.stateNumberToLanguage
    state_number_cache_dict: dict[int, str] = {}

    def stateNumberToLanguage(self, n: int) -> str:
        """
        Return the string state corresponding to the given integer state.
        """

        def default_language(n: int) -> str:
            # This optimization is crucial for large text.
            if n in self.state_number_cache_dict:
                return self.state_number_cache_dict.get(n)
            c = self.c
            p = c.p
            language = c.getLanguage(p)
            self.state_number_cache_dict[n] = language or c.target_language
            return language or c.target_language

        state_s = self.stateNumberToStateString(n)
        language = state_s.split(';')[0]
        d = {
            'py': 'python',
            'initial-state': default_language(n),
        }
        return d.get(language, language)
    #@+node:ekr.20241104162429.1: *4* jedit.stateNumberToStateString
    def stateNumberToStateString(self, n: int) -> str:
        """
        Return the string state corresponding to the given integer state.
        """
        return self.stateDict.get(n, 'initial-state')
    #@-others
#@+node:ekr.20250327040215.1: ** class JEditModeDescriptor
class JEditModeDescriptor:

    """A class fully describing a jEdit mode file."""

    def __init__(self, *,
        attributesDict: dict,
        defaultColor: str,
        keywordsDict: dict,
        language: str,
        module: ModuleType,  # For debugging.
        properties: dict,
        rulesDict: dict,
        rulesetName: str,
        word_chars: dict[str, str],
    ) -> None:
        self.attributesDict = attributesDict
        self.defaultColor = defaultColor
        self.keywordsDict = keywordsDict
        self.language = language
        self.module = module
        self.properties = properties
        self.rulesDict = rulesDict
        self.rulesetName = rulesetName
        self.word_chars = word_chars
#@+node:ekr.20110605121601.18565: ** class LeoHighlighter (QSyntaxHighlighter)
# Careful: we may be running from the bridge.

if QtGui:


    class LeoHighlighter(QtGui.QSyntaxHighlighter):
        """
        A subclass of QSyntaxHighlighter that overrides
        the highlightBlock and rehighlight methods.

        All actual syntax coloring is done in the highlighter class.

        Used by both the JeditColorizer and PygmentsColorizer classes.
        """
        # This is c.frame.body.colorizer.highlighter
        #@+others
        #@+node:ekr.20110605121601.18566: *3* leo_h.ctor (sets style)
        def __init__(self, c: Cmdr, colorizer: BaseColorizer, document: QtGui.QTextDocument) -> None:
            """ctor for LeoHighlighter class."""
            self.c = c
            self.colorizer = colorizer
            self.n_calls = 0
            # Alas, a QsciDocument is not a QTextDocument.
            assert isinstance(document, QtGui.QTextDocument), document
            self.leo_document = document
            super().__init__(document)
            self.reloadSettings()
        #@+node:ekr.20110605121601.18567: *3* leo_h.highlightBlock
        def highlightBlock(self, s: str) -> None:
            """ Called by QSyntaxHighlighter """
            self.n_calls += 1
            s = g.toUnicode(s)
            self.colorizer.recolor(s)  # Highlight just one line.
        #@+node:ekr.20190327052228.1: *3* leo_h.reloadSettings
        def reloadSettings(self) -> None:
            """Reload all reloadable settings."""
            c, document = self.c, self.leo_document
            if not pygments:
                return
            if not c.config.getBool('use-pygments', default=False):
                return
            # Init pygments ivars.
            self._brushes: dict = {}
            self._document = document
            self._formats: dict = {}
            self.colorizer.style_name = 'default'
            # Style gallery: https://help.farbox.com/pygments.html
            # Dark styles: fruity, monokai, native, vim
            # https://github.com/gthank/solarized-dark-pygments
            style_name = c.config.getString('pygments-style-name') or 'default'
            if not c.config.getBool('use-pygments-styles', default=True):
                return
            # Init pygments style.
            try:
                self.setStyle(style_name)
                # print('using %r pygments style in %r' % (style_name, c.shortFileName()))
            except Exception:
                print(f'pygments {style_name!r} style not found. Using "default" style')
                self.setStyle('default')
                style_name = 'default'
            self.colorizer.style_name = style_name
            assert self._style
        #@+node:ekr.20190320154014.1: *3* leo_h: From PygmentsHighlighter
        #
        # All code in this tree is based on PygmentsHighlighter.
        #
        # Copyright (c) Jupyter Development Team.
        # Distributed under the terms of the Modified BSD License.
        #@+others
        #@+node:ekr.20190320153605.1: *4* leo_h._get_format & helpers
        def _get_format(self, token: object) -> Optional[object]:
            """ Returns a QTextCharFormat for token or None.
            """
            if token in self._formats:
                return self._formats[token]
            if self._style is None:
                result = self._get_format_from_document(token, self._document)
            else:
                result = self._get_format_from_style(token, self._style)
            result = self._get_format_from_style(token, self._style)
            self._formats[token] = result
            return result
        #@+node:ekr.20190320162831.1: *5* pyg_h._get_format_from_document
        def _get_format_from_document(self, token: object, document: object) -> object:
            """ Returns a QTextCharFormat for token by
            """
            # Modified by EKR.
            # These lines cause unbounded recursion.
                # code, html = next(self._formatter._format_lines([(token, 'dummy')]))
                # self._document.setHtml(html)
            return QtGui.QTextCursor(self._document).charFormat()
        #@+node:ekr.20190320153716.1: *5* leo_h._get_format_from_style
        def _get_format_from_style(self, token: object, style: object) -> object:
            """ Returns a QTextCharFormat for token by reading a Pygments style.
            """
            result = QtGui.QTextCharFormat()

            # EKR: handle missing tokens.
            try:
                data = style.style_for_token(token).items()
            except KeyError as err:
                message = f"_get_format_from_style: {err!r}"
                g.print_unique_message(message)
                return result
            for key, value in data:
                if value:
                    if key == 'color':
                        result.setForeground(self._get_brush(value))
                    elif key == 'bgcolor':
                        result.setBackground(self._get_brush(value))
                    elif key == 'bold':
                        result.setFontWeight(Weight.Bold)
                    elif key == 'italic':
                        result.setFontItalic(True)
                    elif key == 'underline':
                        result.setUnderlineStyle(UnderlineStyle.SingleUnderline)
                    elif key == 'sans':
                        result.setFontStyleHint(Weight.SansSerif)
                    elif key == 'roman':
                        result.setFontStyleHint(Weight.Times)
                    elif key == 'mono':
                        result.setFontStyleHint(Weight.TypeWriter)
            return result
        #@+node:ekr.20190320153958.1: *4* leo_h.setStyle
        def setStyle(self, style: object) -> None:
            """ Sets the style to the specified Pygments style.
            """
            from pygments.styles import get_style_by_name

            if isinstance(style, str):
                style = get_style_by_name(style)
            self._style = style
            self._clear_caches()
        #@+node:ekr.20190320154604.1: *4* leo_h.clear_caches
        def _clear_caches(self) -> None:
            """ Clear caches for brushes and formats.
            """
            self._brushes = {}
            self._formats = {}
        #@+node:ekr.20190320154752.1: *4* leo_h._get_brush/color
        def _get_brush(self, color: str) -> QtGui.QBrush:
            """ Returns a brush for the color.
            """
            result = self._brushes.get(color)
            if result is None:
                qcolor = self._get_color(color)
                result = QtGui.QBrush(qcolor)
                self._brushes[color] = result
            return result

        def _get_color(self, color: str) -> QtGui.QColor:
            """ Returns a QColor built from a Pygments color string.
            """
            qcolor = QtGui.QColor()
            qcolor.setRgb(int(color[:2], base=16),
                          int(color[2:4], base=16),
                          int(color[4:6], base=16))
            return qcolor
        #@-others
        #@-others
#@+node:ekr.20140906095826.18717: ** class NullScintillaLexer (QsciLexerCustom)
if Qsci:


    class NullScintillaLexer(Qsci.QsciLexerCustom):
        """A do-nothing colorizer for Scintilla."""

        def __init__(self, c: Cmdr, parent: QWidget = None) -> None:
            super().__init__(parent)  # Init the pase class
            self.leo_c = c
            self.configure_lexer()

        def description(self, style: object) -> str:
            return 'NullScintillaLexer'

        def setStyling(self, length: int, style: object) -> None:
            g.trace('(NullScintillaLexer)', length, style)

        def styleText(self, start: int, end: int) -> None:
            """Style the text from start to end."""

        def configure_lexer(self) -> None:
            """Configure the QScintilla lexer."""
            # c = self.leo_c
            lexer = self
            font = QtGui.QFont("DejaVu Sans Mono", 14)
            lexer.setFont(font)
#@+node:ekr.20190319151826.1: ** class PygmentsColorizer(BaseColorizer)
class PygmentsColorizer(BaseColorizer):
    """
    This class adapts pygments tokens to QSyntaxHighlighter.
    """
    # This is c.frame.body.colorizer
    #@+others
    #@+node:ekr.20220317053040.1: *3*  pyg_c: Birth
    #@+node:ekr.20190319151826.3: *4* pyg_c.__init__
    def __init__(self, c: Cmdr, widget: QWidget) -> None:
        """Ctor for PygmentsColorizer class."""
        super().__init__(c, widget)
        # Create the highlighter. The default is NullObject.
        if isinstance(widget, QtWidgets.QTextEdit):
            self.highlighter = LeoHighlighter(c,
                colorizer=self,
                document=widget.document(),
            )
        # State unique to this class...
        self.color_enabled = self.enabled
        self.getDefaultFormat: Callable
        self.old_v: VNode = None
        # Monkey-patch g.isValidLanguage.
        g.isValidLanguage = self.pygments_isValidLanguage
        # Init common data...
        self.reloadSettings()
    #@+node:ekr.20190324063349.1: *4* pyg_c.format getters
    def getLegacyDefaultFormat(self) -> None:
        return None

    def getLegacyFormat(self, token: object, text: str) -> str:
        """Return a jEdit tag for the given pygments token."""
        # Tables and setTag assume lower-case.
        r = repr(token).lstrip('Token.').lstrip('Literal.').lower()
        if r == 'name':
            # Avoid a collision with existing Leo tag.
            r = 'name.pygments'
        return r

    def getPygmentsFormat(self, token: object, text: str) -> str:
        """Return a pygments format."""
        format = self.highlighter._formats.get(token)
        if not format:
            format = self.highlighter._get_format(token)
        return format
    #@+node:ekr.20190324064341.1: *4* pyg_c.format setters
    def setLegacyFormat(self, index: int, length: int, format: str, s: str) -> None:
        """Call the jEdit style setTag."""
        super().setTag(format, s, index, index + length)

    def setPygmentsFormat(self, index: int, length: int, format: str, s: str) -> None:
        """Call the base setTag to set the Qt format."""
        self.highlighter.setFormat(index, length, format)
    #@+node:ekr.20240716051511.1: *3* pyg_c.force_recolor
    def force_recolor(self) -> None:
        """
        Force a complete recolor. A hook for the 'recolor' command.
        """
        c = self.c
        p = c.p
        self.updateSyntaxColorer(p)
        self.color_enabled = self.enabled
        self.old_v = p.v  # Fix a major performance bug.
        self.init()
    #@+node:ekr.20220316200022.1: *3* pyg_c.pygments_isValidLanguage
    def pygments_isValidLanguage(self, language: str) -> bool:
        """
        A hack: we will monkey-patch g.isValidLanguage to be this method.

        Without this hack this class would have to define its own copy of the
        (complex!) c.getLanguage function.
        """
        lexer_name = 'python3' if language == 'python' else language
        try:
            import pygments.lexers as lexers
            lexers.get_lexer_by_name(lexer_name)
            return True
        except Exception:
            return False
    #@+node:ekr.20190324051704.1: *3* pyg_c.reloadSettings
    def reloadSettings(self) -> None:
        """Reload the base settings, plus pygments settings."""
        # Do basic inits.
        super().reloadSettings()
        # Bind methods.

        if self.use_pygments_styles:
            self.getDefaultFormat = QtGui.QTextCharFormat
            self.getFormat = self.getPygmentsFormat
            self.setFormat = self.setPygmentsFormat
        else:
            self.getDefaultFormat = self.getLegacyDefaultFormat
            self.getFormat = self.getLegacyFormat
            self.setFormat = self.setLegacyFormat
    #@+node:ekr.20190319151826.78: *3* pyg_c.mainLoop & helpers
    format_dict: dict[str, str] = {}  # Keys are repr(Token), values are formats.
    lexers_dict: dict[str, Lexer] = {}  # Keys are language names, values are instantiated, patched lexers.
    state_s_dict: dict[str, int] = {}  # Keys are strings, values are ints.
    state_n_dict: dict[int, str] = {}  # # Keys are ints, values are strings.
    state_index = 1  # Index of state number to be allocated.
    # For traces.
    last_v = None
    tot_time = 0.0

    def mainLoop(self, s: str) -> None:
        """Colorize a *single* line s"""
        if 'coloring' in g.app.debug:
            p = self.c and self.c.p
            if p and p.v != self.last_v:
                self.last_v = p.v
                g.trace(f"(pygments) NEW NODE: {p.h}\n")
        t1 = time.process_time()
        highlighter = self.highlighter
        #
        # First, set the *expected* lexer. It may change later.
        lexer = self.set_lexer()
        #
        # Restore the state.
        # Based on Jupyter code: (c) Jupyter Development Team.
        stack_ivar = '_saved_state_stack'
        prev_data = highlighter.currentBlock().previous().userData()
        if prev_data is not None:
            # New code by EKR. Restore the language if necessary.
            if self.language != prev_data.leo_language:
                # Change the language and the lexer!
                self.language = prev_data.leo_language
                lexer = self.set_lexer()
            setattr(lexer, stack_ivar, prev_data.syntax_stack)
        elif hasattr(lexer, stack_ivar):
            delattr(lexer, stack_ivar)
        #
        # The main loop. Warning: this can change self.language.
        index = 0
        for token, text in lexer.get_tokens(s):
            length = len(text)
            if self.color_enabled:
                format = self.getFormat(token, text)
            else:
                format = self.getDefaultFormat()
            self.setFormat(index, length, format, s)
            index += length
        #
        # Save the state.
        # Based on Jupyter code: (c) Jupyter Development Team.
        stack = getattr(lexer, stack_ivar, None)
        if stack:
            data = PygmentsBlockUserData(syntax_stack=stack, leo_language=self.language)
            highlighter.currentBlock().setUserData(data)
            # Clean up for the next go-round.
            delattr(lexer, stack_ivar)
        #
        # New code by EKR:
        # - Fixes a bug so multiline tokens work.
        # - State supports Leo's color directives.
        state_s = f"{self.language}; {self.color_enabled}: {stack!r}"
        state_n = self.state_s_dict.get(state_s)
        if state_n is None:
            state_n = self.state_index
            self.state_index += 1
            self.state_s_dict[state_s] = state_n
            self.state_n_dict[state_n] = state_s
        highlighter.setCurrentBlockState(state_n)
        self.tot_time += time.process_time() - t1
    #@+node:ekr.20190323045655.1: *4* pyg_c.at_color_callback
    def at_color_callback(self, lexer: object, match: re.Match) -> Generator:
        from pygments.token import Name, Text
        kind = match.group(0)
        self.color_enabled = kind == '@color'
        if self.color_enabled:
            yield match.start(), Name.Decorator, kind
        else:
            yield match.start(), Text, kind
    #@+node:ekr.20190323045735.1: *4* pyg_c.at_language_callback
    def at_language_callback(self, lexer: object, match: re.Match) -> Generator:
        """Colorize the name only if the language has a lexer."""
        from pygments.token import Name
        language = match.group(2)
        # #2484:  The language is known if there is a lexer for it.
        if self.pygments_isValidLanguage(language):
            self.language = language
            yield match.start(), Name.Decorator, match.group(0)
        else:
            # Color only the @language, indicating an unknown language.
            yield match.start(), Name.Decorator, match.group(1)
    #@+node:ekr.20190322082533.1: *4* pyg_c.get_lexer
    unknown_languages: list[str] = []

    def get_lexer(self, language: str) -> Lexer:
        """Return the lexer for self.language, creating it if necessary."""
        import pygments.lexers as lexers
        trace = 'coloring' in g.app.debug
        try:
            # #1520: always define lexer_language.
            lexer_name = 'python3' if language == 'python' else language
            lexer = lexers.get_lexer_by_name(lexer_name)
        except Exception:
            # One of the lexer's will not exist.
            if trace and language not in self.unknown_languages:
                self.unknown_languages.append(language)
                g.trace(f"\nno pygments lexer for {language!r}. Using python 3 lexer\n")
            lexer = lexers.Python3Lexer()  # pylint: disable=no-member
        return lexer
    #@+node:ekr.20190322094034.1: *4* pyg_c.patch_lexer
    def patch_lexer(self, language: str, lexer: Lexer) -> Lexer:

        from pygments.token import Comment
        from pygments.lexer import inherit

        class PatchedLexer(DelegatingLexer, lexer.__class__):  # type:ignore

            leo_sec_ref_pat = r'(?-m:\<\<(.*?)\>\>)'
            tokens = {
                'root': [
                    (r'^@(color|nocolor|killcolor)\b', self.at_color_callback),
                    (r'^(@language)\s+(\w+)', self.at_language_callback),
                    # Single-line, non-greedy match.
                    (leo_sec_ref_pat, self.section_ref_callback),
                    # Multi-line, non-greedy match.
                    (r'(^\s*@doc|@)(\s+|\n)(.|\n)*?^@c', Comment.Leo.DocPart),
                   inherit,
                ],
            }

            def __init__(self, **options: KWargs) -> None:
                super().__init__(PatchedLexer, lexer.__class__, **options)

        try:
            return PatchedLexer()
        except Exception:
            if 0:  # #3456: Suppress this error.
                g.trace(f"can not patch {language!r}")
                g.es_exception()
            return lexer
    #@+node:ekr.20190322133358.1: *4* pyg_c.section_ref_callback
    def section_ref_callback(self, lexer: Lexer, match: re.Match) -> Generator:
        """pygments callback for section references."""
        c = self.c
        from pygments.token import Comment, Name
        name, ref, start = match.group(1), match.group(0), match.start()
        found = g.findReference(ref, c.p)
        found_tok = Name.Entity if found else Name.Other
        yield match.start(), Comment, '<<'
        yield start + 2, found_tok, name
        yield start + 2 + len(name), Comment, '>>'
    #@+node:ekr.20190323064820.1: *4* pyg_c.set_lexer
    def set_lexer(self) -> Lexer:
        """Return the lexer for self.language."""
        if self.language == 'patch':
            self.language = 'diff'
        key = f"{self.language}:{id(self)}"
        lexer = self.lexers_dict.get(key)
        if not lexer:
            lexer = self.get_lexer(self.language)
            lexer = self.patch_lexer(self.language, lexer)
            self.lexers_dict[key] = lexer
        return lexer
    #@+node:ekr.20190319151826.79: *3* pyg_c.recolor
    def recolor(self, s: str) -> None:
        """
        PygmentsColorizer.recolor: Recolor a *single* line, s.
        QSyntaxHighligher calls this method repeatedly and automatically.
        """
        p = self.c.p
        self.recolorCount += 1
        if p.v != self.old_v:
            # Force a full recolor
            # sets self.language and self.enabled.
            self.updateSyntaxColorer(p)
            self.color_enabled = self.enabled
            self.old_v = p.v  # Fix a major performance bug.
            self.init()
            assert self.language
        if s is not None:
            # For pygments, we *must* call for all lines.
            self.mainLoop(s)
    #@-others
#@+node:ekr.20140906081909.18689: ** class QScintillaColorizer(BaseColorizer)
# This is c.frame.body.colorizer


class QScintillaColorizer(BaseColorizer):
    """A colorizer for a QsciScintilla widget."""
    #@+others
    #@+node:ekr.20140906081909.18709: *3* qsc.__init__ & reloadSettings
    def __init__(self, c: Cmdr, widget: QWidget) -> None:
        """Ctor for QScintillaColorizer. widget is a """
        super().__init__(c)
        self.count = 0  # For unit testing.
        self.colorCacheFlag = False
        self.error = False  # Set if there is an error in jeditColorizer.recolor
        self.flag = True  # Per-node enable/disable flag.
        self.full_recolor_count = 0  # For unit testing.
        self.language = 'python'  # set by scanLanguageDirectives.
        self.highlighter = None
        self.lexer: Lexer = None  # Set in changeLexer.
        widget.leo_colorizer = self
        # Define/configure various lexers.
        self.reloadSettings()
        self.nullLexer: Union[NullScintillaLexer, g.NullObject]
        if Qsci:
            self.lexersDict = self.makeLexersDict()
            self.nullLexer = NullScintillaLexer(c)
        else:
            self.lexersDict = {}
            self.nullLexer = g.NullObject()

    def reloadSettings(self) -> None:
        c = self.c
        self.enabled = c.config.getBool('use-syntax-coloring')
    #@+node:ekr.20170128141158.1: *3* qsc.scanColorDirectives (over-ride)
    def scanColorDirectives(self, p: Position) -> str:
        """
        Return language based on the directives in p's ancestors.
        Same as BaseColorizer.scanColorDirectives, except it also scans p.b.
        """
        c = self.c
        root = p.copy()
        for p in root.self_and_parents(copy=False):
            language = g.findFirstValidAtLanguageDirective(p.b)
            if language:
                return language
        #  Get the language from the nearest ancestor @<file> node.
        language = c.getLanguage(root)
        return language
    #@+node:ekr.20140906081909.18718: *3* qsc.changeLexer
    def changeLexer(self, language: str) -> None:
        """Set the lexer for the given language."""
        c = self.c
        wrapper = c.frame.body.wrapper
        w = wrapper.widget  # A Qsci.QsciSintilla object.
        self.lexer = self.lexersDict.get(language, self.nullLexer)
        w.setLexer(self.lexer)
    #@+node:ekr.20140906081909.18707: *3* qsc.colorize
    def colorize(self, p: Position, *, force: bool = False) -> None:
        """The main Scintilla colorizer entry point."""
        # It would be much better to use QSyntaxHighlighter.
        # Alas, a QSciDocument is not a QTextDocument.
        self.updateSyntaxColorer(p)
        self.changeLexer(self.language)
        # if self.NEW:
            # # Works, but QScintillaWrapper.tag_configuration is presently a do-nothing.
            # for s in g.splitLines(p.b):
                # self.jeditColorizer.recolor(s)
    #@+node:ekr.20140906095826.18721: *3* qsc.configure_lexer
    def configure_lexer(self, lexer: Lexer) -> None:
        """Configure the QScintilla lexer using @data qt-scintilla-styles."""
        c = self.c
        font = QtGui.QFont("DejaVu Sans Mono", 14)
        lexer.setFont(font)
        lexer.setEolFill(False, -1)
        if hasattr(lexer, 'setStringsOverNewlineAllowed'):
            lexer.setStringsOverNewlineAllowed(False)
        table: list[tuple[str, str]] = []
        aList = c.config.getData('qt-scintilla-styles')
        color: str
        style: str
        if aList:
            aList = [s.split(',') for s in aList]  # type:ignore
            for z in aList:
                if len(z) == 2:
                    color, style = z  # type:ignore
                    table.append((color.strip(), style.strip()),)
                else:
                    g.trace(f"entry: {z}")
        if not table:
            black = '#000000'
            firebrick3 = '#CD2626'
            leo_green = '#00aa00'
            # See http://pyqt.sourceforge.net/Docs/QScintilla2/classQsciLexerPython.html
            # for list of selector names.
            table = [
                # EKR's personal settings are reasonable defaults.
                (black, 'ClassName'),
                (firebrick3, 'Comment'),
                (leo_green, 'Decorator'),
                (leo_green, 'DoubleQuotedString'),
                (black, 'FunctionMethodName'),
                ('blue', 'Keyword'),
                (black, 'Number'),
                (leo_green, 'SingleQuotedString'),
                (leo_green, 'TripleSingleQuotedString'),
                (leo_green, 'TripleDoubleQuotedString'),
                (leo_green, 'UnclosedString'),
                # End of line where string is not closed
                # style.python.13=fore:#000000,$(font.monospace),back:#E0C0E0,eolfilled
            ]
        for color, style in table:
            if hasattr(lexer, style):
                style_number = getattr(lexer, style)
                try:
                    lexer.setColor(QtGui.QColor(color), style_number)
                except Exception:
                    g.trace('bad color', color)
            else:
                pass
                # Not an error. Not all lexers have all styles.
                    # g.trace('bad style: %s.%s' % (lexer.__class__.__name__, style))
    #@+node:ekr.20170128031840.1: *3* qsc.init
    def init(self) -> None:
        """QScintillaColorizer.init"""
        self.updateSyntaxColorer(self.c.p)
        self.changeLexer(self.language)
    #@+node:ekr.20170128133525.1: *3* qsc.makeLexersDict
    def makeLexersDict(self) -> dict[str, Lexer]:
        """Make a dictionary of Scintilla lexers, and configure each one."""
        c = self.c
        # g.printList(sorted(dir(Qsci)))
        parent = c.frame.body.wrapper.widget
        table = (
            # 'Asm', 'Erlang', 'Forth', 'Haskell',
            # 'LaTeX', 'Lisp', 'Markdown', 'Nsis', 'R',
            'Bash', 'Batch', 'CPP', 'CSS', 'CMake', 'CSharp', 'CoffeeScript',
            'D', 'Diff', 'Fortran', 'Fortran77', 'HTML',
            'Java', 'JavaScript', 'Lua', 'Makefile', 'Matlab',
            'Pascal', 'Perl', 'Python', 'PostScript', 'Properties',
            'Ruby', 'SQL', 'TCL', 'TeX', 'XML', 'YAML',
        )
        d: dict[str, Lexer] = {}
        for language_name in table:
            class_name = 'QsciLexer' + language_name
            lexer_class = getattr(Qsci, class_name, None)
            if lexer_class:
                lexer = lexer_class(parent=parent)  # pylint: disable=not-callable
                self.configure_lexer(lexer)
                d[language_name.lower()] = lexer
            elif 0:
                g.trace('no lexer for', class_name)
        return d
    #@-others
#@+node:ekr.20190320062618.1: ** Jupyter classes
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

if pygments:
    #@+others
    #@+node:ekr.20190320062624.2: *3* RegexLexer.get_tokens_unprocessed
    # Copyright (c) Jupyter Development Team.
    # Distributed under the terms of the Modified BSD License.

    def get_tokens_unprocessed(self: Any, text: str, stack: Sequence[str] = ('root',)) -> Generator:
        """
        Split ``text`` into (tokentype, text) pairs.

        Monkey patched to store the final stack on the object itself.

        The `text` parameter this gets passed is only the current line, so to
        highlight things like multiline strings correctly, we need to retrieve
        the state from the previous line (this is done in PygmentsHighlighter,
        below), and use it to continue processing the current line.
        """
        pos = 0
        tokendefs = self._tokens
        if hasattr(self, '_saved_state_stack'):
            statestack = list(self._saved_state_stack)
        else:
            statestack = list(stack)
        # Fix #1113...
        try:
            statetokens = tokendefs[statestack[-1]]
        except Exception:
            # g.es_exception()
            return
        while 1:
            for rexmatch, action, new_state in statetokens:
                if m := rexmatch(text, pos):
                    if action is not None:
                        # pylint: disable=unidiomatic-typecheck
                        # EKR: Why not use isinstance?
                        if type(action) is _TokenType:
                            yield pos, action, m.group()
                        else:
                            for item in action(self, m):
                                yield item
                    pos = m.end()
                    if new_state is not None:
                        # state transition
                        if isinstance(new_state, tuple):
                            for state in new_state:
                                if state == '#pop':
                                    statestack.pop()
                                elif state == '#push':
                                    statestack.append(statestack[-1])
                                else:
                                    statestack.append(state)
                        elif isinstance(new_state, int):
                            # pop
                            del statestack[new_state:]
                        elif new_state == '#push':
                            statestack.append(statestack[-1])
                        else:
                            assert False, f"wrong state def: {new_state!r}"  # noqa
                        statetokens = tokendefs[statestack[-1]]
                    break
            else:
                try:
                    if text[pos] == '\n':
                        # at EOL, reset state to "root"
                        pos += 1
                        statestack = ['root']
                        statetokens = tokendefs['root']
                        yield pos, Text, '\n'
                        continue
                    yield pos, Error, text[pos]
                    pos += 1
                except IndexError:
                    break
        self._saved_state_stack = list(statestack)

    # Monkeypatch!

    if pygments:
        RegexLexer.get_tokens_unprocessed = get_tokens_unprocessed
    #@+node:ekr.20190320062624.3: *3* class PygmentsBlockUserData(QTextBlockUserData)
    # Copyright (c) Jupyter Development Team.
    # Distributed under the terms of the Modified BSD License.

    if QtGui:


        class PygmentsBlockUserData(QtGui.QTextBlockUserData):
            """ Storage for the user data associated with each line."""

            syntax_stack = tuple('root')

            def __init__(self, **kwargs: KWargs) -> None:
                for key, value in kwargs.items():
                    setattr(self, key, value)
                super().__init__()

            def __repr__(self) -> str:
                attrs = ['syntax_stack']
                kwargs = ', '.join([
                    f"{attr}={getattr(self, attr)!r}"
                        for attr in attrs
                ])
                return f"PygmentsBlockUserData({kwargs})"
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
