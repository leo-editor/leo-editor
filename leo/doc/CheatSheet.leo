<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
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
<v t="ekr.20160401160027.1"><vh>Executing minibuffer commands</vh></v>
<v t="ekr.20131019184243.16689"><vh>Frequently used commands</vh></v>
<v t="ekr.20131019184243.16690"><vh>Leo directives</vh></v>
<v t="ekr.20131019184243.16691"><vh>Settings</vh></v>
<v t="ekr.20131031101712.19298"><vh>Node types</vh></v>
<v t="ekr.20131019184243.16692"><vh>Notable Plugins</vh></v>
<v t="ekr.20131019184243.16693"><vh>External files (@&lt;file&gt; nodes)</vh>
<v t="ekr.20160410111255.1"><vh>Path expressions</vh></v>
<v t="ekr.20160410111226.1"><vh>Sections</vh></v>
</v>
<v t="ekr.20131019184243.16694"><vh>Scripting</vh>
<v t="ekr.20131019184243.16695"><vh>Pre-defined symbols</vh></v>
<v t="ekr.20170315015836.1"><vh>LeoApp class</vh></v>
<v t="ekr.20131019184243.16697"><vh>Commands class</vh></v>
<v t="ekr.20131019184243.16698"><vh>VNode class</vh></v>
<v t="ekr.20131019184243.16699"><vh>Position class</vh></v>
<v t="ekr.20131019184243.16700"><vh>The leoGlobals module</vh></v>
<v t="ekr.20170311121717.1"><vh>Test driven development</vh></v>
<v t="ekr.20170403190104.1"><vh>Performance gotchas</vh></v>
<v t="ekr.20170403190120.1"><vh>About names</vh></v>
</v>
<v t="ekr.20170311122518.1"><vh>Command line options</vh></v>
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
<v t="ekr.20160315141648.1"><vh>Code academy</vh>
<v t="ekr.20160315141648.3"><vh>CA: uA's</vh></v>
<v t="ekr.20160315141648.4"><vh>CA: icons</vh></v>
<v t="ekr.20160315141648.5"><vh>CA: using git</vh></v>
<v t="ekr.20160315141648.6"><vh>CA: finding nodes with c.cloneFindByPredicate</vh></v>
</v>
<v t="ekr.20131019184243.16694"></v>
</vnodes>
<tnodes>
<t tx="ekr.20131019184243.16683">@wrap
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
<t tx="ekr.20131019184243.16693">@&lt;file&gt; nodes create external files:

    @asis &lt;filename&gt;        write only, no sentinels, exact line endings
    @auto &lt;filename&gt;        recommended
    @clean &lt;filename&gt;       recommended
    @edit &lt;filename&gt;        @edit node contains entire file
    @file &lt;filename&gt;        recommended
    @nosent &lt;filename&gt;      write only, no sentinels

This table summarizes the differences between @&lt;file&gt; nodes:

                             Sections &amp;   File data in
    @&lt;file&gt; kind  Sentinels?  @others?    .leo file?    Notes             
    ------------  ---------- -----------  ------------  -----
    @asis            no         no           yes
    @auto            no         yes          no         1, 2
    @auto-xx         no         yes          no         1, 2
    @clean           no         yes          yes     
    @edit            no         no           no    
    @file            yes        yes          no
    @nosent          no         yes          yes
    
**Note 1**: @auto nodes read files using language-specific importers.
By default, the file's extension determines the importer:

    Extensions                  Importer
    ----------                  --------
    .c, .cc, .c++, .cpp,.cxx    C
    .cs', .c#'                  C Sharp
    .el                         Elisp
    .h, .h++                    C
    .html, .htm                 HTML
    .ini                        Config file
    .ipynb                      Jupyter notebook
    .java                       Java
    .js                         JavaScript
    .md                         Markdown
    .org                        Org Mode
    .otl                        Vim outline
    .pas                        Pascal
    .php                        PHP
    .py, .pyi, .pyw             Python
    .rest, .rst                 reStructuredText
    .ts                         TypeScript
    .xml                        XML
    
**Note 2**: You can also specify importers *explicitly* as follows:

    @auto-xxx           Importer
    ---------           --------
    @auto-ctext         ctext
    @auto-markdown      markdown
    @auto-md            markdown
    @auto-org           org-mode
    @auto-org-mode      org-mode
    @auto-otl           vimoutline
    @auto-vim-outline   vimoutline
    @auto-rst           reStructuredText
    
For full details, see Leo's Directives reference:
http://leoeditor.com/directives.html
    </t>
<t tx="ekr.20131019184243.16694">@wrap

This section lists the ivars, properties, functions and methods most
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
<t tx="ekr.20131019184243.16697">Ivars:

    c.config                c's configuration object
    c.frame                 c's outer frame, a leoFrame instance.
    c.undoer                c's undo handler.
    c.user_dict             A temporary dict for use of scripts and plugins.
    
SubCommanders:

    # in leo/core...
    c.atFileCommands
    c.chapterController
    c.fileCommands
    c.findCommands
    c.importCommands
    c.keyHandler = c.k
    c.persistenceController
    c.printingController
    c.rstCommands
    c.shadowController
    c.tangleCommands
    c.testManager
    c.vimCommands

    # In leo/commands...
    c.abbrevCommands
    c.controlCommands
    c.convertCommands
    c.debugCommands
    c.editCommands
    c.editFileCommands
    c.gotoCommands
    c.helpCommands
    c.keyHandlerCommands
    c.killBufferCommands
    c.rectangleCommands
    c.spellCommands
    
For example, c.k is an instance of the LeoKeys class in leo/core/leoKeys.py.
    
Generators:

    c.all_positions()
    c.all_unique_positions()
    
New in Leo 5.5: All generators yield distinct positions.
    
Most useful methods:

    c.isChanged()
    c.deletePositionsInList(aList, callback=None)
                            # safely deletes all the positions in aList.
    c.positionExists(p)
    c.redraw(p=None)        # Redraw the screen. Select p if given.
    c.redraw_later()        # Ensure that Leo redraws the outline.
    c.save()                # Save the present outline.
    c.selectPosition()      # Select the position, without redrawing the screen.
    
Suppressing screen flash when redrawing the outline:

    try:
        c.disable_redraw()
        &lt;&lt; Code that might otherwise update the outline &gt;&gt;
    finally:
        c.enable_redraw()
        c.redraw()
    
**Official ivars** of any leoFrame f:

    f.c                     is the frame’s commander.
    f.body                  is a leoBody instance.
    f.body.bodyCtl          is a leoQTextEditWidget instance.
    f.body.bodyCtrl.widget  is a LeoQTextBrowser(QTextBrowser) instance.
    f.log                   is a leoLog instance.
    f.tree                  is a leoQtTree instance.
    f.tree.treeWidget       is a LeoQTreeWidget (a QTreeWidget) instance.
    
Use autocompletion to explore these objects!
</t>
<t tx="ekr.20131019184243.16698">Ivars:

    v.b:    v's body text.
    v.gnx:  v's gnx.
    v.h:    v's headline text.
    v.u:    v.unknownAttributes, a persistent Python dictionary.
    
v.u (uA's or unknownAttributes or userAttributes) allow plugins or scripts
to associate persistent data with vnodes. For details see:
http://leoeditor.com/customizing.html#adding-extensible-attributes-to-nodes-and-leo-files
</t>
<t tx="ekr.20131019184243.16699">**Properties**:

    p.b: same as p.v.b. *Warning*: p.b = s is expensive.
    p.h: same as p.v.h. *Warning*: p.h = s is expensive.
    p.u: same as p.v.u.
    
**Generators**:

    p.children()
    p.parents()
    p.self_and_parents()
    p.self_and_siblings()
    p.following_siblings()
    p.subtree()
    p.self_and_subtree()
    
New in Leo 5.5: All generators yield distinct positions.

**Getters**:

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
    
**Setters**:

    p.setDirty() *Warning*: p.setDirty() is expensive.
    p.setMarked()

**Operations on nodes**:

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
        
**Moving positions**:

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

**g vars**:

    g.app
    g.app.gui
    g.app.windowlist
    g.unitTesting
    g.user_dict  # a temporary dict for use of scripts and plugins.
    
**g decorator**:

    @g.command(command-name)
    
**g functions** (the most interesting: there are many more in leoGlobals.py):
    
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
<t tx="ekr.20131030071311.17126">**Important**: to take effect, all settings must be descendants of this
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
<t tx="ekr.20160315141648.1">@language rest
@wrap

Leo's Code Academy posts discuss how to do useful things in Leo. The following are distilled from online discussions about Leo's scripting.</t>
<t tx="ekr.20160315141648.3">uA's (user Attributes) associate arbitrary data with any vnode. uA's are dictionaries of dictionaries--an **outer dictionary** and zero or more **inner dictionaries**. The outer dictionary associates plugin names (or Leo's core) with inner dictionaries. The inner dictionaries carry the actual data.

The v.u or p.v properties get and set uA's. You can think of p.u as a synonym for p.v.unknownAttributes on both sides of an assignment. For example::

    plugin_name = 'test_plugin'
    d = p.u.get(plugin_name,{})
    d ['n'] = 8
    p.u [plugin_name] = d

p.u is the outer dictionary. p.u.get.(plugin_name, {}) is the inner dictionary. The last line is all that is needed to update the outer dictionary!

It is easy to search for particular uA's. The following script prints all the keys in the outer-level uA dictionaries:

    for p in c.all_unique_positions():
        if p.u:
            print(p.h, sorted(p.u.keys()))

This is a typical usage of Leo's generators.  Generators visit each position (or node) quickly. Even if you aren't going to program much, you should be aware of how easy it is to get and set the data in each node. In fact, now would be a great time to read Leo's Scripting Tutorial again :-) This will allow you to "dream bigger" with Leo.

The following script creates a list of all positions having an icon, that is, an outer uA dict with a 'icon' key.

    aList = [p.copy() for p in c.all_unique_positions() if 'icon' in p.u]
    print('\n'.join([p.h for p in aList]))

*Important*: If you don't understand these lines, please study Python's list comprehensions.  They are incredibly useful. '\n'.join(aList) is a great idiom to know.  str.join is one of python's most useful string methods. It converts between lists and strings.
</t>
<t tx="ekr.20160315141648.4">@language rest

This script inserts three icons in the current outline node. Running the script again will insert three more::

@language python

    table = (
        'edittrash.png',
        'connect_no.png',
        'error.png',
    )
    for icon in table:
        fn = g.os_path_finalize_join(g.app.loadDir,
            '..', 'Icons', 'Tango', '16x16', 'status', icon)
        if g.os_path_exists(fn):
            c.editCommands.insertIconFromFile(path=fn)
        
@language rest
        
This deletes all icons of the node at position p::

    c.editCommands.deleteNodeIcons(p=p)
</t>
<t tx="ekr.20160315141648.5">Using Leo’s latest sources from GitHub is highly recommended. Once git is installed, the following gets the latest Leo sources::

    git clone https://github.com/leo-editor/leo-editor.git

Thereafter, you can update Leo's sources with::

    git pull

Git is great in tracking history and reverting unwanted changes. And it has many other benefits.

Using git is very similar to using bzr or hg or any other SCCS.  To change Leo, you add files, you commit files, and you push files.  That's about it.
</t>
<t tx="ekr.20160315141648.6">@language rest

c.cloneFindByPredicate is a powerful new addition to Leo.  Here is its docstring:

    Traverse the tree given using the generator, cloning all positions for
    which predicate(p) is True. Undoably move all clones to a new node, created
    as the last top-level node. Returns the newly-created node. Arguments:

    generator,      The generator used to traverse the tree.
    predicate,      A function of one argument p returning true if p should be included.
    failMsg=None,   Message given if nothing found. Default is no message.
    flatten=False,  True: Move all node to be parents of the root node.
    iconPath=None,  Full path to icon to attach to all matches.
    redraw=True,    True: redraw the screen.
    undo_type=None, The undo/redo name shown in the Edit:Undo menu.
                    The default is 'clone-find-predicate'
                    
For example, clone-find-all-marked command is essentially:
    
@language python

    @cmd('clone-find-all-marked')
    def cloneFindMarked(self, flatten):
        
        def isMarked(p):
            return p.isMarked()
            
        self.cloneFindByPredicate(
            generator = self.all_unique_positions,
            predicate = isMarked,
            failMsg = 'nothing found',
            flatten = flatten,
            undoType = 'clone-find-marked',
        )
        
@language rest

The predicate could filter on an attribute or *combination* of attributes. For example, the predicate could return p has attributes A and B but *not* attribute C. This instantly gives Leo full database query capabilities. If we then hoist the resulting node we see *all and only* those nodes satisfying the query.

These following position methods make it easy to skip @ignore trees or @&lt;file&gt; trees containing @all::
        
    p.is_at_all()          True if p is an @&lt;file&gt; node containing an @all directive.
    p.in_at_all()          True if p is in an @&lt;file&gt; tree whose root contains @all.
    p.is_at_ignore()       True if p is an @ignore node
    p.in_at_ignore_tree()  True if p is in an @ignore tree.

For example, here is how to gather only those marked nodes that lie outside any @ignore tree::

@language python

    def isMarked(p):
        return p.isMarked() and not p.in_at_ignore_tree()
      
    c.cloneFindByPredicate(
        generator = self.all_unique_positions,
        predicate = isMarked,
        flatten = flatten,
        undoType = 'gather-marked',
    )
</t>
<t tx="ekr.20160401160027.1">Alt-X puts focus in the minibuffer. Ctrl-G escapes from the minibuffer.

Once there, you can use tab completion to reduce typing. For example, &lt;Alt-X&gt;open&lt;tab&gt; shows all commands that start with open.

Hit &lt;Enter&gt; to run a complete command.

Ctrl-P (repeat-complex-command) repeat the last command entered from the minibuffer.

Leo maintains a **command history list** of all minibuffer commands you have entered.

When focus is in the minibuffer, UpArrow shows the previous minibuffer command, and DnArrow show the commands before that.

The body text of an @data history-list *setting node* preloads commands into the command history list, ignoring lines starting with '#'. For example::

    run-pylint
    beautify-tree
    cff
    sort-lines
    # show-data
    check-clones
    expand-log-pane
    contract-log-pane</t>
<t tx="ekr.20160410111226.1">**Section names** have the form::

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
<t tx="ekr.20160410111255.1">Within @path and @&lt;file&gt; paths, Leo evaluates ``{{exp}}`` with the the following symbols defined: ``c``, ``g``, ``p``, ``os`` and ``sys``.  For example::

    @file {{os.path.abspath(os.curdir)}}/abc.py
    
refers to the file abc.py in (absolute path of) the current directory.
</t>
<t tx="ekr.20170311121717.1">- Use imp.reload to reload all changed modules.
- Make sure to *instantiate* any changed objects.
- See "Unit testing with Leo" for full details.
</t>
<t tx="ekr.20170311122518.1">Usage: launchLeo.py [options] file1, file2, ...

Options:
  -h, --help            show this help message and exit
  --debug               enable debug mode
  --diff                use Leo as an external git diff
  --fullscreen          start fullscreen
  --ipython             enable ipython support
  --fail-fast           stop unit tests after the first failure
  --gui=GUI             gui to use (qt/qttabs/console/null)
  --listen-to-log       start log_listener.py on startup
  --load-type=LOAD_TYPE
                        @&lt;file&gt; type for loading non-outlines from command
                        line
  --maximized           start maximized
  --minimized           start minimized
  --no-cache            disable reading of cached files
  --no-plugins          disable all plugins
  --no-splash           disable the splash screen
  --screen-shot=SCREENSHOT_FN
                        take a screen shot and then exit
  --script=SCRIPT       execute a script and then exit
  --script-window=SCRIPT_WINDOW
                        open a window for scripts
  --select=SELECT       headline or gnx of node to select
  --session-restore     restore previously saved session tabs at startup
  --session-save        save session tabs on exit
  --silent              disable all log messages
  --trace-binding=BINDING
                        trace key bindings
  --trace-focus         trace changes of focus
  --trace-plugins       trace imports of plugins
  --trace-setting=SETTING
                        trace where setting is set
  --trace-shutdown      trace shutdown logic
  -v, --version         print version number and exit
  --window-size=WINDOW_SIZE
                        initial window size (height x width)</t>
<t tx="ekr.20170315015836.1">Ivars:

    g.app                   A LeoApp instance.
    g.app.gui               A LeoGui instance. 
    g.app.pluginsController A LeoPluginsController instance.
    g.app.*                 Leo's global variables.
</t>
<t tx="ekr.20170403190104.1">**Warning**: The p.b and p.h setters and p.setDirty() are *very* expensive:

- p.b = s calls c.setBodyString(p, s) which will recolor body text and update the node's icon.
- p.h = s calls c.setHeadString(p, s) which calls p.setDirty().
- p.setDirty() changes the icons of all ancestor @file nodes.

In contrast, the corresponding p.v.b and p.v.b setters and p.v.setDirty() are extremely fast.

Usually, code *should* use the p.b and p.h setters and p.setDirty(), despite their cost, because they update Leo's outline pane properly. Calling c.redraw() is *not* enough.

These performance gotchas become important for repetitive commands, like cff, replace-all and recursive import. In such situations, code should use p.v.b and p.v.h setters instead of p.b and p.h setters.
</t>
<t tx="ekr.20170403190120.1">Scripts may safely assume that most names defined in Leo's core will never change. Names used outside their defining module *can't* be changed, because doing so would impact existing user scripts. This includes virtually everything in leoGlobals.py, and many names in leoCommands.py and other files. The only names that might change are unlikely every to be of use to scripts anyway. For example, helper functions.
</t>
</tnodes>
</leo_file>
