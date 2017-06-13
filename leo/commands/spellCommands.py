# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040239.1: * @file ../commands/spellCommands.py
#@@first
'''Leo's spell-checking commands.'''
#@+<< imports >>
#@+node:ekr.20150514050530.1: ** << imports >> (spellCommands.py)
import re
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
try:
    import enchant
except Exception: # May throw WinError(!)
    enchant = None
#@-<< imports >>

def cmd(name):
    '''Command decorator for the SpellCommandsClass class.'''
    return g.new_cmd_decorator(name, ['c', 'spellCommands',])
#@+others
#@+node:ekr.20150514063305.510: ** class EnchantClass
class EnchantClass(object):
    """A wrapper class for PyEnchant spell checker"""
    #@+others
    #@+node:ekr.20150514063305.511: *3*  __init__ (EnchantClass)
    def __init__(self, c):
        """Ctor for EnchantClass class."""
        # pylint: disable=super-init-not-called
        self.c = c
        language = g.toUnicode(c.config.getString('enchant_language'))
        # Set the base language
        if language and not enchant.dict_exists(language):
            g.warning('Invalid language code for Enchant', repr(language))
            g.es_print('Using "en_US" instead')
            language = 'en_US'
        # Compute fn, the full path to the local dictionary.
        fn = c.config.getString('enchant_local_dictionary')
        if not fn:
            fn = g.os_path_finalize_join(g.app.loadDir, "..", "plugins", 'spellpyx.txt')
        # Fix bug https://github.com/leo-editor/leo-editor/issues/108
        if not g.os_path_exists(fn):
            fn = g.os_path_finalize_join(g.app.homeDir, '.leo', 'spellpyx.txt')
        self.open_dict(fn, language)
    #@+node:ekr.20150514063305.512: *3* add
    def add(self, word):
        '''Add a word to the user dictionary.'''
        self.d.add(word)
    #@+node:ekr.20150514063305.513: *3* clean_dict
    def clean_dict(self, fn):
        if g.os_path_exists(fn):
            f = open(fn, mode='rb')
            s = f.read()
            f.close()
            # Blanks lines cause troubles.
            s2 = s.replace(b'\r', b'').replace(b'\n\n', b'\n')
            if s2.startswith(b'\n'): s2 = s2[1:]
            if s != s2:
                g.es_print('cleaning', fn)
                f = open(fn, mode='wb')
                f.write(s2)
                f.close()
    #@+node:ekr.20150514063305.514: *3* create
    def create(self, fn):
        '''Create the given file with empty contents.'''
        theDir = g.os_path_dirname(fn)
        g.makeAllNonExistentDirectories(theDir, c=self.c, force=True, verbose=True)
            # Make the directories as needed.
        try:
            f = open(fn, mode='wb')
            f.close()
            g.note('created: %s' % (fn))
        except IOError:
            g.error('can not create: %s' % (fn))
        except Exception:
            g.error('unexpected error creating: %s' % (fn))
            g.es_exception()
    #@+node:ekr.20150514063305.515: *3* ignore
    def ignore(self, word):
        self.d.add_to_session(word)
    #@+node:ekr.20150514063305.516: *3* open_dict
    def open_dict(self, fn, language):
        '''Open or create the dict with the given fn.'''
        trace = False and not g.unitTesting
        if not fn or not language:
            return
        d = g.app.spellDict
        if d:
            self.d = d
            if trace: g.trace('already open', self.c.fileName(), fn)
            return
        if not g.os_path_exists(fn):
            # Fix bug 1175013: leo/plugins/spellpyx.txt is both source controlled and customized.
            self.create(fn)
        if g.os_path_exists(fn):
            # Merge the local and global dictionaries.
            try:
                self.clean_dict(fn)
                self.d = enchant.DictWithPWL(language, fn)
                if trace: g.trace('open', g.shortFileName(self.c.fileName()), fn)
            except Exception:
                g.es_exception()
                g.error('not a valid dictionary file', fn)
                self.d = enchant.Dict(language)
        else:
            # A fallback.  Unlikely to happen.
            self.d = enchant.Dict(language)
        # Use only a single copy of the dict.
        g.app.spellDict = self.d
    #@+node:ekr.20150514063305.517: *3* processWord

    def processWord(self, word):
        """
        Check the word. Return None if the word is properly spelled.
        Otherwise, return a list of alternatives.
        """
        d = self.d
        if not d:
            return None
        elif d.check(word):
            return None
        # Speed doesn't matter here. The more we find, the more convenient.
        word = ''.join([i for i in word if not i.isdigit()])
            # Remove all digits.
        if d.check(word) or d.check(word.lower()):
            return None 
        if word.find('_') > -1:
            # Snake case.
            words = word.split('_')
            for word2 in words:
                if not d.check(word2) and not d.check(word2.lower()):
                    return d.suggest(word)
            return None
        words = g.unCamel(word)
        if words:
            for word2 in words:
                if not d.check(word2) and not d.check(word2.lower()):
                    return d.suggest(word)
            return None
        else:
            return d.suggest(word)
    #@-others
#@+node:ekr.20150514063305.481: ** class SpellCommandsClass
class SpellCommandsClass(BaseEditCommandsClass):
    '''Commands to support the Spell Tab.'''
    #@+others
    #@+node:ekr.20150514063305.482: *3* ctor (SpellCommandsClass)
    def __init__(self, c):
        '''
        Ctor for SpellCommandsClass class.
        Inits happen when the first frame opens.
        '''
        # pylint: disable=super-init-not-called
        self.c = c
        self.handler = None
        self.page_width = c.config.getInt("page-width")
            # for wrapping
    #@+node:ekr.20150514063305.484: *3* openSpellTab
    @cmd('spell-tab-open')
    def openSpellTab(self, event=None):
        '''Open the Spell Checker tab in the log pane.'''
        c = self.c
        log = c.frame.log
        tabName = 'Spell'
        if log.frameDict.get(tabName):
            log.selectTab(tabName)
        else:
            log.selectTab(tabName)
            self.handler = SpellTabHandler(c, tabName)
        # Bug fix: 2013/05/22.
        if not self.handler.loaded:
            log.deleteTab(tabName, force=True)
        # spell as you type stuff
        self.suggestions = []
        self.suggestions_idx = None
        self.word = None
        self.spell_as_you_type = False
        self.wrap_as_you_type = False
    #@+node:ekr.20150514063305.485: *3* commands...(SpellCommandsClass)
    #@+node:ekr.20150514063305.486: *4* find
    @cmd('spell-find')
    def find(self, event=None):
        '''
        Simulate pressing the 'Find' button in the Spell tab.

        Just open the Spell tab if it has never been opened.
        For minibuffer commands, we must also force the Spell tab to be visible.
        '''
        # self.handler is a SpellTabHandler object (inited by openSpellTab)
        if self.handler:
            self.openSpellTab()
            self.handler.find()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.487: *4* change
    @cmd('spell-change')
    def change(self, event=None):
        '''Simulate pressing the 'Change' button in the Spell tab.'''
        if self.handler:
            self.openSpellTab()
            self.handler.change()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.488: *4* changeThenFind
    @cmd('spell-change-then-find')
    def changeThenFind(self, event=None):
        '''Simulate pressing the 'Change, Find' button in the Spell tab.'''
        if self.handler:
            self.openSpellTab()
            # A workaround for a pylint warning:
            # self.handler.changeThenFind()
            f = getattr(self.handler, 'changeThenFind')
            f()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.489: *4* hide
    @cmd('spell-tab-hide')
    def hide(self, event=None):
        '''Hide the Spell tab.'''
        if self.handler:
            self.c.frame.log.selectTab('Log')
            self.c.bodyWantsFocus()
    #@+node:ekr.20150514063305.490: *4* ignore
    @cmd('spell-ignore')
    def ignore(self, event=None):
        '''Simulate pressing the 'Ignore' button in the Spell tab.'''
        if self.handler:
            self.openSpellTab()
            self.handler.ignore()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.491: *4* focusToSpell
    @cmd('focus-to-spell-tab')
    def focusToSpell(self, event=None):
        '''Put focus in the spell tab.'''
        self.openSpellTab()
            # Makes Spell tab visible.
        # This is not a great idea. There is no indication of focus.
            # if self.handler and self.handler.tab:
                # self.handler.tab.setFocus()
    #@+node:ekr.20150514063305.492: *3* as_you_type_* commands
    #@+node:ekr.20150514063305.493: *4* as_you_type_toggle
    @cmd('spell-as-you-type-toggle')
    def as_you_type_toggle(self, event):
        """as_you_type_toggle - toggle spell as you type."""
        # c = self.c
        if self.spell_as_you_type:
            self.spell_as_you_type = False
            if not self.wrap_as_you_type:
                g.unregisterHandler('bodykey2', self.as_you_type_onkey)
            g.es("Spell as you type disabled")
            return
        self.spell_as_you_type = True
        if not self.wrap_as_you_type:
            g.registerHandler('bodykey2', self.as_you_type_onkey)
        g.es("Spell as you type enabled")
    #@+node:ekr.20150514063305.494: *4* as_you_type_wrap
    @cmd('spell-as-you-type-wrap')
    def as_you_type_wrap(self, event):
        """as_you_type_wrap - toggle wrap as you type."""
        # c = self.c
        if self.wrap_as_you_type:
            self.wrap_as_you_type = False
            if not self.spell_as_you_type:
                g.unregisterHandler('bodykey2', self.as_you_type_onkey)
            g.es("Wrap as you type disabled")
            return
        self.wrap_as_you_type = True
        if not self.spell_as_you_type:
            g.registerHandler('bodykey2', self.as_you_type_onkey)
        g.es("Wrap as you type enabled")
    #@+node:ekr.20150514063305.495: *4* as_you_type_next
    @cmd('spell-as-you-type-next')
    def as_you_type_next(self, event):
        """as_you_type_next - cycle word behind cursor to next suggestion."""
        if not self.suggestions:
            g.es('[no suggestions]')
            return
        word = self.suggestions[self.suggestion_idx]
        self.suggestion_idx = (self.suggestion_idx + 1) % len(self.suggestions)
        self.as_you_type_replace(word)
    #@+node:ekr.20150514063305.496: *4* as_you_type_undo
    @cmd('spell-as-you-type-undo')
    def as_you_type_undo(self, event):
        """as_you_type_undo - replace word behind cursor with word
        user typed before it started cycling suggestions.
        """
        if not self.word:
            g.es('[no previous word]')
            return
        self.as_you_type_replace(self.word)
    #@+node:ekr.20150514063305.497: *4* as_you_type_onkey
    def as_you_type_onkey(self, tag, kwargs):
        """as_you_type_onkey - handle a keystroke in the body when
        spell as you type is active

        :Parameters:
        - `tag`: hook tag
        - `kwargs`: hook arguments
        """
        if kwargs['c'] != self.c:
            return
        if kwargs['ch'] not in '\'",.:) \n\t':
            return
        c = self.c
        spell_ok = True
        if self.spell_as_you_type: # might just be for wrapping
            w = c.frame.body.wrapper
            txt = w.getAllText()
            i = w.getInsertPoint()
            word = txt[: i].rsplit(None, 1)[-1]
            word = ''.join(i if i.isalpha() else ' ' for i in word).split()
            if word:
                word = word[-1]
                ec = c.spellCommands.handler.spellController
                suggests = ec.processWord(word)
                if suggests:
                    spell_ok = False
                    g.es(' '.join(suggests[: 5]) +
                         ('...' if len(suggests) > 5 else ''),
                         color='red')
                elif suggests is not None:
                    spell_ok = False
                    g.es('[no suggestions]')
                self.suggestions = suggests
                self.suggestion_idx = 0
                self.word = word
        if spell_ok and self.wrap_as_you_type and kwargs['ch'] == ' ':
            w = c.frame.body.wrapper
            txt = w.getAllText()
            i = w.getInsertPoint()
            # calculate the current column
            parts = txt.split('\n')
            popped = 0 # chars on previous lines
            while len(parts[0]) + popped < i:
                popped += len(parts.pop(0)) + 1 # +1 for the \n that's gone
            col = i - popped
            if col > self.page_width:
                txt = txt[: i] + '\n' + txt[i:] # replace space with \n
                w.setAllText(txt)
                c.p.b = txt
                w.setInsertPoint(i + 1) # must come after c.p.b assignment
    #@+node:ekr.20150514063305.498: *4* as_you_type_replace
    def as_you_type_replace(self, word):
        """as_you_type_replace - replace the word behind the cursor
        with `word`

        :Parameters:
        - `word`: word to use as replacement
        """
        c = self.c
        w = c.frame.body.wrapper
        txt = w.getAllText()
        j = i = w.getInsertPoint()
        i -= 1
        while i and not txt[i].isalpha():
            i -= 1
        xtra = j - i
        j = i + 1
        while i and txt[i].isalpha():
            i -= 1
        if i or (txt and not txt[0].isalpha()):
            i += 1
        txt = txt[: i] + word + txt[j:]
        w.setAllText(txt)
        c.p.b = txt
        w.setInsertPoint(i + len(word) + xtra - 1)
        c.bodyWantsFocusNow()
    #@-others
#@+node:ekr.20150514063305.499: ** class SpellTabHandler
class SpellTabHandler(object):
    """A class to create and manage Leo's Spell Check dialog."""
    #@+others
    #@+node:ekr.20150514063305.500: *3* Birth & death
    #@+node:ekr.20150514063305.501: *4* SpellTabHandler.__init__
    def __init__(self, c, tabName):
        """Ctor for SpellTabHandler class."""
        if g.app.gui.isNullGui:
            return ###
        self.c = c
        self.body = c.frame.body
        self.currentWord = None
        self.re_word = re.compile(
            # Don't include underscores in words. It just complicates things.
            # [^\W\d_] means any unicode char except underscore or digit.
            r"([^\W\d_]+)(['`][^\W\d_]+)?",
            flags=re.UNICODE)
        self.outerScrolledFrame = None
        self.seen = set()
            # Adding a word to seen will ignore it until restart.
        self.workCtrl = g.app.gui.plainTextWidget(c.frame.top)
            # A text widget for scanning.
            # Must have a parent frame even though it is not packed.
        if enchant:
            self.spellController = EnchantClass(c)
            self.tab = g.app.gui.createSpellTab(c, self, tabName)
            self.loaded = True
        else:
            self.spellController = None
            self.tab = None
            self.loaded = False
    #@+node:ekr.20150514063305.502: *3* Commands
    #@+node:ekr.20150514063305.503: *4* add (spellTab)
    def add(self, event=None):
        """Add the selected suggestion to the dictionary."""
        if self.loaded:
            w = self.currentWord
            if w:
                self.spellController.add(w)
                self.tab.onFindButton()
    #@+node:ekr.20150514063305.504: *4* change (spellTab)
    def change(self, event=None):
        """Make the selected change to the text"""
        if not self.loaded:
            return
        c = self.c
        w = c.frame.body.wrapper
        selection = self.tab.getSuggestion()
        if selection:
            # Use getattr to keep pylint happy.
            if hasattr(self.tab, 'change_i') and getattr(self.tab, 'change_i') is not None:
                start = getattr(self.tab, 'change_i')
                end = getattr(self.tab, 'change_j')
                oldSel = start, end
                # g.trace('using',start,end)
            else:
                start, end = oldSel = w.getSelectionRange()
            if start is not None:
                if start > end: start, end = end, start
                w.delete(start, end)
                w.insert(start, selection)
                w.setSelectionRange(start, start + len(selection))
                c.frame.body.onBodyChanged("Change", oldSel=oldSel)
                c.invalidateFocus()
                c.bodyWantsFocus()
                return True
        # The focus must never leave the body pane.
        c.invalidateFocus()
        c.bodyWantsFocus()
        return False
    #@+node:ekr.20150514063305.505: *4* find & helper
    def find(self, event=None):
        """Find the next unknown word."""
        trace = False and not g.unitTesting
        trace_lookup = False
        trace_end_body = False
        if not self.loaded:
            return
        c, n, p = self.c, 0, self.c.p
        if trace: g.trace('entry', p.h)
        sc = self.spellController
        w = c.frame.body.wrapper
        c.selectPosition(p)
        s = w.getAllText().rstrip()
        ins = w.getInsertPoint()
        # New in Leo 5.3: use regex to find words.
        last_p = p.copy()
        while True:
            for m in self.re_word.finditer(s[ins:]):
                start, word = m.start(0), m.group(0)
                if word in self.seen:
                    continue
                n += 1
                # Ignore the word if numbers precede or follow it.
                # Seems difficult to do this in the regex itself.
                k1 = ins + start - 1
                if k1 >= 0 and s[k1].isdigit():
                    continue
                k2 = ins + start + len(word)
                if k2 < len(s) and s[k2].isdigit():
                    continue
                if trace and trace_lookup: g.trace('lookup', word)
                alts = sc.processWord(word)
                if alts:
                    if trace: g.trace('%s searches' % n)
                    self.currentWord = word
                    i = ins + start
                    j = i + len(word)
                    self.showMisspelled(p)
                    self.tab.fillbox(alts, word)
                    c.invalidateFocus()
                    c.bodyWantsFocus()
                    w.setSelectionRange(i, j, insert=j)
                    w.see(j)
                    return
                else:
                    self.seen.add(word)
            # No more misspellings in p
            if trace and trace_end_body: g.trace('----- end of text', p.h)
            p.moveToThreadNext()
            if p:
                ins = 0
                s = p.b
            else:
                if trace: g.trace('%s searches' % n)
                g.es("no more misspellings")
                c.selectPosition(last_p)
                self.tab.fillbox([])
                c.invalidateFocus()
                c.bodyWantsFocus()
                return
    #@+node:ekr.20160415033936.1: *5* showMisspelled
    def showMisspelled(self, p):
        '''Show the position p, contracting the tree as needed.'''
        c = self.c
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
    #@+node:ekr.20150514063305.508: *4* hide
    def hide(self, event=None):
        self.c.frame.log.selectTab('Log')
    #@+node:ekr.20150514063305.509: *4* ignore
    def ignore(self, event=None):
        """Ignore the incorrect word for the duration of this spell check session."""
        if self.loaded:
            w = self.currentWord
            if w:
                self.spellController.ignore(w)
                self.tab.onFindButton()
    #@-others
#@-others
#@-leo
