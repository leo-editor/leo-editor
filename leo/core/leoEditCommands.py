# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20050710142719: * @file leoEditCommands.py
#@@first

'''Basic editor commands for Leo.

Modelled after Emacs and Vim commands.'''

#@+<< imports >>
#@+node:ekr.20050710151017: ** << imports >> (leoEditCommands)
import leo.core.leoGlobals as g
import leo.core.leoFind as leoFind
import difflib   
docutils = g.importExtension('docutils',pluginName='leoEditCommands.py')
try:
    import enchant
except ImportError:
    enchant = None
import os
import re
if g.isPython3:
    from functools import reduce
import shlex
import string
import subprocess # Always exists in Python 2.6 and above.
import sys
#@-<< imports >>

#@+<< define class baseEditCommandsClass >>
#@+node:ekr.20050920084036.1: ** << define class baseEditCommandsClass >>
class baseEditCommandsClass:

    '''The base class for all edit command classes'''

    #@+others
    #@+node:ekr.20050920084036.2: *3*  Birth (baseEditCommandsClass)
    def __init__ (self,c):

        self.c = c
        self.k = None
        self.registers = {} # To keep pychecker happy.
        self.undoData = None
        self.w = None

    def finishCreate(self):

        self.k = self.c.k
        try:
            self.w = self.c.frame.body.bodyCtrl # New in 4.4a4.
        except AttributeError:
            self.w = None

    def init (self):
        '''Called from k.keyboardQuit to init all classes.'''
        pass
    #@+node:ekr.20051214132256: *3* begin/endCommand (baseEditCommands)
    #@+node:ekr.20051214133130: *4* beginCommand  & beginCommandWithEvent
    def beginCommand (self,undoType='Typing'):

        '''Do the common processing at the start of each command.'''

        return self.beginCommandHelper(ch='',undoType=undoType,w=self.w)

    def beginCommandWithEvent (self,event,undoType='Typing'):

        '''Do the common processing at the start of each command.'''

        return self.beginCommandHelper(
            ch=event and event.char or '',
            undoType=undoType,w=event.widget)
    #@+node:ekr.20051215102349: *5* beingCommandHelper
    # New in Leo 4.4b4: calling beginCommand is valid for all widgets,
    # but does nothing unless we are in the body pane.

    def beginCommandHelper (self,ch,undoType,w):

        c = self.c ; p = c.p
        name = c.widget_name(w)

        if name.startswith('body'):
            oldSel =  w.getSelectionRange()
            oldText = p.b
            self.undoData = b = g.Bunch()
            # To keep pylint happy.
            b.ch=ch
            b.name=name
            b.oldSel=oldSel
            b.oldText=oldText
            b.w=w
            b.undoType=undoType
        else:
            self.undoData = None

        return w
    #@+node:ekr.20051214133130.1: *4* endCommand (baseEditCommand)
    # New in Leo 4.4b4: calling endCommand is valid for all widgets,
    # but handles undo only if we are in body pane.

    def endCommand(self,label=None,changed=True,setLabel=True):

        '''Do the common processing at the end of each command.'''

        trace =  False and not g.unitTesting
        c = self.c ; b = self.undoData ; k = self.k

        if trace: g.trace('changed',changed)

        if b and b.name.startswith('body') and changed:
            c.frame.body.onBodyChanged(undoType=b.undoType,
                oldSel=b.oldSel,oldText=b.oldText,oldYview=None)

        self.undoData = None # Bug fix: 1/6/06 (after a5 released).

        k.clearState()

        # Warning: basic editing commands **must not** set the label.
        if setLabel:
            if label:
                k.setLabelGrey(label)
            else:
                k.resetLabel()
    #@+node:ekr.20061007105001: *3* editWidget (baseEditCommandsClass)
    def editWidget (self,event,forceFocus=True):

        trace = False and not g.unitTesting
        c = self.c
        w = event and event.widget
        wname = (w and c.widget_name(w)) or '<no widget>'
        isTextWidget = g.app.gui.isTextWidget(w)

        # New in Leo 4.5: single-line editing commands apply to minibuffer widget.
        if w and isTextWidget:
            self.w = w
        else:
            self.w = self.c.frame.body and self.c.frame.body.bodyCtrl

        if trace: g.trace(isTextWidget,wname,w)

        if self.w and forceFocus:
            c.widgetWantsFocusNow(self.w)

        return self.w
    #@+node:ekr.20050920084036.5: *3* getPublicCommands & getStateCommands
    def getPublicCommands (self):

        '''Return a dict describing public commands implemented in the subclass.
        Keys are untranslated command names.  Values are methods of the subclass.'''

        return {}
    #@+node:ekr.20050920084036.6: *3* getWSString
    def getWSString (self,s):

        return ''.join([g.choose(ch=='\t',ch,' ') for ch in s])
    #@+node:ekr.20050920084036.7: *3* oops
    def oops (self):

        g.pr("baseEditCommandsClass oops:",
            g.callers(),
            "must be overridden in subclass")
    #@+node:ekr.20050929161635: *3* Helpers
    #@+node:ekr.20050920084036.249: *4* _chckSel
    def _chckSel (self,event,warning='no selection'):

        k = self.k
        w = self.editWidget(event)
        val = w and w.hasSelection()
        if warning and not val:
            k.setLabelGrey(warning)
        return val
    #@+node:ekr.20050920084036.250: *4* _checkIfRectangle
    def _checkIfRectangle (self,event):

        c,k = self.c,self.k

        key = event and event.char.lower() or ''

        val = self.registers.get(key)

        if val and type(val) == type([]):
            k.clearState()
            k.setLabelGrey("Register contains Rectangle, not text")
            return True

        return False
    #@+node:ekr.20050920084036.233: *4* getRectanglePoints
    def getRectanglePoints (self,w):

        c = self.c
        c.widgetWantsFocusNow(w)

        s = w.getAllText()
        i,j = w.getSelectionRange()
        r1,r2 = g.convertPythonIndexToRowCol(s,i)
        r3,r4 = g.convertPythonIndexToRowCol(s,j)

        return r1+1,r2,r3+1,r4
    #@+node:ekr.20051002090441: *4* keyboardQuit
    def keyboardQuit (self,event=None):

        '''Clear the state and the minibuffer label.'''

        return self.k.keyboardQuit()
    #@-others
#@-<< define class baseEditCommandsClass >>

#@+others
#@+node:ekr.20120315062642.9746: ** Module-level commands
#@+node:ekr.20120315062642.9743: *3* URL's (leoEditCommands)
#@+node:ekr.20120315062642.9742: *4* openUrl (open-url)
@g.command('open-url')
def openUrl(event):
    c = event.get('c')
    if c:
        g.openUrl(c.p)

@g.command('open-url-under-cursor')
def openUrlUnderCursor(event):
    return g.openUrlOnClick(event)
#@+node:ekr.20120315062642.9745: *4* ctrlClickAtCursor (ctrl-click-at-cursor)
@g.command('ctrl-click-at-cursor')
def ctrlClickAtCursor(event):
    c = event.get('c')
    if c:
        g.openUrlOnClick(event)
#@+node:ekr.20120211121736.10817: ** class EditCommandsManager
class EditCommandsManager:

    '''A class to init all edit commands properly.

    This class eliminates the circular dependencies that otherwise
    would arise from the module-level classesList.
    '''


    #@+others
    #@+node:ekr.20120211121736.10830: *3*  ecm.ctor
    def __init__ (self,c):

        self.c = c

        self.classesList = (
            ('abbrevCommands',      abbrevCommandsClass),
            ('bufferCommands',      bufferCommandsClass),
            ('editCommands',        editCommandsClass),
            ('chapterCommands',     chapterCommandsClass),
            ('controlCommands',     controlCommandsClass),
            ('debugCommands',       debugCommandsClass),
            ('editFileCommands',    editFileCommandsClass),
            ('helpCommands',        helpCommandsClass),
            ('keyHandlerCommands',  keyHandlerCommandsClass),
            ('killBufferCommands',  killBufferCommandsClass),
            ('leoCommands',         leoCommandsClass),
            ('macroCommands',       macroCommandsClass),
            # ('queryReplaceCommands',queryReplaceCommandsClass),
            ('rectangleCommands',   rectangleCommandsClass),
            ('registerCommands',    registerCommandsClass),
            ('searchCommands',      searchCommandsClass),
            ('spellCommands',       spellCommandsClass),
        )


    #@+node:ekr.20120211121736.10827: *3* ecm.createEditCommanders
    def createEditCommanders (self):

        '''Create edit classes in the commander.'''

        c = self.c

        for name, theClass in self.classesList:
            theInstance = theClass(c)# Create the class.
            setattr(c,name,theInstance)
            # g.trace(name,theInstance)
    #@+node:ekr.20120211121736.10828: *3* ecm.finishCreateEditCommanders
    def finishCreateEditCommanders (self):

        '''Finish creating edit classes in the commander.
        Return the commands dictionary for all the classes.'''

        c,d = self.c,{}
        for name, theClass in self.classesList:
            theInstance = getattr(c,name)
            theInstance.finishCreate()
            theInstance.init()
            d2 = theInstance.getPublicCommands()
            if d2:
                d.update(d2)
                if 0:
                    g.pr('----- %s' % name)
                    for key in sorted(d2): g.pr(key)

        return d
    #@+node:ekr.20120211121736.10829: *3* ecm.initAllEditCommanders
    def initAllEditCommanders (self):

        '''Re-init classes in the commander.'''

        c = self.c

        for name, theClass in self.classesList:
            theInstance = getattr(c,name)
            theInstance.init()
    #@-others
#@+node:ekr.20050920084036.13: ** abbrevCommandsClass
class abbrevCommandsClass (baseEditCommandsClass):

    '''A class to handle user-defined abbreviations.

    See apropos-abbreviations for details.'''

    #@+others
    #@+node:ekr.20100901080826.6002: *3*  Birth
    #@+node:ekr.20100901080826.6003: *4* ctor (abbrevCommandsClass
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        # Set local ivars.
        self.abbrevs ={} # Keys are names, values are (abbrev,tag).
        self.daRanges = []
        self.event = None
        self.dynaregex = re.compile( # For dynamic abbreviations
            r'[%s%s\-_]+'%(string.ascii_letters,string.digits))
            # Not a unicode problem.
        self.globalDynamicAbbrevs = c.config.getBool('globalDynamicAbbrevs')
        self.store ={'rlist':[], 'stext':''} # For dynamic expansion.
        self.w = None
    #@+node:ekr.20100901080826.6004: *4* finishCreate (abbrevClass) & helpers
    def finishCreate(self):
        
        c,k = self.c,self.c.k
        baseEditCommandsClass.finishCreate(self)
        self.init_settings()
        self.init_abbrev()
        self.init_env()
        if (not g.app.initing and not g.unitTesting and
            not g.app.batchMode and not c.gui.isNullGui
        ):
            g.red('Abbreviations %s' % ('on' if c.k.abbrevOn else 'off'))
    #@+node:ekr.20130924110246.13738: *5* init_abbrev
    def init_abbrev(self):
        
        '''Init the user abbreviations from @data global-abbreviations
        and @data abbreviations nodes.
        '''

        c = self.c
        table = (
            ('global-abbreviations','global'),
            ('abbreviations','local'),
        )
        for source,tag in table:
            aList = c.config.getData(source,strip_data=False) or []
            abbrev,result = [],[]
            for s in aList:
                if s.startswith('\\:'):
                    # Continue the previous abbreviation.
                    abbrev.append(s[2:])
                else:
                    # End the previous abbreviation.
                    if abbrev:
                        result.append(''.join(abbrev))
                        abbrev = []
                    # Start the new abbreviation.
                    if s.strip():
                        abbrev.append(s)
            # End any remaining abbreviation.
            if abbrev:
                result.append(''.join(abbrev))
            for s in result:
                self.addAbbrevHelper(s,tag)
    #@+node:ekr.20130924110246.13748: *5* init_env
    def init_env(self):
        
        '''Init c.abbrev_subst_env by executing the contents of the
        @data abbreviations-subst-env node.'''
        
        c = self.c
        if c.abbrev_place_start and self.enabled:
            aList = self.subst_env
            result = []
            for z in aList:
                # Compatibility with original design.
                if z.startswith('\\:'):
                    result.append(z[2:])
                else:
                    result.append(z)
            result = ''.join(result)
            try:
                exec(result,c.abbrev_subst_env,c.abbrev_subst_env)
            except Exception:
                g.es('Error exec\'ing @data abbreviations-subst-env')
                g.es_exception()
        else:
            c.abbrev_subst_start = False
            # if c.config.getString('abbreviations-subst-start'):
                # g.es("Note: @abbreviations-subst-start found, but no substitutions "
                     # "without @scripting-at-script-nodes = True")
    #@+node:ekr.20130924110246.13749: *5* init_settings
    def init_settings(self):
        
        c = self.c
        c.k.abbrevOn = c.config.getBool('enable-abbreviations',default=False)
        # Init these here for k.masterCommand.
        c.abbrev_place_end = c.config.getString('abbreviations-place-end')
        c.abbrev_place_start = c.config.getString('abbreviations-place-start')
        c.abbrev_subst_end = c.config.getString('abbreviations-subst-end')
        c.abbrev_subst_env = {'c': c,'g': g,'_values': {},}
            # The environment for all substitutions.
            # May be augmented in init_env.
        c.abbrev_subst_start = c.config.getString('abbreviations-subst-start')
        # Local settings.
        self.enabled = (
            c.config.getBool('scripting-at-script-nodes') or
            c.config.getBool('scripting-abbreviations'))
        self.subst_env = c.config.getData('abbreviations-subst-env',strip_data=False)
        
        
    #@+node:ekr.20050920084036.15: *4* getPublicCommands & getStateCommands
    def getPublicCommands (self):

        return {

            # Non-prefixed commands.
            'toggle-abbrev-mode':   self.toggleAbbrevMode,

            # Dynamic...
            'dabbrev-completion':   self.dynamicCompletion,
            'dabbrev-expands':      self.dynamicExpansion,

            # Static...
            'abbrev-add-global':        self.addAbbreviation,
            # 'abbrev-expand-region':   self.regionalExpandAbbrev,
            'abbrev-inverse-add-global':self.addInverseAbbreviation,
            'abbrev-kill-all':          self.killAllAbbrevs,
            'abbrev-list':              self.listAbbrevs,
            'abbrev-read':              self.readAbbreviations,
            'abbrev-write':             self.writeAbbreviations,
        }
    #@+node:ekr.20100901080826.6155: *3*  Entry point
    #@+node:ekr.20050920084036.27: *4* expandAbbrev
    def expandAbbrev (self,event,stroke):

        '''Not a command.  Called from k.masterCommand to expand
        abbreviations in event.widget.

        Words start with '@'.
        '''

        trace = False and not g.unitTesting
        c = self.c
        ch = event and event.char or ''
        w = self.editWidget(event,forceFocus=False)
        if not w: return False
        if w.hasSelection(): return False
        assert g.isStrokeOrNone(stroke)
        if stroke in ('BackSpace','Delete'):
            if trace: g.trace(stroke)
            return False
        d = {'Return':'\n','Tab':'\t','space':' ','underscore':'_'}
        if stroke:
            ch = d.get(stroke.s,stroke.s)
            if len(ch) > 1:
                if (stroke.find('Ctrl+') > -1 or
                    stroke.find('Alt+') > -1 or
                    stroke.find('Meta+') > -1
                ):
                    ch = ''
                else:
                    ch = event and event.char or ''
        else:
            ch = event.char
        if trace: g.trace('ch',repr(ch),'stroke',repr(stroke))

        # New code allows *any* sequence longer than 1 to be an abbreviation.
        # Any whitespace stops the search.
        s = w.getAllText()
        j = w.getInsertPoint()
        i = j-1
        while len(s) > i >= 0 and s[i] not in ' \t\n':
            prefix = s[i:j]
            word = prefix+ch
            val,tag = self.abbrevs.get(word,(None,None))
            if trace: g.trace(repr(word),val,tag)
            if val:
                # Require a word match if the abbreviation is itself a word.
                if ch in ' \t\n': word = word.rstrip()
                if word.isalnum() and word[0].isalpha():
                    if i == 0 or s[i-1] in ' \t\n':
                        break
                    else:
                        i -= 1
                else:
                    break
            else: i -= 1
        else:
            return False

        if c.abbrev_subst_start:
            
            while c.abbrev_subst_start in val:
                
                prefix, rest = val.split(c.abbrev_subst_start, 1)
                content = rest.split(c.abbrev_subst_end, 1)
                if len(content) != 2:
                    break
                content, rest = content
                c.abbrev_subst_env['_abr'] = word

                exec(content, c.abbrev_subst_env, c.abbrev_subst_env)

                val = "%s%s%s" % (prefix, c.abbrev_subst_env['x'], rest)
                
        if val == "__NEXT_PLACEHOLDER":
            # user explicitly called for next placeholder in an abbrev.
            # inserted previously
            val = ''
            do_placeholder = True
        else:
            do_placeholder = False 

        if trace: g.trace('**inserting',repr(val))
        oldSel = j,j
        c.frame.body.onBodyChanged(undoType='Typing',oldSel=oldSel)
        if i != j: w.delete(i,j)
        w.insert(i,val)
        c.frame.body.forceFullRecolor() # 2011/10/21
        c.frame.body.onBodyChanged(undoType='Abbreviation',oldSel=oldSel)

        if (do_placeholder or
            c.abbrev_place_start and c.abbrev_place_start in val):
            new_text, start, end = self.next_place(c.frame.body.getAllText(), offset=i)
            if start is not None:
                c.frame.body.setAllText(new_text)
                # setInsertPoint() clears selection raise, so must come first
                c.frame.body.setInsertPoint(end)
                c.frame.body.setSelectionRange(start, end)
            
        return True
    #@+node:tbrown.20130326094709.25669: *4* next_place
    def next_place(self, text, offset=0):
        """Given text containing a placeholder like <|block01|>,
        return text2, start, end where text2 is the text without
        the <| and |>, and start, end are the positions of the
        beginning and end of block01.
        """

        c = self.c
        new_pos = text.find(c.abbrev_place_start, offset)
        new_end = text.find(c.abbrev_place_end, offset)
        if (new_pos < 0 or new_end < 0) and offset:
            new_pos = text.find(c.abbrev_place_start)
            new_end = text.find(c.abbrev_place_end)
            if not(new_pos < 0 or new_end < 0):
                g.es("Found placeholder earlier in body")
            
        if new_pos < 0 or new_end < 0:
            return text, None, None

        start = new_pos
        place_holder_delim = text[new_pos:new_end+len(c.abbrev_place_end)]
        place_holder = place_holder_delim[
            len(c.abbrev_place_start):-len(c.abbrev_place_end)]
        text2 = text[:start]+place_holder+text[start+len(place_holder_delim):]
        
        return text2, start, start+len(place_holder)
    #@+node:ekr.20050920084036.58: *3* dynamic abbreviation...
    #@+node:ekr.20050920084036.60: *4* dynamicCompletion C-M-/
    def dynamicCompletion (self,event=None):

        '''dabbrev-completion
        Insert the common prefix of all dynamic abbrev's matching the present word.
        This corresponds to C-M-/ in Emacs.'''

        c,p,u = self.c,self.c.p,self.c.p.v.u
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins -= 1
        i,j = g.getWord(s,ins)
        word = w.get(i,j)
        aList = self.getDynamicList(w,word)
        if not aList: return
        # Bug fix: remove s itself, otherwise we can not extend beyond it.
        if word in aList and len(aList) > 1: aList.remove(word)
        prefix = reduce(g.longestCommonPrefix,aList)
        if prefix.strip():
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p,oldYScroll=ypos)
            p.b = p.b[:i] + prefix + p.b[j:]
            w.setAllText(p.b)
            w.setInsertPoint(i+len(prefix))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p,
                command='dabbrev-completion',bunch=b,dirtyVnodeList=[]) 
    #@+node:ekr.20050920084036.59: *4* dynamicExpansion M-/
    def dynamicExpansion (self,event=None):

        '''dabbrev-expands (M-/ in Emacs).
        Inserts the longest common prefix of the word at the cursor. Displays
        all possible completions if the prefix is the same as the word.
        '''

        c = self.c
        p = c.p
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins -= 1
        i,j = g.getWord(s,ins)
        word = w.get(i,j)
        aList = self.getDynamicList(w,word)
        if not aList: return
        if word in aList and len(aList) > 1: aList.remove(word)
        prefix = reduce(g.longestCommonPrefix,aList)
        prefix = prefix.strip()
        # g.trace(word,prefix,aList)
        if False and prefix and prefix != word and len(aList) == 1:
            s = w.getAllText()
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p,oldYScroll=ypos)
            p.b = p.b[:i] + prefix + p.b[j:]
            w.setAllText(p.b)
            w.setInsertPoint(i+len(prefix))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p,
                command='dabbrev-expands',bunch=b,dirtyVnodeList=[])
        else:
            self.dynamicExpandHelper(event,prefix,aList,w)
    #@+node:ekr.20070605110441: *5* dynamicExpandHelper (added event arg)
    def dynamicExpandHelper (self,event,prefix=None,aList=None,w=None):

        c = self.c ; k = c.k ; p = c.p
        tag = 'dabbrev-expand'
        state = k.getState(tag)
        if state == 0:
            self.w = w
            prefix2 = 'dabbrev-expand: '
            c.frame.log.deleteTab('Completion')
            g.es('','\n'.join(aList),tabName='Completion')
            k.setLabelBlue(prefix2+prefix,protect=True)
            k.getArg(event,tag,1,self.dynamicExpandHelper,prefix=prefix2,tabList=aList)
        else:
            c.frame.log.deleteTab('Completion')
            k.clearState()
            k.resetLabel()
            if k.arg:
                w = self.w
                s = w.getAllText()
                ypos = w.getYScrollPosition()
                b = c.undoer.beforeChangeNodeContents(p,oldYScroll=ypos)
                ins = w.getInsertPoint()
                if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins -= 1
                i,j = g.getWord(s,ins)
                p.b = p.b[:i] + k.arg + p.b[j:]
                w.setAllText(p.b)
                w.setInsertPoint(i+len(k.arg))
                w.setYScrollPosition(ypos)
                c.undoer.afterChangeNodeContents(p,
                    command=tag,bunch=b,dirtyVnodeList=[]) 
    #@+node:ekr.20050920084036.61: *4* getDynamicList (helper)
    def getDynamicList (self,w,s):

        if self.globalDynamicAbbrevs:
            # Look in all nodes.h
            items = []
            for p in self.c.all_unique_positions():
                items.extend(self.dynaregex.findall(p.b))
        else:
            # Just look in this node.
            items = self.dynaregex.findall(w.getAllText())

        items = sorted(set([z for z in items if z.startswith(s)]))

        # g.trace(repr(s),repr(sorted(items)))
        return items
    #@+node:ekr.20070531103114: *3* static abbrevs
    #@+node:ekr.20100901080826.6001: *4* addAbbrevHelper
    def addAbbrevHelper (self,s,tag=''):

        '''Enter the abbreviation 's' into the self.abbrevs dict.'''

        if not s.strip(): return

        try:
            d = self.abbrevs
            data = s.split('=')
            # name = data[0].strip()
            # 2012/02/29: Do *not* strip ws, and allow the user to specify ws.
            name = data[0].replace('\\t','\t').replace('\\n','\n')
            val = '='.join(data[1:])
            if val.endswith('\n'): val = val[:-1]
            val = val.replace('\\n','\n')
            old,tag = d.get(name,(None,None),)
            if old and old != val and not g.unitTesting:
                g.es_print('redefining abbreviation',name,
                    '\nfrom',repr(old),'to',repr(val))
            d [name] = val,tag

        except ValueError:
            g.es_print('bad abbreviation: %s' % s)
    #@+node:ekr.20050920084036.25: *4* addAbbreviation
    def addAbbreviation (self,event):

        '''Add an abbreviation:
        The selected text is the abbreviation;
        the minibuffer prompts you for the name of the abbreviation.
        Also sets abbreviations on.'''

        k = self.k ; state = k.getState('add-abbr')

        if state == 0:
            w = self.editWidget(event) # Sets self.w
            if not w: return
            k.setLabelBlue('Add Abbreviation: ',protect=True)
            k.getArg(event,'add-abbr',1,self.addAbbreviation)
        else:
            w = self.w
            k.clearState()
            k.resetLabel()
            value = k.argSelectedText # 2010/09/01.
            if k.arg.strip():
                self.abbrevs [k.arg] = value,'dynamic'
                k.abbrevOn = True
                k.setLabelGrey(
                    "Abbreviation (on): '%s' = '%s'" % (
                        k.arg,value))
    #@+node:ekr.20051004080550: *4* addInverseAbbreviation
    def addInverseAbbreviation (self,event):

        '''Add an inverse abbreviation:
        The selected text is the abbreviation name;
        the minibuffer prompts you for the value of the abbreviation.'''

        k = self.k ; state = k.getState('add-inverse-abbr')

        if state == 0:
            w = self.editWidget(event) # Sets self.w
            if not w: return
            k.setLabelBlue('Add Inverse Abbreviation: ',protect=True)
            k.getArg(event,'add-inverse-abbr',1,self.addInverseAbbreviation)
        else:
            w = self.w
            k.clearState()
            k.resetLabel()
            s = w.getAllText()
            i = w.getInsertPoint()
            i,j = g.getWord(s,i-1)
            word = s[i:j]
            if word:
                self.abbrevs [word] = k.arg,'add-inverse-abbr'
    #@+node:ekr.20050920084036.18: *4* killAllAbbrevs
    def killAllAbbrevs (self,event):

        '''Delete all abbreviations.'''

        self.abbrevs = {}
    #@+node:ekr.20050920084036.19: *4* listAbbrevs
    def listAbbrevs (self,event=None):

        '''List all abbreviations.'''

        d = self.abbrevs
        if d:
            g.es('Abbreviations...')
            keys = list(d.keys())
            keys.sort()
            for name in keys:
                val,tag = d.get(name)
                val = val.replace('\n','\\n')
                tag = tag or ''
                tag = g.choose(tag,tag+': ','')
                g.es('','%s%s=%s' % (tag,name,val))
        else:
            g.es('No present abbreviations')
    #@+node:ekr.20050920084036.20: *4* readAbbreviations & helper
    def readAbbreviations (self,event=None):

        '''Read abbreviations from a file.'''

        fileName = g.app.gui.runOpenFileDialog(
            title = 'Open Abbreviation File',
            filetypes = [("Text","*.txt"), ("All files","*")],
            defaultextension = ".txt")

        if fileName:
            self.readAbbreviationsFromFile(fileName)
    #@+node:ekr.20100901080826.6156: *5* readAbbreviationsFromFile
    def readAbbreviationsFromFile(self,fileName):

        k = self.c.k

        try:
            f = open(fileName)
            for s in f:
                self.addAbbrevHelper(s,'file')
            f.close()
            k.abbrevOn = True
            g.es("Abbreviations on")
            # self.listAbbrevs()
        except IOError:
            g.es('can not open',fileName)
    #@+node:ekr.20050920084036.23: *4* toggleAbbrevMode
    def toggleAbbrevMode (self,event=None):

        '''Toggle abbreviation mode.'''

        k = self.k
        k.abbrevOn = not k.abbrevOn
        k.keyboardQuit()
        # k.setLabel('Abbreviations are ' + g.choose(k.abbrevOn,'On','Off'))
        if not g.unitTesting and not g.app.batchMode:
            g.es('Abbreviations are ' + g.choose(k.abbrevOn,'on','off'))
    #@+node:ekr.20050920084036.24: *4* writeAbbreviation
    def writeAbbreviations (self,event):

        '''Write abbreviations to a file.'''

        fileName = g.app.gui.runSaveFileDialog(
            initialfile = None,
            title='Write Abbreviations',
            filetypes = [("Text","*.txt"), ("All files","*")],
            defaultextension = ".txt")

        if not fileName: return

        try:
            d = self.abbrevs
            f = open(fileName,'w')
            keys = list(d.keys)
            keys.sort()
            for name in keys:
                val,tag = self.abbrevs.get(name)
                val=val.replace('\n','\\n')
                s = '%s=%s\n' % (name,val)
                if not g.isPython3:
                    s = g.toEncodedString(s,reportErrors=True)
                f.write(s)
            f.close()
        except IOError:
            g.es('can not create',fileName)
    #@-others
#@+node:ekr.20050920084036.31: ** bufferCommandsClass
#@+at
# An Emacs instance does not have knowledge of what is considered a
# buffer in the environment.
# 
# The call to setBufferInteractionMethods calls the buffer configuration methods.
#@@c

class bufferCommandsClass (baseEditCommandsClass):

    #@+others
    #@+node:ekr.20050920084036.32: *3*  ctor (bufferCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        self.fromName = '' # Saved name from getBufferName.
        self.nameList = [] # [n: <headline>]
        self.names = {}
        self.tnodes = {} # Keys are n: <headline>, values are tnodes.

        try:
            self.w = c.frame.body.bodyCtrl
        except AttributeError:
            self.w = None
    #@+node:ekr.20050920084036.33: *3*  getPublicCommands
    def getPublicCommands (self):

        return {

            # These do not seem useful.
                # 'copy-to-buffer':     self.copyToBuffer,
                # 'insert-to-buffer':   self.insertToBuffer,

            'buffer-append-to':             self.appendToBuffer,
            'buffer-kill' :                 self.killBuffer,
            'buffer-prepend-to':            self.prependToBuffer,
            # 'buffer-rename':              self.renameBuffer,
            'buffer-switch-to':             self.switchToBuffer,
            'buffers-list' :                self.listBuffers,
            'buffers-list-alphabetically':  self.listBuffersAlphabetically,
        }
    #@+node:ekr.20050920084036.34: *3* Entry points
    #@+node:ekr.20050920084036.35: *4* appendToBuffer
    def appendToBuffer (self,event):

        '''Add the selected body text to the end of the body text of a named buffer (node).'''

        w = self.editWidget(event) # Sets self.w
        if w:
            self.k.setLabelBlue('Append to buffer: ')
            self.getBufferName(event,self.appendToBufferFinisher)

    def appendToBufferFinisher (self,name):

        c,w = self.c,self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            w = self.w
            c.selectPosition(p)
            self.beginCommand('append-to-buffer: %s' % p.h)
            w.insert('end',s)
            w.setInsertPoint('end')
            w.seeInsertPoint()
            self.endCommand()
            c.redraw_after_icons_changed()
            c.recolor()
    #@+node:ekr.20050920084036.36: *4* copyToBuffer
    def copyToBuffer (self,event):

        '''Add the selected body text to the end of the body text of a named buffer (node).'''

        w = self.editWidget(event) # Sets self.w
        if w:
            self.k.setLabelBlue('Copy to buffer: ')
            self.getBufferName(event,self.copyToBufferFinisher)

    def copyToBufferFinisher (self,name):

        c,w = self.c,self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand('copy-to-buffer: %s' % p.h)
            w.insert('end',s)
            w.setInsertPoint('end')
            self.endCommand()
            c.redraw_after_icons_changed()
            c.recolor()
    #@+node:ekr.20050920084036.37: *4* insertToBuffer
    def insertToBuffer (self,event):

        '''Add the selected body text at the insert point of the body text of a named buffer (node).'''

        w = self.editWidget(event) # Sets self.w
        if w:
            self.k.setLabelBlue('Insert to buffer: ')
            self.getBufferName(event,self.insertToBufferFinisher)

    def insertToBufferFinisher (self,name):

        c,w = self.c,self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand('insert-to-buffer: %s' % p.h)
            i = w.getInsertPoint()
            w.insert(i,s)
            w.seeInsertPoint()
            self.endCommand()
            c.redraw_after_icons_changed()
    #@+node:ekr.20050920084036.38: *4* killBuffer
    def killBuffer (self,event):

        '''Delete a buffer (node) and all its descendants.'''

        w = self.editWidget(event) # Sets self.w
        if not w: return

        self.k.setLabelBlue('Kill buffer: ')
        self.getBufferName(event,self.killBufferFinisher)

    def killBufferFinisher (self,name):

        c = self.c ; p = self.findBuffer(name)
        if p:
            h = p.h
            current = c.p
            c.selectPosition(p)
            c.deleteOutline (op_name='kill-buffer: %s' % h)
            c.selectPosition(current)
            self.k.setLabelBlue('Killed buffer: %s' % h)
            c.redraw(current)
    #@+node:ekr.20050920084036.42: *4* listBuffers & listBuffersAlphabetically
    def listBuffers (self,event):

        '''List all buffers (node headlines), in outline order.
        Nodes with the same headline are disambiguated by giving their parent or child index.
        '''

        self.computeData()
        g.es('buffers...')
        for name in self.nameList:
            g.es('',name)

    def listBuffersAlphabetically (self,event):

        '''List all buffers (node headlines), in alphabetical order.
        Nodes with the same headline are disambiguated by giving their parent or child index.'''

        self.computeData()
        names = self.nameList[:] ; names.sort()

        g.es('buffers...')
        for name in names:
            g.es('',name)
    #@+node:ekr.20050920084036.39: *4* prependToBuffer
    def prependToBuffer (self,event):

        '''Add the selected body text to the start of the body text of a named buffer (node).'''

        w = self.editWidget(event) # Sets self.w
        if w:
            self.k.setLabelBlue('Prepend to buffer: ')
            self.getBufferName(event,self.prependToBufferFinisher)

    def prependToBufferFinisher (self,name):

        c,w = self.c,self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand('prepend-to-buffer: %s' % p.h)
            w.insert(0,s)
            w.setInsertPoint(0)
            w.seeInsertPoint()
            self.endCommand()
            c.redraw_after_icons_changed()
            c.recolor()
    #@+node:ekr.20050920084036.43: *4* renameBuffer
    def renameBuffer (self,event):

        '''Rename a buffer, i.e., change a node's headline.'''

        g.es('rename-buffer not ready yet')
        if 0:
            self.k.setLabelBlue('Rename buffer from: ')
            self.getBufferName(event,self.renameBufferFinisher1)

    def renameBufferFinisher1 (self,name):

        self.fromName = name
        self.k.setLabelBlue('Rename buffer from: %s to: ' % (name))
        event = None
        self.getBufferName(event,self.renameBufferFinisher2)

    def renameBufferFinisher2 (self,name):

        c = self.c ; p = self.findBuffer(self.fromName)
        if p:
            c.endEditing()
            c.setHeadString(p,name)
            c.redraw(p)
    #@+node:ekr.20050920084036.40: *4* switchToBuffer
    def switchToBuffer (self,event):

        '''Select a buffer (node) by its name (headline).'''

        self.k.setLabelBlue('Switch to buffer: ')
        self.getBufferName(event,self.switchToBufferFinisher)

    def switchToBufferFinisher (self,name):

        c = self.c ; p = self.findBuffer(name)
        if p:
            c.selectPosition(p)
            c.redraw_after_select(p)

    #@+node:ekr.20050927102133.1: *3* Utils
    #@+node:ekr.20051215121416: *4* computeData
    def computeData (self):

        self.nameList = []
        self.names = {} ; self.tnodes = {}

        for p in self.c.all_unique_positions():
            h = p.h.strip()
            v = p.v
            nameList = self.names.get(h,[])
            if nameList:
                if p.parent():
                    key = '%s, parent: %s' % (h,p.parent().h)
                else:
                    key = '%s, child index: %d' % (h,p.childIndex())
            else:
                key = h
            self.nameList.append(key)
            self.tnodes[key] = v
            nameList.append(key)
            self.names[h] = nameList
    #@+node:ekr.20051215164823: *4* findBuffer
    def findBuffer (self,name):

        v = self.tnodes.get(name)

        for p in self.c.all_unique_positions():
            if p.v == v:
                return p

        g.trace("Can't happen",name)
        return None
    #@+node:ekr.20050927093851: *4* getBufferName (added event arg)
    def getBufferName (self,event,finisher):

        '''Get a buffer name into k.arg and call k.setState(kind,n,handler).'''

        c,k = self.c,self.k
        state = k.getState('getBufferName')

        if state == 0:
            self.computeData()
            self.getBufferNameFinisher = finisher
            prefix = k.getLabel()
            k.getArg(event,'getBufferName',1,self.getBufferName,
                prefix=prefix,tabList=self.nameList)
        else:
            k.resetLabel()
            k.clearState()
            finisher = self.getBufferNameFinisher
            self.getBufferNameFinisher = None
            finisher(k.arg)
    #@-others
#@+node:ekr.20070522085324: ** chapterCommandsClass
class chapterCommandsClass (baseEditCommandsClass):

    #@+others
    #@+node:ekr.20070522085340: *3*  ctor (chapterCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        # c.chapterController does not exist yet.
    #@+node:ekr.20070522085429: *3*  getPublicCommands (chapterCommandsClass)
    def getPublicCommands (self):

        c = self.c ; cc = c.chapterController

        if cc:
            return {
                'chapter-clone-node-to':    cc.cloneNodeToChapter,
                'chapter-convert-node-to':  cc.convertNodeToChapter,
                'chapter-copy-node-to':     cc.copyNodeToChapter,
                'chapter-create':           cc.createChapter,
                'chapter-create-from-node': cc.createChapterFromNode,
                'chapter-move-node-to':     cc.moveNodeToChapter,
                'chapter-remove':           cc.removeChapter,
                'chapter-rename':           cc.renameChapter,
                'chapter-select':           cc.selectChapter,
            }
        else:
            return {}
    #@-others
#@+node:ekr.20050920084036.150: ** controlCommandsClass
class controlCommandsClass (baseEditCommandsClass):

    #@+others
    #@+node:ekr.20050920084036.151: *3*  ctor (controlCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        self.payload = None
    #@+node:ekr.20050920084036.152: *3*  getPublicCommands
    def getPublicCommands (self):

        k = self.c.k

        return {

            # Miscellaneous.
            'advertised-undo':          self.advertizedUndo,
            'iconify-frame':            self.iconifyFrame, # Same as suspend.
            'keyboard-quit':            k and k.keyboardQuit,
            'save-buffers-kill-leo':    self.saveBuffersKillLeo,
            'set-silent-mode':          self.setSilentMode,
            'suspend':                  self.suspend,
            'act-on-node':              self.actOnNode,

            # Plugin info.
            'print-plugin-handlers':    self.printPluginHandlers,
            'print-plugins-info':       self.printPluginsInfo,

            # Shell commands.
            'shell-command':            self.shellCommand,
            'shell-command-on-region':  self.shellCommandOnRegion,
        }
    #@+node:ekr.20050922110030: *3* advertizedUndo
    def advertizedUndo (self,event):

        '''Undo the previous command.'''

        self.c.undoer.undo()
    #@+node:ekr.20050920084036.160: *3* executeSubprocess
    def executeSubprocess (self,event,command):

        '''Execute a command in a separate process.'''

        k = self.k

        try:
            args = shlex.split(command)
            subprocess.Popen(args).wait()
            k.setLabelGrey('Done: %s' % command)
        except Exception:
            junk, x, junk = sys.exc_info()
            k.setLabelRed('Exception: %s' % repr(x))
    #@+node:ekr.20070429090859: *3* print plugins info...
    def printPluginHandlers (self,event=None):

        '''Print the handlers for each plugin.'''

        g.app.pluginsController.printHandlers(self.c)

    def printPlugins (self,event=None):

        '''Print the file name responsible for loading a plugin.

        This is the first .leo file containing an @enabled-plugins node
        that enables the plugin.'''

        g.app.pluginsController.printPlugins(self.c)

    def printPluginsInfo (self,event=None):

        '''Print the file name responsible for loading a plugin.

        This is the first .leo file containing an @enabled-plugins node
        that enables the plugin.'''

        g.app.pluginsController.printPluginsInfo(self.c)
    #@+node:ekr.20060603161041: *3* setSilentMode
    def setSilentMode (self,event=None):

        '''Set the mode to be run silently, without the minibuffer.
        The only use for this command is to put the following in an @mode node::

            --> set-silent-mode'''

        self.c.k.silentMode = True
    #@+node:ekr.20050920084036.158: *3* shellCommand
    def shellCommand (self,event):

        '''Execute a shell command.'''

        k = self.k ; state = k.getState('shell-command')

        if state == 0:
            k.setLabelBlue('shell-command: ',protect=True)
            k.getArg(event,'shell-command',1,self.shellCommand)
        else:
            command = k.arg
            k.commandName = 'shell-command: %s' % command
            k.clearState()
            self.executeSubprocess(event,command)

    #@+node:ekr.20050930112126: *3* shellCommandOnRegion
    def shellCommandOnRegion (self,event):

        '''Execute a command taken from the selected text in a separate process.'''

        k = self.k
        w = self.editWidget(event)
        if not w: return

        if w.hasSelection():
            command = w.getSelectedText()
            k.commandName = 'shell-command: %s' % command
            self.executeSubprocess(event,command)
        else:
            k.clearState()
            k.setLabelRed('No text selected')
    #@+node:ville.20090222184600.2: *3* actOnNode
    def actOnNode(self, event):
        """ Execute node-specific action (typically defined by plugins)

        Actual behaviour is to be defined by plugins.

        Here's how to define actions for nodes in your plugins::

            import leo.core.leoPlugins
            def act_print_upcase(c,p,event):
                if not p.h.startswith('@up'):
                    raise leo.core.leoPlugins.TryNext
                p.h = p.h.upper()

            g.act_on_node.add(act_print_upcase)        

        This will upcase the headline when it starts with @up.            

        """
        g.act_on_node(self.c,self.c.p,event)
    #@+node:ekr.20050920084036.155: *3* shutdown, saveBuffersKillEmacs & setShutdownHook
    def shutdown (self,event):

        '''Quit Leo, prompting to save any unsaved files first.'''

        g.app.onQuit()

    saveBuffersKillLeo = shutdown
    #@+node:ekr.20050920084036.153: *3* suspend & iconifyFrame
    def suspend (self,event):

        '''Minimize the present Leo window.'''

        w = self.editWidget(event)
        if not w: return
        self.c.frame.top.iconify()

    # Must be a separate function so that k.inverseCommandsDict will be a true inverse.

    def iconifyFrame (self,event):

        '''Minimize the present Leo window.'''

        self.suspend(event)
    #@-others
#@+node:ekr.20060127162818.1: ** debugCommandsClass
class debugCommandsClass (baseEditCommandsClass):

    #@+others
    #@+node:ekr.20060127162921: *3*  ctor (debugCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.
    #@+node:ekr.20060127163325: *3*  getPublicCommands
    def getPublicCommands (self):

        return {

            # debugging.
            'debug':        self.debug,
            'pdb':          self.pdb,
            'print-focus':  self.printFocus,

            # Tracing of garbase collecor.
            'gc-collect-garbage':       self.collectGarbage,
            'gc-dump-all-objects':      self.dumpAllObjects,
            'gc-dump-new-objects':      self.dumpNewObjects,
            'gc-dump-objects-verbose':  self.verboseDumpObjects,
            'gc-print-summary':         self.printGcSummary,
            'gc-trace-disable':         self.disableGcTrace,
            'gc-trace-enable':          self.enableGcTrace,

            # Unit tests run externally: deprecated.
            'run-all-unit-tests-externally':        self.runAllUnitTestsExternally,
                # was 'run-all-unit-tests.
            'run-marked-unit-tests-externally':     self.runMarkedUnitTestsExternally,
                # 2011/10/31: new.
            'run-selected-unit-tests-externally':   self.runSelectedUnitTestsExternally,
                # was 'run-unit-tests.

            # Unit tests run locally.
            'run-all-unit-tests-locally':       self.runAllUnitTestsLocally,
            'run-marked-unit-tests-locally':    self.runMarkedUnitTestsLocally,
                # 2011/10/31: new.
            'run-selected-unit-tests-locally':  self.runSelectedUnitTestsLocally,
        }
    #@+node:ekr.20060205050659: *3* collectGarbage
    def collectGarbage (self,event=None):

        """Run Python's Gargabe Collector."""

        g.collectGarbage()
    #@+node:ekr.20060519003651: *3* debug & helper
    def debug (self,event=None):

        '''Start an external debugger in another process to debug a script.
        The script is the presently selected text or then entire tree's script.'''

        c = self.c ; p = c.p
        python = sys.executable
        script = g.getScript(c,p)
        winpdb = self.findDebugger()
        if not winpdb: return

        #check for doctest examples
        try:
            import doctest
            parser = doctest.DocTestParser()
            examples = parser.get_examples(script)

            # if this is doctest, extract the examples as a script
            if len(examples) > 0:
                script = doctest.script_from_examples(script)
        except ImportError:
            pass

        # special case; debug code may include g.es("info string").
        # insert code fragment to make this expression legal outside Leo.
        hide_ges = "class G:\n def es(s,c=None):\n  pass\ng = G()\n"
        script = hide_ges + script

        # Create a temp file from the presently selected node.
        filename = c.writeScriptFile(script)
        if not filename: return

        # Invoke the debugger, retaining the present environment.
        os.chdir(g.app.loadDir)
        if False and subprocess:
            cmdline = '%s %s -t %s' % (python,winpdb,filename)
            subprocess.Popen(cmdline)
        else:
            args = [sys.executable, winpdb, '-t', filename]
            os.spawnv(os.P_NOWAIT, python, args)
    #@+node:ekr.20060521140213: *4* findDebugger
    def findDebugger (self):

        '''Find the debugger using settings.'''

        c = self.c
        pythonDir = g.os_path_dirname(sys.executable)

        debuggers = (
            c.config.getString('debugger_path'),
            g.os_path_join(pythonDir,'Lib','site-packages','winpdb.py'), # winpdb 1.1.2 or newer
            g.os_path_join(pythonDir,'scripts','_winpdb.py'), # oder version.
        )

        for debugger in debuggers:
            if debugger:
                debugger = c.os_path_finalize(debugger)
                if g.os_path_exists(debugger):
                    return debugger
                else:
                    g.warning('debugger does not exist:',debugger)
        else:
            g.es('no debugger found.')
            return None
    #@+node:ekr.20060202160523: *3* dumpAll/New/VerboseObjects
    def dumpAllObjects (self,event=None):

        '''Print a summary of all existing Python objects.'''

        old = g.trace_gc
        g.trace_gc = True
        g.printGcAll()
        g.trace_gc = old

    def dumpNewObjects (self,event=None):

        '''Print a summary of all Python objects created
        since the last time Python's Garbage collector was run.'''

        old = g.trace_gc
        g.trace_gc = True
        g.printGcObjects()
        g.trace_gc = old

    def verboseDumpObjects (self,event=None):

        '''Print a more verbose listing of all existing Python objects.'''

        old = g.trace_gc
        g.trace_gc = True
        g.printGcVerbose()
        g.trace_gc = old
    #@+node:ekr.20060127163325.1: *3* enable/disableGcTrace
    def disableGcTrace (self,event=None):

        '''Enable tracing of Python's Garbage Collector.'''

        g.trace_gc = False


    def enableGcTrace (self,event=None):

        '''Disable tracing of Python's Garbage Collector.'''

        g.trace_gc = True
        g.enable_gc_debug()

        if g.trace_gc_verbose:
            g.blue('enabled verbose gc stats')
        else:
            g.blue('enabled brief gc stats')
    #@+node:ekr.20060202154734: *3* freeTreeWidgets
    def freeTreeWidgets (self,event=None):

        '''Free all widgets used in Leo's outline pane.'''

        c = self.c

        c.frame.tree.destroyWidgets()
        c.redraw()
    #@+node:ekr.20090226080753.8: *3* pdb
    def pdb (self,event=None):

        '''Fall into pdb.'''

        g.pdb()
    #@+node:ekr.20060210100432: *3* printFocus
    # Doesn't work if the focus isn't in a pane with bindings!

    def printFocus (self,event=None):

        '''Print information about the requested focus (for debugging).'''

        c = self.c

        g.es_print('      hasFocusWidget:',c.widget_name(c.hasFocusWidget))
        g.es_print('requestedFocusWidget:',c.widget_name(c.requestedFocusWidget))
        g.es_print('           get_focus:',c.widget_name(c.get_focus()))
    #@+node:ekr.20060205043324.3: *3* printGcSummary
    def printGcSummary (self,event=None):

        '''Print a brief summary of all Python objects.'''

        g.printGcSummary()
    #@+node:ekr.20060202133313: *3* printStats
    def printStats (self,event=None):

        '''Print statistics about the objects that Leo is using.'''

        c = self.c
        c.frame.tree.showStats()
        self.dumpAllObjects()
    #@+node:ekr.20060328121145: *3* runUnitTest commands
    def runAllUnitTestsLocally (self,event=None):
        '''Run all unit tests contained in the presently selected outline.
        Tests are run in the outline's process, so tests *can* change the outline.'''
        self.c.testManager.doTests(all=True)

    def runMarkedUnitTestsLocally (self,event=None):
        '''Run marked unit tests in the outline.
        Tests are run in the outline's process, so tests *can* change the outline.'''
        self.c.testManager.doTests(all=True,marked=True)

    def runSelectedUnitTestsLocally (self,event=None):
        '''Run all unit tests contained in the presently selected outline.
        Tests are run in the outline's process, so tests *can* change the outline.'''
        self.c.testManager.doTests(all=False,marked=False)

    # Externally run tests...

    def runAllUnitTestsExternally (self,event=None):
        '''Run all unit tests contained in the entire outline.
        Tests are run in an external process, so tests *cannot* change the outline.'''
        self.c.testManager.runTestsExternally(all=True,marked=False)

    def runMarkedUnitTestsExternally(self,event=None):
        '''Run all marked unit tests in the outline.
        Tests are run in an external process, so tests *cannot* change the outline.'''
        self.c.testManager.runTestsExternally(all=True,marked=True)

    def runSelectedUnitTestsExternally(self,event=None):
        '''Run all unit tests contained in the presently selected outline
        Tests are run in an external process, so tests *cannot* change the outline.'''
        self.c.testManager.runTestsExternally(all=False,marked=False)
    #@-others
#@+node:ekr.20050920084036.53: ** editCommandsClass
class editCommandsClass (baseEditCommandsClass):

    '''Contains editing commands with little or no state.'''

    #@+others
    #@+node:ekr.20050929155208: *3*  birth
    #@+node:ekr.20050920084036.54: *4*  ctor (editCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        self.ccolumn = '0'   # For comment column functions.
        self.extendMode = False # True: all cursor move commands extend the selection.
        self.fillPrefix = '' # For fill prefix functions.
        self.fillColumn = 0 # For line centering.
            # Set by the set-fill-column command.
            # If zero, @pagewidth value is used.
        self.moveSpotNode = None # A vnode.
        self.moveSpot = None # For retaining preferred column when moving up or down.
        self.moveCol = None # For retaining preferred column when moving up or down.
        self.sampleWidget = None # Created later.
        self.swapSpots = []
        self._useRegex = False # For replace-string
        self.w = None # For use by state handlers.

        # Settings...
        cf = c.config
        self.autocompleteBrackets   = cf.getBool('autocomplete-brackets')
        self.bracketsFlashBg        = cf.getColor('flash-brackets-background-color')
        self.bracketsFlashCount     = cf.getInt('flash-brackets-count')
        self.bracketsFlashDelay     = cf.getInt('flash-brackets-delay')
        self.bracketsFlashFg        = cf.getColor('flash-brackets-foreground-color')
        self.flashMatchingBrackets  = cf.getBool('flash-matching-brackets')
        self.smartAutoIndent        = cf.getBool('smart_auto_indent')
        self.openBracketsList       = cf.getString('open_flash_brackets')  or '([{'
        self.closeBracketsList      = cf.getString('close_flash_brackets') or ')]}'

        self.initBracketMatcher(c)
    #@+node:ekr.20050920084036.55: *4*  getPublicCommands (editCommandsClass)
    def getPublicCommands (self):        

        c = self.c

        return {
            'activate-cmds-menu':                   self.activateCmdsMenu,
            'activate-edit-menu':                   self.activateEditMenu,
            'activate-file-menu':                   self.activateFileMenu,
            'activate-help-menu':                   self.activateHelpMenu,
            'activate-outline-menu':                self.activateOutlineMenu,
            'activate-plugins-menu':                self.activatePluginsMenu,
            'activate-window-menu':                 self.activateWindowMenu,
            'add-editor':                           c.frame.body and c.frame.body.addEditor,
            'add-space-to-lines':                   self.addSpaceToLines,
            'add-tab-to-lines':                     self.addTabToLines, 
            'back-to-indentation':                  self.backToIndentation,
            'back-to-home':                         self.backToHome,
            'back-char':                            self.backCharacter,
            'back-char-extend-selection':           self.backCharacterExtendSelection,
            'back-page':                            self.backPage,
            'back-page-extend-selection':           self.backPageExtendSelection,
            'back-paragraph':                       self.backwardParagraph,
            'back-paragraph-extend-selection':      self.backwardParagraphExtendSelection,
            'back-sentence':                        self.backSentence,
            'back-sentence-extend-selection':       self.backSentenceExtendSelection,
            'back-word':                            self.backwardWord,
            'back-word-extend-selection':           self.backwardWordExtendSelection,
            'back-word-smart':                      self.backwardWordSmart,
            'back-word-smart-extend-selection':     self.backwardWordSmartExtendSelection,
            'backward-delete-char':                 self.backwardDeleteCharacter,
            'backward-delete-word':                 self.backwardDeleteWord,
            'backward-delete-word-smart':           self.backwardDeleteWordSmart,
            'backward-kill-paragraph':              self.backwardKillParagraph,
            'backward-find-character':              self.backwardFindCharacter,
            'backward-find-character-extend-selection': self.backwardFindCharacterExtendSelection,
            'beginning-of-buffer':                  self.beginningOfBuffer,
            'beginning-of-buffer-extend-selection': self.beginningOfBufferExtendSelection,
            'beginning-of-line':                    self.beginningOfLine,
            'beginning-of-line-extend-selection':   self.beginningOfLineExtendSelection,
            'c-to-python':                          self.cToPy,
            'capitalize-word':                      self.capitalizeWord,
            'center-line':                          self.centerLine,
            'center-region':                        self.centerRegion,
            'clean-all-lines':                      self.cleanAllLines,
            'clean-lines':                          self.cleanLines,
            'clear-all-caches':                     self.clearAllCaches,
            'clear-all-uas':                        self.clearAllUas,
            'clear-cache':                          self.clearCache,
            'clear-extend-mode':                    self.clearExtendMode,
            'clear-node-uas':                       self.clearNodeUas,
            'clear-selected-text':                  self.clearSelectedText,
            'click-click-box':                      self.clickClickBox,
            'click-headline':                       self.clickHeadline,
            'click-icon-box':                       self.clickIconBox,
            'clone-marked-nodes':                   c.cloneMarked,
            'cls':                                  g.cls,
            'contract-body-pane':                   c.frame.contractBodyPane,
            'contract-log-pane':                    c.frame.contractLogPane,
            'contract-outline-pane':                c.frame.contractOutlinePane,
            'contract-pane':                        c.frame.contractPane,
            'count-region':                         self.countRegion,
            'ctrl-click-icon':                      self.ctrlClickIconBox,
            'cycle-focus':                          self.cycleFocus,
            'cycle-all-focus':                      self.cycleAllFocus,
            'cycle-editor-focus':                   c.frame.body.cycleEditorFocus,
            'cycle-log-focus':                      c.frame.log.cycleTabFocus,
            # 'delete-all-icons':                   self.deleteAllIcons,
            'delete-char':                          self.deleteNextChar,
            'delete-editor':                        c.frame.body.deleteEditor,
            'delete-first-icon':                    self.deleteFirstIcon,
            'delete-indentation':                   self.deleteIndentation,
            'delete-last-icon':                     self.deleteLastIcon,
            'delete-marked-nodes':                  c.deleteMarked,
            'delete-node-icons':                    self.deleteNodeIcons,
            'delete-spaces':                        self.deleteSpaces,
            'delete-word':                          self.deleteWord,
            'delete-word-smart':                    self.deleteWordSmart,
            'do-nothing':                           self.doNothing,
            'downcase-region':                      self.downCaseRegion,
            'downcase-word':                        self.downCaseWord,
            'double-click-headline':                self.doubleClickHeadline,
            'double-click-icon-box':                self.doubleClickIconBox,
            'end-of-buffer':                        self.endOfBuffer,
            'end-of-buffer-extend-selection':       self.endOfBufferExtendSelection,
            'end-of-line':                          self.endOfLine,
            'end-of-line-extend-selection':         self.endOfLineExtendSelection,
            'escape':                               self.watchEscape,
            'eval-expression':                      self.evalExpression,
            'exchange-point-mark':                  self.exchangePointMark,
            'expand-body-pane':                     c.frame.expandBodyPane,
            'expand-log-pane':                      c.frame.expandLogPane,
            'expand-outline-pane':                  c.frame.expandOutlinePane,
            'expand-pane':                          c.frame.expandPane,
            'extend-to-line':                       self.extendToLine,
            'extend-to-paragraph':                  self.extendToParagraph,
            'extend-to-sentence':                   self.extendToSentence,
            'extend-to-word':                       self.extendToWord,
            'fill-paragraph':                       self.fillParagraph,
            'fill-region':                          self.fillRegion,
            'fill-region-as-paragraph':             self.fillRegionAsParagraph,
            'find-character':                       self.findCharacter,
            'find-character-extend-selection':      self.findCharacterExtendSelection,
            'find-word':                            self.findWord,
            'find-word-in-line':                    self.findWordInLine,
            'flush-lines':                          self.flushLines,
            'focus-to-body':                        self.focusToBody,
            'focus-to-log':                         self.focusToLog,
            'focus-to-minibuffer':                  self.focusToMinibuffer,
            'focus-to-tree':                        self.focusToTree,
            'forward-char':                         self.forwardCharacter,
            'forward-char-extend-selection':        self.forwardCharacterExtendSelection,
            'forward-page':                         self.forwardPage,
            'forward-page-extend-selection':        self.forwardPageExtendSelection,
            'forward-paragraph':                    self.forwardParagraph,
            'forward-paragraph-extend-selection':   self.forwardParagraphExtendSelection,
            'forward-sentence':                     self.forwardSentence,
            'forward-sentence-extend-selection':    self.forwardSentenceExtendSelection,
            'forward-end-word':                     self.forwardEndWord, # New in Leo 4.4.2.
            'forward-end-word-extend-selection':    self.forwardEndWordExtendSelection, # New in Leo 4.4.2.
            'forward-word':                         self.forwardWord,
            'forward-word-extend-selection':        self.forwardWordExtendSelection,
            'forward-word-smart':                   self.forwardWordSmart,
            'forward-word-smart-extend-selection':  self.forwardWordSmartExtendSelection,
            'fully-expand-body-pane':               c.frame.fullyExpandBodyPane,
            'fully-expand-log-pane':                c.frame.fullyExpandLogPane,
            'fully-expand-pane':                    c.frame.fullyExpandPane,
            'fully-expand-outline-pane':            c.frame.fullyExpandOutlinePane,
            'goto-char':                            self.gotoCharacter,
            'goto-global-line':                     self.gotoGlobalLine,
            'goto-line':                            self.gotoLine,
            'hide-body-pane':                       c.frame.hideBodyPane,
            'hide-log-pane':                        c.frame.hideLogPane,
            'hide-pane':                            c.frame.hidePane,
            'hide-outline-pane':                    c.frame.hideOutlinePane,
            'how-many':                             self.howMany,
            # Use indentBody in leoCommands.py
            'indent-relative':                      self.indentRelative,
            'indent-rigidly':                       self.tabIndentRegion,
            'indent-to-comment-column':             self.indentToCommentColumn,
            'insert-hard-tab':                      self.insertHardTab,
            'insert-icon':                          self.insertIcon,
            'insert-newline':                       self.insertNewline,
            'insert-parentheses':                   self.insertParentheses,
            'insert-soft-tab':                      self.insertSoftTab,
            'keep-lines':                           self.keepLines,
            'kill-paragraph':                       self.killParagraph,
            'line-number':                          self.lineNumber,
            'move-lines-down':                      self.moveLinesDown,
            'move-lines-up':                        self.moveLinesUp,
            'move-marked-nodes':                    c.moveMarked,
            'move-past-close':                      self.movePastClose,
            'move-past-close-extend-selection':     self.movePastCloseExtendSelection,
            'newline-and-indent':                   self.insertNewLineAndTab,
            'next-line':                            self.nextLine,
            'next-line-extend-selection':           self.nextLineExtendSelection,
            'previous-line':                        self.prevLine,
            'previous-line-extend-selection':       self.prevLineExtendSelection,
            'print-all-uas':                        self.printAllUas,
            'print-node-uas':                       self.printUas,
            'remove-blank-lines':                   self.removeBlankLines,
            'remove-space-from-lines':              self.removeSpaceFromLines,
            'remove-tab-from-lines':                self.removeTabFromLines,
            'replace-current-character':            self.replaceCurrentCharacter,
            'reverse-region':                       self.reverseRegion,
            'reverse-sort-lines':                   self.reverseSortLines,
            'reverse-sort-lines-ignoring-case':     self.reverseSortLinesIgnoringCase,
            'scroll-down-half-page':                self.scrollDownHalfPage,                
            'scroll-down-line':                     self.scrollDownLine,
            'scroll-down-page':                     self.scrollDownPage,
            'scroll-outline-down-line':             self.scrollOutlineDownLine,
            'scroll-outline-down-page':             self.scrollOutlineDownPage,
            'scroll-outline-left':                  self.scrollOutlineLeft,
            'scroll-outline-right':                 self.scrollOutlineRight,
            'scroll-outline-up-line':               self.scrollOutlineUpLine,
            'scroll-outline-up-page':               self.scrollOutlineUpPage,
            'scroll-up-half-page':                  self.scrollUpHalfPage,                        
            'scroll-up-line':                       self.scrollUpLine,
            'scroll-up-page':                       self.scrollUpPage,
            'select-all':                           self.selectAllText,
            'select-to-matching-bracket':           self.selectToMatchingBracket,
            # Exists, but can not be executed via the minibuffer.
            'self-insert-command':                  self.selfInsertCommand,
            'set-comment-column':                   self.setCommentColumn,
            'set-extend-mode':                      self.setExtendMode,
            'set-fill-column':                      self.setFillColumn,
            'set-fill-prefix':                      self.setFillPrefix,
            #'set-mark-command':                    self.setRegion,
            'set-ua':                               self.setUa,
            'show-colors':                          self.showColors,
            'show-fonts':                           self.showFonts,
            'simulate-begin-drag':                  self.simulateBeginDrag,
            'simulate-end-drag':                    self.simulateEndDrag,
            'sort-columns':                         self.sortColumns,
            'sort-fields':                          self.sortFields,
            'sort-lines':                           self.sortLines,
            'sort-lines-ignoring-case':             self.sortLinesIgnoringCase,
            'split-line':                           self.splitLine,
            'tabify':                               self.tabify,
            'toggle-extend-mode':                   self.toggleExtendMode,
            'toggle-case-region':                   self.toggleCaseRegion,
            'transpose-chars':                      self.transposeCharacters,
            'transpose-lines':                      self.transposeLines,
            'transpose-words':                      self.transposeWords,
            'typescript-to-py':                     self.tsToPy,
            'untabify':                             self.untabify,
            'upcase-region':                        self.upCaseRegion,
            'upcase-word':                          self.upCaseWord,
            'view-lossage':                         self.viewLossage,
            'what-line':                            self.whatLine,
        }
    #@+node:ekr.20061012113455: *4* doNothing
    def doNothing (self,event):

        '''A placeholder command, useful for testing bindings.'''

        pass
    #@+node:ekr.20110916215321.6709: *3* brackets (leoEditCommands)
    #@+node:ekr.20110916215321.6708: *4* selectToMatchingBracket (leoEditCommands)
    def selectToMatchingBracket (self,event):

        '''Select text that matches the bracket near the cursor.'''

        c = self.c
        w = self.editWidget(event)
        if not w: return
        i = w.getInsertPoint()
        s = w.getAllText()
        allBrackets = self.openBracketsList + self.closeBracketsList
        if i < len(s) and s[i] in allBrackets:
            ch = s[i]
        elif i > 0 and s[i-1] in allBrackets:
            i -= 1
            ch = s[i]
        else:
            g.es('no bracket selected')
            return

        d = {}
        if ch in self.openBracketsList:
            for z in range(len(self.openBracketsList)):
                d [self.openBracketsList[z]] = self.closeBracketsList[z]
            reverse = False # Search forward
        else:
            for z in range(len(self.openBracketsList)):
                d [self.closeBracketsList[z]] = self.openBracketsList[z]
            reverse = True # Search backward
        delim2 = d.get(ch)

        # This should be generalized...
        language = g.findLanguageDirectives(c,c.p)
        if language in ('c','cpp','csharp'):
            j = g.skip_matching_c_delims(s,i,ch,delim2,reverse=reverse)
        else:
            j = g.skip_matching_python_delims(s,i,ch,delim2,reverse=reverse)
        # g.trace(i,j,ch,delim2,reverse,language)
        if j not in (-1,i):
            if reverse:
                i += 1; j += 1
            w.setSelectionRange(i,j,insert=j)
                # 2011/11/21: Bug fix: was ins=j.
            w.see(j)
    #@+node:ekr.20121016093159.10182: *3* c/ts/toPY
    #@+<< theory of operation >>
    #@+node:ekr.20121016093159.10240: *4* << theory of operation >>
    #@@nocolor
    #@+at
    # 
    # 1. We use a single list, aList, for all changes to the text. This reduces
    #    stress on the gc. All replacesments are done **in place** in aList.
    # 
    # 2. The following pattern ensures replacements do not happen in strings and comments::
    # 
    #     def someScan(self,aList):
    #         i = 0
    #         while i < len(aList):
    #             if self.is_string_or_comment(aList,i):
    #                 i = skip_string_or_comment(aList,i)
    #             elif < found what we are looking for >:
    #                 <convert what we are looking for, setting i>
    #             else: i += 1
    # 
    #@-<< theory of operation >>
    #@+<< class To_Python >>
    #@+node:ekr.20121016093159.10183: *4* << class To_Python >>
    class To_Python:

        '''The base class for x-to-python commands.'''

        #@+others
        #@+node:ekr.20121016093159.10241: *5* ctor (To_Python)
        def __init__ (self,c):

            self.c = c
            self.p = self.c.p.copy()

            aList = g.get_directives_dict_list(self.p)
            self.tab_width = g.scanAtTabwidthDirectives(aList) or 4
        #@+node:ekr.20121016093159.10299: *5* go
        def go (self):

            import time
            t1 = time.time()
            c = self.c
            u = c.undoer ; undoType = 'typescript-to-python'
            pp = c.CPrettyPrinter(c)

            u.beforeChangeGroup(c.p,undoType)
            changed, dirtyVnodeList = False,[]
            n_files, n_nodes = 0,0
            special = ('class ','module ','@file ','@@file ')
            files = ('@file ','@@file ')
            for p in self.p.self_and_subtree():
                if p.b:
                    n_nodes += 1
                    if any([p.h.startswith(z) for z in special]):
                        g.es_print(p.h)
                        if any([p.h.startswith(z) for z in files]):
                            n_files += 1
                    bunch = u.beforeChangeNodeContents(p)

                    s = pp.indent(p,giveWarnings=False)
                    aList = list(s)
                    self.convertCodeList(aList)

                    s = ''.join(aList)
                    if s != p.b:
                        p.b = s
                        p.v.setDirty()
                        dirtyVnodeList.append(p.v)
                        u.afterChangeNodeContents(p,undoType,bunch)
                        changed = True

            # Call this only once, at end.
            if changed:
                u.afterChangeGroup(c.p,undoType,
                    reportFlag=False,dirtyVnodeList=dirtyVnodeList)

            t2 = time.time()
            g.es_print('done! %s files, %s nodes, %2.2f sec' % (n_files,n_nodes,t2-t1))
        #@+node:ekr.20121016093159.10245: *5* convertCodeList (must be defined in subclasses)
        def convertCodeList(self,aList):

            '''The main search/replace method.'''

            g.trace('must be defined in subclasses.')
        #@+node:ekr.20121016093159.10259: *5* Utils
        #@+node:ekr.20121016093159.10260: *6* match...
        #@+node:ekr.20121016093159.10261: *7* match
        def match (self,s,i,pat):

            '''Return True if s[i:] matches the pat string.

            We can't use g.match because s is usually a list.
            '''

            assert pat

            j = 0
            while i+j < len(s) and j < len(pat):
                if s[i+j] == pat[j]:
                    j += 1
                    if j == len(pat):
                        return True
                else:
                    return False

            return False
        #@+node:ekr.20121016093159.10293: *7* match_word
        def match_word (self,s,i,pat):

            '''Return True if s[i:] word matches the pat string.

            We can't use g.match_word because s is usually a list
            and g.match_word uses s.find.

            '''

            if self.match(s,i,pat):
                j = i + len(pat)
                if j >= len(s):
                    return True
                elif not pat[-1].isalnum():
                    # Bug fix 10/16/2012: The pattern terminates the word.
                    return True
                else:
                    ch = s[j]
                    return not ch.isalnum() and ch != '_'
            else:
                return False
        #@+node:ekr.20121016093159.10247: *6* insert_not
        # This may be defined in subclasses, but is not at present.

        def insert_not (self,aList):

            '''Change "!" to "not" except before "="'''

            i = 0
            while i < len(aList):
                if self.is_string_or_comment(aList,i):
                    i = self.skip_string_or_comment(aList,i)
                elif aList[i] == '!' and not self.match(aList,i+1,'='):
                    aList[i:i+1] = list('not ')
                    i += 4
                else:
                    i += 1
        #@+node:ekr.20121016093159.10263: *6* is...
        #@+node:ekr.20121126103128.10144: *7* is_section_def/ref
        def is_section_def (self,p):

            return self.is_section_ref(p.h)

        def is_section_ref (self,s):

            n1 = s.find("<<",0)
            n2 = s.find(">>",0)
            return -1 < n1 < n2 and s[n1+2:n2].strip()
        #@+node:ekr.20121016093159.10265: *7* is_string_or_comment
        def is_string_or_comment (self,s,i):

            # Does range checking.
            m = self.match
            return m(s,i,"'") or m(s,i,'"') or m(s,i,"//") or m(s,i,"/*")
        #@+node:ekr.20121016093159.10266: *7* is_ws and is_ws_or_nl
        def is_ws (self,ch):
            return ch in ' \t'

        def is_ws_or_nl (self,ch):
            return ch in ' \t\n'
        #@+node:ekr.20121016093159.10267: *6* prevNonWsChar and prevNonWsOrNlChar
        def prevNonWsChar (self,s,i):

            i -= 1
            while i >= 0 and self.is_ws(s[i]):
                i -= 1
            return i

        def prevNonWsOrNlChar (self,s,i):

            i -= 1
            while i >= 0 and self.is_ws_or_nl(s[i]):
                i -= 1
            return i
        #@+node:ekr.20121016093159.10268: *6* remove...
        #@+node:ekr.20121016093159.10269: *7* removeBlankLines
        def removeBlankLines (self,aList):

            i = 0
            while i < len(aList):
                j = i
                while j < len(aList) and aList[j] in " \t":
                    j += 1
                if j == len(aList) or aList[j] == '\n':
                    del aList[i:j+1]
                else:
                    i = self.skip_past_line(aList,i)
        #@+node:ekr.20121016093159.10270: *7* removeExcessWs
        def removeExcessWs (self,aList):

            i = 0
            i = self.removeExcessWsFromLine(aList,i)
            while i < len(aList):
                if self.is_string_or_comment(aList,i):
                    i = self.skip_string_or_comment(aList,i)
                elif self.match(aList,i,'\n'):
                    i += 1
                    i = self.removeExcessWsFromLine(aList,i)
                else: i += 1
        #@+node:ekr.20121016093159.10271: *7* removeExessWsFromLine
        def removeExcessWsFromLine (self,aList,i):

            assert(i==0 or aList[i-1] == '\n')
            i = self.skip_ws(aList,i)
                # Retain the leading whitespace.

            while i < len(aList):
                if self.is_string_or_comment(aList,i):
                    break # safe
                elif self.match(aList,i,'\n'):
                    break
                elif self.match(aList,i,' ') or self.match(aList,i,'\t'):
                    # Replace all whitespace by one blank.
                    j = self.skip_ws(aList,i)
                    assert(j > i)
                    aList[i:j] = [' ']
                    i += 1 # make sure we don't go past a newline!
                else: i += 1
            return i
        #@+node:ekr.20121016093159.10272: *7* removeMatchingBrackets
        def removeMatchingBrackets (self,aList, i):

            j = self.skip_to_matching_bracket(aList, i)
            if j > i and j < len(aList):
                # print "del brackets:", ''.join(aList[i:j+1])
                c = aList[j]
                if c == ')' or c == ']' or c == '}':
                    del aList[j:j+1]
                    del aList[i:i+1]
                    # print "returning:", ''.join(aList[i:j])
                    return j - 1
                else: return j + 1
            else: return j
        #@+node:ekr.20121016093159.10273: *7* removeSemicolonsAtEndOfLines
        def removeSemicolonsAtEndOfLines (self,aList):

            i = 0
            while i < len(aList):
                if self.is_string_or_comment(aList,i):
                    i = self.skip_string_or_comment(aList,i)
                elif aList[i] == ';':
                    j = self.skip_ws(aList,i+1)
                    if (
                        j >= len(aList) or
                        self.match(aList,j,'\n') or
                        self.match(aList,j,'#') or
                        self.match(aList,j,"//")
                    ):
                        del aList[i]
                    else: i += 1
                else: i += 1
        #@+node:ekr.20121016093159.10274: *7* removeTrailingWs
        def removeTrailingWs (self,aList):

            i = 0
            while i < len(aList):
                if self.is_ws(aList[i]):
                    j = i
                    i = self.skip_ws(aList,i)
                    assert(j < i)
                    if i >= len(aList) or aList[i] == '\n':
                        # print "removing trailing ws:", `i-j`
                        del aList[j:i]
                        i = j
                else: i += 1
        #@+node:ekr.20121016093159.10275: *6* replace... & safe_replace
        #@+node:ekr.20121016093159.10276: *7* replace
        def replace (self,aList,findString,changeString):

            '''# Replaces all occurances of findString by changeString.
            changeString may be the empty string, but not None.
            '''

            if not findString: return

            changeList = list(changeString)
            i = 0
            while i < len(aList):
                if self.match(aList,i,findString):
                    aList[i:i+len(findString)] = changeList
                    i += len(changeList)
                else:
                    i += 1
        #@+node:ekr.20121016093159.10277: *7* replaceComments
        def replaceComments (self,aList):

            i = 0
            while i < len(aList):
                # Loop invariant: j > progress at end.
                progress = i
                if self.match(aList,i,"//"):
                    aList[i:i+2] = ['#']
                    j = self.skip_past_line(aList,i)
                elif self.match(aList,i,"/*"):
                    j = self.skip_c_block_comment(aList,i)
                    k = i
                    while k-1 >= 0 and aList[k-1] in ' \t':
                        k -= 1
                    assert k == 0 or aList[k-1] not in ' \t'
                    lws = ''.join(aList[k:i])
                    comment_body = ''.join(aList[i+2:j-2])
                    comment_lines = g.splitLines(lws + comment_body)
                    comment_lines = self.munge_block_comment(comment_lines)
                    comment = '\n'.join(comment_lines) # A list of lines.
                    comment_list = list(comment) # A list of characters.
                    aList[k:j] = comment_list
                    j = k + len(comment_list)
                    progress = j - 1 # Disable the check below.
                elif self.match(aList,i,'"') or self.match(aList,i,"'"):
                    j = self.skip_string(aList,i)
                else:
                    j = i+1

                # Defensive programming.
                if j == progress:
                    j += 1
                assert j > progress
                i = j
        #@+node:ekr.20121016093159.10278: *8* munge_block_comment
        def munge_block_comment (self,comment_lines):

            trace = False
            n = len(comment_lines)
            assert n > 0

            s = comment_lines[0]
            junk,w = g.skip_leading_ws_with_indent(s,0,tab_width=4)

            if n == 1:
                return ['%s# %s' % ((' ' * (w-1)),s.strip())]

            junk,w = g.skip_leading_ws_with_indent(s,0,tab_width=4)
            i,result = 0,[]
            for i in range(len(comment_lines)):
                s = comment_lines[i]
                if s.strip():
                    result.append('%s# %s' % ((' ' * w),s.strip()))
                elif i == n-1:
                    pass # Omit the line entirely.
                else:
                    result.append('') # Add a blank line

            if trace:
                g.trace()
                for z in result: print(repr(z))

            return result
        #@+node:ekr.20121016093159.10279: *7* replaceSectionDefs
        def replaceSectionDefs (self,aList):

            '''Replaces < < x > > = by @c (at the start of lines).'''

            if not aList: return
            i = 0
            j = self.is_section_def(aList[i])
            if j > 0: aList[i:j] = list("@c ")

            while i < len(aList):
                if self.is_string_or_comment(aList,i):
                    i = self.skip_string_or_comment(aList,i)
                elif self.match(aList,i,"\n"):
                    i += 1
                    j = self.is_section_def(aList[i])
                    if j > i: aList[i:j] = list("@c ")
                else: i += 1
        #@+node:ekr.20121016093159.10280: *7* safe_replace
        def safe_replace (self,aList,findString,changeString):

            '''Replaces occurances of findString by changeString,
            but only outside of C comments and strings.
            changeString may be the empty string, but not None.
            '''

            if not findString: return

            changeList = list(changeString)
            i = 0
            if findString[0].isalpha(): # use self.match_word
                while i < len(aList):
                    if self.is_string_or_comment(aList,i):
                        i = self.skip_string_or_comment(aList,i)
                    elif self.match_word(aList,i,findString):
                        aList[i:i+len(findString)] = changeList
                        i += len(changeList)
                    else:
                        i += 1
            else: #use self.match
                while i < len(aList):
                    if self.match(aList,i,findString):
                        aList[i:i+len(findString)] = changeList
                        i += len(changeList)
                    else:
                        i += 1
        #@+node:ekr.20121016093159.10281: *6* skip
        #@+node:ekr.20121016093159.10282: *7* skip_c_block_comment
        def skip_c_block_comment (self,s,i):

            # if 'replaceComments' in g.callers():
                # g.trace(repr(''.join(s[i:i+20])))

            assert(self.match(s,i,"/*"))
            i += 2

            while i < len(s):
                if self.match(s,i,"*/"):
                    return i + 2
                else:
                    i += 1

            return i
        #@+node:ekr.20121016093159.10298: *7* skip_line
        def skip_line (self,s,i):

            while i < len(s) and s[i] != '\n':
                i += 1
            return i
        #@+node:ekr.20121016093159.10283: *7* skip_past_line
        def skip_past_line (self,s,i):

            while i < len(s) and s[i] != '\n':
                i += 1
            if i < len(s) and s[i] == '\n':
                i += 1
            return i
        #@+node:ekr.20121016093159.10284: *7* skip_past_word
        def skip_past_word (self,s,i):

            assert(s[i].isalpha() or s[i]=='~')

            # Kludge: this helps recognize dtors.
            if s[i]=='~':
                i += 1

            while i < len(s):
                ch = s[i]
                if ch.isalnum() or ch =='_':
                    i += 1
                else:
                    break
            return i
        #@+node:ekr.20121016093159.10285: *7* skip_string
        def skip_string (self,s,i):

            delim = s[i] # handle either single or double-quoted strings
            assert(delim == '"' or delim == "'")
            i += 1

            while i < len(s):
                if s[i] == delim:
                    return i + 1
                elif s[i] == '\\':
                    i += 2
                else:
                    i += 1
            return i
        #@+node:ekr.20121016093159.10286: *7* skip_string_or_comment
        def skip_string_or_comment (self,s,i):

            if self.match(s,i,"'") or self.match(s,i,'"'):
                j = self.skip_string(s,i)
            elif self.match(s,i,"//"):
                j = self.skip_past_line(s,i)
            elif self.match(s,i,"/*"):
                j = self.skip_c_block_comment(s,i)
            else: assert(0)

            # g.trace(repr(''.join(s[i:j])))
            return j
        #@+node:ekr.20121016093159.10287: *7* skip_to_matching_bracket
        def skip_to_matching_bracket (self,s,i):

            ch = s[i]
            if   ch == '(': delim = ')'
            elif ch == '{': delim = '}'
            elif ch == '[': delim = ']'
            else: assert(0)

            i += 1
            while i < len(s):
                ch = s[i]
                if self.is_string_or_comment(s,i):
                    i = self.skip_string_or_comment(s,i)
                elif ch == delim:
                    return i
                elif ch == '(' or ch == '[' or ch == '{':
                    i = self.skip_to_matching_bracket(s,i)
                    i += 1 # skip the closing bracket.
                else: i += 1
            return i
        #@+node:ekr.20121016093159.10288: *7* skip_ws and skip_ws_and_nl
        def skip_ws (self,aList,i):

            while i < len(aList):
                c = aList[i]
                if c == ' ' or c == '\t':
                    i += 1
                else: break
            return i

        def skip_ws_and_nl (self,aList,i):

            while i < len(aList):
                c = aList[i]
                if c == ' ' or c == '\t' or c == '\n':
                    i += 1
                else: break
            return i
        #@-others
    #@-<< class To_Python >>
    #@+<< class C_To_Python (To_Python) >>
    #@+node:ekr.20121016093159.10184: *4* << class C_To_Python (To_Python) >>
    class C_To_Python (To_Python):

        #@+others
        #@+node:ekr.20110916215321.8057: *5* ctor & helpers (C_to_Python)
        def __init__ (self,c):

            c.editCommands.To_Python.__init__(self,c)
                # init the base class

            # Internal state...
            self.class_name = ''
                # The class name for the present function.  Used to modify ivars.

            self.ivars = []
                # List of ivars to be converted to self.ivar


            self.get_user_types()
        #@+node:ekr.20110916215321.7984: *6* get_user_types
        #@@nocolor
        #@+at
        # 
        # Change the following lists so they contain the types and classes used by your
        # program. c-to-python converts::
        # 
        #     new aType(...)
        # 
        # to::
        # 
        #     aType(...)
        # 
        # Change ivarsDict so it represents the instance variables (ivars) used by your
        # program's classes. ivarsDict is a dictionary used to translate ivar i of class c
        # to self.i. It also translates this->i to self.i.
        # 
        #@@c
        #@@color

        def get_user_types (self):

            c = self.c

            self.class_list = c.config.getData('c-to-python-class-list') or []

            self.type_list  = (
                c.config.getData('c-to-python-type-list') or
                ["char", "void", "short", "long", "int", "double", "float"]
            )
            aList = c.config.getData('c-to-python-ivars-dict')
            if aList:
                self.ivars_dict = self.parse_ivars_data(aList)
            else:
                self.ivars_dict = {}

            if 0:
                #g.trace('class_list',self.class_list)
                #g.trace('type_list',self.type_list)
                g.trace('ivars_dict...')
                d = self.ivars_dict
                keys = list(d.keys())
                for key in sorted(keys):
                    print('%s:' % (key))
                    for val in d.get(key):
                        print('  %s' % (val))

        #@+node:ekr.20110917104720.6877: *6* parse_ivars_data
        def parse_ivars_data (self,aList):

            d,key = {},None
            aList = [z.strip() for z in aList if z.strip()]
            for s in aList:
                if s.endswith(':'):
                    key = s[:-1].strip()
                elif key:
                    ivars = [z.strip() for z in s.split(',') if z.strip()]
                    aList = d.get(key,[])
                    aList.extend(ivars)
                    d [key] = aList
                else:
                    g.error('invalid @data c-to-python-ivars-dict',repr(s))
                    return {}

            return d
        #@+node:ekr.20110916215321.7997: *5* convertCodeList (C_To_Python) & helpers
        def convertCodeList(self,aList):

            r,sr = self.replace,self.safe_replace

            # First...
            r(aList, "\r", '')
            # self.convertLeadingBlanks(aList) # Now done by indent.
            # if leoFlag: replaceSectionDefs(aList)
            self.mungeAllFunctions(aList)

            # Next...
            if 1:
                # CC2 stuff:
                sr(aList, "TRACEPB",   "if trace: g.trace")
                sr(aList, "TRACEPN",   "if trace: g.trace")
                sr(aList, "TRACEPX",   "if trace: g.trace")
                sr(aList, "TICKB",     "if trace: g.trace")
                sr(aList, "TICKN",     "if trace: g.trace")
                sr(aList, "TICKX",     "if trace: g.trace")
                sr(aList, "g.trace(ftag,", "g.trace(")
                sr(aList, "ASSERT_TRACE", "assert")

            sr(aList, "ASSERT","assert")
            sr(aList, " -> ", '.')
            sr(aList, "->", '.')
            sr(aList, " . ", '.')
            sr(aList, "this.self", "self")
            sr(aList, "{", '')
            sr(aList, "}", '')
            sr(aList, "#if", "if")
            sr(aList, "#else", "else")
            sr(aList, "#endif", '')
            sr(aList, "else if", "elif")
            sr(aList, "else", "else:")
            sr(aList, "&&", " and ")
            sr(aList, "||", " or ")
            sr(aList, "TRUE", "True")
            sr(aList, "FALSE", "False")
            sr(aList, "NULL", "None")
            sr(aList, "this", "self")
            sr(aList, "try", "try:")
            sr(aList, "catch", "except:")
            # if leoFlag: sr(aList, "@code", "@c")

            # Next...
            self.handle_all_keywords(aList)
            self.insert_not(aList)
            self.removeSemicolonsAtEndOfLines(aList)
                # after processing for keywords

            # Last...
            # if firstPart and leoFlag: removeLeadingAtCode(aList)
            self.removeBlankLines(aList)
            self.removeExcessWs(aList)
            # your taste may vary: in Python I don't like extra whitespace
            sr(aList, " :", ":") 
            sr(aList, ", ", ",")
            sr(aList, " ,", ",")
            sr(aList, " (", "(")
            sr(aList, "( ", "(")
            sr(aList, " )", ")")
            sr(aList, ") ", ")")
            sr(aList, "@language c","@language python")
            self.replaceComments(aList) # should follow all calls to safe_replace
            self.removeTrailingWs(aList)
            r(aList, "\t ", "\t") # happens when deleting declarations.
        #@+node:ekr.20110916215321.8011: *6* handle_all_keywords
        def handle_all_keywords (self,aList):

            '''
            converts if ( x ) to if x:
            converts while ( x ) to while x:
            '''

            i = 0
            while i < len(aList):
                if self.is_string_or_comment(aList,i):
                    i = self.skip_string_or_comment(aList,i)
                elif (
                    self.match_word(aList,i,"if") or
                    self.match_word(aList,i,"while") or
                    self.match_word(aList,i,"for") or
                    self.match_word(aList,i,"elif")
                ):
                    i = self.handle_keyword(aList,i)
                else:
                    i += 1
            # print "handAllKeywords2:", ''.join(aList)
        #@+node:ekr.20110916215321.8012: *7* handle_keyword
        def handle_keyword (self,aList,i):

            if self.match_word(aList,i,"if"):
                i += 2
            elif self.match_word(aList,i,"elif"):
                i += 4
            elif self.match_word(aList,i,"while"):
                i += 5
            elif self.match_word(aList,i,"for"):
                i += 3
            else: assert(0)

            # Make sure one space follows the keyword.
            k = i
            i = self.skip_ws(aList,i)
            if k == i:
                c = aList[i]
                aList[i:i+1] = [ ' ', c ]
                i += 1

            # Remove '(' and matching ')' and add a ':'
            if aList[i] == "(":
                # Look ahead.  Don't remove if we span a line.
                j = self.skip_to_matching_bracket(aList, i)
                k = i
                found = False
                while k < j and not found:
                    found = aList[k] == '\n'
                    k += 1
                if not found:
                    j = self.removeMatchingBrackets(aList,i)
                if j > i and j < len(aList):
                    ch = aList[j]
                    aList[j:j+1] = [ch,":", " "]
                    j = j + 2
                return j
            return i
        #@+node:ekr.20110916215321.8003: *6* mungeAllFunctions
        def mungeAllFunctions(self,aList):

            '''Scan for a '{' at the top level that is preceeded by ')' '''

            prevSemi = 0 # Previous semicolon: header contains all previous text
            i = 0
            firstOpen = None
            while i < len(aList):
                progress = i
                if self.is_string_or_comment(aList,i):
                    j = self.skip_string_or_comment(aList,i)
                    prevSemi = j
                elif self.match(aList,i,'('):
                    if not firstOpen:
                        firstOpen = i
                    j = i + 1
                elif self.match(aList,i,'#'):
                    # At this point, it is a preprocessor directive.
                    j = self.skip_past_line(aList, i)
                    prevSemi = j
                elif self.match(aList,i,';'):
                    j = i + 1
                    prevSemi = j
                elif self.match(aList,i,"{"):
                    j = self.handlePossibleFunctionHeader(aList,i,prevSemi,firstOpen)
                    prevSemi = j
                    firstOpen = None # restart the scan
                    # g.trace(repr(''.join(aList[prevSemi:prevSemi+20])))
                else:
                    j = i + 1

                # Handle unusual cases.
                if j <= progress:
                    j = progress + 1
                assert j > progress

                i = j
        #@+node:ekr.20110916215321.8004: *7* handlePossibleFunctionHeader
        # converts function header lines from c++ format to python format.
        # That is, converts
        # x1..nn w::y ( t1 z1,..tn zn) {
        # to
        # def y (z1,..zn): {

        def handlePossibleFunctionHeader (self,aList,i,prevSemi,firstOpen):

            trace = False
            assert(self.match(aList,i,"{"))

            prevSemi = self.skip_ws_and_nl(aList, prevSemi)
            close = self.prevNonWsOrNlChar(aList,i)

            if close < 0 or aList[close] != ')':
                # Should not increase *Python* indent.
                return 1 + self.skip_to_matching_bracket(aList,i)

            if not firstOpen:
                return 1 + self.skip_to_matching_bracket(aList,i)

            close2 = self.skip_to_matching_bracket(aList, firstOpen)
            if close2 != close:
                return 1 + self.skip_to_matching_bracket(aList,i)

            open_paren = firstOpen
            assert(aList[open_paren]=='(')
            head = aList[prevSemi:open_paren]

            # do nothing if the head starts with "if", "for" or "while"
            k = self.skip_ws(head,0)
            if k >= len(head) or not head[k].isalpha():
                return 1 + self.skip_to_matching_bracket(aList,i)

            kk = self.skip_past_word(head,k)
            if kk > k:
                headString = ''.join(head[k:kk])
                # C keywords that might be followed by '{'
                # print "headString:", headString
                if headString in [ "class", "do", "for", "if", "struct", "switch", "while"]:
                    return 1 + self.skip_to_matching_bracket(aList, i)

            args = aList[open_paren:close+1]
            k = 1 + self.skip_to_matching_bracket(aList,i)
            body = aList[close+1:k]

            if True and trace:
                g.trace('\nhead: %s\nargs: %s\nbody: %s' % (
                    ''.join(head),''.join(args),''.join(body)))

            head = self.massageFunctionHead(head)
            args = self.massageFunctionArgs(args)
            body = self.massageFunctionBody(body)

            if False and trace:
                g.trace('\nhead2: %s\nargs2: %s\nbody2: %s' % (
                    ''.join(head),''.join(args),''.join(body)))

            result = []
            if head: result.extend(head)
            if args: result.extend(args)
            if body: result.extend(body)

            aList[prevSemi:k] = result
            return prevSemi + len(result)
        #@+node:ekr.20110916215321.8005: *7* massageFunctionArgs
        def massageFunctionArgs (self,args):

            assert(args[0]=='(')
            assert(args[-1]==')')

            result = ['('] ; lastWord = []
            if self.class_name:
                for item in list("self,"): result.append(item) #can put extra comma

            i = 1
            while i < len(args):
                i = self.skip_ws_and_nl(args, i)
                c = args[i]
                if c.isalpha():
                    j = self.skip_past_word(args,i)
                    lastWord = args[i:j]
                    i = j
                elif c == ',' or c == ')':
                    for item in lastWord:
                        result.append(item)
                    if lastWord != [] and c == ',':
                        result.append(',')
                    lastWord = []
                    i += 1
                else: i += 1
            if result[-1] == ',':
                del result[-1]
            result.append(')')
            result.append(':')
            # print "new args:", ''.join(result)
            return result
        #@+node:ekr.20110916215321.8006: *7* massageFunctionHead (sets .class_name)
        def massageFunctionHead (self,head):

            result = []
            prevWord = []
            self.class_name = ''
            i = 0
            # g.trace(repr(''.join(head)))
            while i < len(head):
                i = self.skip_ws_and_nl(head,i)
                if i < len(head) and head[i].isalpha():
                    result = []
                    j = self.skip_past_word(head,i)
                    prevWord = head[i:j]
                    i = j
                    # look for ::word2
                    i = self.skip_ws(head,i)
                    if self.match(head,i,"::"):
                        # Set the global to the class name.
                        self.class_name = ''.join(prevWord)
                        # print(class name:", self.class_name)
                        i = self.skip_ws(head,i+2)
                        if i < len(head) and (head[i]=='~' or head[i].isalpha()):
                            j = self.skip_past_word(head,i)
                            if head[i:j] == prevWord:
                                result.extend('__init__')
                            elif head[i]=='~' and head[i+1:j] == prevWord:
                                result.extend('__del__')
                            else:
                                # result.extend(list('::'))
                                result.extend(head[i:j])
                            i = j
                    else:
                        result.extend(prevWord)
                else: i += 1

            finalResult = list("def ")
            finalResult.extend(result)
            return finalResult
        #@+node:ekr.20110916215321.8007: *7* massageFunctionBody & helpers
        def massageFunctionBody (self,body):

            body = self.massageIvars(body)
            body = self.removeCasts(body)
            body = self.removeTypeNames(body)
            body = self.dedentBlocks(body)
            return body
        #@+node:ekr.20110919224143.6928: *8* dedentBlocks
        def dedentBlocks (self,body):

            '''Look for '{' preceded by '{' or '}' or ';'
            (with intervening whitespace and comments).
            '''

            i = 0
            while i < len(body):
                j = i
                ch = body[i]
                if self.is_string_or_comment(body,i):
                    j = self.skip_string_or_comment(body,i)
                elif ch in '{};':
                    # Look ahead ofr '{'
                    j += 1
                    while True:
                        k = j
                        j = self.skip_ws_and_nl(body,j)
                        if self.is_string_or_comment(body,j):
                            j = self.skip_string_or_comment(body,j)
                        if k == j: break
                        assert k < j
                    if self.match(body,j,'{'):
                        k = j
                        j = self.skip_to_matching_bracket(body,j)
                        # g.trace('found block\n',''.join(body[k:j+1]))
                        m = '# <Start dedented block>...'
                        body[k:k+1] = list(m)
                        j += len(m)
                        while k < j:
                            progress = k
                            if body[k] == '\n':
                                k += 1
                                spaces = 0
                                while spaces < 4 and k < j:
                                    if body[k] == ' ':
                                        spaces += 1
                                        k += 1
                                    else:
                                        break
                                if spaces > 0:
                                    del body[k-spaces:k]
                                    k -= spaces
                                    j -= spaces
                            else:
                                k += 1
                            assert progress < k
                        m = '    # <End dedented block>'
                        body[j:j+1] = list(m)
                        j += len(m)
                else:
                    j = i + 1

                # Defensive programming.
                if i == j:
                    j += 1
                assert i < j
                i = j

            return body
        #@+node:ekr.20110916215321.8008: *8* massageIvars
        def massageIvars (self,body):

            ivars = self.ivars_dict.get(self.class_name,[])
            i = 0
            while i < len(body):
                if self.is_string_or_comment(body,i):
                    i = self.skip_string_or_comment(body,i)
                elif body[i].isalpha():
                    j = self.skip_past_word(body,i)
                    word = ''.join(body[i:j])
                    # print "looking up:", word
                    if word in ivars:
                        # replace word by self.word
                        # print "replacing", word, " by self.", word
                        word = "self." + word
                        word = list(word)
                        body[i:j] = word
                        delta = len(word)-(j-i)
                        i = j + delta
                    else: i = j
                else: i += 1
            return body
        #@+node:ekr.20110916215321.8009: *8* removeCasts
        def removeCasts (self,body):

            i = 0
            while i < len(body):
                if self.is_string_or_comment(body,i):
                    i = self.skip_string_or_comment(body,i)
                elif self.match(body, i, '('):
                    start = i
                    i = self.skip_ws(body, i+1)
                    if body[i].isalpha():
                        j = self.skip_past_word(body,i)
                        word = ''.join(body[i:j])
                        i = j
                        if word in self.class_list or word in self.type_list:
                            i = self.skip_ws(body, i)
                            while self.match(body,i,'*'):
                                i += 1
                            i = self.skip_ws(body, i)
                            if self.match(body,i,')'):
                                i += 1
                                # print "removing cast:", ''.join(body[start:i])
                                del body[start:i]
                                i = start
                else: i += 1
            return body
        #@+node:ekr.20110916215321.8010: *8* removeTypeNames
        # Do _not_ remove type names when preceeded by new.

        def removeTypeNames (self,body):

            i = 0
            while i < len(body):
                if self.is_string_or_comment(body,i):
                    i = self.skip_string_or_comment(body,i)
                elif self.match_word(body, i, "new"):
                    i = self.skip_past_word(body,i)
                    i = self.skip_ws(body,i)
                    # don't remove what follows new.
                    if body[i].isalpha():
                        i = self.skip_past_word(body,i)
                elif body[i].isalpha():
                    j = self.skip_past_word(body,i)
                    word = ''.join(body[i:j])
                    if word in self.class_list or word in self.type_list:
                        j = self.skip_ws(body,j)
                        while self.match(body,j,'*'):
                            j += 1
                        # print "Deleting type name:", ''.join(body[i:j])
                        j = self.skip_ws(body,j)
                        del body[i:j]
                    else:
                        i = j
                else: i += 1
            return body
        #@-others
    #@-<< class C_To_Python (To_Python) >>
    #@+<< class TS_To_Python (To_Python) >>
    #@+node:ekr.20121016093159.10185: *4* << class TS_To_Python (To_Python) >>
    class TS_To_Python (To_Python):

        #@+others
        #@+node:ekr.20121016093159.10297: *5* ctor (TS_To_Python)
        def __init__ (self,c):

            c.editCommands.To_Python.__init__(self,c)
                # init the base class

            self.class_name = ''
                # The class name for the present function.  Used to modify ivars.
        #@+node:ekr.20121015183335.10145: *5* convertCodeList (TS_To_Python) & helpers
        def convertCodeList(self,aList):

            r,sr = self.replace,self.safe_replace

            # First...
            r(aList, '\r', '')
            self.mungeAllFunctions(aList)
            self.mungeAllClasses(aList)

            # Second...
            sr(aList, ' -> ', '.')
            sr(aList, '->', '.')
            sr(aList, ' . ', '.')
            # sr(aList, 'this.self', 'self')
            sr(aList, '{', '')
            sr(aList, '}', '')
            sr(aList, 'else if', 'elif')
            sr(aList, 'else', 'else:')
            sr(aList, '&&', ' and ')
            sr(aList, '||', ' or ')
            sr(aList, 'true', 'True')
            sr(aList, 'false', 'False')
            sr(aList, 'null', 'None')
            sr(aList, 'this', 'self')
            sr(aList, 'try', 'try:')
            sr(aList, 'catch', 'except:')
            sr(aList, 'constructor', '__init__')
            sr(aList, 'new ','')
            # sr(aList, 'var ','')
                # var usually indicates something weird, or an uninited var,
                # so it may be good to retain as a marker.

            # Third...
            self.handle_all_keywords(aList)
            self.insert_not(aList)
            self.removeSemicolonsAtEndOfLines(aList)
                # after processing for keywords
            self.comment_scope_ids(aList)

            # Last...
            self.removeBlankLines(aList)
            self.removeExcessWs(aList)
            # I usually don't like extra whitespace. YMMV.
            sr(aList, '  and ', ' and ')
            sr(aList, '  not ', ' not ')
            sr(aList, '  or ',  ' or ')
            sr(aList, ' and  ', ' and ')
            sr(aList, ' not  ', ' not ')
            sr(aList, ' or  ',  ' or ')
            sr(aList, ' :', ':') 
            sr(aList, ', ', ',')
            sr(aList, ' ,', ',')
            sr(aList, ' (', '(')
            sr(aList, '( ', '(')
            sr(aList, ' )', ')')
            sr(aList, ') ', ')')
            sr(aList, ' and(', ' and (')
            sr(aList, ' not(', ' not (')
            sr(aList, ' or(',  ' or (')
            sr(aList, ')and ', ') and ')
            sr(aList, ')not ', ') not ')
            sr(aList, ')or ',  ') or ')
            sr(aList, ')and(', ') and (')
            sr(aList, ')not(', ') not (')
            sr(aList, ')or(',  ') or (')
            sr(aList, '@language javascript','@language python')
            self.replaceComments(aList) # should follow all calls to safe_replace
            self.removeTrailingWs(aList)
            r(aList, '\t ', '\t') # happens when deleting declarations.
        #@+node:ekr.20121015183335.10191: *6* comment_scope_ids
        def comment_scope_ids (self,aList):

            '''convert (public|private|export) aLine to aLine # (public|private|export)'''

            scope_ids = ('public','private','export',)
            i = 0
            if any([self.match_word(aList,i,z) for z in scope_ids]):
                i = self.handle_scope_keyword(aList,i)
            while i < len(aList):
                progress = i
                if self.is_string_or_comment(aList,i):
                    i = self.skip_string_or_comment(aList,i)
                elif aList[i] == '\n':
                    i += 1
                    i = self.skip_ws(aList,i)
                    if any([self.match_word(aList,i,z) for z in scope_ids]):
                        i = self.handle_scope_keyword(aList,i)
                else:
                    i += 1
                assert i > progress
            # print "handAllKeywords2:", ''.join(aList)
        #@+node:ekr.20121015183335.10193: *7* handle_scope_keyword
        def handle_scope_keyword (self,aList,i):

            i1 = i
            for word in ('public','private','export'):
                if self.match_word(aList,i,word):
                    i += len(word)
                    break
            else:
                assert False,'not a scope id: %s' % word

            # Skip any following spaces.
            i2 = self.skip_ws(aList,i)

            # Scan to the next newline:
            i3 = self.skip_line(aList,i)

            # Optional: move the word to a trailing comment.
            comment = list(' # %s' % word) if False else []

            # Change the list in place.
            aList[i1:i3] = aList[i2:i3] + comment
            i = i1 + (i3-i2) + len(comment)
            # g.trace(''.join(aList[i1:i]))
            return i
        #@+node:ekr.20121015183335.10157: *6* handle_all_keywords
        def handle_all_keywords (self,aList):

            '''
            converts if ( x ) to if x:
            converts while ( x ) to while x:
            '''

            statements = ('elif','for','if','while',)
            i = 0
            while i < len(aList):
                if self.is_string_or_comment(aList,i):
                    i = self.skip_string_or_comment(aList,i)
                elif any([self.match_word(aList,i,z) for z in statements]):
                    i = self.handle_keyword(aList,i)
                # elif (
                    # self.match_word(aList,i,"if") or
                    # self.match_word(aList,i,"while") or
                    # self.match_word(aList,i,"for") or
                    # self.match_word(aList,i,"elif")
                # ):
                    # i = self.handle_keyword(aList,i)
                else:
                    i += 1
            # print "handAllKeywords2:", ''.join(aList)
        #@+node:ekr.20121015183335.10158: *7* handle_keyword
        def handle_keyword (self,aList,i):

            if self.match_word(aList,i,"if"):
                i += 2
            elif self.match_word(aList,i,"elif"):
                i += 4
            elif self.match_word(aList,i,"while"):
                i += 5
            elif self.match_word(aList,i,"for"):
                i += 3
            else: assert False,'not a keyword'

            # Make sure one space follows the keyword.
            k = i
            i = self.skip_ws(aList,i)
            if k == i:
                c = aList[i]
                aList[i:i+1] = [ ' ', c ]
                i += 1

            # Remove '(' and matching ')' and add a ':'
            if aList[i] == "(":
                # Look ahead.  Don't remove if we span a line.
                j = self.skip_to_matching_bracket(aList, i)
                k = i
                found = False
                while k < j and not found:
                    found = aList[k] == '\n'
                    k += 1
                if not found:
                    j = self.removeMatchingBrackets(aList,i)
                if j > i and j < len(aList):
                    ch = aList[j]
                    aList[j:j+1] = [ch,":", " "]
                    j = j + 2
                return j
            return i
        #@+node:ekr.20121016024338.10190: *6* mungeAllClasses
        def mungeAllClasses(self,aList):

            '''Scan for a '{' at the top level that is preceeded by ')' '''

            i = 0
            while i < len(aList):
                progress = i
                if self.is_string_or_comment(aList,i):
                    i = self.skip_string_or_comment(aList,i)
                elif self.match_word(aList,i,'class'):
                    i1 = i
                    i = self.skip_line(aList,i)
                    aList[i-1:i] = list('%s:' % aList[i-1])
                    s = ''.join(aList[i1:i])
                    k = s.find(' extends ')
                    if k > -1:
                        k1 = k
                        k = g.skip_id(s,k+1)
                        k = g.skip_ws(s,k)
                        if k < len(s) and g.is_c_id(s[k]):
                            k2 = g.skip_id(s,k)
                            word = s[k:k2]
                            aList[i1:i] = list('%s (%s)' % (s[:k1],word))

                elif self.match_word(aList,i,'interface'):
                    aList[i:i+len('interface')] = list('class')
                    i = self.skip_line(aList,i)
                    aList[i-1:i] = list('%s: # interface' % aList[i-1])
                    i = self.skip_line(aList,i) # Essential.
                else:
                    i += 1
                assert i > progress
        #@+node:ekr.20121015183335.10148: *6* mungeAllFunctions & helpers
        def mungeAllFunctions(self,aList):

            '''Scan for a '{' at the top level that is preceeded by ')' '''

            prevSemi = 0 # Previous semicolon: header contains all previous text
            i = 0
            firstOpen = None
            while i < len(aList):
                progress = i
                if self.is_string_or_comment(aList,i):
                    j = self.skip_string_or_comment(aList,i)
                    prevSemi = j
                elif self.match(aList,i,'('):
                    if not firstOpen:
                        firstOpen = i
                    j = i + 1
                elif self.match(aList,i,';'):
                    j = i + 1
                    prevSemi = j
                elif self.match(aList,i,"{"):
                    j = self.handlePossibleFunctionHeader(aList,i,prevSemi,firstOpen)
                    prevSemi = j
                    firstOpen = None # restart the scan
                    # g.trace(repr(''.join(aList[prevSemi:prevSemi+20])))
                else:
                    j = i + 1

                # Handle unusual cases.
                if j <= progress:
                    j = progress + 1
                assert j > progress

                i = j
        #@+node:ekr.20121015183335.10149: *7* handlePossibleFunctionHeader
        # converts function header lines from typescript format to python format.
        # That is, converts
        ### x1..nn w::y ( t1 z1,..tn zn) { C++
        # (public|private|export) name (t1: z1, ... tn: zn {
        # to
        # def y (z1,..zn): { # (public|private|export)

        def handlePossibleFunctionHeader (self,aList,i,prevSemi,firstOpen):

            trace = False
            assert(self.match(aList,i,"{"))

            prevSemi = self.skip_ws_and_nl(aList, prevSemi)
            close = self.prevNonWsOrNlChar(aList,i)

            if close < 0 or aList[close] != ')':
                # Should not increase *Python* indent.
                return 1 + self.skip_to_matching_bracket(aList,i)

            if not firstOpen:
                return 1 + self.skip_to_matching_bracket(aList,i)

            close2 = self.skip_to_matching_bracket(aList, firstOpen)
            if close2 != close:
                return 1 + self.skip_to_matching_bracket(aList,i)

            open_paren = firstOpen
            assert(aList[open_paren]=='(')
            head = aList[prevSemi:open_paren]

            # do nothing if the head starts with "if", "for" or "while"
            k = self.skip_ws(head,0)
            if k >= len(head) or not head[k].isalpha():
                return 1 + self.skip_to_matching_bracket(aList,i)

            kk = self.skip_past_word(head,k)
            if kk > k:
                headString = ''.join(head[k:kk])
                # C keywords that might be followed by '{'
                # print "headString:", headString
                if headString in [ "do", "for", "if", "struct", "switch", "while"]: ### "class", 
                    return 1 + self.skip_to_matching_bracket(aList, i)

            args = aList[open_paren:close+1]
            k = 1 + self.skip_to_matching_bracket(aList,i)
            body = aList[close+1:k]

            if trace:
                g.trace('\nhead: %s\nargs: %s\nbody: %s' % (
                    ''.join(head),''.join(args),''.join(body)))

            head = self.massageFunctionHead(head)
            args = self.massageFunctionArgs(args)
            body = self.massageFunctionBody(body)

            if False and trace:
                g.trace('\nhead2: %s\nargs2: %s\nbody2: %s' % (
                    ''.join(head),''.join(args),''.join(body)))

            result = []
            if head: result.extend(head)
            if args: result.extend(args)
            if body: result.extend(body)

            aList[prevSemi:k] = result
            return prevSemi + len(result)
        #@+node:ekr.20121015183335.10150: *7* massageFunctionArgs
        def massageFunctionArgs (self,args):

            assert(args[0]=='(')
            assert(args[-1]==')')

            result = ['('] ; lastWord = []
            if self.class_name:
                for item in list("self,"): result.append(item) #can put extra comma

            i = 1
            while i < len(args):
                i = self.skip_ws_and_nl(args, i)
                c = args[i]
                if c.isalpha():
                    j = self.skip_past_word(args,i)
                    lastWord = args[i:j]
                    i = j
                elif c == ',' or c == ')':
                    for item in lastWord:
                        result.append(item)
                    if lastWord != [] and c == ',':
                        result.append(',')
                    lastWord = []
                    i += 1
                else: i += 1
            if result[-1] == ',':
                del result[-1]
            result.append(')')
            result.append(':')
            # print "new args:", ''.join(result)
            return result
        #@+node:ekr.20121015183335.10151: *7* massageFunctionHead (sets .class_name)
        def massageFunctionHead (self,head):

            result = []
            prevWord = []
            self.class_name = ''
            i = 0
            # g.trace(repr(''.join(head)))
            while i < len(head):
                i = self.skip_ws_and_nl(head,i)
                if i < len(head) and head[i].isalpha():
                    result = []
                    j = self.skip_past_word(head,i)
                    prevWord = head[i:j]
                    i = j
                    # look for ::word2
                    i = self.skip_ws(head,i)
                    if self.match(head,i,"::"):
                        # Set the global to the class name.
                        self.class_name = ''.join(prevWord)
                        # print(class name:", self.class_name)
                        i = self.skip_ws(head,i+2)
                        if i < len(head) and (head[i]=='~' or head[i].isalpha()):
                            j = self.skip_past_word(head,i)
                            if head[i:j] == prevWord:
                                result.extend('__init__')
                            elif head[i]=='~' and head[i+1:j] == prevWord:
                                result.extend('__del__')
                            else:
                                # result.extend(list('::'))
                                result.extend(head[i:j])
                            i = j
                    else:
                        result.extend(prevWord)
                else: i += 1

            finalResult = list("def ")
            finalResult.extend(result)
            return finalResult
        #@+node:ekr.20121015183335.10152: *7* massageFunctionBody & helper
        def massageFunctionBody (self,body):

            # body = self.massageIvars(body)
            # body = self.removeCasts(body)
            # body = self.removeTypeNames(body)
            body = self.dedentBlocks(body)
            return body
        #@+node:ekr.20121015183335.10153: *8* dedentBlocks
        def dedentBlocks (self,body):

            '''Look for '{' preceded by '{' or '}' or ';'
            (with intervening whitespace and comments).
            '''

            i = 0
            while i < len(body):
                j = i
                ch = body[i]
                if self.is_string_or_comment(body,i):
                    j = self.skip_string_or_comment(body,i)
                elif ch in '{};':
                    # Look ahead ofr '{'
                    j += 1
                    while True:
                        k = j
                        j = self.skip_ws_and_nl(body,j)
                        if self.is_string_or_comment(body,j):
                            j = self.skip_string_or_comment(body,j)
                        if k == j: break
                        assert k < j
                    if self.match(body,j,'{'):
                        k = j
                        j = self.skip_to_matching_bracket(body,j)
                        # g.trace('found block\n',''.join(body[k:j+1]))
                        m = '# <Start dedented block>...'
                        body[k:k+1] = list(m)
                        j += len(m)
                        while k < j:
                            progress = k
                            if body[k] == '\n':
                                k += 1
                                spaces = 0
                                while spaces < 4 and k < j:
                                    if body[k] == ' ':
                                        spaces += 1
                                        k += 1
                                    else:
                                        break
                                if spaces > 0:
                                    del body[k-spaces:k]
                                    k -= spaces
                                    j -= spaces
                            else:
                                k += 1
                            assert progress < k
                        m = '    # <End dedented block>'
                        body[j:j+1] = list(m)
                        j += len(m)
                else:
                    j = i + 1

                # Defensive programming.
                if i == j:
                    j += 1
                assert i < j
                i = j

            return body
        #@-others
    #@-<< class TS_To_Python (To_Python) >>

    def cToPy (self,event):

        ''' The c-to-python command converts c or c++ text to python text.
        The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.'''

        self.C_To_Python(self.c).go()
        self.c.bodyWantsFocus()

    def tsToPy (self,event):

        ''' The typescript-to-python command converts typescript text to python
        text. The conversion is not perfect, but it eliminates a lot of tedious
        text manipulation.'''

        # Compiler stats: 35 files, 1489 nodes, 100 to 120 sec.
        self.TS_To_Python(self.c).go()
        self.c.bodyWantsFocus()
    #@+node:ekr.20100209160132.5763: *3* cache (leoEditCommands)
    def clearAllCaches (self,event=None):

        '''Clear all of Leo's file caches.'''

        c = self.c
        if c.cacher:
            c.cacher.clearAllCaches()

    def clearCache (self,event=None):

        '''Clear the outline's file cache.'''

        c = self.c
        if c.cacher:
            c.cacher.clearCache()
    #@+node:ekr.20050920084036.57: *3* capitalization & case
    #@+node:ekr.20051015114221: *4* capitalizeWord & up/downCaseWord
    def capitalizeWord (self,event):
        '''Capitalize the word at the cursor.'''
        self.capitalizeHelper(event,'cap','capitalize-word')

    def downCaseWord (self,event):
        '''Convert all characters of the word at the cursor to lower case.'''
        self.capitalizeHelper(event,'low','downcase-word')

    def upCaseWord (self,event):
        '''Convert all characters of the word at the cursor to UPPER CASE.'''
        self.capitalizeHelper(event,'up','upcase-word')
    #@+node:ekr.20050920084036.145: *4* changePreviousWord (not used)
    # def changePreviousWord (self,event):

        # k = self.k ; stroke = k.stroke
        # w = self.editWidget(event)
        # if not w: return

        # i = w.getInsertPoint()
        # self.beginCommand(undoType='change-previous-word')
        # self.moveWordHelper(event,extend=False,forward=False)

        # if stroke == '<Alt-c>':
            # self.capitalizeWord(event)
        # elif stroke == '<Alt-u>':
            # self.upCaseWord(event)
        # elif stroke == '<Alt-l>':
            # self.downCaseWord(event)

        # w.setInsertPoint(i)

        # self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20051015114221.1: *4* capitalizeHelper
    def capitalizeHelper (self,event,which,undoType):

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getWord(s,ins)
        word = s[i:j]
        # g.trace('word',repr(word))
        if not word.strip(): return

        self.beginCommand(undoType=undoType)

        if   which == 'cap':  word2 = word.capitalize()
        elif which == 'low':  word2 = word.lower()
        elif which == 'up':   word2 = word.upper()
        else: g.trace('can not happen: which = %s' %s (which))

        changed = word != word2
        # g.trace('changed',changed,'word2',repr(word2))

        if changed:
            w.delete(i,j)
            w.insert(i,word2)
            w.setSelectionRange(ins,ins,insert=ins)

        self.endCommand(changed=changed,setLabel=True)
    #@+node:ekr.20051022142249: *3* clicks and focus (editCommandsClass)
    #@+node:ekr.20060211100905: *4* activate-x-menu & activateMenu (editCommandsClass)
    def activateCmdsMenu    (self,event=None):
        '''Activate Leo's Cmnds menu.'''
        self.activateMenu('Cmds')

    def activateEditMenu    (self,event=None):
        '''Activate Leo's Edit menu.'''
        self.activateMenu('Edit')

    def activateFileMenu    (self,event=None):
        '''Activate Leo's File menu.'''
        self.activateMenu('File')

    def activateHelpMenu    (self,event=None):
        '''Activate Leo's Help menu.'''
        self.activateMenu('Help')

    def activateOutlineMenu (self,event=None):
        '''Activate Leo's Outline menu.'''
        self.activateMenu('Outline')

    def activatePluginsMenu (self,event=None):
        '''Activate Leo's Plugins menu.'''
        self.activateMenu('Plugins')

    def activateWindowMenu  (self,event=None):
        '''Activate Leo's Window menu.'''
        self.activateMenu('Window')

    def activateMenu (self,menuName):
        c = self.c
        c.frame.menu.activateMenu(menuName)
    #@+node:ekr.20051022144825.1: *4* cycleFocus
    def cycleFocus (self,event):

        '''Cycle the keyboard focus between Leo's outline, body and log panes.'''

        c = self.c ; k = c.k ; w = event and event.widget

        body = c.frame.body.bodyCtrl
        log  = c.frame.log.logCtrl
        tree = c.frame.tree.canvas

        # A hack for the Qt gui.
        if hasattr(w,'logCtrl'):
            w = w.logCtrl

        panes = [body,log,tree]

        # g.trace(w in panes,event.widget,panes)

        if w in panes:
            i = panes.index(w) + 1
            if i >= len(panes): i = 0
            pane = panes[i]
        else:
            pane = body

        # Warning: traces mess up the focus
        # g.pr(g.app.gui.widget_name(w),g.app.gui.widget_name(pane))

        # This works from the minibuffer *only* if there is no typing completion.
        c.widgetWantsFocusNow(pane)
        k.newMinibufferWidget = pane
        k.showStateAndMode()
    #@+node:ekr.20060613090701: *4* cycleAllFocus (editCommandsClass)
    editWidgetCount = 0

    def cycleAllFocus (self,event):

        '''Cycle the keyboard focus between Leo's outline,
        all body editors and all tabs in the log pane.'''

        trace = False and not g.unitTesting
        c,k = self.c,self.c.k
        w = event and event.widget # Does **not** require a text widget.
        pane = None # The widget that will get the new focus.
        log = c.frame.log
        w_name = g.app.gui.widget_name
        if trace: g.trace('**before',w_name(w),'isLog',log.isLogWidget(w))
        # w may not be the present body widget, so test its name, not its id.
        if w_name(w).find('tree') > -1 or w_name(w).startswith('head'):
            pane = c.frame.body.bodyCtrl
        elif w_name(w).startswith('body'):
            # Cycle through the *body* editor if there are several.
            n = c.frame.body.numberOfEditors
            if n > 1:
                self.editWidgetCount += 1
                if self.editWidgetCount == 1:
                    pane = c.frame.body.bodyCtrl
                elif self.editWidgetCount > n:
                    self.editWidgetCount = 0
                    c.frame.log.selectTab('Log')
                    pane = c.frame.log.logCtrl
                else:
                    c.frame.body.cycleEditorFocus(event)
                    pane = None
            else:
                self.editWidgetCount = 0
                c.frame.log.selectTab('Log')
                pane = c.frame.log.logCtrl
        elif log.isLogWidget(w):
            # A log widget.  Cycle until we come back to 'Log'.
            log.cycleTabFocus()
            pane = c.frame.tree.canvas if log.tabName == 'Log' else None
        else:
            # A safe default: go to the body.
            if trace: g.trace('* default to body')
            pane = c.frame.body.bodyCtrl
        if trace: g.trace('**after',w_name(pane),pane)
        if pane:
            k.newMinibufferWidget = pane
            c.widgetWantsFocusNow(pane)
            k.showStateAndMode()
    #@+node:ekr.20051022144825: *4* focusTo...
    def focusToBody (self,event=None):
        '''Put the keyboard focus in Leo's body pane.'''
        c = self.c ; k = c.k
        c.bodyWantsFocus()
        if k:
            k.setDefaultInputState()
            k.showStateAndMode()

    def focusToLog (self,event=None):
        '''Put the keyboard focus in Leo's log pane.'''
        self.c.logWantsFocus()

    def focusToMinibuffer (self,event=None):
        '''Put the keyboard focus in Leo's minibuffer.'''
        self.c.minibufferWantsFocus()

    def focusToTree (self,event=None):
        '''Put the keyboard focus in Leo's outline pane.'''
        self.c.treeWantsFocus()
    #@+node:ekr.20060211063744.1: *4* clicks in the headline (leoEditCommands)
    # These call wrappers that trigger hooks.

    def clickHeadline (self,event=None):
        '''Simulate a click in the headline of the presently selected node.'''
        c = self.c
        c.frame.tree.onHeadlineClick(event,c.p)

    def doubleClickHeadline (self,event=None):
        '''Simulate a double click in headline of the presently selected node.'''
        c = self.c
        return c.frame.tree.onDoubleClickHeadline(event,c.p)

    # This is not used in Leo at present.

    def rightClickHeadline (self,event=None):
        '''Simulate a right click in the headline of the presently selected node.'''
        c = self.c
        c.frame.tree.onHeadlineRightClick(event,c.p)
    #@+node:ekr.20060211055455: *4* clicks in the icon box (leoEditCommands)
    # These call the actual event handlers so as to trigger hooks.

    def ctrlClickIconBox(self,event=None):
        '''Simulate a ctrl-click in the icon box of the presently selected node.'''
        c = self.c
        c.frame.tree.OnIconCtrlClick(c.p)
            # Calls the base leoTree method.

    def clickIconBox (self,event=None):
        '''Simulate a click in the icon box of the presently selected node.'''
        c = self.c ; p = c.p
        c.frame.tree.onIconBoxClick(event,p=p)

    def doubleClickIconBox (self,event=None):
        '''Simulate a double-click in the icon box of the presently selected node.'''
        c = self.c ; p = c.p
        c.frame.tree.onIconBoxDoubleClick(event,p=p)

    def rightClickIconBox (self,event=None):

        '''Simulate a right click in the icon box of the presently selected node.'''
        c = self.c ; p = c.p
        c.frame.tree.onIconBoxRightClick(event,p=p)
    #@+node:ekr.20060211062025: *4* clickClickBox
    # Call the actual event handlers so as to trigger hooks.

    def clickClickBox (self,event=None):

        '''Simulate a click in the click box (+- box) of the presently selected node.'''

        c = self.c ; p = c.p
        c.frame.tree.onClickBoxClick(event,p=p)
    #@+node:ekr.20060211063744.2: *4* simulate...Drag
    # These call the drag setup methods which in turn trigger hooks.

    def simulateBeginDrag (self,event=None):

        '''Simulate the start of a drag in the presently selected node.'''
        c = self.c ; p = c.p
        c.frame.tree.startDrag(event,p=p)

    def simulateEndDrag (self,event=None):

        '''Simulate the end of a drag in the presently selected node.'''
        c = self.c

        # Note: this assumes that tree.startDrag has already been called.
        c.frame.tree.endDrag(event)
    #@+node:ekr.20051019183105: *3* color & font
    #@+node:ekr.20051019183105.1: *4* show-colors
    def showColors (self,event):

        '''Open a tab in the log pane showing various color pickers.'''

        c = self.c ; log = c.frame.log ; tabName = 'Colors'

        if log.frameDict.get(tabName):
            log.selectTab(tabName)
        else:
            log.selectTab(tabName)
            log.createColorPicker(tabName)
    #@+node:ekr.20051019201809: *4* editCommands.show-fonts & helpers
    def showFonts (self,event):

        '''Open a tab in the log pane showing a font picker.'''

        c = self.c ; log = c.frame.log ; tabName = 'Fonts'

        if log.frameDict.get(tabName):
            log.selectTab(tabName)
        else:
            log.selectTab(tabName)
            log.createFontPicker(tabName)
    #@+node:ekr.20050920084036.132: *3* comment column...
    #@+node:ekr.20050920084036.133: *4* setCommentColumn
    def setCommentColumn (self,event):

        '''Set the comment column for the indent-to-comment-column command.'''

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        ins = w.getInsertPoint()
        row,col = g.convertPythonIndexToRowCol(s,ins)
        self.ccolumn = col
    #@+node:ekr.20050920084036.134: *4* indentToCommentColumn
    def indentToCommentColumn (self,event):

        '''Insert whitespace to indent the line containing the insert point to the comment column.'''

        w = self.editWidget(event)
        if not w: return
        self.beginCommand(undoType='indent-to-comment-column')
        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        line = s[i:j]
        c1 = int(self.ccolumn)
        line2 = ' ' * c1 + line.lstrip()
        if line2 != line:
            w.delete(i,j)
            w.insert(i,line2)
        w.setInsertPoint(i+c1)
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.62: *3* esc methods for Python evaluation
    #@+node:ekr.20050920084036.63: *4* watchEscape
    def watchEscape (self,event):

        '''Enter watch escape mode.'''

        c,k = self.c,self.k

        char = event and event.char or ''

        if not k.inState():
            k.setState('escape','start',handler=self.watchEscape)
            k.setLabelBlue('Esc ')
        elif k.getStateKind() == 'escape':
            state = k.getState('escape')
            # hi1 = k.keysymHistory [0]
            # hi2 = k.keysymHistory [1]
            data1 = g.app.lossage[0]
            data2 = g.app.lossage[1]
            ch1, stroke1 = data1
            ch2, stroke2 = data2

            if state == 'esc esc' and char == ':':
                self.evalExpression(event)
            elif state == 'evaluate':
                self.escEvaluate(event)
            # elif hi1 == hi2 == 'Escape':
            elif stroke1 == 'Escape' and stroke2 == 'Escape':
                k.setState('escape','esc esc')
                k.setLabel('Esc Esc -')
            elif char not in ('Shift_L','Shift_R'):
                k.keyboardQuit()
    #@+node:ekr.20050920084036.64: *4* escEvaluate (Revise)
    def escEvaluate (self,event):

        c,k = self.c,self.k

        w = self.editWidget(event)
        if not w: return

        char = event and event.char or ''

        if k.getLabel() == 'Eval:':
            k.setLabel('')

        if char in ('\n','Return'):
            expression = k.getLabel()
            try:
                ok = False
                result = eval(expression,{},{})
                result = str(result)
                i = w.getInsertPoint()
                w.insert(i,result)
                ok = True
            finally:
                k.keyboardQuit()
                if not ok:
                    k.setLabel('Error: Invalid Expression')
        else:
            k.updateLabel(event)
    #@+node:ekr.20050920084036.65: *3* evalExpression
    def evalExpression (self,event):

        '''Evaluate a Python Expression entered in the minibuffer.'''

        k = self.k ; state = k.getState('eval-expression')

        if state == 0:
            k.setLabelBlue('Eval: ',protect=True)
            k.getArg(event,'eval-expression',1,self.evalExpression)
        else:
            k.clearState()
            try:
                e = k.arg
                result = str(eval(e,{},{}))
                k.setLabelGrey('Eval: %s -> %s' % (e,result))
            except Exception:
                k.setLabelGrey('Invalid Expression: %s' % e)
    #@+node:ekr.20050920084036.66: *3* fill column and centering
    #@+at
    # These methods are currently just used in tandem to center the line or region within the fill column.
    # for example, dependent upon the fill column, this text:
    # 
    # cats
    # raaaaaaaaaaaats
    # mats
    # zaaaaaaaaap
    # 
    # may look like
    # 
    #                                  cats
    #                            raaaaaaaaaaaats
    #                                  mats
    #                              zaaaaaaaaap
    # 
    # after an center-region command via Alt-x.
    #@@c

    #@+others
    #@+node:ekr.20050920084036.67: *4* centerLine
    def centerLine (self,event):

        '''Centers line within current fill column'''

        c,k,w = self.c,self.k,self.editWidget(event)
        if not w: return

        if self.fillColumn > 0:
            fillColumn = self.fillColumn
        else:
            d = c.scanAllDirectives()
            fillColumn = d.get("pagewidth")

        s = w.getAllText()
        i,j = g.getLine(s,w.getInsertPoint())
        line = s [i:j].strip()
        if not line or len(line) >= fillColumn: return

        self.beginCommand(undoType='center-line')
        n = (fillColumn-len(line)) / 2
        ws = ' ' * n
        k = g.skip_ws(s,i)
        if k > i: w.delete(i,k-i)
        w.insert(i,ws)
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.68: *4* setFillColumn
    def setFillColumn (self,event):

        '''Set the fill column used by the center-line and center-region commands.'''

        k = self.k ; state = k.getState('set-fill-column')

        if state == 0:
            k.setLabelBlue('Set Fill Column: ')
            k.getArg(event,'set-fill-column',1,self.setFillColumn)
        else:
            k.clearState()
            try:
                # Bug fix: 2011/05/23: set the fillColumn ivar!
                self.fillColumn = n = int(k.arg)
                k.setLabelGrey('fill column is: %d' % n)
                k.commandName = 'set-fill-column %d' % n
            except ValueError:
                k.resetLabel()
    #@+node:ekr.20050920084036.69: *4* centerRegion
    def centerRegion (self,event):

        '''Centers the selected text within the fill column'''

        c,k,w = self.c,self.k,self.editWidget(event)
        if not w: return

        s = w.getAllText()
        sel_1, sel_2 = w.getSelectionRange()
        ind, junk = g.getLine(s,sel_1)
        junk, end = g.getLine(s,sel_2)

        if self.fillColumn > 0:
            fillColumn = self.fillColumn
        else:
            d = c.scanAllDirectives()
            fillColumn = d.get("pagewidth")

        self.beginCommand(undoType='center-region')

        inserted = 0
        while ind < end:
            s = w.getAllText()
            i, j = g.getLine(s,ind)
            line = s [i:j].strip()
            # g.trace(len(line),repr(line))
            if len(line) >= fillColumn:
                ind = j
            else:
                n = int((fillColumn-len(line))/2)
                inserted += n
                k = g.skip_ws(s,i)
                if k > i: w.delete(i,k-i)
                w.insert(i,' '*n)
                ind = j + n-(k-i)

        w.setSelectionRange(sel_1,sel_2+inserted)

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.70: *4* setFillPrefix
    def setFillPrefix( self, event ):

        '''Make the selected text the fill prefix.'''

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        i,j = w.getSelectionRange()
        self.fillPrefix = s[i:j]
    #@+node:ekr.20050920084036.71: *4* _addPrefix
    def _addPrefix (self,ntxt):

        ntxt = ntxt.split('.')
        ntxt = map(lambda a: self.fillPrefix+a,ntxt)
        ntxt = '.'.join(ntxt)
        return ntxt
    #@-others
    #@+node:ekr.20060417194232: *3* find (quick)
    #@+node:ekr.20060925151926: *4* backward/findCharacter & helper
    def backwardFindCharacter (self,event):
        '''Search backwards for a character.'''
        return self.findCharacterHelper(event,backward=True,extend=False)

    def backwardFindCharacterExtendSelection (self,event):
        '''Search backward for a character, extending the selection.'''
        return self.findCharacterHelper(event,backward=True,extend=True)

    def findCharacter (self,event):
        '''Search for a character.'''
        return self.findCharacterHelper(event,backward=False,extend=False)

    def findCharacterExtendSelection (self,event):
        '''Search for a character, extending the selection.'''
        return self.findCharacterHelper(event,backward=False,extend=True)
    #@+node:ekr.20060417194232.1: *5* findCharacterHelper
    def findCharacterHelper (self,event,backward,extend):

        '''Put the cursor at the next occurance of a character on a line.'''

        c = self.c ; k = c.k ; tag = 'find-char' ; state = k.getState(tag)

        if state == 0:
            w = self.editWidget(event) # Sets self.w
            if not w: return
            self.event = event
            self.backward = backward
            self.extend = extend or self.extendMode # Bug fix: 2010/01/19
            self.insert = w.getInsertPoint()
            s = '%s character%s: ' % (
                g.choose(backward,'Backward find','Find'),
                g.choose(extend,' & extend',''))
            k.setLabelBlue(s,protect=True)
            # Get the arg without touching the focus.
            k.getArg(event,tag,1,self.findCharacter,oneCharacter=True,useMinibuffer=False)
        else:
            event = self.event ; w = self.w
            backward = self.backward
            extend = self.extend or self.extendMode
            ch = k.arg ; s = w.getAllText()
            ins = w.toPythonIndex(self.insert)
            i = ins + g.choose(backward,-1,+1) # skip the present character.
            if backward:
                start = 0
                j = s.rfind(ch,start,max(start,i)) # Skip the character at the cursor.
                if j > -1: self.moveToHelper(event,j,extend)
            else:
                end = len(s)
                j = s.find(ch,min(i,end),end) # Skip the character at the cursor.
                if j > -1: self.moveToHelper(event,j,extend)
            k.resetLabel()
            k.clearState()
    #@+node:ekr.20060417194232.2: *4* findWord and FindWordOnLine & helper
    def findWord(self,event):

        '''Put the cursor at the next word that starts with a character.'''

        return self.findWordHelper(event,oneLine=False)

    def findWordInLine(self,event):

        '''Put the cursor at the next word (on a line) that starts with a character.'''

        return self.findWordHelper(event,oneLine=True)

    #@+node:ekr.20080408060320.1: *5* findWordHelper
    def findWordHelper (self,event,oneLine):

        k = self.k ; tag = 'find-word' ; state = k.getState(tag)

        if state == 0:
            w = self.editWidget(event) # Sets self.w
            if not w: return
            self.oneLineFlag = oneLine
            k.setLabelBlue('Find word %sstarting with: ' % (
                g.choose(oneLine,'in line ','')))
            k.getArg(event,tag,1,self.findWord,oneCharacter=True)
        else:        
            ch = k.arg
            if ch:
                w = self.w
                i = w.getInsertPoint()
                s = w.getAllText()
                end = len(s)
                if self.oneLineFlag:
                    end = s.find('\n',i) # Limit searches to this line.
                    if end == -1: end = len(s)
                while i < end:
                    i = s.find(ch,i+1,end) # Ensure progress and i > 0.
                    if i == -1:
                        break
                    elif not g.isWordChar(s[i-1]):
                        w.setSelectionRange(i,i,insert=i)
                        break
            k.resetLabel()
            k.clearState()
    #@+node:ekr.20050920084036.72: *3* goto...
    #@+node:ekr.20050929115226: *4* gotoCharacter
    def gotoCharacter (self,event):

        '''Put the cursor at the n'th character of the buffer.'''

        k = self.k ; state = k.getState('goto-char')

        if state == 0:
            w = self.editWidget(event) # Sets self.w
            if not w: return
            k.setLabelBlue("Goto n'th character: ")
            k.getArg(event,'goto-char',1,self.gotoCharacter)
        else:
            n = k.arg ; w = self.w ; ok = False
            if n.isdigit():
                n = int(n)
                if n >= 0:
                    w.setInsertPoint(n)
                    w.seeInsertPoint()
                    ok = True
            if not ok:
                g.warning('goto-char takes non-negative integer argument')
            k.resetLabel()
            k.clearState()
    #@+node:ekr.20060417181052: *4* gotoGlobalLine
    def gotoGlobalLine (self,event):

        '''Put the cursor at the n'th line of a file or script.
        This is a minibuffer interface to Leo's legacy Go To Line number command.'''

        c = self.c
        k = self.k ; tag = 'goto-global-line' ; state = k.getState(tag)

        if state == 0:
            w = self.editWidget(event) # Sets self.w
            if not w: return
            k.setLabelBlue('Goto global line: ')
            k.getArg(event,tag,1,self.gotoGlobalLine)
        else:
            n = k.arg
            k.resetLabel()
            k.clearState()
            if n.isdigit():
                c.goToLineNumber(c).go(n=int(n))
    #@+node:ekr.20050929124234: *4* gotoLine
    def gotoLine (self,event):

        '''Put the cursor at the n'th line of the buffer.'''

        k = self.k ; state = k.getState('goto-line')

        if state == 0:
            w = self.editWidget(event) # Sets self.w
            if not w: return
            k.setLabelBlue('Goto line: ')
            k.getArg(event,'goto-line',1,self.gotoLine)
        else:
            n = k.arg ;  w = self.w
            if n.isdigit():
                s = w.getAllText()
                i = g.convertRowColToPythonIndex(s,n,0)
                w.setInsertPoint(i)
                w.seeInsertPoint()
            k.resetLabel()
            k.clearState()
    #@+node:ekr.20071114081313: *3* icons...
    #@+at
    # 
    # To do:
    # 
    # - Define standard icons in a subfolder of Icons folder?
    # - Tree control recomputes height of each line.
    #@+node:ekr.20080108092811: *4*  Helpers
    #@+node:ekr.20080108091349: *5* appendImageDictToList
    def appendImageDictToList(self,aList,iconDir,path,xoffset,**kargs):

        c = self.c
        path = c.os_path_finalize_join(iconDir,path)
        relPath = g.makePathRelativeTo(path,iconDir)
        image,image_height = g.app.gui.getTreeImage(c,path)
        if not image:
            g.es('can not load image:',path)
            return xoffset
        if image_height is None:
            yoffset = 0
        else:
            yoffset = 0 # (c.frame.tree.line_height-image_height)/2
            # TNB: I suspect this is being done again in the drawing code
        newEntry = {
            'type' : 'file',
            'file' : path,
            'relPath': relPath,
            'where' : 'beforeHeadline',
            'yoffset' : yoffset, 'xoffset' : xoffset, 'xpad' : 1, # -2,
            'on' : 'vnode',
        }
        newEntry.update(kargs)  # may switch 'on' to 'vnode'
        aList.append (newEntry)
        xoffset += 2
        return xoffset
    #@+node:ekr.20090701125429.6013: *5* dHash
    def dHash(self, d):
        """Hash a dictionary"""
        return ''.join(['%s%s' % (str(k),str(d[k])) for k in sorted(d)])
    #@+node:tbrown.20080119085249: *5* getIconList
    def getIconList(self, p):
        """Return list of icons for position p, call setIconList to apply changes"""

        trace = False and not g.unitTesting
        if trace:
            if p == self.c.rootPosition(): g.trace('='*40)
            g.trace(p.h)

        fromVnode = []
        if hasattr(p.v,'unknownAttributes'):
            if trace: g.trace(p.v.u)
            fromVnode = [dict(i) for i in p.v.u.get('icons',[])]
            for i in fromVnode: i['on'] = 'vnode'

        if trace and fromVnode: g.trace('fromVnode',fromVnode,p.h)

        return fromVnode
    #@+node:tbrown.20080119085249.1: *5* setIconList & helpers
    def setIconList(self, p, l):
        """Set list of icons for position p to l"""

        trace = False and not g.unitTesting

        current = self.getIconList(p)
        if not l and not current: return  # nothing to do
        lHash = ''.join([self.dHash(i) for i in l])
        cHash = ''.join([self.dHash(i) for i in current])
        # if trace: g.trace('lHash:',lHash)
        # if trace: g.trace('cHash:',cHash)
        if lHash == cHash:
            # no difference between original and current list of dictionaries
            return

        if trace: g.trace(l)

        self._setIconListHelper(p, l, p.v)

    #@+node:ekr.20090701125429.6012: *6* _setIconListHelper
    def _setIconListHelper(self, p, subl, uaLoc):
        """icon setting code common between v and t nodes

        p - postion
        subl - list of icons for the v or t node
        uaLoc - the v or t node"""

        trace = False and not g.unitTesting

        if subl: # Update the uA.
            if not hasattr(uaLoc,'unknownAttributes'):
                uaLoc.unknownAttributes = {}
            uaLoc.unknownAttributes['icons'] = list(subl)
            # g.es((p.h,uaLoc.unknownAttributes['icons']))
            uaLoc.unknownAttributes["lineYOffset"] = 3
            uaLoc._p_changed = 1
            p.setDirty()
            if trace: g.trace('uA',uaLoc.u,uaLoc)
        else: # delete the uA.
            if hasattr(uaLoc,'unknownAttributes'):
                if 'icons' in uaLoc.unknownAttributes:
                    del uaLoc.unknownAttributes['icons']
                    uaLoc.unknownAttributes["lineYOffset"] = 0
                    uaLoc._p_changed = 1
                    p.setDirty()
            if trace: g.trace('del uA[icons]',uaLoc)
    #@+node:ekr.20071114082418: *4* deleteFirstIcon
    def deleteFirstIcon (self,event=None):

        '''Delete the first icon in the selected node's icon list.'''

        c = self.c ; p = c.p

        aList = self.getIconList(p)

        if aList:
            self.setIconList(p, aList[1:])
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20071114092622: *4* deleteIconByName
    def deleteIconByName (self,t,name,relPath): # t not used.
        """for use by the right-click remove icon callback"""
        c = self.c ; p = c.p

        aList = self.getIconList(p)
        if not aList: return

        basePath = c.os_path_finalize_join(g.app.loadDir,"..","Icons")
        absRelPath = c.os_path_finalize_join(basePath,relPath)
        name = c.os_path_finalize(name)

        newList = []
        for d in aList:
            name2 = d.get('file')
            name2 = c.os_path_finalize(name2)
            name2rel = d.get('relPath')
            # g.trace('name',name,'\nrelPath',relPath,'\nabsRelPath',absRelPath,'\nname2',name2,'\nname2rel',name2rel)
            if not (name == name2 or absRelPath == name2 or relPath == name2rel):
                newList.append(d)

        if len(newList) != len(aList):
            self.setIconList(p, newList)       
            c.setChanged(True)
            c.redraw_after_icons_changed()
        else:
            g.trace('not found',name)
    #@+node:ekr.20071114085054: *4* deleteLastIcon
    def deleteLastIcon (self,event=None):

        '''Delete the first icon in the selected node's icon list.'''

        c = self.c ; p = c.p

        aList = self.getIconList(p)

        if aList:
            self.setIconList(p, aList[:-1])
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20071114082418.1: *4* deleteNodeIcons
    def deleteNodeIcons (self,event=None):

        '''Delete all of the selected node's icons.'''

        c = self.c ; p = c.p

        if hasattr(p.v,"unknownAttributes"):
            a = p.v.unknownAttributes
            p.v._p_changed = 1
            self.setIconList(p,[])
            a["lineYOffset"] = 0
            p.setDirty()
            c.setChanged(True)
            c.redraw_after_icons_changed()
    #@+node:ekr.20071114081313.1: *4* insertIcon
    def insertIcon (self,event=None):

        '''Prompt for an icon, and insert it into the node's icon list.'''

        c = self.c ; p = c.p
        iconDir = c.os_path_finalize_join(g.app.loadDir,"..","Icons")
        os.chdir(iconDir)
        paths = g.app.gui.runOpenFileDialog(
            title='Get Icons',
            filetypes=[('All files','*'),('Gif','*.gif'), ('Bitmap','*.bmp'),('Icon','*.ico'),],
            defaultextension=None,
            multiple=True)
        if not paths: return
        aList = [] ; xoffset = 2
        for path in paths:
            xoffset = self.appendImageDictToList(aList,iconDir,path,xoffset)
        aList2 = self.getIconList(p)
        aList2.extend(aList)
        self.setIconList(p, aList2)
        c.setChanged(True)
        c.redraw_after_icons_changed()
    #@+node:ekr.20080108090719: *4* insertIconFromFile
    def insertIconFromFile (self,path,p=None,pos=None,**kargs):

        c = self.c
        if not p: p = c.p
        iconDir = c.os_path_finalize_join(g.app.loadDir,"..","Icons")
        os.chdir(iconDir)
        aList = [] ; xoffset = 2
        xoffset = self.appendImageDictToList(aList,iconDir,path,xoffset,**kargs)
        aList2 = self.getIconList(p)
        if pos is None: pos = len(aList2)
        aList2.insert(pos,aList[0])
        self.setIconList(p, aList2)
        c.setChanged(True)
        c.redraw_after_icons_changed()
    #@+node:ekr.20050920084036.74: *3* indent...
    #@+node:ekr.20050920084036.76: *4* deleteIndentation
    def deleteIndentation (self,event):

        '''Delete indentation in the presently line.'''

        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        line = s[i:j]
        line2 = s[i:j].lstrip()
        delta = len(line) - len(line2)
        if delta:
            self.beginCommand(undoType='delete-indentation')
            w.delete(i,j)
            w.insert(i,line2)
            ins -= delta
            w.setSelectionRange(ins,ins,insert=ins)
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.78: *4* indentRelative
    def indentRelative (self,event):

        '''The indent-relative command indents at the point based on the previous
        line (actually, the last non-empty line.) It inserts whitespace at the
        point, moving point, until it is underneath an indentation point in the
        previous line.

        An indentation point is the end of a sequence of whitespace or the end of
        the line. If the point is farther right than any indentation point in the
        previous line, the whitespace before point is deleted and the first
        indentation point then applicable is used. If no indentation point is
        applicable even then whitespace equivalent to a single tab is inserted.'''

        c = self.c ; undoType = 'indent-relative' ; w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        oldSel = w.getSelectionRange()
        oldYview = w.getYScrollPosition()
        # Find the previous non-blank line
        i,j = g.getLine(s,ins)
        while 1:
            if i <= 0: return
            i,j = g.getLine(s,i-1)
            line = s[i:j]
            if line.strip(): break
        self.beginCommand(undoType=undoType)
        try:
            k = g.skip_ws(s,i)
            ws = s[i:k]
            i2,j2 = g.getLine(s,ins)
            k = g.skip_ws(s,i2)
            line = ws + s[k:j2]
            w.delete(i2,j2)
            w.insert(i2,line)
            w.setInsertPoint(i2+len(ws))
            c.frame.body.onBodyChanged(undoType,oldSel=oldSel,oldText=s,oldYview=oldYview)
        finally:
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.85: *3* insert & delete...
    #@+node:ekr.20060417171125: *4* addSpace/TabToLines & removeSpace/TabFromLines & helper
    def addSpaceToLines (self,event):
        '''Add a space to start of all lines, or all selected lines.'''
        self.addRemoveHelper(event,ch=' ',add=True,undoType='add-space-to-lines')

    def addTabToLines (self,event):
        '''Add a tab to start of all lines, or all selected lines.'''
        self.addRemoveHelper(event,ch='\t',add=True,undoType='add-tab-to-lines')

    def removeSpaceFromLines (self,event):
        '''Remove a space from start of all lines, or all selected lines.'''
        self.addRemoveHelper(event,ch=' ',add=False,undoType='remove-space-from-lines')

    def removeTabFromLines (self,event):
        '''Remove a tab from start of all lines, or all selected lines.'''
        self.addRemoveHelper(event,ch='\t',add=False,undoType='remove-tab-from-lines')
    #@+node:ekr.20060417172056: *5* addRemoveHelper
    def addRemoveHelper(self,event,ch,add,undoType):

        c = self.c
        w = self.editWidget(event)
        if not w: return

        if w.hasSelection():s = w.getSelectedText()
        else:               s = w.getAllText()
        if not s: return

        # Insert or delete spaces instead of tabs when negative tab width is in effect.
        d = c.scanAllDirectives() ; width = d.get('tabwidth')
        if ch == '\t' and width < 0: ch = ' ' * abs(width)

        self.beginCommand(undoType=undoType)
        lines = g.splitLines(s)
        if add:
            result = [ch + line for line in lines]
        else:
            result = [g.choose(line.startswith(ch),line[len(ch):],line) for line in lines]
        result = ''.join(result)
        # g.trace('add',add,'hasSelection',w.hasSelection(),'result',repr(result))
        if w.hasSelection():
            i,j = w.getSelectionRange()
            w.delete(i,j)
            w.insert(i,result)
            w.setSelectionRange(i,i+len(result))
        else:
            w.setAllText(result)
            w.setSelectionRange(0,len(s))
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20051026092433.1: *4* backwardDeleteCharacter
    def backwardDeleteCharacter (self,event=None):

        '''Delete the character to the left of the cursor.'''

        c = self.c ; p = c.p
        w = self.editWidget(event)
        if not w: return

        wname = c.widget_name(w)
        ins = w.getInsertPoint()
        i,j = w.getSelectionRange()
        # g.trace(wname,i,j,ins)

        if wname.startswith('body'):
            self.beginCommand()
            try:
                d = c.scanAllDirectives(p)
                tab_width = d.get("tabwidth",c.tab_width)
                changed = True
                if i != j:
                    w.delete(i,j)
                    w.setSelectionRange(i,i,insert=i)
                elif i == 0:
                    changed = False
                elif tab_width > 0:
                    w.delete(ins-1)
                    w.setSelectionRange(ins-1,ins-1,insert=ins-1)
                else:
                    #@+<< backspace with negative tab_width >>
                    #@+node:ekr.20051026092746: *5* << backspace with negative tab_width >>
                    s = prev = w.getAllText()
                    ins = w.getInsertPoint()
                    i,j = g.getLine(s,ins)
                    s = prev = s[i:ins]
                    n = len(prev)
                    abs_width = abs(tab_width)

                    # Delete up to this many spaces.
                    n2 = (n % abs_width) or abs_width
                    n2 = min(n,n2) ; count = 0

                    while n2 > 0:
                        n2 -= 1
                        ch = prev[n-count-1]
                        if ch != ' ': break
                        else: count += 1

                    # Make sure we actually delete something.
                    i = ins-(max(1,count))
                    w.delete(i,ins)
                    w.setSelectionRange(i,i,insert=i)
                    #@-<< backspace with negative tab_width >>
            finally:
                self.endCommand(changed=changed,setLabel=False)
                    # Necessary to make text changes stick.
        else:
            # No undo in this widget.
            # Make sure we actually delete something if we can.
            s = w.getAllText()
            if i != j:
                j = max(i,min(j,len(s)))
                w.delete(i,j)
                w.setSelectionRange(i,i,insert=i)
            elif ins != 0:
                # Do nothing at the start of the headline.
                w.delete(ins-1)
                ins = ins-1
                w.setSelectionRange(ins,ins,insert=ins)
    #@+node:ekr.20070325094935: *4* cleanAllLines
    def cleanAllLines (self,event):

        '''Clean all lines in the selected tree.'''

        c = self.c
        u = c.undoer
        w = c.frame.body.bodyCtrl
        if not w: return
        tag = 'clean-all-lines'
        u.beforeChangeGroup(c.p,tag)
        n = 0
        for p in c.p.self_and_subtree():
            lines = []
            for s in g.splitLines(p.b):
                if s.strip():
                    lines.append(s)
                else:
                    # Ensures a trailing newline.
                    lines.append('\n')
            s2 = ''.join(lines)
            if s2 != p.b:
                print(p.h)
                bunch = u.beforeChangeNodeContents(p)
                p.b = s2
                p.v.setDirty()
                n += 1
                u.afterChangeNodeContents(p,tag,bunch)
        u.afterChangeGroup(c.p,tag)
        c.redraw_after_icons_changed()
        g.es('cleaned %s nodes' % n)
    #@+node:ekr.20060415112257: *4* cleanLines
    def cleanLines (self,event):

        '''Removes trailing whitespace from all lines, preserving newlines.
        '''

        w = self.editWidget(event)
        if not w: return
        if w.hasSelection():
            s = w.getSelectedText()
        else:
            s = w.getAllText()
        lines = []
        for line in g.splitlines(s):
            if line.rstrip():
                lines.append(line.rstrip())
            if line.endswith('\n'): lines.append('\n')
        result = ''.join(lines)
        if s != result:
            self.beginCommand(undoType='clean-lines')
            if w.hasSelection():
                i,j = w.getSelectionRange()
                w.delete(i,j)
                w.insert(i,result)
                w.setSelectionRange(i,j+len(result))
            else:
                i = w.getInsertPoint()
                w.delete(0,'end')
                w.insert(0,result)
                w.setInsertPoint(i)
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20060414085834: *4* clearSelectedText
    def clearSelectedText (self,event):

        '''Delete the selected text.'''

        w = self.editWidget(event)
        if not w: return
        i,j = w.getSelectionRange()
        if i == j: return
        self.beginCommand(undoType='clear-selected-text')
        w.delete(i,j)
        w.setInsertPoint(i)
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20100817125519.5833: *4* delete-word & backward-delete-word
    def deleteWord(self,event=None):
        '''Delete the word at the cursor.'''
        self.deleteWordHelper(event,forward=True)

    def backwardDeleteWord(self,event=None):
        '''Delete the word in front of the cursor.'''
        self.deleteWordHelper(event,forward=False)

    # Patch by NH2.
    def deleteWordSmart(self,event=None):
        '''Delete the word at the cursor, treating whitespace
        and symbols smartly.'''
        self.deleteWordHelper(event,forward=True,smart=True)

    def backwardDeleteWordSmart(self,event=None):
        '''Delete the word in front of the cursor, treating whitespace
        and symbols smartly.'''
        self.deleteWordHelper(event,forward=False,smart=True)

    def deleteWordHelper(self,event,forward,smart=False):
        c = self.c ; w = self.editWidget(event)
        if not w: return

        self.beginCommand(undoType="delete-word")
        if w.hasSelection():
            from_pos,to_pos = w.getSelectionRange()
        else:
            from_pos = w.getInsertPoint()
            self.moveWordHelper(event,extend=False,forward=forward,smart=smart)
            to_pos = w.getInsertPoint()

        # For Tk GUI, make sure to_pos > from_pos
        if from_pos > to_pos:
            from_pos,to_pos = to_pos,from_pos

        w.delete(from_pos,to_pos)
        c.frame.body.forceFullRecolor()
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.87: *4* deleteNextChar
    def deleteNextChar (self,event):

        '''Delete the character to the right of the cursor.'''

        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        i,j = w.getSelectionRange()
        self.beginCommand(undoType='delete-char')
        changed = True
        if i != j:
            w.delete(i,j)
            w.setInsertPoint(i)
        elif j < len(s):
            w.delete(i)
            w.setInsertPoint(i)
        else:
            changed = False
        self.endCommand(changed=changed,setLabel=False)
    #@+node:ekr.20050920084036.135: *4* deleteSpaces
    def deleteSpaces (self,event,insertspace=False):

        '''Delete all whitespace surrounding the cursor.'''

        w = self.editWidget(event)
        if not w: return
        # undoType = g.choose(insertspace,'insert-space','delete-spaces')
        undoType = 'insert-space' if insertspace else 'delete-spaces'
        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        w1 = ins-1
        while w1 >= i and s[w1].isspace():
            w1 -= 1
        w1 += 1
        w2 = ins
        while w2 <= j and s[w2].isspace():
            w2 += 1
        spaces = s[w1:w2]
        if spaces:
            self.beginCommand(undoType=undoType)
            if insertspace: s = s[:w1] + ' ' + s[w2:]
            else:           s = s[:w1] + s[w2:]
            w.setAllText(s)
            w.setInsertPoint(w1)
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20110528103005.18328: *4* insertHardTab
    def insertHardTab(self,event):

        '''Insert one hard tab.'''

        c = self.c
        w = self.editWidget(event)
        if not w: return
        assert g.app.gui.isTextWidget(w)
        name = c.widget_name(w)
        if name.startswith('head'): return
        ins = w.getInsertPoint()
        self.beginCommand(undoType='insert-hard-tab')
        w.insert(ins,'\t')
        ins += 1
        w.setSelectionRange(ins,ins,insert=ins)
        self.endCommand()
    #@+node:ekr.20050920084036.138: *4* insertNewLine
    def insertNewLine (self,event):

        '''Insert a newline at the cursor.'''

        c = self.c ; k = c.k ; w = self.editWidget(event)
        if not w: return

        assert g.app.gui.isTextWidget(w)
        name = c.widget_name(w)
        if name.startswith('head'): return

        oldSel = w.getSelectionRange()
        # g.trace('oldSel',oldSel)

        self.beginCommand(undoType='newline')

        # New in Leo 4.5: use the same logic as in selfInsertCommand.
        self.insertNewlineHelper(w=w,oldSel=oldSel,undoType=None)
        k.setInputState('insert')
        k.showStateAndMode()

        self.endCommand()

    insertNewline = insertNewLine
    #@+node:ekr.20050920084036.86: *4* insertNewLineAndTab
    def insertNewLineAndTab (self,event):

        '''Insert a newline and tab at the cursor.'''

        c = self.c ; k = c.k
        w = self.editWidget(event) ; p = c.p
        if not w: return

        assert g.app.gui.isTextWidget(w)
        name = c.widget_name(w)
        if name.startswith('head'): return

        self.beginCommand(undoType='insert-newline-and-indent')

        # New in Leo 4.5: use the same logic as in selfInsertCommand.
        oldSel = w.getSelectionRange()
        self.insertNewlineHelper(w=w,oldSel=oldSel,undoType=None)
        self.updateTab(p,w,smartTab=False)
        k.setInputState('insert')
        k.showStateAndMode()

        self.endCommand(changed=True,setLabel=False)
    #@+node:ekr.20050920084036.139: *4* insertParentheses
    def insertParentheses (self,event):

        '''Insert () at the cursor.'''

        w = self.editWidget(event)
        if not w: return

        self.beginCommand(undoType='insert-parenthesis')

        i = w.getInsertPoint()
        w.insert(i,'()')
        w.setInsertPoint(i+1)

        self.endCommand(changed=True,setLabel=False)
    #@+node:ekr.20110528103005.18329: *4* insertSoftTab
    def insertSoftTab (self,event):

        '''Insert spaces equivalent to one tab.'''

        c = self.c ; p = c.p
        w = self.editWidget(event) 
        if not w: return

        assert g.app.gui.isTextWidget(w)
        name = c.widget_name(w)
        if name.startswith('head'): return

        d = c.scanAllDirectives(p)
        n = abs(d.get("tabwidth",c.tab_width))
        ins = w.getInsertPoint()

        self.beginCommand(undoType='insert-soft-tab')

        w.insert(ins,' ' * n)
        ins += n
        w.setSelectionRange(ins,ins,insert=ins)

        self.endCommand()

    #@+node:ekr.20050920084036.141: *4* removeBlankLines
    def removeBlankLines (self,event):

        '''The remove-blank-lines command removes lines containing nothing but
        whitespace. If there is a text selection, only lines within the selected
        text are affected; otherwise all blank lines in the selected node are
        affected.'''

        c = self.c
        head,lines,tail,oldSel,oldYview = c.getBodyLines()

        changed = False ; result = []
        for line in lines:
            if line.strip():
                result.append(line)
            else:
                changed = True
        result = ''.join(result)

        if changed:
            oldSel = None ; undoType = 'remove-blank-lines'
            c.updateBodyPane(head,result,tail,undoType,oldSel,oldYview)
    #@+node:ekr.20110530082209.18248: *4* replaceCurrentCharacter
    def replaceCurrentCharacter (self,event):

        '''Replace the current character with the next character typed.'''

        k = self.k ; tag = 'replace-current-character'
        state = k.getState(tag)

        if state == 0:
            w = self.editWidget(event) # sets self.w
            if w:
                k.setLabelBlue('Replace Character: ',protect=True)
                k.getArg(event,tag,1,self.replaceCurrentCharacter)
        else:
            w = self.w
            ch = k.arg
            if ch:
                i,j = w.getSelectionRange()
                if i > j: i,j = j,i
                # Use raw insert/delete to retain the coloring.
                if i == j:
                    i = max(0,i-1)
                    w.delete(i)
                else:
                    w.delete(i,j)
                w.insert(i,ch)
                w.setInsertPoint(i+1)
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
    #@+node:ekr.20051125080855: *4* selfInsertCommand, helpers
    def selfInsertCommand(self,event,action='insert'):

        '''Insert a character in the body pane.
        This is the default binding for all keys in the body pane.'''

        trace = False and not g.unitTesting
        c,k = self.c,self.k
        verbose = True
        w = self.editWidget(event)
        if not w: return # (for Tk) 'break'
        #@+<< set local vars >>
        #@+node:ekr.20061103114242: *5* << set local vars >>
        p = c.p

        stroke = event and event.stroke or None
        ch = event and event.char or ''

        if ch == 'Return':
            ch = '\n' # This fixes the MacOS return bug.
        if ch == 'Tab':
            ch = '\t'

        name = c.widget_name(w)
        oldSel =  name.startswith('body') and w.getSelectionRange() or (None,None)
        oldText = name.startswith('body') and p.b or ''
        undoType = 'Typing'
        brackets = self.openBracketsList + self.closeBracketsList
        inBrackets = ch and g.toUnicode(ch) in brackets
        # if trace: g.trace(name,repr(ch),ch and ch in brackets)
        #@-<< set local vars >>
        assert g.isStrokeOrNone(stroke)

        if trace: g.trace('ch',repr(ch),'stroke',stroke)
        if g.doHook("bodykey1",c=c,p=p,v=p,ch=ch,oldSel=oldSel,undoType=undoType):
            return # (for Tk) "break" # The hook claims to have handled the event.
        if ch == '\t':
            self.updateTab(p,w)
        elif ch == '\b':
            # This is correct: we only come here if there no bindngs for this key. 
            self.backwardDeleteCharacter(event)
        elif ch in ('\r','\n'):
            ch = '\n'
            self.insertNewlineHelper(w,oldSel,undoType)
        elif inBrackets and self.autocompleteBrackets:
            self.updateAutomatchBracket(p,w,ch,oldSel)
        elif ch: # Null chars must not delete the selection.
            isPlain = stroke.find('Alt') == -1 and stroke.find('Ctrl') == -1
            i,j = oldSel
            if i > j: i,j = j,i
            # Use raw insert/delete to retain the coloring.
            if i != j:                  w.delete(i,j)
            elif action == 'overwrite': w.delete(i)
            if isPlain: # 2013/10/07: call insertKeyEvent for non-plain characters.
                w.insert(i,ch)
                w.setInsertPoint(i+1)
            else:
                g.app.gui.insertKeyEvent(event,i)
            if inBrackets and self.flashMatchingBrackets:
                self.flashMatchingBracketsHelper(w,i,ch)               
        else:
            return # (for Tk) 'break' # This method *always* returns 'break'

        # Set the column for up and down keys.
        spot = w.getInsertPoint()
        c.editCommands.setMoveCol(w,spot)

        # Update the text and handle undo.
        newText = w.getAllText()
        changed = newText != oldText
        if trace and verbose:
            g.trace('ch',repr(ch),'changed',changed,'newText',repr(newText[-10:]))
        if changed:
            # g.trace('ins',w.getInsertPoint())
            c.frame.body.onBodyChanged(undoType=undoType,
                oldSel=oldSel,oldText=oldText,oldYview=None)

        g.doHook("bodykey2",c=c,p=p,v=p,ch=ch,oldSel=oldSel,undoType=undoType)
        return # (for Tk) 'break'
    #@+node:ekr.20090213065933.14: *5* doPlainTab
    def doPlainTab(self,s,i,tab_width,w):

        '''Insert spaces equivalent to one tab.'''

        start,end = g.getLine(s,i)
        s2 = s[start:i]
        width = g.computeWidth(s2,tab_width)

        if tab_width > 0:
            w.insert(i,'\t')
            ins = i+1
        else:
            n = abs(tab_width) - (width % abs(tab_width))
            w.insert(i,' ' * n)
            ins = i+n

        w.setSelectionRange(ins,ins,insert=ins)
    #@+node:ekr.20060627091557: *5* flashCharacter (leoEditCommands)
    def flashCharacter(self,w,i):

        bg      = self.bracketsFlashBg or 'DodgerBlue1'
        fg      = self.bracketsFlashFg or 'white'
        flashes = self.bracketsFlashCount or 3
        delay   = self.bracketsFlashDelay or 75

        w.flashCharacter(i,bg,fg,flashes,delay)
    #@+node:ekr.20060627083506: *5* flashMatchingBracketsHelper
    def flashMatchingBracketsHelper (self,w,i,ch):

        d = {}
        if ch in self.openBracketsList:
            for z in range(len(self.openBracketsList)):
                d [self.openBracketsList[z]] = self.closeBracketsList[z]
            reverse = False # Search forward
        else:
            for z in range(len(self.openBracketsList)):
                d [self.closeBracketsList[z]] = self.openBracketsList[z]
            reverse = True # Search backward

        delim2 = d.get(ch)

        s = w.getAllText()
        j = g.skip_matching_python_delims(s,i,ch,delim2,reverse=reverse)
        if j != -1:
            self.flashCharacter(w,j)
    #@+node:ekr.20060804095512: *5* initBracketMatcher
    def initBracketMatcher (self,c):

        if len(self.openBracketsList) != len(self.closeBracketsList):

            g.es_print('bad open/close_flash_brackets setting: using defaults')
            self.openBracketsList  = '([{'
            self.closeBracketsList = ')]}'

        # g.trace('self.openBrackets',openBrackets)
        # g.trace('self.closeBrackets',closeBrackets)
    #@+node:ekr.20051026171121: *5* insertNewlineHelper
    def insertNewlineHelper (self,w,oldSel,undoType):

        trace = False and not g.unitTesting
        c = self.c ; p = c.p
        i,j = oldSel ; ch = '\n'
        if trace:
            s = w.widget.toPlainText()
            g.trace(i,j,len(s),w)

        if i != j:
            # No auto-indent if there is selected text.
            w.delete(i,j)
            w.insert(i,ch)
            w.setInsertPoint(i+1)
        else:
            w.insert(i,ch)
            w.setInsertPoint(i+1)

            if (c.autoindent_in_nocolor or 
                (c.frame.body.colorizer.useSyntaxColoring(p) and
                undoType != "Change")
            ):
                # No auto-indent if in @nocolor mode or after a Change command.
                self.updateAutoIndent(p,w)

        w.seeInsertPoint()
    #@+node:ekr.20051026171121.1: *5* updateAutoIndent (leoEditCommands)
    def updateAutoIndent (self,p,w):

        trace = False and not g.unitTesting
        c = self.c
        d = c.scanAllDirectives(p)
        tab_width = d.get("tabwidth",c.tab_width)
        # Get the previous line.
        s = w.getAllText()
        ins = w.getInsertPoint()
        i = g.skip_to_start_of_line(s,ins)
        i,j = g.getLine(s,i-1)
        s = s[i:j-1]

        # Add the leading whitespace to the present line.
        junk, width = g.skip_leading_ws_with_indent(s,0,tab_width)
        # g.trace('width',width,'tab_width',tab_width)

        if s and s [-1] == ':':
            # For Python: increase auto-indent after colons.
            if g.findLanguageDirectives(c,p) == 'python':
                width += abs(tab_width)

        if self.smartAutoIndent:
            # Determine if prev line has unclosed parens/brackets/braces
            bracketWidths = [width] ; tabex = 0
            for i in range(0,len(s)):
                if s [i] == '\t':
                    tabex += tab_width-1
                if s [i] in '([{':
                    bracketWidths.append(i+tabex+1)
                elif s [i] in '}])' and len(bracketWidths) > 1:
                    bracketWidths.pop()
            width = bracketWidths.pop()

        ws = g.computeLeadingWhitespace(width,tab_width)
        if ws:
            if trace: g.trace('width: %s, tab_width: %s, ws: %s' % (
                width,tab_width,repr(ws)))
            i = w.getInsertPoint()
            w.insert(i,ws)
            w.setInsertPoint(i+len(ws))
            w.seeInsertPoint()
                # 2011/10/02: Fix cursor-movement bug.
    #@+node:ekr.20051027172949: *5* updateAutomatchBracket
    def updateAutomatchBracket (self,p,w,ch,oldSel):

        # assert ch in ('(',')','[',']','{','}')

        c = self.c ; d = c.scanAllDirectives(p)
        i,j = oldSel
        language = d.get('language')
        s = w.getAllText()

        if ch in ('(','[','{',):
            automatch = language not in ('plain',)
            if automatch:
                ch = ch + {'(':')','[':']','{':'}'}.get(ch)
            if i != j: w.delete(i,j)
            w.insert(i,ch)
            if automatch:
                ins = w.getInsertPoint()
                w.setInsertPoint(ins-1)
        else:
            ins = w.getInsertPoint()
            ch2 = ins<len(s) and s[ins] or ''
            if ch2 in (')',']','}'):
                ins = w.getInsertPoint()
                w.setInsertPoint(ins+1)
            else:
                if i != j: w.delete(i,j)
                w.insert(i,ch)
                w.setInsertPoint(i+1)
    #@+node:ekr.20051026092433: *5* updateTab
    def updateTab (self,p,w,smartTab=True):

        trace = False and not g.unitTesting
        c = self.c

        # g.trace('tab_width',tab_width)
        i,j = w.getSelectionRange()
            # Returns insert point if no selection, with i <= j.

        if i != j:
            # w.delete(i,j)
            c.indentBody()
        else:
            d = c.scanAllDirectives(p)
            tab_width = d.get("tabwidth",c.tab_width)
            if trace: g.trace(tab_width)

            # Get the preceeding characters.
            s = w.getAllText()
            start,end = g.getLine(s,i)
            after = s[i:end]
            if after.endswith('\n'): after = after[:-1]

            # Only do smart tab at the start of a blank line.
            doSmartTab = (smartTab and c.smart_tab and i == start)
                # Truly at the start of the line.
                # and not after # Nothing *at all* after the cursor.

            if trace:
                g.trace('smartTab',doSmartTab,'tab_width',tab_width)
                    # 'i %s start %s after %s' % (i,start,repr(after)))

            if doSmartTab:
                self.updateAutoIndent(p,w)
                # Add a tab if otherwise nothing would happen.
                if s == w.getAllText():
                    self.doPlainTab(s,i,tab_width,w)
            else:
                self.doPlainTab(s,i,tab_width,w)
    #@+node:ekr.20050920084036.79: *3* info...
    #@+node:ekr.20050920084036.80: *4* howMany
    def howMany (self,event):

        '''Print how many occurances of a regular expression are found
        in the body text of the presently selected node.'''

        k = self.k
        w = self.editWidget(event)
        if not w: return

        state = k.getState('how-many')
        if state == 0:
            k.setLabelBlue('How many: ',protect = True)
            k.getArg(event,'how-many',1,self.howMany)
        else:
            k.clearState()
            s = w.getAllText()
            reg = re.compile(k.arg)
            i = reg.findall(s)
            k.setLabelGrey('%s occurances of %s' % (len(i),k.arg))
    #@+node:ekr.20050920084036.81: *4* lineNumber
    def lineNumber (self,event):

        '''Print the line and column number and percentage of insert point.'''

        k = self.k
        w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        i = w.getInsertPoint()
        row,col = g.convertPythonIndexToRowCol(s,i)
        percent = int((i*100)/len(s))

        k.setLabelGrey(
            'char: %s row: %d col: %d pos: %d (%d%% of %d)' % (
                repr(s[i]),row,col,i,percent,len(s)))
    #@+node:ekr.20050920084036.83: *4* k.viewLossage
    def viewLossage (self,event):

        '''Put the Emacs-lossage in the minibuffer label.'''

        k = self.k

        g.es('lossage...')
        aList = g.app.lossage
        aList.reverse()
        for data in aList:
            ch,stroke = data
            g.es('',k.prettyPrintKey(stroke))
    #@+node:ekr.20050920084036.84: *4* whatLine
    def whatLine (self,event):

        '''Print the line number of the line containing the cursor.'''

        k = self.k ; w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        i = w.getInsertPoint()
        row,col = g.convertPythonIndexToRowCol(s,i)

        k.keyboardQuit()
        k.setLabel("Line %s" % row)
    #@+node:ekr.20050920084036.88: *3* line...
    #@+node:ekr.20050920084036.90: *4* flushLines
    def flushLines (self,event):

        '''Delete each line that contains a match for regexp, operating on the text after point.

        In Transient Mark mode, if the region is active, the command operates on the region instead.'''

        k = self.k ; state = k.getState('flush-lines')

        if state == 0:
            k.setLabelBlue('Flush lines regexp: ',protect=True)
            k.getArg(event,'flush-lines',1,self.flushLines)
        else:
            k.clearState()
            k.resetLabel()
            self.linesHelper(event,k.arg,'flush')
            k.commandName = 'flush-lines %s' % k.arg
    #@+node:ekr.20051002095724: *4* keepLines
    def keepLines (self,event):

        '''Delete each line that does not contain a match for regexp, operating on the text after point.

        In Transient Mark mode, if the region is active, the command operates on the region instead.'''

        k = self.k ; state = k.getState('keep-lines')

        if state == 0:
            k.setLabelBlue('Keep lines regexp: ',protect=True)
            k.getArg(event,'keep-lines',1,self.keepLines)
        else:
            k.clearState()
            k.resetLabel()
            self.linesHelper(event,k.arg,'keep')
            k.commandName = 'keep-lines %s' % k.arg
    #@+node:ekr.20050920084036.92: *4* linesHelper
    def linesHelper (self,event,pattern,which):

        w = self.editWidget(event)
        if not w: return

        self.beginCommand(undoType=which+'-lines')
        if w.hasSelection():
            i,end = w.getSelectionRange()
        else:
            i = w.getInsertPoint()
            end = 'end'
        txt = w.get(i,end)
        tlines = txt.splitlines(True)
        if which == 'flush':    keeplines = list(tlines)
        else:                   keeplines = []

        try:
            regex = re.compile(pattern)
            for n, z in enumerate(tlines):
                f = regex.findall(z)
                if which == 'flush' and f:
                    keeplines [n] = None
                elif f:
                    keeplines.append(z)
        except Exception:
            return
        if which == 'flush':
            keeplines = [x for x in keeplines if x != None]
        w.delete(i,end)
        w.insert(i,''.join(keeplines))
        w.setInsertPoint(i)
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.77: *4* splitLine
    def splitLine (self,event):

        '''Split a line at the cursor position.'''

        w = self.editWidget(event)
        if not w: return

        self.beginCommand(undoType='split-line')

        s = w.getAllText()
        ins = w.getInsertPoint()
        w.setAllText(s[:ins] + '\n' + s[ins:])
        w.setInsertPoint(ins+1)

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050929114218: *3* move cursor... (leoEditCommands)
    #@+node:ekr.20051218170358: *4*  general helpers
    #@+node:ekr.20060113130510: *5* extendHelper
    def extendHelper (self,w,extend,spot,upOrDown=False):
        '''Handle the details of extending the selection.
        This method is called for all cursor moves.

        extend: Clear the selection unless this is True.
        spot:   The *new* insert point.
        '''

        trace = False and not g.unitTesting
        verbose = False
        c = self.c ; p = c.p
        extend = extend or self.extendMode

        ins = w.getInsertPoint()
        i,j = w.getSelectionRange()
        if trace: g.trace(
            'extend',extend,'ins',ins,'sel=',i,j,
            'spot=',spot,'moveSpot',self.moveSpot)

        # Reset the move spot if needed.
        if self.moveSpot is None or p.v != self.moveSpotNode:
            if trace: g.trace('no spot')
            self.setMoveCol(w,g.choose(extend,ins,spot)) # sets self.moveSpot.
        elif extend:
            # 2011/05/20: Fix bug 622819
            # Ctrl-Shift movement is incorrect when there is an unexpected selection.
            if i == j:
                if trace: g.trace('extend and no sel')
                self.setMoveCol(w,ins) # sets self.moveSpot.
            elif self.moveSpot in (i,j) and self.moveSpot != ins:
                if trace and verbose: g.trace('extend and movespot matches')
                # The bug fix, part 1.
            else:
                # The bug fix, part 2.
                # Set the moveCol to the *not* insert point.
                if ins == i: k = j
                elif ins == j: k = i
                else: k = ins
                if trace: g.trace('extend and unexpected spot',k)
                self.setMoveCol(w,k) # sets self.moveSpot.
        else:
            if upOrDown:
                s = w.getAllText()
                i2,j2 = g.getLine(s,spot)
                line = s[i2:j2]
                row,col = g.convertPythonIndexToRowCol(s,spot)
                if True: # was j2 < len(s)-1:
                    n = min(self.moveCol,max(0,len(line)-1))
                else:
                    n = min(self.moveCol,max(0,len(line))) # A tricky boundary.
                # g.trace('using moveCol',self.moveCol,'line',repr(line),'n',n)
                spot = g.convertRowColToPythonIndex(s,row,n)
            else:  # Plain move forward or back.
                # g.trace('plain forward/back move')
                self.setMoveCol(w,spot) # sets self.moveSpot.

        if extend:
            if trace: g.trace('range',spot,self.moveSpot)
            if spot < self.moveSpot:
                w.setSelectionRange(spot,self.moveSpot,insert=spot)
            else:
                w.setSelectionRange(self.moveSpot,spot,insert=spot)
        else:
            if trace: g.trace('insert point',spot)
            w.setSelectionRange(spot,spot,insert=spot)

        w.seeInsertPoint()
        c.frame.updateStatusLine()
    #@+node:ekr.20051218122116: *5* moveToHelper (leoEditCommands)
    def moveToHelper (self,event,spot,extend):

        '''Common helper method for commands the move the cursor
        in a way that can be described by a Tk Text expression.'''

        c = self.c ; k = c.k ; w = self.editWidget(event)
        if not w: return

        c.widgetWantsFocusNow(w)

        # Put the request in the proper range.
        if c.widget_name(w).startswith('mini'):
            i,j = k.getEditableTextRange()
            if   spot < i: spot = i
            elif spot > j: spot = j

        self.extendHelper(w,extend,spot,upOrDown=False)
    #@+node:ekr.20060209095101: *5* setMoveCol
    def setMoveCol (self,w,spot):

        '''Set the column to which an up or down arrow will attempt to move.'''

        c = self.c ; p = c.p

        i,row,col = w.toPythonIndexRowCol(spot)

        self.moveSpot = i
        self.moveCol = col
        self.moveSpotNode = p.v

        # g.trace('moveSpot',i)
    #@+node:ekr.20081123102100.1: *4* backToHome
    def backToHome (self,event):

        '''Smart home:
        Position the point at the first non-blank character on the line,
        or the start of the line if already there.'''

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        ins = w.getInsertPoint()
        if ins == 0 or not(s): return

        # Toggle back and forth between start of line and first-non-blank character.
        i,j = g.getLine(s,ins)
        i1 = i
        while i < j and s[i] in (' \t'):
            i += 1
        if i == ins:
            i = i1

        self.moveToHelper(event,i,extend=False)
    #@+node:ekr.20050920084036.75: *4* backToIndentation
    def backToIndentation (self,event):

        '''Position the point at the first non-blank character on the line.'''

        w = self.editWidget(event)
        if not w: return

        # None of the other cursor move commands are undoable.
        # self.beginCommand(undoType='back-to-indentation')

        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        while i < j and s[i] in (' \t'):
            i += 1

        self.moveToHelper(event,i,extend=False)

        # self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20051218141237: *4* between lines & helper
    def nextLine (self,event):
        '''Move the cursor down, extending the selection if in extend mode.'''
        self.moveUpOrDownHelper(event,'down',extend=False)

    def nextLineExtendSelection (self,event):
        '''Extend the selection by moving the cursor down.'''
        self.moveUpOrDownHelper(event,'down',extend=True)

    def prevLine (self,event):
        '''Move the cursor up, extending the selection if in extend mode.'''
        self.moveUpOrDownHelper(event,'up',extend=False)

    def prevLineExtendSelection (self,event):
        '''Extend the selection by moving the cursor up.'''
        self.moveUpOrDownHelper(event,'up',extend=True)
    #@+node:ekr.20060113105246.1: *5* moveUpOrDownHelper
    def moveUpOrDownHelper (self,event,direction,extend):

        trace = False and not g.unitTesting
        w = self.editWidget(event)
        if not w: return

        ins = w.getInsertPoint()
        s = w.getAllText()
        w.seeInsertPoint()

        if hasattr(w,'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=direction,extend=extend)
        else:
            # Find the start of the next/prev line.
            row,col = g.convertPythonIndexToRowCol(s,ins)
            if trace:
                gui_ins = w.toGuiIndex(ins)
                bbox = w.bbox(gui_ins)
                if bbox:
                    x,y,width,height = bbox
                    # bbox: x,y,width,height;  dlineinfo: x,y,width,height,offset
                    g.trace('gui_ins',gui_ins,'dlineinfo',w.dlineinfo(gui_ins),'bbox',bbox)
                    g.trace('ins',ins,'row',row,'col',col,
                        'event.x',event and event.x,'event.y',event and event.y)
                    g.trace('subtracting line height',w.index('@%s,%s' % (x,y-height)))
                    g.trace('adding      line height',w.index('@%s,%s' % (x,y+height)))
            i,j = g.getLine(s,ins)
            if direction == 'down':
                i2,j2 = g.getLine(s,j)
            else:
                i2,j2 = g.getLine(s,i-1)

            # The spot is the start of the line plus the column index.
            n = max(0,j2-i2-1) # The length of the new line.
            col2 = min(col,n)
            spot = i2 + col2
            if trace: g.trace('spot',spot,'n',n,'col',col,'line',repr(s[i2:j2]))

            self.extendHelper(w,extend,spot,upOrDown=True)
    #@+node:ekr.20050920084036.148: *4* buffers & helper
    def beginningOfBuffer (self,event):
        '''Move the cursor to the start of the body text.'''
        self.moveToBufferHelper(event,'home',extend=False)

    def beginningOfBufferExtendSelection (self,event):
        '''Extend the text selection by moving the cursor to the start of the body text.'''
        self.moveToBufferHelper(event,'home',extend=True)

    def endOfBuffer (self,event):
        '''Move the cursor to the end of the body text.'''
        self.moveToBufferHelper(event,'end',extend=False)

    def endOfBufferExtendSelection (self,event):
        '''Extend the text selection by moving the cursor to the end of the body text.'''
        self.moveToBufferHelper(event,'end',extend=True)
    #@+node:ekr.20100109094541.6227: *5* moveToBufferHelper
    def moveToBufferHelper (self,event,spot,extend):

        w = self.editWidget(event)
        if not w: return

        if hasattr(w,'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot,extend=extend)
        else:
            if spot == 'home':
                self.moveToHelper(event,0,extend=extend)
            elif spot == 'end':
                s = w.getAllText()
                self.moveToHelper(event,len(s),extend=extend)
            else:
                g.trace('can not happen: bad spot',spot)
    #@+node:ekr.20051213080533: *4* characters & helper
    def backCharacter (self,event):
        '''Move the cursor back one character, extending the selection if in extend mode.'''
        self.moveToCharacterHelper(event,'left',extend=False)

    def backCharacterExtendSelection (self,event):
        '''Extend the selection by moving the cursor back one character.'''
        self.moveToCharacterHelper(event,'left',extend=True)

    def forwardCharacter (self,event):
        '''Move the cursor forward one character, extending the selection if in extend mode.'''
        self.moveToCharacterHelper(event,'right',extend=False)

    def forwardCharacterExtendSelection (self,event):
        '''Extend the selection by moving the cursor forward one character.'''
        self.moveToCharacterHelper(event,'right',extend=True)
    #@+node:ekr.20100109094541.6228: *5* moveToCharacterHelper
    def moveToCharacterHelper (self,event,spot,extend):

        w = self.editWidget(event)
        if not w: return

        if hasattr(w,'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot,extend=extend)
        else:
            i = w.getInsertPoint()
            if spot == 'left':
                i=max(0,i-1)
                self.moveToHelper(event,i,extend=extend)
            elif spot == 'right':
                i = min(i+1,len(w.getAllText()))
                self.moveToHelper(event,i,extend=extend)
            else:
                g.trace('can not happen: bad spot: %s' % spot)
    #@+node:ekr.20051218174113: *4* clear/set/ToggleExtendMode
    def clearExtendMode (self,event):
        '''Turn off extend mode: cursor movement commands do not extend the selection.'''
        self.extendModeHelper(event,False)

    def setExtendMode (self,event):
        '''Turn on extend mode: cursor movement commands do extend the selection.'''
        self.extendModeHelper(event,True)

    def toggleExtendMode (self,event):
        '''Toggle extend mode, i.e., toggle whether cursor movement commands extend the selections.'''
        self.extendModeHelper(event,not self.extendMode)

    def extendModeHelper (self,event,val):

        c = self.c
        w = self.editWidget(event)
        if not w: return

        self.extendMode = val
        if not g.unitTesting:
            # g.red('extend mode',g.choose(val,'on','off'))
            c.k.showStateAndMode()
        c.widgetWantsFocusNow(w)
    #@+node:ekr.20050920084036.136: *4* exchangePointMark
    def exchangePointMark (self,event):

        '''Exchange the point (insert point) with the mark (the other end of the selected text).'''

        c = self.c
        w = self.editWidget(event)
        if not w: return

        if hasattr(w,'leoMoveCursorHelper'):
            w.leoMoveCursorHelper(kind='exchange',extend=False)
        else:
            c.widgetWantsFocusNow(w)
            i,j = w.getSelectionRange(sort=False)
            if i == j: return
            ins = w.getInsertPoint()
            ins = g.choose(ins==i,j,i)
            w.setInsertPoint(ins)
            w.setSelectionRange(i,j,insert=None)
    #@+node:ekr.20061007082956: *4* extend-to-line
    def extendToLine (self,event):

        '''Select the line at the cursor.'''

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText() ; n = len(s)
        i = w.getInsertPoint()

        while 0 <= i < n and not s[i] == '\n':
            i -= 1
        i += 1 ; i1 = i
        while 0 <= i < n and not s[i] == '\n':
            i += 1

        w.setSelectionRange(i1,i)
    #@+node:ekr.20061007214835.4: *4* extend-to-sentence
    def extendToSentence (self,event):

        '''Select the line at the cursor.'''

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText() ; n = len(s)
        i = w.getInsertPoint()

        i2 = 1 + s.find('.',i)
        if i2 == -1: i2 = n
        i1 = 1 + s.rfind('.',0,i2-1)

        w.setSelectionRange(i1,i2)
    #@+node:ekr.20060116074839.2: *4* extend-to-word
    def extendToWord (self,event,direction='forward',select=True):

        '''Compute the word at the cursor. Select it if select arg is True.'''

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText() ; n = len(s)
        i = w.getInsertPoint()

        if direction == 'forward':
            while i < n and not g.isWordChar(s[i]):
                i += 1
        else:
            while 0 <= i < n and not g.isWordChar(s[i]):
                i -= 1

        while 0 <= i < n and g.isWordChar(s[i]):
            i -= 1
        i += 1
        i1 = i

        # Move to the end of the word.
        while 0 <= i < n and g.isWordChar(s[i]):
            i += 1

        if select:
            w.setSelectionRange(i1,i)

        return i1,i
    #@+node:ekr.20050920084036.140: *4* movePastClose & helper
    def movePastClose (self,event):
        '''Move the cursor past the closing parenthesis.'''
        self.movePastCloseHelper(event,extend=False)

    def movePastCloseExtendSelection (self,event):
        '''Extend the selection by moving the cursor past the closing parenthesis.'''
        self.movePastCloseHelper(event,extend=True)
    #@+node:ekr.20051218171457: *5* movePastCloseHelper
    def movePastCloseHelper (self,event,extend):

        c = self.c ; w = self.editWidget(event)
        if not w: return

        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        ins = w.getInsertPoint()
        # Scan backwards for i,j.
        i = ins
        while i >= 0 and s[i] != '\n':
            if s[i] == '(': break
            i -= 1
        else: return
        j = ins
        while j >= 0 and s[j] != '\n':
            if s[j] == '(': break
            j -= 1
        if i < j: return
        # Scan forward for i2,j2.
        i2 = ins
        while i2 < len(s) and s[i2] != '\n':
            if s[i2] == ')': break
            i2 += 1
        else: return
        j2 = ins
        while j2 < len(s) and s[j2] != '\n':
            if s[j2] == ')': break
            j2 += 1
        if i2 > j2: return

        self.moveToHelper(event,i2+1,extend)
    #@+node:ekr.20100109094541.6231: *4* moveWithinLineHelper
    def moveWithinLineHelper (self,event,spot,extend):

        w = self.editWidget(event)
        if not w: return

        # Bug fix: 2012/02/28: don't use the Qt end-line logic:
        # it apparently does not work for wrapped lines.
        if hasattr(w,'leoMoveCursorHelper') and spot != 'end-line':
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(kind=spot,extend=extend)
        else:
            s = w.getAllText()
            ins = w.getInsertPoint()
            i,j = g.getLine(s,ins)
            if spot == 'start-line':
                self.moveToHelper(event,i,extend=extend)
            elif spot == 'end-line':
                # Bug fix: 2011/11/13: Significant in external tests.
                if g.match(s,j-1,'\n'): j -= 1
                self.moveToHelper(event,j,extend=extend)
            else:
                g.trace('can not happen: bad spot: %s' % spot)
    #@+node:ekr.20090530181848.6034: *4* pages & helper
    def backPage (self,event):
        '''Move the cursor back one page,
        extending the selection if in extend mode.'''
        self.movePageHelper(event,kind='back',extend=False)

    def backPageExtendSelection (self,event):
        '''Extend the selection by moving the cursor back one page.'''
        self.movePageHelper(event,kind='back',extend=True)

    def forwardPage (self,event):
        '''Move the cursor forward one page,
        extending the selection if in extend mode.'''
        self.movePageHelper(event,kind='forward',extend=False)

    def forwardPageExtendSelection (self,event):
        '''Extend the selection by moving the cursor forward one page.'''
        self.movePageHelper(event,kind='forward',extend=True)
    #@+node:ekr.20090530181848.6035: *5* movePageHelper
    def movePageHelper(self,event,kind,extend): # kind in back/forward.

        '''Move the cursor up/down one page, possibly extending the selection.'''

        trace = False and not g.unitTesting
        w = self.editWidget(event)
        if not w: return

        linesPerPage = 15 # To do.
        if hasattr(w,'leoMoveCursorHelper'):
            extend = extend or self.extendMode
            w.leoMoveCursorHelper(
                kind=g.choose(kind=='forward','page-down','page-up'),
                extend=extend,linesPerPage=linesPerPage)
            # w.seeInsertPoint()
            # c.frame.updateStatusLine()
            # w.rememberSelectionAndScroll()
        else:
            ins = w.getInsertPoint()
            s = w.getAllText()
            lines = g.splitLines(s)
            row,col = g.convertPythonIndexToRowCol(s,ins)
            row2 = g.choose(kind=='back',
                max(0,row-linesPerPage),
                min(row+linesPerPage,len(lines)-1))
            if row == row2: return
            spot = g.convertRowColToPythonIndex(s,row2,col,lines=lines)
            if trace: g.trace('spot',spot,'row2',row2)
            self.extendHelper(w,extend,spot,upOrDown=True)
    #@+node:ekr.20050920084036.102: *4* paragraphs & helpers
    def backwardParagraph (self,event):
        '''Move the cursor to the previous paragraph.'''
        self.backwardParagraphHelper (event,extend=False)

    def backwardParagraphExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the previous paragraph.'''
        self.backwardParagraphHelper (event,extend=True)

    def forwardParagraph (self,event):
        '''Move the cursor to the next paragraph.'''
        self.forwardParagraphHelper(event,extend=False)

    def forwardParagraphExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the next paragraph.'''
        self.forwardParagraphHelper(event,extend=True)
    #@+node:ekr.20051218133207: *5* backwardParagraphHelper
    def backwardParagraphHelper (self,event,extend):

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        i,j = w.getSelectionRange()
        # A hack for wx gui: set the insertion point to the end of the selection range.
        if g.app.unitTesting:
            w.setInsertPoint(j)
        i,j = g.getLine(s,j)
        line = s[i:j]

        if line.strip():
            # Find the start of the present paragraph.
            while i > 0:
                i,j = g.getLine(s,i-1)
                line = s[i:j]
                if not line.strip(): break

        # Find the end of the previous paragraph.
        while i > 0:
            i,j = g.getLine(s,i-1)
            line = s[i:j]
            if line.strip():
                i = j-1 ; break

        self.moveToHelper(event,i,extend)
    #@+node:ekr.20051218133207.1: *5* forwardParagraphHelper
    def forwardParagraphHelper (self,event,extend):

        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        line = s[i:j]

        if line.strip(): # Skip past the present paragraph.
            self.selectParagraphHelper(w,i)
            i,j = w.getSelectionRange()
            j += 1

        # Skip to the next non-blank line.
        i = j
        while j < len(s):
            i,j = g.getLine(s,j)
            line = s[i:j]
            if line.strip(): break

        w.setInsertPoint(ins) # Restore the original insert point.
        self.moveToHelper(event,i,extend)
    #@+node:ekr.20061111223516: *4* selectAllText (leoEditCommands)
    def selectAllText (self,event):

        '''Select all text.'''

        c = self.c 
        w = self.editWidget(event)
        isTextWidget = w and g.app.gui.isTextWidget(w)
        if 0:
            wname = (w and c.widget_name(w)) or '<no widget>'
            g.trace(isTextWidget,wname,w)
        if w and isTextWidget:
            return w.selectAllText()
    #@+node:ekr.20050920084036.131: *4* sentences & helpers
    def backSentence (self,event):
        '''Move the cursor to the previous sentence.'''
        self.backSentenceHelper(event,extend=False)

    def backSentenceExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the previous sentence.'''
        self.backSentenceHelper(event,extend=True)

    def forwardSentence (self,event):
        '''Move the cursor to the next sentence.'''
        self.forwardSentenceHelper(event,extend=False)

    def forwardSentenceExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the next sentence.'''
        self.forwardSentenceHelper(event,extend=True)
    #@+node:ekr.20051213094517: *5* backSentenceHelper
    def backSentenceHelper (self,event,extend):

        c = self.c
        w = self.editWidget(event)
        if not w: return

        c.widgetWantsFocusNow(w)
        s = w.getAllText()
        ins = w.getInsertPoint()

        # Find the starting point of the scan.
        i = ins
        i -= 1 # Ensure some progress.
        if i < 0:
            return

        # Tricky.
        if s[i] == '.':
            i -= 1
        while i >= 0 and s[i] in ' \n':
            i -= 1
        if i >= ins:
            i -= 1
        if i >= len(s):
            i -= 1
        if i <= 0:
            return
        if s[i] == '.':
            i -= 1

        # Scan backwards to the end of the paragraph.
        # Stop at empty lines.
        # Skip periods within words.
        # Stop at sentences ending in non-periods.
        end = False
        while not end and i >= 0:
            progress = i
            if s[i] == '.':
                # Skip periods surrounded by letters/numbers
                if i > 0 and s[i-1].isalnum() and s[i+1].isalnum():
                    i -= 1
                else:
                    i += 1
                    while i < len(s) and s[i] in ' \n':
                        i += 1
                    i -= 1
                    break
            elif s[i] == '\n':
                j = i-1
                while j >= 0:
                    if s[j] == '\n':
                        # Don't include first newline.
                        end = True ; break # found blank line.
                    elif s[j] == ' ':
                        j -= 1
                    else:
                        i -= 1 ; break # no blank line found.
                else:
                    # No blank line found.
                    i -= 1
            else:
                i -= 1
            assert end or progress > i
        i += 1

        if i < ins:
            self.moveToHelper(event,i,extend)
    #@+node:ekr.20050920084036.137: *5* forwardSentenceHelper
    def forwardSentenceHelper (self,event,extend):

        c = self.c
        w = self.editWidget(event)
        if not w: return

        c.widgetWantsFocusNow(w)

        s = w.getAllText()
        ins = w.getInsertPoint()
        if ins >= len(s): return

        # Find the starting point of the scan.
        i = ins
        if i+1 < len(s) and s[i+1] == '.':
            i += 1
        if s[i] == '.':
            i += 1
        else:
            while i < len(s) and s[i] in ' \n':
                i += 1
            i -= 1
        if i <= ins:
            i += 1
        if i >= len(s):
            return

        # Scan forward to the end of the paragraph.
        # Stop at empty lines.
        # Skip periods within words.
        # Stop at sentences ending in non-periods.
        end = False
        while not end and i < len(s):
            progress = i
            if s[i] == '.':
                # Skip periods surrounded by letters/numbers
                if 0 < i < len(s) and s[i-1].isalnum() and s[i+1].isalnum():
                    i += 1
                else:
                    i += 1 ; break # Include the paragraph.
            elif s[i] == '\n':
                j = i+1
                while j < len(s):
                    if s[j] == '\n':
                        # Don't include first newline.
                        end = True ; break # found blank line.
                    elif s[j] == ' ':
                        j += 1
                    else:
                        i += 1 ; break # no blank line found.
                else:
                    # No blank line found.
                    i += 1
            else:
                i += 1
            assert end or progress < i

        i = min(i,len(s))
        if i > ins:
            self.moveToHelper(event,i,extend)
    #@+node:ekr.20100109094541.6232: *4* within lines
    def beginningOfLine (self,event):
        '''Move the cursor to the start of the line, extending the selection if in extend mode.'''
        self.moveWithinLineHelper(event,'start-line',extend=False)

    def beginningOfLineExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the start of the line.'''
        self.moveWithinLineHelper(event,'start-line',extend=True)

    def endOfLine (self,event):
        '''Move the cursor to the end of the line, extending the selection if in extend mode.'''
        self.moveWithinLineHelper(event,'end-line',extend=False)

    def endOfLineExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the end of the line.'''
        self.moveWithinLineHelper(event,'end-line',extend=True)
    #@+node:ekr.20050920084036.149: *4* words & helper
    def backwardWord (self,event):
        '''Move the cursor to the previous word.'''
        self.moveWordHelper(event,extend=False,forward=False)

    def backwardWordExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the previous word.'''
        self.moveWordHelper(event,extend=True,forward=False)

    def forwardEndWord (self,event): # New in Leo 4.4.2
        '''Move the cursor to the next word.'''
        self.moveWordHelper(event,extend=False,forward=True,end=True)

    def forwardEndWordExtendSelection (self,event): # New in Leo 4.4.2
        '''Extend the selection by moving the cursor to the next word.'''
        self.moveWordHelper(event,extend=True,forward=True,end=True)

    def forwardWord (self,event):
        '''Move the cursor to the next word.'''
        self.moveWordHelper(event,extend=False,forward=True)

    def forwardWordExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the end of the next word.'''
        self.moveWordHelper(event,extend=True,forward=True)

    def backwardWordSmart (self,event):
        '''Move the cursor to the beginning of the current or the end of the previous word.'''
        self.moveWordHelper(event,extend=False,forward=False,smart=True)

    def backwardWordSmartExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the beginning of the current
        or the end of the previous word.'''
        self.moveWordHelper(event,extend=True,forward=False,smart=True)

    def forwardWordSmart (self,event):
        '''Move the cursor to the end of the current or the beginning of the next word.'''
        self.moveWordHelper(event,extend=False,forward=True,smart=True)

    def forwardWordSmartExtendSelection (self,event):
        '''Extend the selection by moving the cursor to the end of the current
        or the beginning of the next word.'''
        self.moveWordHelper(event,extend=True,forward=True,smart=True)
    #@+node:ekr.20051218121447: *5* moveWordHelper
    def moveWordHelper (self,event,extend,forward,end=False,smart=False):

        '''Move the cursor to the next/previous word.
        The cursor is placed at the start of the word unless end=True'''

        c = self.c
        w = self.editWidget(event)
        if not w: return

        c.widgetWantsFocusNow(w)
        s = w.getAllText() ; n = len(s)
        i = w.getInsertPoint()

        alphanumeric_re = re.compile("\w")
        whitespace_re = re.compile("\s")
        simple_whitespace_re = re.compile("[ \t]")

        def is_alphanumeric(c):
            return alphanumeric_re.match(c) is not None
        def is_whitespace(c):
            return whitespace_re.match(c) is not None
        def is_simple_whitespace(c):
            return simple_whitespace_re.match(c) is not None
        def is_line_break(c):
            return is_whitespace(c) and not is_simple_whitespace(c)
        def is_special(c):
            return not is_alphanumeric(c) and not is_whitespace(c)

        def seek_until_changed(i, match_function, step):
            while 0 <= i < n and match_function(s[i]):
                i += step
            return i

        def seek_word_end(i): return seek_until_changed(i,is_alphanumeric,1)
        def seek_word_start(i): return seek_until_changed(i,is_alphanumeric,-1)

        def seek_simple_whitespace_end(i): return seek_until_changed(i,is_simple_whitespace,1)
        def seek_simple_whitespace_start(i): return seek_until_changed(i,is_simple_whitespace,-1)

        def seek_special_end(i): return seek_until_changed(i,is_special,1)
        def seek_special_start(i): return seek_until_changed(i,is_special,-1)

        if smart:
            if forward:
                if 0 <= i < n:
                    if is_alphanumeric(s[i]):
                        i = seek_word_end(i)
                        i = seek_simple_whitespace_end(i)
                    elif is_simple_whitespace(s[i]):
                        i = seek_simple_whitespace_end(i)
                    elif is_special(s[i]):
                        i = seek_special_end(i)
                        i = seek_simple_whitespace_end(i)
                    else:
                        i += 1  # e.g. for newlines
            else:
                i -= 1  # Shift cursor temporarily by -1 to get easy read access to the prev. char
                if 0 <= i < n:
                    if is_alphanumeric(s[i]):
                        i = seek_word_start(i)
                        # Do not seek further whitespace here
                    elif is_simple_whitespace(s[i]):
                        i = seek_simple_whitespace_start(i)
                    elif is_special(s[i]):
                        i = seek_special_start(i)
                        # Do not seek further whitespace here
                    else:
                        i -= 1  # e.g. for newlines
                i += 1
        else:
            if forward:
                # Unlike backward-word moves, there are two options...
                if end:
                    while 0 <= i < n and not g.isWordChar(s[i]):
                        i += 1
                    while 0 <= i < n and g.isWordChar(s[i]):
                        i += 1
                else:
                    while 0 <= i < n and g.isWordChar(s[i]):
                        i += 1
                    while 0 <= i < n and not g.isWordChar(s[i]):
                        i += 1
            else:
                i -= 1
                while 0 <= i < n and not g.isWordChar(s[i]):
                    i -= 1
                while 0 <= i < n and g.isWordChar(s[i]):
                    i -= 1

        self.moveToHelper(event,i,extend)
    #@+node:ekr.20050920084036.95: *3* paragraph...
    #@+others
    #@+node:ekr.20050920084036.99: *4* backwardKillParagraph
    def backwardKillParagraph (self,event):

        '''Kill the previous paragraph.'''

        k = self.k ; c = k.c ; w = self.editWidget(event)
        if not w: return

        self.beginCommand(undoType='backward-kill-paragraph')
        try:
            self.backwardParagraphHelper(event,extend=True)
            i,j = w.getSelectionRange()
            if i > 0: i = min(i+1,j)
            c.killBufferCommands.kill(event,i,j,undoType=None)
            w.setSelectionRange(i,i,insert=i)
        finally:
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.100: *4* fillRegion (can hang)
    def fillRegion (self,event):

        '''Fill all paragraphs in the selected text.'''

        # New in Leo 4.4.4: just use reformat-paragraph logic.

        c = self.c ; p = c.p ; undoType = 'fill-region'
        w = self.editWidget(event)
        i,j = w.getSelectionRange()
        c.undoer.beforeChangeGroup(p,undoType)
        while 1:
            progress = w.getInsertPoint()
            c.reformatParagraph(event,undoType='reformat-paragraph')
            ins = w.getInsertPoint()
            s = w.getAllText()
            if progress >= ins or ins >= j or ins >= len(s):
                break
        c.undoer.afterChangeGroup(p,undoType)
    #@+node:ekr.20050920084036.104: *4* fillRegionAsParagraph
    def fillRegionAsParagraph (self,event):

        '''Fill the selected text.'''

        w = self.editWidget(event)
        if not w or not self._chckSel(event): return

        self.beginCommand(undoType='fill-region-as-paragraph')

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.103: *4* fillParagraph
    def fillParagraph( self, event ):

        '''Fill the selected paragraph'''

        w = self.editWidget(event)
        if not w: return

        # Clear the selection range.
        i,j = w.getSelectionRange()
        w.setSelectionRange(i,i,insert=i)

        self.c.reformatParagraph(event)
    #@+node:ekr.20050920084036.98: *4* killParagraph
    def killParagraph (self,event):

        '''Kill the present paragraph.'''

        k = self.k ; c = k.c ; w = self.editWidget(event)
        if not w: return

        self.beginCommand(undoType='kill-paragraph')
        try:
            self.extendToParagraph(event)
            i,j = w.getSelectionRange()
            c.killBufferCommands.kill(event,i,j,undoType=None)
            w.setSelectionRange(i,i,insert=i)
        finally:
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.96: *4* extend-to-paragraph & helper
    def extendToParagraph (self,event):

        '''Select the paragraph surrounding the cursor.'''

        w = self.editWidget(event)
        if not w: return
        s = w.getAllText() ; ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        line = s[i:j]

        # Find the start of the paragraph.
        if line.strip(): # Search backward.
            while i > 0:
                i2,j2 = g.getLine(s,i-1)
                line = s[i2:j2]
                if line.strip(): i = i2
                else: break # Use the previous line.
        else: # Search forward.
            while j < len(s):
                i,j = g.getLine(s,j)
                line = s[i:j]
                if line.strip(): break
            else: return

        # Select from i to the end of the paragraph.
        self.selectParagraphHelper(w,i)
    #@+node:ekr.20050920084036.97: *5* selectParagraphHelper
    def selectParagraphHelper (self,w,start):

        '''Select from start to the end of the paragraph.'''

        s = w.getAllText()
        i1,j = g.getLine(s,start)
        while j < len(s):
            i,j2 = g.getLine(s,j)
            line = s[i:j2]
            if line.strip(): j = j2
            else: break

        j = max(start,j-1)
        w.setSelectionRange(i1,j,insert=j)
    #@-others
    #@+node:ekr.20050920084036.105: *3* region...
    #@+others
    #@+node:ekr.20050920084036.108: *4* tabIndentRegion (indent-rigidly)
    def tabIndentRegion (self,event):

        '''Insert a hard tab at the start of each line of the selected text.'''

        w = self.editWidget(event)
        if not w or not self._chckSel(event): return

        self.beginCommand(undoType='indent-rigidly')

        s = w.getAllText()
        i1,j1 = w.getSelectionRange()
        i,junk = g.getLine(s,i1)
        junk,j = g.getLine(s,j1)

        lines = g.splitlines(s[i:j])
        n = len(lines)
        lines = g.joinLines(['\t' + line for line in lines])
        s = s[:i] + lines + s[j:]
        w.setAllText(s)

        # Retain original row/col selection.
        w.setSelectionRange(i1,j1+n,insert=j1+n)

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.109: *4* countRegion
    def countRegion (self,event):

        '''Print the number of lines and characters in the selected text.'''

        k = self.k
        w = self.editWidget(event)
        if not w: return

        txt = w.getSelectedText()
        lines = 1 ; chars = 0
        for z in txt:
            if z == '\n': lines += 1
            else:         chars += 1

        k.setLabelGrey('Region has %s lines, %s character%s' % (
            lines,chars,g.choose(chars==1,'','s')))
    #@+node:ekr.20060417183606: *4* moveLinesDown
    def moveLinesDown (self,event):

        '''Move all lines containing any selected text down one line,
        moving to the next node if the lines are the last lines of the body.'''

        c = self.c ; w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        sel_1,sel_2 = w.getSelectionRange()
        insert_pt = w.getInsertPoint() # 2011/04/01
        i,junk = g.getLine(s,sel_1)
        i2,j   = g.getLine(s,sel_2)
        lines  = s[i:j]

        # Select from start of the first line to the *start* of the last line.
        # This prevents selection creep.
        # n = i2-i
        # g.trace('moveLinesDown:',repr('%s[[%s|%s|%s]]%s' % (
        #    s[i-20:i], s[i:sel_1], s[sel_1:sel_2], s[sel_2:j], s[j:j+20])))
        self.beginCommand(undoType='move-lines-down')
        changed = False
        try:
            if j < len(s):
                next_i,next_j = g.getLine(s,j) # 2011/04/01: was j+1
                next_line = s[next_i:next_j]
                n2 = next_j-next_i
                w.delete(i,next_j)
                if next_line.endswith('\n'):
                    # Simply swap positions with next line
                    new_lines = next_line+lines
                else:
                    # Last line of the body to be moved up doesn't end in a newline
                    # while we have to remove the newline from the line above moving down.
                    new_lines = next_line+'\n'+lines[:-1]
                    n2 += 1
                w.insert(i,new_lines)
                w.setSelectionRange(sel_1+n2,sel_2+n2,insert=insert_pt+n2)
                changed = True
                # Fix bug 799695: colorizer bug after move-lines-up into a docstring
                c.recolor_now(incremental=False)
        finally:
            self.endCommand(changed=changed,setLabel=True)
    #@+node:ekr.20060417183606.1: *4* moveLinesUp
    def moveLinesUp (self,event):

        '''Move all lines containing any selected text up one line,
        moving to the previous node as needed.'''

        c = self.c ; w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        sel_1,sel_2 = w.getSelectionRange()
        insert_pt = w.getInsertPoint() # 2011/04/01     
        i,junk = g.getLine(s,sel_1)
        i2,j   = g.getLine(s,sel_2)
        lines  = s[i:j]
        # g.trace('moveLinesUp:',repr('%s[[%s|%s|%s]]%s' % (
        #    s[max(0,i-20):i], s[i:sel_1], s[sel_1:sel_2], s[sel_2:j], s[j:j+20])))
        self.beginCommand(undoType='move-lines-up')
        changed = False
        try:
            if i>0:
                prev_i,prev_j = g.getLine(s,i-1)
                prev_line = s[prev_i:prev_j]
                n2 = prev_j - prev_i
                w.delete(prev_i,j)
                if lines.endswith('\n'):
                    # Simply swap positions with next line
                    new_lines = lines+prev_line
                else:
                    # Lines to be moved up don't end in a newline while the
                    # previous line going down needs its newline taken off.
                    new_lines = lines+'\n'+prev_line[:-1]
                w.insert(prev_i,new_lines)
                w.setSelectionRange(sel_1-n2,sel_2-n2,insert=insert_pt-n2)
                changed = True
                # Fix bug 799695: colorizer bug after move-lines-up into a docstring
                c.recolor_now(incremental=False)
        finally:
            self.endCommand(changed=changed,setLabel=True)
    #@+node:ekr.20050920084036.110: *4* reverseRegion
    def reverseRegion (self,event):

        '''Reverse the order of lines in the selected text.'''

        w = self.editWidget(event)
        if not w or not self._chckSel(event): return

        self.beginCommand(undoType='reverse-region')

        s = w.getAllText()
        i1,j1 = w.getSelectionRange()
        i,junk = g.getLine(s,i1)
        junk,j = g.getLine(s,j1)

        txt = s[i:j]
        aList = txt.split('\n')
        aList.reverse()
        txt = '\n'.join(aList) + '\n'

        w.setAllText(s[:i1] + txt + s[j1:])
        ins = i1 + len(txt) - 1
        w.setSelectionRange(ins,ins,insert=ins)

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.111: *4* up/downCaseRegion & helper
    def downCaseRegion (self,event):
        '''Convert all characters in the selected text to lower case.'''
        self.caseHelper(event,'low','downcase-region')

    def toggleCaseRegion (self,event):
        '''Toggle the case of all characters in the selected text.'''
        self.caseHelper(event,'toggle','toggle-case-region')

    def upCaseRegion (self,event):
        '''Convert all characters in the selected text to UPPER CASE.'''
        self.caseHelper(event,'up','upcase-region')

    def caseHelper (self,event,way,undoType):

        w = self.editWidget(event)
        if not w or not w.hasSelection(): return

        self.beginCommand(undoType=undoType)

        s = w.getAllText()
        i,j = w.getSelectionRange()
        ins = w.getInsertPoint()

        # sel = g.choose(way=='low',s[i:j].lower(),s[i:j].upper())
        s2 = s[i:j]
        if way == 'low':
            sel = s2.lower()
        elif way == 'up':
            sel = s2.upper()
        else:
            assert way == 'toggle'
            sel = s2.swapcase()

        s2 = s[:i] + sel + s[j:]
        # g.trace('sel',repr(sel),'s2',repr(s2))
        changed = s2 != s
        if changed:
            w.setAllText(s2)
            w.setSelectionRange(i,j,insert=ins)

        self.endCommand(changed=changed,setLabel=True)
    #@-others
    #@+node:ekr.20060309060654: *3* scrolling...
    #@+node:ekr.20050920084036.116: *4* scrollUp/Down & helper
    def scrollDownHalfPage (self,event):
        '''Scroll the presently selected pane down one lline.'''
        self.scrollHelper(event,'down','half-page')

    def scrollDownLine (self,event):
        '''Scroll the presently selected pane down one lline.'''
        self.scrollHelper(event,'down','line')

    def scrollDownPage (self,event):
        '''Scroll the presently selected pane down one page.'''
        self.scrollHelper(event,'down','page')

    def scrollUpHalfPage (self,event):
        '''Scroll the presently selected pane down one lline.'''
        self.scrollHelper(event,'up','half-page')

    def scrollUpLine (self,event):
        '''Scroll the presently selected pane up one page.'''
        self.scrollHelper(event,'up','line')

    def scrollUpPage (self,event):
        '''Scroll the presently selected pane up one page.'''
        self.scrollHelper(event,'up','page')
    #@+node:ekr.20060113082917: *5* scrollHelper (leoEditCommands)
    def scrollHelper (self,event,direction,distance):

        '''Scroll the present pane up or down one page
        kind is in ('up/down-half-page/line/page)'''

        w = event and event.w
        if w and hasattr(w,'scrollDelegate'):
            kind = direction + '-' + distance
            w.scrollDelegate(kind)
    #@+node:ekr.20060309060654.1: *4* scrollOutlineUp/Down/Line/Page
    def scrollOutlineDownLine (self,event=None):
        '''Scroll the outline pane down one line.'''
        c = self.c ; tree = c.frame.tree
        if hasattr(tree,'scrollDelegate'):
            tree.scrollDelegate('down-line')
        elif hasattr(tree.canvas,'leo_treeBar'):
            a,b = tree.canvas.leo_treeBar.get()
            if b < 1.0: tree.canvas.yview_scroll(1,"unit")

    def scrollOutlineDownPage (self,event=None):
        '''Scroll the outline pane down one page.'''
        c = self.c ; tree = c.frame.tree
        if hasattr(tree,'scrollDelegate'):
            tree.scrollDelegate('down-page')
        elif hasattr(tree.canvas,'leo_treeBar'):
            a,b = tree.canvas.leo_treeBar.get()
            if b < 1.0: tree.canvas.yview_scroll(1,"page")

    def scrollOutlineUpLine (self,event=None):
        '''Scroll the outline pane up one line.'''
        c = self.c ; tree = c.frame.tree
        if hasattr(tree,'scrollDelegate'):
            tree.scrollDelegate('up-line')
        elif hasattr(tree.canvas,'leo_treeBar'):
            a,b = tree.canvas.leo_treeBar.get()
            if a > 0.0: tree.canvas.yview_scroll(-1,"unit")

    def scrollOutlineUpPage (self,event=None):
        '''Scroll the outline pane up one page.'''
        c = self.c ; tree = c.frame.tree
        if hasattr(tree,'scrollDelegate'):
            tree.scrollDelegate('up-page')
        elif hasattr(tree.canvas,'leo_treeBar'):
            a,b = tree.canvas.leo_treeBar.get()
            if a > 0.0: tree.canvas.yview_scroll(-1,"page")
    #@+node:ekr.20060726154531: *4* scrollOutlineLeftRight
    def scrollOutlineLeft (self,event=None):
        '''Scroll the outline left.'''
        c = self.c ; tree = c.frame.tree
        if hasattr(tree,'scrollDelegate'):
            tree.scrollDelegate('left')
        elif hasattr(tree.canvas,'xview_scroll'):
            tree.canvas.xview_scroll(1,"unit")

    def scrollOutlineRight (self,event=None):
        '''Scroll the outline left.'''
        c = self.c ; tree = c.frame.tree
        if hasattr(tree,'scrollDelegate'):
            tree.scrollDelegate('right')
        elif hasattr(tree.canvas,'xview_scroll'):
            tree.canvas.xview_scroll(-1,"unit")
    #@+node:ekr.20050920084036.117: *3* sort...
    #@@nocolor
    #@@color
    #@+at
    # XEmacs provides several commands for sorting text in a buffer.  All
    # operate on the contents of the region (the text between point and the
    # mark).  They divide the text of the region into many "sort records",
    # identify a "sort key" for each record, and then reorder the records
    # using the order determined by the sort keys.  The records are ordered so
    # that their keys are in alphabetical order, or, for numerical sorting, in
    # numerical order.  In alphabetical sorting, all upper-case letters `A'
    # through `Z' come before lower-case `a', in accordance with the ASCII
    # character sequence.
    # 
    #    The sort commands differ in how they divide the text into sort
    # records and in which part of each record they use as the sort key.
    # Most of the commands make each line a separate sort record, but some
    # commands use paragraphs or pages as sort records.  Most of the sort
    # commands use each entire sort record as its own sort key, but some use
    # only a portion of the record as the sort key.
    # 
    # `M-x sort-lines'
    #      Divide the region into lines and sort by comparing the entire text
    #      of a line.  A prefix argument means sort in descending order.
    # 
    # `M-x sort-paragraphs'
    #      Divide the region into paragraphs and sort by comparing the entire
    #      text of a paragraph (except for leading blank lines).  A prefix
    #      argument means sort in descending order.
    # 
    # `M-x sort-pages'
    #      Divide the region into pages and sort by comparing the entire text
    #      of a page (except for leading blank lines).  A prefix argument
    #      means sort in descending order.
    # 
    # `M-x sort-fields'
    #      Divide the region into lines and sort by comparing the contents of
    #      one field in each line.  Fields are defined as separated by
    #      whitespace, so the first run of consecutive non-whitespace
    #      characters in a line constitutes field 1, the second such run
    #      constitutes field 2, etc.
    # 
    #      You specify which field to sort by with a numeric argument: 1 to
    #      sort by field 1, etc.  A negative argument means sort in descending
    #      order.  Thus, minus 2 means sort by field 2 in reverse-alphabetical
    #      order.
    # 
    # `M-x sort-numeric-fields'
    #      Like `M-x sort-fields', except the specified field is converted to
    #      a number for each line and the numbers are compared.  `10' comes
    #      before `2' when considered as text, but after it when considered
    #      as a number.
    # 
    # `M-x sort-columns'
    #      Like `M-x sort-fields', except that the text within each line used
    #      for comparison comes from a fixed range of columns.  An explanation
    #      is given below.
    # 
    #    For example, if the buffer contains:
    # 
    #      On systems where clash detection (locking of files being edited) is
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      whether the file has changed on disk since it was last visited or
    #      saved.  If it has, you are asked to confirm that you want to change
    #      the buffer.
    # 
    # then if you apply `M-x sort-lines' to the entire buffer you get:
    # 
    #      On systems where clash detection (locking of files being edited) is
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      saved.  If it has, you are asked to confirm that you want to change
    #      the buffer.
    #      whether the file has changed on disk since it was last visited or
    # 
    # where the upper case `O' comes before all lower case letters.  If you
    # apply instead `C-u 2 M-x sort-fields' you get:
    # 
    #      saved.  If it has, you are asked to confirm that you want to change
    #      implemented, XEmacs also checks the first time you modify a buffer
    #      the buffer.
    #      On systems where clash detection (locking of files being edited) is
    #      whether the file has changed on disk since it was last visited or
    # 
    # where the sort keys were `If', `XEmacs', `buffer', `systems', and `the'.
    # 
    #    `M-x sort-columns' requires more explanation.  You specify the
    # columns by putting point at one of the columns and the mark at the other
    # column.  Because this means you cannot put point or the mark at the
    # beginning of the first line to sort, this command uses an unusual
    # definition of `region': all of the line point is in is considered part
    # of the region, and so is all of the line the mark is in.
    # 
    #    For example, to sort a table by information found in columns 10 to
    # 15, you could put the mark on column 10 in the first line of the table,
    # and point on column 15 in the last line of the table, and then use this
    # command.  Or you could put the mark on column 15 in the first line and
    # point on column 10 in the last line.
    # 
    #    This can be thought of as sorting the rectangle specified by point
    # and the mark, except that the text on each line to the left or right of
    # the rectangle moves along with the text inside the rectangle.  *Note
    # Rectangles::.
    # 
    #@+node:ekr.20050920084036.118: *4* sortLines commands
    def reverseSortLinesIgnoringCase(self,event):
        '''Sort the selected lines in reverse order, ignoring case.'''
        return self.sortLines(event,ignoreCase=True,reverse=True)

    def reverseSortLines(self,event):
        '''Sort the selected lines in reverse order.'''
        return self.sortLines(event,reverse=True)

    def sortLinesIgnoringCase(self,event):
        '''Sort the selected lines, ignoring case.'''
        return self.sortLines(event,ignoreCase=True)

    def sortLines (self,event,ignoreCase=False,reverse=False):
        '''Sort the selected lines.'''
        w = self.editWidget(event)
        if not self._chckSel(event): return

        undoType = g.choose(reverse,'reverse-sort-lines','sort-lines')
        self.beginCommand(undoType=undoType)
        try:
            s = w.getAllText()
            sel_1,sel_2 = w.getSelectionRange()
            ins = w.getInsertPoint()
            i,junk = g.getLine(s,sel_1)
            junk,j = g.getLine(s,sel_2)
            s2 = s[i:j]
            if not s2.endswith('\n'): s2 = s2+'\n'
            aList = g.splitLines(s2)
            def lower(s):
                if ignoreCase: return s.lower()
                else: return s
            aList.sort(key=lower)
                # key is a function that extracts args.
            if reverse:
                aList.reverse()
            s = g.joinLines(aList)
            w.delete(i,j)
            w.insert(i,s)
            w.setSelectionRange(sel_1,sel_2,insert=ins)
        finally:
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.119: *4* sortColumns
    def sortColumns (self,event):

        '''Sort lines of selected text using only lines in the given columns to do the comparison.'''

        w = self.editWidget(event)
        if not self._chckSel(event): return
        self.beginCommand(undoType='sort-columns')
        try:
            s = w.getAllText()
            sel_1,sel_2 = w.getSelectionRange()
            sint1,sint2 = g.convertPythonIndexToRowCol(s,sel_1)
            sint3,sint4 = g.convertPythonIndexToRowCol(s,sel_2)
            sint1 += 1 ; sint3 += 1
            i,junk = g.getLine(s,sel_1)
            junk,j = g.getLine(s,sel_2)
            txt = s[i:j]
            columns = [w.get('%s.%s' % (z,sint2),'%s.%s' % (z,sint4))
                for z in range(sint1,sint3+1)]
            aList = g.splitLines(txt)
            zlist = list(zip(columns,aList))
            zlist.sort()
            s = g.joinLines([z[1] for z in zlist])
            w.delete(i,j)
            w.insert(i,s)
            w.setSelectionRange(sel_1,sel_1+len(s),insert=sel_1+len(s))
        finally:
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.120: *4* sortFields
    def sortFields (self,event,which=None):

        '''Divide the selected text into lines and sort by comparing the contents of
         one field in each line. Fields are defined as separated by whitespace, so
         the first run of consecutive non-whitespace characters in a line
         constitutes field 1, the second such run constitutes field 2, etc.

         You specify which field to sort by with a numeric argument: 1 to sort by
         field 1, etc. A negative argument means sort in descending order. Thus,
         minus 2 means sort by field 2 in reverse-alphabetical order.'''

        w = self.editWidget(event)
        if not w or not self._chckSel(event): return

        self.beginCommand(undoType='sort-fields')

        s = w.getAllText()
        ins = w.getInsertPoint()
        r1,r2,r3,r4 = self.getRectanglePoints(w)
        i,junk = g.getLine(s,r1)
        junk,j = g.getLine(s,r4)
        txt = s[i:j] # bug reported by pychecker.
        txt = txt.split('\n')
        fields = []
        fn = r'\w+'
        frx = re.compile(fn)
        for line in txt:
            f = frx.findall(line)
            if not which:
                fields.append(f[0])
            else:
                i = int(which)
                if len(f) < i: return
                i = i-1
                fields.append(f[i])
        nz = zip(fields,txt)
        nz.sort()
        w.delete(i,j)
        int1 = i
        for z in nz:
            w.insert('%s.0' % int1,'%s\n' % z[1])
            int1 = int1 + 1
        w.setInsertPoint(ins)

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.121: *3* swap/transpose...
    #@+node:ekr.20050920084036.122: *4* transposeLines
    def transposeLines (self,event):

        '''Transpose the line containing the cursor with the preceding line.'''

        w = self.editWidget(event)
        if not w: return

        ins = w.getInsertPoint()
        s = w.getAllText()
        if not s.strip(): return

        i,j = g.getLine(s,ins)
        line1 = s[i:j]

        self.beginCommand(undoType='transpose-lines')

        if i == 0: # Transpose the next line.
            i2,j2 = g.getLine(s,j+1)
            line2 = s[i2:j2]
            w.delete(0,j2)
            w.insert(0,line2+line1)
            w.setInsertPoint(j2-1)
        else: # Transpose the previous line.
            i2,j2 = g.getLine(s,i-1)
            line2 = s[i2:j2]
            w.delete(i2,j)
            w.insert(i2,line1+line2)
            w.setInsertPoint(j-1)

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20060529184652.1: *4* transposeWords
    def transposeWords (self,event):

        '''Transpose the word at the cursor with the preceding or following word.'''

        trace = False and not g.unitTesting
        w = self.editWidget(event)
        if not w: return

        self.beginCommand(undoType='transpose-words')

        s = w.getAllText()
        i1,j1 = self.extendToWord(event,direction='back',select=False)
        s1 = s[i1:j1]
        if trace: g.trace(i1,j1,s1)
        if i1 > j1: i1,j1 = j1,i1

        # First, search backward.
        k = i1-1
        while k >= 0 and s[k].isspace():
            k -= 1
        changed = k > 0
        if changed:
            ws = s[k+1:i1]
            if trace: g.trace(repr(ws))
            w.setInsertPoint(k+1)
            i2,j2 = self.extendToWord(event,direction='back',select=False)
            s2 = s[i2:j2]
            if trace: g.trace(i2,j2,repr(s2))
            s3 = s[:i2] + s1 + ws + s2 + s[j1:]
            w.setAllText(s3)
            if trace: g.trace(s3)
            w.setSelectionRange(j1,j1,insert=j1)
        else:
            # Next search forward.
            k = j1+1
            while k < len(s) and s[k].isspace():
                k += 1
            changed = k < len(s)
            if changed:
                ws = s[j1:k]
                if trace: g.trace(repr(ws))
                w.setInsertPoint(k+1)
                i2,j2 = self.extendToWord(event,direction='forward',select=False)
                s2 = s[i2:j2]
                if trace: g.trace(i2,j2,repr(s2))
                s3 = s[:i1] + s2 + ws + s1 + s[j2:]
                w.setAllText(s3)
                if trace: g.trace(s3)
                w.setSelectionRange(j1,j1,insert=j1)

        self.endCommand(changed=changed,setLabel=True)
    #@+node:ekr.20050920084036.124: *4* swapCharacters & transeposeCharacters
    def swapCharacters (self,event):

        '''Swap the characters at the cursor.'''

        w = self.editWidget(event)
        if not w: return

        self.beginCommand(undoType='swap-characters')
        s = w.getAllText()
        i = w.getInsertPoint()
        if 0 < i < len(s):
            w.setAllText(s[:i-1] + s[i] + s[i-1] + s[i+1:])
            w.setSelectionRange(i,i,insert=i)
        self.endCommand(changed=True,setLabel=True)

    transposeCharacters = swapCharacters
    #@+node:ekr.20050920084036.126: *3* tabify & untabify
    def tabify (self,event):
        '''Convert 4 spaces to tabs in the selected text.'''
        self.tabifyHelper (event,which='tabify')

    def untabify (self,event):
        '''Convert tabs to 4 spaces in the selected text.'''
        self.tabifyHelper (event,which='untabify')

    def tabifyHelper (self,event,which):

        w = self.editWidget(event)
        if not w or not w.hasSelection(): return

        self.beginCommand(undoType=which)
        i,end = w.getSelectionRange()
        txt = w.getSelectedText()
        if which == 'tabify':
            pattern = re.compile(' {4,4}') # Huh?
            ntxt = pattern.sub('\t',txt)
        else:
            pattern = re.compile('\t')
            ntxt = pattern.sub('    ',txt)
        w.delete(i,end)
        w.insert(i,ntxt)
        n = i + len(ntxt)
        w.setSelectionRange(n,n,insert=n)
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20110527105255.18384: *3* uA's (leoEditCommands)
    #@+node:ekr.20110527105255.18387: *4* clearNodeUas & clearAllUas
    def clearNodeUas (self,event=None):

        '''Clear the uA's in the selected vnode.'''

        if self.c.p:
            self.c.p.v.u = {}

    def clearAllUas (self,event=None):

        '''Clear all uAs in the entire outline.'''

        for v in self.c.all_unique_nodes():
            v.u = {}
    #@+node:ekr.20110527105255.18385: *4* printUas & printAllUas
    def printAllUas (self,event=None):

        '''Print all uA's in the outline.'''

        g.es_print('Dump of uAs...')
        for v in self.c.all_unique_nodes():
            if v.u:
                self.printUas(v=v)

    def printUas (self,event=None,v=None):

        '''Print the uA's in the selected node.'''

        c = self.c
        if v: d,h = v.u,v.h
        else: d,h = c.p.v.u,c.p.h
        g.es_print(h)
        keys = list(d.keys())
        keys.sort()
        n = 4
        for key in keys:
            n = max(len(key),n)
        for key in keys:
            pad = ' '*(len(key)-n)
            g.es_print('    %s%s: %s' % (pad,key,d.get(key)))
    #@+node:ekr.20110527105255.18386: *4* setUa
    def setUa (self,event):

        '''Prompt for the name and value of a uA, then set the uA in the present node.'''

        c,k = self.c,self.k
        tag = 'set-ua' ; state = k.getState(tag)
        if state == 0:
            w = self.editWidget(event) # sets self.w
            if w:
                k.setLabelBlue('Set uA: ',protect=True)
                k.getArg(event,tag,1,self.setUa)
        elif state == 1:
            self.uaName = k.arg
            s = 'Set uA: %s To: ' % (self.uaName)
            k.setLabelBlue(s,protect=True)
            k.getArg(event,tag,2,self.setUa,completion=False,prefix=s)
        else:
            assert state == 2,state
            val = k.arg
            d = c.p.v.u
            d[self.uaName] = val
            self.printUas()
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
    #@-others
#@+node:ekr.20050920084036.161: ** editFileCommandsClass
class editFileCommandsClass (baseEditCommandsClass):

    '''A class to load files into buffers and save buffers to files.'''

    #@+others
    #@+node:ekr.20050920084036.162: *3*  ctor (editFileCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.
    #@+node:ekr.20050920084036.163: *3*  getPublicCommands (editFileCommandsClass)
    def getPublicCommands (self):

        return {
            'directory-make':           self.makeDirectory,
            'directory-remove':         self.removeDirectory,
            'file-compare-leo-files':   self.compareLeoFiles,
            'file-delete':              self.deleteFile,
            'file-diff-files':          self.diff, 
            'file-insert':              self.insertFile,
            'file-open-by-name':        self.openOutlineByName,
            'file-save':                self.saveFile
        }
    #@+node:ekr.20070920104110: *3* compareLeoFiles
    def compareLeoFiles (self,event):

        '''Compare two .leo files.'''

        trace = False and not g.unitTesting
        c = c1 = self.c ; w = c.frame.body.bodyCtrl

        # Prompt for the file to be compared with the present outline.
        filetypes = [("Leo files", "*.leo"),("All files", "*"),]
        fileName = g.app.gui.runOpenFileDialog(
            title="Compare .leo Files",filetypes=filetypes,defaultextension='.leo')
        if not fileName: return

        # Read the file into the hidden commander.
        c2 = self.createHiddenCommander(fileName)
        if not c2: return

        # Compute the inserted, deleted and changed dicts.
        d1 = self.createFileDict(c1)
        d2 = self.createFileDict(c2)  
        inserted, deleted, changed = self.computeChangeDicts(d1,d2)
        if trace: self.dumpCompareNodes(fileName,c1.mFileName,inserted,deleted,changed)

        # Create clones of all inserted, deleted and changed dicts.
        self.createAllCompareClones(c1,c2,inserted,deleted,changed)
        c2.frame.destroySelf()
        g.app.gui.set_focus(c,w)
    #@+node:ekr.20070921072608: *4* computeChangeDicts
    def computeChangeDicts (self,d1,d2):

        '''Compute inserted, deleted, changed dictionaries.
        
        New in Leo 4.11: show the nodes in the *invisible* file, d2, if possible.'''

        inserted = {}
        for key in d2:
            if not d1.get(key):
                inserted[key] = d2.get(key)
        deleted = {}
        for key in d1:
            if not d2.get(key):
                deleted[key] = d1.get(key)
        changed = {}
        for key in d1:
            if d2.get(key):
                p1 = d1.get(key)
                p2 = d2.get(key)
                if p1.h != p2.h or p1.b != p2.b:
                    changed[key] = p2 # Show the node in the *other* file.
        return inserted, deleted, changed
    #@+node:ekr.20070921072910: *4* createAllCompareClones & helper
    def createAllCompareClones(self,c1,c2,inserted,deleted,changed):

        c = self.c # Always use the visible commander
        assert c == c1
        # Create parent node at the start of the outline.
        u = c.undoer ; undoType = 'Compare .leo Files'
        u.beforeChangeGroup(c.p,undoType)
        undoData = u.beforeInsertNode(c.p)
        parent = c.p.insertAfter()
        parent.setHeadString(undoType)
        u.afterInsertNode(parent,undoType,undoData,dirtyVnodeList=[])
        for d,kind in (
            (deleted,'not in %s' % c2.shortFileName()),
            (inserted,'not in %s' % c1.shortFileName()),
            (changed,'changed: as in %s' % c2.shortFileName()),
        ):
            self.createCompareClones(d,kind,parent)
        c.selectPosition(parent)
        u.afterChangeGroup(parent,undoType,reportFlag=True) 
        c.redraw()
    #@+node:ekr.20070921074410: *5* createCompareClones
    def createCompareClones (self,d,kind,parent):

        if d:
            c = self.c # Use the visible commander.
            parent = parent.insertAsLastChild()
            parent.setHeadString(kind)
            for key in d:
                p = d.get(key)
                if p.v.context == c:
                    clone = p.clone()
                    clone.moveToLastChildOf(parent)
                else:
                    # Fix bug 1160660: File-Compare-Leo-Files creates "other file" clones.
                    copy = p.copyTreeAfter()
                    copy.moveToLastChildOf(parent)
                    for p2 in copy.self_and_subtree():
                        p2.v.context = c
    #@+node:ekr.20070921070101: *4* createHiddenCommander (editFileCommandsClass)
    def createHiddenCommander(self,fn):

        '''Read the file into a hidden commander (Similar to g.openWithFileName).'''

        import leo.core.leoCommands as leoCommands
        lm = g.app.loadManager

        c2 = leoCommands.Commands(fn,gui=g.app.nullGui)
        theFile = lm.openLeoOrZipFile(fn)

        if theFile:
            c2.fileCommands.openLeoFile(theFile,fn,
                readAtFileNodesFlag=True,silent=True)
            return c2
        else:
            return None
    #@+node:ekr.20070921070101.1: *4* createFileDict
    def createFileDict (self,c):

        '''Create a dictionary of all relevant positions in commander c.'''

        d = {}
        for p in c.all_positions():
            try:
                # fileIndices for pre-4.x versions of .leo files have a different format.
                i,j,k = p.v.fileIndex
                d[str(i),str(j),str(k)] = p.copy()
            except Exception:
                pass
        return d
    #@+node:ekr.20070921072608.1: *4* dumpCompareNodes
    def dumpCompareNodes (self,fileName1,fileName2,inserted,deleted,changed):

        for d,kind in (
            (inserted,'inserted (only in %s)' % (fileName1)),
            (deleted, 'deleted  (only in %s)' % (fileName2)),
            (changed, 'changed'),
        ):
            g.pr('\n',kind)
            for key in d:
                p = d.get(key)
                if g.isPython3:
                    g.pr('%-32s %s' % (key,p.h))
                else:
                    g.pr('%-32s %s' % (key,g.toEncodedString(p.h,'ascii')))
    #@+node:ekr.20050920084036.164: *3* deleteFile
    def deleteFile (self,event):

        '''Prompt for the name of a file and delete it.'''

        k = self.k ; state = k.getState('delete_file')

        if state == 0:
            prefix = 'Delete File: '
            k.setLabelBlue('%s%s%s' % (prefix,os.getcwd(),os.sep))
            k.getArg(event,'delete_file',1,self.deleteFile,prefix=prefix)
        else:
            k.keyboardQuit()
            k.clearState()
            try:
                os.remove(k.arg)
                k.setLabel('Deleted: %s' % k.arg)
            except Exception:
                k.setLabel('Not Deleted: %s' % k.arg)
    #@+node:ekr.20050920084036.165: *3* diff (revise)
    def diff (self,event):

        '''Creates a node and puts the diff between 2 files into it.'''

        w = self.editWidget(event)
        if not w: return
        fn = self.getReadableTextFile()
        if not fn: return
        fn2 = self.getReadableTextFile()
        if not fn2: return
        s1,e = g.readFileIntoString(fn)
        if s1 is None: return
        s2,e = g.readFileIntoString(fn2)
        if s2 is None: return

        # self.switchToBuffer(event,"*diff* of ( %s , %s )" % (name,name2))
        data = difflib.ndiff(s1,s2)
        idata = []
        for z in data:
            idata.append(z)
        w.delete(0,'end')
        w.insert(0,''.join(idata))
    #@+node:ekr.20050920084036.166: *3* getReadableTextFile
    def getReadableTextFile (self):

        fn = g.app.gui.runOpenFileDialog(
            title = 'Open Text File',
            filetypes = [("Text","*.txt"), ("All files","*")],
            defaultextension = ".txt")

        return fn
    #@+node:ekr.20050920084036.167: *3* insertFile
    def insertFile (self,event):

        '''Prompt for the name of a file and put the selected text into it.'''

        w = self.editWidget(event)
        if not w: return

        fn = self.getReadableTextFile()
        if not fn: return

        s,e = g.readFileIntoString(fn)
        if s is None: return

        self.beginCommand(undoType='insert-file')
        i = w.getInsertPoint()
        w.insert(i,s)
        w.seeInsertPoint()
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.168: *3* makeDirectory
    def makeDirectory (self,event):

        '''Prompt for the name of a directory and create it.'''

        k = self.k ; state = k.getState('make_directory')

        if state == 0:
            prefix = 'Make Directory: '
            k.setLabelBlue('%s%s%s' % (prefix,os.getcwd(),os.sep))
            k.getArg(event,'make_directory',1,self.makeDirectory,prefix=prefix)
        else:
            k.keyboardQuit()
            k.clearState()
            try:
                os.mkdir(k.arg)
                k.setLabel("Created: %s" % k.arg)
            except Exception:
                k.setLabel("Not Create: %s" % k.arg)
    #@+node:ekr.20060419123128: *3* open-outline-by-name
    def openOutlineByName (self,event):

        '''Prompt for the name of a Leo outline and open it.'''

        c = self.c ; k = self.k ; fileName = ''.join(k.givenArgs)

        # Bug fix: 2012/04/09: only call g.openWithFileName if the file exists.
        if fileName and g.os_path_exists(fileName):
            g.openWithFileName(fileName,old_c=c)
        else:
            k.setLabelBlue('Open Leo Outline: ',protect=True)
            k.getFileName(event,handler=self.openOutlineByNameFinisher)

    def openOutlineByNameFinisher (self,event):

        c = self.c ; k = self.k ; fileName = k.arg

        k.resetLabel()
        if fileName and g.os_path_exists(fileName) and not g.os_path_isdir(fileName):
            g.openWithFileName(fileName,old_c=c)
    #@+node:ekr.20050920084036.169: *3* removeDirectory
    def removeDirectory (self,event):

        '''Prompt for the name of a directory and delete it.'''

        k = self.k ; state = k.getState('remove_directory')

        if state == 0:
            prefix = 'Remove Directory: '
            k.setLabelBlue('%s%s%s' % (prefix,os.getcwd(),os.sep))
            k.getArg(event,'remove_directory',1,self.removeDirectory,prefix=prefix)
        else:
            k.keyboardQuit()
            k.clearState()
            try:
                os.rmdir(k.arg)
                k.setLabel('Removed: %s' % k.arg)
            except Exception:
                k.setLabel('Not Removed: %s' % k.arg)
    #@+node:ekr.20050920084036.170: *3* saveFile (changed)
    def saveFile (self,event):

        '''Prompt for the name of a file and put the body text of the selected node into it..'''

        w = self.editWidget(event)
        if not w: return

        fileName = g.app.gui.runSaveFileDialog(
            initialfile = None,
            title='save-file',
            filetypes = [("Text","*.txt"), ("All files","*")],
            defaultextension = ".txt")

        if not fileName: return

        try:
            f = open(fileName,'w')
            s = w.getAllText()
            if not g.isPython3: # 2010/08/27
                s = g.toEncodedString(s,encoding='utf-8',reportErrors=True)
            f.write(s)
            f.close()
        except IOError:
            g.es('can not create',fileName)
    #@-others
#@+node:ekr.20060205164707: ** helpCommandsClass
class helpCommandsClass (baseEditCommandsClass):

    '''A class to load files into buffers and save buffers to files.'''

    #@+others
    #@+node:ekr.20060205165501: *3* getPublicCommands (helpCommands)
    def getPublicCommands (self):

        return {
        'help':                         self.help,
        'help-for-abbreviations':       self.helpForAbbreviations,
        'help-for-autocompletion':      self.helpForAutocompletion,
        'help-for-bindings':            self.helpForBindings,
        'help-for-command':             self.helpForCommand,
        'help-for-debugging-commands':  self.helpForDebuggingCommands,
        'help-for-dynamic-abbreviations': self.helpForDynamicAbbreviations,
        'help-for-find-commands':       self.helpForFindCommands,
        'help-for-minibuffer':          self.helpForMinibuffer,
        'help-for-python':              self.pythonHelp,
        'help-for-regular-expressions': self.helpForRegularExpressions,
        'print-settings':               self.printSettings,
        }
    #@+node:ekr.20051014170754: *3* helpForMinibuffer
    def helpForMinibuffer (self,event=None):

        '''Print a messages telling you how to get started with Leo.'''

        # A bug in Leo: triple quotes puts indentation before each line.
        c = self.c    
        #@+<< define s >>
        #@+node:ekr.20120522024827.9899: *4* << define s >> (helpForMinibuffer)
        #@@language rest

        s = '''\

        ++++++++++++++++++++
        About the Minibuffer
        ++++++++++++++++++++

        The mini-buffer is intended to be like the Emacs buffer:

        full-command: (default shortcut: Alt-x) Puts the focus in the minibuffer. Type a
        full command name, then hit <Return> to execute the command. Tab completion
        works, but not yet for file names.

        quick-command-mode (default shortcut: Alt-x). Like Emacs Control-C. This mode is
        defined in leoSettings.leo. It is useful for commonly-used commands.

        universal-argument (default shortcut: Alt-u). Like Emacs Ctrl-u. Adds a repeat
        count for later command. Ctrl-u 999 a adds 999 a's. Many features remain
        unfinished.

        keyboard-quit (default shortcut: Ctrl-g) Exits any minibuffer mode and puts
        the focus in the body pane.

        Use the help-for-command command to see documentation for a particular command.
        '''
        #@-<< define s >>
        c.putHelpFor(s)
    #@+node:ekr.20060417203717: *3* helpForCommand & helpers
    def helpForCommand (self,event):

        '''Prompts for a command name and prints the help message for that command.'''

        k = self.k
        #@+<< define s >>
        #@+node:ekr.20130412180825.10342: *4* << define s >> (help-for-command)
        s = '''

        Type the name of the command, followed by Return.

        '''

        #@-<< define s >>
        self.c.putHelpFor(s)
        k.fullCommand(event,help=True,helpHandler=self.helpForCommandFinisher)

    #@+node:ekr.20120521114035.9870: *4* getBindingsForCommand
    def getBindingsForCommand(self,commandName):

        c = self.c ; k = c.k
        data = [] ; n1 = 4 ; n2 = 20
        d = k.bindingsDict
        for stroke in sorted(d):
            assert g.isStroke(stroke),repr(stroke)
            aList = d.get(stroke,[])
            for si in aList:
                assert g.isShortcutInfo(si),si
                if si.commandName == commandName:
                    pane = g.choose(si.pane=='all','',' %s:' % (si.pane))
                    s1 = pane
                    s2 = k.prettyPrintKey(stroke)
                    s3 = si.commandName
                    n1 = max(n1,len(s1))
                    n2 = max(n2,len(s2))
                    data.append((s1,s2,s3),)

        data.sort(key=lambda x: x[1])
        return ','.join(['%s %s' % (s1,s2) for s1,s2,s3 in data]).strip()
    #@+node:ekr.20120521114035.9871: *4* helpForCommandFinisher
    def helpForCommandFinisher (self,commandName):

        c = self.c ; s = None

        if commandName and commandName.startswith('help-for-'):
            # Execute the command itself.
            c.k.simulateCommand(commandName)
        else:
            if commandName:
                bindings = self.getBindingsForCommand(commandName)
                func = c.commandsDict.get(commandName)
                s = g.getDocStringForFunction(func)
                if s:
                    s = self.replaceBindingPatterns(s)
                else:
                    s = 'no docstring available'

                # Create the title.
                s2 = '%s (%s)' % (commandName,bindings) if bindings else commandName
                underline = '+' * len(s2)
                # title = '%s\n%s\n%s\n\n' % (underline,s2,underline)
                title = '%s\n%s\n\n' % (s2,underline)

                # Fixes bug 618570:
                s = title + ''.join([
                    g.choose(line.strip(),line.lstrip(),'\n')
                        for line in g.splitLines(s)])
            else:
                #@+<< set s to about help-for-command >>
                #@+node:ekr.20120521114035.9872: *5* << set s to about help-for-command >>
                s = '''\

                ++++++++++++++++++++++++
                About Leo's help command
                ++++++++++++++++++++++++

                Invoke Leo's help-for-command as follows::

                    <F1>
                    <Alt-X>help-for-command<return>

                Next, type the name of one of Leo's commands.
                You can use tab completion.  Examples::

                    <F1><tab>           shows all commands.
                    <F1>help-for<tab>   shows all help-for- commands.

                Here are the help-for commands::

                    help-for-abbreviations
                    help-for-autocompletion
                    help-for-bindings
                    help-for-command
                    help-for-debugging-commands
                    help-for-dynamic-abbreviations
                    help-for-find-commands
                    help-for-minibuffer
                    help-for-python
                    help-for-regular-expressions

                '''
                #@-<< set s to about help-for-command >>

            c.putHelpFor(s) # calls g.adjustTripleString.
    #@+node:ekr.20120524151127.9886: *4* replaceBindingPatterns
    def replaceBindingPatterns (self,s):

        '''For each instance of the pattern !<command-name>! is s,
        replace the pattern by the key binding for command-name.'''

        c = self.c
        pattern = re.compile('!<(.*)>!')
        while True:
            m = pattern.search(s,0)
            if m is None: break
            name = m.group(1)
            junk,aList = c.config.getShortcut(name)
            for si in aList:
                if si.pane == 'all':
                    key = c.k.prettyPrintKey(si.stroke.s)
                    break
            else: key = '<Alt-X>%s<Return>' % name
            s = s[:m.start()] + key + s[m.end():]
        return s

    #@+node:ekr.20100901080826.5850: *3* helpForAbbreviations
    def helpForAbbreviations (self,event=None):

        '''Prints a discussion of abbreviations.'''

        #@+<< define s >>
        #@+node:ekr.20110530082209.18251: *4* << define s >> (helpForAbbreviations)
        #@@language rest

        s = '''\

        +++++++++++++++++++
        About Abbreviations
        +++++++++++++++++++

        Leo optionally expands abbreviations as you type.

        Abbreviations typically end with something like ";;" so they won't trigger
        by accident.

        You define abbreviations in @data abbreviations nodes or @data
        global-abbreviations nodes. None come predefined, but leoSettings.leo
        contains example abbreviations in the node::

            @@data abbreviations examples

        Abbreviations can simply be shortcuts::

            ncn;;=@nocolor
            
        Abbreviations can span multiple lines. Continued lines start with \\:, like
        this::

            form;;=<form action="main_submit" method="get" accept-charset="utf-8">
            \:<p><input type="submit" value="Continue &rarr;"></p>
            \:</form>\n

        Abbreviations can define templates in which <\|a-field-name\|> denotes a field
        to be filled in::

            input;;=<input type="text/submit/hidden/button"
            \:name="<|name|>"
            \:value="" id="<|id|>">\n

        Typing ",," after inserting a template selects the next field.

        Abbreviations can execute **abbreviation scripts**, delimited by {\|{ and
        }\|}::

            date;;={|{import time ; x=time.asctime()}|}
            ts;;={|{import time ; x=time.strftime("%Y%m%d%H%M%S")}|}
            
        For example, typing ts;; gives::

            20131009171117
            
        It's even possible to define a context in which abbreviation scripts execute.

        See leoSettings.leo for full details.

        '''
        #@-<< define s >>

        self.c.putHelpFor(s)
    #@+node:ekr.20060226131603.1: *3* helpForAutocompletion
    def helpForAutocompletion (self,event=None):

        '''Prints a discussion of autocompletion.'''

        #@+<< define s >>
        #@+node:ekr.20110530082209.18252: *4* << define s >> (helpForAutocompletion)
        # @pagewidth 40
        #@@language rest

        s = '''
        +++++++++++++++++++++++++++++++++
        About Autocompletion and Calltips
        +++++++++++++++++++++++++++++++++

        This documentation describes both
        autocompletion and calltips.

        Typing a period when @language python is
        in effect starts autocompletion. Typing
        '(' during autocompletion shows the
        calltip. Typing Return or Control-g
        (keyboard-quit) exits autocompletion or
        calltips.

        Autocompletion
        ==============

        Autocompletion shows what may follow a
        period in code. For example, after
        typing g. Leo will show a list of all
        the global functions in leoGlobals.py.
        Autocompletion works much like tab
        completion in the minibuffer. Unlike the
        minibuffer, the presently selected
        completion appears directly in the body
        pane.

        A leading period brings up 'Autocomplete
        Modules'. (The period goes away.) You
        can also get any module by typing its
        name. If more than 25 items would appear
        in the Autocompleter tab, Leo shows only
        the valid starting characters. At this
        point, typing an exclamation mark shows
        the complete list. Thereafter, typing
        further exclamation marks toggles
        between full and abbreviated modes.

        If x is a list 'x.!' shows all its
        elements, and if x is a Python
        dictionary, 'x.!' shows list(x.keys()).
        For example, 'sys.modules.!' Again,
        further exclamation marks toggles
        between full and abbreviated modes.

        During autocompletion, typing a question
        mark shows the docstring for the object.
        For example: 'g.app?' shows the
        docstring for g.app. This doesn't work
        (yet) directly for Python globals, but
        '__builtin__.f?' does. Example:
        '__builtin__.pow?' shows the docstring
        for pow.

        Autocompletion works in the Find tab;
        you can use <Tab> to cycle through the
        choices. The 'Completion' tab appears
        while you are doing this; the Find tab
        reappears once the completion is
        finished.

        Calltips
        ========

        Calltips appear after you type an open
        parenthesis in code. Calltips shows the
        expected arguments to a function or
        method. Calltips work for any Python
        function or method, including Python's
        global function. Examples:

        a) g.toUnicode(
           gives:
           g.toUnicode(s,encoding, reportErrors=False

        b) c.widgetWantsFocusNow
           gives:
           c.widgetWantsFocusNow(w

        c) reduce(
           gives:
           reduce(function, sequence[,initial]) -> value

        The calltips appear directly in the text
        and the argument list is highlighted so
        you can just type to replace it. The
        calltips appear also in the status line
        for reference after you have started to
        replace the args.

        Options
        =======

        Both autocompletion and calltips are
        initially enabled or disabled by the
        enable_autocompleter_initially and
        enable_calltips_initially settings in
        leoSettings.leo. You may enable or
        disable these features at any time with
        these commands: enable-autocompleter,
        enable-calltips, disable-autocompleter
        and disable-calltips. '''
        #@-<< define s >>

        self.c.putHelpFor(s)
    #@+node:ekr.20060205170335: *3* helpForBindings
    def helpForBindings (self,event=None):

        '''Prints a discussion of keyboard bindings.'''

        #@+<< define s >>
        #@+node:ekr.20110530082209.18253: *4* << define s >> (helpForBindings)
        # @pagewidth 40
        #@@language rest

        s = '''
        ++++++++++++++++++
        About Key Bindings
        ++++++++++++++++++

        A shortcut specification has the form:

        command-name = shortcutSpecifier

        or

        command-name ! pane = shortcutSpecifier

        The first form creates a binding for all
        panes except the minibuffer. The second
        form creates a binding for one or more
        panes. The possible values for 'pane'
        are:

        ====    ===============
        pane    bound panes
        ====    ===============
        all     body,log,tree
        body    body
        log     log
        mini    minibuffer
        text    body,log
        tree    tree
        ====    ===============

        You may use None as the specifier.
        Otherwise, a shortcut specifier consists
        of a head followed by a tail. The head
        may be empty, or may be a concatenation
        of the following: (All entries in each
        row are equivalent)::

            Shift+ Shift-
            Alt+ or Alt-
            Control+, Control-, Ctrl+ or Ctrl-

        Notes:

        1. The case of plain letters is significant:
           a is not A.

        2. The Shift- (or Shift+) prefix can be
           applied *only* to letters or
           multi-letter tails. Leo will ignore
           (with a warning) the shift prefix
           applied to other single letters,
           e.g., Ctrl-Shift-(

        3. The case of letters prefixed by
           Ctrl-, Alt-, Key- or Shift- is *not*
           significant.

        The following table illustrates these
        rules. In each row, the first entry is
        the key (for k.bindingsDict) and the
        other entries are equivalents that the
        user may specify in leoSettings.leo::

            a, Key-a, Key-A
            A, Shift-A
            Alt-a, Alt-A
            Alt-A, Alt-Shift-a, Alt-Shift-A
            Ctrl-a, Ctrl-A
            Ctrl-A, Ctrl-Shift-a, Ctrl-Shift-A
            !, Key-!,Key-exclam,exclam

        '''
        #@-<< define s >>

        self.c.putHelpFor(s)
    #@+node:ekr.20130412173637.10333: *3* help
    def help (self,event=None):

        '''Prints and introduction to Leo's help system.'''

        #@+<< define rst_s >>
        #@+node:ekr.20130412173637.10330: *4* << define rst_s >> (F1)
        rst_s = '''

        **Welcome to Leo's help system.**

        To learn about ``<Alt-X>`` commands, type::
            
            <Alt-X>help-for-minibuffer<Enter>
            
        To get a list of help topics, type::
            
            <Alt-X>help-<tab>
            
        For Leo commands (tab completion allowed), type::
            
            <Alt-X>help-for-command<Enter>
            <a Leo command name><Enter>
            
        To use Python's help system, type::
            
            <Alt-X>help-for-python<Enter>
            <a python symbol><Enter>

        '''
        #@-<< define rst_s >>
        self.c.putHelpFor(rst_s)
    #@+node:ekr.20070501092655: *3* helpForDebuggingCommands
    def helpForDebuggingCommands (self,event=None):

        '''Prints a discussion of of Leo's debugging commands.'''

        #@+<< define s >>
        #@+node:ekr.20070501092655.1: *4* << define s >> (helpForDebuggingCommands)
        # @pagewidth 40
        #@@language rest

        s = '''
        ++++++++++++++++++++++++
        About Debugging Commands
        ++++++++++++++++++++++++

        The following commands are useful for debugging::

            collect-garbage:   Invoke the garbage collector.
            debug:             Start an external debugger in another process.
            disable-gc-trace:  Disable tracing of the garbage collector.
            dump-all-objects:  Print a summary of all existing Python objects.
            dump-new-objects:  Print a summary of all newly-created Python objects.
            enable-gc-trace:   Enable tracing of the garbage collector.
            free-tree-widgets: Free all widgets used in Leo's outline pane.
            print-focus:       Print information about the requested focus.
            print-stats:       Print statistics about existing Python objects.
            print-gc-summary:  Print a brief summary of all Python objects.
            run-unit-tests:    Run unit tests in the presently selected tree.
            verbose-dump-objects: Print a more verbose listing of all existing Python objects.

        Leo also has many debugging settings that enable and disable traces.
        For details, see the node: @settings-->Debugging in leoSettings.leo.
        '''
        #@-<< define s >>

        self.c.putHelpFor(s)
    #@+node:ekr.20131029061413.17094: *3* helpForDynamicAbbreviations
    def helpForDynamicAbbreviations (self,event=None):

        '''Prints a discussion of abbreviations.'''

        #@+<< define s >>
        #@+node:ekr.20131029061413.17095: *4* << define s >> (helpForDynamicAbbreviations)
        #@@language rest

        s = '''\

        +++++++++++++++++++++++++++
        About Dynamic Abbreviations
        +++++++++++++++++++++++++++

        .. Description taken from http://www.emacswiki.org/emacs/DynamicAbbreviations

        A dynamic abbreviation (dabbrev) is like a normal abbreviation except:

        - You do not have to define it(!)
        - You expand it with Alt-/ (dabbrev-expand) or Alt-Ctrl-/ (dabbrev-completion)

        For example, suppose the text aLongIvarName appears anywhere in the
        outline. To type this name again type::

            aLong<Alt-/>

        You will see a list of possible completions in the log pane.

        Alt-Ctrl-/ (dabbrev-completion) inserts the longest prefix of all
        completions immediately.  For instance, suppose the following appear in text::

            aVeryLongIvarName
            aVeryLongMethodName
            
        Typing::

            aVery<Alt-Ctrl-/>
            
        will immediately extend the typing to::

            aVeryLong

        '''
        #@-<< define s >>

        self.c.putHelpFor(s)
    #@+node:ekr.20060205170335.1: *3* helpForFindCommands
    def helpForFindCommands (self, event=None):

        '''Prints a discussion of of Leo's find commands.'''

        #@+<< define s >>
        #@+node:ekr.20130411023826.16595: *4* << define s >> (helpFor-find-commands)
        #@@language rest

        s = '''

        .. |br| raw:: html

           <br />

        Finding & replacing text
        ------------------------

        Ctrl-F (search-with-present-options) shows the Find Tab and puts the focus
        in the minibuffer.

        **Important**: the Find tab just shows you the status of search and replace
        operations.

        You control those operations from the minibuffer.

        **Note**: You can toggle the radio buttons and check boxes in the Find Tab
        with Ctrl-Alt keys. For example, Ctrl-Alt-X (toggle-find-regex-option)
        toggles the Regexp checkbox.

        After typing Ctrl-F, type the search string, say "def", in the minibuffer.

        Start the find by typing <Return>.

        But suppose you want to replace "def" with "foo", instead of just finding
        "foo".

        Before typing <Return> type Shift-Ctrl-R. The minibuffer prompts for the
        replacement string. Notice that the status area now shows “def” as the Find
        string.

        Type "foo" and type <Return> to start the find-next command.

        When Leo finds the next instance of "def", it will select it. |br|
        You may type any command.  The following are most useful:

        - Ctrl-minus (replace-then-find) replaces the selected text.
        - F3 (find-next) continues searching without making a replacement.
        - F2 (find-previous) continues the search in reverse.
        - Ctrl-G (keyboard-quit) ends the search.

        Incremental searching
        ---------------------

        **Alt-S** starts an incremental search. |br|
        **Alt-R** starts a reverse incremental search.

        Any characters you type extend the search. |br|
        **Backspace** retracts the search. 

        During an incremental search:
            **Enter** or **Ctrl-G** stops the search. |br|
            **Alt-S** finds the search string again. |br|
            **Alt-R** does the same during a reverse search.

        '''
        #@-<< define s >>
        self.c.putHelpFor(s)
    #@+node:ekr.20120522024827.9897: *3* helpForRegularExpressions
    def helpForRegularExpressions (self, event=None):

        '''Prints a discussion of of Leo's find commands.'''

        #@+<< define s >>
        #@+node:ekr.20120522024827.9898: *4* << define s >> (helpForRegularExpressions)
        #@@language rest

        # Using raw string is essential.
        s = r'''\

        .. _`regular expressions`: http://docs.python.org/library/re.html
        .. _`quick reference`:     http://rgruet.free.fr/PQR26/PQR2.6.html

        +++++++++++++++++++++++++++
        About Regular expressions
        +++++++++++++++++++++++++++

        Leo supports Python's regular expressionsin find patterns.
        Here is a quick reference::

            .               Matches any character (including newline if DOTALL flag specified).
            ^               Matches start of the string (of every line in MULTILINE mode).
            $               Matches end of the string (of every line in MULTILINE mode).
            *               0 or more of preceding regular expression (as many as possible).
            +               1 or more of preceding regular expression (as many as possible).
            ?               0 or 1 occurrence of preceding regular expression.
            *?, +?, ??      Same as *, + and ? but matches as few characters as possible.
            {m,n}           Matches from m to n repetitions of preceding RE.
            {m,n}?          Same as {m,n}, but attempting to match as few repetitions as possible.
            [ ]             Defines character set: e.g. '[a-zA-Z]' to match all letters (see also \w \S).
            [^ ]            Defines complemented character set: matches if char is NOT in set.
            \               Escapes special chars '*?+&$|()' and introduces special sequences (see below).
                            If not using a raw string, write as '\\' in the pattern string.
            \\              Matches a literal '\'.
            |               Specifies alternative: 'foo|bar' matches 'foo' or 'bar'.
            (...)           Matches any RE inside (), and delimits a group.
            (?:...)         Mathces RE inside (), but doesn't delimit a group.
            (?P<name>...)   Matches any RE inside (), and delimits a named group.
                            r'(?P<id>[a-zA-Z_]\w*)' defines a group named id.
            (?P=name)       Matches whatever text was matched by the earlier group named name.
            (?=...)         Matches if ... matches next, but doesn't consume any of the string
                            'Isaac (?=Asimov)' matches 'Isaac' only if followed by 'Asimov'.
            (?!...)         Matches if ... doesn't match next. Negative of (?=...).
            (?<=...)        Matches if the current position in the string is preceded by a match
                            for ... that ends at the current position.
                            This is called a positive lookbehind assertion.
            (?<!...)        Matches if the current position in the string is not preceded by a match for ...
                            This is called a negative lookbehind assertion.
            (?(group)A|B)   Group is either a numeric group ID or a group name defined with (?Pgroup...)
                            earlier in the expression.
                            If the specified group matched, the regular expression pattern A will be tested
                            against the string; if the group didn't match, the pattern B will be used instead.
            (?#...)         A comment; ignored.
            (?letters)      Each letter is in 'ilmsux' and sets the corresponding flag.
                            re.I, re.L, re.M, re.S, re.U, re.X.
            \number         Matches content of the group of the same number.     
            \A              Matches only at the start of the string.
            \b              Empty str at beginning or end of word:
                            '\bis\b' matches 'is', but not 'his'.
            \B              Empty str NOT at beginning or end of word.
            \d              Any decimal digit:          [0-9]
            \D              Any non-decimal digit char  [^0-9]).
            \s              Any whitespace char         [ \t\n\r\f\v]
            \S              Any non-whitespace char     [^ \t\n\r\f\v]
            \w              Any alphaNumeric char (depends on LOCALE flag).
            \W              Any non-alphaNumeric char (depends on LOCALE flag).
            \Z              Matches only at the end of the string.

        For complete details, see: http://docs.python.org/library/re.html

        '''
        #@-<< define s >>

        self.c.putHelpFor(s)
    #@+node:ekr.20060602154458: *3* pythonHelp
    def pythonHelp (self,event=None):

        '''Prompt for a arg for Python's help function, and put it to the log pane.'''

        c = self.c ; k = c.k ; tag = 'python-help' ; state = k.getState(tag)

        if state == 0:
            c.minibufferWantsFocus()
            k.setLabelBlue('Python help: ',protect=True)
            k.getArg(event,tag,1,self.pythonHelp)
        else:
            k.clearState()
            k.resetLabel()
            s = k.arg.strip()
            if s:
                # Capture the output of Python's help command.
                old = sys.stdout
                try:
                    sys.stdout = stdout = g.fileLikeObject()
                    help(str(s))
                    s2 = stdout.read()
                finally:
                    sys.stdout = old
                # Send it to the vr pane as a <pre> block
                s2 = '<pre>' + s2 + '</pre>'
                c.putHelpFor(s2)
    #@+node:ekr.20070418074444: *3* printSettings
    def printSettings (self,event=None):

        '''Prints the value of every setting, except key bindings and commands and open-with tables.
        The following shows where the active setting came from:

        -     leoSettings.leo,
        - [D] default settings.
        - [F] indicates the file being loaded,
        - [M] myLeoSettings.leo,

        '''

        self.c.config.printSettings()
    #@-others
#@+node:ekr.20050920084036.171: ** keyHandlerCommandsClass (add docstrings)
class keyHandlerCommandsClass (baseEditCommandsClass):

    '''User commands to access the keyHandler class.'''

    #@+others
    #@+node:ekr.20050920084036.172: *3*  ctor (keyHandlerCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.
    #@+node:ekr.20050920084036.173: *3* getPublicCommands (keyHandlerCommandsClass)
    def getPublicCommands (self):

        k = self.k

        if k:
            return {
                'auto-complete':            k.autoCompleter.autoComplete,
                'auto-complete-force':      k.autoCompleter.autoCompleteForce,
                'digit-argument':           k.digitArgument,
                'disable-autocompleter':    k.autoCompleter.disableAutocompleter,
                'disable-calltips':         k.autoCompleter.disableCalltips,
                'enable-autocompleter':     k.autoCompleter.enableAutocompleter,
                'enable-calltips':          k.autoCompleter.enableCalltips,
                'exit-named-mode':          k.exitNamedMode,
                'full-command':             k.fullCommand, # For menu.
                # 'hide-mini-buffer':         k.hideMinibuffer,
                'mode-help':                k.modeHelp,
                'negative-argument':        k.negativeArgument,
                'number-command':           k.numberCommand,
                'number-command-0':         k.numberCommand0,
                'number-command-1':         k.numberCommand1,
                'number-command-2':         k.numberCommand2,
                'number-command-3':         k.numberCommand3,
                'number-command-4':         k.numberCommand4,
                'number-command-5':         k.numberCommand5,
                'number-command-6':         k.numberCommand6,
                'number-command-7':         k.numberCommand7,
                'number-command-8':         k.numberCommand8,
                'number-command-9':         k.numberCommand9,
                'print-bindings':           k.printBindings,
                'print-buttons':            k.printButtons,
                'print-commands':           k.printCommands,
                # 'propagate-key-event':      k.propagateKeyEvent,
                'repeat-complex-command':   k.repeatComplexCommand,
                # 'scan-for-autocompleter':   k.autoCompleter.scan,
                'set-command-state':        k.setCommandState,
                'set-insert-state':         k.setInsertState,
                'set-overwrite-state':      k.setOverwriteState,
                'show-calltips':            k.autoCompleter.showCalltips,
                'show-calltips-force':      k.autoCompleter.showCalltipsForce,
                # 'show-mini-buffer':         k.showMinibuffer,
                'toggle-autocompleter':     k.autoCompleter.toggleAutocompleter,
                'toggle-calltips':          k.autoCompleter.toggleCalltips,
                #'toggle-mini-buffer':       k.toggleMinibuffer,
                'toggle-input-state':       k.toggleInputState,
                'universal-argument':       k.universalArgument,
            }
        else:
            return {}
    #@-others
#@+node:ekr.20050920084036.174: ** killBufferCommandsClass
class killBufferCommandsClass (baseEditCommandsClass):

    '''A class to manage the kill buffer.'''

    #@+others
    #@+node:ekr.20050920084036.175: *3*  ctor & finishCreate (killBufferCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        self.addWsToKillRing = c.config.getBool('add-ws-to-kill-ring')
        self.k = None
        self.kbiterator = self.iterateKillBuffer()
        self.last_clipboard = None  # For interacting with system clipboard.
        self.lastYankP = None
            # Position of the last item returned by iterateKillBuffer.
        self.reset = None
            # The index of the next item to be returned in
            # g.app.globalKillBuffer by iterateKillBuffer.

    def finishCreate (self):

        baseEditCommandsClass.finishCreate(self)
            # Call the base finishCreate.
            # This sets self.k
    #@+node:ekr.20050920084036.176: *3*  getPublicCommands
    def getPublicCommands (self):

        return {
            'backward-kill-sentence':   self.backwardKillSentence,
            'backward-kill-word':       self.backwardKillWord,
            'clear-kill-ring':          self.clearKillRing,
            'kill-line':                self.killLine,
            'kill-to-end-of-line':      self.killToEndOfLine,
            'kill-word':                self.killWord,
            'kill-sentence':            self.killSentence,
            'kill-region':              self.killRegion,
            'kill-region-save':         self.killRegionSave,
            'kill-ws':                  self.killWs,
            'yank':                     self.yank,
            'yank-pop':                 self.yankPop,
            'zap-to-character':         self.zapToCharacter,
        }
    #@+node:ekr.20050920084036.183: *3* addToKillBuffer
    def addToKillBuffer (self,text):

        '''Insert the text into the kill buffer if force is True or
        the text contains something other than whitespace.'''

        if self.addWsToKillRing or text.strip():
            g.app.globalKillBuffer = [
                z for z in g.app.globalKillBuffer if z != text]
            g.app.globalKillBuffer.insert(0,text)
    #@+node:ekr.20050920084036.181: *3* backwardKillSentence
    def backwardKillSentence (self,event):

        '''Kill the previous sentence.'''

        w = self.editWidget(event)
        if not w: return

        s = w.getAllText()
        ins = w.getInsertPoint()
        i = s.rfind('.',ins)
        if i == -1: return

        undoType='backward-kill-sentence'

        self.beginCommand(undoType=undoType)

        i2 = s.rfind('.',0,i) + 1
        self.kill(event,i2,i+1,undoType=undoType)
        self.c.frame.body.forceFullRecolor()
        w.setInsertPoint(i2)

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050920084036.180: *3* backwardKillWord & killWord
    def backwardKillWord (self,event):
        '''Kill the previous word.'''
        c = self.c ; e = c.editCommands
        self.beginCommand(undoType='backward-kill-word')
        e.backwardWord(event)
        self.killWordHelper(event,'back')

    def killWord (self,event):
        '''Kill the word containing the cursor.'''
        self.beginCommand(undoType='kill-word')
        self.killWordHelper(event,'forward')

    def killWordHelper(self,event,direction):
        c = self.c ; e = c.editCommands ; w = e.editWidget(event)
        # self.killWs(event)
        e.extendToWord(event,direction)
        i,j = w.getSelectionRange()
        self.kill(event,i,j,undoType = None)
        c.frame.body.forceFullRecolor()
        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20051216151811: *3* clearKillRing
    def clearKillRing (self,event=None):

        '''Clear the kill ring.'''

        g.app.globalKillbuffer = []
    #@+node:ekr.20050920084036.185: *3* getClipboard
    def getClipboard (self):

        '''Return the contents of the clipboard.'''

        try:
            ctxt = g.app.gui.getTextFromClipboard()
            if not g.app.globalKillBuffer or ctxt != self.last_clipboard:
                self.last_clipboard = ctxt
                if not g.app.globalKillBuffer or g.app.globalKillBuffer [0] != ctxt:
                    return ctxt
        except Exception:
            g.es_exception()

        return None
    #@+node:ekr.20050920084036.184: *3* iterateKillBuffer
    class killBuffer_iter_class:

        """Returns a list of positions in a subtree, possibly including the root of the subtree."""

        #@+others
        #@+node:ekr.20071003160252.1: *4* __init__ & __iter__ (iterateKillBuffer)
        def __init__(self,c):

            # g.trace('iterateKillBuffer.__init')
            self.c = c
            self.index = 0 # The index of the next item to be returned.

        def __iter__(self):

            return self
        #@+node:ekr.20071003160252.2: *4* next
        def next(self):

            commands = self.c.killBufferCommands
            aList = g.app.globalKillBuffer # commands.killBuffer

            # g.trace(g.listToString([repr(z) for z in aList]))

            if not aList:
                self.index = 0
                return None

            if commands.reset is None:
                i = self.index
            else:
                i = commands.reset
                commands.reset = None

            if i < 0 or i >= len(aList): i = 0
            # g.trace(i)
            val = aList[i]
            self.index = i + 1
            return val

        __next__ = next
        #@-others

    def iterateKillBuffer (self):

        return self.killBuffer_iter_class(self.c)
    #@+node:ekr.20050920084036.178: *3* kill
    def kill (self,event,frm,to,undoType=None):

        '''A helper method for all kill commands.'''

        w = self.editWidget(event)
        if not w: return
        s = w.get(frm,to)
        # g.trace(repr(s))
        if undoType: self.beginCommand(undoType=undoType)
        self.addToKillBuffer(s)
        g.app.gui.replaceClipboardWith(s)
        w.delete(frm,to)
        w.setInsertPoint(frm)
        if undoType:
            self.c.frame.body.forceFullRecolor()
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20130918042415.11297: *3* killToEndOfLine (New in Leo 4.11)
    def killToEndOfLine (self,event):
        '''Kill from the cursor to end of the line.'''
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        # g.trace(ins,j,repr(s[i:j]))
        if ins >= len(s) and g.match(s,j-1,'\n'):
            # Kill the trailing newline of the body text.
            i = max(0,len(s)-1)
            j = len(s)
        elif ins + 1 < j and s[ins:j-1].strip() and g.match(s,j-1,'\n'):
            # Kill the line, but not the newline.
            i,j = ins,j-1
        elif g.match(s,j-1,'\n'):
            i = ins # Kill the newline in the present line.
        else:
            i = j
        if i < j:
            self.kill(event,i,j,undoType='kill-line')
    #@+node:ekr.20071003183657: *3* KillLine
    def killLine (self,event):
        '''Kill the line containing the cursor.'''
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i,j = g.getLine(s,ins)
        if ins >= len(s) and g.match(s,j-1,'\n'):
            # Kill the trailing newline of the body text.
            i = max(0,len(s)-1)
            j = len(s)
        elif j > i+1 and g.match(s,j-1,'\n'):
            # Kill the line, but not the newline.
            j -= 1
        else:
            pass # Kill the newline in the present line.
        self.kill(event,i,j,undoType='kill-line')
    #@+node:ekr.20050920084036.182: *3* killRegion & killRegionSave & helper
    def killRegion (self,event):
        '''Kill the text selection.'''
        self.killRegionHelper(event,deleteFlag=True)

    def killRegionSave (self,event):
        '''Add the selected text to the kill ring, but do not delete it.'''
        self.killRegionHelper(event,deleteFlag=False)

    def killRegionHelper (self,event,deleteFlag):

        w = self.editWidget(event)
        if not w: return
        i,j = w.getSelectionRange()
        if i == j: return
        s = w.getSelectedText()
        if deleteFlag:
            self.beginCommand(undoType='kill-region')
            w.delete(i,j)
            self.c.frame.body.forceFullRecolor()
            self.endCommand(changed=True,setLabel=True)
        self.addToKillBuffer(s)
        g.app.gui.replaceClipboardWith(s)
        # self.removeRKeys(w)
    #@+node:ekr.20050930095323.1: *3* killSentence
    def killSentence (self,event):

        '''Kill the sentence containing the cursor.'''

        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = w.getInsertPoint()
        i = s.find('.',ins)
        if i == -1: return

        undoType='kill-sentence'

        self.beginCommand(undoType=undoType)

        i2 = s.rfind('.',0,ins) + 1
        self.kill(event,i2,i+1,undoType=undoType)
        self.c.frame.body.forceFullRecolor()
        w.setInsertPoint(i2)

        self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050930100733: *3* killWs
    def killWs (self,event,undoType='kill-ws'):

        '''Kill whitespace.'''

        ws = ''
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        i = j = ins = w.getInsertPoint()

        while i >= 0 and s[i] in (' ','\t'):
            i-= 1
        if i < ins: i += 1

        while j < len(s) and s[j] in (' ','\t'):
            j += 1

        if j > i:
            ws = s[i:j]
            # g.trace(i,j,repr(ws))
            w.delete(i,j)
            if undoType: self.beginCommand(undoType=undoType)
            if self.addWsToKillRing:
                self.addToKillBuffer(ws)
            if undoType: self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050930091642.1: *3* yank
    def yank (self,event,pop=False):

        '''yank: insert the first entry of the kill ring.
        yank-pop: insert the next entry of the kill ring.
        '''

        c = self.c ; w = self.editWidget(event)
        if not w: return
        current = c.p
        if not current: return
        text = w.getAllText()
        i, j = w.getSelectionRange()
        clip_text = self.getClipboard()
        if not g.app.globalKillBuffer and not clip_text: return

        undoType = g.choose(pop,'yank-pop','yank')
        self.beginCommand(undoType=undoType)
        try:
            if not pop or self.lastYankP and self.lastYankP != current:
                self.reset = 0
            s = self.kbiterator.next()
            if s is None: s = clip_text or ''
            if i != j: w.deleteTextSelection()
            if s != s.lstrip(): # s contains leading whitespace.
                i2,j2 = g.getLine(text,i)
                k = g.skip_ws(text,i2)
                if i2 < i <= k:
                    # Replace the line's leading whitespace by s's leading whitespace.
                    w.delete(i2,k)
                    i = i2
            w.insert(i,s)
            # Fix bug 1099035: Leo yank and kill behaviour not quite the same as emacs.
            # w.setSelectionRange(i,i+len(s),insert=i+len(s))
            w.setInsertPoint(i+len(s))
            self.lastYankP = current.copy()
            c.frame.body.forceFullRecolor()
        finally:
            self.endCommand(changed=True,setLabel=True)
    #@+node:ekr.20050930091642.2: *3* yankPop
    def yankPop (self,event):

        '''Insert the next entry of the kill ring.'''

        self.yank(event,pop=True)

    #@+node:ekr.20050920084036.128: *3* zapToCharacter
    def zapToCharacter (self,event):

        '''Kill characters from the insertion point to a given character.'''

        k = self.k ; w = self.editWidget(event)
        if not w: return

        state = k.getState('zap-to-char')
        if state == 0:
            k.setLabelBlue('Zap To Character: ',protect=True)
            k.setState('zap-to-char',1,handler=self.zapToCharacter)
        else:
            ch = event and event.char or ' '
            k.resetLabel()
            k.clearState()
            s = w.getAllText()
            ins = w.getInsertPoint()
            i = s.find(ch,ins)
            if i == -1: return
            self.beginCommand(undoType='zap-to-char')
            self.addToKillBuffer(s[ins:i])
            g.app.gui.replaceClipboardWith(s[ins:i]) # Support for proper yank.
            w.setAllText(s[:ins] + s[i:])
            w.setInsertPoint(ins)
            self.endCommand(changed=True,setLabel=True)
    #@-others
#@+node:ekr.20050920084036.186: ** leoCommandsClass (add docstrings)
class leoCommandsClass (baseEditCommandsClass):

    #@+others
    #@+node:ekr.20050920084036.187: *3*  ctor (leoCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.
    #@+node:ekr.20050920084036.188: *3* leoCommands.getPublicCommands
    def getPublicCommands (self):

        '''(leoCommands) Return a dict of the 'legacy' Leo commands.'''

        k = self.k ; d2 = {}

        #@+<< define dictionary d of names and Leo commands >>
        #@+node:ekr.20050920084036.189: *4* << define dictionary d of names and Leo commands >>
        c = self.c ; f = c.frame

        d = {
            'abort-edit-headline':          f.abortEditLabelCommand,
            'about-leo':                    c.about,
            'add-comments':                 c.addComments,     
            'beautify':                     c.beautifyPythonCode,
            'beautify-c':                   c.beautifyCCode,
            'beautify-all':                 c.beautifyAllPythonCode,
            'beautify-tree':                c.beautifyPythonTree,
            'cascade-windows':              f.cascade,
            # 'check-all-python-code':      c.checkAllPythonCode,
            'check-derived-file':           c.atFileCommands.checkDerivedFile,
            'check-leo-file':               c.fileCommands.checkLeoFile,
            'check-outline':                c.checkOutline,
            # 'check-python-code':          c.checkPythonCode,
            'clean-recent-files':           c.cleanRecentFiles,
            'clear-recent-files':           c.clearRecentFiles,
            'clone-node':                   c.clone,
            'close-window':                 c.close,
            'contract-all':                 c.contractAllHeadlines,
            'contract-all-other-nodes':     c.contractAllOtherNodes,
            'contract-node':                c.contractNode,
            'contract-or-go-left':          c.contractNodeOrGoToParent,
            'contract-parent':              c.contractParent,
            'convert-all-blanks':           c.convertAllBlanks,
            'convert-all-tabs':             c.convertAllTabs,
            'convert-blanks':               c.convertBlanks,
            'convert-tabs':                 c.convertTabs,
            'copy-node':                    c.copyOutline,
            'copy-text':                    f.copyText,
            'cut-node':                     c.cutOutline,
            'cut-text':                     f.cutText,
            'de-hoist':                     c.dehoist,
            'delete-comments':              c.deleteComments,
            'delete-node':                  c.deleteOutline,
            'demote':                       c.demote,
            'dump-outline':                 c.dumpOutline,
            'edit-headline':                c.editHeadline,
            'end-edit-headline':            f.endEditLabelCommand,
            'equal-sized-panes':            f.equalSizedPanes,
            'execute-script':               c.executeScript,
            'exit-leo':                     g.app.onQuit,
            'expand-all':                   c.expandAllHeadlines,
            'expand-all-subheads':          c.expandAllSubheads,
                # Fixes bug 604037 Status of expandAllSubheads
            'expand-ancestors-only':        c.expandOnlyAncestorsOfNode,
            'expand-and-go-right':          c.expandNodeAndGoToFirstChild,
            'expand-next-level':            c.expandNextLevel,
            'expand-node':                  c.expandNode,
            'expand-or-go-right':           c.expandNodeOrGoToFirstChild,
            'expand-prev-level':            c.expandPrevLevel,
            'expand-to-level-1':            c.expandLevel1,
            'expand-to-level-2':            c.expandLevel2,
            'expand-to-level-3':            c.expandLevel3,
            'expand-to-level-4':            c.expandLevel4,
            'expand-to-level-5':            c.expandLevel5,
            'expand-to-level-6':            c.expandLevel6,
            'expand-to-level-7':            c.expandLevel7,
            'expand-to-level-8':            c.expandLevel8,
            'expand-to-level-9':            c.expandLevel9,
            'export-headlines':             c.exportHeadlines,
            'extract':                      c.extract,
            'extract-names':                c.extractSectionNames,
            # 'extract-python-method':        c.extractPythonMethod,
            # 'extract-section':              c.extractSection,
            'find-next-clone':              c.findNextClone,
            'flatten-outline':              c.flattenOutline,
            'go-back':                      c.goPrevVisitedNode,
            'go-forward':                   c.goNextVisitedNode,
            'goto-first-node':              c.goToFirstNode,
            'goto-first-sibling':           c.goToFirstSibling,
            'goto-first-visible-node':      c.goToFirstVisibleNode,
            'goto-last-node':               c.goToLastNode,
            'goto-last-sibling':            c.goToLastSibling,
            'goto-last-visible-node':       c.goToLastVisibleNode,
            'goto-next-changed':            c.goToNextDirtyHeadline,
            'goto-next-clone':              c.goToNextClone,
            'goto-next-history-node':       c.goToNextHistory,
            'goto-next-marked':             c.goToNextMarkedHeadline,
            'goto-next-node':               c.selectThreadNext,
            'goto-next-sibling':            c.goToNextSibling,
            'goto-next-visible':            c.selectVisNext,
            'goto-parent':                  c.goToParent,
            'goto-prev-history-node':       c.goToPrevHistory,
            'goto-prev-node':               c.selectThreadBack,
            'goto-prev-sibling':            c.goToPrevSibling,
            'goto-prev-visible':            c.selectVisBack,
            'hide-invisibles':              c.hideInvisibles,
            'hoist':                        c.hoist,
            'import-file':                  c.importAnyFile,
            # 'import-at-file':               c.importAtFile,
            # 'import-at-root':               c.importAtRoot,
            # 'import-cweb-files':            c.importCWEBFiles,
            # 'import-derived-file':          c.importDerivedFile,
            # 'import-flattened-outline':     c.importFlattenedOutline,
            # 'import-noweb-files':           c.importNowebFiles,
            'indent-region':                c.indentBody,
            'insert-body-time':             c.insertBodyTime,
            'insert-child':                 c.insertChild,
            'insert-headline-time':         f.insertHeadlineTime,
            'insert-node':                  c.insertHeadline,
            'insert-node-before':            c.insertHeadlineBefore,
            'mark':                         c.markHeadline,
            'mark-changed-items':           c.markChangedHeadlines,
            # 'mark-changed-roots':           c.markChangedRoots,
            # 'mark-clones':                c.markClones,
            'mark-subheads':                c.markSubheads,
            'match-brackets':               c.findMatchingBracket,
            'minimize-all':                 f.minimizeAll,
            'move-outline-down':            c.moveOutlineDown,
            'move-outline-left':            c.moveOutlineLeft,
            'move-outline-right':           c.moveOutlineRight,
            'move-outline-up':              c.moveOutlineUp,
            'new':                          c.new,
            # 'open-compare-window':        c.openCompareWindow,
            'open-cheat-sheet-leo':         c.openCheatSheet,
            'open-leoDocs-leo':             c.leoDocumentation,
            'open-leoPlugins-leo':          c.openLeoPlugins,
            'open-leoSettings-leo':         c.openLeoSettings,
            'open-myLeoSettings-leo':       c.openMyLeoSettings,
            'open-offline-tutorial':        f.leoHelp,
            'open-online-home':             c.leoHome,
            # 'open-online-tutorial':       c.leoTutorial,
            'open-outline':                 c.open,
            'open-python-window':           c.openPythonWindow,
            'open-quickstart-leo':          c.leoQuickStart,
            'open-scripts-leo':             c.openLeoScripts,
            'open-users-guide':             c.leoUsersGuide,
            'open-with':                    c.openWith,
            'outline-to-cweb':              c.outlineToCWEB,
            'outline-to-noweb':             c.outlineToNoweb,
            'paste-node':                   c.pasteOutline,
            'paste-retaining-clones':       c.pasteOutlineRetainingClones,
            'paste-text':                   f.pasteText,
            'pretty-print-all-python-code': c.prettyPrintAllPythonCode,
            'pretty-print-python-code':     c.prettyPrintPythonCode,
            'promote':                      c.promote,
            'read-at-auto-nodes':           c.readAtAutoNodes,
            'read-at-file-nodes':           c.readAtFileNodes,
            'read-at-shadow-nodes':         c.readAtShadowNodes,
            'read-file-into-node':          c.readFileIntoNode,
            'read-outline-only':            c.readOutlineOnly,
            'redo':                         c.undoer.redo,
            # 'reformat-body':              c.reformatBody, # 2013/10/02.
            'reformat-paragraph':           c.reformatParagraph,
            'remove-sentinels':             c.removeSentinels,
            'resize-to-screen':             f.resizeToScreen,
            'revert':                       c.revert,
            'save-all':                     c.saveAll,
            'save-file':                    c.save,
            'save-file-as':                 c.saveAs,
            'save-file-as-unzipped':        c.saveAsUnzipped,
            'save-file-as-zipped':          c.saveAsZipped,
            'save-file-to':                 c.saveTo,
            'set-colors':                   c.colorPanel,
            'set-font':                     c.fontPanel,
            'settings':                     c.preferences,
            'show-invisibles':              c.showInvisibles,
            'sort-children':                c.sortChildren,
            'sort-recent-files':            c.sortRecentFiles,
            'sort-siblings':                c.sortSiblings,
            'tangle':                       c.tangle,
            'tangle-all':                   c.tangleAll,
            'tangle-marked':                c.tangleMarked,
            'toggle-active-pane':           f.toggleActivePane,
            'toggle-angle-brackets':        c.toggleAngleBrackets,
            'toggle-invisibles':            c.toggleShowInvisibles,
            'toggle-sparse-move':           c.toggleSparseMove,
            'toggle-split-direction':       f.toggleSplitDirection,
            'undo':                         c.undoer.undo,
            'unindent-region':              c.dedentBody,
            'unmark-all':                   c.unmarkAll,
            'untangle':                     c.untangle,
            'untangle-all':                 c.untangleAll,
            'untangle-marked':              c.untangleMarked,
            'weave':                        c.weave,
            'write-at-auto-nodes':          c.atFileCommands.writeAtAutoNodes,
            'write-at-file-nodes':          c.fileCommands.writeAtFileNodes,
            'write-at-shadow-nodes':        c.fileCommands.writeAtShadowNodes,
            'write-dirty-at-auto-nodes':    c.atFileCommands.writeDirtyAtAutoNodes,
            'write-dirty-at-file-nodes':    c.fileCommands.writeDirtyAtFileNodes,
            'write-dirty-at-shadow-nodes':  c.fileCommands.writeDirtyAtShadowNodes,
            'write-file-from-node':         c.writeFileFromNode,
            'write-missing-at-file-nodes':  c.fileCommands.writeMissingAtFileNodes,
            'write-outline-only':           c.fileCommands.writeOutlineOnly,
        }
        #@-<< define dictionary d of names and Leo commands >>

        # Create a callback for each item in d.
        for name in sorted(d):
            f = d.get(name)
            d2 [name] = f
            k.inverseCommandsDict [f.__name__] = name
            # g.trace('leoCommands %24s = %s' % (f.__name__,name))

        return d2
    #@-others
#@+node:ekr.20050920084036.190: ** macroCommandsClass
class macroCommandsClass (baseEditCommandsClass):

    '''A class for recording, playing back, saving and restoring keyboard macros.
    '''

    #@+others
    #@+node:ekr.20050920084036.191: *3*  ctor (macroCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        self.lastMacro = None
        self.macros = []
        self.macro = []
        self.namedMacros = {}

        # Important: we must not interfere with k.state in startRecordingMacro!
        self.recordingMacro = False
    #@+node:ekr.20050920084036.192: *3*  getPublicCommands
    def getPublicCommands (self):

        return {
            'macro-call':           self.callNamedMacro,
            'macro-call-last':      self.callLastMacro,
            'macro-end-recording':  self.endMacro,
            'macro-load-all':       self.loadMacros,
            'macro-name-last':      self.nameLastMacro,
            'macro-print-all':      self.printMacros,
            'macro-print-last':     self.printLastMacro,
            'macro-save-all':       self.saveMacros,
            'macro-start-recording':self.startRecordingMacro,
        }
    #@+node:ekr.20050920084036.202: *3* callLastMacro
    # Called from universal-command.

    def callLastMacro (self,event=None):

        '''Call the last recorded keyboard macro.'''

        # g.trace(self.lastMacro)

        if self.lastMacro:
            self.executeMacro(self.lastMacro)
    #@+node:ekr.20050920084036.194: *3* callNamedMacro
    def callNamedMacro (self,event):

        '''Prompts for a macro name, then executes it.'''

        k = self.k ; tag = 'macro-name'
        state = k.getState(tag)
        prompt = 'Call macro named: '

        if state == 0:
            k.setLabelBlue(prompt,protect=True)
            k.getArg(event,tag,1,self.callNamedMacro)
        else:
            macro = self.namedMacros.get(k.arg)
            # Must do this first!
            k.clearState()
            if macro:
                self.executeMacro(macro)
            else:
                g.es('no macro named %s' % k.arg)
            k.resetLabel()

    #@+node:ekr.20050920085536.15: *3* completeMacroDef
    # Called from loadFile and nameLastMacro.

    def completeMacroDef (self,name,macro):

        '''Add the macro to the list of macros,
        and add the macro's name to c.commandsDict.
        '''

        trace = False and not g.unitTesting
        k= self ; c = k.c

        if trace:
            g.trace('macro::%s' % (name))
            for event in macro:
                g.trace(event.stroke)

        def func (event,macro=macro):
            return self.executeMacro(macro)

        if name in c.commandsDict:
            g.es_print('over-riding command: %s' % (name))
        else:
            g.es_print('loaded: %s' % (name))

        c.commandsDict [name] = func
        self.namedMacros [name] = macro
    #@+node:ekr.20050920084036.206: *3* endMacro
    def endMacro (self,event=None):

        '''Stops recording a macro.'''

        k = self.k
        self.recordingMacro = False
            # Tell k.masterKeyHandler and masterCommandHandler we are done.

        if self.macro:
            # self.macro = self.macro [: -4]
            self.macros.insert(0,self.macro)
            self.lastMacro = self.macro[:]
            self.macro = []
            k.setLabelBlue('Keyboard macro defined, not named')
        else:
            k.setLabelBlue('Empty keyboard macro')
    #@+node:ekr.20050920084036.203: *3* executeMacro
    def executeMacro (self,macro):

        trace = False and not g.unitTesting
        c = self.c ; k = self.k

        c.bodyWantsFocus()

        for event in macro:
            if trace: g.trace(repr(event))
            k.masterKeyHandler(event)
    #@+node:ekr.20110606152005.16785: *3* getMacrosNode
    def getMacrosNode (self):

        '''Return the position of the @macros node.'''

        c = self.c

        for p in c.all_unique_positions():
            if p.h == '@macros':
                return p

        # Not found.
        for p in c.all_unique_positions():
            if p.h == '@settings':
                # Create as the last child of the @settings node.
                p2 = p.insertAsLastChild()
                break
        else:
            # Create as the root node.
            oldRoot = c.rootPosition()
            p2 = oldRoot.insertAfter()
            p2.moveToRoot(oldRoot)

        c.setHeadString(p2,'@macros')
        g.es_print('Created: %s' % p2.h)
        c.redraw()
        return p2
    #@+node:ekr.20110606152005.16788: *3* getWidgetName
    def getWidgetName(self,obj):

        if not obj:
            return ''
        if hasattr(obj,'objectName'):
            return obj.objectName()
        if hasattr(obj,'widget'):
            if hasattr(obj.widget,'objectName'):
                return obj.widget.objectName()
        return ''
    #@+node:ekr.20110606152005.16787: *3* loadMacros
    def loadMacros (self,event=None):

        '''Load macros from the @macros node.'''

        trace = False and not g.unitTesting
        c = self.c
        create_event = g.app.gui.create_key_event
        p = self.getMacrosNode()

        def oops(message):
            g.trace(message)

        lines = g.splitLines(p.b)
        i = 0
        macro = [] ; name = None
        while i < len(lines):
            progress = i
            s = lines[i].strip()
            i += 1

            if s.startswith('::') and s.endswith('::'):
                name = s[2:-2]
                if name:
                    macro = []
                    while i < len(lines):
                        s = lines[i].strip()
                        if trace: g.trace(repr(name),repr(s))
                        if s:
                            stroke=s
                            char = c.k.stroke2char(stroke)
                            w = c.frame.body.bodyCtrl
                            macro.append(create_event(c,char,stroke,w))
                            i += 1
                        else: break
                    # Create the entries.
                    if macro:
                        self.completeMacroDef(name,macro)
                        macro = [] ; name = None
                    else:
                        oops('empty expansion for %s' % (name))
            elif s:
                if s.startswith('#') or s.startswith('@'):
                    pass
                else:
                    oops('ignoring line: %s' % (repr(s)))
            else: pass
            assert progress < i

        # finish of the last macro.
        if macro:
            self.completeMacroDef(name,macro)
    #@+node:ekr.20050920084036.198: *3* nameLastMacro
    def nameLastMacro (self,event):

        '''Prompts for the name to be given to the last recorded macro.'''

        k = self.k ; state = k.getState('name-macro')

        if state == 0:
            k.setLabelBlue('Name of macro: ',protect=True)
            k.getArg(event,'name-macro',1,self.nameLastMacro)
        else:
            k.clearState()
            name = k.arg
            self.completeMacroDef(name,self.lastMacro)
            k.setLabelGrey('Macro defined: %s' % name)
    #@+node:ekr.20090201152408.1: *3* printMacros & printLastMacro
    def printMacros (self,event=None):

        '''Prints the name and definition of all named macros.'''

        names = list(self.namedMacros.keys())

        if names:
            names.sort()
            print('macros',names)
            # g.es('\n'.join(names),tabName='Macros')
        else:
            g.es('no macros')

    def printLastMacro (self,event=None):

        '''Print the last (unnamed) macro.'''

        if self.lastMacro:
            for event in self.lastMacro:
                g.es(repr(event.stroke))
    #@+node:ekr.20050920084036.199: *3* saveMacros
    def saveMacros (self,event=None):

        '''Store macros in the @macros node..'''

        p = self.getMacrosNode()
        result = []
        # g.trace(list(self.namedMacros.keys()))
        for name in self.namedMacros:
            macro = self.namedMacros.get(name)
            result.append('::%s::' % (name))
            for event in macro:
                if 0:
                    w_name = self.getWidgetName(event.w)
                    result.append('%s::%s::%s' % (repr(event.char),event.stroke,w_name))
                result.append(event.stroke)
            result.append('') # Blank line terminates

        p.b = '\n'.join(result)

    #@+node:ekr.20050920084036.204: *3* startRecordingMacro
    def startRecordingMacro (self,event):

        '''Start recording or continue to record a macro.'''

        trace = False and not g.unitTesting
        k = self.k

        if event:
            if self.recordingMacro:
                if trace: g.trace('stroke',event.stroke)
                self.macro.append(event)
            else:
                self.recordingMacro = True
                k.setLabelBlue('Recording macro. ctrl-g to end...',protect=True)
        else:
            g.trace('can not happen: no event')
    #@-others
#@+node:ekr.20050920084036.221: ** rectangleCommandsClass
class rectangleCommandsClass (baseEditCommandsClass):

    #@+others
    #@+node:ekr.20050920084036.222: *3*  Birth (rectangleCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        self.theKillRectangle = [] # Do not re-init this!
        self.stringRect = None

    def finishCreate(self):

        baseEditCommandsClass.finishCreate(self)

        self.commandsDict = {
            'c': ('clear-rectangle',    self.clearRectangle),
            'd': ('delete-rectangle',   self.deleteRectangle),
            'k': ('kill-rectangle',     self.killRectangle),
            'o': ('open-rectangle',     self.openRectangle),
            'r': ('copy-rectangle-to-register',
                self.c.registerCommands.copyRectangleToRegister),
            't': ('string-rectangle',   self.stringRectangle),
            'y': ('yank-rectangle',     self.yankRectangle),
        }
    #@+node:ekr.20051004112630: *3* check
    def check (self,event,warning='No rectangle selected'):

        '''Return True if there is a selection.
        Otherwise, return False and issue a warning.'''

        return self._chckSel(event,warning)
    #@+node:ekr.20050920084036.223: *3* getPublicCommands
    def getPublicCommands (self):

        return {
            'rectangle-clear':  self.clearRectangle,
            'rectangle-close':  self.closeRectangle,
            'rectangle-delete': self.deleteRectangle,
            'rectangle-kill':   self.killRectangle,
            'rectangle-open':   self.openRectangle,
            'rectangle-string': self.stringRectangle,
            'rectangle-yank':   self.yankRectangle,
        }
    #@+node:ekr.20051215103053: *3* beginCommand & beginCommandWithEvent (rectangle)
    def beginCommand (self,undoType='Typing'):

        w = baseEditCommandsClass.beginCommand(self,undoType)
        r1,r2,r3,r4 = self.getRectanglePoints(w)
        return w,r1,r2,r3,r4


    def beginCommandWithEvent (self,event,undoType='Typing'):

        '''Do the common processing at the start of each command.'''

        w = baseEditCommandsClass.beginCommandWithEvent(self,event,undoType)
        r1,r2,r3,r4 = self.getRectanglePoints(w)
        return w,r1,r2,r3,r4
    #@+node:ekr.20050920084036.224: *3* Entries (rectangleCommandsClass)
    #@+node:ekr.20050920084036.225: *4* clearRectangle
    def clearRectangle (self,event):

        '''Clear the rectangle defined by the start and end of selected text.'''

        w = self.editWidget(event)
        if not w or not self.check(event): return

        w,r1,r2,r3,r4 = self.beginCommand('clear-rectangle')

        # Change the text.
        fill = ' ' *(r4-r2)
        for r in range(r1,r3+1):
            w.delete('%s.%s' % (r,r2),'%s.%s' % (r,r4))
            w.insert('%s.%s' % (r,r2),fill)

        w.setSelectionRange('%s.%s'%(r1,r2),'%s.%s'%(r3,r2+len(fill)))

        self.endCommand()
    #@+node:ekr.20050920084036.226: *4* closeRectangle
    def closeRectangle (self,event):

        '''Delete the rectangle if it contains nothing but whitespace..'''

        w = self.editWidget(event)
        if not w or not self.check(event): return

        w,r1,r2,r3,r4 = self.beginCommand('close-rectangle')

        # Return if any part of the selection contains something other than whitespace.
        for r in range(r1,r3+1):
            s = w.get('%s.%s' % (r,r2),'%s.%s' % (r,r4))
            if s.strip(): return

        # Change the text.
        for r in range(r1,r3+1):
            w.delete('%s.%s' % (r,r2),'%s.%s' % (r,r4))

        i = '%s.%s' % (r1,r2)
        j = '%s.%s' % (r3,r2)
        w.setSelectionRange(i,j,insert=j)

        self.endCommand()
    #@+node:ekr.20050920084036.227: *4* deleteRectangle
    def deleteRectangle (self,event):

        '''Delete the rectangle defined by the start and end of selected text.'''

        w = self.editWidget(event)
        if not w or not self.check(event): return

        w,r1,r2,r3,r4 = self.beginCommand('delete-rectangle')

        for r in range(r1,r3+1):
            w.delete('%s.%s' % (r,r2),'%s.%s' % (r,r4))

        i = '%s.%s' % (r1,r2)
        j = '%s.%s' % (r3,r2)
        w.setSelectionRange(i,j,insert=j)

        self.endCommand()
    #@+node:ekr.20050920084036.228: *4* killRectangle
    def killRectangle (self,event):

        '''Kill the rectangle defined by the start and end of selected text.'''

        w = self.editWidget(event)
        if not w or not self.check(event): return

        w,r1,r2,r3,r4 = self.beginCommand('kill-rectangle')

        self.theKillRectangle = []

        for r in range(r1,r3+1):
            s = w.get('%s.%s' % (r,r2),'%s.%s' % (r,r4))
            self.theKillRectangle.append(s)
            w.delete('%s.%s' % (r,r2),'%s.%s' % (r,r4))

        # g.trace('killRect',repr(self.theKillRectangle))

        if self.theKillRectangle:
            ins = '%s.%s' % (r,r2)
            w.setSelectionRange(ins,ins,insert=ins)

        self.endCommand()
    #@+node:ekr.20050920084036.230: *4* openRectangle
    def openRectangle (self,event):

        '''Insert blanks in the rectangle defined by the start and end of selected text.
        This pushes the previous contents of the rectangle rightward.'''

        w = self.editWidget(event)
        if not w or not self.check(event): return

        w,r1,r2,r3,r4 = self.beginCommand('open-rectangle')

        fill = ' ' * (r4-r2)
        for r in range(r1,r3+1):
            w.insert('%s.%s' % (r,r2),fill)

        i = '%s.%s' % (r1,r2)
        j = '%s.%s' % (r3,r2+len(fill))
        w.setSelectionRange(i,j,insert=j)

        self.endCommand()
    #@+node:ekr.20050920084036.232: *4* stringRectangle
    def stringRectangle (self,event):

        '''Prompt for a string, then replace the contents of a rectangle
        with a string on each line.'''

        c = self.c ; k = self.k ; state = k.getState('string-rect')
        if g.app.unitTesting:
            state = 1 ; k.arg = 's...s' # This string is known to the unit test.
            w = self.editWidget(event)
            self.stringRect = self.getRectanglePoints(w)
        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w or not self.check(event): return
            self.stringRect = self.getRectanglePoints(w)
            k.setLabelBlue('String rectangle: ',protect=True)
            k.getArg(event,'string-rect',1,self.stringRectangle)
        else:
            k.clearState()
            k.resetLabel()
            c.bodyWantsFocus()
            w = self.w
            self.beginCommand('string-rectangle')
            r1, r2, r3, r4 = self.stringRect
            s = w.getAllText()
            for r in range(r1,r3+1):
                i = g.convertRowColToPythonIndex(s,r-1,r2)
                j = g.convertRowColToPythonIndex(s,r-1,r4)
                s = s[:i] + k.arg + s[j:]
            w.setAllText(s)
            i = g.convertRowColToPythonIndex(s,r1-1,r2)
            j = g.convertRowColToPythonIndex(s,r3-1,r2+len(k.arg))
            w.setSelectionRange(i,j)
            self.endCommand()
            # 2010/1/1: Fix bug 480422:
            # string-rectangle kills syntax highlighting.
            c.frame.body.recolor(c.p,incremental=False)

    #@+node:ekr.20050920084036.229: *4* yankRectangle
    def yankRectangle (self,event,killRect=None):

        '''Yank into the rectangle defined by the start and end of selected text.'''

        # c = self.c
        k = self.k
        w = self.editWidget(event)
        if not w: return

        killRect = killRect or self.theKillRectangle
        if g.app.unitTesting:
            # This value is used by the unit test.
            killRect = ['Y1Y','Y2Y','Y3Y','Y4Y']
        elif not killRect:
            k.setLabelGrey('No kill rect') ; return

        w,r1,r2,r3,r4 = self.beginCommand('yank-rectangle')

        n = 0
        for r in range(r1,r3+1):
            # g.trace(n,r,killRect[n])
            if n >= len(killRect): break
            w.delete('%s.%s' % (r,r2), '%s.%s' % (r,r4))
            w.insert('%s.%s' % (r,r2), killRect[n])
            n += 1

        i = '%s.%s' % (r1,r2)
        j = '%s.%s' % (r3,r2+len(killRect[n-1]))
        w.setSelectionRange(i,j,insert=j)
        self.endCommand()
    #@-others
#@+node:ekr.20050920084036.234: ** registerCommandsClass
class registerCommandsClass (baseEditCommandsClass):

    '''A class to represent registers a-z and the corresponding Emacs commands.'''

    #@+others
    #@+node:ekr.20051004095209: *3* Birth
    #@+node:ekr.20050920084036.235: *4*  Birth (registerCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.
        self.methodDict, self.helpDict = self.addRegisterItems()

        # Init these here to keep pylint happy.
        self.method = None 
        self.registerMode = 0 # Must be an int.
        self.registers = g.app.globalRegisters

    def finishCreate (self):

        baseEditCommandsClass.finishCreate(self)
            # finish the base class.

    def init (self):
        self.method = None 
        self.registerMode = 0 # Must be an int.
        self.registers = {}

    #@+node:ekr.20050920084036.247: *4*  getPublicCommands
    def getPublicCommands (self):

        return {
            'register-append-to':           self.appendToRegister,
            'register-copy-rectangle-to':   self.copyRectangleToRegister,
            'register-copy-to':             self.copyToRegister,
            'register-increment':           self.incrementRegister,
            'register-insert':              self.insertRegister,
            'register-jump-to':             self.jumpToRegister,
            # 'register-number-to':         self.numberToRegister,
            'register-point-to':            self.pointToRegister,
            'register-prepend-to':          self.prependToRegister,
            'register-view':                self.viewRegister,
        }
    #@+node:ekr.20050920084036.252: *4* addRegisterItems
    def addRegisterItems( self ):

        methodDict = {
            '+':        self.incrementRegister,
            ' ':        self.pointToRegister,
            'a':        self.appendToRegister,
            'i':        self.insertRegister,
            'j':        self.jumpToRegister,
            # 'n':        self.numberToRegister,
            'p':        self.prependToRegister,
            'r':        self.copyRectangleToRegister,
            's':        self.copyToRegister,
            'v' :       self.viewRegister,
        }    

        helpDict = {
            's':    'copy to register',
            'i':    'insert from register',
            '+':    'increment register',
            'n':    'number to register',
            'p':    'prepend to register',
            'a':    'append to register',
            ' ':    'point to register',
            'j':    'jump to register',
            'r':    'rectangle to register',
            'v':    'view register',
        }

        return methodDict, helpDict
    #@+node:ekr.20051004123217: *3* checkBodySelection
    def checkBodySelection (self,warning='No text selected'):

        return self._chckSel(event=None,warning=warning)
    #@+node:ekr.20050920084036.236: *3* Entries... (register commands)
    #@+node:ekr.20050920084036.238: *4* appendToRegister
    def appendToRegister (self,event):

        '''Prompt for a register name and append the selected text to the register's contents.'''

        c = self.c ; k = self.k
        tag = 'append-to-register' ; state = k.getState(tag)

        char = event and event.char or ''

        if state == 0:
            k.commandName = tag
            k.setLabelBlue('Append to Register: ',protect=True)
            k.setState(tag,1,self.appendToRegister)
        else:
            k.clearState()
            if self.checkBodySelection():
                if char.isalpha():
                    w = c.frame.body.bodyCtrl
                    c.bodyWantsFocus()
                    key = char.lower()
                    val = self.registers.get(key,'')
                    val = val + w.getSelectedText()
                    self.registers[key] = val
                    k.setLabelGrey('Register %s = %s' % (key,repr(val)))
                else:
                    k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20050920084036.237: *4* prependToRegister
    def prependToRegister (self,event):

        '''Prompt for a register name and prepend the selected text to the register's contents.'''

        c = self.c ; k = self.k
        tag = 'prepend-to-register' ; state = k.getState(tag)

        char = event and event.char or ''

        if state == 0:
            k.commandName = tag
            k.setLabelBlue('Prepend to Register: ',protect=True)
            k.setState(tag,1,self.prependToRegister)
        else:
            k.clearState()
            if self.checkBodySelection():
                if char.isalpha():
                    w = c.frame.body.bodyCtrl
                    c.bodyWantsFocus()
                    key = char.lower()
                    val = self.registers.get(key,'')
                    val = w.getSelectedText() + val
                    self.registers[key] = val
                    k.setLabelGrey('Register %s = %s' % (key,repr(val)))
                else:
                    k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20050920084036.239: *4* copyRectangleToRegister
    def copyRectangleToRegister (self,event):

        '''Prompt for a register name and append the rectangle defined by selected
        text to the register's contents.'''

        c = self.c ; k = self.k ; state = k.getState('copy-rect-to-reg')

        char = event and event.char or ''

        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            k.commandName = 'copy-rectangle-to-register'
            k.setLabelBlue('Copy Rectangle To Register: ',protect=True)
            k.setState('copy-rect-to-reg',1,self.copyRectangleToRegister)
        elif self.checkBodySelection('No rectangle selected'):
            k.clearState()
            if char.isalpha():
                key = char.lower()
                w = self.w
                c.widgetWantsFocusNow(w)
                r1, r2, r3, r4 = self.getRectanglePoints(w)
                rect = []
                while r1 <= r3:
                    txt = w.get('%s.%s' % (r1,r2),'%s.%s' % (r1,r4))
                    rect.append(txt)
                    r1 = r1 + 1
                self.registers [key] = rect
                k.setLabelGrey('Register %s = %s' % (key,repr(rect)))
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20050920084036.240: *4* copyToRegister
    def copyToRegister (self,event):

        '''Prompt for a register name and append the selected text to the register's contents.'''

        c = self.c ; k = self.k
        tag = 'copy-to-register' ; state = k.getState(tag)

        char = event and event.char or ''

        if state == 0:
            k.commandName = tag
            k.setLabelBlue('Copy to Register: ',protect=True)
            k.setState(tag,1,self.copyToRegister)
        else:
            k.clearState()
            if self.checkBodySelection():
                if char.isalpha():
                    key = char.lower()
                    w = c.frame.body.bodyCtrl
                    c.bodyWantsFocus()
                    val = w.getSelectedText()
                    self.registers[key] = val
                    k.setLabelGrey('Register %s = %s' % (key,repr(val)))
                else:
                    k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20050920084036.241: *4* incrementRegister
    def incrementRegister (self,event):

        '''Prompt for a register name and increment its value if it has a numeric value.'''

        c = self.c ; k = self.k ; state = k.getState('increment-reg')

        char = event and event.char or ''

        if state == 0:
            k.setLabelBlue('Increment register: ',protect=True)
            k.setState('increment-reg',1,self.incrementRegister)
        else:
            k.clearState()
            if self._checkIfRectangle(event):
                pass # Error message is in the label.
            elif char.isalpha():
                key = char.lower()
                val = self.registers.get(key,0)
                try:
                    val = str(int(val)+1)
                    self.registers[key] = val
                    k.setLabelGrey('Register %s = %s' % (key,repr(val)))
                except ValueError:
                    k.setLabelGrey("Can't increment register %s = %s" % (key,val))
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20050920084036.242: *4* insertRegister
    def insertRegister (self,event):

        '''Prompt for a register name and and insert the value of another register into its contents.'''

        c = self.c ; k = self.k ; state = k.getState('insert-reg')

        char = event and event.char or ''

        if state == 0:
            k.commandName = 'insert-register'
            k.setLabelBlue('Insert register: ',protect=True)
            k.setState('insert-reg',1,self.insertRegister)
        else:
            k.clearState()
            if char.isalpha():
                w = c.frame.body.bodyCtrl
                c.bodyWantsFocus()
                key = char.lower()
                val = self.registers.get(key)
                if val:
                    if type(val)==type([]):
                        c.rectangleCommands.yankRectangle(val)
                    else:
                        i = w.getInsertPoint()
                        w.insert(i,val)
                    k.setLabelGrey('Inserted register %s' % key)
                else:
                    k.setLabelGrey('Register %s is empty' % key)
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20050920084036.243: *4* jumpToRegister
    def jumpToRegister (self,event):

        '''Prompt for a register name and set the insert point to the value in its register.'''

        c = self.c ; k = self.k ; state = k.getState('jump-to-reg')

        char = event and event.char or ''

        if state == 0:
            k.setLabelBlue('Jump to register: ',protect=True)
            k.setState('jump-to-reg',1,self.jumpToRegister)
        else:
            k.clearState()
            if char.isalpha():
                if self._checkIfRectangle(event): return
                key = char.lower()
                val = self.registers.get(key)
                w = c.frame.body.bodyCtrl
                c.bodyWantsFocus()
                if val:
                    try:
                        w.setInsertPoint(val)
                        k.setLabelGrey('At %s' % repr(val))
                    except Exception:
                        k.setLabelGrey('Register %s is not a valid location' % key)
                else:
                    k.setLabelGrey('Register %s is empty' % key)
        c.bodyWantsFocus()
    #@+node:ekr.20050920084036.244: *4* numberToRegister (not used)
    #@+at
    # C-u number C-x r n reg
    #     Store number into register reg (number-to-register).
    # C-u number C-x r + reg
    #     Increment the number in register reg by number (increment-register).
    # C-x r g reg
    #     Insert the number from register reg into the buffer.
    #@@c

    def numberToRegister (self,event):

        c,k = self.c,self.k
        state = k.getState('number-to-reg')

        char = event and event.char or ''

        if state == 0:
            k.commandName = 'number-to-register'
            k.setLabelBlue('Number to register: ',protect=True)
            k.setState('number-to-reg',1,self.numberToRegister)
        else:
            k.clearState()
            if char.isalpha():
                # self.registers[char.lower()] = str(0)
                k.setLabelGrey('number-to-register not ready yet.')
            else:
                k.setLabelGrey('Register must be a letter')
    #@+node:ekr.20050920084036.245: *4* pointToRegister
    def pointToRegister (self,event):

        '''Prompt for a register name and put a value indicating the insert point in the register.'''

        c = self.c ; k = self.k ; state = k.getState('point-to-reg')

        char = event and event.char or ''

        if state == 0:
            k.commandName = 'point-to-register'
            k.setLabelBlue('Point to register: ',protect=True)
            k.setState('point-to-reg',1,self.pointToRegister)
        else:
            k.clearState()
            if char.isalpha():
                w = c.frame.body.bodyCtrl
                c.bodyWantsFocus()
                key = char.lower()
                val = w.getInsertPoint()
                self.registers[key] = val
                k.setLabelGrey('Register %s = %s' % (key,repr(val)))
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20050920084036.246: *4* viewRegister
    def viewRegister (self,event):

        '''Prompt for a register name and print its contents.'''

        c = self.c ; k = self.k ; state = k.getState('view-reg')

        char = event and event.char or ''

        if state == 0:
            k.commandName = 'view-register'
            k.setLabelBlue('View register: ',protect=True)
            k.setState('view-reg',1,self.viewRegister)
        else:
            k.clearState()
            if char.isalpha():
                key = char.lower()
                val = self.registers.get(key)
                k.setLabelGrey('Register %s = %s' % (key,repr(val)))
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@-others
#@+node:ekr.20051023094009: ** Search classes
#@+node:ekr.20060123125256: *3* class minibufferFind (the findHandler)
class minibufferFind (baseEditCommandsClass):

    '''An adapter class that implements minibuffer find commands using the (hidden) Find Tab.'''

    #@+others
    #@+node:ekr.20060123125317.2: *4*  ctor (minibufferFind)
    def __init__(self,c,finder):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        # g.trace('minibufferFind: finder',finder)

        self.c = c
        self.k = k = c.k
        self.w = None
        self.finder = finder
        self.findTextList = []
        self.changeTextList = []

        commandName = 'replace-string'
        s = k.getShortcutForCommandName(commandName)
        s = k.prettyPrintKey(s)
        s = k.strokeFromSetting(s)
        # g.trace('replaceStringShortcut',s)
        self.replaceStringShortcut = s
    #@+node:ekr.20090126063121.1: *4* editWidget (minibufferFind)
    def editWidget (self,event,forceFocus=True):

        '''An override of baseEditCommands.editWidget

        that does *not* set focus when using anything other than the tk gui.

        This prevents this class from caching an edit widget
        that is about to be deallocated.'''

        c = self.c
        bodyCtrl = c.frame.body and c.frame.body.bodyCtrl

        # Do not cache a pointer to a headline!
        # It will die when the minibuffer is selected.
        self.w = bodyCtrl
        return self.w
    #@+node:ekr.20060124140114: *4*  Options (minibufferFind)
    #@+node:ekr.20060124123133: *5* setFindScope
    def setFindScope(self,where):

        '''Set the find-scope radio buttons.

        `where` must be in ('node-only','entire-outline','suboutline-only'). '''

        h = self.finder

        if where in ('node-only','entire-outline','suboutline-only'):
            var = h.svarDict['radio-search-scope'].get()
            if var:
                h.svarDict["radio-search-scope"].set(where)
        else:
            g.trace('oops: bad `where` value: %s' % where)
    #@+node:ekr.20060124122844: *5* get/set/toggleOption (minibufferFind)
    # This redirection is required to remove gui-dependencies.

    def getOption (self,ivar):          return self.finder.getOption(ivar)
    def setOption (self,ivar,val):      self.finder.setOption(ivar,val)
    def toggleOption (self,ivar):       self.finder.toggleOption(ivar)
    #@+node:ekr.20060125074939: *5* showFindOptions
    def showFindOptions (self):

        '''Show the present find options in the status line.'''

        frame = self.c.frame ; z = []
        # Set the scope field.
        head  = self.getOption('search_headline')
        body  = self.getOption('search_body')
        scope = self.getOption('radio-search-scope')
        d = {'entire-outline':'all','suboutline-only':'tree','node-only':'node'}
        scope = d.get(scope) or ''
        head = g.choose(head,'head','')
        body = g.choose(body,'body','')
        sep = g.choose(head and body,'+','')

        frame.clearStatusLine()
        s = '%s%s%s %s  ' % (head,sep,body,scope)
        frame.putStatusLine(s,color='blue')

        # Set the type field.
        script = self.getOption('script_search')
        regex  = self.getOption('pattern_match')
        change = self.getOption('script_change')
        if script:
            s1 = '*Script-find'
            s2 = g.choose(change,'-change*','*')
            z.append(s1+s2)
        elif regex: z.append('regex')

        table = (
            ('reverse',         'reverse'),
            ('ignore_case',     'noCase'),
            ('whole_word',      'word'),
            ('wrap',            'wrap'),
            ('mark_changes',    'markChg'),
            ('mark_finds',      'markFnd'),
        )

        for ivar,s in table:
            val = self.getOption(ivar)
            if val: z.append(s)

        frame.putStatusLine(' '.join(z))
    #@+node:ekr.20060205105950: *5* setupChangePattern
    def setupChangePattern (self,pattern):

        # g.trace('pattern',g.callers(4))

        h = self.finder ; w = h.change_ctrl

        s = g.toUnicode(pattern)

        w.delete(0,'end')
        w.insert(0,s)

        h.update_ivars()
    #@+node:ekr.20060125091234: *5* setupSearchPattern
    def setupSearchPattern (self,pattern):

        h = self.finder ; w = h.find_ctrl

        # g.trace(pattern)

        s = g.toUnicode(pattern)

        w.delete(0,'end')
        w.insert(0,s)

        h.update_ivars()
    #@+node:ekr.20060210180352: *4* addChangeStringToLabel
    def addChangeStringToLabel (self,protect=True):

        c = self.c ; k = c.k ; h = self.finder ; w = h.change_ctrl

        c.frame.log.selectTab('Find')
        c.minibufferWantsFocus()

        s = w.getAllText()

        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]

        k.extendLabel(s,select=True,protect=protect)
    #@+node:ekr.20060210164421: *4* addFindStringToLabel
    def addFindStringToLabel (self,protect=True):

        c = self.c ; k = c.k ; h = self.finder ; w = h.find_ctrl

        c.frame.log.selectTab('Find')
        c.minibufferWantsFocus()

        s = w.getAllText()
        while s.endswith('\n') or s.endswith('\r'):
            s = s[:-1]

        k.extendLabel(s,select=True,protect=protect)
    #@+node:ekr.20070105123800: *4* changeAll (minibufferFind)
    def changeAll (self,event):

        k = self.k ; tag = 'replace-all' ; state = k.getState(tag)

        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            # Bug fix: 2009-5-31.
            # None denotes that we use the present value of the option.
            self.setupArgs(forward=None,regexp=None,word=None)
            k.setLabelBlue('Replace All From: ',protect=True)
            k.getArg(event,tag,1,self.changeAll)
        elif state == 1:
            self._sString = k.arg
            self.updateFindList(k.arg)
            s = 'Replace All: %s With: ' % (self._sString)
            k.setLabelBlue(s,protect=True)
            self.addChangeStringToLabel()
            k.getArg(event,tag,2,self.changeAll,completion=False,prefix=s)
        elif state == 2:
            self.updateChangeList(k.arg)
            self.lastStateHelper()
            self.generalChangeHelper(self._sString,k.arg,changeAll=True)
    #@+node:ekr.20060128080201: *4* cloneFindAll (minibufferFind)
    def cloneFindAll (self,event):

        c = self.c ; k = self.k ; tag = 'clone-find-all'
        state = k.getState(tag)

        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            self.setupArgs(forward=None,regexp=None,word=None)
            # Init the pattern from the search pattern.
            self.stateZeroHelper(
                event,tag,'Clone Find All: ',self.cloneFindAll)
        else:
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            self.generalSearchHelper(k.arg,cloneFindAll=True)
            c.treeWantsFocus()

    #@+node:ekr.20120226131923.10220: *4* cloneFindAllFlattened (minibufferFind)
    def cloneFindAllFlattened (self,event):

        c = self.c ; k = self.k ; tag = 'clone-find-all-flattened'
        state = k.getState(tag)

        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            self.setupArgs(forward=None,regexp=None,word=None)
            # Init the pattern from the search pattern.
            self.stateZeroHelper(
                event,tag,'Clone Find All Flattened: ',self.cloneFindAllFlattened)
        else:
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            self.generalSearchHelper(k.arg,cloneFindAllFlattened=True)
            c.treeWantsFocus()
    #@+node:ekr.20060204120158: *4* findAgain (minibufferFind)
    def findAgain (self,event):

        f = self.finder

        f.p = self.c.p
        f.v = self.finder.p.v

        # This handles the reverse option.
        return f.findAgainCommand()
    #@+node:ekr.20060209064140: *4* findAll (minibufferFind)
    def findAll (self,event):

        k = self.k ; state = k.getState('find-all')
        if state == 0:
            w = self.editWidget(event) # sets self.w
            if not w: return
            self.setupArgs(forward=True,regexp=False,word=True)
            k.setLabelBlue('Find All: ',protect=True)
            k.getArg(event,'find-all',1,self.findAll)
        else:
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            self.generalSearchHelper(k.arg,findAll=True)
    #@+node:ekr.20060205105950.1: *4* generalChangeHelper (minibufferFind)
    def generalChangeHelper (self,find_pattern,change_pattern,changeAll=False):

        # g.trace(repr(change_pattern))

        c = self.c

        self.setupSearchPattern(find_pattern)
        self.setupChangePattern(change_pattern)

        c.widgetWantsFocusNow(self.w)

        self.finder.p = self.c.p
        self.finder.v = self.finder.p.v

        # Bug fix: 2007-12-14: remove call to self.finder.findNextCommand.
        # This was the cause of replaces not starting in the right place!

        if changeAll:
            self.finder.changeAllCommand()
        else:
            # This handles the reverse option.
            self.finder.findNextCommand()
    #@+node:ekr.20060124181213.4: *4* generalSearchHelper (minibufferFind)
    def generalSearchHelper (self,pattern,cloneFindAll=False,cloneFindAllFlattened=False,findAll=False):

        c = self.c

        self.setupSearchPattern(pattern)

        c.widgetWantsFocusNow(self.w)

        self.finder.p = self.c.p
        self.finder.v = self.finder.p.v

        if findAll:
            self.finder.findAllCommand()
        elif cloneFindAll:
            self.finder.cloneFindAllCommand()
        elif cloneFindAllFlattened:
            self.finder.cloneFindAllFlattenedCommand()
        else:
            # This handles the reverse option.
            self.finder.findNextCommand()
    #@+node:ekr.20060210174441: *4* lastStateHelper
    def lastStateHelper (self):

        k = self.k
        k.clearState()
        k.resetLabel()
        k.showStateAndMode()
    #@+node:ekr.20050920084036.113: *4* replaceString
    def replaceString (self,event):

        k = self.k ; tag = 'replace-string' ; state = k.getState(tag)
        pattern_match = self.getOption ('pattern_match')
        prompt = 'Replace ' + g.choose(pattern_match,'Regex','String')
        if state == 0:
            self.setupArgs(forward=None,regexp=None,word=None)
            prefix = '%s: ' % prompt
            self.stateZeroHelper(event,tag,prefix,self.replaceString)
        elif state == 1:
            self._sString = k.arg
            self.updateFindList(k.arg)
            s = '%s: %s With: ' % (prompt,self._sString)
            k.setLabelBlue(s,protect=True)
            self.addChangeStringToLabel()
            k.getArg(event,'replace-string',2,self.replaceString,completion=False,prefix=s)
        elif state == 2:
            self.updateChangeList(k.arg)
            self.lastStateHelper()
            self.generalChangeHelper(self._sString,k.arg)
    #@+node:ekr.20060124140224.3: *4* reSearchBackward/Forward
    def reSearchBackward (self,event):

        k = self.k ; tag = 're-search-backward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=False,regexp=True,word=None)
            self.stateZeroHelper(
                event,tag,'Regexp Search Backward:',self.reSearchBackward,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            k.setState('replace-string',1,self.replaceString)
            self.replaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)

    def reSearchForward (self,event):

        k = self.k ; tag = 're-search-forward' ; state = k.getState(tag)
        if state == 0:
            self.setupArgs(forward=True,regexp=True,word=None)
            self.stateZeroHelper(
                event,tag,'Regexp Search:',self.reSearchForward,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            k.setState('replace-string',1,self.replaceString)
            self.replaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20060124140224.1: *4* seachForward/Backward
    def searchBackward (self,event):

        k = self.k ; tag = 'search-backward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=False,regexp=False,word=False)
            self.stateZeroHelper(
                event,tag,'Search Backward: ',self.searchBackward,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            k.setState('replace-string',1,self.replaceString)
            self.replaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)

    def searchForward (self,event):

        k = self.k ; tag = 'search-forward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=True,regexp=False,word=False)
            self.stateZeroHelper(
                event,tag,'Search: ',self.searchForward,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            k.setState('replace-string',1,self.replaceString)
            self.replaceString(event=None)
        else:
            self.updateFindList(k.arg)
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20060125093807: *4* searchWithPresentOptions
    def searchWithPresentOptions (self,event):

        trace = False and not g.unitTesting
        k = self.k ; tag = 'search-with-present-options'
        state = k.getState(tag)

        if trace: g.trace('state',state)
        if state == 0:
            self.setupArgs(forward=None,regexp=None,word=None)
            self.stateZeroHelper(
                event,tag,'Search: ',self.searchWithPresentOptions,
                escapes=[self.replaceStringShortcut])
        elif k.getArgEscape:
            # Switch to the replace command.
            self.setupSearchPattern(k.arg) # 2010/01/10: update the find text immediately.
            k.setState('replace-string',1,self.replaceString)
            self.replaceString(event=None)
        else:
            self.updateFindList(k.arg)
            k.clearState()
            k.resetLabel()
            k.showStateAndMode()
            self.generalSearchHelper(k.arg)
    #@+node:ekr.20060124134356: *4* setupArgs
    def setupArgs (self,forward=False,regexp=False,word=False):

        h = self.finder
        reverse = None if forward is None else not forward
        # if forward is None:
            # reverse = None
        # else:
            # reverse = not forward

        for ivar,val,in (
            ('reverse', reverse),
            ('pattern_match',regexp),
            ('whole_word',word),
        ):
            if val is not None:
                self.setOption(ivar,val)

        h.p = p = self.c.p
        h.v = p.v
        h.update_ivars()
        self.showFindOptions()
    #@+node:ekr.20060210173041: *4* stateZeroHelper
    def stateZeroHelper (self,event,tag,prefix,handler,escapes=None):

        k = self.k
        self.w = self.editWidget(event)
        if not self.w: return

        k.setLabelBlue(prefix,protect=True)
        self.addFindStringToLabel(protect=False)

        # g.trace(escapes,g.callers())
        if escapes is None: escapes = []
        k.getArgEscapes = escapes
        k.getArgEscape = None # k.getArg may set this.
        k.getArg(event,tag,1,handler, # enter state 1
            tabList=self.findTextList,completion=True,prefix=prefix)
    #@+node:ekr.20060224171851: *4* updateChange/FindList
    def updateChangeList (self,s):

        if s not in self.changeTextList:
            self.changeTextList.append(s)

    def updateFindList (self,s):

        if s not in self.findTextList:
            self.findTextList.append(s)
    #@+node:ekr.20060124140224.2: *4* wordSearchBackward/Forward
    def wordSearchBackward (self,event):

        k = self.k ; tag = 'word-search-backward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=False,regexp=False,word=True)
            self.stateZeroHelper(event,tag,'Word Search Backward: ',self.wordSearchBackward)
        else:
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)

    def wordSearchForward (self,event):

        k = self.k ; tag = 'word-search-forward' ; state = k.getState(tag)

        if state == 0:
            self.setupArgs(forward=True,regexp=False,word=True)
            self.stateZeroHelper(event,tag,'Word Search: ',self.wordSearchForward)
        else:
            self.lastStateHelper()
            self.generalSearchHelper(k.arg)
    #@-others
#@+node:ekr.20050920084036.257: *3* class searchCommandsClass
class searchCommandsClass (baseEditCommandsClass):

    '''Implements many kinds of searches.'''

    #@+others
    #@+node:ekr.20050920084036.258: *4*  ctor (searchCommandsClass)
    def __init__ (self,c):

        # g.trace('searchCommandsClass')

        baseEditCommandsClass.__init__(self,c)
            # init the base class.
            # sets self.c

        self.findTabHandler = None
        self.minibufferFindHandler = None
        self.inited = False

        # For isearch commands.
        self.ifinder = None
        self.stack = [] # Entries are (p,sel)
        self.ignoreCase = None
        self.forward = None
        self.regexp = None
    #@+node:ekr.20050920084036.259: *4* getPublicCommands (searchCommandsClass)
    def getPublicCommands (self):

        return {
            'clone-find-all':                       self.cloneFindAll,
            'clone-find-all-flattened':             self.cloneFindAllFlattened,

            # These are now replace-xxx.
            # 'change':                               self.findTabChange,
            # 'change-all':                           self.changeAll,
            # 'change-then-find':                     self.findTabChangeThenFind,

            'find-all':                             self.findAll,
            'find-clone-all':                       self.cloneFindAll, # Synonym.
            'find-clone-all-flattened':             self.cloneFindAllFlattened, # Synonym.
            'find-next':                            self.findTabFindNext,
            'find-prev':                            self.findTabFindPrev,

            'find-tab-hide':                        self.hideFindTab, # new name
            'find-tab-open':                        self.openFindTab, # new name

            'isearch-forward':                      self.isearchForward,
            'isearch-backward':                     self.isearchBackward,
            'isearch-forward-regexp':               self.isearchForwardRegexp,
            'isearch-backward-regexp':              self.isearchBackwardRegexp,
            'isearch-with-present-options':         self.isearchWithPresentOptions,

            'replace':                              self.findTabChange,
            'replace-all':                          self.changeAll,
            'replace-string':                       self.replaceString,
            'replace-then-find':                    self.findTabChangeThenFind,

            're-search-forward':                    self.reSearchForward,
            're-search-backward':                   self.reSearchBackward,

            'search-again':                         self.findAgain,
            'search-forward':                       self.searchForward,
            'search-backward':                      self.searchBackward,
            'search-with-present-options':          self.searchWithPresentOptions,

            'set-find-everywhere':                  self.setFindScopeEveryWhere,
            'set-find-node-only':                   self.setFindScopeNodeOnly,
            'set-find-suboutline-only':             self.setFindScopeSuboutlineOnly,

            'show-find-options':                    self.showFindOptions,

            'toggle-find-collapses-nodes':          self.toggleFindCollapesNodes,

            'toggle-find-ignore-case-option':       self.toggleIgnoreCaseOption,
            'toggle-find-in-body-option':           self.toggleSearchBodyOption,
            'toggle-find-in-headline-option':       self.toggleSearchHeadlineOption,
            'toggle-find-mark-changes-option':      self.toggleMarkChangesOption,
            'toggle-find-mark-finds-option':        self.toggleMarkFindsOption,
            'toggle-find-regex-option':             self.toggleRegexOption,
            # 'toggle-find-reverse-option':           self.toggleReverseOption,
            'toggle-find-word-option':              self.toggleWholeWordOption,
            'toggle-find-wrap-around-option':       self.toggleWrapSearchOption,

            'word-search-forward':                  self.wordSearchForward,
            'word-search-backward':                 self.wordSearchBackward,
        }
    #@+node:ekr.20060123131421: *4* Top-level methods
    #@+node:ekr.20051020120306: *5* openFindTab
    def openFindTab (self,event=None,show=True):

        '''Open the Find tab in the log pane.'''

        c = self.c ; log = c.frame.log ; tabName = 'Find'

        wasOpen = self.inited

        if self.inited:
            log.selectTab(tabName)
        else:
            self.inited = True
            log.selectTab(tabName,createText=False)
            f = log.frameDict.get(tabName)
            self.findTabHandler = g.app.gui.createFindTab(c,f)

        if show or wasOpen or c.config.getBool('minibufferSearchesShowFindTab'):
            pass # self.findTabHandler.bringToFront()
        else:
            log.hideTab(tabName)
    #@+node:ekr.20051022212004: *5* Find Tab commands
    # Just open the Find tab if it has never been opened.
    # For minibuffer commands, it would be good to force the Find tab to be visible.
    # However, this leads to unfortunate confusion when executed from a shortcut.

    def findTabChange(self,event=None):
        '''Execute the 'Change' command with the settings shown in the Find tab.'''
        if self.findTabHandler:
            self.findTabHandler.changeCommand()
        else:
            self.openFindTab()

    def findTabChangeThenFind(self,event=None):
        '''Execute the 'Replace, Find' command with the settings shown in the Find tab.'''
        if self.findTabHandler:
            self.findTabHandler.changeThenFindCommand()
        else:
            self.openFindTab()

    def findTabFindAll(self,event=None):
        '''Execute the 'Find All' command with the settings shown in the Find tab.'''
        if self.findTabHandler:
            self.findTabHandler.findAllCommand()
        else:
            self.openFindTab()

    def findTabFindNext (self,event=None):
        '''Execute the 'Find Next' command with the settings shown in the Find tab.'''
        if self.findTabHandler:
            self.findTabHandler.findNextCommand()
        else:
            self.openFindTab()

    def findTabFindPrev (self,event=None):
        '''Execute the 'Find Previous' command with the settings shown in the Find tab.'''
        if self.findTabHandler:
            self.findTabHandler.findPrevCommand()
        else:
            self.openFindTab()

    def hideFindTab (self,event=None):
        '''Hide the Find tab.'''
        if self.findTabHandler:
            self.c.frame.log.selectTab('Log')
    #@+node:ekr.20060124115801: *5* getHandler
    def getHandler(self,show=False):

        '''Return the minibuffer handler, creating it if necessary.'''

        c = self.c

        self.openFindTab(show=show)
            # sets self.findTabHandler,
            # but *not* minibufferFindHandler.

        if not self.minibufferFindHandler:
            self.minibufferFindHandler = minibufferFind(c,self.findTabHandler)

        return self.minibufferFindHandler
    #@+node:ekr.20060123115459: *5* Find options wrappers
    def setFindScopeEveryWhere (self, event):
        '''Set the 'Entire Outline' radio button in the Find tab.'''
        return self.setFindScope('entire-outline')
    def setFindScopeNodeOnly  (self, event):
        '''Set the 'Node Only' radio button in the Find tab.'''
        return self.setFindScope('node-only')
    def setFindScopeSuboutlineOnly (self, event):
        '''Set the 'Suboutline Only' radio button in the Find tab.'''
        return self.setFindScope('suboutline-only')
    def showFindOptions (self,event):
        '''Show all Find options in the minibuffer label area.'''
        self.getHandler().showFindOptions()
    def toggleFindCollapesNodes(self,event):
        '''Toggle the 'Collapse Nodes' checkbox in the find tab.'''
        c = self.c
        c.sparse_find = not c.sparse_find
        if not g.unitTesting:
            g.es('sparse_find',c.sparse_find)
    def toggleIgnoreCaseOption     (self, event):
        '''Toggle the 'Ignore Case' checkbox in the Find tab.'''
        return self.toggleOption('ignore_case')
    def toggleMarkChangesOption (self, event):
        '''Toggle the 'Mark Changes' checkbox in the Find tab.'''
        return self.toggleOption('mark_changes')
    def toggleMarkFindsOption (self, event):
        '''Toggle the 'Mark Finds' checkbox in the Find tab.'''
        return self.toggleOption('mark_finds')
    def toggleRegexOption (self, event):
        '''Toggle the 'Regexp' checkbox in the Find tab.'''
        return self.toggleOption('pattern_match')
    # def toggleReverseOption        (self, event):
        # '''Toggle the 'Reverse' checkbox in the Find tab.'''
        # return self.toggleOption('reverse')
    def toggleSearchBodyOption (self, event):
        '''Set the 'Search Body' checkbox in the Find tab.'''
        return self.toggleOption('search_body')
    def toggleSearchHeadlineOption (self, event):
        '''Toggle the 'Search Headline' checkbox in the Find tab.'''
        return self.toggleOption('search_headline')
    def toggleWholeWordOption (self, event):
        '''Toggle the 'Whole Word' checkbox in the Find tab.'''
        return self.toggleOption('whole_word')
    def toggleWrapSearchOption (self, event):
        '''Toggle the 'Wrap Around' checkbox in the Find tab.'''
        return self.toggleOption('wrap')
    def setFindScope (self, where):
        self.getHandler().setFindScope(where)
    def toggleOption (self, ivar):
        self.getHandler().toggleOption(ivar)
    #@+node:ekr.20060124093828: *5* Find wrappers
    def changeAll(self,event=None):
        '''Execute the 'Replace All' command with the settings shown in the Find tab.'''
        self.getHandler().changeAll(event)

    def cloneFindAll (self,event):
        '''Do search-with-present-options and print all matches in the log pane. It
        also creates a node at the beginning of the outline containing clones of all
        nodes containing the 'find' string. Only one clone is made of each node,
        regardless of how many clones the node has, or of how many matches are found
        in each node. Nodes that are descendants of previously added nodes are not
        added again.'''
        self.getHandler().cloneFindAll(event)

    def cloneFindAllFlattened (self,event):
        '''Do search-with-present-options and print all matches in the log pane. It
        also creates a node at the beginning of the outline containing clones of all
        nodes containing the 'find' string. Only one clone is made of each node,
        regardless of how many clones the node has, or of how many matches are found
        in each node. Nodes that are descendants of previously added nodes **are**
        added again at the top level.'''
        self.getHandler().cloneFindAllFlattened(event)

    def findAll (self,event):
        '''Do search-with-present-options and print all matches in the log pane.'''
        self.getHandler().findAll(event)

    def replaceString (self,event):
        '''Prompts for a search string. Type <Return> to end the search string. The
        command will then prompt for the replacement string. Typing a second
        <Return> key will place both strings in the Find tab and executes a **find**
        command, that is, the search-with-present-options command.'''
        self.getHandler().replaceString(event)

    def reSearchBackward   (self,event):
        '''Do a reverse regex search.'''
        self.getHandler().reSearchBackward(event)

    def reSearchForward    (self,event):
        '''Do a forward regex search.'''
        self.getHandler().reSearchForward(event)

    def searchBackward     (self,event):
        '''Do a backward plain search.'''
        self.getHandler().searchBackward(event)

    def searchForward      (self,event):
        '''Do a forward plain search.'''
        self.getHandler().searchForward(event)

    def wordSearchBackward (self,event):
        '''Do a backward word-only search.'''
        self.getHandler().wordSearchBackward(event)

    def wordSearchForward  (self,event):
        '''Do a forward word-only search.'''
        self.getHandler().wordSearchForward(event)

    def searchWithPresentOptions (self,event):
        '''Prompts for a search string. Typing the <Return> key puts the search
        string in the Find tab and executes a search based on all the settings in
        the Find tab. Recommended as the default search command.'''
        self.getHandler().searchWithPresentOptions(event)
    #@+node:ekr.20060204120158.2: *5* findAgain
    def findAgain (self,event):

        '''The find-again command is the same as the find-next command
        if the search pattern in the Find tab is not '<find pattern here>'
        Otherwise, the find-again is the same as the search-with-present-options command.'''

        h = self.getHandler()

        # h.findAgain returns False if there is no search pattern.
        # In that case, we revert to search-with-present-options.
        if not h.findAgain(event):
            h.searchWithPresentOptions(event)
    #@+node:ekr.20050920084036.261: *4* incremental search...
    #@+node:ekr.20120524151127.9879: *5* Top-level incremental search
    #@+node:ekr.20120524151127.9880: *6* isearchForward
    def isearchForward (self,event):

        '''Begin a forward incremental search.

        - Plain characters extend the search.
        - !<isearch-forward>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-forward',
            forward=True,ignoreCase=False,regexp=False)
    #@+node:ekr.20120524151127.9881: *6* isearchBackward
    def isearchBackward (self,event):

        '''Begin a backward incremental search.

        - Plain characters extend the search backward.
        - !<isearch-forward>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-backward',
            forward=False,ignoreCase=False,regexp=False)
    #@+node:ekr.20120524151127.9882: *6* isearchForwardRegexp
    def isearchForwardRegexp (self,event):

        '''Begin a forward incremental regexp search.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-forward-regexp',
            forward=True,ignoreCase=False,regexp=True)
    #@+node:ekr.20120524151127.9883: *6* isearchBackwardRegexp
    def isearchBackwardRegexp (self,event):

        '''Begin a backward incremental regexp search.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-backward-regexp',
            forward=False,ignoreCase=False,regexp=True)
    #@+node:ekr.20120524151127.9884: *6* isearchWithPresentOptions
    def isearchWithPresentOptions (self,event):

        '''Begin an incremental search using find panel options.

        - Plain characters extend the search.
        - !<isearch-forward-regexp>! repeats the search.
        - Esc or any non-plain key ends the search.
        - Backspace reverses the search.
        - Backspacing to an empty search pattern 
          completely undoes the effect of the search.
        '''

        self.startIncremental(event,'isearch-with-present-options',
            forward=None,ignoreCase=None,regexp=None)
    #@+node:ekr.20120524151127.9885: *5* Utils
    #@+node:ekr.20090204084607.1: *6* abortSearch
    def abortSearch (self):

        '''Restore the original position and selection.'''

        c = self.c ; k = self.k ; w = c.frame.body.bodyCtrl

        k.clearState()
        k.resetLabel()

        p,i,j,in_headline = self.stack[0]
        self.ifinder.in_headline = in_headline
        c.selectPosition(p)
        c.redraw_after_select(p)
        c.bodyWantsFocus()
        w.setSelectionRange(i,j)

        # g.trace(p.h,i,j)
    #@+node:ekr.20060203072636: *6* endSearch
    def endSearch (self):

        c,k = self.c,self.k

        k.clearState()
        k.resetLabel()
        c.bodyWantsFocus()
    #@+node:ekr.20090204084607.2: *6* iSearch
    def iSearch (self,again=False):

        '''Handle the actual incremental search.'''

        c = self.c ; k = self.k ; p = c.p
        ifinder = self.ifinder
        reverse = not self.forward
        pattern = k.getLabel(ignorePrompt=True)
        if not pattern:
            return self.abortSearch()
        ifinder.c = c ; ifinder.p = p.copy()
        # Get the base ivars from the find tab.
        ifinder.update_ivars()
        # Save
        oldPattern = ifinder.find_text
        oldRegexp  = ifinder.pattern_match
        oldReverse = ifinder.reverse
        oldWord =  ifinder.whole_word
        # Override
        ifinder.pattern_match = self.regexp
        ifinder.reverse = reverse
        ifinder.find_text = pattern
        ifinder.whole_word = False # Word option can't be used!
        # Prepare the search.
        if len(self.stack) <= 1: ifinder.in_headline = False
        w = self.setWidget()
        s = w.getAllText()
        i,j = w.getSelectionRange()
        if again: ins = i if reverse else j+len(pattern)
        else:     ins = j+len(pattern) if reverse else i
        ifinder.init_s_ctrl(s,ins)
        # Do the search!
        pos, newpos = ifinder.findNextMatch()
        # Restore.
        ifinder.find_text = oldPattern
        ifinder.pattern_match = oldRegexp
        ifinder.reverse = oldReverse
        ifinder.whole_word = oldWord
        # Handle the results of the search.
        if pos is not None: # success.
            w = ifinder.showSuccess(pos,newpos,showState=False)
            if w: i,j = w.getSelectionRange(sort=False)
            # else: g.trace('****')
            if not again: self.push(c.p,i,j,ifinder.in_headline)
        elif ifinder.wrapping:
            # g.es("end of wrapped search")
            k.setLabelRed('end of wrapped search')
        else:
            g.es("not found: %s" % (pattern))
            if not again:
                event = g.app.gui.create_key_event(c,'\b','BackSpace',w)
                k.updateLabel(event)
    #@+node:ekr.20050920084036.264: *6* iSearchStateHandler
    # Called from the state manager when the state is 'isearch'

    def iSearchStateHandler (self,event):

        trace = False and not g.unitTesting
        # c = self.c
        k = self.k

        stroke = event and event.stroke or None
        s = stroke.s if stroke else ''

        if trace: g.trace('again',stroke in self.iSearchStrokes,'s',repr(s))

        # No need to recognize ctrl-z.
        if s in ('Escape','\n','Return'):
            self.endSearch()
        elif stroke in self.iSearchStrokes:
            self.iSearch(again=True)
        elif s in ('\b','BackSpace'):
            k.updateLabel(event)
            self.iSearchBackspace()
        elif (
            s.startswith('Ctrl+') or
            s.startswith('Alt+') or
            k.isFKey(s) # 2011/06/13.
        ):
            # End the search.
            self.endSearch()
            k.masterKeyHandler(event)
        else:
            if trace: g.trace('event',event)
            k.updateLabel(event)
            self.iSearch()
    #@+node:ekr.20090204084607.4: *6* iSearchBackspace
    def iSearchBackspace (self):

        trace = False and not g.unitTesting
        c = self.c
        if len(self.stack) <= 1:
            self.abortSearch()
            return

        # Reduce the stack by net 1.
        junk = self.pop()
        p,i,j,in_headline = self.pop()
        self.push(p,i,j,in_headline)
        if trace: g.trace(p.h,i,j,in_headline)

        if in_headline:
            # Like ifinder.showSuccess.
            selection = i,j,i
            c.redrawAndEdit(p,selectAll=False,
                selection=selection,
                keepMinibuffer=True)
        else:
            c.selectPosition(p)
            w = c.frame.body.bodyCtrl
            c.bodyWantsFocus()
            if i > j: i,j = j,i
            w.setSelectionRange(i,j)

        if len(self.stack) <= 1:
            self.abortSearch()



    #@+node:ekr.20090204084607.6: *6* getStrokes
    def getStrokes (self,commandName):

        aList = self.inverseBindingDict.get(commandName,[])
        return [key for pane,key in aList]
    #@+node:ekr.20090204084607.5: *6* push & pop
    def push (self,p,i,j,in_headline):

        data = p.copy(),i,j,in_headline
        self.stack.append(data)

    def pop (self):

        data = self.stack.pop()
        p,i,j,in_headline = data
        return p,i,j,in_headline
    #@+node:ekr.20090205085858.1: *6* setWidget
    def setWidget (self):

        c = self.c ; p = c.currentPosition()
        bodyCtrl = c.frame.body.bodyCtrl
        ifinder = self.ifinder

        if ifinder.in_headline:
            w = c.edit_widget(p)
            if not w:
                # Selecting the minibuffer can kill the edit widget.
                selection = 0,0,0
                c.redrawAndEdit(p,selectAll=False,
                    selection=selection,keepMinibuffer=True)
                w = c.edit_widget(p)
            if not w: # Should never happen.
                g.trace('**** no edit widget!')
                ifinder.in_headline = False ; w = bodyCtrl
        else:
            w = bodyCtrl
        if w == bodyCtrl:
            c.bodyWantsFocus()
        return w
    #@+node:ekr.20050920084036.262: *6* startIncremental
    def startIncremental (self,event,commandName,forward,ignoreCase,regexp):

        c = self.c ; k = self.k

        # None is a signal to get the option from the find tab.

        if forward is None or not self.findTabHandler:
            self.openFindTab(show=False)

        self.ifinder = self.findTabHandler

        if not self.minibufferFindHandler:
            self.minibufferFindHandler = minibufferFind(c,self.findTabHandler)

        getOption = self.minibufferFindHandler.getOption

        self.event = event
        self.forward    = not getOption('reverse') if forward is None else forward
        self.ignoreCase = getOption('ignore_case') if ignoreCase is None else ignoreCase
        self.regexp     = getOption('pattern_match') if regexp is None else regexp
        # Note: the word option can't be used with isearches!

        self.w = w = c.frame.body.bodyCtrl
        self.p1 = c.p.copy()
        self.sel1 = w.getSelectionRange(sort=False)
        i,j = self.sel1
        self.push(c.p,i,j,self.ifinder.in_headline)
        self.inverseBindingDict = k.computeInverseBindingDict()
        self.iSearchStrokes = self.getStrokes(commandName)

        k.setLabelBlue('Isearch%s%s%s: ' % (
                g.choose(self.forward,'',' Backward'),
                g.choose(self.regexp,' Regexp',''),
                g.choose(self.ignoreCase,' NoCase',''),
            ),protect=True)

        k.setState('isearch',1,handler=self.iSearchStateHandler)
        c.minibufferWantsFocus()
    #@-others
#@+node:ekr.20051025071455: ** Spell classes
#@+others
#@+node:ekr.20051025071455.1: *3* class spellCommandsClass
class spellCommandsClass (baseEditCommandsClass):

    '''Commands to support the Spell Tab.'''

    #@+others
    #@+node:ekr.20051025080056: *4* ctor (spellCommandsClass)
    def __init__ (self,c):

        baseEditCommandsClass.__init__(self,c) # init the base class.

        self.handler = None

        # All the work happens when we first open the frame.
    #@+node:ekr.20051025080420: *4* getPublicCommands (searchCommandsClass)
    def getPublicCommands (self):

        return {
            'open-spell-tab':           self.openSpellTab,
            'spell-find':               self.find,
            'spell-change':             self.change,
            'spell-change-then-find':   self.changeThenFind,
            'spell-ignore':             self.ignore,
            'hide-spell-tab':           self.hide,
        }
    #@+node:ekr.20051025080633: *4* openSpellTab
    def openSpellTab (self,event=None):

        '''Open the Spell Checker tab in the log pane.'''

        c = self.c ; log = c.frame.log ; tabName = 'Spell'

        if log.frameDict.get(tabName):
            log.selectTab(tabName)
        else:
            log.selectTab(tabName)
            self.handler = spellTabHandler(c,tabName)

        # Bug fix: 2013/05/22.
        if not self.handler.loaded:
            log.deleteTab(tabName,force=True)
    #@+node:ekr.20051025080420.1: *4* commands...(spellCommandsClass)
    # Just open the Spell tab if it has never been opened.
    # For minibuffer commands, we must also force the Spell tab to be visible.
    # self.handler is a spellTabHandler object (inited by openSpellTab)

    def find (self,event=None):
        '''Simulate pressing the 'Find' button in the Spell tab.'''
        if self.handler:
            self.openSpellTab()
            self.handler.find()
        else:
            self.openSpellTab()

    def change(self,event=None):
        '''Simulate pressing the 'Change' button in the Spell tab.'''
        if self.handler:
            self.openSpellTab()
            self.handler.change()
        else:
            self.openSpellTab()

    def changeThenFind (self,event=None):
        '''Simulate pressing the 'Change, Find' button in the Spell tab.'''
        if self.handler:
            self.openSpellTab()
            # A workaround for a pylint warning:
            # self.handler.changeThenFind()
            f = getattr(self.handler,'changeThenFind')
            f()
        else:
            self.openSpellTab()

    def hide (self,event=None):
        '''Hide the Spell tab.'''
        if self.handler:
            self.c.frame.log.selectTab('Log')
            self.c.bodyWantsFocus()

    def ignore (self,event=None):
        '''Simulate pressing the 'Ignore' button in the Spell tab.'''
        if self.handler:
            self.openSpellTab()
            self.handler.ignore()
        else:
            self.openSpellTab()
    #@-others
#@+node:ekr.20051025071455.18: *3* class spellTabHandler (leoFind.leoFind)
class spellTabHandler (leoFind.leoFind):

    """A class to create and manage Leo's Spell Check dialog."""

    #@+others
    #@+node:ekr.20051025071455.19: *4* Birth & death
    #@+node:ekr.20051025071455.20: *5* spellTabHandler.__init__
    def __init__(self,c,tabName):

        """Ctor for the Leo Spelling dialog."""

        leoFind.leoFind.__init__(self,c) # Call the base ctor.
        self.c = c
        self.body = c.frame.body
        self.currentWord = None
        self.outerScrolledFrame = None
        self.workCtrl = g.app.gui.plainTextWidget(c.frame.top)
            # A text widget for scanning.
            # Must have a parent frame even though it is not packed.
        if enchant:
            self.spellController = EnchantClass(c)
            # self.controller = self.spellController 
            self.tab = g.app.gui.createSpellTab(c,self,tabName)
            self.loaded = True
        else:
            self.spellController = None
            self.tab = None
            self.loaded = False
    #@+node:ekr.20051025071455.36: *4* Commands
    #@+node:ekr.20051025071455.37: *5* add (spellTab)
    def add(self,event=None):
        """Add the selected suggestion to the dictionary."""
        
        # Bug fix: 2013/05/22.
        if self.loaded:
            w = self.currentWord
            if w:
                self.spellController.add(w)
                # self.dictionary[w] = 0
                self.tab.onFindButton()
    #@+node:ekr.20051025071455.38: *5* change (spellTab)
    def change(self,event=None):
        """Make the selected change to the text"""
        
        # Bug fix: 2013/05/22.
        if not self.loaded:
            return

        c = self.c ; body = self.body ; w = body.bodyCtrl

        selection = self.tab.getSuggestion()
        if selection:
            # Use getattr to keep pylint happy.
            if hasattr(self.tab,'change_i') and getattr(self.tab,'change_i') is not None:
                start = getattr(self.tab,'change_i')
                end   = getattr(self.tab,'change_j')
                oldSel = start,end
                # g.trace('using',start,end)
            else:
                start,end = oldSel = w.getSelectionRange()
            if start is not None:
                if start > end: start,end = end,start
                w.delete(start,end)
                w.insert(start,selection)
                w.setSelectionRange(start,start+len(selection))
                c.frame.body.onBodyChanged("Change",oldSel=oldSel)
                c.invalidateFocus()
                c.bodyWantsFocus()
                return True

        # The focus must never leave the body pane.
        c.invalidateFocus()
        c.bodyWantsFocus()
        return False
    #@+node:ekr.20051025071455.40: *5* find & helpers
    def find (self,event=None):
        """Find the next unknown word."""
        
        # Bug fix: 2013/05/22.
        if not self.loaded:
            return

        c = self.c ; body = c.frame.body ; w = body.bodyCtrl

        # Reload the work pane from the present node.
        s = w.getAllText().rstrip()
        self.workCtrl.delete(0,"end")
        self.workCtrl.insert("end",s)

        # Reset the insertion point of the work widget.
        ins = w.getInsertPoint()
        self.workCtrl.setInsertPoint(ins)

        alts, word = self.findNextMisspelledWord()
        self.currentWord = word # Need to remember this for 'add' and 'ignore'

        if alts:
            # Save the selection range.
            ins = w.getInsertPoint()
            i,j = w.getSelectionRange()
            self.tab.fillbox(alts,word)
            c.invalidateFocus()
            c.bodyWantsFocus()
            # Restore the selection range.
            w.setSelectionRange(i,j,insert=ins)
            w.see(ins)
        else:
            g.es("no more misspellings")
            self.tab.fillbox([])
            c.invalidateFocus()
            c.bodyWantsFocus()
    #@+node:ekr.20051025071455.45: *6* findNextMisspelledWord
    def findNextMisspelledWord(self):
        """Find the next unknown word."""

        trace = False and not g.unitTesting
        c = self.c ; p = c.p
        w = c.frame.body.bodyCtrl
        sc = self.spellController
        alts = None ; word = None
        try:
            while 1:
                i,j,p,word = self.findNextWord(p)
                # g.trace(i,j,p and p.h or '<no p>')
                if not p or not word:
                    alts = None
                    break
                alts = sc.processWord(word)
                if trace: g.trace('alts',alts and len(alts) or 0,i,j,word,p and p.h or 'None')
                if alts:
                    redraw = not p.isVisible(c)
                    # New in Leo 4.4.8: show only the 'sparse' tree when redrawing.
                    if c.sparse_spell and not c.p.isAncestorOf(p):
                        for p2 in c.p.self_and_parents():
                            p2.contract()
                            redraw = True
                    for p2 in p.parents():
                        if not p2.isExpanded():
                            p2.expand()
                            redraw = True
                    if redraw:
                        c.redraw(p)
                    else:
                        c.selectPosition(p)
                    w.setSelectionRange(i,j,insert=j)
                    break
        except Exception:
            g.es_exception()
        return alts, word
    #@+node:ekr.20051025071455.47: *6* findNextWord (spellTab)
    def findNextWord(self,p):
        """Scan for the next word, leaving the result in the work widget"""

        trace = False and not g.unitTesting
        c = self.c ; p = p.copy()
        while 1:
            s = self.workCtrl.getAllText()
            i = self.workCtrl.getInsertPoint()
            while i < len(s) and not g.isWordChar1(s[i]):
                i += 1
            # g.trace('p',p and p.h,'i',i,'len(s)',len(s))
            if i < len(s):
                # A non-empty word has been found.
                j = i
                while j < len(s) and g.isWordChar(s[j]):
                    j += 1
                word = s[i:j]
                # This trace verifies that all words have been checked.
                # g.trace(repr(word))
                for w in (self.workCtrl,c.frame.body.bodyCtrl):
                    c.widgetWantsFocusNow(w)
                    w.setSelectionRange(i,j,insert=j)
                if trace: g.trace(i,j,word,p.h)
                return i,j,p,word
            else:
                # End of the body text.
                p.moveToThreadNext()
                if not p: break
                self.workCtrl.delete(0,'end')
                self.workCtrl.insert(0,p.b)
                for w in (self.workCtrl,c.frame.body.bodyCtrl):
                    c.widgetWantsFocusNow(w)
                    w.setSelectionRange(0,0,insert=0)
                if trace: g.trace(0,0,'-->',p.h)

        return None,None,None,None
    #@+node:ekr.20051025121408: *5* hide
    def hide (self,event=None):

        self.c.frame.log.selectTab('Log')
    #@+node:ekr.20051025071455.41: *5* ignore
    def ignore(self,event=None):

        """Ignore the incorrect word for the duration of this spell check session."""
        
        # Bug fix: 2013/05/22.
        if self.loaded:
            w = self.currentWord
            if w:
                self.spellController.ignore(w)
                self.tab.onFindButton()
    #@-others
#@+node:ekr.20100904095239.5914: *3* class EnchantClass
class EnchantClass:

    """A wrapper class for PyEnchant spell checker"""

    #@+others
    #@+node:ekr.20100904095239.5916: *4*  __init__ (EnchantClass)
    def __init__ (self,c):

        """Ctor for the EnchantClass class."""

        self.c = c
        language = g.toUnicode(c.config.getString('enchant_language'))
        # Set the base language
        if language and not enchant.dict_exists(language):
            g.warning('Invalid language code for Enchant',repr(language))
            g.es_print('Using "en_US" instead')
            language = 'en_US'
        # Compute fn, the full path to the local dictionary.
        fn = g.os_path_finalize(
            c.config.getString('enchant_local_dictionary') or
            os.path.join(g.app.loadDir,"..","plugins",'spellpyx.txt'))
        self.open_dict(fn,language)
    #@+node:ekr.20130116142831.10185: *4* clean_dict
    def clean_dict (self,fn):
        
        if g.os_path_exists(fn):
            f = open(fn,mode='rb')
            s = f.read()
            f.close()
            # Blanks lines cause troubles.
            s2 = s.replace(b'\r',b'').replace(b'\n\n',b'\n')
            if s2.startswith(b'\n'): s2 = s2[1:]
            if s != s2:
                g.es_print('cleaning',fn)
                f = open(fn,mode='wb')
                f.write(s2)
                f.close()
    #@+node:ekr.20130915181927.11293: *4* create
    def create (self,fn):
        
        '''Create the given file with empty contents.'''
        try:
            f = open(fn,mode='wb')
            f.close()
            g.note('created: %s' % (fn))
        except IOError:
            g.error('can not create: %s' % (fn))
        except Exception:
            g.error('unexpected error creating: %s' % (fn))
            g.es_exception()
    #@+node:ekr.20100904095239.5927: *4* add
    def add (self,word):

        '''Add a word to the user dictionary.'''

        self.d.add(word)
    #@+node:ekr.20100904095239.5928: *4* ignore
    def ignore (self,word):

        self.d.add_to_session(word)
    #@+node:ekr.20130915181927.11294: *4* open_dict
    def open_dict(self,fn,language):
        
        '''Open or create the dict with the given fn.'''
        
        if not g.os_path_exists(fn):
            # Fix bug 1175013: leo/plugins/spellpyx.txt is both source controlled and customized.
            self.create(fn)
        if g.os_path_exists(fn):
            # Merge the local and global dictionaries.
            try:
                self.clean_dict(fn)
                self.d = enchant.DictWithPWL(language,fn)
            except Exception:
                g.es_exception()
                g.error('not a valid dictionary file',fn)
                self.d = enchant.Dict(language)
        else:
            # A fallback.  Unlikely to happen.
            self.d = enchant.Dict(language)
    #@+node:ekr.20100904095239.5920: *4* processWord
    def processWord(self, word):

        """Check the word. Return None if the word is properly spelled.
        Otherwise, return a list of alternatives."""

        d = self.d 

        if not d:
            return None
        elif d.check(word):
            return None
        else:
            return d.suggest(word)
    #@-others
#@-others
#@-others
#@-leo
