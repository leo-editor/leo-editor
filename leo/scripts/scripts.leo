<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo (http://webpages.charter.net/edreamleo/front.html) -->
<?xml-stylesheet ekr_test?>
<leo_file xmlns:leo="http://www.leo-editor.org/2011/leo" >
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20070615131954"><vh>Startup</vh>
<v t="ekr.20070427110751"><vh>@chapters</vh></v>
<v t="ekr.20111017085134.16069"><vh>Disabled buttons</vh>
<v t="ekr.20111017085134.16070"><vh>@@button jython</vh></v>
<v t="ekr.20111017085134.16071"><vh>@@button pydoc</vh></v>
<v t="ekr.20111017085134.16072"><vh>@@button check-dirty</vh></v>
<v t="ekr.20111017085134.16073"><vh>@@button Ipython</vh></v>
<v t="ekr.20111017085134.16074"><vh>@@button Lines Down</vh>
<v t="ekr.20111017085134.16075"><vh>moveLinesDown</vh></v>
</v>
<v t="ekr.20111017085134.16076"><vh>@@button Lines Up</vh>
<v t="ekr.20111017085134.16077"><vh>moveLinesUp</vh></v>
</v>
<v t="ekr.20111017085134.16078"><vh>@@button lispCall @key=alt+6</vh>
<v t="ekr.20111017085134.16079"><vh>ctor</vh></v>
<v t="ekr.20111017085134.16080"><vh>run &amp; helpers</vh>
<v t="ekr.20111017085134.16081"><vh>findCalls</vh></v>
<v t="ekr.20111017085134.16082"><vh>findDefs</vh></v>
<v t="ekr.20111017085134.16083"><vh>stripComments</vh></v>
<v t="ekr.20111017085134.16084"><vh>stripLispIds</vh></v>
<v t="ekr.20111017085134.16085"><vh>stripStrings</vh></v>
</v>
<v t="ekr.20111017085134.16086"><vh>class token</vh></v>
<v t="ekr.20111017085134.16087"><vh>choose</vh></v>
<v t="ekr.20111017085134.16088"><vh>dumpList</vh></v>
<v t="ekr.20111017085134.16089"><vh>Parsing...</vh>
<v t="ekr.20111017085134.16090"><vh>parse</vh></v>
<v t="ekr.20111017085134.16091"><vh>scan &amp; helpers</vh>
<v t="ekr.20111017085134.16092"><vh>skipComment</vh></v>
<v t="ekr.20111017085134.16093"><vh>skipId</vh></v>
<v t="ekr.20111017085134.16094"><vh>skipString</vh></v>
</v>
<v t="ekr.20111017085134.16095"><vh>scanForest</vh></v>
</v>
<v t="ekr.20111017085134.16096"><vh>Code generators...</vh>
<v t="ekr.20111017085134.16097"><vh>gen</vh></v>
<v t="ekr.20111017085134.16098"><vh>gen_token</vh></v>
<v t="ekr.20111017085134.16099"><vh>gen_block &amp; helper</vh>
<v t="ekr.20111017085134.16100"><vh>gen_block_id</vh></v>
</v>
<v t="ekr.20111017085134.16101"><vh>gen_call &amp; helper</vh>
<v t="ekr.20111017085134.16102"><vh>gen_arg</vh></v>
</v>
<v t="ekr.20111017085134.16103"><vh>gen_def</vh></v>
<v t="ekr.20111017085134.16104"><vh>gen_if &amp; helpers</vh>
<v t="ekr.20111017085134.16105"><vh>gen_then</vh></v>
</v>
<v t="ekr.20111017085134.16106"><vh>gen_expr</vh></v>
<v t="ekr.20111017085134.16107"><vh>gen_let &amp; helper</vh>
<v t="ekr.20111017085134.16108"><vh>gen_let_bindings</vh></v>
</v>
<v t="ekr.20111017085134.16109"><vh>put...</vh>
<v t="ekr.20111017085134.16110"><vh>put </vh></v>
<v t="ekr.20111017085134.16111"><vh>put_token</vh></v>
<v t="ekr.20111017085134.16112"><vh>put_code &amp; put_code_line</vh></v>
<v t="ekr.20111017085134.16113"><vh>put_code_token</vh></v>
</v>
</v>
</v>
<v t="ekr.20111017085134.16114"><vh>@@button outlineToClipboard</vh></v>
</v>
</v>
<v t="ekr.20061008055616"><vh>Scripts</vh>
<v t="ekr.20051110111150"
expanded="ekr.20120328102352.6938,ekr.20051104082605,"><vh>@thin leoScripts.txt</vh></v>
<v t="ekr.20110914030246.2405"
expanded="ekr.20110914030403.2417,"><vh>@file gen_blender_docs.py</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20061008055616"></t>
<t tx="ekr.20070427110751"></t>
<t tx="ekr.20070615131954"></t>
<t tx="ekr.20111017085134.16069"></t>
<t tx="ekr.20111017085134.16070"># **** Change these as needed ***
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
    s = "no script in %s" % p.h
    g.es(s) ; print s
else:
    f = file(tempFileName,'w')
    f.write(script + '\n')
    f.close()
    print command
    os.system(command)
</t>
<t tx="ekr.20111017085134.16071">import os, sys, threading

python = sys.executable
pythonDir,junk = g.os_path_split(python)
pydoc = g.os_path_join(pythonDir,'Lib','pydoc.py')
command = '%s %s -g' % (python,pydoc)

# Execute the command in a separate thread.
def go():
    os.system(command)
    
threading.Thread(target=go).start()</t>
<t tx="ekr.20111017085134.16072"># This works, but is too slow to be really useful.

count = 0
for p in c.all_unique_positions():
    if p.isDirty():
        c.checkPythonNode (p,suppressErrors=False)
        count += 1
        
g.es('%s nodes checked' % count)</t>
<t tx="ekr.20111017085134.16073">from IPython.Shell import IPShellEmbed

ipshell = IPShellEmbed()
ipshell()</t>
<t tx="ekr.20111017085134.16074"># Move selected text of the body down one line.

@others

moveLinesDown(c,p)</t>
<t tx="ekr.20111017085134.16075">def moveLinesDown(c,p):
    
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
<t tx="ekr.20111017085134.16076"># Move selected text of the body up one line.

@others

moveLinesUp(c,p)</t>
<t tx="ekr.20111017085134.16077">def moveLinesUp(c,p):
    
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
<t tx="ekr.20111017085134.16078">'''Analyze external calls in lisp files.'''

import glob
class lispAnalyzer:
    @others

base = '/media/disk/XEmacs/XEmacs-21.4.13/lisp/*.el'
paths = glob.glob(base)
# g.es(g.listToString(paths))
paths = [paths[0]]

x = lispAnalyzer(c,paths)
x.run()</t>
<t tx="ekr.20111017085134.16079">def __init__ (self,c,paths):

    self.c = c
    self.paths = paths

    # Debugging.
    self.debug = True
    self.trace = False

    # Semantic info.
    self.def_keywords = ('defun','defvar',)
    self.indent_keywords = ('if','prog','prog1','progn','set',)
    self.expr_keywords = ('and','not','or',)

    self.indent = 0 # Indentation of production output.

    # Dispatch dictionary.
    self.dispatchDict = {}</t>
<t tx="ekr.20111017085134.16080">def run(self):

    fn = self.paths[0]
    f = open(fn)
    s = f.read()
    g.es_print(fn)
    # g.trace(s)
    s = self.stripStrings(s)
    s = self.stripComments(s)
    defs = self.findDefs(s)
    calls = self.findCalls(s,defs)
    calls = self.stripLispIds(calls)
    defs.sort()
    calls.sort()
    g.trace('defs...\n',g.listToString(defs))
    g.trace('calls...\n',g.listToString(calls))
</t>
<t tx="ekr.20111017085134.16081">def findCalls (self,s,defs):

    calls = []
    i = 0
    while i &lt; len(s):
        progress = i
        ch = s[i]
        if ch.isalnum() or ch == u'_':
            j = self.skipId(s,i)
            theId = s[i:j].strip()
            if theId not in defs and theId not in calls:
                calls.append(theId)
            i = j
        else: i += 1
        assert progress &lt; i

    return calls       
</t>
<t tx="ekr.20111017085134.16082">def findDefs (self,s):

    defs = [] ; tag = '(defun'
    i = 0
    while True:
        progress = i
        j = s.find(tag,i)
        if j == -1:
            return defs
        i = j + len(tag)
        j = g.skip_ws(s,i)
        if j &gt; i:
            k = self.skipId(s,j)
            if k &gt; j:
                defs.append(s[j:k])
            i = k
        assert progress &lt; i 
</t>
<t tx="ekr.20111017085134.16083">def stripComments(self,s):

    result = []
    i = 0
    while i &lt; len(s):
        progress = i
        ch = s[i]
        if ch == ';':
            i = self.skipComment(s,i)
        else:
            result.append(ch)
            i += 1
        assert progress &lt; i

    return ''.join(result)
</t>
<t tx="ekr.20111017085134.16084">def stripLispIds (self,aList):

    lispIds = [
        't','f',
        'apply',
        'boundp',
        'car','cons','cdr','consp',
        'eq','equal','eval',
        'lamda','lambda',
        'macro',
        'nil','not','null','numberp',
        'or',
        'unless',
        'vector','vectorp',
        # special forms
        'and',
        'catch',
        'cond',
        'condition-case',
        'defconst',
        'defmacro',
        'defun',
        'defvar',
        'function',
        'if',
        'interactive',
        'let',
        'let*',
        'or',
        'prog1',
        'prog2',
        'progn',
        'quote',
        'save-current-buffer',
        'save-excursion',
        'save-restriction',
        'save-window-excursion',
        'setq',
        'setq-default',
        'track-mouse',
        'unwind-protect',
        'while',
        'with-output-to-temp-buffer',
    ]

    return [z for z in aList if z not in lispIds]</t>
<t tx="ekr.20111017085134.16085">def stripStrings(self,s):

    result = []
    i = 0
    while i &lt; len(s):
        progress = i
        ch = s[i]
        if ch == '"':
            i = self.skipString(s,i)
        elif ch == "'":
            i = self.skipId(s,i+1)
        else:
            result.append(ch)
            i += 1
        assert progress &lt; i

    return ''.join(result)
</t>
<t tx="ekr.20111017085134.16086">class token:

    '''Representing one elisp syntactic entity,
    with a list of preceding comments.'''

    def __init__ (self,comments,kind,val):
        self.comments = comments[:]
        self.kind = kind
        self.val = val
            # For blocks, a list of tokens.
            # For all other tokens, the spelling of the token.

    def __repr__ (self):
        return '&lt;token kind: %s, val: %s&gt;' % (self.kind,self.val)

    def __str__ (self):
        if self.kind == 'block:':
            return 'block: [snip]'
        elif self.kind == 'string:':
            return '%s%s' % (self.kind,self.val[:20])
        else:
            return '%s%s' % (self.kind,self.val)
</t>
<t tx="ekr.20111017085134.16087">def choose(self,cond,a,b): # warning: evaluates all arguments

    if cond: return a
    else: return b
</t>
<t tx="ekr.20111017085134.16088">def dumpList(self,aList):

    if type(aList) == type([]):
        result = self.dumpListHelper(aList,indent=0)
        return '\n'.join(result)
    else:
        return repr(aList)

def dumpListHelper(self,aList,indent):

    result = []
    leading = ' ' * (4 * indent)

    for z in aList:
        if z is None:
            result.append('%s%s' % (leading,'None'))
        elif z == []:
            result.append('%s%s' % (leading,'[]'))
        elif type(z) == type([]):
            result.append('%s%s' % (leading,'['))
            result.extend(self.dumpListHelper(z,indent+1))
            result.append('%s%s' % (leading,']'))
        elif isinstance(z,self.token):
            if z.kind=='block:':
                result.append('%s%s' % (leading,'block:'))
                result.extend(self.dumpListHelper(z.val,indent+1))
                # result.append('%s%s' % (leading,'block:]'))
            else:
                result.append('%s%s' % (leading,str(z)))
        else:
            result.append('%s%s' % (leading,str(z)))

    return result

listToString = dumpList</t>
<t tx="ekr.20111017085134.16089"></t>
<t tx="ekr.20111017085134.16090">def parse(self,s):

    # Generate the nodes, including directive and section references.
    return self.scanForest(s)
</t>
<t tx="ekr.20111017085134.16091">def scan(self,s,i):

    '''Scan an elisp expression.'''

    start = i ; end = len(s) ; result = []
    comments = [] ; token = self.token
    # A hack. ignore initial @language lisp
    tag = '@language lisp'
    if i == 0 and s[i:i+len(tag)]==tag:
        i += len(tag)
    while i &lt; end:
        progress = i
        ch = s[i]
        if ch == ';':
            j = self.skipComment(s,i)
            start = i = j
        elif ch == '"':
            j = self.skipString(s,i)
            start = i = j
        elif ch.isalnum() or ch == u'_':
            j = self.skipId(s,i)
            result.append(token(comments,'id:',s[i:j]))
            start = i = j
        elif ch =='(':
            i += 1
            j,aList = self.scan(s,i)
            result.append(token(comments,'block:',aList))
            start = i = j
        elif ch == ')':
            i += 1
            return i,result
        else:
            # if ch == "'": ch = 'quote'
            # if ch not in (' ','\t','\n','\r'):
                # result.append(token(comments,'op:',ch))
            i += 1
        assert progress &lt; i,'i: %d, ch: %s' % (i,repr(s[i]))

    if start &lt; end:
        tail = s[start:end].strip()
        if tail:
            result.append(token(comments,'tail:',tail))
            comment = []
    if comments:
        result.append(token(comments,'trailing-comment:',''))

    return i,result
</t>
<t tx="ekr.20111017085134.16092">def skipComment (self,s,i):

    '''Skip a comment.'''

    while i &lt; len(s):
        if s[i] == '\n':
            break
        i += 1
    return i
</t>
<t tx="ekr.20111017085134.16093">def skipId (self,s,i):

    while i &lt; len(s):
        ch = s[i]
        if ch.isalnum() or ch in ('_','-'):
            i += 1
        else:
            break
    return i
</t>
<t tx="ekr.20111017085134.16094">def skipString(self,s,i):

    """Skip a string literal."""

    assert(s[i] == '"')
    i += 1
    while i &lt; len(s):
        ch = s[i]
        if ch == '\\' : i += 2
        elif ch == '"':
            i += 1 ; break
        else: i += 1

    return i</t>
<t tx="ekr.20111017085134.16095">def scanForest (self,s):

    i = 0 ; result = []

    while i &lt; len(s):
        progress = i
        i,aList = self.scan(s,i)
        aList and result.extend(aList)
        assert i &gt; progress

    return result


</t>
<t tx="ekr.20111017085134.16096">@ From Richard Deibenkorn:

1. Attempt what is not certain. Certainty may or may not come later. It may then
be a valuable delusion.

2. The pretty, initial position which falls short of completeness is not to be
valued--except as stimulus for further moves.

3. Do search.  But in order to find other than what is looked for.

4. Use and respond to the initial fresh qualities but consider them absolutely
expendable.
</t>
<t tx="ekr.20111017085134.16097">def gen(self,tokens,indent,init=False):

    result = []

    if init: result.append('='*40)

    for token in tokens:
        aList = self.gen_token(token,indent)
        result.extend(aList)

    if init: result.append('-'*40)

    return result

</t>
<t tx="ekr.20111017085134.16098">def gen_token(self,token,indent):

    result = []

    if self.debug:
        if token.kind == 'block:':
            aList = self.gen_block(token,indent)
            result.extend(aList)
        else:
            self.put_token(token,indent,result)
    else:
        if token.kind == 'block:':
            self.gen_block(token,indent)
        else:
            self.put_code_token(token)

    return result
</t>
<t tx="ekr.20111017085134.16099">def gen_block (self,token,indent):

    if not (token and token.val):
        return []

    blockList = token.val
    token2 = blockList[0]
    result = []

    if token2.kind.startswith('id'):
        aList = self.gen_block_id(token2.val,blockList,indent)
    else:
        if self.debug:
            self.put('block...',[],indent,result)
        aList = self.gen(token.val,indent+1)

    result.extend(aList)
    return result
</t>
<t tx="ekr.20111017085134.16100">def gen_block_id (self,theId,tokens,indent):

    result = []

    # Eventually there will be a lookup of the dispatch dict here.
    if theId == 'let':
        aList = self.gen_let(tokens,indent)
    elif theId == 'if':
        aList = self.gen_if(tokens,indent)
    elif theId in self.def_keywords:
        aList = self.gen_def(theId,tokens,indent)
    elif theId in self.indent_keywords:
        self.put('%s...' % (theId),[],indent,result)
        aList = self.gen(tokens[1:],indent+1)
    elif theId in self.expr_keywords:
        aList = self.gen_expr(theId,tokens[1:],indent+1)
    else:
        aList = self.gen_call(theId,tokens[1:],indent)

    result.extend(aList)
    return result
</t>
<t tx="ekr.20111017085134.16101">def gen_call (self,funcId,tokens,indent):

    result = []

    if self.debug:
        self.put('call: %s' % (funcId),[],indent,result)
        for token in tokens:
            aList = self.gen_arg(token,indent+1)
            result.extend(aList)
    else:
        self.put_code_line('%s(' % (funcId))
        for token in tokens:
            self.gen_arg(token,indent+1)
        self.put_code(')')

    return result

</t>
<t tx="ekr.20111017085134.16102">def gen_arg(self,token,indent):

    result = []

    if self.debug:
        if token.kind == 'block:':
            self.put('arg block:...',[],indent,result)
            aList = self.gen_block(token,indent)
            result.extend(aList)
        else:
            self.put_token(token,indent,result)
    else:
        if token.kind == 'block:':
            aList = self.gen_block(token,indent)
            self.put_code(''.join(aList))
        else:
            self.put_code_token(token)

    return result
</t>
<t tx="ekr.20111017085134.16103">def gen_def(self,theId,tokens,indent):

    result = []

    if not tokens or len(tokens) &lt; 3:
        result.append('*** bad def tokens')
        return result

    defToken,idToken = tokens[0:2]
    if idToken.kind != 'id:':
        result.append('*** bad def id')
        return result

    if self.debug:
        self.put(theId,idToken.val,indent,result)
        aList = self.gen(tokens[2:],indent+1)
        result.extend(aList)
    else:
        self.put_code('def %s (' % idToken.val)
        self.gen_token(tokens[2],indent)
        self.put_code('): # end def\n')
        self.indent += 1
        self.gen(tokens[3:],indent+1)
        self.indent -= 1

    return result
</t>
<t tx="ekr.20111017085134.16104">@ if condition then-form else-forms.

If the evaluated condition is non-nil, then-form is evaluated and the result
returned. Otherwise, the else-forms are evaluated in textual order, and the
value of the last one is returned. If condition has the value nil, and no
else-forms are given, if returns nil.
@c

def gen_if (self,tokens,indent):

    # tokens[0]: id:if
    # tokens[1] cond

    for i in xrange(len(tokens)):
        g.trace('tokens[%d]: %s' % (i,self.dumpList(tokens[i])))

    # g.trace(self.dumpList(tokens))

    result = []

    if self.debug:
        self.put('if...',[],indent,result)
        aList = self.gen(tokens[1:],indent+1)
        result.extend(aList)
    else:
        self.put_code('if ')
        self.gen(tokens[1:],indent+1)
        self.put_code(': # end if\n')

    return result
</t>
<t tx="ekr.20111017085134.16105">def gen_then (self,token):

    pass
</t>
<t tx="ekr.20111017085134.16106">def gen_expr (self,theId,aList,indent):

    binops = ('and','or',)
    result = []

    self.put(theId,[],indent,result)
    aList = self.gen(aList,indent+1)

    result.extend(aList)
    return result
</t>
<t tx="ekr.20111017085134.16107">@
(let ((variable value)
      (variable value)
      ...)
  body...)
@c

def gen_let (self,tokens,indent):

    if not tokens: return []
    if len(tokens) != 3:
        g.trace('unusual let')
        result = self.gen(tokens,indent+1)
        return result

    if 0:
        for i in xrange(len(tokens)):
            g.trace('token',i,tokens[i])

    letToken,bindingToken,bodyToken = tokens
    result = []
    self.put('let...',[],indent,result)
    self.put('let-bindings...',[],indent+1,result)
    aList = self.gen_let_bindings(bindingToken,indent+2)
    result.extend(aList)
    self.put('let-block...',[],indent+1,result)
    aList = self.gen_block(bodyToken,indent+2)
    result.extend(aList)
    return result</t>
<t tx="ekr.20111017085134.16108">def gen_let_bindings (self,token,indent):

    result = []

    if token.kind != 'block:':
        g.trace('unexpected let')
        return result

    for z in token.val:
        if z.kind == 'block:': # one (id,val) pair
            if z.val and len(z.val) == 2:
                token1 = z.val[0]
                token2 = z.val[1]
                self.put('let-id',token1,indent,result)
                self.put('let-val...',[],indent,result)
                if token2.kind == 'block:':
                    aList = self.gen_block(token2,indent+1)
                    result.extend(aList)
                else:
                    #g.trace('no let list')
                    self.put_token(token2,indent+1,result)
            else:
                g.trace('unexpected let 2')

    return result
</t>
<t tx="ekr.20111017085134.16109"></t>
<t tx="ekr.20111017085134.16110">def put (self,kind,val,indent,result):

    '''Append one or more lines of output to result.'''

    leading = '%2d: %s' % (indent,' ' * indent)

    if kind == 'string:':
        val = self.choose(len(val)&gt;20,val[:20]+'..."',val)

    if val:
        s = '%s%s %s' % (leading,str(kind),str(val))
    else:
        s = '%s%s' % (leading,str(kind))

    result.append(s)
</t>
<t tx="ekr.20111017085134.16111">def put_token (self,token,indent,result):

    for z in token.comments:
        self.put('comment:',z,indent,result)

    self.put(token.kind,token.val,indent,result)
</t>
<t tx="ekr.20111017085134.16112">def put_code_line (self,s):

    s2 = '%s%s' % (' '*self.indent,s)
    print s2,

def put_code (self,s):

    print s,
</t>
<t tx="ekr.20111017085134.16113">def put_code_token (self,token):

    if token.kind == 'block:':
        self.put_code('&lt;block&gt;')
    else:
        self.put_code(token.val)

</t>
<t tx="ekr.20111017085134.16114">result = []
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
</tnodes>
</leo_file>
