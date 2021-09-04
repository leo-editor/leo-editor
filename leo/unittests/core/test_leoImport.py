# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210904064440.2: * @file ../unittests/core/test_leoImport.py
#@@first
"""Tests of leoImport.py"""
import glob
import importlib
import textwrap
from leo.core import leoGlobals as g
from leo.core.leoTest2 import LeoUnitTest
# Import all tested scanners.
import leo.plugins.importers.coffeescript as cs
import leo.plugins.importers.dart as dart
import leo.plugins.importers.linescanner as linescanner
import leo.plugins.importers.markdown as markdown
import leo.plugins.importers.org as org
import leo.plugins.importers.otl as otl
import leo.plugins.importers.pascal as pascal
import leo.plugins.importers.python as python
import leo.plugins.importers.xml as xml
#@+others
#@+node:ekr.20210904064440.3: ** class TestImporter(LeoUnitTest):
class TestImporter(LeoUnitTest):
    """Test cases for leoImport.py"""
    #@+others
    #@+node:ekr.20210904064548.1: *3* TestImporter.setUp
    def setUp(self):
        super().setUp()
        g.app.loadManager.createAllImporterData()
    #@+node:ekr.20210904065613.1: *3* Tests of @auto
    #@+node:ekr.20210904065459.2: *4* TestImport.test_collapse_all
    def test_collapse_all(self):
        # Not a real unit test.
        c = self.c
        c.contractAllHeadlines()
    #@+node:ekr.20210904065632.1: *4* C tests
    #@+node:ekr.20210904065459.3: *5* TestImport.test_c_class_1
    def test_c_class_1(self):
        c = self.c
        s = textwrap.dedent("""\
            class cTestClass1 {
        
                int foo (int a) {
                    a = 2 ;
                }
        
                char bar (float c) {
                    ;
                }
            }
        """)
        table = (
            'class cTestClass1',
            'int foo',
            'char bar',
        )
        c.importCommands.cUnitTest(c.p, s=s, showTree=True)
        # Check structure
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.4: *5* TestImport.test_c_class_underindented_line
    def test_c_class_underindented_line(self):
        c = self.c
        ic = c.importCommands  
        s = textwrap.dedent("""\
            class cTestClass1 {
        
                int foo (int a) {
            // an underindented line.
                    a = 2 ;
                }
        
                // This should go with the next function.
        
                char bar (float c) {
                    ;
                }
            }
        """)
        table = (
            'class cTestClass1',
            'int foo',
            'char bar',
        )
        ic.cUnitTest(c.p, s=s, showTree=True)
        # Check structure
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.5: *5* TestImport.test_c_comment_follows_arg_list
    def test_c_comment_follows_arg_list(self):
        c = self.c
        ic = c.importCommands
        s = textwrap.dedent("""\
            void
            aaa::bbb::doit
                (
                awk* b
                )
            {
                assert(false);
            }
        
            bool
            aaa::bbb::dothat
                (
                xyz *b
                ) //  <---------------------problem
            {
                return true;
            }
        """)
        table = (
            'void aaa::bbb::doit',
            'bool aaa::bbb::dothat',
        )
        ic.cUnitTest(c.p, s=s, showTree=True)
        # Check structure
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.6: *5* TestImport.test_c_comment_follows_block_delim
    def test_c_comment_follows_block_delim(self):
        c = self.c
        ic = c.importCommands  
        s = textwrap.dedent("""\
            void
            aaa::bbb::doit
                (
                awk* b
                )
            {
                assert(false);
            }
        
            bool
            aaa::bbb::dothat
                (
                xyz *b
                ) 
            {
                return true;
            } //  <---------------------problem
        """)
        table = (
            'void aaa::bbb::doit',
            'bool aaa::bbb::dothat',
        )
        ic.cUnitTest(c.p, s=s) ###, fileName='test', showTree=True)
        # Check structure
        root = c.p.lastChild()
        assert root.h == '@file test', root.h
        p2 = root.firstChild()
        assert p2
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.7: *5* TestImport.test_c_intermixed_blanks_and_tabs
    def test_c_intermixed_blanks_and_tabs(self):
        c = self.c
        ic = c.importCommands
        s = textwrap.dedent("""\
            void
            aaa::bbb::doit
                (
                awk* b  // leading blank
                )
            {
                assert(false); // leading tab
            }
        
        """)
        table = (
            'void aaa::bbb::doit',
        )
       
        ic.cUnitTest(c.p, s=s, showTree=True)
        # Check structure
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
        
    #@+node:ekr.20210904065459.8: *5* TestImport.test_c_old_style_decl_1
    def test_c_old_style_decl_1(self):
        c = self.c
        ic = c.importCommands  
        s = textwrap.dedent("""\
            static void
            ReleaseCharSet(cset)
                CharSet *cset;
            {
                ckfree((char *)cset->chars);
                if (cset->ranges) {
                ckfree((char *)cset->ranges);
                }
            }
        """)
        table = (
            'static void ReleaseCharSet',
        )
        ic.cUnitTest(c.p, s=s, showTree=True)
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.9: *5* TestImport.test_c_old_style_decl_2
    def test_c_old_style_decl_2(self):
        c = self.c
        ic = c.importCommands  
        s = textwrap.dedent("""\
            Tcl_Obj *
            Tcl_NewLongObj(longValue)
                register long longValue;	/* Long integer used to initialize the
                     * new object. */
            {
                return Tcl_DbNewLongObj(longValue, "unknown", 0);
            }
        """)
        table = (
            'Tcl_Obj * Tcl_NewLongObj',
        )
        ic.cUnitTest(c.p, s=s, showTree=True)
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.10: *5* TestImport.test_c_extern
    def test_c_extern(self):
        c = self.c
        ic = c.importCommands  
        s = textwrap.dedent("""\
            extern "C"
            {
            #include "stuff.h"
            void    init(void);
            #include "that.h"
            }
        """)
        table = (
            'extern "C"',
        )
        p = c.p
        ic.cUnitTest(p, s=s, showTree=True)
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904084324.1: *4* Cython tests
    #@+node:ekr.20210904065459.11: *5* TestImport.test_cython_importer
    def test_cython_importer(self):
        c = self.c
        ic = c.importCommands  

        s = textwrap.dedent('''\
            from libc.math cimport pow
        
            cdef double square_and_add (double x):
                """Compute x^2 + x as double.
        
                This is a cdef function that can be called from within
                a Cython program, but not from Python.
                """
                return pow(x, 2.0) + x
        
            cpdef print_result (double x):
                """This is a cpdef function that can be called from Python."""
                print("({} ^ 2) + {} = {}".format(x, x, square_and_add(x)))

        ''')
        table = (
            'Declarations',
            'double',
            'print_result',
        )
        ic.cythonUnitTest(c.p, s=s, showTree=True)
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.12: *5* TestImport.test_c_namespace_indent
    def test_c_namespace_indent(self):
        c = self.c
        s = textwrap.dedent("""\
            namespace {
                class cTestClass1 {
                    ;
                }
            }
        """)
        table = [
            'namespace',
            'class cTestClass1',
        ]
        c.importCommands.cSharpUnitTest(c.p, s=s, showTree=True)
        root = c.p.firstChild()
        assert root.h.endswith('c# namespace indent'), root.h
        p2 = root.firstChild()
        for i, h in enumerate(table):
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.13: *5* TestImport.test_c_namespace_no_indent
    def test_c_namespace_no_indent(self):
        c = self.c
        s = textwrap.dedent("""\
            namespace {
            class cTestClass1 {
                ;
            }
            }
        """)
        c.importCommands.cSharpUnitTest(c.p, s=s, showTree=True)
        table = [
            'namespace',
            'class cTestClass1',
        ]
        root = c.p.firstChild()
        assert root.h.endswith('c# namespace no indent'), root.h
        p2 = root.firstChild()
        for i, h in enumerate(table):
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904122726.1: *4* Coffeescript tests
    #@+node:ekr.20210904065459.14: *5* TestImport.test_coffeescript_1
    def test_coffeescript_1(self):
        c = self.c

        s = textwrap.dedent(r"""\

        # The JavaScript to CoffeeScript compiler.
        # Common usage:
        #
        #
        #     var src = "var square = function(n) { return n * n };"
        #
        #     js2coffee = require('js2coffee');
        #     js2coffee.build(src);
        #     //=> "square = (n) -> n * n"

        # ## Requires
        #
        # Js2coffee relies on Narcissus's parser. (Narcissus is Mozilla's JavaScript
        # engine written in JavaScript).

        {parser} = @Narcissus or require('./narcissus_packed')

        _ = @_ or require('underscore')

        {Types, Typenames, Node} = @NodeExt or require('./node_ext')

        {Code, p, strEscape, unreserve, unshift, isSingleLine, trim, blockTrim,
          ltrim, rtrim, strRepeat, paren, truthy} = @Js2coffeeHelpers or require('./helpers')

        # ## Main entry point
        # This is `require('js2coffee').build()`. It takes a JavaScript source
        # string as an argument, and it returns the CoffeeScript version.
        #
        # 1. Ask Narcissus to break it down into Nodes (`parser.parse`). This
        #    returns a `Node` object of type `script`.
        #
        # 2. This node is now passed onto `Builder#build()`.

        buildCoffee = (str) ->
          str  = str.replace /\r/g, ''
          str += "\n"

          builder    = new Builder
          scriptNode = parser.parse str

          output = trim builder.build(scriptNode)
          (rtrim line for line in output.split('\n')).join('\n')
        # ## Builder class
        # This is the main class that proccesses the AST and spits out streng.
        # See the `buildCoffee()` function above for info on how this is used.

        class Builder
          constructor: ->
            @transformer = new Transformer
          # `build()`
          # The main entry point.

          # This finds the appropriate @builder function for `node` based on it's type,
          # the passes the node onto that function.
          #
          # For instance, for a `function` node, it calls `@builders.function(node)`.
          # It defaults to `@builders.other` if it can't find a function for it.

          build: (args...) ->
            node = args[0]
            @transform node

            name = 'other'
            name = node.typeName()  if node != undefined and node.typeName

            fn  = (@[name] or @other)
            out = fn.apply(this, args)

            if node.parenthesized then paren(out) else out
          # `transform()`
          # Perform a transformation on the node, if a transformation function is
          # available.

          transform: (args...) ->
            @transformer.transform.apply(@transformer, args)
          # `body()`
          # Works like `@build()`, and is used for code blocks. It cleans up the returned
          # code block by removing any extraneous spaces and such.

          body: (node, opts={}) ->
            str = @build(node, opts)
            str = blockTrim(str)
            str = unshift(str)

            if str.length > 0 then str else ""
          # ## The builders
          #
          # Each of these method are passed a Node, and is expected to return
          # a string representation of it CoffeeScript counterpart.
          #
          # These are invoked using the main entry point, `Builder#build()`.

          # `script`
          # This is the main entry point.

          'script': (n, opts={}) ->
            c = new Code

            # *Functions must always be declared first in a block.*
            _.each n.functions,    (item) => c.add @build(item)
            _.each n.nonfunctions, (item) => c.add @build(item)

            c.toString()
          # `property_identifier`
          # A key in an object literal.

          'property_identifier': (n) ->
            str = n.value.toString()

            # **Caveat:**
            # *In object literals like `{ '#foo click': b }`, ensure that the key is
            # quoted if need be.*

            if str.match(/^([_\$a-z][_\$a-z0-9]*)$/i) or str.match(/^[0-9]+$/i)
              str
            else
              strEscape str
          # `identifier`
          # Any object identifier like a variable name.

          'identifier': (n) ->
            if n.value is 'undefined'
              '`undefined`'
            else if n.property_accessor
              n.value.toString()
            else
              unreserve n.value.toString()
          'number': (n) ->
            "#{n.src()}"
          'id': (n) ->
            if n.property_accessor
              n
            else
              unreserve n
          # `id_param`
          # Function parameters. Belongs to `list`.

          'id_param': (n) ->
            if n.toString() in ['undefined']
              "#{n}_"
            else
              @id n
          # `return`
          # A return statement. Has `n.value` of type `id`.

          'return': (n) ->
            if not n.value?
              "return\n"

            else
              "return #{@build(n.value)}\n"
          # `;` (aka, statement)
          # A single statement.

          ';': (n) ->
            # **Caveat:**
            # Some statements can be blank as some people are silly enough to use `;;`
            # sometimes. They should be ignored.

            unless n.expression?
              ""

            else if n.expression.typeName() == 'object_init'
              src = @object_init(n.expression)
              if n.parenthesized
                src
              else
                "#{unshift(blockTrim(src))}\n"

            else
              @build(n.expression) + "\n"
          # `new` + `new_with_args`
          # For `new X` and `new X(y)` respctively.

          'new': (n) -> "new #{@build n.left()}"
          'new_with_args': (n) -> "new #{@build n.left()}(#{@build n.right()})"
          # ### Unary operators

          'unary_plus': (n) -> "+#{@build n.left()}"
          'unary_minus': (n) -> "-#{@build n.left()}"
          # ### Keywords

          'this': (n) -> 'this'
          'null': (n) -> 'null'
          'true': (n) -> 'true'
          'false': (n) -> 'false'
          'void': (n) -> 'undefined'
          'debugger': (n) -> "debugger\n"
          'break': (n) -> "break\n"
          'continue': (n) -> "continue\n"
          # ### Some simple operators

          '~': (n) -> "~#{@build n.left()}"
          'typeof': (n) -> "typeof #{@build n.left()}"
          'index': (n) ->
            right = @build n.right()
            if _.any(n.children, (child) -> child.typeName() == 'object_init' and child.children.length > 1)
              right = "{#{right}}"
            "#{@build n.left()}[#{right}]"
          'throw': (n) -> "throw #{@build n.exception}"
          '!': (n) ->
            target = n.left()
            negations = 1
            ++negations while (target.isA '!') and target = target.left()
            if (negations & 1) and target.isA '==', '!=', '===', '!==', 'in', 'instanceof' # invertible binary operators
              target.negated = not target.negated
              return @build target
            "#{if negations & 1 then 'not ' else '!!'}#{@build target}"
          # ### Binary operators
          # All of these are rerouted to the `binary_operator` @builder.

          # TODO: make a function that generates these functions, invoked like so:
          #   in: binop 'in', 'of'
          #   '+': binop '+'
          #   and so on...

          in: (n) ->    @binary_operator n, 'of'
          '+': (n) ->   @binary_operator n, '+'
          '-': (n) ->   @binary_operator n, '-'
          '*': (n) ->   @binary_operator n, '*'
          '/': (n) ->   @binary_operator n, '/'
          '%': (n) ->   @binary_operator n, '%'
          '>': (n) ->   @binary_operator n, '>'
          '<': (n) ->   @binary_operator n, '<'
          '&': (n) ->   @binary_operator n, '&'
          '|': (n) ->   @binary_operator n, '|'
          '^': (n) ->   @binary_operator n, '^'
          '&&': (n) ->  @binary_operator n, 'and'
          '||': (n) ->  @binary_operator n, 'or'
          '<<': (n) ->  @binary_operator n, '<<'
          '<=': (n) ->  @binary_operator n, '<='
          '>>': (n) ->  @binary_operator n, '>>'
          '>=': (n) ->  @binary_operator n, '>='
          '===': (n) -> @binary_operator n, 'is'
          '!==': (n) -> @binary_operator n, 'isnt'
          '>>>': (n) ->  @binary_operator n, '>>>'
          instanceof: (n) -> @binary_operator n, 'instanceof'
          '==': (n) ->
            # TODO: throw warning
            @binary_operator n, 'is'
          '!=': (n) ->
            # TODO: throw warning
            @binary_operator n, 'isnt'
          'binary_operator': do ->
            INVERSIONS =
              is: 'isnt'
              in: 'not in'
              of: 'not of'
              instanceof: 'not instanceof'
            INVERSIONS[v] = k for own k, v of INVERSIONS
            (n, sign) ->
              sign = INVERSIONS[sign] if n.negated
              "#{@build n.left()} #{sign} #{@build n.right()}"
          # ### Increments and decrements
          # For `a++` and `--b`.

          '--': (n) -> @increment_decrement n, '--'
          '++': (n) -> @increment_decrement n, '++'
          'increment_decrement': (n, sign) ->
            if n.postfix
              "#{@build n.left()}#{sign}"
            else
              "#{sign}#{@build n.left()}"
          # `=` (aka, assignment)
          # For `a = b` (but not `var a = b`: that's `var`).

          '=': (n) ->
            sign = if n.assignOp?
              Types[n.assignOp] + '='
            else
              '='

            "#{@build n.left()} #{sign} #{@build n.right()}"
          # `,` (aka, comma)
          # For `a = 1, b = 2'

          ',': (n) ->
            list = _.map n.children, (item) => @build(item) + "\n"
            list.join('')
          # `regexp`
          # Regular expressions.

          'regexp': (n) ->
            m     = n.value.toString().match(/^\/(.*)\/([a-z]?)/)
            value = m[1]
            flag  = m[2]

            # **Caveat:**
            # *If it begins with `=` or a space, the CoffeeScript parser will choke if
            # it's written as `/=/`. Hence, they are written as `new RegExp('=')`.*

            begins_with = value[0]

            if begins_with in [' ', '=']
              if flag.length > 0
                "RegExp(#{strEscape value}, \"#{flag}\")"
              else
                "RegExp(#{strEscape value})"
            else
              "/#{value}/#{flag}"
          'string': (n) ->
            strEscape n.value
          # `call`
          # A Function call.
          # `n.left` is an `id`, and `n.right` is a `list`.

          'call': (n) ->
            if n.right().children.length == 0
              "#{@build n.left()}()"
            else
              "#{@build n.left()}(#{@build n.right()})"
          # `call_statement`
          # A `call` that's on it's own line.

          'call_statement': (n) ->
            left = @build n.left()

            # **Caveat:**
            # *When calling in this way: `function () { ... }()`,
            # ensure that there are parenthesis around the anon function
            # (eg, `(-> ...)()`).*

            left = paren(left)  if n.left().isA('function')

            if n.right().children.length == 0
              "#{left}()"
            else
              "#{left} #{@build n.right()}"
          # `list`
          # A parameter list.

          'list': (n) ->
            list = _.map(n.children, (item) =>
              if n.children.length > 1
                item.is_list_element = true
              @build(item))

            list.join(", ")
          'delete': (n) ->
            ids = _.map(n.children, (el) => @build(el))
            ids = ids.join(', ')
            "delete #{ids}\n"
          # `.` (scope resolution?)
          # For instances such as `object.value`.

          '.': (n) ->
            # **Caveat:**
            # *If called as `this.xxx`, it should use the at sign (`n.xxx`).*

            # **Caveat:**
            # *If called as `x.prototype`, it should use double colons (`x::`).*

            left  = @build n.left()
            right_obj = n.right()
            right_obj.property_accessor = true
            right = @build right_obj

            if n.isThis and n.isPrototype
              "@::"
            else if n.isThis
              "@#{right}"
            else if n.isPrototype
              "#{left}::"
            else if n.left().isPrototype
              "#{left}#{right}"
            else
              "#{left}.#{right}"
          'try': (n) ->
            c = new Code
            c.add 'try'
            c.scope @body(n.tryBlock)

            _.each n.catchClauses, (clause) =>
              c.add @build(clause)

            if n.finallyBlock?
              c.add "finally"
              c.scope @body(n.finallyBlock)

            c
          'catch': (n) ->
            body_ = @body(n.block)
            return '' if trim(body_).length == 0

            c = new Code

            if n.varName?
              c.add "catch #{n.varName}"
            else
              c.add 'catch'

            c.scope @body(n.block)
            c
          # `?` (ternary operator)
          # For `a ? b : c`. Note that these will always be parenthesized, as (I
          # believe) the order of operations in JS is different in CS.

          '?': (n) ->
            "(if #{@build n.left()} then #{@build n.children[1]} else #{@build n.children[2]})"
          'for': (n) ->
            c = new Code

            if n.setup?
              c.add "#{@build n.setup}\n"

            if n.condition?
              c.add "while #{@build n.condition}\n"
            else
              c.add "loop"

            c.scope @body(n.body)
            c.scope @body(n.update)  if n.update?
            c
          'for_in': (n) ->
            c = new Code

            c.add "for #{@build n.iterator} of #{@build n.object}"
            c.scope @body(n.body)
            c
          'while': (n) ->
            c = new Code

            keyword   = if n.positive then "while" else "until"
            body_     = @body(n.body)

            # *Use `loop` whin something will go on forever (like `while (true)`).*
            if truthy(n.condition)
              statement = "loop"
            else
              statement = "#{keyword} #{@build n.condition}"

            if isSingleLine(body_) and statement isnt "loop"
              c.add "#{trim body_}  #{statement}\n"
            else
              c.add statement
              c.scope body_
            c
          'do': (n) ->
            c = new Code

            c.add "loop"
            c.scope @body(n.body)
            c.scope "break unless #{@build n.condition}"  if n.condition?

            c
          'if': (n) ->
            c = new Code

            keyword = if n.positive then "if" else "unless"
            body_   = @body(n.thenPart)
            n.condition.parenthesized = false

            # *Account for `if (xyz) {}`, which should be `xyz`. (#78)*
            # *Note that `!xyz` still compiles to `xyz` because the `!` will not change anything.*
            if n.thenPart.isA('block') and n.thenPart.children.length == 0 and !n.elsePart?
              console.log n.thenPart
              c.add "#{@build n.condition}\n"

            else if isSingleLine(body_) and !n.elsePart?
              c.add "#{trim body_}  #{keyword} #{@build n.condition}\n"

            else
              c.add "#{keyword} #{@build n.condition}"
              c.scope @body(n.thenPart)

              if n.elsePart?
                if n.elsePart.typeName() == 'if'
                  c.add "else #{@build(n.elsePart).toString()}"
                else
                  c.add "else\n"
                  c.scope @body(n.elsePart)

            c
          'switch': (n) ->
            c = new Code

            c.add "switch #{@build n.discriminant}\n"

            fall_through = false
            _.each n.cases, (item) =>
              if item.value == 'default'
                c.scope "else"
              else
                if fall_through == true
                  c.add ", #{@build item.caseLabel}\n"
                else
                  c.add "  when #{@build item.caseLabel}"
              
              if @body(item.statements).length == 0
                fall_through = true
              else
                fall_through = false
                c.add "\n"
                c.scope @body(item.statements), 2

              first = false

            c
          'existence_check': (n) ->
            "#{@build n.left()}?"
          'array_init': (n) ->
            if n.children.length == 0
              "[]"
            else
              "[ #{@list n} ]"
          # `property_init`
          # Belongs to `object_init`;
          # left is a `identifier`, right can be anything.

          'property_init': (n) ->
            left = n.left()
            right = n.right()
            right.is_property_value = true
            "#{@property_identifier left}: #{@build right}"
          # `object_init`
          # An object initializer.
          # Has many `property_init`.

          'object_init': (n, options={}) ->
            if n.children.length == 0
              "{}"

            else if n.children.length == 1 and not (n.is_property_value or n.is_list_element)
              @build n.children[0]

            else
              list = _.map n.children, (item) => @build item

              c = new Code
              c.scope list.join("\n")
              c = "{#{c}}"  if options.brackets?
              c
          # `function`
          # A function. Can be an anonymous function (`function () { .. }`), or a named
          # function (`function name() { .. }`).

          'function': (n) ->
            c = new Code

            params = _.map n.params, (str) =>
              if str.constructor == String
                @id_param str
              else
                @build str

            if n.name
              c.add "#{n.name} = "

            if n.params.length > 0
              c.add "(#{params.join ', '}) ->"
            else
              c.add "->"

            body = @body(n.body)
            if trim(body).length > 0
              c.scope body
            else
              c.add "\n"

            c
          'var': (n) ->
            list = _.map n.children, (item) =>
              "#{unreserve item.value} = #{if item.initializer? then @build(item.initializer) else 'undefined'}"

            _.compact(list).join("\n") + "\n"
          # ### Unsupported things
          #
          # Due to CoffeeScript limitations, the following things are not supported:
          #
          #  * New getter/setter syntax (`x.prototype = { get name() { ... } };`)
          #  * Break labels (`my_label: ...`)
          #  * Constants

          'other': (n) ->   @unsupported n, "#{n.typeName()} is not supported yet"
          'getter': (n) ->  @unsupported n, "getter syntax is not supported; use __defineGetter__"
          'setter': (n) ->  @unsupported n, "setter syntax is not supported; use __defineSetter__"
          'label': (n) ->   @unsupported n, "labels are not supported by CoffeeScript"
          'const': (n) ->   @unsupported n, "consts are not supported by CoffeeScript"
          'block': (args...) ->
            @script.apply @, args
          # `unsupported()`
          # Throws an unsupported error.
          'unsupported': (node, message) ->
            throw new UnsupportedError("Unsupported: #{message}", node)
        # ## AST manipulation
        # Manipulation of the abstract syntax tree happens here. All these are done on
        # the `build()` step, done just before a node is passed onto `Builders`.

        class Transformer
          transform: (args...) ->
            node = args[0]
            return  if node.transformed?
            type = node.typeName()
            fn = @[type]

            if fn
              fn.apply(this, args)
              node.transformed = true
          'script': (n) ->
            n.functions    = []
            n.nonfunctions = []

            _.each n.children, (item) =>
              if item.isA('function')
                n.functions.push item
              else
                n.nonfunctions.push item

            last = null

            # *Statements don't need parens, unless they are consecutive object
            # literals.*
            _.each n.nonfunctions, (item) =>
              if item.expression?
                expr = item.expression

                if last?.isA('object_init') and expr.isA('object_init')
                  item.parenthesized = true
                else
                  item.parenthesized = false

                last = expr
          '.': (n) ->
            n.isThis      = n.left().isA('this')
            n.isPrototype = (n.right().isA('identifier') and n.right().value == 'prototype')
          ';': (n) ->
            if n.expression?
              # *Statements don't need parens.*
              n.expression.parenthesized = false

              # *If the statement only has one function call (eg, `alert(2);`), the
              # parentheses should be omitted (eg, `alert 2`).*
              if n.expression.isA('call')
                n.expression.type = Typenames['call_statement']
                @call_statement n
          'function': (n) ->
            # *Unwrap the `return`s.*
            n.body.walk last: true, (parent, node, list) ->
              if node.isA('return') and node.value
                # Hax
                lastNode = if list
                  parent[list]
                else
                  parent.children[parent.children.length-1]

                if lastNode
                  lastNode.type = Typenames[';']
                  lastNode.expression = lastNode.value
          'switch': (n) ->
            _.each n.cases, (item) =>
              block = item.statements
              ch    = block.children

              # *CoffeeScript does not need `break` statements on `switch` blocks.*
              delete ch[ch.length-1] if block.last()?.isA('break')
          'call_statement': (n) ->
            if n.children[1]
              _.each n.children[1].children, (child, i) ->
                if child.isA('function') and i != n.children[1].children.length-1
                  child.parenthesized = true
          'return': (n) ->
            # *Doing "return {x:2, y:3}" should parenthesize the return value.*
            if n.value and n.value.isA('object_init') and n.value.children.length > 1
              n.value.parenthesized = true
          'block': (n) ->
            @script n
          'if': (n) ->
            # *Account for `if(x) {} else { something }` which should be `something unless x`.*
            if n.thenPart.children.length == 0 and n.elsePart?.children.length > 0
              n.positive = false
              n.thenPart = n.elsePart
              delete n.elsePart

            @inversible n
          'while': (n) ->
            # *A while with a blank body (`while(x){}`) should be accounted for.*
            # *You can't have empty blocks, so put a `continue` in there. (#78)*
            if n.body.children.length is 0
              n.body.children.push n.clone(type: Typenames['continue'], value: 'continue', children: [])

            @inversible n
          'inversible': (n) ->
            @transform n.condition
            positive = if n.positive? then n.positive else true

            # *Invert a '!='. (`if (x != y)` => `unless x is y`)*
            if n.condition.isA('!=')
              n.condition.type = Typenames['==']
              n.positive = not positive

            # *Invert a '!'. (`if (!x)` => `unless x`)*
            else if n.condition.isA('!')
              n.condition = n.condition.left()
              n.positive = not positive

            else
              n.positive = positive
          '==': (n) ->
            if n.right().isA('null', 'void')
              n.type     = Typenames['!']
              n.children = [n.clone(type: Typenames['existence_check'], children: [n.left()])]
          '!=': (n) ->
            if n.right().isA('null', 'void')
              n.type     = Typenames['existence_check']
              n.children = [n.left()]
        class UnsupportedError
          constructor: (str, src) ->
            @message = str
            @cursor  = src.start
            @line    = src.lineno
            @source  = src.tokenizer.source
          toString: -> @message

        # ## Exports

        @Js2coffee = exports =
          version: '0.1.3'
          build: buildCoffee
          UnsupportedError: UnsupportedError

        module.exports = exports  if module?
        """)

        table = (
            "buildCoffee = (str) ->",
            "class Builder",
            "constructor: ->",
            "build: (args...) ->",
            "transform: (args...) ->",
            "body: (node, opts={}) ->",
            "'script': (n, opts={}) ->",
            "'property_identifier': (n) ->",
            "'identifier': (n) ->",
            "'number': (n) ->",
            "'id': (n) ->",
            "'id_param': (n) ->",
            "'return': (n) ->",
            "';': (n) ->",
            "'new': (n) -> \"new #{@build n.left()}\"",
            "'new_with_args': (n) -> \"new #{@build n.left()}(#{@build n.right()})\"",
            "'unary_plus': (n) -> \"+#{@build n.left()}\"",
            "'unary_minus': (n) -> \"-#{@build n.left()}\"",
            "'this': (n) -> 'this'",
            "'null': (n) -> 'null'",
            "'true': (n) -> 'true'",
            "'false': (n) -> 'false'",
            "'void': (n) -> 'undefined'",
            "'debugger': (n) -> \"debugger\\n\"",
            "'break': (n) -> \"break\\n\"",
            "'continue': (n) -> \"continue\\n\"",
            "'~': (n) -> \"~#{@build n.left()}\"",
            "'typeof': (n) -> \"typeof #{@build n.left()}\"",
            "'index': (n) ->",
            "'throw': (n) -> \"throw #{@build n.exception}\"",
            "'!': (n) ->",
            "in: (n) ->    @binary_operator n, 'of'",
            "'+': (n) ->   @binary_operator n, '+'",
            "'-': (n) ->   @binary_operator n, '-'",
            "'*': (n) ->   @binary_operator n, '*'",
            "'/': (n) ->   @binary_operator n, '/'",
            "'%': (n) ->   @binary_operator n, '%'",
            "'>': (n) ->   @binary_operator n, '>'",
            "'<': (n) ->   @binary_operator n, '<'",
            "'&': (n) ->   @binary_operator n, '&'",
            "'|': (n) ->   @binary_operator n, '|'",
            "'^': (n) ->   @binary_operator n, '^'",
            "'&&': (n) ->  @binary_operator n, 'and'",
            "'||': (n) ->  @binary_operator n, 'or'",
            "'<<': (n) ->  @binary_operator n, '<<'",
            "'<=': (n) ->  @binary_operator n, '<='",
            "'>>': (n) ->  @binary_operator n, '>>'",
            "'>=': (n) ->  @binary_operator n, '>='",
            "'===': (n) -> @binary_operator n, 'is'",
            "'!==': (n) -> @binary_operator n, 'isnt'",
            "'>>>': (n) ->  @binary_operator n, '>>>'",
            "instanceof: (n) -> @binary_operator n, 'instanceof'",
            "'==': (n) ->",
            "'!=': (n) ->",
            "'binary_operator': do ->",
            "'--': (n) -> @increment_decrement n, '--'",
            "'++': (n) -> @increment_decrement n, '++'",
            "'increment_decrement': (n, sign) ->",
            "'=': (n) ->",
            "',': (n) ->",
            "'regexp': (n) ->",
            "'string': (n) ->",
            "'call': (n) ->",
            "'call_statement': (n) ->",
            "'list': (n) ->",
            "'delete': (n) ->",
            "'.': (n) ->",
            "'try': (n) ->",
            "'catch': (n) ->",
            "'?': (n) ->",
            "'for': (n) ->",
            "'for_in': (n) ->",
            "'while': (n) ->",
            "'do': (n) ->",
            "'if': (n) ->",
            "'switch': (n) ->",
            "'existence_check': (n) ->",
            "'array_init': (n) ->",
            "'property_init': (n) ->",
            "'object_init': (n, options={}) ->",
            "'function': (n) ->",
            "'var': (n) ->",
            "'other': (n) ->   @unsupported n, \"#{n.typeName()} is not supported yet\"",
            "'getter': (n) ->  @unsupported n, \"getter syntax is not supported; use __defineGetter__\"",
            "'setter': (n) ->  @unsupported n, \"setter syntax is not supported; use __defineSetter__\"",
            "'label': (n) ->   @unsupported n, \"labels are not supported by CoffeeScript\"",
            "'const': (n) ->   @unsupported n, \"consts are not supported by CoffeeScript\"",
            "'block': (args...) ->",
            "'unsupported': (node, message) ->",
            "class Transformer",
            "transform: (args...) ->",
            "'script': (n) ->",
            "'.': (n) ->",
            "';': (n) ->",
            "'function': (n) ->",
            "n.body.walk last: true, (parent, node, list) ->",
            "'switch': (n) ->",
            "'call_statement': (n) ->",
            "'return': (n) ->",
            "'block': (n) ->",
            "'if': (n) ->",
            "'while': (n) ->",
            "'inversible': (n) ->",
            "'==': (n) ->",
            "'!=': (n) ->",
            "class UnsupportedError",
            "constructor: (str, src) ->",
            "toString: -> @message",
        )
        c.importCommands.coffeeScriptUnitTest(c.p, s=s, showTree=True)
        if 1:
          p2 = c.p.firstChild().firstChild()
          for h in table:
              assert p2.h == h, (p2.h, h)
              p2.moveToThreadNext()
    #@+node:ekr.20210904065459.15: *5* TestImport.test_coffeescript_2
    def test_coffeescript_2(self):
        c = self.c
        s = r'''

        # Js2coffee relies on Narcissus's parser.

        {parser} = @Narcissus or require('./narcissus_packed')

        # Main entry point

        buildCoffee = (str) ->
          str  = str.replace /\r/g, ''
          str += "\n"

          builder    = new Builder
          scriptNode = parser.parse str
        '''
        table = (
            'buildCoffee = (str) ->',
        )
        c.importCommands.coffeeScriptUnitTest(c.p, s=s, showTree=True)
        if 1:
          p2 = c.p.firstChild().firstChild()
          for h in table:
              assert p2.h == h, (p2.h, h)
              p2.moveToThreadNext()
    #@+node:ekr.20210904065459.16: *5* TestImport.test_coffeescript_3
    #@@tabwidth -2 # Required

    def test_coffeescript_3(self):
        c = self.c
        
        s = textwrap.dedent("""\
        class Builder
          constructor: ->
            @transformer = new Transformer
          # `build()`

          build: (args...) ->
            node = args[0]
            @transform node

            name = 'other'
            name = node.typeName()  if node != undefined and node.typeName

            fn  = (@[name] or @other)
            out = fn.apply(this, args)

            if node.parenthesized then paren(out) else out
          # `transform()`

          transform: (args...) ->
            @transformer.transform.apply(@transformer, args)

          # `body()`

          body: (node, opts={}) ->
            str = @build(node, opts)
            str = blockTrim(str)
            str = unshift(str)
            if str.length > 0 then str else ""
        """)
        table = (
          'class Builder',
          'constructor: ->',
          'build: (args...) ->',
          'transform: (args...) ->',
          'body: (node, opts={}) ->',
        )
        c.importCommands.coffeeScriptUnitTest(c.p, s=s, showTree=True)
        if 1:
          p2 = c.p.firstChild().firstChild()
          for h in table:
              assert p2.h == h, (p2.h, h)
              p2.moveToThreadNext()
    #@+node:ekr.20210904065459.17: *4* TestImport.test_dart_hello_world
    def test_dart_hello_world(self):
        c = self.c
        s = r'''
        var name = 'Bob';

        hello() {
          print('Hello, World!');
        }

        // Define a function.
        printNumber(num aNumber) {
          print('The number is $aNumber.'); // Print to console.
        }

        // This is where the app starts executing.
        void main() {
          var number = 42; // Declare and initialize a variable.
          printNumber(number); // Call a function.
        }
        '''
        table = (
            'hello',
            'printNumber',
            'void main',
        )
        c.importCommands.dartUnitTest(c.p, s=s, showTree=True)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
       
    #@+node:ekr.20210904065459.18: *4* TestImport.test_elisp
    def test_elisp(self):
        c = self.c
        ic = c.importCommands
        s = textwrap.dedent("""\
            ;;; comment
            ;;; continue
            ;;;
        
            (defun abc (a b)
               (+ 1 2 3))
        
            ; comm
            (defun cde (a b)
               (+ 1 2 3))
        """)
        table = (
            'defun abc',
            'defun cde',
        )
        ic.elispUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.lastChild()
            assert root.h.startswith('@@'), root.h
            p2 = root.firstChild()
            for h in table:
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904122741.1: *4* HTML tests
    #@+node:ekr.20210904065459.19: *5* TestImport.test_html_lowercase_tags
    def test_html_lowercase_tags(self):
        c = self.c
        s = textwrap.dedent("""\
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class="bodystring">
            <div id='bodydisplay'></div>
            </body>
            </html>
        """)
        table = [
            '<html>',
            '<head>',
            '<body class="bodystring">',
        ]

        c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        root = c.p.firstChild()
        assert root.h.endswith('lowercase tags'), root.h
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        ### p.deleteAllChildren()
       
    #@+node:ekr.20210904065459.20: *5* TestImport.test_html_multiple_tags_on_a_line
    def test_html_multiple_tags_on_a_line(self):
        c = self.c
        
        # tags that cause nodes: html, head, body, div, table, nodeA, nodeB
        # NOT: tr, td, tbody, etc.
        s = textwrap.dedent("""\
        @language html
        <html>
        <body>
            <table id="0">
                <tr valign="top">
                <td width="619">
                <table id="2"> <tr valign="top"> <td width="377">
                    <table id="3">
                    <tr>
                    <td width="368">
                    <table id="4">
                        <tbody id="5">
                        <tr valign="top">
                        <td width="550">
                        <table id="6">
                            <tbody id="6">
                            <tr>
                            <td class="blutopgrabot"><a href="href1">Listing Standards</a> | <a href="href2">Fees</a> | <strong>Non-compliant Issuers</strong> | <a href="href3">Form 25 Filings</a> </td>
                            </tr>
                            </tbody>
                        </table>
                        </td>
                        </tr><tr>
                        <td width="100%" colspan="2">
                        <br />
                        </td>
                        </tr>
                        </tbody>
                    </table>	
                    </td>
                    </tr>
                </table>
                <!-- View First part --> </td> <td width="242"> <!-- View Second part -->
                <!-- View Second part --> </td> </tr></table>
            <DIV class="webonly">
                <script src="/scripts/footer.js"></script>
            </DIV>
            </td>
            </tr>
            <script language="JavaScript1.1">var SA_ID="nyse;nyse";</script>
            <script language="JavaScript1.1" src="/scripts/stats/track.js"></script>
            <noscript><img src="/scripts/stats/track.js" height="1" width="1" alt="" border="0"></noscript>
        </body>
        </html>
        """)

        # c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        table = (
            '<html>',
            '<body>',
            '<table id="0">',
        )
      
        c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        ### p.deleteAllChildren()
        
    #@+node:ekr.20210904065459.21: *5* TestImport.test_html_multple_node_completed_on_a_line
    def test_html_multple_node_completed_on_a_line(self):
        c = self.c
       
        s = textwrap.dedent("""\
            <!-- tags that start nodes: html,body,head,div,table,nodeA,nodeB -->
            <html><head>headline</head><body>body</body></html>
        """)
        table = (
            # The new xml scanner doesn't generate any new nodes,
            # because the scan state hasn't changed at the end of the line!
        )
        c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            assert p2 and p2.h == h, (p2 and p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.22: *5* TestImport.test_html_multple_node_starts_on_a_line
    def test_html_multple_node_starts_on_a_line(self):
        c = self.c
        s = '''
        @language html
        <html>
        <head>headline</head>
        <body>body</body>
        </html>
        '''
        table = (
            '<html>',
        )
        c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            assert p2 and p2.h == h, (p2 and p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.23: *5* TestImport.test_html_underindented_comment
    def test_html_underindented_comment(self):
        c = self.c
        s = r'''
        <td width="550">
        <table cellspacing="0" cellpadding="0" width="600" border="0">
            <td class="blutopgrabot" height="28"></td>
        
            <!-- The indentation of this element causes the problem. -->
            <table>
        
        <!--
        <div align="center">
        <iframe src="http://www.amex.com/atamex/regulation/listingStatus/index.jsp"</iframe>
        </div>
        -->

        </table>
        </table>

        <p>Paragraph</p>
        </td>

        '''
        table = (
            '<table cellspacing="0" cellpadding="0" width="600" border="0">',
            '<table>',
        )
        c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()

        
    #@+node:ekr.20210904065459.24: *5* TestImport.test_html_uppercase_tags
    def test_html_uppercase_tags(self):
        c = self.c
        s = textwrap.dedent("""\
            <HTML>
            <HEAD>
                <title>Bodystring</title>
            </HEAD>
            <BODY class='bodystring'>
            <DIV id='bodydisplay'></DIV>
            </BODY>
            </HTML>
        """)
        c.importCommands.htmlUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.25: *5* TestImport.test_html_improperly_nested_tags
    def test_html_improperly_nested_tags(self):
        c = self.c
        s = textwrap.dedent("""\
            <body>
        
            <!-- OOPS: the div and p elements not properly nested.-->
            <!-- OOPS: this table got generated twice. -->
        
            <p id="P1">
            <div id="D666">Paragraph</p> <!-- P1 -->
            <p id="P2">
        
            <TABLE id="T666"></TABLE></p> <!-- P2 -->
            </div>
            </p> <!-- orphan -->
        
            </body>
        """)
        table = (
            ('<body>'),
            ('<div id="D666">'),
        )

        c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
            
    #@+node:ekr.20210904065459.26: *5* TestImport.test_html_improperly_terminated_tags
    def test_html_improperly_terminated_tags(self):
        c = self.c
        s = r'''
        <html>

        <head>
            <!-- oops: link elements terminated two different ways -->
            <link id="L1">
            <link id="L2">
            <link id="L3" />
            <link id='L4' />
        
            <title>TITLE</title>
        
        <!-- oops: missing tags. -->
        '''
        table = (
            '<html>',
            '<head>',
        )
        c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        p2 = c.p.firstChild().firstChild()
        for i, h in enumerate(table):
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.27: *5* TestImport.test_html_improperly_terminated_tags2
    def test_html_improperly_terminated_tags2(self):
        c = self.c
        s = '''
        <html>
        <head>
            <!-- oops: link elements terminated two different ways -->
            <link id="L1">
            <link id="L2">
            <link id="L3" />
            <link id='L4' />
        
            <title>TITLE</title>
        
        </head>
        </html>
        '''
        table = ('<html>', '<head>') # , '<link id="L1">'
        c.importCommands.htmlUnitTest(c.p, s=s, showTree=True)
        p2 = c.p.firstChild().firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
    #@+node:ekr.20210904065459.28: *5* TestImport.test_html_brython
    def test_html_brython(self):
        c = self.c
        # https://github.com/leo-editor/leo-editor/issues/479
        s = textwrap.dedent('''\
            <!DOCTYPE html>
            <html>
            <head>
            <script type="text/python3">
            """Code for the header menu"""
            from browser import document as doc
            from browser import html
            import header
        
            qs_lang,language = header.show()
        
            doc["content"].html = doc["content_%s" %language].html
        
            if qs_lang:
                doc["c_%s" %qs_lang].href += "?lang=%s" %qs_lang
        
            def ch_lang(ev):
                sel = ev.target
                new_lang = sel.options[sel.selectedIndex].value
                doc.location.href = 'index.html?lang=%s' %new_lang
        
            for elt in doc[html.SELECT]:
                if elt.id.startswith('change_lang_'):
                    doc[elt.id].bind('change',ch_lang)
            </script>
        
            <script type="text/python3">
            """Code for the clock"""
        
            import time
            import math
            import datetime
        
            from browser import document as doc
            import browser.timer
        
            sin,cos = math.sin,math.cos
            width,height = 250,250 # canvas dimensions
            ray = 100 # clock ray
        
            def needle(angle,r1,r2,color="#000000"):
                # draw a needle at specified angle in specified color
                # r1 and r2 are percentages of clock ray
                x1 = width/2-ray*cos(angle)*r1
                y1 = height/2-ray*sin(angle)*r1
                x2 = width/2+ray*cos(angle)*r2
                y2 = height/2+ray*sin(angle)*r2
                ctx.beginPath()
                ctx.strokeStyle = color
                ctx.moveTo(x1,y1)
                ctx.lineTo(x2,y2)
                ctx.stroke()
        
            def set_clock():
                # erase clock
                ctx.beginPath()
                ctx.fillStyle = "#FFF"
                ctx.arc(width/2,height/2,ray*0.89,0,2*math.pi)
                ctx.fill()
            
                # redraw hours
                show_hours()
        
                # print day
                now = datetime.datetime.now()
                day = now.day
                ctx.font = "bold 14px Arial"
                ctx.textAlign = "center"
                ctx.textBaseline = "middle"
                ctx.fillStyle="#FFF"
                ctx.fillText(day,width*0.7,height*0.5)
        
                # draw needles for hour, minute, seconds    
                ctx.lineWidth = 3
                hour = now.hour%12 + now.minute/60
                angle = hour*2*math.pi/12 - math.pi/2
                needle(angle,0.05,0.5)
                minute = now.minute
                angle = minute*2*math.pi/60 - math.pi/2
                needle(angle,0.05,0.85)
                ctx.lineWidth = 1
                second = now.second+now.microsecond/1000000
                angle = second*2*math.pi/60 - math.pi/2
                needle(angle,0.05,0.85,"#FF0000") # in red
            
            def show_hours():
                ctx.beginPath()
                ctx.arc(width/2,height/2,ray*0.05,0,2*math.pi)
                ctx.fillStyle = "#000"
                ctx.fill()
                for i in range(1,13):
                    angle = i*math.pi/6-math.pi/2
                    x3 = width/2+ray*cos(angle)*0.75
                    y3 = height/2+ray*sin(angle)*0.75
                    ctx.font = "20px Arial"
                    ctx.textAlign = "center"
                    ctx.textBaseline = "middle"
                    ctx.fillText(i,x3,y3)
                # cell for day
                ctx.fillStyle = "#000"
                ctx.fillRect(width*0.65,height*0.47,width*0.1,height*0.06)
        
            canvas = doc["clock"]
            # draw clock border
            if hasattr(canvas,'getContext'):
                ctx = canvas.getContext("2d")
                ctx.beginPath()
                ctx.lineWidth = 10
                ctx.arc(width/2,height/2,ray,0,2*math.pi)
                ctx.stroke()
            
                for i in range(60):
                    ctx.lineWidth = 1
                    if i%5 == 0:
                        ctx.lineWidth = 3
                    angle = i*2*math.pi/60 - math.pi/3
                    x1 = width/2+ray*cos(angle)
                    y1 = height/2+ray*sin(angle)
                    x2 = width/2+ray*cos(angle)*0.9
                    y2 = height/2+ray*sin(angle)*0.9
                    ctx.beginPath()
                    ctx.moveTo(x1,y1)
                    ctx.lineTo(x2,y2)
                    ctx.stroke()
                browser.timer.set_interval(set_clock,100)
                show_hours()
            else:
                doc['navig_zone'].html = "On Internet Explorer 9 or more, use a Standard rendering engine"
            </script>
        
            <title>Brython</title>
            <link rel="stylesheet" href="Brython_files/doc_brython.css">
            </head>
            <body onload="brython({debug:1, cache:'none'})">
            </body></html>
        ''')
        table = (
            '<html>',
            '<head>', 
            '<body onload="brython({debug:1, cache:\'none\'})">',
        )
        c.importCommands.htmlUnitTest(c.p, s=s) ###, showTree=True)
        p2 = c.p.firstChild().firstChild()
        assert p2
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
            
    #@+node:ekr.20210904065459.29: *4* TestImport.test_ini_test_1
    def test_ini_test_1(self):
        c = self.c
        s = r'''; last modified 1 April 2001 by John Doe
        [owner]
        name=John Doe
        organization=Acme Widgets Inc.

        ; [ not a section ]

        [database]
        server=192.0.2.62
            ; use IP address
        port=143
        file = "payroll.dat"
        '''

        table = ('[owner]', '[database]')
        c.importCommands.iniUnitTest(c.p, s=s, showTree=True)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
        
    #@+node:ekr.20210904122815.1: *4* Java tests
    #@+node:ekr.20210904065459.30: *5* TestImport.test_from_AdminPermission_java
    def test_from_AdminPermission_java(self):
        c = self.c
        ic = c.importCommands  
        s = textwrap.dedent("""\
            /**
             * Indicates the caller's authority to perform lifecycle operations on
             */
        
            public final class AdminPermission extends BasicPermission
            {
                /**
                 * Creates a new <tt>AdminPermission</tt> object.
                 */
                public AdminPermission()
                {
                    super("AdminPermission");
                }
            }
        """)
        table = (
            'public final class AdminPermission extends BasicPermission',
            'public AdminPermission',
        )
        ic.javaUnitTest(c.p, s=s, showTree=True)
        if 1: # Check structure
            root = c.p.lastChild()
            assert root.h.startswith('@@'), root.h
            p2 = root.firstChild()
            for i, h in enumerate(table):
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
        
    #@+node:ekr.20210904065459.31: *5* TestImport.test_from_BundleException_java
    def test_from_BundleException_java(self):
        c = self.c
        ic = c.importCommands  
        ### @language python
        ### @tabwidth 8
            # Must be in this node when run externally.
        s = textwrap.dedent("""\
            /*
             * $Header: /cvs/leo/test/unitTest.leo,v 1.247 2008/02/14 14:59:04 edream Exp $
             * 
             * Copyright (c) OSGi Alliance (2000, 2005). All Rights Reserved.
             * 
             * This program and the accompanying materials are made available under the
             * terms of the Eclipse Public License v1.0 which accompanies this 
             * distribution, and is available at http://www.eclipse.org/legal/epl-v10.html.
             */
        
            package org.osgi.framework;
        
            /**
             * A Framework exception used to indicate that a bundle lifecycle problem
             * occurred.
             * 
             * <p>
             * <code>BundleException</code> object is created by the Framework to denote
             * an exception condition in the lifecycle of a bundle.
             * <code>BundleException</code>s should not be created by bundle developers.
             * 
             * <p>
             * This exception is updated to conform to the general purpose exception
             * chaining mechanism.
             * 
             * @version $Revision: 1.247 $
             */
        
            public class BundleException extends Exception {
                static final long	serialVersionUID	= 3571095144220455665L;
                /**
                 * Nested exception.
                 */
                private Throwable	cause;
        
                /**
                 * Creates a <code>BundleException</code> that wraps another exception.
                 * 
                 * @param msg The associated message.
                 * @param cause The cause of this exception.
                 */
                public BundleException(String msg, Throwable cause) {
                    super(msg);
                    this.cause = cause;
                }
            }

        """)
        table = (
            'public class BundleException extends Exception',
            'public BundleException',
        )
        ic.javaUnitTest(c.p, s=s, showTree=True)
        if 1: # Check structure
            root = c.p.lastChild()
            assert root.h.startswith('@@'), root.h
            p2 = root.firstChild()
            for i, h in enumerate(table):
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
       
    #@+node:ekr.20210904065459.32: *5* TestImport.test_java_interface_test1
    def test_java_interface_test1(self):
        c = self.c
        ic = c.importCommands  
        s = textwrap.dedent("""\
            interface Bicycle {
                void changeCadence(int newValue);
                void changeGear(int newValue);
            }
        """)
        table = (
            'interface Bicycle',
        )
        ic.javaUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.lastChild()
            assert root.h.startswith('@@'), root.h
            p2 = root.firstChild()
            for i, h in enumerate(table):
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.33: *5* TestImport.test_java_interface_test2
    def test_java_interface_test2(self):
        c = self.c
        ic = c.importCommands  

        s = textwrap.dedent("""\
            interface Bicycle {
            void changeCadence(int newValue);
            void changeGear(int newValue);
            }
        """)
        table = (
            'interface Bicycle',
        )
        ic.javaUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.lastChild()
            assert root.h.startswith('@@'), root.h
            p2 = root.firstChild()
            for i, h in enumerate(table):
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904122826.1: *4* Javascript tests
    #@+node:ekr.20210904065459.34: *5* TestImport.test_Javascript_regex_1
    def test_Javascript_regex_1(self):
        c = self.c
        s = textwrap.dedent("""\
            String.prototype.toJSONString = function()
            {
                if(/["\\\\\\x00-\\x1f]/.test(this))
                    return '"' + this.replace(/([\\x00-\\x1f\\"])/g,replaceFn) + '"';
        
                return '"' + this + '"';
            };
        """)
        c.importCommands.javaScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.35: *5* TestImport.test_Javascript_3
    def test_Javascript_3(self):
        c = self.c
        s = textwrap.dedent("""\
            // Restarting
            function restart()
            {
                invokeParamifier(params,"onstart");
                if(story.isEmpty()) {
                    var tiddlers = store.filterTiddlers(store.getTiddlerText("DefaultTiddlers"));
                    for(var t=0; t<tiddlers.length; t++) {
                        story.displayTiddler("bottom",tiddlers[t].title);
                    }
                }
                window.scrollTo(0,0);
            }
        """)
        c.importCommands.javaScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.36: *5* TestImport.test_Javascript_4
    def test_Javascript_4(self):
        c = self.c
        s = textwrap.dedent("""\
            var c3 = (function () {
                "use strict";
        
                // Globals
                var c3 = { version: "0.0.1"   };
        
                c3.someFunction = function () {
                    console.log("Just a demo...");
                };
        
                return c3;
            }());
        """)
        c.importCommands.javaScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.37: *5* TestImport.test_Javascript_5
    def test_Javascript_5(self):
        c = self.c
        s = textwrap.dedent("""\
            var express = require('express');
        
            var app = express.createServer(express.logger());
        
            app.get('/', function(request, response) {
            response.send('Hello World!');
            });
        
            var port = process.env.PORT || 5000;
            app.listen(port, function() {
            console.log("Listening on " + port);
            });
        """)
        c.importCommands.javaScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.38: *5* TestImport.test_Javascript_639_many_top_level_nodes
    def test_Javascript_639_many_top_level_nodes(self):
        c = self.c
        s = textwrap.dedent("""\
            // Easy test for #639: https://github.com/leo-editor/leo-editor/issues/639
        
            //=============================================================================
            // rpg_core.js v1.3.0
            //=============================================================================
        
            //-----------------------------------------------------------------------------
            /**
             * This is not a class, but contains some methods that will be added to the
             * standard Javascript objects.
             *
             * @class JsExtensions
             */
            function JsExtensions() {
                throw new Error('This is not a class');
            }
        
            /**
             * Returns a number whose value is limited to the given range.
             *
             * @method Number.prototype.clamp
             * @param {Number} min The lower boundary
             * @param {Number} max The upper boundary
             * @return {Number} A number in the range (min, max)
             */
            Number.prototype.clamp = function(min, max) {
                return Math.min(Math.max(this, min), max);
            };
        """)
        c.importCommands.javaScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.39: *5* TestImport.test_Javascript_639_acid_test_1
    def test_Javascript_639_acid_test_1(self):
        c = self.c
        s = textwrap.dedent("""\
            // Acid test for #639: https://github.com/leo-editor/leo-editor/issues/639
            require([
                'jquery',
            ], function(
                    $,
                    termjs,
            ){
                var header = $("#header")[0];
                function calculate_size() {
                    var height = $(window).height() - header.offsetHeight;
                }
                page.show_header();
                window.onresize = function() {
                  terminal.socket.send(JSON.stringify([
                        "set_size", geom.rows, geom.cols,
                        $(window).height(), $(window).width()])
                    );
                };
                window.terminal = terminal;
            });
        """)
        c.importCommands.javaScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.40: *5* TestImport.test_Javascript_639_acid_test_2
    def test_Javascript_639_acid_test_2(self):
        c = self.c
        s = textwrap.dedent("""\
            // Acid test for #639: https://github.com/leo-editor/leo-editor/issues/639
            require([
                'jquery',
            ], function(
                    $,
                    termjs,
            ){
                var head = "head"
                function f1() {
                    var head1 = "head1"
                    function f11 () {
                        var v11 ="v1.1"
                    }
                    var middle1 = "middle1"
                    function f12 () {
                        var v12 ="v1.2"
                    }
                    var tail1 = "tail1"
                }
                var middle = "middle"
                function f2() {
                    var head2 = "head2"
                    function f21 () {
                        var v21 ="2.1"
                    }
                    var middle2 = "middle2"
                    function f22 () {
                        var v22 = "2.2.1"
                    }
                    var tail2 = "tail2"
                }
                var tail = "tail"
            });
        """)
        c.importCommands.javaScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904122840.1: *4* Org mode tests
    #@+node:ekr.20210904065459.41: *5* TestImport.test_org_pattern
    def test_org_pattern(self):
        c = self.c
        x = org.Org_Importer(c.importCommands, atAuto=False)    
        pattern = x.org_pattern
        table = (
            # 'body * line',
            '* line 1',
            '** level 2',
        )
        for line in table:
            m = pattern.match(line)
            # print('%20s ==> (%r)(%r)' % (line, m and m.group(1), m and m.group(2)))
            assert m, repr(line)
    #@+node:ekr.20210904065459.42: *5* TestImport.test_org_1
    def test_org_1(self):
        c = self.c
        s = textwrap.dedent("""\
            * Section 1
            Sec 1.
            * Section 2
            Sec 2.
            ** Section 2-1
            Sec 2.1
            *** Section 2-1-1
            Sec 2.1.1
            * Section 3
            ** Section 3.1
            Sec 3.1
        """)
        table = (
            'Section 1',
            'Section 2', 'Section 2-1', 'Section 2-1-1',
            'Section 3', 'Section 3.1',
        )
        c.importCommands.orgUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.firstChild()
            p2 = root.firstChild()
            for h in table:
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.43: *5* TestImport.test_org_tags
    def test_org_tags(self):
        c = self.c
        s = textwrap.dedent("""\
            * Section 1 :tag1:
            * Section 2 :tag2:
            * Section 3 :tag3:tag4:
        """)
        table = (
            'Section 1 :tag1:',
            'Section 2 :tag2:',
            'Section 3 :tag3:tag4:',
        )
        c.importCommands.orgUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.firstChild()
            p2 = root.firstChild()
            for h in table:
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.44: *5* TestImport.test_org_intro
    def test_org_intro(self):
        c = self.c
        s = textwrap.dedent("""\
            Intro line.
            * Section 1
            Sec 1.
            * Section 2
            Sec 2.
        """)
        table = (
            'Section 1',
            'Section 2',
        )
        c.importCommands.orgUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.firstChild()
            p2 = root.firstChild()
            for h in table:
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.45: *5* TestImport.test_org_552
    def test_org_552(self):
        c = self.c
        s = textwrap.dedent("""\
            * Events
              :PROPERTIES:
              :CATEGORY: events
              :END:
            ** 整理个人生活
            *** 每周惯例
        """)
        table = (
            'Events',
            '整理个人生活',
            '每周惯例',
        )
        c.importCommands.orgUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.firstChild()
            p2 = root.firstChild()
            for h in table:
                assert p2.h == g.toUnicode(h), (p2.h, g.toUnicode(h))
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.46: *5* TestImport.test_org_1074
    def test_org_1074(self):
        c = self.c
        s = textwrap.dedent("""\
            *  Test
            First line.
        """)
        table = (
            ' Test',
        )
        c.importCommands.orgUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.firstChild()
            p2 = root.firstChild()
            for h in table:
                assert p2.h == g.toUnicode(h), (p2.h, g.toUnicode(h))
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904065459.47: *5* TestImport.test_org_placeholder
    def test_org_placeholder(self):
        c = self.c
        ic = c.importCommands 
        # insert test for org here.
        s = textwrap.dedent("""\
            * Section 1
            Sec 1.
            * Section 2
            Sec 2.
            ** Section 2-1
            Sec 2.1
            *** Section 2-1-1
            Sec 2.1.1
            * Section 3
            ****** Section 3-1-1-1-1-1
            : Sec 3-1-1-1-1-1
            ** Section 3.1
            Sec 3.1
        """)
        table = (
            'Section 1',
            'Section 2', 'Section 2-1', 'Section 2-1-1',
            'Section 3',
            'placeholder', 'placeholder', 'placeholder', 'placeholder',
            'Section 3-1-1-1-1-1',
            'Section 3.1',
        )
        g.app.suppressImportChecks = True
        ic.orgUnitTest(c.p, s=s, showTree=True)
        root = c.p.firstChild()
        p2 = root.firstChild()
        for h in table:
            assert p2.h == h, (p2.h, h)
            p2.moveToThreadNext()
        assert not root.isAncestorOf(p2), p2.h # Extra nodes
    #@+node:ekr.20210904122853.1: *4* Otl tests
    #@+node:ekr.20210904065459.48: *5* TestImport.test_otl_vim_outline_mode
    def test_otl_vim_outline_mode(self):
        c = self.c
        x = otl.Otl_Importer(c.importCommands, atAuto=False)    
        pattern = x.otl_pattern
        table = (
            'body line',
            '\tline 1',
            '  \tlevel 2',
        )
        for line in table:
            m = pattern.match(line)
            # print('%20r ==> (%r)(%r)' % (
                # line, m and m.group(1), m and m.group(2)))
            assert m
    #@+node:ekr.20210904065459.49: *5* TestImport.test_otl_1
    def test_otl_1(self):
        c = self.c
        ### @tabwidth 4 # Required
        s = textwrap.dedent("""\
            preamble.
            Section 1
            : Sec 1.
            Section 2
            : Sec 2.
            \tSection 2-1
            : Sec 2-1
            \t\tSection 2-1-1
            : Sect 2-1-1
            Section 3
            : Sec 3
            \tSection 3.1
            : Sec 3.1
        """)
        table = (
            'Section 1',
            'Section 2', 'Section 2-1', 'Section 2-1-1',
            'Section 3', 'Section 3.1',
        )
        c.importCommands.otlUnitTest(c.p, s=s, showTree=True)
        if 0:
            root = c.p.firstChild()
            p2 = root.firstChild()
            for h in table:
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
       
    #@+node:ekr.20210904065459.50: *4* TestImport.test_pascal_to_delphi_interface
    def test_pascal_to_delphi_interface(self):
        c = self.c
        ic = c.importCommands  
        s = '''
        unit Unit1;

        interface

        uses
        Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls,
        Forms,
        Dialogs;

        type
        TForm1 = class(TForm)
        procedure FormCreate(Sender: TObject);
        private
        { Private declarations }
        public
        { Public declarations }
        end;

        var
        Form1: TForm1;

        implementation

        {$R *.dfm}

        procedure TForm1.FormCreate(Sender: TObject);
        var
        x,y: double;
        begin
        x:= 4;
        Y := x/2;
        end;

        end. // interface
        '''
        table = (
            'interface',
            'procedure FormCreate',
            'procedure TForm1.FormCreate',
        )
        ic.pascalUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.lastChild()
            assert root.h.startswith('@@'), root.h
            p2 = root.firstChild()
            for i, h in enumerate(table):
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
       
    #@+node:ekr.20210904122909.1: *4* Perl tests
    #@+node:ekr.20210904065459.51: *5* TestImport.test_perl_1
    def test_perl_1(self):
        c = self.c
        s = textwrap.dedent("""\
            #!/usr/bin/perl
        
            # Function definition
            sub Hello{
               print "Hello, World!\n";
            }
        
            sub Test{
               print "Test!\n";
            }
            "\N{LATIN SMALL LIGATURE FI}" =~ /fi/i;
        
            $bar = "foo";
            if ($bar =~ /foo/){
               print "Second time is matching\n";
            }else{
               print "Second time is not matching\n";
            }
        
            # Function call
            Hello();
        """)
        c.importCommands.perlUnitTest(c.p, s=s, showTree=True)
    #@+node:ekr.20210904065459.52: *5* TestImport.test_perlpod_comment
    def test_perlpod_comment(self):
        c = self.c
        s = textwrap.dedent("""\
            #!/usr/bin/perl
                  
            sub Test{
               print "Test!\n";
            }
        
            =begin comment
            sub World {
                print "This is not a funtion!"
            }
            =cut
        
            # Function definition
            sub Hello{
               print "Hello, World!\n";
            }
        """)
        c.importCommands.perlUnitTest(c.p, s=s, showTree=True)
    #@+node:ekr.20210904065459.53: *5* TestImport.test_perl_multi_line_string
    def test_perl_multi_line_string(self):
        c = self.c
        s = textwrap.dedent("""\
            #!/usr/bin/perl
        
            # This would print with a line break in the middle
            print "Hello
        
            sub World {
                print "This is not a funtion!"
            }
        
            world\n";
        """)
        c.importCommands.perlUnitTest(c.p, s=s, showTree=True)
    #@+node:ekr.20210904065459.54: *5* TestImport.test_perl_regex_1
    def test_perl_regex_1(self):
        c = self.c
        # ('len',   'tr///', '/',       context,  0,       0,       0),
        # ('len',   's///',  '/',       context,  0,       0,       0),
        # ('len',   'm//',   '/',       context,  0,       0,       0),
        # ('len',   '/',     '/',       '',       0,       0,       0),
        s = textwrap.dedent("""\
            #!/usr/bin/perl
        
            sub test1 {
                s = /{/g;
            }
        
            sub test2 {
                s = m//{/;
            }
        
            sub test3 {
                s = s///{/;
            }
        
            sub test4 {
                s = tr///{/;
            }
        """)
        c.importCommands.perlUnitTest(c.p, s=s, showTree=True)
       
    #@+node:ekr.20210904065459.55: *5* TestImport.test_perl_regex_2
    def test_perl_regex_2(self):
        c = self.c
        s = textwrap.dedent("""\
            #!/usr/bin/perl
        
            sub test1 {
                s = /}/g;
            }
        
            sub test2 {
                s = m//}/;
            }
        
            sub test3 {
                s = s///}/;
            }
        
            sub test4 {
                s = tr///}/;
            }
        """)
        table = (
            'sub test1',
            'sub test2',
            'sub test3',
            'sub test4'
        )
        c.importCommands.perlUnitTest(c.p, s=s, showTree=True)
        if 1:
            root = c.p.lastChild()
            assert root.h.startswith('@@'), root.h
            p2 = root.firstChild()
            for h in table:
                assert p2.h == h, (p2.h, h)
                p2.moveToThreadNext()
            assert not root.isAncestorOf(p2), p2.h # Extra nodes
      
    #@+node:ekr.20210904122920.1: *4* PHP tests
    #@+node:ekr.20210904065459.56: *5* TestImport.test_php_import_class
    def test_php_import_class(self):
        c = self.c
        s = textwrap.dedent("""\
            <?php
        
            $type = 'cc';
            $obj = new $type; // outputs "hi!"
        
            class cc {
                function __construct() {
                    echo 'hi!';
                }
            }
        
            ?>
        """)
        c.importCommands.phpUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.57: *5* TestImport.test_php_import_conditional_class
    def test_php_import_conditional_class(self):
        c = self.c
        s = textwrap.dedent("""\
            <?php
        
            if (expr) {
                class cc {
                    // version 1
                }
            } else {
                class cc {
                    // version 2
                }
            }
        
            ?>
        """)
        c.importCommands.phpUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.58: *5* TestImport.test_php_import_classes__functions
    def test_php_import_classes__functions(self):
        c = self.c
        s = textwrap.dedent("""\
            <?php
            class Enum {
                protected $self = array();
                public function __construct( /*...*/ ) {
                    $args = func_get_args();
                    for( $i=0, $n=count($args); $i<$n; $i++ )
                        $this->add($args[$i]);
                }
        
                public function __get( /*string*/ $name = null ) {
                    return $this->self[$name];
                }
        
                public function add( /*string*/ $name = null, /*int*/ $enum = null ) {
                    if( isset($enum) )
                        $this->self[$name] = $enum;
                    else
                        $this->self[$name] = end($this->self) + 1;
                }
            }
        
            class DefinedEnum extends Enum {
                public function __construct( /*array*/ $itms ) {
                    foreach( $itms as $name => $enum )
                        $this->add($name, $enum);
                }
            }
        
            class FlagsEnum extends Enum {
                public function __construct( /*...*/ ) {
                    $args = func_get_args();
                    for( $i=0, $n=count($args), $f=0x1; $i<$n; $i++, $f *= 0x2 )
                        $this->add($args[$i], $f);
                }
            }
            ?>
        """)
        c.importCommands.phpUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.59: *5* TestImport.test_php_here_doc
    def test_php_here_doc(self):
        c = self.c
        s = textwrap.dedent("""\
            <?php
            class foo {
                public $bar = <<<EOT
            a test.
            bar
            EOT;
            }
            ?>
        """)
        c.importCommands.phpUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.60: *4* TestImport.test_i_scan_state_for_python_
    def test_i_scan_state_for_python_(self):
        c = self.c
        c = self.c
        # A list of dictionaries.
        if 0:
            tests = [
                # g.Bunch(line='s = "\\""', ctx=('', '')),
                g.Bunch(line='\\\n'),
            ]
        else:
            tests = [
                g.Bunch(line='\n'),
                g.Bunch(line='\\\n'),
                g.Bunch(line='s = "\\""', ctx=('', '')), # empty string.
                g.Bunch(line="s = '\\''", ctx=('', '')), # empty string.
                g.Bunch(line='# comment'),
                g.Bunch(line='  # comment'),
                g.Bunch(line='    # comment'),
                g.Bunch(line='a = "string"'),
                g.Bunch(line='a = "Continued string', ctx=('', '"')),
                g.Bunch(line='end of continued string"', ctx=('"', '')),
                g.Bunch(line='a = """Continued docstring', ctx=('', '"""')),
                g.Bunch(line='a = """#', ctx=('', '"""')),
                g.Bunch(line='end of continued string"""', ctx=('"""', '')),
                g.Bunch(line="a = '''Continued docstring", ctx=('', "'''")),
                g.Bunch(line="end of continued string'''", ctx=("'''", '')),
                g.Bunch(line='a = {[(')
            ]
        if hasattr(python, 'Py_Importer'):
            importer = python.Py_Importer(c.importCommands)
            importer.test_scan_state(tests, State=python.Python_ScanState)
        else:
            self.skipTest('Skipping test for new python importer')
    #@+node:ekr.20210904122944.1: *4* Python tests
    #@+node:ekr.20210904065459.61: *5* TestImport.test_leoApp_fail
    def test_leoApp_fail(self):
        c = self.c
        ic = c.importCommands
        
        s = '''
        def isValidPython(self):
            if sys.platform == 'cli':
                return True
            minimum_python_version = '2.6'
            message = """\
        Leo requires Python %s or higher.
        You may download Python from
        http://python.org/download/
        """ % minimum_python_version
            try:
                version = '.'.join([str(sys.version_info[i]) for i in (0, 1, 2)])
                ok = g.CheckVersion(version, minimum_python_version)
                if not ok:
                    print(message)
                    try:
                        # g.app.gui does not exist yet.
                        import Tkinter as Tk
                        class EmergencyDialog(object):
                            def run(self):
                                """Run the modal emergency dialog."""
                                self.top.geometry("%dx%d%+d%+d" % (300, 200, 50, 50))
                                self.top.lift()
                                self.top.grab_set() # Make the dialog a modal dialog.
                                self.root.wait_window(self.top)
                        d = EmergencyDialog(
                            title='Python Version Error',
                            message=message)
                        d.run()
                    except Exception:
                        pass
                return ok
            except Exception:
                print("isValidPython: unexpected exception: g.CheckVersion")
                traceback.print_exc()
                return 0
        def loadLocalFile(self, fn, gui, old_c):
            trace = (False or g.trace_startup) and not g.unitTesting
        '''
        table = (
            (1, 'isValidPython'),
            # (2, 'class EmergencyDialog'),
            # (3, 'run'),
            (1, 'loadLocalFile'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
            
    #@+node:ekr.20210904065459.62: *5* TestImport.test_python_bad_class_test
    def test_python_bad_class_test(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            class testClass1 # no colon
                pass
        
            def spam():
                pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.63: *5* TestImport.test_python_basic_nesting_test
    def test_python_basic_nesting_test(self):
        c = self.c
        # Was unittest/at_auto-unit-test.py
        ic = c.importCommands

        s = textwrap.dedent("""\
            class class1:
                def class1_method1():
                    pass
                def class1_method2():
                    pass
                # After @others in child1.
            class class2:
                def class2_method1():
                    pass
                def class2_method2():
                    pass
            # last line
        """)
        table = (
            (1, 'class class1'),
            (2, 'class1_method1'),
            (2, 'class1_method2'),
            (1, 'class class2'),
            (2, 'class2_method1'),
            (2, 'class2_method2'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
            
    #@+node:ekr.20210904065459.64: *5* TestImport.test_python_bug_346
    def test_python_bug_346(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands  
        s = textwrap.dedent('''\
            import sys
        
            if sys.version_info[0] >= 3:
                exec_ = eval('exec')
            else:
                def exec_(_code_, _globs_=None, _locs_=None):
                    """Execute code in a namespace."""
                    if _globs_ is None:
                        frame = sys._getframe(1)
                        _globs_ = frame.f_globals
                        if _locs_ is None:
                            _locs_ = frame.f_locals
                        del frame
                    elif _locs_ is None:
                        _locs_ = _globs_
                    exec("""exec _code_ in _globs_, _locs_""")
        
            def make_parser():
        
                parser = argparse.ArgumentParser(
                    description="""Raster calcs. with GDAL.
                    The first --grid defines the projection, extent, cell size, and origin
                    for all calculations, all other grids are transformed and resampled
                    as needed to match.""",
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
        ''')
        table = (
            (1, 'Declarations'),
            (1, 'make_parser'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
            
    #@+node:ekr.20210904065459.65: *5* TestImport.test_python_bug_354
    def test_python_bug_354(self):
        c = self.c
        ic = c.importCommands 
        s = """
        if isPython3:
            def u(s):
                '''Return s, converted to unicode from Qt widgets.'''
                return s

            def ue(s, encoding):
                return s if g.isUnicode(s) else str(s, encoding)
        else:
            def u(s):
                '''Return s, converted to unicode from Qt widgets.'''
                return builtins.unicode(s) # Suppress pyflakes complaint.

            def ue(s, encoding):
                return builtins.unicode(s, encoding)
        """
        table = (
            (1, 'Declarations'),
            # (1, 'u'),
            # (1, 'ue'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
            
    #@+node:ekr.20210904065459.66: *5* TestImport.test_python_bug_357
    def test_python_bug_357(self):
        c = self.c
        ic = c.importCommands 
        s = '''
        """
        sheet_stats.py - report column stats for spreadsheets

        requires openpyxl and numpy

        Terry N. Brown, terrynbrown@gmail.com, Fri Dec 16 13:20:47 2016
        2016-12-26 Henry Helgen added average, variance, standard deviation,
                                coefficient of variation to output
        2016-12-23 Henry Helgen updated to Python 3.5 syntax including print() and
                                writer = csv.writer(open(opt.output, 'w', newline=''))
        """

        import csv
        import argparse
        import glob
        import multiprocessing
        import os
        import sys
        from collections import namedtuple
        from math import sqrt, isnan
        NAN = float('NAN')

        from openpyxl import load_workbook

        PYTHON_2 = sys.version_info[0] < 3
        if not PYTHON_2:
            unicode = str

        class AttrDict(dict):
            """allow d.attr instead of d['attr']
            http://stackoverflow.com/a/14620633
            """
            def __init__(self, *args, **kwargs):
                super(AttrDict, self).__init__(*args, **kwargs)
                self.__dict__ = self

        FIELDS = [  # fields in outout table
            'file', 'field', 'n', 'blank', 'bad', 'min', 'max', 'mean', 'std',
            'sum', 'sumsq', 'variance', 'coefvar'
        ]
        def make_parser():
            """build an argparse.ArgumentParser, don't call this directly,
               call get_options() instead.
            """
            parser = argparse.ArgumentParser(
                description="""Report column stats for spreadsheets""",
                formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )

            parser.add_argument('files', type=str, nargs='+',
                help="Files to process, '*' patterns expanded."
            )

            required_named = parser.add_argument_group('required named arguments')

            required_named.add_argument("--output",
                help="Path to .csv file for output, will be overwritten",
                metavar='FILE'
            )

            return parser

        def get_options(args=None):
            """
            get_options - use argparse to parse args, and return a
            argparse.Namespace, possibly with some changes / expansions /
            validatations.

            Client code should call this method with args as per sys.argv[1:],
            rather than calling make_parser() directly.

            :param [str] args: arguments to parse
            :return: options with modifications / validations
            :rtype: argparse.Namespace
            """
            opt = make_parser().parse_args(args)

            # modifications / validations go here

            if not opt.output:
                print("No --output supplied")
                exit(10)

            return opt

        def get_aggregate(psumsqn, psumn, pcountn):
            """
            get_aggregate - compute mean, variance, standard deviation,
            coefficient of variation This function is used instead of
            numpy.mean, numpy.var, numpy.std since the sum, sumsq, and count are
            available when the function is called. It avoids an extra pass
            through the list.

            # note pcountn means the full list n,  not a sample n - 1

            :param sum of squares, sum, count
            :return: a tuple of floats mean, variance, standard deviation, coefficient of variation
            """

            Agg = namedtuple("Agg", "mean variance std coefvar")

            # validate inputs check for count == 0
            if pcountn == 0:
                result = Agg(NAN, NAN, NAN, NAN)
            else:

                mean = psumn / pcountn # mean

                # compute variance from sum squared without knowing mean while summing
                variance = (psumsqn - (psumn * psumn) / pcountn ) / pcountn

                #compute standard deviation
                if variance < 0:
                    std = NAN
                else:
                    std = sqrt(variance)

                # compute coefficient of variation
                if mean == 0:
                    coefvar = NAN
                else:
                    coefvar = std / mean

                result = Agg(mean, variance, std, coefvar)

            return result


        def proc_file(filepath):
            """
            proc_file - process one .xlsx file

            :param str filepath: path to file
            :return: list of lists, rows of info. as expected in main()
            """

            print(filepath)

            # get the first sheet
            book = load_workbook(filename=filepath, read_only=True)
            sheets = book.get_sheet_names()
            sheet = book[sheets[0]]
            row_source = sheet.rows
            row0 = next(row_source)
            # get field names from the first row
            fields = [i.value for i in row0]

            data = {
                'filepath': filepath,
                'fields': {field:AttrDict({f:0 for f in FIELDS}) for field in fields}
            }

            for field in fields:
                # init. mins/maxs with invalid value for later calc.
                data['fields'][field].update(dict(
                    min=NAN,
                    max=NAN,
                    field=field,
                    file=filepath,
                ))

            rows = 0
            for row in row_source:

                if rows % 1000 == 0:  # feedback every 1000 rows
                    print(rows)
                    # Much cleaner to exit by creating a file called "STOP" in the
                    # local directory than to try and use Ctrl-C, when using
                    # multiprocessing.  Save time by checking only every 1000 rows.
                    if os.path.exists("STOP"):
                        return

                rows += 1

                for cell_n, cell in enumerate(row):
                    d = data['fields'][fields[cell_n]]
                    if cell.value is None or unicode(cell.value).strip() == '':
                        d.blank += 1
                    else:
                        try:
                            x = float(cell.value)
                            d.sum += x
                            d.sumsq += x*x
                            d.n += 1
                            # min is x if no value seen yet, else min(prev-min, x)
                            if isnan(d.min):
                                d.min = x
                            else:
                                d.min = min(d.min, x)
                            # as for min
                            if isnan(d.max):
                                d.max = x
                            else:
                                d.max = max(d.max, x)
                        except ValueError:
                            d.bad += 1

            assert sum(d.n+d.blank+d.bad for d in data['fields'].values()) == rows * len(fields)

            # compute the derived values
            for field in data['fields']:
                d = data['fields'][field]
                d.update(get_aggregate(d.sumsq, d.sum, d.n)._asdict().items())

            return data
        def get_answers(opt=None, **kwargs):
            """get_answers - process files

            :param argparse.Namespace opt: options
            :return: list of answers from proc_file
            """

            if opt is None:  # API call rather than command line
                opt = type("opt", (), kwargs)

            # pass filenames through glob() to expand "2017_*.xlsx" etc.
            files = []
            for filepath in opt.files:
                files.extend(glob.glob(filepath))

            # create a pool of processors
            pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)

            # process file list with processor pool
            return pool.map(proc_file, files)
        def get_table_rows(answers):
            """get_table_rows - generator - convert get_answers() output to table format

            :param list answers: output from get_answers()
            :return: list of rows suitable for csv.writer
            """
            yield FIELDS
            for answer in answers:
                for field in answer['fields']:
                    row = [answer['fields'][field][k] for k in FIELDS]
                    if PYTHON_2:
                        yield [unicode(col).encode('utf-8') for col in row]
                    else:
                        yield row

        def main():
            """main() - when invoked directly"""
            opt = get_options()

            # csv.writer does its own EOL handling,
            # see https://docs.python.org/3/library/csv.html#csv.reader
            if PYTHON_2:
                output = open(opt.output, 'wb')
            else:
                output = open(opt.output, 'w', newline='')

            with output as out:
                writer = csv.writer(out)
                for row in get_table_rows(get_answers(opt)):
                    writer.writerow(row)

        if __name__ == '__main__':
            main()
        '''
        table = (
            (1, "Declarations"),
            (1, "class AttrDict(dict)"),
            (2, "__init__"),
            (1, "make_parser"),
            (1, "get_options"),
            (1, "get_aggregate"),
            (1, "proc_file"),
            (1, "get_answers"),
            (1, "get_table_rows"),
            (1, "main"),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
            
    #@+node:ekr.20210904065459.67: *5* TestImport.test_python_bug_360
    def test_python_bug_360(self):
        c = self.c
        s = """
        @base_task(
            targets=['img/who_map.png', 'img/who_map.pdf'],
            file_dep=[data_path('phyto')],
            task_dep=['load_data'],
        )
        def make_map():
            '''make_map - plot the Thompson / Bartsh / WHO map'''
        """
        table = (
            (1, '@base_task make_map'),
        )
        p = c.p
        c.importCommands.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
    #@+node:ekr.20210904065459.68: *5* TestImport.test_python_bug_390
    def test_python_bug_390(self):
        c = self.c
        s = """\
        import sys

        class Foo():
            pass
        
        a = 2

        def main(self):
            pass

        if __name__ == '__main__':
            main()
        """
        table = (
            (1, 'Declarations'),
            (1, 'class Foo'),
            (1, 'main'),
        )
        p = c.p
        c.importCommands .pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
            assert root.b.find("if __name__ == '__main__':") > -1
    #@+node:ekr.20210904065459.69: *5* TestImport.test_python_bug_978
    def test_python_bug_978(self):
        c = self.c
        s = """\
        import foo
        import bar

        class A(object):
        pass
        class B(foo):
        pass
        class C(bar.Bar):
        pass
        """
        table = (
            (1, 'Declarations'),
            (1, 'class A(object)'),
            (1, 'class B(foo)'),
            (1, 'class C(bar.Bar)'),
        )
        p = c.p
        c.importCommands .pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
    #@+node:ekr.20210904065459.70: *5* TestImport.test_python_bug_603720
    def test_python_bug_603720(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.

        # Leo bug 603720
        # Within the docstring we must change '\' to '\\'
        s = textwrap.dedent('''\
            def foo():
                s = \\
            """#!/bin/bash
            cd /tmp
            ls"""
                file('/tmp/script', 'w').write(s)
        
            class bar:
                pass
        
            foo()
        ''')
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.71: *5* TestImport.test_python_enhancement_481
    def test_python_enhancement_481(self):
        c = self.c
        s = textwrap.dedent("""\
            @g.cmd('my-command')
            def myCommand(event=None):
                pass
        """)
        table = (
            # (1, '@g.cmd myCommand'),
            (1, "@g.cmd('my-command') myCommand"),
        )
        p = c.p
        c.importCommands.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
    #@+node:ekr.20210904065459.72: *5* TestImport.test_python_class_test_2
    def test_python_class_test_2(self):
        c = self.c
        ###@tabwidth -4
            # Required when running unit tests externally.

        s = textwrap.dedent("""\
            class testClass2:
                pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.73: *5* TestImport.test_python_class_tests_1
    def test_python_class_tests_1(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent('''\
        class testClass1:
            """A docstring"""
            def __init__ (self):
                pass
            def f1(self):
                pass
        ''')
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.74: *5* TestImport.test_python_comment_after_dict_assign
    def test_python_comment_after_dict_assign(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands  

        s = textwrap.dedent("""\
            NS = { 'i': 'http://www.inkscape.org/namespaces/inkscape',
                  's': 'http://www.w3.org/2000/svg',
                  'xlink' : 'http://www.w3.org/1999/xlink'}
        
            tabLevels = 4  # number of defined tablevels, FIXME, could derive from template?
        """)
        table = (
            (1, 'Declarations'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
           
    #@+node:ekr.20210904065459.75: *5* TestImport.test_python_decls_test_1
    def test_python_decls_test_1(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands  

        s = textwrap.dedent("""\
            import leo.core.leoGlobals as g

            a = 3
        """)
        table = (
            (1, 'Declarations'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
    #@+node:ekr.20210904065459.76: *5* TestImport.test_python_decorator
    def test_python_decorator(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent('''\
            class Index:
                """docstring"""
                @cherrypy.nocolor
                @cherrypy.expose
                def index(self):
                    return "Hello world!"
                
                @cmd('abc')
                def abc(self):
                    return "abc"
        ''')
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=True) # Must be true.
        index = g.findNodeInTree(c, c.p, '@cherrypy.nocolor index')
        assert index
        lines = g.splitLines(index.b)
        assert lines[0] == '@cherrypy.nocolor\n', repr(lines[0])
        assert lines[1] == '@cherrypy.expose\n', repr(lines[1])
        abc = g.findNodeInTree(c, c.p, "@cmd('abc') abc")
        lines = g.splitLines(abc.b)
        assert lines[0] == "@cmd('abc')\n", repr(lines[0])
    #@+node:ekr.20210904065459.77: *5* TestImport.test_python_decorator_2
    def test_python_decorator_2(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.

        s = '''
        """
        A PyQt "task launcher" for quick access to python scripts.

        Buttons to click to make working in Windows less unproductive.

        e.g. a button to move the current window to top or bottom half
        of screen, because Windows-Up / Windows-Down doesn't do that.
        Or quote the text on the clipboard properly, because Outlook
        can't do that.

        terrynbrown@gmail.com, 2016-12-23
        """

        import sys
        import time
        from PyQt4 import QtGui, QtCore, Qt
        from PyQt4.QtCore import Qt as QtConst

        COMMANDS = []

        class Draggable(QtGui.QWidget):
            def __init__(self, *args, **kwargs):
                """__init__
                """

                QtGui.QWidget.__init__(self, *args, **kwargs)
                # self.setMouseTracking(True)
                self.offset = None
                layout = QtGui.QHBoxLayout()
                self.setLayout(layout)
                layout.addItem(QtGui.QSpacerItem(15, 5))
                layout.setSpacing(0)
                layout.setContentsMargins(0, 0, 0, 0)

            def mousePressEvent(self, event):
                self.offset = event.pos()

            def mouseMoveEvent(self, event):
                x=event.globalX()
                y=event.globalY()
                x_w = self.offset.x()
                y_w = self.offset.y()
                self.parent().move(x-x_w, y-y_w)

        def command(name):
            def makebutton(function):
                COMMANDS.append((name, function))
                return function
            return makebutton

        @command("Exit")
        def exit_():
            exit()

        def main():

            app = Qt.QApplication(sys.argv)

            main = QtGui.QMainWindow(None,
               # QtConst.CustomizeWindowHint  |
               QtConst.FramelessWindowHint #  |
               # QtConst.WindowCloseButtonHint
            )

            main.resize(800,16)
            main.move(40,40)
            mainwidj = Draggable()

            for name, function in COMMANDS:
                button = QtGui.QPushButton(name)
                button.clicked.connect(function)
                mainwidj.layout().addWidget(button)

            main.setCentralWidget(mainwidj)
            main.show()
            app.exec_()

        if __name__ == '__main__':
            main()
        '''
        table = (
            (1, "Declarations"),
            (1, "class Draggable(QtGui.QWidget)"),
            (2, "__init__"),
            (2, "mousePressEvent"),
            (2, "mouseMoveEvent"),
            (1, "command"),
            (1, '@command("Exit") exit_'),
            (1, "main"),
        )
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=True) # Must be true.
        after = c.p.nodeAfterTree()
        root = c.p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
        target = g.findNodeInTree(c, root, '@command("Exit") exit_')
        assert target
        lines = g.splitLines(target.b)
        assert lines[0] == '@command("Exit")\n', repr(lines[0])
       
    #@+node:ekr.20210904065459.78: *5* TestImport.test_python_def_inside_def
    def test_python_def_inside_def(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands  
        s = textwrap.dedent('''\
        class aClass:
            def outerDef(self):
                """docstring.
                line two."""

                def pr(*args,**keys):
                    g.es_print(color='blue',*args,**keys)

                a = 3
        ''')
        table = (
            (1, 'class aClass'),
            (2, 'outerDef'),
            # (3, 'pr'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
           
    #@+node:ekr.20210904065459.79: *5* TestImport.test_python_def_test_1
    def test_python_def_test_1(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands  
        s = textwrap.dedent("""\
            class test:
        
                def importFilesCommand (self,files=None,treeType=None,
                    perfectImport=True,testing=False,verbose=False):
                        # Not a command.  It must *not* have an event arg.
        
                    c = self.c
                    if c == None: return
                    p = c.currentPosition()
        
                # Used by paste logic.
        
                def convertMoreStringToOutlineAfter (self,s,firstVnode):
                    s = string.replace(s,"\\r","")
                    strings = string.split(s,"\\n")
                    return self.convertMoreStringsToOutlineAfter(strings,firstVnode)
        """)
        table = (
            (1, 'class test'),
            (2, 'importFilesCommand'),
            (2, 'convertMoreStringToOutlineAfter'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
        
    #@+node:ekr.20210904065459.80: *5* TestImport.test_python_def_test_2
    def test_python_def_test_2(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands

        s = textwrap.dedent("""\
            class test:
                def spam(b):
                    pass
        
                # Used by paste logic.
        
                def foo(a):
                    pass
        """)
        table = (
            (1, 'class test'),
            (2, 'spam'),
            (2, 'foo'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
        
    #@+node:ekr.20210904065459.81: *5* TestImport.test_python_docstring_only
    def test_python_docstring_only(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent('''\
            """A file consisting only of a docstring.
            """
        ''')
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.82: *5* TestImport.test_python_empty_decls
    def test_python_empty_decls(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            import leo.core.leoGlobals as g
        
            a = 3
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.83: *5* TestImport.test_python_extra_leading_ws_test
    def test_python_extra_leading_ws_test(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.

        s = textwrap.dedent("""\
            class cls:
                 def fun(): # one extra space.
                    pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.84: *5* TestImport.test_python_indent_decls
    def test_python_indent_decls(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands  
        s = textwrap.dedent('''\
            class mammalProviderBase(object):
                """Root class for content providers used by DWEtree.py"""
                def __init__(self, params):
                    """store reference to parameters"""
                    self.params = params
                def provide(self, what):
                    """default <BASE> value"""
                    if what == 'doctitle':
                        return ELE('base', href=self.params['/BASE/'])
                    return None
        
                def imagePath(self, sppdat):
                    """return path to images and list of images for *species*"""
                    path = 'MNMammals/imglib/Mammalia'
                    for i in 'Order', 'Family', 'Genus', 'Species':
                        path = os.path.join(path, sppdat['%sName' % (i,)])
                    imglib = os.path.join('/var/www',path)
                    imglib = os.path.join(imglib, '*.[Jj][Pp][Gg]')
                    path = os.path.join('/',path)
                    lst = [os.path.split(i)[1] for i in glob.glob(imglib)]
                    lst.sort()
                    return path, lst
        
            class mainPages(mammalProviderBase):
                """provide content for pages in 'main' folder"""
                __parent = mammalProviderBase
                def provide(self, what):
                    """add one layer to <BASE>"""
                    ans = self.__parent.provide(self, what)
                    if what == 'doctitle':
                        return ELE('base', href=self.params['/BASE/']+'main/')
                    return ans
        ''') 
        table = (
            (1, 'class mammalProviderBase(object)'),
            (2, '__init__'),
            (2, 'provide'),
            (2, 'imagePath'),
            (1, 'class mainPages(mammalProviderBase)'),
            (2, 'provide'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
           
    #@+node:ekr.20210904065459.85: *5* TestImport.test_python_leoImport_py_small_
    def test_python_leoImport_py_small_(self):
        c = self.c
        ic = c.importCommands

        s = """\
        # -*- coding: utf-8 -*-
        import leo.core.leoGlobals as g
        class LeoImportCommands(object):
            '''A class implementing all of Leo's import/export code.'''
            def createOutline(self, fileName, parent, s=None, ext=None):
                '''Create an outline by importing a file or string.'''

            def dispatch(self, ext, p):
                '''Return the correct scanner function for p, an @auto node.'''
                # Match the @auto type first, then the file extension.
                return self.scanner_for_at_auto(p) or self.scanner_for_ext(ext)
            def scanner_for_at_auto(self, p):
                '''A factory returning a scanner function for p, an @auto node.'''
                d = self.atAutoDict
                for key in d.keys():
                    aClass = d.get(key)
                    if aClass and g.match_word(p.h, 0, key):
                        if trace: g.trace('found', aClass.__name__)

                        def scanner_for_at_auto_cb(parent, s, prepass=False):
                            try:
                                scanner = aClass(importCommands=self)
                                return scanner.run(s, parent, prepass=prepass)
                            except Exception:
                                g.es_print('Exception running', aClass.__name__)
                                g.es_exception()
                                return None

                        if trace: g.trace('found', p.h)
                        return scanner_for_at_auto_cb
                if trace: g.trace('not found', p.h, sorted(d.keys()))
                return None
            def scanner_for_ext(self, ext):
                '''A factory returning a scanner function for the given file extension.'''
                aClass = self.classDispatchDict.get(ext)
                if aClass:

                    def scanner_for_ext_cb(parent, s, prepass=False):
                        try:
                            scanner = aClass(importCommands=self)
                            return scanner.run(s, parent, prepass=prepass)
                        except Exception:
                            g.es_print('Exception running', aClass.__name__)
                            g.es_exception()
                            return None

                    return scanner_for_ext_cb
                else:
                    return None
            def get_import_filename(self, fileName, parent):
                '''Return the absolute path of the file and set .default_directory.'''

            def init_import(self, ext, fileName, s):
                '''Init ivars & vars for imports.'''
        """
        table = (
            (1, 'Declarations'),
            (1, "class LeoImportCommands(object)"),
            (2, "createOutline"),
            (2, "dispatch"),
            (2, "scanner_for_at_auto"),
            (2, "scanner_for_ext"),
            (2, "get_import_filename"),
            (2, "init_import"),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
           
    #@+node:ekr.20210904065459.86: *5* TestImport.test_python_looks_like_section_ref
    def test_python_looks_like_section_ref(self):
        c = self.c
        # ~/at-auto-test.py

        # Careful: don't put a section reference in the string.
        s = textwrap.dedent("""\
            # This is valid Python, but it looks like a section reference.
            a = b < < c > > d
        """).replace('> >', '>>').replace('< <', '<<')
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.87: *5* TestImport.test_python_minimal_class_1
    def test_python_minimal_class_1(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent('''\
            class ItasException(Exception):
        
                pass
        
            def gpRun(gp, cmd, args, log = None):
        
                """Wrapper for making calls to the geoprocessor and reporting errors"""
        
                if log:
        
                    log('gp: %s: %s\\n' % (cmd, str(args)))
        ''')
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.88: *5* TestImport.test_python_minimal_class_2
    def test_python_minimal_class_2(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.

        s = textwrap.dedent("""\
            class emptyClass: pass
        
            def followingDef():
                pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.89: *5* TestImport.test_python_minimal_class_3
    def test_python_minimal_class_3(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            class emptyClass: pass # comment
        
            def followingDef(): # comment
                pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.90: *5* TestImport.test_python_overindent_def_no_following_def
    def test_python_overindent_def_no_following_def(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.

        s = textwrap.dedent("""\
            class aClass:
                def def1(self):
                    pass
        
                if False or g.unitTesting:
        
                    def pr(*args,**keys): # reportMismatch test
                        g.es_print(color='blue',*args,**keys)
        
                    pr('input...')
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.91: *5* TestImport.test_python_overindent_def_one_following_def
    def test_python_overindent_def_one_following_def(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            class aClass:
                def def1(self):
                    pass
        
                if False or g.unitTesting:
        
                    def pr(*args,**keys): # reportMismatch test
                        g.es_print(color='blue',*args,**keys)
        
                    pr('input...')
        
                def def2(self):
                    pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.92: *5* TestImport.test_python_overindented_def_3
    def test_python_overindented_def_3(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands  
        # This caused PyParse.py not to be imported properly.
        s = r'''
        import re
        if 0: # Causes the 'overindent'
           if 0:   # for throwaway debugging output
              def dump(*stuff):
                sys.__stdout__.write(" ".join(map(str, stuff)) + "\n")
        for ch in "({[":
           _tran[ord(ch)] = '('
        class testClass1:
            pass
        '''
        table = (
            (1, 'Declarations'),
            (1, 'class testClass1'),
        )
        p = c.p
        ic.pythonUnitTest(c.p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
           
    #@+node:ekr.20210904065459.93: *5* TestImport.test_python_string_test_extra_indent
    def test_python_string_test_extra_indent(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent('''\
        class BaseScanner:

                """The base class for all import scanner classes."""

                def __init__ (self,importCommands,language):

                    self.c = ic.c

                def createHeadline (self,parent,body,headline):
                    # g.trace("parent,headline:",parent,headline)
                    return p
        ''')
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.94: *5* TestImport.test_python_string_underindent_lines
    def test_python_string_underindent_lines(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            class BaseScanner:
                def containsUnderindentedComment(self):
                    a = 2
                # A true underindented comment.
                    b = 3
                # This underindented comment should be placed with next function.
                def empty(self):
                    pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.95: *5* TestImport.test_python_string_underindent_lines_2
    def test_python_string_underindent_lines_2(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            class BaseScanner:
                def containsUnderindentedComment(self):
                    a = 2
                #
                    b = 3
                    # This comment is part of the present function.
        
                def empty(self):
                    pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.96: *5* TestImport.test_python_top_level_later_decl
    def test_python_top_level_later_decl(self):
        c = self.c
        # From xo.py.
        ic = c.importCommands  

        s = r'''#!/usr/bin/env python3

        import os
        import re

        def merge_value(v1, v2):
            return v

        class MainDisplay(object):

            def save_file(self):
                """Write the file out to disk."""
                with open(self.save_name, "w") as f:
                    for newline in newlines:
                        f.write(newline)

        # This line should be included at the end of the class node.
        ensure_endswith_newline = lambda x: x if x.endswith('\n') else x + '\n'

        def retab(s, tabsize):
            return ''.join(pieces)

        if __name__=="__main__":
            main()
        '''
        table = (
            (1, 'Declarations'),
            (1, 'merge_value'),
            (1, 'class MainDisplay(object)'),
            (2, 'save_file'),
            (1, 'retab'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
    #@+node:ekr.20210904065459.97: *5* TestImport.test_python_trailing_comment
    def test_python_trailing_comment(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            class aClass: # trailing comment
        
        
                def def1(self):             # trailing comment
                    pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.98: *5* TestImport.test_python_trailing_comment_outer_levels
    def test_python_trailing_comment_outer_levels(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            xyz = 6 # trailing comment
            pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.99: *5* TestImport.test_python_two_functions
    def test_python_two_functions(self):
        c = self.c
        # For comparison with unindent does not end function.

        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent("""\
            def foo():
                pass
        
            def bar():
                pass
        """)
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.100: *5* TestImport.test_python_underindent_method
    def test_python_underindent_method(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        ic = c.importCommands  
        s = textwrap.dedent('''\
            class emptyClass: 
        
                def spam():
                    """docstring line 1
            under-indented docstring line"""
                    pass
        
            def followingDef(): # comment
                pass
        ''')
        table = (
            (1, 'class emptyClass'),
            (2, 'spam'),
            (1, 'followingDef'),
        )
        p = c.p
        ic.pythonUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
           
    #@+node:ekr.20210904065459.101: *5* TestImport.test_python_unindent_in_triple_string_does_not_end_function
    def test_python_unindent_in_triple_string_does_not_end_function(self):
        c = self.c
        ### @tabwidth -4
            # Required when running unit tests externally.
        s = textwrap.dedent('''\
            def foo():
        
                error("""line1
            line2.
            """)
        
                a = 5
        
            def bar():
                pass
        ''')
        p = c.p
        c.importCommands.pythonUnitTest(p, s=s, showTree=True)
        child = p.firstChild()
        n = child.numberOfChildren()
        assert n == 2, 'expected 2 children, got %s' % n
    #@+node:ekr.20210904065459.102: *5* TestImport.test_python_unittest_perfectImport_formatter_py
    def test_python_unittest_perfectImport_formatter_py(self):
        c = self.c

        s = textwrap.dedent('''\

            """Generic output formatting.
            """
        
            import sys
        
        
            AS_IS = None
        
        
            class NullFormatter:
                """A formatter which does nothing.
        
                If the writer parameter is omitted, a NullWriter instance is created.
                No methods of the writer are called by NullFormatter instances.
        
                Implementations should inherit from this class if implementing a writer
                interface but don't need to inherit any implementation.
        
                """
        
                def __init__(self, writer=None):
                    if writer is None:
                        writer = NullWriter()
                    self.writer = writer
                def end_paragraph(self, blankline): pass
                def add_line_break(self): pass
                def add_hor_rule(self, *args, **kw): pass
                def add_label_data(self, format, counter, blankline=None): pass
                def add_flowing_data(self, data): pass
                def add_literal_data(self, data): pass
                def flush_softspace(self): pass
                def push_alignment(self, align): pass
                def pop_alignment(self): pass
                def push_font(self, x): pass
                def pop_font(self): pass
                def push_margin(self, margin): pass
                def pop_margin(self): pass
                def set_spacing(self, spacing): pass
                def push_style(self, *styles): pass
                def pop_style(self, n=1): pass
                def assert_line_data(self, flag=1): pass
        
        
            class AbstractFormatter:
                """The standard formatter.
        
                This implementation has demonstrated wide applicability to many writers,
                and may be used directly in most circumstances.  It has been used to
                implement a full-featured World Wide Web browser.
        
                """
        
                #  Space handling policy:  blank spaces at the boundary between elements
                #  are handled by the outermost context.  "Literal" data is not checked
                #  to determine context, so spaces in literal data are handled directly
                #  in all circumstances.
        
                def __init__(self, writer):
                    self.writer = writer            # Output device
                    self.align = None               # Current alignment
                    self.align_stack = []           # Alignment stack
                    self.font_stack = []            # Font state
                    self.margin_stack = []          # Margin state
                    self.spacing = None             # Vertical spacing state
                    self.style_stack = []           # Other state, e.g. color
                    self.nospace = 1                # Should leading space be suppressed
                    self.softspace = 0              # Should a space be inserted
                    self.para_end = 1               # Just ended a paragraph
                    self.parskip = 0                # Skipped space between paragraphs?
                    self.hard_break = 1             # Have a hard break
                    self.have_label = 0
        
                def end_paragraph(self, blankline):
                    if not self.hard_break:
                        self.writer.send_line_break()
                        self.have_label = 0
                    if self.parskip < blankline and not self.have_label:
                        self.writer.send_paragraph(blankline - self.parskip)
                        self.parskip = blankline
                        self.have_label = 0
                    self.hard_break = self.nospace = self.para_end = 1
                    self.softspace = 0
        
                def add_line_break(self):
                    if not (self.hard_break or self.para_end):
                        self.writer.send_line_break()
                        self.have_label = self.parskip = 0
                    self.hard_break = self.nospace = 1
                    self.softspace = 0
        
                def add_hor_rule(self, *args, **kw):
                    if not self.hard_break:
                        self.writer.send_line_break()
                    self.writer.send_hor_rule(*args, **kw)
                    self.hard_break = self.nospace = 1
                    self.have_label = self.para_end = self.softspace = self.parskip = 0
        
                def add_label_data(self, format, counter, blankline = None):
                    if self.have_label or not self.hard_break:
                        self.writer.send_line_break()
                    if not self.para_end:
                        self.writer.send_paragraph((blankline and 1) or 0)
                    if isinstance(format, str):
                        self.writer.send_label_data(self.format_counter(format, counter))
                    else:
                        self.writer.send_label_data(format)
                    self.nospace = self.have_label = self.hard_break = self.para_end = 1
                    self.softspace = self.parskip = 0
        
                def format_counter(self, format, counter):
                    label = ''
                    for c in format:
                        if c == '1':
                            label = label + ('%d' % counter)
                        elif c in 'aA':
                            if counter > 0:
                                label = label + self.format_letter(c, counter)
                        elif c in 'iI':
                            if counter > 0:
                                label = label + self.format_roman(c, counter)
                        else:
                            label = label + c
                    return label
        
                def format_letter(self, case, counter):
                    label = ''
                    while counter > 0:
                        counter, x = divmod(counter-1, 26)
                        # This makes a strong assumption that lowercase letters
                        # and uppercase letters form two contiguous blocks, with
                        # letters in order!
                        s = chr(ord(case) + x)
                        label = s + label
                    return label
        
                def format_roman(self, case, counter):
                    ones = ['i', 'x', 'c', 'm']
                    fives = ['v', 'l', 'd']
                    label, index = '', 0
                    # This will die of IndexError when counter is too big
                    while counter > 0:
                        counter, x = divmod(counter, 10)
                        if x == 9:
                            label = ones[index] + ones[index+1] + label
                        elif x == 4:
                            label = ones[index] + fives[index] + label
                        else:
                            if x >= 5:
                                s = fives[index]
                                x = x-5
                            else:
                                s = ''
                            s = s + ones[index]*x
                            label = s + label
                        index = index + 1
                    if case == 'I':
                        return label.upper()
                    return label
        
                def add_flowing_data(self, data):
                    if not data: return
                    # The following looks a bit convoluted but is a great improvement over
                    # data = regsub.gsub('[' + string.whitespace + ']+', ' ', data)
                    prespace = data[:1].isspace()
                    postspace = data[-1:].isspace()
                    data = " ".join(data.split())
                    if self.nospace and not data:
                        return
                    elif prespace or self.softspace:
                        if not data:
                            if not self.nospace:
                                self.softspace = 1
                                self.parskip = 0
                            return
                        if not self.nospace:
                            data = ' ' + data
                    self.hard_break = self.nospace = self.para_end = \
                                      self.parskip = self.have_label = 0
                    self.softspace = postspace
                    self.writer.send_flowing_data(data)
        
                def add_literal_data(self, data):
                    if not data: return
                    if self.softspace:
                        self.writer.send_flowing_data(" ")
                    self.hard_break = data[-1:] == '\n'
                    self.nospace = self.para_end = self.softspace = \
                                   self.parskip = self.have_label = 0
                    self.writer.send_literal_data(data)
        
                def flush_softspace(self):
                    if self.softspace:
                        self.hard_break = self.para_end = self.parskip = \
                                          self.have_label = self.softspace = 0
                        self.nospace = 1
                        self.writer.send_flowing_data(' ')
        
                def push_alignment(self, align):
                    if align and align != self.align:
                        self.writer.new_alignment(align)
                        self.align = align
                        self.align_stack.append(align)
                    else:
                        self.align_stack.append(self.align)
        
                def pop_alignment(self):
                    if self.align_stack:
                        del self.align_stack[-1]
                    if self.align_stack:
                        self.align = align = self.align_stack[-1]
                        self.writer.new_alignment(align)
                    else:
                        self.align = None
                        self.writer.new_alignment(None)
        
                def push_font(self, (size, i, b, tt)):
                    if self.softspace:
                        self.hard_break = self.para_end = self.softspace = 0
                        self.nospace = 1
                        self.writer.send_flowing_data(' ')
                    if self.font_stack:
                        csize, ci, cb, ctt = self.font_stack[-1]
                        if size is AS_IS: size = csize
                        if i is AS_IS: i = ci
                        if b is AS_IS: b = cb
                        if tt is AS_IS: tt = ctt
                    font = (size, i, b, tt)
                    self.font_stack.append(font)
                    self.writer.new_font(font)
        
                def pop_font(self):
                    if self.font_stack:
                        del self.font_stack[-1]
                    if self.font_stack:
                        font = self.font_stack[-1]
                    else:
                        font = None
                    self.writer.new_font(font)
        
                def push_margin(self, margin):
                    self.margin_stack.append(margin)
                    fstack = filter(None, self.margin_stack)
                    if not margin and fstack:
                        margin = fstack[-1]
                    self.writer.new_margin(margin, len(fstack))
        
                def pop_margin(self):
                    if self.margin_stack:
                        del self.margin_stack[-1]
                    fstack = filter(None, self.margin_stack)
                    if fstack:
                        margin = fstack[-1]
                    else:
                        margin = None
                    self.writer.new_margin(margin, len(fstack))
        
                def set_spacing(self, spacing):
                    self.spacing = spacing
                    self.writer.new_spacing(spacing)
        
                def push_style(self, *styles):
                    if self.softspace:
                        self.hard_break = self.para_end = self.softspace = 0
                        self.nospace = 1
                        self.writer.send_flowing_data(' ')
                    for style in styles:
                        self.style_stack.append(style)
                    self.writer.new_styles(tuple(self.style_stack))
        
                def pop_style(self, n=1):
                    del self.style_stack[-n:]
                    self.writer.new_styles(tuple(self.style_stack))
        
                def assert_line_data(self, flag=1):
                    self.nospace = self.hard_break = not flag
                    self.para_end = self.parskip = self.have_label = 0
        
        
            class NullWriter:
                """Minimal writer interface to use in testing & inheritance.
        
                A writer which only provides the interface definition; no actions are
                taken on any methods.  This should be the base class for all writers
                which do not need to inherit any implementation methods.
        
                """
                def __init__(self): pass
                def flush(self): pass
                def new_alignment(self, align): pass
                def new_font(self, font): pass
                def new_margin(self, margin, level): pass
                def new_spacing(self, spacing): pass
                def new_styles(self, styles): pass
                def send_paragraph(self, blankline): pass
                def send_line_break(self): pass
                def send_hor_rule(self, *args, **kw): pass
                def send_label_data(self, data): pass
                def send_flowing_data(self, data): pass
                def send_literal_data(self, data): pass
        
        
            class AbstractWriter(NullWriter):
                """A writer which can be used in debugging formatters, but not much else.
        
                Each method simply announces itself by printing its name and
                arguments on standard output.
        
                """
        
                def new_alignment(self, align):
                    print "new_alignment(%s)" % `align`
        
                def new_font(self, font):
                    print "new_font(%s)" % `font`
        
                def new_margin(self, margin, level):
                    print "new_margin(%s, %d)" % (`margin`, level)
        
                def new_spacing(self, spacing):
                    print "new_spacing(%s)" % `spacing`
        
                def new_styles(self, styles):
                    print "new_styles(%s)" % `styles`
        
                def send_paragraph(self, blankline):
                    print "send_paragraph(%s)" % `blankline`
        
                def send_line_break(self):
                    print "send_line_break()"
        
                def send_hor_rule(self, *args, **kw):
                    print "send_hor_rule()"
        
                def send_label_data(self, data):
                    print "send_label_data(%s)" % `data`
        
                def send_flowing_data(self, data):
                    print "send_flowing_data(%s)" % `data`
        
                def send_literal_data(self, data):
                    print "send_literal_data(%s)" % `data`
        
        
            class DumbWriter(NullWriter):
                """Simple writer class which writes output on the file object passed in
                as the file parameter or, if file is omitted, on standard output.  The
                output is simply word-wrapped to the number of columns specified by
                the maxcol parameter.  This class is suitable for reflowing a sequence
                of paragraphs.
        
                """
        
                def __init__(self, file=None, maxcol=72):
                    self.file = file or sys.stdout
                    self.maxcol = maxcol
                    NullWriter.__init__(self)
                    self.reset()
        
                def reset(self):
                    self.col = 0
                    self.atbreak = 0
        
                def send_paragraph(self, blankline):
                    self.file.write('\n'*blankline)
                    self.col = 0
                    self.atbreak = 0
        
                def send_line_break(self):
                    self.file.write('\n')
                    self.col = 0
                    self.atbreak = 0
        
                def send_hor_rule(self, *args, **kw):
                    self.file.write('\n')
                    self.file.write('-'*self.maxcol)
                    self.file.write('\n')
                    self.col = 0
                    self.atbreak = 0
        
                def send_literal_data(self, data):
                    self.file.write(data)
                    i = data.rfind('\n')
                    if i >= 0:
                        self.col = 0
                        data = data[i+1:]
                    data = data.expandtabs()
                    self.col = self.col + len(data)
                    self.atbreak = 0
        
                def send_flowing_data(self, data):
                    if not data: return
                    atbreak = self.atbreak or data[0].isspace()
                    col = self.col
                    maxcol = self.maxcol
                    write = self.file.write
                    for word in data.split():
                        if atbreak:
                            if col + len(word) >= maxcol:
                                write('\n')
                                col = 0
                            else:
                                write(' ')
                                col = col + 1
                        write(word)
                        col = col + len(word)
                        atbreak = 1
                    self.col = col
                    self.atbreak = data[-1].isspace()
        
        
            def test(file = None):
                w = DumbWriter()
                f = AbstractFormatter(w)
                if file is not None:
                    fp = open(file)
                elif sys.argv[1:]:
                    fp = open(sys.argv[1])
                else:
                    fp = sys.stdin
                while 1:
                    line = fp.readline()
                    if not line:
                        break
                    if line == '\n':
                        f.end_paragraph(1)
                    else:
                        f.add_flowing_data(line)
                f.end_paragraph(0)
        
        
            if __name__ == '__main__':
                test()
        ''')
        c.importCommands.pythonUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904123047.1: *4* Typescript tests
    #@+node:ekr.20210904065459.103: *5* TestImport.test_TypeScript_class
    def test_TypeScript_class(self):
        c = self.c
        s = '''

        class Greeter {
            greeting: string;
            constructor (message: string) {
                this.greeting = message;
            }
            greet() {
                return "Hello, " + this.greeting;
            }
        }

        var greeter = new Greeter("world");

        var button = document.createElement('button')
        button.innerText = "Say Hello"
        button.onclick = function() {
            alert(greeter.greet())
        }

        document.body.appendChild(button)

        '''

        c.importCommands.typeScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904065459.104: *5* TestImport.test_TypeScript_module
    def test_TypeScript_module(self):
        c = self.c
        s = '''

        module Sayings {
            export class Greeter {
                greeting: string;
                constructor (message: string) {
                    this.greeting = message;
                }
                greet() {
                    return "Hello, " + this.greeting;
                }
            }
        }
        var greeter = new Sayings.Greeter("world");

        var button = document.createElement('button')
        button.innerText = "Say Hello"
        button.onclick = function() {
        	alert(greeter.greet())
        }

        document.body.appendChild(button)


        '''

        c.importCommands.typeScriptUnitTest(c.p, s=s, showTree=False)
    #@+node:ekr.20210904123056.1: *4* XML tests
    #@+node:ekr.20210904065459.105: *5* TestImport.test_xml_with_standard_opening_elements
    def test_xml_with_standard_opening_elements(self):
        c = self.c
        s = textwrap.dedent("""\
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE note SYSTEM "Note.dtd">
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class='bodystring'>
            <div id='bodydisplay'></div>
            </body>
            </html>
        """)
        ic = c.importCommands
        table = (
            (1, "<html>"),
            (2, "<head>"),
            (2, "<body class='bodystring'>"),
        )
        p = c.p
        ic.xmlUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
       
    #@+node:ekr.20210904065459.106: *5* TestImport.test_xml_1
    def test_xml_1(self):
        c = self.c
        s = textwrap.dedent("""\
            <html>
            <head>
                <title>Bodystring</title>
            </head>
            <body class='bodystring'>
            <div id='bodydisplay'></div>
            </body>
            </html>
        """)
        ic = c.importCommands
        table = (
            (1, "<html>"),
            (2, "<head>"),
            (2, "<body class='bodystring'>"),
        )
        p = c.p
        ic.xmlUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        assert p
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
        
    #@+node:ekr.20210904065459.107: *5* TestImport.test_xml_2
    def test_xml_2(self):
        c = self.c
        s = textwrap.dedent("""\
            <nodeA>
            <nodeB/>
            </nodeA>
        """)
        ic = c.importCommands
        table = (
            (1, "<nodeA>"),
        )
        p = c.p
        ic.xmlUnitTest(p, s=s, showTree=True)
        after = p.nodeAfterTree()
        root = p.lastChild()
        assert root.h.startswith('@@'), root.h
        p = root.firstChild()
        assert p
        if 1:
            for n, h in table:
                n2 = p.level() - root.level()
                assert h == p.h, (h, p.h)
                assert n == n2, (n, n2, p.h)
                p.moveToThreadNext()
            assert p == after, ('tree comp failed', p.h)
        
    #@+node:ekr.20210904065459.108: *5* TestImport.test_xml_non_ascii_tags
    def test_xml_non_ascii_tags(self):
        c = self.c
        s = textwrap.dedent("""\
            <:À.Ç>
            <Ì>
            <_.ÌÑ>
        """)
        c.importCommands.xmlUnitTest(c.p, s=s, showTree=True)
    #@-others
#@+node:ekr.20210904071301.1: ** Tests of @auto-md
#@+node:ekr.20210904065459.109: *3* TestImport.test_md_import_test
def test_md_import_test(self):
    c = self.c
    ic = c.importCommands
    s = textwrap.dedent("""\
        #Top
        The top section
        
        ##Section 1
        section 1, line 1
        section 1, line 2
        
        ##Section 2
        section 2, line 1
        
        ###Section 2.1
        section 2.1, line 1
        
        ####Section 2.1.1
        section 2.2.1 line 1
        The next section is empty. It must not be deleted.
        
        ###Section 2.2
        
        ##Section 3
        Section 3, line 1
""")
    ic.markdownUnitTest(c.p, s=s, showTree=True) # Must be true.
    table = (
        (1, 'Top'),
        (2, 'Section 1'),
        (2, 'Section 2'),
        (3, 'Section 2.1'),
        (4, 'Section 2.1.1'),
        (3, 'Section 2.2'),
        (2, 'Section 3'),
    )
    after = c.p.nodeAfterTree()
    root = c.p.lastChild()
    assert root.h.startswith('@@auto-m'), root.h
    p = root.firstChild()
    for n, h in table:
        n2 = p.level() - root.level()
        assert h == p.h, (h, p.h)
        assert n == n2, (n, n2, p.h)
        p.moveToThreadNext()
    assert p == after, p.h
#@+node:ekr.20210904065459.110: *3* TestImport.test_md_import_test_rst_style
def test_md_import_test_rst_style(self):
    c = self.c
    ic = c.importCommands  
    s = textwrap.dedent("""\
        Top
        ====
        
        The top section
        
        Section 1
        ---------
        
        section 1, line 1
        -- Not an underline
        secttion 1, line 2
        
        Section 2
        ---------
        
        section 2, line 1
        
        ###Section 2.1
        
        section 2.1, line 1
        
        ####Section 2.1.1
        
        section 2.2.1 line 1
        
        ###Section 2.2
        section 2.2, line 1.
        
        Section 3
        ---------
        
        section 3, line 1
""")
    
    ic.markdownUnitTest(c.p, s=s, showTree=True) # Must be True.
    table = (
        (1, 'Top'),
        (2, 'Section 1'),
        (2, 'Section 2'),
        (3, 'Section 2.1'),
        (4, 'Section 2.1.1'),
        (3, 'Section 2.2'),
        (2, 'Section 3'),
    )
    p = c.p
    after = p.nodeAfterTree()
    root = p.lastChild()
    assert root.h.startswith('@@auto-m'), root.h
    p = root.firstChild()
    for n, h in table:
        n2 = p.level() - root.level()
        assert h == p.h, (h, p.h)
        assert n == n2, (n, n2, p.h)
        p.moveToThreadNext()
    assert p == after, p.h
#@+node:ekr.20210904065459.111: *3* TestImport.test_markdown_importer_basic
def test_markdown_importer_basic(self):
    c = self.c
    ic = c.importCommands  
    # insert test for markdown here.
    s = textwrap.dedent("""\
        Decl line.
        #Header
    
        After header text
    
        ##Subheader
    
        Not an underline
    
        ----------------
    
        After subheader text
    
        #Last header: no text
    """)
    table = (
        '!Declarations',
        'Header',
            'Subheader',
            'Last header: no text',
    )
    ic.markdownUnitTest(c.p, s=s, showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@auto-m'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.112: *3* TestImport.test_markdown_importer_implicit_section
def test_markdown_importer_implicit_section(self):
    c = self.c
    ic = c.importCommands  
    # insert test for markdown here.
    s = textwrap.dedent("""\
        Decl line.
        #Header
    
        After header text
    
        ##Subheader
    
        Not an underline
    
        ----------------
    
        This *should* be a section
        ==========================
    
        After subheader text
    
        #Last header: no text
    """)
    table = (
        '!Declarations',
        'Header',
            'Subheader',
                'This *should* be a section',
            'Last header: no text',
    )
    g.app.suppressImportChecks = True
        # Required, because the implicit underlining *must*
        # cause the perfect-import test to fail!
    ic.markdownUnitTest(c.p, s=s, showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@auto-m'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.113: *3* TestImport.test_markdown_importer__section_name
def test_markdown_importer__section_name(self):
    c = self.c
    ic = c.importCommands  
    # insert test for markdown here.
    s = textwrap.dedent("""\
        Decl line.
    
#@verbatim
        #@@ Header
    
        After header text
    
        ##@@Subheader
    
        Not an underline
    
        ----------------
    
        This *should* be a section
        ==========================
    
        After subheader text
    
        #Last header: no text
    """)
    table = (
        '!Declarations',
        '@verbatim', # This is an artifact of the unit test.
        '@@ Header',
            '@@Subheader',
                'This *should* be a section',
            'Last header: no text',
    )
    g.app.suppressImportChecks = True
        # Required, because the implicit underlining *must*
        # cause the perfect-import test to fail!
    ic.markdownUnitTest(c.p, s=s, showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@auto-m'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.114: *3* TestImport.test_markdown_github_syntax
def test_markdown_github_syntax(self):
    c = self.c
    ic = c.importCommands  
    ### insert test for markdown here.
    s = textwrap.dedent("""\
        Decl line.
        #Header
    
        `​``python
        loads.init = {
            Chloride: 11.5,
            TotalP: 0.002,
        }
        `​``
        #Last header
    """)
    table = (
        '!Declarations',
        'Header',
        'Last header',
    )
    ic.markdownUnitTest(c.p, s=s, showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904071345.1: ** Tests of @auto-rst
#@+node:ekr.20210904065459.115: *3* TestImport.test_rST_import_test
def test_rST_import_test(self):
    c = self.c
    ic = c.importCommands
    try:
        import docutils
        assert docutils
    except Exception:
        self.skipTest('no docutils')

    s = textwrap.dedent("""\
        .. toc
    
        ====
        top
        ====
    
        The top section
    
        section 1
        ---------
    
        section 1, line 1
        --
        section 1, line 2
    
        section 2
        ---------
    
        section 2, line 1
    
        section 2.1
        ~~~~~~~~~~~
    
        section 2.1, line 1
    
        section 2.1.1
        .............
    
        section 2.2.1 line 1
    
        section 3
        ---------
    
        section 3, line 1
    
        section 3.1.1
        .............
    
        section 3.1.1, line 1
    """)
    table = (
        '!Dummy chapter',
        'top',
        'section 1',
        'section 2',
        'section 2.1',
        'section 2.1.1',
        'section 3',
        'placeholder',
        'section 3.1.1',
    )
    ic.rstUnitTest(c.p, s=s, showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.116: *3* TestImport.test_rST_import_test_simple
def test_rST_import_test_simple(self):
    c = self.c
    try:
        import docutils
        assert docutils
    except Exception:
        self.skipTest('no docutils')

    s = textwrap.dedent("""\
        .. toc
    
        .. The section name contains trailing whitespace.
    
        =======
        Chapter 
        =======
    
        The top chapter.
    """)
    table = (
        "!Dummy chapter",
        "Chapter",
    )
    c.importCommands.rstUnitTest(c.p, s=s ,showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.117: *3* TestImport.test_rST_import_test_no_double_underlines
def test_rST_import_test_no_double_underlines(self):
    c = self.c
    ic = c.importCommands
    try:
        import docutils
        assert docutils
    except Exception:
        self.skipTest('no docutils')

    s = textwrap.dedent("""\
        .. toc
    
        top
        ====
    
        The top section
    
        section 1
        ---------
    
        section 1, line 1
        --
        section 1, line 2
    
        section 2
        ---------
    
        section 2, line 1
    
        section 2.1
        ~~~~~~~~~~~
    
        section 2.1, line 1
    
        section 2.1.1
        .............
    
        section 2.2.1 line 1
    
        section 3
        ---------
    
        section 3, line 1
    
        section 3.1.1
        .............
    
        section 3.1.1, line 1
    """)
    table = (
        '!Dummy chapter',
        'top',
        'section 1',
        'section 2',
        'section 2.1',
        'section 2.1.1',
        'section 3',
        'placeholder',
        'section 3.1.1',
    )
    ic.rstUnitTest(c.p, s=s, showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.118: *3* TestImport.test_rST_import_test_long_underlines
def test_rST_import_test_long_underlines(self):
    c = self.c
    ic = c.importCommands
    try:
        import docutils
        assert docutils
    except Exception:
        self.skipTest('no docutils')
    s = textwrap.dedent("""\
        .. toc
    
        top
        -------------
    
        The top section
    """)
    table = (
        '!Dummy chapter',
        'top',
    )
    ic.rstUnitTest(c.p,s=s,showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.119: *3* TestImport.test_rST_import_test_long_overlines
def test_rST_import_test_long_overlines(self):
    c = self.c
    ic = c.importCommands
    try:
        import docutils
        assert docutils
    except Exception:
        self.skipTest('no docutils')

    s = textwrap.dedent("""\
        .. toc
    
        ======
        top
        ======
    
        The top section
    """)
    table = (
        "!Dummy chapter",
        "top",
    )
    ic.rstUnitTest(c.p, s=s, showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.120: *3* TestImport.test_rST_import_test_trailing_whitespace
def test_rST_import_test_trailing_whitespace(self):
    c = self.c
    try:
        import docutils
        assert docutils
    except Exception:
        self.skipTest('no docutils')

    s = textwrap.dedent("""\
        .. toc
    
        .. The section name contains trailing whitespace.
    
        ======
        top 
        ======
    
        The top section.
    """)
    table = (
        "!Dummy chapter",
        "top",
    )
    p = c.p
    c.importCommands.rstUnitTest(p, s=s, showTree=True)
    root = p.lastChild()
    assert root.h.startswith('@@'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904065459.121: *3* TestImport.test_leo_rst
def test_leo_rst(self):
    c = self.c
    ic = c.importCommands
    try:
        import docutils
        assert docutils
    except Exception:
        self.skipTest('no docutils')

    # Notes:
    # All heading must be followed by an empty line.
    s = textwrap.dedent("""\
        #########
        Chapter 1
        #########
    
        It was a dark and stormy night.
        section 1
        +++++++++
    
        Sec 1.
        section 2
        +++++++++
    
        Sec 2.
    """)
    table = (
        '!Dummy chapter',
        'section 1',
        'section 2',
    )
    ic.rstUnitTest(c.p, s=s, showTree=True)
    root = c.p.lastChild()
    assert root.h.startswith('@@'), root.h
    p2 = root.firstChild()
    for h in table:
        assert p2.h == h, (p2.h, h)
        p2.moveToThreadNext()
    assert not root.isAncestorOf(p2), p2.h # Extra nodes
#@+node:ekr.20210904071422.1: ** All other tests
#@+node:ekr.20210904065459.122: *3* TestImport.test_at_auto_importers
def test_at_auto_importers(self):
    path = g.os_path_finalize_join(g.app.loadDir,'..','plugins','importers')
    assert g.os_path_exists(path), repr(path)
    pattern = g.os_path_finalize_join(path,'*.py')
    for fn in glob.glob(pattern):
        sfn = g.shortFileName(fn)
        m = importlib.import_module('leo.plugins.importers.%s' % sfn[:-3])
        assert m
#@+node:ekr.20210904065459.123: *3* TestImport.test_Importer_get_leading_indent
def test_Importer_get_leading_indent(self):
    c = self.c
    lines_table = [
        'abc',
        '    xyz',
        '    ',
        '  # comment',
    ]
    for language in ('python', 'coffeescript'):
        importer = linescanner.Importer(
            c.importCommands,
            language = language,
        )
        # print('%s %r' % (language, importer.comment_delim))
        assert importer.single_comment == '#', importer.single_comment
        if 0:
            for line in lines_table:
                lines = [line]
                n = importer.get_leading_indent(lines, 0)
                print('%s %r' % (n, line))
#@+node:ekr.20210904065459.124: *3* TestImport.test_Importer_get_str_lws
def test_Importer_get_str_lws(self):
    c = self.c
    table = [
        ('', 'abc\n'),
        ('    ', '    xyz\n'),
        ('    ', '    \n'),
        ('  ','  # comment\n'),
        ('', '\n'),
    ]
    importer = linescanner.Importer(c.importCommands, language='python')
    for val, s in table:
        assert val == importer.get_str_lws(s), (val, repr(s))
#@+node:ekr.20210904065459.125: *3* TestImport.test_Importer_is_ws_line
def test_Importer_is_ws_line(self):
    c = self.c
    table = [
        (False, 'abc'),
        (False, '    xyz'),
        (True, '    '),
        (True,'  # comment'),
    ]
    importer = linescanner.Importer(c.importCommands, language = 'python')
    for val, s in table:
        assert val == importer.is_ws_line(s), (val, repr(s))
#@+node:ekr.20210904065459.126: *3* TestImport.test_importers_coffee_scan_line
def test_importers_coffee_scan_line(self):
    c = self.c
    table = [] # State after line, line
    x = cs.CS_Importer(c.importCommands, atAuto=True)
    assert x.single_comment == '#', x.single_comment
    for new_state, line in table:
        print('%5s %r' % (new_state, line))
    if 0:
        for line in table:
            lines = [line]
            n = x.get_leading_indent(lines, 0)
            print('%s %r' % (n, line))
#@+node:ekr.20210904065459.127: *3* TestImport.test_importers_dart_clean_headline
def test_importers_dart_clean_headline(self):
    c = self.c
    x = dart.Dart_Importer(c.importCommands, atAuto=False)    
    table = (
        ('func(abc) {', 'func'),
        ('void foo() {', 'void foo'),
    )
    for s, expected in table:
        # print('%20s ==> %s' % (s, x.clean_headline(s)))
        got = x.clean_headline(s)
        assert got == expected
#@+node:ekr.20210904065459.128: *3* TestImport.test_importers_markdown_is_hash
def test_importers_markdown_is_hash(self):
    c = self.c
    ic = c.importCommands
    x = markdown.Markdown_Importer(ic, atAuto=False)   
    # insert test for markdown here.
    assert x.md_pattern_table
    table = (
        (1, 'name',     '# name\n'),
        (2, 'a test',   '## a test\n'),
        (3, 'a test',   '### a test\n'),
    )
    for data in table:
        level, name, line = data
        level2, name2 = x.is_hash(line)
        assert level == level2
        assert name == name2
    level3, name = x.is_hash('Not a hash')
    assert level3 is None
    assert name is None
#@+node:ekr.20210904065459.129: *3* TestImport.test_importers_markdown_is_underline
def test_importers_markdown_is_underline(self):
    c = self.c
    ic = c.importCommands
    x = markdown.Markdown_Importer(ic, atAuto=False)
    for line in ('----\n', '-----\n', '====\n', '====\n'):
        got = x.is_underline(line)
        assert got, repr(line)
    for line in ('-\n', '--\n', '---\n', '==\n', '===\n', '===\n','==-==\n', 'abc\n'):
        got = x.is_underline(line)
        assert not got, repr(line)
#@+node:ekr.20210904065459.130: *3* TestImport.test_importers_pascal_methods
def test_importers_pascal_methods(self):
    c = self.c
    x = pascal.Pascal_Importer(c.importCommands, atAuto=False)    
    table = (
        ('procedure TForm1.FormCreate(Sender: TObject);\n', 'procedure TForm1.FormCreate'),
    )
    state = g.Bunch(context='')
    for line, cleaned in table:
        assert x.starts_block(0, [line], state, state)
        assert x.clean_headline(line) == cleaned
#@+node:ekr.20210904065459.132: *3* TestImport.test_importers_xml_is_ws_line
def test_importers_xml_is_ws_line(self):
    c = self.c
    x = xml.Xml_Importer(importCommands = c.importCommands, atAuto = False)
    table = (
       (1, ' \n'),
       (1, '\n'),
       (1, ' '),
       (1, '<!-- comment -->'),
       (0, '  <!-- comment --> Help'),
       (0, 'x <!-- comment -->'),
       (0, 'Help'),
    )
    for expected, line in table:
        got = x.is_ws_line(line)
        assert expected == got, (expected, int(got), repr(line))
#@+node:ekr.20210904065459.133: *3* TestImport.test_importesrs_xml_scan_line
def test_importesrs_xml_scan_line(self):
    c = self.c
    x = xml.Xml_Importer(importCommands = c.importCommands, atAuto = False)
    table = (
        (0, '<tag>'),
        (0, '<tag></tag'),
        (1, '<html'),
        (1, '<html attrib="<">'),
        (0, '<html attrib="<" />'),
        (0, '<html>x</html>'),
        (0, '</br>'), # Tag underflow
        (0, '<br />'),
        (0, '<br/>'),
    )
    for level, line in table:
        prev_state = x.state_class()
        assert prev_state.tag_level == 0
        new_state = x.scan_line(line, prev_state)
        assert new_state.tag_level == level, (new_state, repr(line))
#@+node:ekr.20210904065459.131: ** TestImport.test_importers_python_test_scan_state
def test_importers_python_test_scan_state(self):
    c = self.c
    State = python.Python_ScanState
    # A list of dictionaries.
    if 0:
        tests = [
            g.Bunch(line='s = "\\""', ctx=('', '')),
        ]
    else:
        tests = [
            g.Bunch(line='\n'),
            g.Bunch(line='\\\n'),
            g.Bunch(line='s = "\\""', ctx=('', '')),
            g.Bunch(line="s = '\\''", ctx=('', '')),
            g.Bunch(line='# comment'),
            g.Bunch(line='  # comment'),
            g.Bunch(line='    # comment'),
            g.Bunch(line='a = "string"'),
            g.Bunch(line='a = "Continued string', ctx=('', '"')),
            g.Bunch(line='end of continued string"', ctx=('"', '')),
            g.Bunch(line='a = """Continued docstring', ctx=('', '"""')),
            g.Bunch(line='a = """#', ctx=('', '"""')),
            g.Bunch(line='end of continued string"""', ctx=('"""', '')),
            g.Bunch(line="a = '''Continued docstring", ctx=('', "'''")),
            g.Bunch(line="end of continued string'''", ctx=("'''", '')),
            g.Bunch(line='a = {[(')
        ]
    importer = python.Py_Importer(c.importCommands, atAuto=True)
    importer.test_scan_state(tests, State)
#@-others


#@-leo
