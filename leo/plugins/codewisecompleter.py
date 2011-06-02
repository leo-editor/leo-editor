#@+leo-ver=5-thin
#@+node:ville.20091204224145.5355: * @file codewisecompleter.py
#@+<< docstring >>
#@+node:ville.20091204224145.5356: ** << docstring >>
''' This plugin uses the ctags database created by codewise.py
    (in the codewise branch) to provide an autocompletion list.

Instructions:

    sudo apt-get install exuberant-ctags
    bzr branch lp:codewise
    cd codewise
    python setup.py install

    run "codewise" to get help

    Press alt-0 to start completion in leo

'''
#@-<< docstring >>

# See http://ctags.sourceforge.net/ctags.html#TAG%20FILE%20FORMAT for the file format:
# tag_name<TAB>file_name<TAB>ex_cmd;"<TAB>extension_fields
# Example

__version__ = '0.2'
#@+<< version history >>
#@+node:ville.20091204224145.5357: ** << version history >>
#@@nocolor-node
#@+at
# 
# 0.1 EKR: place helpers as children of callers.
# 0.2 EKR: Don't crash if the ctags file doesn't exist.
# 0.3 EKR 2011/03/09: refactored using per-commander controllers.
#@-<< version history >>
#@+<< imports >>
#@+node:ville.20091204224145.5358: ** << imports >>
import leo.core.leoGlobals as g

import leo.external.codewise as codewise
    # The code that interfaces with ctags.
    # It contains commands that can be run stand-alone,
    # or imported as is done here.

import os
import re

try:
    from PyQt4.QtGui import QCompleter
    from PyQt4 import QtCore
    from PyQt4 import QtGui
except ImportError:
    # no qt available - some functionality should still exist
    pass
#@-<< imports >>

# Global variables
controllers = {}
    # Keys are commanders, values are CodewiseControllers.
tagLines = []
    # The saved contents of the tags file.
    # This is used only if keep_tag_lines is True

keep_tag_lines = True
    # True:  Read the tags file only once, keeping
    #        the contents of the tags file in memory.
    #        This might stress the garbage collector.
    # False: Read the tags file each time it is needed,
    #        in a separate process, and return the
    #        results of running grep on the file.
    #        This saves lots of memory, but reads the
    #        tags file many times.

#@+others
#@+node:ville.20091205173337.10141: ** class ContextSniffer
class ContextSniffer:
    
    """ Class to analyze surrounding context and guess class

    For simple dynamic code completion engines.
    """

    def __init__(self):

        self.vars = {}
            # Keys are var names; values are list of classes
        
    #@+others
    #@+node:ekr.20110309051057.14285: *3* get_classes
    def get_classes (self,s,varname):
        
        '''Return a list of classes for string s.'''
        
        self.push_declarations(s)

        aList = self.vars.get(varname,[])
        
        g.trace(aList)
        
        return aList
    #@+node:ekr.20110309051057.14282: *3* set_small_context
    # def set_small_context(self, body):
        
        # """ Set immediate function """

        # self.push_declarations(body)
    #@+node:ekr.20110309051057.14283: *3* push_declarations & helper
    def push_declarations(self,s):

        for line in s.splitlines():
            line = line.lstrip()
            if line.startswith('#'):
                line = line.lstrip('#')
                parts = line.split(':')
                if len(parts) == 2:
                    a,b = parts
                    self.declare(a.strip(),b.strip())
    #@+node:ekr.20110309051057.14284: *4* declare
    def declare(self, var, klass):
        
        # g.trace(var,klass) # Very large trace.

        vars = self.vars.get(var, [])
        if not vars:
            self.vars[var] = vars

        vars.append(klass)
    #@-others
#@+node:ekr.20110309051057.14267: ** Module level...
#@+node:ville.20091204224145.5359: *3* init & helper
def init ():

    global tagLines

    ok = g.app.gui.guiName() == "qt"

    if ok:
        if keep_tag_lines:
            tagLines = read_tags_file()
            if not tagLines:
                print('ctagscompleter: can not read ~/.leo/tags')
                ok = False

        if ok:
            g.registerHandler('after-create-leo-frame',onCreate)
            g.plugin_signon(__name__)

    return ok


# def init ():

    # global tagLines

    # ok = g.app.gui.guiName() == "qt"

    # if ok:
        # g.registerHandler('after-create-leo-frame',onCreate)
        # g.plugin_signon(__name__)

    # return ok
#@+node:ville.20091204224145.5362: *3* install_codewise_completer
# def install_codewise_completer(c):

    # c.k.registerCommand(
            # 'codewise-complete','Alt-0',codewise_complete)

    # c.k.registerCommand(
            # 'codewise-suggest',None, codewise_suggest)

#@+node:ville.20091204224145.5361: *3* onCreate
def onCreate (tag, keys):
    
    '''Register the ctags-complete command for the newly-created commander.'''

    c = keys.get('c')
    if c:
        c.k.registerCommand('ctags-complete','Alt-0',start)
        c.k.registerCommand('codewise-suggest',None, suggest)

# def onCreate (tag, keys):

    # c = keys.get('c')
    # if not c: return

    # install_codewise_completer(c)
#@+node:ekr.20110309051057.14287: *3* read_tags_file
def read_tags_file():

    '''Return the lines of ~/.leo/tags.
    Return [] on error.'''

    trace = False ; verbose = False
    tagsFileName = os.path.expanduser('~/.leo/tags')
    if not os.path.exists(tagsFileName):
        return [] # EKR: 11/18/2009
    assert os.path.isfile(tagsFileName)

    try:
        f = open(tagsFileName)
        tags = f.read()
        lines = g.splitLines(tags)
        if trace:
            print('ctagscomplter.py: ~/.leo/tags has %s lines' % (
                len(lines)))
            if verbose:
                for z in lines[:30]:
                    print(repr(z))
        return lines
    except IOError:
        return []
#@+node:ekr.20110309051057.14269: *3* start (top-level)
def start(event):
    
    '''Call cc.start() where cc is the controller for event's commander.'''
    
    global conrollers

    c = event.get('c')
    if c:
        h = c.hash()
        cc = controllers.get(h)
        if not cc:
            controllers[h] = cc = CodewiseController(c)
        cc.start(event)
#@+node:vivainio.20091217144258.5737: *3* suggest (top-level)
def suggest(event):
    
    '''Call cc.suggest() where cc is the controller for event's commander.'''
    
    global conrollers

    c = event.get('c')
    if not c: return
    
    h = c.hash()
    cc = controllers.get(h)
    if not cc:
        controllers[h] = cc = CodewiseController(c)

    cc.suggest(event)
#@+node:ekr.20110309051057.14270: ** class CodewiseController
class CodewiseController:
    
    #@+others
    #@+node:ekr.20110309051057.14275: *3*  ctor
    def __init__ (self,c):
            
        self.active = False
        self.body = c.frame.top.ui.richTextEdit
        self.c = c
        self.completer = None
        self.popup = None
        self.popup_filter = None
        self.w = c.frame.body.bodyCtrl # A leoQTextEditWidget
        
        # Init.
        self.ev_filter = self.w.ev_filter
        
        # g.trace('CodewiseController',c.shortFileName(),self.body)
    #@+node:ville.20091204224145.5363: *3* complete
    def complete(self,event):

        c = self.c
        cpl = self.completer
        p = c.p
        w = self.w # A leoQTextEditWidget

        head, tail = self.get_current_line(w)
        m = self.get_attr_target_python(head)
        if m:
            obj = m.group(1)
            prefix = m.group(3)
            klasses = guess_class(c,p, obj)
        else:
            klasses = []

        if klasses:
            hits = self.lookup_methods(klasses, prefix)
        else:
            s = self.get_word()
            hits = self.lookup(s)

        model = QtGui.QStringListModel(hits)
        cpl.setModel(model)
        cpl.setCompletionPrefix(prefix)  
        cpl.complete()
    #@+node:ekr.20110309051057.14280: *3* get_attr_target_python
    def get_attr_target_python(self,s):
        
        """ a.b.foob """

        m = re.match(r"(\S+(\.\w+)*)\.(\w*)$", s.lstrip())

        return m
    #@+node:ekr.20110309051057.14279: *3* get_current_line
    def get_current_line(self,w):
        
        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        head, tail = s[i:ins], s[ins:j]

        return head, tail
    #@+node:ekr.20110309051057.14288: *3* get_word
    def get_word (self):
        
        body = self.body 
        tc = body.textCursor()
        tc.select(tc.WordUnderCursor)
        return tc.selectedText()
    #@+node:ville.20091205173337.10142: *3* guess_class
    def guess_class(self,c,p,varname):
        
        '''Return the applicable classes for c,p'''

        # if varname == 'g':
            # return ['leoGlobals']
        if varname == 'p':
            return ['position']
        if varname == 'c':
            return ['Commands']
        if varname == 'self':
            # Return the nearest enclosing class.
            for par in p.parents():
                h = par.h
                m = re.search('class\s+(\w+)', h)
                if m:
                    return [m.group(1)]

        # Do a 'real' analysis
        aList = ContextSniffer().get_classes(p.b,varname)
        g.trace(varname,aList)
        return aList
    #@+node:ville.20091204224145.5364: *3* lookup
    def lookup(self,prefix):

        trace = False
        aList = codewise.cmd_functions([prefix])
        if trace: g.trace(prefix,len(aList))
        hits = (z.split(None,1) for z in aList if z.strip())

        desc = []
        for h in hits:
            s = h[0]
            if 1:
                desc.append(s)
            else:
                sig = h[1].strip()[2:-4].strip()
                desc.append(s + '\t' + sig)

        aList = list(set(desc))
        aList.sort()
        return aList
    #@+node:ville.20091205173337.10140: *3* lookup_methods
    def lookup_methods(self,klasses, prefix):
        
        trace = True

        aList = codewise.cmd_members([klasses[0]])
        hits = (z.split(None,1) for z in aList if z.strip())

        #ctags patterns need radical cleanup
        desc = []
        for h in hits:
            s = h[0]
            fn = h[1].strip()
            if fn.startswith('/'):
                sig = fn[2:-4].strip()
            else:
                sig = fn
            desc.append(s + '\t' + sig)

        aList = list(set(desc))
        aList.sort()
        
        if trace: g.trace(prefix,len(aList))
        return aList
    #@+node:ekr.20110309051057.14273: *3* start
    def start (self,event):
        
        c = self.c
        
        # Create the callback to insert the selected completion.
        def completion_callback(completion,self=self):
            self.end(completion)
        
        # Create the completer.
        cpl = c.frame.top.completer = self.completer = QCompleter()
        cpl.setWidget(self.body)
        cpl.connect(cpl,QtCore.SIGNAL("activated(QString)"),completion_callback)

        # Set the flag for the event filter: all keystrokes will go to cc.onKey.
        self.active = True
        self.ev_filter.ctagscompleter_active = True
        self.ev_filter.ctagscompleter_onKey = self.onKey
        
        # Show the completions.
        self.complete(event)
    #@+node:ekr.20110309051057.14272: *3* suggest
    def suggest(self,event=None,pattern=''):

        trace = True
        c,w = self.c,self.w ; p = c.p
        
        if not pattern:
            pattern,tail = self.get_current_line(w)
         
        m = self.get_attr_target_python(pattern)

        if m:
            obj = m.group(1)
            prefix = m.group(3)
            klasses = self.guess_class(c,p,obj)
        else:
            if trace: g.trace('no attr for %s' % (pattern))
            prefix = pattern
            klasses = []

        if klasses:
            if trace: g.trace('klasses: %s' % (klasses))
            hits = self.lookup_methods(klasses,prefix)
            hits = [h for h in hits if h.startswith(prefix)]
        else:
            # s = self.get_word()
            if trace: g.trace('prefix: %s' % (prefix))
            hits = self.lookup(prefix)

        if 0:
            cpl = self.completer
            model = QtGui.QStringListModel(hits)
            cpl.setModel(model)
            cpl.setCompletionPrefix(prefix)  
            cpl.complete()
        else:
            print("%s Completions for %s:" % (len(hits),prefix))
            for h in hits[:20]:
                print(h)
    #@-others
#@-others
#@-leo
