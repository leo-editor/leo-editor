#@+leo-ver=5-thin
#@+node:ekr.20040916084945: * @file macros.py
#@+<< docstring >>
#@+node:ekr.20061102090532: ** << docstring >>
r''' Creates new nodes containing parameterized section reference.

.. No longer available: http://sourceforge.net/forum/message.php?msg_id=2444117

This plugin adds nodes under the currently selected tree that are to act as
section references. To do so, go the Outline menu and select the
'Parameterize Section Reference' command. This plugin looks for a top level node called
'Parameterized Nodes'. If it finds a headline that matches the section reference
it adds a node/nodes to the current tree.

To see this in action, do the following:

0. **Important**: in the examples below, type << instead of < < and
   type >> instead of > >.  Docstrings can not contain section references!

1. Create a node called 'Parameterized Nodes', with a sub-node called  < < Meow \>\>.
   The body of < < Meow > > should have the text::

        I mmmm sooo happy I could  < < 1$  > >.
        But I don't know if I have all the  < < 2$  > >
        money in the world.

2. In a node called A, type::

        < < meow( purrrrrr, zzooot )  > >
        (leave the cursor at the end of the line)

3. In a node called B, type::

         < < meow ( spit or puke, blinkin  )  > >
        (leave the cursor at the end of the line)

4. Leave the cursor in Node A at the designated point.

5. Go to Outline and select Parameterize Section Reference.

The plugin searches the outline, goes to level one and finds a Node with the Headline,
"Parameterized Nodes". It looks for nodes under that headline with the the headline
<\< meow >\>. It then creates this node structure under Node A::

        < < meow ( purrrrrr, zzooot ) > >
            < <2$> >
            < <1$> >

6. Examine the new subnodes of Node A:

        < < meow ( purrrrrr, zzooot ) > >
            contains the body text of the < < meow > > node.
        < < 1$ > > contains the word purrrrrr.
        < < 2$ > > contains the word zzooot.

7. Go to Node B, and leave the cursor at the designated point.

Go to Outline Menu and select Parameterize Section Reference command.

8. Examine the new subnodes of Node B.

It's a lot easier to use than to explain!

'''
#@-<< docstring >>
__version__ = "2.0" # BobS & EKR.
#@+<< version history >>
#@+node:ekr.20040916091520: ** << version history >>
#@+at
# 
# 1.2 EKR:
# - Converted to outline.
# - Use g.angleBrackets to enclose lines with < < and > >.
# - Use new instead of start2 hook.
# - onCreate creates a new class for each commander.
# - Removed all globals.
# 1.3 EKR: Changed 'new_c' logic to 'c' logic.
# 1.4 EKR: Replaced tree.begin/endUpdate by c.beginEndUpdate.
# 1.5 EKR: Added event param to parameterize.
# 1.6 EKR: imported leoNodes.
# 1.7 Rich Ries: improved the docstring.
# 1.8 EKR: Add the menu only for the tkinter gui.
# 1.9 BobS: Revised self.pattern & added traces.
# 2.0 EKR: Many code cleanups & fixed several crashers.
#@-<< version history >>
import leo.core.leoGlobals as g
import re
import pprint
#@+others
#@+node:ekr.20070302121133: ** init
def init ():
    '''Return True if this plugin loaded correctly.'''
    # Ok for unit testing: adds command to Outline menu.
    g.registerHandler( ('new','menu2') ,onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:ekr.20040916091520.1: ** onCreate
def onCreate(tag,keywords):
    '''Create the per-commander instance of ParamClass.'''
    c = keywords.get("c")
    if c:
        ParamClass(c)
#@+node:ekr.20040916091520.2: ** class ParamClass
class ParamClass(object):

    #@+others
    #@+node:ekr.20040916091520.3: *3* __init__
    def __init__ (self,c):
        '''Ctor for ParamClass.'''
        self.c = c
        # self.pattern = g.angleBrackets(r'\w*?\(([^,]*?,)*?([^,])+?\)') + '$'
        self.pattern = g.angleBrackets(r'\s*\w*?\s*\(\s*([^,]*?,)\s*?(\w+)\s*\)\s*') + '$'
        # g.trace("self.pattern: %s" % self.pattern)
        self.regex = re.compile(self.pattern)
        self.addMenu() # Now gui-independent.
    #@+node:ekr.20040916084945.1: *3* parameterize
    def parameterize (self,event=None):
        trace = False and not g.unitTesting
        c = self.c
        w = c.frame.body.wrapper
        # EKR: always search for parms.
        params = self.findParameters(c.p)
        if not params:
            return
        sr = s = w.getAllText()
        if trace: g.trace("body: %s" % sr)
        sr = sr.split('\n')
        i = w.getInsertPoint()
        row,col = g.convertPythonIndexToRowCol(s,i)
        sr = sr[row]
        sr = sr[:col]
        sr = sr.rstrip()
        if trace: g.trace("regex search on: %s" % sr)
        match = self.regex.search(sr)
        if not match:
            g.es("no match")
            return
        sr = sr [match.start(): match.end()]
        if trace: g.trace("found sr",sr)
        for child in c.p.children():
            if child.h == sr:
                return
        pieces = sr.split('(',1)
        searchline = pieces [0] + ">>"
        # EKR: added rstrip().
        pieces [1] = pieces [1].rstrip().rstrip('>')
        pieces [1] = pieces [1].rstrip().rstrip(')')
        sections = pieces [1].split(',')
        if trace: g.trace(
            "pieces: %s\n" % (pprint.pformat(pieces)),
            "searchline: %s\n" % (searchline),
            "sections: %s\n" % (pprint.pformat(sections)))
        node = None
        for child in params.children():
            if child.matchHeadline(searchline):
                node = child
                break
        else:
            if trace: g.trace('not found',searchline)
            return
        c.setCurrentPosition(node)
        if trace: g.trace("found: %s'\n%s" % (node.h,node.b))
        for i, section in enumerate(sections):
            p = c.p.insertAsNthChild(i)
            p.b = section
            p.h = g.angleBrackets(str(i+1)+"$")
        c.redraw()
    #@+node:ekr.20040916084945.2: *3* findParameters
    def findParameters (self,p):
        '''Find the parameterized nodes in p's parents..'''
        trace = False and not g.unitTesting
        tag = "parameterized nodes"
        for parent in p.parents():
            if trace: g.trace('parent:',parent.h)
            for sib in parent.self_and_siblings():
                if sib.h.lower() == tag:
                    if trace: g.trace('found:',sib.h)
                    return sib
        g.es('not found',tag)
        return None
    #@+node:ekr.20040916084945.3: *3* addMenu
    def addMenu(self):
        '''Add a submenu in the outline menu.'''
        c = self.c
        table = (
            ("Parameterize Section Reference",None,self.parameterize),
        )
        c.frame.menu.createMenuItemsFromTable("Outline",table,dynamicMenu=True)
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
