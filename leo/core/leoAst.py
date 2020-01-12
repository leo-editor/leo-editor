# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20141012064706.18389: * @file leoAst.py
#@@first
"""
AST (Abstract Syntax Tree) related classes.
"""
#@+<< imports >>
#@+node:ekr.20200105054219.1: ** << imports >>
import ast
import codecs
import difflib
import io
import os
import re
import sys
import time
import tokenize
import traceback
import unittest
#@-<< imports >>
#@+others
#@+node:ekr.20191226175251.1: **  class LeoGlobals
#@@nosearch

class LeoGlobals: # pragma: no cover
    """
    Simplified version of functions in leoGlobals.py.
    """

    #@+others
    #@+node:ekr.20191227114503.1: *3* LeoGlobals.adjustTripleString
    def adjustTripleString(self, s):
        """Remove leading indentation from a triple-quoted string."""
        lines = g.splitLines(s)
        for line in lines:
            if line.strip():
                n = len(line)-len(line.lstrip())
                lws = line[:n]
                break
        if not lws:
            return s
        return ''.join(
            (z[n:] if z.startswith(lws) else z) for z in lines)
    #@+node:ekr.20191226175903.1: *3* LeoGlobals.callerName
    def callerName(self, n):
        """Get the function name from the call stack."""
        try:
            f1 = sys._getframe(n)
            code1 = f1.f_code
            return code1.co_name
        except Exception:
            return ''
    #@+node:ekr.20191226175426.1: *3* LeoGlobals.callers
    def callers(self, n=4):
        """
        Return a string containing a comma-separated list of the callers
        of the function that called g.callerList.
        """
        i, result = 2, []
        while True:
            s = self.callerName(n=i)
            if s:
                result.append(s)
            if not s or len(result) >= n:
                break
            i += 1
        return ','.join(reversed(result))
    #@+node:ekr.20191226190709.1: *3* leoGlobals.es_exception & helper
    def es_exception(self):
        typ, val, tb = sys.exc_info()
        for line in traceback.format_exception(typ, val, tb):
            print(line)
        fileName, n = self.getLastTracebackFileAndLineNumber()
        return fileName, n
    #@+node:ekr.20191226192030.1: *4* LeoGlobals.getLastTracebackFileAndLineNumber
    def getLastTracebackFileAndLineNumber(self):
        typ, val, tb = sys.exc_info()
        if typ == SyntaxError:
            # IndentationError is a subclass of SyntaxError.
            return val.filename, val.lineno
        #
        # Data is a list of tuples, one per stack entry.
        # The tuples have the form (filename, lineNumber, functionName, text).
        data = traceback.extract_tb(tb)
        item = data[-1]  # Get the item at the top of the stack.
        filename, n, functionName, text = item
        return filename, n
    #@+node:ekr.20191231153754.1: *3* LeoGlobals.pdb
    def pdb(self):
        """Fall into pdb."""
        import pdb
        try:
            import PyQt5.QtCore as QtCore
            QtCore.pyqtRemoveInputHook()
        except Exception:
            print('can not import PyQt5.QtCore')
            return
        pdb.set_trace()
    #@+node:ekr.20191226190425.1: *3* LeoGlobals.plural
    def plural(self, obj):
        """Return "s" or "" depending on n."""
        if isinstance(obj, (list, tuple, str)):
            n = len(obj)
        else:
            n = obj
        return '' if n == 1 else 's'
    #@+node:ekr.20191226175441.1: *3* LeoGlobals.printObj
    def printObj(self, obj, indent='', tag=None):
        """Simplified version of g.printObj."""
        if tag:
            print(f"{tag}...")
        if isinstance(obj, str):
            obj = g.splitLines(obj)
        if isinstance(obj, list):
            print('[')
            for z in obj:
                print(f"  {z!r}")
            print(']')
        elif isinstance(obj, tuple):
            print('(')
            for z in obj:
                print(f"  {z!r}")
            print(')')
        else:
            print(repr(obj))
        print('')
    #@+node:ekr.20191226190131.1: *3* LeoGlobals.splitLines
    def splitLines(self, s):
        """Split s into lines, preserving the number of lines and
        the endings of all lines, including the last line."""
        # g.stat()
        if s:
            return s.splitlines(True)
                # This is a Python string function!
        return []
    #@+node:ekr.20191226190844.1: *3* LeoGlobals.toEncodedString
    def toEncodedString(self, s, encoding='utf-8'):
        """Convert unicode string to an encoded string."""
        if not isinstance(s, str):
            return s
        try:
            s = s.encode(encoding, "strict")
        except UnicodeError:
            s = s.encode(encoding, "replace")
            print(f"toEncodedString: Error converting {s!r} to {encoding}")
        return s
    #@+node:ekr.20191226190006.1: *3* LeoGlobals.toUnicode
    def toUnicode(self, s, encoding='utf-8'):
        """Convert bytes to unicode if necessary."""
        if isinstance(s, str):
            return s
        tag = 'g.toUnicode'
        try:
            s = s.decode(encoding, 'strict')
        except(UnicodeDecodeError, UnicodeError):
            s = s.decode(encoding, 'replace')
            print(f"{tag}: unicode error. encoding: {encoding!r}, s:\n{s!r}")
            g.trace(g.callers())
        except Exception:
            g.es_exception()
            print(f"{tag}: unexpected error! encoding: {encoding!r}, s:\n{s!r}")
            g.trace(g.callers())
        return s
    #@+node:ekr.20191226175436.1: *3* LeoGlobals.trace
    def trace(self, *args):
        """Print a tracing message."""
        # Compute the caller name.
        try:
            f1 = sys._getframe(1)
            code1 = f1.f_code
            name = code1.co_name
        except Exception:
            name = ''
        print(f"{name}: {' '.join(str(z) for z in args)}")
    #@+node:ekr.20191226190241.1: *3* LeoGlobals.truncate
    def truncate(self, s, n):
        """Return s truncated to n characters."""
        if len(s) <= n:
            return s
        s2 = s[: n - 3] + f'...({len(s)})'
        return s2 + '\n' if s.endswith('\n') else s2
    #@-others
#@+node:ekr.20160521104628.1: **  leoAst.py: top-level
if 1: # pragma: no cover
    #@+others
    #@+node:ekr.20200101030236.1: *3* function: tokens_to_string
    def tokens_to_string(tokens):
        """Return the string represented by the list of tokens."""
        if tokens is None:
            # This indicates an internal error.
            print('')
            g.trace('===== token list is None ===== ')
            print('')
            return ''
        return ''.join([z.to_string() for z in tokens])
    #@+node:ekr.20200107114409.1: *3* functions: reading & writing files
    #@+node:ekr.20200106171502.1: *4* function: get_encoding_directive
    encoding_pattern = re.compile(r'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)')
        # This is the pattern in PEP 263.

    def get_encoding_directive(bb):
        """
        Get the encoding from the encoding directive at the start of a file.
        
        bb: The bytes of the file. 
        
        Returns the codec name, or 'UTF-8'.
        
        Adapted from pyzo. Copyright 2008 to 2020 by Almar Klein.
        """
        for line in bb.split(b'\n', 2)[:2]:
            # Try to make line a string
            try:
                line = line.decode('ASCII').strip()
            except Exception:
                continue
            # Does the line match the PEP 263 pattern?
            m = encoding_pattern.match(line)
            if not m:
                continue
            # Is it a known encoding? Correct the name if it is.
            try:
                c = codecs.lookup(m.group(1))
                return c.name
            except Exception:
                pass
        return 'UTF-8'
    #@+node:ekr.20200103113417.1: *4* function: read_file
    def read_file(filename):
        """
        Return the contents of the given file.
        Print an error message and return None on error.
        """
        tag = 'read_file'
        try:
            with open(filename, 'rb') as f:
                s = f.read()
            return g.toUnicode(s)
        except Exception:
            print(f"{tag}: can not read {filename}")
            return None
    #@+node:ekr.20200106173430.1: *4* function: read_file_with_encoding
    def read_file_with_encoding(filename):
        """
        Read the file, returning (e, s).

        s is the string, converted to unicode, or None if there was an error.
        
        e is the encoding of s, computed in the following order:

        - The BOM encoding if the file starts with a BOM mark.
        - The encoding given in the # -*- coding: utf-8 -*- line.
        - The encoding given by the 'encoding' keyword arg.
        - 'utf-8'.
        """
        # First, read the file.
        tag = 'read_with_encoding'
        try:
            with open(filename, 'rb') as f:
                bb = f.read()
        except Exception:
            print(f"{tag}: can not read {filename}")
        if not bb:
            return 'UTF-8', ''
        # Look for the BOM.
        e, bb = strip_BOM(bb)
        if not e:
            # Python's encoding comments override everything else. 
            e = get_encoding_directive(bb)
        return e, g.toUnicode(bb, encoding=e)
    #@+node:ekr.20200106174158.1: *4* function: strip_BOM
    def strip_BOM(bb):
        """
        bb must be the bytes contents of a file.
        
        If bb starts with a BOM (Byte Order Mark), return (e, bb2), where:
        
        - e is the encoding implied by the BOM.
        - bb2 is bb, stripped of the BOM.
        
        If there is no BOM, return (None, bb)
        """
        assert isinstance(bb, bytes), bb.__class__.__name__
        table = (
            # Test longer bom's first.
            (4, 'utf-32', codecs.BOM_UTF32_BE),
            (4, 'utf-32', codecs.BOM_UTF32_LE),
            (3, 'utf-8', codecs.BOM_UTF8),
            (2, 'utf-16', codecs.BOM_UTF16_BE),
            (2, 'utf-16', codecs.BOM_UTF16_LE),
        )
        for n, e, bom in table:
            assert len(bom) == n
            if bom == bb[: len(bom)]:
                return e, bb[len(bom):]
        return None, bb
    #@+node:ekr.20200103163100.1: *4* function: write_file
    def write_file(filename, s, encoding='utf-8'):
        """Write the string s to the file whose name is given."""
        try:
            # newline='' suppresses newline munging.
            with open(filename, 'w', encoding=encoding, newline='') as f:
                f.write(s)
        except Exception as e:
            g.trace(f"Error writing {filename}\n{e}")
    #@+node:ekr.20200107114620.1: *3* functions: unit testing
    #@+node:ekr.20191027072126.1: *4* function: compare_asts & helpers
    def compare_asts(ast1, ast2):
        """Compare two ast trees. Return True if they are equal."""
        # Compare the two parse trees.
        try:
            _compare_asts(ast1, ast2)
        except AstNotEqual:
            dump_ast(ast1, tag='AST BEFORE')
            dump_ast(ast2, tag='AST AFTER')
            return False
        except Exception:
            g.trace(f"Unexpected exception")
            g.es_exception()
            return False
        return True
    #@+node:ekr.20191027071653.2: *5* function._compare_asts
    def _compare_asts(node1, node2):
        """
        Compare both nodes, and recursively compare their children.
        
        See also: http://stackoverflow.com/questions/3312989/
        """
        # Compare the nodes themselves.
        _compare_nodes(node1, node2)
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
                _compare_asts(attr1, attr2)
    #@+node:ekr.20191027071653.3: *5* function._compare_nodes
    def _compare_nodes(node1, node2):
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
                _compare_asts(item1, item2)
    #@+node:ekr.20191121081439.1: *4* function: compare_lists
    def compare_lists(list1, list2):
        """
        Compare two lists of strings, showing the first mismatch.

        Return the index of the first mismatched lines, or None if identical.
        """
        import itertools
        it = itertools.zip_longest(list1, list2, fillvalue='Missing!')
        for i, (s1, s2) in enumerate(it):
            if s1 != s2:
                return i
        return None
    #@+node:ekr.20200106094631.1: *4* function: expected_got
    def expected_got(expected, got):
        """Return a message, mostly for unit tests."""
        return (
            f"\n"
            f"expected: {expected!s}\n"
            f"     got: {got!s}"
        )
    #@+node:ekr.20191231072039.1: *3* functions: utils...
    # General utility functions on tokens and nodes.
    #@+node:ekr.20191226071135.1: *4* function: get_time
    def get_time():
        return time.process_time()
    #@+node:ekr.20191124123830.1: *4* function: is_significant & is_significant_token
    def is_significant(kind, value):
        """
        Return True if (kind, value) represent a token that can be used for
        syncing generated tokens with the token list.
        """
        # Making 'endmarker' significant ensures that all tokens are synced.
        return (
            kind in ('async', 'await', 'endmarker', 'name', 'number', 'string') or
            kind == 'op' and value not in ',;()')

    def is_significant_token(token):
        """Return True if the given token is a syncronizing token"""
        return is_significant(token.kind, token.value)
    #@+node:ekr.20191119085222.1: *4* function: obj_id
    def obj_id(obj):
        """Return the last four digits of id(obj), for dumps & traces."""
        return str(id(obj))[-4:]
    #@+node:ekr.20191231060700.1: *4* function: op_name
    #@@nobeautify

    # https://docs.python.org/3/library/ast.html

    _op_names = {
        # Binary operators.
        'Add':       '+',
        'BitAnd':    '&',
        'BitOr':     '|',
        'BitXor':    '^',
        'Div':       '/',
        'FloorDiv':  '//',
        'LShift':    '<<',
        'MatMult':   '@', # Python 3.5.
        'Mod':       '%',
        'Mult':      '*',
        'Pow':       '**',
        'RShift':    '>>',
        'Sub':       '-',
        # Boolean operators.
        'And':   ' and ',
        'Or':    ' or ',
        # Comparison operators
        'Eq':    '==',
        'Gt':    '>',
        'GtE':   '>=',
        'In':    ' in ',
        'Is':    ' is ',
        'IsNot': ' is not ',
        'Lt':    '<',
        'LtE':   '<=',
        'NotEq': '!=',
        'NotIn': ' not in ',
        # Context operators.
        'AugLoad':  '<AugLoad>',
        'AugStore': '<AugStore>',
        'Del':      '<Del>',
        'Load':     '<Load>',
        'Param':    '<Param>',
        'Store':    '<Store>',
        # Unary operators.
        'Invert':   '~',
        'Not':      ' not ',
        'UAdd':     '+',
        'USub':     '-',
    }

    def op_name(node):
        """Return the print name of an operator node."""
        class_name = node.__class__.__name__
        assert class_name in _op_names, repr(class_name)
        return _op_names [class_name].strip()
    #@+node:ekr.20200107114452.1: *3* node/token creators...
    #@+node:ekr.20200103082049.1: *4* function: make_tokens
    def make_tokens(contents):
        """
        Return a list (not a generator) of Token objects corresponding to the
        list of 5-tuples generated by tokenize.tokenize.
        """
        
        def check(contents, tokens):
            result = tokens_to_string(tokens)
            ok = result == contents
            if not ok:
                print('\nRound-trip check FAILS')
                print('Contents...\n')
                g.printObj(contents)
                print('\nResult...\n')
                g.printObj(result)
            return ok
        try:
            five_tuples = tokenize.tokenize(io.BytesIO(contents.encode('utf-8')).readline)
        except Exception:
            print('make_tokens: exception in tokenize.tokenize')
            g.es_exception()
            return None
        tokens = Tokenizer().create_input_tokens(contents, five_tuples)
        assert check(contents, tokens)
        return tokens
    #@+node:ekr.20191027075648.1: *4* function: parse_ast
    def parse_ast(s):
        """
        Parse string s, catching & reporting all exceptions.
        Return the ast node, or None.
        """

        def oops(message):
            print('')
            print(f"parse_ast: {message}")
            g.printObj(s)
            print('')

        try:
            s1 = g.toEncodedString(s)
            tree = ast.parse(s1, filename='before', mode='exec')
            return tree
        except IndentationError:
            oops('Indentation Error')
        except SyntaxError:
            oops('Syntax Error')
        except Exception:
            oops('Unexpected Exception')
            g.es_exception()
        return None
    #@+node:ekr.20191231110051.1: *3* node/token dumpers...
    #@+node:ekr.20191027074436.1: *4* function: dump_ast
    def dump_ast(ast, tag='dump_ast'):
        """Utility to dump an ast tree."""
        g.printObj(AstDumper().dump_ast(ast), tag=tag)
    #@+node:ekr.20191228095945.4: *4* function: dump_contents
    def dump_contents(contents, tag='Contents'):
        print('')
        print(f"{tag}...\n")
        for i, z in enumerate(g.splitLines(contents)):
            print(f"{i+1:<3} ", z.rstrip())
        print('')
    #@+node:ekr.20191228095945.5: *4* function: dump_lines
    def dump_lines(tokens):
        print('')
        print('Token lines...\n')
        for z in tokens:
            if z.line.strip():
                print(z.line.rstrip())
            else:
                print(repr(z.line))
        print('')
    #@+node:ekr.20191228095945.7: *4* function: dump_results
    def dump_results(tokens):
        print('')
        print('Results...\n')
        print(tokens_to_string(tokens))
        print('')
    #@+node:ekr.20191228095945.8: *4* function: dump_tokens
    def dump_tokens(tokens):
        print('')
        print('Tokens...\n')
        print("Note: values shown are repr(value) *except* for 'string' tokens.\n")
        for z in tokens:
            print(z.dump())
        print('')
    #@+node:ekr.20191228095945.9: *4* function: dump_tree
    def dump_tree(tree):
        print('')
        print('Tree...\n')
        print(AstDumper().dump_tree(tree))
    #@+node:ekr.20200107040729.1: *4* function: show_diffs
    def show_diffs(s1, s2, filename=''):
        """Print diffs between strings s1 and s2."""
        lines = list(difflib.unified_diff(
            g.splitLines(s1),
            g.splitLines(s2),
            fromfile=f"Old {filename}",
            tofile=f"New {filename}",
        ))
        print('')
        tag = f"Diffs for {filename}" if filename else 'Diffs'
        g.printObj(lines, tag=tag)
    #@+node:ekr.20191223095408.1: *3* node/token finders...
    # Functions that associate tokens with nodes.
    #@+node:ekr.20191223093539.1: *4* function: find_anchor_token
    def find_anchor_token(node):
        """
        Return the anchor_token for node, a token such that token.node == node.
        """
        
        node1 = node
        
        def anchor_token(node):
            """Return the anchor token in node.token_list"""
            # Careful: some tokens in the token list may have been killed.
            for token in getattr(node, 'token_list', []):
                if is_ancestor(node1, token):
                    return token
            return None
            
        # This table only has to cover fields for ast.Nodes that
        # won't have any associated token.
        fields = (
            # Common...
            'elt', 'elts', 'body', 'value',
            # Less common...
            'dims', 'ifs', 'names', 's',
            'test', 'values', 'targets',
        )
        while node:
            # First, try the node itself.
            token = anchor_token(node)
            if token:
                return token
            # Second, try the most common nodes w/o token_lists:
            if isinstance(node, ast.Call):
                node = node.func
            elif isinstance(node, ast.Tuple):
                node = node.elts
            # Finally, try all other nodes.
            else:
                # This will be used rarely.
                for field in fields:
                    node = getattr(node, field, None)
                    if node:
                        token = anchor_token(node)
                        if token:
                            return token
                else:
                    break
        return None
    #@+node:ekr.20191231160225.1: *4* function: find_paren_token
    def find_paren_token(i, tokens):
        """Return i of the next paren token, starting at tokens[i]."""
        while i < len(tokens):
            token = tokens[i]
            if token.kind == 'op' and token.value in '()':
                return i
            if is_significant_token(token):
                break
            i += 1
        return None
    #@+node:ekr.20191223054300.1: *4* function: is_ancestor
    def is_ancestor(node, token):
        """Return True if node is an ancestor of token."""
        t_node = token.node
        if not t_node:
            assert token.kind == 'killed', repr(token)
            return False
        while t_node:
            if t_node == node:
                return True
            t_node = t_node.parent
        return False
    #@+node:ekr.20191231082137.1: *4* function: nearest_common_ancestor
    def nearest_common_ancestor(node1, node2):
        """
        Return the nearest common ancestor nodes for the given nodes.
        
        The nodes must have parent links.
        """

        def parents(node):
            aList = []
            while node:
                aList.append(node)
                node = node.parent
            return list(reversed(aList))
            
        result = None
        parents1 = parents(node1)
        parents2 = parents(node2)
        while parents1 and parents2:
            parent1 = parents1.pop(0)
            parent2 = parents2.pop(0)
            if parent1 == parent2:
                result = parent1
            else:
                break
        return result
    #@+node:ekr.20191223053324.1: *4* function: tokens_for_node
    def tokens_for_node(node, tokens):
        """Return the list of all tokens descending from node."""
        # Find any token descending from node.
        token = find_anchor_token(node)
        if not token:
            if 0: # A good trace for debugging.
                print('')
                g.trace('===== no tokens', node.__class__.__name__)
                g.printObj(getattr(node, 'token_list', []), tag="Useless tokens")
            return []
        assert is_ancestor(node, token)
        # Scan backward.
        i = first_i = token.index
        while i >= 0:
            token2 = tokens[i-1]
            if getattr(token2, 'node', None):
                if is_ancestor(node, token2):
                    first_i = i - 1
                else:
                    break
            i -= 1
        # Scan forward.
        j = last_j = token.index
        while j + 1 < len(tokens):
            token2 = tokens[j+1]
            if getattr(token2, 'node', None):
                if is_ancestor(node, token2):
                    last_j = j + 1
                else:
                    break
            j += 1
        last_j = match_parens(first_i, last_j, tokens)
        results = tokens[first_i : last_j + 1]
        return results
    #@+node:ekr.20191224093336.1: *4* function: match_parens
    match_parens_message_given = False

    def match_parens(i, j, tokens):
        """
        Match parens in tokens[i:j]. Return the new j.
        """
        if j >= len(tokens):
            return len(tokens)
        # Calculate paren level...
        level = 0
        for n in range(i, j+1):
            token = tokens[n]
            if token.kind == 'op' and token.value == '(':
                level += 1
            if token.kind == 'op' and token.value == ')':
                level -= 1
        # Find matching ')' tokens...
        if level > 0:
            while level > 0 and j + 1 < len(tokens):
                token = tokens[j+1]
                if token.kind == 'op' and token.value == ')':
                    level -= 1
                elif token.kind == 'op' and token.value == '(': # Bug fix.
                    level += 1
                elif is_significant_token(token):
                    break
                j += 1
        if level != 0:
            print('')
            s = tokens_to_string(tokens[i:j+1])
            g.trace(f"Unmatched tokens. level={level}, {s!r}\n")
        return j
    #@+node:ekr.20191225061516.1: *3* node/token replacers...
    # Functions that replace tokens or nodes.
    #@+node:ekr.20191231162249.1: *4* function: add_token_to_token_list
    def add_token_to_token_list(token, node):
        """Insert token in the proper location of node.token_list."""
        token_i = token.index
        token_list = getattr(node, 'token_list', [])
        for i, t, in enumerate(token_list):
            if t.index > token_i:
                token_list.insert(i, token)
                node.token_list = token_list
                return
        token_list.append(token)
        node.token_list = token_list
    #@+node:ekr.20191225055616.1: *4* function: replace_node
    def replace_node(new_node, old_node):
        """Replace new_node by old_node in the parse tree."""
        parent = old_node.parent
        new_node.parent = parent
        new_node.node_index = old_node.node_index
        children = parent.children
        i = children.index(old_node)
        children[i] = new_node
        fields = getattr(old_node, '_fields', None)
        if fields:
            for field in fields:
                field = getattr(old_node, field)
                if field == old_node:
                    setattr(old_node, field, new_node)
                    break
    #@+node:ekr.20191225055626.1: *4* function: replace_token
    def replace_token(token, kind, value):
        """Replace kind and value of the given token."""
        if token.kind in ('endmarker', 'killed'):
            return
        token.kind = kind
        token.value = value
        token.node = None  # Should be filled later.
    #@-others
#@+node:ekr.20191027072910.1: ** Exception classes
class AssignLinksError(Exception):
    """Assigning links to ast nodes failed."""

class AstNotEqual(Exception):
    """The two given AST's are not equivalent."""
    
class FailFast(Exception):
    """Abort tests in TestRunner class."""
#@+node:ekr.20191227170540.1: ** Test classes...
#@+node:ekr.20191227154302.1: *3*  class BaseTest (TestCase)
class BaseTest (unittest.TestCase):
    """
    The base class of all tests of leoAst.py.
    
    This class contains only helpers.
    """
    
    # Statistics.
    counts, times = {}, {}

    #@+others
    #@+node:ekr.20200110103036.1: *4* BaseTest.adjust_expected
    def adjust_expected(self, s):
        """Adjust leading indentation in the expected string s."""
        return g.adjustTripleString(s.lstrip('\\\n')).rstrip() + '\n'
    #@+node:ekr.20200110092217.1: *4* BaseTest.check_roundtrip
    def check_roundtrip(self, contents):
        """Check that the tokenizer round-trips the given contents."""
        contents, tokens, tree = self.make_data(contents)
        results = tokens_to_string(tokens)
        assert contents == results, expected_got(contents, results)
    #@+node:ekr.20191227054856.1: *4* BaseTest.make_data
    def make_data(self, contents, description=None):
        """Return (contents, tokens, tree) for the given contents."""
        contents = contents.lstrip('\\\n')
        if not contents:  # pragma: no cover
            return None, None, None
        t1 = get_time()
        self.update_counts('characters', len(contents))
        contents = g.adjustTripleString(contents).rstrip()
        # Create the TOG instance.
        self.tog = TokenOrderGenerator()
        self.tog.filename = description or '<unit test>'
        # Pass 0: create the tokens and parse tree
        tokens = self.make_tokens(contents)
        if not tokens:  # pragma: no cover
            return None, None, None
        tree = self.make_tree(contents)
        if not tree:  # pragma: no cover
            return None, None, None
        if 1: # Excellent traces for tracking down mysteries.
            dump_contents(contents)
            dump_ast(tree)
            # dump_tokens(tokens)
        self.balance_tokens(tokens)
        # Pass 1: create the links
        try:
            self.create_links(tokens, tree)
        except Exception as e:
            # The caller will give the error.
            return None, None, None
        self.reassign_tokens(tokens, tree)
        t2 = get_time()
        self.update_times('90: TOTAL', t2 - t1)
        return contents, tokens, tree
    #@+node:ekr.20191227103533.1: *4* BaseTest.make_file_data
    def make_file_data(self, filename):
        """Return (contents, tokens, tree) corresponding to the contents of the given file."""
        directory = r'c:\leo.repo\leo-editor\leo\core'
        filename = os.path.join(directory, filename)
        contents = read_file(filename)
        contents, tokens, tree = self.make_data(contents, filename)
        return contents, tokens, tree
        
    #@+node:ekr.20191228101601.1: *4* BaseTest: passes...
    #@+node:ekr.20191228095945.11: *5* 0.1: BaseTest.make_tokens
    def make_tokens(self, contents):
        """
        BaseTest.make_tokens.
        
        Make tokens from contents.
        """
        t1 = get_time()
        # Tokenize.
        tokens = make_tokens(contents)
        t2 = get_time()
        self.update_counts('tokens', len(tokens))
        self.update_times('01: make-tokens', t2-t1)
        return tokens
    #@+node:ekr.20191228102101.1: *5* 0.2: BaseTest.make_tree
    def make_tree(self, contents):
        """
        BaseTest.make_tree.
        
        Return the parse tree for the given contents string.
        """
        t1 = get_time()
        tree = parse_ast(contents)
        t2 = get_time()
        self.update_times('02: parse_ast', t2-t1)
        return tree
    #@+node:ekr.20191228185201.1: *5* 0.3: BaseTest.balance_tokens
    def balance_tokens(self, tokens):
        """
        BastTest.balance_tokens.
        
        Insert links between corresponding paren tokens.
        """
        t1 = get_time()
        count = self.tog.balance_tokens(tokens)
        t2 = get_time()
        self.update_counts('paren-tokens', count)
        self.update_times('03: balance-tokens', t2-t1)
        return count
    #@+node:ekr.20191228101437.1: *5* 1.1: BaseTest.create_links
    def create_links(self, tokens, tree, filename='unit test'):
        """
        BaseTest.create_links.
        
        Insert two-way links between the tokens and ast tree.
        """
        tog = self.tog
        # Catch exceptions so we can get data late.
        try:
            t1 = get_time()
            # Yes, list *is* required here.
            list(tog.create_links(tokens, tree))
            t2 = get_time()
            self.update_counts('nodes', tog.n_nodes)
            self.update_times('11: create-links', t2 - t1)
        except Exception as e:
            print('')
            g.trace(f"Exception...\n")
            # Don't use g.trace.  It doesn't handle newlines properly.
            print(e)
            # g.es_exception()
            raise
    #@+node:ekr.20191229065358.1: *5* 1.2: BaseTest.reassign_tokens
    def reassign_tokens(self, tokens, tree, filename='unit test'):
        """
        BaseTest.reassign_tokens.
        
        Reassign tokens to ast nodes. This pass is optional.
        """
        t1 = get_time()
        self.tog.reassign_tokens(tokens, tree)
        t2 = get_time()
        self.update_times('12: reassign-links', t2 - t1)
    #@+node:ekr.20191228095945.10: *5* 2.1: BaseTest.fstringify
    def fstringify(self, contents, filename, tokens, tree):
        """
        BaseTest.fstringify.
        """
        t1 = get_time()
        result_s = Fstringify().fstringify(contents, filename, tokens, tree)
        t2 = get_time()
        self.update_times('21: fstringify', t2 - t1)
        return result_s
    #@+node:ekr.20200107175223.1: *5* 2.2: BaseTest.beautify
    def beautify(self, contents, filename, tokens, tree):
        """
        BaseTest.beautify.
        """
        t1 = get_time()
        result_s = Orange().beautify(contents, filename, tokens, tree)
        t2 = get_time()
        self.update_times('22: beautify', t2 - t1)
        return result_s
    #@+node:ekr.20191228095945.1: *4* BaseTest: stats...
    # Actions should fail by throwing an exception.
    #@+node:ekr.20191228095945.12: *5* BaseTest.dump_stats & helpers
    def dump_stats(self):
        """Show all calculated statistics."""
        if self.counts or self.times:
            print('')
            self.dump_counts()
            self.dump_times()
            print('')
    #@+node:ekr.20191228154757.1: *6* BaseTest.dump_counts
    def dump_counts(self):
        """Show all calculated counts."""
        for key, n in self.counts.items():
            print(f"{key:>16}: {n:>6}")
    #@+node:ekr.20191228154801.1: *6* BaseTest.dump_times
    def dump_times(self):
        """
        Show all calculated times.
        
        Keys should start with a priority (sort order) of the form `[0-9][0-9]:`
        """
        for key in sorted(self.times):
            t = self.times.get(key)
            key2 = key[3:]
            print(f"{key2:>16}: {t:6.3f} sec.")
       
    #@+node:ekr.20191228181624.1: *5* BaseTest.update_counts & update_times
    def update_counts(self, key, n):
        """Update the count statistic given by key, n."""
        old_n = self.counts.get(key, 0)
        self.counts [key] = old_n + n

    def update_times(self, key, t):
        """Update the timing statistic given by key, t."""
        old_t = self.times.get(key, 0.0)
        self.times [key] = old_t + t
    #@-others
#@+node:ekr.20141012064706.18390: *3* class AstDumper
class AstDumper:  # pragma: no cover
    """A class supporting various kinds of dumps of ast nodes."""

    #@+others
    #@+node:ekr.20191112033445.1: *4* dumper.dump_tree & helper
    def dump_tree(self, node):
        """Briefly show a tree, properly indented."""
        result = [self.show_header()]
        self.dump_tree_and_links_helper(node, 0, result)
        return ''.join(result)
    #@+node:ekr.20191125035321.1: *5* dumper.dump_tree_and_links_helper
    def dump_tree_and_links_helper(self, node, level, result):
        """Return the list of lines in result."""
        if node is None:
            return
        # Let block.
        indent = ' ' * 2 * level
        children = getattr(node, 'children', [])
        node_s = self.compute_node_string(node, level)
        # Dump...
        if isinstance(node, (list, tuple)):
            for z in node:
                self.dump_tree_and_links_helper(z, level, result)
        elif isinstance(node, str):
            result.append(f"{indent}{node.__class__.__name__:>8}:{node}\n")
        elif isinstance(node, ast.AST):
            # Node and parent.
            result.append(node_s)
            # Children.
            for z in children:
                self.dump_tree_and_links_helper(z, level+1, result)
        else:
            result.append(node_s)
    #@+node:ekr.20191125035600.1: *4* dumper.compute_node_string & helpers
    def compute_node_string(self, node, level):
        """Return a string summarizing the node."""
        indent = ' ' * 2 * level
        parent = getattr(node, 'parent', None)
        node_id = getattr(node, 'node_index', '??')
        parent_id = getattr(parent, 'node_index', '??')
        parent_s = f"{parent_id:>3}.{parent.__class__.__name__} " if parent else ''
        class_name = node.__class__.__name__
        descriptor_s = f"{node_id}.{class_name}: " + self.show_fields(class_name, node, 30)
        tokens_s = self.show_tokens(node, 70, 100)
        lines = self.show_line_range(node)
        full_s1 = f"{parent_s:<16} {lines:<10} {indent}{descriptor_s} "
        node_s =  f"{full_s1:<62} {tokens_s}\n"
        return node_s
    #@+node:ekr.20191113223424.1: *5* dumper.show_fields
    def show_fields(self, class_name, node, truncate_n):
        """Return a string showing interesting fields of the node."""
        val = ''
        if class_name == 'JoinedStr':
            values = node.values
            assert isinstance(values, list)
            # Str tokens may represent *concatenated* strings.
            results = []
            fstrings, strings = 0, 0
            for z in values:
                assert isinstance(z, (ast.FormattedValue, ast.Str))
                if isinstance(z, ast.Str):
                    results.append(z.s)
                    strings += 1
                else:
                    results.append(z.__class__.__name__)
                    fstrings += 1
            val = f"{strings} str, {fstrings} f-str"
        elif class_name == 'keyword':
            if isinstance(node.value, ast.Str):
                val = f"arg={node.arg}..Str.value.s={node.value.s}"
            elif isinstance(node.value, ast.Name):
                val = f"arg={node.arg}..Name.value.id={node.value.id}"
            else:
                val = f"arg={node.arg}..value={node.value.__class__.__name__}"
        elif class_name == 'Name':
            val = f"id={node.id!r}"
        elif class_name == 'NameConstant':
            val = f"value={node.value!r}"
        elif class_name == 'Num':
            val = f"n={node.n}"
        elif class_name == 'Starred':
            if isinstance(node.value, ast.Str):
                val = f"s={node.value.s}"
            elif isinstance(node.value, ast.Name):
                val = f"id={node.value.id}"
            else:
                val = f"s={node.value.__class__.__name__}"
        elif class_name == 'Str':
            val = f"s={node.s!r}"
        elif class_name in ('AugAssign', 'BinOp', 'BoolOp', 'UnaryOp'): # IfExp
            name = node.op.__class__.__name__
            val = f"op={_op_names.get(name, name)}"
        elif class_name == 'Compare':
            ops = ','.join([_op_names.get(z, repr(z)) for z in node.ops])
            val = f"ops={ops}"
        else:
            val = ''
        return g.truncate(val, truncate_n)

    #@+node:ekr.20191114054726.1: *5* dumper.show_line_range
    def show_line_range(self, node):
        
        token_list = getattr(node, 'token_list', [])
        if not token_list:
            return ''
        min_ = min([z.line_number for z in token_list])
        max_ = max([z.line_number for z in token_list])
        return f"{min_}" if min_ == max_ else f"{min_}..{max_}"
    #@+node:ekr.20191113223425.1: *5* dumper.show_tokens
    def show_tokens(self, node, n, m):
        """
        Return a string showing node.token_list.
        
        Split the result if n + len(result) > m
        """
        token_list = getattr(node, 'token_list', [])
        result = []
        for z in token_list:
            if z.kind == 'comment':
                val = g.truncate(z.value,10) # Short is good.
                result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'name':
                val = g.truncate(z.value,20)
                result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'newline':
                result.append(f"{z.kind}.{z.index}({z.line_number}:{len(z.line)})")
            elif z.kind == 'number':
                result.append(f"{z.kind}.{z.index}({z.value})")
            elif z.kind == 'op':
                result.append(f"{z.kind}.{z.index}={z.value}")
            elif z.kind == 'string':
                val = g.truncate(z.value,30)
                result.append(f"{z.kind}.{z.index}({val})")
            elif z.kind == 'ws':
                result.append(f"{z.kind}.{z.index}({len(z.value)})")
            else:
                # Indent, dedent, encoding, etc.
                # Don't put a blank.
                continue 
            result.append(' ')
        #
        # split the line if it is too long.
        # g.printObj(result, tag='show_tokens')
        if 1:
            return ''.join(result)
        line, lines = [], []
        for r in result:
            line.append(r)
            if n + len(''.join(line)) >= m:
                lines.append(''.join(line))
                line = []
        lines.append(''.join(line))
        pad = '\n' + ' '*n
        return pad.join(lines)
    #@+node:ekr.20191110165235.5: *4* dumper.show_header
    def show_header(self):
        """Return a header string, but only the fist time."""
        return (
            f"{'parent':<16} {'lines':<10} {'node':<34} {'tokens'}\n"
            f"{'======':<16} {'=====':<10} {'====':<34} {'======'}\n")
    #@+node:ekr.20141012064706.18392: *4* dumper.dump_ast & helper
    annotate_fields=False
    include_attributes = False
    indent_ws = ' '

    def dump_ast(self, node, level=0):
        """
        Dump an ast tree. Adapted from ast.dump.
        """
        sep1 = f'\n%s' % (self.indent_ws * (level + 1))
        if isinstance(node, ast.AST):
            fields = [(a, self.dump_ast(b, level+1)) for a, b in self.get_fields(node)]
            if self.include_attributes and node._attributes:
                fields.extend([(a, self.dump_ast(getattr(node, a), level+1))
                    for a in node._attributes])
            if self.annotate_fields:
                aList = [f'%s=%s' % (a, b) for a, b in fields]
            else:
                aList = [b for a, b in fields]
            name = node.__class__.__name__
            sep = '' if len(aList) <= 1 else sep1
            return f'%s(%s%s)' % (name, sep, sep1.join(aList))
        if isinstance(node, list):
            sep = sep1
            return f'LIST[%s]' % ''.join(
                [f'%s%s' % (sep, self.dump_ast(z, level+1)) for z in node])
        return repr(node)
    #@+node:ekr.20141012064706.18393: *5* dumper.get_fields
    def get_fields(self, node):
        
        

        return (
            (a, b) for a, b in ast.iter_fields(node)
                if a not in ['ctx',] and b not in (None, [])
        )
    #@-others
#@+node:ekr.20191229083512.1: *3* class TestFstringify (BaseTest)
class TestFstringify (BaseTest):
    """Tests for the TokenOrderGenerator class."""

    #@+others
    #@+node:ekr.20200111043311.1: *4* Bugs...
    #@+node:ekr.20200111043311.2: *5* test_fs.test_crash_1
    def test_crash_1(self):
        # leoCheck.py.
        contents = """return ('error', 'no member %s' % ivar)"""
        expected = """return ('error', f'no member {ivar}')"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, 'test_braces', tokens, tree)
        assert results == expected, expected_got(expected, results)
    #@+node:ekr.20200111075114.1: *5* test_fs.test_crash_2
    def test_crash_2(self):
        # leoCheck.py, line 1704.
        # format = 
            # 'files: %s lines: %s chars: %s classes: %s\n'
            # 'defs: %s calls: %s undefined calls: %s returns: %s'
        # )
        contents = r"""'files: %s\n' 'defs: %s'"""
        expected = contents
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, 'test_braces', tokens, tree)
        assert results == expected, expected_got(expected, results)

    #@+node:ekr.20200106163535.1: *4* test_braces
    def test_braces(self):

        # From pr.construct_stylesheet in leoPrinting.py
        contents = r"""'h1 {font-family: %s}' % (family)"""
        expected = r"""f'h1 {{font-family: {family}}}'"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, 'test_braces', tokens, tree)
        assert results == expected, expected_got(expected, results)
    #@+node:ekr.20191230150653.1: *4* test_call_in_rhs
    def test_call_in_rhs(self):
        
        contents = """'%s' % d()"""
        expected = """f'{d()}'"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, '<string>', tokens, tree)
        assert results == expected, expected_got(expected, results)
    #@+node:ekr.20200104045907.1: *4* test_call_in_rhs_2
    def test_call_with_attribute_2(self):
        
        # From LM.traceSettingsDict
        contents = """print('%s' % (len(d.keys())))"""
        expected = """print(f'{len(d.keys())}')"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, '<string>', tokens, tree)
        assert results == expected, expected_got(expected, results)
    #@+node:ekr.20200105073155.1: *4* test_call_with_attribute
    def test_call_with_attribute(self):
        
        contents = """g.blue('wrote %s' % p.atShadowFileNodeName())"""
        expected = """g.blue(f'wrote {p.atShadowFileNodeName()}')"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, '<string>', tokens, tree)
        assert results == expected, expected_got(expected, results)
    #@+node:ekr.20200101060616.1: *4* test_complex_rhs
    def test_complex_rhs(self):
        # From LM.mergeShortcutsDicts.
        contents = (
            """g.trace('--trace-binding: %20s binds %s to %s' % ("""
            """   c.shortFileName(), binding, d.get(binding) or []))""")
        expected = (
            """g.trace(f'--trace-binding: {c.shortFileName():20} """
            """binds {binding} to {d.get(binding) or []}')""")
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, '<string>', tokens, tree)
        assert results == expected, expected_got(expected, results)
    #@+node:ekr.20200106085608.1: *4* test_ImportFrom
    def test_ImportFrom(self):
        
        table = (
            """from .globals import a, b""",
            """from ..globals import x, y, z""",
            """from . import j""",
        )
        for contents in table:
            contents, tokens, tree = self.make_data(contents)
            results = self.fstringify(contents, '<string>', tokens, tree)
            assert results == contents, expected_got(contents, results)
    #@+node:ekr.20200106042452.1: *4* test_ListComp
    def test_ListComp(self):
        
        table = (
            """replaces = [L + c + R[1:] for L, R in splits if R for c in letters]""",
            """[L for L in x for c in y]""",
            """[L for L in x for c in y if L if not c]""",
        )
        for contents in table:
            contents, tokens, tree = self.make_data(contents)
            results = self.fstringify(contents, '<string>', tokens, tree)
            expected = contents
            assert results == expected, expected_got(expected, results)
    #@+node:ekr.20200104042705.1: *4* test_newlines
    def test_newlines(self):

        contents = r"""\
    print("hello\n")
    print('world\n')
    print("hello\r\n")
    print('world\r\n')
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents
        results = self.fstringify(contents, '<string>', tokens, tree)
        assert results == expected, expected_got(expected, results)
    #@+node:ekr.20191230183652.1: *4* test_parens_in_rhs
    def test_parens_in_rhs(self):

        contents = """print('%20s' % (ivar), val)"""
        expected = """print(f'{ivar:20}', val)"""
        contents, tokens, tree = self.make_data(contents)
        results = self.fstringify(contents, '<string>', tokens, tree)
        assert results == expected, expected_got(expected, results)
    #@+node:ekr.20200106091740.1: *4* test_single_quotes
    def test_single_quotes(self):
        
        table = (
            ("""print('%r "default"' % style_name)""",
             """print(f'{style_name!r} "default"')"""),
            ("""print('%r' % "val")""",
             """print(f'{"val"!r}')"""),
            # f-strings can't contain backslashes.
            ("""print("%r" % "val")""",
             """print("%r" % "val")"""),
        )
        fails = []
        for i, data in enumerate(table):
            contents, expected = data
            contents, tokens, tree = self.make_data(contents)
            description = f"test_single_quotes: {i}"
            results = self.fstringify(contents, description, tokens, tree)
            if results != expected:  # pragma: no cover
                expected_got(expected, results)
                fails.append(description)
        assert not fails, fails
    #@-others
#@+node:ekr.20200107174645.1: *3* class TestOrange (BaseTest)
class TestOrange (BaseTest):
    """Tests for the Orange class."""

    #@+others
    #@+node:ekr.20200107174742.1: *4* test_small_contents
    def test_small_contents(self):

        contents = """print('hi')"""
        expected = """print('hi')\n"""
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_braces', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200108082833.1: *4* test_lines_before_class
    def test_lines_before_class(self):

        contents = """\
    a = 2
    class aClass:
        pass
    """
        expected = """\
    a = 2


    class aClass:
        pass
    """
        contents, tokens, tree = self.make_data(contents)
        contents = g.adjustTripleString(contents)
        expected = g.adjustTripleString(expected) + '\n'
        results = self.beautify(contents, 'test_lines_before_class', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200108075541.1: *4* test_leo_sentinels
    def test_leo_sentinels(self):

        # Careful: don't put a sentinel into the file directly.
        # That would corrupt leoAst.py.
        sentinel = '#@+node:ekr.20200105143308.54: ** test'
        contents = f"""\
    {sentinel}
    def spam():
        pass
    """
        contents, tokens, tree = self.make_data(contents)
        expected = contents.rstrip() + '\n\n'
        results = self.beautify(contents, 'test_leo_sentinels', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110102248.1: *4* Pet peeves...
    #@+node:ekr.20200110014220.26: *5* test_ws_after_unary_minus
    def test_ws_after_unary_minus(self):

        contents = """\
    def spam():
        if - 1 < 2:
            pass
    """
        expected = """\
    def spam():
        if -1 < 2:
            pass
    """
        expected = self.adjust_expected(expected) + '\n'
            # Add newline because of def.
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_ws_after_unary_minus', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.80: *5* test_ws_around_arith_op_in_args
    def test_ws_around_arith_op_in_args(self):
        # Pet peeve.
        contents = """\
    def foo(a, b):
        foo(a = 2+3, b = 4-5, c = 6*7, d = 8 / 9, e =10 // 11)
        bar(2 + baz)
    """
        expected = """\
    def foo(a, b):
        foo(a=2+3, b=4-5, c=6*7, d=8/9, e=10//11)
        bar(2+baz)
    """
        expected = self.adjust_expected(expected) + '\n'
            # Add newline because of def.
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_spaces_before_trailing_comment', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.86: *5* test_ws_before_comma_semicolon_colon
    def test_ws_before_comma_semicolon_colon(self):
        # Pet peeve.
        contents = """\
    if x == 4: pass
    if x == 4 : pass
    print (x, y); x, y = y, x
    print (x , y) ; x , y = y , x
    x, y = y, x
    x , y = y , x
    """
        expected = """\
    if x == 4: pass
    if x == 4: pass
    print(x, y); x, y = y, x
    print(x, y); x, y = y, x
    x, y = y, x
    x, y = y, x
    """
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_spaces_before_trailing_comment', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.74: *5* test_ws_before_trailing_comment
    def test_ws_before_trailing_comment(self):
        # Pet peeve.
        contents = """\
    a = b # comment
    c = d# comment
    e - f   # comment
    # Single-line comment.
    """
        expected = """\
    a = b  # comment
    c = d  # comment
    e - f  # comment
    # Single-line comment.
    """
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_spaces_before_trailing_comment', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.83: *5* test_ws_before_word_ops
    def test_ws_before_word_ops(self):
        # Pet peeve.
        contents = """\
    b =    ('and', 'in', 'not', 'not in', 'or')
    # def foo():
        # return ''.join([z.to_string() for z in self.code_list])

    """
        expected = """\
    b = ('and', 'in', 'not', 'not in', 'or')
    # def foo():
        # return ''.join([z.to_string() for z in self.code_list])

    """
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_spaces_before_trailing_comment', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.89: *5* test_ws_in_parens_1
    def test_ws_in_parens_1(self):
        # Pet peeve.
        contents = """\
    spam(1)
    spam ( 1 )
    dct ['key'] = lst [index]
    dct['key'] = lst[index]
    """
        expected = """\
    spam(1)
    spam(1)
    dct['key'] = lst[index]
    dct['key'] = lst[index]
    """
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_spaces_before_trailing_comment', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.92: *5* test_ws_in_parens_2
    def test_ws_in_parens_2(self):
        # Pet peeve.
        contents = """\
    foo = (0,)
    bar = (0, )
    """
        expected = """\
    foo = (0,)
    bar = (0,)
    """
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_spaces_before_trailing_comment', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.95: *5* test_ws_in_slices_1
    def test_ws_in_slices_1(self):
        # Pet peeve.
        contents = """\
    a1[lower + offset: upper + offset]
    """
    # a2[lower+offset : upper+offset]
        expected = """\
    a1[lower + offset : upper + offset]
    """
    # a2[lower + offset : upper + offset]
        tag = 'test_ws_in_slices_1'
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents, tag)
        results = self.beautify(contents, tag, tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.98: *5* test_ws_in_slices_2
    def test_ws_in_slices_2(self):
        # Pet peeve.
        contents = """\
    ham[ : upper_fn(x) : step_fn(x)]
    """
        expected = """\
    ham[: upper_fn(x) : step_fn(x)]
    """
        tag = 'test_ws_in_slices_2'
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents, tag)
        results = self.beautify(contents, tag, tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110122249.1: *5* test_ws_in_slices_3
    def test_ws_in_slices_3(self):
        # Pet peeve.
        contents = """\
    ham[ : : step_fn(x)]
    """
        expected = """\
    ham[:: step_fn(x)]
    """
        tag = 'test_ws_in_slices_3'
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents, tag)
        results = self.beautify(contents, tag, tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110121819.1: *5* test_ws_in_slices_4
    def test_ws_in_slices_4(self):
        # Pet peeve.
        contents = """empty [ : ]"""
        expected = """empty[:]"""
        tag = 'test_ws_in_slice_4'
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents, tag)
        results = self.beautify(contents, tag, tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.101: *5* test_ws_in_slices_5
    def test_ws_in_slices_5(self):
        # Pet peeve.
        contents = """\
    a1[1: 9], a2[1: 9: 3]
    """
    # a1[1: 9], a2[1: 9: 3], a3[: 9: 3], a4[1:: 3]
    # a5[ lower: upper ], a6[lower :: step]
    # a7[: upper]
        expected = """\
    a1[1 : 9], a2[1 : 9 : 3]
    """
    # a1[1 : 9], a2[1 : 9 : 3], a3[:9 : 3], a4[1 :: 3]
    # a5[lower : upper], a6[lower :: step]
    # a7[: upper]
        tag = 'test_ws_in_slices_5'
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents, tag)
        results = self.beautify(contents, tag, tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110124656.1: *5* test_ws_in_slices_6
    def test_ws_in_slices_6(self):
        # Pet peeve.
        # Empty step.
        contents = """a1[1: 9: ], a2[lower : upper: ]"""
        expected = """a1[1 : 9:], a2[lower : upper:]"""
        tag = 'test_ws_in_slices_6'
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents, tag)
        results = self.beautify(contents, tag, tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@+node:ekr.20200110014220.104: *5* test_ws_inside_parens_etc
    def test_ws_inside_parens_etc(self):
        # Pet peeve.
        contents = """\
    spam(ham[1], {eggs: 2})
    spam( ham[ 1 ], { eggs: 2 } )
    """
        expected = """\
    spam(ham[1], {eggs: 2})
    spam(ham[1], {eggs: 2})
    """
        expected = self.adjust_expected(expected)
        contents, tokens, tree = self.make_data(contents)
        results = self.beautify(contents, 'test_spaces_before_trailing_comment', tokens, tree)
        assert results == expected, expected_got(repr(expected), repr(results))
    #@-others
    
#@+node:ekr.20191231130208.1: *3* class TestReassignTokens (BaseTest)
class TestReassignTokens (BaseTest):
    """Test cases for the ReassignTokens class."""

    #@+others
    #@+node:ekr.20191231130320.1: *4* test_reassign_tokens (to do)
    def test_reassign_tokens(self):
        pass
    #@+node:ekr.20191231130334.1: *4* test_nearest_common_ancestor
    def test_nearest_common_ancestor(self):
        
        contents = """name='uninverted %s' % d.name()"""
        contents, tokens, tree = self.make_data(contents)
        # dump_tokens(tokens)
        # dump_tree(tree)
        
    #@-others
#@+node:ekr.20191227051737.1: *3* class TestTOG (BaseTest)
class TestTOG (BaseTest):
    """
    Tests for the TokenOrderGenerator class.
    
    These tests call BaseTest.make_data, which creates the two-way links
    between tokens and the parse tree.
    
    The asserts in tog.sync_tokens suffice to create strong unit tests.
    """

    #@+others
    #@+node:ekr.20200111042805.1: *4* Bugs...
    #@+node:ekr.20191227052446.10: *4* Contexts...
    #@+node:ekr.20191227052446.11: *5* test_ClassDef
    def test_ClassDef(self):
        contents = r"""\
    class TestClass1:
        pass
        
    def decorator():
        pass

    @decorator
    class TestClass2:
        pass
        
    @decorator
    class TestClass(base1, base2):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.12: *5* test_ClassDef2
    def test_ClassDef2(self):
        contents = r'''\
    """ds 1"""
    class TestClass:
        """ds 2"""
        def long_name(a, b=2):
            """ds 3"""
            print('done')
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.13: *5* test_FunctionDef
    def test_FunctionDef(self):
        contents = r"""\
    def run(fileName=None, pymacs=None, *args, **keywords):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20200111171738.1: *5* test_FunctionDef_with_annotations
    def test_FunctionDef_with_annotations(self):
        contents = r"""\
    def foo(a: 'x', b: 5 + 6, c: list) -> max(2, 9):
        pass
    """
        self.make_data(contents)
        # contents, tokens, tree = self.make_data(contents)
        # dump_ast(tree)
    #@+node:ekr.20191227052446.14: *4* Expressions & operators...
    #@+node:ekr.20191227052446.15: *5* test_attribute
    def test_attribute(self):
        contents = r"""\
    open(os.devnull, "w")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.16: *5* test_CompareOp
    def test_CompareOp(self):
        contents = r"""\
    if a and not b and c:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.17: *5* test_Dict_1
    def test_Dict(self):
        contents = r"""\
    d = {'a' if x else 'b': True,}
    """
        self.make_data(contents)
    #@+node:ekr.20200111191153.1: *5* test_Dict_2
    def test_Dict_2(self):
        contents = r"""\
    d = {}
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.18: *5* test_DictComp
    def test_DictComp(self):
        # leoGlobals.py, line 3028.
        contents = r"""\
    d2 = {val: key for key, val in d.iteritems()}
    """
        self.make_data(contents)
    #@+node:ekr.20200112042410.1: *5* test_ExtSlice
    def test_ExtSlice(self):
        contents = r"""a [1, 2: 3]"""
        self.make_data(contents)
    #@+node:ekr.20191227052446.19: *5* test_ListComp
    def test_ListComp(self):
        # ListComp and comprehension.
        contents = r"""\
    any([p2.isDirty() for p2 in p.subtree()])
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.20: *5* test_NameConstant
    def test_NameConstant(self):
        contents = r"""\
    run(a=None, b=str)
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.21: *5* test_Operator: semicolon
    def test_op_semicolon(self):
        contents = r"""\
    print('c');
    print('d')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.22: *5* test_Operator: semicolon between statements
    def test_op_semicolon2(self):
        contents = r"""\
    a = 1 ; b = 2
    print('a') ; print('b')
    """
        self.make_data(contents)
    #@+node:ekr.20200111194454.1: *5* test_Set
    def test_Set(self):
        contents = """{'a', 'b'}"""
        self.make_data(contents)
    #@+node:ekr.20200111195654.1: *5* test_SetComp
    def test_SetComp(self):
        contents = """aSet = { (x, y) for x in r for y in r if x < y }"""
        self.make_data(contents)

    #@+node:ekr.20191227052446.23: *5* test_UnaryOp
    def test_UnaryOp(self):
        contents = r"""\
    print(-(2))
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.65: *4* f-strings....
    #@+node:ekr.20191227052446.66: *5* test_fstring01: complex Call
    def test_fstring1(self):
        # Line 1177, leoApp.py
        contents = r"""\
    print(
        message = f"line 1: {old_id!r}\n" "line 2\n"
    )
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.67: *5* test_fstring02: Ternary
    def test_fstring2(self):
        contents = r"""\
    func(f"{b if not cond1 else ''}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.68: *5* test_fstring03: single f-string
    def test_fstring3(self):
        contents = r"""\
    print(f'{7.1}')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.69: *5* test_fstring04: f-string + plain
    def test_fstring4(self):
        contents = r"""\
    print(f'{7.1}' 'p7.2')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.70: *5* test_fstring05: plain + f-string
    def test_fstring5(self):
        contents = r"""\
    print('p1' f'{f2}')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.71: *5* test_fstring06: f-string + fstring
    def test_fstring6(self):
        contents = r"""\
    print(f'{f1}' f'{f2}')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.72: *5* test_fstring07: many
    def test_fstring7(self):
        contents = r"""\
    print('s1', f'{f2}' f'f3' f'{f4}' 's5')
    'end'
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.73: *5* test_fstring08: ternary op
    def test_fstring8(self):
        # leoFind.py line 856
        contents = r"""\
    a = f"{'a' if x else 'b'}"
    f()

    # Pass
    # print(f"{'a' if x else 'b'}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.74: *5* test_fstring09: leoFind.py line 856
    def test_fstring9(self):
        contents = r"""\
    func(
        "Isearch"
        f"{' Backward' if True else ''}"
    )
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.75: *5* test_fstring10: leoFind.py: line 861
    def test_fstring10(self):
        # leoFind.py: line 861
        contents = r"""\
    one(f"{'B'}" ": ")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.76: *5* test_fstring11: joins
    def test_fstring11(self):
        contents = r"""\
    print(f'x3{e3+1}y3' f'x4{e4+2}y4')
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.77: *6* more
    # Single f-strings.
    # 'p1' ;
    # f'f1' ;
    # f'x1{e1}y1' ;
    # f'x2{e2+1}y2{e2+2}z2' ;

    # Concatentated strings...
    # 'p2', 'p3' ;
    # f'f2' 'f3' ;

    # f'x5{e5+1}y5{e5+1}z5' f'x6{e6+1}y6{e6+1}z6' ;
    #@+node:ekr.20191227052446.78: *5* test_fstring12: joins + 1 f-expr
    def test_fstring12(self):
        contents = r"""\
    print(f'x1{e1}y1', 'p1')
    print(f'x2{e2}y2', f'f2')
    print(f'x3{e3}y3', f'x4{e4}y4')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.79: *5* test_fstring13: joins + 2 f-exprs
    def test_fstring13(self):
        contents = r"""\
    print(f'x1{e1}y1{e2}z1', 'p1')
    print(f'x2{e3}y2{e3}z2', f'f2')
    print(f'x3{e4}y3{e5}z3', f'x4{e6}y4{e7}z4')
    print('end')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.80: *5* test_fstring14: complex, with commas
    def test_fstring14(self):
        contents = r"""\
    print(f"{list(z for z in ('a', 'b', 'c') if z != 'b')}")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.81: *5* test_fstring15
    def test_fstring15(self):
        contents = r"""\
    print(f"test {a}={2}")
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.83: *5* test_fstring16: simple
    def test_fstring16(self):
        contents = r"""\
    'p1' ;
    f'f1' ;
    'done' ;
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.82: *5* test_regex_fstring
    def test_regex_fstring(self):
        # Line 7709, leoGlobals.py
        contents = r'''\
    fr"""{kinds}://[^\s'"]+[\w=/]"""
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.24: *4* Files...
    #@+node:ekr.20191227052446.25: *5* test_leoApp.py
    def test_leoApp(self):
        self.make_file_data('leoApp.py')
        
    #@+node:ekr.20191227052446.26: *5* test_leoAst.py
    def test_leoAst(self):
        self.make_file_data('leoAst.py')
       
    #@+node:ekr.20191227052446.27: *5* test_leoDebugger.py
    def test_leoDebugger(self):
        self.make_file_data('leoDebugger.py')
       
    #@+node:ekr.20191227052446.28: *5* test_leoFind.py
    def test_leoFind(self):
        self.make_file_data('leoFind.py')
       
    #@+node:ekr.20191227052446.29: *5* test_leoGlobals.py
    def test_leoGlobals(self):
        self.make_file_data('leoGlobals.py')
       
    #@+node:ekr.20191227052446.30: *5* test_leoTips.py
    def test_leoTips(self):
        self.make_file_data('leoTips.py')
       
    #@+node:ekr.20191227052446.31: *5* test_runLeo.py
    def test_runLeo(self):
        self.make_file_data('runLeo.py')
       
    #@+node:ekr.20191227052446.32: *4* If...
    #@+node:ekr.20191227052446.33: *5* test_from leoTips.py
    def test_if1(self):
        # Line 93, leoTips.py
        contents = r"""\
    self.make_data(contents)
    unseen = [i for i in range(5) if i not in seen]
    for issue in data:
        for a in aList:
            print('a')
        else:
            print('b')
    if b:
        print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.34: *5* test_if + tuple
    def test_if2(self):
        contents = r"""\
    for i, j in b:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.35: *5* test_if + unary op
    def test_if3(self):
        contents = r"""\
    if -(2):
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.36: *5* test_if, elif
    def test_if4(self):
        contents = r"""\
    if 1:
        print('a')
    elif 2:
        print('b')
    elif 3:
        print('c')
        print('d')
    print('-')
    if 1:
        print('e')
    elif 2:
        print('f')
        print('g')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.37: *5* test_if, elif + 2
    def test_if5(self):
        contents = r"""\
    if 1:
        pass
    elif 2:
        pass
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.38: *5* test_if, elif, else
    def test_if6(self):
        contents = r"""\
    if (a):
        print('a1')
        print('a2')
    elif b:
        print('b1')
        print('b2')
    else:
        print('c1')
        print('c2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.39: *5* test_if, else
    def test_if7(self):
        contents = r"""\
    if 1:
        print('a')
    else:
        print('b')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.40: *5* test_if, else, if
    def test_if8(self):
        contents = r"""\
    if 1:
        print('a')
    else:
        if 2:
            print('b')
    """
        self.make_data(contents)

    #@+node:ekr.20191227052446.41: *5* test_Nested If's
    def test_if9(self):
        contents = r"""\
    if a:
        if b:
            print('b')
    else:
        if d:
            print('d')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.42: *5* test_ternary + if
    def test_if10(self):
        contents = r"""\
    if 1:
        a = 'class' if cond else 'def'
        # find_pattern = prefix + ' ' + word
        print('1')
    else:
        print('2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227145620.1: *4* Miscellaneous...
    #@+node:ekr.20191227075951.1: *5* test_end_of_line
    def test_end_of_line(self):
        self.make_data("""# Only a comment.""")
    #@+node:ekr.20160521103254.1: *5* test_vistors_exist
    def test_vistors_exist(self):
        """Ensure that visitors for all ast nodes exist."""
        import _ast
        # Compute all fields to BaseTest.
        aList = sorted(dir(_ast))
        remove = [
            'Interactive', 'Suite',  # Not necessary.
            'PyCF_ONLY_AST',  # A constant,
            'AST',  # The base class,
        ]
        aList = [z for z in aList if not z[0].islower()]
            # Remove base classe
        aList = [z for z in aList
            if not z.startswith('_') and not z in remove]
        # Now test them.
        table = (
            TokenOrderGenerator,
        )
        for class_ in table:
            traverser = class_()
            errors, nodes, ops = 0, 0, 0
            for z in aList:
                if hasattr(traverser, 'do_'+z):
                    nodes += 1
                elif _op_names.get(z):
                    ops += 1
                else:  # pragma: no cover
                    errors += 1
                    print(
                        f"Missing {traverser.__class__.__name__} visitor "
                        f"for: {z}")
        msg = f"{nodes} node types, {ops} op types, {errors} errors"
        assert not errors, msg
    #@+node:ekr.20191227052446.50: *4* Plain Strings...
    #@+node:ekr.20191227052446.52: *5* test_\x and \o escapes
    def test_escapes(self):
        # Line 4609, leoGlobals.py
        contents = r"""\
    print("\x7e" "\0777") # tilde.
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.53: *5* test_backslashes in docstring
    def test_backslashes(self):
        # leoGlobals.py.
        contents = r'''\
    class SherlockTracer:
        """before\\after"""
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.54: *5* test_bs/nl
    def test_bs_nl(self):
        contents = r"""\
    print('hello\
    world')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.55: *5* test_bytes bs-x
    def test_bytes(self):
        # Line 201, leoApp.py
        contents = r"""\
    print(b'\xfe')
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.56: *5* test_empty string
    def test_empyt_string(self):
        contents = r"""\
    self.s = ''
    self.i = 0
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.57: *5* test_escaped string delims
    def test_escaped_delims(self):
        contents = r"""\
    print("a\"b")
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.58: *5* test_escaped strings
    def test_escaped_strings(self):
        contents = r"""\
    f1(a='\b', b='\n', t='\t')
    f2(f='\f', r='\r', v='\v')
    f3(bs='\\')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.59: *5* test_f-string join
    def test_fstring_join(self):
        # The first newline causes the fail.
        contents = r"""\
    print(f"a {old_id!r}\n" "b\n")
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.64: *5* test_potential_fstring
    def test_potential_fstring(self):
        contents = r"""\
    print('test %s=%s'%(a, 2))
    print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.60: *5* test_raw docstring
    def test_raw_docstring(self):
        contents = r'''\
    # Line 1619 leoFind.py
    print(r"""DS""")
    '''
        self.make_data(contents)
    #@+node:ekr.20191227052446.61: *5* test_raw escaped strings
    def test_raw_escapes(self):
        contents = r"""\
    r1(a=r'\b', b=r'\n', t=r'\t')
    r2(f=r'\f', r=r'\r', v=r'\v')
    r3(bs=r'\\')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.62: *5* test_single quote
    def test_single_quote(self):
        # leoGlobals.py line 806.
        contents = r"""\
    print('"')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.63: *5* test_string concatenation_1
    def test_concatenation_1(self):
        contents = r"""\
    print('a' 'b')
    print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20200111042825.1: *5* test_string_concatenation_2
    def test_string_concatenation_2(self):
        # Crash in leoCheck.py.
        contents = """return self.Type('error', 'no member %s' % ivar)"""
        self.make_data(contents)
    #@+node:ekr.20191227052446.43: *4* Statements...
    #@+node:ekr.20200111175043.1: *5* test_AsyncDef
    def test_AsyncDef(self):
        contents = r"""\
    async def count():
        print("One")
        await asyncio.sleep(1)
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.44: *5* test_Call
    def test_Call(self):
        contents = """func(a, b, one='one', two=2, three=4+5, *args, **kwargs)"""
        # contents = """func(*args, **kwargs)"""
    # f1(a,b=2)
    # f2(1 + 2)
    # f3(arg, *args, **kwargs)
    # f4(a='a', *args, **kwargs)
        self.make_data(contents)
    #@+node:ekr.20200111175335.1: *5* test_For
    def test_For(self):
        contents = r"""\
    for a in b:
        pass
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.45: *5* test_Global
    def test_Global(self):
        # Line 1604, leoGlobals.py
        contents = r"""
    def spam():
        global gg
        print('')
    """
        self.make_data(contents)

    #@+node:ekr.20200111200424.1: *5* test_ImportFrom
    def test_ImportFrom(self):
        contents = r"""from a import b as c"""
        self.make_data(contents)
    #@+node:ekr.20200111200640.1: *5* test_Nonlocal
    def test_Nonlocal(self):
        contents = r"""nonlocal name1, name2"""
        self.make_data(contents)

    #@+node:ekr.20191227052446.46: *5* test_Try
    def test_Try(self):
        contents = r"""\
    try:
        print('a1')
        print('a2')
    except ImportError:
        print('b1')
        print('b2')
    except SyntaxError:
        print('c1')
        print('c2')
    finally:
        print('d1')
        print('d2')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.47: *5* test_TryExceptElse
    def test_Try2(self):
        # Line 240: leoDebugger.py
        contents = r"""\
    try:
        print('a')
    except ValueError:
        print('b')
    else:
        print('c')
    """
        self.make_data(contents)
    #@+node:ekr.20191227052446.48: *5* test_With
    def test_With(self):
        # leoGlobals.py, line 1785.
        contents = r"""\
    with open(fn) as f:
        pass
    """
        self.make_data(contents)

    #@+node:ekr.20191227052446.49: *5* test_YieldFrom
    def test_YieldFrom(self):
        # Line 1046, leoAst.py
        contents = r"""\
    def gen_test():
        self.node = tree
        yield from self.gen_token('newline', '\n')
        print('done')
    """
        self.make_data(contents)
    #@+node:ekr.20191228193740.1: *4* test_aa && zz
    def test_aaa(self):
        """The first test."""
        g.total_time = get_time()
        
    def test_zzz(self):
        """The last test."""
        t2 = get_time()
        self.update_times('90: TOTAL', t2 - g.total_time)
        self.dump_stats()
    #@-others
#@+node:ekr.20200110093802.1: *3* class TestTokens (BaseTest)
class TestTokens (BaseTest):
    """Unit tests for tokenizing."""

    #@+others
    #@+node:ekr.20200110015014.6: *4* test_bs_nl_tokens
    def test_bs_nl_tokens(self):
        # Test https://bugs.python.org/issue38663.

        contents = """\
    print \
        ('abc')
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20200110015014.8: *4* test_continuation_1
    def test_continuation_1(self):
        
        contents = """\
    a = (3,4,
        5,6)
    y = [3, 4,
        5]
    z = {'a': 5,
        'b':15, 'c':True}
    x = len(y) + 5 - a[
        3] - a[2] + len(z) - z[
        'b']
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20200111085210.1: *4* test_continuation_2
    def test_continuation_2(self):
        # Backslash means line continuation, except for comments
        contents = """\
    x=1+\\\n2
    # This is a comment\\\n# This also
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20200111085211.1: *4* test_continuation_3
    def test_continuation_3(self):

        contents = """\
    # Comment \\\n
    x = 0
    """
        self.check_roundtrip(contents)
    #@+node:ekr.20200110015014.10: *4* test_string_concatenation_1
    def test_string_concatentation_1(self):
        # Two *plain* string literals on the same line
        self.check_roundtrip("""'abc' 'xyz'""")
    #@+node:ekr.20200111081801.1: *4* test_string_concatenation_2
    def test_string_concatentation_2(self):
        # f-string followed by plain string on the same line
        self.check_roundtrip("""f'abc' 'xyz'""")
    #@+node:ekr.20200111081832.1: *4* test_string_concatenation_3
    def test_string_concatentation_3(self):
        # plain string followed by f-string on the same line
        self.check_roundtrip("""'abc' f'xyz'""")
    #@-others
#@+node:ekr.20200107144010.1: *3* class TestTopLevelFunctions (BaseTest)
class TestTopLevelFunctions (BaseTest):
    """Tests for the top-level functions in leoAst.py."""

    #@+others
    #@+node:ekr.20200107144227.1: *4* test_get_encoding_directive
    def test_get_encoding_directive(self):
        
        directory = r'c:\leo.repo\leo-editor\leo\core'
        filename = os.path.join(directory, 'leoAst.py')
        if not os.path.exists(filename):
            self.skipTest(f"not found: {filename}")
        with open(filename, 'rb') as f:
            bb = f.read()
        e = get_encoding_directive(bb)
        assert e.lower() == 'utf-8', repr(e)
    #@+node:ekr.20200107150857.1: *4* test_strip_BOM
    def test_strip_BOM(self):
        
        directory = r'c:\leo.repo\leo-editor\leo\core'
        filename = os.path.join(directory, 'leoAst.py')
        assert os.path.exists(filename), filename
        with open(filename, 'rb') as f:
            bb = f.read()
        assert bb, filename
        e, s = strip_BOM(bb)
        if e is not None:
            assert e.lower() == 'utf-8', repr(e)
        
    #@-others
    
#@+node:ekr.20191227152538.1: *3* class TestTOT (BaseTest)
class TestTOT (BaseTest):
    """Tests for the TokenOrderTraverser class."""
    #@+others
    #@+node:ekr.20200111115318.1: *4* test_tot.test_traverse
    def test_traverse(self):
            
        contents = """\
    f(1)
    b = 2 + 3
    """
    # print('%s = %s' % (2+3, 4*5))
        if 1:
            contents, tokens, tree = self.make_file_data('leoApp.py')
        else:
            contents, tokens, tree = self.make_data(contents)
        # dump_contents(contents)
        # dump_tokens(tokens)
        # dump_tree(tree)
        tot = TokenOrderTraverser()
        t1 = get_time()
        n_nodes = tot.traverse(tree)
        t2 = get_time()
        self.update_counts('nodes', n_nodes)
        self.update_times('50: TOT.traverse', t2 - t1)
        self.dump_stats()
    #@-others
    
#@+node:ekr.20191227170628.1: ** TOG classes
#@+node:ekr.20191113063144.1: *3*  class TokenOrderGenerator
class TokenOrderGenerator:
    """A class that traverses ast (parse) trees in token order."""

    n_nodes = 0  # The number of nodes that have been visited.
    silent = True  # True: suppress all informational messages.

    #@+others
    #@+node:ekr.20200103174914.1: *4* tog: Init...
    #@+node:ekr.20191228184647.1: *5* tog.balance_tokens
    def balance_tokens(self, tokens):
        """
        TOG.balance_tokens.
        
        Find matching paren tokens.
        """
        count, stack = 0, []
        for token in tokens:
            if token.kind == 'op':
                if token.value == '(':
                    count += 1
                    stack.append(token.index)
                if token.value == ')':
                    if stack:
                        index = stack.pop()
                        tokens[index].matching_paren = token.index
                        tokens[token.index].matching_paren = index
                    else:
                        g.trace(f"unmatched ')' at index {token.index}")
        # g.trace(f"tokens: {len(tokens)} matched parens: {count}")
        if stack:
            g.trace("unmatched '(' at {','.join(stack)}")
        return count
    #@+node:ekr.20191113063144.4: *5* tog.create_links
    def create_links(self, tokens, tree, file_name=''):
        """
        A generator creates two-way links between the given tokens and ast-tree.
        
        Callers should call this generator with list(tog.create_links(...))
        
        The sync_tokens method creates the links and verifies that the resulting
        tree traversal generates exactly the given tokens in exact order.
        
        tokens: the list of Token instances for the input.
                Created by make_tokens().
        tree:   the ast tree for the input.
                Created by parse_ast().
        """
        #
        # Init all ivars.
        self.file_name = file_name
            # For tests.
        self.level = 0
            # Python indentation level.
        self.node = None
            # The node being visited.
            # The parent of the about-to-be visited node.
        self.tokens = tokens
            # The immutable list of input tokens.
        self.tree = tree
            # The tree of ast.AST nodes.
        #
        # Traverse the tree.
        try:
            while True:
                next(self.visitor(tree))
        except StopIteration:
            pass
        #
        # Patch the last tokens.
        # Thise ensures that all tokens are patched.
        self.node = tree
        yield from self.gen_token('newline', '\n')
        yield from self.gen_token('endmarker', '')
    #@+node:ekr.20191229071733.1: *5* tog.init_from_file
    def init_from_file(self, filename):  # pragma: no cover
        """
        Create the tokens and ast tree for the given file.
        
        Return (contents, encoding, tokens, tree).
        """
        self.level = 0
        self.filename = filename
        encoding, contents = read_file_with_encoding(filename)
        if contents is None:
            return None, None, None, None
        self.tokens = tokens = make_tokens(contents)
        self.tree = tree = parse_ast(contents)
        list(self.create_links(tokens, tree))
        self.reassign_tokens(tokens, tree)
        return contents, encoding, tokens, tree
    #@+node:ekr.20191229071746.1: *5* tog.init_from_string
    def init_from_string(self, contents):  # pragma: no cover
        """
        Tokenize, parse and create links in the contents string.
        
        Return (tokens, tree).
        """
        self.filename = '<string>'
        self.level = 0
        self.tokens = tokens = make_tokens(contents)
        self.tree = tree = parse_ast(contents)
        list(self.create_links(tokens, tree))
        self.reassign_tokens(tokens, tree)
        return tokens, tree
    #@+node:ekr.20191229072907.1: *5* tog.reassign_tokens
    def reassign_tokens(self, tokens, tree):
        """
        Reassign links between the given token list and ast-tree.
        """
        ReassignTokens().reassign(tokens, tree)
            
    #@+node:ekr.20191223052749.1: *4* tog: Traversal...
    #@+node:ekr.20191113063144.3: *5* tog.begin_visitor
    begin_end_stack = []
    node_index = 0  # The index into the node_stack.
    node_stack = []  # The stack of parent nodes.

    def begin_visitor(self, node):
        """Enter a visitor."""
        # Update the stats.
        self.n_nodes += 1
        # Do this first, *before* updating self.node.
        node.parent = self.node
        if self.node:
            children = getattr(self.node, 'children', [])
            children.append(node)
            self.node.children = children
        # Inject the node_index field.
        assert not hasattr(node, 'node_index'), g.callers()
        node.node_index = self.node_index
        self.node_index += 1
        # begin_visitor and end_visitor must be paired.
        self.begin_end_stack.append(node.__class__.__name__)
        # Push the previous node.
        self.node_stack.append(self.node)
        # Update self.node *last*.
        self.node = node
    #@+node:ekr.20200104032811.1: *5* tog.end_visitor
    def end_visitor(self, node):
        """Leave a visitor."""
        # begin_visitor and end_visitor must be paired.
        entry_name = self.begin_end_stack.pop()
        assert entry_name == node.__class__.__name__, (repr(entry_name), node.__class__.__name__)
        assert self.node == node, (repr(self.node), repr(node))
        # Restore self.node.
        self.node = self.node_stack.pop()
    #@+node:ekr.20200110162044.1: *5* tog.find_next_significant_token
    def find_next_significant_token(self):
        """
        Scan from *after* the previous significant token looking
        for the next significant token.
        
        Return the token, or None. Never change self.px.
        """
        px = self.px + 1
        while px < len(self.tokens):
            token = self.tokens[px]
            px += 1
            if is_significant_token(token):
                return token
        # This will never be taken. because endtoken is significant.
        return None  # pragma: no cover
    #@+node:ekr.20191121180100.1: *5* tog.gen*
    # Useful wrappers.

    def gen(self, z):
        yield from self.visitor(z)
        
    def gen_name(self, val):
        yield from self.visitor(self.sync_name(val))
                    
    def gen_newline(self):
        yield from self.visitor(self.sync_token('newline', '\n'))

    def gen_op(self, val):
        yield from self.visitor(self.sync_op(val))
        
    def gen_token(self, kind, val):
        yield from self.visitor(self.sync_token(kind, val))
    #@+node:ekr.20191113063144.7: *5* tog.sync_token & set_links
    px = -1 # Index of the previous *significant* token.

    def sync_token(self, kind, val):
        """
        Handle a token whose kind & value are given.
        
        If the token is significant, do the following:
            
        1. Find the next significant token*after* px. Call it T.
        2. Verify that T matches the token described by (kind, val).
        3. Create two-way links between all assignable tokens between px and T.
        4. Create two-way links between T and self.node.
        5. Advance by updating self.px.
        """
        trace = False
        node, tokens = self.node, self.tokens
        assert isinstance(node, ast.AST), repr(node)
        if trace:
            g.trace('Ignore:', self.px, kind, repr(val))
        #
        # Leave all non-significant tokens for later.
        if not is_significant(kind, val):
            if trace:
                g.trace('  Scan:', self.px, kind, repr(val))
            return
        #
        # Step one: Scan from *after* the previous significant token,
        #           looking for a token that matches (kind, val)
        #           Leave px pointing at the next significant token.
        #
        #           Special case: because of JoinedStr's, syncing a
        #           string may jump over *many* significant tokens.
        old_px = px = self.px + 1
        while px < len(self.tokens):
            token = tokens[px]
            if trace: g.trace('Token', px, token)
            if (kind, val) == (token.kind, token.value):
                if trace: g.trace('   OK', px, token)
                break  # Success.
            if kind == token.kind == 'number':
                if trace: g.trace('   OK', px, token)
                val = token.value
                break  # Benign: use the token's value, a string, instead of a number.
            if is_significant_token(token):  # pragma: no cover
                # Unrecoverable sync failure.
                if 0:
                    pre_tokens = tokens[max(0, px-10):px+1]
                    g.trace('\nSync Failed...\n')
                    for s in [f"{i:>4}: {z!r}" for i, z in enumerate(pre_tokens)]:
                        print(s)
                line_s = f"line {token.line_number}:"
                val = g.truncate(val, 40)
                raise AssignLinksError(
                    f"       file: {self.filename}\n"
                    f"{line_s:>12} {token.line.strip()}\n"
                    f"Looking for: {kind}.{val}\n"
                    f"      found: {token.kind}.{g.truncate(token.value, 80)}")
            # Skip the insignificant token.
            if trace: g.trace(' SKIP', px, token)
            px += 1
        else:  # pragma: no cover
            # Unrecoverable sync failure.
            if 0:
                g.trace('\nSync failed...')
                g.printObj(tokens[max(0, px-5):], tag='Tokens')
            val = g.truncate(val, 40)
            raise AssignLinksError(
                 f"       file: {self.filename}\n"
                 f"Looking for: {kind}.{val}\n"
                 f"      found: end of token list")
        #
        # Step two: Associate all previous assignable tokens to the ast node.
        while old_px < px:
            token = tokens[old_px]
            if trace: g.trace('Link insignificant', old_px, token)
            old_px += 1
            self.set_links(self.node, token)
        #
        # Step three: Set links in the significant token.
        token = tokens[px]
        if is_significant_token(token):
            self.set_links(node, token)
        else:
            if trace: g.trace('Skip insignificant', px, token, g.callers())
        #
        # Step four. Advance.
        if is_significant_token(token):
            self.px = px
    #@+node:ekr.20191125120814.1: *6* tog.set_links
    def set_links(self, node, token):
        """Make two-way links between token and the given node."""
        trace = False
        if token.node is not None:  # pragma: no cover
            line_s = f"line {token.line_number}:"
            raise AssignLinksError(
                    f"       file: {self.filename}\n"
                    f"{line_s:>12} {token.line.strip()}\n"
                    f"token index: {self.px}\n"
                    f"token.node is not None\n"
                    f" token.node: {token.node.__class__.__name__}\n"
                    f"    callers: {g.callers()}")
        if (
            is_significant_token(token)
            or token.kind in ('comment', 'newline')
        ):
            if trace:
                g.trace(
                    f"node: {node.__class__.__name__!s:16}"
                    f"token: {token.dump()}")
            # Link the token to the ast node.
            token.node = node
            # Add the token to node's token_list.
            token_list = getattr(node, 'token_list', [])
            node.token_list = token_list + [token]
    #@+node:ekr.20191124083124.1: *5* tog.sync_token helpers
    # It's valid for these to return None.

    def sync_name(self, val):
        aList = val.split('.')
        if len(aList) == 1:
            self.sync_token('name', val)
        else:
            for i, part in enumerate(aList):
                self.sync_token('name', part)
                if i < len(aList) - 1:
                    self.sync_op('.')

    def sync_op(self, val):
        if val not in ',()':
            self.sync_token('op', val)
    #@+node:ekr.20191113081443.1: *5* tog.visitor (calls begin/end_visitor)
    def visitor(self, node):
        """Given an ast node, return a *generator* from its visitor."""
        # This saves a lot of tests.
        trace = False
        if node is None:
            return
        if trace:
            # Keep this trace. It's useful.
            cn = node.__class__.__name__ if node else ' '
            caller1, caller2 = g.callers(2).split(',')
            g.trace(f"{caller1:>15} {caller2:<14} {cn}")
        # More general, more convenient.
        if isinstance(node, (list, tuple)):
            for z in node or []:
                if isinstance(z, ast.AST):
                    yield from self.visitor(z)
                else:
                    # Some fields contain ints or strings.
                    assert isinstance(z, (int, str)), z.__class__.__name__
            return
        # We *do* want to crash if the visitor doesn't exist.
        method = getattr(self, 'do_' + node.__class__.__name__)
        # Allow begin/end visitor to be generators.
        self.begin_visitor(node)
        yield from method(node)
        self.end_visitor(node)
    #@+node:ekr.20191113063144.13: *4* tog: Visitors...
    #@+node:ekr.20191113063144.32: *5*  tog.keyword: not called
    # keyword arguments supplied to call (NULL identifier for **kwargs)

    # keyword = (identifier? arg, expr value)

    def do_keyword(self, node):
        """A keyword arg in an ast.Call."""
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"file: {filename}\n"
            f"do_keyword should never be called")
            
        # if node.arg:
            # yield from self.gen_name(node.arg)
            # yield from self.gen_op('=')
            # yield from self.gen(node.value)
        # else:
            # yield from self.gen_op('**')
            # yield from self.gen(node.value)
    #@+node:ekr.20191113063144.14: *5* tog: Contexts
    #@+node:ekr.20191113063144.28: *6*  tog.arg
    # arg = (identifier arg, expr? annotation)

    def do_arg(self, node):
        """This is one argument of a list of ast.Function or ast.Lambda arguments."""
        yield from self.gen_name(node.arg)
        annotation = getattr(node, 'annotation', None)
        if annotation is not None:
            yield from self.gen_op(':')
            yield from self.gen(node.annotation)
    #@+node:ekr.20191113063144.27: *6*  tog.arguments
    #arguments = (
    #       arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs,
    #       expr* kw_defaults, arg? kwarg, expr* defaults
    #   )

    def do_arguments(self, node):
        
        """Arguments to ast.Function or ast.Lambda, **not** ast.Call."""

        # No need to generate commas anywhere below.
        n_plain = len(node.args) - len(node.defaults)
        # Add the plain arguments.
        i = 0
        while i < n_plain:
            yield from self.gen(node.args[i])
            i += 1
        # Add the arguments with defaults.
        j = 0
        while i < len(node.args) and j < len(node.defaults):
            yield from (self.gen(node.args[i]))
            yield from self.gen_op('=')
            yield from self.gen(node.defaults[j])
            i += 1
            j += 1
        assert i == len(node.args)
        assert j == len(node.defaults)
        # Add the vararg and kwarg expressions.
        vararg = getattr(node, 'vararg', None)
        if vararg is not None:
            yield from self.gen_op('*')
            yield from self.gen(vararg)
        kwarg = getattr(node, 'kwarg', None)
        if kwarg is not None:
            yield from self.gen_op('**')
            yield from self.gen(kwarg)
    #@+node:ekr.20191113063144.15: *6* tog.AsyncFunctionDef
    # AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    #                expr? returns)

    def do_AsyncFunctionDef(self, node):

        if node.decorator_list:
            for z in node.decorator_list:
                # '@%s\n'
                yield from self.gen_op('@')
                yield from self.gen(z)
                yield from self.gen_newline()
        # 'asynch def (%s): -> %s\n'
        # 'asynch def %s(%s):\n'
        yield from self.gen_token('async', 'async')
        yield from self.gen_name('def')
        yield from self.gen_name(node.name) # A string
        yield from self.gen_op('(')
        yield from self.gen(node.args)
        yield from self.gen_op(')')
        yield from self.gen_op(':')
        returns = getattr(node, 'returns', None)
        if returns is not None:
            yield from self.gen_op('->')
            yield from self.gen(node.returns)
        yield from self.gen_newline()
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.16: *6* tog.ClassDef
    def do_ClassDef(self, node, print_body=True):
        
        for z in node.decorator_list or []:
            # @{z}\n
            yield from self.gen_op('@')
            yield from self.gen(z)
            yield from self.gen_newline()
        # class name(bases):\n
        yield from self.gen_name('class')
        yield from self.gen_name(node.name) # A string.
        if node.bases:
            yield from self.gen_op('(')
            yield from self.gen(node.bases)
            yield from self.gen_op(')')
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.17: *6* tog.FunctionDef
    # FunctionDef(
    #   identifier name, arguments args,
    #   stmt* body,
    #   expr* decorator_list,
    #   expr? returns,
    #   string? type_comment)

    def do_FunctionDef(self, node):
        
        # Guards...
        returns = getattr(node, 'returns', None)
        # Decorators...
            # @{z}\n
        for z in node.decorator_list or []:
            yield from self.gen_op('@')
            yield from self.gen(z)
            yield from self.gen_newline()
        # Signature...
            # def name(args): -> returns\n
            # def name(args):\n
        yield from self.gen_name('def')
        yield from self.gen_name(node.name) # A string.
        yield from self.gen_op('(')
        yield from self.gen(node.args)
        yield from self.gen_op(')')
        if returns is not None:
            yield from self.gen_op('->')
            yield from self.gen(node.returns)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.18: *6* tog.Interactive
    def do_Interactive(self, node):  # pragma: no cover
        
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.20: *6* tog.Lambda
    def do_Lambda(self, node):

        yield from self.gen_name('lambda')
        yield from self.gen(node.args)
        yield from self.gen_op(':')
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.19: *6* tog.Module
    def do_Module(self, node):

        # Encoding is a non-syncing statement.
        yield from self.gen_token('encoding', '')
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.21: *5* tog: Expressions
    #@+node:ekr.20191113063144.22: *6* tog.Expr
    def do_Expr(self, node):
        """An outer expression."""
        # No need to put parentheses.
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.23: *6* tog.Expression
    def do_Expression(self, node):  # pragma: no cover
        """An inner expression."""
        # No need to put parentheses.
        yield from self.gen(node.body)
    #@+node:ekr.20191113063144.24: *6* tog.GeneratorExp
    def do_GeneratorExp(self, node):

        # '<gen %s for %s>' % (elt, ','.join(gens))
        # No need to put parentheses or commas.
        yield from self.gen(node.elt)
        yield from self.gen_name('for')
        yield from self.gen(node.generators)
    #@+node:ekr.20191113063144.26: *5* tog: Operands
    #@+node:ekr.20191113063144.29: *6* tog.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self, node):

        yield from self.gen(node.value)
        yield from self.gen_op('.')
        yield from self.gen_name(node.attr) # A string.
    #@+node:ekr.20191113063144.30: *6* tog.Bytes
    def do_Bytes(self, node):
        
        """
        It's invalid to mix bytes and non-bytes literals, so just
        advancing to the next 'string' token suffices.
        """
        token = self.find_next_significant_token()
        yield from self.gen_token('string', token.value)
    #@+node:ekr.20191113063144.31: *6* tog.Call & helpers
    # Call(expr func, expr* args, keyword* keywords)

    # Python 3 ast.Call nodes do not have 'starargs' or 'kwargs' fields.

    def do_Call(self, node):
        
        if False:
            #@+<< trace the ast.Call >>
            #@+node:ekr.20191204105344.1: *7* << trace the ast.Call >>
            dumper = AstDumper()

            def show_fields(node):
                class_name = 'None' if node is None else node.__class__.__name__
                return dumper.show_fields(class_name, node, 80)
                
            def dump(node):
                class_name = node.__class__.__name__
                if node is None:
                    class_name, fields = 'None', ''
                elif isinstance(node, (list, tuple)):
                    fields = ', '.join([show_fields(z) for z in node])
                else:
                    fields = show_fields(node)
                return f"{class_name:>12}: {fields}"
                
            print('\ndo_Call...\n\n'
                f"    func: {dump(node.func)}\n"
                f"    args: {dump(node.args)}\n"
                f"keywords: {dump(node.keywords)}\n")
            #@-<< trace the ast.Call >>
        yield from self.gen(node.func)
        yield from self.gen_op('(')
        # No need to generate any commas.
        yield from self.handle_call_arguments(node)
        yield from self.gen_op(')')
    #@+node:ekr.20191204114930.1: *7* tog.arg_helper
    def arg_helper(self, node):
        """
        Yield the node, with a special case for strings.
        """
        if 0:
            g.trace(AstDumper().show_fields(node.__class__.__name__, node, 40))

        if isinstance(node, str):
            yield from self.gen_token('name', node)
        else:
            yield from self.gen(node)
    #@+node:ekr.20191204105506.1: *7* tog.handle_call_arguments
    def handle_call_arguments(self, node):
        """
        Generate arguments in the correct order.
        
        See https://docs.python.org/3/reference/expressions.html#calls.
        
        This is similar to tog.do_arguments.
        
        At present, this code assumes the standard order:
        
        positional args, then keyword args, then * arg the ** kwargs.
        """
        trace = False
        #
        # Filter the * arg from args.
        args = [z for z in node.args or [] if not isinstance(z, ast.Starred)]
        star_arg = [z for z in node.args or [] if isinstance(z, ast.Starred)]
        #
        # Filter the ** kwarg arg from keywords.
        keywords = [z for z in node.keywords or [] if z.arg]
        kwarg_arg = [z for z in node.keywords or [] if not z.arg]
        if trace:
            #@+<< trace the ast.Call arguments >>
            #@+node:ekr.20191204113843.1: *8* << trace the ast.Call arguments >>
                
            def show_fields(node):
                class_name = 'None' if node is None else node.__class__.__name__
                return AstDumper().show_fields(class_name, node, 40)
                
            # Let block.
            arg_fields = ', '.join([show_fields(z) for z in args])
            keyword_fields = ', '.join([show_fields(z) for z in keywords])
            star_field = show_fields(star_arg[0]) if star_arg else 'None'
            kwarg_field = show_fields(kwarg_arg[0]) if kwarg_arg else 'None'
            # Print.
            print(
                f"\nhandle_call_args...\n\n"
                f"    args: {arg_fields!s}\n"
                f"keywords: {keyword_fields!s}\n"
                f"    star: {star_field!s}\n"
                f"   kwarg: {kwarg_field!s}")
            #@-<< trace the ast.Call arguments >>
            print('')
        #
        # Add the plain arguments.
        for z in args:
            yield from self.arg_helper(z)
        #
        # Add the keyword args.
        for z in keywords:
            yield from self.arg_helper(z.arg)
            yield from self.gen_op('=')
            yield from self.arg_helper(z.value)
        # Add the * arg.
        if star_arg:
            assert len(star_arg) == 1
            star = star_arg[0]
            assert isinstance(star, ast.Starred)
            yield from self.arg_helper(star)
        # Add the kwarg.
        if kwarg_arg:
            assert len(kwarg_arg) == 1
            kwarg = kwarg_arg[0]
            assert isinstance(kwarg, ast.keyword)
            ### yield from self.arg_helper(kwarg)
            yield from self.gen_op('**')
            yield from self.gen(kwarg.value)
    #@+node:ekr.20191113063144.33: *6* tog.comprehension
    # comprehension = (expr target, expr iter, expr* ifs, int is_async)

    def do_comprehension(self, node):

        # No need to put parentheses.
        yield from self.gen(node.target) # A name
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        for z in node.ifs or []:
            yield from self.gen_name('if')
            yield from self.gen(z)
    #@+node:ekr.20191113063144.34: *6* tog.Constant
    def do_Constant(self, node):   # pragma: no cover
        
        # Maybe in later versions of Python.
        # In that case, more testing will be needed.
        assert False, g.callers()
        yield from self.gen_token('number', str(node.s))
    #@+node:ekr.20191113063144.35: *6* tog.Dict
    # Dict(expr* keys, expr* values)

    def do_Dict(self, node):

        assert len(node.keys) == len(node.values)
        yield from self.gen_op('{')
        # No need to put commas.
        for i, key in enumerate(node.keys):
            key, value = node.keys[i], node.values[i]
            yield from self.gen(key) # a Str node.
            yield from self.gen_op(':')
            if value is not None:
                yield from self.gen(value)
        yield from self.gen_op('}')
    #@+node:ekr.20191113063144.36: *6* tog.DictComp
    # DictComp(expr key, expr value, comprehension* generators)

    # d2 = {val: key for key, val in d.iteritems()}

    def do_DictComp(self, node):

        yield from self.gen_token('op', '{')
        yield from self.gen(node.key)
        yield from self.gen_op(':')
        yield from self.gen(node.value)
        for z in node.generators or []:
            yield from self.gen_name('for')
            yield from self.gen(z)
            yield from self.gen_token('op', '}')
    #@+node:ekr.20191113063144.37: *6* tog.Ellipsis
    def do_Ellipsis(self, node):
        
        yield from self.gen_op('...')
    #@+node:ekr.20191113063144.38: *6* tog.ExtSlice
    # https://docs.python.org/3/reference/expressions.html#slicings

    # ExtSlice(slice* dims)

    def do_ExtSlice(self, node):
        
        # ':'.join(node.dims)
        for i, z in enumerate(node.dims):
            yield from self.gen(z)
            if i < len(node.dims) - 1:
                yield from self.gen_op(':')
    #@+node:ekr.20191113063144.40: *6* tog.Index
    def do_Index(self, node):

        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.39: *6* tog.FormattedValue: not called!
    # FormattedValue(expr value, int? conversion, expr? format_spec)

    def do_FormattedValue(self, node):
        """
        This node represents the *components* of a *single* f-string.
        
        Happily, JoinedStr nodes *also* represent *all* f-strings,
        so the TOG should *never visit this node!
        """
        filename = getattr(self, 'filename', '<no file>')
        raise AssignLinksError(
            f"file: {filename}\n"
            f"do_FormattedValue should never be called")

        # This code has no chance of being useful...

            # conv = node.conversion
            # spec = node.format_spec
            # yield from self.gen(node.value)
            # if conv is not None:
                # yield from self.gen_token('number', conv)
            # if spec is not None:
                # yield from self.gen(node.format_spec)
    #@+node:ekr.20191113063144.41: *6* tog.JoinedStr & helpers
    # JoinedStr(expr* values)

    def do_JoinedStr(self, node):
        """
        JoinedStr nodes represent at least one f-string and all other strings
        concatentated to it.
        
        Analyzing JoinedStr.values would be extremely tricky, for reasons that
        need not be explained here.
        
        Instead, we get the tokens *from the token list itself*!
        """
        for z in self.get_concatenated_string_tokens():
            yield from self.gen_token(z.kind, z.value)
    #@+node:ekr.20191113063144.42: *6* tog.List
    def do_List(self, node):

        # No need to put commas.
        yield from self.gen_op('[')
        yield from self.gen(node.elts)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.43: *6* tog.ListComp
    # ListComp(expr elt, comprehension* generators)

    def do_ListComp(self, node):
       
        yield from self.gen_op('[')
        yield from self.gen(node.elt)
        for z in node.generators:
            yield from self.gen_name('for')
            yield from self.gen(z)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.44: *6* tog.Name & NameConstant
    def do_Name(self, node):
        
        yield from self.gen_name(node.id)

    def do_NameConstant(self, node):

        yield from self.gen_name(repr(node.value))
    #@+node:ekr.20191113063144.45: *6* tog.Num
    def do_Num(self, node):
        
        yield from self.gen_token('number', node.n)
    #@+node:ekr.20191113063144.47: *6* tog.Set
    # Set(expr* elts)

    def do_Set(self, node):

        yield from self.gen_op('{')
        yield from self.gen(node.elts)
        yield from self.gen_op('}')
    #@+node:ekr.20191113063144.48: *6* tog.SetComp
    # SetComp(expr elt, comprehension* generators)

    def do_SetComp(self, node):

        yield from self.gen_op('{')
        yield from self.gen(node.elt)
        for z in node.generators or []:
            yield from self.gen_name('for')
            yield from self.gen(z)
        yield from self.gen_op('}')
    #@+node:ekr.20191113063144.49: *6* tog.Slice
    # slice = Slice(expr? lower, expr? upper, expr? step)

    def do_Slice(self, node):

        lower = getattr(node, 'lower', None)
        upper = getattr(node, 'upper', None)
        step = getattr(node, 'step', None)
        if lower is not None:
            yield from self.gen(lower)
        # Always put the colon between upper and lower.
        yield from self.gen_op(':')
        if upper is not None:
            yield from self.gen(upper)
        # Put the second colon if it exists in the token list.
        if step is None:
            token = self.find_next_significant_token()
            if token and token.value == ':':
                yield from self.gen_op(':')
        else:
            yield from self.gen_op(':')
            yield from self.gen(step)
    #@+node:ekr.20191113063144.50: *6* tog.Str & helper
    def do_Str(self, node):
        """This node represents a string constant."""
        # This loop is necessary to handle string concatenation.
        for z in self.get_concatenated_string_tokens():
            yield from self.gen_token(z.kind, z.value)
    #@+node:ekr.20200111083914.1: *7* tog.get_concatenated_tokens (revised)
    def get_concatenated_string_tokens(self):
        """
        Return the next 'string' token and all 'string' tokens concatenated to
        it. *Never* update self.px here.
        """
        trace = False
        tag = 'tog.get_concatenated_string_tokens'
        i = self.px
        if i > -1:
            # self.px should point at a significant token.
            token = self.tokens[i]
            assert is_significant_token(token), (i, token)
        #
        # First, find the next significant token.  It should be a string.
        i, token = i + 1, None
        while i < len(self.tokens):
            token = self.tokens[i]
            i += 1
            if token.kind == 'string':
                # Rescan the string.
                i -= 1
                break
            # Skip over *all* insignificant tokens!
            if is_significant_token(token):
                break
        if not token or token.kind != 'string':  # pragma: no cover
            if not token:
                token = self.tokens[-1]
            filename = getattr(self, 'filename', '<no filename>')
            raise AssignLinksError(
                f"\n"
                f"{tag}...\n"
                f"file: {filename}\n"
                f"line: {token.line_number}\n"
                f"   i: {i}\n"
                f"expected 'string' token, got {token!s}")
        #
        # Accumulate string tokens.
        assert self.tokens[i].kind == 'string'
        results = []
        while i < len(self.tokens):
            token = self.tokens[i]
            i += 1
            if token.kind == 'string':
                results.append(token)
            elif token.kind in ('endmarker', 'name', 'number', 'op'):
                # Note 1: Unlike is_significant_token, *any* op will halt the scan.
                #         This is valid because ')' surely will halt string concatenation.
                #
                # Note 2: The 'endmarker' token ensures we will have a token.
                break
            # 'ws', 'nl', 'newline', 'comment', 'indent', 'dedent', etc.
        if trace:
            g.printObj(results, tag=f"{tag}: Results")
        return results
    #@+node:ekr.20191113063144.51: *6* tog.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self, node):
        
        yield from self.gen(node.value)
        yield from self.gen_op('[')
        yield from self.gen(node.slice)
        yield from self.gen_op(']')
    #@+node:ekr.20191113063144.52: *6* tog.Tuple
    # Tuple(expr* elts, expr_context ctx)

    def do_Tuple(self, node):

        # no need to put commas.
        # The parens are also optional, but they help a tiny bit.
        yield from self.gen_op('(')
        yield from self.gen(node.elts)
        yield from self.gen_op(')')
    #@+node:ekr.20191113063144.53: *5* tog: Operators
    #@+node:ekr.20191113063144.55: *6* tog.BinOp
    def do_BinOp(self, node):

        op_name_ = op_name(node.op)
        yield from self.gen(node.left)
        yield from self.gen_op(op_name_)
        yield from self.gen(node.right)
    #@+node:ekr.20191113063144.56: *6* tog.BoolOp
    # boolop = And | Or

    def do_BoolOp(self, node):
        
        # op.join(node.values)
        op_name_ = op_name(node.op)
        for i, z in enumerate(node.values):
            yield from self.gen(z)
            if i < len(node.values) - 1:
                yield from self.gen_name(op_name_)
    #@+node:ekr.20191113063144.57: *6* tog.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self, node):
        
        assert len(node.ops) == len(node.comparators)
        yield from self.gen(node.left)
        for i, z in enumerate(node.ops):
            op_name_ = op_name(node.ops[i])
            if op_name_ in ('not in', 'is not'):
                for z in op_name_.split(' '):
                    yield from self.gen_name(z)
            elif op_name_.isalpha():
                yield from self.gen_name(op_name_)
            else:
                yield from self.gen_op(op_name_)
            yield from self.gen(node.comparators[i])
    #@+node:ekr.20191113063144.58: *6* tog.UnaryOp
    def do_UnaryOp(self, node):

        op_name_ = op_name(node.op)
        if op_name_.isalpha():
            yield from self.gen_name(op_name_)
        else:
            yield from self.gen_op(op_name_)
        yield from self.gen(node.operand)
    #@+node:ekr.20191113063144.59: *6* tog.IfExp (ternary operator)
    # IfExp(expr test, expr body, expr orelse)

    def do_IfExp(self, node):
        
        #'%s if %s else %s'
        yield from self.gen(node.body)
        yield from self.gen_name('if')
        yield from self.gen(node.test)
        yield from self.gen_name('else')
        yield from self.gen(node.orelse)
    #@+node:ekr.20191113063144.60: *5* tog: Statements
    #@+node:ekr.20191113063144.83: *6*  tog.Starred
    # Starred(expr value, expr_context ctx)

    def do_Starred(self, node):
        
        """A starred argument to an ast.Call"""
        
        # g.trace(f"\n{node.value.__class__.__name__}")
        yield from self.gen_op('*')
        yield from self.gen(node.value)
    #@+node:ekr.20191113063144.61: *6* tog.AnnAssign
    # AnnAssign(expr target, expr annotation, expr? value, int simple)

    def do_AnnAssign(self, node):

        # {node.target}:{node.annotation}={node.value}\n'
        yield from self.gen(node.target)
        yield from self.gen_op(':')
        yield from self.gen(node.annotation)
        yield from self.gen_op('=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.62: *6* tog.Assert
    # Assert(expr test, expr? msg)

    def do_Assert(self, node):
        
        # Guards...
        msg = getattr(node, 'msg', None)
        # No need to put parentheses or commas.
        yield from self.gen_name('assert')
        yield from self.gen(node.test)
        if msg is not None:
            yield from self.gen(node.msg)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.63: *6* tog.Assign
    def do_Assign(self, node):
            
        for z in node.targets:
            yield from self.gen(z)
            yield from self.gen_op('=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.64: *6* tog.AsyncFor
    def do_AsyncFor(self, node):
        
        # The def line...
        yield from self.gen_name('async')
        yield from self.gen_name('for')
        yield from self.gen(node.target)
        yield from self.gen_op(':')
        yield from self.gen(node.iter)
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.65: *6* tog.AsyncWith
    def do_AsyncWith(self, node):
        
        yield from self.gen_name('async')
        yield from self.do_With(node)
    #@+node:ekr.20191113063144.66: *6* tog.AugAssign
    # AugAssign(expr target, operator op, expr value)

    def do_AugAssign(self, node):
        
        # %s%s=%s\n'
        op_name_ = op_name(node.op)
        yield from self.gen(node.target)
        yield from self.gen_op(op_name_+'=')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.67: *6* tog.Await
    # Await(expr value)

    def do_Await(self, node):
        
        #'await %s\n'
        yield from self.gen_token('await', 'await')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.68: *6* tog.Break
    def do_Break(self, node):
        
        yield from self.gen_name('break')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.69: *6* tog.Continue
    def do_Continue(self, node):

        yield from self.gen_name('continue')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.70: *6* tog.Delete
    def do_Delete(self, node):

        # No need to put commas.
        yield from self.gen_name('del')
        yield from self.gen(node.targets)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.71: *6* tog.ExceptHandler
    def do_ExceptHandler(self, node):
        
        # Except line...
        yield from self.gen_name('except')
        if getattr(node, 'type', None):
            yield from self.gen(node.type)
        if getattr(node, 'name', None):
            yield from self.gen_name('as')
            if isinstance(node.name, ast.AST):
                yield from self.gen(node.name)
            else:
                yield from self.gen_name(node.name)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.73: *6* tog.For
    def do_For(self, node):

        # The def line...
        yield from self.gen_name('for')
        yield from self.gen(node.target)
        yield from self.gen_name('in')
        yield from self.gen(node.iter)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.74: *6* tog.Global
    # Global(identifier* names)

    def do_Global(self, node):

        yield from self.gen_name('global')
        for z in node.names:
            yield from self.gen_name(z)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.75: *6* tog.If & helpers
    # If(expr test, stmt* body, stmt* orelse)

    def do_If(self, node):
        #@+<< do_If docstring >>
        #@+node:ekr.20191122222412.1: *7* << do_If docstring >>
        """
        The parse trees for the following are identical!

          if 1:            if 1:
              pass             pass
          else:            elif 2:
              if 2:            pass
                  pass
                  
        So there is *no* way for the 'if' visitor to disambiguate the above two
        cases from the parse tree alone.

        Instead, we scan the tokens list for the next 'if', 'else' or 'elif' token.
        """
        #@-<< do_If docstring >>
        # Use the next significant token to distinguish between 'if' and 'elif'.
        token = self.find_next_significant_token()
        yield from self.gen_name(token.value)
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        #
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
        #
        # Else and elif clauses...
        if node.orelse:
            self.level += 1
            token = self.find_next_significant_token()
            if token.value == 'else':
                yield from self.gen_name('else')
                yield from self.gen_op(':')
                yield from self.gen_newline()
                yield from self.gen(node.orelse)
            else:
                yield from self.gen(node.orelse)
            self.level -= 1
    #@+node:ekr.20191113063144.76: *6* tog.Import & helper
    def do_Import(self, node):
        
        yield from self.gen_name('import')
        for alias in node.names:
            yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.77: *6* tog.ImportFrom
    # ImportFrom(identifier? module, alias* names, int? level)

    def do_ImportFrom(self, node):

        yield from self.gen_name('from')
        for i in range(node.level):
            yield from self.gen_op('.')
        if node.module:
            yield from self.gen_name(node.module)
        yield from self.gen_name('import')
        # No need to put commas.
        for alias in node.names:
            yield from self.gen_name(alias.name)
            if alias.asname:
                yield from self.gen_name('as')
                yield from self.gen_name(alias.asname)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.78: *6* tog.Nonlocal
    # Nonlocal(identifier* names)

    def do_Nonlocal(self, node):
        
        # nonlocal %s\n' % ','.join(node.names))
        # No need to put commas.
        yield from self.gen_name('nonlocal')
        yield from self.gen(node.names)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.79: *6* tog.Pass
    def do_Pass(self, node):
        
        yield from self.gen_name('pass')
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.81: *6* tog.Raise
    # Raise(expr? exc, expr? cause)

    def do_Raise(self, node):
       
        # No need to put commas.
        yield from self.gen_name('raise')
        exc = getattr(node, 'exc', None)
        cause = getattr(node, 'cause', None)
        tback = getattr(node, 'tback', None)
        yield from self.gen(exc)
        yield from self.gen(cause)
        yield from self.gen(tback)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.82: *6* tog.Return
    def do_Return(self, node):
        
        yield from self.gen_name('return')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.85: *6* tog.Try
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self, node):

        # Try line...
        yield from self.gen_name('try')
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        yield from self.gen(node.handlers)
        # Else...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen(node.orelse)
        # Finally...
        if node.finalbody:
            yield from self.gen_name('finally')
            yield from self.gen_op(':')
            yield from self.gen_newline()
            yield from self.gen(node.finalbody)
        self.level -= 1
    #@+node:ekr.20191113063144.88: *6* tog.While
    def do_While(self, node):
        
        # While line...
            # while %s:\n'
        yield from self.gen_name('while')
        yield from self.gen(node.test)
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        # Else clause...
        if node.orelse:
            yield from self.gen_name('else')
            yield from self.gen_op(':')
            yield from self.gen_newline()
            yield from self.gen(node.orelse)
        self.level -= 1
    #@+node:ekr.20191113063144.89: *6* tog.With
    # With(withitem* items, stmt* body)

    # withitem = (expr context_expr, expr? optional_vars)

    def do_With(self, node):
        
        expr = getattr(node, 'context_expression', None)
        items = getattr(node, 'items', [])
        yield from self.gen_name('with')
        yield from self.gen(expr)
        # No need to put commas.
        for item in items:
            yield from self.gen(item.context_expr)
            optional_vars = getattr(item, 'optional_vars', None)
            if optional_vars is not None:
                yield from self.gen_name('as')
                try:
                    for z in item.optional_vars:
                        yield from self.gen(z)
                except TypeError:  # Not iterable.
                    yield from self.gen(item.optional_vars)
        # End the line.
        yield from self.gen_op(':')
        yield from self.gen_newline()
        # Body...
        self.level += 1
        yield from self.gen(node.body)
        self.level -= 1
    #@+node:ekr.20191113063144.90: *6* tog.Yield
    def do_Yield(self, node):

        yield from self.gen_name('yield')
        if hasattr(node, 'value'):
            yield from self.gen(node.value)
        yield from self.gen_newline()
    #@+node:ekr.20191113063144.91: *6* tog.YieldFrom
    # YieldFrom(expr value)

    def do_YieldFrom(self, node):

        yield from self.gen_name('yield')
        yield from self.gen_name('from')
        yield from self.gen(node.value)
        yield from self.gen_newline()
    #@-others
#@+node:ekr.20191226195813.1: *3*  class TokenOrderTraverser
class TokenOrderTraverser:
    """
    Traverse an ast tree using the parent/child links created by the
    TokenOrderInjector class.
    """
    #@+others
    #@+node:ekr.20191226200154.1: *4* TOT.traverse
    def traverse(self, tree):
        """
        Call visit, in token order, for all nodes in tree.
        
        Recursion is not allowed.
        
        The code follows p.moveToThreadNext exactly.
        """
        
        def has_next(i, node, stack):
            """Return True if stack[i] is a valid child of node.parent."""
            # g.trace(node.__class__.__name__, stack)
            parent = node.parent
            return parent and parent.children and i < len(parent.children)
            
        # Update stats
        self.last_node_index = -1  # For visit
        # The stack contains child indices.
        node, stack = tree, [0]
        seen = set()
        while node and stack:
            if False: g.trace(
                f"{node.node_index:>3} "
                f"{node.__class__.__name__:<12} {stack}")
            # Visit the node.
            assert node.node_index not in seen, node.node_index
            seen.add(node.node_index)
            self.visit(node)
            # if p.v.children: p.moveToFirstChild()
            children = getattr(node, 'children', [])
            if children:
                # Move to the first child.
                stack.append(0)
                node = children[0]
                # g.trace(' child:', node.__class__.__name__, stack)
                continue
            # elif p.hasNext(): p.moveToNext()
            stack[-1] += 1
            i = stack[-1]
            if has_next(i, node, stack):
                node = node.parent.children[i]
                continue
            # else...
            # p.moveToParent()
            node = node.parent
            stack.pop()
            # while p:
            while node and stack:
                # if p.hasNext():
                stack[-1] += 1
                i = stack[-1]
                if has_next(i, node, stack):
                    # Move to the next sibling.
                    node = node.parent.children[i]
                    break  # Found.
                # p.moveToParent()
                node = node.parent
                stack.pop()
                # g.trace('parent:', node.__class__.__name__, stack)
            # not found.
            else:
                break
        # g.trace('done', node and node.__class__.__name__, stack)
        return self.last_node_index
    #@+node:ekr.20191227160547.1: *4* TOT.visit
    def visit(self, node):

        self.last_node_index += 1
        assert self.last_node_index == node.node_index, (
            self.last_node_index, node.node_index)
    #@-others
#@+node:ekr.20191222083453.1: *3* class Fstringify (TOT)
class Fstringify (TokenOrderTraverser):
    """A class to fstringify files."""
    #@+others
    #@+node:ekr.20191222083947.1: *4* fs.fstringify
    def fstringify(self, contents, filename, tokens, tree):
        """
        Fstringify.fstringify:
            
        f-stringify the sources given by (tokens, tree).
        
        Return the resulting string.
        """
        self.filename = filename
        self.tokens = tokens
        self.tree = tree
        self.traverse(self.tree)
        results = tokens_to_string(self.tokens)
        return results
    #@+node:ekr.20200103054101.1: *4* fs.fstringify_file (entry)
    def fstringify_file(self, filename):  # pragma: no cover
        """
        Fstringify.fstringify_file.
        
        The entry point for the fstringify-file command.
        
        f-stringify the given external file with the Fstrinfify class.
        
        Return True if the file was changed.
        """
        tag = 'fstringify-file'
        self.filename = filename
        tog = TokenOrderGenerator()
        contents, encoding, tokens, tree = tog.init_from_file(filename)
        if not contents or not tokens or not tree:
            print(f"{tag}: Can not fstringify: {filename}")
            return False
        # fstringify.
        results = self.fstringify(contents, filename, tokens, tree)
        ### results = tokens_to_string(tokens)
        if contents == results:
            print(f"{tag}: Unchanged: {filename}")
            return False
        # Show the diffs.
        show_diffs(contents, results, filename=filename)
        # Write the results
        print(f"{tag}: Wrote {filename}")
        write_file(filename, results, encoding=encoding)
        return True
    #@+node:ekr.20200103065728.1: *4* fs.fstringify_file_diff (entry)
    def fstringify_file_diff(self, filename):  # pragma: no cover
        """
        Fstringify.fstringify_file_diff.
        
        The entry point for the diff-fstringify-file command.
        
        Print the diffs that would resulf from the fstringify-file command.
        
        Return True if the file would be changed.
        """
        tag = 'diff-fstringify-file'
        self.filename = filename
        tog = TokenOrderGenerator()
        contents, encoding, tokens, tree = tog.init_from_file(filename)
        if not contents or not tokens or not tree:
            return False
        # fstringify.
        results = self.fstringify(contents, filename, tokens, tree)
        if contents == results:
            print(f"{tag}: Unchanged: {filename}")
            return False
        # Show the diffs.
        show_diffs(contents, results, filename=filename)
        return True
    #@+node:ekr.20191222095754.1: *4* fs.make_fstring & helpers
    def make_fstring(self, node):
        """
        node is BinOp node representing an '%' operator.
        node.left is an ast.Str node.
        node.right reprsents the RHS of the '%' operator.

        Convert this tree to an f-string, if possible.
        Replace the node's entire tree with a new ast.Str node.
        Replace all the relevant tokens with a single new 'string' token.
        """
        assert isinstance(node.left, ast.Str), (repr(node.left), g.callers())
        # Careful: use the tokens, not Str.s.  This preserves spelling.
        if not hasattr(node.left, 'token_list'):  # pragma: no cover
            print('')
            g.trace('Error: no token list in Str')
            dump_tree(node)
            print('')
            return
                
        lt_s = tokens_to_string(node.left.token_list)
        # Get the RHS values, a list of token lists.
        values = self.scan_rhs(node.right)
        # Compute rt_s, line and line_number for later messages.
        token0 = node.left.token_list[0]
        line_number = token0.line_number
        line = token0.line.strip()
        rt_s = ''.join(tokens_to_string(z) for z in values)
        # Get the % specs in the LHS string.
        specs = self.scan_format_string(lt_s)
        if len(values) != len(specs):  # pragma: no cover
            token_list = getattr(node.left, 'token_list', None)
            token = token_list and token_list[0]
            line_number = token.line_number
            line = token.line
            n_specs, n_values = len(specs), len(values)
            print(
                f"\n"
                f"f-string mismatch: "
                f"{n_values} value{g.plural(n_values)}, "
                f"{n_specs} spec{g.plural(n_specs)}\n"
                f"             file: {self.filename}\n"
                f"      line number: {line_number}\n"
                f"             line: {line.strip()!r}")
            return
        # Replace specs with values.
        results = self.substitute_values(lt_s, specs, values)
        result = self.compute_result(line, line_number, lt_s, results)
        if not result:
            return
        # Remove whitespace before ! and :.
        result = self.clean_ws(result)
        # Show the results
        print(
            f"\n"
            f"       file: {self.filename}\n"
            f"line number: {line_number}\n"
            f"       line: {line!r}\n"
            f"       from: {lt_s} % {rt_s}\n"
            f"         to: {result}")
        # Adjust the tree and the token list.
        self.replace(node, result, values)
    #@+node:ekr.20191222102831.3: *5* fs.clean_ws
    ws_pat = re.compile(r'(\s+)([:!][0-9]\})')

    def clean_ws(self, s):
        """Carefully remove whitespace before ! and : specifiers."""
        s = re.sub(self.ws_pat, r'\2', s)
        return s

    #@+node:ekr.20191222102831.4: *5* fs.compute_result & helpers
    def compute_result(self, line, line_number, lt_s, tokens):
        """
        Create the final result, with various kinds of munges.

        Return the result string, or None if there are errors.
        """
        # Fail if there is a backslash within { and }.
        if not self.check_newlines(tokens):
            return None
        # Ensure consistent quotes.
        if not self.change_quotes(lt_s, tokens):
            print(
                f"\n"
                f"can't create f-fstring: {lt_s!r}\n"
                f"                  file: {self.filename}\n"
                f"           line number: {line_number}\n"
                f"                  line: {line.strip()!r}")
            return None
        return tokens_to_string(tokens)
    #@+node:ekr.20191222102831.2: *6* fs.check_newlines
    def check_newlines(self, tokens):
        """
        Check to ensure that no newlines appear within { and }.
        
        Return False if there is an error
        """
        level = 0
        for token in tokens:
            kind, val = token.kind, token.value
            if kind == 'op':
                if val == '{':
                    level += 1
                elif val == '}':
                    level -= 1
                    if level < 0:  # pragma: no cover
                        print('curly bracket underflow')
                        return False
            if '\\n' in val and level > 0:
                print('f-expression would contain a backslash')
                return False
        if level > 0:  # pragma: no cover
            print('unclosed curly bracket')
            return False
        return True
    #@+node:ekr.20191222102831.7: *6* fs.change_quotes
    def change_quotes(self, lt_s, aList):
        """
        Carefully check quotes in all "inner" tokens as necessary.
        
        Return False if the f-string would contain backslashes.
        
        We expect the following "outer" tokens.
            
        aList[0]:  ('string', 'f')
        aList[1]:  ('string', a string starting with a quote)
        aList[-1]: ('string', a string ending with a quote that matches aList[1])
        """
        trace = False
        # Sanity checks.
        if len(aList) < 4:  # pragma: no cover
            return True
        if not lt_s:  # pragma: no cover
            g.trace('no lt_s!')
            return False
        if trace:
            g.trace(f"lt_s: {lt_s!s}")
            g.printObj(aList, tag='aList')
        delim = lt_s[0]
        # Check tokens 0, 1 and -1.
        token0 = aList[0]
        token1 = aList[1]
        token_last = aList[-1]
        for token in token0, token1, token_last:
            # These are the only kinds of tokens we expect to generate.
            ok = (
                token.kind == 'string' or
                token.kind == 'op' and token.value in '{}')
            if not ok:  # pragma: no cover
                g.trace(
                    f"unexpected token: {token.kind} {token.value}\n"
                    f"            lt_s: {lt_s!r}\n"
                    f"            line: {token0.line!r}")
                g.printObj(aList, tag = 'aList')
                return False
        # These checks are important...
        if token0.value != 'f':  # pragma: no cover
            if trace:
                g.trace('token[0]  error:', repr(token0))
            return False
        val1 = token1.value and token1.value[0]
        if delim != val1:  # pragma: no cover
            if trace:
                g.trace('token[1]  error:', delim, val1, repr(token1))
                g.printObj(aList, tag = 'aList')
            return False
        val_last = token_last.value and token_last.value[-1]
        if delim != val_last:  # pragma: no cover
            if trace:
                g.trace('token[-1] error:', delim, val_last, repr(token_last))
                g.printObj(aList, tag = 'aList')
            return False
        # Return False if any inner token contains the delim or a backslash.
        for z in aList[2:-1]:
            if delim in z.value or '\\' in z.value:
                return False
        return True
    #@+node:ekr.20191222102831.6: *5* fs.munge_spec
    def munge_spec(self, spec):
        """
        Return (head, tail).
        
        The format is spec !head:tail or :tail
        
        Example specs: s2, r3
        """
        ### To do: handle more specs.
        head, tail = [], []
        if spec.startswith('+'):
            pass # Leave it alone!
        elif spec.startswith('-'):
            tail.append('>')
            spec = spec[1:]
        if spec.endswith('s'):
            spec = spec[:-1]
        if spec.endswith('r'):
            head.append('r')
            spec = spec[:-1]
        tail = ''.join(tail) + spec
        head = ''.join(head)
        return head, tail
    #@+node:ekr.20191222102831.9: *5* fs.scan_format_string
    # format_spec ::=  [[fill]align][sign][#][0][width][,][.precision][type]
    # fill        ::=  <any character>
    # align       ::=  "<" | ">" | "=" | "^"
    # sign        ::=  "+" | "-" | " "
    # width       ::=  integer
    # precision   ::=  integer
    # type        ::=  "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g" | "G" | "n" | "o" | "s" | "x" | "X" | "%"

    format_pat = re.compile(r'%(([+-]?[0-9]*(\.)?[0.9]*)*[bcdeEfFgGnoxrsX]?)')

    def scan_format_string(self, s):
        """Scan the format string s, returning a list match objects."""
        result = list(re.finditer(self.format_pat, s))
        return result
    #@+node:ekr.20191222104224.1: *5* fs.scan_rhs
    def scan_rhs(self, node):
        """
        Scan the right-hand side of a potential f-string.
        
        Return a list of the token lists for each element.
        """
        trace = False
        # First, Try the most common cases.
        if isinstance(node, ast.Str):
            return [node.token_list]
        if isinstance(node, (list, tuple, ast.Tuple)):
            result = []
            if isinstance(node, ast.Tuple):
                elts = node.elts
            else:
                elts = [] ### Found by coverage.
            for i, elt in enumerate(elts):
                tokens = tokens_for_node(elt, self.tokens)
                result.append(tokens)
                if trace:
                    g.trace(f"item: {i}: {elt.__class__.__name__}")
                    g.printObj(tokens, tag=f"Tokens for item {i}")
            return result
        
        # Now we expect only one result. 
        tokens = tokens_for_node(node, self.tokens)
        if trace:
            g.trace('One node:', node.__class__.__name__)
            dump_tokens(tokens)
            dump_tree(node)
        return [tokens]
    #@+node:ekr.20191226155316.1: *5* fs.substitute_values
    def substitute_values(self, lt_s, specs, values):
        """
        Replace specifieriers with values in lt_s string.
        
        Double { and } as needed.
        """
        i, results = 0, [Token('string', 'f')]
        for spec_i, m in enumerate(specs):
            value = tokens_to_string(values[spec_i])
            start, end, spec = m.start(0), m.end(0), m.group(1)
            if start > i:
                val = lt_s[i : start].replace('{', '{{').replace('}', '}}')
                results.append(Token('string', val))
            head, tail = self.munge_spec(spec)
            results.append(Token('op', '{'))
            results.append(Token('string', value))
            if head:
                results.append(Token('string', '!'))
                results.append(Token('string', head))
            if tail:
                results.append(Token('string', ':'))
                results.append(Token('string', tail))
            results.append(Token('op', '}'))
            i = end
        # Add the tail.
        tail = lt_s[i:]
        if tail:
            tail = tail.replace('{', '{{').replace('}', '}}')
            results.append(Token('string', tail))
        return results
    #@+node:ekr.20191225054848.1: *4* fs.replace
    def replace(self, node, s, values):
        """
        Replace node with an ast.Str node for s.
        Replace all tokens in the range of values with a single 'string' node.
        """
        # Replace the tokens...
        tokens = tokens_for_node(node, self.tokens)
        i1 = i = tokens[0].index
        replace_token(self.tokens[i], 'string', s)
        j = 1
        while j < len(tokens):
            replace_token(self.tokens[i1 + j], 'killed', '')
            j += 1
        # Replace the node.
        new_node = ast.Str()
        new_node.s = s
        replace_node(new_node, node)
        # Update the token.
        token = self.tokens[i1]
        token.node = new_node
        # Update the token list.
        new_node.token_list = [token]
    #@+node:ekr.20191231055008.1: *4* fs.visit
    def visit(self, node):
        """
        FStringify.visit. (Overrides TOT visit).
        
        Call fs.makes_fstring if node is a BinOp that might be converted to an
        f-string.
        """
        if (
            isinstance(node, ast.BinOp)
            and op_name(node.op) == '%'
            and isinstance(node.left, ast.Str)
        ):
            self.make_fstring(node)
    #@-others
#@+node:ekr.20200107165250.1: *3* class Orange
class Orange:
    """Orange is the new black."""
    #@+others
    #@+node:ekr.20200107165250.2: *4* orange.ctor
    def __init__(self, settings=None):
        """Ctor for Orange class."""
        if settings is None:
            settings = {}
        valid_keys = (
            'delete_blank_lines',
            'max_join_line_length',
            'max_split_line_length',
            'orange',
            'tab_width',
        )
        # Default settings...
        self.delete_blank_lines = True
        self.max_join_line_length = 88
        self.max_split_line_length = 88
        self.orange = False  # Split or join lines only if orange is True.
        self.tab_width = 4
        # Override from settings dict...
        for key in settings:  # pragma: no cover
            value = settings.get(key)
            if key in valid_keys and value is not None:
                setattr(self, key, value)
            else:
                g.trace(f"Unexpected setting: {key} = {value!r}")
    #@+node:ekr.20200107165250.50: *4* orange.find_delims
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
    #@+node:ekr.20200107165250.51: *4* orange.push_state
    def push_state(self, kind, value=None):
        """Append a state to the state stack."""
        state = ParseState(kind, value)
        self.state_stack.append(state)
    #@+node:ekr.20200107165250.8: *4* orange: Entries
    #@+node:ekr.20200107173542.1: *5* orange.beautify
    def oops(self):
        g.trace(f"Unknown kind: {self.kind}")

    def beautify(self, contents, filename, tokens, tree):
        """
        The main line. Create output tokens and return the result as a string.
        """
        # State vars...
        self.curly_brackets_level = 0 # Number of unmatched '{' tokens.
        self.decorator_seen = False  # Set by do_name for do_op.
        self.in_arg_list = 0  # > 0 if in an arg list of a def.
        self.level = 0  # Set only by do_indent and do_dedent.
        self.lws = ''  # Leading whitespace.
        self.paren_level = 0  # Number of unmatched '(' tokens.
        self.square_brackets_level = 0  # Number of unmatched '[' tokens.
        self.state_stack = []  # Stack of ParseState objects.
        self.val = None  # The input token's value (a string).
        #
        # Init output list and state...
        self.code_list = []  # The list of output tokens.
        self.tokens = tokens  # The list of input tokens.
        self.add_token('file-start')
        self.push_state('file-start')
        while self.tokens:
            token = self.tokens.pop(0)
            self.kind, self.val, self.line = token.kind, token.value, token.line
            func = getattr(self, f"do_{token.kind}", self.oops)
            func()
        return tokens_to_string(self.code_list)
    #@+node:ekr.20200107172450.1: *5* orange.beautify_file (entry)
    def beautify_file(self, filename):  # pragma: no cover
        """
        Orange: Beautify the the given external file.
        
        Return True if the file was changed.
        """
        tag = 'orange-file'
        self.filename = filename
        tog = TokenOrderGenerator()
        contents, encoding, tokens, tree = tog.init_from_file(filename)
        if not contents or not tokens or not tree:
            print(f"{tag}: Can not fstringify: {filename}")
            return False
        # Beautify.
        results = self.beautify(contents, filename, tokens, tree)
        if contents == results:
            print(f"{tag}: Unchanged: {filename}")
            return False
        # Show the diffs.
        show_diffs(contents, results, filename=filename)
        # Write the results
        print(f"{tag}: Wrote {filename}")
        write_file(filename, results, encoding=encoding)
        return True
    #@+node:ekr.20200107172512.1: *5* orange.beautify_file_diff (entry)
    def beautify_file_diff(self, filename):  # pragma: no cover
        """
        Orange: Print the diffs that would resulf from the orange-file command.
        
        Return True if the file would be changed.
        """
        tag = 'diff-orange-file'
        self.filename = filename
        tog = TokenOrderGenerator()
        contents, encoding, tokens, tree = tog.init_from_file(filename)
        if not contents or not tokens or not tree:
            return False
        # fstringify.
        results = self.beautify(contents, filename, tokens, tree)
        if contents == results:
            print(f"{tag}: Unchanged: {filename}")
            return False
        # Show the diffs.
        show_diffs(contents, results, filename=filename)
        return True
    #@+node:ekr.20200107165250.13: *4* orange: Input token handlers
    #@+node:ekr.20200107165250.14: *5* orange.do_comment
    def do_comment(self):
        """Handle a comment token."""
        self.clean('blank')
        entire_line = self.line.lstrip().startswith('#')
        if entire_line:
            self.clean('line-indent')
            val = self.line.rstrip()
        else:
            # Exactly two spaces before trailing comments.
            val = '  ' + self.val.rstrip()
        self.add_token('comment', val)
    #@+node:ekr.20200107165250.15: *5* orange.do_encoding
    def do_encoding(self):
        """
        Handle the encoding token.
        """
        pass
    #@+node:ekr.20200107165250.16: *5* orange.do_endmarker
    def do_endmarker(self):
        """Handle an endmarker token."""
        pass
    #@+node:ekr.20200107165250.18: *5* orange.do_indent & do_dedent
    def do_dedent(self):
        """Handle dedent token."""
        self.level -= 1
        self.lws = self.level * self.tab_width * ' '
        self.line_indent()
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
        new_indent = self.val
        old_indent = self.level * self.tab_width * ' '
        if new_indent > old_indent:
            self.level += 1
        elif new_indent < old_indent:  # pragma: no cover
            g.trace('\n===== can not happen', repr(new_indent), repr(old_indent))
        self.lws = new_indent
        self.line_indent()
    #@+node:ekr.20200107165250.20: *5* orange.do_name
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
                self.blank_lines(2 if name == 'class' else 1)
                # self.blank_lines(2 if self.level == 0 else 1)
            self.push_state(name)
            self.push_state('indent', self.level)
                # For trailing lines after inner classes/defs.
            self.word(name)
        elif name in ('and', 'in', 'not', 'not in', 'or', 'for'):
            self.word_op(name)
        else:
            self.word(name)
    #@+node:ekr.20200107165250.21: *5* orange.do_newline & do_nl
    def do_newline(self):
        """Handle a regular newline."""
        # Retain any sidecar ws in the newline.
        self.line_end(self.val)

    def do_nl(self):
        """Handle a continuation line."""
        # Retain any sidecar ws in the newline.
        self.line_end(self.val)
    #@+node:ekr.20200107165250.22: *5* orange.do_number
    def do_number(self):
        """Handle a number token."""
        assert isinstance(self.val, str), repr(self.val)
        self.add_token('number', self.val)
    #@+node:ekr.20200107165250.23: *5* orange.do_op
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
    #@+node:ekr.20200107165250.24: *5* orange.do_string (sets backslash_seen)
    def do_string(self):
        """Handle a 'string' token."""
        self.add_token('string', self.val)
        self.blank()
    #@+node:ekr.20200107165250.25: *5* orange.do_ws
    def do_ws(self):
        """
        Handle the "ws" pseudo-token.
        
        Put the whitespace only if if ends with backslash-newline.
        """
        # Short-circuit if there is no ws to add.
        if not self.val:
            return
        #
        # Handle backslash-newline.
        if '\\\n' in self.val:
            # Prepend a *real* blank, so later code won't add any more ws.
            self.clean('blank')
            self.add_token('blank', ' ')
            self.add_token('ws', self.val.lstrip())
            if self.val.endswith((' ', '\t')):
                # Add a *empty* blank, so later code won't add any more ws.
                self.add_token('blank', '')
            return
        #
        # Handle start-of-line whitespace.
        prev = self.code_list[-1]
        inner = self.paren_level or self.square_brackets_level or self.curly_brackets_level
        if prev.kind == 'line-indent' and inner:
            # Retain the indent that won't be cleaned away.
            self.clean('line-indent')
            self.add_token('hard-blank', self.val)
    #@+node:ekr.20200107165250.26: *4* orange: Output token generators
    #@+node:ekr.20200107170523.1: *5* orange.add_token
    def add_token(self, kind, value=''):
        """Add an output token to the code list."""
        tok = Token(kind, value)
        self.code_list.append(tok)
        self.prev_output_token = self.code_list[-1]
    #@+node:ekr.20200107165250.27: *5* orange.blank
    def blank(self):
        """Add a blank request to the code list."""
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank',
            'blank-lines',
            'file-start',
            'hard-blank', # Unique to orange.
            'line-end',
            'line-indent',
            'lt',
            'op-no-blanks',
            'unary-op',
        ):
            self.add_token('blank', ' ')
    #@+node:ekr.20200107165250.28: *5* orange.blank_before_end_line_comment
    def blank_before_end_line_comment(self):
        """Add two blanks before an end-of-line comment."""
        prev = self.code_list[-1]
        self.clean('blank')
        if prev.kind not in ('blank-lines', 'file-start', 'line-end', 'line-indent'):
            self.add_token('blank', ' ')
            self.add_token('blank', ' ')
    #@+node:ekr.20200107165250.29: *5* orange.blank_lines
    def blank_lines(self, n):
        """
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        """
        self.clean_blank_lines()
        prev = self.code_list[-1]
        if prev.kind == 'file-start':
            self.add_token('blank-lines', n)
            return
        # Special case for Leo comments that start a node.
        if prev.kind == 'comment' and prev.value.startswith('#@+node:'):
            n = 0
        for i in range(0, n+1):
            self.add_token('line-end', '\n')
        # Retain the token (intention) for debugging.
        self.add_token('blank-lines', n)
        self.line_indent()
    #@+node:ekr.20200107165250.30: *5* orange.clean
    def clean(self, kind):
        """Remove the last item of token list if it has the given kind."""
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20200107165250.31: *5* orange.clean_blank_lines
    def clean_blank_lines(self):
        """Remove all vestiges of previous lines."""
        table = ('blank-lines', 'line-end', 'line-indent')
        while self.code_list[-1].kind in table:
            self.code_list.pop()
    #@+node:ekr.20200107165250.32: *5* orange.colon
    def colon(self, val):
        """Handle a colon."""
        if self.square_brackets_level > 0:
            # Put blanks on either side of the colon,
            # but not between commas, and not next to [.
            self.clean('blank')
            prev = self.code_list[-1]
            if prev.value == '[':
                # Never put a blank after "[:"
                self.add_token('op', val)
            elif prev.value == ':':
                self.add_token('op', val)
                self.blank()
            else:
                self.op(val)
        else:
            self.op_blank(val)
    #@+node:ekr.20200107165250.6: *5* orange.file_end
    def file_end(self):
        """
        Add a file-end token to the code list.
        Retain exactly one line-end token.
        """
        self.clean_blank_lines()
        self.add_token('line-end', '\n')
        self.add_token('line-end', '\n')
        self.add_token('file-end')
    #@+node:ekr.20200107165250.33: *5* orange.line_end & split/join helpers
    def line_end(self, ws=''):
        """Add a line-end request to the code list."""
        prev = self.code_list[-1]
        if prev.kind == 'file-start':
            return
        self.clean('blank')  # Important!
        if self.delete_blank_lines:
            self.clean_blank_lines()
        self.clean('line-indent')
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
    #@+node:ekr.20200107165250.34: *6* orange.break_line (new) & helpers
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
        tail = line_tokens[len(prefix):]
        if prefix[0].kind == 'line-indent':
            prefix = prefix[1:]
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
    #@+node:ekr.20200107165250.35: *7* orange.append_tail
    def append_tail(self, prefix, tail):
        """Append the tail tokens, splitting the line further as necessary."""
        g.trace('='*20)
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
        open_delim = Token(kind='lt', value=prefix[-1].value)
        close_delim = Token(
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
                    self.code_list.extend(tail[i:])
                    return
                lws = lws[:-4]
                self.code_list.append(t)
            elif t.kind == open_delim.kind and t.value == open_delim.value:
                delim_count += 1
                lws = lws + ' ' * 4
                self.code_list.append(t)
            else:
                self.code_list.append(t)
        g.trace('BAD DELIMS', delim_count)
    #@+node:ekr.20200107165250.36: *7* orange.find_prev_line (new)
    def find_prev_line(self):
        """Return the previous line, as a list of tokens."""
        line = []
        for t in reversed(self.code_list[:-1]):
            if t.kind == 'line-end':
                break
            line.append(t)
        return list(reversed(line))
    #@+node:ekr.20200107165250.37: *7* orange.find_line_prefix (new)
    def find_line_prefix(self, token_list):
        """
        Return all tokens up to and including the first lt token.
        Also add all lt tokens directly following the first lt token.
        """
        result = []
        for i, t in enumerate(token_list):
            result.append(t)
            if t.kind == 'lt':
                for t in token_list[i + 1:]:
                    if t.kind == 'blank' or self.is_any_lt(t):
                    # if t.kind in ('lt', 'blank'):
                        result.append(t)
                    else:
                        break
                break
        return result
    #@+node:ekr.20200107165250.38: *7* orange.is_any_lt
    def is_any_lt(self, output_token):
        """Return True if the given token is any lt token"""
        return (
            output_token == 'lt'
            or output_token.kind == 'op-no-blanks'
            and output_token.value in "{[("
        )
    #@+node:ekr.20200107165250.39: *6* orange.join_lines (new) & helpers
    def join_lines(self):
        """
        Join preceding lines, if the result would be short enough.
        Should be called only at the end of a line.
        """
        # Must be called just after inserting the line-end token.
        trace = False
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
    #@+node:ekr.20200107165250.40: *5* orange.line_indent
    def line_indent(self):
        """Add a line-indent token."""
        self.clean('line-indent')
            # Defensive. Should never happen.
        self.add_token('line-indent', self.lws)
    #@+node:ekr.20200107165250.41: *5* orange.lt & rt
    #@+node:ekr.20200107165250.42: *6* orange.lt
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
    #@+node:ekr.20200107165250.43: *6* orange.rt
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
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind == 'arg-end' or (prev.kind, prev.value) == ('op', ':'):
            # # Remove a blank token preceding the arg-end or ')' token.
            prev = self.code_list.pop()
            self.clean('blank')
            self.code_list.append(prev)
        self.add_token('rt', s)
    #@+node:ekr.20200107165250.44: *5* orange.op*
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
    #@+node:ekr.20200107165250.45: *5* orange.possible_unary_op & unary_op
    def possible_unary_op(self, s):
        """Add a unary or binary op to the token list."""
        self.clean('blank')
        prev = self.code_list[-1]
        if prev.kind in ('lt', 'op', 'op-no-blanks', 'word-op'):
            self.unary_op(s)
        elif prev.kind == 'word' and prev.value in (
            'elif', 'else', 'if', 'return', 'while',
        ):
            self.unary_op(s)
        else:
            self.op(s)

    def unary_op(self, s):
        """Add an operator request to the code list."""
        assert s and isinstance(s, str), repr(s)
        self.clean('blank')
        prev = self.code_list[-1]
        prev2 = self.code_list[-2]
        if prev.kind == 'lt':
            self.add_token('unary-op', s)
            return
        if prev2.kind == 'lt' and (prev.kind, prev.value) == ('op', ':'):
            self.add_token('unary-op', s)
            return
        self.blank()
        self.add_token('unary-op', s)
    #@+node:ekr.20200107165250.46: *5* orange.star_op
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
    #@+node:ekr.20200107165250.47: *5* orange.star_star_op
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
    #@+node:ekr.20200107165250.48: *5* orange.word & word_op
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
    #@-others
#@+node:ekr.20200107170847.1: *3* class OrangeSettings
class OrangeSettings:
    
    pass
#@+node:ekr.20200107170126.1: *3* class ParseState
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
#@+node:ekr.20191231084514.1: *3* class ReassignTokens (TOT)
class ReassignTokens (TokenOrderTraverser):
    
    """A class that reassigns tokens to more appropriate ast nodes."""
    
    #@+others
    #@+node:ekr.20191231084640.1: *4* reassign.reassign
    def reassign(self, tokens, tree):
        """The main entry point."""
        self.tokens = tokens
        self.tree = tree
        # For now, only one pass is needed.
        # self.pass_n = 1
        self.traverse(tree)
    #@+node:ekr.20191231084853.1: *4* reassign.visit
    def visit(self, node):
        """ReassignTokens.visit"""
        # For now, just handle call nodes.
        if not isinstance(node, ast.Call):
            return
        tokens = tokens_for_node(node, self.tokens)
        node0, node9 = tokens[0].node, tokens[-1].node
        nca = nearest_common_ancestor(node0, node9)
        if not nca:
            # g.trace(f"no nca: {tokens_to_string(tokens)}")
            return
        if node.args:
            pass
            # arg0, arg9 = node.args[0], node.args[-1]
            # g.trace(arg0.node_index, arg9.node_index)
        else:
            # Associate () with the call node.
            i = tokens[-1].index
            j = find_paren_token(i + 1, self.tokens)
            if j is None: return
            k = find_paren_token(j + 1, self.tokens)
            if k is None: return
            self.tokens[j].node = nca
            self.tokens[k].node = nca
            add_token_to_token_list(self.tokens[j], nca)
            add_token_to_token_list(self.tokens[k], nca)
    #@-others
#@+node:ekr.20191227170803.1: ** Token classes
#@+node:ekr.20191110080535.1: *3* class Token
class Token:
    """
    A class representing a 5-tuple, plus additional data.

    The TokenOrderTraverser class creates a list of such tokens.
    """

    def __init__(self, kind, value):
        
        self.kind = kind
        self.value = value
        #
        # Injected by Tokenizer.add_token.
        self.five_tuple = None
        self.index = 0
        self.line = ''
            # The entire line containing the token.
            # Same as five_tuple.line.
        self.line_number = 0
            # The line number, for errors and dumps.
            # Same as five_tuple.start[0]
        #
        # Injected by Linker class.
        self.level = 0
        self.node = None

    def __repr__(self):
        s = f"{self.kind:}.{self.index:<3}"
        return f"{s:>15} {self.show_val(80)}"

    def __str__(self):
        return f"{self.kind}.{self.index:<3} {self.show_val(80)}"

    def to_string(self):
        """Return the contribution of the token to the source file."""
        return self.value if isinstance(self.value, str) else ''
        
    #@+others
    #@+node:ekr.20191231114927.1: *4* token.brief_dump
    def brief_dump(self):  # pragma: no cover
        """Dump a token."""
        return (
            f"{self.index:>3} line: {self.line_number:<2} "
            f"{self.kind:>11} {self.show_val(100)}")
    #@+node:ekr.20191113095410.1: *4* token.dump
    def dump(self):  # pragma: no cover
        """Dump a token and related links."""
        # Let block.
        node_id = self.node.node_index if self.node else ''
        node_cn = self.node.__class__.__name__ if self.node else ''
        parent = getattr(self.node, 'parent', None)
        parent_class = parent.__class__.__name__ if parent else ''
        parent_id = parent.node_index if parent else ''
        kind_s = f"{self.kind}.{self.index:<3}"
        return (
            f"{kind_s:>15} {self.show_val(20):<24} "
            f"line: {self.line_number:<2} "
            f"{node_id:4} {node_cn:16} "
            f"parent: {parent_id:>4} {parent_class}")
    #@+node:ekr.20191116154328.1: *4* token.error_dump
    def error_dump(self):  # pragma: no cover
        """Dump a token or result node for error message."""
        if self.node:
            node_id = obj_id(self.node)
            node_s = f"{node_id} {self.node.__class__.__name__}"
        else:
            node_s = "None"
        return(
            f"index: {self.index:<3} {self.kind:>12} {self.show_val(20):<20} "
            f"{node_s}")
    #@+node:ekr.20191113095507.1: *4* token.show_val
    def show_val(self, truncate_n):  # pragma: no cover
        """Return the token.value field."""
        if self.kind in ('ws', 'indent'):
            val = len(self.value)
        elif self.kind == 'string':
            # Important: don't add a repr for 'string' tokens.
            # repr just adds another layer of confusion.
            val = g.truncate(self.value, truncate_n)
        else:
            val = g.truncate(repr(self.value), truncate_n)
        return val
    #@-others
#@+node:ekr.20191110165235.1: *3* class Tokenizer
class Tokenizer:
    
    """Create a list of Tokens from contents."""
    
    #@+others
    #@+node:ekr.20191110165235.2: *4* tokenizer.add_token
    token_index = 0

    def add_token(self, kind, five_tuple, line, s_row, value):
        """
        Add a token to the results list.
        
        Subclasses could override this method to filter out specific tokens.
        """
        tok = Token(kind, value)
        tok.five_tuple = five_tuple
        tok.index = self.token_index
        self.token_index += 1
        tok.line = line
        tok.line_number = s_row
        self.results.append(tok)
    #@+node:ekr.20191110170551.1: *4* tokenizer.check_results
    def check_results(self, contents):

        # Split the results into lines.
        result = ''.join([z.to_string() for z in self.results])
        result_lines = g.splitLines(result)
        # Check.
        ok = result == contents and result_lines == self.lines
        assert ok, (
            f"\n"
            f"      result: {result!r}\n"
            f"    contents: {contents!r}\n"
            f"result_lines: {result_lines}\n"
            f"       lines: {self.lines}"
        )
    #@+node:ekr.20191110165235.3: *4* tokenizer.create_input_tokens
    def create_input_tokens(self, contents, tokens):
        """
        Generate a list of Token's from tokens, a list of 5-tuples.
        """
        # Create the physical lines.
        self.lines = contents.splitlines(True)
        # Create the list of character offsets of the start of each physical line.
        last_offset, self.offsets = 0, [0]
        for line in self.lines:
            last_offset += len(line)
            self.offsets.append(last_offset)
        # Handle each token, appending tokens and between-token whitespace to results.
        self.prev_offset, self.results = -1, []
        for token in tokens:
            self.do_token(contents, token)
        # Print results when tracing.
        self.check_results(contents)
        # Return results, as a list.
        return self.results
    #@+node:ekr.20191110165235.4: *4* tokenizer.do_token (the gem)
    header_has_been_shown = False

    def do_token(self, contents, five_tuple):
        """
        Handle the given token, optionally including between-token whitespace.
        
        This is part of the "gem".
        """
        import token as token_module
        # Unpack..
        tok_type, val, start, end, line = five_tuple
        s_row, s_col = start  # row/col offsets of start of token.
        e_row, e_col = end    # row/col offsets of end of token.
        kind = token_module.tok_name[tok_type].lower()
        # Calculate the token's start/end offsets: character offsets into contents.
        s_offset = self.offsets[max(0, s_row-1)] + s_col
        e_offset = self.offsets[max(0, e_row-1)] + e_col
        # tok_s is corresponding string in the line.
        tok_s = contents[s_offset : e_offset]
        # Add any preceding between-token whitespace.
        ws = contents[self.prev_offset : s_offset]
        if ws:
            # No need for a hook.
            self.add_token('ws', five_tuple, line, s_row, ws)
        # Always add token, even if it contributes no text!
        self.add_token(kind, five_tuple, line, s_row, tok_s)
        # Update the ending offset.
        self.prev_offset = e_offset
    #@-others
#@-others
g = LeoGlobals()
if __name__ == '__main__':
    unittest.main()
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
