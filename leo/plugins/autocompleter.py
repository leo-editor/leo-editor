#@+leo-ver=4-thin
#@+node:ekr.20091015103601.5232:@thin autocompleter.py
"""
autocompletion and calltips plugin.

Warning:  this code is for study only: it is way out of date.

Special characters:

    . summons the autocompletion.
    ( summons the calltips
    Escape closes either box.
    Ctrl selects an item.
    alt-up_arrow, alt-down_arrow moves up or down in the list.
    The mouse will work for this as well.

This plugin scans the complete outline at startup..

You many enable or disable features in autocomplete.ini( see configuration section ).
"""

#@@language python 
#@@tabwidth-4

#@<<imports>>
#@+node:ekr.20091015103601.5233:<< imports >>
import leoGlobals as g 
import leoPlugins 
import leoTkinterFrame 

import leoColor 
import ConfigParser 
import os
import os.path  

import re 
import sets 
import string 
import threading
import weakref

Tk  = g.importExtension('Tkinter',pluginName=__name__,verbose=True)
Pmw = g.importExtension("Pmw",    pluginName=__name__,verbose=True)
#@nonl
#@-node:ekr.20091015103601.5233:<< imports >>
#@nl
__version__ = ".73"
#@<<version history>>
#@+node:ekr.20091015103601.5234:<<version history>>
#@+at
# .425:
#     -The initial scan thread is now a daemon thread.
#     -Creates autocompleter box and Calltip box once.
#     -Broke long functions apart.
#     -'Esc'now closes autobox and calltip.
# 
# .500 EKR:
#     - Made minor changes based on .425:
#     -Improved docstring.
#     -Converted to 4.2style.
# .501 EKR:
#     - Changed select method following patch by original author.
#     - Added event.keysym=='Up' case to
# .55 Lu:
#      - Made the watcher def more greedy.  See def for rationale
#      - Made the calltip identification regex more liberal.
#      - streamlined some code.
#      - added DictSet class, experimental in the sense that I haven't had a 
# bug with it yet.  see <<DictSet>> node, under << globals>>
#      - discovered dependency between this and Chapters, auto needs to be 
# loaded first
# .60 Lu
#     - Changed some method names to more acuaretely reflect what they do.  
# Added more comments.
#     - processKeyStroke cleaned up.
#     - added Functionality where any mouse button press, anywhere in Leo will 
# turn off autobox and calltip label.
#     - waiting for Chapters( or chapters ) to have its walkChapters def fixed 
# up, so we can walk the chapters on startup.
#  .7 Lu( The placer revolution!)
#    -migrated to the placer!  This got rid of Canvas based drawing.  The 
# placer may be a good tool to know in the future.  This seemed to
#    be about an even replacement codewise, but I think it gives us an 
# efficiency boost.
#    -changed some lambdas to defs, more for clarities sake then anything.
#    -made global changes to how objects are referred to
#    -got rid of factory defs, autobox and calltip label are created at Editor 
# creation time
#    -dependency between this and Chapters eliminated.
#    -added code to automatically create the .ini file and the autocompleter 
# directory if they do not exist.
#    -added a section about how to configure autocompleter
#    -switched the patterns from using '+' to add pieces together to using 
# '%s'.
# .71 investigated and hopefully fixed startup bug on Windows. Changes that 
# appear to have fixed it:
# 1. We synchronize with an threading Event object.  IO acting screw on 
# windows in a thread.
# 2. There is a global flag indicating whether the config file needs to be 
# read again.
# 3. Explicitly set the file type to 't'.  This could all be attributed to a 
# bug in ConfigParser.  I looked at the source and it doesnt write its data 
# with a 't'.  This indicates trouble with windows.
# 4. Make the 'aini' path composed of os.sep instead of the char '/'.  Im 
# uncertain if the config file ever got read on Windows at this point because 
# of the explicit '/' , instead of using os.path.
# 5. Moved createConfig part out of thread. problems seems centered on 
# Windows/IO/Threading.
# 
#  .72 The thesis and experiments to confirm the problem identified in .71 
# appear
# completely wrong. I could not recreate threading+writeIO staling on XP at 
# all.
# Windows 98 didnt even work. But after commenting out g.es calls it did work. 
# My
# new target for the problem is now focused on keeping g.es calls out of the
# initialScan thread. This will just entail moving all the reading and writing 
# of
# the config and language files out of the thread.
# 
# .73 EKR:
#     - Changed 'new_c' logic to 'c' logic in initialScan.
#     - Added init function.
# .74 EKR:
#     - Changed 'start2' hook to 'new' hook.
# .75 EKR:
#     - Disable scan during unit testing.
#@-at
#@nonl
#@-node:ekr.20091015103601.5234:<<version history>>
#@nl
#@<<a note on newCreateControl>>
#@+node:ekr.20091015103601.5235:<<a note on newCreateControl>>
#@+at
# 
# the function newCreateControl decorates the
# leoTkinterFrame.leoTkinterBody.createControl method.
# 
# It does so to intercept the point where the editor is created. By doing so,
# autocompleter is able to ensure that the placer is used instead of the 
# packer.
# By using the placer autocompleter is able to put the autobox and calltip 
# label
# over the editor when the appropiate time is reached. In versions prior to 
# .7,
# this was achieved by using a Tk Canvas as the background of the Editor. The
# placer is simpler and from what I see more efficient.
#@-at
#@nonl
#@-node:ekr.20091015103601.5235:<<a note on newCreateControl>>
#@nl
#@<<load notes>>
#@+node:ekr.20091015103601.5236:<<load notes>>
#@+at 
# 
# switching to the placer appears to have gotten rid of this dependency
# 
# --no longer true--- Autocompleter needs to be loaded before 
# Chapters/chapters or
# the autobox and the calltip label do not appear in the correct place. --no
# longer true---
# 
# 
#@-at
#@@c 
#@-node:ekr.20091015103601.5236:<<load notes>>
#@nl
#@<<coding conventions>>
#@+node:ekr.20091015103601.5237:<<coding conventions>>
#@+at
# 
# context - means the widget that backs the editor. In versions before .7 it 
# was
# called c and was a canvas. context is the new name, and it is no longer a
# canvas. c, now means commander.
# 
# context.autobox - means the Pmw.ScrolledListBox that offers the 
# autocompletion
# options.
# 
# The autobox contains other widgets that can be accessed by 
# autobox.component(
# 'widgetname' )
# 
# context.calltip - means the Tk.Label that offers calltip information
# 
# context.which = 0 indicates its in autocompleter mode
# context.which = 1 indicates its in calltip mode
# 
# 
#@-at
#@-node:ekr.20091015103601.5237:<<coding conventions>>
#@nl
#@<< configuration >>
#@+node:ekr.20091015103601.5238:<< configuration >>
#@+at
# Autocompleter looks in the plugin directory for a file called 
# autocompleter.ini
# 
# This file contains two options under the [ autocompleter ] section:
#     useauto
#     usecalltips
#     setting either to 1 will turn on the feature. 0 means off.
# 
# If there is a section called [ newlanguages ] it will read each option as a 
# new
# language for autocompleter to recognize, and compile its value as a regex
# pattern for the autocompleter system to recognize as a calltip. This has
# relevance for the .ato system described below.
# 
# languages that currently have patterns: python, java, c++, c and perl
# 
# This file will automatically be generated for the user if it does not exist 
# at
# startup time.
# 
# Autocompleter looks in the plugin directory for a directory called
# autocompleter. If it doesn't find one it will attempt to create this 
# directory.
# This directory should contain what are called .ato files ( pronounced auto 
# ).
# Autocompleter will scan each .ato file that has a first part that matches a
# languages name. For example::
# 
#     python.ato
# 
# autocompleter recognizes python, and will scan this file. The contents are 
# read
# with the same mechanism that reads the information in the nodes, so calltip 
# and
# autocompleter information is added to autocompleters runtime database.
# 
# If a new language has been added in the autocompleter.ini file then an .ato 
# file
# that starts with the new languages name will be recognized and read in. 
# Note,
# this language needs to be recognizable to Leo. Used correctly an .ato file 
# is a
# mechanism by which a user can carry autocompletion and calltip information
# between .leo files/sessions.
#@-at
#@-node:ekr.20091015103601.5238:<< configuration >>
#@nl
useauto = 1 #These two global determine if the autocompleter and calltip systems are used.  Default is on.
usecall = 1
#@<<globals>>
#@+node:ekr.20091015103601.5239:<< globals >>
orig_CreateControl = leoTkinterFrame.leoTkinterBody.createControl 

#@<<DictSet>>
#@+node:ekr.20091015103601.5240:<<DictSet>>
class DictSet( dict ):
    '''A dictionary that always returns either a fresh sets.Set or one that has been stored from a previous call.
    a different datatype can be used by setting the factory keyword in __init__ to a different class.'''

    def __init__( self , factory = sets.Set ):
        dict.__init__( self )
        self.factory = factory

    def __getitem__( self, key ):
        try:
            return dict.__getitem__( self, key ) # EAFTP
        except:
            dict.__setitem__( self, key, self.factory() )
            return dict.__getitem__( self, key )

#@-node:ekr.20091015103601.5240:<<DictSet>>
#@nl
#watchwords ={} switched to DictSet
watchwords = DictSet() # a DictSet that is the autocompleter database.
#calltips ={} switched to DictSet
calltips = DictSet( factory = DictSet) # a DictSet that is the calltip database
pats ={} #used to hold regex patterns to find defintions for calltips
lang = None #determines what language is in effect.  Though its global, only one autobox or calltip label should be visible for the entire leo instance.
configfilesread = False #Determines if the config files need to be read
haveseen = weakref.WeakKeyDictionary()# a dict that tracks the commanders that have been seen without stopping garbage collection of that commander.
#@-node:ekr.20091015103601.5239:<< globals >>
#@nl
#@<<patterns>>
#@+node:ekr.20091015103601.5241:<< patterns >>
# This section defines patterns for calltip recognition.
# The autocompleter does not use regexes.
space = r'[ \t\r\f\v ]+'
end = r'\w+\s*\([^)]*\)'

pats['python'] = re.compile(r'def\s+%s' % end)

pats['java'] = re.compile(
    r'((public\s+|private\s+|protected\s+)?(static%s|\w+%s){1,2}%s)' % (
        space, space, end ) )

pats['perl'] = re.compile(r'sub\s+%s' % end)

pats['c++'] = re.compile(r'((virtual\s+)?\w+%s%s)' %( space, end ))

pats['c'] = re.compile(r'\w+%s%s' % ( space ,end ))

r = string.punctuation.replace('(','').replace('.','')
pt = string.digits+string.letters+r 

ripout = string.punctuation+string.whitespace+'\n'
ripout = ripout.replace('_','')

okchars ={}
for z in string.ascii_letters:
    okchars[z] = z 
okchars['_'] = '_'
#@nonl
#@-node:ekr.20091015103601.5241:<< patterns >>
#@nl

#@+others
#@+node:ekr.20091015103601.5242:init
def init ():

    ok = Pmw and Tk and not g.app.unitTesting # Not for unit tests: modifies core classes.

    if ok:
        leoTkinterFrame.leoTkinterBody.createControl = newCreateControl 
        leoPlugins.registerHandler(('new','open2'),initialScan)   
        g.plugin_signon(__name__)

    return ok
#@nonl
#@-node:ekr.20091015103601.5242:init
#@+node:ekr.20091015103601.5243:watcher
watchitems = ( '.',')' )
txt_template = '%s%s%s'
def watcher (event):
    '''A function that tracks what chars are typed in the Text Editor.  Certain chars activate the text scanning
       code.'''
    global lang 
    if event.char.isspace() or event.char in watchitems:
        bCtrl = event.widget
        #This if statement ensures that attributes set in another node
        #are put in the database.  Of course the user has to type a whitespace
        # to make sure it happens.  We try to be selective so that we dont burn
        # through the scanText def for every whitespace char entered.  This will
        # help when the nodes become big.
        if event.char.isspace():
            if bCtrl.get( 'insert -1c' ).isspace(): return #We dont want to do anything if the previous char was a whitespace
            if bCtrl.get( 'insert -1c wordstart -1c') != '.': return

        c = bCtrl.commander
        lang = c.frame.body.getColorizer().language 
        txt = txt_template %( bCtrl.get( "1.0", 'insert' ), 
                             event.char, 
                             bCtrl.get( 'insert', "end" ) ) #We have to add the newest char, its not in the bCtrl yet

        scanText(txt)

#@-node:ekr.20091015103601.5243:watcher
#@+node:ekr.20091015103601.5244:scanText
def scanText (txt):
    '''This function guides what gets scanned.'''

    if useauto:
        scanForAutoCompleter(txt)
    if usecall:
        scanForCallTip(txt)
#@-node:ekr.20091015103601.5244:scanText
#@+node:ekr.20091015103601.5245:scanForAutoCompleter
def scanForAutoCompleter (txt):
    '''This function scans text for the autocompleter database.'''
    t1 = txt.split('.')
    g =[]
    reduce(lambda a,b:makeAutocompletionList(a,b,g),t1)
    if g:
        for a, b in g:
            #if watchwords.has_key(a):
            #    watchwords[a].add(b)
            #else:
            #    watchwords[a] = sets.Set([b])
            watchwords[ a ].add( b ) # we are using the experimental DictSet class here, usage removed the above statements
            #notice we have cut it down to one line of code here!
#@nonl
#@-node:ekr.20091015103601.5245:scanForAutoCompleter
#@+node:ekr.20091015103601.5246:scanForCallTip
def scanForCallTip (txt):
    '''this function scans text for calltip info'''
    pat2 = pats['python']
    if lang!=None:
        if pats.has_key(lang):
            pat2 = pats[lang]
    g2 = pat2.findall(txt)
    if g2:
        for z in g2:
            if isinstance(z,tuple):
                z = z[0]
            pieces2 = z.split('(')
            pieces2[0] = pieces2[0].split()[-1]
            a, b = pieces2[0], pieces2[1]
            calltips[ lang ][ a ].add( z ) #we are using the experimental DictSet here, usage removed all of the commented code. notice we have cut all this down to one line of code!
            #if calltips.has_key(lang):
            #    if calltips[lang].has_key(a):
            #        calltips[lang][a].add(z)
            #    else:
            #        calltips[lang][a] = sets.Set([z]) 
            #else:
            #    calltips[lang] ={}
            #    calltips[lang][a] = sets.Set([z])        
#@nonl
#@-node:ekr.20091015103601.5246:scanForCallTip
#@+node:ekr.20091015103601.5247:makeAutocompletionList
def makeAutocompletionList (a,b,glist):
    '''A helper function for autocompletion'''
    a1 = _reverseFindWhitespace(a)
    if a1:
        b2 = _getCleanString(b)
        if b2!='':
            glist.append((a1,b2))
    return b 
#@-node:ekr.20091015103601.5247:makeAutocompletionList
#@+node:ekr.20091015103601.5248:_getCleanString
def _getCleanString (s):
    '''a helper for autocompletion scanning'''
    if s.isalpha():return s 

    for n, l in enumerate(s):
        if l in okchars:pass 
        else:return s[:n]
    return s 
#@-node:ekr.20091015103601.5248:_getCleanString
#@+node:ekr.20091015103601.5249:_reverseFindWhitespace
def _reverseFindWhitespace (s):
    '''A helper for autocompletion scan'''
    for n, l in enumerate(s):
        n =(n+1)*-1
        if s[n].isspace()or s[n]=='.':return s[n+1:]
    return s 
#@-node:ekr.20091015103601.5249:_reverseFindWhitespace
#@+node:ekr.20091015103601.5250:initialScan
def initialScan (tag,keywords):
    '''This method walks the node structure to build the in memory database.'''
    c = keywords.get("c")
    if not c or haveseen.has_key(c):
        return 

    haveseen[c] = None 

    #This part used to be in its own thread until problems were encountered on Windows 98 and XP with g.es
    pth = os.path.split(g.app.loadDir)  
    aini = pth[0]+r"%splugins%sautocompleter.ini" % ( os.sep, os.sep )    
    if not os.path.exists(aini):
        createConfigFile( aini )
    try:
        if not hasReadConfig():
            if os.path.exists(aini):
                readConfigFile(aini) 

            bankpath = pth[0]+r"%splugins%sautocompleter%s" % ( os.sep, os.sep, os.sep )
            readLanguageFiles(bankpath)#This could be too expensive to do here if the user has many and large language files.
    finally:
        setReadConfig()

    # Use a thread to do the initial scan so as not to interfere with the user.            
    def scan():
        #g.es( "This is for testing if g.es blocks in a thread", color = 'pink' )
        # During unit testing c gets destroyed before the scan finishes.
        if not g.app.unitTesting:
            readOutline( c )

    t = threading.Thread( target = scan )
    t.setDaemon(True)
    t.start()
#@-node:ekr.20091015103601.5250:initialScan
#@+node:ekr.20091015103601.5251:has read config file meths
#These functions determine if the config and language files have been read or not.  No need to read it more than once.
def hasReadConfig():
    return configfilesread


def setReadConfig():
    global configfilesread
    configfilesread = True
#@-node:ekr.20091015103601.5251:has read config file meths
#@+node:ekr.20091015103601.5252:readConfigFile
def readConfigFile (aini):
    '''reads the autocompleter config file in.'''
    global usecall, useauto 

    try:
        cp = ConfigParser.ConfigParser()
        fp = open( aini, 'rt' )
        cp.readfp( fp )
        fp.close()
    except Exception, x:
        g.es( "Could not open %s because of %s" % ( aini, x ), color = 'red' )
    ac = None 

    for z in cp.sections():
        if z.strip()=='autocompleter':
            ac = z 
        else:
            continue
        if cp.has_section(ac):
            if cp.has_option(ac,'useauto'):
                useauto = int(cp.get(ac,'useauto'))
                if useauto:
                    g.es( "autocompleter enabled", color = 'blue' )
            if cp.has_option(ac,'usecalltips'):
                usecall = int(cp.get(ac,'usecalltips'))
                if usecall:
                    g.es( "calltips enabled" , color = 'blue' )
        break

    nl = None
    for z in cp.sections():
        if z.strip()=='newlanguages':
            nl = z 
        else:
            continue
        if nl and cp.has_section( nl ):
            for z in cp.options( nl ):
                try:
                    pats[ z ] = re.compile( cp.get( nl, z ) )
                    g.es( 'added %s to autocompleter languages' % z , color = 'blue' )
                except Exception, x:
                    g.es( "Could not add %s pattern, because of %s " %( z, x ) , color = 'red')

        break
#@-node:ekr.20091015103601.5252:readConfigFile
#@+node:ekr.20091015103601.5253:createConfigFile
def createConfigFile( aini ):
    '''This function creates a config file identified by the parameter aini'''
    cp = ConfigParser.ConfigParser()
    cp.add_section( 'autocompleter' )
    cp.set( 'autocompleter', 'useauto', '1' )
    cp.set( 'autocompleter', 'usecalltips', '1' )
    cp.add_section( 'newlanguages' )
    try:
        ini = open( aini, 'wt' )
        cp.write( ini )
        ini.close()
        g.es( "autocompleter .ini file created in %s" % aini, color = 'blue' )
    except Exception, x:
        g.es( "Error in creating %s, caused by %s" % ( aini, x ) , color = 'red' )


#@-node:ekr.20091015103601.5253:createConfigFile
#@+node:ekr.20091015103601.5254:readLanguageFiles
def readLanguageFiles (bankpath):
    '''reads language files in directory specified by the bankpath parameter'''
    global lang
    if not os.path.exists( bankpath ):
        try:
            os.mkdir( bankpath )
        except Exception, x:
            g.es( "Could not make %s because of %s" %( bankpath, x ) )
    for z in pats:
        bpath = bankpath+z+'.ato'
        if os.path.exists(bpath):
            f = open(bpath)
            lang = z 
            map( scanText, f )
            #for x in f:
            #    scanText(x)
            f.close()
#@nonl
#@-node:ekr.20091015103601.5254:readLanguageFiles
#@+node:ekr.20091015103601.5255:readOutline
def readOutline (c):
    '''This method walks the Outline(s) and builds the database from which
    autocompleter draws its autocompletion options
    c is a commander in this case'''
    global lang
    if 'Chapters'in g.app.loadedPlugins: #Chapters or chapters needs work for this function properly again.
        import chapters 
        it = chapters.walkChapters()
        for x in it:
            lang = None 
            setLanguage(x)
            scanText(x.bodyString())
    else:
        for z in c.rootPosition().allNodes_iter():
            setLanguage( z )
            scanText( z.bodyString() )
#@nonl
#@-node:ekr.20091015103601.5255:readOutline
#@+node:ekr.20091015103601.5256:reducer
def reducer (lis,pat):
    '''This def cuts a list down to only those items that start with the parameter pat, pure utility.'''
    return[x for x in lis if x.startswith(pat)]
#@-node:ekr.20091015103601.5256:reducer
#@+node:ekr.20091015103601.5257:unbind
def unbind ( context ):
    '''This method turns everything off and removes the calltip and autobox from the canvas.'''
    if context.on: #no need to do this stuff, if were not 'on'
        context.on = False
        context.clean_editor()
        map( context.unbind, ( "<Control_L>", "<Control_R>", "<Alt-Up>", "<Alt-Down>", "<Alt_L>" , "<Alt_R>" ) )
        context.unbind_all( '<Button>' )
        context.update_idletasks()
#@nonl
#@-node:ekr.20091015103601.5257:unbind
#@+node:ekr.20091015103601.5258:moveSelItem
def moveSelItem (event, context ):
    '''This def moves the selection in the autobox up or down.'''

    autobox = context.autobox
    i = autobox.curselection()
    if len(i)==0:
        return None 
    i = int(i[0])
    # g.trace(event.keysym,i)
    try:
        if event.keysym=='Down':
            if autobox.size() - 1 > autobox.index( i ):
                i += 1
            elif i!=0:
                i -1
        elif event.keysym=='Up': # EKR.
            if i > 0:
                i -= 1
    finally:

        autobox.select_clear( 0, 'end' )
        autobox.select_set( i )
        autobox.see( i )
        context.update_idletasks()
        return "break"
#@-node:ekr.20091015103601.5258:moveSelItem
#@+node:ekr.20091015103601.5259:processKeyStroke
def processKeyStroke (event,context ,body):
    '''c in this def is not a commander but a Tk Canvas.  This def determine what action to take dependent upon
       the state of the canvas and what information is in the Event'''
    #if not c.on:return None #nothing on, might as well return
    if not context.on or event.keysym in ( "??", "Shift_L","Shift_R" ):
        return None 
    #if event.keysym=='Escape':
    #    #turn everything off
    #    unbind( c )
    #    return None 
    #if c.which and event.keysym in('parenright','Control_L','Control_R'):
    #    unbind( c )
    #    c.on = False 
    elif testForUnbind( event, context ): #all of the commented out code is being tested in the new testForUnbind def or moved above.
        unbind( context )
        return None
    #elif event.keysym in("Shift_L","Shift_R"):
    #    #so the user can use capital letters.
    #    return None 
    #elif not c.which and event.char in ripout:
    #    unbind( c )
    elif context.which==1:
        #no need to add text if its calltip time.
        return None 
    ind = body.index('insert-1c wordstart')
    pat = body.get(ind,'insert')+event.char 
    pat = pat.lstrip('.')

    autobox = context.autobox
    ww = list( autobox.get( 0, 'end' ) )
    lis = reducer(ww,pat)
    if len(lis)==0:return None #in this section we are selecting which item to select based on what the user has typed.
    i = ww.index(lis[0])

    autobox.select_clear( 0, 'end' ) #This section sets the current selection to match what the user has typed
    autobox.select_set( i )
    autobox.see( i )
    return 'break'
#@nonl
#@-node:ekr.20091015103601.5259:processKeyStroke
#@+node:ekr.20091015103601.5260:testForUnbind
def testForUnbind( event, context ):
    '''c in this case is a Tkinter Canvas.
      This def checks if the autobox or calltip label needs to be turned off'''

    if event.keysym in ('parenright','Control_L','Control_R', 'Escape' ):
        return True
    elif not context.which and event.char in ripout:
        return True
    return False
#@-node:ekr.20091015103601.5260:testForUnbind
#@+node:ekr.20091015103601.5261:processAutoBox
def processAutoBox(event, context , body ):
    '''This method processes the selection from the autobox.'''
    if event.keysym in("Alt_L","Alt_R"):
        return None 

    a = context.autobox.getvalue()
    if len(a)==0:return None 
    try:
        a = a[0]
        ind = body.index('insert-1c wordstart')
        pat = body.get(ind,'insert')
        pat = pat.lstrip('.')

        if a.startswith(pat):a = a[len(pat):]
        body.insert('insert',a)
        body.event_generate("<Key>")
        body.update_idletasks()
    finally:
        unbind( context )
#@-node:ekr.20091015103601.5261:processAutoBox
#@+node:ekr.20091015103601.5262:add_item
def add_item (event, context ,body,colorizer):
    '''This function will add the autobox or the calltip label.'''
    if not event.char in('.','(')or context.on:return None 
    txt = body.get('insert linestart','insert')
    txt = _reverseFindWhitespace(txt)
    if event.char!='('and not watchwords.has_key(txt):
         return None 

    if event.char=='.' and useauto:

        ww = list(watchwords[txt])
        ww.sort()
        autobox = context.autobox
        configureAutoBox( autobox, ww )
        autolist = autobox.component( 'listbox' )
        #We have to hand the listbox in, its the only thing providing accuracy of size and position.
        calculatePlace( body, autolist, context, autobox )
        autobox.select_set( 0 )
        context.which = 0 #indicates it's in autocompletion mode
        add_bindings( context, body )

    elif event.char=='(' and usecall:
        language = colorizer.language 
        if calltips.has_key(language):
            if calltips[language].has_key(txt):

                s = list(calltips[language][txt])
                t = '\n'.join(s)
                calltip = context.calltip 
                calltip.configure(text=t)
                #The calltip provides sufficient size information to calculate its place on top of the context. 
                calculatePlace(body, calltip ,context, calltip  )
                context.which = 1 #indicates it's in calltip mode

        else:
            context.on = False 
            return None 

#@-node:ekr.20091015103601.5262:add_item
#@+node:ekr.20091015103601.5263:add_bindings
def add_bindings( context, body ):
    '''This def adds bindings to the Canvas so it can work with the autobox properly.'''

    event = Tk.Event()
    event.keysym = ''

    def processAutoBoxHandler( event = event , context = context, body = body  ): 
        processAutoBox( event, context , body  )

    context.autobox.configure( selectioncommand = processAutoBoxHandler )

    def moveSelItemHandler( event, context = context ): 
        moveSelItem( event, context )

    bindings = ( ( "<Control_L>", processAutoBoxHandler ), ( "<Control_R>", processAutoBoxHandler ),
                 ( "<Alt-Up>", moveSelItemHandler, '+' ), ( "<Alt-Down>", moveSelItemHandler , '+'),
                 ( "<Alt_L>", processAutoBoxHandler ), ( "<Alt_R>", processAutoBoxHandler ) )

    def bind2( args ): context.bind( *args )
    map( bind2, bindings )

#@-node:ekr.20091015103601.5263:add_bindings
#@+node:ekr.20091015103601.5264:configureAutoBox
def configureAutoBox ( autobox ,ww):
    '''sets data and size of autobox.'''
    autobox.setlist(ww)
    lb = autobox.component('listbox')
    height = len(ww)
    if height>5:height = 5
    lb.configure(height=height)
#@-node:ekr.20091015103601.5264:configureAutoBox
#@+node:ekr.20091015103601.5265:calculatePlace
def calculatePlace (body,cwidg, context ,toBePlaced):
     '''This def determines where the autobox or calltip label goes on the canvas.
       And then it puts it on the canvas.
       body is the Tk Text instance.
       cwidg is the widget from which we derive the calculations.
       context is the parent of the cwidg, we bind the context in this function.
       toBePlaced is the widget that is placed with the calculatsions performed.'''
     try:
        x, y, lww, lwh = body.bbox('insert -1c')
        x, y = x+lww, y+lwh 
     except:
         x = 1
         y = 1
     rwidth = cwidg.winfo_reqwidth()
     rheight = cwidg.winfo_reqheight()
     if body.winfo_width()<x+rwidth:  
        x = x-rwidth 
     if y>body.winfo_height()/2:
        h2 = rheight 
        h3 = h2+lwh 
        y = y-h3 

     toBePlaced.place( x = x, y = y )
     context.on = True
     context.bind_all( '<Button>', context.do_unbind )
#@-node:ekr.20091015103601.5265:calculatePlace
#@+node:ekr.20091015103601.5266:setLanguage
def setLanguage ( pos ):
    '''This method checks a node for the current language in effect
       and accends the parent line until it finds a language.'''
    global lang 
    while pos:
        xs1 = pos.bodyString()
        dict = g.get_directives_dict(xs1)
        if dict.has_key('language'):
            lang = g.set_language(xs1,dict['language'])[0]
            break 
        pos = pos.parent()
#@-node:ekr.20091015103601.5266:setLanguage
#@+node:ekr.20091015103601.5267:newCreateControl
def newCreateControl (self,frame,parentFrame):
    '''This def is a decoration of the createControl def.  We set up the ancestory of the control so we can draw
       Widgets over the Text editor without disturbing the text.'''
    #creating background
    #We have moved to using the placer, this is simpler to use and more efficient.  We have to decorate the Tk.Text
    #widget with a constructor that creates an intermediate Frame for the Text to be placed instead of packed.  Had no
    #idea that the placer could do this so nicely.  With a couple changes in 3 places, we are using the placer!
    orig_init = Tk.Text.__init__ #We stash the original init of Tk.Text
    def pre_init( self, master, *args, **kwords ):

        context = Tk.Frame( master ) #This is what we need to put in before the text to make place work.
        orig_init( self, context, *args, **kwords )

    Tk.Text.__init__ = pre_init #We restore the original init of Tk.Text
    body = orig_CreateControl(self,frame, parentFrame )#orig_CreatControl is the method this def decorates
    Tk.Text.__init__ = orig_init

    context = body.master #This is the Frame we created to intercept the passed in master.
    context.pack( expand = 1, fill = 'both', after = frame.bodyBar )  #We have to add it to the environment, since we pass on it in the __init__   
    body.place( relwidth = 1.0, relheight = 1.0 )
    body.commander = self.c #used in watcher
    context.on = False #determines if the system is autocompleting or calltiping
    addAutoboxAndCalltipWidgets( context )
    #These used to be lambdas, but I think this is clearer.
    def processKeyStrokeHandler( event, context= context, body = body ): 
        processKeyStroke( event, context, body )
    def addItemHandler( event, context = context, body = body, colorizer = frame.body ): 
        add_item( event, context, body, colorizer.getColorizer() )

    for z in ( watcher, processKeyStrokeHandler, addItemHandler ):
        context.bind( "<Key>", z, '+' )

    ignore = [] #ignore items added to this list when a Button event occurs.
    if hasattr( context, 'autobox' ):
        ignore.append(  context.autobox.component( 'listbox' ) )
        ignore.append( context.autobox.component( 'vertscrollbar' ) )
    def do_unbind( event ):
        '''This def is for doing the unbind on any <Button> events.
           It only is in effect when the autobox or calltip label are showing.'''            
        if event.widget not in ignore: #This ensures a click or scroll in the autobox takes effect.
                unbind( context )

    context.do_unbind = do_unbind

    #This part protects this plugin from others that use Alt-Up, Alt-Down, an example being temacs.py
    #The frame didnt seem to work.  Im assuming it was not appropiate enought in the bindtag order for the event.
    context.block_alt = Tk.Entry()
    def block_alt( event ):
        '''This def blocks specific keyboard commands from reaching the Text editor.  'breaking' in
           the context does not occur before the event reaches the Text editor, so it has no effect'''
        if context.on: return 'break'
    for z in ( '<Alt-Up>', '<Alt-Down>' ): context.block_alt.bind( z, block_alt ) 

    #set the bindtags for the body, protects the autocompleter from other plugins unbinding this plugins bindings.
    ctags = []
    ctags.append( context.bindtags()[ 0 ] )
    ctags.append( context.block_alt.bindtags()[ 0 ] )
    ctags.extend( body.bindtags() ) 
    body.bindtags( tuple( ctags ))

    return body  







#@-node:ekr.20091015103601.5267:newCreateControl
#@+node:ekr.20091015103601.5268:addAutoboxAndCalltipWidgets
def addAutoboxAndCalltipWidgets( context ):
    '''This builds the autobox and the calltip label for the editor.
      It should be called once for every editor created.'''

    call_pack_forget = []

    if useauto:
        context.autobox = Pmw.ScrolledListBox( context ,hscrollmode='none',
                                         listbox_selectbackground='#FFE7C6',
                                         listbox_selectforeground='blue',
                                         listbox_background='white',
                                         listbox_foreground='blue',
                                         vertscrollbar_background='#FFE7C6',
                                         vertscrollbar_width=10)
        call_pack_forget.append( context.autobox.component( 'hull' ) )

    if usecall:            
        context.calltip = Tk.Label(context,background='lightyellow',
                         foreground='black')
        call_pack_forget.append( context.calltip )

    def clean_editor( ca = call_pack_forget ):#This def makes removing the autobox or calltip label easy.  No need for an intermediate variable like 'current'.
        for z in ca: z.place_forget()
    context.clean_editor = clean_editor

#@-node:ekr.20091015103601.5268:addAutoboxAndCalltipWidgets
#@+node:ekr.20091015103601.5269:onOpenWindow
def onOpenWindow ():
    #what does this do?
    c = keywords.get("c")
    if haveseen.has_key(c):
        return 

    autocompleter = autocomplet(c)
#@nonl
#@-node:ekr.20091015103601.5269:onOpenWindow
#@-others
#@nonl
#@-node:ekr.20091015103601.5232:@thin autocompleter.py
#@-leo
