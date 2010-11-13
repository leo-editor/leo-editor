#@+leo-ver=5-thin
#@+node:timo.20050213160555: * @file bibtex.py

#@+<< docstring >>
#@+node:ekr.20050912175750: ** << docstring >>
r''' Manages BibTeX files with Leo.

Create a bibliographic database by
putting '@bibtex filename' in a headline. Entries are added as nodes, with
'@entrytype key' as the headline, and the contents of the entry in body text.
The plugin will automatically insert a template for the entry in the body pane
when a new entry is created (hooked to pressing enter when typing the headline
text). The templates are defined in dictionary 'templates' in the \<\<globals\>\>
section, by default containing all required fields for every entry.

The file is written by double-clicking the node. Thus the following outline::

    -@bibtex biblio.bib
     +@book key
      author = {A. Uthor},
      year = 1999

will be written in the file 'biblio.bib' as::

    @book{key,
    author = {A. Uthor},
    year= 1999}

Strings are defined in @string nodes and they can contain multiple entries.
All @string nodes are written at the start of the file. Thus the following
outline::

    -@bibtext biblio.bib
     +@string
      j1 = {Journal1}
     +@article AUj1
      author = {A. Uthor},
      journal = j1
     +@string
      j2 = {Journal2}
      j3 = {Journal3}

Will be written as::

    @string{j1 = {Journal1}}
    @string{j2 = {Journal2}}
    @string{j3 = {Journal3}}

    @article{AUj1,
    author = {A. Uthor},
    journal = j1}

No error checking is made on the syntax. The entries can be organized under
nodes --- if the headline doesn't start with '@', the headline and body text are
ignored, but the child nodes are parsed as usual.

BibTeX files can be imported by creating an empty node with '@bibtex filename'
in the headline. Double-clicking it will read the file 'filename' and parse it
into a @bibtex tree. No syntax checking is made, 'filename' is expected to be a
valid BibTeX file.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

# By Timo Honkasalo: contributed under the same license as Leo.py itself.

__version__ = "0.4" # Set version for the plugin handler.
#@+<< change log >>
#@+node:timo.20050213160555.2: ** <<change log>>
#@@nocolor-node
#@+at 
# 
# 
# 0.1
# - @bibtex nodes introduced, writing the contents in a BibTeX format.
#   Timo Honkasalo 2005/02/13
# 
# 0.2
# - Importing BibTeX files added.
#   Timo Honkasalo 2005/02/14
# 
# 0.3
# - Automatic inserting of templates when new entries are created.
#   Timo Honkasalo 2005/02/15
# 
# 0.4
# - Some changes in writeTreeAsBibTex (better format), added entrytypes in globals.
# - Greatly simplified and enhanced the performance of readBibTexFileIntoTree.
# - Fixed parsing of files in readBibTexFileIntoTree: they are now split at '\n@' (whitespace stripped) instead of '@', so that fields may contain '@' (like a 'mailto' field most likely would).
# - Changed <<write template>> to move cursor to the entry point of first field (16 columns right).
# - Bugfix: templates now include commas after each field
#   Timo Honkasalo 2005/03/02
#@-<< change log >>
#@+<< imports >>
#@+node:timo.20050213193129: ** <<imports>>
import leo.core.leoGlobals as g

#@-<< imports >>
#@+<< globals >>
#@+node:timo.20050215183130: ** <<globals>>
templates = {'@article':'author       = {},\ntitle        = {},\njournal      = {},\nyear         = ',
             '@book':'author       = {},\ntitle        = {},\npublisher    = {},\nyear         = ',
             '@booklet':'title        = {}',
             '@conference':'author       = {},\ntitle        = {},\nbooktitle    = {},\nyear         = ',
             '@inbook':'author       = {},\ntitle        = {},\nchapter      = {},\npublisher    = {},\nyear         = ',
             '@incollection':'author       = {},\ntitle        = {},\nbooktitle    = {},\npublisher    = {},\nyear         = ',
             '@inproceedings':'author       = {},\ntitle        = {},\nbooktitle    = {},\nyear         = ',
             '@manual':'title        = {},',
             '@mastersthesis':'author       = {},\ntitle        = {},\nschool       = {},\nyear         = ',
             '@misc':'',
             '@phdthesis':'author       = {},\ntitle        = {},\nschool       = {},\nyear         = ',
             '@proceedings':'title        = {},\nyear         = ',
             '@techreport':'author       = {},\ntitle        = {},\ninstitution  = {},\nyear         = ',
             '@unpublished':'author       = {},\ntitle        = {},\nnote         = {}'
             }

entrytypes = list(templates.keys())
entrytypes.append('@string') 
#@-<< globals >>
#@+<< to do >>
#@+node:timo.20050213185039: ** <<to do>>
#@+at To do list (in approximate order of importance):
# 
# - Translating between non-ascii characters and LaTeX code when reading/writing
# - Checking for duplicate keys
# - Checking for missing commas when writing the file
# - Customisable config file (for defining the templates)
# - Easy access to the tree as a Python object for scripting (maybe Pybliographer)
# - Import/write in BibTeXml format
# - Sorting by chosen fields
# - Import/write in other bibliographic formats
# - Expanding strings
# - Syntax checking
# - Syntax highligting
# 
#@-<< to do >>

#@+others
#@+node:ekr.20100128073941.5370: ** init
def init():

    ok = not g.app.unitTesting
    if ok:
        # Register the handlers...
        g.registerHandler("icondclick1",onIconDoubleClick)
        g.registerHandler("headkey2",onHeadKey)
        g.plugin_signon(__name__)

    return ok
#@+node:timo.20050213160555.3: ** onIconDoubleClick
#
# this does not check for proper filename syntax.
# path is the current dir, or the place @folder points to
# this should probably be changed to @path or so.

def onIconDoubleClick(tag,keywords):
    """Read or write a bibtex file when the node is double-clicked.

    Write the @bibtex tree as bibtex file when the root node is double-clicked. 
    If it has no child nodes, read bibtex file."""

    v = keywords.get("p") or keywords.get("v")
    c = keywords.get("c")
    h = v.h.strip()
    if g.match_word(h,0,"@bibtex"):
        fname = h[8:]
        if v.hasChildren():
            #@+<< write bibtex file >>
            #@+node:timo.20050213160555.6: *3* << write bibtex file >>
            bibFile = file(fname,'w')
            writeTreeAsBibTex(bibFile, v, c)

            bibFile.close()
            g.es('written: '+str(fname))
            #@-<< write bibtex file >>
        else:
            #@+<< read bibtex file >>
            #@+node:timo.20050214174623: *3* << read bibtex file >>
            g.es('reading: ' + str(fname))
            try: 
                bibFile = file(fname,'r')
            except IOError:
                g.es('IOError: file not found')
                return    
            readBibTexFileIntoTree(bibFile, c)

            bibFile.close()
            #@-<< read bibtex file >>


#@+node:timo.20050215222802: ** onHeadKey
def onHeadKey(tag,keywords):
    """Write template for the entry in body pane.

    If body pane is empty, get template for the entry from a dictionary 'templates ' and write it in the body pane."""
    # checking for duplicate keys will be also done in this function (to be implemented).

    v = keywords.get("p") or keywords.get("v")
    c = keywords.get("c")
    h = v.h.strip()
    ch = keywords.get("ch")
    if (ch == '\r') and (h[:h.find(' ')] in templates.keys()) and (not v.b):
        for p in v.parents():
            if p.h[:8] == '@bibtex ':
                #@+<< write template >>
                #@+node:timo.20050215232157: *3* << write template >>
                c.setBodyString(v,templates[h[:h.find(' ')]])
                c.frame.body.setInsertPoint('1.16')
                return
                #@-<< write template >>

#@+node:timo.20050213160555.7: ** writeTreeAsBibTex
def writeTreeAsBibTex(bibFile, vnode, c):
    """Write the tree under vnode to the file bibFile"""

    # body text of @bibtex node is ignored
    dict = c.scanAllDirectives(p=vnode)
    encoding = dict.get("encoding",None)
    if encoding == None:
        encoding = g.app.config.default_derived_file_encoding

    strings = ''
    entries = ''
    # iterate over nodes in this tree
    for v in vnode.subtree():    
        h = v.h
        h = g.toEncodedString(h,encoding,reportErrors=True)
        if h.lower() == '@string':
            typestring = '@string'
        else:
            typestring = h[:h.find(' ')].lower()
        if typestring in entrytypes:
            s = v.b
            s = g.toEncodedString(s,encoding,reportErrors=True)
            if h == '@string': # store string declarations in strings
                for i in s.split('\n'):
                    if i and (not i.isspace()):
                        strings = strings + '@string{' + i + '}\n'
            else:  # store other stuff in entries  
                entries = entries + typestring + '{' + h[h.find(' ')+1:]+  ',\n' + s + '}\n\n'
    if strings:
        bibFile.write(strings + '\n\n')
    bibFile.write(entries)  
#@+node:timo.20050214174623.1: ** readBibTexFileIntoTree
def readBibTexFileIntoTree(bibFile, c):
    """Read BibTeX file and parse it into @bibtex tree

    The file is split at '\n@' and each section is divided into headline
    ('@string' in strings and '@entrytype key' in others) and body text
    (without outmost braces). These are stored in biblist, which is a list
    of tuples ('headline', 'body text') for each entry, all the strings in
    the first element. For each element of biblist, a vnode is created and
    headline and body text put into place."""
    entrylist = biblist = []
    strings = ''
    rawstring = '\n'
    # read 'bibFile' by lines, strip leading whitespace and store as one 
    # string into 'rawstring'. Split 'rawstring' at '\n@' get a list of entries.
    for i in [o.lstrip() for o in bibFile.readlines()]:
        rawstring = rawstring + i
    for i in rawstring.split('\n@')[1:]:
        if i[:6] == 'string': # store all @string declarations into 'strings'
            strings = strings + i[7:].strip()[:-1] + '\n'
        else: # store all alse into 'entrylist'
            entrylist.append(('@' + i[:i.find(',')].replace('{',' ').replace('(',
            ' ').replace('\n',''), i[i.find(',')+1:].rstrip().lstrip('\n')[:-1]))
    if strings:
        biblist.append(('@string', strings)) 
    biblist = biblist + entrylist
    p = c.p
    for i in biblist:
        v = p.insertAsLastChild()
        c.setHeadString(v,str(i[0]))
        c.setBodyString(v,str(i[1]))





#@-others

#@-leo
