<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2"/>
<globals/>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20081121105001.1076"><vh>Startup</vh>
<v t="ekr.20081121105001.1077"><vh>@chapters</vh></v>
<v t="ekr.20081121105001.1078"><vh>@settings</vh>
<v t="ekr.20081121105001.1079"><vh>@page http plugin</vh>
<v t="ekr.20081121105001.1080"><vh>@bool http_active = False</vh></v>
<v t="ekr.20081121105001.1081"><vh>@int  port = 8080</vh></v>
<v t="ekr.20081121105001.1082"><vh>@string rst_http_attributename = rst_http_attribute</vh></v>
</v>
</v>
<v t="ekr.20081121105001.1083"><vh>buttons</vh>
<v t="ekr.20090620053541.3858"><vh>@@button add-test @key=alt-9</vh></v>
<v t="ekr.20081121105001.1084"><vh>@@button settings.leo</vh></v>
<v t="ekr.20081121105001.1085"><vh>@@button scripts.leo</vh></v>
<v t="ekr.20081121105001.1086"><vh>@@button Beautify</vh></v>
<v t="ekr.20081121105001.1087"><vh>@@button Spell</vh></v>
<v t="ekr.20081121105001.1088"><vh>@@button Save</vh></v>
</v>
<v t="ekr.20081121105001.1089"><vh>regex: replace w.bind by c.bind(w...)</vh></v>
<v t="ekr.20081121105001.1090"><vh>@@button change leo imports</vh></v>
<v t="ekr.20100102164747.3702"><vh>Count pages</vh></v>
</v>
<v t="ekr.20081121105001.1110"><vh>Other guis</vh>
<v t="ekr.20081121105001.80"><vh>@file ./obsolete/ironPythonGui.py</vh></v>
<v t="ekr.20081121105001.595"><vh>@file ./obsolete/swing_gui.py</vh></v>
<v t="ekr.20081121110412.2"><vh>@file ./obsolete/tkGui.py</vh></v>
<v t="ekr.20090126093408.1"><vh>@file ./obsolete/wxGui.py</vh></v>
</v>
</vnodes>
<tnodes>
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
<t tx="ekr.20081121105001.1110"></t>
<t tx="ekr.20090620053541.3858">u = c.undoer
w = c.frame.body.bodyCtrl
p2 = p.insertAsNthChild(0)
c.setHeadString(p2,'@test xxx')
s = '''\
if g.unitTesting:
    c,p = g.getTestVars()

    '''
c.setBodyString(p2,s)
c.selectPosition(p2)
c.redraw()
w.setInsertPoint(len(s))
c.bodyWantsFocus()
c.outerUpdate()
</t>
<t tx="ekr.20100102164747.3702">nodes = 0 ; lines = 0
for p in c.all_unique_positions():
    nodes += 1
    lines += len(g.splitLines(p.b))

pages = ((nodes * 10) + lines) / 50
s = "%d nodes,  %d lines, %d pages" % (nodes,lines,pages)
print(s); g.es(s)</t>
</tnodes>
</leo_file>
