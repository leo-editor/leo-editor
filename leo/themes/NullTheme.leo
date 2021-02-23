<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2"/>
<globals/>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20180312111155.1"><vh>Read me</vh></v>
<v t="ekr.20180312110809.1"><vh>Theme Tests</vh>
<v t="ekr.20180314052441.1"><vh>Syntax coloring template</vh>
<v t="ekr.20180314052441.2"><vh>&lt;&lt; defined section &gt;&gt;</vh></v>
</v>
<v t="ekr.20180312110809.4"><vh>Test g.es(color=*)</vh></v>
<v t="ekr.20180312110809.5"><vh>g.error/note/warning test</vh></v>
</v>
<v t="ekr.20180318145515.1"><vh>@settings</vh>
<v t="ekr.20200914053650.138"><vh>@data qt-gui-plugin-style-sheet</vh></v>
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
<t tx="ekr.20180312111155.1" str_leo_pos="2,0,3">An empty theme, using all defaults.</t>
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
<t tx="ekr.20200914053650.138">/*

  NullThemek.leo: @data qt-gui-plugin-style-sheet.

  at-tabwidth -2 causes a crash in parse-template!

@language css
*/</t>
</tnodes>
</leo_file>
