#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file ../plugins/importers/javascript.py
"""The @auto importer for JavaScript."""
import re
from typing import Any, Dict, Generator
from leo.core import leoGlobals as g  # Required
from leo.core.leoCommands import Commands as Cmdr
from leo.core.leoNodes import Position
from leo.plugins.importers.linescanner import Importer
#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer(Importer)
class JS_Importer(Importer):

    def __init__(self, c: Cmdr) -> None:
        """The ctor for the JS_ImportController class."""
        # Init the base class.
        super().__init__(c, language='javascript')

    #@+others
    #@+node:ekr.20161101183354.1: *3* js_i.compute_headline
    clean_regex_list1 = [
        # (function name (
        re.compile(r'\s*\(?(function\b\s*[\w]*)\s*\('),
        # name: (function (
        re.compile(r'\s*(\w+\s*\:\s*\(*\s*function\s*\()'),
        # const|let|var name = .* =>
        re.compile(r'\s*(?:const|let|var)\s*(\w+\s*(?:=\s*.*)=>)'),
    ]
    clean_regex_list2 = [
        re.compile(r'(.*\=)(\s*function)'),  # .* = function
    ]
    clean_regex_list3 = [
        re.compile(r'(.*\=\s*new\s*\w+)\s*\(.*(=>)'),  # .* = new name .* =>
        re.compile(r'(.*)\=\s*\(.*(=>)'),  # .* = ( .* =>
        re.compile(r'(.*)\((\s*function)'),  # .* ( function
        re.compile(r'(.*)\(.*(=>)'),  # .* ( .* =>
        re.compile(r'(.*)(\(.*\,\s*function)'),  # .* \( .*, function
    ]
    clean_regex_list4 = [
        re.compile(r'(.*)\(\s*(=>)'),  # .* ( =>
    ]

    def compute_headline(self, s: str) -> str:
        """Return a cleaned up headline s."""
        s = s.strip()
        # Don't clean a headline twice.
        if s.endswith('>>') and s.startswith('<<'):  # pragma: no cover (missing test)
            return s
        for ch in '{(=':
            if s.endswith(ch):
                s = s[:-1].strip()
        # First regex cleanup. Use \1.
        for pattern in self.clean_regex_list1:
            m = pattern.match(s)
            if m:
                s = m.group(1)
                break
        # Second regex cleanup. Use \1 + \2
        for pattern in self.clean_regex_list2:
            m = pattern.match(s)
            if m:
                s = m.group(1) + m.group(2)
                break
        # Third regex cleanup. Use \1 + ' ' + \2
        for pattern in self.clean_regex_list3:
            m = pattern.match(s)
            if m:
                s = m.group(1) + ' ' + m.group(2)
                break
        # Fourth cleanup. Use \1 + ' ' + \2 again
        for pattern in self.clean_regex_list4:  # pragma: no cover (mysterious)
            m = pattern.match(s)
            if m:
                s = m.group(1) + ' ' + m.group(2)
                break
        # Final whitespace cleanups.
        s = s.replace('  ', ' ')
        s = s.replace(' (', '(')
        return g.truncate(s, 100)
    #@-others
#@+node:ekr.20200131110322.2: ** JsLexer...
# JsLex: a lexer for Javascript
# Written by Ned Batchelder. Used by permission.
#
# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/jslex/src/default/NOTICE.txt
#@+node:ekr.20200131110322.4: *3* class Tok
class Tok:
    """A specification for a token class."""

    num = 0

    def __init__(self, name: str, regex: str, next: str = None) -> None:
        self.id = Tok.num
        Tok.num += 1
        self.name = name
        self.regex = regex
        self.next = next
#@+node:ekr.20200131110322.7: *3* class Lexer
class Lexer:
    """A generic multi-state regex-based lexer."""

    #@+others
    #@+node:ekr.20200131110322.8: *4* Lexer.__init__
    def __init__(self, states: Dict, first: Any) -> None:
        self.regexes = {}
        self.toks = {}
        for state, rules in states.items():
            parts = []
            for tok in rules:
                groupid = "t%d" % tok.id
                self.toks[groupid] = tok
                parts.append("(?P<%s>%s)" % (groupid, tok.regex))
            self.regexes[state] = re.compile("|".join(parts), re.MULTILINE | re.VERBOSE)  # |re.UNICODE)
        self.state = first
    #@+node:ekr.20200131110322.9: *4* Lexer.lex
    def lex(self, text: str) -> Generator:
        """Lexically analyze `text`.

        Yields pairs (`name`, `tokentext`).
        """
        end = len(text)
        state = self.state
        regexes = self.regexes
        toks = self.toks
        start = 0
        while start < end:
            for match in regexes[state].finditer(text, start):
                # g.trace(state, start, text, match)
                # g.printObj(regexes[state])
                name = match.lastgroup
                tok = toks[name]
                toktext = match.group(name)
                start += len(toktext)
                yield(tok.name, toktext)
                if tok.next:
                    state = tok.next
                    break
        self.state = state
    #@-others
#@+node:ekr.20200131110322.6: *3* function: literals
def literals(choices: str, prefix: str = "", suffix: str = "") -> str:
    """
    Create a regex from a space-separated list of literal `choices`.

    If provided, `prefix` and `suffix` will be attached to each choice
    individually.

    """
    return "|".join(prefix + re.escape(c) + suffix for c in choices.split())
#@+node:ekr.20200131110322.10: *3* class JsLexer(Lexer)
class JsLexer(Lexer):
    """A Javascript lexer

    >>> lexer = JsLexer()
    >>> list(lexer.lex("a = 1"))
    [('id', 'a'), ('ws', ' '), ('punct', '='), ('ws', ' '), ('dnum', '1')]

    This doesn't properly handle non-Ascii characters in the Javascript source.
    """
    # EKR: Happily, the JS importer doesn't need to handle id's carefully.

    #@+<< constants >>
    #@+node:ekr.20200131190707.1: *4* << constants >> (JsLexer)
    # Because these tokens are matched as alternatives in a regex, longer possibilities
    # must appear in the list before shorter ones, for example, '>>' before '>'.
    #
    # Note that we don't have to detect malformed Javascript, only properly lex
    # correct Javascript, so much of this is simplified.

    # Details of Javascript lexical structure are taken from
    # http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-262.pdf

    # A useful explanation of automatic semicolon insertion is at
    # http://inimino.org/~inimino/blog/javascript_semicolons

    # See https://stackoverflow.com/questions/6314614/match-any-unicode-letter

    both_before = [
        Tok("comment", r"/\*(.|\n)*?\*/"),
        Tok("linecomment", r"//.*?$"),
        Tok("ws", r"\s+"),
        Tok("keyword", literals("""
                                async await
                                break case catch class const continue debugger
                                default delete do else enum export extends
                                finally for function if import in instanceof new
                                return super switch this throw try typeof var
                                void while with
                                """, suffix=r"\b"), next='reg'),
        Tok("reserved", literals("null true false", suffix=r"\b"), next='div'),
        #
        # EKR: This would work if patterns were compiled with the re.UNICODE flag.
        #      However, \w is not the same as valid JS characters.
        #      In any case, the JS importer doesn't need to handle id's carefully.
        #
        # Tok("id",           r"""([\w$])([\w\d]*)""", next='div'),
        #
        Tok("id", r"""
                            ([a-zA-Z_$   ]|\\u[0-9a-fA-Z]{4})       # first char
                            ([a-zA-Z_$0-9]|\\u[0-9a-fA-F]{4})*      # rest chars
                            """, next='div'),
        Tok("hnum", r"0[xX][0-9a-fA-F]+", next='div'),
        Tok("onum", r"0[0-7]+"),
        Tok("dnum", r"""
                            (   (0|[1-9][0-9]*)         # DecimalIntegerLiteral
                                \.                      # dot
                                [0-9]*                  # DecimalDigits-opt
                                ([eE][-+]?[0-9]+)?      # ExponentPart-opt
                            |
                                \.                      # dot
                                [0-9]+                  # DecimalDigits
                                ([eE][-+]?[0-9]+)?      # ExponentPart-opt
                            |
                                (0|[1-9][0-9]*)         # DecimalIntegerLiteral
                                ([eE][-+]?[0-9]+)?      # ExponentPart-opt
                            )
                            """, next='div'),
        Tok("punct", literals("""
                                >>>= === !== >>> <<= >>= <= >= == != << >> &&
                                || += -= *= %= &= |= ^=
                                """), next="reg"),
        Tok("punct", literals("++ -- ) ]"), next='div'),
        Tok("punct", literals("{ } ( [ . ; , < > + - * % & | ^ ! ~ ? : ="), next='reg'),
        Tok("string", r'"([^"\\]|(\\(.|\n)))*?"', next='div'),
        Tok("string", r"'([^'\\]|(\\(.|\n)))*?'", next='div'),
        ]

    both_after = [
        Tok("other", r"."),
        ]

    states = {
        'div':  # slash will mean division
            both_before + [
            Tok("punct", literals("/= /"), next='reg'),
            ] + both_after,

        'reg':  # slash will mean regex
            both_before + [
            Tok("regex",
                r"""
                    /                       # opening slash
                    # First character is..
                    (   [^*\\/[]            # anything but * \ / or [
                    |   \\.                 # or an escape sequence
                    |   \[                  # or a class, which has
                            (   [^\]\\]     #   anything but \ or ]
                            |   \\.         #   or an escape sequence
                            )*              #   many times
                        \]
                    )
                    # Following characters are same, except for excluding a star
                    (   [^\\/[]             # anything but \ / or [
                    |   \\.                 # or an escape sequence
                    |   \[                  # or a class, which has
                            (   [^\]\\]     #   anything but \ or ]
                            |   \\.         #   or an escape sequence
                            )*              #   many times
                        \]
                    )*                      # many times
                    /                       # closing slash
                    [a-zA-Z0-9]*            # trailing flags
                """, next='div'),
            ] + both_after,
        }
    #@-<< constants >>

    def __init__(self) -> None:
        super().__init__(self.states, 'reg')
#@-others

def do_import(c: Cmdr, parent: Position, s: str) -> None:
    """The importer callback for javascript."""
    JS_Importer(c).import_from_string(parent, s)

importer_dict = {
    'extensions': ['.js',],
    'func': do_import,
}
#@@language python
#@@tabwidth -4
#@-leo
