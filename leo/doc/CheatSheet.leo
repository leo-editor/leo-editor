<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo (http://leoeditor.com/leo_toc.html) -->
<?xml-stylesheet ekr_test?>
<leo_file xmlns:leo="http://www.leo-editor.org/2011/leo" >
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.50" body_secondary_ratio="0.50">
	<global_window_position top="93" left="303" height="750" width="1255"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20131019184243.16683"><vh>Leo's cheat sheet</vh>
<v t="ekr.20131019184243.16685"><vh>Key bindings</vh>
<v t="ekr.20131019184243.16686"><vh>Selecting outline nodes</vh></v>
<v t="ekr.20131019184243.16687"><vh>Moving outline nodes</vh></v>
<v t="ekr.20131019184243.16688"><vh>Moving the cursor</vh></v>
</v>
<v t="ekr.20131019184243.16689"><vh>Frequently used commands</vh></v>
<v t="ekr.20131019184243.16690"><vh>Leo directives</vh></v>
<v t="ekr.20131019184243.16691"><vh>Settings</vh></v>
<v t="ekr.20131019184243.16692"><vh>Notable Plugins</vh></v>
<v t="ekr.20131019184243.16693"><vh>External files (@&lt;file&gt; nodes)</vh></v>
<v t="ekr.20131019184243.16694"><vh>Scripting</vh>
<v t="ekr.20131019184243.16695"><vh>Pre-defined symbols</vh></v>
<v t="ekr.20131019184243.16696"><vh>Generators</vh></v>
<v t="ekr.20131019184243.16697"><vh>Commands class</vh></v>
<v t="ekr.20131019184243.16698"><vh>vnode class</vh></v>
<v t="ekr.20131019184243.16699"><vh>position class</vh></v>
<v t="ekr.20131019184243.16700"><vh>leo.core.leoGlobals module</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20131019184243.16683" str_leo_pos="0">@language rest
</t>
<t tx="ekr.20131019184243.16685"></t>
<t tx="ekr.20131019184243.16686">When focus is in the outline pane::

    Right-arrow (expand-and-go-right)
    Left-arrow (contract-or-go-left)
    Up-arrow (goto-prev-visible) 
    Down-arrow (goto-next-visible)
    
Regardless of focus::

    Alt-Home (goto-first-visible-node) 
    Alt-End (goto-last-visible-node)
    Alt-Right-arrow (expand-and-go-right)
    Alt-Left-arrow (contract-or-go-left)
    Alt-Up-arrow (goto-prev-visible) 
    Alt-Down-arrow (goto-next-visible)
</t>
<t tx="ekr.20131019184243.16687">When focus is in the outline::

    Shift-Down-arrow (move-outline-down) 
    Shift-Left-arrow (move-outline-left) 
    Shift-Right-arrow (move-outline-right) 
    Shift-Up-arrow (move-outline-up)

Regardless of focus::

    Alt-Shift-Down-arrow (move-outline-down) 
    Alt-Shift-Left-arrow (move-outline-left) 
    Alt-Shift-Right-arrow (move-outline-right) 
    Alt-Shift-Up-arrow (move-outline-up)
    Ctrl-D (move-outline-down)
    Ctrl-L (move-outline-left) 
    Ctrl-R (move-outline-right)
    Ctrl-U (move-outline-up)
</t>
<t tx="ekr.20131019184243.16688">When focus is in any of Leo's text panes (body pane, log pane, headlines):

    +-------------------+-----------------------+
    | **Key**           | **Move Cursor**       |
    +-------------------+-----------------------+
    | Arrow keys        | one character         |
    +-------------------+-----------------------+
    | Ctrl-LeftArrow    | back one word         |
    +-------------------+-----------------------+
    | Ctrl-RightArrow   | forward one word      |
    +-------------------+-----------------------+
    | Home              | beginning of line     |
    +-------------------+-----------------------+
    | End               | end of line           |
    +-------------------+-----------------------+
    | Ctrl-Home         | beginning of the body |
    +-------------------+-----------------------+
    | Ctrl-End          | end of body           |
    +-------------------+-----------------------+
    | PageDown          | down one page         |
    +-------------------+-----------------------+
    | PageUp            | up one page           |
    +-------------------+-----------------------+
    
Adding the Shift key modifier to any of the keys above
moves the cursor and extends the selected text.
</t>
<t tx="ekr.20131019184243.16689">For much more information, see Leo's Commands Reference: http://leoeditor.com/commands.html

Files::

    Ctrl-N (new) 
    Ctrl-O (open-outline)
    Ctrl-S (save-file) 
    Ctrl-Q (exit-leo)

Focus::

    Alt-T (focus-to-tree) 
    Ctrl-T (toggle-active-pane)
    Ctrl-Tab (tab-cycle-next)
    
Help::

    Alt-0 (vr-toggle)
    F1 (help) 
    F11 (help-for-command) 
    F12 (help-for-python)
    print-bindings
    print-settings
    help-for-...

Find/Replace::

    Ctrl-F (search-with-present-options) 
    Shift-Ctrl-R (replace-string)
    Ctrl-minus (replace-then-find) 
    F3 (find-next) 
    F2 (find-previous)
    
Minibuffer::

    Alt-X (full-command)
    Ctrl-G (keyboard-quit)

Nodes::

    Ctrl-I or Insert (insert-node)
    Ctrl-H (edit-headline)
    &lt;Return&gt; (when editing a headline) (end-edit-headline)
    Ctrl-Shift-C (copy-node)
    Ctrl-Shift-X (cut-node) 
    Ctrl-Shift-V (paste-node) 
    Ctrl-{ (promote)
    Ctrl-} (demote)
    Ctrl-M (mark) 

Undo::

    Ctrl-Z (undo)
    Ctrl-Shift-Z (redo)
</t>
<t tx="ekr.20131019184243.16690">Directives starting with '@ in the leftmost column
    
For full details, see Leo's Directives reference: http://leoeditor.com/directives.html

    @                       # starts doc part
    @c                      # ends doc part
    @color
    @doc                    # starts doc part
    @killcolor
    @nocolor
    @language python
    @language c
    @language rest          # restructured text
    @language plain         # plain text: no syntax coloring.
    @lineending lineending
    @pagewidth 100
    @raw, @end_raw          # @file only.
    @tabwidth -4            # use spaces
    @tabwidth 8             # use tabs
    @nowrap
    @wrap
    
Leading whitespace is allowed (and significant) for::

    @all
    @others
    </t>
<t tx="ekr.20131019184243.16691">For documentation see node: "About this file" in leoSettings.leo.

- Key bindings:     @shortcuts
- Visual settings:  @data qt-gui-plugin-style-sheet
- Enabling plugins: @enabled-plugins

To disable a binding for a key, bind it to do-nothing::

    do-nothing = Insert
    
This overrides the following default binding in leoSettings.leo::

    insert-node = Insert
</t>
<t tx="ekr.20131019184243.16692">See the docstring of these plugins for more details:

- bookmarks.py: Manages URL's used as bookmarks.
- contextmenu.py: Brings up context menu when user right-clicks a headline.
- mod_scripting.py: Supports @button and @command nodes.
- quicksearch.py: Adds Nav tab for searching.
- todo.py: Manages to-do lists and simple project management.
- valuepace.py: Creates an outline-oriented spreadsheet.
- viewrendered.py: Creates a rendering pane. Automatically loaded by Leo's help commands.
</t>
<t tx="ekr.20131019184243.16693">\@&lt;file&gt; nodes create external files::

    @asis &lt;filename&gt;    
    @auto &lt;filename&gt;    
    @edit &lt;filename&gt;
    @file &lt;filename&gt;
    @nosent &lt;filename&gt;  
    @shadow &lt;filename&gt;
    
For full details, see Leo's Directives reference: http://leoeditor.com/directives.html
    
**Section names** have the form::

    &lt;&lt; any text, except double closing angle brackets &gt;&gt;
    
**Section-definition nodes** have headlines starting with a section name.

Leo performs **expansions** for all @&lt;file&gt; nodes except @asis.

Expansion of @all:

- Leo replaces @all by the *unexpanded* body text of *all* nodes.

Expansion of section names and @others:

- Leo replaces section names in body text by the *expanded*
  text of the corresponding section definition node.
  
- Leo replaces @others with the *expanded* text of all nodes
  that *aren't* section-definition nodes.
</t>
<t tx="ekr.20131019184243.16694">This sections lists the ivars, properties, functions and methods most
commonly used in Leo scripts.

**Very important**: use Alt-1 (toggle-autocompleter) and Alt-2
(toggle-calltips) to recreate these lists as you type.
</t>
<t tx="ekr.20131019184243.16695">execute-script predefines::

    c: The commander of the present outline.
    g: The leo.core.leoGlobals module.
    p: The presently selected position, c.p.
    
@test scripts predefine all the above, plus::

    self: The instance of unittest.TestCase
</t>
<t tx="ekr.20131019184243.16696">::

    c.all_positions()
    c.all_unique_positions()
    p.children()
    p.parents()
    p.self_and_parents()
    p.self_and_siblings()
    p.following_siblings()
    p.subtree()
    p.self_and_subtree()
</t>
<t tx="ekr.20131019184243.16697">::

    c.frame         c's outer frame, a leoFrame instance.
    c.user_dict     a temporary dict for use of scripts and plugins.
    c.redraw()
    c.positionExists(p)

Here is a partial list of the **official ivars** of any leoFrame f::

    f.c                     is the frame’s commander.
    f.body                  is a leoBody instance.
    f.body.bodyCtl          is a leoQTextEditWidget instance.
    f.body.bodyCtrl.widget  is a LeoQTextBrowser(QTextBrowser) instance.
    f.log                   is a leoLog instance.
    f.tree                  is a leoQtTree instance.
    f.tree.treeWidget       is a LeoQTreeWidget (a QTreeWidget) instance.
    
Use autocompletion to explore these objects!
</t>
<t tx="ekr.20131019184243.16698">::

    v.b: v's body text.
    v.h: v's headline text.
    v.u: v.unknownAttributes, a persistent Python dictionary.
    
v.u (uA's or unknownAttributes or userAttributes) allow plugins or scripts
to associate persistant data with vnodes. For details see:
http://leoeditor.com/customizing.html#adding-extensible-attributes-to-nodes-and-leo-files
</t>
<t tx="ekr.20131019184243.16699">**Properties**::

    p.b: same as p.v.b.
    p.h: same as p.v.h.
    p.u: same as p.v.u.

**Getters**::

    p.back()
    p.children()
    p.firstChild()
    p.hasBack()
    p.hasChildren()
    p.hasNext()
    p.hasParent()
    p.hasThreadBack()
    p.hasThreadNext()
    p.isAncestorOf(p2)
    p.isAnyAtFileNode()
    p.isAt...Node()
    p.isCloned()
    p.isDirty()
    p.isExpanded()
    p.isMarked()
    p.isRoot()
    p.isVisible()
    p.lastChild()
    p.level()
    p.next()
    p.nodeAfterTree()
    p.nthChild()
    p.numberOfChildren()
    p.parent()
    p.parents()
    p.threadBack()
    p.threadNext()
    p.visBack()
    p.visNext()
    
**Setters**::

    p.setDirty()
    p.setMarked()

**Operations on nodes**::

    p.clone()
    p.contract()
    p.doDelete(new_position)
    p.expand()
    p.insertAfter()
    p.insertAsNthChild(n)
    p.insertBefore()
    p.moveAfter(p2)
    p.moveToNthChildOf(parent,n)
    p.moveToRoot(oldRoot=None)
        # oldRoot **must** be the old root position if it exists.
        
**Moving positions**

The following move positions *themselves*: they change the node to which a
position refers. They do *not* change outline structure in any way! Use
these when generators are not flexible enough::

    p.moveAfter(p2)
    p.moveToBack()
    p.moveToFirstChild()
    p.moveToFirstChildOf(p2)
    p.moveToLastChild()
    p.moveToLastChildOf(p2)
    p.moveToLastNode()
    p.moveToNext()
    p.moveToNodeAfterTree(p2)
    p.moveToNthChild()
    p.moveToNthChildOf(p2)
    p.moveToParent()
    p.moveToRoot()
    p.moveToThreadBack()
    p.moveToThreadNext()
    p.moveToVisBack(c)
    p.moveToVisNext(c)
</t>
<t tx="ekr.20131019184243.16700">For full details, see @file leoGlobals.py in LeoPyRef.leo.

**g vars**::

    g.app
    g.app.gui
    g.app.windowlist
    g.unitTesting
    g.user_dict  # a temporary dict for use of scripts and plugins.
    
**g decorator**::

    @g.command(command-name)
    
**g functions** (the most interesting: there are many more in leoGlobals.py)::
    
    g.angleBrackets()
    g.app.commanders()
    g.app.gui.guiName()
    g.es(*args,**keys)
    g.es_print(*args,**keys)
    g.es_exception()
    g.getScript(c,p,
        useSelectedText=True,
        forcePythonSentinels=True,
        useSentinels=True)
    g.openWithFileName(fileName,old_c=None,gui=None)
    g.os_path_... # Wrappers for os.path methods.
    g.pdb(message='')
    g.toEncodedString(s,encoding='utf-8',reportErrors=False)
    g.toUnicode(s, encoding='utf-8',reportErrors=False)
    g.trace(*args,**keys)
    g.warning(*args,**keys)
</t>
</tnodes>
</leo_file>
