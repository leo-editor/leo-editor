#@+leo-ver=4-thin
#@+node:ekr.20040331071319:@thin rst2.py
#@<< docstring >>
#@+node:ekr.20050420105800:<< docstring >>
"""A plugin to generate HTML or LaTeX files from reStructured Text
embedded in Leo outlines.

If a headline starts with @rst <filename>, double-clicking on it will 
write a file in outline order, with the headlines converted to reStructuredText 
section headings.

If the name of the <filename> has the extension .html, .htm or .tex, and if you have
docutils installed, it will generate HTML or LaTeX, respectively.

The following settings are presently available: They can be set in the rst2 code
itself, or (maybe?) using @settings trees:
    
rst2_bodyfilter = False
# True: call body_filter to massage text.
# Removes @ignore, @nocolor, @wrap directives.

rst2file = False
# Controls whether to use external file or string.

rst2_pure_document = False
# Controls the following code in writeTreeAsRst
if config.rst2_pure_document or g.match_word(h,0,"@rst"):
    < < handle an rst node > >
    # Removes @ignore, @nocolor, @wrap directives.
    # Removes code blocks if rst2_replace_code_blocks is True.
    # Formats headlines only if rst2_format_headlines is True.
else:
    < < handle a plain node > >
    # Deletes @others from output.
    # Formats headlines only if rst2_format_headlines is False. (opposite of meaning in rst nodes!)
        
rst2_format_headlines = False
# Used differently.  See rst2_pure_document.
    
rst2_http_server_support = True
# True:
# 1. add_node_marker writes a string using generate_node_marker.
# Generates 'http-node-marker-'+str(number), where number is config.node_counter (incremented each time add_node_marker is called.
# 2. Enables the following code in writeTreeAsRst
    if config.tag == 'open2':
        http_map = config.http_map
    else:
        http_map = {}
        config.anchormap = {}
       # maps v nodes to markers.
        config.node_counter = 0
    # [snip] code to write the tree
    if config.rst2_http_server_support:
        config.http_map = http_map
# 3. http_support_main does nothing unless this option is True.
# False: add_node_marker does nothing.

rst2_clear_attributes = False
    # Deletes p.v.rst2_http_attributename from all nodes after writing.
    # Deletes p.v.unknownAttributes if it then becomes empty.
    
rst2_run_on_window_open = False
# Runs an alternative 'main line' in onFileOpen when a new window is opened.

rst2_replace_code_blocks = True
# See notes for rst2_pure_document. (Uses do_replace_code_blocks)
< < define alternate code block implementation> >
# Don't know what to do here: Can someone make a suggestion?
#import docutils.parsers.rst.directives.admonitions
#import docutils.parsers.rst.directives.body
# docutils.parsers.rst.directives._directives['code-block'] = docutils.parsers.rst.directives.body.block 
# docutils.parsers.rst.directives.register_directive('code-block', docutils.parsers.rst.directives.admonitions.admonition)
#docutils.parsers.rst.directives._directives['code-block'] = docutils.parsers.rst.directives.body.pull_quote 
# g.es("Registered some alternate implementation for code-block directive")
config.do_replace_code_blocks = config.rst2_replace_code_blocks
        
rst2_install_menu_item_in_edit_menu = True
# True: install 'Transform rst text in subtree'command to Edit menu.

rst2_node_begin_marker = 'http-node-marker-'
rst2_http_attributename = 'rst_http_attribute'

"""
#@nonl
#@-node:ekr.20050420105800:<< docstring >>
#@nl

# By Josef Dalcolmo: contributed under the same licensed as Leo.py itself.

#@<< imports >>
#@+node:ekr.20050420105800.1:<< imports >>

import leoGlobals as g
import leoPlugins

import os
import ConfigParser
from HTMLParser import HTMLParser
from pprint import pprint
try:
    import sys
    dir = os.path.split(__file__)[0]
    if dir not in sys.path:
        sys.path.append(dir)
    import mod_http
    from mod_http import set_http_attribute, get_http_attribute, reconstruct_html_from_attrs
except:
    mod_http = None
#@nonl
#@-node:ekr.20050420105800.1:<< imports >>
#@nl
#@<< change log >>
#@+node:ekr.20040331071319.2:<< change log >>
#@+at 
#@nonl
# Change log:
# 
# - JD 2003-03-10 (rev 1.3): some more corrections to the unicode-> encoding 
# translation.
#   No only check for missing docutils (doesn't mask other errors any more).
# 
# - JD 2003-03-11 (rev 1.4): separated out the file launching code to a 
# different pluging.
# 
# - 2003-11-02 Added generation of LaTeX files, just make the extension of the 
# filename '.tex'. --Timo Honkasalo
# 
# - 2003-12-24 S Zatz modifications to introduce concept of plain @rst nodes 
# to improve program documentation
# 
# - 2004-04-08 EKR:
#     - Eliminated "comment" text at start of nodes.
#     - Rewrote code that strips @nocolor, @ignore and @wrap directives from 
# start of text.
#     - Changed code to show explicitly that it uses positions.
#     - Added comments to << define code-block>>
#     - Added div.code-block style to silver_city.css (see documentation)
#     - Rewrote documentation.
# 2.2 EKR 2005-03-07 changed publish() to publish(argv=[''])
# 
# 2.3 bwmulder
#     - added various options which can be set with @settings directive
#     - add support for mod_http plugin.
#     - added possible settings to the beginning of the Leo file
# 2.4 EKR:
#     - Call onFileOpen from both "new" and "open2" hooks.
#@-at
#@nonl
#@-node:ekr.20040331071319.2:<< change log >>
#@nl

#@+others
#@+node:bwmulder.20050319123911:http plugin interface
#@+doc
# if enabled, this plugin stores information for the http plugin.
# 
# Each node can have one additional attribute, with the name 
# config.rst_http_attributename, which is a list.
# 
# The first three elements are stack of tags, the rest is html code.
# 
# [<tag n start>, <tag n end>, <other stack elements>, <html line 1>, <html 
# line 2>, ...]
# 
# <other stack elements has the same structure:
#     [<tag n-1 start>, <tag n-1 end>, <other stack elements>]
#@-doc
#@nonl
#@-node:bwmulder.20050319123911:http plugin interface
#@+node:bwmulder.20050314132625:config
class config:
    # 
    rst2_bodyfilter = False
    rst2file = False
    rst2_pure_document = False
    rst2_http_server_support = True
    rst2_format_headlines = False
    # number_headlines = False
    # warnofdrags = False
    rst2_clear_attributes = False
    rst2_run_on_window_open = False
    rst2_replace_code_blocks = True
    
    # debug flags: ignore in normal use
    rst2_debug_handle_starttag = False
    rst2_debug_handle_endtag = False
    rst2_debug_store_lines = False
    rst2_debug_show_unknownattributes = False
    rst2_debug_node_html_1 = False
    rst2_debug_anchors = False
    rst2_debug_before_and_after_replacement = False
    rst2_install_menu_item_in_edit_menu = True
    
    # These are really configuration options.
    rst2_node_begin_marker = 'http-node-marker-'
    rst2_http_attributename = 'rst_http_attribute'
    
    firstCall = True
    # set to False after the optional menu is installed.
    
    # Some data is also stored in the config class
    http_map = None
    # Maps node anchors to node.
    # A node anchor is a marker beginning with
    # rst2_node_begin_marker.
    # It is currently assumed that such a marker
    # does not occur in the rst document.
    
    tag = None
    # either doubleclick or open2.
    
    current_file = None
    
    node_counter = 0
    # Used to mark the beginning of the html code for each new
    # node.
    
    do_replace_code_blocks = False
#@nonl
#@-node:bwmulder.20050314132625:config
#@+node:bwmulder.20050327204614:transform_rst2_text_in_subtree
def transform_rst2_text_in_subtree(c):
    
    class callOnFileOpen(object):
        """
        Call onFileOpen passing the commander c.
        """
        def __init__(self):
            self.c = c
        def __call__(self):
            onFileOpen("menuItem", {"new_c": self.c})
            
    editMenu = c.frame.menu.getMenu('Edit')
        
    newEntries = (
            ("-", None, None),
            ("Transform rst2 text in subtree", "", callOnFileOpen))
        
    c.frame.menu.createMenuEntries(editMenu, newEntries)
#@-node:bwmulder.20050327204614:transform_rst2_text_in_subtree
#@+node:bwmulder.20050320000243:onFileOpen
def onFileOpen(tag, keywords):
    # c,old_c,new_c,fileName):
    c = keywords["new_c"]
    applyConfiguration(c)
    if config.firstCall and config.rst2_install_menu_item_in_edit_menu:
        config.firstCall = False
        transform_rst2_text_in_subtree(c)
    ignoreset = {}
    if c.config.getBool("rst2_run_on_open_window"):
    # if config.rst2_run_on_window_open:
        http_map = {}
        anchormap = {}
        config.node_counter = 0
        found_rst_trees = False
        root = c.currentVnode()
        
        if tag == 'open2':
            iterator = c.allNodes_iter(root)
        else:
            iterator = root.self_and_subtree_iter()
        for p in iterator:
            if p.v not in ignoreset:
                s = p.v.headString()
                if s.startswith("@rst ") and len(s.split()) >= 2:
                    for p1 in p.subtree_iter():
                        ignoreset[p1.v] = True
                    try:
                        config.http_map = {}
                        config.anchormap = {}
                        onIconDoubleClick("open2", {"c": c, "p": p})
                        http_map.update(config.http_map)
                        anchormap.update(config.anchormap)
                        found_rst_trees = True
                    except SystemExit, s:
                        g.es("Formatting failed for %s" % p, color='red')
        if found_rst_trees:
            config.http_map = http_map
            config.anchormap = anchormap
            relocate_references() 
          
            config.http_map = None
            config.anchormap = None
            g.es('html updated for html plugin', color="blue")
        if config.rst2_clear_attributes:
            g.es("http attributes cleared")
#@-node:bwmulder.20050320000243:onFileOpen
#@+node:ekr.20040331071319.3:onIconDoubleClick
# by Josef Dalcolmo 2003-01-13
#
# this does not check for proper filename syntax.
# path is the current dir, or the place @folder points to
# this should probably be changed to @path or so.

def onIconDoubleClick(tag,keywords):

    c = keywords.get("c")
    p = keywords.get("p")
    # g.trace(c)

    if not c or not p:
        return
    
    applyConfiguration(c)
    config.tag = tag

    h = p.headString().strip()

    if g.match_word(h,0,"@rst"):
        if len(h) > 5:
            fname = h[5:]
            ext = os.path.splitext(fname)[1].lower()
            if ext in ('.htm','.html','.tex'):
                #@                << write rST as HTML/LaTeX >>
                #@+node:ekr.20040331071319.4:<< write rST as HTML/LaTeX >>
                try:
                    import docutils
                except:
                    g.es('HTML/LaTeX generation requires docutils')
                    return
                else:
                    import docutils.parsers.rst
                    from docutils.core import Publisher
                    from docutils.io import StringOutput, StringInput, FileOutput,FileInput
                    import StringIO
                    
                # Set the writer and encoding for the converted file
                if ext in ('.html','.htm'):
                    writer='html' ; enc="utf-8"
                else:
                    writer='latex' ; enc="iso-8859-1"
                
                syntax = False
                if writer == 'html':
                    try:
                        import SilverCity
                        #@        << define code-block >>
                        #@+node:ekr.20040331071319.5:<< define code-block >>
                        def code_block(name,arguments,options,content,lineno,content_offset,block_text,state,state_machine):
                            
                            """Create a code-block directive for docutils."""
                            
                            # See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252170
                            language = arguments[0]
                            module = getattr(SilverCity,language)
                            generator = getattr(module,language+"HTMLGenerator")
                            io = StringIO.StringIO()
                            generator().generate_html(io, '\n'.join(content))
                            html = '<div class="code-block">\n%s\n</div>\n'%io.getvalue()
                            raw = docutils.nodes.raw('',html, format='html') #(self, rawsource='', text='', *children, **attributes):
                            return [raw]
                            
                        # These are documented at http://docutils.sourceforge.net/spec/howto/rst-directives.html.
                        code_block.arguments = (
                            1, # Number of required arguments.
                            0, # Number of optional arguments.
                            0) # True if final argument may contain whitespace.
                        
                        # A mapping from option name to conversion function.
                        code_block.options = {
                            'language' :
                            docutils.parsers.rst.directives.unchanged # Return the text argument, unchanged
                        }
                        
                        code_block.content = 1 # True if content is allowed.
                         
                        # Register the directive with docutils.
                        docutils.parsers.rst.directives.register_directive('code-block',code_block)
                        
                        config.do_replace_code_blocks = False
                        #@nonl
                        #@-node:ekr.20040331071319.5:<< define code-block >>
                        #@nl
                        syntax = True
                    except ImportError:
                        g.es('SilverCity not present so no syntax highlighting')
                        #@        << define alternate code block implementation>>
                        #@+node:bwmulder.20050326114320: << define alternate code block implementation>>
                        # Don't know what to do here: Can someone make a suggestion?
                        #import docutils.parsers.rst.directives.admonitions
                        #import docutils.parsers.rst.directives.body
                        # docutils.parsers.rst.directives._directives['code-block'] = docutils.parsers.rst.directives.body.block 
                        # docutils.parsers.rst.directives.register_directive('code-block', docutils.parsers.rst.directives.admonitions.admonition)
                        #docutils.parsers.rst.directives._directives['code-block'] = docutils.parsers.rst.directives.body.pull_quote 
                        # g.es("Registered some alternate implementation for code-block directive")
                        config.do_replace_code_blocks = config.rst2_replace_code_blocks
                        #@-node:bwmulder.20050326114320: << define alternate code block implementation>>
                        #@nl
                
                if config.rst2file:
                    rstFileName = os.path.splitext(fname)[0] + ".txt"
                    rstFile = file(rstFileName, "w")
                    g.es("Using %s as rst file" % rstFileName)
                else:
                    rstFile = StringIO.StringIO()
                config.current_file = fname
                writeTreeAsRst(rstFile,fname,p,c,syntax=syntax)
                if config.rst2file:
                    rstFile.close()
                else:
                    rstText = rstFile.getvalue()
                
                # This code snipped has been taken from code contributed by Paul Paterson 2002-12-05.
                pub = Publisher()
                if config.rst2file:
                    pub.source = FileInput(source_path=rstFileName)
                    pub.destination = FileOutput(destination_path=fname, encoding='unicode')
                else:
                    pub.source = StringInput(source=rstText)
                    pub.destination = StringOutput(pub.settings, encoding=enc)
                pub.set_reader('standalone', None, 'restructuredtext')
                pub.set_writer(writer)
                output = pub.publish(argv=[''])
                
                if config.rst2file:
                    pass
                else:
                    convertedFile = file(fname,'w')
                    convertedFile.write(output)
                    convertedFile.close()
                rstFile.close()
                writeFullFileName(fname)
                return http_support_main(tag, fname)
                
                #@-node:ekr.20040331071319.4:<< write rST as HTML/LaTeX >>
                #@nl
            else:
                #@                << write rST file >>
                #@+node:ekr.20040331071319.6:<< write rST file >>
                rstFile = file(fname,'w')
                writeTreeAsRst(rstFile,fname,p,c)
                rstFile.close()
                writeFullFileName(fname)
                #@nonl
                #@-node:ekr.20040331071319.6:<< write rST file >>
                #@nl
        else:
            # if the headline only contains @rst then open the node and its parent in text editor
            # this works for me but needs to be generalized and should probably be a component
            # of the open_with plugin.
            if 0:
                c.openWith(("os.startfile", None, ".txt"))
                c.selectVnode(p.parent())
                c.openWith(("os.startfile", None, ".tp"))
#@nonl
#@-node:ekr.20040331071319.3:onIconDoubleClick
#@+node:ekr.20040811064922:writeFullFileName
def writeFullFileName (fname):
    
    path = g.os_path_join(os.getcwd(),fname)
    path = g.os_path_abspath(path)
    
    g.es('rst written: ' + path,color="blue")
#@nonl
#@-node:ekr.20040811064922:writeFullFileName
#@+node:bwmulder.20050326125712:replace_code_block_directive
def replace_code_block_directive(line):
    if u"code-block::" in line:
        parts = line.split()
        if len(parts) == 3 and (parts[0] == '..') and (parts[1]=='code-block::'):
            line = '%s code::\n' % parts[2]
    return line
#@nonl
#@-node:bwmulder.20050326125712:replace_code_block_directive
#@+node:ekr.20040331071319.7:writeTreeAsRst & add_node_marker
def writeTreeAsRst(rstFile,fname,p,c,syntax=False):
    
    'Write the tree under position p to the file rstFile (fname is the filename)'
    
    def add_node_marker():
        if config.rst2_http_server_support:
            config.node_counter += 1
            marker = rst_htmlparser.generate_node_marker(config.node_counter)
            config.last_marker = marker
            http_map[marker] = p.copy()
            # the p.copy is necessary, since otherwise the
            # position is modified and unusable later.
            rstFile.write("\n\n.. _%s:\n\n" % marker)
            
    # we don't write a title, so the titlepage can be customized
    # use '#' for title under/overline
    directives = g.scanDirectives(c,p=p) # changed name because don't want to use keyword dict
    #@    << set encoding >>
    #@+node:ekr.20040408160625.1:<< set encoding >>
    encoding = directives.get("encoding",None)
    if encoding == None:
        encoding = c.config.default_derived_file_encoding
    #@nonl
    #@-node:ekr.20040408160625.1:<< set encoding >>
    #@nl
    #@    << set code_dir >>
    #@+node:ekr.20040403202850:<< set code_dir >>
    if syntax:
        lang_dict = {'python':'Python', 'ruby':'Ruby', 'perl':'Perl', 'c':'CPP'}
        language = directives['language']
        # SilverCity modules have first letter in caps
        if language in lang_dict:
            code_dir = '**code**:\n\n.. code-block:: %s\n\n' % lang_dict[language]
        else:
            code_dir = '**code**:\n\n.. class:: code\n..\n\n::\n\n'
    else:
        code_dir = '**code**:\n\n.. class:: code\n..\n\n::\n\n'
    #@nonl
    #@-node:ekr.20040403202850:<< set code_dir >>
    #@nl
    s = g.toEncodedString(fname,encoding,reportErrors=True)
    rstFile.write('.. filename: '+s+'\n')
    rstFile.write('\n')

    if config.rst2_bodyfilter:
        s = bodyfilter(p)
    else:
        s = p.bodyString()
    s = g.toEncodedString(s,encoding,reportErrors=True)
    rstFile.write(s+'\n')		# write body of titlepage.
    rstFile.write('\n')
    
    toplevel = p.level()+1 # Dec 20
    h = p.headString()
    
    if config.rst2_http_server_support:
        if config.tag == 'open2':
            http_map = config.http_map
        else:
            http_map = {}
            config.anchormap = {}
           # maps v nodes to markers.
            config.node_counter = 0
    for p in p.subtree_iter():
        h = p.headString().strip()
        if config.rst2_pure_document or g.match_word(h,0,"@rst"):
            #@            << handle an rst node >>
            #@+node:ekr.20040403202850.1:<< handle an rst node >>
            s = p.bodyString()
            s = g.toEncodedString(s,encoding,reportErrors=True)
            
            # Skip any leading @ignore, @nocolor, @wrap directives.
            while (
                g.match_word(s,0,"@ignore") or
                g.match_word(s,0,"@nocolor") or
                g.match_word(s,0,"@wrap")
            ):
                i = g.skip_line(s,0)
                s = s[i:]
            
            add_node_marker()    
            
            if config.rst2_format_headlines:
                rstFile.write(h+'\n')
                rstFile.write(underline(h,p.level()-toplevel))
                rstFile.write('\n')
            
            if config.do_replace_code_blocks and 'code-block::' in s:
                s = '\n'.join([replace_code_block_directive(line) for line in s.split("\n")])
            
            rstFile.write('%s\n\n'%s.strip())
            #@nonl
            #@-node:ekr.20040403202850.1:<< handle an rst node >>
            #@nl
        else:
            #@            << handle a plain node >>
            #@+node:ekr.20040403202850.2:<< handle a plain node >>
            if g.match_word(h,0,"@file-nosent"):
                h = h[13:]
            h = g.toEncodedString(h,encoding,reportErrors=True)
            if config.rst2_bodyfilter:
                s = bodyfilter(p)
            else:
                s = p.bodyString()
            s = g.toEncodedString(s,encoding,reportErrors=True)
            
            add_node_marker()    
            
            if config.rst2_format_headlines:
                pass
            else:
                rstFile.write(h+'\n')
                rstFile.write(underline(h,p.level()-toplevel))
                rstFile.write('\n')
            
            if s.strip():
                rstFile.write(code_dir)
                s = s.split('\n')
                for linenum,linetext in enumerate(s[:-1]):
                    if "@others" in linetext: #deleting lines with @other directive from output
                        continue
                    rstFile.write('\t%2d  %s\n'%(linenum+1,linetext))
            
            rstFile.write('\n')
            #@nonl
            #@-node:ekr.20040403202850.2:<< handle a plain node >>
            #@nl
        #@        << clear attributes >>
        #@+node:bwmulder.20050315150045:<< clear attributes >>
        if config.rst2_clear_attributes:
            if hasattr(p.v, 'unknownAttributes'):
                if p.v.unknownAttributes.has_key(config.rst2_http_attributename):
                    del p.v.unknownAttributes[config.rst2_http_attributename]
                    if p.v.unknownAttributes == {}:
                        del p.v.unknownAttributes
        #@nonl
        #@-node:bwmulder.20050315150045:<< clear attributes >>
        #@nl
    add_node_marker()
    if config.rst2_http_server_support:
        config.http_map = http_map
#@-node:ekr.20040331071319.7:writeTreeAsRst & add_node_marker
#@+node:bwmulder.20050314131619:applyConfiguration
def applyConfiguration (c):

    """Called when the user presses the "Apply" button on the Properties form.
 
    Default: behave like the previous plugin.
    """

    def getboolean(name):
        value = getattr(config, name)
        newvalue = c.config.getBool(name)
        if newvalue is not None:
            setattr(config, name, newvalue)
        
    getboolean("rst2file")
    getboolean("rst2_bodyfilter")
    getboolean("rst2_clear_attributes")
    getboolean("rst2_http_server_support")
    if config.rst2_http_server_support and not mod_http:
        g.es("Resetting rst2_http_server_support because mod_http plugin was not imported successfully", color='red')
        config.rst2_http_server_support = False
    getboolean("rst2_pure_document")
    getboolean("rst2_format_headlines")
    # getboolean("rst2_warnofdrags")
    getboolean("rst2_run_on_window_open")
    
    getboolean("rst2_debug_handle_endtag")
    getboolean("rst2_debug_store_lines")
    getboolean("rst2_debug_handle_starttag")
    getboolean("rst2_debug_show_unknownattributes")
    getboolean("rst2_debug_node_html_1")
    getboolean("rst2_debug_anchors")
    getboolean("rst2_debug_before_and_after_replacement")
    getboolean("rst2_install_menu_item_in_edit_menu")

#@-node:bwmulder.20050314131619:applyConfiguration
#@+node:bwmulder.20041011145032:bodyfilter
def bodyfilter(p):
    s = p.bodyString()
    while (s.startswith("@ignore") or
           s.startswith("@nocolor") or
           s.startswith("@wrap")):
       i = g.skip_line(s,0)
       s = s[i:]
    return s
#@-node:bwmulder.20041011145032:bodyfilter
#@+node:ekr.20040331071319.8:underline
# note the first character is intentionally unused, to serve as the underline
# character in a title (in the body of the @rst node)

def underline(h,level):
    
    """Return the underlining string to be used at the given level for headline h."""

    str = """#=+*^~"'`-:><_"""[level]

    return str*max(len(h),4)+'\n'
#@-node:ekr.20040331071319.8:underline
#@+node:bwmulder.20050319191929:http related stuff
#@+node:bwmulder.20050320092000:http_support_main
def http_support_main(tag, fname):
    if config.rst2_http_server_support:
        set_initial_http_attributes(fname)
        find_anchors()
        if tag == 'open2':
            return True
        
        # We relocate references here if we are only running
        # for one file, otherwise we must postpone the
        # relocation until we have processed all files.
        relocate_references() 
      
        config.http_map = None
        config.anchormap = None
        g.es('html updated for html plugin', color="blue")
        if config.rst2_clear_attributes:
            g.es("http attributes cleared")
#@nonl
#@-node:bwmulder.20050320092000:http_support_main
#@+node:bwmulder.20050319191929.1:general routines
#@+node:bwmulder.20050319181934:link_anchor_parser
class link_anchor_parser(HTMLParser):
    #@    @+others
    #@+node:bwmulder.20050319181934.1:docstring
    """
    This subclass of HTMLParser contains functions to recognise anchors and links.
    """
    #@nonl
    #@-node:bwmulder.20050319181934.1:docstring
    #@+node:bwmulder.20050319181934.2:is_anchor
    def is_anchor(self, tag, attrs):
        if tag != 'a':
            return False
        for name, value in attrs:
            if name == 'name':
                return True
        return False
      
    #@-node:bwmulder.20050319181934.2:is_anchor
    #@+node:bwmulder.20050323091905:is_link
    def is_link(self, tag, attrs):
        if tag != 'a':
            return False
        for name, value in attrs:
            if name == 'href':
                return True
        return False
      
    #@-node:bwmulder.20050323091905:is_link
    #@-others
#@nonl
#@-node:bwmulder.20050319181934:link_anchor_parser
#@+node:bwmulder.20050319152820.1:http_attribute_iter
def http_attribute_iter():
    for p in config.http_map.values():
        attr = get_http_attribute(p)
        if attr:
            yield (p, attr)
#@-node:bwmulder.20050319152820.1:http_attribute_iter
#@-node:bwmulder.20050319191929.1:general routines
#@+node:bwmulder.20050314184440:rst_htmlparser
class rst_htmlparser(link_anchor_parser):
    #@    @+others
    #@+node:bwmulder.20050319111254:docstring
    """
    The responsibility of the html parser is:
        1. to find out which html belongs to which node.
        2. to keep a stack of html markings which proceed each node.
        
    Later, we have to relocate inter-file links: if a reference to another location
    is in a file, we must change the link.
    
    """
    #@nonl
    #@-node:bwmulder.20050319111254:docstring
    #@+node:bwmulder.20050315115739:__init__
    def __init__(self, http_map):
        HTMLParser.__init__(self)
        self.stack = None
        # The stack contains lists of the form:
            # [text1, text2, previous].
            # text1 is the opening tag
            # text2 is the closing tag
            # previous points to the previous stack element
        
        self.http_map = http_map
        # see remark in config class
            
        self.node_marker_stack = []
        # self.node_marker_stack.pop() returns True for a closing
        # tag if the opening tag identified an anchor belonging to a vnode.
        
        self.node_code = []
        # Accumulated html code. Once the hmtl code is assigned a vnode,
        # it is deleted here.
        
        self.deleted_lines = 0
        # Number of lines deleted in self.node_code
        
        self.endpos_pending = False
        # self.node_code[0:self.endpos_pending] should not be included in
        # the html code stored in a vnode.
        
        self.last_position = None
        # Last vnode; we must attach html code to this node.
            
    
    #@-node:bwmulder.20050315115739:__init__
    #@+node:bwmulder.20050315115739.1:handle_starttag
    def handle_starttag(self, tag, attrs):
        """
        1. Find out if the current tag is an achor.
        2. If it is an anchor, we check if this anchor marks the beginning of a new 
           node
        3. If a new node begins, then we might have to store html code in the
           previous code.
        4. In any case, put the new tag on the stack.
        """
        is_node_marker = False
        if self.is_anchor(tag, attrs):
            for name, value in attrs:
                if name == 'name' and value.startswith(config.rst2_node_begin_marker):
                    is_node_marker = True
                    break
            if is_node_marker:
                is_node_marker = value
                line, column = self.getpos()
                if self.last_position:
                    lines = self.node_code[:]
                    lines[0] = lines[0][self.startpos:]
                    del lines[line - self.deleted_lines - 1:]
                    if config.rst2_debug_store_lines:
                        print "rst2: Storing in", self.last_position, ":"
                        print lines
                    get_http_attribute(self.last_position).extend(lines)
    
                    if config.rst2_debug_show_unknownattributes:
                        print "rst2: unknownAttributes[config.rst2_http_attributename]"
                        print "For:", self.last_position
                        pprint(get_http_attr(self.last_position))
                                
                if self.deleted_lines < line - 1:
                    del self.node_code[:line - 1 - self.deleted_lines]
                    self.deleted_lines = line - 1
                    self.endpos_pending = True
        if config.rst2_debug_handle_starttag:
            from pprint import pprint
            print "rst2: handle_starttag:", tag, attrs, is_node_marker
        starttag = self.get_starttag_text( ) 
        self.stack = [starttag, None, self.stack]
        self.node_marker_stack.append(is_node_marker)
                
    #@nonl
    #@-node:bwmulder.20050315115739.1:handle_starttag
    #@+node:bwmulder.20050315115739.2:handle_endtag
    def handle_endtag(self, tag):
        """
        1. Set the second element of the current top of stack.
        2. If this is the end tag for an anchor for a node,
           store the current stack for that node.
        """
        self.stack[1] = "</" + tag + ">"
        if config.rst2_debug_handle_endtag:
            from pprint import pprint
            print "rst2: handle_endtag:", tag
            pprint(self.stack)
        if self.endpos_pending:
            line, column = self.getpos()
            self.startpos = self.node_code[0].find(">", column) + 1
            self.endpos_pending = False
        is_node_marker = self.node_marker_stack.pop()
        if is_node_marker and not config.rst2_clear_attributes:
            self.last_position = self.http_map[is_node_marker]
            if is_node_marker != config.last_marker:
                set_http_attribute(self.http_map[is_node_marker], self.stack)
        self.stack = self.stack[2]
        
    #@nonl
    #@-node:bwmulder.20050315115739.2:handle_endtag
    #@+node:bwmulder.20050315115739.3:generate_node_marker
    def generate_node_marker(cls, number):
        
        """
        Generate a node marker for 
        """
        return config.rst2_node_begin_marker + ("%s" % number)
        
    generate_node_marker = classmethod(generate_node_marker)
        
    
    #@-node:bwmulder.20050315115739.3:generate_node_marker
    #@+node:bwmulder.20050315134705:feed
    def feed(self, line):
        self.node_code.append(line)
        HTMLParser.feed(self, line)
    #@-node:bwmulder.20050315134705:feed
    #@-others
#@nonl
#@-node:bwmulder.20050314184440:rst_htmlparser
#@+node:bwmulder.20050319180047:anchor_htmlparser
class anchor_htmlparser(link_anchor_parser):
    #@    @+others
    #@+node:bwmulder.20050319180047.1:docstring
    """
    This htmlparser does the first step of relocating: finding all the anchors within the html node.
    
    Each anchor is mapped to a tuple:
        (current_file, vnode).
        
    Filters out markers which mark the beginning of the html code for a node.
    """
    #@nonl
    #@-node:bwmulder.20050319180047.1:docstring
    #@+node:bwmulder.20050319235437:__init__
    def __init__(self, vnode, first_node):
        HTMLParser.__init__(self)
        self.vnode = vnode
        self.anchormap = config.anchormap
        self.first_node = first_node
    #@-node:bwmulder.20050319235437:__init__
    #@+node:bwmulder.20050319181934.3:handle_starttag
    def handle_starttag(self, tag, attrs):
        """
        1. Find out if the current tag is an achor.
        2. If the current tag is an anchor, update the mapping;
             anchor -> vnode
        """
        if not self.is_anchor(tag, attrs):
            return
        if self.first_node:
            self.anchormap[config.current_file] = (config.current_file, self.vnode)
            self.first_node = False
        for name, value in attrs:
            if name == 'name':
                if not value.startswith(config.rst2_node_begin_marker):
                    self.anchormap[value] = (config.current_file, self.vnode)
                  
    #@nonl
    #@-node:bwmulder.20050319181934.3:handle_starttag
    #@-others
#@-node:bwmulder.20050319180047:anchor_htmlparser
#@+node:bwmulder.20050320102006:link_htmlparser
class link_htmlparser(link_anchor_parser):
    #@    @+others
    #@+node:bwmulder.20050320102006.1:docstring
    """
    This html parser does the second step of relocating links:
        1. It scans the html code for links.
        2. If there is a link which links to a previously processed file, then
           this link is changed so that it now refers to the node.
    """
    #@nonl
    #@-node:bwmulder.20050320102006.1:docstring
    #@+node:bwmulder.20050320102006.2:__init__
    def __init__(self, vnode):
        HTMLParser.__init__(self)
        self.vnode = vnode
        self.anchormap = config.anchormap
        self.replacements = []
    #@-node:bwmulder.20050320102006.2:__init__
    #@+node:bwmulder.20050320102006.3:handle_starttag
    def handle_starttag(self, tag, attrs):
        """
        1. Find out if the current tag is an achor.
        2. If the current tag is an anchor, update the mapping;
             anchor -> vnode
        """
        if not self.is_link(tag, attrs):
            return
        for name, value in attrs:
            if name == 'href':
                href = value
                href_parts = href.split("#")
                if len(href_parts) == 1:
                    href_a = href_parts[0]
                else:
                    href_a = href_parts[1]
                if not href_a.startswith(config.rst2_node_begin_marker):
                    if href_a in self.anchormap:
                        href_file, href_node = self.anchormap[href_a]
                        http_node_ref = mod_http.node_reference(href_node)
                        line, column = self.getpos()
                        self.replacements.append((line, column, href, href_file, http_node_ref))
                                
    #@nonl
    #@-node:bwmulder.20050320102006.3:handle_starttag
    #@+node:bwmulder.20050320155022:get_replacements
    def get_replacements(self):
        return self.replacements
    #@nonl
    #@-node:bwmulder.20050320155022:get_replacements
    #@-others
#@-node:bwmulder.20050320102006:link_htmlparser
#@+node:bwmulder.20050319131813:set_initial_http_attributes
def set_initial_http_attributes(filename):
    http_map = config.http_map
    f = file(filename)
    parser = rst_htmlparser(config.http_map)
    line = f.readline()
    while line:
        parser.feed(line)
        line = f.readline()

#@-node:bwmulder.20050319131813:set_initial_http_attributes
#@+node:bwmulder.20050319131813.1:relocate_references
def relocate_references():
    relocate_references_using_anchormap()
#@-node:bwmulder.20050319131813.1:relocate_references
#@+node:bwmulder.20050319152820:find_anchors
def find_anchors():
    """
    Find the anchors in all the nodes.
    """
    first_node = True
    for vnode, attrs in http_attribute_iter():
        html = reconstruct_html_from_attrs(attrs)
        if config.rst2_debug_node_html_1:
            pprint(html)
        parser = anchor_htmlparser(vnode, first_node)
        for line in html:
            parser.feed(line)
        first_node = parser.first_node
    if config.rst2_debug_anchors:
        print "Anchors found:"
        pprint(config.anchormap)
#@-node:bwmulder.20050319152820:find_anchors
#@+node:bwmulder.20050319153321:relocate_references_using_anchormap
def relocate_references_using_anchormap():
    for vnode, attr in http_attribute_iter():
        if config.rst2_debug_before_and_after_replacement:
            print "Before replacement:", vnode
            pprint (attr)
        http_lines = attr[3:]
        parser = link_htmlparser(vnode)
        for line in attr[3:]:
            parser.feed(line)
        replacements = parser.get_replacements()
        replacements.reverse()
        for line, column, href, href_file, http_node_ref in replacements:
            marker_parts = href.split("#")
            if len(marker_parts) == 2:
                marker = marker_parts[1]
                replacement = "%s#%s" % (http_node_ref, marker)
                attr[line+2] = attr[line+2].replace('href="%s"' % href, 'href="%s"' % replacement)
            else:
                filename = marker_parts[0]
                attr[line+2] = attr[line+2].replace('href="%s"' % href, 'href="%s"' % http_node_ref)
    if config.rst2_debug_before_and_after_replacement:
            print "After replacement"
            pprint (attr)
            for i in range(3): print
            

#@-node:bwmulder.20050319153321:relocate_references_using_anchormap
#@-node:bwmulder.20050319191929:http related stuff
#@-others

if 1: # Ok for unit testing.
    leoPlugins.registerHandler("icondclick1",onIconDoubleClick)
    leoPlugins.registerHandler(("new","open2"), onFileOpen)
    __version__ = "2.4"

    g.plugin_signon(__name__)
#@nonl
#@-node:ekr.20040331071319:@thin rst2.py
#@-leo
