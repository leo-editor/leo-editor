# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514035236.1: * @file ../commands/abbrevCommands.py
#@@first

'''Leo's abbreviations commands.'''

#@+<< imports >>
#@+node:ekr.20150514045700.1: ** << imports >> (abbrevCommands.py)
import leo.core.leoGlobals as g

from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass

import functools
import re
import string
#@-<< imports >>

def cmd(name):
    '''Command decorator for the abbrevCommands class.'''
    return g.new_cmd_decorator(name,['c','abbrevCommands',])

class AbbrevCommandsClass(BaseEditCommandsClass):
    '''
    A class to handle user-defined abbreviations.
    See apropos-abbreviations for details.
    '''
    #@+others
    #@+node:ekr.20150514043850.2: ** abbrev.Birth
    #@+node:ekr.20150514043850.3: *3* abbrev.ctor
    def __init__ (self,c):
        '''Ctor for AbbrevCommandsClass class.'''
        self.c = c
        # Set local ivars.
        self.abbrevs = {} # Keys are names, values are (abbrev,tag).
        self.daRanges = []
        self.dynaregex = re.compile( # For dynamic abbreviations
            r'[%s%s\-_]+'%(string.ascii_letters,string.digits))
            # Not a unicode problem.
        self.expanding = False # True: expanding abbreviations.
        self.event = None
        self.globalDynamicAbbrevs = c.config.getBool('globalDynamicAbbrevs')
        self.last_hit = None # Distinguish between text and tree abbreviations.
        self.save_ins = None # Saved insert point.
        self.save_sel = None # Saved selection range.
        self.store ={'rlist':[], 'stext':''} # For dynamic expansion.
        self.tree_abbrevs_d = {} # Keys are names, values are (tree,tag).
        self.w = None
    #@+node:ekr.20150514043850.5: *3* abbrev.finishCreate & helpers
    def finishCreate(self):
        '''AbbrevCommandsClass.finishCreate.'''
        c,k = self.c,self.c.k
        self.init_settings()
        self.init_abbrev()
        self.init_tree_abbrev()
        self.init_env()
        if 0: # Annoying.
            if (not g.app.initing and not g.unitTesting and
                not g.app.batchMode and not c.gui.isNullGui
            ):
                g.red('Abbreviations %s' % ('on' if c.k.abbrevOn else 'off'))
    #@+node:ekr.20150514043850.6: *4* abbrev.init_abbrev
    def init_abbrev(self):
        '''
        Init the user abbreviations from @data global-abbreviations
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
    #@+node:ekr.20150514043850.7: *4* abbrev.init_env
    def init_env(self):
        '''
        Init c.abbrev_subst_env by executing the contents of the
        @data abbreviations-subst-env node.
        '''
        c = self.c
        at = c.atFileCommands
        if c.abbrev_place_start and self.enabled:
            aList = self.subst_env
            script = []
            for z in aList:
                # Compatibility with original design.
                if z.startswith('\\:'):
                    script.append(z[2:])
                else:
                    script.append(z)
            script = ''.join(script)
            # Allow Leo directives in @data abbreviations-subst-env trees.
            import leo.core.leoNodes as leoNodes
            v = leoNodes.VNode(context=c)
            root = leoNodes.Position(v)
            # Similar to g.getScript.
            script = at.writeFromString(
                root=root,
                s=script,
                forcePythonSentinels=True,
                useSentinels=False)
            script = script.replace("\r\n","\n")
            try:
                exec(script,c.abbrev_subst_env,c.abbrev_subst_env)
            except Exception:
                g.es('Error exec\'ing @data abbreviations-subst-env')
                g.es_exception()
        else:
            c.abbrev_subst_start = False
    #@+node:ekr.20150514043850.8: *4* abbrev.init_settings
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
    #@+node:ekr.20150514043850.9: *4* abbrev.init_tree_abbrev
    def init_tree_abbrev (self):
        '''Init tree_abbrevs_d from @data tree-abbreviations nodes.'''
        trace = False
        verbose = True
        c = self.c
        fn = c.shortFileName()
        d = {} # Keys are abbreviation names. Values are (xml) strings.
        # Careful. This happens early in startup.
        root = c.rootPosition()
        if not root:
            # if trace and verbose: g.trace('no root',fn)
            return
        if not c.p:
            c.selectPosition(root)
        if not c.p:
            if trace and verbose: g.trace('no c.p',fn)
            return
        tree_s = c.config.getOutlineData('tree-abbreviations')
        if not tree_s:
            if trace and verbose: g.trace('no tree_s',fn)
            return
        if trace and verbose: g.trace(fn,len(tree_s or ''))
        # Expand the tree so we can traverse it.
        if not c.canPasteOutline(tree_s):
            if trace and verbose: g.trace('bad copied outline',fn)
            return
        c.fileCommands.leo_file_encoding='utf-8'
        old_p = c.p.copy()
        p = c.pasteOutline(s=tree_s,redrawFlag=False,undoFlag=False,tempOutline=True)
        if not p: return g.trace('no pasted node')
        for s in g.splitLines(p.b):
            if s.strip() and not s.startswith('#'):
                abbrev_name = s.strip()
                for child in p.children():
                    if child.h.strip() == abbrev_name:
                        c.selectPosition(child)
                        abbrev_s = c.fileCommands.putLeoOutline()
                        if trace and verbose:
                            g.trace('define',abbrev_name,len(abbrev_s))
                            # g.trace('define',abbrev_name,'\n\n',abbrev_s)
                        d[abbrev_name] = abbrev_s
                        break
                else:
                    g.trace('no definition for %s' % abbrev_name)
        p.doDelete(newNode=old_p)
        c.selectPosition(old_p)
        if trace and (d or verbose):
            if verbose:
                g.trace(fn)
                for key in sorted(d.keys()):
                    g.trace(key,'...\n\n',d.get(key))
            else:
                g.trace(fn,sorted(d.keys()))
        self.tree_abbrevs_d = d
    #@+node:ekr.20150514043850.10: *3* abbrev.reloadAbbreviations
    def reloadAbbreviations(self):
        '''Reload all abbreviations from all files.'''
    #@+node:ekr.20150514043850.11: ** abbrev.expandAbbrev & helpers (entry point)
    def expandAbbrev (self,event,stroke):
        '''
        Not a command.  Called from k.masterCommand to expand
        abbreviations in event.widget.

        Words start with '@'.
        '''
        trace = False and not g.unitTesting
        verbose = False
        c = self.c
        ch = event and event.char or ''
        w = self.editWidget(event,forceFocus=False)
        if not w: return False
        if self.expanding: return False
        if w.hasSelection(): return False
        assert g.isStrokeOrNone(stroke),stroke
        if stroke in ('BackSpace','Delete'):
            if trace and verbose: g.trace(stroke)
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
        if trace and verbose: g.trace('ch',repr(ch),'stroke',repr(stroke))
        # New code allows *any* sequence longer than 1 to be an abbreviation.
        # Any whitespace stops the search.
        s = w.getAllText()
        j = w.getInsertPoint()
        i,prefixes = j-1,[]
        while i >= 0 and s[i] not in ' \t\n':
            prefixes.append(s[i:j])
            i -= 1
        prefixes = list(reversed(prefixes))
        if '' not in prefixes: prefixes.append('')
        for prefix in prefixes:
            i = j - len(prefix)
            word = prefix+ch
            val,tag = self.tree_abbrevs_d.get(word),'tree'
            # if val: g.trace('*****',word,'...\n\n',len(val))
            if not val:
                val,tag = self.abbrevs.get(word,(None,None))
            if val:
                if trace and verbose: g.trace(repr(word),'val',val,'tag',tag)
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
        c.abbrev_subst_env['_abr'] = word
        if tag == 'tree':
            self.last_hit = c.p.copy()
            self.expand_tree(w,i,j,val,word)
            c.frame.body.forceFullRecolor()
            c.bodyWantsFocusNow()
        else:
            # Never expand a search for text matches.
            place_holder = '__NEXT_PLACEHOLDER' in val
            if place_holder:
                expand_search = bool(self.last_hit)
            else:
                self.last_hit = None
                expand_search = False
            if trace: g.trace('expand_search',expand_search,'last_hit',self.last_hit)
            self.expand_text(w,i,j,val,word,expand_search)
            c.frame.body.forceFullRecolor()
            c.bodyWantsFocusNow()
            # Restore the selection range.
            if self.save_ins:
                if trace: g.trace('sel',self.save_sel,'ins',self.save_ins)
                ins = self.save_ins
                # pylint: disable=unpacking-non-sequence
                sel1,sel2 = self.save_sel
                if sel1 != sel2:
                    # some abbreviations *set* the selection range
                    # so only restore non-empty ranges
                    w.setSelectionRange(sel1,sel2,insert=ins)
        return True
    #@+node:ekr.20150514043850.12: *3* abbrev.expand_text
    def expand_text(self,w,i,j,val,word,expand_search=False):
        '''Make a text expansion at location i,j of widget w.'''
        c = self.c
        val,do_placeholder = self.make_script_substitutions(i,j,val)
        self.replace_abbrev_name(w,i,j,val)
        # Search to the end.  We may have been called via a tree abbrev.
        p = c.p.copy()
        if expand_search:
            while p:
                if self.find_place_holder(p,do_placeholder):
                    return
                else:
                    p.moveToThreadNext()
        else:
            self.find_place_holder(p,do_placeholder)
    #@+node:ekr.20150514043850.13: *3* abbrev.expand_tree & helper
    def expand_tree(self,w,i,j,tree_s,word):
        '''Paste tree_s as children of c.p.'''
        c,u = self.c,self.c.undoer
        if not c.canPasteOutline(tree_s):
            return g.trace('bad copied outline: %s' % tree_s)
        old_p = c.p.copy()
        bunch = u.beforeChangeTree(old_p)
        self.replace_abbrev_name(w,i,j,None)
        self.paste_tree(old_p,tree_s)
        # Make all script substitutions first.
        do_placeholder = False
        for p in old_p.subtree():
            # Search for the next place-holder.
            val,do_placeholder = self.make_script_substitutions(0,0,p.b)
            if not do_placeholder: p.b = val
        # Now search for all place-holders.
        for p in old_p.subtree():
            if self.find_place_holder(p,do_placeholder):
                break
        u.afterChangeTree(old_p,'tree-abbreviation',bunch)
    #@+node:ekr.20150514043850.14: *3* abbrev.find_place_holder
    def find_place_holder(self,p,do_placeholder):
        '''
        Search for the next place-holder.
        If found, select the place-holder (without the delims).
        '''
        c = self.c
        s = p.b
        if do_placeholder or c.abbrev_place_start and c.abbrev_place_start in s:
            new_s,i,j = self.next_place(s,offset=0)
            if i is None:
                return False
            w = c.frame.body.wrapper
            switch = p != c.p
            if switch:
                c.selectPosition(p)
            else:
                scroll = w.getYScrollPosition()
            oldSel = w.getSelectionRange()
            w.setAllText(new_s)
            c.frame.body.onBodyChanged(undoType='Typing',oldSel=oldSel)
            c.p.b = new_s
            if switch:
                c.redraw()
            w.setSelectionRange(i,j,insert=j)
            if switch:
                w.seeInsertPoint()
            else:
                # Keep the scroll point if possible.
                w.setYScrollPosition(scroll)
                w.seeInsertPoint()
            return True
        else:
            return False
    #@+node:ekr.20150514043850.15: *3* abbrev.make_script_substitutions
    def make_script_substitutions(self,i,j,val):
        '''Make scripting substitutions in node p.'''
        trace = False and not g.unitTesting
        c = self.c
        if not c.abbrev_subst_start:
            if trace: g.trace('no subst_start')
            return val,False
        # Nothing to undo.
        if c.abbrev_subst_start not in val:
            return val,False
        # Perform all scripting substitutions.
        self.save_ins = None 
        self.save_sel = None 
        while c.abbrev_subst_start in val:
            prefix,rest = val.split(c.abbrev_subst_start,1)
            content = rest.split(c.abbrev_subst_end,1)
            if len(content) != 2:
                break
            content,rest = content
            if trace: g.trace('**content',content)
            try:
                self.expanding = True
                c.abbrev_subst_env['x']=''
                exec(content,c.abbrev_subst_env,c.abbrev_subst_env)
            finally:
                self.expanding = False
            x = c.abbrev_subst_env.get('x')
            if x is None: x = ''
            val = "%s%s%s" % (prefix,x,rest)
            # Save the selection range.
            w = c.frame.body.wrapper
            self.save_ins = w.getInsertPoint()
            self.save_sel = w.getSelectionRange()
            if trace: g.trace('sel',self.save_sel,'ins',self.save_ins)
        if val == "__NEXT_PLACEHOLDER":
            # user explicitly called for next placeholder in an abbrev.
            # inserted previously
            val = ''
            do_placeholder = True
        else:
            do_placeholder = False
            # Huh?
            oldSel = i,j
            c.frame.body.onBodyChanged(undoType='Typing',oldSel=oldSel)
        if trace:
            g.trace(do_placeholder,val)
        return val,do_placeholder
    #@+node:ekr.20150514043850.16: *3* abbrev.next_place
    def next_place(self,s,offset=0):
        """
        Given string s containing a placeholder like <| block |>,
        return (s2,start,end) where s2 is s without the <| and |>,
        and start, end are the positions of the beginning and end of block.
        """
        trace = False
        c = self.c
        new_pos = s.find(c.abbrev_place_start,offset)
        new_end = s.find(c.abbrev_place_end,offset)
        if (new_pos < 0 or new_end < 0) and offset:
            new_pos = s.find(c.abbrev_place_start)
            new_end = s.find(c.abbrev_place_end)
            if not(new_pos < 0 or new_end < 0):
                g.es("Found placeholder earlier in body")
        if new_pos < 0 or new_end < 0:
            if trace: g.trace('new_pos',new_pos,'new_end',new_end)
            return s,None,None
        start = new_pos
        place_holder_delim = s[new_pos:new_end+len(c.abbrev_place_end)]
        place_holder = place_holder_delim[
            len(c.abbrev_place_start):-len(c.abbrev_place_end)]
        s2 = s[:start]+place_holder+s[start+len(place_holder_delim):]
        end = start+len(place_holder)
        if trace: g.trace(start,end,g.callers())
        return s2,start,end
    #@+node:ekr.20150514043850.17: *3* abbrev.paste_tree
    def paste_tree(self,old_p,s):
        '''Paste the tree corresponding to s (xml) into the tree.'''
        c = self.c
        c.fileCommands.leo_file_encoding='utf-8'
        p = c.pasteOutline(s=s,redrawFlag=False,undoFlag=False)
        if p:
            # Promote the name node, then delete it.
            p.moveToLastChildOf(old_p)
            c.selectPosition(p)
            c.promote(undoFlag=False)
            p.doDelete()
        else:
            g.trace('paste failed')
    #@+node:ekr.20150514043850.18: *3* abbrev.replace_abbrev_name
    def replace_abbrev_name(self,w,i,j,s):
        '''Replace the abbreviation name by s.'''
        c = self.c
        if i == j:
            abbrev = ''
        else:
            abbrev = w.get(i,j)
            w.delete(i,j)
        if s is not None:
            w.insert(i,s)
        oldSel = j,j
        c.frame.body.onBodyChanged(undoType='Abbreviation',oldSel=oldSel)
        # Adjust self.save_sel & self.save_ins
        if s is not None and self.save_sel is not None:
            # pylint: disable=unpacking-non-sequence
            i,j = self.save_sel
            ins = self.save_ins
            delta = len(s) - len(abbrev)
            # g.trace('abbrev',abbrev,'s',repr(s),'delta',delta)
            self.save_sel = i+delta,j+delta
            self.save_ins = ins+delta
    #@+node:ekr.20150514043850.19: ** abbrev.dynamic abbreviation...
    #@+node:ekr.20150514043850.20: *3* abbrev.dynamicCompletion C-M-/
    @cmd('dabbrev-completion')
    def dynamicCompletion (self,event=None):
        '''
        dabbrev-completion
        Insert the common prefix of all dynamic abbrev's matching the present word.
        This corresponds to C-M-/ in Emacs.
        '''
        c,p,u = self.c,self.c.p,self.c.p.v.u
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins1 -= 1
        i,j = g.getWord(s,ins1)
        word = w.get(i,j)
        aList = self.getDynamicList(w,word)
        if not aList: return
        # Bug fix: remove s itself, otherwise we can not extend beyond it.
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix,aList)
        if prefix.strip():
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p,oldYScroll=ypos)
            s = s[:i] + prefix + s[j:]
            w.setAllText(s)
            w.setInsertPoint(i+len(prefix))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p,
                command='dabbrev-completion',bunch=b,dirtyVnodeList=[]) 
            c.recolor()
    #@+node:ekr.20150514043850.21: *3* abbrev.dynamicExpansion M-/ & helper
    @cmd('dabbrev-expands')
    def dynamicExpansion (self,event=None):
        '''
        dabbrev-expands (M-/ in Emacs).

        Inserts the longest common prefix of the word at the cursor. Displays
        all possible completions if the prefix is the same as the word.
        '''
        trace = False and not g.unitTesting
        c = self.c
        p = c.p
        w = self.editWidget(event)
        if not w:
            if trace: g.trace('no widget!')
            return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins1 -= 1
        i,j = g.getWord(s,ins1)
        w.setInsertPoint(j)
            # This allows the cursor to be placed anywhere in the word.
        word = w.get(i,j)
        aList = self.getDynamicList(w,word)
        if not aList:
            if trace: g.trace('empty completion list')
            return
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix,aList)
        prefix = prefix.strip()
        if trace: g.trace(word,prefix,aList)
        self.dynamicExpandHelper(event,prefix,aList,w)
    #@+node:ekr.20150514043850.22: *4* abbrev.dynamicExpandHelper
    def dynamicExpandHelper (self,event,prefix=None,aList=None,w=None):
        '''State handler for dabbrev-expands command.'''
        trace = False and not g.unitTesting
        c,k = self.c,self.c.k
        p = c.p
        tag = 'dabbrev-expand'
        state = k.getState(tag)
        if state == 0:
            self.w = w
            prefix2 = 'dabbrev-expand: '
            c.frame.log.deleteTab('Completion')
            g.es('','\n'.join(aList),tabName='Completion')
            # Protect only prefix2.
            # This is required for tab completion and backspace to work properly.
            k.setLabelBlue(prefix2,protect=True)
            k.setLabelBlue(prefix2+prefix,protect=False)
            if trace: g.trace('len(aList)',len(aList))
            k.getArg(event,tag,1,self.dynamicExpandHelper,tabList=aList,prefix=prefix)
        else:
            c.frame.log.deleteTab('Completion')
            k.clearState()
            k.resetLabel()
            if k.arg:
                w = self.w
                s = w.getAllText()
                ypos = w.getYScrollPosition()
                b = c.undoer.beforeChangeNodeContents(p,oldYScroll=ypos)
                ins = ins1 = w.getInsertPoint()
                if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins1 -= 1
                i,j = g.getWord(s,ins1)
                word = s[i:j]
                s = s[:i] + k.arg + s[j:]
                if trace: g.trace('ins',ins,'k.arg',repr(k.arg),'word',word)
                w.setAllText(s)
                w.setInsertPoint(i+len(k.arg))
                w.setYScrollPosition(ypos)
                c.undoer.afterChangeNodeContents(p,
                    command=tag,bunch=b,dirtyVnodeList=[])
                c.recolor()
    #@+node:ekr.20150514043850.23: *3* abbrev.getDynamicList (helper)
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
    #@+node:ekr.20150514043850.24: ** abbrev.static abbrevs
    #@+node:ekr.20150514043850.25: *3* abbrev.addAbbrevHelper
    def addAbbrevHelper (self,s,tag=''):
        '''Enter the abbreviation 's' into the self.abbrevs dict.'''
        if not s.strip():
            return
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
    #@+node:ekr.20150514043850.26: *3* abbrev.addAbbreviation
    @cmd('abbrev-add-global')
    def addAbbreviation (self,event):
        '''
        Add an abbreviation:
        The selected text is the abbreviation.
        The minibuffer prompts you for the name of the abbreviation.
        Also sets abbreviations on.
        '''
        k = self.c.k
        state = k.getState('add-abbr')
        if state == 0:
            self.w = self.editWidget(event)
            if self.w:
                k.setLabelBlue('Add Abbreviation: ')
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
    #@+node:ekr.20150514043850.27: *3* abbrev.addInverseAbbreviation
    @cmd('abbrev-inverse-add-global')
    def addInverseAbbreviation (self,event):
        '''
        Add an inverse abbreviation:
        The selected text is the abbreviation name.
        The minibuffer prompts you for the value of the abbreviation.
        '''
        k = self.c.k
        state = k.getState('add-inverse-abbr')
        if state == 0:
            self.w = self.editWidget(event)
            if self.w:
                k.setLabelBlue('Add Inverse Abbreviation: ')
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
    #@+node:ekr.20150514043850.28: *3* abbrev.killAllAbbrevs
    @cmd('abbrev-kill-all')
    def killAllAbbrevs (self,event):
        '''Delete all abbreviations.'''
        self.abbrevs = {}
    #@+node:ekr.20150514043850.29: *3* abbrev.listAbbrevs
    @cmd('abbrev-list')
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
                tag = tag+': ' if tag else ''
                g.es('','%s%s=%s' % (tag,name,val))
        else:
            g.es('No present abbreviations')
    #@+node:ekr.20150514043850.30: *3* abbrev.readAbbreviations & helper
    @cmd('abbrev-read')
    def readAbbreviations (self,event=None):
        '''Read abbreviations from a file.'''
        c = self.c
        fileName = g.app.gui.runOpenFileDialog(c,
            title = 'Open Abbreviation File',
            filetypes = [("Text","*.txt"), ("All files","*")],
            defaultextension = ".txt")
        if fileName:
            self.readAbbreviationsFromFile(fileName)
    #@+node:ekr.20150514043850.31: *4* abbrev.readAbbreviationsFromFile
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
    #@+node:ekr.20150514043850.32: *3* abbrev.toggleAbbrevMode
    @cmd('toggle-abbrev-mode')
    def toggleAbbrevMode (self,event=None):
        '''Toggle abbreviation mode.'''
        k = self.c.k
        k.abbrevOn = not k.abbrevOn
        k.keyboardQuit()
        if not g.unitTesting and not g.app.batchMode:
            g.es('Abbreviations are ' + 'on' if k.abbrevOn else 'off')
    #@+node:ekr.20150514043850.33: *3* abbrev.writeAbbreviation
    @cmd('abbrev-write')
    def writeAbbreviations (self,event):
        '''Write abbreviations to a file.'''
        c = self.c
        fileName = g.app.gui.runSaveFileDialog(c,
            initialfile = None,
            title='Write Abbreviations',
            filetypes = [("Text","*.txt"), ("All files","*")],
            defaultextension = ".txt")
        if not fileName: return
        try:
            d = self.abbrevs
            f = open(fileName,'w')
            for name in sorted(d.keys()):
                val,tag = self.abbrevs.get(name)
                val=val.replace('\n','\\n')
                s = '%s=%s\n' % (name,val)
                if not g.isPython3:
                    s = g.toEncodedString(s,reportErrors=True)
                f.write(s)
            f.close()
            g.es_print('wrote: %s' % fileName)
        except IOError:
            g.es('can not create',fileName)
    #@-others
#@-leo
