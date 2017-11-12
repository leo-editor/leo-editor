
This is the theory of operation document for py2cs.py. The most interesting aspect of this script is the TokenSync class. This class provides a reliable way of associating tokenizer tokens with ast nodes.


### The problem

The initial version of py2cs.py (the script) used only tokens. This solved all token-related problems, but made parsing difficult. Alas, it is [difficult](http://stackoverflow.com/questions/16748029/how-to-get-source-corresponding-to-a-python-ast-node) to associate tokens with ast nodes.

The script needs the following token-related data:

- The **ignored lines** (comment lines and blank lines) that precede any statement.

- The **trailing comment** strings that might follow any line.

- Optionally, the **line breaks** occurring within lines. At present, this script does not preserve such breaks, and it's probably not worth doing. Indeed, automatically breaking long lines seems more useful, especially considering that coffeescript lines may be substantially shorter than the corresponding python lines.

- The **exact spelling** of all strings.

The [ast_utils module](
https://bitbucket.org/plas/thonny/src/3b71fda7ac0b66d5c475f7a668ffbdc7ae48c2b5/thonny/ast_utils.py?at=master) purports to solve this problem with convoluted adjustments to the col_offset field. This approach is subject to subtle Python bugs, and subtle differences between Python 2 and Python 3. There is a better way...

### Design

The main idea is to use *only* the ast.lineno fields and the tokenizer module to recreate token data. The design assumes only that both the ast.lineno field and Python's tokenizer module are solid. This is a much more reasonable assumption than assuming that the col_offset field always tells the truth. In short, this design *ignores* the ast.col_offset field.

At startup, the TokenSync ctor assigns all the incoming tokens to various lists.  These lists are indexed by lineno:

    ts.line_tokens[i]: all the tokens on line i
    ts.string_tokens[i]: all string tokens on line i
    st.ignored_lines: the blank or comment line on line i

It is very easy to create these lists. The code does not depend on any arcane details.

#### Recovering the exact spelling of stings.

ts.synch_string returns the *next* string on the line. Here it is, stripped of defensive code:

    def sync_string(self, node):
        '''Return the spelling of the string at the given node.'''
        tokens = self.string_tokens[node.lineno-1]
        token = tokens.pop(0)
        self.string_tokens[node.lineno-1] = tokens
        return self.token_val(token)

Stripped of defensive code, the do_Str visitor is just:

    def do_Str(self, node):
        '''A string constant, including docstrings.'''
        return self.sync_string(node)

#### Recovering otherwise ignored nodes

**ts.leading_lines(node)** returns a list of otherwise ignored lines that
precede the node's line that have not already been returned.
**ts.leading_string(node)** is a convenience method that returns ''.join(ts.leading_lines(node)). The visitors of the CoffeeScriptTraverser class show how to use these methods.

### Using the TokenSync class

The present code is driven by ast trees, but each visitor of the CoffeeScriptTraverser class takes care to preserve **otherwise-ignored tokens**. These are tokens that would otherwise be ignored: namely blank lines and comments, both entire-line comments and trailing comments.

The visitor for each statement intersperses otherwise ignored tokens using calls to the TokenSync class.  The simplest cases are like this:

    def do_Break(self, node):
        head = self.leading_string(node)
        tail = self.trailing_comment(node)
        return head + self.indent('break') + tail

The leading_string and trailing_comment methods simply redirect to the corresponding methods in the TokenSync class.  Saves a bit of typing. Compound statements are a bit more bother, but not overly so. For example:

    def do_If(self, node):

        result = self.leading_lines(node)
        tail = self.trailing_comment(node)
        s = 'if %s:%s' % (self.visit(node.test), tail)
        result.append(self.indent(s))
        for z in node.body:
            self.level += 1
            result.append(self.visit(z))
            self.level -= 1
        if node.orelse:
            tail = self.tail_after_body(node.body, node.orelse, result)
            result.append(self.indent('else:' + tail))
            for z in node.orelse:
                self.level += 1
                result.append(self.visit(z))
                self.level -= 1
        return ''.join(result)

The line:

        tail = self.tail_after_body(node.body, node.orelse, result)

is a hack needed to compensate for the lack of an actual ast.Else node.

### Summary

The TokenSync class is, a new, elegant, unexpected and happy development. It is a relatively easy-to-use helper that allows parser-based code to preserve data that is not easily accessible in parse trees.

The TokenSync class avoids [problems with the col_offset field](
http://stackoverflow.com/questions/16748029/how-to-get-source-corresponding-to-a-python-ast-node) in ast nodes. The TokenSync class depends only on the ast.lineno field and the tokenize module. We can expect it to be rock solid.

Edward K. Ream
February 20 to 25, 2016



