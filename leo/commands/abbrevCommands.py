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
    return g.new_cmd_decorator(name, ['c', 'abbrevCommands',])

#@+others
#@+node:ekr.20160514095531.1: ** class AbbrevCommands
class AbbrevCommandsClass(BaseEditCommandsClass):
    '''
    A class to handle user-defined abbreviations.
    See apropos-abbreviations for details.
    '''
    #@+others
    #@+node:ekr.20150514043850.2: *3* abbrev.Birth
    #@+node:ekr.20150514043850.3: *4* abbrev.ctor
    def __init__(self, c):
        '''Ctor for AbbrevCommandsClass class.'''
        # pylint: disable=super-init-not-called
        self.c = c
        # Set local ivars.
        self.abbrevs = {} # Keys are names, values are (abbrev,tag).
        self.daRanges = []
        self.dynaregex = re.compile(# For dynamic abbreviations
            r'[%s%s\-_]+' % (string.ascii_letters, string.digits))
            # Not a unicode problem.
        self.n_regex = re.compile(r'(?<!\\)\\n') # to replace \\n but not \\\\n
        self.expanding = False # True: expanding abbreviations.
        self.event = None
        self.last_hit = None # Distinguish between text and tree abbreviations.
        self.root = None # The root of tree abbreviations.
        self.save_ins = None # Saved insert point.
        self.save_sel = None # Saved selection range.
        self.store = {'rlist': [], 'stext': ''} # For dynamic expansion.
        self.tree_abbrevs_d = {} # Keys are names, values are (tree,tag).
        self.w = None
    #@+node:ekr.20150514043850.5: *4* abbrev.finishCreate & helpers
    def finishCreate(self):
        '''AbbrevCommandsClass.finishCreate.'''
        self.reload_settings()
        if 0: # Annoying.
            c = self.c
            if (not g.app.initing and not g.unitTesting and
                not g.app.batchMode and not c.gui.isNullGui
            ):
                g.red('Abbreviations %s' % ('on' if c.k.abbrevOn else 'off'))
    #@+node:ekr.20170221035644.1: *5* abbrev.reload_settings & helpers
    def reload_settings(self):
        '''Reload all abbreviation settings.'''
        self.abbrevs = {}
        self.init_settings()
        self.init_abbrev()
        self.init_tree_abbrev()
        self.init_env()

    reloadSettings = reload_settings
    #@+node:ekr.20150514043850.6: *6* abbrev.init_abbrev
    def init_abbrev(self):
        '''
        Init the user abbreviations from @data global-abbreviations
        and @data abbreviations nodes.
        '''
        c = self.c
        table = (
            ('global-abbreviations', 'global'),
            ('abbreviations', 'local'),
        )
        for source, tag in table:
            aList = c.config.getData(source, strip_data=False) or []
            abbrev, result = [], []
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
                self.addAbbrevHelper(s, tag)

        # fake the next placeholder abbreviation
        if c.config.getString("abbreviations-next-placeholder"):
            self.addAbbrevHelper("%s=__NEXT_PLACEHOLDER" %
                c.config.getString("abbreviations-next-placeholder"), 'global')
    #@+node:ekr.20150514043850.7: *6* abbrev.init_env
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
            script = script.replace("\r\n", "\n")
            try:
                exec(script, c.abbrev_subst_env, c.abbrev_subst_env)
            except Exception:
                g.es('Error exec\'ing @data abbreviations-subst-env')
                g.es_exception()
        else:
            c.abbrev_subst_start = False
    #@+node:ekr.20150514043850.8: *6* abbrev.init_settings (called from reload_settings)
    def init_settings(self):
        '''Called from AbbrevCommands.reload_settings aka reloadSettings.'''
        c = self.c
        c.k.abbrevOn = c.config.getBool('enable-abbreviations', default=False)
        # Init these here for k.masterCommand.
        c.abbrev_place_end = c.config.getString('abbreviations-place-end')
        c.abbrev_place_start = c.config.getString('abbreviations-place-start')
        c.abbrev_subst_end = c.config.getString('abbreviations-subst-end')
        c.abbrev_subst_env = {'c': c, 'g': g, '_values': {},}
            # The environment for all substitutions.
            # May be augmented in init_env.
        c.abbrev_subst_start = c.config.getString('abbreviations-subst-start')
        # Local settings.
        self.enabled = (
            c.config.getBool('scripting-at-script-nodes') or
            c.config.getBool('scripting-abbreviations'))
        self.globalDynamicAbbrevs = c.config.getBool('globalDynamicAbbrevs')
        self.subst_env = c.config.getData('abbreviations-subst-env', strip_data=False)
    #@+node:ekr.20150514043850.9: *6* abbrev.init_tree_abbrev
    def init_tree_abbrev(self):
        '''Init tree_abbrevs_d from @data tree-abbreviations nodes.'''
        trace = False and not g.unitTesting
        trace_dict = False
        trace_return = False
        c = self.c
        fn = c.shortFileName()
        # Careful. This happens early in startup.
        root = c.rootPosition()
        if not root:
            # if trace and trace_return: g.trace('no root',fn)
            return
        if not c.p:
            c.selectPosition(root)
        if not c.p:
            if trace and trace_return: g.trace('no c.p', fn)
            return
        tree_s = c.config.getOutlineData('tree-abbreviations')
        if not tree_s:
            if trace and trace_return: g.trace('no tree_s', fn)
            return
        # Expand the tree so we can traverse it.
        if not c.canPasteOutline(tree_s):
            if trace: g.trace('bad copied outline', fn)
            return
        c.fileCommands.leo_file_encoding = 'utf-8'
        # As part of #427, disable all redraws.
        try:
            g.app.disable_redraw = True
            d = {}
            self.init_tree_abbrev_helper(d, tree_s)
            self.tree_abbrevs_d = d
        finally:
            g.app.disable_redraw = False
        if trace and trace_dict:
            g.trace(fn)
            for key in sorted(d):
                g.trace(key, '...\n\n', d.get(key))
    #@+node:ekr.20170227062001.1: *7* abbrev.init_tree_abbrev_helper
    def init_tree_abbrev_helper(self, d, tree_s):

        trace = False and not g.unitTesting
        c = self.c
        p = c.fileCommands.getPosFromClipboard(tree_s)
        if not p: return g.trace('no pasted node')
        for s in g.splitLines(p.b):
            if s.strip() and not s.startswith('#'):
                abbrev_name = s.strip()
                for child in p.children():
                    if child.h.strip() == abbrev_name:
                        abbrev_s = c.fileCommands.putLeoOutline(child)
                        if trace: g.trace('define', abbrev_name, len(abbrev_s))
                        d[abbrev_name] = abbrev_s
                        break
                else:
                    g.trace('no definition for %s' % abbrev_name)

    #@+node:ekr.20150514043850.11: *3* abbrev.expandAbbrev & helpers (entry point)
    def expandAbbrev(self, event, stroke):
        '''
        Not a command.  Called from k.masterCommand to expand
        abbreviations in event.widget.

        Words start with '@'.
        '''
        trace = False and not g.unitTesting
        verbose = True
        c, p = self.c, self.c.p
        w = self.editWidget(event, forceFocus=False)
        w_name = g.app.gui.widget_name(w)
        if not w:
            return False
        ch = self.get_ch(event, stroke, w)
        if not ch: return False
        if trace and verbose:
            g.trace('ch: %5r stroke.s: %12r w: %s %s %s' % (
                ch, stroke and stroke.s, id(w), w_name , p.h))
        s, i, j, prefixes = self.get_prefixes(w)
        for prefix in prefixes:
            i, tag, word, val = self.match_prefix(ch, i, j, prefix, s)
            if word:
                # Fix another part of #438.
                if w_name.startswith('head'):
                    if val == '__NEXT_PLACEHOLDER':
                        i = w.getInsertPoint()
                        if i > 0:
                            w.delete(i-1)
                            p.h = w.getAllText()
                    # Do not call c.endEditing here.
                if trace: g.trace('FOUND tag: %r word: %r' % (tag, word))
                break
        else:
            return False
        # 448: Add abbreviations for commands.
        if 0: # This is not worth documenting.
            val, tag = self.abbrevs.get(word, (None, None))
            if val and c.k.commandExists(val):
                if trace: g.trace(word, '==>', val)
                # Execute the command directly, so as not to call this method recursively.
                commandName = val
                func = c.commandsDict.get(commandName)
                c.doCommand(func, commandName, event)
                return
        c.abbrev_subst_env['_abr'] = word
        if tag == 'tree':
            self.root = p.copy()
            self.last_hit = p.copy()
            self.expand_tree(w, i, j, val, word)
        else:
            # Never expand a search for text matches.
            place_holder = '__NEXT_PLACEHOLDER' in val
            if place_holder:
                expand_search = bool(self.last_hit)
            else:
                self.last_hit = None
                expand_search = False
            if trace:
                g.trace('expand_search: %s last_hit: %s' % (
                    expand_search, self.last_hit and self.last_hit.h))
            self.expand_text(w, i, j, val, word, expand_search)
            # Restore the selection range.
            if self.save_ins:
                if trace:  g.trace('RESTORE sel: %s ins: %s' % (
                    self.save_sel, self.save_ins))
                ins = self.save_ins
                # pylint: disable=unpacking-non-sequence
                sel1, sel2 = self.save_sel
                if sel1 == sel2:
                    # New in Leo 5.5
                    self.post_pass()
                else:
                    # some abbreviations *set* the selection range
                    # so only restore non-empty ranges
                    w.setSelectionRange(sel1, sel2, insert=ins)
        return True
    #@+node:ekr.20161121121636.1: *4* abbrev.exec_content
    def exec_content(self, content):
        '''Execute the content in the environment, and return the result.'''
    #@+node:ekr.20150514043850.12: *4* abbrev.expand_text
    def expand_text(self, w, i, j, val, word, expand_search=False):
        '''Make a text expansion at location i,j of widget w.'''
        trace = False and not g.unitTesting
        c = self.c
        if word == c.config.getString("abbreviations-next-placeholder"):
            val = ''
            do_placeholder = True
        else:
            val, do_placeholder = self.make_script_substitutions(i, j, val)
        if trace:
            g.trace('i: %s j: %s val: %r word: %r w: %s %s %s' % (
                i, j, val, word, id(w), g.app.gui.widget_name(w), c.p.h))
        self.replace_selection(w, i, j, val)
        # Search to the end.  We may have been called via a tree abbrev.
        p = c.p.copy()
        if expand_search:
            while p:
                if self.find_place_holder(p, do_placeholder):
                    return
                else:
                    p.moveToThreadNext()
        else:
            self.find_place_holder(p, do_placeholder)
    #@+node:ekr.20150514043850.13: *4* abbrev.expand_tree (entry) & helpers
    def expand_tree(self, w, i, j, tree_s, word):
        '''
        Paste tree_s as children of c.p.
        This happens *before* any substitutions are made.
        '''
        trace = False and not g.unitTesting
        c, u = self.c, self.c.undoer
        if not c.canPasteOutline(tree_s):
            return g.trace('bad copied outline: %s' % tree_s)
        old_p = c.p.copy()
        bunch = u.beforeChangeTree(old_p)
        self.replace_selection(w, i, j, None)
        self.paste_tree(old_p, tree_s)
        # Make all script substitutions first.
        if trace:
            g.trace()
            g.printList([z.h for z in old_p.self_and_subtree()])
        # Original code.  Probably unwise to change it.
        do_placeholder = False
        for p in old_p.self_and_subtree():
            # Search for the next place-holder.
            val, do_placeholder = self.make_script_substitutions(0, 0, p.b)
            if not do_placeholder: p.b = val
        # Now search for all place-holders.
        for p in old_p.subtree():
            if self.find_place_holder(p, do_placeholder):
                break
        u.afterChangeTree(old_p, 'tree-abbreviation', bunch)
    #@+node:ekr.20150514043850.17: *5* abbrev.paste_tree
    def paste_tree(self, old_p, s):
        '''Paste the tree corresponding to s (xml) into the tree.'''
        c = self.c
        c.fileCommands.leo_file_encoding = 'utf-8'
        p = c.pasteOutline(s=s, redrawFlag=False, undoFlag=False)
        if p:
            # Promote the name node, then delete it.
            p.moveToLastChildOf(old_p)
            c.selectPosition(p)
            c.promote(undoFlag=False)
            p.doDelete()
            c.redraw(old_p) # 2017/02/27: required.
        else:
            g.trace('paste failed')
    #@+node:ekr.20150514043850.14: *4* abbrev.find_place_holder
    def find_place_holder(self, p, do_placeholder):
        '''
        Search for the next place-holder.
        If found, select the place-holder (without the delims).
        '''
        trace = False and not g.unitTesting
        c = self.c
        # Do #438: Search for placeholder in headline.
        s = p.h
        if do_placeholder or c.abbrev_place_start and c.abbrev_place_start in s:
            if trace: g.trace(repr(s))
            new_s, i, j = self.next_place(s, offset=0)
            if i is not None:
                if trace: g.trace('found in headline', p.h)
                p.h = new_s
                c.redraw(p)
                c.editHeadline()
                w = c.edit_widget(p)
                if trace: g.trace(id(w))
                w.setSelectionRange(i, j, insert=j)
                return True
        s = p.b
        if do_placeholder or c.abbrev_place_start and c.abbrev_place_start in s:
            new_s, i, j = self.next_place(s, offset=0)
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
            c.frame.body.onBodyChanged(undoType='Typing', oldSel=oldSel)
            c.p.b = new_s
            if switch:
                c.redraw()
            w.setSelectionRange(i, j, insert=j)
            if switch:
                w.seeInsertPoint()
            else:
                # Keep the scroll point if possible.
                w.setYScrollPosition(scroll)
                w.seeInsertPoint()
            c.bodyWantsFocusNow()
            return True
        else:
            # Fix bug 453: do nothing here.
                # c.frame.body.forceFullRecolor()
                # c.bodyWantsFocusNow()
            return False
    #@+node:ekr.20150514043850.15: *4* abbrev.make_script_substitutions
    def make_script_substitutions(self, i, j, val):
        '''Make scripting substitutions in node p.'''
        trace = False and not g.unitTesting
        c = self.c
        if not c.abbrev_subst_start:
            if trace: g.trace('no subst_start')
            return val, False
        # Nothing to undo.
        if c.abbrev_subst_start not in val:
            return val, False
        # Perform all scripting substitutions.
        self.save_ins = None
        self.save_sel = None
        while c.abbrev_subst_start in val:
            prefix, rest = val.split(c.abbrev_subst_start, 1)
            content = rest.split(c.abbrev_subst_end, 1)
            if len(content) != 2:
                break
            content, rest = content
            if trace:
                g.trace('**c', c.shortFileName())
                g.trace('**p', c.p.h)
                g.trace('**content', repr(content))
            try:
                self.expanding = True
                c.abbrev_subst_env['x'] = ''
                exec(content, c.abbrev_subst_env, c.abbrev_subst_env)
            except Exception:
                g.es_print('exception evaluating', content)
            finally:
                self.expanding = False
            x = c.abbrev_subst_env.get('x')
            if x is None: x = ''
            val = "%s%s%s" % (prefix, x, rest)
            # Save the selection range.
            w = c.frame.body.wrapper
            self.save_ins = w.getInsertPoint()
            self.save_sel = w.getSelectionRange()
            if trace: g.trace('sel', self.save_sel, 'ins', self.save_ins)
        if val == "__NEXT_PLACEHOLDER":
            # user explicitly called for next placeholder in an abbrev.
            # inserted previously
            val = ''
            do_placeholder = True
        else:
            do_placeholder = False
            # Huh?
            oldSel = i, j
            c.frame.body.onBodyChanged(undoType='Typing', oldSel=oldSel)
        if trace:
            g.trace(do_placeholder, val)
        return val, do_placeholder
    #@+node:ekr.20161121102113.1: *4* abbrev.make_script_substitutions_in_headline
    def make_script_substitutions_in_headline(self, p):
        '''Make scripting substitutions in p.h.'''
        trace = False and not g.unitTesting
        c = self.c
        pattern = re.compile('^(.*)%s(.+)%s(.*)$' % (
            re.escape(c.abbrev_subst_start),
            re.escape(c.abbrev_subst_end),
        ))
        changed = False
        if trace: g.trace(p.h)
        # Perform at most one scripting substition.
        m = pattern.match(p.h)
        if m:
            content = m.group(2)
            if trace: g.trace('MATCH:', m.group(1))
            c.abbrev_subst_env['x'] = ''
            try:
                exec(content, c.abbrev_subst_env, c.abbrev_subst_env)
                x = c.abbrev_subst_env.get('x')
                if x:
                    p.h = "%s%s%s" % (m.group(1), x, m.group(3))
                    changed = True
                elif trace:
                    g.trace('ignoring empty result', p.h)
            except Exception:
                # Leave p.h alone.
                g.trace('scripting error in', p.h)
                g.es_exception()
        return changed
    #@+node:ekr.20161121112837.1: *4* abbrev.match_prefix
    def match_prefix(self, ch, i, j, prefix, s):
        trace = False and not g.unitTesting
        i = j - len(prefix)
        word = g.toUnicode(prefix) + g.toUnicode(ch)
        tag = 'tree'
        val = self.tree_abbrevs_d.get(word)
        if trace: g.trace('word: %r val: %r' % (word, val))
        if not val:
            val, tag = self.abbrevs.get(word, (None, None))
        if val:
            # Require a word match if the abbreviation is itself a word.
            if ch in ' \t\n':
                word = word.rstrip()
            if word.isalnum() and word[0].isalpha():
                if i == 0 or s[i - 1] in ' \t\n':
                    pass
                else:
                    i -= 1
                    word, val = None, None # 2017/03/19.
        else:
            i -= 1
            word, val = None, None
        if trace: g.trace('returns %s word: %r val: %r' % (i, word, val))
        return i, tag, word, val
    #@+node:ekr.20150514043850.16: *4* abbrev.next_place
    def next_place(self, s, offset=0):
        """
        Given string s containing a placeholder like <| block |>,
        return (s2,start,end) where s2 is s without the <| and |>,
        and start, end are the positions of the beginning and end of block.
        """
        trace = False and not g.unitTesting
        c = self.c
        new_pos = s.find(c.abbrev_place_start, offset)
        new_end = s.find(c.abbrev_place_end, offset)
        if (new_pos < 0 or new_end < 0) and offset:
            new_pos = s.find(c.abbrev_place_start)
            new_end = s.find(c.abbrev_place_end)
            if not (new_pos < 0 or new_end < 0):
                g.es("Found earlier placeholder")
        if new_pos < 0 or new_end < 0:
            if trace: g.trace('new_pos', new_pos, 'new_end', new_end)
            return s, None, None
        if trace: g.trace(new_pos, new_end, offset)
        start = new_pos
        place_holder_delim = s[new_pos: new_end + len(c.abbrev_place_end)]
        place_holder = place_holder_delim[
            len(c.abbrev_place_start): -len(c.abbrev_place_end)]
        s2 = s[: start] + place_holder + s[start + len(place_holder_delim):]
        end = start + len(place_holder)
        if trace: g.trace('Found', start, end, repr(s2))
        return s2, start, end
    #@+node:ekr.20161121114504.1: *4* abbrev.post_pass
    def post_pass(self):
        '''The post pass: make script substitutions in all headlines.'''
        trace = False and not g.unitTesting
        c = self.c
        if self.root:
            if trace: g.trace(self.root.h)
            bunch = c.undoer.beforeChangeTree(c.p)
            changed = False
            for p in self.root.self_and_subtree():
                changed2 = self.make_script_substitutions_in_headline(p)
                changed = changed or changed2
            if changed:
                c.undoer.afterChangeTree(c.p, 'tree-post-abbreviation', bunch)
    #@+node:ekr.20150514043850.18: *4* abbrev.replace_selection
    def replace_selection(self, w, i, j, s):
        '''Replace w[i:j] by s.'''
        trace = False and not g.unitTesting
        w_name = g.app.gui.widget_name(w)
        if trace: g.trace(i, j, w_name, repr(s))
        c = self.c
        if i == j:
            abbrev = ''
        else:
            abbrev = w.get(i, j)
            w.delete(i, j)
        if s is not None:
            w.insert(i, s)
        if w_name.startswith('head'):
            pass # Don't set p.h here!
        else:
            # Fix part of #438. Don't leave the headline.
            oldSel = j, j
            c.frame.body.onBodyChanged(undoType='Abbreviation', oldSel=oldSel)
        # Adjust self.save_sel & self.save_ins
        if s is not None and self.save_sel is not None:
            # pylint: disable=unpacking-non-sequence
            i, j = self.save_sel
            ins = self.save_ins
            delta = len(s) - len(abbrev)
            self.save_sel = i + delta, j + delta
            self.save_ins = ins + delta
            if trace: g.trace('SAVE SEL: %r SAVE_INS %r:' % (self.save_ins, self.save_sel))
    #@+node:ekr.20161121111502.1: *4* abbrev_get_ch
    def get_ch(self, event, stroke, w):
        '''Get the ch from the stroke.'''
        ch = g.toUnicode(event and event.char or '')
        if self.expanding: return None
        if w.hasSelection(): return None
        assert g.isStrokeOrNone(stroke), stroke
        if stroke in ('BackSpace', 'Delete'):
            return None
        d = {'Return': '\n', 'Tab': '\t', 'space': ' ', 'underscore': '_'}
        if stroke:
            ch = d.get(stroke.s, stroke.s)
            if len(ch) > 1:
                if (stroke.find('Ctrl+') > -1 or
                    stroke.find('Alt+') > -1 or
                    stroke.find('Meta+') > -1
                ):
                    ch = ''
                else:
                    ch = event.char if event else ''
        else:
            ch = event.char
        return ch
    #@+node:ekr.20161121112346.1: *4* abbrev_get_prefixes
    def get_prefixes(self, w):
        '''Return the prefixes at the current insertion point of w.'''
        # New code allows *any* sequence longer than 1 to be an abbreviation.
        # Any whitespace stops the search.
        s = w.getAllText()
        j = w.getInsertPoint()
        i, prefixes = j - 1, []
        while len(s) > i >= 0 and s[i] not in ' \t\n':
            prefixes.append(s[i: j])
            i -= 1
        prefixes = list(reversed(prefixes))
        if '' not in prefixes:
            prefixes.append('')
        return s, i, j, prefixes
    #@+node:ekr.20150514043850.19: *3* abbrev.dynamic abbreviation...
    #@+node:ekr.20150514043850.20: *4* abbrev.dynamicCompletion C-M-/
    @cmd('dabbrev-completion')
    def dynamicCompletion(self, event=None):
        '''
        dabbrev-completion
        Insert the common prefix of all dynamic abbrev's matching the present word.
        This corresponds to C-M-/ in Emacs.
        '''
        c, p = self.c, self.c.p
        w = self.editWidget(event)
        if not w: return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins1 -= 1
        i, j = g.getWord(s, ins1)
        word = w.get(i, j)
        aList = self.getDynamicList(w, word)
        if not aList: return
        # Bug fix: remove s itself, otherwise we can not extend beyond it.
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix, aList)
        if prefix.strip():
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p, oldYScroll=ypos)
            s = s[: i] + prefix + s[j:]
            w.setAllText(s)
            w.setInsertPoint(i + len(prefix))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p,
                command='dabbrev-completion', bunch=b, dirtyVnodeList=[])
            c.recolor()
    #@+node:ekr.20150514043850.21: *4* abbrev.dynamicExpansion M-/ & helper
    @cmd('dabbrev-expands')
    def dynamicExpansion(self, event=None):
        '''
        dabbrev-expands (M-/ in Emacs).

        Inserts the longest common prefix of the word at the cursor. Displays
        all possible completions if the prefix is the same as the word.
        '''
        trace = False and not g.unitTesting
        w = self.editWidget(event)
        if not w:
            if trace: g.trace('no widget!')
            return
        s = w.getAllText()
        ins = ins1 = w.getInsertPoint()
        if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins1 -= 1
        i, j = g.getWord(s, ins1)
        w.setInsertPoint(j)
            # This allows the cursor to be placed anywhere in the word.
        word = w.get(i, j)
        aList = self.getDynamicList(w, word)
        if not aList:
            if trace: g.trace('empty completion list')
            return
        if word in aList and len(aList) > 1:
            aList.remove(word)
        prefix = functools.reduce(g.longestCommonPrefix, aList)
        prefix = prefix.strip()
        if trace: g.trace(word, prefix, aList)
        self.dynamicExpandHelper(event, prefix, aList, w)
    #@+node:ekr.20150514043850.22: *5* abbrev.dynamicExpandHelper
    def dynamicExpandHelper(self, event, prefix=None, aList=None, w=None):
        '''State handler for dabbrev-expands command.'''
        c, k = self.c, self.c.k
        self.w = w
        if prefix is None: prefix = ''
        prefix2 = 'dabbrev-expand: '
        c.frame.log.deleteTab('Completion')
        g.es('', '\n'.join(aList or []), tabName='Completion')
        # Protect only prefix2 so tab completion and backspace to work properly.
        k.setLabelBlue(prefix2, protect=True)
        k.setLabelBlue(prefix2 + prefix, protect=False)
        k.get1Arg(event, handler=self.dynamicExpandHelper1, tabList=aList, prefix=prefix)

    def dynamicExpandHelper1(self, event):
        trace = False and not g.unitTesting
        c, k = self.c, self.c.k
        p = c.p
        c.frame.log.deleteTab('Completion')
        k.clearState()
        k.resetLabel()
        if k.arg:
            w = self.w
            s = w.getAllText()
            ypos = w.getYScrollPosition()
            b = c.undoer.beforeChangeNodeContents(p, oldYScroll=ypos)
            ins = ins1 = w.getInsertPoint()
            if 0 < ins < len(s) and not g.isWordChar(s[ins]): ins1 -= 1
            i, j = g.getWord(s, ins1)
            word = s[i: j]
            s = s[: i] + k.arg + s[j:]
            if trace: g.trace('ins', ins, 'k.arg', repr(k.arg), 'word', word)
            w.setAllText(s)
            w.setInsertPoint(i + len(k.arg))
            w.setYScrollPosition(ypos)
            c.undoer.afterChangeNodeContents(p,
                command='dabbrev-expand', bunch=b, dirtyVnodeList=[])
            c.recolor()
    #@+node:ekr.20150514043850.23: *4* abbrev.getDynamicList (helper)
    def getDynamicList(self, w, s):
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
    #@+node:ekr.20150514043850.24: *3* abbrev.static abbrevs
    #@+node:ekr.20150514043850.25: *4* abbrev.addAbbrevHelper
    def addAbbrevHelper(self, s, tag=''):
        '''Enter the abbreviation 's' into the self.abbrevs dict.'''
        trace = False and not g.unitTesting
        if not s.strip():
            return
        try:
            d = self.abbrevs
            data = s.split('=')
            # Do *not* strip ws so the user can specify ws.
            name = data[0].replace('\\t', '\t').replace('\\n', '\n')
            val = '='.join(data[1:])
            if val.endswith('\n'): val = val[: -1]
            val = self.n_regex.sub('\n', val).replace('\\\\n', '\\n')
            old, tag = d.get(name, (None, None),)
            if old and old != val and not g.unitTesting:
                g.es_print('redefining abbreviation', name,
                    '\nfrom', repr(old), 'to', repr(val))
            if trace:
                val1 = val if val.find('\n') == -1 else g.splitLines(val)[0]+'...'
                g.trace('%12s %r' % (name, g.truncate(val1,80)))
            d[name] = val, tag
        except ValueError:
            g.es_print('bad abbreviation: %s' % s)
    #@+node:ekr.20150514043850.28: *4* abbrev.killAllAbbrevs
    @cmd('abbrev-kill-all')
    def killAllAbbrevs(self, event):
        '''Delete all abbreviations.'''
        self.abbrevs = {}
    #@+node:ekr.20150514043850.29: *4* abbrev.listAbbrevs
    @cmd('abbrev-list')
    def listAbbrevs(self, event=None):
        '''List all abbreviations.'''
        d = self.abbrevs
        if d:
            g.es_print('Abbreviations...')
            keys = list(d.keys())
            keys.sort()
            for name in keys:
                val, tag = d.get(name)
                val = val.replace('\n', '\\n')
                tag = tag or ''
                tag = tag + ': ' if tag else ''
                g.es_print('', '%s%s=%s' % (tag, name, val))
        else:
            g.es_print('No present abbreviations')
    #@+node:ekr.20150514043850.32: *4* abbrev.toggleAbbrevMode
    @cmd('toggle-abbrev-mode')
    def toggleAbbrevMode(self, event=None):
        '''Toggle abbreviation mode.'''
        k = self.c.k
        k.abbrevOn = not k.abbrevOn
        k.keyboardQuit()
        if not g.unitTesting and not g.app.batchMode:
            g.es('Abbreviations are ' + 'on' if k.abbrevOn else 'off')
    #@-others
#@-others
#@-leo
