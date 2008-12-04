<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="10" left="353" height="866" width="859"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20081121105001.1076" str_leo_pos="4,3"><vh>Startup</vh>
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
<v t="ekr.20081121105001.147"
marks="ekr.20081121105001.148,ekr.20081121105001.149,ekr.20081121105001.156,ekr.20081121105001.163,ekr.20081121105001.172,ekr.20081121105001.310,ekr.20081121105001.195,ekr.20081121105001.196,"><vh>@thin qtNotes.txt</vh></v>
</v>
<v t="ekr.20081121105001.1110"><vh>Other guis</vh>
<v t="ekr.20081121105001.12"><vh>@thin cursesGui.py</vh></v>
<v t="ekr.20081121105001.1111"><vh>@thin experimental/__wx_alt_gui.py</vh></v>
<v t="ekr.20081121105001.1707"><vh>@thin experimental/__wx_gui.py</vh></v>
<v t="ekr.20081121105001.80"><vh>@thin ironPythonGui.py</vh></v>
<v t="ekr.20081121105001.595"><vh>@thin swing_gui.py</vh></v>
<v t="ekr.20081121110412.2"
marks="ekr.20081121110412.443,ekr.20081121110412.489,ekr.20081121110412.552,"><vh>@thin tkGui.py</vh></v>
</v>
<v t="ekr.20081121105001.1092"><vh>Qt gui</vh>
<v t="ekr.20081121105001.1093"><vh>QDesigner files</vh>
<v t="ekr.20081121105001.1094"><vh>@auto ../test/qtui_generate.py</vh></v>
<v t="ekr.20081121105001.1095"><vh>@auto qt_main.py</vh></v>
<v t="ekr.20081121105001.1096"><vh>@auto qt_main.ui</vh></v>
<v t="ekr.20081121105001.1097"><vh>@auto qt_quicksearch.py</vh></v>
<v t="ekr.20081121105001.1098"><vh>@auto qt_quicksearch.ui</vh></v>
</v>
<v t="leohag.20081204085551.2"><vh>Qt Scrolled Message Dialog</vh>
<v t="leohag.20081204085551.1" a="E"
expanded="leohag.20081203143921.9,leohag.20081203143921.19,"><vh>@thin scrolledmessage.py</vh></v>
</v>
<v t="ekr.20081121105001.188"
marks="ekr.20081121105001.207,ekr.20081121105001.254,ekr.20081121105001.310,ekr.20081121105001.317,ekr.20081121105001.377,ekr.20081121105001.402,ekr.20081121105001.414,ekr.20081121105001.443,ekr.20081121105001.445,ekr.20081121105001.456,ekr.20081121105001.156,ekr.20081121105001.163,ekr.20081121105001.172,ekr.20081121105001.536,ekr.20081121105001.551,ekr.20081121105001.553,ekr.20081121105001.557,ekr.20081121105001.558,"
expanded="ekr.20081121105001.325,"><vh>@thin qtGui.py</vh></v>
</v>
<v t="ekr.20081121105001.148" a="EM"><vh> qt To do</vh>
<v t="ekr.20081121105001.149" a="M"><vh>Finish colorizer</vh></v>
<v t="ekr.20081121105001.150"><vh>QScintilla stuff</vh></v>
<v t="ekr.20081121105001.151"><vh>Finally/maybe</vh></v>
<v t="ekr.20081124094918.1"><vh>Fix problems with accented characters</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20081121105001.148">@nocolor-node

First:
- Support wrap option.
- Optimize tree updates.
- Clicks in body text do not update row/column position.

Next:
- Allow coloring of icon bar buttons.
- Support multiple body editors.
- Optimize the Qt colorizer.

Finally:
- Install new Qt version and play with QScintilla.
    From QScintilla change log:
    2008/10/12 14:32:05  phil
    QsciScintilla::setSelection() is now implemented using SCI_SETSEL so that the
    carat can be left at either the start or the end of the selection.
    Exposed QsciScintilla::positionFromLineIndex() and
    QsciScintilla::lineIndexFromPosition().
    - Fix problem with accented characters: see child node for notes.
- Add stylesheets for dialogs.
    - Set font for dummy widget in style sheet, then copy that font.
</t>
<t tx="ekr.20081121105001.149">@nocolor-node

- Simulate Tk's handling of tags (an optimization)
- Use Qt threading.
- Handle all colorizer tags.</t>
<t tx="ekr.20081121105001.150">- Check event handling with QScintilla.
- Experiment with sending &lt;shift-tab&gt; directly to QScintilla.
- Call setLexer(0) for nocolor nodes.
- Add settings for syntax coloring.
- Make Scintilla handle Leo markup.</t>
<t tx="ekr.20081121105001.151">- Can style sheets really do the job?
- Flash characters without changing the selection?
- Remove old-style Leo settings?
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
<t tx="ekr.20081124094918.1">http://groups.google.com/group/leo-editor/browse_thread/thread/59c1e5d6acaf4de0

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
<t tx="leohag.20081204085551.2"></t>
</tnodes>
</leo_file>
