#@+leo-ver=4-thin
#@+node:mork.20041013092542.1:@thin usetemacs.py
#@<< docstring >>
#@+node:ekr.20050513171201:<< docstring >>
'''usetemacs is a Leo plugin that patches the temacs modules Emacs emulation
into the standard Leo Tkinter Text editor.

Create a usetemacs.ini file to rebind shortcuts that conflict with those in your
leoSettings.leo file. There are many such conflicts. For example, Ctrl-s is
incremental search forward here but by default it is Save in Leo. 

See Help->Temacs Help for a complete listing of commands and keystrokes.
'''
#@nonl
#@-node:ekr.20050513171201:<< docstring >>
#@nl

#@@language python
#@@tabwidth -4

#@<< imports >>
#@+node:ekr.20041106100326:<< imports >>
import leoGlobals as g
import leoNodes
import leoPlugins
import leoTkinterFrame

try:
    import Tkinter as Tk
    import ScrolledText
    import tkFont
except:
    Tk = None

import ConfigParser
import os
import sys
import weakref

try:
    pth = os.path.split( g.app.loadDir ) 
    ppath = pth[ 0 ] + os.sep + 'plugins'
    ext_path = pth[ 0 ] + os.sep + 'plugins' + os.sep + 'temacs_ext'
    try:
        if not os.path.exists( ext_path ):
            os.mkdir( ext_path )
    except Exception, x:
        g.es( "Attempt to create %s failed because of %s" %( ext_path, x ) )
    sys.path.append( ppath )
    sys.path.append( ext_path )
    temacs = __import__( 'temacs', globals(), locals())
except Exception, x:
    g.es( "temacs not loadable. Aborting load of usetemacs because of: " + str( x ))
    temacs = None
#@-node:ekr.20041106100326:<< imports >>
#@nl
#@<< globals >>
#@+node:mork.20041013092542.2:<< globals >>


labels = weakref.WeakKeyDictionary()
editors = weakref.WeakKeyDictionary()
haveseen = weakref.WeakKeyDictionary()
extensions = []
new_keystrokes = {}
leocommandnames = None
#@nonl
#@-node:mork.20041013092542.2:<< globals >>
#@nl
__version__ = '.57'
#@<<version history>>
#@+node:mork.20041101132349:<<version history>>
#@+at 
# 
# .5 -- fixed problem with spurious whitespace being added in some of the 
# paste commands when Return was entered.  This was
#       because Leo is programmed to indent after Enter is pressed.  We 
# decorate the OnBodyKey with usetemacs modifyOnBodyKey.
#    -- made transitions to temacs.Emacs class
#    -- Help text can now be searched.  Search is initiated by either typing 
# Return in the Entry or pressing the go button.
#    -- Set it up so when the Text widget has all of its text deleted via a 
# call to delete '1.0', 'end', this calls
#       the StopControlX method of the Emacs object.  This is equivilant of 
# pressing Control-G.
#    -- Added ability to load temacs.Emacs extensions
#    -- Added ability to change default key bindings( in alpha stage ).
#    -- Created example Emacs extension.
#    -- Added ability for user to see each node in the outline as a buffer.  
# There are methods in temacs such as
#       append-to-buffer, copy-to-buffer, etc... that needs a name and some 
# supplied functionality to do its work.
#       usetemacs does this for the Emacs instance.  Note: if a group of nodes 
# have the same name, then only one will be viewable
#       by the Emacs instance.  This might be enhanced in the future to 
# include all headlines.
#       I would not recommend 'list-buffers' if you have a large outline.  
# This will have to be enhanced in the future as well.
#    -- Removed all references to Pmw in code( still exists in comments ).  
# Reports of some weirdness with the string.atoi and how
#       it was behaving in Pmw.  This helps lower the bar of entry to this.  I 
# have replaced the megawidgets with items like
#       ScrolledText and a minibuffer composed of a Frame, a Frame in this 
# Frame, and 2 labels.
#    -- folded in changes from .4 that could be detected
# 
# .51
# .52 EKR: Minor style changes.
# .53 EKR: Use __name__ in .plugin_signon
# .55
#     --added a def that adds all the Leo Commands to the Emacs instance, in 
# command addLeoCommands.  I no longer need to
#     remember how to summon the find panel, its done via Alt-x 'find panel'.  
# This was a very good use of the extension mechanism
#     that was put into place in .5.  I should note that there are a couple I 
# left out like Recent Files, and End Edit Headline,
#     since they didnt seem to functional( i.e. no good way to use them within 
# the Alt-x mechanism).
#     --changed the location of where text appears in the minibuffer, it now 
# always starts from the left instead of the center.
#     This is what Emacs does, and its less disorienting.
#     --added a dialog to show up if there are multiple nodes with the same 
# name.  This gives the user the ability to select a node
#     in its numerical position in the graph, from 1 to N.  Im still surprised 
# that this works as quick as it does, more power to the
#     graph!
#     --added Leo Commands to Temacs Help, good to see which Leo commands you 
# can execute.
# .56 EKR:
#     - Removed 'start2' hook and haveseen dict.
#     - Added init function.
# .57 EKR:
#     - Added global orig_Bindings,orig_OnBodyKey to init().
#     - Removed writeNewDerivedFiles writeOldDerivedFiles and 'apply settings' 
# commands.
#     - Changed c.findPanel to c.showFindPanel.
#     - Changed leoConfig.txt to leoSettings.leo in docstring.
#@-at
#@-node:mork.20041101132349:<<version history>>
#@nl
#@<< documentation >>
#@+node:ekr.20041106100326.1:<< documentation >>
#@+others
#@+node:mork.20041104100514:future directions
#@+at
# 
# Hard to say at this point.  usetemacs is essentially the glue between Leo 
# and temacs.py.  Anytime
# temacs needs some machinery from the surrounding environment, usetemacs.py 
# is supposed to supply it.
# temacs development drives this development.
#@-at
#@-node:mork.20041104100514:future directions
#@+node:mork.20041101204659:adding Emacs extensions via usetemacs
#@+at
# 
# to begin to understand how to write an Emacs extension see temacs.py section 
# 'how to write an Emacs extension'.
# 
# usetemacs will look for a file called usetemacs.ini
# 
# It will open this file and look for a sections called [ extensions ]
# 
# every option under this section will act as an indicator to import a module.
# 
# For example:
# [ extensions ]
# 1=anExtension
# 
# The module anExtension.py must be importable by usetemacs.
# 
# -----
# usetemacs will load anExtension as a module.  For each Emacs object created 
# it will
# call the modules getExtensions() method which should return a dictionary 
# containing:
#     a. keys that are strings.  These are the names that will be added to the 
# Alt-x command in Emacs.
#     b. functions.  These should not be methods, as they become methods when 
# added to Emacs.
#     for example:
#         module test.py:
#         def power( self, event ):
#             print 'power'
#         def getExtensions():
#             return { 'power' : power }
#     upon loading by usetemacs, every Emacs instance will have 'power' added 
# as an Alt-x command which will call
#     the power function( method after adding ).  The extension write should 
# not worry about the name of the function,
#     they should only worry about the name that they want to access the 
# function-method by.  It is possible to overwrite
#     a default Alt-x method if the same name is used.
# -----
# 
# To test an Emacs extensions try out the exampleTemacsExtension.py with this 
# mechanism.
# 
#@-at
#@-node:mork.20041101204659:adding Emacs extensions via usetemacs
#@+node:mork.20041104100856:where to put your temacs-Emacs Python extensions
#@+at
# In the plugins directory there should be a subdirectory called: temacs_ext.
# usetemacs will add that directory to the import list.
# 
# 
# This keeps temacs extensions separate from regular plugins.
# 
# usetemacs creates this directory for the user if it doesn't alread exist 
# upon startup.
# 
#@-at
#@-node:mork.20041104100856:where to put your temacs-Emacs Python extensions
#@+node:mork.20041102102111:change Emacs keystrokes via configuration
#@+at
# 
# usetemacs allows the user to change keystrokes in the Emacs instances via 
# the ustemacs.ini file.
# 
# the section should be called [ newkeystrokes ].
# 
# To reconfigure a keystroke or add a keystroke, under the section add for 
# example:
# Alt-q=Alt-f
# 
# 
# 
# this will rebind Alt-q to what Alt-f does.
# 
# ------
# note this feature is largely untested and will most likely need work.
# 
#@-at
#@-node:mork.20041102102111:change Emacs keystrokes via configuration
#@+node:mork.20041102094131:usetemacs design
#@+at 
# 
# usetemacs depends on temacs and Leo like so:
# temacs.py  <------ usetemacs.py -------> Leo
# 
# temacs can function by itself.
# Leo can function by itself.
# 
# usetemacs brings the two together.
# 
# Its the glue between the temacs module and Leo.  Leo doesn't need usetemacs 
# to function, temacs doesn't need usetemacs to be used.
# But if temacs.py and Leo are to work together usetemacs.py must be employed 
# as a plugin for Leo.
# 
# It performs several helpful functions for temacs and Leo:
# 
# 1. Protects against bad whitespace being added because of a Return key 
# press.
# 2. Does a keyboardQuit if a new node is selected.
# 3. Configures temacs with temacs extensions.
# 4. Adds abbreviations and macros to Emacs instances
# 5. Configures Emac instances with functions that allow it to treat nodes as 
# buffers.
#@-at
#@nonl
#@-node:mork.20041102094131:usetemacs design
#@+node:mork.20041102094341:a note on loading temacs
#@+at 
# 
# temacs.py prior to the .4 version needed to be installed so that it could be 
# loaded anywhere from a python instance.
# Now all the user needs to do is have temacs.py in the same plugins directory 
# of the usetemacs plugin.  The plugin should
# be able to load the module if done in this way.
#@-at
#@nonl
#@-node:mork.20041102094341:a note on loading temacs
#@-others
#@@nocolor
#@nonl
#@-node:ekr.20041106100326.1:<< documentation >>
#@nl

#@+others
#@+node:ekr.20050311155753:init
def init ():
    
    ok = temacs and Tk and not g.app.unitTesting
    
    if ok:
        if g.app.gui is None: 
            g.app.createTkGui(__file__)
    
        if g.app.gui.guiName() == "tkinter":
            global orig_Bindings,orig_OnBodyKey
            #@            << override createBindings and onBodyKey >>
            #@+node:ekr.20041106100326.2:<< override createBindings and onBodyKey >>
            orig_Bindings = leoTkinterFrame.leoTkinterBody.createBindings
            leoTkinterFrame.leoTkinterBody.createBindings = initialise() #createBindings
            
            orig_OnBodyKey = leoTkinterFrame.leoTkinterBody.onBodyKey
            leoTkinterFrame.leoTkinterBody.onBodyKey = modifyOnBodyKey
            #@nonl
            #@-node:ekr.20041106100326.2:<< override createBindings and onBodyKey >>
            #@nl
            loadConfig()
            g.plugin_signon(__name__)
            leoPlugins.registerHandler( ('open2', "new") , addMenu )
            
    return ok
#@nonl
#@-node:ekr.20050311155753:init
#@+node:mork.20041013092542.3:utTailEnd
def utTailEnd( buffer , frame ):
    '''A method that Emacs will call with its _tailEnd method'''
    buffer.event_generate( '<Key>' )
    buffer.update_idletasks()
    return 'break'
#@-node:mork.20041013092542.3:utTailEnd
#@+node:mork.20041013092542.6:seeHelp
def seeHelp():
    '''Opens a Help dialog that shows the Emac systems commands and keystrokes'''
    tl = Tk.Toplevel()
    ms = tl.maxsize()
    tl.geometry( '%sx%s+0+0' % ( ( ms[ 0 ]/3 ) *2 , ms[ 1 ]/2 )) #half the screen height, half the screen width
    tl.title( "Temacs Help" )
    #fixedFont = Pmw.logicalfont( 'Fixed' )
    fixedFont = tkFont.Font( family = 'Fixed', size = 14 )
    #t = Pmw.ScrolledText( tl , text_font = fixedFont , text_background = 'white', hscrollmode = 'static', text_wrap='none')
    tc = ScrolledText.ScrolledText( tl, font = fixedFont, background = 'white', wrap = 'word' )
    sbar = Tk.Scrollbar( tc.frame, orient = 'horizontal' )
    sbar.configure( command = tc.xview )
    tc.configure( xscrollcommand = sbar.set )
    sbar.pack( side = 'bottom', fill = 'x' )
    for z in tc.frame.children.values():
        sbar.pack_configure( before = z )
    #t.settext( temacs.Emacs.getHelpText() )
    tc.insert( '1.0', temacs.Emacs.getHelpText() )
    lc='''\n---------Leo Commands-----------\n'''
    tc.insert( 'end', lc )
    leocommandnames.sort()
    lstring = '\n'.join( leocommandnames )
    tc.insert( 'end', lstring )
    def clz( tl = tl ):
        tl.withdraw()
        tl.destroy()
    #g = Pmw.Group( tl )
    g = Tk.Frame( tl )
    g.pack( side = 'bottom' )
    tc.pack( side = 'top' ,expand = 1, fill = 'both')
    e = Tk.Label( g, text = 'Search:' )
    e.pack( side = 'left' )
    #ef = Pmw.EntryField( g.interior() , 
    #                     labelpos = 'w', 
    #                     label_text = 'Search:' ,
    #                     entry_background = 'white',
    #                     entry_foreground = 'blue')
    #ef.pack( side = 'left' )
    ef = Tk.Entry( g, background = 'white', foreground = 'blue' )
    ef.pack( side = 'left' )
    def search():
        
        #stext = ef.getvalue()
        stext = ef.get()
        #tc = t.component( 'text' )
        tc.tag_delete( 'found' )
        tc.tag_configure( 'found', background = 'red' )
        ins = tc.index( 'insert' )
        ind = tc.search( stext, 'insert', stopindex = 'end', nocase = True )
        if not ind:
            ind = tc.search( stext, '1.0', stopindex = 'end', nocase = True )
        if ind:
            tc.mark_set( 'insert', '%s +%sc' % ( ind , len( stext ) ) )
            tc.tag_add(  'found', 'insert -%sc' % len( stext ) , 'insert' )
            tc.see( ind )
        
    go = Tk.Button( g , text = 'Go', command = search )
    go.pack( side = 'left' )
    b = Tk.Button( g  , text = 'Close' , command = clz )
    b.pack( side = 'left' )
    def watch( event ):
        search()
        
    #ef.component( 'entry' ).bind( '<Return>', watch )
    ef.bind( '<Return>', watch )
    #fixedFont = Pmw.logicalfont( 'Fixed' )
    #t = Pmw.ScrolledText( tl , text_font = fixedFont , text_background = 'white', hscrollmode = 'static', text_wrap='none')
    #t.pack( expand = 1, fill = 'both')
    #t.settext( temacs.Emacs.getHelpText() )
#@-node:mork.20041013092542.6:seeHelp
#@+node:mork.20041013092542.5:addMenu
def addMenu( tag, keywords ):
    '''Adds the Temacs Help option to Leo's Help menu'''
    
    c = keywords.get('c')
    if not c: return

    men = c.frame.menu.getMenu( 'Help' )
    men.add_separator()
    men.add_command( label = 'Temacs Help', command = seeHelp )
#@nonl
#@-node:mork.20041013092542.5:addMenu
#@+node:mork.20041101124927:modifyOnBodyKey
def modifyOnBodyKey( self, event ):
    '''stops Return and Tab from being processed if the Emacs instance has state.'''
    if event.char.isspace(): 
        Emacs = temacs.Emacs.Emacs_instances[ event.widget ]   
        if Emacs.mcStateManager.hasState():
           return None
    return orig_OnBodyKey( self, event )
#@-node:mork.20041101124927:modifyOnBodyKey
#@+node:mork.20041101205414:watchDelete
def watchDelete(  i, j = None, Emacs = None , orig_del = None , Text = None ):
    '''Watches for complete text deletion.  If it occurs, turns off all state in the Emacs instance.'''
    if j:
        if i == '1.0' and j == 'end':
            event = Tk.Event()
            event.widget = Text
            Emacs.keyboardQuit( event )
    return orig_del( i, j )
#@nonl
#@-node:mork.20041101205414:watchDelete
#@+node:mork.20041102094928:changeKeyStrokes
def changeKeyStrokes( Emacs, tbuffer ):
    
    for z in new_keystrokes.keys():
        Emacs.reconfigureKeyStroke( tbuffer, z, new_keystrokes[ z ] )
#@-node:mork.20041102094928:changeKeyStrokes
#@+node:mork.20041101210722:addTemacsAbbreviations
def addTemacsAbbreviations( Emacs ):
    '''Adds abbreviatios and kbd macros to an Emacs instance'''
    pth = os.path.split( g.app.loadDir ) 
    aini = pth[ 0 ] + os.sep + 'plugins' + os.sep
    if os.path.exists( aini + r'usetemacs.kbd' ):
        f = file( aini +  r'usetemacs.kbd', 'r' )
        Emacs._loadMacros( f )
    if os.path.exists( aini + r'usetemacs.abv' ):
        f = file( aini + r'usetemacs.abv', 'r' )
        Emacs._readAbbrevs( f )
        

#@-node:mork.20041101210722:addTemacsAbbreviations
#@+node:mork.20041101191351:loadConfig
def loadConfig():
    '''Loads Emacs extensions and new keystrokes to be added to Emacs instances'''
    pth = os.path.split(g.app.loadDir)   
    aini = pth[0]+r"/plugins/usetemacs.ini"
    if os.path.exists( aini ):
        
        cp = ConfigParser.ConfigParser()
        cp.read( aini )
        section = None
        for z in cp.sections():
            if z.strip() == 'extensions':
                section = z
                break
        
        if section:
            for z in cp.options( section ):
                extension = cp.get( section, z )
                try:
                    ex = __import__( extension )
                    extensions.append( ex )
                except Exception, x:
                    g.es( "Could not load %s because of %s" % ( extension, x ), color = 'red' )
                
        kstroke_sec = None
        for z in cp.sections():
            if z.strip() == 'newkeystrokes':
                kstroke_sec = z
                break
        if kstroke_sec:
            for z in cp.options( kstroke_sec ):
                new_keystrokes[ z.capitalize() ] = cp.get( kstroke_sec, z )




#@-node:mork.20041101191351:loadConfig
#@+node:mork.20041101202945:addTemacsExtensions
def addTemacsExtensions( Emacs ):
    '''Adds extensions to Emacs parameter.'''
    for z in extensions:
            try:
                if hasattr( z, 'getExtensions' ):
                    ex_meths = z.getExtensions()
                    for x in ex_meths.keys():
                        Emacs.extendAltX( x, ex_meths[ x ] )
                else:
                    g.es( 'Module %s does not have a getExtensions function' % z , color = 'red' )
            except Exception, x:
                g.es( 'Could not add extension because of %s' % x, color = 'red' )
#@-node:mork.20041101202945:addTemacsExtensions
#@+node:mork.20041103160433:setBufferGetters and Setters
tnodes = {}
positions =  {}
def setBufferInteractionMethods( c, emacs, buffer ):
    '''This function configures the Emacs instance so that
       it can see all the nodes as buffers for its buffer commands.'''
    def buildBufferList(): #This builds a buffer list from what is in the outline.  Worked surprisingly fast on LeoPy.
        if not tnodes.has_key( c ): #I was worried that speed factors would make it unusable.
            tnodes[ c ] = {}
        tdict = tnodes[ c ]
        pos = c.rootPosition()
        utni = pos.allNodes_iter()
        bufferdict = {}
        tdict.clear()
        positions.clear()
        for z in utni:
        
           t = z.v.t
           if positions.has_key( t.headString ):
            positions[ t.headString ].append( z.copy() )
           else:
            positions[ t.headString ] = [ z.copy() ]#not using a copy seems to have bad results.
           #positions[ t.headString ] = z
        
           bS = ''
           if t.bodyString: bS = t.bodyString
 
           
           bufferdict[ t.headString ] = bS
           tdict[ t.headString ] = t 
        
        return bufferdict
        
    def setBufferData( name, data ):
        
        data = unicode( data )
        tdict = tnodes[ c ]
        if tdict.has_key( name ):
            tdict[ name ].bodyString = data
            
    def gotoNode( name ):
        
        c.beginUpdate()
        if positions.has_key( name ):
            posis = positions[ name ]
            if len( posis ) > 1:
                tl = Tk.Toplevel()
                #tl.geometry( '%sx%s+0+0' % ( ( ms[ 0 ]/3 ) *2 , ms[ 1 ]/2 ))
                tl.title( "Select node by numeric position" )
                fr = Tk.Frame( tl )
                fr.pack()
                header = Tk.Label( fr, text='select position' )
                header.pack()
                lbox = Tk.Listbox( fr, background='white', foreground='blue' )
                lbox.pack()
                for z in xrange( len( posis ) ):
                    lbox.insert( z, z + 1 )
                lbox.selection_set( 0 )
                def setPos( event ):
                    cpos = int( lbox.nearest( event.y ) )
                    tl.withdraw()
                    tl.destroy()
                    if cpos != None:
                        gotoPosition( c, posis[ cpos ] )
                lbox.bind( '<Button-1>', setPos )
                geometry = tl.geometry()
                geometry = geometry.split( '+' )
                geometry = geometry[ 0 ]
                width = tl.winfo_screenwidth()/3
                height = tl.winfo_screenheight()/3
                geometry= '+%s+%s' %( width,height )
                tl.geometry( geometry )
            else:
                pos = posis[ 0 ]
                gotoPosition( c, pos )
        else:
            pos2 = c.currentPosition()
            tnd = leoNodes.tnode( '', name )
            pos = pos2.insertAfter( tnd )
            gotoPosition( c, pos )
        #c.frame.tree.expandAllAncestors( pos )
        #c.selectPosition( pos )
        #c.endUpdate()
    
    def deleteNode( name ):
        
        c.beginUpdate()
        if positions.has_key( name ):
            pos = positions[ name ]
            cpos = c.currentPosition()
            pos.doDelete( cpos )
        c.endUpdate()
    
    def renameNode( name ):
    
        c.beginUpdate()
        pos = c.currentPosition()
        pos.setHeadString( name )
        c.endUpdate()

        
    emacs.setBufferListGetter( buffer, buildBufferList ) #This gives the Emacs instance the ability to get a buffer list
    emacs.setBufferSetter( buffer, setBufferData )# This gives the Emacs instance the ability to set a tnodes bodyString
    emacs.setBufferGoto( buffer, gotoNode )# This gives the Emacs instance the ability to jump to a node
    emacs.setBufferDelete( buffer, deleteNode )# This gives the Emacs instance the ability to delete a node
    emacs.setBufferRename( buffer, renameNode )# This gives the Emacs instance the ability to rename the current node

#@-node:mork.20041103160433:setBufferGetters and Setters
#@+node:mork.20041213112640:gotoPosition
def gotoPosition( c, pos ):
    c.frame.tree.expandAllAncestors( pos )
    c.selectPosition( pos )
    c.endUpdate()
    
#@-node:mork.20041213112640:gotoPosition
#@+node:mork.20041104145603:initialise
def initialise():
    '''This fuction sets up the module'''
    def createBindings (self,frame): 
     
        if not labels.has_key( frame ):
            #group = Pmw.Group( frame.split2Pane2, tag_text = 'mini buffer' )
            group = Tk.Frame( frame.split2Pane2 , 
                              relief = 'ridge', 
                              borderwidth = 3 )
            f2 = Tk.Frame( group )
            f2.pack( side = 'top', fill = 'x' )
            gtitle = Tk.Label( f2, 
                               text = 'mini-buffer' , 
                               justify = 'left' , 
                               anchor = 'nw',
                               foreground = 'blue',
                               background = 'white' )
            #gtitle.pack( side = 'top', fill ='x' )
            #gtitle.place( x = 5, y = 10 )
            group.pack( side = 'bottom', fill = 'x', expand = 1 )
            #gtitle.place( x = 0, y = 0 , relwidth = 1.0, relheight = 1.0 )
            #gtitle.grid( columnspan = 5 )
            for z in frame.split2Pane2.children.values():
                group.pack_configure( before = z )
            label = Tk.Label( group , 
                              relief = 'groove',
                              justify = 'left',
                              anchor='w',
                               )
            label.pack( side = 'bottom', fill = 'both', expand = 1, padx = 2, pady = 2 )   
            gtitle.pack( side = 'left' ) #, fill ='x' )
            #label.place( x = 10, y = 10 )
            #label.grid( column =2, columnspan = 15, rowspan = 3 )
            labels[ frame ] = label  
        else:
            label = labels[ frame ]
            
        orig_Bindings( self, frame )
        Emacs = temacs.Emacs( frame.bodyCtrl, label, useGlobalKillbuffer = True, useGlobalRegisters = True )
        Emacs.setUndoer( frame.bodyCtrl, self.c.undoer.undo ) 
        Emacs.setTailEnd( frame.bodyCtrl, lambda buffer, frame = frame: utTailEnd( buffer, frame ) )
        Emacs.setShutdownHook( self.c.close )
        addTemacsExtensions( Emacs )
        addTemacsAbbreviations( Emacs )
        addLeoCommands( self.c, Emacs )
        changeKeyStrokes( Emacs, frame.bodyCtrl )
        setBufferInteractionMethods( self.c, Emacs, frame.bodyCtrl )
                
        orig_del = frame.bodyCtrl.delete
        def wD( i, j = None, Emacs = Emacs, orig_del = orig_del, Text = frame.bodyCtrl ):
                return watchDelete( i,j, Emacs, orig_del, Text )
        frame.bodyCtrl.delete = wD

    return createBindings
#@nonl
#@-node:mork.20041104145603:initialise
#@+node:mork.20041204141826:addLeoCommands
def addLeoCommands( c, emacs ):
    
    global leocommandnames
    f = c.frame
    
    commands = {
    'new': c.new,
    'open': c.open,
    'openWith': c.openWith,
    'close': c.close,
    'save': c.save,
    'saveAs': c.saveAs,
    'saveTo': c.saveTo,
    'revert': c.revert,
    'readOutlineOnly': c.readOutlineOnly,
    'readAtFileNodes': c.readAtFileNodes,
    'importDerivedFile': c.importDerivedFile,
    #'writeNewDerivedFiles': c.writeNewDerivedFiles,
    #'writeOldDerivedFiles': c.writeOldDerivedFiles,
    'tangle': c.tangle,
    'tangle all': c.tangleAll,
    'tangle marked': c.tangleMarked,
    'untangle': c.untangle,
    'untangle all': c.untangleAll,
    'untangle marked': c.untangleMarked,
    'export headlines': c.exportHeadlines,
    'flatten outline': c.flattenOutline,
    'import AtRoot': c.importAtRoot,
    'import AtFile': c.importAtFile,
    'import CWEB Files': c.importCWEBFiles,
    'import Flattened Outline': c.importFlattenedOutline,
    'import Noweb Files': c.importNowebFiles,
    'outline to Noweb': c.outlineToNoweb,
    'outline to CWEB': c.outlineToCWEB,
    'remove sentinels': c.removeSentinels,
    'weave': c.weave,
    'delete': c.delete,
    'execute script': c.executeScript,
    'go to line number': c.goToLineNumber,
    'set font': c.fontPanel,
    'set colors': c.colorPanel,
    'show invisibles': c.viewAllCharacters,
    'preferences': c.preferences,
    'convert all blanks': c.convertAllBlanks,
    'convert all tabs': c.convertAllTabs,
    'convert blanks': c.convertBlanks,
    'convert tabs': c.convertTabs,
    'indent': c.indentBody,
    'unindent': c.dedentBody,
    'reformat paragraph': c.reformatParagraph,
    'insert time': c.insertBodyTime,
    'extract section': c.extractSection,
    'extract names': c.extractSectionNames,
    'extract': c.extract,
    'match bracket': c.findMatchingBracket,
    'find panel': c.showFindPanel, ## c.findPanel,
    'find next': c.findNext,
    'find previous': c.findPrevious,
    'replace': c.replace,
    'replace then find': c.replaceThenFind,
    'edit headline': c.editHeadline,
    'toggle angle brackets': c.toggleAngleBrackets,
    'cut node': c.cutOutline,
    'copy node': c.copyOutline,
    'paste node': c.pasteOutline,
    'paste retaining clone': c.pasteOutlineRetainingClones,
    'hoist': c.hoist,
    'de-hoist': c.dehoist,
    'insert node': c.insertHeadline,
    'clone node': c.clone,
    'delete node': c.deleteOutline,
    'sort children': c.sortChildren,
    'sort siblings': c.sortSiblings,
    'demote': c.demote,
    'promote': c.promote,
    'move right': c.moveOutlineRight,
    'move left': c.moveOutlineLeft,
    'move up': c.moveOutlineUp,
    'move down': c.moveOutlineDown,
    'unmark all': c.unmarkAll,
    'mark clones': c.markClones,
    'mark': c.markHeadline,
    'mark subheads': c.markSubheads,
    'mark changed items': c.markChangedHeadlines,
    'mark changed roots': c.markChangedRoots,
    'contract all': c.contractAllHeadlines,
    'contract node': c.contractNode,
    'contract parent': c.contractParent,
    'expand to level 1': c.expandLevel1,
    'expand to level 2': c.expandLevel2,
    'expand to level 3': c.expandLevel3,
    'expand to level 4': c.expandLevel4,
    'expand to level 5': c.expandLevel5,
    'expand to level 6': c.expandLevel6,
    'expand to level 7': c.expandLevel7,
    'expand to level 8': c.expandLevel8,
    'expand to level 9': c.expandLevel9,
    'expand prev level': c.expandPrevLevel,
    'expand next level': c.expandNextLevel,
    'expand all': c.expandAllHeadlines,
    'expand node': c.expandNode,
    'check outline': c.checkOutline,
    'dump outline': c.dumpOutline,
    'check python code': c.checkPythonCode,
    'check all python code': c.checkAllPythonCode,
    'pretty print python code': c.prettyPrintPythonCode,
    'pretty print all python code': c.prettyPrintAllPythonCode,
    'goto parent': c.goToParent,
    'goto next sibling': c.goToNextSibling,
    'goto previous sibling': c.goToPrevSibling,
    'goto next clone': c.goToNextClone,
    'goto next marked': c.goToNextMarkedHeadline,
    'goto next changed': c.goToNextDirtyHeadline,
    'goto first': c.goToFirstNode,
    'goto last': c.goToLastNode,
    "go to prev visible":c.selectVisBack,
    "go to next visible" : c.selectVisNext,
    "go to prev node" : c.selectThreadBack,
    "go to next node" : c.selectThreadNext,
    'about leo...': c.about,
    #'apply settings': c.applyConfig,
    'open LeoConfig.leo': c.leoConfig,
    'open LeoDocs.leo': c.leoDocumentation,
    'open online home': c.leoHome,
    'open online tutorial': c.leoTutorial,
    'open compare window': c.openCompareWindow,
    'open Python window': c.openPythonWindow,
    "equal sized panes": f.equalSizedPanes,
    "toggle active pane": f.toggleActivePane,
    "toggle split direction": f.toggleSplitDirection,
    "resize to screen": f.resizeToScreen,
    "cascade": f.cascade,
    "minimize all": f.minimizeAll,
    }
    
    for z in commands.keys():
        #z2 = 'leo-%s' % z -- no need to do this, Leos command names dont clash with temacs so far
        def coverdef( self, event, command=commands[ z ] ):
            command()
            emacs.keyboardQuit( event )
            
        emacs.extendAltX( z, coverdef )
    leocommandnames = commands.keys()
    
    






























































#@-node:mork.20041204141826:addLeoCommands
#@-others

#@<<exampleTemacsExtension.py>>
#@+node:mork.20041102091309:<<exampleTemacsExtension.py>>
#@+at
# 
# '''An example of a temacs Extension.  To test example:
#     1. Create usetemacs.ini file.
#     2. Make an [ extensions ] section.
#     3. put:
#        1=exampleTemacsExtension
#     When Leo starts,
#     select a set of lines
#     type Alt-x
#     the format-selection-as-list and hit Enter( or type format and hit tab, 
# the autocompletion will work ).
#     After typing Enter you should see you selection indented and each line 
# prefixed with an ascending number.'''
# 
# 
# def formatSelectionAsList( self, event ):
#     '''This function indents and prepends a number to a selection of text'''
#     try: #We guard against there not being anything selected, which throws 
# an Exception in this block.
#         tbuffer = event.widget # call the Text instance tbuffer as in Emacs 
# class.
#         self.indentRegion( event ) # use the Emacs instances indentRegion 
# method to do initial formatting.
#         start = tbuffer.index( 'sel.first linestart' )
#         start = tbuffer.search( '\w', start, regexp = True, stopindex = '%s 
# lineend' % 'sel.last' )
#         if not start:
#             return self.keyboardQuit( event )
#         end = tbuffer.index( 'sel.last' )
#     except Exception, x:
#         return self.keyboardQuit( event )
#     r1, c1 = start.split( '.' )
#     r1, c1 = int( r1 ), int( c1 )
#     r2, c2 = end.split( '.' )
#     r2 = int( r2 )
#     amount = r2 - r1
#     for z in xrange( amount + 1 ):
#         tbuffer.insert( '%s.%s' % ( r1, c1 ), '%s. ' % ( z + 1 ))
#         r1 = r1 + 1
#     self.keyboardQuit( event ) # this turns off the state and sets things to 
# normal
#     return self._tailEnd( tbuffer ) # this calls the _tailEnd method, which 
# when used with usetemacs will ensure that the text sticks.
# 
# def getExtensions():
# 
#     return { 'format-selection-as-list': formatSelectionAsList } #We return 
# the one function in this module.
#@-at
#@nonl
#@-node:mork.20041102091309:<<exampleTemacsExtension.py>>
#@nl
#@<<usetemacs.ini example>>
#@+node:mork.20041102092057:<<usetemacs.ini example>>
#@+at
# 
# #An example usetemacs .ini file
# [ extensions ]
# 1=exampleTemacsExtension
# 
# [ newkeystrokes ]
# #Alt-q=Alt-f
#@-at
#@nonl
#@-node:mork.20041102092057:<<usetemacs.ini example>>
#@nl
#@nonl
#@-node:mork.20041013092542.1:@thin usetemacs.py
#@-leo
