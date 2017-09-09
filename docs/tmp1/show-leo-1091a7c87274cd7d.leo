<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo (http://leoeditor.com/leo_toc.html) -->
<?xml-stylesheet type="text/xsl" href="/leo_to_html.xsl"?>
<leo_file xmlns:leo="http://www.leo-editor.org/2011/leo" >
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20131030071311.17125"><vh>Startup</vh>
<v t="ekr.20131030071311.18741"><vh>@button make-sphinx</vh></v>
<v t="ekr.20131030071311.17126"><vh>@settings</vh>
<v t="ekr.20131030071311.18671"><vh>@string target_language = rest</vh></v>
<v t="ekr.20131030071311.17128"><vh>For rst3 command</vh>
<v t="ekr.20131030071311.17127"><vh>@bool rst3_call_docutils = True</vh></v>
<v t="ekr.20131030071311.17129"><vh>@bool rst3_write_intermediate_file = True</vh></v>
<v t="ekr.20131030071311.18669"><vh>@string rst3_write_intermediate_extension = .txt</vh></v>
</v>
</v>
</v>
<v t="ekr.20131019184243.16683"><vh>Leo's cheat sheet</vh>
<v t="ekr.20131019184243.16685"><vh>Key bindings</vh>
<v t="ekr.20131019184243.16686"><vh>Selecting outline nodes</vh></v>
<v t="ekr.20131019184243.16687"><vh>Moving outline nodes</vh></v>
<v t="ekr.20131019184243.16688"><vh>Moving the cursor</vh></v>
</v>
<v t="ekr.20131019184243.16689"><vh>Frequently used commands</vh></v>
<v t="ekr.20131019184243.16690"><vh>Leo directives</vh></v>
<v t="ekr.20131019184243.16691"><vh>Settings</vh></v>
<v t="ekr.20131031101712.19298"><vh>Node types</vh></v>
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
<v t="ekr.20131030071311.18723"><vh>The rst3 tutorial</vh>
<v t="ekr.20131030071311.18732"><vh>@rst ~/myDocument.html</vh>
<v t="ekr.20131030071311.18733"><vh>Chapter I</vh>
<v t="ekr.20131030071311.18734"><vh>@rst-ignore</vh></v>
</v>
<v t="ekr.20131030071311.18735"><vh>@rst-ignore-tree Chapter 2+</vh>
<v t="ekr.20131030071311.18736"><vh>Chapter II</vh>
<v t="ekr.20131030071311.18737"><vh>translation</vh></v>
</v>
</v>
<v t="ekr.20131030071311.18738"><vh>Chapter XII</vh></v>
<v t="ekr.20131030071311.18739"><vh>@rst-no-head The End</vh></v>
</v>
<v t="ekr.20131102044158.16563"><vh>~/myDocument.html.txt</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20131019184243.16683"></t>
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

Copy/Paste (text)::

    Ctrl-C (copy-text)
    Ctrl-K (kill)
    Ctrl-V (paste-text)
    Ctrl-X (cut-text)
    Ctrl-Y (yank)
    Alt-Y  (yank-pop)
    kill-...

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
- valuespace.py: Creates an outline-oriented spreadsheet.
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
<t tx="ekr.20131019184243.16694">This section lists the ivars, properties, functions and methods most
commonly used in Leo scripts.

**Very important**: use Alt-1 (toggle-autocompleter) and Alt-2
(toggle-calltips) to recreate these lists as you type.

As an alternative to this chapter, Jacob Peck has written a more informal scripting tutorial:
http://blog.suspended-chord.info/2014/01/28/intro-to-leo-scripting/</t>
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
<t tx="ekr.20131030071311.17125">By convention, a Startup node contains settings, scripts, etc.
that mostly one wants to have hidden.
</t>
<t tx="ekr.20131030071311.17126">**Imortant**: to take effect, all settings must be descendants of this
@settings node.

**Note**: This file colors text as reStructuredText by default because of
the setting::

    @string target_language = rest
</t>
<t tx="ekr.20131030071311.17127"># Use False when using Sphinx</t>
<t tx="ekr.20131030071311.17128"></t>
<t tx="ekr.20131030071311.17129"></t>
<t tx="ekr.20131030071311.18669"></t>
<t tx="ekr.20131030071311.18671">The default language if no @language or @comment is in effect.

Valid values are (case is ignored):

actionscript,c,csharp,css,cweb,elisp,html,java,latex,
pascal,perl,perlpod,php,plain,plsql,python,rapidq,rebol,shell,tcltk.</t>
<t tx="ekr.20131030071311.18723">Here is an expanded version of the example from
http://leoeditor.com/tutorial-rst3.html

Control-click the URL above to open the page in your browser.

Notes:

1. The Startup node in this file contains the settings for the rst3
   command. If you use sphinx, **set @bool rst3_call_docutils = False**.
   
2. Leo will not create ~/myDocument.html automatically. Only the rst3
   command does that.
   
3. Executing the make-sphinx command will do everything needed to make
   myDocument.html. The @button make-sphinx node (a child of the Startup
   node) creates the make-sphinx command.
   
4. The node myDocument.html.txt is the intermediate file produced by the
   rst3 command.
</t>
<t tx="ekr.20131030071311.18732">#############
War and Peace
#############

        by Leo Tolstoy/Tolstoi
        
        BOOK ONE: 1805
</t>
<t tx="ekr.20131030071311.18733">"Well, Prince, so Genoa and Lucca are now just family estates of the
Buonapartes. But I warn you, if you don't tell me that this means war, if
you still try to defend the infamies and horrors perpetrated by that
Antichrist--I really believe he is Antichrist--I will have nothing more to
do with you and you are no longer my friend, no longer my 'faithful slave',
as you call yourself! But how do you do? I see I have frightened you--sit
down and tell me all the news."

It was in July, 1805, and the speaker was the well-known Anna Pavlovna
Scherer, maid of honor and favorite of the Empress Marya Fedorovna. With
these words she greeted Prince Vasili Kuragin, a man of high rank and
importance, who was the first to arrive at her reception. Anna Pavlovna had
had a cough for some days. She was, as she said, suffering from la grippe;
grippe being then a new word in St. Petersburg, used only by the elite.

...stuff happens...</t>
<t tx="ekr.20131030071311.18734">You can make whatever notes 
to yourself you like here, 
as these lines won't appear 
in the output files. :)

</t>
<t tx="ekr.20131030071311.18735">Neither this node nor any descendant node will appear in the output file.</t>
<t tx="ekr.20131030071311.18736">TL;DR

...la femme la plus seduisante de Petersbourg,* ...</t>
<t tx="ekr.20131030071311.18737">*The most fascinating woman in Petersburg.</t>
<t tx="ekr.20131030071311.18738">From the time the law of Copernicus was discovered and proved, the mere
recognition of the fact that it was not the sun but the earth that moves
sufficed to destroy the whole cosmography of the ancients.

...
</t>
<t tx="ekr.20131030071311.18739">..  and now we skip to the end of last chapter, while demonstrating use of an
..  organizer node (a node whose name does not appear in the output document),
..  and that rst comments appear as html comments (try 'View Source' on
..  output.html)

In the first case it was necessary to renounce the consciousness of an
unreal immobility in space and to recognize a motion we did not feel; in
the present case it is similarly necessary to renounce a freedom that does
not exist, and to recognize a dependence of which we are not conscious.
   
--- The End ---
</t>
<t tx="ekr.20131030071311.18741">@language python
import os
trace = True
g.cls()
c.setComplexCommand('make-sphinx')
c.save()
aList = c.rstCommands.rst3()
if aList:
    path = g.os_path_finalize_join(g.app.loadDir,'..','doc','html')
    os.chdir(path)
    if len(aList) &gt; 1: g.execute_shell_commands('make clean',trace=trace)
    g.execute_shell_commands('make html',trace=trace)
    fn = aList[0].h.strip() if len(aList) == 1 else 'leo_toc.html'
    fn = g.os_path_finalize_join(path,'_build','html',g.os_path_basename(fn))
    if g.os_path_exists(fn):
        # Don't wait for this command to exit!
        g.execute_shell_commands(['&amp;%s' % (fn)],trace=trace)
</t>
<t tx="ekr.20131031101712.19298">Supported by Leo's core:

- @chapters, @chapter
- @rst, @rst-no-head, @rst-ignore, @rst-ignore-tree
- @settings
- @test, @testsetup, @testclass
- @url

Within @settings trees:

- @bool, @color, @directory, @encoding, @int
- @float, @font, @ratio, @path, @string
- @enabled-plugins
- @buttons, @commands
- @menus, @menu, @menuat, @item
- @openwith, @shortcuts

Supported by plugins:

- bookmarks.py: @bookmarks, @bookmark
- at_folder.py: @folder
- at_produce.py: @produce
- at_view.py: @clip, @strip, @view
- expfolder.py: @expfolder
- mod_scripting.py: @button, @command, @script
- viewrendered.py: @graphics-script, @image, @html, @md, @movie and @svg
- rss.py: @feed

</t>
<t tx="ekr.20131102044158.16563">.. rst3: filename: ~/myDocument.html

#############
War and Peace
#############

        by Leo Tolstoy/Tolstoi
        
        BOOK ONE: 1805

Chapter I
+++++++++

"Well, Prince, so Genoa and Lucca are now just family estates of the
Buonapartes. But I warn you, if you don't tell me that this means war,
if you still try to defend the infamies and horrors perpetrated by
that Antichrist--I really believe he is Antichrist--I will have
nothing more to do with you and you are no longer my friend, no longer
my 'faithful slave,' as you call yourself! But how do you do? I see
I have frightened you--sit down and tell me all the news."

...stuff happens...

Chapter XII
+++++++++++

From the time the law of Copernicus was discovered and proved, the
mere recognition of the fact that it was not the sun but the earth
that moves sufficed to destroy the whole cosmography of the
ancients.

...

.. and now we skip to the end of last chapter, while demonstrating use of an
    organizer node (a node whose name does not appear in the output document),
    and that rst comments appear as html comments (try 'View Source' on
    output.html)

In the first case it was necessary to renounce the consciousness
of an unreal immobility in space and to recognize a motion we did
not feel; in the present case it is similarly necessary to renounce
a freedom that does not exist, and to recognize a dependence of
which we are not conscious.
   
--- The End ---

</t>
</tnodes>
</leo_file>
