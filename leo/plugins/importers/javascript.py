#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file ../plugins/importers/javascript.py
"""The @auto importer for JavaScript."""
from __future__ import annotations
import re
from typing import Any, Generator, TYPE_CHECKING
from leo.core import leoGlobals as g
from leo.plugins.importers.base_importer import Importer

if TYPE_CHECKING:
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position

#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer(Importer)
class JS_Importer(Importer):

    language = 'javascript'

    # These patterns won't find all functions, but they are a reasonable start.

    # Group 1 must be the block name.
    block_patterns: tuple = (
        # (? function name ( .*? {
        ('function', re.compile(r'\s*?\(?function\b\s*([\w\.]*)\s*\(.*?\{')),

        # name: ( function ( .*? {
        ('function', re.compile(r'\s*([\w.]+)\s*\:\s*\(*\s*function\s*\(.*?{')),

        # var name = ( function ( .*? {
        ('function', re.compile(r'\s*\bvar\s+([\w\.]+)\s*=\s*\(*\s*function\s*\(.*?{')),

        # name = ( function ( .*? {
        ('function', re.compile(r'\s*([\w\.]+)\s*=\s*\(*\s*function\s*\(.*?{')),

        # ('const', re.compile(r'\s*\bconst\s*(\w+)\s*=.*?=>')),
        # ('let', re.compile(r'\s*\blet\s*(\w+)\s*=.*?=>')),
    )

    #@+others
    #@+node:ekr.20230919103544.1: *3* js_i.delete_comments_and_strings
    def delete_comments_and_strings(self, lines: list[str]) -> list[str]:
        """
        JS_Importer.delete_comments_and_strings.

        Return **guide-lines** from the lines, replacing strings, multi-line
        comments and regular expressions with spaces, thereby preserving
        (within the guide-lines) the position of all significant characters.
        """
        string_delims = self.string_list
        line_comment, start_comment, end_comment = g.set_delims_from_language(self.language)
        target = ''  # The string ending a multi-line comment or string.
        escape = '\\'
        result = []
        for line in lines:
            result_line, skip_count = [], 0
            for i, ch in enumerate(line):
                if ch == '\n':
                    break  # Avoid appending the newline twice.
                elif skip_count > 0:
                    # Replace the character with a blank.
                    result_line.append(' ')
                    skip_count -= 1
                elif target:
                    result_line.append(' ')
                    # Clear the target, but skip any remaining characters of the target.
                    if g.match(line, i, target):
                        skip_count = max(0, (len(target) - 1))
                        target = ''
                elif ch == escape:
                    assert skip_count == 0
                    result_line.append(' ')
                    skip_count = 1
                elif line_comment and line.startswith(line_comment, i):
                    # Skip the rest of the line. It can't contain significant characters.
                    break
                elif any(g.match(line, i, z) for z in string_delims):
                    # Allow multi-character string delimiters.
                    result_line.append(' ')
                    for z in string_delims:
                        if g.match(line, i, z):
                            target = z
                            skip_count = max(0, (len(z) - 1))
                            break
                elif start_comment and g.match(line, i, start_comment):
                    result_line.append(' ')
                    target = end_comment
                    skip_count = max(0, len(start_comment) - 1)
                else:
                    result_line.append(ch)

            # End the line and append it to the result.
            # Strip trailing whitespace. It can't affect significant characters.
            end_s = '\n' if line.endswith('\n') else ''
            result.append(''.join(result_line).rstrip() + end_s)
        assert len(result) == len(lines)  # A crucial invariant.
        return result
    #@-others
#@+node:ekr.20231014081529.1: ** JsLex...
# JsLex: a lexer for Javascript
# Written by Ned Batchelder. Used by permission.

# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/jslex/src/default/NOTICE.txt
#@+node:ekr.20231014081617.1: *3* class Tok
class Tok:
    """A specification for a token class."""

    num = 0

    def __init__(self, name: str, regex: str, next: str = None) -> None:
        self.id = Tok.num
        Tok.num += 1
        self.name = name
        self.regex = regex
        self.next = next
#@+node:ekr.20231014081649.1: *3* class Lexer
class Lexer:
    """A generic multi-state regex-based lexer."""

    def __init__(self, states: dict, first: Any) -> None:
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

    #@+others
    #@+node:ekr.20231014082415.1: *4* Lexer.lex
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
#@+node:ekr.20231014081748.1: *3* function: literals
def literals(choices: str, prefix: str = "", suffix: str = "") -> str:
    """
    Create a regex from a space-separated list of literal `choices`.

    If provided, `prefix` and `suffix` will be attached to each choice
    individually.

    """
    return "|".join(prefix + re.escape(c) + suffix for c in choices.split())
#@+node:ekr.20231014081748.2: *3* class JsLexer(Lexer)
class JsLexer(Lexer):
    """A Javascript lexer

    >>> lexer = JsLexer()
    >>> list(lexer.lex("a = 1"))
    [('id', 'a'), ('ws', ' '), ('punct', '='), ('ws', ' '), ('dnum', '1')]

    This doesn't properly handle non-Ascii characters in the Javascript source.
    """
    # EKR: Happily, the JS importer doesn't need to handle id's carefully.

    #@+<< constants: JsLexer>>
    #@+node:ekr.20231014082018.1: *4* << constants: JsLexer>>
    # Because these tokens are matched as alternatives in a regex, longer possibilities
    # must appear in the list before shorter ones, for example, '>>' before '>'.

    # Note that we don't have to detect malformed Javascript, so much of this is simplified.

    # Details of Javascript lexical structure are taken from
    # http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-262.pdf

    # A useful explanation of automatic semicolon insertion is at:
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
    #@-<< constants: JsLexer>>

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
