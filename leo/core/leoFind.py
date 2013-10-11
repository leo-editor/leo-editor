#@+leo-ver=5-thin
#@+node:ekr.20060123151617: * @file leoFind.py
'''Leo's gui-independent find classes.'''

#@@language python
#@@tabwidth -4
#@@pagewidth 70

import leo.core.leoGlobals as g
import re

#@+<< Theory of operation of find/change >>
#@+node:ekr.20031218072017.2414: ** << Theory of operation of find/change >>
#@@nocolor-node
#@+at
# 
# leoFind.py contains the gui-independant part of all of Leo's
# find/change code.
# 
# Such code is tricky, which is why it should be gui-independent code!
# 
# Here are the governing principles:
# 
# 1. Find and Change commands initialize themselves using only the state
#    of the present Leo window. In particular, the Find class must not
#    save internal state information from one invocation to the next.
#    This means that when the user changes the nodes, or selects new
#    text in headline or body text, those changes will affect the next
#    invocation of any Find or Change command. Failure to follow this
#    principle caused all kinds of problems earlier versions.
#    
#    There is one exception to this rule: we must remember where
#    interactive wrapped searches start.
#    
#    This principle simplifies the code because most ivars do not
#    persist. However, each command must ensure that the Leo window is
#    left in a state suitable for restarting the incremental
#    (interactive) Find and Change commands. Details of initialization
#    are discussed below.
# 
# 2. The Find and Change commands must not change the state of the
#    outline or body pane during execution. That would cause severe
#    flashing and slow down the commands a great deal. In particular,
#    c.selectPosition and c.editPosition must not be called while
#    looking for matches.
# 
# 3. When incremental Find or Change commands succeed they must leave
#    the Leo window in the proper state to execute another incremental
#    command. We restore the Leo window as it was on entry whenever an
#    incremental search fails and after any Find All and Replace All
#    command. Initialization involves setting the self.c, self.v,
#    self.in_headline, self.wrapping and self.s_text ivars.
# 
# Setting self.in_headline is tricky; we must be sure to retain the
# state of the outline pane until initialization is complete.
# Initializing the Find All and Replace All commands is much easier
# because such initialization does not depend on the state of the Leo
# window. Using the same kind of text widget for both headlines and body
# text results in a huge simplification of the code.
# 
# Indeed, the searching code does not know whether it is searching
# headline or body text. The search code knows only that self.s_text is
# a text widget that contains the text to be searched or changed and the
# insert and sel attributes of self.search_text indicate the range of
# text to be searched. Searching headline and body text simultaneously
# is complicated. The selectNextVnode() method handles the many details
# involved by setting self.s_text and its insert and sel attributes.
#@-<< Theory of operation of find/change >>

#@+others
#@+node:ekr.20070105092022.1: ** class searchWidget
class searchWidget:

    '''A class to simulating a hidden Tk Text widget.'''

    def __repr__(self):
        return 'searchWidget id: %s' % (id(self))

    #@+others
    #@+node:ekr.20070105092438: *3* ctor (searchWidget)
    def __init__ (self,*args,**keys):

        # g.trace ('searchWidget',g.callers())

        self.s = ''    # The widget text
        self.i = 0     # The insert point
        self.sel = 0,0 # The selection range
    #@+node:ekr.20070105093138: *3* getters
    def getAllText (self):          return self.s
    def getInsertPoint (self):      return self.i       # Returns Python index.
    def getSelectionRange(self):    return self.sel     # Returns Python indices.

    #@+node:ekr.20070105102419: *3* setters (leoFind)
    def delete(self,i,j=None):
        i = self.toPythonIndex(i)
        if j is None: j = i + 1
        else: j = self.toPythonIndex(j)
        self.s = self.s[:i] + self.s[j:]
        # Bug fix: 2011/11/13: Significant in external tests.
        self.i = i
        self.sel = i,i

    def insert(self,i,s):
        if not s: return
        i = self.toPythonIndex(i)
        self.s = self.s[:i] + s + self.s[i:]
        self.i = i
        self.sel = i,i

    def setAllText (self,s):
        self.s = s
        self.i = 0
        self.sel = 0,0

    def setInsertPoint (self,i):
        self.i = i

    def setSelectionRange (self,i,j,insert=None):
        self.sel = self.toPythonIndex(i),self.toPythonIndex(j)
        if insert is not None:
            self.i = self.toPythonIndex(insert)
    #@+node:ekr.20070105092022.4: *3* toPythonIndex (leoFind)
    def toPythonIndex (self,i):

        return g.toPythonIndex(self.s,i)
    #@-others
#@+node:ekr.20061212084717: ** class leoFind
class leoFind:

    """The base class for Leo's Find commands."""

    #@+others
    #@+node:ekr.20031218072017.3053: *3* leoFind.__init__ & helpers
    def __init__ (self,c,title=None):

        self.c = c
        self.trace = False

        # g.trace('leoFind',c)

        # Spell checkers use this class, so we can't always compute a title.
        if title:
            self.title = title
        else:
            #@+<< compute self.title >>
            #@+node:ekr.20041121145452: *4* << compute self.title >>
            if not c.mFileName:
                s = "untitled"
            else:
                path,s = g.os_path_split(c.mFileName)

            self.title = "Find/Change for %s" %  s
            #@-<< compute self.title >>

        #@+<< init the gui-independent ivars >>
        #@+node:ekr.20031218072017.3054: *4* << init the gui-independent ivars >>
        self.backwardAttempts = 0
        self.wrapPosition = None
        self.onlyPosition = None
        self.find_text = ""
        self.change_text = ""
        self.unstick = False
        self.re_obj = None

        #@+at
        # New in 4.3:
        # - These are the names of leoFind ivars. (no more _flag hack).
        # - There are no corresponding commander ivars to keep in synch (hurray!)
        # - These ivars are inited (in the subclass by init) when this class is created.
        # - These ivars are updated by update_ivars just before doing any find.
        #@@c

        #@+<< do dummy initialization to keep Pychecker happy >>
        #@+node:ekr.20050123164539: *5* << do dummy initialization to keep Pychecker happy >>
        if 1:
            self.batch = None
            self.clone_find_all = None
            self.ignore_case = None
            self.node_only = None
            self.pattern_match = None
            self.search_headline = None
            self.search_body = None
            self.suboutline_only = None
            self.mark_changes = None
            self.mark_finds = None
            self.reverse = None
            self.script_search = None
            self.script_change = None
            self.wrap = None
            self.whole_word = None

        if 1:
            self.change_ctrl = None
            self.find_ctrl = None
            self.frame = None
            self.svarDict = {}
        #@-<< do dummy initialization to keep Pychecker happy >>

        self.intKeys = [
            "batch","ignore_case", "node_only",
            "pattern_match", "search_headline", "search_body",
            "suboutline_only", "mark_changes", "mark_finds", "reverse",
            "script_search","script_change","selection_only",
            "wrap", "whole_word",
        ]

        self.newStringKeys = ["radio-find-type", "radio-search-scope"]

        # Ivars containing internal state...
        self.c = None # The commander for this search.
        self.clone_find_all = False
        self.clone_find_all_flattened = False
        self.p = None # The position being searched.  Never saved between searches!
        self.in_headline = False # True: searching headline text.
        self.s_ctrl = searchWidget() # The search text for this search.
        self.wrapping = False # True: wrapping is enabled.
            # This is _not_ the same as self.wrap for batch searches.

        #@+at
        # Initializing a wrapped search is tricky. The search() method will fail
        # if p==wrapPosition and pos >= wrapPos. selectNextPosition() will fail
        # if p == wrapPosition. We set wrapPos on entry, before the first
        # search. We set wrapPosition in selectNextPosition after the first
        # search fails. We also set wrapPosition on exit if the first search
        # suceeds.
        # 
        # 2011/06/13: wrapPosition must be reset when the find pattern changes.
        #@@c

        self.wrapPosition = None # The start of wrapped searches: persists between calls.
        self.onlyPosition = None # The starting node for suboutline-only searches.
        self.wrapPos = None # The starting position of the wrapped search: persists between calls.
        self.errors = 0
        #@-<< init the gui-independent ivars >>

    def init (self,c):
        self.oops()
    #@+node:ekr.20060123065756.1: *3* Top Level Buttons
    #@+node:ekr.20031218072017.3057: *4* changeAllButton
    # The user has pushed the "Replace All" button from the find panel.

    def changeAllButton(self):

        c = self.c
        self.setup_button()
        c.clearAllVisited() # Clear visited for context reporting.

        if self.script_change:
            self.doChangeAllScript()
        else:
            self.changeAll()
    #@+node:ekr.20031218072017.3056: *4* changeButton
    # The user has pushed the "Change" button from the find panel.

    def changeButton(self):

        self.setup_button()

        if self.script_change:
            self.doChangeScript()
        else:
            self.change()
    #@+node:ekr.20031218072017.3058: *4* changeThenFindButton
    # The user has pushed the "Change Then Find" button from the find panel.

    def changeThenFindButton(self):

        self.setup_button()

        if self.script_change:
            self.doChangeScript()
            if self.script_search:
                self.doFindScript()
            else:
                self.findNext()
        else:
            if self.script_search:
                self.change()
                self.doFindScript()
            else:
                self.changeThenFind()
    #@+node:ekr.20031218072017.3060: *4* findAllButton
    # The user has pushed the "Find All" button from the find panel.

    def findAllButton(self):

        c = self.c
        self.setup_button()
        c.clearAllVisited() # Clear visited for context reporting.

        if self.script_search:
            self.doFindAllScript()
        else:
            self.findAll()
    #@+node:ekr.20031218072017.3059: *4* findButton
    # The user has pushed the "Find" button from the find panel.

    def findButton(self):

        self.setup_button()

        if self.script_search:
            self.doFindScript()
        else:
            self.findNext()
    #@+node:ekr.20031218072017.3065: *4* setup_button
    # Initializes a search when a button is pressed in the Find panel.

    def setup_button(self):

        c = self.c
        self.p = c.p

        c.bringToFront()
        if 0: # We _must_ retain the editing status for incremental searches!
            c.endEditing()

        self.update_ivars()
    #@+node:ekr.20031218072017.3055: *3* Top Level Commands
    #@+node:ekr.20031218072017.3061: *4* changeCommand
    # The user has selected the "Replace" menu item.

    def changeCommand(self,c):

        self.setup_command()

        if self.script_search:
            self.doChangeScript()
        else:
            self.change()
    #@+node:ekr.20031218072017.3062: *4* changeThenFindCommand
    # The user has pushed the "Change Then Find" button from the Find menu.

    def changeThenFindCommand(self,c):

        self.setup_command()

        if self.script_search:
            self.doChangeScript()
            self.doFindScript()
        else:
            self.changeThenFind()
    #@+node:ekr.20051013084200.1: *4* dismiss: defined in subclass class
    def dismiss (self):
        pass
    #@+node:ekr.20031218072017.3063: *4* findNextCommand
    # The user has selected the "Find Next" menu item.

    def findNextCommand(self,c):

        self.setup_command()

        if self.script_search:
            self.doFindScript()
        else:
            self.findNext()
    #@+node:ekr.20031218072017.3064: *4* findPreviousCommand
    # The user has selected the "Find Previous" menu item.

    def findPreviousCommand(self,c):

        self.setup_command()

        self.reverse = not self.reverse

        if self.script_search:
            self.doFindScript()
        else:
            self.findNext()

        self.reverse = not self.reverse
    #@+node:EKR.20040503070514: *4* handleUserClick
    def handleUserClick (self,p):

        """Reset suboutline-only search when the user clicks a headline."""

        try:
            if self.c and self.suboutline_only:
                # g.trace(p)
                self.onlyPosition = p.copy()
        except: pass
    #@+node:ekr.20031218072017.3066: *4* setup_command
    # Initializes a search when a command is invoked from the menu.

    def setup_command(self):

        # g.trace('leoFind')

        if 0: # We _must_ retain the editing status for incremental searches!
            self.c.endEditing()

        self.update_ivars()
    #@+node:ekr.20031218072017.3067: *3* Find/change utils
    #@+node:ekr.20031218072017.2293: *4* batchChange (leoFind) (sets start of replace-all group)
    #@+at This routine performs a single batch change operation, updating the
    # head or body string of p and leaving the result in s_ctrl. We update
    # the body if we are changing the body text of c.currentVnode().
    # 
    # s_ctrl contains the found text on entry and contains the changed text
    # on exit. pos and pos2 indicate the selection. The selection will never
    # be empty. NB: we can not assume that self.p is visible.
    #@@c

    def batchChange (self,pos1,pos2):

        c = self.c ; u = c.undoer
        p = self.p ; w = self.s_ctrl
        # Replace the selection with self.change_text
        if pos1 > pos2: pos1,pos2=pos2,pos1
        s = w.getAllText()
        if pos1 != pos2: w.delete(pos1,pos2)
        w.insert(pos1,self.change_text)
        # Update the selection.
        insert=g.choose(self.reverse,pos1,pos1+len(self.change_text))
        w.setSelectionRange(insert,insert)
        w.setInsertPoint(insert)
        # Update the node
        s = w.getAllText() # Used below.
        if self.in_headline:
            #@+<< change headline >>
            #@+node:ekr.20031218072017.2294: *5* << change headline >>
            if len(s) > 0 and s[-1]=='\n': s = s[:-1]

            if s != p.h:

                undoData = u.beforeChangeNodeContents(p)

                p.initHeadString(s)
                if self.mark_changes:
                    p.setMarked()
                p.setDirty()
                if not c.isChanged():
                    c.setChanged(True)

                u.afterChangeNodeContents(p,'Change Headline',undoData)
            #@-<< change headline >>
        else:
            #@+<< change body >>
            #@+node:ekr.20031218072017.2295: *5* << change body >>
            if len(s) > 0 and s[-1]=='\n': s = s[:-1]

            if s != p.b:

                undoData = u.beforeChangeNodeContents(p)

                c.setBodyString(p,s)
                if self.mark_changes:
                    p.setMarked()
                p.setDirty()
                if not c.isChanged():
                    c.setChanged(True)

                u.afterChangeNodeContents(p,'Change Body',undoData)
            #@-<< change body >>
    #@+node:ekr.20031218072017.3068: *4* change (leoFind)
    def change(self,event=None):

        if self.checkArgs():
            self.initInHeadline()
            self.changeSelection()
    #@+node:ekr.20031218072017.3069: *4* changeAll (leoFind)
    def changeAll(self):

        # g.trace('leoFind',g.callers())

        c = self.c ; u = c.undoer ; undoType = 'Replace All'
        current = c.p
        if not self.checkArgs(): return
        self.initInHeadline()
        saveData = self.save()
        self.initBatchCommands()
        count = 0
        u.beforeChangeGroup(current,undoType)
        while 1:
            pos1, pos2 = self.findNextMatch()
            if pos1 is None: break
            count += 1
            self.batchChange(pos1,pos2)
            # if 0:
                # w = self.s_ctrl
                # s = w.getAllText()
                # i,j = g.getLine(s,pos1)
                # line = s[i:j]
                # self.printLine(line,allFlag=True)
        p = c.p
        u.afterChangeGroup(p,undoType,reportFlag=True)
        g.es("changed:",count,"instances")
        c.redraw(p)
        self.restore(saveData)
    #@+node:ekr.20031218072017.3070: *4* changeSelection (leoFind)
    # Replace selection with self.change_text.
    # If no selection, insert self.change_text at the cursor.

    def changeSelection(self):

        c = self.c ; p = self.p
        bodyCtrl = c.frame.body and c.frame.body.bodyCtrl
        w = g.choose(self.in_headline,c.edit_widget(p),bodyCtrl)
        if not w:
            self.in_headline = False
            w = bodyCtrl
        if not w: return

        oldSel = sel = w.getSelectionRange()
        start,end = sel
        if start > end: start,end = end,start
        if start == end:
            g.es("no text selected") ; return False

        # g.trace(start,end)

        # Replace the selection in _both_ controls.
        start,end = oldSel
        change_text = self.change_text

        # Perform regex substitutions of \1, \2, ...\9 in the change text.
        if self.pattern_match and self.match_obj:
            groups = self.match_obj.groups()
            if groups:
                change_text = self.makeRegexSubs(change_text,groups)
        # change_text = change_text.replace('\\n','\n').replace('\\t','\t')
        change_text = self.replaceBackSlashes(change_text)

        for w2 in (w,self.s_ctrl):
            if start != end: w2.delete(start,end)
            w2.insert(start,change_text)
            w2.setInsertPoint(g.choose(self.reverse,start,start+len(change_text)))

        # Update the selection for the next match.
        w.setSelectionRange(start,start+len(change_text))
        c.widgetWantsFocus(w)

        # No redraws here: they would destroy the headline selection.
        if self.mark_changes:
            p.setMarked()
        if self.in_headline:
            c.frame.tree.onHeadChanged(p,'Change')
        else:
            c.frame.body.onBodyChanged('Change',oldSel=oldSel)

        c.frame.tree.drawIcon(p) # redraw only the icon.

        return True
    #@+node:ekr.20060526201951: *5* makeRegexSubs
    def makeRegexSubs(self,s,groups):

        '''Carefully substitute group[i-1] for \i strings in s.
        The group strings may contain \i strings: they are *not* substituted.'''

        digits = '123456789'
        result = [] ; n = len(s)
        i = j = 0 # s[i:j] is the text between \i markers.
        while j < n:
            k = s.find('\\',j)
            if k == -1 or k + 1 >= n:
                break
            j = k + 1 ; ch = s[j]
            if ch in digits:
                j += 1
                result.append(s[i:k]) # Append up to \i
                i = j
                gn = int(ch)-1
                if gn < len(groups):
                    result.append(groups[gn]) # Append groups[i-1]
                else:
                    result.append('\\%s' % ch) # Append raw '\i'
        result.append(s[i:])
        return ''.join(result)
    #@+node:ekr.20031218072017.3071: *4* changeThenFind (leoFind)
    def changeThenFind(self):

        if not self.checkArgs():
            return

        self.initInHeadline()
        if self.changeSelection():
            self.findNext(False) # don't reinitialize
    #@+node:ekr.20031218072017.2417: *4* doChange...Scrip (leoFind)t
    def doChangeScript (self):

        g.app.searchDict["type"] = "change"
        self.runChangeScript()

    def doChangeAllScript (self):

        """The user has just pressed the Replace All button with script-change box checked.

        N.B. Only this code is executed."""

        g.app.searchDict["type"] = "changeAll"
        while 1:
            self.runChangeScript()
            if not g.app.searchDict.get("continue"):
                break

    def runChangeScript (self):

        try:
            assert(self.script_change)
            exec(self.change_text,{},{})
        except Exception:
            g.es("exception executing change script")
            g.es_exception(full=False)
            g.app.searchDict["continue"] = False # 2/1/04
    #@+node:ekr.20031218072017.3072: *4* doFind...Script (leoFind)
    def doFindScript (self):

        g.app.searchDict["type"] = "find"
        self.runFindScript()

    def doFindAllScript (self):

        """The user has just pressed the Find All button with script-find radio button checked.

        N.B. Only this code is executed."""

        g.app.searchDict["type"] = "findAll"
        while 1:
            self.runFindScript()
            if not g.app.searchDict.get("continue"):
                break

    def runFindScript (self):

        try:
            exec(self.find_text,{},{})
        except:
            g.es("exception executing find script")
            g.es_exception(full=False)
            g.app.searchDict["continue"] = False # 2/1/04
    #@+node:ekr.20031218072017.3073: *4* findAll & helper (leoFind)
    def findAll(self):

        trace = False and not g.unitTesting
        c = self.c ; w = self.s_ctrl ; u = c.undoer
        undoType = 'Clone Find All Flattened' if self.clone_find_all_flattened else 'Clone Find All'
        if not self.checkArgs():
            return
        self.initInHeadline()
        if self.clone_find_all:
            self.p = None # Restore will select the root position.
        data = self.save()
        self.initBatchCommands()
        skip = {} # Nodes that should be skipped.
            # Keys are vnodes, values not important.
        count,found = 0,None
        if trace: g.trace(self.clone_find_all_flattened,self.p)
        while 1:
            pos, newpos = self.findNextMatch() # sets self.p.
            if pos is None: break
            if self.clone_find_all and self.p.v in skip:
                continue
            count += 1
            s = w.getAllText()
            i,j = g.getLine(s,pos)
            line = s[i:j]
            if self.clone_find_all:
                if not skip:
                    undoData = u.beforeInsertNode(c.p)
                    found = self.createCloneFindAllNode()
                if self.clone_find_all_flattened:
                    skip[self.p.v] = True
                else:
                    # Don't look at the node or it's descendants.
                    for p2 in self.p.self_and_subtree():
                        skip[p2.v] = True
                # Create a clone of self.p under the find node.
                p2 = self.p.clone()
                p2.moveToLastChildOf(found)
            else:
                self.printLine(line,allFlag=True)

        if self.clone_find_all and skip:
            u.afterInsertNode(found,undoType,undoData,dirtyVnodeList=[])
            c.selectPosition(found)
            c.setChanged(True)

        self.restore(data)
        c.redraw()
        g.es("found",count,"matches")
    #@+node:ekr.20051113110735: *5* createCloneFindAllNode
    def createCloneFindAllNode(self):

        c = self.c
        oldRoot = c.rootPosition()
        found = oldRoot.insertAfter()
        found.moveToRoot(oldRoot)
        c.setHeadString(found,'Found: ' + self.find_text)
        return found
    #@+node:ekr.20031218072017.3074: *4* findNext (leoFind)
    def findNext(self,initFlag=True):

        # c = self.c
        if not self.checkArgs():
            return

        if initFlag:
            self.initInHeadline()
            data = self.save()
            self.initInteractiveCommands()
        else:
            data = self.save()

        pos, newpos = self.findNextMatch()

        if pos is None:
            if self.wrapping:
                g.es("end of wrapped search")
            else:
                g.es("not found","'%s'" % (self.find_text))
            self.restore(data)
        else:
            self.showSuccess(pos,newpos)
    #@+node:ekr.20031218072017.3075: *4* findNextMatch (leoFind)
    # Resumes the search where it left off.
    # The caller must call set_first_incremental_search or set_first_batch_search.

    def findNextMatch(self):

        trace = False and not g.unitTesting
        c = self.c ; p = self.p

        if trace: g.trace('entry','p',p and p.h,
            'search_headline',self.search_headline,
            'search_body',self.search_body)

        if not self.search_headline and not self.search_body:
            if trace: g.trace('nothing to search')
            return None, None

        if len(self.find_text) == 0:
            if trace: g.trace('no find text')
            return None, None

        self.errors = 0
        attempts = 0
        self.backwardAttempts = 0

        # New in Leo 4.4.8: precompute the regexp for regexHelper.
        if self.pattern_match:
            try: # Precompile the regexp.
                flags = re.MULTILINE
                if self.ignore_case: flags |= re.IGNORECASE
                # New in Leo 4.5: escape the search text.
                b,s = '\\b',self.find_text
                if self.whole_word:
                    if not s.startswith(b): s = b + s
                    if not s.endswith(b): s = s + b
                # g.trace(self.whole_word,repr(s))

                self.re_obj = re.compile(s,flags)
                # self.re_obj = re.compile(re.escape(self.find_text),flags)
            except Exception:
                g.warning('invalid regular expression:',self.find_text)
                self.errors += 1 # Abort the search.
                return None,None

        while p:
            pos, newpos = self.search()
            if trace: g.trace('attempt','pos',pos,'p',p.h,'in_headline',self.in_headline)
            if pos is not None:
                if self.mark_finds:
                    p.setMarked()
                    c.frame.tree.drawIcon(p) # redraw only the icon.
                if trace: g.trace('success',pos,newpos)
                return pos, newpos
            elif self.errors:
                g.trace('find errors')
                return None,None # Abort the search.
            elif self.node_only:
                # Bug fix: 2009-5-31.
                # Attempt to switch from headline to body.
                if self.in_headline:
                    self.in_headline = False
                    self.initNextText()
                else: 
                    if trace: g.trace('fail: node only')
                    return None,None # We are only searching one node.
            else:
                if trace: g.trace('failed attempt',p)
                attempts += 1
                p = self.p = self.selectNextPosition()

        if trace: g.trace('attempts',attempts,'backwardAttempts',self.backwardAttempts)
        return None, None
    #@+node:ekr.20031218072017.3076: *4* resetWrap (leoFind)
    def resetWrap (self,event=None):

        self.wrapPosition = None
        self.onlyPosition = None
    #@+node:ekr.20031218072017.3077: *4* search & helpers (leoFind)
    def search (self):

        """Search s_ctrl for self.find_text under the control of the
        whole_word, ignore_case, and pattern_match ivars.

        Returns (pos, newpos) or (None,None)."""

        trace = False and not g.unitTesting
        # c = self.c
        p = self.p
        w = self.s_ctrl
        index = w.getInsertPoint()
        s = w.getAllText()

        if trace: g.trace(index,repr(s[index:index+20]))
        stopindex = g.choose(self.reverse,0,len(s)) # 'end' doesn't work here.
        pos,newpos = self.searchHelper(s,index,stopindex,self.find_text,
            backwards=self.reverse,nocase=self.ignore_case,
            regexp=self.pattern_match,word=self.whole_word)

        if trace: g.trace('pos,newpos',pos,newpos)
        if pos == -1:
            if trace: g.trace('** pos is -1',pos,newpos)
            return None,None
        #@+<< fail if we are passed the wrap point >>
        #@+node:ekr.20060526140328: *5* << fail if we are passed the wrap point >>
        if self.wrapping and self.wrapPos is not None and self.wrapPosition and p == self.wrapPosition:

            if self.reverse and pos < self.wrapPos:
                if trace: g.trace("** reverse wrap done",pos,newpos)
                return None, None

            if not self.reverse and newpos > self.wrapPos:
                if trace: g.trace('** wrap done',pos,newpos)
                return None, None
        #@-<< fail if we are passed the wrap point >>
        insert = g.choose(self.reverse,min(pos,newpos),max(pos,newpos))
        w.setSelectionRange(pos,newpos,insert=insert)

        if trace: g.trace('** returns',pos,newpos)
        return pos,newpos
    #@+node:ekr.20060526081931: *5* searchHelper & allies
    def searchHelper (self,s,i,j,pattern,backwards,nocase,regexp,word,swapij=True):

        trace = self.trace

        if swapij and backwards: i,j = j,i

        if trace: g.trace('back,nocase,regexp,word,',
            backwards,nocase,regexp,word,i,j,repr(s[i:i+20]))

        if not s[i:j] or not pattern:
            if trace: g.trace('empty',i,j,'len(s)',len(s),'pattern',pattern)
            return -1,-1

        if regexp:
            pos,newpos = self.regexHelper(s,i,j,pattern,backwards,nocase)
        elif backwards:
            pos,newpos = self.backwardsHelper(s,i,j,pattern,nocase,word)
        else:
            pos,newpos = self.plainHelper(s,i,j,pattern,nocase,word)

        if trace: g.trace('returns',pos,newpos)
        return pos,newpos
    #@+node:ekr.20060526092203: *6* regexHelper
    def regexHelper (self,s,i,j,pattern,backwards,nocase):

        re_obj = self.re_obj # Use the pre-compiled object
        if not re_obj:
            g.trace('can not happen: no re_obj')
            return -1,-1

        if backwards: # Scan to the last match.  We must use search here.
            last_mo = None ; i = 0
            while i < len(s):
                mo = re_obj.search(s,i,j)
                if not mo: break
                i += 1 ; last_mo = mo
            mo = last_mo
        else:
            mo = re_obj.search(s,i,j)

        if 0:
            g.trace('i',i,'j',j,'s[i:j]',repr(s[i:j]),
                'mo.start',mo and mo.start(),'mo.end',mo and mo.end())

        while mo and 0 <= i < len(s):
            if mo.start() == mo.end():
                if backwards:
                    # Search backward using match instead of search.
                    i -= 1
                    while 0 <= i < len(s):
                        mo = re_obj.match(s,i,j)
                        if mo: break
                        i -= 1
                else:
                    i += 1 ; mo = re_obj.search(s,i,j)
            else:
                self.match_obj = mo
                return mo.start(),mo.end()
        self.match_obj = None
        return -1,-1
    #@+node:ekr.20060526140744: *6* backwardsHelper
    debugIndices = []

    #@+at
    # rfind(sub [,start [,end]])
    # 
    # Return the highest index in the string where substring sub is found, such that
    # sub is contained within s[start,end]. Optional arguments start and end are
    # interpreted as in slice notation. Return -1 on failure.
    #@@c

    def backwardsHelper (self,s,i,j,pattern,nocase,word):

        debug = False
        if nocase:
            s = s.lower() ; pattern = pattern.lower() # Bug fix: 10/5/06: At last the bug is found!
        pattern = self.replaceBackSlashes(pattern)
        n = len(pattern)

        if i < 0 or i > len(s) or j < 0 or j > len(s):
            g.trace('bad index: i = %s, j = %s' % (i,j))
            i = 0 ; j = len(s)

        if debug and (s and i == 0 and j == 0):
            g.trace('two zero indices')

        self.backwardAttempts += 1

        # short circuit the search: helps debugging.
        if s.find(pattern) == -1:
            if debug:
                self.debugCount += 1
                if self.debugCount < 50:
                    g.trace(i,j,'len(s)',len(s),self.p.h)
            return -1,-1

        if word:
            while 1:
                k = s.rfind(pattern,i,j)
                if debug: g.trace('**word** %3s %3s %5s -> %s %s' % (i,j,g.choose(j==len(s),'(end)',''),k,self.p.h))
                if k == -1: return -1, -1
                if self.matchWord(s,k,pattern):
                    return k,k+n
                else:
                    j = max(0,k-1)
        else:
            k = s.rfind(pattern,i,j)
            if debug: g.trace('%3s %3s %5s -> %s %s' % (i,j,g.choose(j==len(s),'(end)',''),k,self.p.h))
            if k == -1:
                return -1, -1
            else:
                return k,k+n
    #@+node:ekr.20060526093531: *6* plainHelper
    def plainHelper (self,s,i,j,pattern,nocase,word):

        trace = self.trace

        # if trace: g.trace(i,j,repr(s[i:i+20]),'pattern',repr(pattern),'word',repr(word))
        if trace: g.trace(i,j,repr(s[i:i+20]))

        if nocase:
            s = s.lower() ; pattern = pattern.lower()
        pattern = self.replaceBackSlashes(pattern)
        n = len(pattern)
        if word:
            while 1:
                k = s.find(pattern,i,j)
                # g.trace(k,n)
                if k == -1:
                    if trace: g.trace('no match word',i)
                    return -1, -1
                elif self.matchWord(s,k,pattern):
                    if trace: g.trace('match word',k)
                    return k, k + n
                else: i = k + n
        else:
            k = s.find(pattern,i,j)
            if k == -1:
                if trace: g.trace('no match word',i)
                return -1, -1
            else:
                if trace: g.trace('match', k)
                return k, k + n
    #@+node:ekr.20060526140744.1: *6* matchWord
    def matchWord(self,s,i,pattern):

        trace = self.trace

        pattern = self.replaceBackSlashes(pattern)
        if not s or not pattern or not g.match(s,i,pattern):
            if trace: g.trace('empty')
            return False

        pat1,pat2 = pattern[0],pattern[-1]
        # n = self.patternLen(pattern)
        n = len(pattern)
        ch1 = 0 <= i-1 < len(s) and s[i-1] or '.'
        ch2 = 0 <= i+n < len(s) and s[i+n] or '.'

        isWordPat1 = g.isWordChar(pat1)
        isWordPat2 = g.isWordChar(pat2)
        isWordCh1 = g.isWordChar(ch1)
        isWordCh2 = g.isWordChar(ch2)

        # g.trace('i',i,'ch1,ch2,pat',repr(ch1),repr(ch2),repr(pattern))

        inWord = isWordPat1 and isWordCh1 or isWordPat2 and isWordCh2
        if trace: g.trace('returns',not inWord)
        return not inWord

    #@+node:ekr.20070105165924: *6* replaceBackSlashes
    def replaceBackSlashes (self,s):

        '''Carefully replace backslashes in a search pattern.'''

        # This is NOT the same as s.replace('\\n','\n').replace('\\t','\t').replace('\\\\','\\')
        # because there is no rescanning.

        i = 0
        while i + 1 < len(s):
            if s[i] == '\\':
                ch = s[i+1]
                if ch == '\\':
                    s = s[:i] + s[i+1:] # replace \\ by \
                elif ch == 'n':
                    s = s[:i] + '\n' + s[i+2:] # replace the \n by a newline
                elif ch == 't':
                    s = s[:i] + '\t' + s[i+2:] # replace \t by a tab
                else:
                    i += 1 # Skip the escaped character.
            i += 1

        if self.trace: g.trace(repr(s))
        return s
    #@+node:ekr.20031218072017.3081: *4* selectNextPosition (leoFind)
    # Selects the next node to be searched.

    def selectNextPosition(self):

        trace = False and not g.unitTesting
        c = self.c ; p = self.p

        # Start suboutline only searches.
        if self.suboutline_only and not self.onlyPosition:
            # p.copy not needed because the find code never calls p.moveToX.
            # Furthermore, p might be None, so p.copy() would be wrong!
            self.onlyPosition = p 

        # Start wrapped searches.
        if self.wrapping and not self.wrapPosition:
            assert(self.wrapPos != None)
            # p.copy not needed because the find code never calls p.moveToX.
            # Furthermore, p might be None, so p.copy() would be wrong!
            self.wrapPosition = p 

        if self.in_headline and self.search_body:
            # just switch to body pane.
            self.in_headline = False
            self.initNextText()
            if trace: g.trace('switching to body',g.callers(5))
            return p

        if self.reverse: p = p.threadBack()
        else:            p = p.threadNext()

        # if trace: g.trace(p and p.h or 'None')

        # New in 4.3: restrict searches to hoisted area.
        # End searches outside hoisted area.
        if c.hoistStack:
            if not p:
                if self.wrapping:
                    g.warning('wrap disabled in hoisted outlines')
                return
            bunch = c.hoistStack[-1]
            if not bunch.p.isAncestorOf(p):
                g.warning('found match outside of hoisted outline')
                return None

        # Wrap if needed.
        if not p and self.wrapping and not self.suboutline_only:
            p = c.rootPosition()
            if self.reverse:
                # Set search_v to the last node of the tree.
                while p and p.next():
                    p = p.next()
                if p: p = p.lastNode()

        # End wrapped searches.
        if self.wrapping and p and p == self.wrapPosition:
            if trace: g.trace("ending wrapped search")
            p = None ; self.resetWrap()

        # End suboutline only searches.
        if (self.suboutline_only and self.onlyPosition and p and
            (p == self.onlyPosition or not self.onlyPosition.isAncestorOf(p))):
            # g.trace("end outline-only")
            p = None ; self.onlyPosition = None

        # p.copy not needed because the find code never calls p.moveToX.
        # Furthermore, p might be None, so p.copy() would be wrong!
        self.p = p # used in initNextText().
        if p: # select p and set the search point within p.
            self.in_headline = self.search_headline
            self.initNextText()
        return p
    #@+node:ekr.20061212095134.1: *3* General utils (leoFind)
    #@+node:ekr.20051020120306.26: *4* bringToFront (leoFind)
    def bringToFront (self):

        """Bring the Find Tab to the front and select the entire find text."""

        c = self.c ; w = self.find_ctrl

        g.trace(g.callers(4))

        c.widgetWantsFocusNow(w)
        # g.app.gui.selectAllText(w)
        w.selectAllText()
        c.widgetWantsFocus(w)
    #@+node:ekr.20061111084423.1: *4* oops (leoFind)
    def oops(self):
        g.pr(("leoFind oops:",
            g.callers(10),"should be overridden in subclass"))
    #@+node:ekr.20051020120306.27: *4* selectAllFindText (leoFind)
    def selectAllFindText (self,event=None):

        # This is called only when the user presses ctrl-a in the find panel.

        w = self.frame.focus_get()
        if g.app.gui.isTextWidget(w):
            w.selectAllText()

        return # (for Tk) "break"
    #@+node:ekr.20031218072017.3082: *3* Initing & finalizing (leoFind)
    #@+node:ekr.20031218072017.3083: *4* checkArgs
    def checkArgs (self):

        val = True
        if not self.search_headline and not self.search_body:
            g.es("not searching headline or body")
            val = False
        if len(self.find_text) == 0:
            g.es("empty find patttern")
            val = False
        return val
    #@+node:ekr.20031218072017.3084: *4* initBatchCommands
    # Initializes for the Find All and Replace All commands.

    def initBatchCommands (self):

        c = self.c
        self.in_headline = self.search_headline # Search headlines first.
        self.errors = 0

        # Select the first node.
        if self.suboutline_only or self.node_only:
            self.p = c.p
        else:
            p = c.rootPosition()
            if self.reverse:
                while p and p.next():
                    p = p.next()
                p = p.lastNode()
            self.p = p

        # Set the insert point.
        self.initBatchText()
    #@+node:ekr.20031218072017.3085: *4* initBatchText, initNextText & init_s_ctrl
    # Returns s_ctrl with "insert" point set properly for batch searches.
    def initBatchText(self,ins=None):
        p = self.p
        self.wrapping = False # Only interactive commands allow wrapping.
        s = g.choose(self.in_headline,p.h, p.b)
        self.init_s_ctrl(s,ins)

    # Call this routine when moving to the next node when a search fails.
    # Same as above except we don't reset wrapping flag.
    def initNextText(self,ins=None):
        c,p = self.c,self.p
        s = g.choose(self.in_headline,p.h, p.b)
        if True:
            tree = c.frame and c.frame.tree
            if tree and hasattr(tree,'killEditing'):
                # g.trace('kill editing before find')
                tree.killEditing()
        self.init_s_ctrl(s,ins)

    def init_s_ctrl (self,s,ins):

        w = self.s_ctrl
        w.setAllText(s)
        if ins is None:
            ins = g.choose(self.reverse,len(s),0)
            # print(g.choose(self.reverse,'.','*'),)
        else:
            pass # g.trace('ins',ins)
        w.setInsertPoint(ins)
    #@+node:ekr.20031218072017.3086: *4* initInHeadline
    # Guesses which pane to start in for incremental searches and changes.
    # This must not alter the current "insert" or "sel" marks.

    def initInHeadline (self):

        trace = False
        c = self.c ; p = self.p

        # Do not change this without careful thought and extensive testing!
        if self.search_headline and self.search_body:
            # A temporary expedient.
            if self.reverse:
                self.in_headline = False
            else:
                editPosition = c.frame.tree.editPosition()
                focus = c.get_focus()
                # Search headline first.
                self.in_headline = (
                    p == editPosition and
                    focus != c.frame.body.bodyCtrl)
                if trace: g.trace(
                    '** p: %s, editPosition: %s, focus: %s, bodyCtrl: %s' % (
                    p and p.h,editPosition,focus, c.frame.body.bodyCtrl))
        else:
            self.in_headline = self.search_headline
    #@+node:ekr.20031218072017.3087: *4* initInteractiveCommands
    def initInteractiveCommands(self):

        c = self.c ; p = self.p
        bodyCtrl = c.frame.body and c.frame.body.bodyCtrl

        w = g.choose(self.in_headline,c.edit_widget(p),bodyCtrl)
        if not w:
            self.in_headline = False
            w = bodyCtrl
        if not w: return

        self.errors = 0

        # We only use the insert point, *never* the selection range.
        ins = w.getInsertPoint()
        # g.trace('ins',ins)
        self.debugCount = 0
        self.initNextText(ins=ins)
        c.widgetWantsFocus(w)

        self.wrapping = self.wrap
        if self.wrap and self.wrapPosition == None:
            self.wrapPos = ins
            # Do not set self.wrapPosition here: that must be done after the first search.
    #@+node:ekr.20031218072017.3088: *4* printLine
    def printLine (self,line,allFlag=False):

        both = self.search_body and self.search_headline
        context = self.batch # "batch" now indicates context

        if allFlag and both and context:
            g.es('','-' * 20,'',self.p.h)
            theType = g.choose(self.in_headline,"head: ","body: ")
            g.es('',theType + line)
        elif allFlag and context and not self.p.isVisited():
            # We only need to print the context once.
            g.es('','-' * 20,'',self.p.h)
            g.es('',line)
            self.p.setVisited()
        else:
            g.es('',line)
    #@+node:ekr.20031218072017.3089: *4* restore
    # Restores the screen after a search fails

    def restore (self,data):

        c = self.c
        in_headline,p,t,insert,start,end = data

        c.frame.bringToFront() # Needed on the Mac

        # Don't try to reedit headline.
        if p:
            c.selectPosition(p)
        else:
            c.selectPosition(c.rootPosition()) # New in Leo 4.5.

        if not in_headline:
            # Looks good and provides clear indication of failure or termination.
            t.setSelectionRange(insert,insert)
            t.setInsertPoint(insert)
            t.seeInsertPoint()

        if 1: # I prefer always putting the focus in the body.
            c.invalidateFocus()
            c.bodyWantsFocus()
            c.k.showStateAndMode(c.frame.body.bodyCtrl)
        else:
            c.widgetWantsFocus(t)
    #@+node:ekr.20031218072017.3090: *4* save (leoFind)
    def save (self):

        c = self.c ; p = self.p

        w = g.choose(self.in_headline,c.edit_widget(p),c.frame.body.bodyCtrl)

        if w:
            insert = w.getInsertPoint()
            sel = w.getSelectionRange()
            if len(sel) == 2:
                start,end = sel
            else:
                start,end = None,None
        else:
            insert,start,end = None,None,None

        return (self.in_headline,p,w,insert,start,end)
    #@+node:ekr.20031218072017.3091: *4* showSuccess (leoFind)
    def showSuccess(self,pos,newpos,showState=True):

        '''Display the result of a successful find operation.'''

        trace = False and not g.unitTesting
        c = self.c ; p = self.p.copy()
        if not p:
            return g.trace('can not happen: self.p is None')

        # Old code.  Not needed now that we always call c.selectPosition.
        # Expand ancestors and set redraw if a redraw is needed.
        # redraw1 = not p.isVisible(c)
        # if c.sparse_find:
            # # Show only the 'sparse' tree when redrawing.
            # for p2 in c.p.self_and_parents():
                # if p2.isAncestorOf(p):
                    # break
                # # 2012/05/29: don't redraw unless we actually contract something.
                # if p2.isExpanded():
                    # p2.contract()
                    # redraw1 = True # Important bug fix. Was redraw = True.

        # redraw2 = c.expandAllAncestors(self.p)
        # redraw = redraw1 or redraw2

        # Set state vars.
        # Ensure progress in backwards searches.
        insert = g.choose(self.reverse,min(pos,newpos),max(pos,newpos))
        if self.wrap and not self.wrapPosition:
            self.wrapPosition = self.p

        if trace: g.trace('in_headline',self.in_headline)

        if self.in_headline:
            c.endEditing() # 2011/06/10: A major bug fix.
            selection = pos,newpos,insert
            c.redrawAndEdit(p,
                selection=selection,
                keepMinibuffer=True)
            w = c.edit_widget(p)
        else:
            w = c.frame.body.bodyCtrl

            # Bug fix: 2012/11/26: *Always* do the full selection logic.
            # This ensures that the body text is inited  and recolored.
            c.selectPosition(p)

            # Old code: fails when setBodyTextAfterSelect does not call w.setAllText.
            # if redraw:
                # c.redraw(p)
            # else:
                # c.selectPosition(p)
                # c.redraw_after_select(p)

            c.bodyWantsFocus()
            if showState:
                c.k.showStateAndMode(w)
            c.bodyWantsFocusNow()
            assert w.getAllText() == p.b.replace('\r','')
            w.setSelectionRange(pos,newpos,insert=insert)
            # w.seeInsertPoint()
            c.outerUpdate()
        return w # Support for isearch.
    #@+node:ekr.20031218072017.1460: *4* update_ivars (leoFind)
    # New in Leo 4.4.3: This is now gui-independent code.

    def update_ivars (self):

        """Called just before doing a find to update ivars from the find panel."""

        trace = False and not g.unitTesting

        self.p = self.c.p
        self.v = self.p.v

        for key in self.intKeys:
            val = self.svarDict[key].get()
            # if trace: g.trace(self.svarDict.get(key),val)
            setattr(self, key, val) # No more _flag hack.

        # Set ivars from radio buttons. Convert these to 1 or 0.
        search_scope = self.svarDict["radio-search-scope"].get()
        # g.trace('radio-search-scope',search_scope)
        self.suboutline_only = g.choose(search_scope == "suboutline-only",1,0)
        self.node_only       = g.choose(search_scope == "node-only",1,0)
        self.selection       = g.choose(search_scope == "selection-only",1,0)

        # New in 4.3: The caller is responsible for removing most trailing cruft.
        # Among other things, this allows Leo to search for a single trailing space.
        s = self.find_ctrl.getAllText()
        s = g.toUnicode(s)
        if trace: g.trace('find',repr(s),self.find_ctrl)
        if s and s[-1] in ('\r','\n'):
            s = s[:-1]

        # 2011/06/13: clear wrap_pos if the find_text changes.
        if s != self.find_text:
            # g.trace('clearing self.wrap_pos')
            self.wrapPosition = None
        self.find_text = s

        s = self.change_ctrl.getAllText()
        if s and s[-1] in ('\r','\n'):
            s = s[:-1]
        s = g.toUnicode(s)
        self.change_text = s
        if trace: g.trace('change',repr(s))
    #@-others
#@+node:ekr.20051020120306.6: ** class findTab (leoFind)
class findTab (leoFind):

    '''An adapter class that implements Leo's Find tab.'''

    #@+others
    #@+node:ekr.20051020120306.11: *3* __init__ & initGui (findTab)
    def __init__(self,c,parentFrame):

        # g.trace('***findTab',c)
        # Init the base class...
        leoFind.__init__(self,c,title='Find Tab')
        self.c = c
        self.parentFrame = parentFrame
        self.frame = self.outerFrame = self.top = None
        self.optionsOnly = c.config.getBool('show_only_find_tab_options')
        # These are created later.
        self.find_ctrl = None
        self.change_ctrl = None 
        self.outerScrolledFrame = None
        self.initGui()
        self.init(c) # New in 4.3: init only once.
    #@+node:ekr.20060221074900: *3* Callbacks
    #@+node:ekr.20060221074900.1: *4* findButtonCallback
    def findButtonCallback(self,event=None):

        self.findButton()
        return # (for Tk) 'break'
    #@+node:ekr.20051020120306.25: *4* hideTab
    def hideTab (self,event=None):

        c = self.c
        c.frame.log.selectTab('Log')
        c.bodyWantsFocus()
    #@+node:ekr.20051024192602: *3*  Top level
    #@+node:ekr.20051024192642.3: *4* change/ThenFindCommand
    def changeCommand (self,event=None):

        self.setup_command()
        self.change()

    def changeThenFindCommand(self,event=None):

        self.setup_command()
        self.changeThenFind()
    #@+node:ekr.20070105123638: *4* changeAllCommand
    def changeAllCommand (self,event=None):

        self.setup_command()
        self.changeAll()
    #@+node:ekr.20060128075225: *4* cloneFindAllCommand & cloneFindAllFlattenedCommand
    def cloneFindAllCommand (self,event=None):

        self.setup_command()
        self.clone_find_all = True
        self.findAll()
        self.clone_find_all = False

    def cloneFindAllFlattenedCommand (self,event=None):

        self.setup_command()
        self.clone_find_all = True
        self.clone_find_all_flattened = True
        self.findAll()
        self.clone_find_all = False
        self.clone_find_all_flattened = False
    #@+node:ekr.20060204120158.1: *4* findAgainCommand
    def findAgainCommand (self):

        s = self.find_ctrl.getAllText()

        if s and s != '<find pattern here>':
            self.findNextCommand()
            return True
        else:
            # Tell the caller that to get the find args.
            return False
    #@+node:ekr.20060209064832: *4* findAllCommand
    def findAllCommand (self,event=None):

        self.setup_command()
        self.findAll()
    #@+node:ekr.20051024192642.2: *4* findNext/PrefCommand
    def findNextCommand (self,event=None):

        self.setup_command()
        self.findNext()

    def findPrevCommand (self,event=None):

        self.setup_command()
        self.reverse = not self.reverse
        self.findNext()
        self.reverse = not self.reverse
    #@+node:ekr.20061212092124: *3* Defined in subclasses (findTab)
    def createFrame (self,parent):
        self.oops()

    def getOption (self,ivar):
        self.oops()

    def init (self,c):
        self.oops()

    def initGui (self):
        pass # Does not need to be defined in subclasses.

    def setOption (self,ivar,val):
        self.oops()

    def toggleOption (self,ivar):
        self.oops()

    # self.oops is defined in the leoFind class.
    #@-others
#@+node:ekr.20070302090616: ** class nullFindTab class (subclass of findTab)
class nullFindTab (findTab):

    #@+others
    #@+node:ekr.20070302090616.1: *3* Birth (nullFindTab)
    #@+node:ekr.20070302090616.2: *4*  ctor (nullFindTab)
    if 0: # Use the base class ctor.

        def __init__ (self,c,parentFrame):

            findTab.__init__(self,c,parentFrame)
            # Init the base class.
                # Calls initGui, createFrame and init(c), in that order.
    #@+node:ekr.20070302090616.3: *4* initGui (nullFindTab)
    # Called from findTab.ctor.

    def initGui (self):

        self.svarDict = {} # Keys are ivar names, values are svar objects.

        for key in self.intKeys:
            self.svarDict[key] = self.svar() # Was Tk.IntVar.

        for key in self.newStringKeys:
            self.svarDict[key] = self.svar() # Was Tk.StringVar.

        # Bug fix: 2011/11/13: significant for external unit tests.
        # Add the same hack as in the qtGui for the 'entire_outline' radio button.
        self.svarDict['entire-outline'] = self.svar()
    #@+node:ekr.20070302090616.4: *4* init (nullFindTab)
    # Called from findTab.ctor.

    def init (self,c):

        # Separate c.ivars are much more convenient than a svarDict.
        for key in self.intKeys:
            # Get ivars from @settings.
            val = c.config.getBool(key)
            setattr(self,key,val)
            val = g.choose(val,1,0)
            svar = self.svarDict.get(key)
            if svar: svar.set(val)
            #g.trace(key,val)

        #@+<< set find/change widgets >>
        #@+node:ekr.20070302090616.5: *5* << set find/change widgets >>
        self.find_ctrl.delete(0,"end")
        self.change_ctrl.delete(0,"end")

        # Get setting from @settings.
        for w,setting,defaultText in (
            (self.find_ctrl,"find_text",'<find pattern here>'),
            (self.change_ctrl,"change_text",''),
        ):
            s = c.config.getString(setting)
            if not s: s = defaultText
            w.insert("end",s)
        #@-<< set find/change widgets >>
        #@+<< set radio buttons from ivars >>
        #@+node:ekr.20070302090616.6: *5* << set radio buttons from ivars >>
        # In Tk, setting the var also sets the widget.
        # Here, we do so explicitly.
        # d = self.widgetsDict
        for ivar,key in (
            ("pattern_match","pattern-search"),
            #("script_search","script-search")
        ):
            svar = self.svarDict[ivar].get()
            if svar:
                self.svarDict["radio-find-type"].set(key)
                # w = d.get(key)
                # if w: w.set(True)
                break
        else:
            self.svarDict["radio-find-type"].set("plain-search")

        for ivar,key in (
            ("suboutline_only","suboutline-only"),
            ("node_only","node-only"),
            # ("selection_only","selection-only")
        ):
            svar = self.svarDict[ivar].get()
            if svar:
                self.svarDict["radio-search-scope"].set(key)
                break
        else:
            key = ivar = 'entire-outline'
            svar = self.svarDict[ivar].get()
            if svar:
                self.svarDict["radio-search-scope"].set(key)
            # self.svarDict["radio-search-scope"].set(key)
            # w = self.widgetsDict.get(key)
            # if w: w.set(True)
        #@-<< set radio buttons from ivars >>
        #@+<< set checkboxes from ivars >>
        #@+node:ekr.20070302090616.7: *5* << set checkboxes from ivars >>
        for ivar in (
            'ignore_case',
            'mark_changes',
            'mark_finds',
            'pattern_match',
            'reverse',
            'search_body',
            'search_headline',
            'whole_word',
            'wrap',
        ):
            # Bug fix: 2011/11/13: significant for external unit tests.
            svar = self.svarDict[ivar]
            if svar:
                svar.set(True)
                # w = self.widgetsDict.get(ivar)
                # if w: w.set(True)
        #@-<< set checkboxes from ivars >>
    #@+node:ekr.20070302090616.9: *4* createFrame (nullFindTab)
    def createFrame (self,parentFrame):

        self.parentFrame = self.top = parentFrame

        self.createFindChangeAreas()
        self.createBoxes()
    #@+node:ekr.20070302090616.10: *5* createFindChangeAreas
    def createFindChangeAreas (self):

        c = self.c

        # A plainTextWidget must be a stringTextWidget
        plainTextWidget = g.app.gui.plainTextWidget

        import leo.core.leoFrame as leoFrame
        assert issubclass(plainTextWidget,leoFrame.stringTextWidget)

        self.find_ctrl   = plainTextWidget(c,name='find-text')
        self.change_ctrl = plainTextWidget(c,name='change-text')
    #@+node:ekr.20070302090616.12: *5* createBoxes
    def createBoxes (self):

        '''Create two columns of radio buttons & check boxes.'''

        # c = self.c
        # f = self.parentFrame
        self.boxes = []
        self.widgetsDict = {} # Keys are ivars, values are checkboxes or radio buttons.

        data = ( # Leading star denotes a radio button.
            ('Whole &Word', 'whole_word',),
            ('&Ignore Case','ignore_case'),
            ('Wrap &Around','wrap'),
            ('&Reverse',    'reverse'),
            ('Rege&xp',     'pattern_match'),
            ('Mark &Finds', 'mark_finds'),
            ("*&Entire Outline","entire-outline"),
            ("*&Suboutline Only","suboutline-only"),  
            ("*&Node Only","node-only"),
            ('Search &Headline','search_headline'),
            ('Search &Body','search_body'),
            ('Mark &Changes','mark_changes'),
        )

        # Important: changing these controls merely changes entries in self.svarDict.
        # First, leoFind.update_ivars sets the find ivars from self.svarDict.
        # Second, self.init sets the values of widgets from the ivars.
        # inGroup = False
        for label,ivar in data:
            if label.startswith('*'):
                label = label[1:]
                w = self.buttonWidget(label)
                self.widgetsDict[ivar] = w
            else:
                w = self.buttonWidget(label)
                self.widgetsDict[ivar] = w
            self.boxes.append(w)
    #@+node:ekr.20070302090616.14: *5* createButtons (not used)
    def createButtons (self):

        '''Create two columns of buttons.'''
    #@+node:ekr.20070302090616.8: *3* class svar (nullFindTab)
    class svar:

        '''A class like Tk's IntVar and StringVar classes.'''

        def __init__(self):
            self.val = None
        def get (self):
            return self.val
        def set (self,val):
            self.val = val

        SetValue = set # SetValue is the wxWidgets spelling.
    #@+node:ekr.20070302092907: *3* class buttonWidget (nullFindTab)
    class buttonWidget:

        '''A class to simulate a Tk.Button.'''

        def __init__ (self,label):
            self.label = label
            self.val = False

        def __repr (self):
            return 'nullFindTab.buttonWidget: %s' % self.label

        def get (self):
            return self.val

        def set (self,val):
            self.val = val
    #@+node:ekr.20070302090616.16: *3* Options
    # This is the same as the Tk code because we simulate Tk svars.
    #@+node:ekr.20070302090616.17: *4* getOption
    def getOption (self,ivar):

        var = self.svarDict.get(ivar)

        if var:
            val = var.get()
            # g.trace('%s = %s' % (ivar,val))
            return val
        else:
            g.trace('bad ivar name: %s' % ivar)
            return None
    #@+node:ekr.20070302090616.18: *4* setOption
    def setOption (self,ivar,val):

        trace = False and not g.unitTesting

        if ivar in self.intKeys:
            if val is not None:
                var = self.svarDict.get(ivar)
                var.set(val)
                if trace: g.trace('nullFindTab: %s = %s' % (ivar,val))

        elif not g.app.unitTesting:
            g.trace('oops: bad find ivar %s' % ivar)
    #@+node:ekr.20070302090616.19: *4* toggleOption
    def toggleOption (self,ivar):

        if ivar in self.intKeys:
            var = self.svarDict.get(ivar)
            val = not var.get()
            var.set(val)
            # g.trace('%s = %s' % (ivar,val),var)
        else:
            g.trace('oops: bad find ivar %s' % ivar)
    #@-others
#@-others
#@-leo
