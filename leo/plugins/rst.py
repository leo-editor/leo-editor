#@+leo-ver=4-thin
#@+node:edream.111803100242:@thin rst.py
"""If a headline starts with @rst <filename>, double-clicking on it will 
write a file in outline order, with the headlines converted to reStructuredText 
section headings.

If the name of the <filename> has the extension .html, .htm or .tex, and if you have
docutils installed, it will generate HTML or LaTeX, respectively."""

#@@language python
#@@tabwidth -4

# By Josef Dalcolmo: contributed under the same licensed as Leo.py itself.

# EKR: The code now lets other plugins handle @folder and @url nodes.

import leoGlobals as g
import leoPlugins

import os

#@<< about this plugin >>
#@+node:edream.111803100242.1:<<about this plugin >>
#@+at 
#@nonl
# This plugin writes out @text nodes as a reStructuredText file.
# 
# If the filename ends in .html, .htm or .tex and if you have docutils_ (a 
# Python
# module) installed, then it will be written as HTML or LaTeX, respectively.
# 
# Headlines are translated into reStructuredText headlines, e.g. underlined
# depending on the level and empty line separated from body text otherwise, 
# text
# is written as it is. The "#" character is not used for underlining, so it 
# may
# be used for a title as in::
# 
#     #####
#     Title
#     #####
# 
# Otherwise, section underlining is discouraged, since it is automatically 
# generated.
# 
# .. _docutils: http://docutils.sourceforge.net
#@-at
#@nonl
#@-node:edream.111803100242.1:<<about this plugin >>
#@nl
#@<< change log >>
#@+node:edream.111803100242.2:<< change log >>
#@+at 
#@nonl
# Change log:
# 
# - New tree types: @rst has been added.
# 
# - EKR: The code now lets other plugins handle @folder and @url nodes.
# 
# - HTML generation: @rst nodes can now generate HTML, if Python docutils_ are
#   installed. Simply give the filename an extension .htm or .html. You can 
# try
#   this out by renaming the filename in this @rst tree.
# 
# - underlines: I changed the order of the underline characters again. The ">" 
# is
#   doesn't really look good as an underline in my opinion, so I moved it to a 
# very
#   low level.
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
# - JD 2004-09-09 changed 'v' to 'p' in onIconDoubleClick to support the new 
# plugin API of Leo 4.2.
# 
# - JD 2004-09-09 changed headline directive from @rst to @text to become 
# compatible with the rst2 plugin.
# 
# 1.7 EKR 2005-03-07 changed publish() to publish(argv=[''])
#@-at
#@nonl
#@-node:edream.111803100242.2:<< change log >>
#@nl

#@+others
#@+node:edream.111803100242.3:onIconDoubleClick
# by Josef Dalcolmo 2003-01-13
#
# this does not check for proper filename syntax.
# path is the current dir, or the place @folder points to
# this should probably be changed to @path or so.

def onIconDoubleClick(tag,keywords):

    v = keywords.get("p") or keywords.get("v")
    c = keywords.get("c")
    # g.trace(c)

    h = v.headString().strip()
    if g.match_word(h,0,"@text"):
        fname = h[5:]
        ext = os.path.splitext(fname)[1].lower()
        if ext in ('.htm','.html','.tex'):
            #@            << write rST as HTML/LaTeX >>
            #@+node:edream.111803100242.4:<< write rST as HTML/LaTeX >>
            try:
                import docutils
            except ImportError:
                docutils = None
                g.es('HTML/LaTeX generation requires docutils')
            
            if docutils:
                import StringIO
                rstFile = StringIO.StringIO()
                writeTreeAsRst(rstFile, fname, v, c)
                rstText = rstFile.getvalue()
                # Set the writer and encoding for the converted file
                if ext in ('.html','.htm'):
                    writer='html'
                    enc="utf-8"
                else:
                    writer='latex'
                    enc="iso-8859-1"
                #@    << convert rST to HTML/LaTeX >>
                #@+node:edream.111803100242.5:<< convert rST to HTML/LaTeX >>
                # this code snipped has been taken from code contributed by Paul Paterson 2002-12-05
                from docutils.core import Publisher
                from docutils.io import StringOutput, StringInput
                
                pub = Publisher()
                # Initialize the publisher
                pub.source = StringInput(source=rstText)
                pub.destination = StringOutput(pub.settings, encoding=enc)
                pub.set_reader('standalone', None, 'restructuredtext')
                pub.set_writer(writer)
                output = pub.publish(argv=[''])
                #@nonl
                #@-node:edream.111803100242.5:<< convert rST to HTML/LaTeX >>
                #@nl
                convertedFile = file(fname,'w')
                convertedFile.write(output)
                convertedFile.close()
                rstFile.close()
                g.es('written: '+str(fname))
            #@nonl
            #@-node:edream.111803100242.4:<< write rST as HTML/LaTeX >>
            #@nl
        else:
            #@            << write rST file >>
            #@+node:edream.111803100242.6:<< write rST file >>
            rstFile = file(fname,'w')
            writeTreeAsRst(rstFile, fname, v, c)
            rstFile.close()
            g.es('written: '+str(fname))
            #@nonl
            #@-node:edream.111803100242.6:<< write rST file >>
            #@nl
#@-node:edream.111803100242.3:onIconDoubleClick
#@+node:edream.111803100242.7:writeTreeAsRst
def writeTreeAsRst(rstFile, fname, vnode, c):
    'Writes the tree under vnode to the file rstFile (fname is the filename)'
    # we don't write a title, so the titlepage can be customized
    # use '#' for title under/overline
    # 3/7/03
    dict = g.scanDirectives(c,p=vnode)
    encoding = dict.get("encoding",None)
    if encoding == None:
        encoding = c.config.default_derived_file_encoding
    # 3/7/03
    s = g.toEncodedString(fname,encoding,reportErrors=True)
    rstFile.write('.. filename: '+s+'\n')
    rstFile.write('\n')
    # 3/7/03
    s = vnode.bodyString()
    s = g.toEncodedString(s,encoding,reportErrors=True)
    rstFile.write(s+'\n')		# write body of titlepage
    rstFile.write('\n')
    
    toplevel = vnode.level()
    stopHere = vnode.nodeAfterTree()
    v = vnode.threadNext()
    # repeat for all nodes in this tree
    while v != stopHere:
        # 3/7/03
        h = v.headString()
        h = g.toEncodedString(h,encoding,reportErrors=True)
        rstFile.write(h+'\n')
        rstFile.write(underline(h,v.level()-toplevel))
        rstFile.write('\n')
        # 3/7/03
        s = v.bodyString()
        s = g.toEncodedString(s,encoding,reportErrors=True)
        rstFile.write(s+'\n')
        rstFile.write('\n')
        v = v.threadNext()
#@nonl
#@-node:edream.111803100242.7:writeTreeAsRst
#@+node:edream.111803100242.8:underline
# note the first character is intentionally unused, to serve as the underline
# character in a title (in the body of the @rst node)

def underline(h,level):
    str = """#=+*^~"'`-:><_"""[level]
    return str*max(len(h),4)+'\n'
#@nonl
#@-node:edream.111803100242.8:underline
#@-others

if 1: # Ok for unit testing??

    # Register the handlers...
    leoPlugins.registerHandler("icondclick1",onIconDoubleClick)
        
    __version__ = "1.7" # Set version for the plugin handler.
    g.plugin_signon(__name__)
#@nonl
#@-node:edream.111803100242:@thin rst.py
#@-leo
