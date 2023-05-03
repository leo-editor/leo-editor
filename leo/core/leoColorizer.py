#@+leo-ver=5-thin
#@+node:ekr.20140827092102.18574: * @file leoColorizer.py
"""All colorizing code for Leo."""

# Indicated code are copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

#@+<< leoColorizer imports >>
#@+node:ekr.20140827092102.18575: ** << leoColorizer imports >>
from __future__ import annotations
import re
import string
import time
from typing import Any, Callable, Dict, Generator, Sequence, List, Optional, Tuple, TYPE_CHECKING
#
# Third-part tools.
try:
    import pygments  # type:ignore
except ImportError:
    pygments = None  # type:ignore
#
# Leo imports...
from leo.core import leoGlobals as g

from leo.core.leoColor import leo_color_database
#
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
    Color = Any
    Font = Any
    Mode = g.Bunch
    RuleSet = Any
    Widget = Any
#@-<< leoColorizer annotations >>
#@+others
#@+node:ekr.20190323044524.1: ** function: make_colorizer
def make_colorizer(c: Cmdr, widget: Widget) -> Any:
    """Return an instance of JEditColorizer or PygmentsColorizer."""
    use_pygments = pygments and c.config.getBool('use-pygments', default=False)
    if use_pygments:
        return PygmentsColorizer(c, widget)
    return JEditColorizer(c, widget)
#@+node:ekr.20170127141855.1: ** class BaseColorizer
class BaseColorizer:
    """The base class for all Leo colorizers."""
    #@+others
    #@+node:ekr.20220317050513.1: *3*  BaseColorizer: birth
    #@+node:ekr.20190324044744.1: *4* BaseColorizer.__init__
    def __init__(self, c: Cmdr, widget: Widget = None) -> None:
        """ctor for BaseColorizer class."""
        # Copy args...
        self.c = c
        self.widget: Widget = widget
        if widget:  # #503: widget may be None during unit tests.
            widget.leo_colorizer = self
        # Configuration dicts...
        self.configDict: Dict[str, Any] = {}  # Keys are tags, values are colors (names or values).
        self.configUnderlineDict: Dict[str, bool] = {}  # Keys are tags, values are bools.
        # Common state ivars...
        self.enabled = False  # Per-node enable/disable flag set by updateSyntaxColorer.
        self.highlighter: Any = g.NullObject()  # May be overridden in subclass...
        self.language = 'python'  # set by scanLanguageDirectives.
        self.prev: Tuple[int, int, str] = None  # Used by setTag.
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
        self.new_fonts: Dict[str, Dict] = {}

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
            valid_languages = g.app.language_delims_dict.keys()
            valid_tags = self.default_font_dict.keys()
            for setting in sorted(c.config.settingsDict):
                gs = c.config.settingsDict.get(setting)
                if gs and gs.source:  # An @font setting.
                    m = setting_pat.match(gs.source)
                    if m:
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
    zoom_dict: Dict[str, int] = {}

    def create_font(self, key: str, setting_name: str) -> Any:
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
        default_size: str = c.config.defaultBodyFontSize
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
    def configure_hard_tab_width(self, font: Font) -> None:
        """
        Set the width of a hard tab.

        Qt does not appear to have the required methods. Indeed,
        https://stackoverflow.com/questions/13027091/how-to-override-tab-width-in-qt
        assumes that QTextEdit's have only a single font(!).

        This method probabably only works probably if the body text contains
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
            #
            # Used in Leo rules...
            # tag name      :( option name,                  default color),
            'blank'         :('show_invisibles_space_color', '#E5E5E5'), # gray90
            'docpart'       :('doc_part_color',              'red'),
            'leokeyword'    :('leo_keyword_color',           'blue'),
            'link'          :('section_name_color',          'red'),
            'name'          :('undefined_section_name_color','red'),
            'namebrackets'  :('section_name_brackets_color', 'blue'),
            'tab'           :('show_invisibles_tab_color',   '#CCCCCC'), # gray80
            'url'           :('url_color',                   'purple'),
            #
            # Pygments tags.  Non-default values are taken from 'default' style.
            #
            # Top-level...
            # tag name          :( option name,         default color),
            'error'             :('error',              '#FF0000'), # border
            'other'             :('other',              'white'),
            'punctuation'       :('punctuation',        'white'),
            'whitespace'        :('whitespace',         '#bbbbbb'),
            'xt'                :('xt',                 '#bbbbbb'),
            #
            # Comment...
            # tag name          :( option name,         default color),
            'comment'           :('comment',            '#408080'), # italic
            'comment.hashbang'  :('comment.hashbang',   '#408080'),
            'comment.multiline' :('comment.multiline',  '#408080'),
            'comment.special'   :('comment.special',    '#408080'),
            'comment.preproc'   :('comment.preproc',    '#BC7A00'), # noitalic
            'comment.single'    :('comment.single',     '#BC7A00'), # italic
            #
            # Generic...
            # tag name          :( option name,         default color),
            'generic'           :('generic',            '#A00000'),
            'generic.deleted'   :('generic.deleted',    '#A00000'),
            'generic.emph'      :('generic.emph',       '#000080'), # italic
            'generic.error'     :('generic.error',      '#FF0000'),
            'generic.heading'   :('generic.heading',    '#000080'), # bold
            'generic.inserted'  :('generic.inserted',   '#00A000'),
            'generic.output'    :('generic.output',     '#888'),
            'generic.prompt'    :('generic.prompt',     '#000080'), # bold
            'generic.strong'    :('generic.strong',     '#000080'), # bold
            'generic.subheading':('generic.subheading', '#800080'), # bold
            'generic.traceback' :('generic.traceback',  '#04D'),
            #
            # Keyword...
            # tag name              :( option name,             default color),
            'keyword'               :('keyword',                '#008000'), # bold
            'keyword.constant'      :('keyword.constant',       '#008000'),
            'keyword.declaration'   :('keyword.declaration',    '#008000'),
            'keyword.namespace'     :('keyword.namespace',      '#008000'),
            'keyword.pseudo'        :('keyword.pseudo',         '#008000'), # nobold
            'keyword.reserved'      :('keyword.reserved',       '#008000'),
            'keyword.type'          :('keyword.type',           '#B00040'),
            #
            # Literal...
            # tag name              :( option name,         default color),
            'literal'               :('literal',            'white'),
            'literal.date'          :('literal.date',       'white'),
            #
            # Name...
            # tag name              :( option name,         default color
            # 'name' defined below.
            'name.attribute'        :('name.attribute',     '#7D9029'), # bold
            'name.builtin'          :('name.builtin',       '#008000'),
            'name.builtin.pseudo'   :('name.builtin.pseudo','#008000'),
            'name.class'            :('name.class',         '#0000FF'), # bold
            'name.constant'         :('name.constant',      '#880000'),
            'name.decorator'        :('name.decorator',     '#AA22FF'),
            'name.entity'           :('name.entity',        '#999999'), # bold
            'name.exception'        :('name.exception',     '#D2413A'), # bold
            'name.function'         :('name.function',      '#0000FF'),
            'name.function.magic'   :('name.function.magic','#0000FF'),
            'name.label'            :('name.label',         '#A0A000'),
            'name.namespace'        :('name.namespace',     '#0000FF'), # bold
            'name.other'            :('name.other',         'red'),
            # A hack: getLegacyFormat returns name.pygments instead of name.
            'name.pygments'         :('name.pygments',      'white'),
            'name.tag'              :('name.tag',               '#008000'), # bold
            'name.variable'         :('name.variable',          '#19177C'),
            'name.variable.class'   :('name.variable.class',    '#19177C'),
            'name.variable.global'  :('name.variable.global',   '#19177C'),
            'name.variable.instance':('name.variable.instance', '#19177C'),
            'name.variable.magic'   :('name.variable.magic',    '#19177C'),
            #
            # Number...
            # tag name              :( option name,         default color
            'number'                :('number',             '#666666'),
            'number.bin'            :('number.bin',         '#666666'),
            'number.float'          :('number.float',       '#666666'),
            'number.hex'            :('number.hex',         '#666666'),
            'number.integer'        :('number.integer',     '#666666'),
            'number.integer.long'   :('number.integer.long','#666666'),
            'number.oct'            :('number.oct',         '#666666'),
            #
            # Operator...
            # tag name          :( option name,         default color
            # 'operator' defined below.
            'operator.word'     :('operator.Word',      '#AA22FF'), # bold
            #
            # String...
            # tag name          :( option name,         default color
            'string'            :('string',             '#BA2121'),
            'string.affix'      :('string.affix',       '#BA2121'),
            'string.backtick'   :('string.backtick',    '#BA2121'),
            'string.char'       :('string.char',        '#BA2121'),
            'string.delimiter'  :('string.delimiter',   '#BA2121'),
            'string.doc'        :('string.doc',         '#BA2121'), # italic
            'string.double'     :('string.double',      '#BA2121'),
            'string.escape'     :('string.escape',      '#BB6622'), # bold
            'string.heredoc'    :('string.heredoc',     '#BA2121'),
            'string.interpol'   :('string.interpol',    '#BB6688'), # bold
            'string.other'      :('string.other',       '#008000'),
            'string.regex'      :('string.regex',       '#BB6688'),
            'string.single'     :('string.single',      '#BA2121'),
            'string.symbol'     :('string.symbol',      '#19177C'),
            #
            # jEdit tags.
            # tag name  :( option name,     default color),
            'comment1'  :('comment1_color', 'red'),
            'comment2'  :('comment2_color', 'red'),
            'comment3'  :('comment3_color', 'red'),
            'comment4'  :('comment4_color', 'red'),
            'function'  :('function_color', 'black'),
            'keyword1'  :('keyword1_color', 'blue'),
            'keyword2'  :('keyword2_color', 'blue'),
            'keyword3'  :('keyword3_color', 'blue'),
            'keyword4'  :('keyword4_color', 'blue'),
            'keyword5'  :('keyword5_color', 'blue'),
            'label'     :('label_color',    'black'),
            'literal1'  :('literal1_color', '#00aa00'),
            'literal2'  :('literal2_color', '#00aa00'),
            'literal3'  :('literal3_color', '#00aa00'),
            'literal4'  :('literal4_color', '#00aa00'),
            'markup'    :('markup_color',   'red'),
            'null'      :('null_color',     None),  # 'black'
            'operator'  :('operator_color', 'black'),
            'trailing_whitespace': ('trailing_whitespace_color', '#808080'),
        }
    #@+node:ekr.20110605121601.18575: *4* BaseColorizer.defineDefaultFontDict
    #@@nobeautify

    def defineDefaultFontDict(self) -> None:

        self.default_font_dict = {
            #
            # Used in Leo rules...
            # tag name      : option name
            'blank'         :'show_invisibles_space_font', # 2011/10/24.
            'docpart'       :'doc_part_font',
            'leokeyword'    :'leo_keyword_font',
            'link'          :'section_name_font',
            'name'          :'undefined_section_name_font',
            'namebrackets'  :'section_name_brackets_font',
            'tab'           :'show_invisibles_tab_font', # 2011/10/24.
            'url'           :'url_font',
            #
            # Pygments tags (lower case)...
            # tag name          : option name
            "comment"           :'comment1_font',
            "comment.preproc"   :'comment2_font',
            "comment.single"    :'comment1_font',
            "error"             :'null_font',
            "generic.deleted"   :'literal4_font',
            "generic.emph"      :'literal4_font',
            "generic.error"     :'literal4_font',
            "generic.heading"   :'literal4_font',
            "generic.inserted"  :'literal4_font',
            "generic.output"    :'literal4_font',
            "generic.prompt"    :'literal4_font',
            "generic.strong"    :'literal4_font',
            "generic.subheading":'literal4_font',
            "generic.traceback" :'literal4_font',
            "keyword"           :'keyword1_font',
            "keyword.pseudo"    :'keyword2_font',
            "keyword.type"      :'keyword3_font',
            "name.attribute"    :'null_font',
            "name.builtin"      :'null_font',
            "name.class"        :'null_font',
            "name.constant"     :'null_font',
            "name.decorator"    :'null_font',
            "name.entity"       :'null_font',
            "name.exception"    :'null_font',
            "name.function"     :'null_font',
            "name.label"        :'null_font',
            "name.namespace"    :'null_font',
            "name.tag"          :'null_font',
            "name.variable"     :'null_font',
            "number"            :'null_font',
            "operator.word"     :'keyword4_font',
            "string"            :'literal1_font',
            "string.doc"        :'literal1_font',
            "string.escape"     :'literal1_font',
            "string.interpol"   :'literal1_font',
            "string.other"      :'literal1_font',
            "string.regex"      :'literal1_font',
            "string.single"     :'literal1_font',
            "string.symbol"     :'literal1_font',
            'xt'                :'text_font',
            "whitespace"        :'text_font',
            #
            # jEdit tags.
            # tag name     : option name
            'comment1'      :'comment1_font',
            'comment2'      :'comment2_font',
            'comment3'      :'comment3_font',
            'comment4'      :'comment4_font',
            # 'default'     :'default_font',
            'function'      :'function_font',
            'keyword1'      :'keyword1_font',
            'keyword2'      :'keyword2_font',
            'keyword3'      :'keyword3_font',
            'keyword4'      :'keyword4_font',
            'keyword5'      :'keyword5_font',
            'label'         :'label_font',
            'literal1'      :'literal1_font',
            'literal2'      :'literal2_font',
            'literal3'      :'literal3_font',
            'literal4'      :'literal4_font',
            'markup'        :'markup_font',
            # 'nocolor' This tag is used, but never generates code.
            'null'          :'null_font',
            'operator'      :'operator_font',
            'trailing_whitespace' :'trailing_whitespace_font',
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
        self.color_tags_list: List[str] = []
        self.showInvisibles      = getBool("show-invisibles-by-default")
        self.underline_undefined = getBool("underline-undefined-section-names")
        self.use_hyperlinks      = getBool("use-hyperlinks")
        self.use_pygments        = None # Set in report_changes.
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
    prev_use_pygments = None
    prev_use_styles = None
    prev_style = None

    def report_changes(self) -> None:
        """Report changes to pygments settings"""
        c = self.c
        use_pygments = c.config.getBool('use-pygments', default=False)
        if not use_pygments:  # 1696.
            return
        trace = 'coloring' in g.app.debug and not g.unitTesting
        if trace:
            g.es_print('\nreport changes...')

        def show(setting: str, val: str) -> None:
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
        show('@bool use-pytments-styles', self.use_pygments_styles)
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
    #@+node:ekr.20190324050727.1: *4* BaseColorizer.init_style_ivars
    def init_style_ivars(self) -> None:
        """Init Style data common to JEdit and Pygments colorizers."""
        # init() properly sets these for each language.
        self.actualColorDict: Dict[str, Color] = {}  # Used only by setTag.
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
        self.trace_leo_matches = False
        self.trace_match_flag = False
        # Profiling...
        self.recolorCount = 0  # Total calls to recolor
        self.stateCount = 0  # Total calls to setCurrentState
        self.totalStates = 0
        self.maxStateNumber = 0
        self.totalKeywordsCalls = 0
        self.totalLeoKeywordsCalls = 0
        # Mode data...
        self.importedRulesets: Dict[str, RuleSet] = {}
        self.prev = None  # The previous token.
        self.fonts: Dict[str, Font] = {}  # Keys are config names.  Values are actual fonts.
        self.keywords: Dict[str, int] = {}  # Keys are keywords, values are 0..5.
        self.modes: Dict[str, Mode] = {}  # Keys are languages, values are modes.
        self.mode: Mode = None  # The mode object for the present language.
        self.modeBunch: g.Bunch = None  # A bunch fully describing a mode.
        self.modeStack: List[Mode] = []
        self.rulesDict: Dict[str, Any] = {}
        # self.defineAndExtendForthWords()
        self.word_chars: Dict[str, str] = {}  # Inited by init_keywords().
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
    #@+node:ekr.20110605121601.18641: *3* BaseColorizer.setTag
    def setTag(self, tag: str, s: str, i: int, j: int) -> None:
        """Set the tag in the highlighter."""
        trace = 'coloring' in g.app.debug and not g.unitTesting
        full_tag = f"{self.language}.{tag}"
        default_tag = f"{tag}_font"  # See default_font_dict.
        font: Any = None  # Set below. Define here for report().

        def report(extra: str = None) -> None:
            """A superb trace. Don't remove it."""
            s2 = repr(s[i:j])
            if len(s2) > 20:
                s2 = repr(s[i : i + 17 - 2] + '...')
            delegate_s = f"{self.delegate_name}:" if self.delegate_name else ''
            font_s = id(font) if font else 'None'
            matcher_name = g.caller(3)
            print(
                f"setTag: {full_tag:32} {i:3} {j:3} {colorName:7} font: {font_s:<14} {s2:>22} "
                f"{self.rulesetName}:{delegate_s}{matcher_name}"
            )
            if extra:
                print(f"{' ':48} {extra}")

        self.n_setTag += 1
        if i == j:
            return
        if not tag.strip():
            return
        tag = tag.lower().strip()
        # A hack to allow continuation dots on any tag.
        dots = tag.startswith('dots')
        if dots:
            tag = tag[len('dots') :]
        # This color name should already be valid.
        d = self.configDict
        colorName = d.get(f"{self.language}.{tag}") or d.get(tag)
        if not colorName:
            return
        # New in Leo 5.8.1: allow symbolic color names here.
        #                   (All keys in leo_color_database are normalized.)
        colorName = self.normalize(colorName)
        colorName = leo_color_database.get(colorName, colorName)
        # Get the actual color.
        color = self.actualColorDict.get(colorName)
        if not color:
            color = QtGui.QColor(colorName)
            if color.isValid():
                self.actualColorDict[colorName] = color
            else:
                # Leo 6.7.2: This should never happen: configure_colors does a pre-check.
                report(extra='*** unknown color name')
                g.trace(full_tag, d.get(full_tag))
                g.trace(tag, d.get(tag))
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
            report()  # A superb trace.
        self.highlighter.setFormat(i, j - i, format)
    #@+node:ekr.20170127142001.1: *3* BaseColorizer.updateSyntaxColorer & helpers
    # Note: these are used by unit tests.

    def updateSyntaxColorer(self, p: Position) -> None:
        """
        Scan for color directives in p and its ancestors.
        Return True unless an coloring is unambiguously disabled.
        Called from Leo's node-selection logic and from the colorizer.
        """
        if p:  # This guard is required.
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
        language = g.getLanguageFromAncestorAtFileNode(p)
        return language or c.target_language
    #@+node:ekr.20170127142001.7: *4* BaseColorizer.useSyntaxColoring & helper
    def useSyntaxColoring(self, p: Position) -> bool:
        """True if p's parents enable coloring in p."""
        # Special cases for the selected node.
        d = self.findColorDirectives(p)
        if 'killcolor' in d:
            return False
        if 'nocolor-node' in d:
            return False
        # Now look at the parents.
        for p in p.parents():
            d = self.findColorDirectives(p)
            #@verbatim
            # @killcolor anywhere disables coloring.
            if 'killcolor' in d:
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

    def findColorDirectives(self, p: Position) -> Dict[str, str]:
        """Return a dict with each color directive in p.b, without the leading '@'."""
        d: Dict[str, str] = {}
        for m in self.color_directives_pat.finditer(p.b):
            word = m.group(0)[1:]
            d[word] = word
        return d
    #@-others
#@+node:ekr.20110605121601.18569: ** class JEditColorizer(BaseColorizer)
# This is c.frame.body.colorizer


class JEditColorizer(BaseColorizer):
    """
    The JEditColorizer class adapts jEdit pattern matchers for QSyntaxHighlighter.
    For full documentation, see:
    https://github.com/leo-editor/leo-editor/blob/master/leo/doc/colorizer.md
    """
    #@+others
    #@+node:ekr.20220317050804.1: *3*  jedit: Birth
    #@+node:ekr.20110605121601.18572: *4* jedit.__init__ & helpers
    def __init__(self, c: Cmdr, widget: Widget) -> None:
        """Ctor for JEditColorizer class."""
        super().__init__(c, widget)
        #
        # Create the highlighter. The default is NullObject.
        if isinstance(widget, QtWidgets.QTextEdit):
            self.highlighter = LeoHighlighter(c,
                colorizer=self,
                document=widget.document(),
            )
        #
        # State data used only by this class...
        self.after_doc_language: str = None
        self.initialStateNumber = -1
        self.old_v: VNode = None
        self.nextState = 1  # Dont use 0.
        self.n2languageDict: Dict[int, str] = {-1: c.target_language}
        self.prev: Tuple[int, int, str] = None
        self.restartDict: Dict[int, Callable] = {}  # Keys are state numbers, values are restart functions.
        self.stateDict: Dict[int, str] = {}  # Keys are state numbers, values state names.
        self.stateNameDict: Dict[str, int] = {}  # Keys are state names, values are state numbers.
        # #2276: Set by init_section_delims.
        self.section_delim1 = '<<'
        self.section_delim2 = '>>'
        #
        # Init common data...
        self.reloadSettings()
    #@+node:ekr.20110605121601.18580: *5* jedit.init
    def init(self) -> None:
        """Init the colorizer, but *not* state."""
        #
        # These *must* be recomputed.
        self.initialStateNumber = self.setInitialStateNumber()
        #
        # Fix #389. Do *not* change these.
            # self.nextState = 1 # Dont use 0.
            # self.stateDict = {}
            # self.stateNameDict = {}
            # self.restartDict = {}
        self.init_mode(self.language)
        self.clearState()
        # Used by matchers.
        self.prev = None
        # Must be done to support per-language @font/@color settings.
        self.init_section_delims()  # #2276
    #@+node:ekr.20170201082248.1: *5* jedit.init_all_state
    def init_all_state(self, v: VNode) -> None:
        """Completely init all state data."""
        assert self.language, g.callers(8)
        self.old_v = v
        self.n2languageDict = {-1: self.language}
        self.nextState = 1  # Dont use 0.
        self.restartDict = {}
        self.stateDict = {}
        self.stateNameDict = {}
    #@+node:ekr.20211029073553.1: *5* jedit.init_section_delims
    def init_section_delims(self) -> None:

        p = self.c.p

        def find_delims(v: VNode) -> Optional[re.Match]:
            for s in g.splitLines(v.b):
                m = g.g_section_delims_pat.match(s)
                if m:
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
    def addImportedRules(self, mode: Mode, rulesDict: Dict[str, Any], rulesetName: str) -> None:
        """Append any imported rules at the end of the rulesets specified in mode.importDict"""
        if self.importedRulesets.get(rulesetName):
            return
        self.importedRulesets[rulesetName] = True
        names = mode.importDict.get(rulesetName, []) if hasattr(mode, 'importDict') else []
        for name in names:
            savedBunch = self.modeBunch
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
            self.initModeFromBunch(savedBunch)
    #@+node:ekr.20110605121601.18577: *4* jedit.addLeoRules
    def addLeoRules(self, theDict: Dict[str, Any]) -> None:
        """Put Leo-specific rules to theList."""
        table = [
            # Rules added at front are added in **reverse** order.
            # Debatable: Leo keywords override langauge keywords.
            ('@', self.match_leo_keywords, True),  # Called after all other Leo matchers.
            ('@', self.match_at_color, True),
            ('@', self.match_at_killcolor, True),
            ('@', self.match_at_language, True),  # 2011/01/17
            ('@', self.match_at_nocolor, True),
            ('@', self.match_at_nocolor_node, True),
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
        bunch = self.modes.get(rulesetName)
        if bunch:
            if bunch.language == 'unknown-language':
                return False
            self.initModeFromBunch(bunch)
            self.language = language  # 2011/05/30
            return True
        # Don't try to import a non-existent language.
        path = g.os_path_join(g.app.loadDir, '..', 'modes')
        fn = g.os_path_join(path, f"{language}.py")
        if g.os_path_exists(fn):
            mode = g.import_module(name=f"leo.modes.{language}")
        else:
            mode = None
        return self.init_mode_from_module(name, mode)
    #@+node:btheado.20131124162237.16303: *5* jedit.init_mode_from_module
    def init_mode_from_module(self, name: str, mode: Mode) -> bool:
        """
        Name may be a language name or a delegate name.
        Mode is a python module or class containing all
        coloring rule attributes for the mode.
        """
        language, rulesetName = self.nameToRulesetName(name)
        if mode:
            # A hack to give modes/forth.py access to c.
            if hasattr(mode, 'pre_init_mode'):
                mode.pre_init_mode(self.c)
        else:
            # Create a dummy bunch to limit recursion.
            self.modes[language] = self.modeBunch = g.Bunch(
                attributesDict={},
                defaultColor=None,
                keywordsDict={},
                language='unknown-language',
                mode=mode,
                properties={},
                rulesDict={},
                rulesetName=rulesetName,
                word_chars=self.word_chars,  # 2011/05/21
            )
            self.rulesetName = rulesetName
            self.language = 'unknown-language'
            return False
        self.language = language
        self.rulesetName = rulesetName
        self.properties = getattr(mode, 'properties', None) or {}
        #
        # #1334: Careful: getattr(mode, ivar, {}) might be None!
        #
        d: Dict[Any, Any] = getattr(mode, 'keywordsDictDict', {}) or {}
        self.keywordsDict = d.get(rulesetName, {})
        self.setKeywords()
        d = getattr(mode, 'attributesDictDict', {}) or {}
        self.attributesDict: Dict[str, Any] = d.get(rulesetName, {})
        self.setModeAttributes()
        d = getattr(mode, 'rulesDictDict', {}) or {}
        self.rulesDict: Dict[str, Any] = d.get(rulesetName, {})
        self.addLeoRules(self.rulesDict)
        self.defaultColor = 'null'
        self.mode = mode
        self.modes[rulesetName] = self.modeBunch = g.Bunch(
            attributesDict=self.attributesDict,
            defaultColor=self.defaultColor,
            keywordsDict=self.keywordsDict,
            language=self.language,
            mode=self.mode,
            properties=self.properties,
            rulesDict=self.rulesDict,
            rulesetName=self.rulesetName,
            word_chars=self.word_chars,  # 2011/05/21
        )
        # Do this after 'officially' initing the mode, to limit recursion.
        self.addImportedRules(mode, self.rulesDict, rulesetName)
        self.updateDelimsTables()
        initialDelegate = self.properties.get('initialModeDelegate')
        if initialDelegate:
            # Replace the original mode by the delegate mode.
            self.init_mode(initialDelegate)
            language2, rulesetName2 = self.nameToRulesetName(initialDelegate)
            self.modes[rulesetName] = self.modes.get(rulesetName2)
            self.language = language2  # 2017/01/31
        else:
            self.language = language  # 2017/01/31
        # Complete the late replacements.
        self.modeBunch.language = self.language
        self.modes[rulesetName] = self.modeBunch
        return True
    #@+node:ekr.20110605121601.18582: *5* jedit.nameToRulesetName
    def nameToRulesetName(self, name: str) -> Tuple[str, str]:
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
        self.word_chars: Dict[str, str] = {}
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
    #@+node:ekr.20110605121601.18585: *5* jedit.initModeFromBunch
    def initModeFromBunch(self, bunch: Any) -> None:
        self.modeBunch = bunch
        self.attributesDict = bunch.attributesDict
        self.setModeAttributes()
        self.defaultColor = bunch.defaultColor
        self.keywordsDict = bunch.keywordsDict
        self.language = bunch.language
        self.mode = bunch.mode
        self.properties = bunch.properties
        self.rulesDict = bunch.rulesDict
        self.rulesetName = bunch.rulesetName
        self.word_chars = bunch.word_chars  # 2011/05/21
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
    def set_wikiview_patterns(self, leadins: List[str], patterns: List[re.Pattern]) -> None:
        """
        Init the colorizer so it will *skip* all patterns.
        The wikiview plugin calls this method.
        """
        d = self.rulesDict
        for leadins_list, pattern in zip(leadins, patterns):
            for ch in leadins_list:

                def wiki_rule(self: Any, s: str, i: int, pattern: re.Pattern = pattern) -> int:
                    """Bind pattern and leadin for jedit.match_wiki_pattern."""
                    return self.match_wiki_pattern(s, i, pattern)

                aList = d.get(ch, [])
                if wiki_rule not in aList:
                    aList.insert(0, wiki_rule)
                    d[ch] = aList
        self.rulesDict = d
    #@+node:ekr.20110605121601.18638: *3* jedit.mainLoop
    last_v = None
    tot_time = 0.0

    def mainLoop(self, n: int, s: str) -> None:
        """Colorize a *single* line s, starting in state n."""
        f = self.restartDict.get(n)
        if 'coloring' in g.app.debug:
            p = self.c and self.c.p
            if p and p.v != self.last_v:
                self.last_v = p.v
                g.trace(f"NEW NODE: {p.h}\n")
        t1 = time.process_time()
        i = f(s) if f else 0
        while i < len(s):
            progress = i
            functions = self.rulesDict.get(s[i], [])
            for f in functions:
                n = f(self, s, i)
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
        """
        p = self.c.p
        self.recolorCount += 1
        block_n = self.currentBlockNumber()
        n = self.prevState()
        if p.v == self.old_v:
            new_language = self.n2languageDict.get(n)
            if new_language != self.language:
                self.language = new_language
                self.init()
        else:
            self.updateSyntaxColorer(p)  # Force a full recolor
            assert self.language
            self.init_all_state(p.v)
            self.init()
        if block_n == 0:
            n = self.initBlock0()
        n = self.setState(n)  # Required.
        # Always color the line, even if colorizing is disabled.
        if s:
            self.mainLoop(n, s)
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
        state = self.languageTag(self.language)
        n = self.stateNameToStateNumber(None, state)
        self.initialStateNumber = n
        self.blankStateNumber = self.stateNameToStateNumber(None, state + ';blank')
        return n
    #@+node:ekr.20170126103925.1: *4* jedit.languageTag
    def languageTag(self, name: str) -> str:
        """
        Return the standardized form of the language name.
        Doing this consistently prevents subtle bugs.
        """
        if name:
            table = (
                ('markdown', 'md'),
                ('python', 'py'),
                ('javascript', 'js'),
            )
            for pattern, s in table:
                name = name.replace(pattern, s)
            return name
        return 'no-language'
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
        s: str, i: int, j: int, tag: str, delegate: str = '', exclude_match: bool = False,
    ) -> None:
        """
        Actually colorize the selected range.

        This is called whenever a pattern matcher succeed.
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
            self.modeStack.append(self.modeBunch)
            self.init_mode(delegate)
            while 0 <= i < j and i < len(s):
                progress = i
                assert j >= 0, j
                for f in self.rulesDict.get(s[i], []):
                    n = f(self, s, i)
                    if n is None:
                        g.trace('Can not happen: delegate matcher returns None')
                    elif n > 0:
                        i += n
                        break
                else:
                    # Use the default chars for everything else.
                    # Use the *delegate's* default characters if possible.
                    default_tag = self.attributesDict.get('default')
                    self.setTag(default_tag or tag, s, i, i + 1)
                    i += 1
                assert i > progress
            bunch = self.modeStack.pop()
            self.initModeFromBunch(bunch)
        elif not exclude_match:
            self.setTag(tag, s, i, j)
        if tag != 'url':
            # Allow UNL's, URL's, and GNX's *everywhere*.
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
        self.prev = (i, j, kind)
        self.trace_match(kind, s, i, j)
        return n
    #@+node:ekr.20110605121601.18593: *5* jedit.match_at_color
    def match_at_color(self, s: str, i: int) -> int:
        if self.trace_leo_matches:
            g.trace()
        # Only matches at start of line.
        if i == 0 and g.match_word(s, 0, '@color'):
            n = self.setRestart(self.restartColor)
            self.setState(n)  # Enable coloring of *this* line.
            # Now required. Sets state.
            self.colorRangeWithTag(s, 0, len('@color'), 'leokeyword')
            return len('@color')
        return 0
    #@+node:ekr.20170125140113.1: *6* restartColor
    def restartColor(self, s: str) -> int:
        """Change all lines up to the next color directive."""
        if g.match_word(s, 0, '@killcolor'):
            self.colorRangeWithTag(s, 0, len('@color'), 'leokeyword')
            self.setRestart(self.restartKillColor)
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
            self.setRestart(self.restartKillColor)
            return len(s)  # Match everything.
        return 0
    #@+node:ekr.20110605121601.18598: *6* jedit.restartKillColor
    def restartKillColor(self, s: str) -> int:
        self.setRestart(self.restartKillColor)
        return len(s) + 1
    #@+node:ekr.20110605121601.18594: *5* jedit.match_at_language
    def match_at_language(self, s: str, i: int) -> int:
        """Match Leo's @language directive."""
        # Only matches at start of line.
        if i != 0:
            return 0
        if g.match_word(s, i, '@language'):
            old_name = self.language
            j = g.skip_ws(s, i + len('@language'))
            k = g.skip_c_id(s, j)
            name = s[j:k]
            ok = self.init_mode(name)
            if ok:
                self.colorRangeWithTag(s, i, k, 'leokeyword')
                if name != old_name:
                    # Solves the recoloring problem!
                    n = self.setInitialStateNumber()
                    self.setState(n)
            return k - i
        return 0
    #@+node:ekr.20110605121601.18595: *5* jedit.match_at_nocolor & restarter
    def match_at_nocolor(self, s: str, i: int) -> int:

        if self.trace_leo_matches:
            g.trace(i, repr(s))
        # Only matches at start of line.
        if i == 0 and not g.match(s, i, '@nocolor-') and g.match_word(s, i, '@nocolor'):
            self.setRestart(self.restartNoColor)
            return len(s)  # Match everything.
        return 0
    #@+node:ekr.20110605121601.18596: *6* jedit.restartNoColor
    def restartNoColor(self, s: str) -> int:
        if self.trace_leo_matches:
            g.trace(repr(s))
        if g.match_word(s, 0, '@color'):
            n = self.setRestart(self.restartColor)
            self.setState(n)  # Enables coloring of *this* line.
            self.colorRangeWithTag(s, 0, len('@color'), 'leokeyword')
            return len('@color')
        self.setRestart(self.restartNoColor)
        return len(s)  # Match everything.
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
        # New in Leo 5.5: optionally colorize doc parts using reStructuredText
        if c.config.getBool('color-doc-parts-as-rest'):
            # Switch langauges.
            self.after_doc_language = self.language
            self.language = 'rest'
            self.clearState()
            self.init()
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
        Restarter for @ and @ contructs.
        Continue until an @c, @code or @language at the start of the line.
        """
        for tag in ('@c', '@code', '@language'):
            if g.match_word(s, 0, tag):
                if tag == '@language':
                    return self.match_at_language(s, 0)
                j = len(tag)
                self.colorRangeWithTag(s, 0, j, 'leokeyword')  # 'docpart')
                # Switch languages.
                self.language = self.after_doc_language
                self.clearState()
                self.init()
                self.after_doc_language = None
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
        m = self.image_url.match(s, i)
        if m:
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
            self.prev = (i, j, kind)
            result = j - i + 1  # Bug fix: skip the last character.
            self.trace_match(kind, s, i, j)
            return result
        # 2010/10/20: also check the keywords dict here.
        # This allows for objective_c keywords starting with '@'
        # This will not slow down Leo, because it is called
        # for things that look like Leo directives.
        word = '@' + word
        kind = self.keywordsDict.get(word)
        if kind:
            self.colorRangeWithTag(s, i, j, kind)
            self.prev = (i, j, kind)
            self.trace_match(kind, s, i, j)
            return j - i
        # Bug fix: allow rescan.  Affects @language patch.
        return 0
    #@+node:ekr.20110605121601.18605: *5* jedit.match_section_ref
    def match_section_ref(self, s: str, i: int) -> int:
        p = self.c.p
        if self.trace_leo_matches:
            g.trace(self.section_delim1, self.section_delim2, s)
        #
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
        # Old code...
            # if not self.showInvisibles:
                # return 0
            # if self.trace_leo_matches: g.trace()
            # j = i; n = len(s)
            # while j < n and s[j] == '\t':
                # j += 1
            # if j > i:
                # self.colorRangeWithTag(s, i, j, 'tab')
                # return j - i
            # return 0
    #@+node:tbrown.20170707150713.1: *5* jedit.match_tabs
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
    def match_compiled_regexp(self,
        s: str, i: int, kind: str, regexp: Any, delegate: str = '',
    ) -> int:
        """Succeed if the compiled regular expression regexp matches at s[i:]."""
        n = self.match_compiled_regexp_helper(s, i, regexp)
        if n > 0:
            j = i + n
            self.colorRangeWithTag(s, i, j, kind, delegate=delegate)
            self.prev = (i, j, kind)
            self.trace_match(kind, s, i, j)
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
    def match_eol_span(
        self,
        s: str,
        i: int,
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
        if at_word_start and i + len(
            seq) + 1 < len(s) and s[i + len(seq)] in self.word_chars:
            return 0
        if g.match(s, i, seq):
            j = len(s)
            self.colorRangeWithTag(
                s, i, j, kind, delegate=delegate, exclude_match=exclude_match)
            self.prev = (i, j, kind)
            self.trace_match(kind, s, i, j)
            return j  # (was j-1) With a delegate, this could clear state.
        return 0
    #@+node:ekr.20110605121601.18612: *4* jedit.match_eol_span_regexp
    def match_eol_span_regexp(
        self,
        s: str,
        i: int,
        kind: str = '',
        regexp: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
        exclude_match: bool = False,
    ) -> int:
        """Succeed if the regular expression regex matches s[i:]."""
        if at_line_start and i != 0 and s[i - 1] != '\n':
            return 0
        if at_whitespace_end and i != g.skip_ws(s, 0):
            return 0
        if at_word_start and i > 0 and s[i - 1] in self.word_chars:
            return 0  # 7/5/2008
        n = self.match_regexp_helper(s, i, regexp)
        if n > 0:
            j = len(s)
            self.colorRangeWithTag(
                s, i, j, kind, delegate=delegate, exclude_match=exclude_match)
            self.prev = (i, j, kind)
            self.trace_match(kind, s, i, j)
            return j - i
        return 0
    #@+node:ekr.20110605121601.18613: *4* jedit.match_everything
    # def match_everything (self,s,i,kind=None,delegate='',exclude_match=False):
        # """Match the entire rest of the string."""
        # j = len(s)
        # self.colorRangeWithTag(s,i,j,kind,delegate=delegate)
        # return j
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
            self.prev = (i, j, kind)
            result = j - i
            self.trace_match(kind, s, i, j)
            return result
        return -len(word)  # An important new optimization.
    #@+node:ekr.20110605121601.18615: *4* jedit.match_line
    def match_line(self,
        s: str, i: int, kind: str = None, delegate: str = '', exclude_match: bool = False,
    ) -> int:
        """Match the rest of the line."""
        j = g.skip_to_end_of_line(s, i)
        self.colorRangeWithTag(s, i, j, kind, delegate=delegate)
        return j - i
    #@+node:ekr.20190606201152.1: *4* jedit.match_lua_literal
    def match_lua_literal(self, s: str, i: int, kind: str) -> int:
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
    def match_mark_following(
        self,
        s: str,
        i: int,
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
                self.prev = (i, j, kind)
                self.trace_match(kind, s, i, j)
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
    def match_mark_previous(
        self,
        s: str,
        i: int,
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
    #@+node:ekr.20110605121601.18619: *4* jedit.match_regexp_helper
    def match_regexp_helper(self, s: str, i: int, pattern: str) -> int:
        """
        Return the length of the matching text if
        seq (a regular expression) matches the present position.
        """
        try:
            flags = re.MULTILINE
            if self.ignore_case:
                flags |= re.IGNORECASE
            re_obj = re.compile(pattern, flags)
        except Exception:
            # Do not call g.es here!
            g.trace(f"Invalid regular expression: {pattern}")
            return 0
        # Match succeeds or fails more quickly than search.
        self.match_obj = mo = re_obj.match(s, i)  # re_obj.search(s,i)
        if mo is None:
            return 0
        start, end = mo.start(), mo.end()
        if start != i:  # Bug fix 2007-12-18: no match at i
            return 0
        return end - start
    #@+node:ekr.20110605121601.18620: *4* jedit.match_seq
    def match_seq(
        self,
        s: str,
        i: int,
        kind: str = '',
        *,
        seq: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
    ) -> int:
        """Succeed if s[:] mathces seq."""
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
            self.prev = (i, j, kind)
            self.trace_match(kind, s, i, j)
        else:
            j = i
        return j - i
    #@+node:ekr.20110605121601.18621: *4* jedit.match_seq_regexp
    def match_seq_regexp(
        self,
        s: str,
        i: int,
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
        self.prev = (i, j, kind)
        self.trace_match(kind, s, i, j)
        return j - i
    #@+node:ekr.20110605121601.18622: *4* jedit.match_span & helpers
    def match_span(
        self,
        s: str,
        i: int,
        *,
        kind: str,
        begin: str,
        end: str,
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
        exclude_match: bool = False,
        no_escape: bool = False,
        no_line_break: bool = False,
        no_word_break: bool = False,
    ) -> int:
        """Succeed if s[i:] starts with 'begin' and contains a following 'end'."""
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
        j = self.match_span_helper(s, i + len(begin), end,
            no_escape=no_escape,
            no_line_break=no_line_break,
            no_word_break=no_word_break,
        )
        if j == -1:
            return 0  # A real failure.
        # A hack to handle continued strings. Should work for most languages.
        # Prepend "dots" to the kind, as a flag to setTag.
        dots = j > len(
            s) and begin in "'\"" and end in "'\"" and kind.startswith('literal')
        dots = dots and self.language not in ('lisp', 'elisp', 'rust')
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
        self.prev = (i, j, kind)
        self.trace_match(kind, s, i, j)
        # New in Leo 5.5: don't recolor everything after continued strings.
        if j > len(s) and not dots:
            j = len(s) + 1

            def span(s: str) -> int:
                # Note: bindings are frozen by this def.
                return self.restart_match_span(s, kind,
                    # Keyword args...
                    delegate=delegate,
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
        pattern: str,
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
            j = s.find(pattern, i)
            if j == -1:
                # Match to end of text if not found and no_line_break is False
                if no_line_break:
                    return -1
                return len(s) + 1
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
    def restart_match_span(
        self,
        s: str,
        kind: str,
        *,
        end: str,
        delegate: str = '',
        exclude_match: bool = False,
        no_escape: bool = False,
        no_line_break: bool = False,
        no_word_break: bool = False,
    ) -> int:
        """Remain in this state until 'end' is seen."""
        i = 0
        j = self.match_span_helper(s, i, end,
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
        self.trace_match(kind, s, i, j)
        if j > len(s):

            def span(s: str) -> int:
                return self.restart_match_span(s, kind,
                    # Must be kword arguments.
                    delegate=delegate,
                    end=end,
                    exclude_match=exclude_match,
                    no_escape=no_escape,
                    no_line_break=no_line_break,
                    no_word_break=no_word_break,
                )

            self.setRestart(span,
                # Must be kword arguments.
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
    def match_span_regexp(
        self,
        s: str,
        i: int,
        kind: str = '',
        begin: str = '',
        end: str = '',
        at_line_start: bool = False,
        at_whitespace_end: bool = False,
        at_word_start: bool = False,
        delegate: str = '',
        exclude_match: bool = False,
        no_escape: bool = False,
        no_line_break: bool = False,
        no_word_break: bool = False,
    ) -> int:
        """
        Succeed if s[i:] starts with 'begin' (a regular expression) and
        contains a following 'end'.
        """
        if at_line_start and i != 0 and s[i - 1] != '\n':
            return 0
        if at_whitespace_end and i != g.skip_ws(s, 0):
            return 0
        if at_word_start and i > 0 and s[i - 1] in self.word_chars:
            return 0  # 7/5/2008
        if (
            at_word_start
            and i + len(begin) + 1 < len(s)
            and s[i + len(begin)] in self.word_chars
        ):
            return 0  # 7/5/2008
        n = self.match_regexp_helper(s, i, begin)
        # We may have to allow $n here, in which case we must use a regex object?
        if n > 0:
            j = i + n
            j2 = s.find(end, j)
            if j2 == -1:
                return 0
            if self.escape and not no_escape:
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
                self.colorRangeWithTag(
                    s, i, j, kind, delegate=None, exclude_match=exclude_match)
                self.colorRangeWithTag(
                    s, j, i2, kind, delegate=delegate, exclude_match=False)
                self.colorRangeWithTag(
                    s, i2, j2, kind, delegate=None, exclude_match=exclude_match)
            else:  # avoid having to merge ranges in addTagsToList.
                self.colorRangeWithTag(
                    s, i, j2, kind, delegate=None, exclude_match=exclude_match)
            self.prev = (i, j, kind)
            self.trace_match(kind, s, i, j2)
            return j2 - i
        return 0
    #@+node:ekr.20190623132338.1: *4* jedit.match_tex_backslash
    ascii_letters = re.compile(r'[a-zA-Z]+')

    def match_tex_backslash(self, s: str, i: int, kind: str) -> int:
        """
        Match the tex s[i:].

        (Conventional) acro names are a backslashe followed by either:
        1. One or more ascii letters, or
        2. Exactly one character, of any kind.
        """
        assert s[i] == '\\'
        m = self.ascii_letters.match(s, i + 1)
        if m:
            n = len(m.group(0))
            j = i + n + 1
        else:
            # Colorize the backslash plus exactly one more character.
            j = i + 2
        self.colorRangeWithTag(s, i, j, kind, delegate='')
        self.prev = (i, j, kind)
        self.trace_match(kind, s, i, j)
        return j - i
    #@+node:ekr.20170205074106.1: *4* jedit.match_wiki_pattern
    def match_wiki_pattern(self, s: str, i: int, pattern: Any) -> int:
        """Show or hide a regex pattern managed by the wikiview plugin."""
        m = pattern.match(s, i)
        if m:
            n = len(m.group(0))
            self.colorRangeWithTag(s, i, i + n, 'url')
            return n
        return 0
    #@+node:ekr.20110605121601.18626: *4* jedit.match_word_and_regexp
    def match_word_and_regexp(
        self,
        s: str,
        i: int,
        kind1: str = '',
        word: str = '',
        kind2: str = '',
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
            return 0
        if (
            at_word_start
            and i + len(word) + 1 < len(s)
            and s[i + len(word)] in self.word_chars
        ):
            j = i
        if not g.match(s, i, word):
            return 0
        j = i + len(word)
        n = self.match_regexp_helper(s, j, pattern)
        if n == 0:
            return 0
        self.colorRangeWithTag(s, i, j, kind1, exclude_match=exclude_match)
        k = j + n
        self.colorRangeWithTag(s, j, k, kind2, exclude_match=False)
        self.prev = (j, k, kind2)
        self.trace_match(kind1, s, i, j)
        self.trace_match(kind2, s, j, k)
        return k - i
    #@+node:ekr.20230420052804.1: *4* jedit.match_plain_seq
    def match_plain_seq(self, s: str, i: int, *, kind: str, seq: str) -> int:
        """Matcher for plain sequence match at at s[i:]."""
        if not g.match(s, i, seq):
            return 0
        j = i + len(seq)
        self.colorRangeWithTag(s, i, j, kind)
        self.prev = (i, j, kind)
        self.trace_match(kind, s, i, j)
        return len(seq)
    #@+node:ekr.20230420052841.1: *4* jedit.match_plain_span
    def match_plain_span(self, s: str, i: int, kind: str, *, begin: str, end: str) -> int:
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
        self.prev = (i, j, kind)
        self.trace_match(kind, s, i, j)

        # Don't recolor everything after continued strings.
        if j > len(s) and not dots:
            j = len(s) + 1

            def span(s: str) -> int:
                # Note: bindings are frozen by this def.
                return self.restart_match_span(s, kind, end=end)

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
    #@+node:ekr.20110605121601.18628: *4* jedit.trace_match
    def trace_match(self, kind: str, s: str, i: int, j: int) -> None:

        if j != i and self.trace_match_flag:
            g.trace(kind, i, j, g.callers(2), self.dump(s[i:j]))
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
    #@+node:ekr.20110605121601.18631: *4* jedit.computeState
    def computeState(self, f: Any, keys: Any) -> int:
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
        result = [self.languageTag(self.language)]
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
        state = ';'.join(result).lower()
        table = (
            ('kind=', ''),
            ('literal', 'lit'),
            ('restart', '@'),
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

    def setState(self, n: int) -> int:
        self.highlighter.setCurrentBlockState(n)
        return n
    #@+node:ekr.20170125141148.1: *4* jedit.inColorState
    def inColorState(self) -> bool:
        """True if the *current* state is enabled."""
        n = self.currentState()
        state = self.stateDict.get(n, 'no-state')
        enabled = (
            not state.endswith('@nocolor') and
            not state.endswith('@nocolor-node') and
            not state.endswith('@killcolor'))
        return enabled
    #@+node:ekr.20110605121601.18633: *4* jedit.setRestart
    def setRestart(self, f: Any, **keys: Any) -> int:
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
    def stateNameToStateNumber(self, f: Any, stateName: Any) -> int:
        """
        stateDict:     Keys are state numbers, values state names.
        stateNameDict: Keys are state names, values are state numbers.
        restartDict:   Keys are state numbers, values are restart functions
        """
        n = self.stateNameDict.get(stateName)
        if n is None:
            n = self.nextState
            self.stateNameDict[stateName] = n
            self.stateDict[n] = stateName
            self.restartDict[n] = f
            self.nextState += 1
            self.n2languageDict[n] = self.language
        return n
    #@-others
#@+node:ekr.20110605121601.18565: ** class LeoHighlighter (QSyntaxHighlighter)
# Careful: we may be running from the bridge.

if QtGui:


    class LeoHighlighter(QtGui.QSyntaxHighlighter):  # type:ignore
        """
        A subclass of QSyntaxHighlighter that overrides
        the highlightBlock and rehighlight methods.

        All actual syntax coloring is done in the highlighter class.

        Used by both the JeditColorizer and PYgmentsColorizer classes.
        """
        # This is c.frame.body.colorizer.highlighter
        #@+others
        #@+node:ekr.20110605121601.18566: *3* leo_h.ctor (sets style)
        def __init__(self, c: Cmdr, colorizer: Any, document: Any) -> None:
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
            self._brushes = {}
            self._document = document
            self._formats = {}
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
        def _get_format(self, token: Any) -> Any:
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
        def _get_format_from_document(self, token: Any, document: Any) -> Any:
            """ Returns a QTextCharFormat for token by
            """
            # Modified by EKR.
            # These lines cause unbounded recursion.
                # code, html = next(self._formatter._format_lines([(token, u'dummy')]))
                # self._document.setHtml(html)
            return QtGui.QTextCursor(self._document).charFormat()
        #@+node:ekr.20190320153716.1: *5* leo_h._get_format_from_style
        key_error_d: Dict[str, bool] = {}

        def _get_format_from_style(self, token: Any, style: Any) -> Any:
            """ Returns a QTextCharFormat for token by reading a Pygments style.
            """
            result = QtGui.QTextCharFormat()
            #
            # EKR: handle missing tokens.
            try:
                data = style.style_for_token(token).items()
            except KeyError as err:
                key = repr(err)
                if key not in self.key_error_d:
                    self.key_error_d[key] = True
                    g.trace(err)
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
        def setStyle(self, style: Any) -> None:
            """ Sets the style to the specified Pygments style.
            """
            from pygments.styles import get_style_by_name  # type:ignore

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
        def _get_brush(self, color: Any) -> Any:
            """ Returns a brush for the color.
            """
            result = self._brushes.get(color)
            if result is None:
                qcolor = self._get_color(color)
                result = QtGui.QBrush(qcolor)
                self._brushes[color] = result
            return result

        def _get_color(self, color: Any) -> Any:
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


    class NullScintillaLexer(Qsci.QsciLexerCustom):  # type:ignore
        """A do-nothing colorizer for Scintilla."""

        def __init__(self, c: Cmdr, parent: Position = None) -> None:
            super().__init__(parent)  # Init the pase class
            self.leo_c = c
            self.configure_lexer()

        def description(self, style: Any) -> str:
            return 'NullScintillaLexer'

        def setStyling(self, length: Any, style: Any) -> None:
            g.trace('(NullScintillaLexer)', length, style)

        def styleText(self, start: Any, end: Any) -> None:
            """Style the text from start to end."""

        def configure_lexer(self) -> None:
            """Configure the QScintilla lexer."""
            # c = self.leo_c
            lexer = self
            # To do: use c.config setting.
            # pylint: disable=no-member
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
    def __init__(self, c: Cmdr, widget: Widget) -> None:
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
        self.old_v = None
        # Monkey-patch g.isValidLanguage.
        g.isValidLanguage = self.pygments_isValidLanguage
        # Init common data...
        self.reloadSettings()
    #@+node:ekr.20190324063349.1: *4* pyg_c.format getters
    def getLegacyDefaultFormat(self) -> None:
        return None

    def getLegacyFormat(self, token: Any, text: Any) -> str:
        """Return a jEdit tag for the given pygments token."""
        # Tables and setTag assume lower-case.
        r = repr(token).lstrip('Token.').lstrip('Literal.').lower()
        if r == 'name':
            # Avoid a colision with existing Leo tag.
            r = 'name.pygments'
        return r

    def getPygmentsFormat(self, token: Any, text: Any) -> str:
        """Return a pygments format."""
        format = self.highlighter._formats.get(token)
        if not format:
            format = self.highlighter._get_format(token)
        return format
    #@+node:ekr.20190324064341.1: *4* pyg_c.format setters
    def setLegacyFormat(self, index: int, length: Any, format: Any, s: str) -> None:
        """Call the jEdit style setTag."""
        super().setTag(format, s, index, index + length)

    def setPygmentsFormat(self, index: int, length: Any, format: Any, s: str) -> None:
        """Call the base setTag to set the Qt format."""
        self.highlighter.setFormat(index, length, format)
    #@+node:ekr.20220316200022.1: *3* pyg_c.pygments_isValidLanguage
    def pygments_isValidLanguage(self, language: str) -> bool:
        """
        A hack: we will monkey-patch g.isValidLanguage to be this method.

        Without this hack this class would have to define its own copy of the
        (complex!) g.getLanguageFromAncestorAtFileNode function.
        """
        lexer_name = 'python3' if language == 'python' else language
        try:
            import pygments.lexers as lexers  # type: ignore
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
    format_dict: Dict[str, str] = {}  # Keys are repr(Token), values are formats.
    lexers_dict: Dict[str, Callable] = {}  # Keys are language names, values are instantiated, patched lexers.
    state_s_dict: Dict[str, int] = {}  # Keys are strings, values are ints.
    state_n_dict: Dict[int, str] = {}  # # Keys are ints, values are strings.
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
    def at_color_callback(self, lexer: Any, match: Any) -> Generator:
        from pygments.token import Name, Text  # type: ignore
        kind = match.group(0)
        self.color_enabled = kind == '@color'
        if self.color_enabled:
            yield match.start(), Name.Decorator, kind
        else:
            yield match.start(), Text, kind
    #@+node:ekr.20190323045735.1: *4* pyg_c.at_language_callback
    def at_language_callback(self, lexer: Any, match: Any) -> Generator:
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
    unknown_languages: List[str] = []

    def get_lexer(self, language: str) -> Any:
        """Return the lexer for self.language, creating it if necessary."""
        import pygments.lexers as lexers  # type: ignore
        trace = 'coloring' in g.app.debug
        try:
            # #1520: always define lexer_language.
            lexer_name = 'python3' if language == 'python' else language
            lexer = lexers.get_lexer_by_name(lexer_name)
        except Exception:
            # One of the lexer's will not exist.
            # pylint: disable=no-member
            if trace and language not in self.unknown_languages:
                self.unknown_languages.append(language)
                g.trace(f"\nno pygments lexer for {language!r}. Using python 3 lexer\n")
            lexer = lexers.Python3Lexer()
        return lexer
    #@+node:ekr.20190322094034.1: *4* pyg_c.patch_lexer
    def patch_lexer(self, language: Any, lexer: Any) -> Any:

        from pygments.token import Comment  # type:ignore
        from pygments.lexer import inherit  # type:ignore


        class PatchedLexer(lexer.__class__):  # type:ignore

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

        try:
            return PatchedLexer()
        except Exception:
            g.trace(f"can not patch {language!r}")
            g.es_exception()
            return lexer
    #@+node:ekr.20190322133358.1: *4* pyg_c.section_ref_callback
    def section_ref_callback(self, lexer: Any, match: Any) -> Generator:
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
    def set_lexer(self) -> Any:
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
    def __init__(self, c: Cmdr, widget: Widget) -> None:
        """Ctor for QScintillaColorizer. widget is a """
        super().__init__(c)
        self.count = 0  # For unit testing.
        self.colorCacheFlag = False
        self.error = False  # Set if there is an error in jeditColorizer.recolor
        self.flag = True  # Per-node enable/disable flag.
        self.full_recolor_count = 0  # For unit testing.
        self.language = 'python'  # set by scanLanguageDirectives.
        self.highlighter = None
        self.lexer = None  # Set in changeLexer.
        widget.leo_colorizer = self
        # Define/configure various lexers.
        self.reloadSettings()
        if Qsci:
            self.lexersDict = self.makeLexersDict()
            self.nullLexer = NullScintillaLexer(c)
        else:
            self.lexersDict = {}  # type:ignore
            self.nullLexer = g.NullObject()  # type:ignore

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
        language = g.getLanguageFromAncestorAtFileNode(root) or c.target_language
        return language
    #@+node:ekr.20140906081909.18718: *3* qsc.changeLexer
    def changeLexer(self, language: str) -> None:
        """Set the lexer for the given language."""
        c = self.c
        wrapper = c.frame.body.wrapper
        w = wrapper.widget  # A Qsci.QsciSintilla object.
        self.lexer = self.lexersDict.get(language, self.nullLexer)  # type:ignore
        w.setLexer(self.lexer)
    #@+node:ekr.20140906081909.18707: *3* qsc.colorize
    def colorize(self, p: Position) -> None:
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
    def configure_lexer(self, lexer: Any) -> None:
        """Configure the QScintilla lexer using @data qt-scintilla-styles."""
        c = self.c
        qcolor, qfont = QtGui.QColor, QtGui.QFont
        font = qfont("DejaVu Sans Mono", 14)
        lexer.setFont(font)
        lexer.setEolFill(False, -1)
        if hasattr(lexer, 'setStringsOverNewlineAllowed'):
            lexer.setStringsOverNewlineAllowed(False)
        table: List[Tuple[str, str]] = []
        aList = c.config.getData('qt-scintilla-styles')
        if aList:
            aList = [s.split(',') for s in aList]
            for z in aList:
                if len(z) == 2:
                    color, style = z
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
                    lexer.setColor(qcolor(color), style_number)
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
    def makeLexersDict(self) -> Dict[str, Any]:
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
        d: Dict[str, Any] = {}
        for language_name in table:
            class_name = 'QsciLexer' + language_name
            lexer_class = getattr(Qsci, class_name, None)
            if lexer_class:
                # pylint: disable=not-callable
                lexer = lexer_class(parent=parent)
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

    from pygments.lexer import RegexLexer, _TokenType, Text, Error

    def get_tokens_unprocessed(self: Any, text: str, stack: Sequence[str] = ('root',)) -> Generator:
        """
        Split ``text`` into (tokentype, text) pairs.

        Monkeypatched to store the final stack on the object itself.

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
                m = rexmatch(text, pos)
                if m:
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


        class PygmentsBlockUserData(QtGui.QTextBlockUserData):  # type:ignore
            """ Storage for the user data associated with each line."""

            syntax_stack = ('root',)

            def __init__(self, **kwds: Any) -> None:
                for key, value in kwds.items():
                    setattr(self, key, value)
                super().__init__()

            def __repr__(self) -> str:
                attrs = ['syntax_stack']
                kwds = ', '.join([
                    f"{attr}={getattr(self, attr)!r}"
                        for attr in attrs
                ])
                return f"PygmentsBlockUserData({kwds})"
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
