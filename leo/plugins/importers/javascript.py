#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file ../plugins/importers/javascript.py
"""The @auto importer for JavaScript."""
import re
from leo.core import leoGlobals as g  # Required
from leo.plugins.importers.linescanner import Importer, scan_tuple
#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer
class JS_Importer(Importer):

    def __init__(self, importCommands, force_at_others=False, **kwargs):
        """The ctor for the JS_ImportController class."""
        # Init the base class.
        super().__init__(
            importCommands,
            gen_refs=False,  # Fix #639.
            language='javascript',
            state_class=JS_ScanState,
        )

    #@+others
    #@+node:ekr.20161105140842.5: *3* js_i.scan_line
    def scan_line(self, s, prev_state):
        """
        Update the scan state at the *end* of the line.
        Return JS_ScanState({'context':context, 'curlies':curlies, 'parens':parens})

        This code uses JsLex to scan the tokens, which scans strings and regexs properly.

        This code also handles *partial* tokens: tokens continued from the
        previous line or continued to the next line.
        """
        context = prev_state.context
        curlies, parens = prev_state.curlies, prev_state.parens
        # Scan tokens, updating context and counts.
        prev_val = None
        for kind, val in JsLexer().lex(s):
            # g.trace(f"context: {context:2} kind: {kind:10} val: {val!r}")
            if context:
                if context in ('"', "'") and kind in ('other', 'punct') and val == context:
                    context = ''
                elif (
                    context == '/*'
                    and kind in ('other', 'punct')
                    and prev_val == '*'
                    and val == '/'
                ):
                    context = ''
            elif kind in ('other', 'punct') and val in ('"', "'"):
                context = val
            elif kind in ('other', 'punct') and val == '*' and prev_val == '/':
                context = '/*'
            elif kind in ('other', 'punct'):
                if val == '*' and prev_val == '/':
                    context = '/*'
                elif val == '{':
                    curlies += 1
                elif val == '}':
                    curlies -= 1
                elif val == '(':
                    parens += 1
                elif val == ')':
                    parens -= 1
            prev_val = val
        d = {'context': context, 'curlies': curlies, 'parens': parens}
        state = JS_ScanState(d)
        return state
    #@+node:ekr.20171224145755.1: *3* js_i.starts_block
    func_patterns = [
        re.compile(r'.*?\)\s*=>\s*\{'),
        re.compile(r'\s*class\b'),
        re.compile(r'\s*function\b'),
        re.compile(r'.*?[(=,]\s*function\b'),
    ]

    def starts_block(self, i, lines, new_state, prev_state):
        """True if the new state starts a block."""
        if new_state.level() <= prev_state.level():
            return False
        # Remove strings and regexs from the line before applying the patterns.
        cleaned_line = []
        for kind, val in JsLexer().lex(lines[i]):
            if kind not in ('string', 'regex'):
                cleaned_line.append(val)
        # Search for any of the patterns.
        line = ''.join(cleaned_line)
        for pattern in self.func_patterns:
            if pattern.match(line) is not None:
                return True
        return False
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

    def compute_headline(self, s, p=None, trace=False):
        """Return a cleaned up headline s."""
        # pylint: disable=arguments-differ
        s = s.strip()
        # Don't clean a headline twice.
        if s.endswith('>>') and s.startswith('<<'):
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
        for pattern in self.clean_regex_list4:
            m = pattern.match(s)
            if m:
                s = m.group(1) + ' ' + m.group(2)
                break
        # Final whitespace cleanups.
        s = s.replace('  ', ' ')
        s = s.replace(' (', '(')
        return g.truncate(s, 100)
    #@-others
#@+node:ekr.20161105092745.1: ** class JS_ScanState
class JS_ScanState:
    """A class representing the state of the javascript line-oriented scan."""

    def __init__(self, d=None):
        """JS_ScanState ctor"""
        if d:
            # d is *different* from the dict created by i.scan_line.
            self.context = d.get('context')
            self.curlies = d.get('curlies')
            self.parens = d.get('parens')
        else:
            self.context = ''
            self.curlies = self.parens = 0

    def __repr__(self):
        """JS_ScanState.__repr__"""
        return 'JS_ScanState context: %r curlies: %s parens: %s' % (
            self.context, self.curlies, self.parens)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20220731093145.1: *3* js_state.in_context
    def in_context(self) -> bool:
        return bool(self.context or self.parens)
    #@+node:ekr.20161119115505.1: *3* js_state.level
    def level(self) -> int:
        """JS_ScanState.level."""
        return self.curlies  # (self.curlies, self.parens)
    #@+node:ekr.20161119051049.1: *3* js_state.update
    def update(self, data: scan_tuple) -> int:
        """
        Javascript_ScanState: Update the state using the given scan_tuple.
        """
        self.context = data.context
        self.curlies += data.delta_c
        self.parens += data.delta_p
        return data.i
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

    def __init__(self, name, regex, next=None):
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
    def __init__(self, states, first):
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
    def lex(self, text):
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
def literals(choices, prefix="", suffix=""):
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

    def __init__(self):
        super().__init__(self.states, 'reg')
#@-others
importer_dict = {
    'func': JS_Importer.do_import(),
    'extensions': ['.js',],
}
#@@language python
#@@tabwidth -4
#@-leo
