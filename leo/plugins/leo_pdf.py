#! /usr/bin/env python
#@+leo-ver=4
#@+node:@file leo_pdf.py
#@@first

#@<< docstring >>
#@+node:<< docstring >>
'''This NOT a Leo plugin: this is a docutils writer for .pdf files.  

That file uses the reportlab module to convert html markup to pdf.

The original code written by Engelbert Gruber.

Rewritten by Edward K. Ream for the Leo rst3 plugin.
'''
#@-node:<< docstring >>
#@nl

# Note: you must copy this file to the Python/Lib/site-packages/docutils/writers folder.

#@@language python
#@@tabwidth -4

#@<< about this code >>
#@+node:<< about this code >>
#@+at
# I. Bugs and bug fixes
# 
# This file, leo_pdf.py, is derived from rlpdf.py. It is intended as a 
# replacement
# for it. The copyright below applies only to this file, and to no other part 
# of
# Leo.
# 
# This code fixes numerous bugs that must have existed in rlpdf.py. That code 
# was
# apparently out-of-date. For known bugs in the present code see the 'to do'
# section.
# 
# II. New and improved code.
# 
# This code pushes only Bunch's on the context stack. The Bunch class is 
# slightly
# adapted from the Python Cookbook.
# 
# Pushing only Bunches greatly simplifies the code and makes it more robust: 
# there
# is no longer any need for one part of the code to pop as many entries as 
# another
# part pushed. Furthermore, Bunch's can have as much internal structure as 
# needed
# without affecting any other part of the code.
# 
# The following methods make using Bunch's trivial: push, pop, peek, 
# inContext.
# inContext searches the context stack for a Bunch of the indicated 'kind'
# attribute, returning the Bunch if found.
# 
# The following 'code generator' methods were heavily rewritten:
# visit/depart_title, visit/depart_visit_footnote_reference, footnote_backrefs
# and visit/depart_label.
# 
# III. Passing intermediateFile.txt to reportlab.
# 
# You can use an 'intermediate' file as the input to reportlab. This can be 
# highly
# useful: you can see what output reportlab will accept before the code 
# generators
# can actually generate it.
# 
# The way this works is as follows:
# 1. Run this code as usual, with the trace in PDFTranslator.createParagraph
# enabled. This trace will print the contents of each paragraph to be sent to
# reportlab, along with the paragraph's style.
# 
# 2. Take the resulting console output and put it in the file called
# intermediateFile.txt, in the same folder as the original document.
# 
# 3. At the start of Writer.translate, change the 'if 1:' to 'if: 0'. This 
# causes
# the code to use the dummyPDFTranslator class instead of the usual 
# PDFTranslator
# class.
# 
# 4. *Rerun* this code. Because of step 3, the code will read
# intermediateFile.txt and send it, paragraph by paragraph, to reportlab. The
# actual work is done in buildFromIntermediateFile. This method assumes the 
# output
# was produced by the trace in PDFTranslator.createParagraph as discussed
# in point 2 above.
# 
# IV. About tracing and debugging.
# 
# As mentioned in the imports section, it is not necessary to import 
# leo.core.leoGlobals as leoGlobals.
# This file is part of Leo, and contains debugging stuff such as g.trace and
# g.toString. There are also g.splitLines, g.es_exception, etc. used by 
# debugging
# code.
# 
# The trace in PDFTranslator.createParagraph is extremely useful for figuring 
# out
# what happened. Various other calls to g.trace are commented out throughout 
# the
# code. These were the way I debugged this code.
# 
# Edward K. Ream:  Aug 22, 2005.
#@-at
#@nonl
#@-node:<< about this code >>
#@nl
#@<< copyright >>
#@+node:<< copyright >>
#####################################################################################
#
#	Copyright (c) 2000-2001, ReportLab Inc.
#	All rights reserved.
#
#	Redistribution and use in source and binary forms, with or without modification,
#	are permitted provided that the following conditions are met:
#
#		*	Redistributions of source code must retain the above copyright notice,
#			this list of conditions and the following disclaimer. 
#		*	Redistributions in binary form must reproduce the above copyright notice,
#			this list of conditions and the following disclaimer in the documentation
#			and/or other materials provided with the distribution. 
#		*	Neither the name of the company nor the names of its contributors may be
#			used to endorse or promote products derived from this software without
#			specific prior written permission. 
#
#	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#	ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#	IN NO EVENT SHALL THE OFFICERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#	INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#	TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#	OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
#	IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
#	IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#	SUCH DAMAGE.
#
#####################################################################################
#@nonl
#@-node:<< copyright >>
#@nl
#@<< version history >>
#@+node:<< version history >>
#@@nocolor
#@+others
#@+node:Early versions
#@+node:Initial conversion
#@+at
# 
# - Added 'c:\reportlab_1_20' to sys.path.
# 
# - Obtained this file and stylesheet.py from
#   http://docutils.sourceforge.net/sandbox/dreamcatcher/rlpdf/
# 
# - Put stylesheet.py in docutils/writers directory.
#   This is a stylesheet class used by the file.
# 
# - Made minor mods to stop crashes.
#     - Added support for the '--stylesheet' option.
#         - This may be doing more harm than good.
#     - Changed the following methods of the PDFTranslator class:
#         - createParagraph
#         - depart_title
#@-at
#@nonl
#@-node:Initial conversion
#@+node:0.0.1
#@+at
# 
# - Removed '\r' characters in Writer.translate.
# - Created self.push and self.pop.
# - Rewrote visit/depart_title.  The code now is clear and works properly.
# 
# To do:
#     The code in several places uses x in self.context.
#     This won't work when g.Bunches are on the context stack,
#     so we shall need a method that searches the bunches on the stack.
#@-at
#@nonl
#@-node:0.0.1
#@+node:0.0.2
#@+at
# 
# - Fixed bug in visit_reference: added self.push(b).
# - Added putHead, putTail utilities.
# - Simplified most of the code.
# - Reorganized node handlers so that it is clear what the important methods 
# are.
# - Almost all the grunt work is done.
#@-at
#@nonl
#@-node:0.0.2
#@+node:0.0.3
#@+at
# 
# All grunt work completed:
# 
# - Moved Bunch class into this file (so no dependencies on leoGlobals.py).
# 
# - Simplified calls to self.push
# 
# - Finish all simple methods.
# 
# - Better dumps in createParagraph.
#@-at
#@nonl
#@-node:0.0.3
#@+node:0.0.4
#@+at
# 
# - Added dummyPDFTranslator class.
# 
# - Added support for this dummy class to Writer.translate.
#@-at
#@nonl
#@-node:0.0.4
#@+node:0.0.5
#@+at
# 
# - First working version.
# 
#@-at
#@-node:0.0.5
#@-node:Early versions
#@+node:0.1
#@+at
# 
# - Completed the conversion to using Bunches on the context stack.
#     - Added peek method.
#     - In context now searches from top of context stack and returns a Bunch.
#     - Rewrote the footnote logic to use bunches:
#         - footnote_backrefs sets b.setLink and b.links.  Much clearer code.
#         - visit/depart_label uses b.setLink and b.links to generate code.
# - The code now passes a minimal test of footnote code.
# 
# - WARNING: auto-footnote numbering does not work.  I doubt it ever did.  I 
# feel under no obligation to make it work.
#@-at
#@nonl
#@-node:0.1
#@+node:0.2
#@+at
# 
# - Added 'about this code' section.
#@-at
#@nonl
#@-node:0.2
#@+node:0.3
#@+at 
#@nonl
# Minor improvements to documentation.
#@-at
#@nonl
#@-node:0.3
#@+node:0.4
#@+at
# 
# - Added warning to docstring that this is not a valid Leo plugin.
# 
# - Added init function that always returns False.  This helps Leo's unit 
# tests.
#@-at
#@nonl
#@-node:0.4
#@-others

#@+at
# 0.5 EKR: Define subclasses of docutils classes only if docutils can be 
# imported.
#          This supresses errors during unit tests.
#@-at
#@-node:<< version history >>
#@nl
#@<< to do >>
#@+node:<< to do >>
#@@nocolor

#@+others
#@-others

#@+at
# 
# - Bullets show up as a black 2 ball.
# 
# - More flexible handling of style sheets.
# 
# - Auto-footnote numbering does not work.
# 
# - Test rST raw: pdf feature.
#@-at
#@nonl
#@-node:<< to do >>
#@nl

__version__ = '0.5'
__docformat__ = 'reStructuredText'
#@<< imports >>
#@+node:<< imports >>
import sys
sys.path.append(r'c:\reportlab_1_20') 

if 1: # This dependency could easily be removed.
    # Used only for tracing and error reporting.
    import leo.core.leoGlobals as g

try:
    # from reportlab.lib.enums import *
    # from reportlab.platypus import *

    # Formatting imports...
    import docutils
    import reportlab.platypus
    import reportlab.platypus.para
    import stylesheet # To do: get this a better way.

    # General imports...
    import StringIO
    # import time
    import types
except ImportError:
    docutils = None

#@-node:<< imports >>
#@nl

#@+others
#@+node:init
def init ():

    '''This file may be distributed in Leo's plugin folder, but this file is NOT
    a Leo plugin!

    The init method returns None to tell Leo's plugin manager and unit tests to
    skip this file.'''

    return None
#@nonl
#@-node:init
#@+node:class Bunch (object)
#@+at 
#@nonl
# From The Python Cookbook:  Often we want to just collect a bunch of stuff 
# together, naming each item of the bunch; a dictionary's OK for that, but a 
# small do-nothing class is even handier, and prettier to use.
# 
# Create a Bunch whenever you want to group a few variables:
# 
#     point = Bunch(datum=y, squared=y*y, coord=x)
# 
# You can read/write the named attributes you just created, add others, del 
# some of them, etc:
#     if point.squared > threshold:
#         point.isok = True
#@-at
#@@c

class Bunch (object):

    """A class that represents a colection of things.

    Especially useful for representing a collection of related variables."""

    def __init__(self,**keywords):
        self.__dict__.update (keywords)

    def __repr__(self):
        return self.toString()

    def ivars(self):
        return self.__dict__.keys()

    def keys(self):
        return self.__dict__.keys()

    def toString(self):
        tag = self.__dict__.get('tag')
        entries = ["%s: %s" % (key,str(self.__dict__.get(key)))
            for key in self.ivars() if key != 'tag']
        if tag:
            return "Bunch(tag=%s)...\n%s\n" % (tag,'\n'.join(entries))
        else:
            return "Bunch...\n%s\n" % '\n'.join(entries)

    # Used by new undo code.
    def __setitem__ (self,key,value):
        '''Support aBunch[key] = val'''
        return operator.setitem(self.__dict__,key,value)

    def __getitem__ (self,key):
        '''Support aBunch[key]'''
        return operator.getitem(self.__dict__,key)

    def get (self,key,theDefault=None):
        return self.__dict__.get(key,theDefault)

bunch = Bunch
#@nonl
#@-node:class Bunch (object)
#@-others

if docutils:
    #@    << define subclasses of docutils classes >>
    #@+node:<< define subclasses of docutils classes >>
    #@+others
    #@+node:class Writer (docutils.writers.Writer)
    class Writer (docutils.writers.Writer):

        #@	<< class Writer declarations >>
        #@+node:<< class Writer declarations >>
        supported = ('pdf','rlpdf')
        """Formats this writer supports."""

        settings_spec = (
            'PDF-Specific Options',
            None,
            (
                # EKR: added this entry.
            (   'Specify a stylesheet URL, used verbatim.  Overrides '
                '--stylesheet-path.  Either --stylesheet or --stylesheet-path '
                'must be specified.',
                ['--stylesheet'],
                {'metavar': '<URL>', 'overrides': 'stylesheet_path'}),

            (   'Specify a stylesheet file, relative to the current working '
                'directory.  The path is adjusted relative to the output HTML '
                'file.  Overrides --stylesheet.',
                ['--stylesheet-path'],
                {'metavar': '<file>', 'overrides': 'stylesheet'}),

            (   'Format for footnote references: one of "superscript" or '
                '"brackets".  Default is "brackets".',
                ['--footnote-references'],
                {'choices': ['superscript', 'brackets'], 'default': 'brackets',
                'metavar': '<FORMAT>'}),
            )
        )

        output = None
        """Final translated form of `document`."""
        #@nonl
        #@-node:<< class Writer declarations >>
        #@nl

        #@	@+others
        #@+node:__init__ (Writer)
        def __init__(self):

            docutils.writers.Writer.__init__(self)

            # self.translator_class = PDFTranslator
        #@nonl
        #@-node:__init__ (Writer)
        #@+node:createParagraphsFromIntermediateFile
        def createParagraphsFromIntermediateFile (self,s,story,visitor):

            if 0: # Not needed now that putParaFromIntermediateFile is in the visitor.
                self.styleSheet = visitor.styleSheet
                self.encode = visitor.encode

            out = StringIO.StringIO()

            doc = reportlab.platypus.SimpleDocTemplate(out,
                pagesize=reportlab.lib.pagesizes.A4)

            # The 'real' code is doc.build(story)
            visitor.buildFromIntermediateFile(s,story,visitor)

            return out.getvalue()
        #@nonl
        #@-node:createParagraphsFromIntermediateFile
        #@+node:createPDF_usingPlatypus
        def createPDF_usingPlatypus (self,story):

            out = StringIO.StringIO()

            doc = reportlab.platypus.SimpleDocTemplate(out,
                pagesize=reportlab.lib.pagesizes.A4)

            doc.build(story)

            return out.getvalue()
        #@nonl
        #@-node:createPDF_usingPlatypus
        #@+node:lower
        def lower(self):

            return 'pdf'
        #@nonl
        #@-node:lower
        #@+node:translate
        def translate(self):

            '''Do final translation of self.document into self.output.'''

            if 1: # Production code.
                visitor = PDFTranslator(self,self.document)
            else: # Use intermediate file, and dummy pdf translator.
                # We can modify the intermediate file by hand to test proposed code generation.
                try:
                    filename = 'intermediateFile.txt'
                    s = file(filename).read()
                    # g.trace('creating .pdf file from %s...' % filename)
                    visitor = dummyPDFTranslator(self,self.document,s)
                except IOError:
                    # g.trace('can not open %s' % filename)
                    return

            # Create a list of paragraphs using Platypus.
            self.document.walkabout(visitor)
            story = visitor.as_what()

            if 0: # Not useful: story is a list of reportlab.platypus.para.Para objects.
                # Use the trace in createParagraph instead.
                g.trace('story','*'*40)
                print story        

            # Generate self.output.  Gets sent to reportlab.
            self.output = self.createPDF_usingPlatypus(story)
            # Solve the newline problem by brute force.
            self.output = self.output.replace('\n\r','\n')
            self.output = self.output.replace('\r\n','\n')
            if 0: # This is the actual .pdf output returned from doc.build(story)
                # doc is a Platypus (and this reportlab) document.
                g.trace('output','*'*40)
                lines = g.splitLines(self.output)
                g.printList(lines)
        #@nonl
        #@-node:translate
        #@-others
    #@nonl
    #@-node:class Writer (docutils.writers.Writer)
    #@+node:class dummyPDFTranslator (docutils.nodes.NodeVisitor)
    class dummyPDFTranslator (docutils.nodes.NodeVisitor):

        #@	@+others
        #@+node:   __init__ (dummyPDFTranslator)
        def __init__(self, writer,doctree,contents):

            self.writer = writer
            self.contents = contents
            self.story = []

            # Some of these may be needed, even though they are not referenced directly.
            self.settings = settings = doctree.settings
            self.styleSheet = stylesheet.getStyleSheet()
            docutils.nodes.NodeVisitor.__init__(self, doctree) # Init the base class.
            self.language = docutils.languages.get_language(doctree.settings.language_code)
        #@nonl
        #@-node:   __init__ (dummyPDFTranslator)
        #@+node:as_what
        def as_what(self):

            return self.story
        #@-node:as_what
        #@+node:encode
        def encode(self, text):

            """Encode special characters in `text` & return."""

            if type(text) is types.UnicodeType:
                text = text.replace(u'\u2020', u' ')
                text = text.replace(u'\xa0', u' ')
                text = text.encode('utf-8')

            return text

        #@-node:encode
        #@+node:visit/depart_document
        def visit_document(self, node):

            self.buildFromIntermediateFile()

            raise docutils.nodes.SkipNode

        def depart_document(self, node):

            pass
        #@nonl
        #@-node:visit/depart_document
        #@+node:buildFromIntermediateFile
        def buildFromIntermediateFile (self):

            'Synthesize calls to reportlab.platypus.para.Paragraph from an intermediate file.'

            lines = g.splitLines(self.contents)
            para = [] # The lines of the next paragraph.

            for line in lines:
                if line:
                    if line.startswith('createParagraph:'):
                        style = line[len('createParagraph:'):].strip()
                        if para:
                            self.putParaFromIntermediateFile(para,style)
                            para = []
                    elif line.startswith('starttag:') or line.startswith('..'):
                        pass
                    else:
                        para.append(line)
            if para:
                self.putParaFromIntermediateFile(para,style)
        #@nonl
        #@-node:buildFromIntermediateFile
        #@+node:putParaFromIntermediateFile
        def putParaFromIntermediateFile (self,lines,style):

            bulletText = None
            text = '\n'.join(lines)

            # g.trace(style,repr(text))

            style = self.styleSheet [style]

            self.story.append(
                reportlab.platypus.para.Paragraph (
                    self.encode(text), style,
                    bulletText = bulletText,
                    context = self.styleSheet))
        #@nonl
        #@-node:putParaFromIntermediateFile
        #@-others
    #@nonl
    #@-node:class dummyPDFTranslator (docutils.nodes.NodeVisitor)
    #@+node:class PDFTranslator (docutils.nodes.NodeVisitor)
    class PDFTranslator (docutils.nodes.NodeVisitor):

        #@	@+others
        #@+node:   __init__ (PDFTranslator)
        def __init__(self, writer,doctree):

            self.writer = writer
            self.settings = settings = doctree.settings
            self.styleSheet = stylesheet.getStyleSheet()
            docutils.nodes.NodeVisitor.__init__(self, doctree) # Init the base class.
            self.language = docutils.languages.get_language(doctree.settings.language_code)

            self.in_docinfo = False
            self.head = [] # Set only by meta() method.  
            self.body = [] # The body text being accumulated.
            self.foot = []
            self.sectionlevel = 0
            self.context = []

            self.story = []
            self.bulletText = '\267'
                # maybe move this into stylesheet.
                # This looks like the wrong glyph.

            if 0: # no longer used.
                self.topic_class = ''
                self.bulletlevel = 0
        #@-node:   __init__ (PDFTranslator)
        #@+node:Complex
        #@+node:footnotes
        #@+node:footnote_reference
        #@+node:visit_footnote_reference
        #@+at 
        #@nonl
        # Bug fixes, EKR 8/22/05:
        #     - Get attributes from node.attributes, not node.
        #     - The proper key is 'ids', not 'id'
        #@-at
        #@@c

        def visit_footnote_reference (self,node):

            '''Generate code for a footnote reference.'''

            # self.dumpNode(node,tag='footnote-ref-node')

            markup = [] # The terminating markup to be supplied by depart_footnote_reference.
            a = node.attributes # EKR.
            if self.settings.footnote_backlinks and a.get('ids'):
                self.body.append(
                    self.starttag(node,'setLink','',destination=a['ids']))
                markup.append('</setLink>')

            if   node.hasattr('refid'):   href = a ['refid']
            elif node.hasattr('refname'): href = self.document.nameids [a ['refname']]
            else:                         href = ''
            # g.trace('href:',href)

            format = self.settings.footnote_references
            if format == 'brackets':
                suffix = '[' ; markup.append(']')
            elif format == 'superscript':
                suffix = '<super>' ; markup.append('</super>')
            else: # shouldn't happen
                suffix = None

            if suffix:
                self.body.append(
                    self.starttag(node,'link',suffix,destination=href))
                markup.append('</link>')

            markup.reverse()
            self.push(kind='footnote-ref',markup=markup)
        #@nonl
        #@-node:visit_footnote_reference
        #@+node:depart_footnote_reference
        def depart_footnote_reference(self, node):

            b = self.pop('footnote-ref')

            for z in b.markup:
                self.body.append(z)
        #@nonl
        #@-node:depart_footnote_reference
        #@-node:footnote_reference
        #@+node:footnote & helpers
        def visit_footnote(self, node):

            self.push(kind='footnotes',context=[])

            self.footnote_backrefs(node)

        def depart_footnote(self, node):

            self.pop('footnotes')

            self.footnote_backrefs_depart(node)
        #@+node:footnote_backrefs
        #@+at 
        #@nonl
        # Bug fixes, EKR 8/22/05:
        #     - Get attributes from node.attributes, not node.
        #     - The proper key is 'ids', not 'id'
        # Warning: this does not work for auto-numbered footnotes.
        #@-at
        #@@c

        def footnote_backrefs (self,node):

            '''Create b.link and b.setLink for visit/depart_label.'''

            # self.dumpNode(node,tag='backrefs-node')

            b = self.peek('footnotes')
            a = node.attributes ; backrefs = a.get('backrefs',[]) # EKR.

            # Set b.setLink.
            b.setLink = self.starttag(
                {},'setLink','',destination=a['ids']) # EKR.

            # Set b.links.
            b.links = []
            if self.settings.footnote_backlinks:
                for backref in backrefs:
                    b.links.append(
                        self.starttag(
                            {},'link',suffix='',destination=backref))
        #@nonl
        #@-node:footnote_backrefs
        #@+node:footnote_backrefs_depart
        def footnote_backrefs_depart(self, node):

            if not self.context and self.body:
                self.createParagraph(self.body)
                self.body = []
        #@-node:footnote_backrefs_depart
        #@-node:footnote & helpers
        #@+node:label
        def visit_label(self, node):

            b = self.inContext('footnotes')
            if b:
                self.body.append(b.setLink)
                self.body.append('</setLink>')
                # Start all links.
                for link in b.links:
                    self.body.append(link)
                self.body.append('[')

        def depart_label(self, node):

            b = self.inContext('footnotes')
            if b:
                self.body.append(']')
                # End all links.
                for link in b.links:
                    self.body.append('</link>')
                # Who knows why this is here...
                self.body.append('   ')
        #@nonl
        #@-node:label
        #@-node:footnotes
        #@+node:reference...
        #@+node:visit_reference
        def visit_reference (self,node):

            markup = [] ; caller = 'visit_reference'

            if node.has_key('refuri'):
                href = node ['refuri']
                self.body.append(
                    self.starttag(node,'a',suffix='',href=href,caller=caller))
                markup.append('</a>')
            else:
                if node.has_key('id'):
                    self.body.append(
                        self.starttag({},'setLink','',
                            destination=node['id'],caller=caller))
                    markup.append('</setLink>')
                if node.has_key('refid'):
                    href = node ['refid']
                elif node.has_key('refname'):
                    href = self.document.nameids [node ['refname']]
                self.body.append(
                    self.starttag(node,'link','',destination=href,caller=caller))
                markup.append('</link>')

            self.push(kind='a',markup=markup)
        #@-node:visit_reference
        #@+node:depart_reference
        def depart_reference(self, node):

            b = self.pop('a')

            for s in b.markup:
                self.body.append(s)
        #@nonl
        #@-node:depart_reference
        #@-node:reference...
        #@+node:target
        def visit_target (self,node):

            if not (
                node.has_key('refuri') or
                node.has_key('refid') or
                node.has_key('refname')
            ):
                href = ''
                if node.has_key('id'):
                    href = node ['id']
                elif node.has_key('name'):
                    href = node ['name']
                self.body.append("%s%s" % (
                    self.starttag(node,'setLink',suffix='',
                        destination=href,caller='visit_targtet'),
                    '</setLink>'))
            raise docutils.nodes.SkipNode

        def depart_target (self,node):
            pass
        #@nonl
        #@-node:target
        #@+node:title
        #@+node:visit_title
        def visit_title (self,node):

            caller='visit_title'
            start = len(self.body) ; markup = []
            isTopic = isinstance(node.parent,docutils.nodes.topic)
            isTitle = self.sectionlevel == 0

            # Set the style.
            if isTopic:   style = 'topic-title'
            elif isTitle: style = 'title'
            else:         style = "h%s" % self.sectionlevel

            # The old code was equivalent to: if style != 'title'.
            if 0:
                self.dumpNode(node.parent,tag='node.parent')
                self.dumpNode(node,tag='node')
            # Bug fix: 8/21/05: changed 'id' to 'ids'.
            if node.parent.hasattr('ids'):
                self.body.append(
                self.starttag({},'setLink','',
                    destination=node.parent['ids'],caller=caller))
                markup.append('</setLink>')
            if node.hasattr('refid'):
                self.body.append(
                self.starttag({},'setLink','',
                    destination=node['refid'],caller=caller))
                markup.append('</setLink>')

            self.push(kind='title',markup=markup,start=start,style=style)
        #@nonl
        #@-node:visit_title
        #@+node:depart_title
        def depart_title (self,node):

            b = self.pop('title')

            for z in b.markup:
                self.body.append(z)

            self.putTail(b.start,style=b.style)
        #@nonl
        #@-node:depart_title
        #@-node:title
        #@-node:Complex
        #@+node:Helpers
        #@+node: starttag
        # The suffix is always '\n' except for a cant-happen situation.

        def starttag (self,node,tagname,suffix='\n',caller='',**attributes):

            # g.trace(repr(attributes))
            atts = {}
            for (name,value) in attributes.items():
                atts [name.lower()] = value
            for att in ('class',): # append to node attribute
                if node.has_key(att):
                    if atts.has_key(att):
                        atts [att] = node [att] + ' ' + atts [att]
            for att in ('id',): # node attribute overrides
                if node.has_key(att):
                    atts [att] = node [att]

            attlist = atts.items() ; attlist.sort()
            parts = [tagname]
            # Convert the attributes in attlist to a single string.
            for name, value in attlist:
                # g.trace('attlist element:',repr(name),repr(value))
                if value is None: # boolean attribute
                    parts.append(name.lower().strip())
                elif isinstance(value,types.ListType):
                    values = [str(v) for v in value]
                    val = ' '.join(values).strip()
                    parts.append('%s="%s"' % (
                        name.lower(), self.encode(val)))
                else:
                    parts.append('%s="%s"' % (
                        name.lower(),self.encode(str(value).strip())))

            val = '<%s>%s' % (' '.join(parts),suffix)
            # g.trace('%-24s %s' % (caller,val))
            return val
        #@nonl
        #@-node: starttag
        #@+node:as_what
        def as_what(self):

            return self.story
        #@-node:as_what
        #@+node:createParagraph
        def createParagraph (self,text,style='Normal',bulletText=None):

            if type(text) in (types.ListType,types.TupleType):
                text = ''.join([self.encode(t) for t in text])

            if not style.strip():
                style = 'Normal'

            if 0:
                s = text.split('>')
                s = '>\n'.join(s)
                print
                if 1: # just print the text.
                    print s
                else:
                    g.trace('%8s\n\n%s' % (style,s))
                print

            style = self.styleSheet [style]

            try:
                self.story.append(
                    reportlab.platypus.para.Paragraph (
                        self.encode(text), style,
                        bulletText = bulletText,
                        context = self.styleSheet))
            except Exception:
                g.es_print('Exception in createParagraph')
                g.es_exception()
                self.dumpContext()
                raise
        #@nonl
        #@-node:createParagraph
        #@+node:dumpContext
        def dumpContext (self):

            print ; print '-' * 40
            print 'Dump of context'

            i = 0
            for bunch in self.context:
                print '%2d %s' % (i,bunch)
                i += 1
        #@nonl
        #@-node:dumpContext
        #@+node:dumpNode
        def dumpNode (self,node,tag=''):

            #@    << define keys to be printed >>
            #@+node:<< define keys to be printed >>
            keys = (
                #'anonymous_refs'
                #'anonymous_targets'
                'attributes'
                'autofootnote_refs'
                'autofootnote_start'
                'autofootnotes'
                #'children'
                #'citation_refs'
                #'citations'
                #'current_line'
                #'current_source'
                #'decoration'
                #'document'
                'footnote_refs'
                'footnotes'
                'id_start'
                'ids'  # keys are sectinon names, values are section objects or reference objects.
                'indirect_targets'
                'nameids' # This might be what we want: keys are section names, values are munged names.
                #'nametypes'
                #'parse_messages'
                #'rawsource'
                'refids'
                'refnames'
                #'reporter'
                #'settings'
                #'substitution_defs'
                #'substitution_names'
                #'substitution_refs'
                #'symbol_footnote_refs'
                #'symbol_footnote_start'
                #'symbol_footnotes'
                #'tagname'
                #'transform_messages'
                #'transformer',
            )
            #@nonl
            #@-node:<< define keys to be printed >>
            #@nl

            d = node.__dict__

            nkeys = d.keys() ; nkeys.sort()

            print ; print '-' * 30
            print 'dump of node %s\n' % (g.choose(tag,'(%s)' % tag,''))

            print 'class',node.__class__

            for nkey in nkeys:
                if nkey in keys:
                    val = d.get(nkey)
                    print nkey,':',g.toString(val,verbose=False,indent='\t')

            print ; print 'done', '-' * 25
        #@nonl
        #@-node:dumpNode
        #@+node:encode
        def encode(self, text):

            """Encode special characters in `text` & return."""
            if type(text) is types.UnicodeType:
                text = text.replace(u'\u2020', u' ')
                text = text.replace(u'\xa0', u' ')
                text = text.encode('utf-8')
            #text = text.replace("&", "&amp;")
            #text = text.replace("<", '"')
            #text = text.replace('"', "(quot)")
            #text = text.replace(">", '"')
            # footnotes have character values above 128 ?
            return text
        #@-node:encode
        #@+node:inContext
        def inContext (self,kind):

            '''Return the most recent bunch having the indicated kind, or None.'''

            i = len(self.context) - 1

            while i >= 0:
                bunch = self.context[i]
                if bunch.kind == kind:
                    return bunch
                i -= 1

            return None
        #@nonl
        #@-node:inContext
        #@+node:pdfMunge
        def pdfMunge (self,s):

            '''Duplicate the munging done (somewhere in docutils) of section names.

            This allows us to use the nameids attribute in the document element.'''

            s = s.lower.replace('\t',' ')

            while s != s.replace('  ',' '):
                s = s.replace('  ',' ')

            return s.replace(' ','-')
        #@nonl
        #@-node:pdfMunge
        #@+node:push, pop, peek
        def push (self,**keys):

            self.context.append(Bunch(**keys))

        def pop (self,kind):

            bunch = self.context.pop()
            assert bunch.kind == kind,\
                'wrong bunch kind popped.  Expected: %s Got: %s' % (
                    kind, bunch.kind)

            return bunch

        def peek (self,kind):

            bunch = self.context[-1]
            assert bunch.kind == kind,\
                'peek at wrong bunch.  Expected: %s Got: %s' % (
                    kind, bunch.kind)
            return bunch
        #@nonl
        #@-node:push, pop, peek
        #@+node:putHead & putTail
        def putHead (self,start,style='Normal',bulletText=None):

            self.createParagraph(self.body[:start],
                style=style,bulletText=bulletText)

            self.body = self.body[start:]


        def putTail (self,start,style='Normal',bulletText=None):

            self.createParagraph(self.body[start:],
                style=style,bulletText=bulletText)

            self.body = self.body[:start]
        #@-node:putHead & putTail
        #@-node:Helpers
        #@+node:Simple...
        #@+node: do nothings...
        #@+node:authors
        def visit_authors(self, node):
            pass

        def depart_authors(self, node):
            pass
        #@-node:authors
        #@+node:block_quote
        def visit_block_quote(self, node):
            pass

        def depart_block_quote(self, node):
            pass
        #@nonl
        #@-node:block_quote
        #@+node:caption
        def visit_caption(self, node):
            pass

        def depart_caption(self, node):
            pass
        #@-node:caption
        #@+node:citation
        def visit_citation(self, node):
            pass

        def depart_citation(self, node):
            pass
        #@-node:citation
        #@+node:citation_reference
        def visit_citation_reference(self, node):
            pass

        def depart_citation_reference(self, node):
            pass
        #@-node:citation_reference
        #@+node:classifier
        def visit_classifier(self, node):
            pass

        def depart_classifier(self, node):
            pass
        #@-node:classifier
        #@+node:colspec
        def visit_colspec(self, node):
            pass

        def depart_colspec(self, node):
            pass
        #@-node:colspec
        #@+node:definition_list_item
        def visit_definition_list_item(self, node):
            pass

        def depart_definition_list_item(self, node):
            pass
        #@nonl
        #@-node:definition_list_item
        #@+node:description
        def visit_description(self, node):
            pass

        def depart_description(self, node):
            pass
        #@-node:description
        #@+node:document
        def visit_document(self, node):
            pass

        def depart_document(self, node):
            pass
        #@nonl
        #@-node:document
        #@+node:entry
        def visit_entry(self, node):
            pass

        def depart_entry(self, node):
            pass
        #@-node:entry
        #@+node:field_argument
        def visit_field_argument(self, node):
            pass

        def depart_field_argument(self, node):
            pass
        #@-node:field_argument
        #@+node:field_body
        def visit_field_body(self, node):
            pass

        def depart_field_body(self, node):
            pass
        #@-node:field_body
        #@+node:generated
        def visit_generated(self, node):
            pass

        def depart_generated(self, node):
            pass
        #@-node:generated
        #@+node:image
        def visit_image(self, node):
            pass

        def depart_image(self, node):
            pass
        #@-node:image
        #@+node:interpreted
        def visit_interpreted(self, node):
            pass

        def depart_interpreted(self, node):
            pass
        #@-node:interpreted
        #@+node:legend
        def visit_legend(self, node):
            pass

        def depart_legend(self, node):
            pass
        #@-node:legend
        #@+node:option
        def visit_option(self, node):
            pass

        def depart_option(self, node):
            pass
        #@-node:option
        #@+node:option_argument
        def visit_option_argument(self, node):
            pass

        def depart_option_argument(self, node):
            pass
        #@-node:option_argument
        #@+node:option_group
        def visit_option_group(self, node):
            pass

        def depart_option_group(self, node):
            pass
        #@-node:option_group
        #@+node:option_list_item
        def visit_option_list_item(self, node):
            pass

        def depart_option_list_item(self, node):
            pass
        #@-node:option_list_item
        #@+node:option_string
        def visit_option_string(self, node):
            pass

        def depart_option_string(self, node):
            pass
        #@-node:option_string
        #@+node:problematic
        def visit_problematic(self, node):
            pass

        def depart_problematic(self, node):
            pass
        #@-node:problematic
        #@+node:system_message
        def visit_system_message(self, node):
            pass

        def depart_system_message(self, node):
            pass
        #@-node:system_message
        #@+node:visit_row
        def visit_row(self, node):
            pass

        def depart_row(self, node):
            pass
        #@-node:visit_row
        #@-node: do nothings...
        #@+node:admonitions...
        def visit_admonition(self, node, name):
            pass

        def depart_admonition(self):
            pass
        #@+node:attention
        def visit_attention(self, node):

            self.visit_admonition(node, 'attention')

        def depart_attention(self, node):

            self.depart_admonition()
        #@-node:attention
        #@+node:caution
        def visit_caution(self, node):
            self.visit_admonition(node, 'caution')

        def depart_caution(self, node):
            self.depart_admonition()
        #@-node:caution
        #@+node:danger
        def visit_danger(self, node):

            self.visit_admonition(node, 'danger')

        def depart_danger(self, node):

            self.depart_admonition()
        #@-node:danger
        #@+node:error
        def visit_error(self, node):
            self.visit_admonition(node, 'error')

        def depart_error(self, node):
            self.depart_admonition()
        #@nonl
        #@-node:error
        #@+node:hint
        def visit_hint(self, node):
            self.visit_admonition(node, 'hint')

        def depart_hint(self, node):
            self.depart_admonition()
        #@-node:hint
        #@+node:important
        def visit_important(self, node):
            self.visit_admonition(node, 'important')

        def depart_important(self, node):
            self.depart_admonition()
        #@-node:important
        #@+node:note
        def visit_note(self, node):

            self.visit_admonition(node, 'note')

        def depart_note(self, node):

            self.depart_admonition()
        #@-node:note
        #@-node:admonitions...
        #@+node:bullet_list
        def visit_bullet_list(self, node):

            self.push(kind='ul',start=len(self.body))

            # At present self.bulletText is a constant.
            self.body.append('<ul bulletText="%s">' % self.bulletText)

        def depart_bullet_list(self, node):

            b = self.pop('ul')

            self.body.append('</ul>')

            if not self.inContext('ul'):
                self.putTail(b.start)
        #@nonl
        #@-node:bullet_list
        #@+node:definition
        def visit_definition(self, node):

            self.push(kind='dd')

            self.body.append('</dt>')
            self.body.append(
                self.starttag(node,'dd',caller='visit_destination'))

        def depart_definition(self, node):

            self.pop('dd')
            self.body.append('</dd>')
        #@nonl
        #@-node:definition
        #@+node:definition_list
        def visit_definition_list(self, node):

            self.push(kind='dl',start=len(self.body))

            self.body.append(self.starttag(node, 'dl'))

        def depart_definition_list(self, node):

            b = self.pop('dl')

            self.body.append('</dl>')

            if not self.inContext('dl'):
                self.putTail(b.start)
        #@-node:definition_list
        #@+node:docinfos...
        #@+node:address
        def visit_address(self, node):
            self.visit_docinfo_item(node, 'address')

        def depart_address(self, node):
            self.depart_docinfo_item()
        #@-node:address
        #@+node:author
        def visit_author(self, node):
            self.visit_docinfo_item(node, 'author')

        def depart_author(self, node):
            self.depart_docinfo_item()
        #@-node:author
        #@+node:contact
        def visit_contact(self, node):

            self.visit_docinfo_item(node, 'contact')

        def depart_contact(self, node):

            self.depart_docinfo_item()
        #@-node:contact
        #@+node:copyright
        def visit_copyright(self, node):

            self.visit_docinfo_item(node, 'copyright')

        def depart_copyright(self, node):

            self.depart_docinfo_item()
        #@-node:copyright
        #@+node:date
        def visit_date(self, node):

            self.visit_docinfo_item(node, 'date')

        def depart_date(self, node):

            self.depart_docinfo_item()

        #@-node:date
        #@+node:docinfo
        def visit_docinfo(self, node):

            self.push(kind='docinfo',start=len(self.body))
            self.in_docinfo = True

        def depart_docinfo(self, node):

            b = self.pop('docinfo')
            self.putHead(b.start)
            self.in_docinfo = False
        #@nonl
        #@-node:docinfo
        #@+node:docinfo_item
        def visit_docinfo_item(self, node, name):

            self.body.append(
                '<para style="DocInfo"><b>%s: </b>' % (
                    self.language.labels[name]))

        def depart_docinfo_item(self):

            self.body.append('</para>')
        #@-node:docinfo_item
        #@+node:organization
        def visit_organization(self, node):

            self.visit_docinfo_item(node, 'organization')

        def depart_organization(self, node):

            self.depart_docinfo_item()
        #@-node:organization
        #@+node:revision
        def visit_revision(self, node):

            self.visit_docinfo_item(node, 'revision')

        def depart_revision(self, node):

            self.depart_docinfo_item()
        #@-node:revision
        #@+node:status
        def visit_status(self, node):

            self.visit_docinfo_item(node, 'status')

        def depart_status(self, node):

            self.depart_docinfo_item()
        #@-node:status
        #@+node:version
        def visit_version(self, node):
            self.visit_docinfo_item(node, 'version')

        def depart_version(self, node):
            self.depart_docinfo_item()
        #@-node:version
        #@-node:docinfos...
        #@+node:emphasis
        def visit_emphasis(self, node):

            self.push(kind='i')

            self.body.append('<i>')

        def depart_emphasis(self, node):

            self.pop('i')

            self.body.append('</i>')
        #@-node:emphasis
        #@+node:enumerated_list
        def visit_enumerated_list(self, node):

            self.push(kind='ol',start=len(self.body))

            self.body.append('<ol>')

        def depart_enumerated_list(self, node):

            b = self.pop('ol')

            self.body.append('</ol>')

            if not self.inContext('ol'):
                self.putTail(b.start)
        #@nonl
        #@-node:enumerated_list
        #@+node:field_list
        def visit_field_list(self, node):

            self.push(kind='<para>',start=len(self.body))

        def depart_field_list(self, node):

            b = self.pop('<para>')

            self.body.append('</para>')

            self.putTail(b.start)
        #@nonl
        #@-node:field_list
        #@+node:list_item
        def visit_list_item(self, node):

            self.push(kind='li')

            self.body.append('<li>')

        def depart_list_item(self, node):

            self.pop('li')

            self.body.append('</li>')
        #@-node:list_item
        #@+node:option_list
        def visit_option_list(self, node):

            self.push(kind='option-list',start=len(self.body))

        def depart_option_list(self, node):

            b = self.pop('option-list')

            if not self.inContext('option_list'):
                self.putTail(b.start)
        #@-node:option_list
        #@+node:paragraph...
        def visit_paragraph(self, node):

            self.push(kind='p',start=len(self.body))

        def depart_paragraph(self, node):

            b = self.pop('p')

            if not self.context and self.body:
                self.putTail(b.start)
        #@nonl
        #@-node:paragraph...
        #@+node:strong
        def visit_strong(self, node):

            self.push(kind='b')

            self.body.append('<b>')

        def depart_strong(self, node):

            self.pop('b')

            self.body.append('</b>')

        #@-node:strong
        #@+node:subtitle
        def visit_subtitle(self, node):

            self.push(kind='subtitle',start=len(self.body))

        def depart_subtitle(self, node):

            b = self.pop('subtitle')

            self.putTail(b.start,b.style)
        #@-node:subtitle
        #@+node:term
        def visit_term (self,node):

            self.push(kind='dt')

            self.body.append(
                self.starttag(node,'dt',suffix='',caller='visit_term'))

        def depart_term (self,node):

            self.pop('dt')
        #@nonl
        #@-node:term
        #@+node:Text...
        def visit_Text (self,node):

            self.push(kind='#text')

            self.body.append(node.astext())

        def depart_Text (self,node):

            self.pop('#text')
        #@nonl
        #@-node:Text...
        #@+node:topic
        def visit_topic (self,node):

            if node.hasattr('id'):
                self.push(kind='topic-id',markup='</setLink>')
                self.body.append(self.starttag({},'setLink',
                    suffix='',destination=node['id'],caller='visit_topic'))

        def depart_topic (self,node):

            if node.hasattr('id'):
                b = self.pop('topic-id')
                self.body.append(b.markup)

        #@-node:topic
        #@-node:Simple...
        #@+node:Unusual...
        #@+node: Does not set context
        #@+node:field
        def visit_field(self, node):

            self.body.append('<para>')

        def depart_field(self, node):

            self.body.append('</para>')
        #@-node:field
        #@+node:field_name
        def visit_field_name(self, node):

            self.body.append('<b>')

        def depart_field_name(self, node):

            self.body.append(': </b>')
        #@nonl
        #@-node:field_name
        #@-node: Does not set context
        #@+node: Raises SkipNode
        #@+node:comment
        def visit_comment(self, node):

            raise docutils.nodes.SkipNode
        #@-node:comment
        #@+node: literal_blocks...
        def visit_literal_block(self, node):

            self.story.append(
                reportlab.platypus.Preformatted(
                    node.astext(),self.styleSheet['Code']))

            raise docutils.nodes.SkipNode

        def depart_literal_block(self, node):
            pass
        #@nonl
        #@+node:doctest_block
        def visit_doctest_block(self, node):

            self.visit_literal_block(node)

        def depart_doctest_block(self, node):

            self.depart_literal_block(node)

        #@-node:doctest_block
        #@+node:line_block
        def visit_line_block(self, node):
            self.visit_literal_block(node)

        def depart_line_block(self, node):
            self.depart_literal_block(node)
        #@-node:line_block
        #@-node: literal_blocks...
        #@-node: Raises SkipNode
        #@+node:invisible_visit
        def invisible_visit(self, node):

            """Invisible nodes should be ignored."""
            pass
        #@nonl
        #@-node:invisible_visit
        #@+node:literal (only changes context)
        def visit_literal(self, node):

            self.push(kind='literal')

        def depart_literal(self, node):

            self.pop('literal')
        #@nonl
        #@-node:literal (only changes context)
        #@+node:meta (appends to self.head)
        def visit_meta(self, node):

            g.trace(**node.attributes)

            self.head.append(
                self.starttag(node, 'meta', **node.attributes))

        def depart_meta(self, node):

            pass
        #@nonl
        #@-node:meta (appends to self.head)
        #@+node:section
        def visit_section(self, node):

            self.sectionlevel += 1

        def depart_section(self, node):

            self.sectionlevel -= 1
        #@-node:section
        #@+node:unimplemented_visit
        def unimplemented_visit(self, node):

            raise NotImplementedError(
                'visiting unimplemented node type: %s' % node.__class__.__name__)
        #@-node:unimplemented_visit
        #@+node:visit_raw
        def visit_raw(self, node):

            if node.has_key('format') and node['format'] == 'html':
                self.body.append(node.astext())

            raise docutils.nodes.SkipNode
        #@-node:visit_raw
        #@-node:Unusual...
        #@-others

        depart_comment = invisible_visit
        visit_substitution_definition = visit_comment
        depart_substitution_definition = depart_comment
        visit_figure = visit_comment
        depart_figure = depart_comment

        visit_sidebar = invisible_visit
        visit_warning = invisible_visit
        visit_tip = invisible_visit
        visit_tbody = invisible_visit
        visit_thead = invisible_visit
        visit_tgroup = invisible_visit
        visit_table = invisible_visit
        visit_title_reference = invisible_visit
        visit_transition = invisible_visit
        visit_pending = invisible_visit
        depart_pending = invisible_visit
        depart_transition = invisible_visit
        depart_title_reference = invisible_visit
        depart_table = invisible_visit
        depart_tgroup = invisible_visit
        depart_thead = invisible_visit
        depart_tbody = invisible_visit
        depart_tip = invisible_visit
        depart_warning = invisible_visit
        depart_sidebar = invisible_visit
    #@nonl
    #@-node:class PDFTranslator (docutils.nodes.NodeVisitor)
    #@-others
    #@nonl
    #@-node:<< define subclasses of docutils classes >>
    #@nl
#@nonl
#@-node:@file leo_pdf.py
#@-leo
