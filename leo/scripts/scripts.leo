<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="21" left="303" height="896" width="923"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20070615131954" str_leo_pos="1"><vh>Startup</vh>
<v t="ekr.20070427110751"><vh>@chapters</vh></v>
<v t="ekr.20041001211817"><vh>Buttons</vh>
<v t="ekr.20051020124457"><vh>Disabled buttons</vh>
<v t="ekr.20041230121429"><vh>@@ button pydoc</vh></v>
<v t="ekr.20050210180937"><vh>@@ button jython</vh></v>
<v t="ekr.20050704170739"><vh>@@button Ipython</vh></v>
<v t="ekr.20050821072028"><vh>@@button Lines Up</vh>
<v t="ekr.20050821072028.1"><vh>moveLinesUp</vh></v>
</v>
<v t="ekr.20050821081021"><vh>@@button Lines Down</vh>
<v t="ekr.20050821081021.1"><vh>moveLinesDown</vh></v>
</v>
<v t="ekr.20050930124917"><vh>@@button outlineToClipboard</vh></v>
<v t="ekr.20051023104813"><vh>@@button check-dirty</vh></v>
</v>
<v t="ekr.20050805150320"><vh>@@button rst3</vh></v>
<v t="ekr.20041001194357"><vh>@@button unit test</vh></v>
<v t="ekr.20051025091355"><vh>@@button Spell</vh></v>
<v t="ekr.20051025070722"><vh>@@button Beautify</vh></v>
</v>
</v>
<v t="ekr.20061008055616"><vh>Scripts</vh>
<v t="ekr.20051110111150" tnodeList="ekr.20051110111150"><vh>@file leoScripts.txt</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20041001194357"># You can run all tests by selecting the Unit Test headline.

import leoTest

leoTest.doTests(all=False)</t>
<t tx="ekr.20041001211817"></t>
<t tx="ekr.20041230121429">import os, sys, threading

python = sys.executable
pythonDir,junk = g.os_path_split(python)
pydoc = g.os_path_join(pythonDir,'Lib','pydoc.py')
command = '%s %s -g' % (python,pydoc)

# Execute the command in a separate thread.
def go():
    os.system(command)
    
threading.Thread(target=go).start()</t>
<t tx="ekr.20050210180937"># **** Change these as needed ***
import os, sys

tempFileName = g.os_path_abspath(
    g.os_path_join(g.app.testDir,'jythonScript.py'))

if sys.platform == 'win32':
    jython = r'C:\Jython-21\jython.bat'
    command = '%s "%s"' % (jython,tempFileName) 
else:
    jython = r'cd ~/jython-2.1 ; ./jython'
    command = '%s "%s" &amp;' % (jython,tempFileName)

script = g.getScript(c,p).strip()
if not script:
    s = "no script in %s" % p.headString()
    g.es(s) ; print s
else:
    f = file(tempFileName,'w')
    f.write(script + '\n')
    f.close()
    print command
    os.system(command)
</t>
<t tx="ekr.20050704170739">from IPython.Shell import IPShellEmbed

ipshell = IPShellEmbed()
ipshell()</t>
<t tx="ekr.20050805150320">import leoPlugins

rst3 = leoPlugins.getPluginModule('rst3')

if rst3:
    rst3.controller.processTree(p)
else:
    rst3 = leoPlugins.loadOnePlugin('rst3',verbose=True)
    if rst3:
        g.es('rst3 loaded')
        rst3.onCreate('tag',{'c':c})
    else:
        # Ask to be removed.
        g.app.scriptDict['removeMe'] = True</t>
<t tx="ekr.20050821072028"># Move selected text of the body up one line.

@others

moveLinesUp(c,p)</t>
<t tx="ekr.20050821072028.1">def moveLinesUp(c,p):
    
    undoType = 'Move Lines Up'
    head,lines,tail,oldSel,oldYview = c.getBodyLines()
    if not head or not lines: return
    # A slight adjustment: lines doesn't end in '\n'.
    head = g.splitLines(head)
    lines = '\n'.join(lines) + '\n'
    lines = g.splitLines(lines)
    # Move the lines up.
    lines.append(head[-1])
    head = head[:-1]
    # Convert back to strings.
    head = ''.join(head)
    lines = ''.join(lines)[:-1] # Undo the adjustment above.
    # Adjust selection.
    sel1,sel2 = oldSel
    row,col = sel1.split('.') ; sel1 = '%d.%s' % (int(row)-1,col)
    row,col = sel2.split('.') ; sel2 = '%d.%s' % (int(row)-1,col)
    newSel = sel1,sel2
    c.updateBodyPane(head,lines,tail,undoType,newSel,oldYview)</t>
<t tx="ekr.20050821081021"># Move selected text of the body down one line.

@others

moveLinesDown(c,p)</t>
<t tx="ekr.20050821081021.1">def moveLinesDown(c,p):
    
    undoType = 'Move Lines Down'
    head,lines,tail,oldSel,oldYview = c.getBodyLines()
    if not tail or not lines: return
    tail = g.splitLines(tail)[1:]
    lines = '\n'.join(lines) + '\n'
    lines = g.splitLines(lines)
    # Move the lines down.
    lines.insert(0,tail[0])
    tail = tail[1:]
    if not tail: lines.insert(1,'\n')
    # Convert back to strings.
    tail = ''.join(tail)
    lines = ''.join(lines)
    # Adjust selection.
    sel1,sel2 = oldSel
    row,col = sel1.split('.') ; sel1 = '%d.%s' % (int(row)+1,col)
    row,col = sel2.split('.') ; sel2 = '%d.%s' % (int(row)+1,col)
    newSel = sel1,sel2
    c.updateBodyPane(head,lines,tail,undoType,newSel,oldYview)</t>
<t tx="ekr.20050930124917">result = []
firstLevel = p.level()

for p in p.self_and_subtree_iter():
    head = p.moreHead(firstLevel)
    head = g.toEncodedString(head,'ascii',reportErrors=True)
    result.append(head)
    body = p.moreBody() # Inserts escapes for '+' and '-' characters.
    if body:
        body = g.toEncodedString(body,'ascii',reportErrors=True)
        result.append(body)

result = '\n'.join(result) + '\n'
# print result
w = c.frame.body.bodyCtrl
w.clipboard_clear()
w.clipboard_append(result)</t>
<t tx="ekr.20051020124457"></t>
<t tx="ekr.20051023104813"># This works, but is too slow to be really useful.

count = 0 ; tnodes = []
for p in c.all_positions_iter():
    if p.isDirty() and p.v.t not in tnodes:
        c.checkPythonNode (p,suppressErrors=False)
        tnodes.append(p.v.t)
        count += 1
        
g.es('%s nodes checked' % count)</t>
<t tx="ekr.20051025070722">c.prettyPrintPythonNode()</t>
<t tx="ekr.20051025091355">c.spellCommands.openSpellTab()
</t>
<t tx="ekr.20051110111150"># We use this file to make it easier to use cvs.

@all</t>
<t tx="ekr.20061008055616"></t>
<t tx="ekr.20070427110751"></t>
<t tx="ekr.20070615131954"></t>
</tnodes>
</leo_file>
