#@+leo-ver=4-thin
#@+node:ekr.20050421093045.103:@thin dynacommon.py
"""not needed in pluginManager.txt
generate this file to exist in the Leo plugins directory.
you have to edit in your correct paths. < set filenames > section 

helper code your macro can call from dyna_menu or other Leo script/plugin.

check your sys.path that plugins is there before import
from dynacommon import *
was clone, is common to dynabutton, dynatester & dyna_menu

some things common like the dynaBunch & init you probably wont call

    rearrange things carelessly at your own peril

have to lazy eval the filename creation till after leoID is defined"""

#__all__ = 'tmpfile py pypath leosrc reindent pycheck2 pycheck  _caller_symbols deangle commafy stripSentinels sanitize_ leotmp scriptbody runAskYesNoCancelDialog init_dyna dycolors dynaBunch dynaerrout dynaerrline dyna_getsubnodes captureStd runcmd dynadoc dynaput dynaplayer pyO'.split()
#this needs its own dictionary dopylint doreindent

import sys, os
import leoGlobals as g
import Tkinter as Tk

__not_a_plugin__ = True
__version__ = '0.0139i' #u05417a10:51
#@+others
#@+node:ekr.20050421093045.104:others

#possibly there are unicode anomalies in cStringIO?
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

try:
    True and False
except NameError:
    # match the 2.2 definition
    (True, False) = (1==1), (1==0)
    
#needed in several macros. what if import htmlize from menu?
try:
    enumerate
except NameError:
    def enumerate(seq):
        '''
        >>> enumerate('123') #does 2.2 enumerate a string ok?
        [(0, '1'), (1, '2'), (2, '3')]
        '''
        import sys
        return zip(xrange(sys.maxint), seq)
    print 'now have enumerate'

try:
    sum #no sum in 2.2, not fully tested compatible
except NameError:
    from operator import add
    def sum(seq, m=0, add=add):
        '''
        >>> sum([1, 4, 5, 2], 0)
        12
        >>> sum([len(x) for x in ['12','23','45']], 0)
        6
        
        '''
        return reduce(add, seq, m)
    print 'now have sum'
    del add


#@+node:ekr.20050421093045.105:_caller_symbols
def _caller_symbols():
    """aspncookbook/52278
    Print an expression and its value, 
    along with filename and linenumber
    by Itamar Shtull-Trauring

    thanks I.! returns the callers callers globals and locals
    """
    try:
        raise StandardError
    except StandardError:
        t = sys.exc_info()[2].tb_frame
        return (t.f_back.f_back.f_globals, t.f_back.f_back.f_locals)
#@-node:ekr.20050421093045.105:_caller_symbols
#@-node:ekr.20050421093045.104:others
#@+node:ekr.20050421093045.106:functs w/doctest
#@+others
#@+node:ekr.20050421093045.107:deangle
def deangle(s, repl=  '+'):
    """
    use repl so output can be pasted w/o appearing as named nodes to leo
    
    >>> deangle( '<%s'%'< whatever >>')
    '<+< whatever >>'
    >>> deangle('< whatever >>')
    '< whatever >>'
    >>> deangle('''|\\ /!@=\\#$%,^&?:;."\'<>`~*+''')
    \'|\\\\ /!@=\\\\#$%,^&?:;."\\\'<>`~*+\'

    """
    if s.startswith('<<') and s.endswith('>'+'>'):
        return '<%s%s'%(repl, s[1:])
    return s
#@nonl
#@-node:ekr.20050421093045.107:deangle
#@+node:ekr.20050421093045.108:commafy
def commafy(val, sep= ','):
    """Bengt , added sep
    mod to use leading seperator if . maybe
    also explore using locale instead. ok for now,
    could using specifyer like k so under 1024 is leading zero?
    >>> commafy(2222)
    '2,222'
    >>> commafy(2222, '.')
    '2.222'
    """
    sign, val = '-'[:val<0], str(abs(val))
    val, dec =  (val.split('.')+[''])[:2]
    if dec: dec = '.'+dec
    rest = ''
    while val: val, rest = val[:-3], '%s%s%s'%(val[-3:], sep, rest)
    return '%s%s%s' %(sign, rest[:-1], dec)
#@nonl
#@-node:ekr.20050421093045.108:commafy
#@+node:ekr.20050421093045.109:stripSentinels
def stripSentinels(s, stripsentinals=1,
           stripcomments=0, stripnodesents=1, stripdirectives=1, **ignored):
    r""" r for doctest, ignored so can pass **hopts from htmlize

    Strip sentinal lines from s. from EKR for test.leo htmlize.
    called by htmlize, disa and sfdots. 

    rewritten to save a few microseconds?, (in case anyone is still on a 486)
      lstrip instead of strip, no excess strip.
      save users newlines and join with '' instead of /n
      break out early if not a comment and stripping everything anyway.
      added raw/end_raw in addition to verbatim

    and not create a superfluous lines list. wherever it is found.
    OTOH, splitlines in the forloop still creates a list, so is a style point I guess.
    
    is startswith Unicode safe? is slice? slice over *with next up.

  #@  << essential doctesting >>
  #@+node:ekr.20050421093045.110:<< essential doctesting >>
  >>> s = '#@+leo=4\n#@+node:sent\nhay\n#@nonl\n#@-node: chk \n#@verbatim\n@deco\n#@  @others\n#cmt'
  >>> stripSentinels(s,0,0,0,0)
  '#@+leo=4\n#@+sent\nhay\n#@nonl\n#@- chk \n#@verbatim\n@deco\n#@  @others\n#cmt'
  >>> stripSentinels(s,1,0,1,1)
  'hay\n@deco\n#cmt'
  >>> stripSentinels(s)
  'hay\n@deco\n#cmt'
  >>> stripSentinels(s,1,0,0,1)
  '#@+sent\nhay\n#@- chk \n@deco\n#cmt'
  >>> stripSentinels(s,1,0,1,0)
  'hay\n#@verbatim\n@deco\n#@  @others\n#cmt'
  >>> stripSentinels(s,1,1,1,1)
  'hay\n@deco\n'
  >>> stripSentinels(s,1,1,1,0)
  'hay\n#@verbatim\n@deco\n#@  @others\n'
  >>> stripSentinels(s,1,1,0,0)
  '#@+sent\nhay\n#@- chk \n#@verbatim\n@deco\n#@  @others\n'
  >>> stripSentinels('#@+node:<<sent>+>\nhay\n#@- chk \n##@cmt',1,0,0,0)
  '#@+<+<sent>+>\nhay\n##@cmt'
  >>> stripSentinels('')
  ''
  >>> stripSentinels('\n##\n')
  '\n##\n'
  >>> o = {'stripcomments':0, 'stripsentinals':0, 'stripnodesents':0, 'stripdirectives':0, 'invalidarg':3} 
  >>> stripSentinels(s, **o)
  '#@+leo=4\n#@+sent\nhay\n#@nonl\n#@- chk \n#@verbatim\n@deco\n#@  @others\n#cmt'
  >>> #this should be fixed to allow commented decorators that look like sentinals
  >>> stripSentinels(u'\r#@verb\r#cmt')
  u'\r#cmt'
  >>> stripSentinels('#@@raw\nbetween raw\n#@@end_raw\n', 1,0,1,1)
  'between raw\n'
  >>> stripSentinels('#@@raw\nbetween raw\n#@@end_raw\n', 1,0,1,0)
  '#@@raw\nbetween raw\n#@@end_raw\n'
  >>> #mixed lang
  >>> stripSentinels(';@@raw\nbetween raw\n;@@end_raw\n//cmt')#, 1,0,1,1
  'between raw\n//cmt'
  >>> stripSentinels('be\n;@@first <...>\n')#, 1,0,1,1
  '<...>\nbe\n'
  >>> #
  
  #@-node:ekr.20050421093045.110:<< essential doctesting >>
  #@nl
  not every possible corner case.

    should also have option to strip only comments other than sentinals
    should have option not to mangle node sentinals.
    
    possiblity of a python decorator comment out is very high
    to be sure, will later have to either do this all in the parser
    or get smarter about what is a directive and allow everything else
    no matter the strip setting. or label/warn about the conflict.
    if in <py2.4 deco is a syntax error in the parser, thats fixable.
    and if Leo adds user configurable leadin chars will have to hack it in.

  Leo write logic adds verbatim, like right here.
#@verbatim
    #@@c looks strange without coresponding #@+at

    first file opening and last closing node sentinals could probably be eliminated
    the @others and named section & nodesents should be enough.
    skip namedsection,
    going to be screwed if a lang uses @ for comments
    
    add forced delims check for c,perl,java, html & python
    if other @lang the first 2 are always #python, might have to fix that
    luckily all the tests passed before thought of this hack
    add @first/@last if simple on the same line 

    add another option to mangle namesection refrences <+< xyz >>
    to allow copy&paste into a node without needing to edit them.

    """
    import leoGlobals as g
    result = []
    verbatim = 0
    first = last = ''

    cmts = ('//', '/*', ';', '<!--')    
    for line in s.splitlines(True):
        s = line.lstrip()
        
        #much trickier if need to know @language & delims
        # otherwise need seperate strippers. 
        #and gets especially screwy in mixed languages

        for icmt, x in enumerate(cmts):
            if not s.startswith(x):   continue
            cmt = cmts[icmt]
            break
        else:
            #print 'didnt find anything'
            cmt = '#'

        #should't hsve to recalc these each time
        tag1 = cmt+'@+node:'
        tag2 = cmt+'@-node:'
        n = len(tag1)

        #@        << linematch >>
        #@+node:ekr.20050421093045.111:<< linematch >>
        #we'll assume no one would use verbatim\n#@@end_raw!
        if verbatim > 0 and not s.startswith(cmt+'@@end_raw'):
            if verbatim == 1: verbatim = 0
            result.append(line)
            continue
        
        elif verbatim > 0 and s.startswith(cmt+'@@end_raw'):
            verbatim = 0
            if not stripdirectives:
                result.append(line)
        
        elif s.startswith(cmt+'@verbatim') or s.startswith(cmt+'@@raw'):
            verbatim = g.choose(s.startswith(cmt+'@verbatim'), 1, 2)
            if not stripdirectives:
                result.append(line)
        
        elif not s.startswith(cmt+'@') and (not stripcomments and s.startswith(cmt)): 
            result.append(line)
            continue
        
        #need a regex here could be #@[ \t]@VALIDDIRECIVE 
        #\t unlikely to work in startswith, fix if you care about tabs
        #otherwise could strip valid comments, but whould a real Leo user do that?
        elif s.startswith(cmt+'@@') or s.startswith(cmt+'@ ') or\
             s.startswith(cmt+'@\t') or s.startswith(cmt+'@<<'):
        
            #actually might be a little more complicated first1 first2
            #might stripsentinal allow too
            if s.startswith(cmt+'@@first'):
                first = line[s.find(' ')+1:]; continue
            if s.startswith(cmt+'@@last'):
                last = line[s.find(' ')+1:]; continue
        
            #skip namedsection, could opt this in
            if stripsentinals and s.find('<<') != -1 and\
                  s.find('>>') != -1: 
                continue
            if not stripdirectives:
                result.append(line)
        
        elif s.startswith(tag1):
            if not stripnodesents:
                i = line.find(tag1)
                result.append(
                  line[:i] + cmt+'@+' + line[i+n:].replace('<<','<+<'))
        
        elif s.startswith(tag2):
            if not stripnodesents:
                i = line.find(tag2)
                result.append(
                  line[:i] + cmt+'@-' + line[i+n:].replace('<<','<+<')) #.strip() happy
        
        elif stripsentinals and s.startswith(cmt+'@'):
            continue
        
        elif stripcomments and s.startswith(cmt):
            continue
        
        else: #could this possibly be sentinals?
            #print s
            result.append(line)
        #@nonl
        #@-node:ekr.20050421093045.111:<< linematch >>
        #@nl


    return ''.join([first]+result+[last])  #user might have other ideas about \n
#@nonl
#@-node:ekr.20050421093045.109:stripSentinels
#@+node:ekr.20050421093045.112:sanitize_
def sanitize_(s):
    """ Leo's sanitize_filename is too aggressive and too lax
    origional regex from away.js
    this should make nobody happy equally.
    strips most characters, space and replaces with underscore, len<128
    the doctest is in a subnode to allow syntax highlighting
    #@    << chk sanitize >>
    #@+node:ekr.20050421093045.113:<< chk sanitize >>
    the best of both worlds, doctest with syntax highlighting!
    >>> sanitize_("|\\ /!@=#$%,^&?:;.\\"'<>`~*+")
    '_____________'
    >>> sanitize_("")
    ''
    >>> sanitize_("@abc123[],(),{}")
    '_abc123[]_()_{}'
    >>> #one comment line required when use subnode this way 
    >>> #to avoid doctest seeing node sentinals. don't ask...
    #@nonl
    #@-node:ekr.20050421093045.113:<< chk sanitize >>
    #@nl
    """
    #if not s: return
    import re

    res = re.compile(r"""
    [|\\ /!@=\#\$%,\x5E&\x3F:;.\x22\x27<>`~\*\+\t\n\f\r\b\a]
    """, re.IGNORECASE | re.VERBOSE);  
    #  ^?"' \xnn,  [],(),{} ok, * not sure always ok

    #should test for unicode before str()
    return res.sub('_', s.strip()).replace('__','_')[:128]
#@nonl
#@-node:ekr.20050421093045.112:sanitize_
#@+node:ekr.20050421093045.114:leotmp
def leotmp(name = None, tmp= None):
    """ attempt to divine the user tmp dir add to input name
    later prepend leoID unless no leoID flag or something
    print os.path.realpath(tempfile.tempdir) simpler?

    """
    #factor out later into combined find @home thing + leoID
    for x in ['tmp', 'temp', 'home']:
        try:
            tmp = os.environ[x]
            break
        except KeyError:
            pass
    else:
        tmp = './'

    if not g.os_path_isdir(tmp):
        tmp = './'

    if name is None:
        return tmp
    return g.os_path_join(tmp, name)

#@-node:ekr.20050421093045.114:leotmp
#@-others
#@+at
# others not required except to enable du_test for all these subnodes
# candidates for adding to g. or g.app at least while dyna running
# have to weigh scripts and macros import common or just assume exists in g.
# comafy, sanitize_ actually more usefull in site-packages/myutils.py
# but I script and run nearly everything in Leo anyway.
# 
# 0 failed.
# all over htmlize and config isn't fully tested and the one test fails.
# with py2.2, 2 places Expected: True Got: 1 same w/False in dyna_menu
# but I don't think any code depends on True or False being 1 or 0
# except for doctest.
#@-at
#@-node:ekr.20050421093045.106:functs w/doctest
#@+node:ekr.20050421093045.115:dynastuff
#@+node:ekr.20050421093045.116:fixbody
#previouslky fixscript selectscript and a few other things
#Leo always outputs sentinals now and follows subnodes
#and stripSentinals has more options
#and default is usually no tabs so expandtabs less critical

def fixbody(c,data=None):
    """ return script following subnodes and @others
    strips all sentinals
    if addscript its prepended to the output or something?
    """

    p = c.currentPosition()

    if not data:
        data = g.getScript(c, p)

    else: #selected text, so comment out directives in the @language
        data = selecbody(data, g.scanDirectives(c, p))

    if not data:  
        data = EOLN  #avoid error on empty script
    else:
        #could work the other way too if anyone wanted tabs.
        if hasattr(g.app.dynaMvar, 'tabstrip'):
            if g.app.dynaMvar.tabstrip: 
                data = data.expandtabs(g.app.dynaMvar.tabstrip)
    return data
#@nonl
#@-node:ekr.20050421093045.116:fixbody
#@+node:ekr.20050421093045.117:selecbody
def selecbody(data, sdict):
    r"""for commenting out directives in selected text.
    should start by commenting out all lines that start with @
    then strip sentinals. not going to follow @others?
    multiline delims probably not currently handled well
    have to add some tests 
    and get back into understanding the full use case.
    
    if selected starts after @ it should be commented anyway?
    
    backslash inside string literal, always skips the next char 
    \s might have to be \\s in raw?
    
    >>> selecbody(None, {'language':'python'})
    
    >>> selecbody('@language python\n#cmt', {'language':'python'})
    '#@language python\n#cmt'
    >>> cdct = {'language':'java', 'delims': ('/*', '*/', '//')}
    >>> selecbody('@language python\n#cmt', cdct)
    '/*@language python\n#cmt'

    have to do some reserch and fix this
    """
    if not data: return
    import leoGlobals as g

    cmtdelim = '#'
    if sdict['language'] != u'python':
        #obviously for other language have to check is valid
        # is more than one, then have to trail each line etc
        #was delims[0] not sure where that came from
        #coverage tool might have caught that so far untested
        #think it needs to be 0+1 if [2] is None
        #wouldv'e made more sense to always have the single in 0?
        cmtdelim = sdict.get('delims', ['#'])[0]
        
    import re
    datalines = data.splitlines(True)
    #g.es('data is %r'%(datalines,))


    #not sure why <\< works
    #does \s work like s, apparently not. 
    #though \s was only for rawstring w/o it misses indented @|<
    repATang = re.compile('\s*<\<.*?>>.*')  #^$ 
    repATc = re.compile('\s*@.*', re.MULTILINE )
    #could use it on the whole string, ok line by line too.


    sx = []
    inATc = False  #a comment, not @c. poor name choice here.
    for x in datalines:
        
        if inATc:  #chances are Leo already does this somewhere
            #what about the foolish @color inside already started comment?
            #any @ is end of comment directive, 
            if x.startswith('@c'): #@ but its not stopping till @x!
                inATc = False
            sx.append('%s%s'%(cmtdelim, x) )
            continue

        if repATc.match(x):  #is start of comment
            if x == '@\n' or x.startswith('@ ') or \
                x.startswith('@\t') or x.startswith('@doc'):
                inATc = True
            sx.append('%s%s'%(cmtdelim, x) )
            continue

        if repATang.match(x): #is sectionname
            #would need to get more fancy here
            sx.append('%s%s'%(cmtdelim, x) )
            continue
        
        #if x == '\n': continue  #delete blank lines?

        sx.append(x)

    return ''.join(sx)
#@-node:ekr.20050421093045.117:selecbody
#@+node:ekr.20050421093045.118:AskYesNo
#file leoTkinterGui.py
#import tkFont,Tkinter,tkFileDialog leoTkinterDialog
#class tkinterGui(leoGui.leoGui):
#when it works add some way to up the damm fonts!

def runAskYesNoCancelDialog(c,title,
    message=None,yesMessage="Yes",noMessage="No",defaultButton="Yes"):
    """Create and run an askYesNoCancel dialog ."""
    import leoTkinterDialog
    d = leoTkinterDialog.tkinterAskYesNoCancel(c,
        title,message,yesMessage,noMessage,defaultButton)
    #d.configure(font=(("Lucida", "Console"), 12)) #nfg
#AttributeError: tkinterAskYesNoCancel instance has no attribute 'configure'
    #d.buttonsFrame.configure(font=(("Lucida", "Console"), 12)) #nfg
    #tryed buttonsFrame, frame, top, root...

    return d.run(modal=True)
#@nonl
#@-node:ekr.20050421093045.118:AskYesNo
#@+node:ekr.20050421093045.119:dynaBunch
import operator

def init_dyna(c, *a, **k):
    """same for both button and menu
    """    
    caller_globals, caller_locals = _caller_symbols()

    dynainst = dynaBunch(
        dynadefaultFlag = Tk.IntVar(),
        dynapastelst = ['print', 'paste', 'doc'],
        dynapasteFlag = Tk.StringVar(),
        #getsubnodes different in button & menu, lst is a list of macros
        dynadeflst = dyna_getsubnodes(c,  globs= caller_globals),
        verbosity = 0, #0or1 just dots in @test from du_test
        justpychecker =  1, #show source after running pychecker & pylint
        htmlize_hilighter = '',  #other language colorizer
        bugimport =  0,  #test fallbacks on ImportError
        )
    
    #print to start, paste over selection later

    dynainst.dynapasteFlag.set(dynainst.dynapastelst[0] )
    dynainst.dynadefaultFlag.set(0)
    return dynainst


class dynaBunch(object):
    """tieing an instance of dynaBunch to c.frame is responsibility of caller
    Bunch aspn python cookbook 52308
    point = Bunch(datum=y, squared=y*y, coord=x)
    if point.squared > threshold:
        point.isok = 1
    in Leo From The Python Cookbook. used setattr & getattr
     not sure of the ivar stuff for now
    repr lifted from c.l.py
    clear might still use, need gc tests
     http://www.norvig.com/python-iaq.html  (Struct class)

    in the sprit of one obvious way to do it.
    the idom appears to be to change the name of the class
    and hype it as a way to turn a dict into a lot of instance vars
    alot are taking credit for this idea through the years,

        """
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, '\n'.join(
            ['%s=%r' % keyval for keyval in self.__dict__.items()]))

    def __clear(self):
        g.es('attempting to clear')
        for key in self.__dict__.keys():
            g.es(';k=',key)
            del key
            g.es('deleted')
        g.es('\ndone clear')

    def set_ivars(self, c):
        """Set the ivars for the find, from searchbox
        might want to use this
        """
        # Modified from leoTkinterFind.set_ivars
        #for key in self.intKeys:
        #    setattr(c, key + "_flag", 0)  

    def ivars(self):
        return self.__dict__.keys()
        
    def __setitem__ (self,key,value):
        #allows access like dyna['dynalst']?
        return operator.setitem(self.__dict__,key,value)
        
    def __getitem__ (self,key):
        return operator.getitem(self.__dict__,key)

    """
    def load(infile):
        strng = infile.read()
        exec( 'bag = Bag(\n' + strng + ')' )
        return bag
    load = staticmethod(load)

    def save(self, outfile):"""
#@nonl
#@-node:ekr.20050421093045.119:dynaBunch
#@+node:ekr.20050421093045.120:names and colors
#Leo log Tk names & HTML names and colors
dycolors = dynaBunch( 
    gAqua = 'aquamarine3',
    gBlack = 'black',
    gBlue = 'blue',
    gFuchsia = 'DeepPink3',
    gGray = 'gray48',
    gGreen = 'LimeGreen',
    gLime = 'PaleGreen2',
    gMaroon = 'maroon4',
    gNavy = 'midnightblue',
    gOlive = 'OliveDrab4',
    gPurple = 'purple3',
    gRed = 'red',
    gSilver = 'SlateGray3',
    gTeal = 'steelblue4',
    gWhite = 'white',
    gYellow = 'Yellow2',
    gError = 'tomato',

    hAqua = '#00FFFF',
    hBlack = '#000000',
    hBlue = '#0000FF',
    hFuchsia = '#FF00FF',
    hGray = '#808080',
    hGreen = '#008000',
    hLime = '#00FF00',
    hMaroon = '#800000',
    hNavy = '#000080',
    hOlive = '#808000',
    hPurple = '#800080',
    hRed = '#FF0000',
    hSilver = '#C0C0C0',
    hTeal = '#008080',
    hWhite = '#FFFFFF',
    hYellow = '#FFFF00',
    )
#print dycolors.gYellow
#@-node:ekr.20050421093045.120:names and colors
#@+node:ekr.20050421093045.121:dynaerrout
#maybe can turn on full exception reporting 
#rather than rolling my own
# es_event_exception (eventName,full=false):

def what_line_am_i_on():
    #from the snippits collection
    import sys
    try:
        raise "Hack"
    except:
        return sys.exc_info()[2].tb_frame.f_back.f_lineno

#    g.es('lineno= ' + what_line_am_i_on() )

def dynaerrout(err, msg):
    """from fuzzy cmd
    previous Leo masked the errors 
    making debuggin of some scripts more painful than not.
    often enough you don't want to gotoline number either.
    """
    from traceback import print_exc

    g.es(msg, color= dycolors.gError)
    f = StringIO.StringIO()
    print_exc(file= f)
    a = f.getvalue().splitlines()
    for line in a:
        #c.goToLineNumber(n=int(newSel))
        g.es(line, color= dycolors.gError)
#@nonl
#@-node:ekr.20050421093045.121:dynaerrout
#@+node:ekr.20050421093045.122:dynaerrline
def dynaerrline():
    """for debuggin, return just the error string on one line
    call in an except after an error.

    >>> try:
    ...    a = 1 / 0
    ... except Exception:
    ...    print dynaerrline()[:49]
    ZeroDivisionError integer division or modulo by z
    """
    import sys
    exctype, value, tb = sys.exc_info()

    if type(exctype) == type(''):
        exc_type_name = exctype
    else: exc_type_name = exctype.__name__

    el = ['%s = %s .'%(k, repr(v)) for k, v in vars(exctype).items()]

    return '%s %s %s '%(exc_type_name, value, el)

#@-node:ekr.20050421093045.122:dynaerrline
#@+node:ekr.20050421093045.123:getsubnodes
#code to operate dynamenu, no user code

def dyna_getsubnodes(c, globs= {}):
    """ changed API slightly, macros now need a common first 5 chars
    if I can change it to dont care about the name I will.
    
    from the plugin, the old way of walking the node to find macros
    is not going to work I just realized
    there is no current node, this has to run before the plugin is made
    and somehow encode the macros and decode them, 
    and insert them into the plugins namespace. yikes
    maybe if I put @others in a stratigic place, they will be included
    all that would remain is to get their names from a __dict__
    
    glitch, they arent added in the order defined in macros node.
    sorting
    glitch when in dynacommon globals isnt the callers globals!
    fails from test.leo
    """
    lst = []

    try:
        lst = [x for x in globs
                if x.startswith('dyna')
                if x[5] == '_'   #x[4] specifys type of macro
                ]

        #possibly decorate somehow to respect the order defined in the py
        #maybe add a user char after _ to specify numeric position
        
    except Exception, e:
        # d=rew  Leo caught syntax error, space
        #Leo caught TypeError: ut() takes exactly 1 argument (2 given)
        #d=rew might not have caught this, or not printed full traceback
        dynaerrout(e, "initMdyna ")

    lst.sort()
    #es('dynamenu macros %s'%(lst,) )
    return lst
#@nonl
#@-node:ekr.20050421093045.123:getsubnodes
#@+node:ekr.20050421093045.124:captureStd
class captureStd(object):
    """the typical redirect stdout
    add stderr and stdin later
    borrowing the class from PH testsuite for redirect stdout

    leo also has filelike objects and its own redirect    
    there isa config option and a plugin to redirect to log
    and to append to body of captured output

    another way
    sys.displayhook = mydisplayhook

    >> def mydisplayhook(a):
    ...     if a is not None:
    ...             sys.stdout.write("%r\n" % (a,))
    ...
    
    only used in evaluator, why not in du_test
    or if it doens't work there why does it work in evaluator w/calc_util?
    maybe can replace now?
        """
    def captureStdout(self):
        sys.stdout = StringIO.StringIO()

    def releaseStdout(self):
        captured = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        return captured
#@-node:ekr.20050421093045.124:captureStd
#@+node:ekr.20050421093045.125:runcmd
def runcmd(cmdlst, to_stdin= None):
    """cmdlst is either a list or string for subprocess
    think is string for popen
    
    for win9x this works better than other popen for me.
    on *nix you can import commands or something else popen5 maybe
    this does wait and leo is inactive so if there is a chance
    the process will infinate loop, better use a spawner
    you get the return output outerr stdout stderr

    use subprocess if available and not on pythonw till that bug fixed
    see forums for usage and download from effbot.org if <py2.4
    
    py2.2 think prints 1 as True and so fails
    >>> 'pythonw.exe'[-5:].upper() == 'W.EXE'
    True
    
    mostly used to run checkers on py file in site-packages
    or wherever you set the defaults
    if Leo or temacs core gets an executeFile we will use that if it works
    shell=True still fails for me on win9x so fork still up in the air.
    and so a flash if no console, latest test seem to deconfirm this.
    
    and a title change on the console if already open to the last command
    seems to be a subprocess bug
    
    adding stdin driver to feed input to command and options
    leave it up to caller to use the -- or no filename conventions

    shell metacharacters?
    
    startupinfo
    ASPN/Cookbook/Python/Recipe/409002

    """
    import os, sys

    try: 
        if g.app.dynaMvar.bugimport: raise ImportError
        import subprocess
    except ImportError:
        #not going to concider name collision if you have an older
        #python with one of the previous incarnations of subprocess
        subprocess = None

    outstd = outerr = ''
    #think only windows pythonw fails stdout/stderr duplication
    #if sys.executable[-5:].upper() == 'W.EXE': subprocess = None

    if not subprocess:
        #should try to get return code its <<128 or something on stderr
        if to_stdin:
            #just haven't programmed it in yet, but get subprocess anyway!
            g.es('stdin redirection not avaiable \nw/o subprocess module')
            return outstd, outerr

        if isinstance(cmdlst, list):
            cmdlst = ' '.join(cmdlst)

        child_stdin, child_stdout, child_stderr = os.popen3(cmdlst)
        #better to_stdin.replace('\n', os.lineterm())
        #do I have to child_stdin.write(to_stdin) & wait?
        outstd = child_stdout.read()
        outerr = child_stderr.read()
    else:
        #@        << subproc >>
        #@+node:ekr.20050421093045.126:<< subproc >>
        try:
            if to_stdin: #could hang w/bad or insufficent data
                if g.app.dynaMvar.verbosity: g.es('piping to stdin')  #, BLINK
        
            startupinfo = subprocess.STARTUPINFO()
        
            #depends on if pywin32 or _subprocess?
            if hasattr(subprocess, 'STARTF_USESHOWWINDOW'):
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            ps = subprocess.Popen(cmdlst, #cwd= fdir,
                universal_newlines= True,
                stdin= subprocess.PIPE,
                stdout= subprocess.PIPE, stderr= subprocess.PIPE
                #,close_fds=True
                , startupinfo=startupinfo
                )
        
            (outstd, outerr) = ps.communicate(to_stdin)
            ret = ps.wait()
        
        except ValueError:  #if Popen is called with invalid arguments. 
            g.es('invalid args?\n', cmdlst)
        
        except Exception:
            g.es_exception(full= True)
            g.es(' args?\n', cmdlst)
        #@nonl
        #@-node:ekr.20050421093045.126:<< subproc >>
        #@nl
    #will probably add ret and force=0 if not subprocess
    return outstd, outerr
#@nonl
#@-node:ekr.20050421093045.125:runcmd
#@+node:ekr.20050421093045.127:dynadoc
def dynadoc(c, sub= 'all', globs= {}):
    """read dynadeflst and createdoc for them
        was previously print, but that doesnt work well in plugin
        add a simple wrap, which isn't appending dash in midword like expected
        could set wrap on for the log. then off again, 
        would probably unwrap  though

    combined the call to all and removed else. works because
    a list is made from sub, will preclude docing a macro named all

    using now \python23\lib\textwrap.py, if available
    too many amonalies in fordoc too little time.
    made a wraper macro, don't really want another depency
    would have to extract the relevant code and have the 
    macro call it too. ok a little code duplication for now
    
    expand to show macro's internal __dict__
    getting doc for fliper for ex, might be nice to know
    add quit sentinal to docs to limit display
    use Leo g.wrap and in dynawrapper or call dynawrapper
    add some reST formatting to docs
    could add some slight blurb on each ini option value.
    a few in dynacommon like runcmd could be doced
  """
    import sys
    try:
        import textwrap as tw
    except ImportError:
        tw = None  #or overwrite formdoc
        g.es('textwrap is going to produce better results.')
        g.es('get it from the python cvs archive\n')
        
    #from pydoc import resolve, describe, inspect, text, plain
    #@    << formdoc >>
    #@+node:ekr.20050421093045.128:<< formdoc >>
    def formdoc(doc, to= 50):
        r"""    
        >>> formdoc('create a rough wraper to 40 charlines', 14)
        '\n  create a rough\n    wraper to 40 charlines\n'
    
        """
        sx = doc.expandtabs(2).splitlines()
        sl = []
        for i, x in enumerate(sx):
            if len(x) < (to-8): sl.append('  ' + x.lstrip()); continue
    
            if len(x) > to: ax = to
            else: ax = len(x) - 1
    
            dash = '-'
            while ax > (to-8):
                if x[ax] in ' .,(){}[]?\n': dash = ''; break
                ax -= 1
            #if ax w/in few char of len(x) may as well be one line
            #check it isnt eating a char at ends
            sl.append('  ' + x.lstrip()[:ax] + dash)
            sl.append('   ' + x.lstrip()[ax:])
    
        return '\n'.join(sl)
    #@nonl
    #@-node:ekr.20050421093045.128:<< formdoc >>
    #@nl
    lst = [sub ] 
    if sub == 'all':
        lst = g.app.dynaMvar.dynadeflst
        lst += [x for x in globs if x.startswith('cmd_')]
        lst.reverse()

    #g.es(g.__dict__.keys()) {}
    #g.es(g.app.__dict__.keys()) Leo ivars

    for x in lst:
        #need to get the callers globals
        #f = g.app.dynaMvar.globals()[x]  nor globals()[x]
        #f = g.app.__dict__[x]  #is this same as app.globals()[x]
        try:
            f = globs[x]  #
        except Exception:
            g.es('cant find', x)
            continue
        
        #if no doc problems
        #try to get len of unsized object or unscriptable object
        #hasattr(f, '__doc__') always true for a function
        elip = ''
        if f.__doc__:

            coln = f.__doc__.find('~EOT') 
            if coln == -1: coln = 520

            doc = f.__doc__[:coln]
            if len(f.__doc__) > coln: elip = ' ...'
        else:
            doc = ' no additional info '

        if not tw:
            st = formdoc(doc)
        else:
            t = tw.TextWrapper(
                     width= 42,
                    initial_indent=' ',
                   subsequent_indent= ' ',
                   expand_tabs= True,
                  replace_whitespace= True,
                 fix_sentence_endings= False,
                break_long_words= True )

            st = t.fill(doc)

        g.es('\n' + x + '.__doc__\n' + st + elip)

    #obj, name = resolve(x, 0)
    #desc = describe(obj)
    #g.es(text.docroutine(f, x))
    
#@nonl
#@-node:ekr.20050421093045.127:dynadoc
#@+node:ekr.20050421093045.129:quiet warnings
def quietwarnings():
    '''quiet warnings from pychecker and tim1 about regex
    this should be part of init rather than module level'''
    
    import warnings
    
    warnings.filterwarnings("ignore",
             r'the regex module is deprecated; please use the re module$',
             DeprecationWarning, r'(<string>|%s)$' % __name__)
    warnings.filterwarnings("ignore",
             r' the regsub module is deprecated; please use re.sub\(\).$.$',
             DeprecationWarning, r'(<string>|%s)$' % __name__)
    
    if sys.version_info >= (2, 3): #py2.2 no simple
        warnings.simplefilter("ignore", DeprecationWarning, append=0)
    
#@nonl
#@-node:ekr.20050421093045.129:quiet warnings
#@-node:ekr.20050421093045.115:dynastuff
#@+node:ekr.20050421093045.130:dynaput
def dynaput(c, slst):
    """return the text selection or put it if slst is not None
    assumes slst is a list to be joined and print/paste as toggled
     add other option, paste w/o delete
    up to the caller to insert \n if required
    eventially pass in event so can get text from any widget
    for now, hardwired to use the Leo API to the Tk text widget   
    **slight problem, wont insert something wth nothing selected
 leoTkinterFrame

  add another menu toggle for print to clipboard 
    in addition to printing or instead of printing
     and replace or append to clipboard.
  bodyCtrl
  allowing fixbody to be called so added test for paste & no selected 
  and selected or slst
  if nothing selected and slst then 3rd choice. must be a full body
  bad idea to past over the node because it wont follow nodes.
  
  problem since split into dynacommonm
  g.top().frame.dynaMvar no longer reliable doe some reason
  maybe that shouve always been based on c? isnt that already c? 
  still havent got a handle on why its failing.
  decide to spend another var. g. works but g.app better
    """
    cg = g.app.dynaMvar
    #print cg

    #this depends on the macro calling dynaput first as they mostly do now
    #bound to be some sideffects untill I put it in the right place
    #maybe the menu has to have a function caller instead of calling the function
    if 'doc' == cg.dynapasteFlag.get():

        #what about dynabutton
        #g.es(sys.modules[dyna_menu].keys())
        caller_globals, caller_locals = _caller_symbols()
        #g.es("this_caller", caller_globals)

        #in dynabutton they are all radio buttions 
        #and its easy to see which was called. unlike in plugin
        #dump all for now
        dynadoc(c, globs= caller_globals)
        return

    Tx = c.frame.body
    if Tx.hasTextSelection() or slst: #*
        
        #returns selection point if nothing selected
        Tst,  Ten = Tx.getTextSelection()

        if not slst: #**and Tx.hasTextSelection()
            return Tx.getTextRange(Tst, Ten)

        else:

            #ux = g.toUnicode(x[1:] )  ?? need to know the encodeing!
            # toUnicode(before,app.tkEncoding), hope Leo handles this
            ux = ''.join(slst)
    
            if 'print' == cg.dynapasteFlag.get():
                #print ux
                g.es(ux)

            elif 'paste' == cg.dynapasteFlag.get() and \
                    Tx.hasTextSelection():
                #g.es('overwrite\n', str(Tx.getTextRange(Tst, Ten)) )
        
                #btw, Tk insert doesnt disturb the selection.
                Tx.deleteTextSelection()
                Tx.setInsertionPoint(Tst)
                #print '%r', ux
                Tx.insertAtInsertPoint(ux)
                Tx.onBodyChanged("Typing")
        
                #selection may wander depending on the final size
                Tx.setTextSelection(Tst,  Ten)

            else:
                g.es('nothing selected',
                         cg.dynapasteFlag.get() )

    else: g.es("no text selected", color= 'orangered' )
#@nonl
#@-node:ekr.20050421093045.130:dynaput
#@+node:ekr.20050421093045.131:python -O
#make part of a larger basic python sanity check
import leoGlobals as g

#indented def's problem in doctest < py2.4b2?
def xt():
    """__ """
    pass

try:
    assert(1 == 0)
    g.es('assert disabled, use g.app._t.assert_()',
        color= 'tomato')

    if __debug__: g.es('__debug__ is',__debug__, color= 'tomato')
    #how to tell if also -OO? __debug__? prob only -O
    #if hasattr(x,"__doc__") and x.__doc__:
    #if not hasattr(dynaB_Clip_dtef, '__doc__'):  #
    #if not len(dynaB_Clip_dtef.__doc__):
        
    #print dynaplay.__doc__  
    #when printed is not None of -O, of not printed is None if -O!
    #x()
    print xt.__doc__, #will this fail on pyw?

    #doc apparently is always defined, even if empty? just None if -OO
    #further caviet, is None untill run regardless if -O due to late binding
    #even if run is None, has to be specifically accessed! weird...
    #if printed is totally unreliable the difference between -O and -OO
    #back to the drawing board.
    if xt.__doc__ is None:
        pyO = 'OO'
        g.es('YOU MAY HAVE RUN python -OO \ndoctest Will fail, @test ok',
            color= 'tomato')
    else:
        pyO = 'O'
        g.es('YOU HAVE RUN python -O',
            color= 'tomato')

except AssertionError: 
    pyO = 'I'  #used in du_test
    pass
del xt
#@nonl
#@-node:ekr.20050421093045.131:python -O
#@-others

#depandance on sanitize_ and leoID
#@<< set filenames >>
#@+node:ekr.20050421093045.132:<< set filenames >>
#note, these changes are at the time the button or menu is created
#to effect these changes you have to 
#write the plugin and start a new python and leo. maybe reload
#execute script on the dynaclick node for the dynabutton
#they will take effect in dynatester imediatly
#preserve the space after to allow for parameters
#those that will be joined to pypath start with seperator \ or /
#any other scripts should have their own full path, 

#pypath = r'C:\c\py\Python233'         #nospace
pypath = g.os_path_split(sys.executable)[0]

#py =  pypath + '/python.exe -tOO '     #_space_
py =  g.os_path_join(pypath, 'python') + ' -tO '

#leosrc = r'c:\c\leo\leo4CVS233\src'
leosrc = g.app.loadDir

#reindent = g.os_path_join(pypath, '/Tools/Scripts/reindent.py ')  #space
reindent = pypath +  '/Tools/Scripts/reindent.py '  #space

#print pypath, py, leosrc

#classic pychecker
pycheck = pypath + '/Lib/site-packages/pychecker/checker.py '  #space
#pychecker2, doesnt import, is alot slower and less details.
# and leaves some temp files, I guess its still experimental.
pycheck2 = pypath + '/Lib/site-packages/pychecker2/main.py '


#
#classic pychecker I think does import regex which causes a warning when called from plugin. maybe they fixed that in the latest version.
#not sure why dont see it when run from dynabutton. output on stderr?
#DeprecationWarning: the regsub module is deprecated; please use re.sub()
# was caused by tim1crunch, I supress the warning now.

#pylint is its own macro now, could delete if you don't run it
#set to 1 to call pylint after pychecker ub makatemp
dopylint = 0  #this call too complicated to code in here


doreindent = 0 #to forgo reindent step in pylint & makatemp macro


#@+at
# it might be preferable to generate a new tmpfile w/pid or something
#  ok for singleuser no security multiuser issues for now.
# YMMV, I set tmp and temp in autoexec,
# 
# it seems pylint has to be able to import from site-packages
# look in makatemp trying to add tmp to syspath isnt easy from Leo
# add leoID, and sanitize, leoID may not exist at this point.
# why would it be None though?
# that seems odd since plugins should be able to call on it at creation
# should create an hname for htmlize also
# or maybe the macro should add the extension
# 
# putting an html file in tmp could still be a huge secuity risk
# maybe should be in user HOME instead?
# also create in site-packages might not be enabled for everyone.
# have to check better for write access
# 
# later generate the filenames inside a function
# and add them to a Bunch allong with the colors
# maybe a Bunch of Bunches class dynaMvar will overtake
#@-at
#@@c

#print 'leoID=', g.app.leoID
Id = g.choose(g.app.leoID, g.app.leoID, 'Leo')
tname = sanitize_('tmptest' + Id )+ '.py'

#use lower if on *nix. 
#windos may set TEMP and TMP by default, case insensitive.
#tmpfile = g.os_path_join(os.environ['tmp'],'tmptest.py')

tmpfile = g.os_path_join(pypath, 'Lib/site-packages', tname)
#
tname = sanitize_('python' + Id )+ '.html'
htmlfile = g.os_path_join(
           os.getenv('tmp', default= g.os_path_abspath('./')), tname)


del Id, tname

#replace forwardslash to backslash if required
#frd slash usually ok except for cd and sometimes openfile
#with filename as parameter in windos frdslash might be taken as option
if sys.platform[:3] == 'win':
    #generally win doesn't care mixed slashes
    #but you might pass py, pypath et al thru here too
    tmpfile = g.os_path_abspath(tmpfile)  #.replace('/', '\\')
    htmlfile = g.os_path_abspath(htmlfile)

#enable the print if not sure its working to satisfaction.
#print tmpfile, htmlfile, py, pypath

#should check is valid and have access and create if doesn't exist...
#may have to defer the creat w/properties so is created on first use
#leoID doesnt exist when dyna imports common and shouldent import * either

#should calculate from @lineending,  does python handle conversion?
EOLN = '\n'  #have to try and use this everywhere, os.linesep()?
#@-node:ekr.20050421093045.132:<< set filenames >>
#@nl
#
#@nonl
#@-node:ekr.20050421093045.103:@thin dynacommon.py
#@-leo
