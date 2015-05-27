#@+leo-ver=5-thin
#@+node:ekr.20150521115018.1: * @file leoBeautify.py
'''Leo's beautification classes.'''

import leo.core.leoGlobals as g
import leo.core.leoAst as leoAst
import leo.external.PythonTidy as tidy
import ast
import glob
import os
import time
import token
import tokenize

#@+others
#@+node:ekr.20110917174948.6903: ** class CPrettyPrinter
class CPrettyPrinter:

    #@+others
    #@+node:ekr.20110917174948.6904: *3* __init__ (CPrettyPrinter)
    def __init__ (self,c):
        '''Ctor for CPrettyPrinter class.'''
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
    #@+node:ekr.20110917174948.6911: *3* indent & helpers
    def indent (self,p,toList=False,giveWarnings=True):

        # c = self.c
        if not p.b: return
        self.p = p.copy()

        aList = self.tokenize(p.b)
        assert ''.join(aList) == p.b

        aList = self.add_statement_braces(aList,giveWarnings=giveWarnings)

        self.bracketLevel = 0
        self.parens = 0
        self.result = []
        for s in aList:
            # g.trace(repr(s))
            self.put_token(s)

        if 0:
            for z in self.result:
                print(repr(z))

        if toList:
            return self.result
        else:
            return ''.join(self.result)
    #@+node:ekr.20110918225821.6815: *4* add_statement_braces
    def add_statement_braces (self,s,giveWarnings=False):

        p = self.p
        trace = False

        def oops(message,i,j):
            # This can be called from c-to-python, in which case warnings should be suppressed.
            if giveWarnings:
                g.error('** changed ',p.h)
                g.es_print('%s after\n%s' % (
                    message,repr(''.join(s[i:j]))))

        i,n,result = 0,len(s),[]
        while i < n:
            token_ = s[i] # token is a module.
            progress = i
            if token_ in ('if','for','while',):
                j = self.skip_ws_and_comments(s,i+1)
                if self.match(s,j,'('):
                    j = self.skip_parens(s,j)
                    if self.match(s,j,')'):
                        old_j = j+1
                        j = self.skip_ws_and_comments(s,j+1)
                        if self.match(s,j,';'):
                            # Example: while (*++prefix);
                            result.extend(s[i:j])
                        elif self.match(s,j,'{'):
                            result.extend(s[i:j])
                        else:
                            oops("insert '{'",i,j)
                            # Back up, and don't go past a newline or comment.
                            j = self.skip_ws(s,old_j)
                            result.extend(s[i:j])
                            result.append(' ')
                            result.append('{')
                            result.append('\n')
                            i = j
                            j = self.skip_statement(s,i)
                            result.extend(s[i:j])
                            result.append('\n')
                            result.append('}')
                            oops("insert '}'",i,j)
                    else:
                        oops("missing ')'",i,j)
                        result.extend(s[i:j])
                else:
                    oops("missing '('",i,j)
                    result.extend(s[i:j])
                i = j
            else:
                result.append(token_)
                i += 1
            assert progress < i

        if trace: g.trace(''.join(result))
        return result

    #@+node:ekr.20110919184022.6903: *5* skip_ws
    def skip_ws (self,s,i):

        while i < len(s):
            token_ = s[i] # token is a module.
            if token_.startswith(' ') or token_.startswith('\t'):
                i += 1
            else:
                break

        return i
    #@+node:ekr.20110918225821.6820: *5* skip_ws_and_comments
    def skip_ws_and_comments (self,s,i):

        while i < len(s):
            token_ = s[i] # token is a module.
            if token_.isspace():
                i += 1
            elif token_.startswith('//') or token_.startswith('/*'):
                i += 1
            else:
                break

        return i
    #@+node:ekr.20110918225821.6817: *5* skip_parens
    def skip_parens(self,s,i):

        '''Skips from the opening ( to the matching ).

        If no matching is found i is set to len(s)'''

        assert(self.match(s,i,'('))

        level = 0
        while i < len(s):
            ch = s[i]
            if ch == '(':
                level += 1 ; i += 1
            elif ch == ')':
                level -= 1
                if level <= 0:  return i
                i += 1
            else: i += 1
        return i
    #@+node:ekr.20110918225821.6818: *5* skip_statement
    def skip_statement (self,s,i):

        '''Skip to the next ';' or '}' token.'''

        while i < len(s):
            if s[i] in ';}':
                i += 1
                break
            else:
                i += 1
        return i
    #@+node:ekr.20110917204542.6967: *4* put_token & helpers
    def put_token (self,s):

        '''Append token s to self.result as is,
        *except* for adjusting leading whitespace and comments.

        '{' tokens bump self.brackets or self.ignored_brackets.
        self.brackets determines leading whitespace.
        '''

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
            else: pass # Use the existing indentation.
        elif s.isspace():
            if self.parens <= 0 and self.result and self.result[-1].startswith('\n'):
                # Kill the whitespace.
                s = ''
            else: pass # Keep the whitespace.
        elif s.startswith('/*'):
            s = self.reformat_block_comment(s)
        else:
            pass # put s as it is.

        if s:
            self.result.append(s)

    #@+at
    #     # It doesn't hurt to increase indentation after *all* '{'.
    #     if s == '{':
    #         # Increase brackets unless '=' precedes it.
    #         if self.prev_token('='):
    #             self.ignored_brackets += 1
    #         else:
    #             self.brackets += 1
    #     elif s == '}':
    #         if self.ignored_brackets:
    #             self.ignored_brackets -= 1
    #         else:
    #             self.brackets -= 1
    #             self.remove_indent()
    #@+node:ekr.20110917204542.6968: *5* prev_token
    def prev_token (self,s):

        '''Return the previous token, ignoring whitespace and comments.'''

        i = len(self.result)-1
        while i >= 0:
            s2 = self.result[i]
            if s == s2:
                return True
            elif s.isspace() or s.startswith('//') or s.startswith ('/*'):
                i -= 1
            else:
                return False
    #@+node:ekr.20110918184425.6916: *5* reformat_block_comment
    def reformat_block_comment (self,s):

        return s
    #@+node:ekr.20110917204542.6969: *5* remove_indent
    def remove_indent (self):

        '''Remove one tab-width of blanks from the previous token.'''

        w = abs(self.tab_width)

        if self.result:
            s = self.result[-1]
            if s.isspace():
                self.result.pop()
                s = s.replace('\t',' ' * w)
                if s.startswith('\n'):
                    s2 = s[1:]
                    self.result.append('\n'+s2[:-w])
                else:
                    self.result.append(s[:-w])
    #@+node:ekr.20110918225821.6819: *3* match
    def match(self,s,i,pat):

        return i < len(s) and s[i] == pat
    #@+node:ekr.20110917174948.6930: *3* tokenize & helper
    def tokenize (self,s):

        '''Tokenize comments, strings, identifiers, whitespace and operators.'''

        i,result = 0,[]
        while i < len(s):
            # Loop invariant: at end: j > i and s[i:j] is the new token.
            j = i
            ch = s[i]
            if ch in '@\n': # Make *sure* these are separate tokens.
                j += 1
            elif ch == '#': # Preprocessor directive.
                j = g.skip_to_end_of_line(s,i)
            elif ch in ' \t':
                j = g.skip_ws(s,i)
            elif ch.isalpha() or ch == '_':
                j = g.skip_c_id(s,i)
            elif g.match(s,i,'//'):
                j = g.skip_line(s,i)
            elif g.match(s,i,'/*'):
                j = self.skip_block_comment(s,i)
            elif ch in "'\"":
                j = g.skip_string(s,i)
            else:
                j += 1

            assert j > i
            result.append(''.join(s[i:j]))
            i = j # Advance.

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
    #@+node:ekr.20110917193725.6974: *4* skip_block_comment
    def skip_block_comment (self,s,i):

        assert(g.match(s,i,"/*"))

        j = s.find("*/",i)
        if j == -1:
            return len(s)
        else:
            return j + 2
    #@-others
#@+node:ekr.20150520173107.1: ** class LeoTidy (Uses PythonTidy)
class LeoTidy:
    '''A class to beautify source code from an AST'''
    
    def __init__(self,c,options_d=None):
        '''Ctor for the LeoTidy class.'''
        self.c = c
        self.code_list = []
        self.in_arg_list = False
        self.indent = ' ' * 4
        self.level = 0
        self.tab_width = 4
    
    #@+others
    #@+node:ekr.20150527171440.1: *3* class OutputToken
    class OutputToken:
        '''A class representing items on the code list.'''
        
        def __init__(self,kind,lws,value):
            self.kind = kind
            self.lws = lws
            self.value = value
            
        def __repr__(self):
            return '%15s %-2s %s' % (self.kind,show_lws(self.lws),repr(self.value))
       
        __str__ = __repr__

        def to_string(self):
            '''Convert an output token to a string.'''
            return self.value if g.isString(self.value) else ''
    #@+node:ekr.20150523083023.1: *3* lt.Code Generators
    #@+node:ekr.20150523131619.1: *4* lt.add_token
    def add_token(self,kind,value=''):
        '''Add a token to the code list.'''
        tok = self.OutputToken(kind,self.level,value)
        self.code_list.append(tok)
    #@+node:ekr.20150526052853.1: *4* lt.arg_start & arg_end
    def arg_end(self):
        '''Add a token indicating the end of an argument list.'''
        self.add_token('arg-end','')
        
    def arg_start(self):
        '''Add a token indicating the start of an argument list.'''
        self.add_token('arg-start','')
    #@+node:ekr.20150523083639.1: *4* lt.blank
    def blank(self):
        '''Add a blank request on the code list.'''
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank','blank-lines',
                # Suppress duplicates.
            'file-start','line-start','line-end',
                # These tokens implicitly suppress blanks.
            'arg-start','lit-no-blanks','lt',
                # These tokens explicity suppress blanks.
        ):
            self.add_token('blank',' ')
    #@+node:ekr.20150523084306.1: *4* lt.blank_lines
    def blank_lines(self,n):
        '''
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        '''
        # Count the number of 'consecutive' end-line tokens, ignoring blank-lines tokens.
        prev_lines = 0
        i = len(self.code_list)-1 # start-file token guarantees i >= 0
        while True:
            kind = self.code_list[i].kind
            if kind == 'file-start':
                prev_lines = n ; break
            elif kind == 'blank-lines':
                i -= 1
            elif kind == 'line-end':
                i -= 1 ; prev_lines += 1
            else: break
        # g.trace('i: %3s n: %s prev: %s' % (len(self.code_list),n,prev_lines))
        while prev_lines <= n:
            self.line_end()
            prev_lines += 1
        # Retain the intention for debugging.
        self.add_token('blank-lines',n)
    #@+node:ekr.20150524075023.1: *4* clean
    def clean(self,kind):
        '''Remove the last item of token list if it has the given kind.'''
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20150523085208.1: *4* lt.conditional_line_start
    def conditional_line_start(self):
        '''Add a conditional line start to the code list.'''
        prev = self.code_list[-1]
        if prev.kind != 'start-line':
            self.add_token('start-line')
    #@+node:ekr.20150523131526.1: *4* lt.file_start & file_end
    def file_end(self):
        '''
        Add a file-end token to the code list.
        Retain exactly one line-end token.
        '''
        while True:
            prev = self.code_list[-1]
            if prev.kind in ('blank-lines','line-end'):
                self.code_list.pop()
            else:
                break
        self.add_token('line-end')
        self.add_token('file-end')

    def file_start(self):
        '''Add a file-start token to the code list.'''
        self.add_token('file-start')
    #@+node:ekr.20150523084222.1: *4* lt.line_start & line_end
    def line_end(self):
        '''Add a line-end request to the code list.'''
        prev = self.code_list[-1]
        if prev.kind != 'file-start':
            self.add_token('line-end','\n')

    def line_start(self):
        '''Add a line-start request to the code list.'''
        prev = self.code_list[-1]
        if prev.kind != 'line-start':
            self.add_token('line-start',self.indent*self.level)
    #@+node:ekr.20150523083627.1: *4* lt.lit*
    def lit(self,s):
        '''Add a request for a literal to the code list.'''
        assert s and g.isString(s),repr(s)
        # g.trace(repr(s),g.callers())
        self.add_token('lit',s)
        
    def lit_blank(self,s):
        '''Add request for a liter (no previous blank) followed by a blank.'''
        self.clean('blank')
        self.lit(s)
        self.blank()

    def lit_no_blanks(self,s):
        '''Add a request for a literal *not* surrounded by blanks.'''
        self.clean('blank')
        self.add_token('lit-no-blanks',s)
    #@+node:ekr.20150523083651.1: *4* lt.lt & rt
    def lt(self,s):
        '''Add a left paren request to the code list.'''
        assert s in '([{',repr(s)
        self.add_token('lt',s)
        
    def rt(self,s):
        '''Add a right paren request to the code list.'''
        assert s in ')]}',repr(s)
        prev = self.code_list[-1]
        if prev.kind == 'arg-end':
            # Remove a blank token preceding the arg-end token.
            prev = self.code_list.pop()
            self.clean('blank')
            self.code_list.append(prev)   
        else:
            self.clean('blank')
        self.add_token('rt',s)
    #@+node:ekr.20150522212520.1: *4* lt.op
    def op(self,s):
        '''Add an operator request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.lit(s)
        self.blank()
    #@+node:ekr.20150523083952.1: *4* lt.word
    def word(self,s):
        '''Add a word request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.add_token('word',s)
        self.blank()
    #@+node:ekr.20150520173107.2: *3* lt.Entries
    #@+node:ekr.20150520173107.4: *4* lt.format
    def format (self,node):
        '''Format the node (or list of nodes) and its descendants.'''
        self.level = 0
        self.file_start()
        val = self.visit(node)
        self.file_end()
        return ''.join([z.to_string() for z in self.code_list])
    #@+node:ekr.20150520173107.5: *4* lt.visit
    def visit(self,node):
        '''Return the formatted version of an Ast node, or list of Ast nodes.'''
        trace = False and not g.unitTesting
        assert isinstance(node,ast.AST),node.__class__.__name__
        method_name = 'do_' + node.__class__.__name__
        method = getattr(self,method_name)
        if trace: g.trace(method_name)
        method(node)
    #@+node:ekr.20150520173107.69: *3* lt.Utils
    #@+node:ekr.20150520173107.70: *4* lt.kind
    def kind(self,node):
        '''Return the name of node's class.'''
        return node.__class__.__name__
    #@+node:ekr.20150520173107.72: *4* lt.op_name
    def op_name (self,node,strict=True):
        '''Return the print name of an operator node.'''
        d = {
        # Binary operators. 
        'Add':       '+',
        'BitAnd':    '&',
        'BitOr':     '|',
        'BitXor':    '^',
        'Div':       '/',
        'FloorDiv':  '//',
        'LShift':    '<<',
        'Mod':       '%',
        'Mult':      '*',
        'Pow':       '**',
        'RShift':    '>>',
        'Sub':       '-',
        # Boolean operators.
        'And':   'and',
        'Or':    'or',
        # Comparison operators
        'Eq':    '==',
        'Gt':    '>',
        'GtE':   '>=',
        'In':    'in',
        'Is':    'is',
        'IsNot': 'is not',
        'Lt':    '<',
        'LtE':   '<=',
        'NotEq': '!=',
        'NotIn': 'not in',
        # Context operators.
        'AugLoad':  '<AugLoad>',
        'AugStore': '<AugStore>',
        'Del':      '<Del>',
        'Load':     '<Load>',
        'Param':    '<Param>',
        'Store':    '<Store>',
        # Unary operators.
        'Invert':   '~',
        'Not':      'not',
        'UAdd':     '+',
        'USub':     '-',
        }
        name = d.get(self.kind(node),'<%s>' % node.__class__.__name__)
        if strict: assert name,self.kind(node)
        return name
    #@+node:ekr.20150523083043.1: *3* lt.Visitors
    #@+node:ekr.20150520173107.12: *4* lt.Expressions
    #@+node:ekr.20150520173107.13: *5* lt.Expr
    def do_Expr(self,node):
        '''An outer expression: must be indented.'''
        self.line_start()
        self.visit(node.value)
        self.line_end()
    #@+node:ekr.20150520173107.14: *5* lt.Expression
    def do_Expression(self,node):
        '''An inner expression: do not indent.'''
        self.visit(node.body)
        self.line_end()
    #@+node:ekr.20150520173107.15: *5* lt.GeneratorExp
    # GeneratorExp(expr elt, comprehension* generators)

    def do_GeneratorExp(self,node):
        
        self.lt('(')
        self.visit(node.elt)
        self.word('for')
        if node.generators:
            for z in node.generators:
                self.visit(z)
        self.rt(')')
    #@+node:ekr.20150520173107.17: *4* lt.Operands
    #@+node:ekr.20150520173107.18: *5* lt.arguments
    # arguments = (expr* args, identifier? vararg, identifier? kwarg, expr* defaults)

    def do_arguments(self,node):
        '''Format the arguments node.'''
        assert self.kind(node) == 'arguments',node
        self.in_arg_list = True
        n_plain = len(node.args) - len(node.defaults)
        n_args = len(node.args)
        self.arg_start()
        for i in range(n_args):
            if i < n_plain:
                self.visit(node.args[i])
            else:
                self.visit(node.args[i])
                self.op('=')
                self.visit(node.defaults[i-n_plain])
            if i + 1 < n_args:
                self.lit_blank(',')
        if getattr(node,'vararg',None):
            if node.args:
                self.lit_blank(',')
            self.lit('*')
            name = getattr(node,'vararg')
            self.word(name.arg if g.isPython3 else name)
        if getattr(node,'kwarg',None):
            if node.args or getattr(node,'vararg',None):
                self.lit_blank(',')
            self.lit('**')
            name = getattr(node,'kwarg')
            self.word(name.arg if g.isPython3 else name)
        self.arg_end()
        self.in_arg_list = False
    #@+node:ekr.20150520173107.19: *5* lt.arg (Python3 only)
    # Python 3:
    # arg = (identifier arg, expr? annotation)

    def do_arg(self,node):
        '''Return the name of the argument.'''
        self.word(node.arg)
    #@+node:ekr.20150520173107.20: *5* lt.Attribute
    # Attribute(expr value, identifier attr, expr_context ctx)

    def do_Attribute(self,node):
        
        self.visit(node.value)
        self.lit_no_blanks('.')
        self.word(node.attr)
    #@+node:ekr.20150520173107.21: *5* lt.Bytes
    def do_Bytes(self,node): # Python 3.x only.
        assert g.isPython3
        self.lit(node.s)
    #@+node:ekr.20150520173107.22: *5* lt.Call & lt.keyword
    # Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)

    def do_Call(self,node):

        self.visit(node.func)
        self.lit_no_blanks('(')
        for i,z in enumerate(node.args):
            self.visit(z)
            if i + 1 < len(node.args):
                self.lit_blank(',')
        if node.args and node.keywords:
            self.lit_blank(',')
        for i,z in enumerate(node.keywords):
            self.visit(z) # Calls f.do_keyword.
            if i + 1 < len(node.keywords):
                self.lit_blank(',')
        if getattr(node,'starargs',None):
            if node.args or node.keywords:
                self.lit_blank(',')
            self.lit('*')
            self.visit(node.starargs)
        if getattr(node,'kwargs',None):
            if node.args or node.keywords or getattr(node,'starargs',None):
                self.lit_blank(',')
            self.lit('**')
            self.visit(node.kwargs)
        self.rt(')')
    #@+node:ekr.20150520173107.23: *6* lt.keyword
    # keyword = (identifier arg, expr value)

    def do_keyword(self,node):
        
        self.lit(node.arg)
            # node.arg is a string.
        self.lit('=')
        self.visit(node.value)
            # This is a keyword *arg*, not a Python keyword!
    #@+node:ekr.20150520173107.24: *5* lt.comprehension
    # comprehension (expr target, expr iter, expr* ifs)

    def do_comprehension(self,node):
        
        self.visit(node.target)
        self.op('in')
        self.visit(node.iter)
        if node.ifs:
            for i,z in enumerate(node.ifs):
                self.word('if')
                self.visit(z)
    #@+node:ekr.20150520173107.25: *5* lt.Dict
    def do_Dict(self,node):
        
        self.lt('{')
        if node.keys:
            if len(node.keys) == len(node.values):
                # g.trace([(z.s,z.str_spelling) for z in node.keys])
                # g.trace([(z.s,z.str_spelling) for z in node.values])
                self.level += 1
                for i in range(len(node.keys)):
                    self.visit(node.keys[i])
                    self.lit(':')
                    self.blank()
                    self.visit(node.values[i])
                    self.lit_blank(',')
                    if i + 1 < len(node.keys):
                        self.line_start()
                self.level -= 1
            else:
                print('Error: f.Dict: len(keys) != len(values)\nkeys: %r\nvals: %r' % (
                    node.keys,node.values))
        self.rt('}')
    #@+node:ekr.20150520173107.26: *5* lt.Ellipsis
    def do_Ellipsis(self,node):
        
        self.lit('...')
    #@+node:ekr.20150520173107.27: *5* lt.ExtSlice
    def do_ExtSlice (self,node):
        
        for i,z in enumerate(node.dims):
            self.visit(z)
            if i + 1 < len(node.dims):
                self.op(':')
    #@+node:ekr.20150520173107.28: *5* lt.Index
    def do_Index (self,node):
        
        self.visit(node.value)
    #@+node:ekr.20150520173107.29: *5* lt.List
    def do_List(self,node):

        # Not used: list context.
        # self.visit(node.ctx)
        self.lt('[')
        if node.elts:
            for i,z in enumerate(node.elts):
                self.visit(z)
                if i + 1 < len(node.elts):
                    self.lit_blank(',')
        self.rt(']')
        
    #@+node:ekr.20150520173107.30: *5* lt.ListComp
    def do_ListComp(self,node):
        
        self.lt('[')
        self.visit(node.elt)
        self.word('for')
        for i,z in enumerate(node.generators):
            self.visit(z)
            ### ?
        self.rt(']')
    #@+node:ekr.20150520173107.31: *5* lt.Name
    def do_Name(self,node):

        self.word(node.id)
    #@+node:ekr.20150520182346.1: *5* lt.NameConstant
    # Python 3 only.

    def do_NameConstant(self,node):
        
        self.lit(str(node.value))
    #@+node:ekr.20150520173107.32: *5* lt.Num
    def do_Num(self,node):
        
        self.lit(repr(node.n))
    #@+node:ekr.20150520173107.33: *5* lt.Repr
    # Python 2.x only
    def do_Repr(self,node):
        
        self.word('repr')
        self.lt('(')
        self.visit(node.value)
        self.rt(')')
    #@+node:ekr.20150520173107.34: *5* lt.Slice
    def do_Slice (self,node):
        
        # g.trace(repr(node.lower),repr(node.upper),repr(node.step))
        if node.lower:
            self.visit(node.lower)
        self.op(':')
        if node.upper:
            self.visit(node.upper)
        if node.step:
            self.op(':')
            if hasattr(node.step,'id') and node.step.id == 'None':
                pass
            else:
                self.visit(node.step) 

        # if getattr(node,'lower',None) is not None:
            # self.visit(node.lower)
        # self.op(':')
        # if getattr(node,'upper',None) is not None:
            # self.visit(node.upper)
        # if getattr(node,'step',None) is not None:
            # if hasattr(node.step,'id'):
                # g.trace(node.step.id)
            # self.op(':')
            # g.trace(node.step)
            # self.visit(node.step) 
    #@+node:ekr.20150520173107.35: *5* lt.Str
    def do_Str (self,node):
        '''This represents a string constant.'''
        self.lit(node.str_spelling)
    #@+node:ekr.20150520173107.36: *5* lt.Subscript
    # Subscript(expr value, slice slice, expr_context ctx)

    def do_Subscript(self,node):
        
        self.visit(node.value)
        self.lt('[')
        self.visit(node.slice)
        self.rt(']')
    #@+node:ekr.20150520173107.37: *5* lt.Tuple
    def do_Tuple(self,node):
        
        self.lt('(')
        for i,z in enumerate(node.elts):
            self.visit(z)
            if i + 1 < len(node.elts):
                self.lit_blank(',')
        self.rt(')')
    #@+node:ekr.20150520173107.38: *4* lt.Operators
    #@+node:ekr.20150520173107.39: *5* lt.BinOp
    def do_BinOp (self,node):

        self.lt('(')
        self.visit(node.left)
        self.op(self.op_name(node.op))
        self.visit(node.right)
        self.rt(')')
        
    #@+node:ekr.20150526141653.1: *5* lt.Compare ops
    # Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
     
    def do_Eq   (self,node): self.op('==')
    def do_Gt   (self,node): self.op('>')
    def do_GtE  (self,node): self.op('>=')
    def do_In   (self,node): self.word('in')
    def do_Is   (self,node): self.word('is')
    def do_IsNot(self,node): self.word('is not')
    def do_Lt   (self,node): self.op('<')
    def do_LtE  (self,node): self.op('<=')
    def do_NotEq(self,node): self.op('!=')
    def do_NotIn(self,node): self.word('not in')
    #@+node:ekr.20150520173107.40: *5* lt.BoolOp
    # BoolOp(boolop op, expr* values)

    def do_BoolOp (self,node):
        
        op_name = self.op_name(node.op)
        self.lt('(')
        for i,z in enumerate(node.values):
            self.visit(z)
            if i + 1 < len(node.values):
                self.op(op_name)
        self.rt(')')
    #@+node:ekr.20150520173107.41: *5* lt.Compare
    # Compare(expr left, cmpop* ops, expr* comparators)

    def do_Compare(self,node):
        
        self.lt('(')
        self.visit(node.left)
        assert len(node.ops) == len(node.comparators)
        for i in range(len(node.ops)):
            self.visit(node.ops[i])
            self.visit(node.comparators[i])
        self.rt(')')
    #@+node:ekr.20150520173107.42: *5* lt.UnaryOp
    # UnaryOp(unaryop op, expr operand)

    def do_UnaryOp (self,node):
        
        name = self.op_name(node.op)
        self.lt('(')
        if name.isalpha():
            self.word(name)
        else:
            self.lit(name)
        self.visit(node.operand)
        self.rt(')')
        
    #@+node:ekr.20150520173107.43: *5* lt.ifExp (ternary operator)
    def do_IfExp (self,node):
        
        self.visit(node.body)
        self.word('if')
        self.visit(node.test)
        self.blank()
        self.word('else')
        self.visit(node.orelse)
        self.blank()
    #@+node:ekr.20150520173107.44: *4* lt.Statements
    #@+node:ekr.20150520173107.45: *5* lt.Assert
    def do_Assert(self,node):

        self.line_start()
        self.word('assert')
        self.visit(node.test)
        if getattr(node,'msg',None):
            self.lit_blank(',')
            self.visit(node.msg)
        self.line_end()
    #@+node:ekr.20150520173107.46: *5* lt.Assign
    def do_Assign(self,node):

        self.line_start()
        for z in node.targets:
            self.visit(z)
            self.op('=')
        self.visit(node.value)
        self.line_end()
        
    #@+node:ekr.20150520173107.47: *5* lt.AugAssign
    def do_AugAssign(self,node):
        
        self.line_start()
        self.visit(node.target)
        self.op(self.op_name(node.op)+'=')
        self.visit(node.value)
        self.line_end()
    #@+node:ekr.20150520173107.48: *5* lt.Break
    def do_Break(self,node):

        self.line_start()
        self.word('break')
        self.line_end()
    #@+node:ekr.20150520173107.7: *5* lt.ClassDef
    # ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)

    def do_ClassDef (self,node):

        self.blank_lines(2)
        decorators = node.decorator_list
        if decorators:
            for i,z in enumerate(decorators):
                self.line_start()
                self.visit(z)
                self.line_end()
        self.line_start()
        self.word('class')
        self.word(node.name)
        if node.bases:
            self.lt('(')
            for i,z in enumerate(node.bases):
                self.visit(z)
                if i + 1 < len(node.bases):
                    self.lit_blank(',')
            self.rt(')')
        self.lit_no_blanks(':')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
        self.blank_lines(2)
    #@+node:ekr.20150520173107.49: *5* lt.Continue
    def do_Continue(self,node):
        
        self.line_start()
        self.word('continue')
        self.line_end()
        
    #@+node:ekr.20150520173107.50: *5* lt.Delete
    def do_Delete(self,node):

        self.line_start()
        self.word('del')
        if node.targets:
            for i, z in enumerate(node.targets):
                self.visit(z)
                if i + 1 < len(node.targets):
                    self.lit_blank(',')
        self.line_end()
    #@+node:ekr.20150520173107.51: *5* lt.ExceptHandler
    def do_ExceptHandler(self,node):
        
        # g.trace(node)
        self.line_start()
        self.word('except')
        if getattr(node,'type',None):
            self.blank()
            self.visit(node.type)
        if getattr(node,'name',None):
            self.word('as')
            if isinstance(node.name,ast.AST):
                self.visit(node.name)
            else:
                self.word(node.name) # Python 3.x.
        self.lit_no_blanks(':')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
    #@+node:ekr.20150520173107.52: *5* lt.Exec
    # Exec(expr body, expr? globals, expr? locals)

    # Python 2.x only
    def do_Exec(self,node):
        
        globals_ = getattr(node,'globals',None)
        locals_ = getattr(node,'locals',None)
        self.line_start()
        self.word('exec')
        self.visit(node.body)
        if globals_ or locals_:
            self.word('in')
        if globals_:
            self.visit(node.globals)
        if locals_:
            if globals_:
                self.lit_blank(',')
            self.visit(node.locals)
        self.line_end()
    #@+node:ekr.20150520173107.53: *5* lt.For
    def do_For (self,node):
        
        self.line_start()
        self.word('for')
        self.visit(node.target)
        self.op('in')
        self.visit(node.iter)
        self.lit_no_blanks(':')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
        if node.orelse:
            self.line_start()
            self.word('else')
            self.lit_no_blanks(':')
            self.line_end()
            for z in node.orelse:
                self.level += 1
                self.visit(z)
                self.level -= 1
    #@+node:ekr.20150520173107.8: *5* lt.FunctionDef
    # FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list)

    def do_FunctionDef (self,node):
        '''Format a FunctionDef node.'''
        self.blank_lines(1)
        if node.decorator_list:
            for z in node.decorator_list:
                self.line_start()
                self.op('@')
                self.visit(z)
                self.line_end()
        self.line_start()
        self.word('def')
        self.word(node.name)
        self.lt('(')
        if node.args:
            self.visit(node.args)
        self.rt(')')
        self.lit_no_blanks(':')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
        self.blank_lines(1)
    #@+node:ekr.20150520173107.54: *5* lt.Global
    def do_Global(self,node):
        
        self.line_start()
        self.word('global')
        for i,z in enumerate(node.names):
            self.word(z)
            if i + 1 < len(node.names):
                self.lit_blank(',')
        self.line_end()
    #@+node:ekr.20150520173107.55: *5* lt.If
    def do_If (self,node):
        
        self.line_start()
        self.word('if')
        self.visit(node.test)
        self.lit_no_blanks(':')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
        if node.orelse:
            self.line_start()
            self.word('else')
            self.lit_no_blanks(':')
            self.line_end()
            for z in node.orelse:
                self.level += 1
                self.visit(z)
                self.level -= 1
    #@+node:ekr.20150520173107.56: *5* lt.Import & helper
    def do_Import(self,node):
        
        self.line_start()
        self.word('import')
        aList = self.get_import_names(node)
        for i,data in enumerate(aList):
            fn,asname = data
            self.word(fn)
            if asname:
                self.op('as')
                self.word(asname)
            if i + 1 < len(aList):
                self.lit_blank(',')
        self.line_end()
    #@+node:ekr.20150520173107.57: *6* lt.get_import_names
    def get_import_names (self,node):
        '''Return a list of the the full file names in the import statement.'''
        result = []
        for ast2 in node.names:
            if self.kind(ast2) == 'alias':
                data = ast2.name,ast2.asname
                result.append(data)
            else:
                g.trace('unsupported kind in Import.names list',self.kind(ast2))
        return result
    #@+node:ekr.20150520173107.58: *5* lt.ImportFrom
    def do_ImportFrom(self,node):
        
        self.line_start()
        self.word('from')
        self.word(node.module)
        self.word('import')
        aList = self.get_import_names(node)
        for i, data in enumerate(aList):
            fn, asname = data
            self.word(fn)
            if asname:
                self.word('as')
                self.word(asname)
            if i + 1 < len(aList):
                self.lit_blank(',')
        self.line_end()
    #@+node:ekr.20150520173107.11: *5* lt.Lambda
    def do_Lambda (self,node):
        
        ### self.conditional_line_start()
        self.word('lambda')
        if node.args:
            self.visit(node.args)
        self.lit_no_blanks(':')
        self.visit(node.body)
        self.line_end()
    #@+node:ekr.20150520173107.10: *5* lt.Module
    def do_Module (self,node):
        
        for z in node.body:
            self.visit(z)
    #@+node:ekr.20150520173107.59: *5* lt.Pass
    def do_Pass(self,node):

        self.line_start()
        self.word('pass')
        self.line_end()
    #@+node:ekr.20150520173107.60: *5* lt.Print (Still a problem)
    # Python 2.x only
    # Print(expr? dest, expr* values, bool nl)
    def do_Print(self,node):

        self.line_start()
        self.word('print')
        self.lt('(')
        for i,z in enumerate(node.values):
            if isinstance(z,ast.Tuple):
                for z2 in z.elts:
                    self.visit(z2)
                    if i + 1 < len(z.elts):
                        self.lit_blank(',')
            else:
                self.visit(z)
            if i + 1 < len(node.values):
                self.lit_blank(',')
        # if getattr(node,'dest',None):
            # vals.append('dest=%s' % self.visit(node.dest))
        # if getattr(node,'nl',None):
            # vals.append('nl=%s' % node.nl)
        self.rt(')')
        self.line_end()
    #@+node:ekr.20150520173107.61: *5* lt.Raise
    def do_Raise(self,node):
        
        has_arg = False
        self.line_start()
        self.word('raise')
        for attr in ('type','inst','tback'):
            if getattr(node,attr,None) is not None:
                if has_arg:
                    self.lit_blank(',')
                self.visit(getattr(node,attr))
                has_arg = True
        self.line_end()
    #@+node:ekr.20150520173107.62: *5* lt.Return
    def do_Return(self,node):
        
        self.line_start()
        self.word('return')
        if node.value:
            self.blank()
            self.visit(node.value)
        self.line_end()
    #@+node:ekr.20150520202136.1: *5* lt.Try
    # Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)

    def do_Try(self,node):

        self.line_start()
        self.word('try')
        self.lit_no_blanks(':')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
        if node.handlers:
            for z in node.handlers:
                self.visit(z)
        if node.orelse:
            self.line_start()
            self.word('else')
            self.lit_no_blanks(':')
            self.line_end()
            for z in node.orelse:
                self.level += 1
                self.visit(z)
                self.level -= 1 
        if node.finalbody:
            self.line_start()
            self.word('finally')
            self.lit_no_blanks(':')
            self.line_end()
            for z in node.finalbody:
                self.level += 1
                self.visit(z)
                self.level -= 1
    #@+node:ekr.20150520173107.64: *5* lt.TryExcept (Python 2)
    # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
    # TryFinally(stmt* body, stmt* finalbody)

    def do_TryExcept(self,node):

        # g.trace(node)
        self.line_start()
        self.word('try:')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
        if node.handlers:
            for z in node.handlers:
                self.visit(z)
        if node.orelse:
            self.line_start()
            self.word('else:')
            self.line_end()
            for z in node.orelse:
                self.level += 1
                self.visit(z)
                self.level -= 1
        self.line_end()
    #@+node:ekr.20150520173107.65: *5* lt.TryFinally (Python 2)
    # TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
    # TryFinally(stmt* body, stmt* finalbody)

    def do_TryFinally(self,node):
        
        # g.trace(node)
        self.line_start()
        self.word('try:')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
        self.line_start()
        self.word('finally:')
        self.line_end()
        for z in node.finalbody:
            self.level += 1
            self.visit(z)
            self.level -= 1
        
    #@+node:ekr.20150520173107.66: *5* lt.While
    def do_While (self,node):
        
        self.line_start()
        self.word('while')
        self.visit(node.test)
        self.lit_no_blanks(':')
        self.line_end()
        for z in node.body:
            self.level += 1
            self.visit(z)
            self.level -= 1
        if node.orelse:
            self.line_start()
            self.word('else')
            self.lit_no_blanks(':')
            self.line_end()
            for z in node.orelse:
                self.level += 1
                self.visit(z)
                self.level -= 1
    #@+node:ekr.20150520173107.67: *5* lt.With
    # With(expr context_expr, expr? optional_vars, stmt* body)

    def do_With (self,node):
        
        self.line_start()
        self.word('with')
        if hasattr(node,'context_expression'):
            self.visit(node.context_expresssion)
        vars_list = []
        if hasattr(node,'optional_vars'):
            try:
                for i,z in enumerate(node.optional_vars):
                    self.visit(z)
                    if i + 1 < len(node.optional_vars):
                        self.lit_blank(',')
            except TypeError: # Not iterable.
                self.visit(node.optional_vars) 
        self.lit_no_blanks(':')
        self.line_end()
        self.level += 1
        for z in node.body:
            self.visit(z)
        self.level -= 1
        self.line_end()
    #@+node:ekr.20150520173107.68: *5* lt.Yield
    # Yield(expr? value)

    def do_Yield(self,node):
        
        self.line_start()
        self.word('yield')
        if hasattr(node,'value'):
            self.blank()
            self.visit(node.value)
        self.line_end()
    #@-others
#@+node:ekr.20150525123715.1: ** class ProjectUtils
class ProjectUtils:
    '''A class to compute the files in a project.'''
    # To do: get project info from @data nodes.

    #@+others
    #@+node:ekr.20150525123715.2: *3* pu.files_in_dir
    def files_in_dir (self,theDir,recursive=True,extList=None,excludeDirs=None):
        '''
        Return a list of all Python files in the directory.
        Include all descendants if recursiveFlag is True.
        Include all file types if extList is None.
        '''
        # if extList is None: extList = ['.py']
        if excludeDirs is None: excludeDirs = []
        result = []
        if recursive:
            for root, dirs, files in os.walk(theDir):
                for z in files:
                    fn = g.os_path_finalize_join(root,z)
                    junk,ext = g.os_path_splitext(fn)
                    if not extList or ext in extList:
                        result.append(fn)
                if excludeDirs and dirs:
                    for z in dirs:
                        if z in excludeDirs:
                            dirs.remove(z)
        else:
            for ext in extList:
                result.extend(glob.glob('%s.*%s' % (theDir,ext)))
        return sorted(list(set(result)))
    #@+node:ekr.20150525123715.3: *3* pu.get_project_directory
    def get_project_directory(self,name):
        
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[:i].strip()
        leo_path,junk = g.os_path_split(__file__)
        d = { # Change these paths as required for your system.
            'coverage': r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
            'leo':      r'C:\leo.repo\leo-editor\leo\core',
            'lib2to3':  r'C:\Python26\Lib\lib2to3',
            'pylint':   r'C:\Python26\Lib\site-packages\pylint',
            'rope':     r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base',
            'test':     g.os_path_finalize_join(g.app.loadDir,'..','test-proj'),
        }
        dir_ = d.get(name.lower())
        # g.trace(name,dir_)
        if not dir_:
            g.trace('bad project name: %s' % (name))
        if not g.os_path_exists(dir_):
            g.trace('directory not found:' % (dir_))
        return dir_ or ''
    #@+node:ekr.20150525123715.4: *3* pu.project_files
    def project_files(self,name,force_all=False):
        '''Return a list of all files in the named project.'''
        # Ignore everything after the first space.
        i = name.find(' ')
        if i > -1:
            name = name[:i].strip()
        leo_path,junk = g.os_path_split(__file__)
        d = { # Change these paths as required for your system.
            'coverage': (
                r'C:\Python26\Lib\site-packages\coverage-3.5b1-py2.6-win32.egg\coverage',
                ['.py'],['.bzr','htmlfiles']),
            'leo':(
                r'C:\leo.repo\leo-editor\leo\core',
                # leo_path,
                ['.py'],['.bzr']),
            'lib2to3': (
                r'C:\Python26\Lib\lib2to3',
                ['.py'],['tests']),
            'pylint': (
                r'C:\Python26\Lib\site-packages\pylint',
                ['.py'],['.bzr','test']),
            'rope': (
                r'C:\Python26\Lib\site-packages\rope-0.9.4-py2.6.egg\rope\base',['.py'],['.bzr']),
            # 'test': (
                # g.os_path_finalize_join(leo_path,'test-proj'),
                # ['.py'],['.bzr']),
        }
        data = d.get(name.lower())
        if not data:
            g.trace('bad project name: %s' % (name))
            return []
        theDir,extList,excludeDirs=data
        files = self.files_in_dir(theDir,recursive=True,extList=extList,excludeDirs=excludeDirs)
        if files:
            if name.lower() == 'leo':
                for exclude in ['__init__.py','format-code.py']:
                    files = [z for z in files if not z.endswith(exclude)]
                fn = g.os_path_finalize_join(theDir,'..','plugins','qtGui.py')
                if fn and g.os_path_exists(fn):
                    files.append(fn)
            if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
                return [files[0]]
        if not files:
            g.trace(theDir)
        if g.app.runningAllUnitTests and len(files) > 1 and not force_all:
            return [files[0]]
        else:
            return files
    #@-others
#@+node:ekr.20040711135244.5: ** class PythonPrettyPrinter (Uses PythonTidy)
class PythonPrettyPrinter:
    '''A class that implements *limited* pep-8 cleaning.'''
    #@+others
    #@+node:ekr.20040711135244.6: *3* ppp.__init
    def __init__ (self,c):
        '''Ctor for PythonPrettyPrinter class.'''
        self.c = c
        self.changed = False
        self.debug = c.config.getBool('tidy_debug',default=False)
        if self.debug: print('tidy DEBUG')
        self.n = 0
            # The number of nodes actually change.

    #@+node:ekr.20040713091855: *3* ppp.endUndo
    def endUndo (self):

        c = self.c ; u = c.undoer ; undoType = 'Pretty Print'
        current = c.p

        if self.changed:
            # Tag the end of the command.
            u.afterChangeGroup(current,undoType,dirtyVnodeList=self.dirtyVnodeList)
    #@+node:ekr.20040711135244.4: *3* ppp.prettyPrintNode
    def prettyPrintNode(self,p,dump=False,leo_tidy=False):
        '''Pretty print a single node.'''
        if leo_tidy:
            self.python_format(p)
        else:
            self.python_tidy(p)
    #@+node:ekr.20150520170138.1: *3* ppp.python_format (Uses LeoTidy)
    def python_format(self,p):
        '''Use subclasses of leoAst.py to pretty-print Python code.'''
        trace = False and not g.unitTesting
        traceResult = True
        c = self.c
        if not p.b:
            return
        if not p.b.strip():
            ### self.replaceBody(p,lines=None,s='')
            return
        ls = p.b.lstrip()
        if ls.startswith('@\n') or ls.startswith('@ '):
            # Don't format nodes starting with a docpart.
            g.warning("skipped doc part",p.h)
            return
        if ls.startswith('"""') or ls.startswith("'''"):
            # Don't format a node starting with docstring.
            g.warning("skipped docstring",p.h)
            return
        tag1,tag2 = '@others','# (TIDY) @others'
        s1 = p.b.replace(tag1,tag2)
        try:
            t1 = ast.parse(s1,filename='before',mode='exec')
            d1 = ast.dump(t1,annotate_fields=False)
        except SyntaxError:
            d1 = None
            g.trace('syntax error in',p.h)
            return
        try:
            f = LeoTidy(c)
            node = ast.parse(s1,filename=p.h,mode='exec')
            s2 = f.format(node)
            # End the body properly
            s2 = s2.replace(tag2,tag1)
            s2 = s2.rstrip()+'\n' if s2.strip() else ''
        except Exception:
            g.es_exception()
            return
        try:
            t2 = ast.parse(s2,filename='after',mode='exec')
            d2 = ast.dump(t2,annotate_fields=False)
        except SyntaxError:
            d2 = None
        if s2 and s2 != s1 and d1 == d2:
            # g.trace('replacing: len(s2)=%4s %s' % (len(s2),p.h))
            self.n += 1
            ### self.replaceBody(p,lines=None,s=s2)
        if d1 != d2:
            if trace:
                g.warning('Python Format error %4s %4s %s' % (
                    len(d1),d2 and len(d2) or 0,p.h))
            if trace:
                g.trace(len(d1),d2 and len(d2) or 0)
                # g.trace('===== d1 %s\n\n%s' % (d1 and len(d1) or 0, d1))
                # g.trace('===== d2 %s\n\n%s' % (d2 and len(d2) or 0, d2))
    #@+node:ekr.20141010071140.18268: *3* ppp.python_tidy (Uses PythonTidy)
    def python_tidy(self,p):
        '''Use PythonTidy to do the formatting.'''
        c = self.c
        trace = False and not g.unitTesting
        if g.isPython3:
            g.warning('PythonTidy does not work with Python 3.x')
            return
        if p.b and not p.b.strip():
            self.replaceBody(p,lines=None,s='')
            return
        ls = p.b.lstrip()
        if ls.startswith('@\n') or ls.startswith('@ '):
            # Don't format nodes starting with a docpart.
            g.warning("skipped doc part",p.h)
            return
        if ls.startswith('"""') or ls.startswith("'''"):
            # Don't format a node starting with docstring.
            g.warning("skipped docstring",p.h)
            return
        tag1,tag2 = '@others','# (TIDY) @others'
        s1 = p.b.replace(tag1,tag2)
        try:
            t1 = ast.parse(s1,filename='s1',mode='exec')
            d1 = ast.dump(t1,annotate_fields=False)
        except SyntaxError:
            d1 = None
        file_in = g.fileLikeObject(fromString=s1)
        file_out = g.fileLikeObject()
        is_module = p.isAnyAtFileNode()
        try:
            tidy.tidy_up(
                file_in=file_in,
                file_out=file_out,
                is_module=is_module,
                leo_c=c)
            s = file_out.get()
            # End the body properly
            s = s.rstrip()+'\n' if s.strip() else ''
            try:
                t2 = ast.parse(s,filename='s2',mode='exec')
                d2 = ast.dump(t2,annotate_fields=False)
            except SyntaxError:
                d2 = None
            if d1 == d2 or self.debug:
                s = s.replace(tag2,tag1)
                self.replaceBody(p,lines=None,s=s)
            else:
                g.warning('PythonTidy error in',p.h)
                g.trace('===== d1\n\n',d1,'\n=====d2\n\n',d2)
        except Exception:
            g.warning("skipped",p.h)
            if g.unitTesting:
                raise
            elif trace:
                g.es_exception()
                # g.trace(s1)
    #@+node:ekr.20040713070356: *3* ppp.replaceBody
    def replaceBody (self,p,lines,s=None):
        '''Replace the body with the pretty version.'''
        c,u = self.c,self.c.undoer
        undoType = 'Pretty Print'
        oldBody = p.b
        body = s if s is not None else ''.join(lines)
        if oldBody != body:
            g.trace('changed',p.h)
            self.n += 1
            if not self.changed:
                # Start the group.
                u.beforeChangeGroup(p,undoType)
                self.changed = True
                self.dirtyVnodeList = []
            undoData = u.beforeChangeNodeContents(p)
            c.setBodyString(p,body)
            dirtyVnodeList2 = p.setDirty()
            self.dirtyVnodeList.extend(dirtyVnodeList2)
            u.afterChangeNodeContents(p,undoType,undoData,dirtyVnodeList=self.dirtyVnodeList)
    #@-others
#@+node:ekr.20150519111457.1: ** class PythonTokenBeautifier
class PythonTokenBeautifier:
    '''A token-based Python beautifier.'''
    #@+others
    #@+node:ekr.20150523132558.1: *3* class OutputToken
    class OutputToken:
        '''A class representing items on the code list.'''
        
        def __init__(self,kind,lws,value):
            self.kind = kind
            self.lws = lws
            self.value = value
            
        def __repr__(self):
            return '%15s %-2s %s' % (self.kind,show_lws(self.lws),repr(self.value))
       
        __str__ = __repr__

        def to_string(self):
            '''Convert an output token to a string.'''
            return self.value if g.isString(self.value) else ''
    #@+node:ekr.20150527113020.1: *3* class ParseState
    class ParseState:
        '''A class representing items parse state stack.'''
        
        def __init__(self,kind,value):
            self.kind = kind
            self.value = value
            
        def __repr__(self):
            return 'State: %10s %s' % (self.kind,repr(self.value))

        __str__ = __repr__
    #@+node:ekr.20150519111713.1: *3* ptb.ctor
    def __init__ (self,c):
        '''Ctor for PythonPrettyPrinter class.'''
        self.c = c
        self.code_list = []
            # The list of output tokens.
        self.bracketLevel = 0
        self.changed = False
        self.continuation = False # True: line ends with backslash-newline.
        self.dirtyVnodeList = []
        ### self.erow = self.ecol = 0 # The ending row/col of the token.
        self.last_name = None # The name of the previous token type.
        self.level = 0 # indentation level, an int.
        self.line_number = 0 # Same as self.srow
        self.lws = '' # Leading whitespace.  ' '*4*self.level
        self.paren_level = 0
        self.s = None # The string containing the line.
        self.square_bracket_level = 0
        ### self.srow = self.scol = 0 # The starting row/col of the token.
        self.starts_line = True # True: the token starts a line.
        self.trailing_ws = '' # The whitespace following *this* token.
        self.val = None
        
    #@+node:ekr.20150526194736.1: *3* ptb.Input token Handlers
    #@+node:ekr.20150526203605.1: *4* ptb.do_comment
    def do_comment(self):
        '''Handle a comment token.'''
        self.add_token('comment',self.val)
    #@+node:ekr.20041021102938: *4* ptb.do_endmarker
    def do_endmarker (self):
        '''Handle an endmarker token.'''
        pass
    #@+node:ekr.20041021102340.1: *4* ptb.do_errortoken
    def do_errortoken (self):
        '''Handle an errortoken token.'''
        # This code is executed for versions of Python earlier than 2.4
        if self.val == '@':
            self.lit(self.val)
    #@+node:ekr.20041021102340.2: *4* ptb.do_indent & do_dedent
    def do_dedent (self):
        '''Handle dedent token.'''
        self.level -= 1
        self.lws = self.level*4*' '
        self.line_start()
       
    def do_indent (self):
        '''Handle indent token.'''
        self.level += 1
        self.lws = self.val
        self.line_start()
    #@+node:ekr.20041021101911.5: *4* ptb.do_name
    def do_name(self):
        '''Handle a name token.'''
        name = self.val
        if name == 'class':
            self.blank_lines(2)
        elif name == 'def':
            self.blank_lines(1)
        self.word(name)
    #@+node:ekr.20041021101911.3: *4* ptb.do_newline
    def do_newline (self):
        '''Handle a regular newline.'''
        self.line_end()
    #@+node:ekr.20141009151322.17828: *4* ptb.do_nl
    def do_nl(self):
        '''Handle a continuation line.'''
        self.line_end()
    #@+node:ekr.20041021101911.6: *4* ptb.do_number
    def do_number (self):
        '''Handle a number token.'''
        self.add_token('number',self.val)
    #@+node:ekr.20040711135244.11: *4* ptb.do_op
    def do_op (self):
        '''Handle an op token.'''
        val = self.val
        if val in '.':
            self.lit_no_blanks(val)
        elif val in ',;:':
            # Pep 8: Avoid extraneous whitespace immediately before
            # comma, semicolon, or colon.
            self.lit_blank(val)
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
            self.op(val)
                # To do: test whether in def/call argument.
        else:
            # Pep 8: always surround binary operators with a single space.
            # '==','+=','-=','*=','**=','/=','//=','%=','!=','<=','>=','<','>',
            
            # '^','~','*','**','&','|','/','//',
            # Possible unary operators '+' '-'
            # Pep 8: If operators with different priorities are used,
            # consider adding whitespace around the operators with the lowest priority(ies).
            self.op(val)
    #@+node:ekr.20150526204248.1: *4* ptb.do_string
    def do_string(self):
        '''Handle a 'string' token.'''
        self.add_token('string',self.val)
            # This does retain the string's spelling.
    #@+node:ekr.20150526201902.1: *3* ptb.Output token generators
    #@+node:ekr.20150526195542.1: *4* ptb.add_token
    def add_token(self,kind,value=''):
        '''Add a token to the code list.'''
        # g.trace(kind,repr(value))
        tok = self.OutputToken(kind,self.lws,value)
        self.code_list.append(tok)
    #@+node:ekr.20150526201701.3: *4* ptb.arg_start & arg_end
    def arg_end(self):
        '''Add a token indicating the end of an argument list.'''
        self.add_token('arg-end')
        
    def arg_start(self):
        '''Add a token indicating the start of an argument list.'''
        self.add_token('arg-start')
    #@+node:ekr.20150526201701.4: *4* ptb.blank
    def blank(self):
        '''Add a blank request on the code list.'''
        prev = self.code_list[-1]
        if prev.kind not in (
            'blank','blank-lines',
                # Suppress duplicates.
            'file-start','line-start','line-end','line-indent',
                # These tokens implicitly suppress blanks.
            'arg-start','lit-no-blanks','lt',
                # These tokens explicity suppress blanks.
        ):
            self.add_token('blank',' ')
    #@+node:ekr.20150526201701.5: *4* ptb.blank_lines
    def blank_lines(self,n):
        '''
        Add a request for n blank lines to the code list.
        Multiple blank-lines request yield at least the maximum of all requests.
        '''
        # Count the number of 'consecutive' end-line tokens, ignoring blank-lines tokens.
        prev_lines = 0
        i = len(self.code_list)-1 # start-file token guarantees i >= 0
        while True:
            kind = self.code_list[i].kind
            if kind == 'file-start':
                prev_lines = n ; break
            elif kind in ('blank-lines','line-indent'):
                i -= 1
            elif kind == 'line-end':
                i -= 1 ; prev_lines += 1
            else: break
        # g.trace('i: %3s n: %s prev: %s' % (len(self.code_list),n,prev_lines))
        while prev_lines <= n:
            self.line_end()
            prev_lines += 1
        # Retain the intention for debugging.
        self.add_token('blank-lines',n)
    #@+node:ekr.20150526201701.6: *4* ptb.clean
    def clean(self,kind):
        '''Remove the last item of token list if it has the given kind.'''
        prev = self.code_list[-1]
        if prev.kind == kind:
            self.code_list.pop()
    #@+node:ekr.20150526201701.7: *4* ptb.conditional_line_start (not used)
    def conditional_line_start(self):
        '''Add a conditional line start to the code list.'''
        prev = self.code_list[-1]
        if prev.kind != 'start-line':
            self.add_token('start-line')
    #@+node:ekr.20150526201701.8: *4* ptb.file_start & file_end
    def file_end(self):
        '''
        Add a file-end token to the code list.
        Retain exactly one line-end token.
        '''
        while True:
            prev = self.code_list[-1]
            if prev.kind in ('blank-lines','line-end'):
                self.code_list.pop()
            else:
                break
        self.add_token('line-end')
        self.add_token('file-end')

    def file_start(self):
        '''Add a file-start token to the code list.'''
        self.add_token('file-start')
    #@+node:ekr.20150526201701.9: *4* ptb.line_start & line_end
    def line_end(self):
        '''Add a line-end request to the code list.'''
        prev = self.code_list[-1]
        if prev.kind != 'file-start':
            self.clean('line-indent')
            self.add_token('line-end','\n')
            self.add_token('line-indent',self.lws)
                # Add then indentation for all lines
                # until the next indent or unindent token.

    def line_start(self):
        '''Add a line-start request to the code list.'''
        self.clean('line-indent')
        self.add_token('line-indent',self.lws)
    #@+node:ekr.20150526201701.10: *4* ptb.lit*
    def lit(self,s):
        '''Add a request for a literal to the code list.'''
        assert s and g.isString(s),repr(s)
        # g.trace(repr(s),g.callers())
        self.add_token('lit',s)
        
    def lit_blank(self,s):
        '''Add request for a liter (no previous blank) followed by a blank.'''
        self.clean('blank')
        self.lit(s)
        self.blank()

    def lit_no_blanks(self,s):
        '''Add a request for a literal *not* surrounded by blanks.'''
        self.clean('blank')
        self.add_token('lit-no-blanks',s)
    #@+node:ekr.20150526201701.11: *4* ptb.lt & rt
    def lt(self,s):
        '''Add a left paren request to the code list.'''
        assert s in '([{',repr(s)
        self.lit_no_blanks(s)
        # self.add_token('lt',s)
        
    def rt(self,s):
        '''Add a right paren request to the code list.'''
        assert s in ')]}',repr(s)
        prev = self.code_list[-1]
        if prev.kind == 'arg-end':
            # Remove a blank token preceding the arg-end token.
            prev = self.code_list.pop()
            self.clean('blank')
            self.code_list.append(prev)   
        else:
            self.clean('blank')
        self.add_token('rt',s)
    #@+node:ekr.20150526201701.12: *4* ptb.op
    def op(self,s):
        '''Add an operator request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.lit(s)
        self.blank()
    #@+node:ekr.20150526201701.13: *4* ptb.word
    def word(self,s):
        '''Add a word request to the code list.'''
        assert s and g.isString(s),repr(s)
        self.blank()
        self.add_token('word',s)
        self.blank()
    #@+node:ekr.20150521122451.1: *3* ptb.replace_body (not used yet)
    def replace_body (self,p,s):
        '''Replace p.b with s.'''
        c,u,undoType = self.c,self.c.undoer,'Pretty Print'
        if p.b != s:
            if not self.changed:
                # Start the group.
                u.beforeChangeGroup(p,undoType)
                self.changed = True
                self.dirtyVnodeList = []
            undoData = u.beforeChangeNodeContents(p)
            c.setBodyString(p,s)
            dirtyVnodeList2 = p.setDirty()
            self.dirtyVnodeList.extend(dirtyVnodeList2)
            u.afterChangeNodeContents(p,undoType,undoData,dirtyVnodeList=self.dirtyVnodeList)
    #@+node:ekr.20150526194715.1: *3* ptb.run
    def run(self,p,tokens):
        '''The main line of PythonTokenBeautifier class.'''

        def oops():
            g.trace('unknown kind',self.kind)

        self.file_start()
        for token5tuple in tokens:
            t1,t2,t3,t4,t5 = self.token5tuple = token5tuple
            self.kind = token.tok_name[t1].lower()
            self.val = g.toUnicode(t2)
            # g.trace('%10s %r'% (self.kind,self.val))
            func = getattr(self,'do_' + self.kind,oops)
            func()
        self.file_end()
        return ''.join([z.to_string() for z in self.code_list])
        
    #@-others
#@+node:ekr.20150524215322.1: ** dumpTokens & dumpToken
def dumpTokens(tokens,verbose=True):
    last_line_number = 0
    for token5tuple in tokens:
        last_line_number = dumpToken(last_line_number,token5tuple,verbose)

def dumpToken (last_line_number,token5tuple,verbose):
    '''Dump the given token.'''
    t1,t2,t3,t4,t5 = token5tuple
    name = token.tok_name[t1].lower()
    val = str(t2) # can fail
    srow,scol = t3
    erow,ecol = t4
    line = str(t5) # can fail
    if last_line_number != srow:
        if verbose:
            print("\n---- line: %3s %3s %r" % (srow,erow,line))
        else:
            print('%3s %7s %r' % (srow,name,line))
    if verbose:
        if name in ('dedent','indent','newline','nl'):
            val = repr(val)
        # print("%10s %3d %3d %-8s" % (name,scol,ecol,val))
        # print('%10s srow: %s erow: %s %s' % (name,srow,erow,val))
        print('%10s %s' % (name,val))
            # line[scol:ecol]
    last_line_number = srow
    return last_line_number
#@+node:ekr.20150527143619.1: ** show_lws
def show_lws(s):
    '''Show leading whitespace in a convenient format.'''
    return repr(s) if s.strip(' ') else len(s)
#@+node:ekr.20150521114057.1: ** test_beautifier (prints stats)
def test_beautifier(c,h,p,settings):
    '''Test Leo's beautifier code'''
    if not p:
        g.trace('not found: %s' % h)
        return
    s = g.getScript(c, p,
                    useSelectedText=False,
                    forcePythonSentinels=True,
                    useSentinels=False)
    g.trace(h.strip())
    t1 = time.clock()
    s1 = g.toEncodedString(s)
    if settings.get('ast-compare'):
        node1 = ast.parse(s1,filename='before',mode='exec')
    t2 = time.clock()
    readlines = g.ReadLinesClass(s).next
    tokens = list(tokenize.generate_tokens(readlines))
    t3 = time.clock()
    beautifier = PythonTokenBeautifier(c)
    s2 = beautifier.run(p,tokens)
    t4 = time.clock()
    ok = True
    if settings.get('ast-compare'):
        s2 = g.toEncodedString(s2)
        try:
            node2 = ast.parse(s2,filename='before',mode='exec')
            ok = leoAst.compare_ast(node1, node2)
        except SyntaxError:
            g.es_exception()
            ok = False
    t5 = time.clock()
    if settings.get('input_string'):
        print('==================== input_string')
        for i,z in enumerate(g.splitLines(s)):
            print('%4s %s' % (i+1,z.rstrip()))
    if settings.get('input_lines'):
        print('==================== input_lines')
        dumpTokens(tokens,verbose=False)
    if settings.get('input_tokens'):
        print('==================== input_tokens')
        dumpTokens(tokens,verbose=True)
    if settings.get('output_tokens'):
        print('==================== code_list')
        for i,z in enumerate(beautifier.code_list):
            print('%4s %s' % (i,z))
    if settings.get('output_string'):
        print('==================== output_string')
        for i,z in enumerate(g.splitLines(s2)):
            print('%4s %s' % (i+1,z.rstrip()))
    if settings.get('stats'):
        print('==================== stats')
        print('tokens:   %s' % len(tokens))
        print('code_list %s' % len(beautifier.code_list))
        print('len(s2):  %s' % len(s2))
        print('parse:    %4.2f sec.' % (t2-t1))
        print('tokenize: %4.2f sec.' % (t3-t2))
        print('format:   %4.2f sec.' % (t4-t3))
        print('check:    %4.2f sec.' % (t5-t4))
        print('total:    %4.2f sec.' % (t5-t1))
    if not ok:
        print('==== fail: %s' % (h))
#@-others
#@@language python
#@@tabwidth -4
#@-leo
