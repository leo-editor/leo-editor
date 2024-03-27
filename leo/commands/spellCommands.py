#@+leo-ver=5-thin
#@+node:ekr.20150514040239.1: * @file ../commands/spellCommands.py
"""Leo's spell-checking commands."""
#@+<< spellCommands imports & annotations >>
#@+node:ekr.20150514050530.1: ** << spellCommands imports & annotations >>
from __future__ import annotations
from collections.abc import Callable
import re
from typing import Any, Optional, TYPE_CHECKING
# Third-party annotations
try:
    import enchant
except Exception:  # May throw WinError(!)
    enchant = None
from leo.commands.baseCommands import BaseEditCommandsClass
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoGui import LeoKeyEvent
    from leo.core.leoNodes import Position
#@-<< spellCommands imports & annotations >>

def cmd(name: str) -> Callable:
    """Command decorator for the SpellCommandsClass class."""
    return g.new_cmd_decorator(name, ['c', 'spellCommands',])

#@+others
#@+node:ekr.20180207071908.1: ** class BaseSpellWrapper
class BaseSpellWrapper:
    """Code common to EnchantWrapper and DefaultWrapper"""
    # pylint: disable=no-member
    # Subclasses set self.c and self.d
    #@+others
    #@+node:ekr.20150514063305.513: *3* BaseSpellWrapper.clean_dict
    def clean_dict(self, fn: str) -> None:
        if g.os_path_exists(fn):
            f = open(fn, mode='rb')
            s = f.read()
            f.close()
            # Blanks lines cause troubles.
            s2 = s.replace(b'\r', b'').replace(b'\n\n', b'\n')
            if s2.startswith(b'\n'):
                s2 = s2[1:]
            if s != s2:
                g.es_print('cleaning', fn)
                f = open(fn, mode='wb')  # type:ignore
                f.write(s2)
                f.close()
    #@+node:ekr.20180207071114.5: *3* BaseSpellWrapper.create
    def create(self, fn: str) -> None:
        """Create the given file with empty contents."""
        # Make the directories as needed.
        theDir = g.os_path_dirname(fn)
        if theDir:
            ok = g.makeAllNonExistentDirectories(theDir)
            # #1453: Don't assume the directory exists.
            if not ok:
                g.error(f"did not create directory: {theDir}")
                return
        # Create the file.
        try:
            f = open(fn, mode='wb')
            f.close()
            g.note(f"created: {fn}")
        except IOError:
            g.error(f"can not create: {fn}")
        except Exception:
            g.error(f"unexpected error creating: {fn}")
            g.es_exception()
    #@+node:ekr.20180207074613.1: *3* BaseSpellWrapper.default_dict
    def default_dict(self, language: Any) -> dict[str, str]:

        try:
            return enchant.Dict(language)
        except Exception:
            return {}
    #@+node:ekr.20180207073536.1: *3* BaseSpellWrapper.create_dict_from_file
    def create_dict_from_file(self, fn: str, language: Any) -> dict[str, str]:

        try:
            return enchant.DictWithPWL(language, fn)
        except Exception:
            return {}
    #@+node:ekr.20150514063305.515: *3* BaseSpellWrapper.ignore
    def ignore(self, word: str) -> None:

        self.d.add_to_session(word)
    #@+node:ekr.20180209142310.1: *3* BaseSpellWrapper.show_info
    def show_info(self) -> None:

        g.es_print('pyenchant spell checker')
        g.es_print(f"user dictionary:   {self.find_user_dict()}")
        try:
            aList = enchant.list_dicts()
            aList2 = [a for a, b in aList]
            g.es_print(f"main dictionaries: {', '.join(aList2)}")
        except Exception:
            g.es_exception()
    #@-others
#@+node:ekr.20180207075606.1: ** class DefaultDict
class DefaultDict:
    """A class with the same interface as the enchant dict class."""

    def __init__(self, words: list[str] = None) -> None:
        self.added_words: set[str] = set()
        self.ignored_words: set[str] = set()
        self.words: set[str] = set() if words is None else set(words)

    #@+others
    #@+node:ekr.20180207075740.1: *3* DefaultDict.add
    def add(self, word: str) -> None:
        """Add a word to the dictionary."""
        self.words.add(word)
        self.added_words.add(word)
    #@+node:ekr.20180207101513.1: *3* DefaultDict.add_words_from_dict
    def add_words_from_dict(self, kind: str, fn: str, words: Any) -> None:
        """For use by DefaultWrapper."""
        for word in words or []:
            self.words.add(word)
            self.words.add(word.lower())
    #@+node:ekr.20180207075751.1: *3* DefaultDict.add_to_session
    def add_to_session(self, word: str) -> None:

        self.ignored_words.add(word)
    #@+node:ekr.20180207080007.1: *3* DefaultDict.check
    def check(self, word: str) -> bool:
        """Return True if the word is in the dict."""
        for s in (word, word.lower(), word.capitalize()):
            if s in self.words or s in self.ignored_words:
                return True
        return False
    #@+node:ekr.20180207081634.1: *3* DefaultDict.suggest & helpers
    def suggest(self, word: str) -> list[str]:

        def known(words: list[str]) -> list[str]:
            """Return the words that are in the dictionary."""
            return [z for z in list(set(words)) if z in self.words]

        assert not known([word]), repr(word)
        suggestions = (
            known(self.edits1(word)) or
            known(self.edits2(word))
            # [word] # Fall back to the unknown word itself.
        )
        return suggestions
    #@+node:ekr.20180207085717.1: *4* dict.edits1 & edits2
    #@@nobeautify

    def edits1(self, word: str) -> list[str]:
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return list(set(deletes + transposes + replaces + inserts))

    def edits2(self, word: str) -> list[str]:
        "All edits that are two edits away from `word`."
        return [e2 for e1 in self.edits1(word) for e2 in self.edits1(e1)]
    #@-others
#@+node:ekr.20180207071114.1: ** class DefaultWrapper (BaseSpellWrapper)
class DefaultWrapper(BaseSpellWrapper):
    """
    A default spell checker for when pyenchant is not available.

    Based on http://norvig.com/spell-correct.html

    Main dictionary: ~/.leo/main_spelling_dict.txt
    User dictionary:
    - @string enchant_local_dictionary or
    - leo/plugins/spellpyx.txt or
    - ~/.leo/spellpyx.txt
    """
    #@+others
    #@+node:ekr.20180207071114.2: *3* DefaultWrapper. __init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for DefaultWrapper class."""
        # pylint: disable=super-init-not-called
        self.c = c
        if not g.app.spellDict:
            g.app.spellDict = DefaultDict()
        self.d = g.app.spellDict
        self.user_fn = self.find_user_dict()
        if not g.os_path_exists(self.user_fn):
            # Fix bug 1175013: leo/plugins/spellpyx.txt is
            # both source controlled and customized.
            self.create(self.user_fn)
        self.main_fn = self.find_main_dict()
        table = (
            ('user', self.user_fn),
            ('main', self.main_fn),
        )
        for kind, fn in table:
            if fn:
                words = self.read_words(kind, fn)
                self.d.add_words_from_dict(kind, fn, words)
    #@+node:ekr.20180207110701.1: *3* DefaultWrapper.add
    def add(self, word: str) -> None:
        """Add a word to the user dictionary."""
        self.d.add(word)
        self.d.add(word.lower())
        self.save_user_dict()
    #@+node:ekr.20180207100238.1: *3* DefaultWrapper.find_main_dict
    def find_main_dict(self) -> Optional[str]:
        """Return the full path to the global dictionary."""
        c = self.c
        fn = c.config.getString('main-spelling-dictionary')
        if fn and g.os_path_exists(fn):
            return fn
        # Default to ~/.leo/main_spelling_dict.txt
        fn = g.finalize_join(g.app.homeDir, '.leo', 'main_spelling_dict.txt')
        return fn if g.os_path_exists(fn) else None
    #@+node:ekr.20230926171905.1: *3* DefaultWrapper.find_user_dict
    def find_user_dict(self) -> Optional[str]:
        """Return the full path to the global dictionary."""
        c = self.c
        fn = c.config.getString('enchant-local-dictionary')
        if fn and g.os_path_exists(fn):
            return fn
        # Default to ~/.leo/main_spelling_dict.txt
        fn = g.finalize_join(g.app.homeDir, '.leo', 'spellpyx.txt')
        return fn if g.os_path_exists(fn) else None
    #@+node:ekr.20180207073815.1: *3* DefaultWrapper.read_words
    def read_words(self, kind: Any, fn: str) -> set[str]:
        """Return all the words from the dictionary file."""
        words = set()
        try:
            with open(fn, 'rb') as f:
                s = g.toUnicode(f.read())
                # #1688: Do this in place.
                for line in g.splitLines(s):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        words.add(line)
        except Exception:
            g.es_print(f"can not open {kind} dictionary: {fn}")
        return words
    #@+node:ekr.20180207110718.1: *3* DefaultWrapper.save_dict
    def save_dict(self, kind: str, fn: str, trace: bool = False) -> None:
        """
        Save the dictionary whose name is given, alphabetizing the file.
        Write added words to the file if kind is 'user'.
        """
        if not fn:
            return
        words = self.read_words(kind, fn)
        if not words:
            return
        words = set(words)
        if kind == 'user':
            for word in self.d.added_words:
                words.add(word)
        aList = sorted(words, key=lambda s: s.lower())
        f = open(fn, mode='wb')
        s = '\n'.join(aList) + '\n'
        f.write(g.toEncodedString(s))
        f.close()
    #@+node:ekr.20180211104628.1: *3* DefaultWrapper.save_main/user_dict
    def save_main_dict(self, trace: bool = False) -> None:

        self.save_dict('main', self.main_fn, trace=trace)

    def save_user_dict(self, trace: bool = False) -> None:

        self.save_dict('user', self.user_fn, trace=trace)
    #@+node:ekr.20180209141933.1: *3* DefaultWrapper.show_info
    def show_info(self) -> None:

        if self.main_fn:
            g.es_print('Default spell checker')
            table = (
                ('main', self.main_fn),
                ('user', self.user_fn),
            )
        else:
            g.es_print('\nSpell checking has been disabled.')
            g.es_print('To enable, put a main dictionary at:')
            g.es_print('~/.leo/main_spelling_dict.txt')
            table = (  # type:ignore
                ('user', self.user_fn),
            )
        for kind, fn in table:
            g.es_print(
                f"{kind} dictionary: {(g.os_path_normpath(fn) if fn else 'None')}")
    #@-others
#@+node:ekr.20150514063305.510: ** class EnchantWrapper (BaseSpellWrapper)
class EnchantWrapper(BaseSpellWrapper):
    """A wrapper class for PyEnchant spell checker"""
    # Contains all methods referencing self.c and self.d

    #@+others
    #@+node:ekr.20150514063305.511: *3* enchant. __init__
    def __init__(self, c: Cmdr) -> None:
        """Ctor for EnchantWrapper class."""
        # pylint: disable=super-init-not-called
        self.c = c
        self.init_language()
        fn = self.find_user_dict()
        self.d: dict[str, str] = self.open_dict_file(fn)
        g.app.spellDict = self.d
    #@+node:ekr.20180207071114.3: *3* enchant.add
    def add(self, word: str) -> None:
        """Add a word to the user dictionary."""
        self.d.add(word)
    #@+node:ekr.20180207072351.1: *3* enchant.find_user_dict
    def find_user_dict(self) -> str:
        """Return the full path to the local dictionary."""
        c = self.c
        join = g.finalize_join
        table = (
            # Settings first.
            c.config.getString('enchant-local-dictionary'),
            # #108: then the .leo directory.
            join(g.app.homeDir, '.leo', 'spellpyx.txt'),
            # The plugins directory as a last resort.
            join(g.app.loadDir, "..", "plugins", 'spellpyx.txt'),
        )
        for path in table:
            if g.os_path_exists(path):
                return path
        g.es_print('Creating ~/.leo/spellpyx.txt')
        # #1453: Return the default path.
        return join(g.app.homeDir, '.leo', 'spellpyx.txt')
    #@+node:ekr.20180207072846.1: *3* enchant.init_language
    def init_language(self) -> None:
        """Init self.language."""
        c = self.c
        language = g.checkUnicode(c.config.getString('enchant-language'))
        if language:
            try:
                enchant.dict_exists(language)
            except AttributeError:
                # Likely an install error.
                # open_dict_file gives the error.
                pass
            except Exception:
                if language == 'en_US':
                    g.es_exception()  # Valid language.
                else:
                    g.warning('Invalid language code for Enchant', repr(language))
                    g.es_print('Using "en_US" instead')
                    g.es_print('Use @string enchant_language to specify your language')
                language = 'en_US'
        self.language = language
    #@+node:ekr.20180207102856.1: *3* enchant.open_dict_file
    def open_dict_file(self, fn: str) -> dict[str, str]:
        """Open or create the dict with the given fn."""
        language = self.language
        if not fn or not language:
            return None
        if g.app.spellDict:
            return g.app.spellDict
        if not g.os_path_exists(fn):
            # Fix bug 1175013: leo/plugins/spellpyx.txt is
            # both source controlled and customized.
            self.create(fn)
        if g.os_path_exists(fn):
            # Merge the local and global dictionaries.
            try:
                self.clean_dict(fn)
                d = enchant.DictWithPWL(language, fn)
            except Exception:
                try:
                    d = enchant.Dict(language)
                except Exception:
                    d = {}
        else:
            # A fallback. Unlikely to happen.
            try:
                d = enchant.Dict(language)
            except Exception:
                d = {}
        if not d:
            g.es_print('Error opening dictionary')
            g.es_print('pip install pyenchant, NOT enchant')
        return d

    #@+node:ekr.20150514063305.517: *3* enchant.process_word
    def process_word(self, word: str) -> list[str]:
        """
        Check the word. Return None if the word is properly spelled.
        Otherwise, return a list of alternatives.
        """
        d = self.d
        if not d:
            return None
        if d.check(word):
            return None
        # Speed doesn't matter here. The more we find, the more convenient.
        # Remove all digits.
        word = ''.join([i for i in word if not i.isdigit()])
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
        return d.suggest(word)
    #@-others
#@+node:ekr.20150514063305.481: ** class SpellCommandsClass
class SpellCommandsClass(BaseEditCommandsClass):
    """Commands to support the Spell Tab."""
    #@+others
    #@+node:ekr.20150514063305.482: *3* ctor & reloadSettings(SpellCommandsClass)
    def __init__(self, c: Cmdr) -> None:
        """
        Ctor for SpellCommandsClass class.
        Inits happen when the first frame opens.
        """
        # pylint: disable=super-init-not-called
        self.c = c
        self.handler: SpellTabHandler = None
        self.reloadSettings()

    def reloadSettings(self) -> None:
        """SpellCommandsClass.reloadSettings."""
        c = self.c
        self.page_width = c.config.getInt("page-width")  # for wrapping
    #@+node:ekr.20150514063305.484: *3* openSpellTab
    @cmd('spell-tab-open')
    def openSpellTab(self, event: LeoKeyEvent = None) -> None:
        """Open the Spell Checker tab in the log pane."""
        if g.unitTesting:
            return
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
            log.deleteTab(tabName)
        # spell as you type stuff
        self.suggestions: list[str] = []
        self.suggestions_idx: int = None
        self.word: str = None
        self.spell_as_you_type = False
        self.wrap_as_you_type = False
    #@+node:ekr.20150514063305.485: *3* commands...(SpellCommandsClass)
    #@+node:ekr.20171205043931.1: *4* add
    @cmd('spell-add')
    def add(self, event: LeoKeyEvent = None) -> None:
        """
        Simulate pressing the 'add' button in the Spell tab.

        Just open the Spell tab if it has never been opened.
        For minibuffer commands, we must also force the Spell tab to be visible.
        """
        # self.handler is a SpellTabHandler object (inited by openSpellTab)
        if self.handler:
            self.openSpellTab()
            self.handler.add()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.486: *4* spell-find
    @cmd('spell-find')
    def find(self, event: LeoKeyEvent = None) -> None:
        """
        Simulate pressing the 'Find' button in the Spell tab.

        Just open the Spell tab if it has never been opened.
        For minibuffer commands, we must also force the Spell tab to be visible.
        """
        # self.handler is a SpellTabHandler object (inited by openSpellTab)
        if self.handler:
            self.openSpellTab()
            self.handler.find()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.487: *4* change
    @cmd('spell-change')
    def change(self, event: LeoKeyEvent = None) -> None:
        """Simulate pressing the 'Change' button in the Spell tab."""
        if self.handler:
            self.openSpellTab()
            self.handler.change()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.488: *4* changeThenFind
    @cmd('spell-change-then-find')
    def changeThenFind(self, event: LeoKeyEvent = None) -> None:
        """Simulate pressing the 'Change, Find' button in the Spell tab."""
        if self.handler:
            self.openSpellTab()
            f = self.handler.changeThenFind
            f()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.489: *4* hide
    @cmd('spell-tab-hide')
    def hide(self, event: LeoKeyEvent = None) -> None:
        """Hide the Spell tab."""
        if self.handler:
            self.c.frame.log.selectTab('Log')
            self.c.bodyWantsFocus()
    #@+node:ekr.20150514063305.490: *4* ignore
    @cmd('spell-ignore')
    def ignore(self, event: LeoKeyEvent = None) -> None:
        """Simulate pressing the 'Ignore' button in the Spell tab."""
        if self.handler:
            self.openSpellTab()
            self.handler.ignore()
        else:
            self.openSpellTab()
    #@+node:ekr.20150514063305.491: *4* focusToSpell
    @cmd('focus-to-spell-tab')
    def focusToSpell(self, event: LeoKeyEvent = None) -> None:
        """Put focus in the spell tab."""
        self.openSpellTab()  # Makes Spell tab visible.
        # This is not a great idea. There is no indication of focus.
            # if self.handler and self.handler.tab:
                # self.handler.tab.setFocus()
    #@+node:ekr.20150514063305.492: *3* as_you_type_* commands
    #@+node:ekr.20150514063305.493: *4* as_you_type_toggle
    @cmd('spell-as-you-type-toggle')
    def as_you_type_toggle(self, event: LeoKeyEvent) -> None:
        """as_you_type_toggle - toggle spell as you type."""
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
    def as_you_type_wrap(self, event: LeoKeyEvent) -> None:
        """as_you_type_wrap - toggle wrap as you type."""
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
    def as_you_type_next(self, event: LeoKeyEvent) -> None:
        """as_you_type_next - cycle word behind cursor to next suggestion."""
        if not self.suggestions:
            g.es('[no suggestions]')
            return
        word = self.suggestions[self.suggestion_idx]  # type:ignore
        self.suggestion_idx = (self.suggestion_idx + 1) % len(self.suggestions)  # type:ignore
        self.as_you_type_replace(word)
    #@+node:ekr.20150514063305.496: *4* as_you_type_undo
    @cmd('spell-as-you-type-undo')
    def as_you_type_undo(self, event: LeoKeyEvent) -> None:
        """as_you_type_undo - replace word behind cursor with word
        user typed before it started cycling suggestions.
        """
        if not self.word:
            g.es('[no previous word]')
            return
        self.as_you_type_replace(self.word)
    #@+node:ekr.20150514063305.497: *4* as_you_type_onkey
    def as_you_type_onkey(self, tag: str, kwargs: Any) -> None:
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
        if self.spell_as_you_type:  # might just be for wrapping
            w = c.frame.body.wrapper
            txt = w.getAllText()
            i = w.getInsertPoint()
            word = txt[:i].rsplit(None, 1)[-1]
            word = ''.join(i if i.isalpha() else ' ' for i in word).split()
            if word:
                word = word[-1]
                ec = c.spellCommands.handler.spellController
                suggests = ec.process_word(word)
                if suggests:
                    spell_ok = False
                    g.es(' '.join(suggests[:5]) +
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
            popped = 0  # chars on previous lines
            while len(parts[0]) + popped < i:
                popped += len(parts.pop(0)) + 1  # +1 for the \n that's gone
            col = i - popped
            if col > self.page_width:
                txt = txt[:i] + '\n' + txt[i:]  # replace space with \n
                w.setAllText(txt)
                c.p.b = txt
                w.setInsertPoint(i + 1)  # must come after c.p.b assignment
    #@+node:ekr.20150514063305.498: *4* as_you_type_replace
    def as_you_type_replace(self, word: str) -> None:
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
        txt = txt[:i] + word + txt[j:]
        w.setAllText(txt)
        c.p.b = txt
        w.setInsertPoint(i + len(word) + xtra - 1)
        c.bodyWantsFocusNow()
    #@-others
#@+node:ekr.20150514063305.499: ** class SpellTabHandler
class SpellTabHandler:
    """A class to create and manage Leo's Spell Check dialog."""
    #@+others
    #@+node:ekr.20150514063305.501: *3* SpellTabHandler.__init__
    def __init__(self, c: Cmdr, tabName: Any) -> None:
        """Ctor for SpellTabHandler class."""
        # New in Leo 6.7.5: This class works in a null gui.
        self.c = c
        self.body = c.frame.body
        self.currentWord: str = None
        self.outerScrolledFrame = None
        self.seen: set[str] = set()  # Adding a word to seen will ignore it until restart.
        # A text widget for scanning. Must have a parent frame.
        self.workCtrl = g.app.gui.plainTextWidget(c.frame.top)
        if enchant:
            self.spellController = EnchantWrapper(c)
            self.tab = g.app.gui.createSpellTab(c, self, tabName)
            self.loaded = True
            return
        # Create the spellController for the show-spell-info command.
        self.spellController = DefaultWrapper(c)  # type:ignore
        self.loaded = bool(self.spellController.main_fn)
        if self.loaded:
            # Create the spell tab only if the main dict exists.
            self.tab = g.app.gui.createSpellTab(c, self, tabName)
        else:
            # g.es_print('No main dictionary')
            self.tab = None
    #@+node:ekr.20150514063305.502: *3* Commands
    #@+node:ekr.20150514063305.503: *4* SpellTabHandler.add
    def add(self, event: LeoKeyEvent = None) -> None:
        """Add the selected suggestion to the dictionary."""
        if self.loaded:
            w = self.currentWord
            if w:
                self.spellController.add(w)
                self.tab.onFindButton()
    #@+node:ekr.20150514063305.504: *4* SpellTabHandler.change
    def change(self, event: LeoKeyEvent = None) -> bool:
        """Make the selected change to the text"""
        if not self.loaded:
            return False
        c, p, u = self.c, self.c.p, self.c.undoer
        w = c.frame.body.wrapper
        selection = self.tab.getSuggestion()
        if selection:
            bunch = u.beforeChangeBody(p)
            # Use getattr to keep pylint happy.
            i = getattr(self.tab, 'change_i', None)
            j = getattr(self.tab, 'change_j', None)
            if i is not None:
                start, end = i, j
            else:
                start, end = w.getSelectionRange()
            if start is not None:
                if start > end:
                    start, end = end, start
                w.delete(start, end)
                w.insert(start, selection)
                w.setSelectionRange(start, start + len(selection))
                p.v.b = w.getAllText()
                u.afterChangeBody(p, 'Change', bunch)
                c.invalidateFocus()
                c.bodyWantsFocus()
                return True
        # The focus must never leave the body pane.
        c.invalidateFocus()
        c.bodyWantsFocus()
        return False
    #@+node:ekr.20150514063305.505: *4* SpellTabHandler.find & helper
    # Create a pattern that matches words, including contractions.

    # The following pattern below is only approximate!
    # The find method checks and modifies its results.

    re_word = re.compile(r"(\w+(['`]\w+)?)", flags=re.UNICODE)
    re_part = re.compile(r'[a-zA-z]+')
    re_http = re.compile(r'.*?(http|https)://(.*?)$')

    def find(self, event: LeoKeyEvent = None) -> Optional[str]:
        """
        Find the next unknown word.

        Return the word for unit tests.
        """
        if not self.loaded:
            return None
        c, p = self.c, self.c.p
        sc = self.spellController
        w = c.frame.body.wrapper
        c.selectPosition(p)
        s = w.getAllText().rstrip()
        ins = w.getInsertPoint()
        last_p = p.copy()
        while True:
            # Note: despite the tests below, finditer is a crucial speed boost.
            for m in self.re_word.finditer(s[ins:]):
                start, word = m.start(0), m.group(0)

                # Strip leading and trailing underscores.
                # sc.process_word throw ValueError otherwise.
                while word and word.startswith(('_', '`')):
                    word = word[1:]
                    start += 1
                if not word:
                    continue
                while word and word.endswith(('_', '`')):
                    word = word[:-1]
                if not word:
                    continue

                # Make sure the spell checker won't throw ValueError.
                if '_' in word:
                    # Only check up to those parts containing word characters.
                    parts = word.split('_')
                    parts = [z for z in parts if z]  # Handle '__'.
                    for i, part in enumerate(parts):
                        if not self.re_part.match(part):
                            word = '_'.join(parts[:i]).replace('__', '_')
                            if not word:
                                continue
                else:
                    parts = [word]
                    if not self.re_part.match(word):
                        continue

                # Ignore the word if numbers precede or follow it.
                # Seems difficult to do this in the regex itself.
                k1 = ins + start - 1
                if k1 >= 0 and s[k1].isdigit():
                    continue

                # Special case: f-strings delimited by single quotes.
                #               Don't bother testing for the obsolete u'xxx' syntax.
                if word.startswith("f'"):
                    word = word[2:]
                    start += 2
                    if not word:
                        continue

                # Don't check short words.
                if len(word) < 3:
                    continue

                # Don't check words following `(http|https)://`.
                i, j = g.getLine(s, ins + start)
                line = s[i:j]
                m = self.re_http.match(line)
                if m and word in m.group(2):
                    continue

                # Special case: \b, \n, and \t delimit words.
                #               It's hard to test for this in the regex.
                alt_word = None
                if word.startswith(('b', 'n', 't')) and k1 >= 0 and s[k1] == '\\':
                    alt_word = word  # Search two ways.
                    word = word[1:]
                    start += 1
                    if not word:
                        continue

                # Last checks.
                k2 = ins + start + len(word)
                if k2 < len(s) and s[k2].isdigit():
                    continue
                if word.startswith('_') or word.endswith('_'):
                    g.trace('Can not happen: underscore in word', repr(word))
                    continue
                if word in self.seen:
                    continue

                # Look up word and alt_word.
                try:
                    # Note: sc.process_word munges the word!
                    alts: list[str] = sc.process_word(word)

                    # Look up the alternate word if the word was not found.
                    if alts and alt_word:
                        alts2 = sc.process_word(alt_word)
                        if alts2:
                            # Add the top three *new* suggestions to the top of alts.
                            new_alts = [alts2[i] for i in range(3)
                                if i < len(alts2) and alts2[i] not in alts
                            ]
                            for z in reversed(new_alts):
                                alts.insert(0, z)
                        else:
                            alts = []  # Done.
                except ValueError:
                    # g.printObj(parts, tag=f"Fail: word: {word!r}")
                    continue
                if alts:
                    self.currentWord = word
                    i = ins + start
                    j = i + len(word)
                    self.showMisspelled(p)
                    self.tab.fillbox(alts, word)
                    c.invalidateFocus()
                    c.bodyWantsFocus()
                    w.setSelectionRange(i, j, insert=j)
                    k = g.see_more_lines(s, j, 4)
                    w.see(k)
                    return alts[0]  # For unit tests.
                # Don't add misspellings.
                self.seen.add(word)
            # No more misspellings in p
            if g.unitTesting:
                return None
            p.moveToThreadNext()
            if p:
                ins = 0
                s = p.b
            else:
                g.es("no more misspellings")
                c.selectPosition(last_p)
                self.tab.fillbox([])
                c.invalidateFocus()
                c.bodyWantsFocus()
                return None
    #@+node:ekr.20160415033936.1: *5* SpellTabHandler.showMisspelled
    def showMisspelled(self, p: Position) -> None:
        """Show the position p, contracting the tree as needed."""
        c = self.c
        redraw = not p.isVisible(c)
        # New in Leo 4.4.8: show only the 'sparse' tree when redrawing.
        if c.sparse_spell and not c.p.isAncestorOf(p):
            for p2 in c.p.self_and_parents(copy=False):
                p2.contract()
                redraw = True
        for p2 in p.parents(copy=False):
            if not p2.isExpanded():
                p2.expand()
                redraw = True
        if redraw:
            c.redraw(p)
        else:
            c.selectPosition(p)
    #@+node:ekr.20150514063305.508: *4* SpellTabHandler.hide
    def hide(self, event: LeoKeyEvent = None) -> None:
        self.c.frame.log.selectTab('Log')
    #@+node:ekr.20150514063305.509: *4* SpellTabHandler.ignore
    def ignore(self, event: LeoKeyEvent = None) -> None:
        """Ignore the incorrect word for the duration of this spell check session."""
        if self.loaded:
            w = self.currentWord
            if w:
                self.spellController.ignore(w)
                self.tab.onFindButton()
    #@-others
#@+node:ekr.20180209141207.1: ** @g.command('show-spell-info')
@g.command('show-spell-info')
def show_spell_info(event: LeoKeyEvent = None) -> None:
    c = event.get('c')
    if c:
        c.spellCommands.handler.spellController.show_info()
#@+node:ekr.20180211104019.1: ** @g.command('clean-main-spell-dict')
@g.command('clean-main-spell-dict')
def clean_main_spell_dict(event: LeoKeyEvent) -> None:
    """
    Clean the main spelling dictionary used *only* by the default spell
    checker.

    This command works regardless of the spell checker being used.
    """
    c = event and event.get('c')
    if c:
        DefaultWrapper(c).save_main_dict(trace=True)
#@+node:ekr.20180211105748.1: ** @g.command('clean-user-spell-dict')
@g.command('clean-user-spell-dict')
def clean_user_spell_dict(event: LeoKeyEvent) -> None:
    """
    Clean the user spelling dictionary used *only* by the default spell
    checker. Mostly for debugging, because this happens automatically.

    This command works regardless of the spell checker being used.
    """
    c = event and event.get('c')
    if c:
        DefaultWrapper(c).save_user_dict(trace=True)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
