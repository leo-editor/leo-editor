<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="73" left="10" height="971" width="913"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20081121105001.1076" str_leo_pos="5,1,2,1,3,3,1"><vh>Startup</vh>
<v t="ekr.20081121105001.1077"><vh>@chapters</vh></v>
<v t="ekr.20081121105001.1078"><vh>@settings</vh>
<v t="ekr.20081121105001.1079"><vh>@page http plugin</vh>
<v t="ekr.20081121105001.1080"><vh>@bool http_active = False</vh></v>
<v t="ekr.20081121105001.1081"><vh>@int  port = 8080</vh></v>
<v t="ekr.20081121105001.1082"><vh>@string rst_http_attributename = rst_http_attribute</vh></v>
</v>
</v>
<v t="ekr.20081121105001.1083"><vh>buttons</vh>
<v t="ekr.20081121105001.1084"><vh>@@button settings.leo</vh></v>
<v t="ekr.20081121105001.1085"><vh>@@button scripts.leo</vh></v>
<v t="ekr.20081121105001.1086"><vh>@@button Beautify</vh></v>
<v t="ekr.20081121105001.1087"><vh>@@button Spell</vh></v>
<v t="ekr.20081121105001.1088"><vh>@@button Save</vh></v>
</v>
<v t="ekr.20081121105001.1089"><vh>regex: replace w.bind by c.bind(w...)</vh></v>
<v t="ekr.20081121105001.1090"><vh>@@button change leo imports</vh></v>
</v>
<v t="ekr.20081121105001.1108"><vh>Notes</vh>
<v t="ekr.20081121105001.147"><vh>@thin qtNotes.txt</vh></v>
</v>
<v t="ekr.20081121105001.148"><vh> qt To do</vh>
<v t="ekr.20081215074704.13"><vh>Bugs 5</vh>
<v t="ekr.20090128113654.1"><vh>Recent files menu is duplicated in qt gui</vh></v>
<v t="ekr.20090123073723.12"><vh>Fix php section coloring</vh></v>
<v t="ekr.20081215074704.16"><vh>Mark finds doesn't work in Qt gui plugin</vh></v>
<v t="ekr.20081124094918.1"><vh>Fix problems with scim</vh></v>
<v t="ekr.20081215074704.18"><vh>Finish qt gui delete_range method</vh></v>
<v t="ekr.20090131123901.2"><vh>Sometime a plug box appears wrongly</vh></v>
</v>
<v t="ekr.20090128083504.1"><vh>Fix plugins 2</vh></v>
<v t="ekr.20081215074704.19"><vh>Features 5</vh>
<v t="ekr.20081215162017.4"><vh>Allow coloring of script buttons</vh></v>
<v t="ekr.20081215162017.5"><vh>Support multiple body editors</vh></v>
<v t="ekr.20081215074704.20"><vh>Change background color of body pane depending on focus</vh></v>
<v t="ekr.20081215074704.21"><vh>Add drag and drop</vh></v>
<v t="ekr.20081121105001.151"><vh>Clean up settings</vh>
<v t="ekr.20081121105001.150"><vh>QScintilla stuff</vh></v>
</v>
</v>
</v>
<v t="ekr.20081121105001.1110"><vh>Other guis</vh>
<v t="ekr.20081121105001.12"><vh>@thin cursesGui.py</vh></v>
<v t="ekr.20081121105001.80"><vh>@thin ironPythonGui.py</vh></v>
<v t="ekr.20081121105001.595"><vh>@thin swing_gui.py</vh></v>
<v t="ekr.20081121110412.2"><vh>@thin tkGui.py</vh></v>
<v t="ekr.20090126093408.1"><vh>@thin wxGui.py</vh></v>
</v>
<v t="ekr.20090124174652.7"><vh>@thin baseNativeTree.py</vh></v>
<v t="ekr.20081121105001.1092" a="E"><vh>Qt gui</vh>
<v t="ekr.20081121105001.1093"><vh>QDesigner files</vh>
<v t="ekr.20081121105001.1094"><vh>@auto ../test/qtui_generate.py</vh></v>
<v t="ekr.20081121105001.1095"><vh>@auto qt_main.py</vh></v>
<v t="ekr.20081121105001.1096"><vh>@auto qt_main.ui</vh></v>
<v t="ekr.20081121105001.1097"><vh>@auto qt_quicksearch.py</vh></v>
<v t="ekr.20081121105001.1098"><vh>@auto qt_quicksearch.ui</vh></v>
</v>
<v t="ekr.20081121105001.188" a="E"
expanded="ekr.20081121105001.194,ekr.20081121105001.205,ekr.20081121105001.206,ekr.20081121105001.212,ekr.20081121105001.227,ekr.20081121105001.235,ekr.20081121105001.236,ekr.20081121105001.238,ekr.20081121105001.471,ekr.20081121105001.513,ekr.20081205131308.27,ekr.20081121105001.515,ekr.20081121105001.516,ekr.20081121105001.521,ekr.20081121105001.524,ekr.20081121105001.541,ekr.20081121105001.572,ekr.20081121105001.573,ekr.20081121105001.578,"><vh>@thin qtGui.py</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20081121105001.148"></t>
<t tx="ekr.20081121105001.150">- Check event handling with QScintilla.
- Experiment with sending &lt;shift-tab&gt; directly to QScintilla.
- Call setLexer(0) for nocolor nodes.
- Add settings for syntax coloring.
- Make Scintilla handle Leo markup.
- Install new Qt version and play with QScintilla.
    From QScintilla change log:
    2008/10/12 14:32:05  phil
    QsciScintilla::setSelection() is now implemented using SCI_SETSEL so that the
    carat can be left at either the start or the end of the selection.
    Exposed QsciScintilla::positionFromLineIndex() and
    QsciScintilla::lineIndexFromPosition().
    - Fix problem with accented characters: see child node for notes.</t>
<t tx="ekr.20081121105001.151">- Can style sheets really do the job?

- Remove old-style Leo settings?

- Add stylesheets for dialogs.
    - Set font for dummy widget in style sheet, then copy that font.
</t>
<t tx="ekr.20081121105001.1076"></t>
<t tx="ekr.20081121105001.1077"></t>
<t tx="ekr.20081121105001.1078">@nocolor</t>
<t tx="ekr.20081121105001.1079"> 
        
        
        </t>
<t tx="ekr.20081121105001.1080"></t>
<t tx="ekr.20081121105001.1081"></t>
<t tx="ekr.20081121105001.1082"></t>
<t tx="ekr.20081121105001.1083"></t>
<t tx="ekr.20081121105001.1084">c.openLeoSettings()</t>
<t tx="ekr.20081121105001.1085">name = "scripts.leo"
fileName = g.os_path_join(g.app.loadDir,"..","scripts",name)
ok,frame = g.openWithFileName(fileName,c)
if not ok:
    g.es("not found: %s" % name)</t>
<t tx="ekr.20081121105001.1086">c.prettyPrintPythonNode()</t>
<t tx="ekr.20081121105001.1087">c.spellCommands.openSpellTab()</t>
<t tx="ekr.20081121105001.1088">c.save()</t>
<t tx="ekr.20081121105001.1089">([a-zA-Z_.]+)\.bind\((.*)\)(.*)$
c.bind(\1,\2)\3

[a-zA-Z_.]+

(\w)+(\.\w+)*

abc.xyz.pdq

# Bind w.bind with more than two args (none found)

w.bind\(.*,.*,.*$

[-w]\.bind\(</t>
<t tx="ekr.20081121105001.1090">change = True # True: actually make the changes.
trace = True

print '-' * 40

tag = 'import leo' ; n = len('import ')

for p in p.self_and_subtree_iter():
    result = []
    for s in g.splitlines(p.bodyString()):
        i = s.find(tag,0)
        if i &gt; -1:
            # Do nothing if we have already done the translation.
            i2 = s.find('&lt;&lt;') ; i3 = s.find('import leo.core')
            if i2 == -1 and i3 == -1:
                i += n
                j = g.skip_c_id(s,i)
                word = s[i:j]
                rest = s[j:]
                if rest.strip().startswith('as'):
                    s = s[:i] + 'leo.core.' + word + rest
                else:
                    s = s[:i] + 'leo.core.' + word + ' as ' + word + rest
                if trace:
                    print p.headString()
                    j,k=g.getLine(s,i) ; print s[j:k]
        result.append(s)
    result = ''.join(result)

    if change and result != p.bodyString():
        c.setBodyString(p,result)

</t>
<t tx="ekr.20081121105001.1092"></t>
<t tx="ekr.20081121105001.1093"></t>
<t tx="ekr.20081121105001.1108"></t>
<t tx="ekr.20081121105001.1110"></t>
<t tx="ekr.20081124094918.1">@nocolor-node

http://groups.google.com/group/leo-editor/browse_thread/thread/59c1e5d6acaf4de0

I've some more information about the problems with accent previously
reported:
- I can confirm that they are caused by the interaction scim+leo (with
and without the qt plugin). If scim is not started leo works fine. If
scim is running the problems appear and are slightly different with
and without the qt plugin. The workaround is obvious: don't use leo
and scim at the same time :-)
- accents are not working in the qt plugin when scintilla is used. If
qt-use-scintilla=False I can write this:

àáä (the same for the rest of vowels)

but if qt-use-scintilla=True when I enter the same sequence in the
keyboard I get:

`aaa (the same for the rest of vowels)

- the problem with the ñ character (reported previously too) is only
present in the qt plugin (both with and without scintilla)
</t>
<t tx="ekr.20081215074704.13"></t>
<t tx="ekr.20081215074704.16">http://groups.google.com/group/leo-editor/browse_thread/thread/b2af78fbb36d3590</t>
<t tx="ekr.20081215074704.18">@nocolor-node

http://groups.google.com/group/leo-editor/browse_thread/thread/51edf3b44d6a587e

revno: 1259.1.10
revision-id: terry_n_brown@yahoo.com-20081130181632-ci0ioaksewdvc257

I added code so that this no longer derails the initialization process,
i.e. just catch the exception and continue.  I don't know what's wrong
except I first noticed it after a tkinter update from Ubuntu.  I
think.  Anyway, that's my story :)

When I added the "clean recent files" menu option long before this
traceback showed up I had a heap of trouble deleting just the file
entries on the recent files menu.  It was originally hardwired that the
menu have a "Clear list" item, and then the file entries, but I wanted
to make it get it's command entries from @menu @settings and add the
files afterward and that was a lot of fiddling.  I.e. originally it
deleted everything and added the "Clear list" item before rebuilding
the file list, now it either tries to delete only the file entries, or
stores the entries before the files (from @menu) and adds them back
before the files each time, I forget which finally worked.

What's my point?  It would be nice if delete_range "just worked".  It's
a 'pass' in qt, and I would guess recent files is the only thing in the
entire code base that uses it.

The menu tree seems to me to be "write only", i.e. not readable, at
least from the Leo API, of course you can walk it in a gui specific
way.  Not necessarily a problem, but would be nice if it was more
robustly dynamic.  Or maybe I'm missing something, but I've only seen
functions which find a menu based on knowing it exists before hand.</t>
<t tx="ekr.20081215074704.19"></t>
<t tx="ekr.20081215074704.20">@nocolor-node

http://groups.google.com/group/leo-editor/browse_thread/thread/1cce885a697d0236/5aea5d0587b47b92?lnk=gst&amp;q=command+and+insert#5aea5d0587b47b92

Set focus in/out events.</t>
<t tx="ekr.20081215074704.21"></t>
<t tx="ekr.20081215162017.4"></t>
<t tx="ekr.20081215162017.5">@

The body part is a QFrame with QGridLayout.

For an example, run this script:
@c

from PyQt4.QtGui import QTextEdit
w = QTextEdit()
c.frame.top.ui.leo_body_inner_frame.layout().addWidget(w,0,1)
</t>
<t tx="ekr.20090123073723.12">http://groups.google.com/group/leo-editor/browse_thread/thread/41870d58718b7b7a#</t>
<t tx="ekr.20090128083504.1">@nocolor-node

rClick


After the qt-plugin merge (rev 1251 ), the image plugin no longer works. I
couldn't find any mention of gsimage in the diff.

 # Erase image if it was previously displayed
             a = g.app ; c = keywords.get("c")

-            if a.gsimage:
+            if getattr(a, 'gsimage', None):
                 try:
                     c.frame.body.bodyCtrl.delete(a.gsimage)
                 except:
</t>
<t tx="ekr.20090128113654.1">Using r1372 and the Qt plugin, I get strange results with the recent-
files menu item.  To reproduce:

1. open a leo window (call this window 1)
2. open an existing .leo file using file-&gt;open... (this opens a new window, window 2)
3. go to the file-&gt;Recent-files menu item of window 1.  The file-list is duplicated.
4. repeat step 2.  Now window 1's recent-files list is duplicated twice...

** Affects: leo-editor
    Importance: Undecided
        Status: New

--
recent-files menu item list is duplicated
https://bugs.launchpad.net/bugs/313320
You received this bug notification because you are a member of The Leo
editor team, which is subscribed to leo-editor.

Status in Leo: a programmer's editor and more: New

Bug description:
Using r1372 and the Qt plugin, I get strange results with the recent-files menu item.  To reproduce:

1. open a leo window (call this window 1)
2. open an existing .leo file using file-&gt;open... (this opens a new window, window 2)
3. go to the file-&gt;Recent-files menu item of window 1.  The file-list is duplicated.
4. repeat step 2.  Now window 1's recent-files list is duplicated twice...</t>
<t tx="ekr.20090131123901.2"># It may happen after a paste?
</t>
</tnodes>
</leo_file>
