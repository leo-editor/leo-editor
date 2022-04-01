#@+leo-ver=5-thin
#@+node:tom.20220222214720.1: * @file bookmark_search_panel.py
#@@language python
"""A log tab panel for a bookmark manager.

"""

#@+others
#@+node:tom.20220222214720.2: ** Imports
import re
from os import startfile
import webbrowser
import urllib
import html

from leo.core.leoQt import QtWidgets, QtCore

QLineEdit = QtWidgets.QLineEdit
QMainWindow = QtWidgets.QMainWindow
QPushButton = QtWidgets.QPushButton
QRect = QtCore.QRect
QStackedWidget = QtWidgets.QStackedWidget
QTextBrowser = QtWidgets.QTextBrowser
QHBoxLayout = QtWidgets.QHBoxLayout
QVBoxLayout = QtWidgets.QVBoxLayout
QUrl = QtCore.QUrl
QWidget = QtWidgets.QWidget

QStatusBar = QtWidgets.QStatusBar
#@+node:tom.20220222214720.3: ** Declarations
VERSION = '0.99'

BOOKMARKS_HOME = '@bookmark-collection'
INDENT = '&nbsp;'*5  # For lists of links
RES = 0
SUBJ = 1
SPARE = 2

HTML_TO_CLIP = False

WORD = r'(\w+)'
PHRASE = r'"(.*?)"'
TERM = re.compile(f'{PHRASE}|{WORD}')

# These initial colors are suitable for the tbp_dark_solarized
# but may be changed depending on the theme in use.
FG = '#839496;'
BG = '#002b36'
BBG = '#073642' # "bright" bg for pushbuttons and line edits

PB_STYLE_WEIGHT_BOLD = 'QPushButton {font-weight: bold;}'
PB_STYLE_WEIGHT_NORMAL = 'QPushButton {font-weight: normal;}'
#@+node:tom.20220225230313.1: ** color_styles()
#@@language python
def color_styles(fg, bg, bbg):
    styles = f"""QTextBrowser 
        {{font-family: "Segoe UI", Verdana, "Bitstream Vera Sans", sans-serif;}}

        QLineEdit {{
        padding-left: .5em;
        padding-right: 1em;
        border: 1px solid {fg};}}
    """


    base_style = f"""* {{
        color: {fg};
        background: {bg};
        font-family: "Segoe UI", Verdana, Arial, "Bitstream Vera Sans", sans-serif;
        font-size: 9pt;
        font-weight: normal;
        padding-left:2em;
        padding-right:2em;
     }}

     QTextBrowser {{
        border: 1px solid {fg};
        padding-left: 1em;
        padding-right:1em;
     }}

    QScrollBar:vertical {{
        width: 12px;
        border: 1px solid {bg};
        margin: 22px 0px 22 0px
    }}
    QScrollBar::hover:vertical{{
        background: {fg};
    }}

    QScrollBar::handle:vertical {{
        min-height: 20px;
        subcontrol-origin: padding;
    }}

    QScrollBar::sub-line:vertical {{
        background: {fg};
        height: 20px;
        border: 1px solid black;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }}    
    QScrollBar::add-line:vertical {{
        background: {fg};
        border: 1px solid black;
        height: 20px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }}    

    QScrollBar::up-arrow:vertical {{
        height: 20px;
    }}    
    QScrollBar::down-arrow:vertical {{
        height: 20px;
    """

    html_css = f'''<style type='text/css'>
    a {{
        color: {fg};
        text-decoration: none;
        font-size: 10pt;
    }}
    li {{
        list-style:none;
        margin-left: -2em;
    }}
    hr {{border: 3px solid {fg};}}
    </style>\n
    '''

    pb_style_ext = f'''QPushButton {{
        background: {bbg};
        padding-bottom: .3em;
        border: 1px solid {fg};
    }}
        QPushButton:hover {{
        color: {bg};
        background: {fg};
        }}
    '''

    le_style_ext = f'''QLineEdit {{
        padding-left: .5em;
        padding-right: 1em;
        border: 1px solid {fg};
    }}'''

    return (styles, base_style, html_css, pb_style_ext, le_style_ext)

#@+node:tom.20220222214720.6: ** class PanelWidget
class PanelWidget(QWidget):
    """Contains the View and Controller for a browser bookmark viewer.
    
    The Leo tree nodes amount to the Model of a MVC
    design.
    """

    def __init__(self, g, c):
        """
        ARGUMENTS
        g -- the Leo Global instance
        c -- the Leo commander for the current outline.
        """

        super().__init__()

        self.c = c
        self.g = g
        bv = self.baseview = BaseView(g, c)
        cont = self.controller = Controller(bv, g, c)
        sb = self.statusbar = QStatusBar()

        layout = QVBoxLayout()
        layout.addWidget(bv)
        layout.addWidget(sb)
        self.setLayout(layout)

        bv.search_box.change_connect(cont.search_resources)
        bv.subjbrowser.anchorClicked.connect(cont.search_subjects)

        res_counts, subj_counts = cont.count_all()
        count_str = f'resources: {res_counts}, subjects: {subj_counts}'

        sb_css = f"""QStatusBar {{
            color: {bv.bg};
            background: {bv.fg};}}"""
        sb.setStyleSheet(sb_css)

        sb.showMessage(count_str, 10000)

#@+node:tom.20220222214720.7: ** Class BaseView
class BaseView(QWidget):
    """Provides a "view" that receives a data package and displays it.

    The display consists of two panes, of which only one
    can be visible at a time, buttons to change 
    the pane in view, and an input field for entering
    search terms.
    """

    #@+<< __init__ >>
    #@+node:tom.20220227003059.1: *3* << __init__ >>
    def __init__(self, g, c):
        super().__init__()
        self.c = c
        self.g = g
        rb = self.resbrowser = QTextBrowser()
        sb = self.subjbrowser = QTextBrowser()
        self.search_box = SearchBox(c)
        self.view_switcher = ViewSwitcher()

        self.model_data = None
        self.subj_term_data = None
        self.HTML_CSS = ''

        self.subjects = 0
        self.resources = 0

        #@+<< compute styles >>
        #@+node:tom.20220226110417.1: *4* << compute styles >>
        fg, bg, bbg = self.get_colors_from_settings()
        STYLES, BASE_STYLE, HTML_CSS, PB_STYLE_EXT,LE_STYLE_EXT = \
            color_styles(fg, bg, bbg)

        self.fg, self.bg = fg, bg

        self.HTML_R = f'''<style type='text/css'>{HTML_CSS}</style>
        <h1>This is the Bookmark App Resource List</h1>
        <a href = 'local resource link'>Example Resource Link</a>
        '''

        self.HTML_S = f'''<style type='text/css'>{HTML_CSS}</style>
        <h1>This is the Bookmark App Subject List</h1>
        <a href = 'local subject term link'>Example Subject Term Link</a>
        '''

        self.HTML_CSS = HTML_CSS
        #@-<< compute styles >>
        #@+<< set up widgets >>
        #@+node:tom.20220222214720.8: *4* << set up widgets >>
        rb.setOpenLinks(False)  # Prevent widget from navigating to links
        sb.setOpenLinks(False)  # Prevent widget from navigating to links
        #rb.setStyleSheet(STYLE)
        #pb.widget.setStyleSheet(STYLE + PB_STYLE_EXT)
        #sw.setStyleSheet(BASE_STYLE + PB_STYLE_EXT)

        # rb.setOpenLinks(False)  # Prevent widget from navigating to links
        # sb.setOpenLinks(False)  # Prevent widget from navigating to links

        #@-<< set up widgets >>
        #@+<< build display widget >>
        #@+node:tom.20220222214720.9: *4* << build display widget >>
        self.display_widget = QStackedWidget()
        self.display_widget.insertWidget(RES, rb)
        self.display_widget.insertWidget(SUBJ, sb)

        #@-<< build display widget >>
        #@+<< set layout >>
        #@+node:tom.20220222214720.10: *4* << set layout >>
        layout = QVBoxLayout()
        layout.addWidget(self.search_box.widget)
        layout.addWidget(self.view_switcher.widget)
        layout.addWidget(self.display_widget)
        #layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        #@-<< set layout >>
        #@+<< connect signals >>
        #@+node:tom.20220222214720.11: *4* << connect signals >>
        self.resbrowser.anchorClicked.connect(self.handleRbAnchorClick)
        #self.subjbrowser.anchorClicked.connect(self.handleSbAnchorClick)

        # Order of the handlers is important here!
        handlers = (self.view_switch_res, self.view_switch_subj,
                    self.view_switch_spare)
        self.view_switcher.connect(handlers)
        #@-<< connect signals >>

        self.setStyleSheet(STYLES)
        self.find_view_kind = RES
        self.display_widget.setCurrentIndex(RES)
    #@-<< __init__ >>

    #@+<< def signal handlers >>
    #@+node:tom.20220222214720.12: *3* << def signal handlers >>
    def view_switch_subj(self):
        """When the "Subjects" button is pressed."""
        self.find_view_kind = SUBJ
        self.display_widget.setCurrentIndex(SUBJ)
        self.view_switcher.clear_bolds()
        self.view_switcher.set_bold(self.view_switcher.buttons[SUBJ])

    def view_switch_res(self):
        """When the "Resources" button is pressed."""
        self.find_view_kind = RES
        self.display_widget.setCurrentIndex(RES)
        self.view_switcher.clear_bolds()
        self.view_switcher.set_bold(self.view_switcher.buttons[RES])

    def view_switch_spare(self):
        """When the "Spare" button is pressed."""
        self.find_view_kind = SPARE
        self.display_widget.setCurrentIndex(SPARE)
        self.view_switcher.clear_bolds()
        self.view_switcher.set_bold(self.view_switcher.buttons[SPARE])

    def handleRbAnchorClick(self, ref):
        ref_st = ref.toString()  # ref is a QUrl
        if ref_st.startswith('http:') or ref_st.startswith('https:'):
            url = urllib.parse.unquote(ref_st)
            webbrowser.open_new_tab(url)
        elif ref_st.startswith('url:file://'):
            url = ref_st.replace('url:file://', '', 1)
            url = urllib.parse.unquote(url)
            if self.g.isWindows:
                url = url.replace('/', '\\')
            assert url, 'URL should not be empty'
            startfile(url)
        elif ref_st.startswith('file:'):
            url = ref_st.replace('"', '')
            self.g.handleUrl(url, self.c)
        elif ref_st.startswith('unl:'):
            # Assume the form is "unl://c:/..."
            unl = ref_st
            host = ref.host()
            if self.g.isWindows and host and not host.endswith(':'):
                unl = unl.replace(host, host + ':', 1)
            self.g.handleUnl(unl, self.c)
        elif not ref_st.startswith('unl'):
            unl = 'unl://#' + ref_st
            self.g.handleUnl(unl, self.c)
        else:
            self.g.handleUnl(ref_st, self.c)
        # else:
            # print(ref)

    def handleSbAnchorClick(self, term):
        print('Sb:', term.toString())


    #@-<< def signal handlers >>
    #@+<< def generate link display >>
    #@+node:tom.20220302135207.1: *3* << def generate link display >>
    def generate_link_display(self):
        html_ = self.generate_link_html()
        if not html_: html_ = '(Nothing found)'
        return html_
    #@-<< def generate link display >>

    def display_html(self, browser, html_):
        browser.setHtml(html_)

    #@+others
    #@+node:tom.20220225231417.1: *3* get_colors_from_settings()
    def get_colors_from_settings(self):
        """Get fg, bg, and bbg colors from the Leo theme.
        
        RETURNS
        a tuple (fg, bg, bbg) of CSS colors.
        """
        g, c = self.g, self.c

        ssm = g.app.gui.styleSheetManagerClass(c)

        w = ssm.get_master_widget()
        sheet = w.styleSheet()

        def find_prop(text, name):
            RE = fr'{name}[ ]*:[ ]*([^;]+)'
            found = re.findall(RE, text)
            found = found[0] if found else ''
            return found

        loc = sheet.find('QTextEdit {')
        frag = sheet[loc:loc + 90]
        bg = find_prop(frag, 'background')
        fg = find_prop(frag, 'color')
        #g.es(fg, bg)

        return (fg, bg, bg)

    #@+node:tom.20220222214720.13: *3* bv.generate_link_html
    def generate_link_html(self):
        """Return an HTML string for the View to use for display.

        The display will show the links data.
        
        find_results = [(<searchterm>, <termlist>, <linklist>)*]
        <termlist> = [(<leaf term>, <unl>)*]
        <linklist> = [(<page title>, <page url>, <term unl>)*]

        ARGUMENT
        data -- a list of results with the above structure.

        RETURNS -- an HTML string
        """

        data = self.model_data
        if not data:
            return 'No data'
        search_phrase = data[0]

        #@+<< utility functions >>
        #@+node:tom.20220302135417.1: *4* << utility functions >>
        def truncate(s, num = 45):
            s = s if len(s) < num else s[:num] + '...'
            return s

        def path_str(path: tuple) -> str:
            """Convert a list of path steps to a "/"-separated string."""
            return '/'.join(path)

        def path2unl_anchors(path, bold = False):
            """Return an html string of a context string for the path.
            
            Each step of the context has an anchor with its UNL.
            
            ARGUMENT
            path -- a sequence of path steps (e.g., 'a/b/c')
            
            RETURNS
            a string
            """
            html_ = ''
            context = ''
            stress = '<b>' if bold else ''
            stress_end = '</b>' if bold else ''
            for n, step in enumerate(path):
                if n == 0:
                    context += step
                else:
                    context = '/' + step
                unl = '-->'.join(path[:n + 1])
                unl = f'#{BOOKMARKS_HOME}-->' + unl
                #unl = urllib.parse.quote('unl://' + unl)
                unl = 'unl://' + unl
                html_ += (f'<a href="{unl}">{stress}{context}{stress_end}</a>\n')
            return html_
        #@-<< utility functions >>

        if data:
            #str = ''
            res_count = 0
            paths = []
            res_by_paths = {}

            # Populate paths list, res_by_paths dict
            #@+<< get resources by paths >>
            #@+node:tom.20220302135436.1: *4* << get resources by paths >>
            for item in data[1]:
                path = item.path
                subject_path = path[:-1]
                paths.append(subject_path)
                if item.type == RES:
                    res_count += 1
                    _l1 = res_by_paths.get(subject_path, [])
                    if not _l1: res_by_paths[subject_path] = _l1
                    _l1.append(item)
            #@-<< get resources by paths >>

            display_list = []
            #@+<< build display list >>
            #@+node:tom.20220302135510.1: *4* << build display list >>
            # Dedup and sort
            pathset = set()
            for path in res_by_paths:
                pathset.add(path)
            pathlist = sorted(pathset)

            for path in pathlist:
                subj_path = path
                # Clickable context line for this path
                display_list.append(path2unl_anchors(subj_path, True))

                # All items for this path
                items = res_by_paths.get(path, [])
                for n, item in enumerate(items):
                    # Build the context line
                    if n %7 == 0 and n != 0:
                        display_list.append('\n')

                    # Build the resource line
                    title = truncate(item.title)
                    url = item.url.replace(':ref: ', '')
                    url = html.unescape(url)
                    unl = item.unl
                    pos = unl.find('#', 1)
                    unl = unl[pos:]
                    unl = 'unl://' + unl
                    resource_str = (f'<a href="{unl}">( <b>?</b> )</a> '
                                    + f'<a href="{url}">{title}</a>\n')
                    display_list.append(resource_str)

                display_list.append('\n')

            #@-<< build display list >>

        html_ = '<br>\n'.join(display_list)

        # Produce the html string for output
        searches = ''
        for s in search_phrase:
            searches += f'"{s}" '
        header = f'<h3>Resource Matches for <i>{searches}</i></h3>\n'
        html_ = self.HTML_CSS + header + f'<div>{html_}</div>\n'
        if HTML_TO_CLIP: 
            self.g.app.gui.replaceClipboardWith(html_)


        return self.HTML_CSS + html_  # + countstr
    #@+node:tom.20220222214720.14: *3* bv.generate_term_display
    def generate_term_html(self):
        """Return an HTML string for the View to use for display.

        The display will show the subject terms data.
        
        find_results = [(<searchterm>, <linklist>, <termlist>)*]
        <termlist> = [Item*]
        <linklist> = [Item*]

        The display pane will deduplicate the entries. 
        
        ARGUMENT
        data -- a list of results with the above structure.

        RETURNS -- an HTML string
        """

        data = self.model_data
        if not data:
            return 'No data'


        search_phrase = data[0]
        try:
            termlist = [t.path[-1] for t in data[2]]
        except:
            print(data[2][0].title, data[2][0].path)
            assert False, 'data error'
        termset = set(termlist)
        terms = sorted(list(termset))


        searches = ''
        for s in search_phrase:
            searches += f'"{s}" '

        header = f'<h3>Subject Matches for <i>{searches}</i></h3>\n'
        results = []
        for leaf in terms:
            if leaf.lower().startswith('and'):
                continue
            else:
                results.append(f'<a href="{leaf}">{leaf}</a>')

        html = header + '<br>'.join(results)
        #if HTML_TO_CLIP: g.app.gui.replaceClipboardWith(html)
        return html

    def generate_term_display(self, html):
        return self.HTML_CSS + html
    #@+node:tom.20220222214720.15: *3* bv.data_available
    def data_available(self, data):
        """Display views of search results.
        
        This method is used as a signal handler when a
        search is made.

        Uses data stored in self.model_data.  Format:

        find_results = [(<searchterm>, <linklist>)*, <termlist> ]
        <termlist> = [Item*]
        <linklist> = [Item*]
        """
        self.model_data = data
        html_ = self.generate_link_display()
        self.display_html(self.resbrowser, html_)

        html_ = self.generate_term_html()
        html_ = self.generate_term_display(html_)
        self.display_html(self.subjbrowser, html_)
    #@+node:tom.20220307223405.1: *3* bv.subj_term_data_available
    def subj_term_data_available(self):
        """Display views of subject term search results.
        
        This method is used as a signal handler when a
        search is made.

        Uses data stored in self.subj_term_data.  Format:

        find_results = [(<searchterm>, <termlist> ]
        <termlist> = [Item*]
        """
        search, subj_items = self.subj_term_data
        print('\n'.join(t.context for t in subj_items))


        # html_ = self.generate_link_display()
        # self.display_html(self.resbrowser, html_)

        # html_ = self.generate_term_html()
        # html_ = self.generate_term_display(html_)
        # self.display_html(self.subjbrowser, html_)
    #@-others
#@+node:tom.20220222214720.16: ** Class SearchBox
class SearchBox:
    """A basic search input having a lineedit input and a pushbutton."""

    def __init__(self, commander = None):
        self.commander = commander
        self.widget = QWidget()
        self.findbox = QLineEdit()
        self.gobutton = QPushButton("Search")

        layout = QHBoxLayout()
        layout.addWidget(self.findbox)
        layout.addWidget(self.gobutton)
        self.widget.setLayout(layout)

        # These connections should be overridden by the
        # using widget or window.
        #self.change_connect(self.controller.search)

    def send_find(self):
        print(self.findbox.text())

    def change_connect(self, handler):
        try:
            self.gobutton.clicked.disconnect()
            self.findbox.returnPressed.disconnect()
        except:
            pass  # Can't disconnect if we've never been connected
        self.gobutton.clicked.connect(handler)
        self.findbox.returnPressed.connect(handler)
#@+node:tom.20220307001140.1: ** class ViewSwitcher
class ViewSwitcher:
    """A class to contain view-switching controls."""

    def __init__(self):
        self.widget = QWidget()
        self.button_res = QPushButton("Resources")
        self.button_subj = QPushButton("Subjects")
        self.button3 = QPushButton("Spare")
        self.buttons = {RES: self.button_res,
                        SUBJ: self.button_subj,
                        SPARE: self.button3}

        layout = QHBoxLayout()
        layout.addWidget(self.button_res)
        layout.addWidget(self.button_subj)
        layout.addWidget(self.button3)
        self.widget.setLayout(layout)

        self.set_bold(self.button_res)

    def connect(self, handlers):
        """Connect signal handlers.

        Handlers are connected to the buttons in order
        of their insertion into the layout.
        """
        self.button_res.clicked.connect(handlers[RES])
        self.button_subj.clicked.connect(handlers[SUBJ])
        self.button3.clicked.connect(handlers[SPARE])

    def clear_bolds(self):
        """Set weight of all buttons back to normal."""
        for b in self.buttons.values():
            b.setStyleSheet(PB_STYLE_WEIGHT_NORMAL)

    def set_bold(self, pb):
        """Set weight of a button to bold."""
        pb.setStyleSheet(PB_STYLE_WEIGHT_BOLD)

#@+node:tom.20220302131316.1: ** class Item
class Item:
    """Represents a collection of attributes of interest
    for nesting search results hierarchically.
    """

    def __init__(self):
        self._unl = ''
        self.context = ''
        self.has_content = False
        self.level = 0
        self.path = []
        self.title = ''
        self.type = None
        self.url = ''

    def __str__(self):
        return f'Item: path = {self.context}, title = {self.title[:40]}'

    @property
    def unl(self):
        return self._unl

    @unl.setter
    def unl(self, value):
        """Add unl and also the corresponding context path."""
        self._unl = value
        self.path = self.make_path()
        self.context = self.make_context()

    def make_path(self):
        """Return this item's path.

        The path is a list of the parent node names.
        For example, a hierarchical structure 
        Food/Recipes/Bread would become
        the list ["Food", "Recipes", "Bread"].
        """
        pth_steps = self.unl.split('-->')[1:]
        return tuple(pth_steps)

    def make_context(self):
        """Return the context string for this item's path.
        
        For a path ('a', 'b', 'c'), the context string is
        "a/b/c".
        """
        return '/'.join(self.path)

#@+node:tom.20220222214720.17: ** class Controller
class Controller:
    """Sends data to View panels."""

#@+<< __init__ >>
#@+node:tom.20220227002924.1: *3* << __init__ >>
    def __init__(self, baseview, g, c):
        """Operates on the data and communicates with
        the "View" and the "Model" (i.e., the Leo tree).
        
        ARGUMENTS
        g -- the Leo Global instance
        c -- the Leo commander for the current outline.
        """
        self.baseview = baseview
        self.g = g
        self.c = c
        self.resources = 0
        self.subjects = 0
        self.data = None
        self.subj_search_term = ''

    # def simulate_search(self, c = None):
        # """Return simulated search results."""
        # self.baseview.data_available(self.FIND_DATA)

#@-<< __init__ >>
    #@+others
    #@+node:tom.20220224183645.1: *3* def move to bookmarks start
    def move_to_bk_start(self):
        """Find and move to the top node of the bookmarks tree.
        
        RETURNS
        the top node, or None if not found
        """
        bk_root = None
        p = self.c.rootPosition()
        while p:
            if p.h.startswith(f'{BOOKMARKS_HOME}'):
                bk_root = p
                break
            p.moveToThreadNext()
        return bk_root
    #@+node:tom.20220302131923.1: *3* def walk_resources()
    def walk_resources(self, p, search_phrases = [], search_type = 'std'):
        """Walk node subtree and return Item list.
        
        Create one new Item for each node for which
        the search term occurs in headline.
        
        Return the list of found Items.
        """

        res_items = []
        subj_items = []
        for p1 in p.subtree():
            h, b = p1.h, p1.b
            item = Item()
            item.title = h
            item.unl = p1.get_UNL()
            item.type = RES if ':ref:' in b else SUBJ
            item.level = p1.level()

            keep = not search_phrases
            for sp in search_phrases:
                if search_type == 'words':
                    # Only keep if match is on word boundary
                    sw = sp.split()
                    target_words = h.lower().split()
                    if target_words == sw:
                        keep = True
                        break
                    len_sw = len(sw)
                    shifts = len(target_words) - len_sw + 1
                    for i in range(shifts):
                        x = target_words[i : i + len_sw]
                        if x == sw:
                            keep = True
                            break
                else:
                    # Keep if search phrase matches any substring
                    if sp in h.lower():
                        keep = True
                        break

            if not keep:
                continue

            if item.type == RES:
                start = b.find(':ref:')
                end = b[start:].find('\n')
                if end > -1:
                    item.url = b[start:start + end].strip()
                else:
                    item.url = b[start:].strip()
                res_items.append(item)
            else:
                subj_items.append(item)
        return res_items, subj_items

    #@+node:tom.20220223110029.1: *3* def search_resources
    #@@language python
    def search_resources(self):
        #@+<< docstring >>
        #@+node:tom.20220223110611.1: *4* << docstring >>
        """Find links and organizer nodes containing search words.

        Link nodes contain a line starting with ":ref:".  Organizers
        do not.

        The outline is searched starting at a top-level node
        whose headline starts with BOOKMARKS_HOME.

        After assembling the search results, they are stored in the
        parent BaseView, and bv.data_available() is called.

        ARGUMENT
        phrase -- a string of one or more search terms.
                  A search term is either a word or a 
                  double-quoted string.

        RETURNS
        nothing -- Stores a "find_results" data structure the Baseview
                   variable "model_data". 

                   find_results = ((<search string>, [Item(),*])
        """
        #@-<< docstring >>
        bv = self.baseview
        sb = bv.search_box
        fb = sb.findbox

        search_terms = []
        #@+<< get search terms >>
        #@+node:tom.20220224183502.1: *4* << get search terms >>
        # Search terms may be phrases in double quotes
        search_phrase = fb.text()

        search_type = 'std'
        if search_phrase.startswith('w:'):
            search_type = 'words'
            search_phrase = search_phrase[2:]

        search_phrase_lower = search_phrase.lower()

        # If there is an unmatched quote, add one to the end
        if search_phrase.count('"') %2:
            search_phrase += '"'

        found = TERM.split(search_phrase_lower)
        search_terms = [t for t in found if t and t.strip()]

        #self.g.es(search_terms)
        # for p in found:
            # t = p[0] if p[0] else p[1]
            # search_terms.append(t)
        #@-<< get search terms >>

        g = self.g

        bk_root = self.move_to_bk_start()
        if not bk_root:
            g.es('No bookmark tree found')
            return None

        res_items, subj_items = self.walk_resources(bk_root, search_terms, search_type)

        self.baseview.resources = len(res_items)
        self.baseview.subjects = len(subj_items)

        bv.data_available((search_terms, res_items, subj_items))
    #@+node:tom.20220307214930.1: *3* def search_subjects
    def search_subjects(self, subject):
        #@+<< docstring >>
        #@+node:tom.20220307215326.1: *4* << docstring >>
        """Return a list of items for nodes whose headline matches the subject.

        After assembling the search results, they are stored in the
        BaseView, and bv.subj_term_data_available() is called.


        ARGUMENT
        subject -- a string

        RETURNS
        Nothing -- a tuple: (<search term>, <list of Items>) is stored in
                   the Baseview variable "subj_term_data".
        """
        #@-<< docstring >>

        bk_root = self.move_to_bk_start()
        if not bk_root:
            self.g.es('No bookmark tree found')
            return None

        subj_items = []
        term = subject.toString().lower()  # subject: QUrl
        for p1 in bk_root.subtree():
            h = p1.h
            if not h.lower() == term:
                continue
            if ':ref:' in p1.b:
                continue
            item = Item()
            item.title = h
            item.unl = p1.get_UNL()
            item.type = SUBJ
            item.level = p1.level()

            subj_items.append(item)

        self.baseview.subj_term_data = (subject, subj_items)
        self.baseview.subj_term_data_available()
    #@+node:tom.20220307143449.1: *3* def count_all
    def count_all(self):
        """Return counts of all subject terms and resource nodes.
        
        RETURNS
        a tuple (subject_counts, resource_counts)
        """
        bk_root = self.move_to_bk_start()
        if not bk_root:
            self.g.es('No bookmark tree found')

        res_counts = subj_counts = 0
        for p1 in bk_root.subtree():
            if ':ref: ' in p1.b:
                res_counts += 1
            else:
                subj_counts += 1

        return res_counts, subj_counts
    #@-others
#@-others
#@-leo
