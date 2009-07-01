<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="186" left="316" height="759" width="1233"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20090628091852.6030" str_leo_pos="3,0,2"><vh>Startup</vh>
<v t="ville.20090627211608.5783"><vh>@chapters</vh></v>
<v t="ekr.20090628091852.6031"><vh>@settings</vh>
<v t="ekr.20090628091852.8471"><vh>@string target_language = rest</vh></v>
<v t="ekr.20090628092246.4267"><vh>@int page_width = 60</vh></v>
</v>
<v t="ekr.20090628092604.1829"><vh>change log</vh></v>
</v>
<v t="ville.20090627211608.5782"><vh>Welcome to Leo!</vh></v>
<v t="ville.20090627211608.5784"><vh>Tree manipulation basics</vh></v>
<v t="ville.20090630234425.12394" a="E"><vh>Programming</vh>
<v t="ville.20090627211608.10118" a="E"><vh>External files</vh>
<v t="ville.20090627211608.10116"><vh>Thin nodes (explanation &amp; excercise)</vh>
<v t="ville.20090627211608.10119" a="E"><vh>@path ~</vh>
<v t="ville.20090627211608.10117"><vh>@@thin myfile_thin.py</vh>
<v t="ville.20090627211608.10120"><vh>imports &amp; setup routines</vh>
<v t="ville.20090627211608.10127"><vh>imports</vh></v>
<v t="ville.20090627211608.10128"><vh>init1, init2</vh></v>
</v>
<v t="ville.20090627211608.10122"><vh>class Foo</vh>
<v t="ville.20090627211608.10123"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="ville.20090627211608.10124"><vh>spam</vh></v>
<v t="ville.20090627211608.10125"><vh>eggs</vh></v>
</v>
</v>
</v>
</v>
<v t="ville.20090627211608.10129"><vh>Auto nodes</vh>
<v t="ville.20090630145410.1517" a="E"><vh>@path ~</vh>
<v t="ville.20090630145410.1509"><vh>@@auto myfile_auto.py</vh>
<v t="ville.20090630145410.1510"><vh>imports &amp; setup routines</vh>
<v t="ville.20090630145410.1512"><vh>imports</vh></v>
<v t="ville.20090630145410.1511"><vh>init1, init2</vh></v>
</v>
<v t="ville.20090630145410.1513"><vh>class Foo</vh>
<v t="ville.20090630145410.1514"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="ville.20090630145410.1515"><vh>spam</vh></v>
<v t="ville.20090630145410.1516"><vh>eggs</vh></v>
</v>
</v>
</v>
</v>
<v t="ville.20090701175849.1532"><vh>Shadow nodes</vh>
<v t="ville.20090701175849.1542" a="E"><vh>@path ~</vh>
<v t="ville.20090701175849.1543"><vh>@@shadow myfile_shadow.py</vh>
<v t="ville.20090701175849.1544"><vh>imports &amp; setup routines</vh>
<v t="ville.20090701175849.1545"><vh>imports</vh></v>
<v t="ville.20090701175849.1546"><vh>init1, init2</vh></v>
</v>
<v t="ville.20090701175849.1547"><vh>class Foo</vh>
<v t="ville.20090701175849.1548"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="ville.20090701175849.1549"><vh>spam</vh></v>
<v t="ville.20090701175849.1550"><vh>eggs</vh></v>
</v>
</v>
</v>
</v>
</v>
</v>
<v t="ville.20090630234425.12395"><vh>Configuration (enabling plugins etc.)</vh>
<v t="ville.20090630234425.14847"><vh>Find out your ~/.leo directory (script)</vh></v>
<v t="ville.20090630234425.12396"><vh>@@settings</vh>
<v t="ville.20090630234425.14842"><vh>@enabled-plugins</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20090628091852.6030">This node contains settings and other "machinery" that you
can usually ignore.</t>
<t tx="ekr.20090628091852.6031"></t>
<t tx="ekr.20090628091852.8471"></t>
<t tx="ekr.20090628092246.4267">The page width for wrapping doc parts in derived files.

Valid values: any nonzero positive integer.</t>
<t tx="ekr.20090628092604.1829">Added settings to use rest by default and use a page width
of 60 for wrapping paragraphs.

Created the startup node and its descendants.</t>
<t tx="ville.20090627211608.5782">This is a brief tutorial for getting familiar with basic Leo
functionality. Click around and experiment.

Note that you probably want to save your own "working copy"
of this file before proceeding further. Do that by "File -&gt;
Save as".</t>
<t tx="ville.20090627211608.5783"></t>
<t tx="ville.20090627211608.5784">You can use Leo as fairly typical outliner. Play around with
some of the commands from the Outline menu:

- Click the expansion box of nodes_ to show and hide their
  children.

- The ``Insert Node`` command (``Ctrl+I``) inserts a new
  headline into the outline.

- The ``Cut Node`` command (``Ctrl+Shift+X``) deletes a
  headline and all its children, and copies the structure to
  clipboard - ready to paste with ``Paste Node`` command
  (``Ctrl+Shift+V``). Use ``Copy Node`` command
  (``Ctrl+Shift+C``) to copy node to clipboard without
  deleting it from outline. Copy-paste command family works
  across different Leo documents.

- The ``Move Up`` (``Ctrl+U``), ``Move Down`` (``Ctrl+D``),
  ``Move Left`` (``Ctrl+L``) and ``Move Right`` (``Ctrl+R``)
  commands move the currently selected node, along with all
  its descendants.

- The ``Promote`` (``Ctrl+}``) command makes all the
  children of a headline siblings of the headline. The
  ``Demote`` (``Ctrl+{``) command makes all following
  siblings_ of a headline children of the headline.

- Move around the tree and expand/collapse nodes by pressing
  Alt + arrow keys. This also moves the focus to tree, so,
  after pressing Alt + arrow, you can move around by using
  arrow keys alone. Return the focus to the body control by
  pressing ``Enter``.

- To edit the headline, use press ``Ctrl+H``. This works
  regardless of whether body or headline has focus.

- We'll discuss the ``Clone Node`` command in the next
  section.

You enter `body text`_ for any node by selecting the node's
headline in the outline pane and then typing in the body
pane. Leo has a full range of `editing commands`_ that apply
to the body pane.

See Chapter 2 of Leo's documentation for more.</t>
<t tx="ville.20090627211608.10116">Remove the first @ from @thin in the subtree below and save
(ctrl+s) to create an "external" file which is directly
usable outside leo - try opening the resulting myfile.py in
a normal text editor (e.g. from right-click menu on the @thin node) 
to see what it looks like.

Note the @others directive, and the the lines that look like

#@-node:ville.20090627211608.10122:class Foo

These are called "sentinels", and they are needed to
preserve the tree structure in the external files. They
allow your tree structure to survive, even when someone else
edits the source (or you edit it yourself in an external
editor).</t>
<t tx="ville.20090627211608.10117">@others
@language python</t>
<t tx="ville.20090627211608.10118">"External file" means a file that resides on your file
system - if you are programming, these are the files you
eventually want to create to get something useful out of Leo
- e.g. C++ or Python source code that you can feed to the
compiler/interpreter.</t>
<t tx="ville.20090627211608.10119"> </t>
<t tx="ville.20090627211608.10120"></t>
<t tx="ville.20090627211608.10122">class Foo:
    &lt;&lt; docstring &gt;&gt;
    @others


</t>
<t tx="ville.20090627211608.10123">""" Some sort of useful class """

</t>
<t tx="ville.20090627211608.10124">def spam(self):
    pass

</t>
<t tx="ville.20090627211608.10125">def eggs(self):
    pass</t>
<t tx="ville.20090627211608.10127">import os
import sys

</t>
<t tx="ville.20090627211608.10128">def init1():
    print "init1"

def init2():
    print "init2"</t>
<t tx="ville.20090627211608.10129">If the sentinels in thin nodes are unacceptable for your workflow 
(typically the case when you are the only one using Leo in a 
particular project), you can use @auto nodes to "play well with 
others". @auto nodes understand the structure of the source code
(parsers exist for popular languages), and create the "typical"
outline for the code when the file is loaded. When you save, the outline is 
written back.

Do the same thing you did with @@thin - i.e., 

- Remove the first @, and save. 
- Check the resulting file (`/myfile_auto.py) and observe that it has 
  no sentinels.   
- There is no "magic" involved. If you execute 'File -&gt; Read auto nodes" 
  (or right click on @auto node and choose "Refresh from disk", or reopen 
  this document), you'll note that  the outline structure was lost, 
  and the "parsed" structure is created instead. This is the cost
  of using @auto nodes.</t>
<t tx="ville.20090630145410.1509">@others
@language python</t>
<t tx="ville.20090630145410.1510"></t>
<t tx="ville.20090630145410.1511">def init1():
    print "init1"

def init2():
    print "init2"</t>
<t tx="ville.20090630145410.1512">import os
import sys

</t>
<t tx="ville.20090630145410.1513">class Foo:
    &lt;&lt; docstring &gt;&gt;
    @others


</t>
<t tx="ville.20090630145410.1514">""" Some sort of useful class """

</t>
<t tx="ville.20090630145410.1515">def spam(self):
    pass

</t>
<t tx="ville.20090630145410.1516">def eggs(self):
    pass</t>
<t tx="ville.20090630145410.1517"></t>
<t tx="ville.20090630234425.12394"></t>
<t tx="ville.20090630234425.12395">- If you are just starting, you should create your own myLeoSettings.leo in ~/.leo. We'll do that next.

- Create the file first: 
  - File -&gt; New (or ctrl+N)
  - File -&gt; Save as
  - Navigate to ~/.leo
  - save as myLeoSettings.leo

- In the current tree, there is @@settings subtree. We are copying this to the new file. Go to node @@settings,
  and copy the whole tree to clipboard (ctrl+shift+c).
  
- Select the document that has myLeoSettings.leo (the one you just created). Drop the settings tree there
  (ctrl+shift+v), Remove extra @ from @@settings, and save again.

- Now, you should be all set. Verify that it worked by Help-&gt;open myLeoSettings.leo
</t>
<t tx="ville.20090630234425.12396"></t>
<t tx="ville.20090630234425.14842"># Leo loads plugins in the order they appear here.
# File names may be indented as desired.

# Standard plugins enabled in official distributions....

plugins_menu.py
open_with.py
leo_to_html.py
mod_scripting.py
quicksearch.py
UNL.py
contextmenu.py

# The plugins manager plugin does not
# understand @enabled-plugins nodes.
# plugin_manager.py

# The rst3 plugin is no longer needed.
# It's code has been moved to Leo's core
# rst3.py

# These plugins used to be enabled when using the tk plugin.
# cleo.py
# hoist.py
# image.py
# nav_buttons.py
# threading_colorizer.py

# All other plugins.
# Order is important for enabled plugins that
# add items to the icon area.

# ConceptualSort.py
# EditAttributes.py
# FileActions.py
# Library.py
# nodeActions.py
# UASearch.py
# URLloader.py
# UniversalScrolling.py

# add_directives.py
# arrows.py
# at_folder.py
# at_view.py
# autotrees.py
# base64Packager.py
# bibtex.py
# chapter_hoist.py
# cleo.py
# color_markup.py
# datenodes.py
# detect_urls.py
# dyna_menu.py
# fastGotoNode.py
# footprints.py
# groupOperations.py
# hoist.py
# image.py
# import_cisco_config.py
# ipython.py
# keybindings.py
# leoOPML.py
# leo_to_html.py
# leo_to_rtf.py
# leoupdate.py
# macros.py
# mod_autosave.py
# mod_http.py
# mod_labels.py
# mod_read_dir_outline.py
# mod_shadow.py
# multifile.py
# nav_buttons.py
# newButtons.py
# niceNosent.py
# nodebar.py
# nodenavigator.py
# open_shell.py
# paste_as_headlines.py
# pie_menus.py
# pretty_print.py
# print_cp.py
# quickMove.py
# rClick.py
# read_only_nodes.py
# rowcol.py
# run_nodes.py
# s_menu.py
# scheduler.py
# searchbox.py
# shortcut_button.py
# slideshow.py
# table.py
# templates.py
# trace_tags.py
# vim.py
# word_count.py
# word_export.py
# xcc_nodes.py
# xemacs.py
# xsltWithNodes.py
# zodb.py
# quicksearch.py
# tomboy_import.py
# ctagscompleter.py
# colorize_headlines.py
# contextmenu.py</t>
<t tx="ville.20090630234425.14847"># execute this script by ctrl+b to find out where your ~/.leo is

g.es('Homedir is at ',g.app.homeLeoDir)

</t>
<t tx="ville.20090701175849.1532">In this tree, you can experiment with @shadow. It combines the benefits
of @thin and @auto - namely, it publishes a file without sentinels, but
still allows the tree structure to survive, even if the external file
is edited outside Leo.

The cost is complexity - @shadow relies on a "shadow file" that remembers
the structure, and a sophisticated diff/patch algorithm that merges
the changes from the external file to the tree structure.

Experiment by editing the external file outside Leo and doing Right click
-&gt; refresh from disk on the @shadow node. </t>
<t tx="ville.20090701175849.1542"></t>
<t tx="ville.20090701175849.1543">@others
@language python</t>
<t tx="ville.20090701175849.1544"></t>
<t tx="ville.20090701175849.1545">import os
import sys

</t>
<t tx="ville.20090701175849.1546">def init1():
    print "init1"

def init2():
    print "init2"</t>
<t tx="ville.20090701175849.1547">class Foo:
    &lt;&lt; docstring &gt;&gt;
    @others


</t>
<t tx="ville.20090701175849.1548">""" Some sort of useful class """

</t>
<t tx="ville.20090701175849.1549">def spam(self):
    pass

</t>
<t tx="ville.20090701175849.1550">def eggs(self):
    pass</t>
</tnodes>
</leo_file>
