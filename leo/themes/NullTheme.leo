<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2"/>
<globals/>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20180312111155.1"><vh>Read me</vh></v>
<v t="ekr.20190522163424.1"><vh>Startup</vh>
<v t="ekr.20190522163405.1"><vh>@button backup</vh></v>
<v t="ekr.20180318145515.1"><vh>@settings</vh>
<v t="ekr.20190621160912.1"><vh>@string target_language = css</vh></v>
<v t="ekr.20200914053650.1"><vh>@theme NULL_Theme</vh>
<v t="ekr.20200914053650.2"><vh>Theme description settings</vh>
<v t="ekr.20200914053650.5"><vh>@string theme-name = NullTheme</vh></v>
</v>
</v>
<v t="ekr.20200914053650.138"><vh>@data qt-gui-plugin-style-sheet</vh></v>
</v>
<v t="ekr.20200914053403.1"><vh>===== Not used style sheet</vh>
<v t="ekr.20180318145515.814"><vh> Widgets: general</vh></v>
<v t="ekr.20180318145515.815"><vh>Body &amp; other text</vh></v>
<v t="ekr.20180318145515.816"><vh>Borders</vh></v>
<v t="ekr.20180318145515.817"><vh>Buttons</vh></v>
<v t="ekr.20190522092828.1"><vh>Dock</vh></v>
<v t="ekr.20190921172001.1"><vh>Labels</vh></v>
<v t="ekr.20180318145515.818"><vh>Log</vh></v>
<v t="ekr.20181005084517.1"><vh>Gutter</vh></v>
<v t="ekr.20180318145515.819"><vh>Menus</vh></v>
<v t="ekr.20180318145515.820"><vh>Minibuffer &amp; label</vh></v>
<v t="ekr.20180318145515.821"><vh>Plugins</vh></v>
<v t="ekr.20180318145515.822"><vh>Scroll bars</vh></v>
<v t="ekr.20180318145515.823"><vh>Splitters</vh></v>
<v t="ekr.20180318145515.824"><vh>Status area</vh></v>
<v t="ekr.20180318145515.825"><vh>Tab bar</vh></v>
<v t="ekr.20180318145515.826"><vh>Tree</vh></v>
</v>
</v>
<v t="ekr.20190522163439.1"><vh>Notes</vh>
<v t="ekr.20180312110809.1"><vh>Theme Tests</vh>
<v t="ekr.20180314052441.1"><vh>Syntax coloring template</vh>
<v t="ekr.20180314052441.2"><vh>&lt;&lt; defined section &gt;&gt;</vh></v>
</v>
<v t="ekr.20180312110809.4"><vh>Test g.es(color=*)</vh></v>
<v t="ekr.20180312110809.5"><vh>g.error/note/warning test</vh></v>
</v>
<v t="ekr.20190106073008.1"><vh>zz Last: contains ~= (no longer used)</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20180312110809.1"></t>
<t tx="ekr.20180312110809.4">table = (
    # g.actualColor calls 
    'error', 'info', 'warning',
    'black', 'white',
    'xxx',
    'firebrick', 'grey', 'pink', 'purple', # Tk colors.
    # Solarized colors...
    'blue', 'cyan', 'green','magenta', 'orange', 'red',
    'violet', 'yellow',
)
for s in table:
    g.es(s, color=s)
</t>
<t tx="ekr.20180312110809.5"># g.cls()
g.error('error')
g.note('note')
g.warning('warning')
g.blue('blue')
g.red('red')
g.es_print('test')
g.es_print('black',color='black')</t>
<t tx="ekr.20180312111155.1" str_leo_pos="2,0,3">An empty theme, using all defaults.
</t>
<t tx="ekr.20180314052441.1">@ A doc part.  *All* languages colorize doc parts as follows:

1. The '@' sign itself is colored with @color leokeyword constant.

2. The rest of the doc parts depends on the @bool color-doc-parts-as-rest setting:
   True:  Colorize the doc part as **markdown**.
   False: Colorize the doc part using @color docpart.
   
Leo colorizes constructs with two kinds of color constants.
- **Default colors** defined in the node "Colors: defaults".
  These constants correspond to jEdit names used in leo/modes/*.py.
  See the "Colors: defaults" node for more details.
- **Leo-specific colors**, defined in the node "Colors: Leo constructs".
  
Most languages use only a subset of these color names.
Here are all the colors used to color python:
@c # @color leo_keyword_color

# Comments: @color comment1

def spam():
    
    # Reserved words...
    pass     # Python keywords: @color keyword1
    abs(1)   # Standard functions: @color keyword2.
    __file__ # double underscore names: @color keyword3
    try:
        frobnicate()
            # Function calls are not specially colored.
            # The default is the text foreground color in the body pane.
    except IOError: # Exception names: @color keyword3
        pass
    a = 2    # Operators (the = sign): @color operator_color
    
    # Strings...
    a = 'Regular string' # @color literal1
    '''Triple single-quoted docstring''' # @color literal2
    """Triple double-quoted docstring""" # @color literal2
    
# All languages use the following names...
    
# Urls: http://leoeditor.com/  @color url_color
&lt;&lt; undefined section &gt;&gt;      # @color undefined_section_name_color
&lt;&lt; defined section &gt;&gt;
    # The brackets:            @color section_name_brackets_color
    # The section name itself: @color section_name_color
    
@language python # @color leo_keyword_color
</t>
<t tx="ekr.20180314052441.2"></t>
<t tx="ekr.20180318145515.1">2018/03/18: from myLeoSettings.leo
</t>
<t tx="ekr.20180318145515.814">/* A Qt bug? More general css should precede more specific. */

QDockWidget {
 border: 5px solid red;
}
QDoubleSpinBox, QSpinBox, QDateEdit, QTimeEdit {
  border: none;
  padding: 3px;
  margin-right: 5px;
}
QLineEdit {
  border: none;
  padding: 3px;
}
QWidget {
  /* Not for text widgets */
  background:  @dark-base03;
  color: @dark-base1;
  border-color: @dark-base1;
  font-size: 16px;
}
</t>
<t tx="ekr.20180318145515.815">/* The body pane */
QTextEdit {
  background: @dark-base03;
  color: @text-foreground;
  font-family: @font-family-body;
  font-size: @font-size-body;
  font-weight: normal; /* normal,bold,100,..,900 */
  font-style: normal; /* normal,italic,oblique */
  padding-left: 3px;
  padding-top: 3px;
  padding-bottom: 3px;
  padding-right: 3px;
  height: 200%;
}
QWidget#richTextEdit {
  font-family: @font-family-body;
  font-size: @font-size-body;
}
</t>
<t tx="ekr.20180318145515.816">/* active pane highlighting */
QTextEdit#log-widget, LeoQTreeWidget#treeWidget, QTextEdit#richTextEdit {
  border-style: solid;
  border-width: 3px;
}
QTextEdit#log-widget {
  border-color: @log_text_background_color;
}
LeoQTreeWidget#treeWidget {
  border-color: @dark-base03;
}
QTextEdit#richTextEdit {
  border-color: @text-background;

}
QTextEdit:focus#log-widget,LeoQTreeWidget:focus#treeWidget, QTextEdit:focus#richTextEdit {
  border-color: @solarized-blue;
}
</t>
<t tx="ekr.20180318145515.817">QPushButton {
  color: @text-foreground;
  background: @bg-gradient;
  border: none;
  padding: 3px;
  margin-right: 5px;
}
QPushButton:hover {
  color: @button-hover-fg;
  background: @bg-gradient-hover;
}
</t>
<t tx="ekr.20180318145515.818">/* The log pane */
QTextEdit#log-widget {
  background: @log_text_background_color;
  color: @log_text_foreground_color;
  selection-color: white;
  selection-background-color: blue;
  font-family: @font-family-log;
  font-size: @font-size-log;
  font-weight: normal; /* normal,bold,100,..,900 */
  font-style: normal; /* normal, italic,oblique */
}
</t>
<t tx="ekr.20180318145515.819">/* Warning: do not change the order of these items! */
QMenu {
  color: @text-foreground-bright
}
QMenuBar::item:selected {
  color: @button-hover-fg;
  background: @bg-gradient-hover;
}
QMenu::item:selected {
  color: @button-hover-fg;
  background: @bg-gradient-hover;
}
QMenuBar::item {
  color: @text-foreground;
  background: @bg-gradient;
}
QMenuBar::item:pressed {
  color: @text-foreground-bright;
  background: @bg-gradient;
}
/* From KDE Dark Theme */
QMenu::separator
{
    height: 0.2ex;
    background: lightblue;
    margin-left: 1ex;
    margin-right: 0.5ex;
}
</t>
<t tx="ekr.20180318145515.820">/* The mini-buffer */
QLabel#minibufferLabel {
  color: @solarized-violet;
}
/* The minibuffer */
QLineEdit#lineEdit {
  color: @solarized-blue;
  font-family: @font-family;
  font-size: @font-size;
  font-weight: normal; /* normal,bold,100,..,900 */
  font-style: normal; /* normal,italic,oblique */
  border: 1px solid @solarized-blue;
}
</t>
<t tx="ekr.20180318145515.821">/* bookmarks plugin styling */

#show_bookmarks QPushButton {
  margin: 0; padding: 1; border: none;
  font-size: @bookmarks_base_size;
  color: @bookmarks_base_color;
  font-weight: @bookmarks_base_weight;
  /* text-decoration: at-bookmarks_base_decoration; */
}
#show_bookmarks QPushButton[style_class='bookmark_children'] {
  /* font-size: at-bookmarks_children_size; */
  /* font-weight: at-bookmarks_children_weight; */
  /* text-decoration: at-bookmarks_children_decoration; */
  color: @bookmarks_children_color;
}
#show_bookmarks QPushButton[style_class='bookmark_expanded'] {
  /* font-size: at-bookmarks_expanded_size; */
  color: @bookmarks_expanded_color;
  font-weight: @bookmarks_expanded_weight;
  text-decoration: @bookmarks_expanded_decoration;
}
#show_bookmarks QPushButton[style_class='bookmark_current'] {
  /* font-size: at-bookmarks_current_size; */
  /* text-decoration: at-bookmarks_current_decoration; */
  color: @bookmarks_current_color;
  font-weight: @bookmarks_current_weight;
}
</t>
<t tx="ekr.20180318145515.822">QScrollBar::horizontal {
   height: 7px;
}
QScrollBar::vertical {
   width: 7px;
}
QScrollBar::add-page, QScrollBar::sub-page {
  background: @dark-base03;
}
QScrollBar::handle {
  background: @dark-base02;
  color: @dark-base02;
}
QScrollBar::handle:hover {
  background: @dark-base0;
  color: @dark-base0;
}
/* to make these show up, remove the ::handle style above... bug? */
QScrollBar::add-line, QScrollBar::sub-line {
  background: @dark-base01;
  color: @dark-base01;
}</t>
<t tx="ekr.20180318145515.823">QSplitter::handle {
  background: @dark-base01;
  border: 2px solid black;
}
QSplitter::handle:hover {
  background: @solarized-violet;
}
</t>
<t tx="ekr.20180318145515.824">/* The status area */
QLineEdit#status1 {
  /* at-color status-bg overrides this! */
  /* background: @dark-base03; */
  border-color: @dark-base02;
  
  border-width: 1px;
  border-style: solid;
}
QLineEdit#status2 {
  /* at-color status-bg overrides this! */
  /* background: @dark-base03; */
  border-color: @dark-base02;
  border-width: 1px;
  border-style: solid;
}
</t>
<t tx="ekr.20180318145515.825">QTabBar:tab {
  background: @bg-gradient;
  color: @solarized-green;
  /* color: green; */
  /* margin-right: 5px; */
  /* padding: 2px; */
}
QTabBar::tab:selected {
  color: @text-foreground;
    /* EKR: Use *higher* visibility for active tab. */
    /* color: @solarized-green; */
}
QTabBar::tab:hover {
  background: @bg-gradient-hover;
  color: @button-hover-fg;
}
</t>
<t tx="ekr.20180318145515.826">/* ----- QTreeView: base class for QTreeWidget ----- */

QTreeView {
  /* These apply to the selected item, but not to editing items.*/
  color: @text-foreground-bright;
  font-family: @font-family-tree;
  font-size: @font-size-tree;
  font-weight: normal; /* normal,bold,100,..,900 */
  font-style: normal; /* normal, italic,oblique */
  show-decoration-selected: 1; /* Extend the selection */
}
QTreeView::item:selected, QTreeView::item:active:selected {
  background: @solarized-blue;
  color: @dark-base03;
}
QTreeView::branch:closed:has-children{
    image: @tree-image-closed;
}
QTreeView::branch:open:has-children{
    image: @tree-image-open;
}

/* ----- Headline edit widgets ----- */
QTreeView QLineEdit {
  font-size: @font-size-tree;
  background: @LeoYellow;
  color: black;
  padding: 0px;
}
</t>
<t tx="ekr.20181005084517.1">QFrame#gutter {
  background: gray;
}</t>
<t tx="ekr.20190106073008.1">/* ===== MUST BE LAST ===== */

QLineEdit#status1[style_class ~= 'info'],
QLineEdit#status2[style_class ~= 'info'] {
    background: @solarized-blue;
    color:      @solarized-white;
}

QLineEdit#status1[style_class ~= 'fail'],
QLineEdit#status2[style_class ~= 'fail'] {
    background: @solarized-red;
    color:      @solarized-white;
}
</t>
<t tx="ekr.20190522092828.1">QMainWindow::separator {
    /* The separator between QDockWidget's. */
    background: @dark-base01;
    width: 4px; height: 4px;
    border: 2px solid black;
}
QDockWidget::title {
    color: @dark-base3;
    background: black; /* @solarized-base01; */
    border: 1px solid @dark-base2;
}
QDockWidget::close-button, QDockWidget::float-button {
    background: @solarized-base01;
}
QLineEdit#editorLabel {
    border: 1px solid @dark-base2;
}
</t>
<t tx="ekr.20190522163405.1">c.backup_helper(sub_dir='ekr')
</t>
<t tx="ekr.20190522163424.1"></t>
<t tx="ekr.20190522163439.1"></t>
<t tx="ekr.20190621160912.1"></t>
<t tx="ekr.20190921172001.1">QLabel {
  color: @dark-base1;
}
QLabel#find-label {
  color: @dark-base1;
  border: 1px solid white;
  padding: 1px;
}</t>
<t tx="ekr.20200914053403.1"></t>
<t tx="ekr.20200914053650.1" lineYOffset="4b002e"></t>
<t tx="ekr.20200914053650.138">/*

  NullThemek.leo: @data qt-gui-plugin-style-sheet.

  at-tabwidth -2 causes a crash in parse-template!

@language css
*/
</t>
<t tx="ekr.20200914053650.2"></t>
<t tx="ekr.20200914053650.5"></t>
</tnodes>
</leo_file>
