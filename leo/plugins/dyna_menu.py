#@+leo-ver=4-thin
#@+node:ekr.20050421093045.2:@thin dyna_menu.py
#be sure and add dyna_menu.py to pluginsManager.txt
#you don't need to enable dynacommon.py in pluginsManager.txt
#you do need dynacommon.py in the plugins directory 
#

from __future__ import generators  # + enumerate for less than py2.3

#@<< doc >>
#@+node:ekr.20050421093045.3:<< doc >>
"""this plugin creates a dyna menu of macro items.
 Alt+y the dyna menu accelerator key.   
 every time you save the leo one of the macros prints a timestamp.
 macros perform any actions you could have with execute script,
 with the added bonus, they work on the selected text or body text.
 they work as well from the dynatester node or dynabutton, insuring
 when they are included in the plugin, minimal time is lost debugging.
see dyna_menu.ini for options you can set, even while Leo is running.
and edit the paths in dynacommon.py to suit your system.
as time goes by, this part will become smarter and require less editing.

 add exS may re-install exS button on the toolbar.
 set doc and hit DQ3 with nothing selected to see docstring of all macros.
 toggle print/paste/doc on the menu. 
 you click on print, paste or doc to enable that action.
 the action refers to the output of the macro in most cases.
 open another leo resets back to print 
 because all dyna share an instance.

 most output actions are to the log,
 or using print redirected to log if you set that in config.
 'print' gets redirected to console if the macro is in the plugin.
 you have to change the macro accordingly from print x to g.es(x) 
 
some macros do need some non standard modules,
will fallback to standard modules if possible.
some are available from python cvs 
or from later python versions.
the only way to know is to try them or read the code.

do post a bug report or feature request
on my comment page from:
 http://rclick.netfirms.com/rCpython.htm
or sourceforge forum:
<http://sourceforge.net/forum/forum.php?thread_id=1255533&forum_id=10226>

expect constant maintance and additions

"""
#@nonl
#@-node:ekr.20050421093045.3:<< doc >>
#@nl
__version__ = '0.0139i' #u05417a10:51
__plugin_requires__ = ["dynacommon"]
__plugin_files__ = ["dyna_menu.ini", "dynacommon.py", "dyna.txt"]
#__plugin_group__ = "ex"
 
#__plugin_optional__ = 'pyparsing csv pydot graphviz textwrap silviecity source-highlight docutils pylint pychecker pyrex mingw astyle elementtree'.split()

#@<< initilize >>
#@+node:ekr.20050421093045.4:<< initilize >>
#@+at
# from future has to be first...
# but to check py version you have to import sys
# isn't that some kind of catch 22?
#@-at
#@@c
import sys

import leoGlobals as g
Tk   = g.importExtension('Tkinter',pluginName=__name__,verbose=True)

#at this point in Leo, code from plugins isn't importable. later it is.
#replace w/importfromfile
#or patch leo to add plugindir sooner rather than later...

k = g.os_path_split(g.app.loadDir)[0]
#this should fix the slashes and lower cases' it on win9x
k = g.os_path_normpath(g.os_path_abspath(g.os_path_join(k, "plugins")))

#path being unicode can affect less than py2.3
if sys.version_info[:2] < (2, 3):
    k = str(k)

#might not be found in sys path on win9x, there is no unicode paths
if k not in sys.path:
    sys.path.append(k)
del k

#should this even be imported if batch mode or no Tk?
try: 
    #import dynacommon as dynacom
    from dynacommon import *
    dynacom = True
except ImportError: 
    dynacom = None
    #no gui maybe print better here? should guard the error too?
    g.es('you have to copy dynacommon.py to plugins')

"""
 to disable the timestamp thing, comment out this line below:
   ...registerHandler("save1", timestamp) 

for refrence, dynabutton and exS were other plugins from the URL below.

with the dyna plugin loaded you can do things in your scripts like:
    
import sys
#theres probably an easier way than this.
sys.modules['dyna_menu'].dynaM_Clip_dtef(0, 'p')

#another way
import dyna_menu
#print help(dyna_menu)
#print dir(dyna_menu)  #dynaM_
print dyna_menu.dynaHexdump('testing 123')


lightly tested with py2.2 or Leo4.3a3,4+ from cvs
tested Python 2.3, 2.4.1 win9x

should not be a problem anywhere else.
but don't quote me on that. make a bug report.

"""
#@nonl
#@-node:ekr.20050421093045.4:<< initilize >>
#@nl
#@<< version history >>
#@+node:ekr.20050421093045.5:<< version history >>
#@+at
# 0.0138 few changes since forum post
# 
# 0.0139 e
#   - updates re Leo4.3 normpath and c for a few dialogs
#   - some config options for htmlize and du_test
#   - htmlize
#    - code folding: still in process
#    - improvements suggested by EKR & Bill P. not fully implimented
#       change fonts to css as an option  no
#       add a plain or RST output option  no
#       hey I could use that myself quite  bit!
#       did add option to stripnodesents, and stripdirectives & stripcomments 
# now works
#  - use subprocess if available when calling external pychecker & pylint
#  - made justPychecker an option not to print source after checking
#   - if you dont want to run pylint you have to edit the source.
#   - pylint is more configurable and doesn't fail on import errors now
#   - highly recomended. see dyna.txt for rc file and URLs'
#   - added a few more flippers from the plugin_menu
#     - for Leodebug, justPychecker and verbosity for @test and doctest
#   - added back a macro uses dynaplay to comment out a python selected text
#     many people asked for this, should get comment for whatever language is 
# active.
#     Leo can do this natively now but dyna can also put arbitrary text if you 
# like.
#   - cmd_flip_onoff_c_gotoline
#   - htmlze
#     -   switch on plain or rst, force @others and send to for docutils
#        and there if there are subnodes of @language preprocess them
#        somehow and this gets recursive and complicated...
#     -  option on hilighter or silvercity for the remaining languages
#   + fix evaluator to select between Leo perttyprint, evaluator and astyle?
#   + just add call to astyle for now for c & java output to htmlize or log
# 
#   work code in runcmd for commands that accept stdin
#   for source-highlight and astyle means no tempfile.
# 
# -a,b,d leapahead to fix htmlize for plain and @rst as simple as possible
# e special bug fix release
# f this version history skips around a little from b and beyond.
#  did some cleanup in various fixbody calls, consolidated selectbody
#  not calls getScript and optionally stripSentinals
#  or comment them if in selected text as for disa.
#  playback broke somehow
# g - make htmlize callable for display of report from pylint
#   - after astyle now too so can see output syntax highlighted.
# h - subprocess.startupinfo from cookbook solves no dos window flash!
#   - still renames the console if its open on windows.
#   - renamed unittest testcase to g.tester instead of g.app._t
#   - added actions lower, upper etc reworked DQ3 and slashes too
#   began help to eventually parse python w/o import as pydoc does
#   pydoc fallback if not epydoc or docutils sandbox available
# i - began parser and reverser which isn't going terribly well.
# j - fixup pydent so it works in other @language and change the name
# 
# 
#  adding more tests, still a few that fail in DQ3 and htmlize
#  testing slightly different in py2.2 and 2.4 as well
# 
# still todo
# remove more bare Exception.
# bribe someone to test it on mac and nix and give some feedback.
# 
#@-at
#@-node:ekr.20050421093045.5:<< version history >>
#@nl
dynaMvar = None
menudefault =-4  #help4, linenumber5
#@+others
#@+node:ekr.20050421093045.6:macros
#@+at
# 
# in theses macro nodes, copy or clone the macros
# you want to appear in dynamenu
# 
# dynaM_ or dynaS_ for macro and system macro
# arbitrary to segment into cascading menus at build time
# see load_menu, dont use beyond Z as a macroname dynaZ_whatever
# change the letter to change the order the macros are created
# change the name of the macro to change the alphabetical order.
# 
# not alot of error checking is done
# each macro must have the same name prefix, dyna*_
# and either take *a or c as argument
# dynaM_DQ3(c)  they appear in the menu in sorted order
# 
# 
# for other less used macros,
# use the dynabutton or the scriptButton
# 
# some of these are calling function further in the file
# that only works becase all parsing is done before calling
# 
# 
# need new macro indexer of selected text or body
# simple words contained and count place found
# 
# need to catagorize them all for print/paste
# and also which are to Log always and only
# or print and if redirect enabled will be to log
# and what about a file toggle would output to file? or to clipboard
# so can tag them in the in the menu as using print/paste.
# 
# many don't care which,
# two are destructive no undo and there is a popup first.
# 
# some are action orientated.
#@-at
#@nonl
#@+node:ekr.20050421093045.7:info macros
#@+node:ekr.20050421093045.8: Clip_dtef
def dynaB_Clip_dtef(c, ret= 'cp'):
    """(c, ret= 'cp') clip, print, return
    ret='cpr' decide if to add to clipboard, print or return 
    time text 
    
    """
    try:
        if g.app.dynaMvar.bugimport: raise ImportError
        #custom datetime format
        import binaryfun as bf
        dt = bf.dtef()
    except ImportError:
        if c:
            #what Leo has for time in body
            dt = c.getTime(body=True)
        else:
            import time
            Leoconfigformat = '%m/%d/%Y %H:%M.%S'
            dt = time.strftime(Leoconfigformat) 

    if 'p' in ret: g.es('%s%s '%(EOLN, dt,) )
    if 'c' in ret: g.app.gui.replaceClipboardWith(dt)
    #ret = r necessary, if dont specify it clips & prints by default
    if 'r' in ret: return dt  
#@-node:ekr.20050421093045.8: Clip_dtef
#@+node:ekr.20050421093045.9:HELP!
def dynaB_help(c):
    """(c)
    call epydoc or pydoc on selected text display in webbrowser.
    pydoc simple output doesn't have links to additional levels.

    pydoc code posted awhile ago on Leo forums
    trees plugin has something similar which creates subnodes
    of the help but that is not too easy to navigate.
    please suggest options for @language other than python.
  ~EOT
    this mirrors the dev rClick action of the same name
    eventually will be one code for both or neither. maybe clone them?
    need to get a master redirect to avoid this code duplication

    doesn't trigger PMW popup like in rClick 
    pydoc can takes quite awhile to produce output
    eventually replace w/twisted happydoc or docutils sandbox code for python
    and maybe call doxegen or something else for other @language
    possibly a local indexer? and/or an 'I feel lucky' from google or yahoo
    """
    newSel = dynaput(c, [])
    if not newSel: return

    try:
        #works ok w/o this as well. but likely help is in ascii
        newSel = g.toEncodedString(newSel, "ascii", reportErrors= True)
    except Exception:
        pass

    #might make sense to distinguish simple from help on a module

    try:
        #import happydoclib  #Assignment to None error in py2.4
        import epydoc
        happydoc = True
    except ImportError:
        happydoc = None

    #double layer of redirection seems necessary
    g.redirectStdout(); g.redirectStderr()
    #@    << stdredirect n>>
    #@+node:ekr.20050421093045.10:<< stdredirect n >>
    sys.stdout = g.fileLikeObject() #'cato'
    sys.stderr = g.fileLikeObject() #'cate'
    
    #usually you dont want to do this,
    _sosav = sys.__stdout__
    sys.__stdout__ = sys.stdout
    _sesav = sys.__stderr__
    sys.__stderr__ = sys.stderr
    #@-node:ekr.20050421093045.10:<< stdredirect n >>
    #@nl
    #@    << happydoc >>
    #@+node:ekr.20050421093045.11:<< happydoc >>
    #actually epydoc which imports, docutils will work soon?
    #and it might require its own css?
    #another hopelessly unscriptable app
    
    if happydoc: 
        from epydoc.html import HTMLFormatter
        from epydoc.objdoc import DocMap, report_param_mismatches
        from epydoc.imports import import_module, find_modules
        from epydoc.objdoc import set_default_docformat
    
        err = None
        try: import_module(newSel)
        except ImportError, err:
            happydoc = None
    
        if not err: 
            options = {}
            g.es('using epydoc')
            set_default_docformat( 'plaintext')
            htmldoc = HTMLFormatter(d, **options)
            print htmldoc
    #@nonl
    #@-node:ekr.20050421093045.11:<< happydoc >>
    #@nl
            
    if happydoc is None:  #or module not found
        import pydoc
        #there may be better ways to call this to get other than text
        #which would have links to sub modules
        #BTW, this prints anyway somehow if not redirected well
        H = pydoc.Helper(input= None, output= sys.stdout )
        H.help(str(newSel))

    #@    << stdredirect f>>
    #@+node:ekr.20050421093045.12:<< stdredirect f >>
    oo = sys.stdout.get()  #read get()
    oe = sys.stderr.get()  #get()
    sys.stdout.close()
    sys.stderr.close()
    
    #if you didnt do this it wouldent need to be reversed
    sys.__stdout__ = _sosav
    sys.__stderr__ = _sesav
    
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    
    #@-node:ekr.20050421093045.12:<< stdredirect f >>
    #@nl
    #redirect is now screwed untill return
    g.restoreStdout(); g.restoreStderr()

    if oo.strip()[:9] == 'no Python' or oo.strip()[:5] == 'Sorry':
        g.es(oo + oe)
    else:
        htmlize(c, (oo + oe), 'report') 
#@nonl
#@-node:ekr.20050421093045.9:HELP!
#@+node:ekr.20050421093045.13:Graphviz node
def dynaB_Graphviznode(c):
    """(c= None) create jpg popup associated viewer
    take the EKR Graphviz pydot demo
    see the 4.2+ test.leo for the origional and other info
    http://www.dkbza.org/pydot.html
    http://www.research.att.com/sw/tools/graphviz/download.html
    pydot, python setup.py install
    install the full Graphviz in a subdir somewhere on  the path
    pydot has a path walker that will find it.
    works on win.

    bring it back down to 4.1 standards and macroize it
    put in a switch for >4.1 use the origional calls
    
    works on any node now. best if there are not too many subnodes
    the graph gets too dense and small
  ~EOT  
    the other demo graph node outline builder worked 4.1.
    also have to refocus. the demo was to visualize 4.2 t\/v nodes
    I dont need to see the numbers just the headlines
    some things are compatable some not. 
    need to dev a good list of what works
    list of cvs commits would help here maybe if the docs dont keep up.
    its not going to make a whole lot of sense in less than 4.2
    untill I find out about the diferences
    makes a nice looking graph though!

 a dependancy graph of which modules a program uses might be doable.
 more nodes for pieces in the module and other filesystem dependancies.
 
 
    numberOfChildren() nthChild(n) lastChild()
    """
    import leoGlobals as g
    import os
    import string  #why?
    try:
        import pydot
    except ImportError:
        g.es('you need http://www.dkbza.org/pydot.html')
        return

    try:
        import dynacommon as dy
        #reload(dy)
        fname = dy.leotmp('pydotOut.jpg')
    except ImportError:
        fname = 'pydotOut.jpg'

    p = c.currentPosition()

    #@    << code >>
    #@+node:ekr.20050421093045.14:<< code >>
    #@+others
    #@+node:ekr.20050421093045.15:addLeoNodesToGraph
    def addLeoNodesToGraph(p, graph, top= False):
        """
        p.v attribute is 4.2, this might be a dealbreaker for 4.1?
        butchering it up just to get some output
        the node ovals are too large
        
        """
    
        # Create p's vnode.
        if Leo > 4.1:
            n = vnodeRepr(p.v)
            l = vnodeLabel(p.v)
        else:
            n = vnodeRepr(p)
            l = vnodeLabel(p)
    
        thisNode = pydot.Node(name= n, label= l)
        graph.add_node(thisNode)
    
        if p.hasChildren():
            child = p.firstChild()
            childNode = addLeoNodesToGraph(child, graph)
            graph.add_node(childNode)
    
            if Leo > 4.1:
                e1 = tnodeRepr(p.v.t)
                e2 = vnodeRepr(child.v)
            else:
                e1 = tnodeRepr(p)
                e2 = vnodeRepr(child)
    
            edge2 = pydot.Edge(e1, e2)
            graph.add_edge(edge2)
    
            
            #     child.next() could error?  hasattr(child, 'next()')?
            while child.next():  #child.hasNext() 4.2
                next = child.next()
                
                if Leo > 4.1:
                    e1 = vnodeRepr(child.v)
                    e2 = vnodeRepr(next.v)
                else:
                    e1 = vnodeRepr(child)
                    e2 = vnodeRepr(next)
    
                edge =  pydot.Edge(e1, e2, dir="both")
    
                nextNode = addLeoNodesToGraph(next, graph)
                graph.add_node(nextNode)
                graph.add_edge(edge)
                child = next
                
        if 1:
            if Leo > 4.1:
                n = tnodeRepr(p.v.t)
                l = tnodeLabel(p.v.t)
            else:
                n = tnodeRepr(p)
                l = tnodeLabel(p)
    
            tnode = pydot.Node(name= n, shape="box", label= l)
            
            if Leo > 4.1:
                e1 = vnodeRepr(p.v)
                e2 = tnodeRepr(p.v.t)
            else:
                e1 = vnodeRepr(p)
                e2 = tnodeRepr(p)
    
            edge1 = pydot.Edge(e1, e2, arrowhead= "none")
            graph.add_edge(edge1)
            graph.add_node(tnode)
        
        if 0: # Confusing.
            if not top and p.v._parent:
                edge = pydot.Edge(vnodeRepr(p.v),vnodeRepr(p.v._parent),
                    style="dotted",arrowhead="onormal")
                graph.add_edge(edge)
    
        if 0: # Marginally useful.
            for v in p.v.t.vnodeList:
                edge = pydot.Edge(tnodeRepr(p.v.t),vnodeRepr(v),
                    style="dotted",arrowhead="onormal")
                graph.add_edge(edge)
    
        return thisNode
    #@nonl
    #@-node:ekr.20050421093045.15:addLeoNodesToGraph
    #@+node:ekr.20050421093045.16:tnode/vnodeLabel
    def tnodeLabel(t):
    
        if Leo > 4.1:
            tl = len(t.vnodeList)
        else:
            tl = 0
    
        return "t %d [%d]" % (id(t), tl)
        
    def vnodeLabel(v):
        
        return "v %d %s" % (id(v),v.t.headString)
    #@-node:ekr.20050421093045.16:tnode/vnodeLabel
    #@+node:ekr.20050421093045.17:tnode/vnodeRepr
    def dotId(s):
        """Convert s to a C id"""
    
        s2 = [ch for ch in s if ch in (string.letters + string.digits + '_')]
        return string.join(s2,'')
    
    def tnodeRepr(t):
    
        return "t_%d" % id(t)
        
    def vnodeRepr(v):
        
        return "v_%d_%s" % (id(v),dotId(v.headString()))
    #@nonl
    #@-node:ekr.20050421093045.17:tnode/vnodeRepr
    #@-others
    #@nonl
    #@-node:ekr.20050421093045.14:<< code >>
    #@nl
        
    graph = pydot.Dot(simplify= True, ordering= "out")

    root = p  #g.findNodeInTree(p, "Root") #another 4.2ism or in leotest

    addLeoNodesToGraph(root, graph, top= True)
    graph.write_jpeg(fname, prog= 'dot')

    g.es('graph of outline written to \n' + fname)
    import webbrowser
    webbrowser.open(fname, new= 1)
#@nonl
#@-node:ekr.20050421093045.13:Graphviz node
#@+node:ekr.20050421093045.18:linenumber
def dynaB_linenumber(c):
    """(c)  print w/sentinals
   selected text or body as Leo sees it, 
   numbering lines or if there is an integer in copybuffer,
    show just +- a few lines around that number.
   selected text doesn't show sentinalsm but exscript uses them
   so lineenumber on selected text may not jive after an error.
   (for more rambling debugging tips see my website)
   syntax errors, indentation errors ,  missing closing paren
   missing colon ':'  in def, if, class
   the actual error can be ahead or behind of the reported error line.
   often at the top of the block continuing the error.
   it wouldn't hurt to examine the bottom and middle either.
  ~EOT   further enhancement, keep track of last section ref node
    last def last method of last class and output all the lines together
    rather than one at a time which can tie up Leo on long programs.
    should output current path and language and wrap to current wrap
    -n +n could be under/over the abs(int) in copy buffer

    could make it jump to linenumber based on env variable
    that way you wouldn't have to remake the plugin to change behavior
    several other macro also could use settable params at ex script time.
    
    """
    #nothing selected will include sentinals
    data = fixbody(c,dynaput(c, [])) 
    datalines = data.splitlines()

    pln = g.app.gui.getTextFromClipboard()
    try:
        pln = int(pln)
        g.es('using line # %d'%(pln,), color= 'turquoise4')
    except Exception, err:
        g.es('no int in copy buffer', color= 'turquoise4')
        pln = 0

    if pln > len(datalines) or pln < 0:
        #who would select zero to print the first line?
        #maybe zero should be all lines as it would be if zero
        g.es('int found is out of range', color= 'turquoise4')
        #still possible to break and maybe too many messages
        if pln > len(datalines): pln = len(datalines) - 5
        if pln < 0: pln = 5

    for i, x in enumerate(datalines):
        if pln and i < (pln - 5): continue
        if pln and i > (pln + 5): break

        #would rather not go thru this every time thru the loop
        if pln and i == pln:
            colr = 'gray'
        else: 
            colr = 'slategray'

        g.es('%- 3d '%(i,), newline= False, color= colr)

        g.es('%s'%(x,))
    g.es('There are %s lines in ? nodes size=%s'%(
            len(datalines),
             sum([len(x) for x in datalines]), 
             ), color= 'turquoise4')
#@nonl
#@-node:ekr.20050421093045.18:linenumber
#@+node:ekr.20050421093045.19:nflatten
def dynaB_nflatten(c):
    """c= None  print
    like flatten but in macro so can
    print/paste or copy to buffer eventually. now out to log.
    should limit the recursion to less than the normal limit
    isn't following the more format of +-
    chg to int, add index level, seperate out the recursive function
    so can return body size and assmble totals
    what is the meaning of the totals if index is one though?
    obviously have to get all and total in here, next refactor for that.
  ~EOT   show if there are subnodes even if dont enumerate.
    dynacolors being a global when run from dyna_menu makes this
    problematic when run from scriptButton now while debugging...
    going to have to exS with dynacommon namespace or something
    or import common if any macr needs them. more complications.
    should just extend g and be done with it

    uses dynacommon deangle, commafy 
    an ini setting could select just @nodes or just @file
    another could leave off the node counts and totals
    
    silly to create a newline connected string of rendered ints
    then splitlines and int on the split string! 
    better just return list of tupple?
    will make no sense to anyone except if they've seen previous version
    but is a major simplification, 
    why it happened in the first place, is surely a mystry.
    there may be a marginal tradeoff of computation for size of list
    and in a recursive function this might matter, we'll see how it goes.
    next will have to resolve why the total of all nodes != filesize
    not even counting @thin etc
    """    
    import leoGlobals as g

    tbytes = 0
    oline = _nflatten(c, index= 1, sx= [])
    g.es("headString, +nodes, bytes")
    for st in oline:
        try:
            i, hs, sz, nz = st
            g.es("%s%s, +%d, %s"%(
                (' '*i), hs, nz, 
                      g.choose(sz<1024,
                       '%s'%sz, '%sk'% commafy(sz, '.')) ),
                     color= dycolors.gFuchsia)
            tbytes += sz
        except Exception:
            g.es(" ", s, dynaerrline(), color= dycolors.gError)  #

    if len(oline) > 1:
        g.es(" =%s"%(
            g.choose(tbytes<1024,'%s'%tbytes, '%sk'% commafy(tbytes, '.')),
            ), color= dycolors.gFuchsia)
        

def _nflatten(c, current= None, indent= 0, index= 0, sx= None):
    """may be trying to combine too many things
     efficency out the window to boot.
    """
    if current is None:
        current = c.currentPosition()
        t = (indent, deangle(current.headString()[:50]),
            len(current.bodyString()), len(list(current.children_iter())) )
        #g.es(t, color="purple")
        sx.append(t)
        indent += 2

    for p in current.children_iter():
        t = ( indent, deangle(p.headString()[:50]),
            len(p.bodyString()), len(list(p.children_iter()))  )
        #g.es(t)
        sx.append(t)
        if p.hasChildren() and index >0:
            _nflatten(c, p, indent +2, index -1, sx)
            continue

    return sx
#@nonl
#@-node:ekr.20050421093045.19:nflatten
#@+node:ekr.20050421093045.20:fileinfo
#@+others
#@+node:ekr.20050421093045.21:print perms
def perms(name):
    """
    a=\xc3 Padraig Brady - http://www.pixelbeat.org
     -rw-rw-rw- leo\src\..\config\leoConfig.txt
    """
    import sys
    import stat
    import os
     
    mode = stat.S_IMODE(os.lstat(name )[stat.ST_MODE ])
    #print mode
    perms = "-"
    for who in "USR", "GRP", "OTH":
        for what in "R", "W", "X":
            if mode & getattr(stat, "S_I" + what + who ):
                perms = perms + what.lower()
            else:
                perms = perms + "-"
    return perms
 
#@-node:ekr.20050421093045.21:print perms
#@-others
def dynaB_fileinfo(c, fname= None):
    """(c= None, fname= None)  print
     show some basic file info size, create date etc.
    try to get filename from selected text then copybuffer,
    if none of these are valid filenames using os.isfile,
    then will try to get current @file @rst path & name,
    then finally c.mFileName of current leo.
    if more than one of these is True, 
    then its up to you to move out of that node, select or whatever.
    feel free to impliment the more stodgy browse to file name first idiom.
  ~EOT  py22 fixed
    AttributeError: 'module' object has no attribute 'getctime'
    
    might popup a dlg to set attributes in v9
    should get user name also
    winUserName = win32api.GetUserName()
    macUserName = ?
    nuxUserName = expand('~')?

    add mode to walk from root and list all the @thin filenames
    and sublist any @file @nosent contained
    then all other @file for backup if you aren't careful with @thin
    you might just backup the leo's and forget the derived files    
    """
    import leoGlobals as g
    import os, time

    drif = 0 #do report intermediate failures 

    def normit(fn): 
        #seems redundant till you get a weird join it fixes
        return fn  #g.os_path_norm()

    if fname is None:
        fname = c.frame.body.getSelectedText()
        if not g.os_path_isfile(normit(fname)):
            if drif and fname: g.es("- ", fname[:53])
            fname = g.app.gui.getTextFromClipboard()

        #chg 1 to 0 or will never try for @file
        if 0 and not g.os_path_isfile(normit(fname)):
            if drif and fname: g.es("- ", fname[:53])
            fname = 'python.txt' #testing default

    if not g.os_path_isfile(normit(fname)):
        if drif and fname: g.es("- ", fname[:53])
        fname = 'the current @file'
        p = c.currentPosition()
        #leocommands has goto should be using an API call to get filename.
        #coping some of the relevent code, its a jungle in there...
        #seems ok on @nosent, goto should be fixed since it skips them

        fileName = None
        for p in p.self_and_parents_iter():
            fileName = p.anyAtFileNodeName()
            if fileName: 
                break
            if p.headString()[:4] == '@rst':
                #this can fail if not the first @rst
                fileName = p.headString()[4:]
                #c:\c\leo\V42leos\ /c/leo/HTML/Colortest.html via join
                break

        if not fileName:
            if drif: g.es("ancestor not @file node")
        else:
            root = p.copy()
            d = g.scanDirectives(c)
            path = d.get("path")
            #need the directive length, thin, file-thin etc [1:] 

            fname = root.headString()
            fname = fname[fname.find(' ')+1:]
            fname = g.os_path_join(path, normit(fname))
            if not g.os_path_isfile(normit(fname)):
                #will double the msg if drif, 
                #but you might want to know
                g.es("not exists", fname[:53])

    if not g.os_path_isfile(normit(fname)):
        if drif and fname: g.es("- ", fname[:53])
        fname = c.mFileName #can fail if not saved

    if not g.os_path_isfile(normit(fname)):
        g.es("no valid filename found %s"% str(fname[:53]))
        return 

    #print g.file_date(fname, format=None)
    #print os.path.getatime(fname)
    fname = normit(fname)
    try:
        if not hasattr(os.path, 'getctime'): #py22
            os.path.getctime = os.path.getmtime
        h = "%s % 5dK  %s\n%- 18s c) %24s m) %24s"%(
            perms(fname),
            os.path.getsize(fname)/1024L,       #comafy
            g.os_path_split(fname)[0],          #dirname
            g.os_path_split(fname)[1],          #text
            time.ctime(os.path.getctime(fname)), #is this locale?
            time.ctime(os.path.getmtime(fname)),
        )
    except (OSError, Exception):
        g.es_exception()
        h = fname

    g.es(h)
#@nonl
#@-node:ekr.20050421093045.20:fileinfo
#@-node:ekr.20050421093045.7:info macros
#@+node:ekr.20050421093045.22:text macros
#@+node:ekr.20050421093045.23:geturls
def dynaM_geturls(c):
    """(c) selected text print/paste
    extract all urls from selected text. included som extra text.
    doesnt span line endings. misses any number of other mal formed urls.
    might use some ideas from the extend rclick post on sf.
    not 100% reliable and not intended to be the last word in re use.
    reconstruction of the found url is at this point just exploratory.

    testing in redemo, modifyed to include rClickclass 
    and multiline text for re's instead of single line entry.
    kodos and redemo work too, but always seeems a little less reliable

    some might want the ability to open the default browser with the url
    thats best let to another plugin or macro or could optionally
    add it to the clipboard.
  ~EOT  
    split out into a dev version.
    add email harvester stage.
    view partial source on a list of url links will add cvrt to &amp;

click enable for geturls, create a page on the fly with the urls
pass it to IE so you can rclick on them
create a numbered range creator 

    added a sort step
   does py2.2 urllib have unquote_plus? remove %20 %7E stuff

    """
    newSel = dynaput(c, [])
    if not newSel: return
    try:
        data = str(newSel)
    except (UnicodeEncodeError, Exception):
        g.es_exception(full= False)
        data = newSel


    import re, urllib

    #from leo
    # A valid url is (according to D.T.Hein):
    # 3 or more lowercase alphas, followed by,
    # one ':', followed by,
    # one or more of: (excludes !"#;<>[\]^`|)
    #   $%&'()*+,-./0-9:=?@A-Z_a-z{}~
    # followed by one of: (same as above, except no minus sign or 
    # comma).
    #   $%&'()*+/0-9:=?@A-Z_a-z}~
    #thers problems with this, I forget what just now.
    #
    #http etc from rClick plugin extension idea posted to leo forum, works
    #scan_url_re="(http|https|ftp)://([^/?#\s]*)([^?#\s]*)(\\?([^#\s]*))?(#(.*))?"
    #re.sub(scan_url_re,new_url_caller,text)  #leaves out a few types
    #
    #r04422a05:03:35 mine still doesnt match everything, and doesnt submatch as well
    #w04519p05:58:10 make a try at verbose,
    #shold relax it from expecting perfect links
    

    #leaves out a few types wais
    # excluding all invalid chars is always for security & sanity
    # worse than including all valid chars, there will be ommisions
    scan_url = r"""
   ([s]*http[s]*|ftp[s]*|[s]*news|gopher|telnet|prospero|link|mailto|file|ur[il])(://)
    ([_0-9a-z%]+?
    :?
    [_0-9a-z%]+?@?)  #takeing some liberties
    ([^/?#\s"']*)
   ([^?#\s"']*)
    (\?*[a-z0-9, %_.:+/-~=]*)
    (\#*[a-z0-9, %_.:+/-~=]*)  #lookup exact name ref link standard
     (&*[a-z0-9, %_.:+/-~=]*)  #needs work
     ([^"<'>\n[\]]*)  #catch the rest till learn repeat
 #   (#|&*[^&?]*.*)
    """
    #(\?*[^&#"'/>\\]*[a-z0-9, %_-~]*?)
    #(\?([^#\s]*?))  #this is doubling the params
    #(&(.*)*?)
    #(#(.*)*?)  
    #end game, this fails
    #urllib.unquote_plus( urllib.quote(

    scan_url_re = re.compile(scan_url, re.IGNORECASE | re.MULTILINE | re.VERBOSE)
    ndata = scan_url_re.findall(data)  #leaves out :// and /
    sx = []
    if ndata:
        g.es('just urls:')
        for x in ndata:
            if not x: continue
            xfixed = list(x)
            #print xfixed
            # some cnet addresses use quot?
            xfixed = [s.replace('&amp;', '&').replace('&quot;', '"')\
                            for s in xfixed]
            try:
                xfixed = [urllib.unquote_plus(s) for s in xfixed]
            except Exception:
                pass

            sx.append( ''.join(xfixed) + '\n')
            #note, this can totally screw things up...
    else: g.es('no urls')  #, data

    #sets another way to get uniq
    #sx = [x for x in dict(sx)] #uniqs it, has problems
    d = {}
    for x in sx:
        d[x] = 1
    sx = [x for x in d.keys()]
    sx.sort()
    dynaput(c, sx)
#@-node:ekr.20050421093045.23:geturls
#@+node:ekr.20050421093045.24:swaper
def dynaM_swaper(c):
    """(c) selected text print/paste
    swap selected and copybuffer. a common task is to cut
    one word or sentance, paste in another place then repete
    with the other word or sentance back to the first position.
    you now can copy the one you want moved, select where you
    want to replace it. and hit swapper. you will have the other
    in the copy buffer and can now paste it over the first.
    
    much harder to describe than to do.
    """
    newSel = dynaput(c, [])
    if not newSel: return
    newSel = str(newSel)

    sx = []

    repchar = g.app.gui.getTextFromClipboard()
    if repchar:
        g.app.gui.replaceClipboardWith(newSel) 
        sx.append(repchar)

    if sx:        
        dynaput(c, sx)
#@-node:ekr.20050421093045.24:swaper
#@+node:ekr.20050421093045.25:flipper
def dynaM_flipper(c):
    """(c) selected text print/paste
    flip selected True to False, 1 to 0 or vice versa
    add your favorite flippable words to the dict below.
    """
    newSel = dynaput(c, [])
    if not newSel: return
    newSel = str(newSel)

    sx = []
    
    #only need one instance of each flip pair, updates w/reverse dict
    flip = {'true':'false',
            'True':'False', 
            # 1/'1' not the same hash, but maybe interchangeable?
             '1':'0',
              1:0,   
             'YES':'NO',
             'yes':'no',
             'right':'left',
             'top':'bottom',
             'up':'dn',
             'n':'f',
             'after':'before',
             'or':'and',
              }
    #print flip

    flip.update(dict([[v, k] for k, v in flip.items()]) )

    #print flip

    if newSel in flip.keys():
        sx.append(flip[newSel])

    if sx:        
        dynaput(c, sx)
#@nonl
#@-node:ekr.20050421093045.25:flipper
#@+node:ekr.20050421093045.26:dupe
def dynaM_dupe(c):
    """(c) selected text print/paste
    very often I want to copy a line or 2, but I only realize
    after I already have something in the buffer to paste over.
    this will duplicate the selected lines after the selected lines
    takeing advantage of the insert point selected being before of after
    pot luck asto which it will be before or after.
  ~EOT  have to unselect first, also makes dependant on the body
    was hopeing to keep those depandancys in dynaput
    incase I allow changes to other widgets or the log
    or even virtual bodys.
    if unselect, or virtual event return to end select kluge
    then dynaput complains nothing selected!
    try just doubling the selected text
    works for single line select anyway. 90% use case
    maybe if nothing selected, copy & paste the node?
    you may need to swith node then back after undo a duped line
    redraw isnt perfect
    """
    newSel = dynaput(c, [])
    if not newSel: return

    sx = newSel.splitlines(True)
    sx += newSel.splitlines(True)

    dynaput(c, sx)
#@nonl
#@-node:ekr.20050421093045.26:dupe
#@+node:ekr.20050421093045.27:clipappend
def dynaM_clipappend(c):
    """(c) selected text 
    append selected to Clipboard
    """
    newSel = dynaput(c, [])
    if not newSel: return

    Clip = g.app.gui.getTextFromClipboard()
    Clip += newSel
    g.app.gui.replaceClipboardWith(Clip)
#@-node:ekr.20050421093045.27:clipappend
#@+node:ekr.20050421093045.28:everycase
def dynaM_everycase(c):
    """(c) selected text print
    take the word or sentance and output in every case
     you can then copy from the log pane which you want.
     this seems easier than trying to consequetively 
     flip through all th possibilities.
     rClick dev version rightclick context menu has this.
    """
    newSel = dynaput(c, [])
    if not newSel: return
    s = str(newSel)

    sx = []

    for x in [
        s.upper(), '  ',
        s.lower(), '  ',
        s.capitalize(), EOLN,
        
        s.swapcase(), '  ',
        s.title(), '  ',
        s.title().swapcase(), EOLN,

        "'%s'"%s, '  ',
        "(%s)"%s, '  ',
        "('%s')"%s.lower(), EOLN,
         ]:
        sx.append(x)

    #here wordwrap or otherwise format and relist it.
    
    if sx:        
        dynaput(c, sx)
#@-node:ekr.20050421093045.28:everycase
#@+node:ekr.20050421093045.29:dyna_regexTk
def dynaM_regexTk(c):
    """(c) selected text print
    changing Tk pack options to dict's
    match alphanumeric on either side of =: or space or coma delimited
    build a dict or list from it. properly quote and verify numbers.
    its only been 3 minutes and I have better results 
    than in plex or pyparsing in more time than I care to admit.
    maybe need re, space double in space delimited means cant ignore
    avoided re for now. probably woulve been easiest

    cuts after the decimal on floats. might want = as an option too
  ~EOT 
    reWhitespace = re.compile( r'[,\s\n]+', re.MULTILINE )
    fields = reWhitespace.split( line )
    
    partially convert to EOLN, need to setup more tests first
        
    """
    newSel = dynaput(c, [])
    if not newSel: return
    newSel = str(newSel)

    g.es('text is', newSel)

    sx = []

    #premassage the data
    newSel = newSel.replace(' ', ',').replace(',,', ',').replace(',,', ',')
    #print 'newSel is %r'%(newSel,)

    for x in newSel: 

        if x in '\'"':
            continue

        if x in [' ', ',', EOLN]: #may fail in py2.2 w/\r\n
            sx.append(EOLN)
            continue

        if x in '=:':
            sx.append(':')
            continue
        
        sx.append(x)


    data = ''.join(sx)
    data = data.replace('\n\n', '\n').replace('\n\n', '\n')
    data = data.replace('\n,\n', ',').replace('\n:\n', ':').replace(',', '\n')
    data = data.replace('\n:', ':').replace(':\n', ':').replace('::', ':')
    #print 'data is %r'%(data,)

    sx = []
    sx.append('{')
    for x in data.splitlines():
        #print 'for x', x

        if not x: 
            continue

        if x in [' ', ',', EOLN]: 
            sx.append(", ")
            continue

        if x.find(':') != -1: 
            x1 = x.split(':') 
            for i, y in enumerate(x1):
                #print 'for y', y

                if i == 1: 
                    sx.append(":")

                try:
                    #sx.append("%d"%int(y) )
                    sx.append("%d"%float(y) )
        
                #maybe float and int will have different errors
                #maybe if int it isnt coerced to float? works for me.
                except Exception, e:
                    #print 'exception', e.args
        
                    s = y.replace('Tk.', "").replace('Tkinter.', "")
                    sx.append("'%s'"%(s.lower(),) )
                #else: sx.append(":") else is only if except tripped

        else: #no : seperator assume is a plain delimited list
            sx.append("'%s':1"%(x,)) 
        sx.append(", ")


    sx.append("}")
    dynaput(c, sx)
#@nonl
#@-node:ekr.20050421093045.29:dyna_regexTk
#@+node:ekr.20050421093045.30:wraper
def dynaM_wraper(c):
    """(c) selected text print/paste
    wrap selected to the len of the first line
    uses the py2.3 textwrap or g.wrap_lines
    http://cvs.sourceforge.net/viewcvs.py/python/
    """
    try:
        if g.app.dynaMvar.bugimport: raise ImportError
        import textwrap as tw
    except ImportError:
        tw = None
        g.es('get textwrap from python cvs or py2.3')
        #return

    newSel = dynaput(c, [])
    if not newSel: return

    data = str(newSel)

    datalines = data.splitlines(True)
    if datalines: width = len(datalines[0])

    width = width or 40
    #get starting indent from first line too

    if tw is None:
        sx = g.wrap_lines(datalines, pageWidth= width, firstLineWidth= width)
        
    else:
        sx = []
    
        t = tw.TextWrapper(
             width= width,
            initial_indent=' ',
           subsequent_indent= ' ',
           expand_tabs= True,
          replace_whitespace= True,
         fix_sentence_endings= False,
        break_long_words= True )

        st = t.fill(data)
        sx.append(st)

    if sx:
        dynaput(c, sx)
    g.es( "len= %d lines= %d len firstline= %d words= %d"%(
        len(data), len(datalines), width, len(data.split())) )
#@nonl
#@-node:ekr.20050421093045.30:wraper
#@+node:ekr.20050421093045.31:+rsortnumb
def dynaM_rsortnumb(c):
    """(c) selected text print/paste
    caller to dyna_sortnumb(c, d= 1 )
    the reverse list will be called before output there
    """
    dynaM_sortnumb.direction = 1
    dynaM_sortnumb(c)

#@-node:ekr.20050421093045.31:+rsortnumb
#@+node:ekr.20050421093045.32:+sortnumb
def dynaM_sortnumb(c):
    """(c) selected text print/paste
    do a numeric aware sort, add field selection later
    maybe even a regex selection or other field specifyer
    can sort a list by copying the seperator then selecting some words
    default seperator is space, \n for multilines
    I realize other options might sometimes be required
    for those times, copy DQ3 and make something specilized.
    checking for multiple lines could be less redundant, ok for now.
    now how do I do a reverse sort?
    have a little helper function to call this with d=1
    need to preserve lineending if selected multiline,
     splitlines(True) ok if body
     how. each choice gets me deeper into trying to guess everything
  ~EOT    keeping indented lines together would allow sorting headlines
     and possibly functions. using a script in the copy buffer?

    """    
    nothingselected = False
    data = dynaput(c, [])
    g.es("selected ")
    if not data:
        nothingselected = True
        g.es("...skip, dump the body")
        v = c.currentVnode() # may chg in 4.2
        data = v.bodyString()

    #maybe use DQ3 thing of the copybuffer to select the splitchar
    splitchar = g.app.gui.getTextFromClipboard()

    multiline = ''
    if not splitchar:
        splitchar = ' '

    
    if 1 == len(data.splitlines(True)):
        sx = [x + splitchar for x in data.split(splitchar)]
    else: 
        multiline = EOLN
        sx = data.splitlines() #True
        
        
    sx.sort(compnum)

    try:
        if dynaM_sortnumb.direction == 1:
            sx.reverse()
            dynaM_sortnumb.direction = 0

    except AttributeError:
        pass

    #deal with nothing selected, must be sort of whole body as lines
    if nothingselected:
        #nothing selected so cant be paste over
        for x in sx:
            print x #might this double line?
    else:
        if multiline:
            sx = [x + multiline for x in sx]
        dynaput(c, sx)

def compnum(x, y ):
    """214202 Pretty_sorting_.htm
    Submitter: Su'\xe9'bastien Keim
    Last Updated: 2003/08/05 
    Sorting strings whith embeded numbers.
    #  sample
    >>> L1 = ["file~2%d.txt"%i for i in range(2, 50, 10)]
    >>> L2 = L1[:]

    >>> L1.sort()
    >>> L2.sort(compnum)
    
    >>> for i,j in zip(L1, L2):
    ...     print "%15s %15s" % (i,j)
       file~212.txt     file~22.txt
        file~22.txt    file~212.txt
       file~222.txt    file~222.txt
       file~232.txt    file~232.txt
       file~242.txt    file~242.txt
    """
    import re
    DIGITS = re.compile(r'[0-9]+')

    nx = ny = 0
    while True:
        a = DIGITS.search(x, nx )
        b = DIGITS.search(y, ny )
        if None in (a, b ):
            return cmp(x[nx:], y[ny:])
        r = (cmp(x[nx:a.start()], y[ny:b.start()])or
            cmp(int(x[a.start():a.end()]), int(y[b.start():b.end()])))
        if r:
            return r
        nx, ny = a.end(), b.end()
#@-node:ekr.20050421093045.32:+sortnumb
#@+node:ekr.20050421093045.33:del_last_char
def dynaM_del_last_char(c):
    """(c) selected text print/paste
    like del first char in the line except
    delete the last char in all the selected lines

    """
    newSel = dynaput(c, [])
    if not newSel: return
    
    try:
        newSel = str(newSel)
    except (UnicodeEncodeError, Exception):
        g.es_exception(full= False)


    sx = []
    for x in newSel.splitlines():
        sx.append(x[:-1] + EOLN )

    dynaput(c, sx)
#@-node:ekr.20050421093045.33:del_last_char
#@-node:ekr.20050421093045.22:text macros
#@+node:ekr.20050421093045.34:codeing macros
#@+node:ekr.20050421093045.35:importnode
#@<< checkFileSyntax >>
#@+node:ekr.20050421093045.36:<< checkFileSyntax >>
#from leoTest params opposit from there
def checkFileSyntax(s, fileName= 'Script'):
    """too hard to get the traceback exact in full= False
    >> checkFileSyntax(''' eros''')
      File "<string>", line 1
        eros
        ^
    SyntaxError: invalid syntax
    True
    >>> checkFileSyntax('''\\n#ok''')
    False
    """
    import leoGlobals as g
    import compiler
    try:
        compiler.parse(s.replace('\r\n', '\n') + '\n')  
        #,"<string>" parse(buf, mode='exec')
        #compile( string, filename, kind[, flags[, dont_inherit]]) 

    except SyntaxError:
        g.es("Syntax error in: %s" % fileName, color= "blue")
        g.es_exception(full= False, color= "orangered")
        return True  #raise

    return False
#@nonl
#@-node:ekr.20050421093045.36:<< checkFileSyntax >>
#@nl

#was pyimportwithindent
def dynaS_importnode(c):
    """(c) selected text/body overwrites.
   combines sfdots, and import to @file.
    assumes code is all in one node. will undo properly,
    but modifys the current node and will write to a temp file,
    then create a subnode from that file.
    @language whatever, you might have to tweek the file extension manually
    if not python c or java, maybe a few others ok, css html.

    will reindent  and syntax check and run evaluator if python.
    for other @language might call astyle.

    should be free of any obvious syntax error.
    when done, you move left, delete the temp node,
    set @path or whatever and fix the headline.
  ~EOT    overwrite False, no sfdots or evaluator
    do I need a pause or update between the selectall and an action?
    added some sense of other lang than python, untested.
    """
    import dyna_menu as dy
    select = g.app.gui.setTextSelection
    overwrite = True

    p = c.currentPosition()
    lang = g.scanForAtLanguage(c, p)
    lang = str(lang).lower()
    tfile = dy.tmpfile

    start = dy.dynaB_Clip_dtef(c, ret='rp')

    if overwrite: 
        #enable to overwrite else will print to log
        dy.dynaMvar.dynapasteFlag.set('paste')
        select(p.c.frame.bodyCtrl, '0.0', 'end')
        dy.dynaS_sfdots(p.c, nodotreturn= True)


    #getsctipy now and check syntax... before/after evaluator
    #what about the undo? can I roll that back too?
    s = g.getScript(c, p)
    
    if lang == 'python':
        if checkFileSyntax(s): g.es(s, 'do undo twice'); return

    #now reindent isn't overwrite and want to run evaluator first
    #but I guess after is ok too.
    #tim1 leaves reindented code in the tmp.py

    if lang == 'python':
        if overwrite: 
            select(p.c.frame.bodyCtrl, '0.0', 'end')
            dy.dynaS_evaluator(p.c)


    if lang == 'python':
        s = g.getScript(c, p)
        if checkFileSyntax(s): g.es(s, 'do undo thrice'); return

    if lang != 'python': #tempfile should already have py extension
        tfile += '.lang' #and pray, there should be a cross ref somewhere
        g.es('writing %s'%tfile)
        fo = open(tfile, 'w')
        fo.write(s+EOLN)
        fo.close()
    else:
        #not sure this shouldn't be a user option instead of hardwired
        dy.doreindent = 1

        #this was depending on reindent being true and file getting written
        select(p.c.frame.bodyCtrl, '0.0', 'end')
        dy.dynaS_tim_one_crunch(p.c)


    c.beginUpdate()
    #might still have to remove a few sentinal lines start & end
    #can this return a sucess or fail? and the maybe the node pointer

    try:
        c.importCommands.importFilesCommand([tfile], '@file')
    except Exception:
        g.es_exception()

    #else: is this if the exception? I can never remember
    #p.selectVnode('after') or something...
    #if headline == ('@file ' + dy.tmpfile):
    #    p.setHeadline('@file some.py')
    #   move before, then select node after, selectall & delete
    c.endUpdate()
    c.redraw()  #update no, redraw seems to work

    dy.dynaMvar.dynapasteFlag.set('print')
    g.es('st:%s\n sp:%s\n may have to wait \nand click to see the new node'%(
        start, dy.dynaB_Clip_dtef(c, ret='r')) )

    #should select child and move left. what if it failed?
#@nonl
#@-node:ekr.20050421093045.35:importnode
#@+node:ekr.20050421093045.37:disa
def dynaS_pydisa(c):
    """(c= None) selected text/body print
    produce a dissasembly into python bytecodes
    of selected text lines of code or the full script
    sentinals are striped to avoid confusing the output
    but of course in execute script they are there
    as should be noted in any timeit type usage
    """
    import leoGlobals as g
    import dis, sys

    import dyna_menu as dy

    p = c.currentPosition()

    #get selected text if any or the whole script
    newSel = dy.fixbody(c,dy.dynaput(c, []))

    if not newSel or len(newSel) == 0:
        return

    newSel = stripSentinels(newSel)

    g.es('dissasembly of: '+ p.headString()[:50])
    g.es(newSel, color= 'MediumOrchid4')
    nc = compile(newSel, '<string>', 'exec')

    #have to find a way to encapsulate this better
    o = g.fileLikeObject()
    sys.stdout = o

    dis.dis(nc)

    s = o.get()
    sys.stdout = sys.__stdout__

    g.es(s.replace('   ', ' '), color= 'sienna3')
#@-node:ekr.20050421093045.37:disa
#@+node:ekr.20050421093045.38:c2py
def dynaS_c2py(c):
    """(c) body+ subnodes overwrite, should backup node first.
    call the fantastic first cut EKR c2py script
    you still have to make it more pythonic but it does quite allot for you.
    c2py doesn't generate an undo event so there is no turning back.    
    @language c, works on other c like language too.

    c2py causing a direct line by line translation of c, you would
    often be served well to rethink some of the program flow.
    dropping just the relevant algorithm translated to python
    into a more generic pythonic wrapper can save allot of time.

    please, be sure to attribute any snippets of code you convert and use.
    I doubt c2py author intends this utility to make plagiarism easy.
  ~EOT  still some things to work out. if the c file is in one node
    it might be better to import it first as c, then let c2py convert it
    using convertCurrentTree it converts in place.
     that might be dangerous if it
    fails or if you need to refer to it later
    OTOH, from a tempfile you wouldn't be able to import
    as there may be logic problems left over from the conversion.

    on selected text or body written to tempfile.
    previously found it easier to call c2py with a filename
    then import the modified file. which did work well.
    usually stick with what works. glad I didn't this time.
    having dyna provide the currentvnode was the missing piece
    and should allow the import as well without a filewrite.
    
    might still make  a backup to another node or to a derived file.
    it also might make sense to run the c thru indent or astyle first
    you definitely want the original to refer to.
    need to run thru reindent or remove tabs maybe too before usage.
    there are clues to give c2py which might help with some specific
    conversions which I haven't examined.
    in the case of declarations I would've left comments on the type
    int x, becomes just x. might have been char or double who knows.
# 
# c2py removes all type definitions correctly; it converts
# 	new aType(...)
# to
# 	aType(...)


classList = [
    "vnode", "tnode", "Commands",
    "wxString", "wxTreeCtrl", "wxTextCtrl", "wxSplitterWindow" ]
    
typeList = ["char", "void", "short", "long", "int", "double", "float"]

 Please change ivarsDict so it represents the instance variables (ivars) used  by your program's classes.
ivarsDict is a dictionary used to translate ivar i of class c to self.i.  
It  also translates this->i to self.i.

    
ivarsDict = {
    "atFile": [ "mCommands", "mErrors", "mStructureErrors",
        "mTargetFileName", "mOutputFileName", "mOutputStream",
        "mStartSentinelComment", "mEndSentinelComment", "mRoot"],

    "vnode": ["mCommands", "mJoinList", "mIconVal", "mTreeID", "mT", "mStatusBits"],

    "tnode": ["mBodyString", "mBodyRTF", "mJoinHead", "mStatusBits", "mFileIndex",
        "mSelectionStart", "mSelectionLength", "mCloneIndex"],
        
    "LeoFrame": ["mNextFrame", "mPrevFrame", "mCommands"],

    "Commands": [
        # public
        "mCurrentVnode", "mLeoFrame", "mInhibitOnTreeChanged", "mMaxTnodeIndex",
        "mTreeCtrl", "mBodyCtrl", "mFirstWindowAndNeverSaved",
        #private
        "mTabWidth", "mChanged", "mOutlineExpansionLevel", "mUsingClipboard",
        "mFileName", "mMemoryInputStream", "mMemoryOutputStream", "mFileInputStream",
        "mInputFile", "mFileOutputStream", "mFileSize", "mTopVnode", "mTagList",
        "mMaxVnodeTag",
        "mUndoType", "mUndoVnode", "mUndoParent", "mUndoBack", "mUndoN",
        "mUndoDVnodes", "mUndoLastChild", "mUndoablyDeletedVnode" ]}  

  maybe I can modify the list dynamically with user input cycle?
  based on an xref of the code to be converted.
  
def convertCurrentTree(c):
    import c2py
    import leo
    import leoGlobals
    v = c.currentVnode()
    c2py.convertLeoTree(v,c) 
    
    wouldn't this obviate any changes to ivars or other code?
    might have to do the same setup w/o the fresh import
    and where to get th custom info from if using M_c2py from plugin?


    messages are going to console instead of log
    converting: NewHeadline
    end of c2py
    might have to capture stdout/err
    or more deviously add a runtime method to change its sys.stdout

   x = {}  will have the {} removed. not sure why...
   removeBlankLines never?
    run tabs to spaces    y/n

    py2.2 coulden't find c2py? try g.import
    """
    import sys
    
    #try g.import, may still fail on py2.2 win9x because
    #uses g.toEncodedString(path,app.tkEncoding) which is utf8 default?
    #it takes verbose as a param, default False, then ignores it on error!
    c2py = g.importFromPath('c2py.py',
        g.os_path_join(g.app.loadDir, '../scripts'))

    if not c2py:
        g.es("can't find the leo/scripts/c2py.py script")
        return

    mess = """\
    the current node & subnodes will be changed
     and there is no undo
     you may have to convert tabs to spaces when done.
     syntax error free code will work the best.
     click ok, then wait for a bit...
     """
    #g.alert(mess)  #g.app.gui
    ans = runAskYesNoCancelDialog(c, "c2py",
                 message= mess, yesMessage= 'ok')

    if 'ok' != ans: g.es('c2py cancled'); return

    #get selected or body... getbody language sensitive
    #write the temp

    #c2py.convertCurrentTree()  #reimports c2py but does work

    #this might fail, but want to try and set some things
    #if it reimports they might get lost...
    c2py.convertLeoTree(c.currentVnode(), c)
    
    #convertLeoTree just node walks, might pass from fixbody
    #then try and reimport to @file from that.
    
    #tmpfile should just be a basename you add extension to?
    #temp = tmpfile[:-3] + '.c'

    #c2py.convertCFileToPython(file) #another way to go
    #cmd = py + c2py + temp
    #out, err = runcmd(cmd)

    c.redraw()  #update nor redraw seems to work every time
    g.es('add an @language python\nand convert tabs to spaces')
#@nonl
#@-node:ekr.20050421093045.38:c2py
#@+node:ekr.20050421093045.39:+dynaHexdump
def dynaS_dump_body(c, ret= 'p'):
    """(c, , ret= 'p') selected text/body print or ret= 'r' return
      yadayada call dynaHexdump(src, length=8), on selected text or body
      if you need an exact output, including any lineendings?
      Leo translates to unicode first so that might be relevant

need feedback from someone who cares about unicode.
UnicodeDecodeError: 'ascii' codec can't decode byte 0x9f in position 1: ordinal not in range(128)
since its not a char at a time, this is going to be hard to trap
maybe will have to filter first. 
    """

    data = dynaput(c, [])
    g.es("selected ")
    if not data:
        g.es("...skip, dump the body")
        v = c.currentVnode() # may chg in 4.2
        data = v.bodyString()

    if data and len(data) > 0:
        #newdata = re.sub("\n", "\r\n", data)
        newdata = dynaHexdump(data)
        if newdata != data:
            #v.setBodyStringOrPane(newdata)
            if 'p' in ret: g.es(newdata)
            if 'r' in ret: return newdata

#had to unicode the FILTER for Leo plugin use
FILTER= u''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def dynaHexdump(src, length=8):
    """
    m02A14p6:31 ASPN Python Cookbook
    Title: Hexdumper.py  Submitter: S?stien Keim  2002/08/05 Version no: 1.0
    Hexadecimal display of a byte stream
    later, output to logwindow of selected text add as a menu option
    maybe can make it read from a file and output as hex
    #r04408ap11:16 chg += to append & join,  not that its particularly slow
    >>> dynaHexdump('ASPN Python Cook')
    u'0000   41 53 50 4E 20 50 79 74    ASPN Pyt    0d\\n0008   68 6F 6E 20 43 6F 6F 6B    hon Cook    8d'
    """
    N = 0; result = []
    while src:
        s, src = src[:length], src[length:]
        hexa = ' '.join(["%02X"%ord(x) for x in s] )
        s = s.translate(FILTER)
        result.append("%04X   %-*s   %s  % 3dd" % (N, length * 3, hexa, s, N) )
        N += length
    return '\n'.join(result)
#@-node:ekr.20050421093045.39:+dynaHexdump
#@+node:ekr.20050421093045.40:_sfdots
def dynaS_sfdots(c, nodotreturn= False, stripsentinals= True):
    """(c, nodotreturn= False, stripsentinals= True) print/paste
    process code from sourceforge forum
    which replaces . for leading indentation which sourceforge eats.
     the reverse too so posters can run their code thru first.
    it would be nice if it could standardize to 4spaces per level
    maybe replacing and rerunning or something to catch max indentation
    run thru reindent and pychecker could be usefull
    the UPL adds only 3 dots when you have 4 spaces and nothing else
    that would probably be an error
    if starts with dots, convert to space DNL
    if all spaces or tabs then is UPL convert to dots
    should check the users tab setting, might want one dot to equal one tab
    other times 4 dots= one tab. you edit in what you want I guess.
  ~EOT  t04323a12:31 optomizing for python indentation, adding use,is at first line
    later make that selectable so can do anything, and or put thru reindent
    and allow add or eat first n chars for command to add to rClick
    using a section header to put the code into a subnode
    precedence of i+1 % n slightly different than c, use (i+1)%n
    messedup indentation this wont fix! shoulve saved a copy of the org...
    this version adds indentation numbers and fails if i>n as yet.
    \n was interpreted from the section literlly as a newline in the output...
    need a slick way to check or switch triple Sq/Dq
    its not transforming 2space into 4spacem it eats \t also
    maybe would be better to change dots to tabs then '\t\tfoo'.expandtabs(2)
    sf eats long lines & spaces ? in view source too. 
    the wiki eats angle brackets and moost html and if you click edit it retranslates 
    f04514a11:22:06 convert to dyna, some sillyness to handle inconsistant dots
    you can run it thru reindent after tim1crunch, copy over then c2py
    which defaults to using tabs. which I will change if I find out how.
    I guess c2py doesnt fail if it finds only python, it tabs it up.
    most of the time that should get standrd indenting no matter what.
   
  I think it still screws up \n literal in strings. not tested w/tabs or unicode
  also will hit a limit on indentation if greater than typical for sf post
  can look weird if printed to log w/non proportional font


This means that the code would refer to Tk.widget instead of Tkinter.widget.  Also, please avoid the use of the completely useless Tk constants such as Tk.RIGHT, Tk.TOP.  Use "right" or "top" instead.  
havent done any replace on the incomming or outgoing data.
chg to fixbody except not sure paste makes sence if it isnt in one node  
might send a download automatically thru reindent then evaluator

allowing conversion of full body, if you try and paste over it will
not follow nodes but probably just overwrite the selected node.

add select leading char ini option 
allow from/to of intrepreter >>> ... for doctest prep
 """
    data = fixbody(c,dynaput(c, []))

    if not data or len(data) == 0: return
    import re
    respc = re.compile(r'^[\s.]*$')

    isdots = [x[:1] for x in data.splitlines() if x.startswith('.')]
    #print 'isdotslist', isdots
    isdots = len(isdots) > 0

    if nodotreturn and not isdots: return

    #py <2.3 YOYO isdots == True , works w/o 
    direction=['UPL', 'DNL',][isdots]  

    #doesnt python have a simpler way to swap varbs? 
    #is this clearer to read though. a='.';b=' '; if UPL: a,b=b,a; 
    #could you have '....' be the eat char in a perfect world?
    
    if direction == 'UPL':
        eatchar=' '
        repchar='.'
    else:
        eatchar='.'
        repchar=' '
    
    if stripsentinals:
        data = stripSentinels(data, stripnodesents=0 )

    #4,3
    lines = ('4,4\n' + str(data.expandtabs(4))).splitlines(True)
    
    #fixes dopy dots, starting off with 3 then continuing with 2
    
    
    n, nm = lines[0].split(',')
    n = int(n) or 4  #what one dot equals
    nm = int(nm) or 3

    #print 'len & direction', len(data), len(lines), direction,
    #print n, nm 

    def chkout(t):
        if respc.findall(t): #cut lines on ., ,\t,\f,\n
            t = '\n'
        return t

    sx = []
    for lt in lines[1:]:
        i = 0
        ix = 0
        for o in lt:
            if o == eatchar: 
                i += 1
                continue
            break
        #print i,
        if i > 0 and len(lt) > 0:
            #this should handle 2 4 or 3 on the first then 2 dots,
            #it will get confused if starts and continues with 3
            if nm == 4: ix = i
            elif i==3 or i == 2: ix = n
            elif i==5 or i == 4: ix = n*2
            elif i==7 or i == 6: ix = n*3
            elif i==9 or i == 8: ix = n*4
            elif i==11 or i == 10: ix = n*5
            elif i==13 or i == 12: ix = n*6
            elif i==15 or i == 14: ix = n*7
            elif i==17 or i == 16: ix = n*8
            else: g.es('**bad ix',i)
            #print (repchar*(ix))+lt[i:]
            sx.append(chkout((repchar*(ix))+lt[i:]) )
            continue
        elif i > 0:
            g.es('')
            continue
        
        #print lt
        sx.append(chkout(lt))

    #print sx
    #reindent or evaluator would help too. before the dots obiously
    dynaput(c, sx)    
    
#@-node:ekr.20050421093045.40:_sfdots
#@+node:ekr.20050421093045.41:+call_evaluator
def dynaS_evaluator(c):
    """(c) selected text/body print/paste
    calc_util.py and its unit tests and rClickclass 
    ******* not available yet *********
   from http://rclick.netfirms.com/rCpython.htm

    parsing python programs perfectly presumes perfect programming.
    its so close, I use it all the time to verify code.
    but I know its limitations and I cant realease it yet,
  ~EOT   does good job of reindenting, but still can make mistakes indenting after dedent or comment or before an indent
   compare to origional code carefully!
   
    forgot to tell evaluator to skip to @c if it finds @ alone
    output to log doesnt colorize so isnt immediatly obvious
    the html mode should be reparsed to change to es color output
    need to add an eval mode so can get expression outpt as well
    have to trap stdout so can use to paste if thats selected
    capture seems to be working now from plugin or button
    fixbody takes care of commenting out @directives now.

    if nothing selected, it seems to have nothing?
    weird, its now going to the console again from the button
    and from plugin nothing if nothing selected.
    this is easily the 3rd time it was then wasnt working.
    all the calls are same as pychecker2, it sometimes prints the data
    inside the if. something is erroring and getting masked.
    
    """
    try:
        if g.app.dynaMvar.bugimport: raise ImportError
        import calc_util ;#reload(calc_util) #if working on calc_util
    except ImportError:
        #can I use Leo prettyprinter instead?
        g.es('you have to get the evaluator first')
        return

    data = fixbody(c,dynaput(c, []))

    if data and len(data) > 0:

        #ta = g.stdOutIsRedirected()
        #g.restoreStdout()
            

        #print repr(data)

        o = captureStd()
        o.captureStdout()

        try:
            #this has print on line by line as parsed
            newdata = calc_util.file_test(data, q= 1,
                 doEval= 0, formater= 'py2py',  #py2py raw html
                    onlyPrintFails= 0, printAny= 0 )

        except Exception, err:
            dynaerrout(err,'evaluator ')

        output = o.releaseStdout()
        #if ta:
        #    g.redirectStdout()
            

        dynaput(c, output.splitlines(True))

    #elif len(data) < 80: maybe check for newlines better?
    #    eror, result, ppir = calc_util.evalcall(data)

#
#@-node:ekr.20050421093045.41:+call_evaluator
#@+node:ekr.20050421093045.42:astyle
def dynaS_astyle(c):
    """(c) selected text/body popup browser
      http://astyle.sourceforge.net/  
    astyle.exe?--pad=oper --style=kr %
    find some other options to try on their homepage.
    A Free , Fast and Small Automatic Formatter
    for C , C++ , C# , Java Source Codes

    mx.Tidy for html

    assumes its on program path.
  ~EOT  possibly add --force  to highlighter or an @force htmlize
    @force node creation & import, many posibilities
    """

    p = c.currentPosition()

    lang = g.scanForAtLanguage(c, p)
    lang = str(lang).lower()
    
    #might be fragile with update of Leo @language
    #and might want to force a mode
    if lang in 'c cpp'.split():
        mode ='c'
    elif lang in 'java javascript jscript'.split():
        mode ='java'
    elif lang in 'html cml css'.split():
        #send thru tidy gets more complicated
        mode ='html'
    else:
        mode = None

    if not mode in 'html c java'.split(): 
        g.es('unsupported language')
        return

    bypass = 2
    source = dynaput(c, [])
    if source: bypass = 0

    source = fixbody(c,source)
    if not source or len(source) <= 0: 
        return

    if bypass: 
        #by pass the problem w/first 2 sentinals syntax errors
        source = ''.join(source.splitlines(True)[bypass:])
        source = stripSentinels(source)

    if mode == 'html': 
        #@        <<tidy>>
        #@+node:ekr.20050421093045.43:<<tidy>>
        try:
            from mx.Tidy import tidy 
        except ImportError:
            g.es('need to install mx.Tidy')
            return
        
        (nerrors, nwarnings, out, err) = \
           tidy(source,
                uppercase_tags=1,
                #alt_text="", 
                char_encoding="utf8",  #raw, ascii, latin1, utf8 or iso2022 
                quiet=0,
                wrap=0,
                indent="yes",  #no, yes or auto 
                clean="yes",
                drop_font_tags=1,
                word_2000="yes", # yes, Tidy will strip out all the surplus stuff 
                )
        #@nonl
        #@-node:ekr.20050421093045.43:<<tidy>>
        #@nl
    else:
        #@        << runastyle >>
        #@+node:ekr.20050421093045.44:<< runastyle >>
        astyle = ["astyle", "--pad=oper", 
                "--style=kr", "-s4", '--mode=%s'%mode]
        g.es(lang, 'running astyle virtual', astyle)
        out, err = runcmd(astyle, source)
        #@nonl
        #@-node:ekr.20050421093045.44:<< runastyle >>
        #@nl

    if out:
        htmlize(c, source= (out + err), lang= lang)

    else:
        for x in (out + err).splitlines():
            g.es(x)
#@nonl
#@-node:ekr.20050421093045.42:astyle
#@+node:ekr.20050421093045.45:pylint
def dynaS_pylint(c):
    """(c) selected text/body popup browser
    create a file and run it thru reindent if enabled then pylint
     default to a tmp filename
    pylint checks over your python code for good form and style
  ~EOTmaybe pylint - options would be best in ini so can override
 or have a dropdown of popular commands for a command
 --generate-rcfile, --help

--statistics=y_or_n 
  Compute statistics on collected data. 
--persistent=y_or_n 
  Pickle collected data for later comparisons. 
--comment=y_or_n 
  Add a comment according to your evaluation note. 
--parseable=y_or_n 
  Use a parseable output format. 
--html=y_or_n Use HTML as output format instead of text. 
--enable-msg=msgids 
  Enable the given messages. 
--disable-msg=msgids 
  Disable the given messages. 
--enable-msg-cat=cats 
  Enable all messages in the given categories. 
--disable-msg-cat=cats 
  
getting no --statistics option error w/pylint 6
not sure I like the html output but spool to log not great either
set html=y, writehead=False and lang=ishtml otherwise
set html=n, writehead=True and lang=report and dohtmlize = 1 for both

    """
    try: import logilab.pylint
    except ImportError:
        g.es('need to install pylint')
        return

    dohtmlize = 1 #show in browser instead of log.    

    data = fixbody(c,dynaput(c, []))

    if not data or len(data) == 0: 
        return

    import sys

    #pylint has to be able to import the file on sys.path

    #this could be trouble on nix or mac. YOYO
    #might not even be necessary in the app, maybe some other
    #if sys.platform[:3] == 'win':
    oldpSath = sys.path[:]
    if not g.os_path_normpath(g.os_path_abspath(
             g.os_path_split(tmpfile)[0])) in sys.path:
        sys.path.append(g.os_path_split(tmpfile)[0] )

    g.es('writeing tmpfile', tmpfile )
    fo = file(tmpfile,'w')
    fo.writelines(data + "%s#e%s"%(EOLN, EOLN, ))
    fo.close()
    
    if doreindent:
        g.es('running reindent', py + reindent + tmpfile )
        out, err = runcmd(py + reindent + tmpfile)
        for x in (out + err).splitlines():
            g.es(x)

    if dohtmlize: html = '--html=n' #y
    else: html = '--html=n'
    
    junk, pylname = g.os_path_split(tmpfile)
    pylname, junk = g.os_path_splitext(pylname) #[:-3] #cut off .py
    g.es('pylint module', pylname )
    pylint = \
    " -c \"import sys; from logilab.pylint import lint;\
             lint.Run(['%s','%s', '%s', '%s', r'%s',])\" "%(
      html, '--comment=n', '--persistent=n', '', pylname,) #--statistics=n

    g.es('running pylint', py + pylint )
    out, err = runcmd( py + pylint)
    
    #should be restored even if error. oh well
    sys.path = oldpSath

    if dohtmlize and out: 
        #the plain text report gets doublespaced in htmlize
        g.es(err)
        htmlize(c, source= out.replace('\n\n', '\n'),
         lang = 'report', writehead= True, show= True) 
    else:
        for x in (out + err).splitlines():
            g.es(x)

    if not g.app.dynaMvar.justpychecker:
        g.es('#source for ', tmpfile, color='blue' ) 
        TextFile = file(tmpfile)
        Text = TextFile.read()
        TextFile.close()
        g.es(Text)

    g.es('done ', color='blue' ) 
#@nonl
#@-node:ekr.20050421093045.45:pylint
#@+node:ekr.20050421093045.46:makatemp
def dynaS_makatemp(c):
    """(c) selected text/body print
    create a file and lightly test it.
     default to a tmp filename

     write out the file and run it thru reindent then pychecker
   then pylint
  external pychecker still has a problem resolveing from import leo*
  not sure how to resolve that. 
  maybe import pythecker.pychecker in the macro?

  using expandtabs(4)
  ***************
    warning, this makes asumptions about where python is, 
    what and where reindent and pychecker is
    at least you have to edit in your correct paths.
    I could guess more but still wouldent be totally sure.
    see the .rc file usefull for pychecker in leoPy.leo
    pylint the same thing.
    url's ...

    I have no idea if pychecker is safe to run on insecure code
    it will create a py and pyc or pyo and maybe a bak file in tmp
    hold me harmless or delete this now.
  ***************
  all paths below are woefully hardwired, you must edit them all.
  you may have to download pychecker and or pylint and install it too.
  ~EOT  wpp[s, this whole thing is breaking down. I forgot one other thing
  the import phase will cause the code to be run. this may or may not be a problem,
  adding a name == main if one doesnt exist might be better
  \nif __name__ == '__main__': pass
  which wont help unless all the indentation on executable lines are indented
  that is too much work I think.

  checking selected text or filenames of generated modules still usefull
  pylint still complaining it cant find the py in temp in sys modules
  may have to dig deeper into that as well
  adding tempdir where the file is doesnt seem to be enough for pylint
    

  for some reason only the @ is getting thru from exS in dynatest
  the re isnt commenting them out either. I HATE re's
  doh, comedy of errors again. forgot the * after .
  was testing date instead of data, misnamed single use varb.
  generated new macro idea to scan for those mistakes.

  have to tell it to skip from @ to @c as well
  
  the name verifyer re isnt workring yet. not fully implimented
     or maybe what is wanted is to take from the copy buffer
     makeatemp and run it thru pychecker then create a subnode with it
     usecsae, posting from c.l.py or from other artical
     handling @directives,
     if copy buffer has a valid path like name, use that
     take the selected text or body (eventually @other & section ref too)
  

  checking plugins would have to add import pychecker; pychecker.pychecker()?
  
    have to abstract the get path thing out to return a tuple of 
    leo, python, scripts, site-packages
    so all macros can find and user only has to change one place
    

  
should   we insert # -*- coding: utf8 -*-
 at the top of the file? or cp1252 or mbswhatever if on windows
 should getscript have that option?
 and dyna does this in several places, need to cosolidate them into one place
    """
    data = fixbody(c,dynaput(c, []))

    if not data or len(data) == 0: 
        return

    tmpname = tmpfile #global or from copybuffer

    import re, os, sys



    #you might not have to fix leo/src either
    #better to get basepath or something, look it up later
    #one run and its in sys.path, sys.path is global for all leo's?
    #another append will be twice in there
    #Leo prepends its src dir but pychecker isnt finding it.

    #this could be trouble on nix or mac. YOYO
    #might not even be necessary in the app, maybe some other
    #if sys.platform[:3] == 'win':
        
    oldpSath = sys.path[:]
    #these changes will be compounded at every run of the script

    if not leosrc in sys.path:
        sys.path.append(leosrc)

    if not g.os_path_split(tmpname)[0] in sys.path:
        sys.path.append(g.os_path_split(tmpname)[0] )
        
    

    g.es('writeing tmpname', tmpname )
    fo = file(tmpname,'w')
    fo.writelines(data + "%s#e%s"%(EOLN, EOLN, ))
    fo.close()
    
    if doreindent:
        g.es('running reindent', py + reindent + tmpname )
        out, err = runcmd(py + reindent + tmpname)
        for x in (out + err).splitlines():
            g.es(x)
        
    g.es('running pychecker', py + pycheck + tmpname )
    out, err = runcmd(py + pycheck + tmpname)
    for x in (out + err).splitlines():
        g.es(x)

    if dopylint:
        pylname = g.os_path_split(tmpname)[1][:-3] #cut off .py
        g.es('pylint module', pylname )
        pylint = \
        " -c \"import sys; from logilab.pylint import lint;\
                   lint.Run([r\'%s\',])\" "%(pylname,)

        g.es('running pylint', py + pylint )
        out, err = runcmd( py + pylint)
        for x in (out + err).splitlines():
            g.es(x)
    
    if not g.app.dynaMvar.justpychecker:
        g.es('#source for ', tmpname, color='blue' ) 
        TextFile = file(tmpname)
        Text = TextFile.read()
        TextFile.close()
        g.es(Text)
    
    #should be restored even if error. oh well
    sys.path = oldpSath  #Leo discards this?

    g.es('done ', color='blue' ) 
#@nonl
#@-node:ekr.20050421093045.46:makatemp
#@+node:ekr.20050421093045.47:tim_one_crunch
def dynaS_tim_one_crunch(c):
    """(c) selected text/body print
    bit of old code from tim peters,
    had to un-htmlify it, then uu.decode it. then un py1.5 it, quite a PITA.
    checks for single use variable and module names. 
    helps catch errors in python code

    write a file only if reindent enabled.
    it can generate alot of false positives.
    
   using the bugfix, slightly more complicated from a later post.
   double check the name polution, uses regex and string too
   woh, was not going to work or needs some updateing.
   more info is better than not hwhen trouble starts.
    its alot faster than you would think too.
~EOT
    might run the makatmp first to create the file and just parse it with this
    rather than pulling in the reindent call. few more lines, what the hell
    reindent doesnt fix to standard indentation. why do I keep thinking it does?
    OTOH, reindent proves the thing has correct syntax so may as well keep it

    have to wait till the last few bugs worked out of evaluator.
    could use to test against known methods and modules in use by the code
    could reduce the false positives.
    if you make the same mistake twice, its no longer unique. is that caught?

    try compile as a way to verify code will import? is it safe?

   patched in import keyword
   added dir(list,dict from the older version
   commented out __modules__ __builtins__ for now
   building a more complete keyword list is the holy grail
   of autocomplete and debuggers and code evaluators of all kinds.

----
    Tim Peters tim_one+msn.com    Thu, 27 Feb 97 09:00:30 UT 
    Attached is a Python program that reports identifiers used only once in a .py (text) file, except for keywords, builtins, and methods on dicts & lists (& the way to expand that set should be obvious). 
    This is much dumber than the other approaches on the table, but has the clear advantage that it's written <wink>, and catches things like "bound but never used" (including-- and this is a mixed blessing! --functions & classes defined but not referenced in their file). ----
    """

    data = fixbody(c,dynaput(c, []))

    if not data or len(data) == 0: 
        return

    tmpname = tmpfile #global or from copybuffer?

    if doreindent:
        g.es('writeing tmpname', tmpname )
        fo = file(tmpname,'w')
        fo.writelines(data + "%s#e%s"%(EOLN, EOLN, ))
        fo.close()
    
        g.es('running reindent', py + reindent + tmpname )
        out, err = runcmd(py + reindent + tmpname)
        for x in (out + err).splitlines():
            g.es(x)

        o = file(tmpname)
        so = StringIO.StringIO(o.read())
        o.close()
    else:
        so = StringIO.StringIO(data + "%s#e%s"%(EOLN, EOLN, ))

    p = c.currentPosition(); 
    #made a caller to hide some of the globals
    Bugfixcrunch(so.readline, '%s '%p.headString()[:15])
    
    if not g.app.dynaMvar.justpychecker:

        g.es('#source for ', tmpname, color='blue' ) 
        
        so.seek(0, 0)
        #.read() and .readlines() doubled up because of \n\r on win
        for x in so.getvalue().splitlines(True):
            g.es(x, newline= false)
    g.es('done ', color='blue' ) 
#@nonl
#@+node:ekr.20050421093045.48:Bugfixcrunch

def Bugfixcrunch(getline, headline='Ex'):
    """u04523p12:01:20  madifying use of globals with 
    calling functions bfcrunch embeded
    the origional crunch has alot of false positives
    
    >Bugfix (RE: Patch to Tim Peters python lint)
    
     (that is, a quote followed by a backslash followed by
     a newline) </I><BR>><i> seems to cause an infinite
     loop... </I><BR><P> More, *any* unclosed uni-quoted
     string fell into that loop -- continued  uni-quoted
     strings are a feature of Python I never used, so was
     blind to the  possibility at first; then conveniently
     convinced myself nobody else used that  misfeature
     <wink> either so I could ignore it.  I lose! <P>
     Attached version fixes that by treating uni-quoted
     and triple-quoted strings  pretty much the same [...]
    """

    [NOTE, CAUTION, WARNING, ERROR] = range(4)
    _level_msg = ['note', 'caution', 'warning', 'error']

    # The function bound to module vrbl "format_msg" defaults to the
    # following, and is used to generate all output; if you don't
    # like this one, you know what to do <wink>.
    
    def _format_msg(
          # the error msg, like "unique id"
          msg,
    
          # sequence of details, passed thru str & joined with
          # space; if empty, not printed
          details = (),
    
          # name of source file
          filename = '???.py',
    
          # source file line number of offending line
          lineno = 0,
    
          # the offending line, w/ trailing newline;
          # or, if null string, not printed
          line = '',
    
          # severity (NOTE, CAUTION, WARNING, ERROR)
          level = CAUTION ):
        try:
            severity = _level_msg[level]
        except:
            raise ValueError, 'unknown error level ' + `level`

        g.es('%(filename)s:%(lineno)d:[%(severity)s]' % locals() )
        if details:
            from string import join
            g.es("%s:" % msg, join(map(str, details)) )
        else:
            g.es(msg)
        if line:
            g.es(line)
    
    format_msg = _format_msg
    
    # Create sets of 'safe' names.
    import sys

    _system_name = {}   # set of __xxx__ special names
    for name in """\
          abs add and
          bases builtins
          call class cmp coerce copy copyright
          deepcopy del delattr delitem delslice
              dict div divmod doc
          file float
          getattr getinitargs getitem getslice getstate
          hash hex
          init int invert
          len long lshift
          members methods mod mul
          name neg nonzero
          oct or
          pos pow
          radd rand rdiv rdivmod repr rlshift rmod rmul ror
              rpow rrshift rshift rsub rxor
          self setattr setitem setslice setstate str sub
          version
          xor""".strip().split():
        _system_name['__' + name + '__'] = 1
    _is_system_name = _system_name.has_key

    import keyword
    
    _keyword = {}   # set of Python keywords
    for name in keyword.kwlist + ['as', 'str'] + dir(__builtins__) + \
            dir(list) + dir(dict):
        _keyword[name] = 1

    #builtins isnt the same from exec as from script outside Leo
    #maybe import builtins? same with methods if it even exists

    _builtin = {}   # set of builtin names
    """for name in dir(__builtins__) + sys.builtin_module_names:
        _builtin[name] = 1
    """
    _methods = {}   # set of common method names
    """for name in [].__methods__ + {}.__methods__:
        _methods[name] = 1"""
    
    _lotsa_names = {}   # the union of the preceding
    for dct in (_system_name, _keyword, _builtin, _methods):
        for name in dct.keys():
            _lotsa_names[name] = 1
    
    #del sys, name  #, dct string,  dict


    
    # Compile helper regexps.
    import regex
    
    # regexps to find the end of a triple quote, given that
    # we know we're in one; use the "match" method; .regs[0][1]
    # will be the index of the character following the final
    # quote
    _dquote3_finder = regex.compile(
        '\([^\\\\"]\|'
        '\\\\.\|'
        '"[^\\\\"]\|'
        '"\\\\.\|'
        '""[^\\\\"]\|'
        '""\\\\.\)*"""' )
    _squote3_finder = regex.compile(
        "\([^\\\\']\|"
        "\\\\.\|"
        "'[^\\\\']\|"
        "'\\\\.\|"
        "''[^\\\\']\|"
        "''\\\\.\)*'''" )
    
    # regexps to find the end of a "uni"-quoted string, given that
    # we know we're in one; use the "match" method; .regs[0][1]
    # will be the index of the character following the final
    # quote
    _dquote1_finder = regex.compile( '\([^"\\\\]\|\\\\.\)*"' )
    _squote1_finder = regex.compile( "\([^'\\\\]\|\\\\.\)*'" )
    
    # _is_junk matches pure comment or blank line
    _is_junk = regex.compile( "^[ \t]*\(#\|$\)" ).match
    
    # find leftmost splat or quote
    _has_nightmare = regex.compile( """["'#]""" ).search
    
    # find Python identifier; .regs[2] bounds the id found;
    # & it's a decent bet that the id is being used as an
    # attribute if and only if .group(1) == '.'
    _id_finder = regex.compile(
        "\(^\|[^_A-Za-z0-9]\)"  # bol or not id char
        "\([_A-Za-z][_A-Za-z0-9]*\)" ) # followed by id

    #del regex, keyword
    #@    << bfcrunch >>
    #@+node:ekr.20050421093045.49:<< bfcrunch >>
    def bfcrunch(getline, filename='???.py' ):
        # for speed, give local names to compiled regexps
        is_junk, has_nightmare, id_finder, is_system_name = \
            _is_junk, _has_nightmare, _id_finder, _is_system_name
    
        end_finder = { "'": { 1: _squote1_finder,
                              3: _squote3_finder },
                       '"': { 1: _dquote1_finder,
                              3: _dquote3_finder }
                     }
    
        multitudinous = {}  # 'safe' names + names seen more than once
        for name in _lotsa_names.keys():
            multitudinous[name] = 1
    
        trail = {}  # maps seen-once name to (lineno, line) pair
        in_quote = last_quote_lineno = lineno = 0
        while 1:
            # eat one line
            where = lineno, line = lineno + 1, getline()
            if not line:
                break
            if in_quote:
                if in_quote.match(line) < 0:
                    # not out of the quote yet, in which case a uni-
                    # quoted string *must* end with a backslash
                    if quote_length == 3 or (len(line) > 1 and
                                             line[-2] == '\\'):
                        continue
                    format_msg( "continued uni-quoted string must \
    end with backslash",  # making this line its own test case <wink>
                                filename=filename,
                                lineno=lineno,
                                line=where[1],
                                level=ERROR )
                    # the source code is so damaged that more
                    # msgs would probably be spurious, so just
                    # get out
                    return
                # else the quote has ended; get rid of everything thru the
                # end of the string & continue
                end = in_quote.regs[0][1]
                line = line[end:]
                in_quote = 0
            # get rid of junk early, for speed
            if is_junk(line) >= 0:
                continue
            # awaken from the nightmares
            while 1:
                i = has_nightmare(line)
                if i < 0:
                    break
                ch = line[i]    # splat or quote
                if ch == '#':
                    # chop off comment; and there are no quotes
                    # remaining because splat was leftmost
                    line = line[:i]
                    break
                else:
                    # a quote is leftmost
                    last_quote_lineno = lineno
                    quote_length = 1  # assume uni-quoted
                    if ch*3 == line[i:i+3]:
                        quote_length = 3
                    in_quote = end_finder[ch][quote_length]
                    if in_quote.match(line, i + quote_length) >= 0:
                        # remove the string & continue
                        end = in_quote.regs[0][1]
                        line = line[:i] + line[end:]
                        in_quote = 0
                    else:
                        # stuck in the quote, but anything
                        # to its left remains fair game
                        if quote_length == 1 and line[-2] != '\\':
                            format_msg( 'continued uni-quoted string \
    must end with backslash',
                                        filename=filename,
                                        lineno=lineno,
                                        line=where[1],
                                        level=ERROR )
                            # the source code is so damaged that more
                            # msgs would probably be spurious, so just
                            # get out
                            return
                        line = line[:i]
                        break
    
            # find the identifiers & remember 'em
            idi = 0     # index of identifier
            while 1:
                if id_finder.search(line, idi) < 0:
                    break
                start, idi = id_finder.regs[2]
                word = line[start:idi]
                if multitudinous.has_key(word):
                    continue
                if trail.has_key(word):
                    # saw it before; don't want to see it again
                    del trail[word]
                    multitudinous[word] = 1
                else:
                    trail[word] = where
                    if word[:2] == '__' == word[-2:] and \
                       not is_system_name(word):
                        format_msg( 'dubious reserved name',
                                    details=[word],
                                    filename=filename,
                                    lineno=where[0],
                                    line=where[1],
                                    level=WARNING )
    
        if in_quote:
            format_msg( 'still in string at EOF',
                        details=['started on line', last_quote_lineno],
                        filename=filename,
                        lineno=lineno,
                        level=ERROR)
    
        inverted = {}
        for oddball, where in trail.items():
            if inverted.has_key(where):
                inverted[where].append(oddball)
            else:
                inverted[where] = [oddball]
        bad_lines = inverted.keys()
        bad_lines.sort()    # i.e., sorted by line number
        for where in bad_lines:
            words = inverted[where]
            format_msg( 'unique id' + 's'[:len(words)>1],
                        details=words,
                        filename=filename,
                        lineno=where[0],
                        line=where[1],
                        level=CAUTION )
    #@-node:ekr.20050421093045.49:<< bfcrunch >>
    #@nl
    bfcrunch(getline, filename= headline)
#@-node:ekr.20050421093045.48:Bugfixcrunch
#@-node:ekr.20050421093045.47:tim_one_crunch
#@-node:ekr.20050421093045.34:codeing macros
#@+node:ekr.20050421093045.50:pre/post macros
#show in the main menu
#@nonl
#@+node:ekr.20050421093045.51:du_test-str
""" if you runthis script on itself it can get infinate on you.
not anymore, but if you do get some recursion in your script,
  if you have a console hit ^C once. save your work often.
  python -i leo your.leo is how to get the console
 @test error reporting seems to go only to the console as yet.
 
 also import of leo* files might be a problem. 
 best used in named sections for functions, 
 you can also put the doc under test in its own node.
 you can also put the code in a named function in a subnode
 inside triple quotes so that the code still has syntax highlighting.
 care to include an extra >>> #blank at the end if used this way.
 there are a few examples in dynacommon, sanitizte_ , ??

 fixed problem for py2.4, master removed from doctest __all__ 
verbosity= fails if leoTest 4.3a1 or earlier

can an option be the first time you click on a dyna item
it becomes a button. 
du_test, delfirstchar often you can't stop at just once.

0 passed and 0 failed. shoud report even if verbosity 0
"""
#@+at
# 
# DO NOT LOAD leo*.py files with load_module it will crash Leo
# leoTest.py is ok, is more or less a standalone to provide @test
# 
# Leo has a safeimport, once it stabalizes can use it for @file.
# you must not run python -OO to use doctest! we detect this
# -O is ok but note, this removes asserts, maybe counter productive!
# 
# uses parts of Rollbackimporter and fileLikeObject
# many thanks to python cookbook providers and contributers
#@-at
#@@c

import leoGlobals as g

#@<< Classes >>
#@+node:ekr.20050421093045.52:<< Classes >>
import os, sys, time

import StringIO #will this be cStringIO from dynacommon?

#__metaclass__ = type

#is sys.platform in less than py2.3?
if sys.platform[:3] == 'win':  
    if sys.version_info[:2] >= (2, 3):
        win_version = {4: "NT", 5: "2K", 6: "XP",
            }[os.sys.getwindowsversion()[0]]
    else: win_version = 'NT' #os.name?
else: win_version = 'NM'

if sys.version_info[:2] >= (2, 5): win_version += ' py>24'
elif sys.version_info[:2] >= (2, 4): win_version += ' py>23'
elif sys.version_info[:2] >= (2, 3): win_version += ' py>22'
elif sys.version_info[:2] >= (2, 2): win_version += ' py>21'
elif sys.version_info[:3] == (1, 5, 2): win_version += ' py152'
else: win_version += ' py<21'

#@verbatim
#@suite unittestfromdoctest needs py2.3

try:
    g.tester
except AttributeError:
    import unittest
    class tester(unittest.TestCase):
        def runTest(self):
            pass
    g.tester = tester()  #now use g.tester in your script
    del unittest

#works exS but points to line 309 in unittest.py instead of here...
#does display in cpmtext better when used in an @test node
#g.tester.assertTrue(1 != 1, 'some message')

#@+others
#@+node:ekr.20050421093045.53:ExitError
class ExitError(Exception):
    """
    this is a cleaner way to exit a script
    raise SystemExit or something else causes much traceback
    so does this but maybe can solve that eventually
    maybe del frames from sys.exception
    also may be called after printing trace from real error
    """
    def __init__(self, value= 'Script decided to bail\n'):
        self.value = value

    def __str__(self):
        return `self.value`
#@-node:ekr.20050421093045.53:ExitError
#@+node:ekr.20050421093045.54:importCode
"""aspncookbook/82234
Importing a dynamically generated module
by Anders Hammarquist
Last update: 2001/10/17, Version: 1.0, Category: System
This recipe will let you import a module from code that is dynamically
generated. My original use for it was to import a module stored in a
database, but it will work for modules from any source.
had to add \n and chg name module and del if already in modules
"""

def importCode(c,code, name, add_to_sys_modules= 0):
    """
    Import dynamically generated code as a module. code is the
    object containing the code (a string, a file handle or an
    actual compiled code object, same types as accepted by an
    exec statement). The name is the name to give to the module,
    and the final argument says wheter to add it to sys.modules
    or not. If it is added, a subsequent import statement using
    name will return this module. If it is not added to sys.modules
    import will try to load it in the normal fashion.

    import foo

    is equivalent to

    foofile = open("/path/to/foo.py")
    foo = importCode(c,foofile, "foo", 1)

    Returns a newly generated module.

    tried to inject a sample unittest sub class
    just to get assert_ and maybe the other tests automatically
    it is shown in the verbose though doctest can be told to ignore.
    next problem, if the test class is injected first, 
    the scripts first docstring is no longer the __doc__ of the module
    if its injected last then _t is undefined...
    do I exec it first to get the doc, then set mymod.__doc__ = doc?
    cant have any code before the doc. might be an acceptable price to pay
    but unittest also doesnt know it then the scripts cant do both
    """
    import sys, imp
    try:
        if hasattr(sys.modules, name):
            del(sys.modules[name])
    
        modl = imp.new_module(name )  #was module

        #problem if run du_test now on new Leo4.3 scripts w/o c,g,p defined
        #shoulden't matter if its other than c,g,p then still errors?
        #might not even be necessary. had a script that was a getscript on itself
        try:
            exec code + '\n' in modl.__dict__ #du_test
        except AttributeError, e:
            g.es('%s\npossibly no doc string defined?'%(e,))
            g.g.es_exception(full= True)

        except NameError:
            p = c.currentPosition()
            d = {'c':c, 'p':p, 'g':g}
            g.es('*** defining c,g & p ***')
            modl.__dict__.update(d)
            exec code + '\n' in modl.__dict__ #du_test w/c,g,p

        if add_to_sys_modules:
            sys.modules[name ] = modl

    except Exception:  #probably not exactly correct
        #g.es_exception()
        raise # ImportError
   
    return modl

if 0: # Example
    code = """
def testFunc():
    print "spam!"

class testClass:
    def testMethod(self):
        print "eggs!"

import unittest
class _t_(unittest.TestCase):
    def runTest(self):
        pass
_t = _t_()
"""

    m = importCode(c,code, "test")
    m.testFunc()
    o = m.testClass()
    t = m._t_()
    o.testMethod()

#
#@nonl
#@-node:ekr.20050421093045.54:importCode
#@-others
#@nonl
#@-node:ekr.20050421093045.52:<< Classes >>
#@nl

def dynaZ_du_test(c):
    """(c= None) selected text/body docstrings + exec any code, print
    run a doctest unittest from a docstring in the script/selected 
    or run @test, see test.leo and leoTest.py
    or @suite all subnodes run.

 _function single underscored ignored in doctest 
 nested sub functions ignored in doctest,
 note also you have to double backslashes or use r raw triple quote strings.

    in your script you can use:
    g.tester.assertTrue(1 == 2, 'help unittest for other compares')
    you may have to import leoGlobals to use.
    which isn't a much of a deal breaker.
    
   care required because the script under test is exec with any sideeffects.
  if __name__ == 'mymod': will be run only under du_test doctest, not @test
  if __name__ == '__main__': standard way to guard from execution
  ~EOT  
    is redirecting the unittest error to log properly. 
    try append -v to argv, no luck.
    need setting for verbose in leoTest instead of hardwired call
    dyna_menu.ini verbosity=0/1/2

    must be in leoText. run w/console python -i open to see
    need version 2.3. convert a doctest into a unittest if use leoTest
    du_test doesn't create temp files and doesn't require @file
  seems I have developed a superstition about reload of sys and unittest. 
  but dammed if @test nodes stoped redirecting, so reloads are back in again!
  put all 3 back but one or the other might be enough. subject closed again.
  flip verbose now flips 0 to 1, 1 to 2 and 2 to 0, default starts out at 0

  is this wrongly bailing after the first failed test?
  sometimes you fix one test of a multiple then another failed test shows up!
    """
    import doctest
    import sys, os

    #1 leo globals, 0 forcefull sys, 2 underlying file stdio nfg
    use_Leo_redirect = 0 

    p = c.currentPosition() 

    #solve the doc/unittest infinate problem if run test on this node
    if p.headString().startswith('du_test-str'): g.es('infinate'); return

    c.frame.putStatusLine('testing '+ p.headString()[:25], color= 'blue')
    #c.frame.statusText.configure(
    #    state="disabled", background="AntiqueWhite1")


    if pyO[0] == 'O':
        g.es('assert disabled, use g.app._t.assert_()',
            color= 'tomato')
        #unreliable as yet...
        if 0 and dynaZ_du_test.__doc__ is None:
            g.es('YOU HAVE RUN python -OO \ndoctest fails, @test ok',
                color= 'tomato')

    s = '*'*10
    g.es(win_version, time.strftime(
        #why is this not available? 
        #g.app.config.body_time_format_string or 
        '%H:%M.%S %m/%d/%Y'
    ))
    

    g.es('%s \ntesting in %s\n%s\n'%(
        s, p.headString()[:25], s), color= 'DodgerBlue')

    reload(sys)
    #print sys.argv
    #if not '-v' in sys.argv:
    #    sys.argv.append('-v')
    #    g.es(sys.argv)

    #@    << n_redirect >>
    #@+middle:ekr.20050421093045.55:guts
    #@+node:ekr.20050421093045.56:<< n_redirect >>
    #when run on @test print goes to console
    #this simple redirect isnt working
    #might need to set stdout/err more forcefully
    #have the same problem with evaluator 
    #and it screwsup log redirect after its done.
    if use_Leo_redirect == 1:
        g.redirectStdout(); g.redirectStderr()
    
    elif use_Leo_redirect == 0:
        sys.stdout = g.fileLikeObject() #'cato'
        sys.stderr = g.fileLikeObject() #'cate'
    
        #usually you dont want to do this,
        _sosav = sys.__stdout__
        sys.__stdout__ = sys.stdout
        _sesav = sys.__stderr__
        sys.__stderr__ = sys.stderr
    
    elif use_Leo_redirect == 2: #c.l.py suggested
        #how ironic, I can remove the requirement for temp file
        #for docutils, but not for redirecting IO? dup needs fileno
        _sosav = sys.__stderr__
        #_sesav = sys.stderr
        def myfileno(self= None, *argy, **kews):
            print 'fn', argy, kews
            return 1
        #g.funcToMethod(myfileno, g.fileLikeObject, 'fileno')
        #g.funcToMethod(fileno, g.fileLikeObject)
    
        #g.fileLikeObject.fileno = myfileno
        f = g.fileLikeObject()
        #f.fileno = 1  
        f.fileno = myfileno  #()
        #not callable, when it is callable it says not attribute!
        #AttributeError: redirectClass instance has no attribute 'fileno'
        #it goes deeper than I first thought, the redirecttolog is still there
    
    
        #f = file('out.txt', 'a')
        #os.dup2(1, sys.__stderr__.fileno())
        os.dup2(f.fileno, sys.__stderr__.fileno())
        #os.dup2(f.fileno(), sys.stderr.fileno())
    #@-node:ekr.20050421093045.56:<< n_redirect >>
    #@-middle:ekr.20050421093045.55:guts
    #@afterref
  #a bad named section is ignored when run
    #import/reload after redirect fixes redirect to log from unittest
    import leoTest
    import unittest

    reload(unittest)
    reload(leoTest)
    

    if p.headString().startswith('@test ') or\
         p.headString().startswith('@suite '):
        leoTest.doTests(all= False,
         verbosity= g.app.dynaMvar.verbosity) #

    else:
        #@        << DocTest >>
        #@+middle:ekr.20050421093045.55:guts
        #@+node:ekr.20050421093045.57:<< DocTest >>
        
        tmpimp = tmp = 'mymod' #name for the mock module
        
        #g.es('mock writeing ', tmpimp)  #
        fo = None
        
        try:
            #could add a real/mock mode default mock, 
            #need to simulate file open for write+ since read will fail
        
            #fo = g.fileLikeObject(tmpimp) 
            script = g.getScript(c, p) #.strip()
            if not script: g.es('no script no test'); return
        
            #fo.write(script + "\n#e\n")
            #fo.seek(0, 0)  #rewind
            #fo.geek()  #test unknown attribute
        
        except Exception:
            g.es_exception(full= False)
            raise ExitError  #be nice if this happened w/o extra exytax error
        
        mod = None
        try:
        
            #mod = __import__(fo, {}, {}, ["*"])
            mod = importCode(c,script, tmpimp, add_to_sys_modules= 1)
        
        #could be other errors the way this is setup isnt there yet.
        except ImportError, err:
            g.es('error importing tmpimp\n', tmpimp, color='tomato')
            g.es_exception()
            #except needs a break or maybe the doctest goes in else?
            #you cant mix except and finally...
            #an exit w/o rais would belp too still need to close the file
        
        try:
            if mod:
                #need to tell it to ignore testing class t_
        
                doctest.testmod(mod, verbose= g.app.dynaMvar.verbosity,
                     report= 1, globs=None, isprivate= doctest.is_private)
                #doctest.master.summarize()
                #ValueError: line 10 docstring xyz inconsistent leading whitespace: 
                #could mean need to double the backslashes like \\n or raw the docstring
        
                try:
                    #no longer exposed in py2.4
                    del doctest.master #bad idea if don't set to None
                    doctest.master = None
                except Exception:
                    pass
        
        except Exception, err:
            g.es('error doctest mod\n', mod, color='tomato')
            g.es_exception()
        
        if fo: fo.close() 
        #@nonl
        #@-node:ekr.20050421093045.57:<< DocTest >>
        #@-middle:ekr.20050421093045.55:guts
        #@nl

    #@    << f_redirect >>
    #@+middle:ekr.20050421093045.55:guts
    #@+node:ekr.20050421093045.58:<< f_redirect >>
    #code below may cause problem if not run 
    #if except traps further up
    #needs its own try/finally
    #is the __ mangling causing sys.__std* not to work corectly?
    
    if use_Leo_redirect == 1:
        g.restoreStdout(); g.restoreStderr()
    
    elif use_Leo_redirect == 0:
        oo = sys.stdout.get()  #read get()
        oe = sys.stderr.get()  #get()
        sys.stdout.close()
        sys.stderr.close()
    
        #if you didnt do this it wouldent need to be reversed
        sys.__stdout__ = _sosav
        sys.__stderr__ = _sesav
    
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    
    elif use_Leo_redirect == 2:
        #if this works eliminate choice 0
        oo = 'stderr'  #sys.stderr.read()  #read get()
        #oe = sys.stderr.get()  #get()
        oe =''
        #sys.stderr.close()
        #sys.stderr.close()
        sys.__stderr__ = _sosav
        #sys.__stderr__ = _sesav
    
    if use_Leo_redirect != 1:
        for x in (oo + oe).splitlines():
            g.es('%s'%x, color= 'chocolate')
    #@nonl
    #@-node:ekr.20050421093045.58:<< f_redirect >>
    #@-middle:ekr.20050421093045.55:guts
    #@nl

    g.es('nonews is goodnews%s'%(g.choose(pyO[0] == 'O', ' +-O', ''),),
        color= 'DodgerBlue')

    #not sure why but this dissapears in a few seconds, 
    #maybe script end clears it? add an idle 200ms
    c.frame.putStatusLine(' fini ', color= 'DodgerBlue')
    #bad color here causes too much traceback
    #c.frame.statusText.configure(background="AntiqueWhite2")
#@+node:ekr.20050421093045.55:guts
#@-node:ekr.20050421093045.55:guts
#@-node:ekr.20050421093045.51:du_test-str
#@+node:ekr.20050421093045.59: htmlize
def dynaZ_htmlize(c, source= None, lang= 'plain', 
        writehead= True, show= True):
    r"""(c= None, source= None, lang= 'plain', 
        writehead= True, show= True)
        lang = report or ishtml or @language
    htmlize a script, popup webbrowser if show is True.
    if you set BROWSER env variable I think you can force
    a particular browser otherwise it uses your default.
    
    grabed parser fromfrom the moinmoin for python code, 
    default is to strip leo sentinal linesm leave node & directives.

    you must edit in browser & filename, 
       explorer c:\WINDOWS\TEMP\python.html
       or use %tmp%/htmlfile.html defined in dynacommon
    
    wonder still about how to solve encoding?
    rst/plain option not fully realized
    source-highlite still wants to make verbose to stderr?
    finish implementing EOLN and check in plain per body
    for new directives of wrap and lineending and language
    will any of this output survive various encoding
    will it validate as error free html?
 ~EOT
    #@    <<more doc>>
    #@+node:ekr.20050421093045.60:<<more doc>>
    you can tweek the title in the format and sanitize_ method
    edit in your favorite style bits there too.
    copy combined default.css silvercity.css where the filename will be
    
    uses psyco if available.
    
    script should be python, free from most syntax errors 
    but accepts other languages 
    and eveutually will use the keywords from that language
    for now call another parser, silvercity if it exists.
    sends @language css html perl c java and others to silvercity
    (not fully tested in all languages for all syntax)
    
    you can choose to colorize Names, Operators and Numbers seperately
    or not at all by editing the htmlize macro hopts dictionary. 
    Note: filesize larger if all 3 different than Text color.
    
    needs Leo4.2 but is easily revertable.
    
    could add linenumber and code metrics options.
    
    can make it capable of reading writing a file as well?
    wonder can I open browser and send it virtual html like in js?
    might mod for class & span instead of pre & font
    
    have to have path set for getScript to work. 
    in new leo it will traceback if not saved once?
    added some traps for empty script. 
    meaningfull errors messages can't really be determiate
    w/o some novice/expert clue from the system. 
    have a few depandancies on dyna otherwise could be scriptButton
    use python webbrowser.
    add experimental code folding on def & class for python only
     works in IE5 and firefox1 and shouldent affect others much
     might just be an extra header above def and class
     eventually will option it invisable for printing and copy&paste
     enable/disable in the htmlize options bunch as with other options
     and there would be an ini option available too in the great beyond.
    its cutting the def/class name and not enclosing the body of it
    
    this guy took it to the next level, like the idea of color themes.
    http://bellsouthpwp.net/m/e/mefjr75 /python/PySourceColor.py
    
    more advanced stripSentinals suggested by EKR.
    getconfig for ini options in hopts
    need another option to looklikeLeo
    show directives but not commented out, 
    others w/o excess space, verbatim as it is etc
    then can almost use extract named section to recreate nodes
    
    if showdefaults, it doesn't take into account
    the override factor in the defaults in hopts
    complicated by Properties dialog not being able to handle them all
    need to have more than one ini seletable as well
    for various class or color schemes or some other way to select them
    which css to embed. maybe get it from parsing a parent node or ???
    
    seems to be taking little longer to popup browser in py2.4.1, not always.
    if not python should check for silvercity, then one of the others
    maybe need option default colorizer, otherwise there is too much guessing.
    if neither then output as text. as it is now, temfile is written first
    and only output as text if it is not one of silvercity languages
    the others have more or less languages supported. a config nightmare.
    check is @file and offer to produce file.xyz.html
    check is @rst and if option dorst then send plain to docutils?
    add option css/font and if css 
    then eliminate dups is mandatory, css triples filesize.
    
    option   silvercity or src-hilite for other than plain or rst or @rst
    sent plain or rst to docutils if if available 
      else pre/pre w/wraping and headlines made of any node healines
    
    there should be an @language rst to help with REST syntax 
    possibly this would be a major pain just because.
    idea for further study though. @rst for now good enough
    and should not interfere with any rst* plugin
    
        seems obvious now, but call the plain text output if
        none of the colorizers can do it, just set silver!=didit & break!
        also explore calling leo colorizer, does it act or can  it be made
        to return a pseudo body one can parse for Tk tags to get color info
        dl jthon port and see how that handles colorizer for various languages
        uses the combined default.css for rst and silvercity in dyna.txt
    
        another thing would be to extract the essential html generation parts
        so it could be called by rst for code-blocks using existing colorizer
        rather than internally attempting to ifdef around the problem.
    
           
    - sgbotsford
    What I want to do is print the outline showing 
    the indents, with all outlines expanded, and optionally: 
    *Don't print any of the body text. 
    *Print the first N lines of body text in each node 
    *Print all the body text. 
     
    Nice to have: 
    Outline and body text is in the respective fonts 
    chosen in preferences. 
    
    
    
    might have to define some lang options, 
    lang=ishtml will assume is complete escaped html
     that will mean nothing can be controeled about the font or css?
     mabe should mean we extract the body
    lang=checker
    #@-node:ekr.20050421093045.60:<<more doc>>
    #@nl

    global EOLN had to import dynacommon
    is somewhat in need of some flow refactoring 
    and -quiet via verbosity
    another dependancie.
    and I'm checking for \n but using EOLN everywhere
    and will fail in less than py2.4 docutils no BLANKLINE
    if silvercity then will output fullhtml so far

    <BLANKLINE> doesn't exist for doctest less than 2.4 maybe will fail?
    not even sure its the proper result at this point either.
    a test that has the wrong output at least shows htmlize is runnable.
    
    >>> dynaZ_htmlize(c,None, '\n', lang= 'checker', writehead=0, show=0)
    <BLANKLINE>
    <BLANKLINE>
    <BLANKLINE>
    >>> dynaZ_htmlize(c,None, '\n', 'c', writehead=0, show=0)
    '<pre><tt>\n\n</tt></pre>\n'

    that one is output instead of returned
    the redirection of stdout shoulden't always happen if show=0

    would be nice if there were a find for variable/keywords not just text
    if source is one line and a URL maybe it should try to open it?
    

    adding a debugging switch to force ImportError fallback for testing
    should extend it to raise any specific errors that might be caught.
    going to have to rethink some of the testing under test.leo
    what will the namespace be, will g.app.dynaMvar.verbosity be defined?
    replace a few of the verboaity with if not source 
    want to get output feedback unless under test
    """
    #@    << initilize >>
    #@+node:ekr.20050421093045.61:<< initilize >>
    #trick from aspn/299485
    #htmlize is really plenty fast even on >100k source, 
    #but may as well see if this ever causes errors
    #forgot to get some base timeings before and after.
    #doesnt help the silvercity branch
    import os, sys
    
    base_class = object #is object in py2.2
    if 1:
        try:
            # If available use the psyco optimizing
            #might psyco be enabled elsewhere and still work in here?
            import psyco.classes
            if sys.version_info[:2] >= (2, 3):
                base_class = psyco.classes.psyobj
        except ImportError:
            pass 
    
    import leoGlobals as g
    
    import cgi, StringIO, re
    import keyword, token, tokenize
    
    #so can test, idealy done only if __doctest__ or in some test
    from dynacommon import stripSentinels, sanitize_, runcmd, EOLN 
    
    
    #this well could be version dependant
    _KEYWORD = token.NT_OFFSET + 1
    _TEXT    = token.NT_OFFSET + 2
    
    _colors = {
        token.NUMBER:     '#483D8B', #black/darkslateblue
        token.OP:         '#000080', #black/navy
        token.STRING:     '#00AA00', #green 00cc66
        tokenize.COMMENT: '#DD0000', #red cc0033
        token.NAME:       '#4B0082', #black/indigo
        token.ERRORTOKEN: '#FF8080', #redred bare null does it
        _KEYWORD:         '#0066ff', #blue
        _TEXT:            '#000000', #black /is text fg color too
        '_leodir':        '#228B22', #directive, forest comment
        '_leosen':        '#BC8F8F', #sentinal, tan fade comment
        'bg':             '#FFFAFA', #snow
    }
    #@nonl
    #@-node:ekr.20050421093045.61:<< initilize >>
    #@nl

    #@    @+others
    #@+node:ekr.20050421093045.62:class Parser
    
    class Parser(base_class):
        """ prep the source for any language
            parse and Send colored python source.
        """
        #@	@+others
        #@+node:ekr.20050421093045.63:__init__
        def __init__(self, raw):
            """ Store the source text.
            """
            #self.raw = string.strip(string.expandtabs(raw) )
            self.raw = raw.strip().expandtabs(4) 
            #might normalize nl too
            
            #need to know delim
            cmtdelim = '#'
            if lang != 'python':
                sdict = g.scanDirectives(c, p) 
                #obviously for other language have to check is valid
                #or need open/close comment. 
                #misses the opening html cmt, [0] only for singles
                #not sure I even know all the comment specifyers
                # its @, // html, ' are there any that screwup regex?
                cmtdelim = sdict.get('delims', ['#'])
                cmtdelim = cmtdelim[0] or cmtdelim[1]
            
            self.posspan = 0 #keep pos for collapse links on def & class
            self.spancnt = 0
            
            self.fnd = re.compile(r"%s@\s*@+."%(cmtdelim,) )
        
            #g.es('using delim=', cmtdelim)
            
            #if hopts['stripsentinals']: almost always do something
            self.raw = stripSentinels(self.raw, **hopts)
        
        #@-node:ekr.20050421093045.63:__init__
        #@+node:ekr.20050421093045.64:format
        def format(self, formatter, form):
            """ Parse and send the colored source.
            """
        
            # store line offsets in self.lines
            self.lines = [0, 0]
            pos = 0
            while 1:
                pos = self.raw.find(EOLN, pos) + 1
                if not pos: break
                self.lines.append(pos)
            self.lines.append(len(self.raw))
        
        
            self.pos = 0
            text = StringIO.StringIO(self.raw)
        
            #use of \n not sure if will follow users lineending, but it should
            #anywhere htmlize adds it should use EOLN
        
            # parse the source and write it
            try:
                tokenize.tokenize(text.readline, self)
            except tokenize.TokenError, ex:
                msg = ex[0]
                line = ex[1][0]
                print "<h3>ERROR: %s</h3>%s" % (
                    msg, self.raw[self.lines[line]:])
        #@-node:ekr.20050421093045.64:format
        #@+node:ekr.20050421093045.65:__call__
        def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
            """ Token handler.
            """
            if 0: print "type", toktype, token.tok_name[toktype], "text",\
                    toktext, "start", srow,scol, "end", erow,ecol, "<br>"
        
        
            # calculate new positions
            oldpos = self.pos
            newpos = self.lines[srow] + scol
            self.pos = newpos + len(toktext)
        
            # handle newlines
            if toktype in [token.NEWLINE, tokenize.NL]:
                print
                return
        
            if hopts['codefold']: 
                if self.posspan >= self.pos:
                    dospan = False
                else: dospan = True
        
            style = ''
            if toktype == tokenize.COMMENT:
                #setrip comment a little more complicated than sentinals
                #sentinals are always exactly one line, sometimes indented
                #comments after code would need to do NL?
                
                if toktext.lstrip().startswith('#@'):
                    
                    #if hopts['stripsentinals']: return  #do in __init__
                        
                    if self.fnd.findall(toktext):
                        toktype = '_leodir'
                    else:
                        toktype = '_leosen'
        
            # send the original whitespace, if needed
            if newpos > oldpos:
                sys.stdout.write(self.raw[oldpos:newpos])
        
            # skip indenting tokens
            if toktype in [token.INDENT, token.DEDENT]:
                self.pos = newpos
                return
        
            # map token type to a color group
            if token.LPAR <= toktype and toktype <= token.OP:
                toktype = token.OP
        
            elif toktype == token.NAME and keyword.iskeyword(toktext):
                toktype = _KEYWORD
        
                if hopts['codefold'] and toktext in ['def', 'class',]:
                    dospan = True
                    self.posspan = self.pos
                    self.spancnt += 1
                    tag = '%s%s'%(cgi.escape(toktext), self.spancnt,)
                    sys.stdout.write("""\
        <a onclick="toggle(%s)" onmouseover="this.style.color='red'" onmouseout="this.style.color='black'">
        <h5>%s<img src="rarrow.gif" width="14" height="14"></h5></a>
        <span ID=%s Style=Display:''>
        """%(tag, tag, tag,  # None, none turns it off by default
            )) #need a 2pass to do this right, or look 1ahead to def/class name
        
        
            #this could be a decorator if run on py2.4 code from <py2.4
            if toktype == token.ERRORTOKEN:
                style = ' style="border: solid 1.5pt #FF0000;"'
        
            #color = _colors.get(toktype, _colors[_TEXT])
            #instead use try to bail if no key defaulting to body fg color
        
            dofont = True
            try:
                color = _colors[toktype]
                sys.stdout.write('<font color="%s"%s>' % (color, style))
            except Exception:
                dofont = False
        
            sys.stdout.write(cgi.escape(toktext))
            if dofont: sys.stdout.write('</font>')
        
            if hopts['codefold']: 
                #this is going to need allot more work to be reliable
                if dospan: #set when out of the def or class
                    self.posspan = 0
                    sys.stdout.write('</span>')
        #@nonl
        #@-node:ekr.20050421093045.65:__call__
        #@-others
    #@-node:ekr.20050421093045.62:class Parser
    #@-others

    p = c.currentPosition() 
    fullhtml = err = out = None
    
    #to remind, really need to get keywords from Leo for some languages
    #then could handle odd languages better w/same parser
    #c.frame.body.colorizer.python_keywords.append("as")
    #@    <<hopts>>
    #@+node:ekr.20050421093045.66:<<hopts>>
    #dyna would have read the ini already into a global Bunch
    #that will be one of the options for htmlize
    #its probably still possible to screwup the ini and dyna won't import
    
    #need to use a getter in Bynch so nonesistant ivar returns None?
    #possibly could set it with a get and default if doesn't exist property?
    
    if not hasattr(g.app.dynaMvar, 'htmlize_filename') or\
             g.app.dynaMvar.htmlize_filename == 'default':
        filename = sys.modules['dyna_menu'].htmlfile
    else:
        #and don't blame me or Leo if you make this a URI and get burned...
        filename = g.app.dynaMvar.htmlize_filename
    
    if not hasattr(g.app.dynaMvar, 'htmlize_timestring') or\
            g.app.dynaMvar.htmlize_timestring == 'default':
        timestring = sys.modules['dyna_menu'].dynaB_Clip_dtef(c, ret= 'r')
    elif g.app.dynaMvar.htmlize_timestring == 'leodefault':
        timestring = c.getTime(body=True)
    
    else:
        #effectively a string because I'm not planning on using eval
        timestring = g.app.dynaMvar.htmlize_timestring
    
    #decide which options to apply
    #strip sentinals, comments, syntaxcheck for only python?
    #then create alternate reality for c, c++, other language
    #assume text only nodes are language plain? respect killcolor?
    #to simplify the output 
    #set True for noNUMBER, noOP or noNAME 
    #to disable seperate colors for that entity.
    # the more colors the bigger the output html
    #have to switch to lowerrunoncase names, ini is not case sensitive for items
    #could make another run thru to use the proper cased attributes but life is too short
    #or make it a caseinsensitive Bunch subclass
    #why isnt this a Bunch already?
    hopts = {
      'codefold':False, #experimental, can be more confusing
      'stripcomments':False, #think this can still allow nodesents
      'stripsentinals':True,   #you can have directives if no sentinals.
      'stripnodesents': False, # False: leave node sentinels.
      'stripdirectives':False,
      #no color key, that item defaults to text color
      'nonumber':False,
      'noop':False,
      'noname':True,  
      'filename': filename,  #in dynacommon or ini
      'timestring': timestring,
       #path to silvercity css file, that might be too hard to debug.
    }
    
    #syncup ini with default hopts
    for k,v in hopts.items():
        if k in ['filename', 'timestring', ]: continue
        #g.trace(k, v)
        if not hasattr(g.app.dynaMvar, 'htmlize_'+k.lower()): continue
        #g.trace('has :', getattr(g.app.dynaMvar, 'htmlize_'+k.lower()))
        #these should already be verified T/F
        hopts[k] = getattr(g.app.dynaMvar, 'htmlize_'+k.lower())
    
    #much as I hate to admit it, the colors will have to be changable
    #and color might be different for each language
    #should allow external css or settable style options same way
    #the Properties dialog only can handle a dozzen options on a large screen
    
    #I know there is a way to do this inside the _color dict
    #it would involve setting hopts before calling initilize
    if hopts['nonumber']: del _colors[token.NUMBER]
    if hopts['noop']:     del _colors[token.OP]
    if hopts['noname']:  del _colors[token.NAME]
    #@nonl
    #@-node:ekr.20050421093045.66:<<hopts>>
    #@nl

    if not source:
        lang = g.scanForAtLanguage(c, p)
    
        #str only fails is there is no current encoding for a char.
        #was erroniously thinking it always fails on Unicode.
        lang = str(lang).lower()

        #think this trips an assert if you pass a vnode    
        #redundant if @rst or plain and fails if the first node is empty
        #will have to redesign this flow
        #think getscript Leo4.3a4 doesnt do selected text w/directives?
    
        source = g.getScript(c, p)  #.strip()

    titl = "%s Leo %s script %s"%(
            p.headString()[:75], lang, hopts['timestring'])

    if hasattr(g.app.dynaMvar, 'htmlize_hilighter'):
        htmlize_hilighter = g.app.dynaMvar.htmlize_hilighter
    else: htmlize_hilighter = ''

    #if no path set getScript will return empty script, bug <4.3a4
    #must get text other way and do another type of htmlize

    _sysstdsav = sys.__stdout__
    #@    <<header plain footer>>
    #@+node:ekr.20050421093045.67:<<header plain footer>>
    def outheader(fontface= 'Lucida,Courier New'):
        sx = []
        #this will have to get actual encoding but its a start
        meta = ['<meta http-equiv="Content-Type" content="text/html; charset=utf-8">']
        #append anyo ther meta required
        sx.append('<html><head>%s%s<title>'%(EOLN, EOLN.join(meta),))
        sx.append('%s </title>%s'%(sanitize_(titl), EOLN))
    
        #here would be a good spot for @noindent directive but skip a line
        #or build the string in the outermost indentation
        sx.append("""<STYLE TYPE="text/css"><!--
    pre, H1 {color:%s; FONT-SIZE: 80%%; FONT-WEIGHT: bold; }
    Text {background:%s;}
    --></STYLE>
    <SCRIPT LANGUAGE="JavaScript"><!-- 
    //Serenity Right Mouse Click Customisation
    function toggle(e) 
    {  
    if (e.style.display == "none") 
    	{
    	e.style.display = "";
    	 } 
    else 
    	{     
    	e.style.display = "none";  
    	}
    }
    //--></SCRIPT>"""%(
           _colors[_TEXT], _colors['bg'])) #was both #cc9999
    
        sx.append('</head><body text="%s" bgColor="%s">'%(
            _colors[_TEXT], _colors['bg']))
        sx.append('<H3># %s</H3>%s'%(cgi.escape(titl), EOLN,))
        sx.append('<pre>')  # style
        sx.append('<font face="%s, courier">'%(fontface, ))
    
        return EOLN.join(sx)
        
    def plainout(src):
        #g.es('bad or no hilighter language or option=', htmlize_hilighter)
        #return '%s%s%s'%(EOLN, cgi.escape(src), EOLN)
        return '%s%s%s'%(EOLN, src, EOLN)
    
    def outfooter():
        sx = []
        sx.append('</font></pre>')
        sx.append('</body></html>')
        return EOLN.join(sx)
    #@-node:ekr.20050421093045.67:<<header plain footer>>
    #@nl
    try:
        if not source: raise ValueError

        # write colorized version to "python.html"/filename
        if show: 
            sys.stdout = open(hopts['filename'], 'wb')  # wt, wb, w
            g.es('output', p.headString())

        if lang in ['checker', 'report', ]:
            if writehead:
                sys.stdout.write(outheader())
            sys.stdout.write(plainout(source))

        elif lang in ['ishtml', ]:
            sys.stdout.write(source)
            fullhtml = 'y'

        elif lang in ['plain', 'rst', ] or \
              c.currentPosition().headString().strip()[:4] == '@rst':
            g.es('rst or %s , wait...'% lang)
            if writehead:
                sys.stdout.write(outheader())
            #@            << plain or rst >>
            #@+node:ekr.20050421093045.68:<< plain or rst >>
            
            #do a linear node crawl, 
            # htmlize @language nodes
            # append docutils or plain text wrapped output
            #can you want plain or rst and also not stripsentinals?
            #might have to add option or flipper to not follow subnodes
            #thats the theory anyway...  FIXME
            
            #codeblock and latex not supported
            #don't want to reimpliment rst2
            #individual bodys are not getting enough <Br>
            #collect all output and send to docutils once
            #otherwise indexes and content links can't work
            #have to insert some Rest at various points
            
            try:
                import docutils
            except:
                docutils = None
            else:
                #have to investigate custom config files
                #please evolve faster docutils.
                import docutils.parsers.rst
                from docutils.core import Publisher
                from docutils.io import StringOutput, StringInput
                pub = Publisher()
                #@    << define code-block >>
                #@+node:ekr.20050421093045.69:<< define code-block >>
                #silvercity + fallback to code-block
                
                try:
                    import silvercity
                except ImportError:
                    silvercity = None
                
                def code_format(value):
                    html = '<div class="code-block">\n%s\n</div>\n'
                    raw = docutils.nodes.raw('',html%(value, ), format='html') 
                    #(self, rawsource='', text='', *children, **attributes):
                    return raw
                
                def code_block(name,arguments,options,content,lineno,content_offset,block_text,state,state_machine):
                    
                    """Create a code-block directive for docutils.
                    lifted from rst2 and attempt to use 
                    in either src-hilite or silvercity while @language plain
                    or provide own generator if neither active
                    where is it listed which languages are supported?
                    """
                    
                    # See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252170
                    language = arguments[0]
                    if silvercity:
                        module = getattr(SilverCity,language)
                    
                        generator = getattr(module,language+"HTMLGenerator")
                        io = StringIO.StringIO()
                        generator().generate_html(io, EOLN.join(content))
                        code_format(io.getvalue())
                    else:
                        #can I convert to another directive here?
                        raw = ['++ other-directive']
                        raw += [name, arguments, options,]
                        print `raw`
                        raw = code_format(EOLN.join(raw + content))
                
                    return [raw]
                    
                # These are documented at http://docutils.sourceforge.net/spec/howto/rst-directives.html.
                code_block.arguments = (
                    1, # Number of required arguments.
                    0, # Number of optional arguments.
                    0) # True if final argument may contain whitespace.
                
                # A mapping from option name to conversion function.
                code_block.options = {
                    'language' :
                    docutils.parsers.rst.directives.unchanged # Return the text argument, unchanged
                }
                
                code_block.content = 1 # True if content is allowed.
                 
                # Register the directive with docutils.
                docutils.parsers.rst.directives.register_directive('code-block',code_block)
                #@nonl
                #@-node:ekr.20050421093045.69:<< define code-block >>
                #@nl
             
            current = c.currentPosition()
            def outheadline(cur ):
                ''' eventually supply Rest command as well for headline '''
                hl = g.choose(cur.headString().startswith('@rst'), 5, 4)
                return '<H%d>%s</H%d>%s'%(hl, cur.headString(), hl, EOLN )
            
            sys.stdout.write(outheadline(current))
            
            sx = []
            for psib in current.self_and_subtree_iter():
                #sys.stdout.write(outheadline(psib))
                #need to add Rest directive for headline
                sx.append(outheadline(psib))
            
                s = psib.bodyString()
                #.. code-block:: Python
            #@verbatim
                #@ignore
                #need to process some directives
                #dynawrap defaults textwrap or will do Leo wrap
                #have to fixit do it returns rather than prints though
                #also check for @language & few others and highlight
                #so will have to functionalize the highliters eventually
                #also might want some nodes line numbered, 
                #using docutils css on some nodes and on other elements 
                #H3 maybe should include a class=
                #subnodes should be indented? that could cause Rest errors
            
                sx.append(s)
            
            s = EOLN.join(sx)
            #@<< docutil out >>
            #@+node:ekr.20050421093045.70:<< docutil out >>
            #here let docutils have the body, but what about
            #previous Rest commands that might still be active?
            
            # This code snipet has been mangled from code in rst2
            #snipped from code contributed by Paul Paterson 2002-12-05.
            if docutils and s.strip():
                pub.source = StringInput(source=s)
            
                # need to set output so doesn't generate
                #its own footers and headers on every other block
                #nowhere does it mention other options! 
                #docutils docs heal thyself.
                writer='html' ; enc="utf-8"
                #standalone, pep, python
                pub.set_reader('standalone', None, 'restructuredtext')
            
                pub.destination = StringOutput(pub.settings, encoding=enc)
                pub.set_writer(writer)
            
                
                try:
                    output = pub.publish(argv=['--traceback']) #--traceback or ''
                except Exception:
                    #docutils puts errors to stderr, not redirected
                    g.es('ERRORS Found in rstText', psib.headString())
                    output = s
            else:
                #output = s.replace(' ', '&nbsp').replace('\n', '<Br>\n')
                output = s
            
            #till I get more docutil aware
            output = output.replace('<body>','').replace('<html>','')
            output = output.replace('</body>','').replace('</html>','')
            #@nonl
            #@-node:ekr.20050421093045.70:<< docutil out >>
            #@nl
            sys.stdout.write(output)
            #@nonl
            #@-node:ekr.20050421093045.68:<< plain or rst >>
            #@nl

        elif lang == 'python':
            #this may no longer be advantagouus 
            #for every option to do first. and in the same order
            if writehead:
                sys.stdout.write(outheader())
            pars = Parser(source)
            pars.format(None, None)

        else:
            if g.app.dynaMvar.verbosity: g.es('hilight %s , wait...'% lang)
            #should decide somehow if can do the language
            #before commiting to a colorizer
            #plain should always be the fallback instead of first
            #this will get some reflow analisis

            source = stripSentinels(source, **hopts)

            if htmlize_hilighter and htmlize_hilighter != 'silvercity' :
                if writehead:
                    sys.stdout.write(outheader())
                #@                << src-highlight >>
                #@+node:ekr.20050421093045.71:<< src-highlight >>
                #@+at
                # does better job on java than silvercity and has more 
                # languages
                # what no elisp in a gnu language?
                # 
                # need to get the css option without the bloated size
                # which might mean a post processing step.
                # why can't I inject font color default on the command line?
                # 
                # sourceforge.net/sourceforge/gnuwin32/src-highlite-1.11-bin.zip 
                # win32
                # other systems will have to build or find their own
                # 
                # source-highlight -s cpp -f html $*
                # source-highlight -s java -f html $*
                # java, javascript, cpp, prolog, perl, php3, python, ruby, 
                # flex, changelog, lua, caml, sml, log)
                #        keyword blue b ;      for language keywords
                #        type darkgreen ;      for basic types
                #        string red ;          for strings and chars
                #        comment brown i ;     for comments
                #        number purple ;       for literal numbers
                #        preproc darkblue b ;  for preproc directives (e.g. 
                # #include, import)
                #        symbol darkred ;      for simbols (e.g. <, >, +)
                #        function black b;     for function calls and 
                # declarations
                #        cbracket red;         for block brackets (e.g. {, })
                # much nicer than silvercity and it does more langs
                # have to play w/the tags.j2h file for colors
                # not sure about the css option yet from htmlize but the file 
                # will be huge!
                # 
                # 
                # ? -f html  --doc --tags-file="c:\UTIL\DLL\xtags.j2h" %N
                # -v source-highlight 1.11 Trying with... tags.j2h 
                # c:/progra~1/Src-Highlite/share/source-highlight/tags.j2h 
                # C:\UTIL/share/source-highlight/tags.j2h No tags.j2h file, 
                # using defaults ...
                # damm,. what ugly default colors source-highlight has
                # putting tags in $HOME and why don't they check there?
                # 
                # java and javascript are not equilevent
                # there is no jscript or javascript in Leo yet.
                # its turning into more and more of a rats nest.
                # 
                # sml out put for html is in a frame unviewable.
                # not sure what happens if there is no tags file
                #@-at
                #@@c
                
                if lang in [  #leo may not have all of these yet
                       'csharp', 'c', 'c++', 'cpp',
                        'css', 
                      'htm', 'html', #
                        'perlpod', 'perl', 
                        'ruby',
                        'sql',
                        'xml',
                        'xslt',
                        'yaml',
                        'elisp', 'php', 'java', 'rapidq', 'actionscript', 'css',
                    ]:
                    if lang in ['htm', 'html', 
                                    'actionscript', 'css', ]: lang = 'sml'
                
                    elif lang in ['java', 'rapidq',]: lang = 'javascript'
                    elif lang in ['jscript', 'javascript',]: lang = 'javascript'
                    elif lang in ['c', 'c++', 'cpp']: lang = 'cpp'
                    elif lang in ['php', ]: lang = 'php3'
                    elif lang in ['perlpod', 'perl',]: lang = 'perl'
                    elif lang in ['elisp',]: lang = 'perl'
                
                    #little foggy here, options for src-hilite might be different
                    #than any other unknown and so should use hilighter options
                    #but I have no other hilighter in mind yet, so punting.
                    cmd = htmlize_hilighter
                
                    #dont want it to create the file, send to stdout
                    #
                    #
                    #have to account for quoted path with space in them and no comma?
                    params = cmd.split(',')
                
                    if len(params) < 2:  #must be source-highlight
                        params = ' -s %s -f html -T %s %s --tags-file=%s --no-doc '%( #-i %s
                           lang, sanitize_(titl),
                           g.choose(g.app.dynaMvar.verbosity != 0, '-v', ' '), #!''
                            g.os_path_join(g.app.homeDir,'tags.j2h'),
                            #tmpfile,  #source-highlight can accept stdin
                            )  
                    else:
                        #not the best way to handle shell commands, but ok YMMV.
                        params = ' '.join(params[1:])
                
                    if g.app.dynaMvar.verbosity: g.es('running %s \n'% (cmd + params,) )
                    out, err = runcmd(cmd + params, source + EOLN )
                
                else:
                    out = plainout(source)
                #@-node:ekr.20050421093045.71:<< src-highlight >>
                #@nl

            elif htmlize_hilighter == 'silvercity':
                #@                << silvercity >>
                #@+node:ekr.20050421093045.72:<< silvercity >>
                #@+at
                # have to do a multitute of things for this to work
                # sc cant read script so have to write tmpfile
                # can view or redirect and use our viewer caller
                # 
                # default colors in silvercity.css need to be matched to Leo
                #@-at
                #@@c
                
                if lang in [  #leo may not have all of these yet
                       'csharp', 'c', 'c++', 'cpp', # (C and C++)
                        'css', # (Cascading Style Sheets)
                      'htm', 'html', # HTML/PHP w/ JavaScript, VBScript, Python
                        'perlpod', 'perl', # (Perl)
                        #'python', # (Python)
                        'ruby', # (Ruby)
                        'smart_python', # (Python with styled strings)
                        'sql', # (SQL)
                        'xml', # (XML)
                        'xslt', # (XSLT)
                        'yaml', # (YAML)
                        #basic & java? missing. might send java as c?
                        'elisp', 'php', 'java', 'rapidq', 'actionscript', 'css',
                    ]:
                    if lang in ['htm', 'html', 'php', 'java', 'rapidq',
                                    'actionscript', 'css', ]: lang = 'html'
                    elif lang in ['c', 'c++', 'cpp']: lang = 'cpp'
                    elif lang in ['perlpod', 'perl',]: lang = 'perl'
                    elif lang in ['elisp',]: lang = 'perl'
                
                
                    #dont want it to create the file, send to stdin
                    #should btry
                    # won't complain if it isn't the right extension
                    g.es('writeing tmpname', tmpfile )
                    fo = file(tmpfile, 'w')
                    fo.writelines(source + "%s"%EOLN)
                    fo.close()
                    
                    cmd = g.os_path_join(pypath, 'Scripts', 'source2html.py')
                
                    #dont want it to create the file, send to stdout
                    #" --view %N  %N.html"
                    # --css=file copy silver_city.css where the filename will be
                    # source2html.py --list-generators
                    params = ' --generator=%s --title=%s --css=default.css %s'%(
                       lang, sanitize_(titl), tmpfile,)  
                
                    if not g.os_path_exists(cmd):
                        g.es('cant find source2html install silvercity')
                        print 'cant find source2html from silvercity'
                
                    else:
                
                        if g.app.dynaMvar.verbosity:
                            g.es('running silvercity \n', py + cmd + params )
                        out, err = runcmd(py + cmd + params )
                        fullhtml = 'FIXME'
                else:
                    out = plainout(source)
                
                #@-node:ekr.20050421093045.72:<< silvercity >>
                #@nl

            else:
                if writehead:
                    sys.stdout.write(outheader())
                out = plainout(source)
        
            if out and show:
                sys.stdout.write(out)
            if err and g.app.dynaMvar.verbosity: 
                g.es(' ** '.join(err.splitlines()), color='tomato')

        #getmetrics(source)
        #tack on fileinfo as a comment
        #generate linkable index of keywords

        if fullhtml is None: #fix when can get it to do fragments
            if writehead:
                sys.stdout.write(outfooter())

        if show:     
            sys.stdout.close()
            sys.stdout = _sysstdsav #missing from org cgi.
    
        # load HTML page into browser, py2.2?
        if 0 and show:
            #might want this if to use other than default browser
            if os.name == "nt":
                os.system(r'explorer %s'%hopts['filename'])
            else:
                os.system("netscape %s &"%hopts['filename'])
        elif 1 and show:
            import webbrowser
            webbrowser.open(hopts['filename'], new= 0) #

    except ValueError:
        g.es('no @path set, unsupported lang or empty script', 
                color= 'tomato')
        g.es(lang, p.headString())

    except Exception:
        g.es('htmlize malfunction?', color= 'tomato')
        g.es_exception(full= True)

    sys.stdout = _sysstdsav #twice is nice
    return out
#@nonl
#@-node:ekr.20050421093045.59: htmlize
#@+node:ekr.20050421093045.73:restoreStd
def dynaZ_restoreStd(c):
    """(c) 
    every now and again run this if prints are blocked"""
    import leoGlobals as g
    print "stdout isRedirected:", g.stdOutIsRedirected()
    print "stderr isRedirected:", g.stdErrIsRedirected()
    g.redirectStderr()
    g.redirectStdout()

    g.restoreStdout()
    g.restoreStderr()
#@-node:ekr.20050421093045.73:restoreStd
#@+node:ekr.20050421093045.74:del first n char
def dynaZ_del_first_char(c):
    """(c) selected text print/paste
    del first char in the line
    abstracted everything get/insert related to dynaput
    del_2nd_char would occasionally be usefuil

    applying the logical reverse, what about an add first char?
    might use that to comment out a section of code
    always remembering to have something selected & copyed could get to be a pain
    decided best to have that in another macro, using dynaplayer
    could defl 2 at a time, but make one at a time changes 
    so you could undo one if you only want one. usually its 4 for me anyway.

    """
    newSel = dynaput(c, [])
    if not newSel: return
    
    try:
        newSel = str(newSel)
    except (UnicodeEncodeError, Exception):
        g.es_exception(full= False)


    sx = []
    for x in newSel.splitlines():
        sx.append(x[1:] + EOLN )

    dynaput(c, sx)
#@-node:ekr.20050421093045.74:del first n char
#@-node:ekr.20050421093045.50:pre/post macros
#@+node:ekr.20050421093045.75:cascade actions
#these get cascades and act on selected text and can print or paste
#choice of action is sometimes from the copybuffer too

#add one for Clip, to call a macro and tell it to work from the clipboard
#print or paste to the clipboard
#@nonl
#@+node:ekr.20050421093045.76:+DQ3
def dynax_DQ3(c, repchar='Do', source= None):
    r'''(c) selected text print/paste
    has its own cascade in dyna menu and the choices act directly.
    or you choose DQ3 to use what is in the clipboard as a pair.
    
    enclose the selected txt in  whatever is in the copy buffer 
    gets put before and the matching after
    if '(' is in the copy then (selected) is put/
    (:) {:} [:] <!--:--> /*:*/  <:>
    currently no match if space before or after pair, but hope to fix that.
    
    special pairs.
    try/except  if/else >>>/...

     chose SQ, DQ DQ3 SQ3 SHow Pairs
    is there a DQ2 SQ2?
    used for commenting out sections of code or to create docstrings

    have to have something selected to insert anything even an empty.
    if nothing selected put a blank docstring.
    its not easy to have an empty copy buffer with the present Tk,
     copy or cut with nothing selected. no change takes place.
  ~EOT  does 'is None' work in py2.2?

    >>> dynax_DQ3(None, repchar='/*', source='\\n ')
    ['/*\\n */']
    >>> #
    #Leo expands \n from inside name section . this makes \n in return tricky
    #and rawstring makes it more counterintuitive but possible

    #@    <<doctest>>
    #@+node:ekr.20050421093045.77:<<doctest>>
    >> dynax_DQ3(None, repchar='Do', source="#")  #w/nothing selected
    ['#']
    
    >>> dynax_DQ3(None, repchar='Show ', source='')  #rmv spc to retest Show
    ['"""\n"""']
    >>> dynax_DQ3(None, repchar='/*', source="""\n """)  #Leo expands \n see in DQ3
    ['/*\n */']
    >>> dynax_DQ3(None, repchar='>', source='hey')
    ['<hey>']
    >>> dynax_DQ3(None, repchar='-->', source='hey')
    ['<!--hey-->']
    >>> dynax_DQ3(None, repchar='<!-- ', source='hey')  #make this work any +-spc+-
    ['<!-- hey<!-- ']
    >>> dynax_DQ3(None, repchar='try', source='  goto 34')
    ['\n  try:\n     goto 34\n  except Exception:\n   g.es_exception(full= True)\n']
    >>> dynax_DQ3(None, repchar='if', source='  goto 3\n  pass\n') #multiline
    ['\n  if 1 == 1:\n     goto 3\n     pass\n\n  else:\n   pass\n']
    >>> dynax_DQ3(None, repchar='if', source='  goto 34') #space
    ['\n  if 1 == 1:\n     goto 34\n  else:\n   pass\n']
    >>> dynax_DQ3(None, repchar='if', source='goto 34') #nospace
    ['\n    if 1 == 1:\n        goto 34\n    else:\n        pass\n']
    >>> dynax_DQ3(None, repchar='>>>', source=' goto 34')
    ['\n >>>   goto 34\n   ...\n']
    >>> #
    #@nonl
    #@-node:ekr.20050421093045.77:<<doctest>>
    #@nl

    might be usefull to backtrack to the previous line, insert enter
    that will put the insertpoint on the right indent
    maybe too much magic though
    add reverse dict to allow selection of either start or end char
    add try/except if/else
    subfunction the replace so can add doctest to it. same elsewhere.
    
    need to allow any space before or after the typical repchars
    and to use similar space before and then no extra space before the afterchar?
    might even make sense to force space after and before double comments
    added a Show pairs option

   repchar = g.app.gui.getTextFromClipboard()
 UnboundLocalError: local variable 'g' referenced before assignment
 why didn't I need an import as g before?
 could have a mode where only the begining or end of the line was added to.
 could have a line by line for that mode and normal mode begin/end each line.

    '''
    import leoGlobals as g  #if __name__ == 'mymod': du_test

    if source is None:
        newSel = dynaput(c, [])
    else:
        newSel = source

    #print '%r'%newSel
    if not newSel: 
        data = '\n'
    else:
        try:
            data = str(newSel)
        except Exception:
            pass

    repdict = {'(':')', '{':'}', '[':']', '<!--':'-->', '/*':'*/', '<':'>'}
    #get cute and use a reverse dict if repchar in .values()
    revdict = dict([[v, k] for k, v in repdict.items()])

    #add some specialized sourounders, need to add to choice menu in putmenu
    repdict.update({'try':'except', 'if':'else', '>>>':'...',})
    
    #could also use a method if # or //, then put at front of every line
    # could have a given repchar to signal get comment from @language dbl/sng
    #what if 2 anglebrackets, should 2 reverse angles be trailing?
    
    if repchar == 'Show':
        #import pprint
        #g.es( pprint.pprint(repdict), color= 'sienna3') 
        #pprint needs redirect, but how did doctest capture it?
        g.es( 'DQ3 pairs\n', repdict, color= 'sienna3')
        return


    #need something to reselect wtith the newsel inserted in case it was empty
    #in circular logic land

    if repchar == 'Do': #was hard to pass in '' from DQ3 menu
        repchar = g.app.gui.getTextFromClipboard()

    if not repchar or not newSel:
        repchar = '"""'

    if repchar in repdict.keys():
        rep2char = repdict[repchar]

    elif repchar in revdict.keys():
        #allow user to copy or either start or end char
        #output will be in the correct order of the pair
        repchar = revdict[repchar]
        rep2char = repdict[repchar]

    else: rep2char = repchar  #rep2char.reverse()?
 
    #@    << tripleline >>
    #@+node:ekr.20050421093045.78:<< tripleline >>
    def tripleline(r1, s, r2, extra1='', extra2=''):
        """
        need to extract the leading space from data and match it
        #will tabs get converted to space? probably not
        #not ideal but should get you close enough
        >>> tripleline('r1', 's', 'r2', extra1='e1', extra2='e2')
        '\\n    r1e1        s\\n    r2        e2'
        """
        spcs = g.skip_ws(s, 0)
        if not spcs: 
            spc = '    '
            spcs = 1
        else: 
            spc = s[0]
    
        sz = '\n%s%s%s'%(spcs*spc, r1, extra1, )
    
        for xz in s.splitlines(True):
            sz += '%s%s%s'%(spcs*spc, spc, xz,)
    
        sz += '\n%s%s'%(spcs*spc, r2,)
    
    
        sz += '%s%s'%(
                spcs*spc+spc, extra2,)
        
        return sz
    #@nonl
    #@-node:ekr.20050421093045.78:<< tripleline >>
    #@nl
    sx = []
    #   these may messup because they don't force proper indent
    #  for language another than python obviously you would need more
    #potential to read pairs and code to impliment them from ini?
    if repchar == 'try':
        sx.append(tripleline(
            repchar+':\n', data, rep2char+' Exception:\n',
                '', 'g.es_exception(full= True)\n'))

    elif repchar == 'if':
        sx.append(tripleline(
                repchar, data, rep2char+':\n',
                 ' 1 == 1:\n', 'pass\n'))

    elif repchar == '>>>':
        sx.append(tripleline(
                repchar, data, '',
                 '', rep2char+'\n'))
    else:
        sx.append('%s%s%s'%(repchar, data, rep2char))
        
    if source is None: 
        dynaput(c, sx)
        return
    else:
        return sx
    if not newSel: g.es(''.join(sx) ) #life is too short
#@nonl
#@-node:ekr.20050421093045.76:+DQ3
#@+node:ekr.20050421093045.79:_actions
def dynax_actions(c, act='lower', script= None):
    r"""(c= None, action) select text print/paste
    action def for macroless action on text or selected text 
    current actions are lowercase uppercase caps and reverse all the lines
    
    caps could easily only cap only the first of a line or of a sentance.
    I have no idea what reverse might be used for.
    rot13 is insecure, b64 as well but its your data.
    ~EOT   need dynatester for this one
     make a few slight transparent changes so can doctest it
     have to recheck in py2.2 because strings aren't iterable there
     py2.3 complains about strict in b64 py2,2 has neither b64 or ror13?

     why did I not see a tuple returned yesterday?
     py2.4 you can just a = codex.encoder and it worked
     going to have to reimpliment unokunebts si ut keaves off b64
     untill I can get the syntax correct
     have to use base64 module in less than py2.4
     and rot13.py in less than py2.3
     
   #@   <<doctest>>
   #@+node:ekr.20050421093045.80:<<doctest>>
   >>> dynax_actions(c,act='lower', script='testO@#\n45SIX')
   ['testo@#\n', '45six']
   >>> dynax_actions(c,act='uppeS', script='testO@#\n45SIX')
   ['testO@#\n', '45SIX']
   >>> dynax_actions(c,act='reverse', script='testO@#\n45SIX')
   ['XIS54', '\n#@Otset']
   >>> dynax_actions(c,act='caps', script='test !@#$ 123@#\nlist of things')
   ['Test !@#$ 123@#\n', 'List Of Things']
   >>> dynax_actions(c,act='>base64', script='another-fun-toy\n\n')#-ly y'rs
   ['YW5vdGhlci1mdW4tdG95Cgo=\n']
   >>> dynax_actions(c,act='<base64', script='YW5vdGhlci1mdW4tdG95\n\n')
   ['another-fun-toy']
   >>> dynax_actions(c,act='>rot13', script="Hello World !\n")
   ['Uryyb Jbeyq !\n']
   >>> dynax_actions(c,act='<rot13', script='Uryyb Jbeyq !\n\n')
   [u'Hello World !\n\n']
   >>> dynax_actions(c,act='>hex', script='test\n')
   ['746573740a']
   >>> dynax_actions(c,act='<hex', script='746573740a')
   ['test\n']
   >>> dynax_actions(c,act='>md5', script='neato')
   ['9c53098eeab0c2457972453bae3248ff']
   >>> #
   #@nonl
   #@-node:ekr.20050421093045.80:<<doctest>>
   #@nl
    
    """
    from dynacommon import EOLN
    import leoGlobals as g
    #this may cause trouble later pep245 
    _impliments__ = 'reverse upper lower caps base64 rot13'

    if script is None:
        newSel = dynaput(c, [])
    else: newSel = script
    
    if not newSel: return

    if act == 'reverse':
        sx = []
        for x in newSel.splitlines(True):
            x = list(iter(x))
            x.reverse()
            sx.append(''.join(x))
        sx.reverse()
    elif act == 'lower':
        #lower or upper or some normal string operation
        #x.act() isn't working like I hoped it would
        #maybe need str.lower  print dir('')
        sx = [x.lower() for x in newSel.splitlines(True)]

    elif act == 'upper':
        sx = [x.upper() for x in newSel.splitlines(True)]

    elif act[1:] == 'md5':
        import md5
        if act[0] == '>': #encode
            sx = [md5.md5(x).hexdigest() for x in newSel.splitlines(True)]
        else:
            #you can supply your own algo for here...
            pass
    elif act[1:] in ['rot13', 'base64', 'hex']:
        #@        << codecs.lookup >>
        #@+node:ekr.20050421093045.81:<< codecs.lookup >>
        import codecs
        #could possibly say actor = '',decode?
        #should just import base64 for all
        ac = None
        
        if act[0] == '>': #encode
            try:
                actor = codecs.lookup(act[1:])[0]
                #actor = codecs.getencoder(act[1:])
                #actor = g.toEncodedString
            except LookupError:
                if act[1:] == 'base64':
                    try:
                        ac = __import__(act[1:])
                        ac.encodestring
                    except (Exception, ImportError):
                        g.es_exception(full= True)
                        return
                elif act[1:] == 'rot13':
                    try:
                        ac = __import__('rotor')
                        ac.encodestring
                        rt = ac.newrotor(s, 12) 
                        actor = rt.encrypt
                        ac = None
                    except (Exception, ImportError):
                        g.es_exception(full= True)
                        return
                else:
                    return
        
        elif act[0] == '<': #decoder
            try:
                if ac is None: #decoder
                    #actor = codecs.lookup(act[1:])[1]
                    #actor = g.toUnicode  #
                    actor = codecs.getdecoder(act[1:])
                else:
                    actor = ac.decodestring
        
            except (Exception, LookupError):
            
                if act == '<rot13':
                    g.es('try import rotor')
                    return
                g.es_exception(full= True)
                return
        try:
            if ac is None:
                s = actor(newSel)
            else:
                s = actor(newSel, act[1:])
            #can they possibily be serious sometimes returning tuple?
            if isinstance(s, tuple):
                #g.es('converted chars %s only %s'%(len(newSel), s[1]))
                s = s[0]
        
        except (Exception, LookupError, AssertionError):
            #g.es_exception(full= True)
            return
        
        sx = [s]
        #@nonl
        #@-node:ekr.20050421093045.81:<< codecs.lookup >>
        #@nl
    elif act == 'caps':
        sx = [' '.join([y.capitalize() for y in x.split(' ')])\
             for x in newSel.splitlines(True)]
    else:
        return script.splitlines(True)

    if script is None:
        dynaput(c, sx)
    return sx
#@nonl
#@-node:ekr.20050421093045.79:_actions
#@+node:ekr.20050421093045.82:_backslashs
def dynax_slashs(c, repchar='Do'):
    """(c) print/paste
    create a file monicur out of a path for IE or NS4
    it has its own cascade in dyna menu and the choices act directly.
    @url file://some.bat will work, not sure with %20 can add params
    or chg forward or backslash to the other. add "'s or %20 for spaces
    r04212p7:05 whiped up out of my head in few mins
    some editors can't handle path with forwardslashes, most can.
    dblclick on @url might not open IE for some reason but doesn't error.
    it might even be simpler to force a translation from one to the other
    as is you might have to transition thru several stops to get there.
    best use case is from \\ to /. or from either to file:/// so it is.
  ~EOT
    u04509p08:56 cvrt to dyna, somehow need to select which...
    using copy buffer or just flip b\/f slashes
    should add 8.3 to longfilename and back
    dblbs isn't working, it want to flip bs/fs if they exist whatever else
    should probably just output the path in every way possible
    folowed by space delimited words make into valid get url
    backslash doesn't seem to flip back from slash again
    """
    newSel = dynaput(c, [])
    if not newSel: return
    newSel = str(newSel)

    if repchar == 'Do': #
        repchar = g.app.gui.getTextFromClipboard()

    if not repchar in ['/', '\\' '\\\\', ':', '|', ' ',]:
        #if nothing in copy buffer flip the back/forward slashes
        if newSel.find('/') != -1:
            repchar = '\\'
        elif newSel.find('\\') != -1:
            repchar = '/'
        elif newSel.find('~') != -1:  #could be 8.3 also
            repchar = ':'
        
    sx = []
    for x in newSel.splitlines(True):
    
        if x == '': continue
    
        #check is valid, starts with drive : and has no non printables
    
        if repchar == ':':
            s =  x.replace('\\\\','\\').replace('\\','/').replace(':','|') 
            s = s.replace(' ','%20')
            sx.append('file:///' + s)
        elif repchar == '|':
            s = x.replace('file:///','').replace('|',':').replace('/','\\') 
            s = s.replace('%20',' ')
            sx.append(s)
    
        elif repchar == '\\\\':
            sx.append(x.replace('/','\\').replace('\\','\\\\') )
    
        elif repchar == '\\':
            sx.append(x.replace('/','\\') )
    
        elif repchar == '/':
            sx.append(x.replace('\\\\','\\').replace('\\','/') )
    
        elif repchar == ' ':
            sx.append(x.replace(' ','%20') )

        else:
            #sx.append(' " ",/,\\,:, %s'%(x,) )
            g.es(' err', x)
        
        g.es(' repchar= %r x=%r'%(repchar,x) )
        dynaput(c, sx)
#@-node:ekr.20050421093045.82:_backslashs
#@-node:ekr.20050421093045.75:cascade actions
#@-node:ekr.20050421093045.6:macros
#@+node:ekr.20050421093045.83:config
#for the plugin manager using the ini
#some of these should be dyna menu items anyway in case no plugin_menu
#calling them prototypes for now. so many switches so little time
#maybe can have some to flip styles & colors for htmlize
#later add @settings compatible options 

#would be nice to find out how to assign a keyboard shortcut to dupe
#and a few others
#at this point maybe I could try a default bind?
#need a macro to look thru Leo config and see which key combos are free
#@nonl
#@+node:ekr.20050421093045.84:flipvers
#@+node:ekr.20050421093045.85:cmd_flipverbosity
def cmd_flip_du_test_verbosity(): 
    """in some macros overall feeback on some operations.
    for @test nodes. 
    you still get traceback on syntax and other errors with just dots ==1
     ==2 is verbosity in unittest @test and @suite. slightly different
     either 1 or 2 is verbose for doctest and 0 is nothing except errors reported.
  ~EOT  requires change in leoTest, (added Leo4.3a2 no objections)
    
    validating config options hasn't been implimented yet either
    can I call a more general flipper for other vars too?
    can there be a cascade of flip vars in plugin_menu?
    """
    g.app.dynaMvar.verbosity += 1
    # is 1 or 0? True or False not sure 2.2 even has this option too?
    #this, like debug,  should increment in a connected range 0..3
    g.app.dynaMvar.verbosity = g.choose(
        g.app.dynaMvar.verbosity >= 3, 0, g.app.dynaMvar.verbosity)
    g.es('now is', g.app.dynaMvar.verbosity)
#@nonl
#@-node:ekr.20050421093045.85:cmd_flipverbosity
#@+node:ekr.20050421093045.86:cmd_flipLeo_debug
def cmd_flip_Leo_debug(): 
    """0,1,2,3 for Leo debug switch
    careful, 3 starts pdb which has some unpredictable results
    maybe it should start rpdb or the debugger of your choice
    and in a seperate thread and in its own window.
    with no console open on windows this could hang Leo?
    no place even to type control C to signal a break.
    """
    g.app.debugSwitch += 1
    g.app.debugSwitch = g.choose(
        g.app.debugSwitch >= 4, 0, g.app.debugSwitch)

    g.es('debugSwitch now is', g.app.debugSwitch)
    if g.app.debugSwitch >= 2: g.es('pdb is now active on errors', color='tomato')
#@nonl
#@-node:ekr.20050421093045.86:cmd_flipLeo_debug
#@+node:ekr.20050421093045.87:cmd_flipjustPyChecker
def cmd_flip_justPyChecker(): 
    """for tim1crunch makeatemp and pylint.
    1 is don't print source after running the check.
    """
    g.app.dynaMvar.justpychecker = g.choose(
        g.app.dynaMvar.justpychecker != 0, 0, 1)
    g.es('now is', g.app.dynaMvar.justpychecker)
#@nonl
#@-node:ekr.20050421093045.87:cmd_flipjustPyChecker
#@+node:ekr.20050421093045.88:flip_onoff_c_gotoline
def cmd_flip_onoff_c_gotoline(c): 
    """this totally violates the goto feature in executeScript
    presently broken if called from selected text.
      unselects the text and goes to the line in the full script.
    broken if error happens in another module
    and you are working in a subnode from a scriptButton
    you probably don't want to goto the top of the script.
      you might not even want or need to see the error
      by then its all too painful what the problem is
      the traceback is just a reminder it isn't fixed yet.
    this solves the one thing. 
    
    subsequent calls turn goto back on or off
    for those vanishingly fewer and fewer times when goto is wrong.
    mean time, take no prisoners. this works today.
  ~EOT   no one wants to see the error wrongly reported ever.
    the other thing is a problem with exec and python and tracebacks.
    compiling the script first would get you a better filename than <SCRIPT>
    but showing exec and leoCommands as part of the problem isn't helpful,
    to old and new alike. grin and bear it I guess.
    
    and why do I need to know Leo knows this:  
     'No ancestor @file node: using script line numbers'
    when gotolinenumber from Edit menu? (no problem if flipped off)

    no idea if c.goToLineNumber called from other scripts 
    or parts of Leo or other leos' will be adversely impacted if off.
    
    of course a config setting or option to turn off goto,
    option to turn off show error in context, would be better.
    """

    import leoGlobals as g
    atribs = cmd_flip_onoff_c_gotoline

    if hasattr(atribs, 'flip'):
        atribs.flip = not atribs.flip
    else:
        atribs.gotolinesave = c.goToLineNumber
        atribs.flip = True

    if atribs.flip:
        def dummygotoline(n, *a, **k):
            'goto is fliped off'
            pass
        c.goToLineNumber = dummygotoline
        g.es('turning off goToLineNumber', color= 'purple')
    else:
        c.goToLineNumber = atribs.gotolinesave
        g.es('turning on goToLineNumber', color= 'purple')

#@-node:ekr.20050421093045.88:flip_onoff_c_gotoline
#@-node:ekr.20050421093045.84:flipvers
#@+node:ekr.20050421093045.89:cmd_SetAsDefault
def cmd_SetAsDefault(): 
    """
    set default would be too hard, 
    no interest in maintaing seperate per leo defaults.
    """
    #g.alert('no ini, check back in 5 minutes')
    #getConfiguration(rw= 'w') #force write
    g.es('no change at this time')
    
#@-node:ekr.20050421093045.89:cmd_SetAsDefault
#@+node:ekr.20050421093045.90:cmd_ShowDefaults
def cmd_ShowDefault(): 
    """
    no need to show all the defaults actually, just user configurables
    shoud show hopts also and make a function so can have the intersection
    with the ini overriding hardwired default values. maybe next time.
    """
    g.es(g.app.dynaMvar)
#@-node:ekr.20050421093045.90:cmd_ShowDefaults
#@+node:ekr.20050421093045.91:@ test _Configuration
#there may be a problem with @test and others, I forget why
#that is annoying because I don't want to import to get access. may have to

#  getConfiguration
#  applyConfiguration
# test_Configuration(): 
import ConfigParser
#@+others
#@+node:ekr.20050421093045.92:getConfiguration
def getConfiguration(fileName): 
    """Return the config object
    should this look in homeDir first then plugins?   
    check __file__ works in py2.2 and under test.leo of plugin 

     Default values can be specified by passing them into the
     ConfigParser constructor as a dictionary. Additional
     defaults may be passed into the get() method which will
     override all others.

    maybe any @settings starting with the plugin name
    could be added to the config dictionary
     g.os_path_split(__file__)[1][:-3]+".ini" fails on XP
    """ 

    #if ini doesn't exist, should we create it?

    #g.trace(fileName)
    config = ConfigParser.ConfigParser() 
    config.read(fileName) 
    return config 
#@nonl
#@-node:ekr.20050421093045.92:getConfiguration
#@+node:ekr.20050421093045.93:applyConfiguration
def applyConfiguration(config):
    """plugin menu calls this after ini edit 
    and on first menu creation or first dyna click if I can swing it.
    
    True/False config saves as string? seems to work ok though
    also if non existant will be error, have to trap
    so default written in plugin can override if no attribute
    or attribute contains nonsense or whole ini or section doesn't exist.
    this addhockism has to go, 
    the ini format is 20 years old an im winging it here again.
    is it lowercasing items but not section names? what about values?
    seems to preserve case now, but decided better if dumenu doesn't
    this way lies maddness to debug otherwise. not everyone is a coder.

    another way to look at it is:
        if you don't want no errors, don't make any mistakes.
    all required options are hardwired defaulted 
    and should be ok if ini is wrong or missing
    
    """
    if not config: 
        config = getConfiguration(
            g.os_path_join(g.app.loadDir,"..","plugins", "dyna_menu.ini"))
    badini = ''
    dyna = g.app.dynaMvar
    #@    << anint(x) >>
    #@+node:ekr.20050421093045.94:<< anint(x) >>
    def anint(x):
        """
        >>> [anint(x) for x in ('t', 'False', 2, 4, '5', 'n', '/')]
        [1, 0, 2, 4, 5, 1, 0]
        """
        try:  
            i = int(x)
        except ValueError:
            if x.lower() in ['true', 't', 'on', 'n', 'y', 'yes',]:
                i = 1
            elif x.lower() in ['false', 'f', 'off', '', 'no',]:
                i = 0
            else:
                i = 0
        return i
    #@nonl
    #@-node:ekr.20050421093045.94:<< anint(x) >>
    #@nl

    #should warn if no section header found?
    #not even sure all of these are properly guarded
    #if not appearing in the ini.

    sections = [] 
    if config.has_section('main'):
        sections += ['main'] 
    if config.has_section('htmlize'):
        sections += ['htmlize'] 

    if not hasattr(config, 'items'): #py22
        config.items = config.options

    items = g.flattenList([config.items(x) for x in sections])
    #g.es(items)

    for x in items:
        xl = x[0].lower()

        #still needs a little something
        #some of these would be better if anint defaulted 2 or 1 or 0
        #some should be defined even if nothing in ini or @settings
        if xl in ('tabstrip', 'verbosity', 'justpychecker', 'bugimport', ):
            setattr(dyna, xl, anint(x[1]))

        elif xl in ('filename', ):
            setattr(dyna, xl, x[1])


    if 'htmlize' not in sections: 
        return

    lx = """\
        hilighter timestring
        codefold stripcomments stripsentinals
        stripnodesents stripdirectives 
        noNAME noOP noNUMBER

        token_NUMBER      token_OP
        token_STRING      token_COMMENT
        token_NAME        token_ERRORTOKEN
        token_KEYWORD     token_TEXT
        token_LeoDir      token_LeoSen
        token_bg""".replace('\n',' ').split()

    #g.es(lx)
    for xini in [xl.strip().lower() for xl in lx]:
        x = 'bad'

        try:
            #this actually needs another step to be caseinsensitive
            #but well leave it to FIXME later as above was done
            x = config.get('htmlize', xini).lower()

        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError, Exception):
            #g.trace('not found', xini, x)
            badini += '.'
            continue

        #no attribute or sometimes default means let dyna handle it
        if not x or x == 'bad': 
            #g.trace('not xImped', xini, x)
            badini += '.'
            continue

        elif xini.startswith('token_') or\
             xini in ('timestring', 'hilighter',): 
            #maybe validate is proper hex and has # or good color name
            #or whatever the user wants the user gets in this case
            xval = x

        #getboolean might work for these few
        #do people say y for yes but never n for no while I use n=on and f=off
        elif ('%s'%(x, )).strip().lower() in (
                'true', '1', 'on', 'n', 't', 'y', 'yes'):
            xval = True
        elif ('%s'%(x, )).strip().lower() in (
                'false', '0', 'off', 'f', '', 'no'): 
            xval = False

        else: 
            #must be user mispelling
            g.es('dyna ini not recognized', xini, x)
            badini += '.'
            continue

        setattr(dyna, 'htmlize_'+xini, xval)

    
    #might want to write the unnamed options commented out?
    #g.es(config.items('htmlize'))

    #g.es('current dyna configized w/%s defaulted values'% len(badini))
    #cmd_ShowDefault()
#@nonl
#@-node:ekr.20050421093045.93:applyConfiguration
#@-others

#@+at
# if __name__ == '__builtin__':
#     #from dynacommon import *
#     print 'should only see this from test'
#     g.es('should only see this from test2')
#     import leoGlobals as g
#     import ConfigParser
#     g.app.unitTesting = True
#@-at
#@@c

def atest_Configuration(): 
    """ pack a config and see how apply applys it to a Mvar
    not ready to test
    just calling each macro would better check syntax errors 
    """ 
    
    #why does Bunch not have a deepcopy method?
    dynasve = g.app.dynaMvar.__dict__.copy()
    
    #otherwise you bork the current dyna
    dyna = g.app.dynaMvar = g.Bunch(nothing=0)

    try:
        print dyna
        print dynasve

        if g.app.unitTesting: 
            __file__ = 'dyna_menu.py'
    
        #permuter needed with all none and either section and use real defaults
        #some have to be defaulted and make sure the ini can't override them
        
        #how to build a config compatible dictionary?
        td = {'main':{'var1':1, 'var2':'2',}, 'htmlize':{}}
        #config = ConfigParser.ConfigParser(td)  #

        config = getConfiguration(
            g.os_path_join(g.app.loadDir,"..","plugins", "dyna_menu.ini"))
    
        if hasattr(config, 'items'): #
            #need something to iterate sections as well as items
            print config.items('main')
        
        applyConfiguration(config)
        
        #compare this config with getconfig and do in try/except
        #need to not screwup some existing dyba vars as well as add new ones
        #create and initilize and @settings not and rerun etc etc
        print dyna

    finally:    
        g.app.dynaMvar = dynasve.__dict__.copy()
    g.es(g.app.dynaMvar)
    
    return
    #does this need an element by element comparison?
    return g.es(liba != libc)
    
#@+at 
#@nonl
# comment this out to test with g.app.unitTesting
# if __name__ == '__builtin__':
#     #@test based on assert fails if python -O, -OO
#     assert test_Configuration() is not None
#@-at
#@nonl
#@-node:ekr.20050421093045.91:@ test _Configuration
#@-node:ekr.20050421093045.83:config
#@+node:ekr.20050421093045.95:load_menu

#no user code besides cascade names tuple

def load_menu (tag,keywords):
    global dynaMvar

    c = keywords.get("c")
    cf = c.frame

    if dynaMvar is None:
        dynaMvar = g.app.dynaMvar = init_dyna(c)

        #maybe pospone ini read further, till first time dyna is clicked?
        if not hasattr(g.app.dynaMvar,'htmlize_filename'):
            dynaMvar.htmlize_filename = 'default'
            #initfilenames()
            applyConfiguration(None)
            quietwarnings()

    #@    << togprpa >>
    #@+node:ekr.20050421093045.96:<< togprpa >>
    def togprpa(cf= cf, *a):
        """called from the menu to set status and Flag
        """
        def doprpa(*a):
            if 'print' == dynaMvar.dynapasteFlag.get():
                dynaMvar.dynapasteFlag.set('print') 
            elif 'paste' == dynaMvar.dynapasteFlag.get():
                dynaMvar.dynapasteFlag.set('paste') 
            elif 'doc' == dynaMvar.dynapasteFlag.get():
                dynaMvar.dynapasteFlag.set('doc') 
    
            cf.clearStatusLine()
            cf.putStatusLine("dynamenu " + dynaMvar.dynapasteFlag.get())
    
        return doprpa
    #@nonl
    #@-node:ekr.20050421093045.96:<< togprpa >>
    #@nl
    casnamtup = (
        'infos', #B   clipdtef, linenumber
        'mod text', #M
        'codeing', #S

        'pre/post', #A:y restoreST, htmlize,
        'zzzzz', #never gets here don't use past Z as a sentinal
    )

    table = [] #first table is built then some items use .add

    #need to option the menu names and expose a list of all menu text
    nu = dynaMvar.dynasMenu = c.frame.menu.createNewMenu("D&yna","top")


    #eventually build some entries outside submenus
    #maybe the first and last letter save for this reason A:z
    #then work from copy lst with those items subtracted
    lst = dynaMvar.dynadeflst [:]
    lst.reverse() #makes no sense but we do it anyway.

    #you change the macro order you assume full responsinility
    #this could be fragile if you use less macros than are standard
    #know B_clipdtef is the first one add B_linenumber now B_help
    #picks the one to appear on main menu from the infos cascade
    #-4 currently is help sorted z..a
    try:
        table.append(
            (lst[menudefault][6:],None,
                lambda c = c, f = globals() [lst [menudefault]]: f(c)))
    except Exception:
        pass

    #@    << add items >>
    #@+node:ekr.20050421093045.97:<< add items >>
    #there better be at least one macro in lst and one cas entry
    a = 0
    ch = dynaMvar.dynadeflst [0] [4]
    subtable = []
    sub = None
    #dynaMvar.dynadeflst.append('dynaz_') #add break sentinal
    
    #the way Leo menu add works is 
    #A. similar to Tk, B. incomprehensable C. it just "works"
    #and why is submenu text  smaller? and how can't I change it.
    #submenus seem to get sorted? forced to the top at some point.
    
    #add items till the 5th char changes, then get next subname
    #does not always degrade gracefully if you go out of bounds
    for s in dynaMvar.dynadeflst:
    
        if s.startswith('dynax_'): continue
    
        if s [4] != ch or sub is None:
            #g.es('a=', a, 's=', s, `subtable`, color= 'orange')
            if sub:
                c.frame.menu.createMenuEntries(sub,subtable,dynamicMenu=True)
                subtable = []
                a += 1 #yada yada test end of cas
                ch = s [4]
            if s [4] >= 'Z': break
            sub = c.frame.menu.createNewMenu(casnamtup[a],"dyna") #nu
    
        subtable.append(
            (s[6:],None,lambda c=c,f=globals()[s]: f(c)))
    
        lst.pop() #quick if not efficent
    
    #append z entries, see above and below above
    for s in lst:
        if s.startswith('dynax_'): continue #actions get cascades
        table.append(
            (s[6:],None,lambda c=c,f=globals()[s]: f(c)))
    #@-node:ekr.20050421093045.97:<< add items >>
    #@nl

    #nu.add_separator()  #gets out of synch w/table here
    table.append(('-',None,None))

    c.frame.menu.createMenuEntries(nu,table,dynamicMenu=True)

    dynaMvar.dynapasteFlag.set('print')

    nu.add_radiobutton(label='print',
            variable = dynaMvar.dynapasteFlag,
            command = togprpa(cf=cf))
    nu.add_radiobutton(label='paste',
            variable = dynaMvar.dynapasteFlag,
            command = togprpa(cf=cf))
    nu.add_radiobutton(label='doc',
            variable = dynaMvar.dynapasteFlag,
            command = togprpa(cf=cf))

    #@    << action >>
    #@+node:ekr.20050421093045.98:<< action >>
    #create a cascade and act on the actions presented
    #why is the PMW error handler catching error in here
    # and not Leo redirected to log?
    
    #@+others
    #@+node:ekr.20050421093045.99:actions
    dynai = Tk.Menu(None, tearoff= 0, takefocus= 0 )
    
    #for x in dynax_actions._impliments__.split(): dwim
    for x in 'lower upper reverse caps <base64  >base64 <rot13 >rot13 >hex <hex >md5'.split():
        dynai.add_command(label= x, 
              command= lambda x= x, c= c: dynax_actions(c, x) ) 
    
    nu.add_cascade(menu= dynai, label= 'actions' )
    #@nonl
    #@-node:ekr.20050421093045.99:actions
    #@+node:ekr.20050421093045.100:_backslashs
    dynai = Tk.Menu(None, tearoff= 0, takefocus= 0 )
    for x in  'Do bs, : file, | !file, \\\\ Dbs'.split(', '):
        dynai.add_command(label= x, 
              command= lambda c= c, r= x.split()[0]:  dynax_slashs(c, r) ) 
    
    nu.add_cascade(menu= dynai, label= 'slashs' )
    #@nonl
    #@-node:ekr.20050421093045.100:_backslashs
    #@+node:ekr.20050421093045.101:show clip
    #show whats in the clipboard, replace clipboard with left side of pair
    #this isn't dynamically updated each menu invocation in plugin
    #nu.add_command(label= "Clip=%r"%(
    #            g.app.gui.getTextFromClipboard()[:6],), )
    #changing to direct action instead of add choice to clipboard
    
    dynai = Tk.Menu(None, tearoff= 0, takefocus= 0 )
    for x in  'Do DQ3, \' Sq, " Dq, \'\'\' Sq3, """ Dq3, ( ), { }, [  ], /* */, <!-- -->, try /ex, if /else, >>> /..., Show Pairs'.split(', '):
        dynai.add_command(label= x, 
              command= lambda c= c, r= x.split()[0]:  dynax_DQ3(c, r) ) 
    
    nu.add_cascade(menu= dynai, label= 'DQ3' )
    #@nonl
    #@-node:ekr.20050421093045.101:show clip
    #@-others
    #@nonl
    #@-node:ekr.20050421093045.98:<< action >>
    #@nl
#@nonl
#@-node:ekr.20050421093045.95:load_menu
#@+node:ekr.20050421093045.102:init
def init():
    """this is one less than one too many ok's."""
    ok = Tk and dynacom and not g.app.unitTesting
    if ok:
        if g.app.gui is None:
            g.app.createTkGui(__file__ )
    
        ok = g.app.gui.guiName() == "tkinter"
        if ok:
            import leoPlugins
            leoPlugins.registerHandler("create-optional-menus", load_menu)
    
            #no finer grained control than command1?
            #seems like this would slow things down conciderable
            #probably because wanted to catch tangle too
            # save1 should be less overhead
            leoPlugins.registerHandler("save1", timestamp)
            
            #plugin_signon reloads the plugin, can forgo that
            #g.plugin_signon(__name__)  # + __version__

            #have to lopkup how to enable these
            #.bind('<Alt-z>', lambda c= c: htmlize(c))
            #.bind('<Alt-x>', lambda c= c: dupe(c))

    return ok
#@nonl
#@-node:ekr.20050421093045.102:init
#@-others

#makeup an alias for importing and for keybindings
#import dyna_menu; print dir(dyna_menu)
#would be slicker if could use alais inside macros but they aren't defined yet
htmlize = dynaZ_htmlize
dtef = dynaB_Clip_dtef
dupe = dynaM_dupe
DQ3 = dynax_DQ3
helps = dynaB_help

#you can use a macro in other ways
def timestamp(tag, keywords):
    """stolen from the timestamp plugin
    chged hook from command1 to save1
    how to hook write @file so can timestamp that?
    
    add nag you if changed and not saved over 5 minutes
    add nag if typing after sunset over 3 hours, yea right~
    """
    cmd = keywords.get('label', 'save')

    if cmd.startswith("save") or cmd.startswith("tangle"):
        c = keywords.get('c')
        if c:
            dynaB_Clip_dtef(c, ret= 'p')  #just print
            g.es('at node:' + (c.currentVnode().headString().strip())[:128])


#@-node:ekr.20050421093045.2:@thin dyna_menu.py
#@-leo
