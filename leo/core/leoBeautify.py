#@+leo-ver=5-thin
#@+node:ekr.20150521115018.1: * @file leoBeautify.py
"""Leo's beautification classes."""
#@+<< imports >>
#@+node:ekr.20150530081336.1: ** << imports >>
try:
    import leo.core.leoGlobals as g
except ImportError:
    # Allow main() to run in any folder containing leoGlobals.py
    # pylint: disable=relative-import
    import leoGlobals as g

    # Create a dummy decorator.

    def command(func):
        return func

    g.command = command

import ast
import optparse
import os
import sys
import time
import token as token_module
import tokenize

try:
    # pylint: disable=import-error
        # We can't assume the user has this.
    import black
except Exception:
    black = None
#@-<< imports >>
#@+others
#@+node:ekr.20150528131012.1: **  commands (leoBeautifier.py)
#@+node:ekr.20150528131012.3: *3* beautify-c (changed)
@g.command('beautify-c')
@g.command('pretty-print-c')
def beautifyCCode(event):
    """Beautify all C code in the selected tree."""
    c = event.get('c')
    if not c:
        return
    if should_kill_beautify(c.p):
        return
    u, undoType = c.undoer, 'beautify-c'
    pp = CPrettyPrinter(c)
    u.beforeChangeGroup(c.p, undoType)
    dirtyVnodeList = []
    changed = False
    for p in c.p.self_and_subtree():
        if g.scanForAtLanguage(c, p) == "c":
            bunch = u.beforeChangeNodeContents(p)
            s = pp.indent(p)
            if p.b != s:
                # g.es('changed: %s' % (p.h))
                p.b = s
                dirtyVnodeList2 = p.setDirty() # Was p.v.setDirty.
                dirtyVnodeList.extend(dirtyVnodeList2)
                ### p.v.setDirty()
                ### dirtyVnodeList.append(p.v)
                u.afterChangeNodeContents(p, undoType, bunch)
                changed = True
    if changed:
        u.afterChangeGroup(
            c.p, undoType, reportFlag=False, dirtyVnodeList=dirtyVnodeList
        )
    c.bodyWantsFocus()
#@+node:ekr.20150528131012.4: *3* beautify-node
@g.command('beautify-node')
@g.command('pretty-print-node')
def prettyPrintPythonNode(event):
    """Beautify a single Python node."""
    c = event.get('c')
    if not c:
        return
    t1 = time.process_time()
    pp = PythonTokenBeautifier(c)
    pp.errors = 0
    changed = 0
    if g.scanForAtLanguage(c, c.p) == "python":
        if pp.prettyPrintNode(c.p):
            changed += 1
    pp.end_undo()
    if g.unitTesting:
        return
    t2 = time.process_time()
    g.es_print(
        f"changed {changed} node{g.plural(changed)}, "
        f"{pp.errors} error{g.plural(pp.errors)} "
        f"in {t2-t1:4.2f} sec."
    )
#@+node:ekr.20150528131012.5: *3* beautify-tree
@g.command('beautify-tree')
@g.command('pretty-print-tree')
def beautifyPythonTree(event):
    """Beautify the Python code in the selected outline."""
    c = event.get('c')
    p0 = event.get('p0')
    # is_auto = bool(p0)
    p0 = p0 or c.p
    if should_kill_beautify(p0):
        return
    t1 = time.process_time()
    pp = PythonTokenBeautifier(c)
    pp.errors = 0
    changed = errors = total = 0
    for p in p0.self_and_subtree():
        if g.scanForAtLanguage(c, p) == "python":
            total += 1
            if pp.prettyPrintNode(p):
                changed += 1
            errors += pp.errors
            pp.errors = 0
    pp.end_undo()
    if g.unitTesting:
        return
    t2 = time.process_time()
    g.es_print(
        f"scanned {total} node{g.plural(total)}, "
        f"changed {changed} node{g.plural(changed)}, "
        f"{errors} error{g.plural(errors)} "
        f"in {t2-t1:4.2f} sec."
    )


                # pp.n_changed_nodes, g.plural(pp.n_changed_nodes), t2 - t1))

        # if is_auto:
            # if pp.n_changed_nodes > 0:
                # g.es_print('auto-beautified %s node%s in\n%s' % (
                    # pp.n_changed_nodes,
                    # g.plural(pp.n_changed_nodes),
                    # p0.h))
        # else:
            # g.es_print('beautified total %s node%s in %4.2f sec.' % (
                # pp.n_changed_nodes, g.plural(pp.n_changed_nodes), t2 - t1))
#@+node:ekr.20190830043650.1: *3* blacken-check-tree
@g.command('blkc')
@g.command('blacken-check-tree')
def blacken_check_tree(event):
    """
    Run black on all nodes of the selected tree, reporting only errors.
    """
    c = event.get('c')
    if not c:
        return
    if black:
        BlackCommand(c).blacken_tree(c.p, diff_flag=False, check_flag=True)
    else:
        g.es_print('can not import black')
#@+node:ekr.20190829163640.1: *3* blacken-diff-node
@g.command('blacken-diff-node')
def blacken_diff_node(event):
    """
    Run black on all nodes of the selected node.
    """
    c = event.get('c')
    if not c:
        return
    if black:
        BlackCommand(c).blacken_node(c.p, diff_flag=True)
    else:
        g.es_print('can not import black')
#@+node:ekr.20190829163652.1: *3* blacken-diff-tree
@g.command('blkd')
@g.command('blacken-diff-tree')
def blacken_diff_tree(event):
    """
    Run black on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    """
    c = event.get('c')
    if not c:
        return
    if black:
        BlackCommand(c).blacken_tree(c.p, diff_flag=True)
    else:
        g.es_print('can not import black')
#@+node:ekr.20190725155006.1: *3* blacken-node
@g.command('blacken-node')
def blacken_node(event):
    """
    Run black on all nodes of the selected node.
    """
    c = event.get('c')
    if not c:
        return
    if black:
        BlackCommand(c).blacken_node(c.p, diff_flag=False)
    else:
        g.es_print('can not import black')
#@+node:ekr.20190729105252.1: *3* blacken-tree
@g.command('blk')
@g.command('blacken-tree')
def blacken_tree(event):
    """
    Run black on all nodes of the selected tree,
    or the first @<file> node in an ancestor.
    """
    c = event.get('c')
    if not c:
        return
    if black:
        BlackCommand(c).blacken_tree(c.p, diff_flag=False)
    else:
        g.es_print('can not import black')
#@+node:ekr.20150528091356.1: **  top-level functions (leoBeautifier.py)
#@+node:ekr.20150530061745.1: *3* main (external entry) & helpers
def main():
    """External entry point for Leo's beautifier."""
    t1 = time.time()
    base = g.os_path_abspath(os.curdir)
    files, options = scan_options()
    for path in files:
        path = g.os_path_finalize_join(base, path)
        beautify(options, path)
    print('beautified %s files in %4.2f sec.' % (len(files), time.time()-t1))
#@+node:ekr.20150601170125.1: *4* beautify (stand alone)
def beautify(options, path):
    """Beautify the file with the given path."""
    fn = g.shortFileName(path)
    s, e = g.readFileIntoString(path)
    if not s:
        return
    print(f"beautifying {fn}")
    try:
        s1 = g.toEncodedString(s)
        node1 = ast.parse(s1, filename='before', mode='exec')
    except IndentationError:
        g.warning(f"IndentationError: can't check {fn}")
        return
    except SyntaxError:
        g.warning(f"SyntaxError: can't check {fn}")
        return
    readlines = g.ReadLinesClass(s).next
    tokens = list(tokenize.generate_tokens(readlines))
    beautifier = PythonTokenBeautifier(c=None)
    s2 = beautifier.run(tokens)
    try:
        s2_e = g.toEncodedString(s2)
        node2 = ast.parse(s2_e, filename='before', mode='exec')
    except IndentationError:
        g.warning(f"{fn}: IndentationError in result")
        g.es_print(f"{fn} will not be changed")
        g.printObj(s2, tag='RESULT')
        return
    except SyntaxError:
        g.warning(f"{fn}: Syntax error in result")
        g.es_print(f"{fn} will not be changed")
        g.printObj(s2, tag='RESULT')
        return
    except Exception:
        g.warning(f"{fn}: Unexpected exception creating the \"after\" parse tree")
        g.es_print(f"{fn} will not be changed")
        g.es_exception()
        g.printObj(s2, tag='RESULT')
        return
    try:
        beautifier.compare_two_asts(node1, node2)
    except Exception:
        print(f"failed to beautify {fn}")
        return
    with open(path, 'wb') as f:
        f.write(s2_e)
#@+node:ekr.20150601162203.1: *4* scan_options (stand alone)
def scan_options():
    """Handle all options. Return a list of files."""
    # This automatically implements the --help option.
    usage = "usage: python -m leo.core.leoBeautify file1, file2, ..."
    parser = optparse.OptionParser(usage=usage)
    add = parser.add_option
    add(
        '-d',
        '--debug',
        action='store_true',
        dest='debug',
        help='print the list of files and exit',
    )
    # add('-k', '--keep-blank-lines', action='store_true', dest='keep',
        # help='keep-blank-lines')
    # Parse the options.
    options, files = parser.parse_args()
    if options.debug:
        # Print the list of files and exit.
        g.trace('files...', files)
        sys.exit(0)
    return files, options
#@+node:ekr.20150602154951.1: *3* should_beautify
def should_beautify(p):
    """
    Return True if @beautify is in effect for node p.
    Ambiguous directives have no effect.
    """
    for p2 in p.self_and_parents(copy=False):
        d = g.get_directives_dict(p2)
        if 'killbeautify' in d:
            return False
        if 'beautify' in d and 'nobeautify' in d:
            if p == p2:
                # honor whichever comes first.
                for line in g.splitLines(p2.b):
                    if line.startswith('@beautify'):
                        return True
                    if line.startswith('@nobeautify'):
                        return False
                g.trace('can not happen', p2.h)
                return False
            # The ambiguous node has no effect.
            # Look up the tree.
            pass
        elif 'beautify' in d:
            return True
        if 'nobeautify' in d:
            # This message would quickly become annoying.
            # g.warning(f"{p.h}: @nobeautify")
            return False
    # The default is to beautify.
    return True
#@+node:ekr.20150602204440.1: *3* should_kill_beautify
def should_kill_beautify(p):
    """Return True if p.b contains @killbeautify"""
    return 'killbeautify' in g.get_directives_dict(p)
#@+node:ekr.20190908033048.1: ** class AstNotEqual (Exception)
class AstNotEqual(Exception):
    """The two given AST's are not equivalent."""
#@+node:ekr.20190725154916.1: ** class BlackCommand
class BlackCommand:
    """A class to run black on all Python @<file> nodes in c.p's tree."""

    # tag1 must be executable, and can't be pass.
    tag1 = "if 1: print('') # black-tag1:::"
    tag2 = ":::black-tag2"
    tag3 = "# black-tag3:::"

    def __init__(self, c):
        self.c = c
        self.wrapper = c.frame.body.wrapper
        self.reloadSettings()

    #@+others
    #@+node:ekr.20190926105124.1: *3* black.reloadSettings
    #@@nobeautify

    def reloadSettings(self):
        c = self.c
        keep_comments = c.config.getBool('black-keep-comment-indentation', default=True)
        self.sanitizer = SyntaxSanitizer(c, keep_comments)
        self.line_length = c.config.getInt("black-line-length") or 88
        # This should be on a single line,
        # so the check-settings script in leoSettings.leo will see them.
        self.normalize_strings = c.config.getBool("black-string-normalization", default=False)
    #@+node:ekr.20190725154916.7: *3* black.blacken_node
    def blacken_node(self, root, diff_flag, check_flag=False):
        """Run black on all Python @<file> nodes in root's tree."""
        c = self.c
        if not black or not root:
            return
        t1 = time.process_time()
        self.changed, self.errors, self.total = 0, 0, 0
        self.undo_type = 'blacken-node'
        self.blacken_node_helper(root, check_flag, diff_flag)
        t2 = time.process_time()
        if not g.unitTesting:
            print(
                f'{root.h}: scanned {self.total} node{g.plural(self.total)}, '
                f'changed {self.changed} node{g.plural(self.changed)}, '
                f'{self.errors} error{g.plural(self.errors)} '
                f'in {t2-t1:5.2f} sec.'
            )
        if self.changed or self.errors:
            c.redraw()
    #@+node:ekr.20190729065756.1: *3* black.blacken_tree
    def blacken_tree(self, root, diff_flag, check_flag=False):
        """Run black on all Python @<file> nodes in root's tree."""
        c = self.c
        if not black or not root:
            return
        t1 = time.process_time()
        self.changed, self.errors, self.total = 0, 0, 0
        undo_type = 'blacken-tree'
        bunch = c.undoer.beforeChangeTree(root)
        # Blacken *only* the selected tree.
        changed = False
        for p in root.self_and_subtree():
            if self.blacken_node_helper(p, check_flag, diff_flag):
                changed = True
        if changed:
            c.setChanged(True)
            c.undoer.afterChangeTree(root, undo_type, bunch)
        t2 = time.process_time()
        if not g.unitTesting:
            print(
                f'{root.h}: scanned {self.total} node{g.plural(self.total)}, '
                f'changed {self.changed} node{g.plural(self.changed)}, '
                f'{self.errors} error{g.plural(self.errors)} '
                f'in {t2-t1:5.2f} sec.'
            )
        if self.changed and not c.changed:
            c.setChanged(True)
        if self.changed or self.errors:
            c.redraw()
    #@+node:ekr.20190726013924.1: *3* black.blacken_node_helper (changed)
    def blacken_node_helper(self, p, check_flag, diff_flag):
        """
        blacken p.b, incrementing counts and stripping unnecessary blank lines.
        
        Return True if p.b was actually changed.
        """
        trace = 'black' in g.app.debug and not g.unitTesting
        if not should_beautify(p):
            return False
        c = self.c
        self.total += 1
        language = g.findLanguageDirectives(c, p)
        if language != 'python':
            g.trace(f"skipping node: {p.h}")
            return False
        body = p.b.rstrip() + '\n'
        comment_string, body2 = self.sanitizer.comment_leo_lines(p=p)
        try:
            # Support black, version 19.3b0.
            mode = black.FileMode()
            mode.line_length = self.line_length
            mode.string_normalization = self.normalize_strings
            # Note: format_str does not check parse trees,
            #       so in effect, it already runs in fast mode.
            body3 = black.format_str(body2, mode=mode)
        except IndentationError:
            g.warning(f"IndentationError: Can't blacken {p.h}")
            g.es_print(f"{p.h} will not be changed")
            g.printObj(body2, tag='Sanitized syntax')
            if g.unitTesting:
                raise
            p.v.setMarked()
            return False
        except(SyntaxError, black.InvalidInput):
            g.warning(f"SyntaxError: Can't blacken {p.h}")
            g.es_print(f"{p.h} will not be changed")
            g.printObj(body2, tag='Sanitized syntax')
            if g.unitTesting:
                raise
            p.v.setMarked()
            return False
        except Exception:
            g.warning(f"Unexpected exception: {p.h}")
            g.es_print(f"{p.h} will not be changed")
            g.printObj(body2, tag='Sanitized syntax')
            g.es_exception()
            if g.unitTesting:
                raise
            p.v.setMarked()
            return False
        if trace:
            g.printObj(body2, tag='Sanitized syntax')
        result = self.sanitizer.uncomment_leo_lines(comment_string, p, body3)
        if check_flag or result == body:
            if not g.unitTesting:
                return False
        if diff_flag:
            print('=====', p.h)
            print(black.diff(body, result, "old", "new")[16 :].rstrip()+'\n')
            return False
        # Update p.b and set undo params.
        self.changed += 1
        p.b = result
        c.frame.body.updateEditors()
        p.v.contentModified()
        c.undoer.setUndoTypingParams(p, 'blacken-node', oldText=body, newText=result)
        if not p.v.isDirty():
            p.setDirty() # Was p.v.setDirty.
        return True
    #@-others
#@+node:ekr.20110917174948.6903: ** class CPrettyPrinter
class CPrettyPrinter:
    #@+others
    #@+node:ekr.20110917174948.6904: *3* cpp.__init__
    def __init__(self, c):
        """Ctor for CPrettyPrinter class."""
        self.c = c
        self.brackets = 0
            # The brackets indentation level.
        self.p = None
            # Set in indent.
        self.parens = 0
            # The parenthesis nesting level.
        self.result = []
            # The list of tokens that form the final result.
        self.tab_width = 4


            # The number of spaces in each unit of leading indentation.
    #@+node:ekr.20110917174948.6911: *3* cpp.indent & helpers
    def indent(self, p, toList=False, giveWarnings=True):
        """Beautify a node with @language C in effect."""
        if not should_beautify(p):
            return None
        if not p.b:
            return None
        self.p = p.copy()
        aList = self.tokenize(p.b)
        assert ''.join(aList) == p.b
        aList = self.add_statement_braces(aList, giveWarnings=giveWarnings)
        self.bracketLevel = 0
        self.parens = 0
        self.result = []
        for s in aList:
            self.put_token(s)
        if toList:
            return self.result
        return ''.join(self.result)
    #@+node:ekr.20110918225821.6815: *4* add_statement_braces
    def add_statement_braces(self, s, giveWarnings=False):
        p = self.p

        def oops(message, i, j):
            # This can be called from c-to-python, in which case warnings should be suppressed.
            if giveWarnings:
                g.error('** changed ', p.h)
                g.es_print('%s after\n%s' % (message, repr(''.join(s[i : j]))))

        i, n, result = 0, len(s), []
        while i < n:
            token = s[i]
            progress = i
            if token in ('if', 'for', 'while'):
                j = self.skip_ws_and_comments(s, i+1)
                if self.match(s, j, '('):
                    j = self.skip_parens(s, j)
                    if self.match(s, j, ')'):
                        old_j = j + 1
                        j = self.skip_ws_and_comments(s, j+1)
                        if self.match(s, j, ';'):
                            # Example: while (*++prefix);
                            result.extend(s[i : j])
                        elif self.match(s, j, '{'):
                            result.extend(s[i : j])
                        else:
                            oops("insert '{'", i, j)
                            # Back up, and don't go past a newline or comment.
                            j = self.skip_ws(s, old_j)
                            result.extend(s[i : j])
                            result.append(' ')
                            result.append('{')
                            result.append('\n')
                            i = j
                            j = self.skip_statement(s, i)
                            result.extend(s[i : j])
                            result.append('\n')
                            result.append('}')
                            oops("insert '}'", i, j)
                    else:
                        oops("missing ')'", i, j)
                        result.extend(s[i : j])
                else:
                    oops("missing '('", i, j)
                    result.extend(s[i : j])
                i = j
            else:
                result.append(token)
                i += 1
            assert progress < i
        return result
    #@+node:ekr.20110919184022.6903: *5* skip_ws
    def skip_ws(self, s, i):
        while i < len(s):
            token = s[i]
            if token.startswith(' ') or token.startswith('\t'):
                i += 1
            else:
                break
        return i
    #@+node:ekr.20110918225821.6820: *5* skip_ws_and_comments
    def skip_ws_and_comments(self, s, i):
        while i < len(s):
            token = s[i]
            if token.isspace():
                i += 1
            elif token.startswith('//') or token.startswith('/*'):
                i += 1
            else:
                break
        return i
    #@+node:ekr.20110918225821.6817: *5* skip_parens
    def skip_parens(self, s, i):
        """Skips from the opening ( to the matching ).

        If no matching is found i is set to len(s)"""
        assert self.match(s, i, '(')
        level = 0
        while i < len(s):
            ch = s[i]
            if ch == '(':
                level += 1
                i += 1
            elif ch == ')':
                level -= 1
                if level <= 0:
                    return i
                i += 1
            else:
                i += 1
        return i
    #@+node:ekr.20110918225821.6818: *5* skip_statement
    def skip_statement(self, s, i):
        """Skip to the next ';' or '}' token."""
        while i < len(s):
            if s[i] in ';}':
                i += 1
                break
            else:
                i += 1
        return i
    #@+node:ekr.20110917204542.6967: *4* put_token & helpers
    def put_token(self, s):
        """Append token s to self.result as is,
        *except* for adjusting leading whitespace and comments.

        '{' tokens bump self.brackets or self.ignored_brackets.
        self.brackets determines leading whitespace.
        """
        if s == '{':
            self.brackets += 1
        elif s == '}':
            self.brackets -= 1
            self.remove_indent()
        elif s == '(':
            self.parens += 1
        elif s == ')':
            self.parens -= 1
        elif s.startswith('\n'):
            if self.parens <= 0:
                s = '\n%s' % (' ' * self.brackets * self.tab_width)
            else:
                pass  # Use the existing indentation.
        elif s.isspace():
            if self.parens <= 0 and self.result and self.result[-1].startswith('\n'):
                # Kill the whitespace.
                s = ''
            else:
                pass  # Keep the whitespace.
        elif s.startswith('/*'):
            s = self.reformat_block_comment(s)
        else:
            pass  # put s as it is.
        if s:
            self.result.append(s)
    #@+node:ekr.20110917204542.6968: *5* prev_token
    def prev_token(self, s):
        """Return the previous token, ignoring whitespace and comments."""
        i = len(self.result) - 1
        while i >= 0:
            s2 = self.result[i]
            if s == s2:
                return True
            if s.isspace() or s.startswith('//') or s.startswith('/*'):
                i -= 1
            else:
                return False
    #@+node:ekr.20110918184425.6916: *5* reformat_block_comment
    def reformat_block_comment(self, s):
        return s
    #@+node:ekr.20110917204542.6969: *5* remove_indent
    def remove_indent(self):
        """Remove one tab-width of blanks from the previous token."""
        w = abs(self.tab_width)
        if self.result:
            s = self.result[-1]
            if s.isspace():
                self.result.pop()
                s = s.replace('\t', ' '*w)
                if s.startswith('\n'):
                    s2 = s[1 :]
                    self.result.append('\n'+s2[: -w])
                else:
                    self.result.append(s[: -w])
    #@+node:ekr.20110918225821.6819: *3* cpp.match
    def match(self, s, i, pat):
        return i < len(s) and s[i] == pat
    #@+node:ekr.20110917174948.6930: *3* cpp.tokenize & helper
    def tokenize(self, s):
        """Tokenize comments, strings, identifiers, whitespace and operators."""
        i, result = 0, []
        while i < len(s):
            # Loop invariant: at end: j > i and s[i:j] is the new token.
            j = i
            ch = s[i]
            if ch in '@\n':  # Make *sure* these are separate tokens.
                j += 1
            elif ch == '#':  # Preprocessor directive.
                j = g.skip_to_end_of_line(s, i)
            elif ch in ' \t':
                j = g.skip_ws(s, i)
            elif ch.isalpha() or ch == '_':
                j = g.skip_c_id(s, i)
            elif g.match(s, i, '//'):
                j = g.skip_line(s, i)
            elif g.match(s, i, '/*'):
                j = self.skip_block_comment(s, i)
            elif ch in "'\"":
                j = g.skip_string(s, i)
            else:
                j += 1
            assert j > i
            result.append(''.join(s[i : j]))
            i = j  # Advance.
        return result


    #@+at The following could be added to the 'else' clause::
    #     # Accumulate everything else.
    #     while (
    #         j < n and
    #         not s[j].isspace() and
    #         not s[j].isalpha() and
    #         not s[j] in '"\'_@' and
    #             # start of strings, identifiers, and single-character tokens.
    #         not g.match(s,j,'//') and
    #         not g.match(s,j,'/*') and
    #         not g.match(s,j,'-->')
    #     ):
    #         j += 1
    #@+node:ekr.20110917193725.6974: *4* cpp.skip_block_comment
    def skip_block_comment(self, s, i):
        assert g.match(s, i, "/*")
        j = s.find("*/", i)
        if j == -1:
            return len(s)
        return j + 2
    #@-others
#@+node:ekr.20150519111457.1: ** class PythonTokenBeautifier
class PythonTokenBeautifier:
    """A token-based Python beautifier."""

    #@+others
    #@+node:ekr.20150523132558.1: *3* class OutputToken
    class OutputToken:
        """A class representing Output Tokens"""

        def __init__(self, kind, value):
            self.kind = kind
            self.value = value

        def __repr__(self):
            val = len(self.value) if self.kind == 'line-indent' else repr(self.value)
            return f"{self.kind:15} {val}"

        def __str__(self):
            # More compact
            val = len(self.value) if self.kind == 'line-indent' else repr(self.value)
            return f"{self.kind} {val}"

        def to_string(self):
            """
            Convert an output token to a string.
            Note: repr shows the length of line-indent string.
            """
            return self.value if isinstance(self.value, str) else ''
    #@+node:ekr.20150527113020.1: *3* class ParseState
    class ParseState:
        """
        A class representing items in the parse state stack.
        
        The present states:
            
        'file-start': Ensures the stack stack is never empty.
            
        'decorator': The last '@' was a decorator.
            
            do_op():    push_state('decorator')
            do_name():  pops the stack if state.kind == 'decorator'.
                        
        'indent': The indentation level for 'class' and 'def' names.
        
            do_name():      push_state('indent', self.level)
            do_dendent():   pops the stack once or twice if state.value == self.level.

        """

        def __init__(self, kind, value):
            self.kind = kind
            self.value = value

        def __repr__(self):
            return f"State: {self.kind} {self.value!r}"

        __str__ = __repr__
    #@+node:ekr.20150519111713.1: *3* ptb.ctor
    #@@nobeautify

    def __init__(self, c):
        """Ctor for PythonPrettyPrinter class."""
        self.c = c
        #
        # Globals...
        self.code_list = []
            # The list of output tokens
        self.orange = False
            # Split or join lines only if orange is True.
        self.raw_val = None
            # Raw value for strings, comments.
        self.s = None
            # The string containing the line.
        self.val = None
            # The string containing the input token's value.
        #
        # State vars...
        self.backslash_seen = False
            # True if a backslash-newline appears at the end of a *string*
            # Comments retain proper spelling, so they never set this flag.
            # Note: run() calls self.backslash() when srow != last_line_number.
        self.decorator_seen = False
            # Set by do_name as a flag to do_op.
        self.in_arg_list = 0
            # > 0 if in an argument list of a function definition.
        self.level = 0
            # indentation level. Set only by do_indent and do_dedent.
            # do_name calls: push_state('indent', self.level)
        self.lws = ''
            # Leading whitespace.
            # Typically ' '*self.tab_width*self.level,
            # but may be changed for continued lines.
        self.state_stack = []
            # Stack of ParseState objects.
            # See the ParseState class for more details.
        #
        # Counts of unmatched brackets and parentheses.
        self.paren_level = 0
            # Number of unmatched '(' tokens.
        self.square_brackets_level = 0
            # Number of unmatched '[' tokens.
        self.curly_brackets_level = 0
            # Number of unmatched '{' tokens.
        #
        # Statistics...
        self.errors = 0
        self.n_changed_nodes = 0
        self.n_input_tokens = 0
        self.n_output_tokens = 0
        self.n_strings = 0
        self.parse_time = 0.0
        self.tokenize_time = 0.0
        self.beautify_time = 0.0
        self.check_time = 0.0
        self.total_time = 0.0
        #
        # Undo vars...
        self.changed = False
        self.dirtyVnodeList = []
        #
        # Complete the init.
        self.sanitizer = None  # For pylint.
        self.reloadSettings()

    def reloadSettings(self):
        c = self.c
        if c:
            # These should be on the same line,
            # so the check-settings script in leoSettings.leo will see them.
            keep_comments = c.config.getBool('beautify-keep-comment-indentation', default=True)
            self.delete_blank_lines = not c.config.getBool('beautify-keep-blank-lines', default=True)
            # Join.
            n = c.config.getInt('beautify-max-join-line-length')
            self.max_join_line_length = 88 if n is None else n
            # Split
            n = c.config.getInt('beautify-max-split-line-length')
            self.max_split_line_length = 88 if n is None else n
            # Join <= Split.
            if self.max_join_line_length > self.max_split_line_length:
                self.max_join_line_length = self.max_split_line_length
            self.tab_width = abs(c.tab_width)
        else:
            keep_comments = True
            self.delete_blank_lines = True
            self.max_join_line_length = 88
            self.max_split_line_length = 88
            self.tab_width = 4
        self.sanitizer = SyntaxSanitizer(c, keep_comments)
    #@+node:ekr.20190908154125.1: *3* ptb.Compare & dump AST's 
    #@+node:ekr.20190908032911.1: *4* ptb.compare_two_asts
    def compare_two_asts(self, node1, node2):
        """
        Compare both nodes, and recursively compare their children.
        
        See also: http://stackoverflow.com/questions/3312989/
        """
        # Compare the nodes themselves.
        self.compare_two_nodes(node1, node2)
        # Get the list of fields.
        fields1 = getattr(node1, "_fields", [])
        fields2 = getattr(node2, "_fields", [])
        if fields1 != fields2:
            raise AstNotEqual(f"node1._fields: {fields1}\n" f"node2._fields: {fields2}")
        # Recursively compare each field.
        for field in fields1:
            if field not in ('lineno', 'col_offset', 'ctx'):
                attr1 = getattr(node1, field, None)
                attr2 = getattr(node2, field, None)
                if attr1.__class__.__name__ != attr2.__class__.__name__:
                    raise AstNotEqual(f"attrs1: {attr1},\n" f"attrs2: {attr2}")
                self.compare_two_asts(attr1, attr2)
    #@+node:ekr.20190908034557.1: *4* ptb.compare_two_nodes
    def compare_two_nodes(self, node1, node2):
        """
        Compare node1 and node2.
        For lists and tuples, compare elements recursively.
        Raise AstNotEqual if not equal.
        """
        # Class names must always match.
        if node1.__class__.__name__ != node2.__class__.__name__:
            raise AstNotEqual(
                f"node1.__class__.__name__: {node1.__class__.__name__}\n"
                f"node2.__class__.__name__: {node2.__class__.__name_}"
            )
        # Special cases for strings and None
        if node1 is None:
            return
        if isinstance(node1, str):
            if node1 != node2:
                raise AstNotEqual(f"node1: {node1!r}\n" f"node2: {node2!r}")
        # Special cases for lists and tuples:
        if isinstance(node1, (tuple, list)):
            if len(node1) != len(node2):
                raise AstNotEqual(f"node1: {node1}\n" f"node2: {node2}")
            for i, item1 in enumerate(node1):
                item2 = node2[i]
                if item1.__class__.__name__ != item2.__class__.__name__:
                    raise AstNotEqual(
                        f"list item1: {i} {item1}\n" f"list item2: {i} {item2}"
                    )
                self.compare_two_asts(item1, item2)
    #@+node:ekr.20190908163223.1: *4* ptb.dump_ast
    def dump_ast(self, node, tag=None):
        """Dump the tree"""
        from leo.core.leoAst import AstDumper

        g.printObj(AstDumper().dump(node), tag=tag)
    #@+node:ekr.20150530072449.1: *3* ptb.Entries
    #@+node:ekr.20150528171137.1: *4* ptb.prettyPrintNode
    def prettyPrintNode(self, p):
        """
        The driver for beautification: beautify a single node.
        Return True if the node was actually changed.
        """
        if not should_beautify(p):
            # @nobeautify is in effect.
            return False
        if not p.b:
            # Pretty printing might add text!
            return False
        if not p.b.strip():
            # Do this *after* we are sure @beautify is in effect.
            self.replace_body(p, '')
            return False
        t1 = time.time()
        # Replace Leonine syntax with special comments.
        comment_string, s0 = self.sanitizer.comment_leo_lines(p=p)
        check_result = True
        try:
            s1 = g.toEncodedString(s0)
            node1 = ast.parse(s1, filename='before', mode='exec')
        except IndentationError:
            g.warning(f"IndentationError: can't check {p.h}")
            self.errors += 1
            if g.unitTesting:
                raise
            p.v.setMarked()
            return False
        except SyntaxError:
            g.warning(f"SyntaxError: can't check {p.h}")
            self.errors += 1
            if g.unitTesting:
                g.printObj(s1, tag='SANITIZED STRING')
                raise
            p.v.setMarked()
            return False
        except Exception:
            g.warning(f"Unexpected exception: {p.h}")
            g.es_exception()
            self.errors += 1
            if g.unitTesting:
                raise
            p.v.setMarked()
            return False
        t2 = time.time()
        #
        # Generate the tokens.
        readlines = g.ReadLinesClass(s0).next
        tokens = list(tokenize.generate_tokens(readlines))
        #
        # Beautify into s2.
        t3 = time.time()
        s2 = self.run(tokens)
        assert isinstance(s2, str), s2.__class__.__name__
        t4 = time.time()
        if check_result:
            #
            # Create the "after" parse tree.
            try:
                s2_e = g.toEncodedString(s2)
                node2 = ast.parse(s2_e, filename='after', mode='exec')
            except IndentationError:
                g.warning(f"{p.h}: Indentation error in the result")
                g.es_print(f"{p.h} will not be changed")
                g.printObj(s2, tag='RESULT')
                if g.unitTesting:
                    raise
                self.errors += 1
                p.v.setMarked()
                return False
            except SyntaxError:
                g.warning(f"{p.h}: Syntax error in the result")
                g.es_print(f"{p.h} will not be changed")
                g.printObj(s2, tag='RESULT')
                if g.unitTesting:
                    raise
                self.errors += 1
                p.v.setMarked()
                return False
            except Exception:
                g.warning(f"{p.h}: Unexpected exception creating the \"after\" parse tree")
                g.es_print(f"{p.h} will not be changed")
                g.es_exception()
                g.printObj(s2, tag='RESULT')
                if g.unitTesting:
                    raise
                self.errors += 1
                p.v.setMarked()
                return False
            #
            # Compare the two parse trees.
            try:
                self.compare_two_asts(node1, node2)
            except AstNotEqual:
                g.warning(f"{p.h}: The beautify command did not preserve meaning!")
                g.printObj(s2, tag='RESULT')
                # g.printObj(self.code_list, 'CODE LIST')
                # self.dump_ast(node1, tag='AST BEFORE')
                # self.dump_ast(node2, tag='AST AFTER')
                if g.unitTesting:
                    raise
                self.errors += 1
                p.v.setMarked()
                return False
            except Exception:
                g.warning(f"{p.h}: Unexpected exception")
                g.es_exception()
                g.printObj(s2, tag='RESULT')
                # self.dump_ast(node1, tag='AST BEFORE')
                # self.dump_ast(node2, tag='AST AFTER')
                self.errors += 1
                if g.unitTesting:
                    raise
                p.v.setMarked()
                return False
        if 'beauty' in g.app.debug:
            # g.printObj(g.toUnicode(s2_e), tag='RESULT')
            g.printObj(self.code_list, tag="Code List")
        t5 = time.time()
        # Restore the tags after the compare
        s3 = self.sanitizer.uncomment_leo_lines(comment_string, p, s2)
        changed = p.b != s3
        if changed:
            self.replace_body(p, s3)
        # Update the stats
        self.n_input_tokens += len(tokens)
        self.n_output_tokens += len(self.code_list)
        self.n_strings += len(s3)
        self.parse_time += t2 - t1
        self.tokenize_time += t3 - t2
        self.beautify_time += t4 - t3
        self.check_time += t5 - t4
        self.total_time += t5 - t1
        # self.print_stats()
        return changed
    #@+node:ekr.20150526194715.1: *4* ptb.run
    def run(self, tokens):
        """
        The main line of PythonTokenBeautifier class.
        Called by prettPrintNode & test_beautifier.
        """

        def oops():
            g.trace('unknown kind', self.kind)

        self.errors = 0
        self.code_list = []
        self.state_stack = []
        last_line_number = 0
        self.file_start()
        for token5tuple in tokens:
            t1, t2, t3, t4, t5 = token5tuple
            srow, scol = t3
            self.kind = token_module.tok_name[t1].lower()
            self.val = g.toUnicode(t2)
            self.raw_val = g.toUnicode(t5)
            if srow != last_line_number:
                # Handle a previous backslash.
                if self.backslash_seen:
                    self.backslash()
                # Start a new row.
                raw_val = self.raw_val.rstrip()
                self.backslash_seen = raw_val.endswith('\\')
                if (
                    self.curly_brackets_level > 0
                    or self.paren_level > 0
                    or self.square_brackets_level > 0
                ):
                    s = self.raw_val.rstrip()
                    n = g.computeLeadingWhitespaceWidth(s, self.tab_width)
                    # This n will be one-too-many if formatting has
                    # changed: foo (
                    # to:      foo(
                    self.line_indent(ws=' '*n)
                        # Do not set self.lws here!
                last_line_number = srow
            func = getattr(self, 'do_'+self.kind, oops)
            func()
        self.file_end()
        # g.printObj(self.code_list, tag='FINAL')
        return ''.join([z.to_string() for z in self.code_list])
    #@+node:ekr.20150526194736.1: *3* ptb.Input token Handlers
    #@+node:ekr.20150526203605.1: *4* ptb.do_comment (clears backslash_seen)
    def do_comment(self):
        """Handle a comment token."""
        raw_val = self.raw_val.rstrip()
        val = self.val.rstrip()
        entire_line = raw_val.lstrip().startswith('#')
        self.backslash_seen = False
            # Putting the comment will put the backslash.
        if entire_line:
            self.clean('line-indent')
            self.add_token('comment', raw_val)
        else:
            self.blank_before_end_line_comment()
            self.add_token('comment', val)
    #@+node:ekr.20041021102938: *4* ptb.do_endmarker
    def do_endmarker(self):
        """Handle an endmarker token."""
        pass
    #@+node:ekr.20041021102340.1: *4* ptb.do_errortoken
    def do_errortoken(self):
        """Handle an errortoken token."""
        # This code is executed for versions of Python earlier than 2.4
        if self.val == '@':
            self.op(self.val)
    #@+node:ekr.20041021102340.2: *4* ptb.do_indent & do_dedent
    def do_dedent(self):
        """Handle dedent token."""
        self.level -= 1
        self.lws = self.level * self.tab_width * ' '
        self.line_indent()
            # was self.line_start()
        state = self.state_stack[-1]
        if state.kind == 'indent' and state.value == self.level:
            self.state_stack.pop()
            state = self.state_stack[-1]
            if state.kind in ('class', 'def'):
                self.state_stack.pop()
                self.blank_lines(1)
                    # Most Leo nodes aren't at the top level of the file.
                    # self.blank_lines(2 if self.level == 0 else 1)

    def do_indent(self):
        """Handle indent token."""
        self.level += 1
        self.lws = self.val
        self.line_indent()
            # Was self.line_start()
    #@+node:ekr.20041021101911.5: *4* ptb.do_name
    def do_name(self):
        """Handle a name token."""
        name = self.val
        if name in ('class', 'def'):
            self.decorator_seen = False
            state = self.state_stack[-1]
            if state.kind == 'decorator':
                self.clean_blank_lines()
                self.line_end()
                self.state_stack.pop()
            else:
                self.blank_lines(1)
                # self.blank_lines(2 if self.level == 0 else 1)
            self.push_state(name)
            self.push_state('indent', self.level)
                # For trailing lines after inner classes/defs.
            self.word(name)
        elif name in ('and', 'in', 'not', 'not in', 'or', 'for'):
            self.word_op(name)
        else:
            self.word(name)
    #@+node:ekr.20041021101911.3: *4* ptb.do_newline
    def do_newline(self):
        """Handle a regular newline."""
        self.line_end()
    #@+node:ekr.20141009151322.17828: *4* ptb.do_nl
    def do_nl(self):
        """Handle a continuation line."""
        self.line_end()
    #@+node:ekr.20041021101911.6: *4* ptb.do_number
    def do_number(self):
        """Handle a number token."""
        assert isinstance(self.val, str), repr(self.val)
        self.add_token('number', self.val)
    #@+node:ekr.20040711135244.11: *4* ptb.do_op
    def do_op(self):
        """Handle an op token."""
        val = self.val
        if val == '.':
            self.op_no_blanks(val)
        elif val == '@':
            if not self.decorator_seen:
                self.blank_lines(1)
                self.decorator_seen = True
            self.op_no_blanks(val)
            self.push_state('decorator')
        elif val == ':':
            # Treat slices differently.
            self.colon(val)
        elif val in ',;':
            # Pep 8: Avoid extraneous whitespace immediately before
            # comma, semicolon, or colon.
            self.op_blank(val)
        elif val in '([{':
            # Pep 8: Avoid extraneous whitespace immediately inside
            # parentheses, brackets or braces.
            self.lt(val)
        elif val in ')]}':
            # Ditto.
            self.rt(val)
        elif val == '=':
            # Pep 8: Don't use spaces around the = sign when used to indicate
            # a keyword argument or a default parameter value.
            if self.paren_level:
                self.op_no_blanks(val)
            else:
                self.op(val)
        elif val in '~+-':
            self.possible_unary_op(val)
        elif val == '*':
            self.star_op()
        elif val == '**':
            self.star_star_op()
        else:
            # Pep 8: always surround binary operators with a single space.
            # '==','+=','-=','*=','**=','/=','//=','%=','!=','<=','>=','<','>',
            # '^','~','*','**','&','|','/','//',
            # Pep 8: If operators with different priorities are used,
            # consider adding whitespace around the operators with the lowest priority(ies).
            self.op(val)
    #@+node:ekr.20150526204248.1: *4* ptb.do_string (sets backslash_seen)
    def do_string(self):
        """Handle a 'string' token."""
        self.add_token('string', self.val)
        if self.val.find('\\\n'):
            self.backslash_seen = False
            # This *does* retain the string's spelling.
        self.blank()
    #@+node:ekr.20150526201902.1: *3* ptb.Output token generators
    #@+node:ekr.20150526195542.1: *4* ptb.add_token
    def add_token(self, kind, value=''):
        """
        Add a token to the code list.
        
        The blank-lines token is the only token whose value isn't a string.
        OutputToken.to_string() ignores such tokens.
        """
        if kind != 'blank-lines':
            assert isinstance(value, str), g.callers()
        tok = self.OutputToken(kind, value)
        self.code_list.append(tok)
    #@+node:ekr.20150601095528.1: *4* ptb.backslash
    def backslash(self):
        """
        Add a backslash token and clear .backslash_seen.
        
        Called in two places:
            
        - run()         if srow != last_line_number.
        - line_end()    if backslash_seen.
        """
        self.add_token('backslash', '\\')
        self.add_token('line-end', '\n')
        self.line_indent()
        self.backslash_seen = False
    #@+node:ekr.20150526201701.4: *4* ptb.blank
    def blank(self):
        """Add a blank request on the code list."""
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank',
            'blank-lines',
            'file-start',
            'line-end',
            'line-indent',
            'lt',
            'op-no-blanks',
            'unary-op',
        ):
            self.add_token('blank', ' ')
    #@+node:ekr.20190915083748.1: *4* ptb.blank_before_end_line_comment
    def blank_before_end_line_comment(self):
        """Add two blanks before an end-of-line comment."""
        prev = self.code_list[-1]
        self.clean('blank')
        if prev.kind not in ('blank-lines', 'file-start', 'line-end', 'line-indent'):
            self.add_token('blank', ' ')
            self.add_token('blank', ' ')
    #@+node:ekr.20150526201701.5: *4* ptb.blank_lines
    def blank_lines(self, n):
        """
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        """
        self.clean_blank_lines()
        kind = self.code_list[-1].kind
        if kind == 'file-start':
            self.add_token('blank-lines', n)
            return
        for i in range(0, n+1):
            self.add_token('line-end', '\n')
        # Retain the token (intention) for debugging.
        self.add_token('blank-lines', n)
        self.line_indent()
    #@+node:ekr.20150526201701.6: *4* ptb.clean
    def clean(self, kind):
        """Remove the last item of token list if it has the given kind."""
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20150527175750.1: *4* ptb.clean_blank_lines
    def clean_blank_lines(self):
        """Remove all vestiges of previous lines."""
        table = ('blank-lines', 'line-end', 'line-indent')
        while self.code_list[-1].kind in table:
            self.code_list.pop()
    #@+node:ekr.20190915120431.1: *4* ptb.colon
    def colon(self, val):
        """Handle a colon."""
        if self.square_brackets_level > 0:
            # Put blanks on either side of the colon,
            # but not between commas, and not next to [.
            self.clean('blank')
            prev = self.code_list[-1]
            if prev.value in '[:':
                self.add_token('op', val)
                self.blank()
            else:
                self.op(val)
        else:
            self.op_blank(val)
    #@+node:ekr.20150526201701.8: *4* ptb.file_start & file_end
    def file_end(self):
        """
        Add a file-end token to the code list.
        Retain exactly one line-end token.
        """
        self.clean_blank_lines()
        self.add_token('line-end', '\n')
        self.add_token('line-end', '\n')
        self.add_token('file-end')

    def file_start(self):
        """Add a file-start token to the code list and the state stack."""
        self.add_token('file-start')
        self.push_state('file-start')
    #@+node:ekr.20150530190758.1: *4* ptb.line_indent
    def line_indent(self, ws=None):
        """Add a line-indent token if indentation is non-empty."""
        self.clean('line-indent')
        ws = ws or self.lws
        if ws:
            self.add_token('line-indent', ws)
    #@+node:ekr.20150526201701.9: *4* ptb.line_end & split/join helpers
    def line_end(self):
        """Add a line-end request to the code list."""
        prev = self.code_list[-1]
        if prev.kind == 'file-start':
            return
        self.clean('blank')  # Important!
        if self.delete_blank_lines:
            self.clean_blank_lines()
        self.clean('line-indent')
        if self.backslash_seen:
            self.backslash()
        self.add_token('line-end', '\n')
        if self.orange:
            allow_join = True
            if self.max_split_line_length > 0:
                allow_join = not self.break_line()
            if allow_join and self.max_join_line_length > 0:
                self.join_lines()
        self.line_indent()
            # Add the indentation for all lines
            # until the next indent or unindent token.
    #@+node:ekr.20190908054807.1: *5* ptb.break_line (new) & helpers
    def break_line(self):
        """
        Break the preceding line, if necessary.
        
        Return True if the line was broken into two or more lines.
        """
        assert self.code_list[-1].kind == 'line-end', repr(self.code_list[-1])
            # Must be called just after inserting the line-end token.
        #
        # Find the tokens of the previous lines.
        line_tokens = self.find_prev_line()
        # g.printObj(line_tokens, tag='PREV LINE')
        line_s = ''.join([z.to_string() for z in line_tokens])
        if self.max_split_line_length == 0 or len(line_s) < self.max_split_line_length:
            return False
        #
        # Return if the previous line has no opening delim: (, [ or {.
        if not any([z.kind == 'lt' for z in line_tokens]):
            return False
        prefix = self.find_line_prefix(line_tokens)
        #
        # Calculate the tail before cleaning the prefix.
        tail = line_tokens[len(prefix) :]
        if prefix[0].kind == 'line-indent':
            prefix = prefix[1 :]
        # g.printObj(prefix, tag='PREFIX')
        # g.printObj(tail, tag='TAIL')
        #
        # Cut back the token list
        self.code_list = self.code_list[: len(self.code_list) - len(line_tokens) - 1]
            # -1 for the trailing line-end.
        # g.printObj(self.code_list, tag='CUT CODE LIST')
        #
        # Append the tail, splitting it further, as needed.
        self.append_tail(prefix, tail)
        #
        # Add the line-end token deleted by find_line_prefix.
        self.add_token('line-end', '\n')
        return True
    #@+node:ekr.20190908065154.1: *6* ptb.append_tail
    def append_tail(self, prefix, tail):
        """Append the tail tokens, splitting the line further as necessary."""
        tail_s = ''.join([z.to_string() for z in tail])
        if len(tail_s) < self.max_split_line_length:
            # Add the prefix.
            self.code_list.extend(prefix)
            # Start a new line and increase the indentation.
            self.add_token('line-end', '\n')
            self.add_token('line-indent', self.lws+' '*4)
            self.code_list.extend(tail)
            return
        #
        # Still too long.  Split the line at commas.
        self.code_list.extend(prefix)
        # Start a new line and increase the indentation.
        self.add_token('line-end', '\n')
        self.add_token('line-indent', self.lws+' '*4)
        open_delim = self.OutputToken(kind='lt', value=prefix[-1].value)
        close_delim = self.OutputToken(
            kind='rt',
            value=open_delim.value.replace('(', ')').replace('[', ']').replace('{', '}'),
        )
        delim_count = 1
        lws = self.lws + ' ' * 4
        for i, t in enumerate(tail):
            # g.trace(delim_count, str(t))
            if t.kind == 'op' and t.value == ',':
                if delim_count == 1:
                    # Start a new line.
                    self.add_token('op-no-blanks', ',')
                    self.add_token('line-end', '\n')
                    self.add_token('line-indent', lws)
                    # Kill a following blank.
                    if i + 1 < len(tail):
                        next_t = tail[i + 1]
                        if next_t.kind == 'blank':
                            next_t.kind = 'no-op'
                            next_t.value = ''
                else:
                    self.code_list.append(t)
            elif t.kind == close_delim.kind and t.value == close_delim.value:
                # Done if the delims match.
                delim_count -= 1
                if delim_count == 0:
                    if 0:
                        # Create an error, on purpose.
                        # This test passes: proper dumps are created,
                        # and the body is not updated.
                        self.add_token('line-end', '\n')
                        self.add_token('op', ',')
                        self.add_token('number', '666')
                    # Start a new line
                    self.add_token('op-no-blanks', ',')
                    self.add_token('line-end', '\n')
                    self.add_token('line-indent', self.lws)
                    self.code_list.extend(tail[i :])
                    return
                lws = lws[: -4]
                self.code_list.append(t)
            elif t.kind == open_delim.kind and t.value == open_delim.value:
                delim_count += 1
                lws = lws + ' ' * 4
                self.code_list.append(t)
            else:
                self.code_list.append(t)
        g.trace('BAD DELIMS', delim_count)
    #@+node:ekr.20190908050434.1: *6* ptb.find_prev_line (new)
    def find_prev_line(self):
        """Return the previous line, as a list of tokens."""
        line = []
        for t in reversed(self.code_list[: -1]):
            if t.kind == 'line-end':
                break
            line.append(t)
        return list(reversed(line))
    #@+node:ekr.20190908061659.1: *6* ptb.find_line_prefix (new)
    def find_line_prefix(self, token_list):
        """
        Return all tokens up to and including the first lt token.
        Also add all lt tokens directly following the first lt token.
        """
        result = []
        for i, t in enumerate(token_list):
            result.append(t)
            if t.kind == 'lt':
                for t in token_list[i + 1 :]:
                    if t.kind == 'blank' or self.is_any_lt(t):
                    # if t.kind in ('lt', 'blank'):
                        result.append(t)
                    else:
                        break
                break
        return result
    #@+node:ekr.20190908072548.1: *6* ptb.is_any_lt
    def is_any_lt(self, output_token):
        """Return True if the given token is any lt token"""
        return (
            output_token == 'lt'
            or output_token.kind == 'op-no-blanks'
            and output_token.value in "{[("
        )
    #@+node:ekr.20190909020458.1: *5* ptb.join_lines (new) & helpers
    def join_lines(self):
        """
        Join preceding lines, if the result would be short enough.
        Should be called only at the end of a line.
        """
        # Must be called just after inserting the line-end token.
        trace = False and not g.unitTesting
        assert self.code_list[-1].kind == 'line-end', repr(self.code_list[-1])
        line_tokens = self.find_prev_line()
        line_s = ''.join([z.to_string() for z in line_tokens])
        if trace:
            g.trace(line_s)
        # Don't bother trying if the line is already long.
        if self.max_join_line_length == 0 or len(line_s) > self.max_join_line_length:
            return
        # Terminating long lines must have ), ] or }
        if not any([z.kind == 'rt' for z in line_tokens]):
            return
        # To do...
        #   Scan back, looking for the first line with all balanced delims.
        #   Do nothing if it is this line.
    #@+node:ekr.20150526201701.11: *4* ptb.lt & rt
    #@+node:ekr.20190915070456.1: *5* ptb.lt
    def lt(self, s):
        """Generate code for a left paren or curly/square bracket."""
        assert s in '([{', repr(s)
        if s == '(':
            self.paren_level += 1
        elif s == '[':
            self.square_brackets_level += 1
        else:
            self.curly_brackets_level += 1
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind in ('op', 'word-op'):
            self.blank()
            self.add_token('lt', s)
        elif prev.kind == 'word':
            # Only suppress blanks before '(' or '[' for non-keyworks.
            if s == '{' or prev.value in ('if', 'else', 'return', 'for'):
                self.blank()
            elif s == '(':
                self.in_arg_list += 1
            self.add_token('lt', s)
        elif prev.kind == 'op':
            self.op(s)
        else:
            self.op_no_blanks(s)
    #@+node:ekr.20190915070502.1: *5* ptb.rt
    def rt(self, s):
        """Generate code for a right paren or curly/square bracket."""
        assert s in ')]}', repr(s)
        if s == ')':
            self.paren_level -= 1
            self.in_arg_list = max(0, self.in_arg_list-1)
        elif s == ']':
            self.square_brackets_level -= 1
        else:
            self.curly_brackets_level -= 1
        prev = self.code_list[-1]
        if prev.kind == 'arg-end':
            # Remove a blank token preceding the arg-end token.
            prev = self.code_list.pop()
            self.clean('blank')
            self.code_list.append(prev)
        else:
            self.clean('blank')
        self.add_token('rt', s)
    #@+node:ekr.20150526201701.12: *4* ptb.op*
    def op(self, s):
        """Add op token to code list."""
        assert s and isinstance(s, str), repr(s)
        if self.in_arg_list > 0 and (s in '+-/*' or s == '//'):
            # Treat arithmetic ops differently.
            self.clean('blank')
            self.add_token('op', s)
        else:
            self.blank()
            self.add_token('op', s)
            self.blank()

    def op_blank(self, s):
        """Remove a preceding blank token, then add op and blank tokens."""
        assert s and isinstance(s, str), repr(s)
        self.clean('blank')
        if self.in_arg_list > 0 and s in ('+-/*' or s == '//'):
            self.add_token('op', s)
        else:
            self.add_token('op', s)
            self.blank()

    def op_no_blanks(self, s):
        """Add an operator *not* surrounded by blanks."""
        self.clean('blank')
        self.add_token('op-no-blanks', s)
    #@+node:ekr.20150527213419.1: *4* ptb.possible_unary_op & unary_op
    def possible_unary_op(self, s):
        """Add a unary or binary op to the token list."""
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind in ('lt', 'op', 'op-no-blanks', 'word-op'):
            self.unary_op(s)
        elif prev.kind == 'word' and prev.value in (
            'elif',
            'else',
            'if',
            'return',
            'while',
        ):
            self.unary_op(s)
        else:
            self.op(s)

    def unary_op(self, s):
        """Add an operator request to the code list."""
        assert s and isinstance(s, str), repr(s)
        self.blank()
        self.add_token('unary-op', s)
    #@+node:ekr.20150531051827.1: *4* ptb.star_op (no change)
    def star_op(self):
        """Put a '*' op, with special cases for *args."""
        val = '*'
        if self.paren_level > 0:
            i = len(self.code_list) - 1
            if self.code_list[i].kind == 'blank':
                i -= 1
            token = self.code_list[i]
            if token.kind == 'lt':
                self.op_no_blanks(val)
            elif token.value == ',':
                self.blank()
                self.add_token('op-no-blanks', val)
            else:
                self.op(val)
        else:
            self.op(val)
    #@+node:ekr.20150531053417.1: *4* ptb.star_star_op (no changed)
    def star_star_op(self):
        """Put a ** operator, with a special case for **kwargs."""
        val = '**'
        if self.paren_level > 0:
            i = len(self.code_list) - 1
            if self.code_list[i].kind == 'blank':
                i -= 1
            token = self.code_list[i]
            if token.value == ',':
                self.blank()
                self.add_token('op-no-blanks', val)
            else:
                self.op(val)
        else:
            self.op(val)
    #@+node:ekr.20150526201701.13: *4* ptb.word & word_op
    def word(self, s):
        """Add a word request to the code list."""
        assert s and isinstance(s, str), repr(s)
        if self.in_arg_list > 0:
            pass
        else:
            self.blank()
        self.add_token('word', s)
        self.blank()

    def word_op(self, s):
        """Add a word-op request to the code list."""
        assert s and isinstance(s, str), repr(s)
        self.blank()
        self.add_token('word-op', s)
        self.blank()
    #@+node:ekr.20150530064617.1: *3* ptb.Utils
    #@+node:ekr.20150528171420.1: *4* ptb.replace_body
    def replace_body(self, p, s):
        """Replace the body with the pretty version."""
        c, u = self.c, self.c.undoer
        undoType = 'Pretty Print'
        if p.b == s:
            return
        self.n_changed_nodes += 1
        if not self.changed:
            # Start the group.
            u.beforeChangeGroup(p, undoType)
            self.changed = True
            self.dirtyVnodeList = []
        undoData = u.beforeChangeNodeContents(p)
        c.setBodyString(p, s)
        dirtyVnodeList2 = p.setDirty()
        self.dirtyVnodeList.extend(dirtyVnodeList2)
        u.afterChangeNodeContents(p, undoType, undoData, dirtyVnodeList=self.dirtyVnodeList)
    #@+node:ekr.20150528180738.1: *4* ptb.end_undo
    def end_undo(self):
        """Complete undo processing."""
        c = self.c
        u = c.undoer
        undoType = 'Pretty Print'
        current = c.p
        if self.changed:
            # Tag the end of the command.
            u.afterChangeGroup(current, undoType, dirtyVnodeList=self.dirtyVnodeList)
    #@+node:ekr.20190909072007.1: *4* ptb.find_delims (new)
    def find_delims(self, tokens):
        """
        Compute the net number of each kind of delim in the given range of tokens.
        
        Return (curlies, parens, squares)
        """
        parens, curlies, squares = 0, 0, 0
        for token in tokens:
            value = token.value
            if token.kind == 'lt':
                assert value in '([{', f"Bad lt value: {token.kind} {value}"
                if value == '{':
                    curlies += 1
                elif value == '(':
                    parens += 1
                elif value == '[':
                    squares += 1
            elif token.kind == 'rt':
                assert value in ')]}', f"Bad rt value: {token.kind} {value}"
                if value == ')':
                    parens -= 1
                elif value == ']':
                    squares -= 1
                elif value == '}':
                    curlies += 1
        return curlies, parens, squares
    #@+node:ekr.20150528172940.1: *4* ptb.print_stats
    def print_stats(self):
        print(
            f"{'='*10} stats\n\n"
            f"changed nodes  {self.n_changed_nodes:4}\n"
            f"tokens         {self.n_input_tokens:4}\n"
            f"len(code_list) {self.n_output_tokens:4}\n"
            f"len(s)         {self.n_strings:4}\n"
            f"\ntimes (seconds)...\n"
            f"parse          {self.parse_time:4.2f}\n"
            f"tokenize       {self.tokenize_time:4.2f}\n"
            f"format         {self.beautify_time:4.2f}\n"
            f"check          {self.check_time:4.2f}\n"
            f"total          {self.total_time:4.2f}"
        )
    #@+node:ekr.20150528084644.1: *4* ptb.push_state
    def push_state(self, kind, value=None):
        """Append a state to the state stack."""
        state = self.ParseState(kind, value)
        self.state_stack.append(state)
    #@-others
#@+node:ekr.20190910081550.1: ** class SyntaxSanitizer
class SyntaxSanitizer:

    #@+<< SyntaxSanitizer docstring >>
    #@+node:ekr.20190910093739.1: *3* << SyntaxSanitizer docstring >>
    r"""
    This class converts section references, @others and Leo directives to
    comments. This allows ast.parse to handle the result.

    Within section references, these comments must *usually* be executable:
        
    BEFORE:
        if condition:
            <\< do something >\>
    AFTER:
        if condition:
            pass # do something
            
    Alas, sanitation can result in a syntax error. For example, leoTips.py contains:
        
    BEFORE:
        tips = [
            <\< define tips >\>
            ]

    AFTER:
        tips = [
            pass # define tips
        ]
        
    This fails because tips = [pass] is a SyntaxError.

    The beautify* and black* commands clearly report such failures.
    """
    #@-<< SyntaxSanitizer docstring >>

    def __init__(self, c, keep_comments):
        self.c = c
        self.keep_comments = keep_comments

    #@+others
    #@+node:ekr.20190910022637.2: *3* sanitize.comment_leo_lines
    def comment_leo_lines(self, p=None, s0=None):
        """
        Replace lines containing Leonine syntax with **special comment lines** of the form:
            
            {lws}#{marker}{line}
            
        where: 
        - lws is the leading whitespace of the original line
        - marker appears nowhere in p.b
        - line is the original line, unchanged.
        
        This convention allows uncomment_special_lines to restore these lines.
        """
        # Choose a marker that appears nowhere in s.
        if p:
            s0 = p.b
        n = 5
        while('#'+ ('!'*n)) in s0:
            n += 1
        comment = '#' + ('!' * n)
        # Create a dict of directives.
        d = {z: True for z in g.globalDirectiveList}
        # Convert all Leonine lines to special comments.
        i, lines, result = 0, g.splitLines(s0), []
        while i < len(lines):
            progress = i
            s = lines[i]
            s_lstrip = s.lstrip()
            # Comment out any containing a section reference.
            j = s.find('<<')
            k = s.find('>>') if j > -1 else -1
            if -1 < j < k:
                result.append(comment+s)
                # Generate a properly-indented pass line.
                j2 = g.skip_ws(s, 0)
                result.append('%spass\n' % (' '*j2))
            elif s_lstrip.startswith('@'):
                # Comment out all other Leonine constructs.
                if self.starts_doc_part(s):
                    # Comment the entire doc part, until @c or @code.
                    result.append(comment+s)
                    i += 1
                    while i < len(lines):
                        s = lines[i]
                        result.append(comment+s)
                        i += 1
                        if self.ends_doc_part(s):
                            break
                else:
                    j = g.skip_ws(s, 0)
                    assert s[j] == '@'
                    j += 1
                    k = g.skip_id(s, j, chars='-')
                    if k > j:
                        word = s[j : k]
                        if word == 'others':
                            # Remember the original @others line.
                            result.append(comment+s)
                            # Generate a properly-indented pass line.
                            result.append('%spass\n' % (' '* (j-1)))
                        else:
                            # Comment only Leo directives, not decorators.
                            result.append(comment+s if word in d else s)
                    else:
                        result.append(s)
            elif s_lstrip.startswith('#') and self.keep_comments:
                # A leading comment.
                result.append(comment+s)
            else:
                # A plain line.
                result.append(s)
            if i == progress:
                i += 1
        return comment, ''.join(result)
    #@+node:ekr.20190910022637.3: *3* sanitize.starts_doc_part & ends_doc_part
    def starts_doc_part(self, s):
        """Return True if s word matches @ or @doc."""
        return s.startswith(('@\n', '@doc\n', '@ ', '@doc '))

    def ends_doc_part(self, s):
        """Return True if s word matches @c or @code."""
        return s.startswith(('@c\n', '@code\n', '@c ', '@code '))
    #@+node:ekr.20190910022637.4: *3* sanitize.uncomment_leo_lines
    def uncomment_leo_lines(self, comment, p, s0):
        """Reverse the effect of comment_leo_lines."""
        lines = g.splitLines(s0)
        i, result = 0, []
        while i < len(lines):
            progress = i
            s = lines[i]
            i += 1
            if comment in s:
                # One or more special lines.
                i = self.uncomment_special_lines(comment, i, lines, p, result, s)
            else:
                # A regular line.
                result.append(s)
            assert progress < i
        return ''.join(result).rstrip() + '\n'
    #@+node:ekr.20190910022637.5: *3* sanitize.uncomment_special_line & helpers
    def uncomment_special_lines(self, comment, i, lines, p, result, s):
        """
        This method restores original lines from the special comment lines
        created by comment_leo_lines. These lines have the form:
            
            {lws}#{marker}{line}
            
        where: 
        - lws is the leading whitespace of the original line
        - marker appears nowhere in p.b
        - line is the original line, unchanged.
        
        s is a line containing the comment delim.
        i points at the *next* line.
        Handle one or more lines, appending stripped lines to result.
        """
        #
        # Delete the lws before the comment.
        # This works because the tail contains the original whitespace.
        assert comment in s
        s = s.lstrip().replace(comment, '')
        #
        # Here, s is the original line.
        if comment in s:
            g.trace(f"can not happen: {s!r}")
            return i
        if self.starts_doc_part(s):
            result.append(s)
            while i < len(lines):
                s = lines[i].lstrip().replace(comment, '')
                i += 1
                result.append(s)
                if self.ends_doc_part(s):
                    break
            return i
        j = s.find('<<')
        k = s.find('>>') if j > -1 else -1
        if -1 < j < k or '@others' in s:
            #
            # A section reference line or an @others line.
            # Such lines are followed by a pass line.
            #
            # The beautifier may insert blank lines before the pass line.
            kind = 'section ref' if -1 < j < k else '@others'
            # Restore the original line, including leading whitespace.
            result.append(s)
            # Skip blank lines.
            while i < len(lines) and not lines[i].strip():
                i += 1
            # Skip the pass line.
            if i < len(lines) and lines[i].lstrip().startswith('pass'):
                i += 1
            else:
                g.trace(f"*** no pass after {kind}: {p.h}")
        else:
            # A directive line or a comment line.
            result.append(s)
        return i
    #@-others
#@-others
if __name__ == "__main__":
    main()
#@@language python
#@@tabwidth -4
#@-leo
