#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18144: * @file importers/javascript.py
'''The @auto importer for JavaScript.'''
import re
import unittest
import leo.core.leoGlobals as g
import leo.plugins.importers.linescanner as linescanner
Importer = linescanner.Importer
Target = linescanner.Target
#@+others
#@+node:ekr.20140723122936.18049: ** class JS_Importer
class JS_Importer(Importer):

    def __init__(self, importCommands, force_at_others=False, **kwargs):
        '''The ctor for the JS_ImportController class.'''
        # Init the base class.
        super().__init__(
            importCommands,
            gen_refs = False, # Fix #639.
            language = 'javascript',
            state_class = JS_ScanState,
        )

    #@+others
    #@+node:ekr.20180123051226.1: *3* js_i.post_pass & helpers
    def post_pass(self, parent):
        '''
        Optional Stage 2 of the javascript pipeline.

        All substages **must** use the API for setting body text. Changing
        p.b directly will cause asserts to fail later in i.finish().
        '''
        self.clean_all_headlines(parent)
        self.remove_singleton_at_others(parent)
        self.clean_all_nodes(parent)
        self.move_trailing_comments(parent)
        if 0:
            self.unindent_all_nodes(parent)
            #
            # This sub-pass must follow unindent_all_nodes.
            self.promote_trailing_underindented_lines(parent)
            self.promote_last_lines(parent)
            #
            # Usually the last sub-pass, but not in javascript.
            self.delete_all_empty_nodes(parent)
            #
            # Must follow delete_all_empty_nodes.
            self.remove_organizer_nodes(parent)
            # 
            # Remove up to 5 more levels of @others.
            for i in range(5):
                if self.remove_singleton_at_others(parent):
                    self.remove_organizer_nodes(parent)
                else:
                    break
    #@+node:ekr.20180123051401.1: *4* js_i.remove_singleton_at_others
    at_others = re.compile(r'^\s*@others\b')

    def remove_singleton_at_others(self, parent):
        '''Replace @others by the body of a singleton child node.'''
        found = False
        for p in parent.subtree():
            if p.numberOfChildren() == 1:
                child = p.firstChild()
                lines = self.get_lines(p)
                matches = [i for i,s in enumerate(lines) if self.at_others.match(s)]
                if len(matches) == 1:
                    found = True
                    i = matches[0]
                    lines = lines[:i] + self.get_lines(child) + lines[i+1:]
                    self.set_lines(p, lines)
                    self.clear_lines(child) # Delete child later. Is this enough???
                    # g.trace('Clear', child.h)
        return found
    #@+node:ekr.20180123060307.1: *4* js_i.remove_organizer_nodes
    def remove_organizer_nodes(self, parent):
        '''Removed all organizer nodes created by i.delete_all_empty_nodes.'''
        # Careful: Restart this loop whenever we find an organizer.
        ### g.trace(parent.h)
        found = True
        while found:
            found = False
            for p in parent.subtree():
                if p.h.lower() == 'organizer' and not self.get_lines(p):
                    p.promote()
                    p.doDelete()
                    found = True # Restart the loop.
    #@+node:ekr.20200202071105.1: *4* js_i.clean_all_nodes
    def clean_all_nodes(self, parent):
        """Remove common leading whitespace from all nodes."""
        c = self.c
        for p in parent.subtree():
            lines = self.get_lines(p)
            s = ''.join(lines)
            s = g.adjustTripleString(s, tab_width=c.tab_width)
            self.set_lines(p, g.splitLines(s))
    #@+node:ekr.20200202091613.1: *4* js_i.move_trailing_comments & helper (new)
    def move_trailing_comments(self, parent):
        """Move all trailing comments to the start of the next node."""
        for p in parent.subtree():
            next = p.next()
            if next:
                lines = self.get_lines(p)
                head_lines, tail_lines = self.get_trailing_comments(lines)
                if tail_lines:
                    g.trace(p.h, next.h)
                    self.set_lines(p, head_lines)
                    next_lines = self.get_lines(next)
                    self.set_lines(next, tail_lines + next_lines)
    #@+node:ekr.20200202092332.1: *5* js_i.get_trailing_comments
    def get_trailing_comments(self, lines):
        """
        Return the trailing comments of p.
        Return (head_lines, tail_lines).
        """
        s = ''.join(lines)
        head, tail = [], []
        if not s.strip:
            return head, tail
        in_block_comment = False
        head = lines
        for i, line in enumerate(lines):
            s = line.strip()
            if in_block_comment:
                tail.append(line)
                if s.startswith('*/'):
                    in_block_comment = False
            elif s.startswith('/*'):
                in_block_comment = True
                head = lines[:i]
                tail = [line]
            elif s.startswith('//'):
                head = lines[:i]
                tail = [line]
            elif s: # Clear any previous comments.
                head = lines
                tail = []
        return head, tail
    #@+node:ekr.20161105140842.5: *3* js_i.scan_line & helpers
    #@@nobeautify

    op_table = [
        # Longest first in each line.
        # '>>>', '>>>=',
        # '<<<', '<<<=',
        # '>>=',  '<<=',
        '>>', '>=', '>',
        '<<', '<=', '<',
        '++', '+=', '+',
        '--', '-=', '-',
              '*=', '*',
              '/=', '/',
              '%=', '%',
        '&&', '&=', '&',
        '||', '|=', '|',
                    '~',
                    '=',
                    '!', # Unary op can trigger regex.
    ]
    op_string = '|'.join([re.escape(z) for z in op_table])
    op_pattern = re.compile(op_string)

    def scan_line(self, s, prev_state):
        '''
        Update the scan state at the *end* of the line by scanning all of s.

        Distinguishing the the start of a regex from a div operator is tricky:
        http://stackoverflow.com/questions/4726295/
        http://stackoverflow.com/questions/5519596/
        (, [, {, ;, and binops can only be followed by a regexp.
        ), ], }, ids, strings and numbers can only be followed by a div operator.
        '''
        context = prev_state.context
        curlies, parens = prev_state.curlies, prev_state.parens
        # div: '/' is an operator. regex: '/' starts a regex.
        expect = None # (None, 'regex', 'div')
        i = 0
        while i < len(s):
            assert expect is None, expect
            progress = i
            ch, s2 = s[i], s[i:i+2]
            ### if "'function'" in s: g.trace(f"context: {context!r:5} ch: {ch!r}")
            if context == '/*':
                if s2 == '*/':
                    i += 2
                    context = ''
                    expect = 'div'
                else:
                    i += 1 # Eat the next comment char.
            elif context:
                assert context in ('"', "'", '`'), repr(context)
                    # #651: support back tick
                if ch == '\\':
                    i += 2
                elif context == ch:
                    i += 1
                    context = '' # End the string.
                    expect = 'regex'
                else:
                    i += 1 # Eat the string character.
            elif s2 == '//':
                break # The single-line comment ends the line.
            elif s2 == '/*':
                # Start a comment.
                i += 2
                context = '/*'
            elif ch in ('"', "'", '`',):
                # #651: support back tick
                # Start a string.
                i += 1
                context = ch
            elif ch in '_$' or ch.isalpha():
                # An identifier. Only *approximately* correct.
                # http://stackoverflow.com/questions/1661197/
                i += 1
                while i < len(s) and (s[i] in '_$' or s[i].isalnum()):
                    i += 1
                expect = 'div'
            elif ch.isdigit():
                i += 1
                # Only *approximately* correct.
                while i < len(s) and (s[i] in '.+-e' or s[i].isdigit()):
                    i += 1
                # This should work even if the scan ends with '+' or '-'
                expect = 'div'
            elif ch in '?:':
                i += 1
                expect = 'regex'
            elif ch in ';,':
                i += 1
                expect = 'regex'
            elif ch == '\\':
                i += 2
            elif ch == '{':
                i += 1
                curlies += 1
                expect = 'regex'
            elif ch == '}':
                i += 1
                curlies -= 1
                expect = 'div'
            elif ch == '(':
                i += 1
                parens += 1
                expect = 'regex'
            elif ch == ')':
                i += 1
                parens -= 1
                expect = 'div'
            elif ch == '[':
                i += 1
                expect = 'regex'
            elif ch == ']':
                i += 1
                expect = 'div'
            else:
                m = self.op_pattern.match(s, i)
                if m:
                    i += len(m.group(0))
                    expect = 'regex'
                elif ch == '/':
                    g.trace('no lookahead for "/"', repr(s))
                    assert False, i
                else:
                    i += 1
                    expect = None
            # Look for a '/' in the expected context.
            if expect:
                assert not context, repr(context)
                i = g.skip_ws(s, i)
                # Careful // is the comment operator.
                if g.match(s, i, '//'):
                    break
                elif g.match(s, i, '/'):
                    if expect == 'div':
                        i += 1
                    else:
                        assert expect == 'regex', repr(expect)
                        i = self.skip_regex(s,i)
            expect = None
            assert progress < i
        d = {'context':context, 'curlies':curlies, 'parens':parens}
        state = JS_ScanState(d)
        return state
    #@+node:ekr.20161011045426.1: *4* js_i.skip_regex
    def skip_regex(self, s, i):
        '''Skip an *actual* regex /'''
        assert s[i] == '/', (i, repr(s))
        i1 = i
        i += 1
        while i < len(s):
            progress = i
            ch = s[i]
            if ch == '\\':
                i += 2
            elif ch == '/':
                i += 1
                if i < len(s) and s[i] in 'igm':
                    i += 1 # Skip modifier.
                return i
            else:
                i += 1
            assert progress < i
        return i1 # Don't skip ahead.
    #@+node:ekr.20171224145755.1: *3* js_i.starts_block
    func_patterns = [
        re.compile(r'\)\s*=>\s*\{'),
        # re.compile(r'\bclass\b'),
        re.compile(r'^\s*class\b'),
        # re.compile(r'\bfunction\b'),
        # re.compile(r'^\s*(^function\b)|([(]+\s*function\b)|(.*?[(=,]\s*\(?\s*function\b)')
        re.compile(r'^\s*(^function\b)|(.*?[(=,]\s*\(?\s*function\b)')
    ]

    def starts_block(self, i, lines, new_state, prev_state):
        '''True if the new state starts a block.'''
        if new_state.level() <= prev_state.level():
            return False
        # #1481. Partially repeat the logic of js_i.scan_line.
        #        Don't look for patterns inside strings.
        #        This could fail if one of the patterns is in a regex.
        in_string = False
        line = lines[i]
        for i, ch in enumerate(line):
            if in_string and ch == in_string:
                in_string = None
            elif in_string:
                pass
            elif ch in '"`\'':
                in_string = ch
            else:
                for pattern in self.func_patterns:
                    if pattern.match(line[i:]) is not None:
                        ### g.trace(repr(line))
                        return True
        return False
    #@+node:ekr.20200131193217.1: *3* js_i.ends_block
    def ends_block(self, line, new_state, prev_state, stack):
        '''True if line ends the block.'''
        # Comparing new_state against prev_state does not work for python.
        top = stack[-1]
        ### g.trace(f"{new_state.level() < top.state.level():1}") # , {line!r}")
        return new_state.level() < top.state.level()
    #@+node:ekr.20161101183354.1: *3* js_i.clean_headline
    clean_regex_list1 = [
        re.compile(r'\s*\(?(function\b\s*[\w]*)\s*\('),
            # (function name (
        re.compile(r'\s*(\w+\s*\:\s*\(*\s*function\s*\()'),
            # name: (function (
        re.compile(r'\s*(?:const|let|var)\s*(\w+\s*(?:=\s*.*)=>)'),
            # const|let|var name = .* =>
    ]
    clean_regex_list2 = [
        re.compile(r'(.*\=)(\s*function)'),
            # .* = function
    ]
    clean_regex_list3 = [
        re.compile(r'(.*\=\s*new\s*\w+)\s*\(.*(=>)'),
            # .* = new name .* =>
        re.compile(r'(.*)\=\s*\(.*(=>)'),
            # .* = ( .* =>
        re.compile(r'(.*)\((\s*function)'),
            # .* ( function
        re.compile(r'(.*)\(.*(=>)'),
            # .* ( .* =>
        re.compile(r'(.*)(\(.*\,\s*function)'),
            # .* \( .*, function
    ]
    clean_regex_list4 = [
        re.compile(r'(.*)\(\s*(=>)'),
            # .* ( =>
    ]

    def clean_headline(self, s, p=None, trace=False):
        '''Return a cleaned up headline s.'''
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
    '''A class representing the state of the javascript line-oriented scan.'''

    def __init__(self, d=None):
        '''JS_ScanState ctor'''
        if d:
            # d is *different* from the dict created by i.scan_line.
            self.context = d.get('context')
            self.curlies = d.get('curlies')
            self.parens = d.get('parens')
        else:
            self.context = ''
            self.curlies = self.parens = 0

    def __repr__(self):
        '''JS_ScanState.__repr__'''
        return 'JS_ScanState context: %r curlies: %s parens: %s' % (
            self.context, self.curlies, self.parens)

    __str__ = __repr__

    #@+others
    #@+node:ekr.20161119115505.1: *3* js_state.level
    def level(self):
        '''JS_ScanState.level.'''
        return (self.curlies, self.parens)
    #@+node:ekr.20161119051049.1: *3* js_state.update
    def update(self, data):
        '''
        Update the state using the 6-tuple returned by i.scan_line.
        Return i = data[1]
        '''
        context, i, delta_c, delta_p, delta_s, bs_nl = data
        # self.bs_nl = bs_nl
        self.context = context
        self.curlies += delta_c
        self.parens += delta_p
        # self.squares += delta_s
        return i

    #@-others

#@+node:ekr.20200131070055.1: ** class TestJSImporter
class TestJSImporter(unittest.TestCase):
    #@+others
    #@+node:ekr.20200202093420.1: *3* test_get_trailing_comments
    def test_get_trailing_comments(self):
        
        table = (
            # Test 1
            ( """\
    head
    // tail""", 1),

            # Test 2
            ("""\
    head
    /* comment 1
     * comment 2
     */""", 3),
     
            # Test 3
            ("""\
    head
    /* comment 1
     * comment 2
     */
    tail""", 0), # no tail

            # Test 4
            ("""\
    head
    // comment
    tail""", 0), # no tail

    ) # End table.
        for s, expected_length in table:
            x = JS_Importer(None)
            s = g.adjustTripleString(s, -4)
            lines = g.splitLines(s)
            head, tail = x.get_trailing_comments(lines)
            expected_lines = lines[-expected_length:] if expected_length else []
            assert tail == expected_lines , (repr(tail), repr(expected_lines))
    #@-others
#@+node:ekr.20200131110322.2: ** JsLex (not used yet)
# JsLex: a lexer for Javascript
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
            self.regexes[state] = re.compile("|".join(parts), re.MULTILINE|re.VERBOSE)

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
                name = match.lastgroup
                tok = toks[name]
                toktext = match.group(name)
                start += len(toktext)
                yield (tok.name, toktext)

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
    return "|".join(prefix+re.escape(c)+suffix for c in choices.split())

#@+node:ekr.20200131110322.10: *3* class JsLexer(Lexer)
class JsLexer(Lexer):
    """A Javascript lexer

    >>> lexer = JsLexer()
    >>> list(lexer.lex("a = 1"))
    [('id', 'a'), ('ws', ' '), ('punct', '='), ('ws', ' '), ('dnum', '1')]

    This doesn't properly handle non-Ascii characters in the Javascript source.

    """
    
    #@+<< constants >>
    #@+node:ekr.20200131190707.1: *4* << constants >>

    # Because these tokens are matched as alternatives in a regex, longer possibilities
    # must appear in the list before shorter ones, for example, '>>' before '>'.
    #
    # Note that we don't have to detect malformed Javascript, only properly lex
    # correct Javascript, so much of this is simplified.

    # Details of Javascript lexical structure are taken from
    # http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-262.pdf

    # A useful explanation of automatic semicolon insertion is at
    # http://inimino.org/~inimino/blog/javascript_semicolons

    both_before = [
        Tok("comment",      r"/\*(.|\n)*?\*/"),
        Tok("linecomment",  r"//.*?$"),
        Tok("ws",           r"\s+"),
        Tok("keyword",      literals("""
                                break case catch class const continue debugger
                                default delete do else enum export extends
                                finally for function if import in instanceof new
                                return super switch this throw try typeof var
                                void while with
                                """, suffix=r"\b"), next='reg'),
        Tok("reserved",     literals("null true false", suffix=r"\b"), next='div'),
        Tok("id",           r"""
                            ([a-zA-Z_$   ]|\\u[0-9a-fA-Z]{4})       # first char
                            ([a-zA-Z_$0-9]|\\u[0-9a-fA-F]{4})*      # rest chars
                            """, next='div'),
        Tok("hnum",         r"0[xX][0-9a-fA-F]+", next='div'),
        Tok("onum",         r"0[0-7]+"),
        Tok("dnum",         r"""
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
        Tok("punct",        literals("""
                                >>>= === !== >>> <<= >>= <= >= == != << >> && 
                                || += -= *= %= &= |= ^=
                                """), next="reg"),
        Tok("punct",        literals("++ -- ) ]"), next='div'),
        Tok("punct",        literals("{ } ( [ . ; , < > + - * % & | ^ ! ~ ? : ="), next='reg'),
        Tok("string",       r'"([^"\\]|(\\(.|\n)))*?"', next='div'),
        Tok("string",       r"'([^'\\]|(\\(.|\n)))*?'", next='div'),
        ]

    both_after = [
        Tok("other",        r"."),
        ]

    states = {
        'div': # slash will mean division
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

    #@+others
    #@+node:ekr.20200131110322.11: *4* JsLexer.__init__
    def __init__(self):
        super(JsLexer, self).__init__(self.states, 'reg')


    #@-others
#@+node:ekr.20200131110608.12: *3* function: js_to_c_for_gettext (Will never be used)
def js_to_c_for_gettext(js):
    """Convert the Javascript source `js` into something resembling C for xgettext.

    What actually happens is that all the regex literals are replaced with
    "REGEX".

    """
    def escape_quotes(m):
        """Used in a regex to properly escape double quotes."""
        s = m.group(0)
        return r'\"' if s == '"' else s

    lexer = JsLexer()
    c = []
    for name, tok in lexer.lex(js):
        if name == 'regex':
            # C doesn't grok regexes, and they aren't needed for gettext,
            # so just output a string instead.
            tok = '"REGEX"'
        elif name == 'string':
            # C doesn't have single-quoted strings, so make all strings
            # double-quoted.
            if tok.startswith("'"):
                guts = re.sub(r"\\.|.", escape_quotes, tok[1:-1])
                tok = '"' + guts + '"'
        elif name == 'id':
            # C can't deal with Unicode escapes in identifiers.  We don't
            # need them for gettext anyway, so replace them with something
            # innocuous
            tok = tok.replace("\\", "U")
        c.append(tok)
    return ''.join(c)
#@-others
importer_dict = {
    'class': JS_Importer,
    'extensions': ['.js',],
}
#@@language python
#@@tabwidth -4
#@-leo
