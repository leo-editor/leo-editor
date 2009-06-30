<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="73" left="10" height="768" width="730"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20090628091852.6030" str_leo_pos="3,1"><vh>Startup</vh>
<v t="ville.20090627211608.5783"><vh>@chapters</vh></v>
<v t="ekr.20090628091852.6031"><vh>@settings</vh>
<v t="ekr.20090628091852.8471"><vh>@string target_language = rest</vh></v>
<v t="ekr.20090628092246.4267"><vh>@int page_width = 60</vh></v>
</v>
<v t="ekr.20090628092604.1829"><vh>change log</vh></v>
</v>
<v t="ville.20090627211608.5782"><vh>Welcome to Leo!</vh></v>
<v t="ville.20090627211608.5784"><vh>Tree manipulation basics</vh></v>
<v t="ville.20090627211608.10118" a="E"><vh>External files</vh>
<v t="ville.20090627211608.10116" a="E"><vh>Thin nodes (explanation &amp; excercise)</vh>
<v t="ville.20090627211608.10119" a="E"><vh>@path ~</vh>
<v t="ville.20090627211608.10117"><vh>@@thin myfile_thin.py</vh>
<v t="ville.20090627211608.10120" a="E"><vh>imports &amp; setup routines</vh>
<v t="ville.20090627211608.10128"><vh>init1, init2</vh></v>
<v t="ville.20090627211608.10127"><vh>imports</vh></v>
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
<v t="ville.20090630145410.1517"><vh>@path ~</vh>
<v t="ville.20090630145410.1509" a="E"><vh>@@auto myfile_auto.py</vh>
<v t="ville.20090630145410.1510" a="E"><vh>imports &amp; setup routines</vh>
<v t="ville.20090630145410.1511"><vh>init1, init2</vh></v>
<v t="ville.20090630145410.1512"><vh>imports</vh></v>
</v>
<v t="ville.20090630145410.1513"><vh>class Foo</vh>
<v t="ville.20090630145410.1514"><vh>&lt;&lt; docstring &gt;&gt;</vh></v>
<v t="ville.20090630145410.1515"><vh>spam</vh></v>
<v t="ville.20090630145410.1516"><vh>eggs</vh></v>
</v>
</v>
</v>
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
a normal text editor to see what it looks like.

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
  (or reopen this document), you'll note that  the outline structure was lost, 
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
</tnodes>
</leo_file>
