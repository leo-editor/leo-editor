# -*- coding: utf-8 -*-
#! /usr/bin/env python
#@+leo-ver=5-thin
#@+node:ekr.20090704103932.5160: * @file leo_pdf.py
#@@first
#@@first

#@+<< docstring >>
#@+node:ekr.20090704103932.5161: ** << docstring >>
''' This NOT a Leo plugin: this is a docutils writer for .pdf files.  

That file uses the reportlab module to convert html markup to pdf.

The original code written by Engelbert Gruber.

Rewritten by Edward K. Ream for the Leo rst3 plugin.
'''
#@-<< docstring >>

# Note: you must copy this file to the Python/Lib/site-packages/docutils/writers folder.

#@@language python
#@@tabwidth -4

#@+<< about this code >>
#@+node:ekr.20090704103932.5163: ** << about this code >>
#@+at
# I. Bugs and bug fixes
# 
# This file, leo_pdf.py, is derived from rlpdf.py. It is intended as a replacement
# for it. The copyright below applies only to this file, and to no other part of
# Leo.
# 
# This code fixes numerous bugs that must have existed in rlpdf.py. That code was
# apparently out-of-date. For known bugs in the present code see the 'to do'
# section.
# 
# II. New and improved code.
# 
# This code pushes only Bunch's on the context stack. The Bunch class is slightly
# adapted from the Python Cookbook.
# 
# Pushing only Bunches greatly simplifies the code and makes it more robust: there
# is no longer any need for one part of the code to pop as many entries as another
# part pushed. Furthermore, Bunch's can have as much internal structure as needed
# without affecting any other part of the code.
# 
# The following methods make using Bunch's trivial: push, pop, peek, inContext.
# inContext searches the context stack for a Bunch of the indicated 'kind'
# attribute, returning the Bunch if found.
# 
# The following 'code generator' methods were heavily rewritten:
# visit/depart_title, visit/depart_visit_footnote_reference, footnote_backrefs
# and visit/depart_label.
# 
# III. Passing intermediateFile.txt to reportlab.
# 
# You can use an 'intermediate' file as the input to reportlab. This can be highly
# useful: you can see what output reportlab will accept before the code generators
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
# 3. At the start of Writer.translate, change the 'if 1:' to 'if: 0'. This causes
# the code to use the dummyPDFTranslator class instead of the usual PDFTranslator
# class.
# 
# 4. *Rerun* this code. Because of step 3, the code will read
# intermediateFile.txt and send it, paragraph by paragraph, to reportlab. The
# actual work is done in buildFromIntermediateFile. This method assumes the output
# was produced by the trace in PDFTranslator.createParagraph as discussed
# in point 2 above.
# 
# IV. About tracing and debugging.
# 
# As mentioned in the imports section, it is not necessary to import leoGlobals.
# This file is part of Leo, and contains debugging stuff such as g.trace and
# g.toString. There are also g.splitLines, g.es_exception, etc. used by debugging
# code.
# 
# The trace in PDFTranslator.createParagraph is extremely useful for figuring out
# what happened. Various other calls to g.trace are commented out throughout the
# code. These were the way I debugged this code.
# 
# Edward K. Ream:  Aug 22, 2005.
#@-<< about this code >>
#@+<< copyright >>
#@+node:ekr.20090704103932.5164: ** << copyright >>
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
#@-<< copyright >>
#@+<< version history >>
#@+node:ekr.20090704103932.5165: ** << version history >>
#@@nocolor
#@+others
#@+node:ekr.20090704103932.5166: *3* Early versions
#@+node:ekr.20090704103932.5167: *4* Initial conversion
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
#@+node:ekr.20090704103932.5168: *4* 0.0.1
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
#@+node:ekr.20090704103932.5169: *4* 0.0.2
#@+at
# 
# - Fixed bug in visit_reference: added self.push(b).
# - Added putHead, putTail utilities.
# - Simplified most of the code.
# - Reorganized node handlers so that it is clear what the important methods are.
# - Almost all the grunt work is done.
#@+node:ekr.20090704103932.5170: *4* 0.0.3
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
#@+node:ekr.20090704103932.5171: *4* 0.0.4
#@+at
# 
# - Added dummyPDFTranslator class.
# 
# - Added support for this dummy class to Writer.translate.
#@+node:ekr.20090704103932.5172: *4* 0.0.5
#@+at
# 
# - First working version.
# 
#@+node:ekr.20090704103932.5173: *3* 0.1
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
# - WARNING: auto-footnote numbering does not work.  I doubt it ever did.  I feel under no obligation to make it work.
#@+node:ekr.20090704103932.5174: *3* 0.2
#@+at
# 
# - Added 'about this code' section.
#@+node:ekr.20090704103932.5175: *3* 0.3
#@+at Minor improvements to documentation.
#@+node:ekr.20090704103932.5176: *3* 0.4
#@+at
# 
# - Added warning to docstring that this is not a valid Leo plugin.
# 
# - Added init function that always returns False.  This helps Leo's unit tests.
#@-others

#@+at
# 0.5 EKR:
# - Define subclasses of docutils classes only if docutils can be imported.
# - This supresses errors during unit tests.
# 
# 1.0 EKR 2011/11/03:
# - Various changes to come accomodate docutils changes.
#     - Added dummy Reporter class for use by get_language.
#     - I suspect this should be logger class, but I don't much care.
# - Incorporate getStyleSheet from stylesheet.py, obtained from:
#     http://docutils.sourceforge.net/sandbox/dreamcatcher/rlpdf/
# 
# Note: passing writer_name = leo.plugins.leo_pdf to docutils does not work,
# presumably because __import__('leo.plugins.leo_pdf') returns the *leo* module,
# and docutils seems not to be aware of it. Thus, the new rst3 code passes writer
# = Writer() (an instance) instead.
#@-<< version history >>
#@+<< to do >>
#@+node:ekr.20090704103932.5177: ** << to do >>
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
#@-<< to do >>

__version__ = '1.0'
__docformat__ = 'reStructuredText'

#@+<< imports >>
#@+node:ekr.20090704103932.5162: ** << imports >>
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

except ImportError:
    print('leo_pdf.py: can not import docutils')
    docutils = None
    raise
    
try:
    import reportlab.platypus
    import reportlab.platypus.para
except ImportError:
    print('leo_pdf.py: can not import reportlab.platypus')
    reportlab = None
    raise
    
try:
    #copyright ReportLab Inc. 2000
    #see rllicense.txt for license details
    # http://docutils.sourceforge.net/sandbox/dreamcatcher/rlpdf/
    from reportlab.lib.styles import StyleSheet1, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib import colors

except ImportError:
    print('leo_pdf.py: can not import reportlab.lib styles info')
    stylesheet = None
    raise

if g.isPython3:
    import io
    StringIO = io.StringIO
else:
    import StringIO

import types

#@-<< imports >>

#@+others
#@+node:ekr.20090704103932.5178: ** init
def init ():

    '''This file may be distributed in Leo's plugin folder, but this file is NOT
    a Leo plugin!

    The init method returns None to tell Leo's plugin manager and unit tests to
    skip this file.'''

    return None
#@+node:ekr.20111103154150.9647: ** getStyleSheet
# Copied from stylesheet.py, from # http://docutils.sourceforge.net/sandbox/dreamcatcher/rlpdf/
# standard stylesheet for our manuals

def getStyleSheet():
    """Returns a stylesheet object"""
    stylesheet = StyleSheet1()

    stylesheet.add(ParagraphStyle(name='Normal',
                                  fontName='Times-Roman',
                                  fontSize=10,
                                  leading=12,
                                  spaceBefore=4,
                                  spaceAfter=4)
                   )

    stylesheet.add(ParagraphStyle(name='DocInfo',
                                  parent=stylesheet['Normal'],
                                  leading=12,
                                  spaceBefore=0,
                                  spaceAfter=0)
                   )

    stylesheet.add(ParagraphStyle(name='Comment',
                                  fontName='Times-Italic')
                   )

    stylesheet.add(ParagraphStyle(name='Indent1',
                                  leftIndent=36,
                                  firstLineIndent=0)
                   )
    
    stylesheet.add(ParagraphStyle(name='BodyText',
                                  parent=stylesheet['Normal'],
                                  spaceBefore=6)
                   )
    stylesheet.add(ParagraphStyle(name='Italic',
                                  parent=stylesheet['BodyText'],
                                  fontName = 'Times-Italic')
                   )

    stylesheet.add(ParagraphStyle(name='Heading1',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=20,
                                  leading=20,
                                  spaceBefore=10,
                                  spaceAfter=6),
                   alias='h1')

    stylesheet.add(ParagraphStyle(name='Heading2',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=18,
                                  leading=18,
                                  spaceBefore=10,
                                  spaceAfter=6),
                   alias='h2')
    
    stylesheet.add(ParagraphStyle(name='Heading3',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-BoldItalic',
                                  fontSize=16,
                                  leading=16,
                                  spaceBefore=10,
                                  spaceAfter=6),
                   alias='h3')

    stylesheet.add(ParagraphStyle(name='Heading4',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-BoldItalic',
                                  fontsize=14,
                                  leading=14,
                                  spaceBefore=8,
                                  spaceAfter=4),
                   alias='h4')

    stylesheet.add(ParagraphStyle(name='Heading5',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-BoldItalic',
                                  fontsize=13,
                                  leading=13,
                                  spaceBefore=8,
                                  spaceAfter=4),
                   alias='h5')

    stylesheet.add(ParagraphStyle(name='Heading6',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-BoldItalic',
                                  fontsize=12,
                                  leading=12,
                                  spaceBefore=8,
                                  spaceAfter=4),
                   alias='h6')

    stylesheet.add(ParagraphStyle(name='Title',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=22,
                                  leading=22,
                                  spaceAfter=8,
                                  alignment=TA_CENTER
                                  ),
                   alias='title')

    stylesheet.add(ParagraphStyle(name='Subtitle',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=20,
                                  leading=20,
                                  spaceAfter=6,
                                  alignment=TA_CENTER
                                  ),
                   alias='subtitle')

    stylesheet.add(ParagraphStyle(name='TopicTitle',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=18,
                                  leading=14,
                                  spaceAfter=6,
                                  ),
                   alias='topic-title')

    for i in range(0, 15):
        indent = 18*i
        stylesheet.add(ParagraphStyle(name='TopicItem%s' % i,
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Roman',
                                  fontSize=12,
                                  leftIndent=indent,
                                  spaceBefore=0,
                                  spaceAfter=0,
                                  ),
                   alias='topic-item-%s' % i)

    stylesheet.add(ParagraphStyle(name='UnorderedList',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  leftIndent=18,
                                  bulletIndent=9,
                                  spaceBefore=0,
                                  bulletFontName='Symbol'),
                   alias='ul')

    stylesheet.add(ParagraphStyle(name='Definition',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  leftIndent=36,
                                  bulletIndent=0,
                                  spaceAfter=2,
                                  spaceBefore=2,
                                  bulletFontName='Times-BoldItalic'),
                   alias='dl')

    stylesheet.add(ParagraphStyle(name='OrderedList',
                                  parent=stylesheet['Definition']),
                   alias='ol')

    stylesheet.add(ParagraphStyle(name='Code',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  textColor=colors.navy,
                                  fontSize=8,
                                  leading=8.8,
                                  leftIndent=36,
                                  firstLineIndent=0))

    stylesheet.add(ParagraphStyle(name='FunctionHeader',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier-Bold',
                                  fontSize=8,
                                  leading=8.8))

    stylesheet.add(ParagraphStyle(name='DocString',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  fontSize=8,
                                  leftIndent=18,
                                  leading=8.8))

    stylesheet.add(ParagraphStyle(name='DocStringIndent',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  fontSize=8,
                                  leftIndent=36,
                                  leading=8.8))

    stylesheet.add(ParagraphStyle(name='URL',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  textColor=colors.navy,
                                  alignment=TA_CENTER),
                   alias='u')
 
    stylesheet.add(ParagraphStyle(name='Centred',
                                  parent=stylesheet['Normal'],
                                  alignment=TA_CENTER
                                  ))

    stylesheet.add(ParagraphStyle(name='Caption',
                                  parent=stylesheet['Centred'],
                                  fontName='Times-Italic'
                                  ))
    
    return stylesheet
#@+node:ekr.20111106070228.12430: ** get_language
def get_language (doctree):
    
    '''A wrapper for changing docutils get_language method.'''
    
    class Reporter (object):
        def warning(s):
            g.es_print('Reporter.warning',s)
    
    try:
        reporter = Reporter()
        language = docutils.languages.get_language(doctree.settings.language_code,reporter)
    except TypeError:
        language = docutils.languages.get_language(doctree.settings.language_code)
        
    return language
#@+node:ekr.20090704103932.5179: ** class Bunch (object)
#@+at
# 
# From The Python Cookbook: Often we want to just collect a bunch of stuff
# together, naming each item of the bunch; a dictionary's OK for that, but a small
# do-nothing class is even handier, and prettier to use.
# 
# Create a Bunch whenever you want to group a few variables:
# 
#     point = Bunch(datum=y, squared=y*y, coord=x)
# 
# You can read/write the named attributes you just created, add others, del some
# of them, etc::
#     
#     if point.squared > threshold:
#         point.isok = True
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
#@-others

if docutils:
    #@+<< define subclasses of docutils classes >>
    #@+node:ekr.20111103122912.9783: ** << define subclasses of docutils classes >>
    #@+others
    #@+node:ekr.20090704103932.5181: *3* class Writer (docutils.writers.Writer)
    class Writer (docutils.writers.Writer):

        #@+<< class Writer declarations >>
        #@+node:ekr.20090704103932.5182: *4* << class Writer declarations >>
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
        #@-<< class Writer declarations >>

        #@+others
        #@+node:ekr.20090704103932.5183: *4* __init__ (Writer)
        def __init__(self):

            docutils.writers.Writer.__init__(self)

            # self.translator_class = PDFTranslator
        #@+node:ekr.20090704103932.5184: *4* createParagraphsFromIntermediateFile
        def createParagraphsFromIntermediateFile (self,s,story,visitor):

            if 0: # Not needed now that putParaFromIntermediateFile is in the visitor.
                self.styleSheet = visitor.styleSheet
                self.encode = visitor.encode
                
            if reportlab:

                out = StringIO.StringIO()
            
                doc = reportlab.platypus.SimpleDocTemplate(out,
                    pagesize=reportlab.lib.pagesizes.A4)
            
                # The 'real' code is doc.build(story)
                visitor.buildFromIntermediateFile(s,story,visitor)
            
                return out.getvalue()
                
            else:
                return ''
        #@+node:ekr.20090704103932.5185: *4* createPDF_usingPlatypus
        def createPDF_usingPlatypus (self,story):
            
            if reportlab:

                out = StringIO.StringIO()
            
                doc = reportlab.platypus.SimpleDocTemplate(out,
                    pagesize=reportlab.lib.pagesizes.A4)
            
                doc.build(story)
            
                return out.getvalue()
                
            else:
                return ''
        #@+node:ekr.20090704103932.5186: *4* lower
        def lower(self):

            return 'pdf'
        #@+node:ekr.20090704103932.5187: *4* translate
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
                g.pr(story)

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
        #@-others
    #@+node:ekr.20090704103932.5188: *3* class dummyPDFTranslator (docutils.nodes.NodeVisitor)
    class dummyPDFTranslator (docutils.nodes.NodeVisitor):

        #@+others
        #@+node:ekr.20090704103932.5189: *4*    __init__ (dummyPDFTranslator)
        def __init__(self, writer,doctree,contents):

            self.writer = writer
            self.contents = contents
            self.story = []

            # Some of these may be needed, even though they are not referenced directly.
            self.settings = settings = doctree.settings
            ### self.styleSheet = stylesheet and stylesheet.getStyleSheet()
            self.styleSheet = getStyleSheet()
            docutils.nodes.NodeVisitor.__init__(self, doctree) # Init the base class.
            self.language = get_language(doctree)
                ### docutils.languages.get_language(doctree.settings.language_code,self.reporter)
        #@+node:ekr.20090704103932.5190: *4* as_what
        def as_what(self):

            return self.story
        #@+node:ekr.20090704103932.5191: *4* encode (dummyPDFTranslator)
        def encode(self, text):

            """Encode special characters in `text` & return."""

            if type(text) is types.UnicodeType:
                # text = text.replace(g.u('\u2020'),g.u(' '))
                # text = text.replace(g.u('\xa0'), g.u(' '))
                text = text.encode('utf-8')

            return text

        #@+node:ekr.20090704103932.5192: *4* visit/depart_document
        def visit_document(self, node):

            self.buildFromIntermediateFile()

            raise docutils.nodes.SkipNode

        def depart_document(self, node):

            pass
        #@+node:ekr.20090704103932.5193: *4* buildFromIntermediateFile
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
        #@+node:ekr.20090704103932.5194: *4* putParaFromIntermediateFile
        def putParaFromIntermediateFile (self,lines,style):
            
            if not reportlab:
                return

            bulletText = None
            text = '\n'.join(lines)

            style = self.styleSheet.get(style)

            self.story.append(
                reportlab.platypus.para.Paragraph (
                    self.encode(text), style,
                    bulletText = bulletText,
                    context = self.styleSheet))
        #@-others
    #@+node:ekr.20090704103932.5195: *3* class PDFTranslator (docutils.nodes.NodeVisitor)
    class PDFTranslator (docutils.nodes.NodeVisitor):

        #@+others
        #@+node:ekr.20090704103932.5196: *4*    __init__ (PDFTranslator)
        def __init__(self, writer,doctree):

            self.writer = writer
            self.settings = settings = doctree.settings
            # self.styleSheet = stylesheet and stylesheet.getStyleSheet()
            self.styleSheet = getStyleSheet()
            docutils.nodes.NodeVisitor.__init__(self, doctree) # Init the base class.
            self.language = get_language(doctree)
                ### docutils.languages.get_language(doctree.settings.language_code,self.reporter)

            self.in_docinfo = False
            self.head = [] # Set only by meta() method.  
            self.body = [] # The body text being accumulated.
            self.foot = []
            self.sectionlevel = 0
            self.context = []

            self.story = []
            self.bulletText = '•' # Bullet: U+2022

            if 0: # no longer used.
                self.topic_class = ''
                self.bulletlevel = 0
        #@+node:ekr.20090704103932.5197: *4* Complex
        #@+node:ekr.20090704103932.5198: *5* footnotes
        #@+node:ekr.20090704103932.5199: *6* footnote_reference
        #@+node:ekr.20090704103932.5200: *7* visit_footnote_reference
        #@+at Bug fixes, EKR 8/22/05:
        #     - Get attributes from node.attributes, not node.
        #     - The proper key is 'ids', not 'id'
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
        #@+node:ekr.20090704103932.5201: *7* depart_footnote_reference
        def depart_footnote_reference(self, node):

            b = self.pop('footnote-ref')

            for z in b.markup:
                self.body.append(z)
        #@+node:ekr.20090704103932.5202: *6* footnote & helpers
        def visit_footnote(self, node):

            self.push(kind='footnotes',context=[])

            self.footnote_backrefs(node)

        def depart_footnote(self, node):

            self.pop('footnotes')

            self.footnote_backrefs_depart(node)
        #@+node:ekr.20090704103932.5203: *7* footnote_backrefs
        #@+at Bug fixes, EKR 8/22/05:
        #     - Get attributes from node.attributes, not node.
        #     - The proper key is 'ids', not 'id'
        # Warning: this does not work for auto-numbered footnotes.
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
        #@+node:ekr.20090704103932.5204: *7* footnote_backrefs_depart
        def footnote_backrefs_depart(self, node):

            if not self.context and self.body:
                self.createParagraph(self.body)
                self.body = []
        #@+node:ekr.20090704103932.5205: *6* label
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
        #@+node:ekr.20090704103932.5206: *5* reference...
        #@+node:ekr.20090704103932.5207: *6* visit_reference
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
        #@+node:ekr.20090704103932.5208: *6* depart_reference
        def depart_reference(self, node):

            b = self.pop('a')

            for s in b.markup:
                self.body.append(s)
        #@+node:ekr.20090704103932.5209: *5* target
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
        #@+node:ekr.20090704103932.5210: *5* title
        #@+node:ekr.20090704103932.5211: *6* visit_title
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
        #@+node:ekr.20090704103932.5212: *6* depart_title
        def depart_title (self,node):

            b = self.pop('title')

            for z in b.markup:
                self.body.append(z)

            try:
                style = b.style
            except AttributeError:
                style = 'Normal'
                
            self.putTail(b.start,style)
        #@+node:ekr.20090704103932.5213: *4* Helpers
        #@+node:ekr.20090704103932.5214: *5*  starttag
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
        #@+node:ekr.20090704103932.5215: *5* as_what
        def as_what(self):

            return self.story
        #@+node:ekr.20090704103932.5216: *5* createParagraph
        def createParagraph (self,text,style='Normal',bulletText=None):
            
            if not reportlab:
                return

            if type(text) in (types.ListType,types.TupleType):
                text = ''.join(text)
            
            #### text = self.encode(text)
            
            # This escapes too much.
            # text = self.escape(text)

            if not style.strip():
                style = 'Normal'

            style = self.styleSheet.get(style)

            try:
                s = reportlab.platypus.para.Paragraph (
                    text, ### self.encode(text),
                    style,
                    bulletText = bulletText,
                    context = self.styleSheet,
                )
                self.story.append(s)
            except Exception:
                g.es_print('\nreportlab error...\n',color='orange')
                g.es_print_exception(full=False)
                g.es_exception(full=False)
                print(repr(text))
                
                # self.dumpContext()
        #@+node:ekr.20090704103932.5217: *5* dumpContext
        def dumpContext (self):
            
            if self.context:

                print('-' * 40)
                print('Dump of context...')
            
                i = 0
                for bunch in self.context:
                    print('%2d %s' % (i,bunch))
                    i += 1
        #@+node:ekr.20090704103932.5218: *5* dumpNode
        def dumpNode (self,node,tag=''):

            #@+<< define keys to be printed >>
            #@+node:ekr.20090704103932.5219: *6* << define keys to be printed >>
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
            #@-<< define keys to be printed >>

            d = node.__dict__

            nkeys = list(d.keys())
            nkeys.sort()

            g.pr('\n','-' * 30)
            g.pr('dump of node %s\n' % (g.choose(tag,'(%s)' % tag,'')))

            g.pr('class',node.__class__)

            for nkey in nkeys:
                if nkey in keys:
                    val = d.get(nkey)
                    g.pr(nkey,':',g.toString(val,verbose=False,indent='\t'))

            g.pr('\ndone', '-' * 25)
        #@+node:ekr.20090704103932.5220: *5* encode (PDFTranslator) (No longer used)
        def encode(self, text):

            """Encode special characters in `text` & return."""
            if type(text) is types.UnicodeType:
                ###text = text.replace(g.u('\u2020'),g.u(' '))
                ###text = text.replace(g.u('\xa0'), g.u(' '))
                text = text.encode('utf-8')
            return text
        #@+node:ekr.20111107181638.9742: *5* escape (PDFTranslator)
        def escape (self,s):
            
            return s.replace('<','&lt').replace('>','&gt')
        #@+node:ekr.20090704103932.5221: *5* inContext
        def inContext (self,kind):

            '''Return the most recent bunch having the indicated kind, or None.'''

            i = len(self.context) - 1

            while i >= 0:
                bunch = self.context[i]
                if bunch.kind == kind:
                    return bunch
                i -= 1

            return None
        #@+node:ekr.20090704103932.5222: *5* pdfMunge
        def pdfMunge (self,s):

            '''Duplicate the munging done (somewhere in docutils) of section names.

            This allows us to use the nameids attribute in the document element.'''

            s = s.lower.replace('\t',' ')

            while s != s.replace('  ',' '):
                s = s.replace('  ',' ')

            return s.replace(' ','-')
        #@+node:ekr.20090704103932.5223: *5* push, pop, peek
        def push (self,**keys):

            bunch = Bunch(**keys)
            self.context.append(bunch)
            # g.trace(bunch)
            

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
        #@+node:ekr.20090704103932.5224: *5* putHead & putTail
        def putHead (self,start,style='Normal',bulletText=None):

            self.createParagraph(self.body[:start],
                style=style,bulletText=bulletText)

            self.body = self.body[start:]


        def putTail (self,start,style='Normal',bulletText=None):

            self.createParagraph(self.body[start:],
                style=style,bulletText=bulletText)

            self.body = self.body[:start]
        #@+node:ekr.20090704103932.5225: *4* Simple...
        #@+node:ekr.20090704103932.5226: *5*  do nothings...
        #@+node:ekr.20090704103932.5227: *6* authors
        def visit_authors(self, node):
            pass

        def depart_authors(self, node):
            pass
        #@+node:ekr.20090704103932.5228: *6* block_quote
        def visit_block_quote(self, node):
            pass

        def depart_block_quote(self, node):
            pass
        #@+node:ekr.20090704103932.5229: *6* caption
        def visit_caption(self, node):
            pass

        def depart_caption(self, node):
            pass
        #@+node:ekr.20090704103932.5230: *6* citation
        def visit_citation(self, node):
            pass

        def depart_citation(self, node):
            pass
        #@+node:ekr.20090704103932.5231: *6* citation_reference
        def visit_citation_reference(self, node):
            pass

        def depart_citation_reference(self, node):
            pass
        #@+node:ekr.20090704103932.5232: *6* classifier
        def visit_classifier(self, node):
            pass

        def depart_classifier(self, node):
            pass
        #@+node:ekr.20090704103932.5233: *6* colspec
        def visit_colspec(self, node):
            pass

        def depart_colspec(self, node):
            pass
        #@+node:ekr.20090704103932.5234: *6* definition_list_item
        def visit_definition_list_item(self, node):
            pass

        def depart_definition_list_item(self, node):
            pass
        #@+node:ekr.20090704103932.5235: *6* description
        def visit_description(self, node):
            pass

        def depart_description(self, node):
            pass
        #@+node:ekr.20090704103932.5236: *6* document
        def visit_document(self, node):
            pass

        def depart_document(self, node):
            pass
        #@+node:ekr.20090704103932.5237: *6* entry
        def visit_entry(self, node):
            pass

        def depart_entry(self, node):
            pass
        #@+node:ekr.20090704103932.5238: *6* field_argument
        def visit_field_argument(self, node):
            pass

        def depart_field_argument(self, node):
            pass
        #@+node:ekr.20090704103932.5239: *6* field_body
        def visit_field_body(self, node):
            pass

        def depart_field_body(self, node):
            pass
        #@+node:ekr.20090704103932.5240: *6* generated
        def visit_generated(self, node):
            pass

        def depart_generated(self, node):
            pass
        #@+node:ekr.20090704103932.5241: *6* image
        def visit_image(self, node):
            pass

        def depart_image(self, node):
            pass
        #@+node:ekr.20090704103932.5242: *6* interpreted
        def visit_interpreted(self, node):
            pass

        def depart_interpreted(self, node):
            pass
        #@+node:ekr.20090704103932.5243: *6* legend
        def visit_legend(self, node):
            pass

        def depart_legend(self, node):
            pass
        #@+node:ekr.20090704103932.5244: *6* option
        def visit_option(self, node):
            pass

        def depart_option(self, node):
            pass
        #@+node:ekr.20090704103932.5245: *6* option_argument
        def visit_option_argument(self, node):
            pass

        def depart_option_argument(self, node):
            pass
        #@+node:ekr.20090704103932.5246: *6* option_group
        def visit_option_group(self, node):
            pass

        def depart_option_group(self, node):
            pass
        #@+node:ekr.20090704103932.5247: *6* option_list_item
        def visit_option_list_item(self, node):
            pass

        def depart_option_list_item(self, node):
            pass
        #@+node:ekr.20090704103932.5248: *6* option_string
        def visit_option_string(self, node):
            pass

        def depart_option_string(self, node):
            pass
        #@+node:ekr.20090704103932.5249: *6* problematic
        def visit_problematic(self, node):
            pass

        def depart_problematic(self, node):
            pass
        #@+node:ekr.20090704103932.5250: *6* system_message
        def visit_system_message(self, node):
            pass

        def depart_system_message(self, node):
            pass
        #@+node:ekr.20090704103932.5251: *6* visit_row
        def visit_row(self, node):
            pass

        def depart_row(self, node):
            pass
        #@+node:ekr.20090704103932.5252: *5* admonitions...
        def visit_admonition(self, node, name):
            pass

        def depart_admonition(self):
            pass
        #@+node:ekr.20090704103932.5253: *6* attention
        def visit_attention(self, node):

            self.visit_admonition(node, 'attention')

        def depart_attention(self, node):

            self.depart_admonition()
        #@+node:ekr.20090704103932.5254: *6* caution
        def visit_caution(self, node):
            self.visit_admonition(node, 'caution')

        def depart_caution(self, node):
            self.depart_admonition()
        #@+node:ekr.20090704103932.5255: *6* danger
        def visit_danger(self, node):

            self.visit_admonition(node, 'danger')

        def depart_danger(self, node):

            self.depart_admonition()
        #@+node:ekr.20090704103932.5256: *6* error
        def visit_error(self, node):
            self.visit_admonition(node, 'error')

        def depart_error(self, node):
            self.depart_admonition()
        #@+node:ekr.20090704103932.5257: *6* hint
        def visit_hint(self, node):
            self.visit_admonition(node, 'hint')

        def depart_hint(self, node):
            self.depart_admonition()
        #@+node:ekr.20090704103932.5258: *6* important
        def visit_important(self, node):
            self.visit_admonition(node, 'important')

        def depart_important(self, node):
            self.depart_admonition()
        #@+node:ekr.20090704103932.5259: *6* note
        def visit_note(self, node):

            self.visit_admonition(node, 'note')

        def depart_note(self, node):

            self.depart_admonition()
        #@+node:ekr.20090704103932.5260: *5* bullet_list
        def visit_bullet_list(self, node):

            self.push(kind='ul',start=len(self.body))

            # At present self.bulletText is a constant.
            self.body.append('<ul bulletText="%s">' % self.bulletText)

        def depart_bullet_list(self, node):

            b = self.pop('ul')

            self.body.append('</ul>')

            if not self.inContext('ul'):
                self.putTail(b.start)
        #@+node:ekr.20090704103932.5261: *5* definition
        def visit_definition(self, node):

            self.push(kind='dd')

            self.body.append('</dt>')
            self.body.append(
                self.starttag(node,'dd',caller='visit_destination'))

        def depart_definition(self, node):

            self.pop('dd')
            self.body.append('</dd>')
        #@+node:ekr.20090704103932.5262: *5* definition_list
        def visit_definition_list(self, node):

            self.push(kind='dl',start=len(self.body))

            self.body.append(self.starttag(node, 'dl'))

        def depart_definition_list(self, node):

            b = self.pop('dl')

            self.body.append('</dl>')

            if not self.inContext('dl'):
                self.putTail(b.start)
        #@+node:ekr.20090704103932.5263: *5* docinfos...
        #@+node:ekr.20090704103932.5264: *6* address
        def visit_address(self, node):
            self.visit_docinfo_item(node, 'address')

        def depart_address(self, node):
            self.depart_docinfo_item()
        #@+node:ekr.20090704103932.5265: *6* author
        def visit_author(self, node):
            self.visit_docinfo_item(node, 'author')

        def depart_author(self, node):
            self.depart_docinfo_item()
        #@+node:ekr.20090704103932.5266: *6* contact
        def visit_contact(self, node):

            self.visit_docinfo_item(node, 'contact')

        def depart_contact(self, node):

            self.depart_docinfo_item()
        #@+node:ekr.20090704103932.5267: *6* copyright
        def visit_copyright(self, node):

            self.visit_docinfo_item(node, 'copyright')

        def depart_copyright(self, node):

            self.depart_docinfo_item()
        #@+node:ekr.20090704103932.5268: *6* date
        def visit_date(self, node):

            self.visit_docinfo_item(node, 'date')

        def depart_date(self, node):

            self.depart_docinfo_item()

        #@+node:ekr.20090704103932.5269: *6* docinfo
        def visit_docinfo(self, node):

            self.push(kind='docinfo',start=len(self.body))
            self.in_docinfo = True

        def depart_docinfo(self, node):

            b = self.pop('docinfo')
            self.putHead(b.start)
            self.in_docinfo = False
        #@+node:ekr.20090704103932.5270: *6* docinfo_item
        def visit_docinfo_item(self, node, name):

            self.body.append(
                '<para style="DocInfo"><b>%s: </b>' % (
                    self.language.labels[name]))

        def depart_docinfo_item(self):

            self.body.append('</para>')
        #@+node:ekr.20090704103932.5271: *6* organization
        def visit_organization(self, node):

            self.visit_docinfo_item(node, 'organization')

        def depart_organization(self, node):

            self.depart_docinfo_item()
        #@+node:ekr.20090704103932.5272: *6* revision
        def visit_revision(self, node):

            self.visit_docinfo_item(node, 'revision')

        def depart_revision(self, node):

            self.depart_docinfo_item()
        #@+node:ekr.20090704103932.5273: *6* status
        def visit_status(self, node):

            self.visit_docinfo_item(node, 'status')

        def depart_status(self, node):

            self.depart_docinfo_item()
        #@+node:ekr.20090704103932.5274: *6* version
        def visit_version(self, node):
            self.visit_docinfo_item(node, 'version')

        def depart_version(self, node):
            self.depart_docinfo_item()
        #@+node:ekr.20090704103932.5275: *5* emphasis
        def visit_emphasis(self, node):

            self.push(kind='i')

            self.body.append('<i>')

        def depart_emphasis(self, node):

            self.pop('i')

            self.body.append('</i>')
        #@+node:ekr.20090704103932.5276: *5* enumerated_list
        def visit_enumerated_list(self, node):

            self.push(kind='ol',start=len(self.body))

            self.body.append('<ol>')

        def depart_enumerated_list(self, node):

            b = self.pop('ol')

            self.body.append('</ol>')

            if not self.inContext('ol'):
                self.putTail(b.start)
        #@+node:ekr.20090704103932.5277: *5* field_list
        def visit_field_list(self, node):

            self.push(kind='<para>',start=len(self.body))

        def depart_field_list(self, node):

            b = self.pop('<para>')

            self.body.append('</para>')

            self.putTail(b.start)
        #@+node:ekr.20090704103932.5278: *5* list_item
        def visit_list_item(self, node):

            self.push(kind='li')

            self.body.append('<li>')

        def depart_list_item(self, node):

            self.pop('li')

            self.body.append('</li>')
        #@+node:ekr.20090704103932.5279: *5* option_list
        def visit_option_list(self, node):

            self.push(kind='option-list',start=len(self.body))

        def depart_option_list(self, node):

            b = self.pop('option-list')

            if not self.inContext('option_list'):
                self.putTail(b.start)
        #@+node:ekr.20090704103932.5280: *5* paragraph...
        def visit_paragraph(self, node):

            self.push(kind='p',start=len(self.body))

        def depart_paragraph(self, node):

            b = self.pop('p')

            if not self.context and self.body:
                self.putTail(b.start)
        #@+node:ekr.20090704103932.5281: *5* strong
        def visit_strong(self, node):

            self.push(kind='b')

            self.body.append('<b>')

        def depart_strong(self, node):

            self.pop('b')

            self.body.append('</b>')

        #@+node:ekr.20090704103932.5282: *5* subtitle
        def visit_subtitle(self, node):

            self.push(kind='subtitle',start=len(self.body))

        def depart_subtitle(self, node):

            b = self.pop('subtitle')
            
            try:
                style = b.style
            except AttributeError:
                style = 'Normal'

            self.putTail(b.start,style)
        #@+node:ekr.20090704103932.5283: *5* term
        def visit_term (self,node):

            self.push(kind='dt')

            self.body.append(
                self.starttag(node,'dt',suffix='',caller='visit_term'))

        def depart_term (self,node):

            self.pop('dt')
        #@+node:ekr.20090704103932.5284: *5* Text...
        def visit_Text (self,node):

            self.push(kind='#text')

            self.body.append(node.astext())

        def depart_Text (self,node):

            self.pop('#text')
        #@+node:ekr.20090704103932.5285: *5* topic
        def visit_topic (self,node):

            if node.hasattr('id'):
                self.push(kind='topic-id',markup='</setLink>')
                self.body.append(self.starttag({},'setLink',
                    suffix='',destination=node['id'],caller='visit_topic'))

        def depart_topic (self,node):

            if node.hasattr('id'):
                b = self.pop('topic-id')
                self.body.append(b.markup)

        #@+node:ekr.20090704103932.5286: *4* Unusual...
        #@+node:ekr.20090704103932.5287: *5*  Does not set context
        #@+node:ekr.20090704103932.5288: *6* field
        def visit_field(self, node):

            self.body.append('<para>')

        def depart_field(self, node):

            self.body.append('</para>')
        #@+node:ekr.20090704103932.5289: *6* field_name
        def visit_field_name(self, node):

            self.body.append('<b>')

        def depart_field_name(self, node):

            self.body.append(': </b>')
        #@+node:ekr.20090704103932.5290: *5*  Raises SkipNode
        #@+node:ekr.20090704103932.5291: *6* comment
        def visit_comment(self, node):

            raise docutils.nodes.SkipNode
        #@+node:ekr.20090704103932.5292: *6*  literal_blocks...
        def visit_literal_block(self, node):
            
            if reportlab:
                self.story.append(
                    reportlab.platypus.Preformatted(
                        node.astext(),self.styleSheet.get('Code')))

            raise docutils.nodes.SkipNode

        def depart_literal_block(self, node):
            pass
        #@+node:ekr.20090704103932.5293: *7* doctest_block
        def visit_doctest_block(self, node):

            self.visit_literal_block(node)

        def depart_doctest_block(self, node):

            self.depart_literal_block(node)

        #@+node:ekr.20090704103932.5294: *7* line_block
        def visit_line_block(self, node):
            self.visit_literal_block(node)

        def depart_line_block(self, node):
            self.depart_literal_block(node)
        #@+node:ekr.20090704103932.5295: *5* invisible_visit
        def invisible_visit(self, node):

            """Invisible nodes should be ignored."""
            pass
        #@+node:ekr.20090704103932.5296: *5* literal (only changes context)
        def visit_literal(self, node):

            self.push(kind='literal')

        def depart_literal(self, node):

            self.pop('literal')
        #@+node:ekr.20090704103932.5297: *5* meta (appends to self.head)
        def visit_meta(self, node):

            g.trace(**node.attributes)

            self.head.append(
                self.starttag(node, 'meta', **node.attributes))

        def depart_meta(self, node):

            pass
        #@+node:ekr.20090704103932.5298: *5* section
        def visit_section(self, node):

            self.sectionlevel += 1

        def depart_section(self, node):

            self.sectionlevel -= 1
        #@+node:ekr.20090704103932.5299: *5* unimplemented_visit
        def unimplemented_visit(self, node):

            raise NotImplementedError(
                'visiting unimplemented node type: %s' % node.__class__.__name__)
        #@+node:ekr.20090704103932.5300: *5* visit_raw
        def visit_raw(self, node):

            if node.has_key('format') and node['format'] == 'html':
                self.body.append(node.astext())

            raise docutils.nodes.SkipNode
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
    #@-others
    #@-<< define subclasses of docutils classes >>
#@-leo
