#@+leo-ver=4-thin
#@+node:mork.20041030164547:@thin temacs.py
'''temacs is a binding module for the Tkinter Text widget.

Using the setBufferStrokes def will bind callbacks to the widget.'''

#@@language python
#@@tabwidth -4

__version__ = ".55"
#@<< version history >>
#@+node:mork.20041101100635:<<version history>>
#@+at
# 
# .5
#        This was a fairly major shift for temacs.
#    -- Changed structure from pure functional to Object Oriented.  Emacs is 
# the central class in the temacs package now.
#       The changes wrought by this are quite extensive.
#    -- worked on complicated control logic, turned some parts into Objects 
# that are state Handlers and Managers
#    -- fixed a bug in block indentation.  If the first line was blank it 
# throw an Exception.  It now finds the first text line.
#    -- added the ability to add extensions.  see 'how to write an Emacs 
# extension' section.  Also look at exampleTemacsExtension.py
#       for a simple example as to how this works.
#    -- fixed control-left control-right up so they do what Emacs does.  This 
# has ramifications for delete previous word as well,
#       since that command relies on the control-left command to do its work.
#    -- added the ability to change the keystrokes via the 
# reconfigureKeyStroke method.  This method is largely untested.
#    -- last count: at around 204 keystrokes and commands( note some commands 
# and keystrokes are the same,
#       just different ways of accesing the functionality.
#    -- enhanced incremental search so that if the search doesnt find anything 
# it will start again either at the top or bottom, depending
#       on which direction it is going.  This is a nice little enhancement.
#    -- enhanced Tabing with alt-x, so that the user can cycle through the 
# matches. Added Tracker class to accomplish this.
#       This will speed up the use of the Alt-x commands and expose 
# functionality that is hard for a user to remember by keystroke.
#    -- added Control-x and regular keystroke commands to Alt-x commands.  Ive 
# focused on the ones Ive found most usefull.  This might be
#       the best way to access rectangle functionality and registers.
#    -- Created a better organized Outline.  There are several organizing 
# nodes now.  Its easier to find things when looking for them.
#    -- Added killing append to system clipboard.  The clipboard gets set with 
# every kill.  Control - y will return the fresh clipboard kill as well as 
# Alt-y.  This will be very nice to have.
#    -- Added ability to test standalone.  Just type: python temacs.py and a 
# simple Editor will appear.
#    -- New commands and keystrokes:
#        Control-j ( insert newline and tab )
#        added goto-char
#        added set-fill-column ( Control-x f )
#        added center-line  ( Alt- s )
#        added center-region ( see node 'fill column and centering' to see 
# what these do )
#        ( these buffer ops have to be configured so the Emacs instance knows 
# what is a 'buffer' in the environment,
#        see 'buffer recognition and alterers' node )
#        append-to-buffer
#        prepend-to-buffer
#        copy-to-buffer
#        insert-buffer
#        list-buffer ( aka Control-x Control-b )
#        switch-to-buffer ( aka Control-x b )
#        kill-buffer ( aka Control-x k )
#        rename-buffer
# 
# 
# 0.51 EKR:  Minor stylistic changes.
# 
# 0.55:
#     added:
#     Control-z or 'iconify-or-deiconfify-frame'
#     Control-x Esc Esc - executes last Alt-x command( repeat-complex-command 
# )
#     Control-x Control-c shutdown code, as well as a replacement hook if 
# configured to do so.
#     re-search-forward, re-search-backward - simple Alt-x regular expression 
# commands
#     Control-Alt-s, Control-Alt-r - regular expression cousins of incremental 
# search( which makes me think that I need to change isearch to python based 
# searches instead of the Tcl way..
#     diff - does a diff on 2 files and adds it as a buffer
#     what-line
#     keep-lines and flush-lines, two fun new text manipulation commands!(see 
# help text )
#     make-directory and remove-directory, two commands that remove and add 
# directories.
#     delete-file - removes a file
#     search-forward search-backward, searchs backward and forward for a word, 
# non-incrementally.  Accessed by Conrtrol-s Enter and Control-r
#     word-search-forward and word-search-backward, incredible!  You search 
# for a group of words ignoring punctuation.  This is mighty stuff, dont know 
# if Ill use it, but I like what I see.
#     replace-regex - like replace-string but uses a python regular expression 
# for the match.
#     query-replace-regex( Control-Alt-% ) -like query-replace but with a 
# python regular expression
#     Esc Esc :, Alt-:, eval-expression  - these evaluate a Python expression 
# in the minibuffer and puts the value in the current buffer.  This I think is 
# different than what Emacs does, but I think it makes the value more 
# accessible if its in the current buffer.  Nice little calculator too.
#     tabify, untabify - turns spaces to tabs and tabs into spaces( current 
# does it on 4 spaces to one tab ).
#     indent-relative - a very nice command that indents from the insert point 
# until it matches the indentation of a word in the above line.
#     changed:
#     replace-string command now will operate on a selection if there is one.  
# Also the function now uses string functionality to replace the
#     strings instead of using the Tk Text widget to do the job.
#     dynamic expansion now will expand with the '-' character, which helps 
# greatly in some cases.  Alot of work for a what will hopefully be a long 
# term gain.  Also will now use quoted strings as actual completion targets, 
# thank goodness.
#     fixed:
#     sort-lines will now clear its state after sorting the lines.
#     Alt-!(shell-command, Alt-|(shell-command-on-region) --now temacs allows 
# one to execute shell commands.  I dont see a shell being added to temacs, so 
# thats one area where it will probably not stray.
#     total 26 new commands added
#     fixed up: sort-lines and its cousins, if nothing is selected the command 
# is deactivated.
#@-at
#@-node:mork.20041101100635:<<version history>>
#@nl
#@<< documentation >>
#@+node:ekr.20041106101311:<< documentation >>
#@@nocolor

#@+others
#@+node:mork.20041101203748:How to write an Emacs extension
#@+at
# Emacs instances offer the user the ability to add functionality
# to itself.  This is accomplished through the Emacs extendAltX method.  
# Functions passed in should not be methods
# but just plain functions.
# 
# An example:
# def burp( self, event ):
#     print 'burp %s' % self     #This will print info about the Emacs 
# instance
#     self.stopControlX( event ) #every extension should call this or the 
# function will be called for each keystroke.
#                                #To be more precise, it should be called when 
# the function has completely cycled through.
# ei.extendAltX( 'burp', burp ) #burp has been added as an Alt-x command and 
# the burp function has become
#                               #a method of the Emacs instance.  self, will 
# now reflect this.
# 
# accessing it through the Alt-X interface will be done like so
# Alt-x
# burp ( Hit return , alternatively the user could type b and hit the tab 
# button )
# 
# Each function/method will be called with two parameters:
#     self -- which is the Emacs instance
#     event -- which is an Tkinter Event instance.
#     self gives the extension writer the ability to access the Emacs intances 
# functionality
#     event gives the user the ability to access the Text widget that the 
# Emacs instance is bound to.
#     the preferred way to do so is like this:
#     tbuffer = event.widget
#@-at
#@nonl
#@-node:mork.20041101203748:How to write an Emacs extension
#@+node:mork.20041102081834:Coding convenions
#@+at 
# 
# tbuffer - a Tkinter Text widget.  Would be called buffer, but this shadows a 
# Python builin.  This is the widget carried
# by the events in the Emacs instancs.  Can be accessed like so 'event.widget'
# svar - a Tkinter StringVar widget.  This should hold what the minibuffer is 
# showing currently.  Can
# be acquired by 'self.getSvarLabel'.
# 
# 
# 
#@-at
#@-node:mork.20041102081834:Coding convenions
#@+node:mork.20041102082911:Known bugs
#@+at 
# 
# .5
# 
# - control-u seems kinda flaky.  Will enhance in the next iteration and make 
# less flaky. :)
# - digit-arguments seem pretty flaky as well.
# --- These are no longer flaky.  A simple change to calling 
# self.keyboardQuit, has eliminated the flakiness Ive seen. :)
#     This was centered on using a command that wasnt a commadn like typing 
# 99a, made it burp!  You can also see the commands
#     as they are done in the Editor.  For example 'Control-u 99 a'  will type 
# 'a' 99 times in the editor.  Or
#     'Control-u 99 Control-_'  will undo the last 99 changes, thats if the 
# Emacs instance has been configure with an undoer.
#@-at
#@nonl
#@-node:mork.20041102082911:Known bugs
#@+node:mork.20041102103822:Future directions
#@+at
# 
# 1. Continue adding the keystroke command names to the Alt-x mechanism.  Much 
# of this has already been done.
# 2. Maybe make it possible for the user to add state to the MC_StateManager 
# instance.  This could allow the extension writer
# to create specific state based extension functions.  They may already be 
# able to do this.
# 3. When python 2.4 is official, look at subprocess module and decide if it 
# can be used to run exterior commands.  Pythons current
# cross platform process commands, dont seem too cross platform at this 
# point.  subprocess hopefully will fix this.
# 4. Continue migrating statefull commands to the MC_StateManager class.
# 5. Add ability for a user to learn the keystroke for a command.  The Help 
# Text should be considered a definitive source of
# information, but it may be quicker for the user to just ask.  This will be 
# accomplished by adding the 'where-is' command or
# 'Control-h w'.  Not essential at this point, and will be done when we are 
# entering a polish iteration.
# 6. Maybe add the ability for the user to evaluate Python expressions.  
# Vanilla Emacs has the ability to do something with
# Lisp expressions, so it may make sense to do this with Python since Python 
# is what this is built out of.
# 7. Maybe add Emacs variables for the commands.  Ive noticed that you can set 
# Emac variables to change some of the behavior
# in subtle ways.  A dictionary should be used to implement this, adding 1000 
# attributes to the Emacs class doesnt seem like a good idea.
# 8 Maybe add local abbreviations 'Control-x a i l'
#@-at
#@nonl
#@-node:mork.20041102103822:Future directions
#@+node:mork.20041104095745:A Note on Alt-X
#@+at
# Alt-x is the mechanism by which the user should be able to access any 
# command in the Emacs instance.
# The first steps in developing temacs was focused on the keystrokes.  Though 
# in reality the keystrokes
# are just ways to access the commands.
# 
# To initiate a command type Alt-x
# Start typing the command name
# Press Tab.  If the command does not come up, continue pressing Tab.
# If you placed the correct prefix in the minibuffer, eventually the command 
# will appear.
# 
# 
# This will help a user to quickly cycle through commands and select the one 
# they want, even if they can somewhat remember what
# the spelling is.
#@-at
#@nonl
#@-node:mork.20041104095745:A Note on Alt-X
#@+node:mork.20041122151944:A Note on the volume of methods
#@+at
# originally when this project started it was not envisioned that there would 
# be that many emacs like commands and stuff implemented.
# But then things changed, it grew.  At one point there were too many 
# functions for the module to be flexible and understandable anymore.
# 
# The first reaction in the development was to decompose the pure module 
# approach to an object approach.  This has helped immensely in
# making temacs more manageable.  But, an Emacs instance now has over 200+ 
# methods in it.  If it continues to grow, there may be
# the need to decompose the families of methods into their own objects.  This 
# could have two benefits:
# 1. More intellectually managable.
# 2. Swapable functionality.  Though its possible to do so now with python, 
# this could be made much easier by having all
# calls to a certain family be made through the __call__ operator.  Then 
# swaping could be simply done by changing the object
# the call is made to.
# 
# 
# We will see if this approach may be taken.  At this point I can say for 
# certain that the original pure functional design was a mistake, but one that 
# was correctable by using Leo and pychecker.  Without these 2 tools, I think 
# it may have been better to start over from scratch.
#@-at
#@-node:mork.20041122151944:A Note on the volume of methods
#@+node:mork.20041126091717:plans for .7
#@+at
# 
# I believe in .7 the transition from one big Emacs object to an Emacs object 
# composed of many method-family objects
# will begin.  This may be as a big as a transition as the change from the 
# flat module structure to the Emacs class based
# structure.  The .6 cycle Ill reserve for improving the functionality and 
# documentation.  The current command crop may be
# froze in that cycle.
#@-at
#@nonl
#@-node:mork.20041126091717:plans for .7
#@+node:mork.20041123150836:the master command is the center of an Emacs instance
#@+at
# 
# just a short note to anyone, including myself, that is working on temacs.  
# Currently all( well all the ones that we have registered interest in ) key 
# events get
# routed through:
# 
# def masterCommand( self, event, method , stroke):
# 
# 
# to understand the flow of the Emacs class, you need to understand this 
# method.  Everything goes through it, there are no sidecuts or anything.  
# This offers the implementor complete control over what happens, and for the 
# stateful commands it is essential to
# keep states from being corrupted.
# 
# 
# dont mess with this method lightly.
#@-at
#@-node:mork.20041123150836:the master command is the center of an Emacs instance
#@+node:mork.20041122152311:adding stateful commands to temacs
#@+at
# Ive noticed a general strategy that works for adding commands that need 
# state to develop.
# 
# 1. Create a start method.  This sets the mcStateManager into a specific 
# state
# 2. Create a process method.  This watches events as they happen in the state
# 3. Create endpoint methods. These perform the final steps in processing the 
# stateful command.
# 
# 
# This general strategy works well so far.  A whole family of methods can be 
# created in this manner.  Steps 1 and 2
# could be combined but at a cost of more complexity, so Id recommend keeping 
# them separate.
#@-at
#@-node:mork.20041122152311:adding stateful commands to temacs
#@+node:mork.20041123150144:how to mix python regular expressions and the Text widget
#@+at
# Using python regular expressions and the Text widget may seem difficult but 
# in reality it is very easy.
# A simple formula:
# 1. get the text you are interested in from the Text widget.
# 2. Do a python regex on it, get the start value from the match object: 
# match.start()
# 3. This gives you the position in the text widget where the regex matched.  
# Change the 'insert' point
# in the Text like so:
# 
# tbuffer.mark_set( 'insert', 'insert +%sc' % match.start() )
# 
# 
# this will change the insert point to where the match started.  Since you can 
# move forward in the Text widget
# by the character amount, bridging python regexes and Text is a simple 
# operation.
#   Need to go after the match, just use
# match.end() instead of match.start().
# 
# I puzzled over this for awhile, so this note is a reminder that it is easy.  
# See the implementation for query-replace-regex for
# an example.  Doing this with just plain string can follow a similar pattern.
# 
#@-at
#@@c
#@nonl
#@-node:mork.20041123150144:how to mix python regular expressions and the Text widget
#@-others
#@nonl
#@-node:ekr.20041106101311:<< documentation >>
#@nl
#@<< imports >>
#@+node:mork.20041030164547.1:<< imports >>
# pretty low level imports. These may be all the imports the module needs

import leoGlobals as g # ekr

import Tkinter
import string
import weakref
import new
import sys
import re
import os
#@-node:mork.20041030164547.1:<< imports >>
#@nl

#@+others
#@+node:mork.20041104102456:Emacs helper classes
#@+others
#@+node:mork.20041031131847:class ControlXHandler
class ControlXHandler:
    '''The ControlXHandler manages how the Control-X based commands operate on the
       Emacs instance.'''    
    
    #@    @+others
    #@+node:mork.20041031162953:__init__
    def __init__( self, emacs ):
            
        self.emacs = emacs
        self.previous = []
        self.rect_commands = {
        'o': emacs.openRectangle,
        'c': emacs.clearRectangle,
        't': emacs.stringRectangle,
        'y': emacs.yankRectangle,
        'd': emacs.deleteRectangle,
        'k': emacs.killRectangle,
        'r': emacs.activateRectangleMethods,             
        }
        
        self.variety_commands = {
        'period': emacs.setFillPrefix,
        'parenleft': emacs.startKBDMacro,
        'parenright' : emacs.stopKBDMacro,
        'semicolon': emacs.setCommentColumn,
        'Tab': emacs.tabIndentRegion,
        'u': lambda event: emacs.doUndo( event, 2 ),
        'equal': emacs.lineNumber,
        'h': emacs.selectAll,
        'f': emacs.setFillColumn,
        'b': lambda event, which = 'switch-to-buffer': emacs.setInBufferMode( event, which ),
        'k': lambda event, which = 'kill-buffer': emacs.setInBufferMode( event, which ),
        }
        
        self.abbreviationDispatch = {    
        'a': lambda event: emacs.abbreviationDispatch( event, 1 ),
        'a i': lambda event: emacs.abbreviationDispatch( event, 2 ),    
        }
        
        self.register_commands ={    
        1: emacs.setNextRegister,
        2: emacs.executeRegister,        
        }
    #@-node:mork.20041031162953:__init__
    #@+node:mork.20041031132342:__call__
    def __call__( self, event , stroke ):
        
        self.previous.insert( 0, event.keysym )
        emacs = self.emacs 
        if len( self.previous ) > 10: self.previous.pop()
        if stroke in ('<Key>', '<Escape>' ):
            return self.processKey( event )
        if stroke in emacs.xcommands:
            emacs.xcommands[ stroke ]( event )
            if stroke != '<Control-b>': emacs.keyboardQuit( event )
        return 'break'
    #@nonl
    #@-node:mork.20041031132342:__call__
    #@+node:mork.20041031133146:processKey
    def processKey( self, event ):
            
        emacs = self.emacs 
        previous = self.previous
        if event.keysym in ( 'Shift_L', 'Shift_R' ):
            return
            
        if emacs.sRect:
            return emacs.stringRectangle( event )
            
        if ( event.keysym == 'r' and emacs.rectanglemode == 0 ) and not emacs.registermode:
            return self.processRectangle( event )
        elif self.rect_commands.has_key( event.keysym ) and emacs.rectanglemode == 1:
            return self.processRectangle( event )
            
        if self.register_commands.has_key( emacs.registermode ):
            self.register_commands[ emacs.registermode ]( event )
            return 'break'
        
        if self.variety_commands.has_key( event.keysym ):
            emacs.stopControlX( event )
            return self.variety_commands[ event.keysym ]( event )
            
        
        #if emacs.sRect:
        #    return emacs.stringRectangle( event )
        #    #return 'break'
        if event.keysym in ( 'a', 'i' , 'e'):
            if self.processAbbreviation( event ): return 'break'
    
        if event.keysym == 'g':
            svar, label = emacs.getSvarLabel( event )
            l = svar.get()
            if self.abbreviationDispatch.has_key( l ):
                emacs.stopControlX( event )
                return self.abbreviationDispatch[ l ]( event )
            #if l == 'a':
            #    emacs.stopControlX( event )
            #    return emacs.abbreviationDispatch( event, 1 )
            #elif l == 'a i':
            #    emacs.stopControlX( event )
            #    return emacs.abbreviationDispatch( event, 2 )
        if event.keysym == 'e':
            emacs.stopControlX( event )
            return emacs.executeLastMacro( event )
        if event.keysym == 'x' and previous[ 1 ] not in ( 'Control_L', 'Control_R'):
            event.keysym = 's' 
            emacs.setNextRegister( event )
            return 'break'
        
        if event.keysym == 'Escape':
            if len( previous ) > 1:
                if previous[ 1 ] == 'Escape':
                    return emacs.repeatComplexCommand( event )
        #if event.keysym == 'r':
        #    return emacs.activateRectangleMethods( event )
        #if self.rect_commands.has_key( event.keysym ):# and emacs.registermode == 1:
        #    return self.processRectangle( event )
         
        #if emacs.registermode == 1:
        #    emacs.setNextRegister( event )
        #    return 'break'
        #elif emacs.registermode == 2:
        #    emacs.executeRegister( event )
        #    return 'break'
        #if self.register_commands.has_key( emacs.registermode ):
        #    print 'register commands'
        #    self.register_commands[ emacs.registermode ]( event )
        #    return 'break'
        #if event.keysym == 'r':
        #    return emacs.activateRectangleMethods( event )
        #    emacs.registermode = 1
        #    svar = emacs.svars[ event.widget ]
        #    svar.set( 'C - x r' )
        #    return 'break'
        #if event.keysym== 'h':
        #    emacs.stopControlX( event )
        #    event.widget.tag_add( 'sel', '1.0', 'end' )
        #tag_add( 'sel', '1.0', 'end' )    return 'break' 
        #if event.keysym == 'equal':
        #    emacs.lineNumber( event )
        #    return 'break'
        #if event.keysym == 'u':
        #    emacs.stopControlX( event )
        #    return emacs.doUndo( event, 2 )   
            
             
    
    
    
    #@-node:mork.20041031133146:processKey
    #@+node:mork.20041031134709:processRectangle
    def processRectangle( self, event ):
        
        self.rect_commands[ event.keysym ]( event )
        return 'break'
        #if event.keysym == 'o':
        #    emacs.openRectangle( event )
        #    return 'break'
        #if event.keysym == 'c':
        #    emacs.clearRectangle( event )
        #    return 'break'
        #if event.keysym == 't':
        #    emacs.stringRectangle( event )
        #    return 'break'
        #if event.keysym == 'y':
        #    emacs.yankRectangle( event )
        #    return 'break'
        #if event.keysym == 'd':
        #    emacs.deleteRectangle( event )
        #    return 'break'
        #if event.keysym == 'k':
        #    emacs.killRectangle( event )
        #    return 'break'       
    #@-node:mork.20041031134709:processRectangle
    #@+node:mork.20041031135748:processAbbreviation
    def processAbbreviation( self, event ):
        
        emacs = self.emacs
        svar, label = emacs.getSvarLabel( event )
        if svar.get() != 'a' and event.keysym == 'a':
            svar.set( 'a' )
            return 'break'
        elif svar.get() == 'a':
            if event.char == 'i':
                svar.set( 'a i' )
            elif event.char == 'e':
                emacs.stopControlX( event )
                event.char = ''
                emacs.expandAbbrev( event )
            return 'break'
    #@nonl
    #@-node:mork.20041031135748:processAbbreviation
    #@-others

#@-node:mork.20041031131847:class ControlXHandler
#@+node:mork.20041031145157:class MC_StateManager
class MC_StateManager:
    
    '''MC_StateManager manages the state that the Emacs instance has entered and
       routes key events to the right method, dependent upon the state in the MC_StateManager'''
       
    #@    @+others
    #@+node:mork.20041031162857:__init__
    def __init__( self, emacs ):
            
        self.emacs = emacs
        self.state = None
        self.states = {}
        #@    <<statecommands>>
        #@+node:mork.20041031150125:<<statecommands>>
        # EKR: used only below.
        def eA( event ):
            if self.emacs.expandAbbrev( event ) :
                return 'break'
        
        self.stateCommands = { #1 == one parameter, 2 == all
            'uC': ( 2, emacs.universalDispatch ),
            'controlx': ( 2, emacs.doControlX ),
            'isearch':( 2, emacs.iSearch ),
            'goto': ( 1, emacs.Goto ),
            'zap': ( 1, emacs.zapTo ),
            'howM': ( 1, emacs.howMany ),
            'abbrevMode': ( 1, emacs.abbrevCommand1 ),
            'altx': ( 1, emacs.doAlt_X ),
            'qlisten': ( 1, emacs.masterQR ),
            'rString': ( 1, emacs.replaceString ),
            'negativeArg':( 2, emacs.negativeArgument ),
            'abbrevOn': ( 1, eA ),
            'set-fill-column': ( 1, emacs.setFillColumn ),
            'chooseBuffer': ( 1, emacs.chooseBuffer ),
            'renameBuffer': ( 1, emacs.renameBuffer ),
            're_search': ( 1, emacs.re_search ),
            'alterlines': ( 1, emacs.processLines ),
            'make_directory': ( 1, emacs.makeDirectory ),
            'remove_directory': ( 1, emacs.removeDirectory ),
            'delete_file': ( 1, emacs.deleteFile ),
            'nonincr-search': ( 2, emacs.nonincrSearch ),
            'word-search':( 1, emacs.wordSearch ),
            'last-altx': ( 1, emacs.executeLastAltX ),
            'escape': ( 1, emacs.watchEscape ),
            'subprocess': ( 1, emacs.subprocesser ),
            }
        #@nonl
        #@-node:mork.20041031150125:<<statecommands>>
        #@nl
    #@nonl
    #@-node:mork.20041031162857:__init__
    #@+node:mork.20041031162857.1:setState
    def setState( self, state, value ):
            
        self.state = state
        self.states[ state ] = value
    #@nonl
    #@-node:mork.20041031162857.1:setState
    #@+node:mork.20041031162857.2:getState
    def getState( self, state ):
        
        return self.states.get(state,False)
    #@nonl
    #@-node:mork.20041031162857.2:getState
    #@+node:mork.20041031162857.3:hasState
    def hasState( self ):
    
        if self.state:
            return self.states[ self.state ]
    #@-node:mork.20041031162857.3:hasState
    #@+node:mork.20041124094511:whichState
    def whichState( self ):
        
        return self.state
    #@-node:mork.20041124094511:whichState
    #@+node:mork.20041031162857.4:__call__
    def __call__( self, *args ):
            
        if self.state:
            which = self.stateCommands[ self.state ]
            
            # EKR: which[0] is a flag: 1 == one parameter, 2 == all
            # EKR: which[1] is the function.
            
            if which[ 0 ] == 1:
                return which[ 1 ]( args[ 0 ] )
            else:
                return which[ 1 ]( *args )
    #@-node:mork.20041031162857.4:__call__
    #@+node:mork.20041031162857.5:clear
    def clear( self ):
            
        self.state = None
    
        for z in self.states.keys():
            self.states[ z ] = False
    #@nonl
    #@-node:mork.20041031162857.5:clear
    #@-others



#@-node:mork.20041031145157:class MC_StateManager
#@+node:mork.20041101083527:class MC_KeyStrokeManager  (hard-coded keystrokes)
class MC_KeyStrokeManager:
    
    #@    @+others
    #@+node:mork.20041101083527.1:__init__
    def __init__( self, emacs ):
        
        self.emacs = emacs
    
        #@    <<keystrokes>>
        #@+node:mork.20041101083527.2:<<keystrokes>> (hard-coded keystrokes)
        self.keystrokes = {
        
            '<Control-s>': ( 2, emacs.startIncremental ), 
            '<Control-r>': ( 2, emacs.startIncremental ),
            '<Alt-g>': ( 1, emacs.startGoto ),
            '<Alt-z>': ( 1, emacs.startZap ),
            '<Alt-percent>': ( 1,  emacs.masterQR ) ,
            '<Control-Alt-w>': ( 1, lambda event: 'break' ),
        }
        #@nonl
        #@-node:mork.20041101083527.2:<<keystrokes>> (hard-coded keystrokes)
        #@nl
    #@-node:mork.20041101083527.1:__init__
    #@+node:mork.20041101084148:hasKeyStroke
    def hasKeyStroke( self, stroke ):
        
        return self.keystrokes.has_key( stroke )
    #@nonl
    #@-node:mork.20041101084148:hasKeyStroke
    #@+node:mork.20041101084148.1:__call__
    def __call__( self, event, stroke ):
        
        kstroke = self.keystrokes[ stroke ]
        
        if 0: # EKR: this would be better:
            numberOfArgs,func = self.keystrokes[ stroke ]
            if numberOfArgs == 1:
                return func(event)
            else:
                return func(event,stroke)
        
        # EKR: which[0] is the number of params.
        # EKR: which[1] is the function.
    
        if kstroke[ 0 ] == 1:
            return kstroke[ 1 ]( event )
        else:
            return kstroke[ 1 ]( event, stroke )
            
        
    #@nonl
    #@-node:mork.20041101084148.1:__call__
    #@-others
#@nonl
#@-node:mork.20041101083527:class MC_KeyStrokeManager  (hard-coded keystrokes)
#@+node:mork.20041102131352:class Tracker
class Tracker:
    '''A class designed to allow the user to cycle through a list
       and to change the list as deemed appropiate.'''

    #@    @+others
    #@+node:mork.20041102131352.1:init
    def __init__( self ):
        
        self.tablist = []
        self.prefix = None
        self.ng = self._next()
    #@nonl
    #@-node:mork.20041102131352.1:init
    #@+node:mork.20041102131352.2:setTabList
    def setTabList( self, prefix, tlist ):
        
        self.prefix = prefix
        self.tablist = tlist
        
    
    #@-node:mork.20041102131352.2:setTabList
    #@+node:mork.20041102131352.3:_next
    def _next( self ):
        
        while 1:
            
            tlist = self.tablist
            if not tlist: yield ''
            for z in self.tablist:
                if tlist != self.tablist:
                    break
                yield z
    #@-node:mork.20041102131352.3:_next
    #@+node:mork.20041102132710:next
    def next( self ):
        
        return self.ng.next()
    #@-node:mork.20041102132710:next
    #@+node:mork.20041102160313:clear
    def clear( self ):
    
        self.tablist = []
        self.prefix = None
    #@-node:mork.20041102160313:clear
    #@-others
#@nonl
#@-node:mork.20041102131352:class Tracker
#@-others
#@-node:mork.20041104102456:Emacs helper classes
#@+node:mork.20041030165020:class Emacs
class Emacs:
    '''The Emacs class binds to a Tkinter Text widget and adds Emac derived keystrokes and commands
       to it.'''
    
    Emacs_instances = weakref.WeakKeyDictionary()
    global_killbuffer = []
    global_registers = {}
    lossage = [] ### EKR: list( ' ' * 100 )
    #@    @+others
    #@+node:mork.20041030165020.1:Emacs.__init__
    def __init__( self , tbuffer = None , minibuffer = None, useGlobalKillbuffer = False, useGlobalRegisters = False):
        '''Sets up Emacs instance.
        
        If a Tkinter Text widget and Tkinter Label are passed in
        via the tbuffer and minibuffer parameters, these are bound to.
        Otherwise an explicit call to setBufferStrokes must be done.
        useGlobalRegisters set to True indicates that the Emacs instance should use a class attribute that functions
        as a global register.
        useGlobalKillbuffer set to True indicates that the Emacs instances should use a class attribute that functions
        as a global killbuffer.'''
        
        self.mbuffers = {} 
        self.svars = {}
        
        
        #self.isearch = False
        self.tailEnds = {} #functions to execute at the end of many Emac methods.  Configurable by environment.
        self.undoers = {} #Emacs instance tracks undoers given to it.
        
        
        self.store = {'rlist': [], 'stext': ''} 
        
        #macros
        self.lastMacro = None 
        self.macs = []
        self.macro = []
        self.namedMacros = {}
        self.macroing = False
        self.dynaregex = re.compile( r'[%s%s\-_]+' %( string.ascii_letters, string.digits ) ) #for dynamic abbreviations
        self.altx_history = []
        self.keysymhistory = [] 
        
        #This section sets up the buffer data structures
        self.bufferListGetters = {}
        self.bufferSetters = {}
        self.bufferGotos = {}
        self.bufferDeletes = {}
        self.renameBuffers = {}
        self.bufferDict = None
        self.bufferTracker = Tracker()
        self.bufferCommands = {
        
        'append-to-buffer': self.appendToBuffer,
        'prepend-to-buffer': self.prependToBuffer,
        'copy-to-buffer': self.copyToBuffer,
        'insert-buffer': self.insertToBuffer,
        'switch-to-buffer': self.switchToBuffer,
         'kill-buffer': self.killBuffer,   
        }
        
        self.swapSpots = []
        self.ccolumn = '0'
        #self.howM = False
        self.reset = False
        if useGlobalKillbuffer:
            self.killbuffer = Emacs.global_killbuffer
        else:
            self.killbuffer = []
        self.kbiterator = self.iterateKillBuffer()
        
        #self.controlx = False
        self.csr = { '<Control-s>': 'for', '<Control-r>':'bak' }
        self.pref = None
        #self.zap = False
        #self.goto = False
        self.previousStroke = ''
        if useGlobalRegisters:
            self.registers = Emacs.global_registers
        else:
            self.registers = {}
        
        #registers
        self.regMeth = None
        self.regMeths, self.regText = self.addRegisterItems()
    
        #Abbreviations
        self.abbrevMode = False 
        self.abbrevOn = False # determines if abbreviations are on for masterCommand and toggle abbreviations
        self.abbrevs = {}
        
        self.regXRpl = None # EKR: a generator: calling self.regXRpl.next() get the next value.
        self.regXKey = None
        
        self.fillPrefix = '' #for fill prefix functions
        self.fillColumn = 70 #for line centering
        self.registermode = False #for rectangles and registers
        
        self.qQ = None
        self.qR = None
        #self.qlisten = False
        #self.lqR = Tkinter.StringVar()
        #self.lqR.set( 'Query with: ' ) # replaced with using the svar and self.mcStateManager
        self.qgetQuery = False
        #self.lqQ = Tkinter.StringVar()
        #self.lqQ.set( 'Replace with:' )# replaced with using the svar and self.mcStateManager
        self.qgetReplace = False
        self.qrexecute = False
        self.querytype = 'normal'
        
        #self.rString = False
        #These attributes are for replace-string and replace-regex
        self._sString = ''
        self._rpString = ''
        self._useRegex = False
        
        self.sRect = False  #State indicating string rectangle.  May be moved to MC_StateManager
        self.krectangle = None #The kill rectangle
        self.rectanglemode = 0 #Determines what state the rectangle system is in.
        
        self.last_clipboard = None #For interacting with system clipboard.
        
        self.negativeArg = False 
        self.negArgs = { '<Alt-c>': self.changePreviousWord,
        '<Alt-u>' : self.changePreviousWord,
        '<Alt-l>': self.changePreviousWord } #For negative argument functionality
        
        #self.altx = False
        #Alt-X commands.
        self.doAltX = self.addAltXCommands()
        self.axTabList = Tracker()
        self.x_hasNumeric = [ 'sort-lines' , 'sort-fields']
        
        #self.uC = False
        #These attributes are for the universal command functionality.
        self.uCstring = string.digits + '\b'
        self.uCdict = { '<Alt-x>' : self.alt_X }
        
        self.cbDict = self.addCallBackDict()# Creates callback dictionary, primarily used in the master command
        self.xcommands = self.addXCommands() # Creates the X commands dictionary
        self.cxHandler = ControlXHandler( self ) #Creates the handler for Control-x commands
        self.mcStateManager = MC_StateManager( self ) #Manages state for the master command
        self.kstrokeManager = MC_KeyStrokeManager( self ) #Manages some keystroke state for the master command.
        self.shutdownhook = None #If this is set via setShutdownHook, it is executed instead of sys.exit when Control-x Control-c is fired
        self.shuttingdown = False #indicates that the Emacs instance is shutting down and no work needs to be done.
        
        if tbuffer and minibuffer:
            self.setBufferStrokes( tbuffer, minibuffer )
    
    #@-node:mork.20041030165020.1:Emacs.__init__
    #@+node:mork.20041030164547.41:getHelpText
    def getHelpText():
        '''This returns a string that describes what all the
        keystrokes do with a bound Text widget.'''
        help_t = [ 'Buffer Keyboard Commands:',
        '----------------------------------------\n',
        '<Control-p>: move up one line',
        '<Control-n>: move down one line',
        '<Control-f>: move forward one char',
        '<Conftol-b>: move backward one char',
        '<Control-o>: insert newline',
        '<Control-Alt-o> : insert newline and indent',
        '<Control-j>: insert newline and tab',
        '<Alt-<> : move to start of Buffer',
        '<Alt- >' +' >: move to end of Buffer',
        '<Control a>: move to start of line',
        '<Control e> :move to end of line',
        '<Alt-Up>: move to start of line',
        '<Alt-Down>: move to end of line',
        '<Alt b>: move one word backward',
        '<Alt f> : move one word forward',
        '<Control - Right Arrow>: move one word forward',
        '<Control - Left Arrow>: move one word backwards',
        '<Alt-m> : move to beginning of indentation',
        '<Alt-g> : goto line number',
        '<Control-v>: scroll forward one screen',
        '<Alt-v>: scroll up one screen',
        '<Alt-a>: move back one sentence',
        '<Alt-e>: move forward one sentence',
        '<Alt-}>: move forward one paragraph',
        '<Alt-{>: move backwards one paragraph',
        '<Alt-:> evaluate a Python expression in the minibuffer and insert the value in the current buffer',
        'Esc Esc : evaluate a Python expression in the minibuffer and insert the value in the current buffer',
        '<Control-x . >: set fill prefix',
        '<Alt-q>: fill paragraph',
        '<Alt-h>: select current or next paragraph',
        '<Control-x Control-@>: pop global mark',
        '<Control-u>: universal command, repeats the next command n times.',
        '<Alt -n > : n is a number.  Processes the next command n times.',
        '<Control-x (>: start definition of kbd macro',
        '<Control-x ) > : stop definition of kbd macro',
        '<Control-x e : execute last macro defined',
        '<Control-u Control-x ( >: execute last macro and edit',
        '<Control-x Esc Esc >: execute last complex command( last Alt-x command',
        '<Control-x Control-c >: save buffers kill Emacs',
        '''<Control-x u > : advertised undo.   This function utilizes the environments.
        If the buffer is not configure explicitly, there is no operation.''',
        '<Control-_>: advertised undo.  See above',
        '<Control-z>: iconfify frame',
        '----------------------------------------\n',
        '<Delete> : delete previous character',
        '<Control d>: delete next character',
        '<Control k> : delete from cursor to end of line. Text goes to kill buffer',
        '<Alt d>: delete word. Word goes to kill buffer',
        '<Alt Delete>: delete previous word. Word goes to kill buffer',
        '<Alt k >: delete current sentence. Sentence goes to kill buffer',
        '<Control x Delete>: delete previous sentence. Sentence goes to kill buffer',
        '<Control y >: yank last deleted text segment from\n kill buffer and inserts it.',
        '<Alt y >: cycle and yank through kill buffer.\n',
        '<Alt z >: zap to typed letter. Text goes to kill buffer',
        '<Alt-^ >: join this line to the previous one',
        '<Alt-\ >: delete surrounding spaces',
        '<Alt-s> >: center line in current fill column',
        '<Control-Alt-w>: next kill is appended to kill buffer\n'
        
        '----------------------------------------\n',
        '<Alt c>: Capitalize the word the cursor is under.',
        '<Alt u>: Uppercase the characters in the word.',
        '<Alt l>: Lowercase the characters in the word.',
        '----------------------------------------\n',
        '<Alt t>: Mark word for word swapping.  Marking a second\n word will swap this word with the first',
        '<Control-t>: Swap characters',
        '<Ctrl-@>: Begin marking region.',
        '<Ctrl-W>: Kill marked region',
        '<Alt-W>: Copy marked region',
        '<Ctrl-x Ctrl-u>: uppercase a marked region',
        '<Ctrl-x Ctrl-l>: lowercase a marked region',
        '<Ctrl-x h>: mark entire buffer',
        '<Alt-Ctrl-backslash>: indent region to indentation of line 1 of the region.',
        '<Ctrl-x tab> : indent region by 1 tab',
        '<Control-x Control-x> : swap point and mark',
        '<Control-x semicolon>: set comment column',
        '<Alt-semicolon>: indent to comment column',
        '----------------------------------------\n',
        'M-! cmd -- Run the shell command line cmd and display the output',
        'M-| cmd -- Run the shell command line cmd with region contents as input',
        '----------------------------------------\n',
        '<Control-x a e>: Expand the abbrev before point (expand-abbrev). This is effective even when Abbrev mode is not enabled',
        '<Control-x a g>: Define an abbreviation for previous word',
        '<Control-x a i g>: Define a word as abbreviation for word before point, or in point',                        
        '----------------------------------------\n',
        '<Control s>: forward search, using pattern in Mini buffer.\n',
        '<Control r>: backward search, using pattern in Mini buffer.\n' ,
        '<Control s Enter>: search forward for a word, nonincremental\n',
        '<Control r Enter>: search backward for a word, nonincremental\n',
        '<Control s Enter Control w>: Search for words, ignoring details of punctuation',
        '<Control r Enter Control w>: Search backward for words, ignoring details of punctuation',
        '<Control-Alt s>: forward regular expression search, using pattern in Mini buffer\n',
        '<Control-Alt r>: backward regular expression search, using pattern in Mini buffer\n',
        '''<Alt-%>: begin query search/replace. n skips to next match. y changes current match.  
        q or Return exits. ! to replace all remaining matches with no more questions''',
        '''<Control Alt %> begin regex search replace, like Alt-%''',
        '<Alt-=>: count lines and characters in regions',
        '<Alt-( >: insert parentheses()',
        '<Alt-) >:  move past close',
        '<Control-x Control-t>: transpose lines.',
        '<Control-x Control-o>: delete blank lines' ,
        '<Control-x r s>: save region to register',
        '<Control-x r i>: insert to buffer from register',
        '<Control-x r +>: increment register',
        '<Control-x r n>: insert number 0 to register',
        '<Control-x r space > : point insert point to register',
        '<Control-x r j > : jump to register',
        '<Control-x x>: save region to register',
        '<Control-x r r> : save rectangle to register',
        '<Control-x r o>: open up rectangle',
        '<Control-x r c> : clear rectangle',
        '<Control-x r d> : delete rectangle',
        '<Control-x r t> : replace rectangle with string',
        '<Control-x r k> : kill rectangle',
        '<Control-x r y> : yank rectangle',
        '<Control-g> : keyboard quit\n',
        '<Control-x = > : position of cursor',
        '<Control-x . > : set fill prefix',
        '<Control-x f > : set the fill column',
        '<Control-x Control-b > : display the buffer list',
        '<Control-x b > : switch to buffer',
        '<Control-x k > : kill the specified buffer',
        '----------------------------------------\n',
        '<Alt - - Alt-l >: lowercase previous word',
        '<Alt - - Alt-u>: uppercase previous word',
        '<Alt - - Alt-c>: capitalise previous word',
        '----------------------------------------\n',
        '<Alt-/ >: dynamic expansion',
        '<Control-Alt-/>: dynamic expansion.  Expands to common prefix in buffer\n'
        '----------------------------------------\n',
        'Alt-x commands:\n',
        '(Pressing Tab will result in auto completion of the options if an appropriate match is found',
        'replace-string  -  replace string with string',
        'replace-regex - replace python regular expression with string',
        'append-to-register  - append region to register',
        'prepend-to-register - prepend region to register\n'
        'sort-lines - sort selected lines',
        'sort-columns - sort by selected columns',
        'reverse-region - reverse selected lines',
        'sort-fields  - sort by fields',
        'abbrev-mode - toggle abbrev mode on/off',
        'kill-all-abbrevs - kill current abbreviations',
        'expand-region-abbrevs - expand all abrevs in region',
        'read-abbrev-file - read abbreviations from file',
        'write-abbrev-file - write abbreviations to file',
        'list-abbrevs   - list abbrevs in minibuffer',
        'fill-region-as-paragraph - treat region as one paragraph and add fill prefix',
        'fill-region - fill paragraphs in region with fill prefix',
        'close-rectangle  - close whitespace rectangle',
        'how-many - counts occurances of python regular expression',
        'kill-paragraph - delete from cursor to end of paragraph',
        'backward-kill-paragraph - delete from cursor to start of paragraph',
        'backward-kill-sentence - delete from the cursor to the start of the sentence',
        'name-last-kbd-macro - give the last kbd-macro a name',
        'insert-keyboard-macro - save macros to file',
        'load-file - load a macro file',
        'kill-word - delete the word the cursor is on',
        'kill-line - delete form the cursor to end of the line', 
        'kill-sentence - delete the sentence the cursor is on',
        'kill-region - delete a marked region',
        'yank - restore what you have deleted',
        'backward-kill-word - delete previous word',
        'backward-delete-char - delete previous character',
        'delete-char - delete character under cursor' , 
        'isearch-forward - start forward incremental search',
        'isearch-backward - start backward incremental search',
        'isearch-forward-regexp - start forward regular expression incremental search',
        'isearch-backward-regexp - start backward return expression incremental search',
        'capitalize-word - capitalize the current word',
        'upcase-word - switch word to upper case',
        'downcase-word - switch word to lower case',
        'indent-region - indent region to first line in region',
        'indent-rigidly - indent region by a tab',
        'indent-relative - Indent from point to under an indentation point in the previous line',
        'set-mark-command - mark the beginning or end of a region',
         'kill-rectangle - kill the rectangle',
        'delete-rectangle - delete the rectangle',
        'yank-rectangle - yank the rectangle',
        'open-rectangle - open the rectangle',
        'clear-rectangle - clear the rectangle',
        'copy-to-register - copy selection to register',
        'insert-register - insert register into buffer',
        'copy-rectangle-to-register - copy buffer rectangle to register',
        'jump-to-register - jump to position in register',
        'point-to-register - insert point into register',
        'number-to-register - insert number into register',
        'increment-register - increment number in register',
        'view-register - view what register contains',
        'beginning-of-line - move to the beginning of the line',
        'end-of-line - move to the end of the line',
        'beginning-of-buffer - move to the beginning of the buffer',
        'end-of-buffer - move to the end of the buffer',
        'newline-and-indent - insert a newline and tab',
        'keyboard-quit - abort current command',
        'iconify-or-deiconify-frame - iconfiy current frame',
        'advertised-undo - undo the last operation',
        'back-to-indentation - move to first non-blank character of line',
        'delete-indentation - join this line to the previous one',
        'view-lossage - see the last 100 characters typed',
        'transpose-chars - transpose two letters',
        'transpose-words - transpose two words',
        'transpose-line - transpose two lines',
        'flush-lines - delete lines that match regex',
        'keep-lines - keep lines that only match regex',
        'insert-file - insert file at current position',
        'save-buffer - save file',
        'split-line - split line at cursor. indent to column of cursor',
        'upcase-region - Upper case region',
        'downcase-region - lower case region',
        'goto-line - goto a line in the buffer',
        'what-line - display what line the cursor is on',
        'goto-char - goto a char in the buffer',
        'set-fill-column - sets the fill column',
        'center-line - centers the current line within the fill column',
        'center-region - centers the current region within the fill column',   
        'forward-char - move the cursor forward one char',
        'backward-char - move the cursor backward one char',
        'previous-line - move the cursor up one line',
        'next-line - move the cursor down one line',
        'universal-argument - Repeat the next command "n" times',
        'digit-argument - Repeat the next command "n" times',
        'set-fill-prefix - Sets the prefix from the insert point to the start of the line',
        'scroll-up - scrolls up one screen',
        'scroll-down - scrolls down one screen',
        'append-to-buffer - Append region to a specified buffer',
        'prepend-to-buffer - Prepend region to a specified buffer',
        'copy-to-buffer - Copy region to a specified buffer, deleting the previous contents',
        'insert-buffer - Insert the contents of a specified buffer into current buffer at point',
        'list-buffers - Display the buffer list',
        'switch-to-buffer - switch to a different buffer, if it does not exits, it is created.',
        'kill-buffer - kill the specified buffer',
        'rename-buffer - rename the buffer',
        'query-replace - query buffer for pattern and replace it.  The user will be asked for a pattern, and for text to replace the pattern with.',
        'query-replace-regex - query buffer with regex and replace it.  The user will be asked for a pattern, and for text to replace the regex matches with.',
        'inverse-add-global-abbrev - add global abbreviation from previous word.  Will ask user for word to expand to',
        'expand-abbrev - Expand the abbrev before point. This is effective even when Abbrev mode is not enabled',
        're-search-forward - do a python regular expression search forward',
        're-search-backward - do a python regular expression search backward',
        'diff - compares two files, displaying the differences in an Emacs buffer named *diff*',
        'make-directory - create a new directory',
        'remove-directory - remove an existing directory if its empty',
        'delete-file - remove an existing file',
        'search-forward - search forward for a word',
        'search-backward - search backward for a word',
        'word-search-forward - Search for words, ignoring details of punctuation.', 
        'word-search-backward - Search backward for words, ignoring details of punctuation',
        'repeat-complex-command - repeat the last Alt-x command',
        'eval-expression - evaluate a Python expression and put the value in the current buffer',
        'tabify - turn the selected text\'s spaces into tabs',
        'untabify - turn the selected text\'s tabs into spaces',
        'shell-command -Run the shell command line cmd and display the output',
        'shell-command-on-region -Run the shell command line cmd with region contents as input',
        ]
        
        return '\n'.join( help_t )
    
    getHelpText = staticmethod( getHelpText )
    
    
    
    
    
    
    
    
    
    
    
    #@-node:mork.20041030164547.41:getHelpText
    #@+node:mork.20041030164547.43:masterCommand
    #self.controlx = False
    #self.csr = { '<Control-s>': 'for', '<Control-r>':'bak' }
    #self.pref = None
    #self.zap = False
    #self.goto = False
    #self.previousStroke = ''
    def masterCommand( self, event, method , stroke):
        '''The masterCommand is the central routing method of the Emacs method.
           All commands and keystrokes pass through here.'''
           
        special = event.keysym in ('Control_L','Control_R','Alt_L','Alt-R','Shift_L','Shift_R')
        inserted = not special or len(self.keysymhistory) == 0 or self.keysymhistory[0] != event.keysym
    
        # Don't add multiple special characters to history.
        if inserted:
            self.keysymhistory.insert(0,event.keysym)
            if len(event.char) > 0:
                if len(Emacs.lossage) > 99: Emacs.lossage.pop()
                Emacs.lossage.insert(0,event.char)
            
            if 1: # traces
                print event.keysym,stroke
                g.trace(self.keysymhistory)
                g.trace(Emacs.lossage)
            
        if 0:
            #@        << old insert code >>
            #@+node:ekr.20050527112828:<< old insert code >>
            Emacs.lossage.reverse()
            Emacs.lossage.append( event.char ) #Then we add the new char.  Hopefully this will keep Python from allocating a new array each time.
            Emacs.lossage.reverse()
            
            self.keysymhistory.reverse()
            self.keysymhistory.append( event.keysym )
            self.keysymhistory.reverse()
            #@nonl
            #@-node:ekr.20050527112828:<< old insert code >>
            #@nl
        
                
        if self.macroing:
            if self.macroing == 2 and stroke != '<Control-x>':
                return self.nameLastMacro( event )
            elif self.macroing == 3 and stroke != '<Control-x>':
                return self.getMacroName( event )
            else:
               self.recordKBDMacro( event, stroke )
             
        if  stroke == '<Control-g>':
            self.previousStroke = stroke
            return self.keyboardQuit( event )
            
        if self.mcStateManager.hasState():
            self.previousStroke = stroke
            return self.mcStateManager( event, stroke ) # EKR: Invoke the __call__ method.
            
        if self.kstrokeManager.hasKeyStroke( stroke ):
            self.previousStroke = stroke
            return self.kstrokeManager( event, stroke ) # EKR: Invoke the __call__ method.
    
        #@    << old code >>
        #@+node:ekr.20050527084754:<< old code >>
        
        #if self.uC:
        #    self.previousStroke = stroke
        #    return self.universalDispatch( event, stroke )
        
        #if self.controlx:
        #    self.previousStroke = stroke
        #     return self.doControlX( event, stroke )
        
        
        #if stroke in ('<Control-s>', '<Control-r>' ): 
        #    self.previousStroke = stroke
        #    return self.startIncremental( event, stroke )
        
        #if self.isearch:
        #   return self.iSearch( event )
        
        #if stroke == '<Alt-g>':
        #    self.previousStroke = stroke
        #    return self.startGoto( event )
        #if self.goto:
        #    return self.Goto( event )
        
        #if stroke == '<Alt-z>':
        #    self.previousStroke = stroke
        #    return self.startZap( event )
        
        #if self.zap:
        #    return self.zapTo( event )
        #@nonl
        #@-node:ekr.20050527084754:<< old code >>
        #@nl
        if self.regXRpl: # EKR: a generator.
            try:
                self.regXKey = event.keysym
                self.regXRpl.next() # EKR: next() may throw StopIteration.
            finally:
                return 'break'
    
        #@    << old code 2 >>
        #@+node:ekr.20050527084754.1:<< old code 2 >>
        
            #if self.howM:
            #    return self.howMany( event )
                
            #if self.abbrevMode:
            #    return self.abbrevCommand1( event )
                
            #if self.altx:
            #    return self.doAlt_X( event )
        
            #if stroke == '<Alt-percent>':
            #    self.previousStroke = stroke
            #    return self.masterQR( event )  
            #if self.qlisten:
            #    return self.masterQR( event )
                
            #if self.rString:
            #    return self.replaceString( event )
             
            #if self.negativeArg:
            #    return self.negativeArgument( event, stroke )
            
            #if stroke == '<Control-Alt-w>':
            #    self.previousStroke = '<Control-Alt-w>'   
            #    return 'break'
        #@nonl
        #@-node:ekr.20050527084754.1:<< old code 2 >>
        #@nl
        if self.abbrevOn:
            if self.expandAbbrev( event ) :
                return 'break'       
    
        if method:
            rt = method( event )
            self.previousStroke = stroke
            return rt
    #@nonl
    #@-node:mork.20041030164547.43:masterCommand
    #@+node:mork.20041102082023:keyboardQuit
    def keyboardQuit( self, event ):
        '''This method cleans the Emacs instance of state and ceases current operations.'''
        return self.stopControlX( event )#This method will eventually contain the stopControlX code.
        
    #@-node:mork.20041102082023:keyboardQuit
    #@+node:mork.20041031182258:add command dictionary methods
    #@+at
    # These methods create the dispatch dictionarys that the
    # Emacs instance uses to execute specific keystrokes and commands.
    # Dont mess with it if you dont understand this section, without these 
    # dictionarys
    # the Emacs system cant work.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041030183331:addCallBackDict (creates cbDict)
    def addCallBackDict( self ):
        '''This method adds a dictionary to the Emacs instance through which the masterCommand can
           call the specified method.'''
        cbDict = {
        'Alt-less' : lambda event, spot = '1.0' : self.moveTo( event, spot ),
        'Alt-greater': lambda event, spot = 'end' : self.moveTo( event, spot ),
        'Control-Right': lambda event, way = 1: self.moveword( event, way ),
        'Control-Left': lambda event, way = -1: self.moveword( event, way ),
        'Control-a': lambda event, spot = 'insert linestart': self.moveTo( event, spot ),
        'Control-e': lambda event, spot = 'insert lineend': self.moveTo( event, spot ),
        'Alt-Up': lambda event, spot = 'insert linestart': self.moveTo( event, spot ),
        'Alt-Down': lambda event, spot = 'insert lineend': self.moveTo( event, spot ),
        'Alt-f': lambda event, way = 1: self.moveword( event, way ),
        'Alt-b' : lambda event, way = -1: self.moveword( event, way ),
        'Control-o': self.insertNewLine,
        'Control-k': lambda event, frm = 'insert', to = 'insert lineend': self.kill( event, frm, to) ,
        'Alt-d': lambda event, frm = 'insert wordstart', to = 'insert wordend': self.kill( event,frm, to ),
        'Alt-Delete': lambda event: self.deletelastWord( event ),
        "Control-y": lambda event, frm = 'insert', which = 'c': self.walkKB( event, frm, which),
        "Alt-y": lambda event , frm = "insert", which = 'a': self.walkKB( event, frm, which ),
        "Alt-k": lambda event : self.killsentence( event ),
        'Control-s' : None,
        'Control-r' : None,
        'Alt-c': lambda event, which = 'cap' : self.capitalize( event, which ),
        'Alt-u': lambda event, which = 'up' : self.capitalize( event, which ),
        'Alt-l': lambda event, which = 'low' : self.capitalize( event, which ),
        'Alt-t': lambda event, sw = self.swapSpots: self.swapWords( event, sw ),
        'Alt-x': self.alt_X,
        'Control-x': self.startControlX,
        'Control-g': self.keyboardQuit,
        'Control-Shift-at': self.setRegion,
        'Control-w': lambda event, which = 'd' :self.killRegion( event, which ),
        'Alt-w': lambda event, which = 'c' : self.killRegion( event, which ),
        'Control-t': self.swapCharacters,
        'Control-u': None,
        'Control-l': None,
        'Alt-z': None,
        'Control-i': None,
        'Alt-Control-backslash': self.indentRegion,
        'Alt-m' : self.backToIndentation,
        'Alt-asciicircum' : self.deleteIndentation,
        'Control-d': self.deleteNextChar,
        'Alt-backslash': self.deleteSpaces, 
        'Alt-g': None,
        'Control-v' : lambda event, way = 'south': self.screenscroll( event, way ),
        'Alt-v' : lambda event, way = 'north' : self.screenscroll( event, way ),
        'Alt-equal': self.countRegion,
        'Alt-parenleft': self.insertParentheses,
        'Alt-parenright': self.movePastClose,
        'Alt-percent' : None,
        'Control-c': None,
        'Delete': lambda event, which = 'BackSpace': self.manufactureKeyPress( event, which ),
        'Control-p': lambda event, which = 'Up': self.manufactureKeyPress( event, which ),
        'Control-n': lambda event, which = 'Down': self.manufactureKeyPress( event, which ),
        'Control-f': lambda event, which = 'Right':self.manufactureKeyPress( event, which ),
        'Control-b': lambda event, which = 'Left': self.manufactureKeyPress( event, which ),
        'Control-Alt-w': None,
        'Alt-a': lambda event, which = 'bak': self.prevNexSentence( event, which ),
        'Alt-e': lambda event, which = 'for': self.prevNexSentence( event, which ),
        'Control-Alt-o': self.insertNewLineIndent,
        'Control-j': self.insertNewLineAndTab,
        'Alt-minus': self.negativeArgument,
        'Alt-slash': self.dynamicExpansion,
        'Control-Alt-slash': self.dynamicExpansion2,
        'Control-u': lambda event, keystroke = '<Control-u>': self.universalDispatch( event, keystroke ),
        'Alt-braceright': lambda event, which = 1: self.movingParagraphs( event, which ),
        'Alt-braceleft': lambda event , which = 0: self.movingParagraphs( event, which ),
        'Alt-q': self.fillParagraph,
        'Alt-h': self.selectParagraph,
        'Alt-semicolon': self.indentToCommentColumn,
        'Alt-0': lambda event, stroke = '<Alt-0>', number = 0: self.numberCommand( event, stroke, number ) ,
        'Alt-1': lambda event, stroke = '<Alt-1>', number = 1: self.numberCommand( event, stroke, number ) ,
        'Alt-2': lambda event, stroke = '<Alt-2>', number = 2: self.numberCommand( event, stroke, number ) ,
        'Alt-3': lambda event, stroke = '<Alt-3>', number = 3: self.numberCommand( event, stroke, number ) ,
        'Alt-4': lambda event, stroke = '<Alt-4>', number = 4: self.numberCommand( event, stroke, number ) ,
        'Alt-5': lambda event, stroke = '<Alt-5>', number = 5: self.numberCommand( event, stroke, number ) ,
        'Alt-6': lambda event, stroke = '<Alt-6>', number = 6: self.numberCommand( event, stroke, number ) ,
        'Alt-7': lambda event, stroke = '<Alt-7>', number = 7: self.numberCommand( event, stroke, number ) ,
        'Alt-8': lambda event, stroke = '<Alt-8>', number = 8: self.numberCommand( event, stroke, number ) ,
        'Alt-9': lambda event, stroke = '<Alt-9>', number = 9: self.numberCommand( event, stroke, number ) ,
        'Control-underscore': self.doUndo,
        'Alt-s': self.centerLine,
        'Control-z': self.suspend, 
        'Control-Alt-s': lambda event, stroke='<Control-s>': self.startIncremental( event, stroke, which='regexp' ),
        'Control-Alt-r': lambda event, stroke='<Control-r>': self.startIncremental( event, stroke, which='regexp' ),
        'Control-Alt-percent': lambda event: self.startRegexReplace() and self.masterQR( event ),
        'Escape': self.watchEscape,
        'Alt-colon': self.startEvaluate,
        'Alt-exclam': self.startSubprocess,
        'Alt-bar': lambda event: self.startSubprocess( event, which = 1 ),
        }
        
        return cbDict
    #@nonl
    #@-node:mork.20041030183331:addCallBackDict (creates cbDict)
    #@+node:mork.20041030183633:addXCommands
    def addXCommands( self ):
        
        xcommands = {
        '<Control-t>': self.transposeLines, 
        '<Control-u>': lambda event , way ='up': self.upperLowerRegion( event, way ),
        '<Control-l>':  lambda event , way ='low': self.upperLowerRegion( event, way ),
        '<Control-o>': self.removeBlankLines,
        '<Control-i>': self.insertFile,
        '<Control-s>': self.saveFile,
        '<Control-x>': self.exchangePointMark,
        '<Control-c>': self.shutdown,
        '<Control-b>': self.listBuffers,
        '<Control-Shift-at>': lambda event: event.widget.selection_clear(),
        '<Delete>' : lambda event, back = True: self.killsentence( event, back ),
        }
        
        return xcommands
    #@nonl
    #@-node:mork.20041030183633:addXCommands
    #@+node:mork.20041030190903:addAltXCommands
    def addAltXCommands( self ):
        
        #many of the simpler methods need self.keyboardQuit( event ) appended to the end to stop the Alt-x mode.
        doAltX= {
        'prepend-to-register': self.prependToRegister,
        'append-to-register': self.appendToRegister,
        'replace-string': self.replaceString,
        'replace-regex': lambda event:  self.activateReplaceRegex() and self.replaceString( event ),
        'sort-lines': self.sortLines,
        'sort-columns': self.sortColumns,
        'reverse-region': self.reverseRegion,
        'sort-fields': self.sortFields,
        'abbrev-mode': self.toggleAbbrevMode,
        'kill-all-abbrevs': self.killAllAbbrevs,
        'expand-region-abbrevs': self.regionalExpandAbbrev,
        'write-abbrev-file': self.writeAbbreviations,
        'read-abbrev-file': self.readAbbreviations,
        'fill-region-as-paragraph': self.fillRegionAsParagraph,
        'fill-region': self.fillRegion,
        'close-rectangle': self.closeRectangle,
        'how-many': self.startHowMany,
        'kill-paragraph': self.killParagraph,
        'backward-kill-paragraph': self.backwardKillParagraph,
        'backward-kill-sentence': lambda event: self.keyboardQuit( event ) and self.killsentence( event, back = True ),
        'name-last-kbd-macro': self.nameLastMacro,
        'load-file': self.loadMacros,
        'insert-keyboard-macro' : self.getMacroName,
        'list-abbrevs': self.listAbbrevs,
        'kill-word': lambda event, frm = 'insert wordstart', to = 'insert wordend': self.kill( event,frm, to ) and self.keyboardQuit( event ),
        'kill-line': lambda event, frm = 'insert', to = 'insert lineend': self.kill( event, frm, to) and self.keyboardQuit( event ), 
        'kill-sentence': lambda event : self.killsentence( event ) and self.keyboardQuit( event ),
        'kill-region': lambda event, which = 'd' :self.killRegion( event, which ) and self.keyboardQuit( event ),
        'yank': lambda event, frm = 'insert', which = 'c': self.walkKB( event, frm, which) and self.keyboardQuit( event ),
        'yank-pop' : lambda event , frm = "insert", which = 'a': self.walkKB( event, frm, which ) and self.keyboardQuit( event ),
        'backward-kill-word': lambda event: self.deletelastWord( event ) and self.keyboardQuit( event ),
        'backward-delete-char':lambda event, which = 'BackSpace': self.manufactureKeyPress( event, which ) and self.keyboardQuit( event ),
        'delete-char': lambda event: self.deleteNextChar( event ) and self.keyboardQuit( event ) , 
        'isearch-forward': lambda event: self.keyboardQuit( event ) and self.startIncremental( event, '<Control-s>' ),
        'isearch-backward': lambda event: self.keyboardQuit( event ) and self.startIncremental( event, '<Control-r>' ),
        'isearch-forward-regexp': lambda event: self.keyboardQuit( event ) and self.startIncremental( event, '<Control-s>', which = 'regexp' ),
        'isearch-backward-regexp': lambda event: self.keyboardQuit( event ) and self.startIncremental( event, '<Control-r>', which = 'regexp' ),
        'capitalize-word': lambda event, which = 'cap' : self.capitalize( event, which ) and self.keyboardQuit( event ),
        'upcase-word': lambda event, which = 'up' : self.capitalize( event, which ) and self.keyboardQuit( event ),
        'downcase-word': lambda event, which = 'low' : self.capitalize( event, which ) and self.keyboardQuit( event ),
        'indent-region': lambda event: self.indentRegion( event ) and self.keyboardQuit( event ),
        'indent-rigidly': lambda event: self.tabIndentRegion( event ) and self.keyboardQuit( event ),
        'indent-relative': self.indent_relative,
        'set-mark-command': lambda event: self.setRegion( event ) and self.keyboardQuit( event ),
        'kill-rectangle': lambda event: self.killRectangle( event ),
        'delete-rectangle': lambda event: self.deleteRectangle( event ),
        'yank-rectangle': lambda event: self.yankRectangle( event ),
        'open-rectangle': lambda event: self.openRectangle( event ),
        'clear-rectangle': lambda event: self.clearRectangle( event ),
        'copy-to-register': lambda event: self.setEvent( event, 's' ) and self.setNextRegister( event ),
        'insert-register': lambda event: self.setEvent( event, 'i' ) and self.setNextRegister( event ),
        'copy-rectangle-to-register': lambda event: self.setEvent( event, 'r' ) and self.setNextRegister( event ),
        'jump-to-register': lambda event: self.setEvent( event, 'j' ) and self.setNextRegister( event ),
        'point-to-register': lambda event: self.setEvent( event, 'space' ) and self.setNextRegister( event ),
        'number-to-register': lambda event: self.setEvent( event, 'n' ) and self.setNextRegister( event ),
        'increment-register': lambda event: self.setEvent( event, 'plus' ) and self.setNextRegister( event ),
        'view-register': lambda event: self.setEvent( event, 'view' ) and self.setNextRegister( event ),
        'beginning-of-line': lambda event, spot = 'insert linestart': self.moveTo( event, spot ) and self.keyboardQuit( event ),
        'end-of-line': lambda event, spot = 'insert lineend': self.moveTo( event, spot ) and self.keyboardQuit( event ),
        'keyboard-quit': lambda event: self.keyboardQuit( event ),
        'advertised-undo': lambda event: self.doUndo( event ) and self.keyboardQuit( event ),
        'back-to-indentation': lambda event: self.backToIndentation( event ) and self.keyboardQuit( event ),
        'delete-indentation': lambda event: self.deleteIndentation( event ) and self.keyboardQuit( event ),    
        'view-lossage': lambda event: self.viewLossage( event ),
         'transpose-chars': lambda event : self.swapCharacters( event ) and self.keyboardQuit( event ),
         'transpose-words': lambda event, sw = self.swapSpots: self.swapWords( event, sw ) and self.keyboardQuit( event ),
         'transpose-lines': lambda event: self.transposeLines( event ) and self.keyboardQuit( event ),
         'insert-file' : lambda event: self.insertFile( event ) and self.keyboardQuit( event ),
         'save-buffer' : lambda event: self.saveFile( event ) and self.keyboardQuit( event ),
         'split-line' : lambda event: self.insertNewLineIndent( event ) and self.keyboardQuit( event ),
         'upcase-region': lambda event: self.upperLowerRegion( event, 'up' ) and self.keyboardQuit( event ),
         'downcase-region': lambda event: self.upperLowerRegion( event , 'low' ) and self.keyboardQuit( event ),
         'dabbrev-expands': lambda event: self.dynamicExpansion( event ) and self.keyboardQuit( event ),
         'dabbrev-completion': lambda event: self.dynamicExpansion2( event ) and self.keyboardQuit( event ),
         'goto-line': lambda event: self.startGoto( event ),
         'goto-char': lambda event: self.startGoto( event, True ),
         'set-fill-prefix': lambda event: self.setFillPrefix( event ) and self.keyboardQuit( event ),
         'set-fill-column': lambda event: self.setFillColumn( event ),
         'center-line': lambda event: self.centerLine( event ) and self.keyboardQuit( event ),
         'center-region': lambda event: self.centerRegion( event ) and self.keyboardQuit( event ),
         'forward-char': lambda event, which = 'Right': self.keyboardQuit( event ) and self.manufactureKeyPress( event, which ),
         'backward-char': lambda event, which = 'Left': self.keyboardQuit( event ) and self.manufactureKeyPress( event, which ),
         'previous-line': lambda event, which = 'Up': self.keyboardQuit( event ) and self.manufactureKeyPress( event, which ),
         'next-line': lambda event, which = 'Down': self.keyboardQuit( event ) and self.manufactureKeyPress( event, which ),
         'digit-argument': lambda event: self.universalDispatch( event, '' ),
         'universal-argument': lambda event: self.universalDispatch( event, '' ),   
         'newline-and-indent': lambda event: self.insertNewLineAndTab( event ) and self.keyboardQuit( event ),
         'beginning-of-buffer': lambda event, spot = '1.0' : self.moveTo( event, spot ) and self.keyboardQuit( event ),
         'end-of-buffer': lambda event, spot = 'end' : self.moveTo( event, spot ) and self.keyboardQuit( event ),
         'scroll-up': lambda event, way = 'north' : self.screenscroll( event, way ) and self.keyboardQuit( event ),
         'scroll-down': lambda event, way = 'south': self.screenscroll( event, way ) and self.keyboardQuit( event ),
         'copy-to-buffer': lambda event, which = 'copy-to-buffer': self.setInBufferMode( event, which ),
         'insert-buffer': lambda event, which = 'insert-buffer': self.setInBufferMode( event, which ),
         'append-to-buffer': lambda event , which = 'append-to-buffer':  self.setInBufferMode( event, which ),
         'prepend-to-buffer': lambda event, which = 'prepend-to-buffer': self.setInBufferMode( event, which ),
         'switch-to-buffer': lambda event, which = 'switch-to-buffer': self.setInBufferMode( event, which ),
         'list-buffers' : lambda event: self.listBuffers( event ),
         'kill-buffer' : lambda event, which = 'kill-buffer': self.setInBufferMode( event, which ),
         'rename-buffer': lambda event: self.renameBuffer( event ),
         'query-replace': lambda event: self.masterQR( event ), 
         'query-replace-regex': lambda event: self.startRegexReplace() and self.masterQR( event ),
         'inverse-add-global-abbrev': lambda event: self.abbreviationDispatch( event, 2 ) ,  
         'expand-abbrev': lambda event : self.keyboardQuit( event ) and self.expandAbbrev( event ), 
         'iconfify-or-deiconify-frame': lambda event: self.suspend( event ) and self.keyboardQuit( event ),
         'save-buffers-kill-emacs': lambda event: self.keyboardQuit( event ) and self.shutdown( event ),
         're-search-forward': lambda event: self.reStart( event ),
         're-search-backward': lambda event: self.reStart( event, which = 'backward' ),
         'diff': self.diff, 
         'what-line': self.whatLine,
         'flush-lines': lambda event: self.startLines( event ),
         'keep-lines': lambda event: self.startLines( event, which = 'keep' ),
         'make-directory': lambda event: self.makeDirectory( event ),
         'remove-directory': lambda event: self.removeDirectory( event ),
         'delete-file': lambda event: self.deleteFile( event ),
         'search-forward': lambda event: self.startNonIncrSearch( event, 'for' ),
         'search-backward': lambda event: self.startNonIncrSearch( event, 'bak' ),
         'word-search-forward': lambda event : self.startWordSearch( event, 'for' ),
         'word-search-backward': lambda event: self.startWordSearch( event, 'bak' ),
         'repeat-complex-command': lambda event: self.repeatComplexCommand( event ),
         'eval-expression': self.startEvaluate,
         'tabify': self.tabify,
         'untabify': lambda event: self.tabify( event, which = 'untabify' ),
         'shell-command': self.startSubprocess,
         'shell-command-on-region': lambda event: self.startSubprocess( event, which=1 ),
        }    
        #Note: if we are reusing some of the cbDict lambdas we need to alter many by adding: self.keyboardQuit( event )
        #Otherwise the darn thing just sits in Alt-X land.  Putting the 'and self.keyboardQuit( event )' part in the killbuffer
        #and yanking it out for each new item, works well.  Adding it to a register might be good to.
        return doAltX
    
    
    
    
    
    
     
    #@nonl
    #@-node:mork.20041030190903:addAltXCommands
    #@+node:mork.20041030190729:addRegisterItems
    def addRegisterItems( self ):
        
        regMeths = {
        's' : self.copyToRegister,
        'i' : self.insertFromRegister,
        'n': self.numberToRegister,
        'plus': self.incrementRegister,
        'space': self.pointToRegister,
        'j': self.jumpToRegister,
        'a': lambda event , which = 'a': self._ToReg( event, which ),
        'p': lambda event , which = 'p': self._ToReg( event, which ),
        'r': self.copyRectangleToRegister,
        'view' : self.viewRegister,
        }    
        
        regText = {
        's' : 'copy to register',
        'i' : 'insert from register',
        'plus': 'increment register',
        'n' : 'number to register',
        'p' : 'prepend to register',
        'a' : 'append to register',
        'space' : 'point to register',
        'j': 'jump to register',
        'r': 'rectangle to register',
        'view': 'view register',
        }
        
        return regMeths, regText
    #@nonl
    #@-node:mork.20041030190729:addRegisterItems
    #@-others
    #@nonl
    #@-node:mork.20041031182258:add command dictionary methods
    #@+node:mork.20041031183614:general utility methods
    #@+at
    # These methods currently do not have a specific class that they belong 
    # to.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041031195549:buffer altering methods
    #@+others
    #@+node:mork.20041030164547.31:moveTo
    def moveTo( self, event, spot ):
        tbuffer = event.widget
        tbuffer.mark_set( Tkinter.INSERT, spot )
        tbuffer.see( spot )
        return 'break'
    #@-node:mork.20041030164547.31:moveTo
    #@+node:mork.20041030164547.33:moveword
    def moveword( self, event, way  ):
        '''This function moves the cursor to the next word, direction dependent on the way parameter'''
        
        tbuffer = event.widget
        #i = way
        
        ind = tbuffer.index( 'insert' )
        if way == 1:
             ind = tbuffer.search( '\w', 'insert', stopindex = 'end', regexp=True )
             if ind:
                nind = '%s wordend' % ind
             else:
                nind = 'end'
        else:
             ind = tbuffer.search( '\w', 'insert -1c', stopindex= '1.0', regexp = True, backwards = True )
             if ind:
                nind = '%s wordstart' % ind 
             else:
                nind = '1.0'
        tbuffer.mark_set( 'insert', nind )
        tbuffer.see( 'insert' )
        tbuffer.event_generate( '<Key>' )
        tbuffer.update_idletasks()
        return 'break'
    #@nonl
    #@-node:mork.20041030164547.33:moveword
    #@+node:mork.20041030164547.39:capitalize
    def capitalize( self, event, which ):
        tbuffer = event.widget
        text = tbuffer.get( 'insert wordstart', 'insert wordend' )
        i = tbuffer.index( 'insert' )
        if text == ' ': return 'break'
        tbuffer.delete( 'insert wordstart', 'insert wordend' )
        if which == 'cap':
            text = text.capitalize() 
        if which == 'low':
            text = text.lower()
        if which == 'up':
            text = text.upper()
        tbuffer.insert( 'insert', text )
        tbuffer.mark_set( 'insert', i )    
        return 'break' 
    #@-node:mork.20041030164547.39:capitalize
    #@+node:mork.20041030164547.40:swapWords
    def swapWords( self, event , swapspots ):
        tbuffer = event.widget
        txt = tbuffer.get( 'insert wordstart', 'insert wordend' )
        if txt == ' ' : return 'break'
        i = tbuffer.index( 'insert wordstart' )
        if len( swapspots ) != 0:
            def swp( find, ftext, lind, ltext ):
                tbuffer.delete( find, '%s wordend' % find )
                tbuffer.insert( find, ltext )
                tbuffer.delete( lind, '%s wordend' % lind )
                tbuffer.insert( lind, ftext )
                swapspots.pop()
                swapspots.pop()
                return 'break'
            if tbuffer.compare( i , '>', swapspots[ 1 ] ):
                return swp( i, txt, swapspots[ 1 ], swapspots[ 0 ] )
            elif tbuffer.compare( i , '<', swapspots[ 1 ] ):
                return swp( swapspots[ 1 ], swapspots[ 0 ], i, txt )
            else:
                return 'break'
        else:
            swapspots.append( txt )
            swapspots.append( i )
            return 'break'
    #@-node:mork.20041030164547.40:swapWords
    #@+node:mork.20041030164547.103:insertParentheses
    def insertParentheses( self, event ):
        tbuffer = event.widget
        tbuffer.insert( 'insert', '()' )
        tbuffer.mark_set( 'insert', 'insert -1c' )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.103:insertParentheses
    #@+node:mork.20041123095436:replace-string and replace-regex
    #@+at
    # both commands use the replaceString method, differentiated by a state 
    # variable
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041030164547.115:replaceString
    #self.rString = False
    #self._sString = ''
    #self._rpString = ''
    def replaceString( self, event ):
        
        svar, label = self.getSvarLabel( event )
        if event.keysym in ( 'Control_L', 'Control_R' ):
            return
        rS = self.mcStateManager.getState( 'rString' )
        regex = self._useRegex
        if not rS:
            #self.rString = 1
            self.mcStateManager.setState( 'rString', 1 )
            self._sString = ''
            self._rpString = ''
            if regex:
                svar.set( 'Replace Regex' )
            else:
                svar.set( 'Replace String' )
            return
        if event.keysym == 'Return':
            #self.rString = self.rString + 1
            rS = rS + 1
            self.mcStateManager.setState( 'rString', rS  )
            #return 'break'
        if rS == 1:
            svar.set( '' )
            #self.rString = self.rString + 1
            rS = rS + 1
            self.mcStateManager.setState( 'rString', rS )
        if rS == 2:
            self.setSvar( event, svar )
            self._sString = svar.get()
            return 'break'
        if rS == 3:
            if regex:
                svar.set( 'Replace regex %s with:' % self._sString )
            else:
                svar.set( 'Replace string %s with:' % self._sString )
            self.mcStateManager.setState( 'rString',rS + 1 )
            #self.rString = self.rString + 1
            return 'break'
        if rS == 4:
            svar.set( '' )
            #self.rString = self.rString + 1
            rS = rS + 1
            self.mcStateManager.setState( 'rString', rS )
        if rS == 5:
            self.setSvar( event, svar )
            self._rpString = svar.get()
            return 'break'
        if rS == 6:
            tbuffer = event.widget
            i = 'insert'
            end = 'end'
            ct = 0
            if tbuffer.tag_ranges( 'sel' ):
                i = tbuffer.index( 'sel.first' )
                end = tbuffer.index( 'sel.last' )
            if regex:
                txt = tbuffer.get( i, end )
                try:
                    pattern = re.compile( self._sString )
                except:
                    self.keyboardQuit( event )
                    svar.set( "Illegal regular expression" )
                    return 'break'
                ct = len( pattern.findall( txt ) )
                if ct:
                    ntxt = pattern.sub( self._rpString, txt )
                    tbuffer.delete( i, end )
                    tbuffer.insert( i, ntxt )
            else:
                txt = tbuffer.get( i, end )
                ct = txt.count( self._sString )
                if ct:
                    ntxt = txt.replace( self._sString, self._rpString )
                    tbuffer.delete( i, end )
                    tbuffer.insert( i, ntxt )
                    
            svar.set( 'Replaced %s occurances' % ct )
            #label.configure( background = 'lightgrey' )
            self.setLabelGrey( label ) 
            #self.rString = False
            self.mcStateManager.clear()
            self._useRegex = False
            #self.mcStateManager.setState( 'rString', False )
            return self._tailEnd( tbuffer )
    
    #@-node:mork.20041030164547.115:replaceString
    #@+node:mork.20041123095123:activateReplaceRegex
    def activateReplaceRegex( self ):
        '''This method turns regex replace on for replaceString'''
        self._useRegex = True
        return True
        
    
    #@-node:mork.20041123095123:activateReplaceRegex
    #@-others
    #@nonl
    #@-node:mork.20041123095436:replace-string and replace-regex
    #@+node:mork.20041030164547.116:swapCharacters
    def swapCharacters( self, event ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        c1 = tbuffer.get( 'insert', 'insert +1c' )
        c2 = tbuffer.get( 'insert -1c', 'insert' )
        tbuffer.delete( 'insert -1c', 'insert' )
        tbuffer.insert( 'insert', c1 )
        tbuffer.delete( 'insert', 'insert +1c' )
        tbuffer.insert( 'insert', c2 )
        tbuffer.mark_set( 'insert', i )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.116:swapCharacters
    #@+node:mork.20041123095507:insert new line methods
    #@+others
    #@+node:mork.20041030164547.117:insertNewLine
    def insertNewLine( self,event ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        tbuffer.insert( 'insert', '\n' )
        tbuffer.mark_set( 'insert', i )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.117:insertNewLine
    #@+node:mork.20041030164547.131:insertNewLineIndent
    #self.negArgs = { '<Alt-c>': changePreviousWord,
    #'<Alt-u>' : changePreviousWord,
    #'<Alt-l>': changePreviousWord }
    
    
    
    def insertNewLineIndent( self, event ):
        tbuffer =  event.widget
        txt = tbuffer.get( 'insert linestart', 'insert lineend' )
        txt = self.getWSString( txt )
        i = tbuffer.index( 'insert' )
        tbuffer.insert( i, txt )
        tbuffer.mark_set( 'insert', i )    
        return self.insertNewLine( event )
    #@-node:mork.20041030164547.131:insertNewLineIndent
    #@+node:mork.20041103135515:insertNewLineAndTab
    def insertNewLineAndTab( self, event ):
        '''Insert a newline and tab'''
        tbuffer = event.widget
        self.insertNewLine( event )
        i = tbuffer.index( 'insert +1c' )
        tbuffer.insert( i, '\t' )
        tbuffer.mark_set( 'insert', '%s lineend' % i )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041103135515:insertNewLineAndTab
    #@-others
    #@nonl
    #@-node:mork.20041123095507:insert new line methods
    #@+node:mork.20041030164547.148:transposeLines
    def transposeLines( self, event ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        i1, i2 = i.split( '.' )
        i1 = str( int( i1 ) -1 )
        if i1 != '0':
            l2 = tbuffer.get( 'insert linestart', 'insert lineend' )
            tbuffer.delete( 'insert linestart-1c', 'insert lineend' )
            tbuffer.insert( i1+'.0', l2 +'\n')
        else:
            l2 = tbuffer.get( '2.0', '2.0 lineend' )
            tbuffer.delete( '2.0', '2.0 lineend' )
            tbuffer.insert( '1.0', l2 + '\n' )
        return self._tailEnd( tbuffer )         
    #@-node:mork.20041030164547.148:transposeLines
    #@+node:mork.20041030164547.130:changePreviousWord
    def changePreviousWord( self, event, stroke ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        self.moveword( event, -1  )
        if stroke == '<Alt-c>': 
            self.capitalize( event, 'cap' )
        elif stroke =='<Alt-u>':
             self.capitalize( event, 'up' )
        elif stroke == '<Alt-l>': 
            self.capitalize( event, 'low' )
        tbuffer.mark_set( 'insert', i )
        self.stopControlX( event )
        return self._tailEnd( tbuffer )    
    #@-node:mork.20041030164547.130:changePreviousWord
    #@+node:mork.20041030164547.150:removeBlankLines
    def removeBlankLines( self, event ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        i1, i2 = i.split( '.' )
        i1 = int( i1 )
        dindex = []
        if tbuffer.get( 'insert linestart', 'insert lineend' ).strip() == '':
            while 1:
                if str( i1 )+ '.0'  == '1.0' :
                    break 
                i1 = i1 - 1
                txt = tbuffer.get( '%s.0' % i1, '%s.0 lineend' % i1 )
                txt = txt.strip()
                if len( txt ) == 0:
                    dindex.append( '%s.0' % i1)
                    dindex.append( '%s.0 lineend' % i1 )
                elif dindex:
                    tbuffer.delete( '%s-1c' % dindex[ -2 ], dindex[ 1 ] )
                    tbuffer.event_generate( '<Key>' )
                    tbuffer.update_idletasks()
                    break
                else:
                    break
        i = tbuffer.index( 'insert' )
        i1, i2 = i.split( '.' )
        i1 = int( i1 )
        dindex = []
        while 1:
            if tbuffer.index( '%s.0 lineend' % i1 ) == tbuffer.index( 'end' ):
                break
            i1 = i1 + 1
            txt = tbuffer.get( '%s.0' % i1, '%s.0 lineend' % i1 )
            txt = txt.strip() 
            if len( txt ) == 0:
                dindex.append( '%s.0' % i1 )
                dindex.append( '%s.0 lineend' % i1 )
            elif dindex:
                tbuffer.delete( '%s-1c' % dindex[ 0 ], dindex[ -1 ] )
                tbuffer.event_generate( '<Key>' )
                tbuffer.update_idletasks()
                break
            else:
                break
    #@-node:mork.20041030164547.150:removeBlankLines
    #@+node:mork.20041030164547.101:screenscroll
    def screenscroll( self, event, way = 'north' ):
        tbuffer = event.widget
        chng = self.measure( tbuffer )
        i = tbuffer.index( 'insert' )
        
        if way == 'north':
            #top = chng[ 1 ]
            i1, i2 = i.split( '.' )
            i1 = int( i1 ) - chng[ 0 ]
        else:
            #bottom = chng[ 2 ]
            i1, i2 = i.split( '.' )
            i1 = int( i1 ) + chng[ 0 ]
            
        tbuffer.mark_set( 'insert', '%s.%s' % ( i1, i2 ) )
        tbuffer.see( 'insert' )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.101:screenscroll
    #@+node:mork.20041030164547.22:exchangePointMark
    def exchangePointMark( self, event ):
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        s1 = tbuffer.index( 'sel.first' )
        s2 = tbuffer.index( 'sel.last' )
        i = tbuffer.index( 'insert' )
        if i == s1:
            tbuffer.mark_set( 'insert', s2 )
        else:
            tbuffer.mark_set('insert', s1 )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.22:exchangePointMark
    #@+node:mork.20041030164547.96:backToIndentation
    def backToIndentation( self, event ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert linestart' )
        i2 = tbuffer.search( r'\w', i, stopindex = '%s lineend' % i, regexp = True )
        tbuffer.mark_set( 'insert', i2 )
        tbuffer.update_idletasks()
        return 'break'
    #@-node:mork.20041030164547.96:backToIndentation
    #@+node:mork.20041124130434:indent-relative
    def indent_relative( self, event ):
        
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        l,c = i.split( '.' )
        c2 = int( c )
        l2 = int( l ) - 1
        if l2 < 1: return self.keyboardQuit( event )
        txt = tbuffer.get( '%s.%s' % (l2, c2 ), '%s.0 lineend' % l2 )
        if len( txt ) <= len( tbuffer.get( 'insert', 'insert lineend' ) ):
            tbuffer.insert(  'insert', '\t' )
        else:
            reg = re.compile( '(\s+)' )
            ntxt = reg.split( txt )
            replace_word = re.compile( '\w' )
            for z in ntxt:
                if z.isspace():
                    tbuffer.insert( 'insert', z )
                    break
                else:
                    z = replace_word.subn( ' ', z )
                    tbuffer.insert( 'insert', z[ 0 ] )
                    tbuffer.update_idletasks()
            
            
        self.keyboardQuit( event )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041124130434:indent-relative
    #@+node:mork.20041030164547.129:negativeArgument
    #self.negativeArg = False
    def negativeArgument( self, event, stroke = None ):
        #global negativeArg
        svar, label = self.getSvarLabel( event )
        svar.set( "Negative Argument" )
        label.configure( background = 'lightblue' )
        nA = self.mcStateManager.getState( 'negativeArg' )
        if not nA:
            self.mcStateManager.setState( 'negativeArg', True )
            #self.negativeArg = True
        if nA:
            if self.negArgs.has_key( stroke ):
                self.negArgs[ stroke ]( event , stroke)
        return 'break'
    #@-node:mork.20041030164547.129:negativeArgument
    #@+node:mork.20041030164547.114:movePastClose
    def movePastClose( self, event ):
        tbuffer = event.widget
        i = tbuffer.search( '(', 'insert' , backwards = True ,stopindex = '1.0' )
        icheck = tbuffer.search( ')', 'insert',  backwards = True, stopindex = '1.0' )
        if ''  ==  i:
            return 'break'
        if icheck:
            ic = tbuffer.compare( i, '<', icheck )
            if ic: 
                return 'break'
        i2 = tbuffer.search( ')', 'insert' ,stopindex = 'end' )
        i2check = tbuffer.search( '(', 'insert', stopindex = 'end' )
        if '' == i2:
            return 'break'
        if i2check:
            ic2 = tbuffer.compare( i2, '>', i2check )
            if ic2:
                return 'break'
        ib = tbuffer.index( 'insert' )
        tbuffer.mark_set( 'insert', '%s lineend +1c' % i2 )
        if tbuffer.index( 'insert' ) == tbuffer.index( '%s lineend' % ib ):
            tbuffer.insert( 'insert' , '\n')
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.114:movePastClose
    #@+node:mork.20041030164547.119:prevNexSentence
    def prevNexSentence( self, event , way ):
        tbuffer = event.widget
        if way == 'bak':
            i = tbuffer.search( '.', 'insert', backwards = True, stopindex = '1.0' )
            if i:
                i2 = tbuffer.search( '.', i, backwards = True, stopindex = '1.0' )
                if not i2:
                    i2 = '1.0'
                if i2:
                    i3 = tbuffer.search( '\w', i2, stopindex = i, regexp = True )
                    if i3:
                        tbuffer.mark_set( 'insert', i3 )
            else:
                tbuffer.mark_set( 'insert', '1.0' )
        else:
            i = tbuffer.search( '.', 'insert', stopindex = 'end' )
            if i:
                tbuffer.mark_set( 'insert', '%s +1c' %i )
            else:
                tbuffer.mark_set( 'insert', 'end' )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.119:prevNexSentence
    #@+node:mork.20041031202438:selectAll
    def selectAll( event ):
    
        event.widget.tag_add( 'sel', '1.0', 'end' )
        return 'break'
        
    #@-node:mork.20041031202438:selectAll
    #@+node:mork.20041120195951:suspend
    def suspend( self, event ):
        
        widget = event.widget
        widget.winfo_toplevel().iconify()
    #@-node:mork.20041120195951:suspend
    #@-others
    #@nonl
    #@-node:mork.20041031195549:buffer altering methods
    #@+node:mork.20041031195908:informational methods
    #@+others
    #@+node:mork.20041030164547.118:lineNumber
    def lineNumber( self, event ):
        self.stopControlX( event )
        svar, label = self.getSvarLabel( event )
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        i1, i2 = i.split( '.' )
        c = tbuffer.get( 'insert', 'insert + 1c' )
        txt = tbuffer.get( '1.0', 'end' )
        txt2 = tbuffer.get( '1.0', 'insert' )
        perc = len( txt ) * .01
        perc = int( len( txt2 ) / perc )
        svar.set( 'Char: %s point %s of %s(%s%s)  Column %s' %( c, len( txt2), len( txt), perc,'%', i1 ) )
        return 'break'
    #@-node:mork.20041030164547.118:lineNumber
    #@+node:mork.20041102161859:viewLossage
    def viewLossage( self, event ):
        
        svar, label = self.getSvarLabel( event )
        loss = ''.join( Emacs.lossage )
        self.keyboardQuit( event )
        svar.set( loss )
    #@nonl
    #@-node:mork.20041102161859:viewLossage
    #@+node:mork.20041121195816:whatLine
    def whatLine( self, event ):
        
        tbuffer = event.widget
        svar, label = self.getSvarLabel( event )
        i = tbuffer.index( 'insert' )
        i1, i2 = i.split( '.' )
        self.keyboardQuit( event )
        svar.set( "Line %s" % i1 )
    #@-node:mork.20041121195816:whatLine
    #@-others
    #@nonl
    #@-node:mork.20041031195908:informational methods
    #@+node:mork.20041031195908.1:pure utility methods
    #@+others
    #@+node:mork.20041102151939:setEvent
    def setEvent( self, event, l ):
        event.keysym = l
        return event
        
    #@-node:mork.20041102151939:setEvent
    #@+node:mork.20041030164547.127:getWSString
    def getWSString( self, txt ):
        ntxt = []
        for z in txt:
            if z == '\t':
                ntxt.append( z )
            else:
                ntxt.append( ' ' )
        return ''.join( ntxt )
    #@-node:mork.20041030164547.127:getWSString
    #@+node:mork.20041030164547.135:findPre
    def findPre( self, a, b ):
        st = ''
        for z in a:
            st1 = st + z
            if b.startswith( st1 ):
                st = st1
            else:
                return st
        return st  
    #@-node:mork.20041030164547.135:findPre
    #@+node:mork.20041030164547.100:measure
    def measure( self, tbuffer ):
        i = tbuffer.index( 'insert' )
        i1, i2 = i.split( '.' )
        start = int( i1 )
        watch = 0
        ustart = start
        pone = 1
        top = i
        bottom = i
        while pone:
            ustart = ustart - 1
            if ustart < 0:
                break
            ds = '%s.0' % ustart
            pone = tbuffer.dlineinfo( ds )
            if pone:
                top = ds
                watch = watch  + 1
        
        pone = 1
        ustart = start
        while pone:
            ustart = ustart +1
            ds = '%s.0' % ustart
            pone = tbuffer.dlineinfo( ds )
            if pone:
                bottom = ds
                watch = watch + 1
                
        return watch , top, bottom
    #@-node:mork.20041030164547.100:measure
    #@+node:mork.20041030164547.95:manufactureKeyPress
    def manufactureKeyPress( self, event, which ):
        tbuffer = event.widget
        tbuffer.event_generate( '<Key>',  keysym = which  )
        tbuffer.update_idletasks()
        return 'break'
    #@nonl
    #@-node:mork.20041030164547.95:manufactureKeyPress
    #@+node:mork.20041030164547.83:changecbDict
    def changecbDict( self, changes ):
        for z in changes:
            if self.cbDict.has_key( z ):
                self.cbDict[ z ] = self.changes[ z ]
    #@-node:mork.20041030164547.83:changecbDict
    #@+node:mork.20041030164547.92:removeRKeys
    def removeRKeys( self, widget ):
        mrk = 'sel'
        widget.tag_delete( mrk )
        widget.unbind( '<Left>' )
        widget.unbind( '<Right>' )
        widget.unbind( '<Up>' )
        widget.unbind( '<Down>' )
    #@-node:mork.20041030164547.92:removeRKeys
    #@+node:mork.20041030164547.142:_findMatch2
    def _findMatch2( self, svar, fdict = None ):#, fdict = self.doAltX ):
        '''This method returns a sorted list of matches.'''
        if not fdict:
            fdict = self.doAltX
        txt = svar.get()
        if not txt.isspace() and txt != '':
            txt = txt.strip()
            pmatches = filter( lambda a : a.startswith( txt ), fdict )
        else:
            pmatches = []
        pmatches.sort()
        return pmatches
        #if pmatches:
        #    #mstring = reduce( self.findPre, pmatches )
        #    #return mstring
        #return txt
    #@-node:mork.20041030164547.142:_findMatch2
    #@+node:mork.20041102133805:_findMatch
    def _findMatch( self, svar, fdict = None ):#, fdict = self.doAltX ):
        '''This method finds the first match it can find in a sorted list'''
        if not fdict:
            fdict = self.doAltX
        txt = svar.get()
        pmatches = filter( lambda a : a.startswith( txt ), fdict )
        pmatches.sort()
        if pmatches:
            mstring = reduce( self.findPre, pmatches )
            return mstring
        return txt
    #@-node:mork.20041102133805:_findMatch
    #@-others
    #@nonl
    #@-node:mork.20041031195908.1:pure utility methods
    #@-others
    #@nonl
    #@-node:mork.20041031183614:general utility methods
    #@+node:mork.20041120223251:shutdown methods
    #@+others
    #@+node:mork.20041120222336:shutdown
    def shutdown( self, event ):
        
        self.shuttingdown = True
        if self.shutdownhook:
            self.shutdownhook()
        else:
            sys.exit( 0 )
    #@nonl
    #@-node:mork.20041120222336:shutdown
    #@+node:mork.20041120223251.1:setShutdownHook
    def setShutdownHook( self, hook ):
            
        self.shutdownhook = hook
    #@nonl
    #@-node:mork.20041120223251.1:setShutdownHook
    #@-others
    #@nonl
    #@-node:mork.20041120223251:shutdown methods
    #@+node:mork.20041031182215:Label( minibuffer ) and svar methods
    #@+at
    # Two closely related categories under this one heading.  Svars are the 
    # internals of the minibuffer
    # and the labels are the presentation of those internals
    # 
    #@-at
    #@@c
    
    #@+others
    #@+node:mork.20041102183901:label( minibuffer ) methods
    #@+node:mork.20041030164547.2:setLabelGrey
    def setLabelGrey( self, label ):
        label.configure( background = 'lightgrey' )
    #@-node:mork.20041030164547.2:setLabelGrey
    #@+node:mork.20041030164547.3:setLabelBlue
    def setLabelBlue( self ,label ):
        label.configure( background = 'lightblue' ) 
    #@-node:mork.20041030164547.3:setLabelBlue
    #@+node:mork.20041030164547.86:resetMiniBuffer
    def resetMiniBuffer( self, event ):
        svar, label = self.getSvarLabel( event )
        svar.set( '' )
        label.configure( background = 'lightgrey' )
    #@-node:mork.20041030164547.86:resetMiniBuffer
    #@-node:mork.20041102183901:label( minibuffer ) methods
    #@+node:mork.20041031182943:svar methods
    #@+at
    # These methods get and alter the Svar variable which is a Tkinter
    # StringVar.  This StringVar contains what is displayed in the minibuffer.
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041030164547.112:getSvarLabel
    def getSvarLabel( self, event ):
        
        '''returns the StringVar and Label( minibuffer ) for a specific Text editor'''
        svar = self.svars[ event.widget ]
        label = self.mbuffers[ event.widget ]
        return svar, label
    
    #@-node:mork.20041030164547.112:getSvarLabel
    #@+node:mork.20041030164547.113:setSvar
    def setSvar( self, event, svar ):
        '''Alters the StringVar svar to represent the change in the event.
           It mimics what would happen with the keyboard and a Text editor
           instead of plain accumalation.''' 
        t = svar.get()  
        if event.char == '\b':
               if len( t ) == 1:
                   t = ''
               else:
                   t = t[ 0 : -1 ]
               svar.set( t )
        else:
                t = t + event.char
                svar.set( t )
    #@-node:mork.20041030164547.113:setSvar
    #@-others
    #@nonl
    #@-node:mork.20041031182943:svar methods
    #@-others
    #@nonl
    #@-node:mork.20041031182215:Label( minibuffer ) and svar methods
    #@+node:mork.20041031194746:configurable methods
    #@+at
    # These methods contain methods by which an Emacs instance is extended, 
    # changed, added to , etc...
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041031182643:tailEnd methods
    #@+others
    #@+node:mork.20041030164547.4:_tailEnd
    def _tailEnd( self, tbuffer ):
        '''This returns the tailEnd function that has been configure for the tbuffer parameter.'''
        if self.tailEnds.has_key( tbuffer ):
            return self.tailEnds[ tbuffer ]( tbuffer )
        else:
            return 'break'
    #@-node:mork.20041030164547.4:_tailEnd
    #@+node:mork.20041030164547.5:setTailEnd
    #self.tailEnds = {}
    def setTailEnd( self, tbuffer , tailCall ):
        '''This method sets a ending call that is specific for a particular Text widget.
           Some environments require that specific end calls be made after a keystroke
           or command is executed.'''
        self.tailEnds[ tbuffer ] = tailCall
    #@-node:mork.20041030164547.5:setTailEnd
    #@-others
    #@nonl
    #@-node:mork.20041031182643:tailEnd methods
    #@+node:mork.20041031182643.1:undoer methods
    #@+at
    # Emacs requires an undo mechanism be added from the environment.
    # If there is no undo mechanism added, there will be no undo functionality 
    # in the instance.
    #@-at
    #@@c
    
    
    
    #@+others
    #@+node:mork.20041030164547.6:setUndoer
    #self.undoers = {}
    def setUndoer( self, tbuffer, undoer ):
        '''This method sets the undoer method for the Emacs instance.'''
        self.undoers[ tbuffer ] = undoer
    #@-node:mork.20041030164547.6:setUndoer
    #@+node:mork.20041030164547.7:doUndo
    def doUndo(  self, event, amount = 1 ):
        tbuffer = event.widget
        if self.undoers.has_key( tbuffer ):
            for z in xrange( amount ):
                self.undoers[ tbuffer ]()
        return 'break'
    #@-node:mork.20041030164547.7:doUndo
    #@-others
    #@nonl
    #@-node:mork.20041031182643.1:undoer methods
    #@+node:mork.20041030164547.30:setBufferStrokes
    #mbuffers = {}
    #svars = {}
    def setBufferStrokes( self, tbuffer, label ):
            '''setBufferStrokes takes a Tk Text widget called 'tbuffer'. 'stext' is a function or method
            that when called will return the value of the search text. 'rtext' is a function or method
            that when called will return the value of the replace text.  It is this method and
            getHelpText that users of the temacs module should call.  The rest are callback functions
            that enable the Emacs emulation.'''
            
            g.trace(tbuffer,label)
        
            Emacs.Emacs_instances[ tbuffer ] = self
            def cb( evstring ):
                _cb = None
                if self.cbDict.has_key( evstring ):
                    _cb = self.cbDict[ evstring ]
                evstring = '<%s>' % evstring
                if evstring != '<Key>':
                    # g.trace(evstring)
                    tbuffer.bind( evstring,  lambda event, meth = _cb: self.masterCommand( event, meth , evstring) )
                else:
                    # g.trace('+',evstring)
                    tbuffer.bind( evstring,  lambda event, meth = _cb: self.masterCommand( event, meth , evstring), '+' )
    
            # EKR: create one binding for each entry in cbDict.
            for z in self.cbDict:
                cb( z )
            
            self.mbuffers[ tbuffer ] = label
            self.svars[ tbuffer ] = Tkinter.StringVar()
            def setVar( event ):
                label = self.mbuffers[ event.widget ]
                svar = self.svars[ event.widget ]
                label.configure( textvariable = svar )
            tbuffer.bind( '<FocusIn>', setVar, '+' )
            def scrollTo( event ):
                event.widget.see( 'insert' )
            
            #tbuffer.bind( '<Enter>', scrollTo, '+' )
            
            # EKR: This _adds_ a binding for all <Key> events, so _all_ key events go through masterCommand.
            cb( 'Key' )
    #@-node:mork.20041030164547.30:setBufferStrokes
    #@+node:mork.20041101190309:extendAltX
    def extendAltX( self, name, function ):
        '''A simple method that extends the functions Alt-X offers.'''
        
        nfunction = new.instancemethod( function, self, Emacs ) #making it an instance method allows the function to be passed 'self'.
        self.doAltX[ name ] = nfunction
        
    
    #@-node:mork.20041101190309:extendAltX
    #@+node:mork.20041102094716:reconfigureKeyStroke
    def reconfigureKeyStroke( self, tbuffer, keystroke , set_to ):
        
        '''This method allows the user to reconfigure what a keystroke does.
           This feature is alpha at best, and untested.'''
    
        if self.cbDict.has_key( set_to ):
            
            command = self.cbDict[ set_to ]
            self.cbDict[ keystroke ] = command
            evstring = '<%s>' % keystroke
            tbuffer.bind( evstring,  lambda event, meth = command: self.masterCommand( event, meth , evstring)  )
    #@nonl
    #@-node:mork.20041102094716:reconfigureKeyStroke
    #@+node:mork.20041103155347:buffer recognition and alterers
    #@+at
    # an Emacs instance does not have knowledge of what is considered a buffer 
    # in the environment.
    # It must be configured by the user so that it can operate on the other 
    # buffers.  Otherwise
    # these methods will be useless.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041104094826:configure buffer methods
    #@+others
    #@+node:mork.20041103155347.1:setBufferGetter
    def setBufferListGetter( self, buffer, method ):
        #Sets a method that returns a buffer name and its text, and its insert position.
        self.bufferListGetters[ buffer ] = method
    #@-node:mork.20041103155347.1:setBufferGetter
    #@+node:mork.20041103155347.2:setBufferSetter
    def setBufferSetter( self, buffer, method ):
        #Sets a method that takes a buffer name and the new contents.
        self.bufferSetters[ buffer ] = method
    #@nonl
    #@-node:mork.20041103155347.2:setBufferSetter
    #@+node:mork.20041103155347.3:getBufferDict
    def getBufferDict( self, event ):
        
        tbuffer = event.widget
        meth = self.bufferListGetters[ tbuffer ]
        return meth()
    #@nonl
    #@-node:mork.20041103155347.3:getBufferDict
    #@+node:mork.20041103162147:setBufferData
    def setBufferData( self, event, name, data ):
        
        tbuffer = event.widget
        meth = self.bufferSetters[ tbuffer ]
        meth( name, data )
    #@nonl
    #@-node:mork.20041103162147:setBufferData
    #@+node:mork.20041103191311:setBufferGoto
    def setBufferGoto( self, tbuffer, method ):
        self.bufferGotos[ tbuffer ] = method 
    #@nonl
    #@-node:mork.20041103191311:setBufferGoto
    #@+node:mork.20041104090224:setBufferDelete
    def setBufferDelete( self, tbuffer, method ):
        
        self.bufferDeletes[ tbuffer ] = method
        
    
    #@-node:mork.20041104090224:setBufferDelete
    #@+node:mork.20041104092349:setBufferRename
    def setBufferRename( self, buffer, method ):
        
        self.renameBuffers[ buffer ] = method
    #@nonl
    #@-node:mork.20041104092349:setBufferRename
    #@-others
    #@nonl
    #@-node:mork.20041104094826:configure buffer methods
    #@+node:mork.20041104094826.1:buffer operations
    #@+others
    #@+node:mork.20041103155347.4:appendToBuffer
    def appendToBuffer( self, event, name ):
    
        tbuffer = event.widget
        try:
            txt = tbuffer.get( 'sel.first', 'sel.last' )
            bdata = self.bufferDict[ name ]
            bdata = '%s%s' % ( bdata, txt )
            self.setBufferData( event, name, bdata )
        except Exception, x:
            pass
        return self.keyboardQuit( event )
    #@nonl
    #@-node:mork.20041103155347.4:appendToBuffer
    #@+node:mork.20041103155347.5:prependToBuffer
    def prependToBuffer( self, event, name ):
        
        tbuffer = event.widget
        try:
            txt = tbuffer.get( 'sel.first', 'sel.last' )
            bdata = self.bufferDict[ name ]
            bdata = '%s%s' % ( txt, bdata )
            self.setBufferData( event, name, bdata )
        except Exception, x:
            pass
        return self.keyboardQuit( event )
    #@nonl
    #@-node:mork.20041103155347.5:prependToBuffer
    #@+node:mork.20041103155347.6:insertToBuffer
    def insertToBuffer( self, event, name ):
    
        tbuffer = event.widget
        bdata = self.bufferDict[ name ]
        tbuffer.insert( 'insert', bdata )
        self._tailEnd( tbuffer )
        return self.keyboardQuit( event )
    #@-node:mork.20041103155347.6:insertToBuffer
    #@+node:mork.20041103190332:listBuffers
    def listBuffers( self, event ):
        
        bdict  = self.getBufferDict( event )
        list = bdict.keys()
        list.sort()
        svar, label = self.getSvarLabel( event )
        data = '\n'.join( list )
        self.keyboardQuit( event )
        svar.set( data )
        return 'break'
        
    #@nonl
    #@-node:mork.20041103190332:listBuffers
    #@+node:mork.20041103155347.7:copyToBuffer
    def copyToBuffer( self, event, name ):
        
        tbuffer = event.widget
        try:
            txt = tbuffer.get( 'sel.first', 'sel.last' )
            self.setBufferData( event, name, txt )
        except Exception, x:
            pass
        return self.keyboardQuit( event )
        
    #@-node:mork.20041103155347.7:copyToBuffer
    #@+node:mork.20041103191311.1:switchToBuffer
    def switchToBuffer( self, event, name ):
        
        method = self.bufferGotos[ event.widget ]
        self.keyboardQuit( event )
        method( name )
        return 'break'
    #@-node:mork.20041103191311.1:switchToBuffer
    #@+node:mork.20041104090224.1:killBuffer
    def killBuffer( self, event, name ):
        
        method = self.bufferDeletes[ event.widget ]
        self.keyboardQuit( event )
        method( name )
        return 'break'
        
    
    #@-node:mork.20041104090224.1:killBuffer
    #@+node:mork.20041104092058:renameBuffer
    def renameBuffer( self, event ):
        
        svar, label = self.getSvarLabel( event )
        if not self.mcStateManager.getState( 'renameBuffer' ):
            self.mcStateManager.setState( 'renameBuffer', True )
            svar.set( '' )
            label.configure( background = 'lightblue' )
            return 'break'
        if event.keysym == 'Return':
           
           nname = svar.get()
           self.keyboardQuit( event )
           self.renameBuffers[ event.widget ]( nname )
            
            
        else:
            self.setSvar( event, svar )
            return 'break'
    #@nonl
    #@-node:mork.20041104092058:renameBuffer
    #@+node:mork.20041103161202:chooseBuffer
    def chooseBuffer( self, event ):
        
        svar, label = self.getSvarLabel( event )
    
        state = self.mcStateManager.getState( 'chooseBuffer' )
        if state.startswith( 'start' ):
            state = state[ 5: ]
            self.mcStateManager.setState( 'chooseBuffer', state )
            svar.set( '' )
        if event.keysym == 'Tab':
            
            stext = svar.get().strip()
            if self.bufferTracker.prefix and stext.startswith( self.bufferTracker.prefix ):
                svar.set( self.bufferTracker.next() ) #get next in iteration
            else:
                prefix = svar.get()
                pmatches = []
                for z in self.bufferDict.keys():
                    if z.startswith( prefix ):
                        pmatches.append( z )
                self.bufferTracker.setTabList( prefix, pmatches )
                svar.set( self.bufferTracker.next() ) #begin iteration on new lsit
            return 'break'        
    
            
        elif event.keysym == 'Return':
           
           bMode = self.mcStateManager.getState( 'chooseBuffer' )
           return self.bufferCommands[ bMode ]( event, svar.get() )
            
            
        else:
            self.setSvar( event, svar )
            return 'break'
    
    #@-node:mork.20041103161202:chooseBuffer
    #@+node:mork.20041103161202.1:setInBufferMode
    def setInBufferMode( self, event, which ):
        
        self.keyboardQuit( event )
        tbuffer = event.widget
        self.mcStateManager.setState( 'chooseBuffer', 'start%s' % which )
        svar, label = self.getSvarLabel( event )
        label.configure( background = 'lightblue' )
        svar.set( 'Choose Buffer Name:' )
        self.bufferDict = self.getBufferDict( event )
        return 'break'
    #@nonl
    #@-node:mork.20041103161202.1:setInBufferMode
    #@-others
    #@nonl
    #@-node:mork.20041104094826.1:buffer operations
    #@-others
    #@nonl
    #@-node:mork.20041103155347:buffer recognition and alterers
    #@-others
    #@nonl
    #@-node:mork.20041031194746:configurable methods
    #@+node:mork.20041031155753:macro methods
    #@+at
    # general macro methods.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041030164547.8:startKBDMacro
    #self.lastMacro = None
    #self.macs = []
    #self.macro = []
    #self.namedMacros = {}
    #self.macroing = False
    def startKBDMacro( self, event ):
    
        svar, label = self.getSvarLabel( event )
        svar.set( 'Recording Keyboard Macro' )
        label.configure( background = 'lightblue' )
        self.macroing = True
        return 'break'
    #@-node:mork.20041030164547.8:startKBDMacro
    #@+node:mork.20041030164547.9:recordKBDMacro
    def recordKBDMacro( self, event, stroke ):
        if stroke != '<Key>':
            self.macro.append( (stroke, event.keycode, event.keysym, event.char) )
        elif stroke == '<Key>':
            if event.keysym != '??':
                self.macro.append( ( event.keycode, event.keysym ) )
        return
    #@-node:mork.20041030164547.9:recordKBDMacro
    #@+node:mork.20041030164547.10:stopKBDMacro
    def stopKBDMacro( self, event ):
        #global macro, lastMacro, macroing
        if self.macro:
            self.macro = self.macro[ : -4 ]
            self.macs.insert( 0, self.macro )
            self.lastMacro = self.macro
            self.macro = []
    
        self.macroing = False
        svar, label = self.getSvarLabel( event )
        svar.set( 'Keyboard macro defined' )
        label.configure( background = 'lightgrey' )
        return 'break' 
    #@-node:mork.20041030164547.10:stopKBDMacro
    #@+node:mork.20041030164547.11:_executeMacro
    def _executeMacro( self, macro, tbuffer ):
        
        for z in macro:
            if len( z ) == 2:
                tbuffer.event_generate( '<Key>', keycode = z[ 0 ], keysym = z[ 1 ] ) 
            else:
                meth = z[ 0 ].lstrip( '<' ).rstrip( '>' )
                method = self.cbDict[ meth ]
                ev = Tkinter.Event()
                ev.widget = tbuffer
                ev.keycode = z[ 1 ]
                ev.keysym = z[ 2 ]
                ev.char = z[ 3 ]
                self.masterCommand( ev , method, '<%s>' % meth )
        return self._tailEnd( tbuffer )  
    
    #@-node:mork.20041030164547.11:_executeMacro
    #@+node:mork.20041030164547.12:executeLastMacro
    def executeLastMacro( self, event ):
        tbuffer = event.widget
        if self.lastMacro:
            return self._executeMacro( self.lastMacro, tbuffer )
        return 'break'
    #@-node:mork.20041030164547.12:executeLastMacro
    #@+node:mork.20041030164547.13:nameLastMacro
    def nameLastMacro( self, event ):
        '''Names the last macro defined.'''
        #global macroing
        svar, label = self.getSvarLabel( event )    
        if not self.macroing :
            self.macroing = 2
            svar.set( '' )
            self.setLabelBlue( label )
            return 'break'
        if event.keysym == 'Return':
            name = svar.get()
            self._addToDoAltX( name, self.lastMacro )
            svar.set( '' )
            self.setLabelBlue( label )
            self.macroing = False
            self.stopControlX( event )
            return 'break'
        self.setSvar( event, svar )
        return 'break'
    #@-node:mork.20041030164547.13:nameLastMacro
    #@+node:mork.20041030164547.14:_addToDoAltX
    def _addToDoAltX( self, name, macro ):
        '''Adds macro to Alt-X commands.'''
        if not self.doAltX.has_key( name ):
            def exe( event, macro = macro ):
                self.stopControlX( event )
                return self._executeMacro( macro, event.widget )
            self.doAltX[ name ] = exe
            self.namedMacros[ name ] = macro
            return True
        else:
            return False
    #@-node:mork.20041030164547.14:_addToDoAltX
    #@+node:mork.20041030164547.15:loadMacros
    def loadMacros( self,event ):
        '''Asks for a macro file name to load.'''
        import tkFileDialog
        f = tkFileDialog.askopenfile()
        if f == None: return 'break'
        else:
            return self._loadMacros( f )       
    #@-node:mork.20041030164547.15:loadMacros
    #@+node:mork.20041030164547.16:_loadMacros
    def _loadMacros( self, f ):
        '''Loads a macro file into the macros dictionary.'''
        import cPickle
        macros = cPickle.load( f )
        for z in macros:
            self._addToDoAltX( z, macros[ z ] )
        return 'break'
    #@-node:mork.20041030164547.16:_loadMacros
    #@+node:mork.20041030164547.17:getMacroName
    def getMacroName( self, event ):
        '''A method to save your macros to file.'''
        #global macroing
        svar, label = self.getSvarLabel( event )
        if not self.macroing:
            self.macroing = 3
            svar.set('')
            self.setLabelBlue( label )
            return 'break'
        if event.keysym == 'Return':
            self.macroing = False
            self.saveMacros( event, svar.get() )
            return 'break'
        if event.keysym == 'Tab':
            svar.set( self._findMatch( svar, self.namedMacros ) )
            return 'break'        
        self.setSvar( event, svar )
        return 'break'    
    #@-node:mork.20041030164547.17:getMacroName
    #@+node:mork.20041030164547.18:saveMacros
    def saveMacros( self, event, macname ):
        '''Asks for a file name and saves it.'''
        import tkFileDialog
        name = tkFileDialog.asksaveasfilename()
        if name:
            f = file( name, 'a+' )
            f.seek( 0 )
            if f:
                self._saveMacros( f, macname ) 
        return 'break'
    #@-node:mork.20041030164547.18:saveMacros
    #@+node:mork.20041030164547.19:_saveMacros
    def _saveMacros( self, f , name ):
        '''Saves the macros as a pickled dictionary'''
        import cPickle
        fname = f.name
        try:
            macs = cPickle.load( f )
        except:
            macs = {}
        f.close()
        if self.namedMacros.has_key( name ):
            macs[ name ] = self.namedMacros[ name ]
            f = file( fname, 'w' )
            cPickle.dump( macs, f )
            f.close()   
    #@-node:mork.20041030164547.19:_saveMacros
    #@-others
    #@nonl
    #@-node:mork.20041031155753:macro methods
    #@+node:mork.20041031194703:comment column methods
    #@+others
    #@+node:mork.20041030164547.20:setCommentColumn
    #self.ccolumn = '0'
    def setCommentColumn( self, event ):
        #global ccolumn
        cc= event.widget.index( 'insert' )
        cc1, cc2 = cc.split( '.' )
        self.ccolumn = cc2
        return 'break'
    #@-node:mork.20041030164547.20:setCommentColumn
    #@+node:mork.20041030164547.21:indentToCommentColumn
    def indentToCommentColumn( self, event ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert lineend' )
        i1, i2 = i.split( '.' )
        i2 = int( i2 )
        c1 = int( self.ccolumn )
        if i2 < c1:
            wsn = c1 - i2
            tbuffer.insert( 'insert lineend', ' '* wsn )
        if i2 >= c1:
            tbuffer.insert( 'insert lineend', ' ')
        tbuffer.mark_set( 'insert', 'insert lineend' )
        return self._tailEnd( tbuffer ) 
    #@-node:mork.20041030164547.21:indentToCommentColumn
    #@-others
    #@nonl
    #@-node:mork.20041031194703:comment column methods
    #@+node:mork.20041031182709:how many methods
    #@+others
    #@+node:mork.20041030164547.23:howMany
    #self.howM = False
    def howMany( self, event ):
        #global howM
        svar, label = self.getSvarLabel( event )
        if event.keysym == 'Return':
            tbuffer = event.widget
            txt = tbuffer.get( '1.0', 'end' )
            import re
            reg1 = svar.get()
            reg = re.compile( reg1 )
            i = reg.findall( txt )
            svar.set( '%s occurances found of %s' % (len(i), reg1 ) )
            self.setLabelGrey( label )
            #self.howM = False
            self.mcStateManager.setState( 'howM', False )
            return 'break'
        self.setSvar( event, svar )
        return 'break'
    #@-node:mork.20041030164547.23:howMany
    #@+node:mork.20041030164547.24:startHowMany
    def startHowMany( self, event ):
        #global howM
        #self.howM = True
        self.mcStateManager.setState( 'howM', True )
        svar, label = self.getSvarLabel( event )
        svar.set( '' )
        self.setLabelBlue( label )
        return 'break'
    #@-node:mork.20041030164547.24:startHowMany
    #@-others
    #@nonl
    #@-node:mork.20041031182709:how many methods
    #@+node:mork.20041031155913:paragraph methods
    #@+others
    #@+node:mork.20041030164547.25:selectParagraph
    def selectParagraph( self, event ):
        tbuffer = event.widget
        txt = tbuffer.get( 'insert linestart', 'insert lineend' )
        txt = txt.lstrip().rstrip()
        i = tbuffer.index( 'insert' )
        if not txt:
            while 1:
                i = tbuffer.index( '%s + 1 lines' % i )
                txt = tbuffer.get( '%s linestart' % i, '%s lineend' % i )
                txt = txt.lstrip().rstrip()
                if txt:
                    self._selectParagraph( tbuffer, i )
                    break
                if tbuffer.index( '%s lineend' % i ) == tbuffer.index( 'end' ):
                    return 'break'
        if txt:
            while 1:
                i = tbuffer.index( '%s - 1 lines' % i )
                txt = tbuffer.get( '%s linestart' % i, '%s lineend' % i )
                txt = txt.lstrip().rstrip()
                if not txt or tbuffer.index( '%s linestart' % i ) == tbuffer.index( '1.0' ):
                    if not txt:
                        i = tbuffer.index( '%s + 1 lines' % i )
                    self._selectParagraph( tbuffer, i )
                    break     
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.25:selectParagraph
    #@+node:mork.20041030164547.26:_selectParagraph
    def _selectParagraph( self, tbuffer, start ):
        i2 = start
        while 1:
            txt = tbuffer.get( '%s linestart' % i2, '%s lineend' % i2 )
            if tbuffer.index( '%s lineend' % i2 )  == tbuffer.index( 'end' ):
                break
            txt = txt.lstrip().rstrip()
            if not txt: break
            else:
                i2 = tbuffer.index( '%s + 1 lines' % i2 )
        tbuffer.tag_add( 'sel', '%s linestart' % start, '%s lineend' % i2 )
        tbuffer.mark_set( 'insert', '%s lineend' % i2 )
    #@-node:mork.20041030164547.26:_selectParagraph
    #@+node:mork.20041030164547.27:killParagraph
    def killParagraph( self, event ):   
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        txt = tbuffer.get( 'insert linestart', 'insert lineend' )
        if not txt.rstrip().lstrip():
            i = tbuffer.search( r'\w', i, regexp = True, stopindex = 'end' )
        self._selectParagraph( tbuffer, i )
        i2 = tbuffer.index( 'insert' )
        self.kill( event, i, i2 )
        tbuffer.mark_set( 'insert', i )
        tbuffer.selection_clear()
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.27:killParagraph
    #@+node:mork.20041030164547.28:backwardKillParagraph
    def backwardKillParagraph( self, event ):   
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        i2 = i
        txt = tbuffer.get( 'insert linestart', 'insert lineend' )
        if not txt.rstrip().lstrip():
            self.movingParagraphs( event, -1 )
            i2 = tbuffer.index( 'insert' )
        self.selectParagraph( event )
        i3 = tbuffer.index( 'sel.first' )
        self.kill( event, i3, i2 )
        tbuffer.mark_set( 'insert', i )
        tbuffer.selection_clear()
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.28:backwardKillParagraph
    #@-others
    #@nonl
    #@-node:mork.20041031155913:paragraph methods
    #@+node:mork.20041031181929:kill methods
    #@+at
    # These methods add text to the killbuffer.
    #@-at
    #@@c
    
    #@+others
    #@+node:mork.20041030164547.34:kill
    def kill( self, event, frm, to  ):
        tbuffer = event.widget
        text = tbuffer.get( frm, to )
        self.addToKillBuffer( text )
        tbuffer.clipboard_clear()
        tbuffer.clipboard_append( text )    
        if frm == 'insert' and to =='insert lineend' and tbuffer.index( frm ) == tbuffer.index( to ):
            tbuffer.delete( 'insert', 'insert lineend +1c' )
            self.addToKillBuffer( '\n' )
        else:
            tbuffer.delete( frm, to )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.34:kill
    #@+node:mork.20041030164547.36:walkKB
    def walkKB( self, event, frm, which ):# kb = self.iterateKillBuffer() ):
            #if not kb1:
            #    kb1.append( self.iterateKillBuffer() )
            #kb = kb1[ 0 ]
            #global reset
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        t , t1 = i.split( '.' )
        clip_text = self.getClipboard( tbuffer )    
        if self.killbuffer or clip_text:
            if which == 'c':
                self.reset = True
                if clip_text:
                    txt = clip_text
                else:
                    txt = self.kbiterator.next()
                tbuffer.tag_delete( 'kb' )
                tbuffer.insert( frm, txt, ('kb') )
                tbuffer.mark_set( 'insert', i )
            else:
                if clip_text:
                    txt = clip_text
                else:
                    txt = self.kbiterator.next()
                t1 = str( int( t1 ) + len( txt ) )
                r = tbuffer.tag_ranges( 'kb' )
                if r and r[ 0 ] == i:
                    tbuffer.delete( r[ 0 ], r[ -1 ] )
                tbuffer.tag_delete( 'kb' )
                tbuffer.insert( frm, txt, ('kb') )
                tbuffer.mark_set( 'insert', i )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.36:walkKB
    #@+node:mork.20041030164547.35:deletelastWord
    def deletelastWord( self, event ):
        #tbuffer = event.widget
        #i = tbuffer.get( 'insert' )
        self.moveword( event, -1 )
        self.kill( event, 'insert', 'insert wordend')
        self.moveword( event ,1 )
        return 'break'
    #@-node:mork.20041030164547.35:deletelastWord
    #@+node:mork.20041030164547.37:killsentence
    def killsentence( self, event, back = False ):
        tbuffer = event.widget
        i = tbuffer.search( '.' , 'insert', stopindex = 'end' )
        if back:
            i = tbuffer.search( '.' , 'insert', backwards = True, stopindex = '1.0' ) 
            if i == '':
                return 'break'
            i2 = tbuffer.search( '.' , i, backwards = True , stopindex = '1.0' )
            if i2 == '':
                i2 = '1.0'
            return self.kill( event, i2, '%s + 1c' % i )
            #return self.kill( event , '%s +1c' % i, 'insert' )
        else:
            i = tbuffer.search( '.' , 'insert', stopindex = 'end' )
            i2 = tbuffer.search( '.', 'insert', backwards = True, stopindex = '1.0' )
        if i2 == '':
           i2 = '1.0'
        else:
           i2 = i2 + ' + 1c '
        if i == '': return 'break'
        return self.kill( event, i2, '%s + 1c' % i )
    #@-node:mork.20041030164547.37:killsentence
    #@+node:mork.20041030164547.91:killRegion
    def killRegion( self, event, which ):
        mrk = 'sel'
        tbuffer = event.widget
        trange = tbuffer.tag_ranges( mrk )
        if len( trange ) != 0:
            txt = tbuffer.get( trange[ 0 ] , trange[ -1 ] )
            if which == 'd':
                tbuffer.delete( trange[ 0 ], trange[ -1 ] )   
            self.addToKillBuffer( txt )
            tbuffer.clipboard_clear()
            tbuffer.clipboard_append( txt )
        self.removeRKeys( tbuffer )
        return 'break'
    #@-node:mork.20041030164547.91:killRegion
    #@+node:mork.20041030164547.42:addToKillBuffer
    #self.killbuffer = []
    def addToKillBuffer( self, text ):
        #global reset
        self.reset = True 
        if self.previousStroke in ( '<Control-k>', '<Control-w>' ,
         '<Alt-d>', '<Alt-Delete', '<Alt-z>', '<Delete>',
         '<Control-Alt-w>' ) and len( self.killbuffer):
            self.killbuffer[ 0 ] = self.killbuffer[ 0 ] + text
            return
        self.killbuffer.insert( 0, text )
    #@-node:mork.20041030164547.42:addToKillBuffer
    #@+node:mork.20041030164547.29:iterateKillBuffer
    #self.reset = False
    def iterateKillBuffer( self ):
        #global reset
        while 1:
            if self.killbuffer:
                self.last_clipboard = None
                for z in self.killbuffer:
                    if self.reset:
                        self.reset = False
                        break        
                    yield z
            
                
    #@-node:mork.20041030164547.29:iterateKillBuffer
    #@+node:mork.20041103120919:getClipboard
    def getClipboard( self, tbuffer ):
        
        ctxt = None
        try:
            ctxt = tbuffer.selection_get( selection='CLIPBOARD' )
            if ctxt != self.last_clipboard or not self.killbuffer:
                self.last_clipboard = ctxt
                if self.killbuffer and self.killbuffer[ 0 ] == ctxt:
                    return None
                return ctxt
            else:
                return None
            
        except:
            return None
            
        return None
    #@nonl
    #@-node:mork.20041103120919:getClipboard
    #@-others
    #@nonl
    #@-node:mork.20041031181929:kill methods
    #@+node:mork.20041031155642:register methods
    #@+at
    # These methods add things to the registers( a-z )
    # 
    #@-at
    #@@c
    
    #@+others
    #@+node:mork.20041030164547.44:copyToRegister
    #self.registers = {}
    
    def copyToRegister( self, event ):
    
        if not self._chckSel( event ):
            return
        if event.keysym in string.letters:
            event.keysym = event.keysym.lower()
            tbuffer = event.widget
            txt = tbuffer.get( 'sel.first', 'sel.last' )
            self.registers[ event.keysym ] = txt
            return 
        self.stopControlX( event )
    #@-node:mork.20041030164547.44:copyToRegister
    #@+node:mork.20041030164547.45:copyRectangleToRegister
    def copyRectangleToRegister( self, event ):
        if not self._chckSel( event ):
            return
        if event.keysym in string.letters:
            event.keysym = event.keysym.lower()
            tbuffer = event.widget
            r1, r2, r3, r4 = self.getRectanglePoints( event )
            rect = []
            while r1 <= r3:
                txt = tbuffer.get( '%s.%s' %( r1, r2 ), '%s.%s' %( r1, r4 ) )
                rect.append( txt )
                r1 = r1 +1
            self.registers[ event.keysym ] = rect
        self.stopControlX( event )        
    #@-node:mork.20041030164547.45:copyRectangleToRegister
    #@+node:mork.20041030164547.46:prependToRegister
    def prependToRegister( self, event ):
        #global regMeth, registermode, controlx, registermode
        event.keysym = 'p'
        self.setNextRegister( event )
        self.mcStateManager.setState( 'controlx', False )
        #self.controlx = True
    #@-node:mork.20041030164547.46:prependToRegister
    #@+node:mork.20041030164547.47:appendToRegister
    def appendToRegister( self, event ):
        #global regMeth, registermode, controlx
        event.keysym = 'a'
        self.setNextRegister( event )
        self.mcStateManager.setState( 'controlx', True )
        #self.controlx = True
    #@-node:mork.20041030164547.47:appendToRegister
    #@+node:mork.20041030164547.49:_ToReg
    def _ToReg( self, event , which):
        if not self._chckSel( event ):
            return
        if self._checkIfRectangle( event ):
            return
        if event.keysym in string.letters:
            event.keysym = event.keysym.lower()
            tbuffer = event.widget
            if not self.registers.has_key( event.keysym ):
                self.registers[ event.keysym ] = ''
            txt = tbuffer.get( 'sel.first', 'sel.last' )
            rtxt = self.registers[ event.keysym ]
            if self.which == 'p':
                txt = txt + rtxt
            else:
                txt = rtxt + txt
            self.registers[ event.keysym ] = txt
            return
    #@-node:mork.20041030164547.49:_ToReg
    #@+node:mork.20041030164547.48:_chckSel
    def _chckSel( self, event ):
         if not 'sel' in event.widget.tag_names():
            return False
         if not event.widget.tag_ranges( 'sel' ):
            return False  
         return True
    #@-node:mork.20041030164547.48:_chckSel
    #@+node:mork.20041030164547.50:_checkIfRectangle
    def _checkIfRectangle( self, event ):
        if self.registers.has_key( event.keysym ):
            if isinstance( self.registers[ event.keysym ], list ):
                svar, label = self.getSvarLabel( event )
                self.stopControlX( event )
                svar.set( "Register contains Rectangle, not text" )
                return True
        return False           
    #@-node:mork.20041030164547.50:_checkIfRectangle
    #@+node:mork.20041030164547.51:insertFromRegister
    def insertFromRegister( self, event ):
        tbuffer = event.widget
        if self.registers.has_key( event.keysym ):
            if isinstance( self.registers[ event.keysym ], list ):
                self.yankRectangle( event, self.registers[ event.keysym ] )
            else:
                tbuffer.insert( 'insert', self.registers[ event.keysym ] )
                tbuffer.event_generate( '<Key>' )
                tbuffer.update_idletasks()
        self.stopControlX( event )
    #@-node:mork.20041030164547.51:insertFromRegister
    #@+node:mork.20041030164547.52:incrementRegister
    def incrementRegister( self, event ):
        if self.registers.has_key( event.keysym ):
            if self._checkIfRectangle( event ):
                return
            if self.registers[ event.keysym ] in string.digits:
                i = self.registers[ event.keysym ]
                i = str( int( i ) + 1 )
                self.registers[ event.keysym ] = i
            else:
                self.invalidRegister( event, 'number' )
                return
        self.stopControlX( event )
    #@-node:mork.20041030164547.52:incrementRegister
    #@+node:mork.20041030164547.53:numberToRegister
    def numberToRegister( self, event ):
        if event.keysym in string.letters:
            self.registers[ event.keysym.lower() ] = str( 0 )
        self.stopControlX( event )
    #@-node:mork.20041030164547.53:numberToRegister
    #@+node:mork.20041030164547.54:pointToRegister
    def pointToRegister( self, event ):
        if event.keysym in string.letters:
            tbuffer = event.widget
            self.registers[ event.keysym.lower() ] = tbuffer.index( 'insert' )
        self.stopControlX( event )
    #@-node:mork.20041030164547.54:pointToRegister
    #@+node:mork.20041030164547.55:jumpToRegister
    def jumpToRegister( self, event ):
        if event.keysym in string.letters:
            if self._checkIfRectangle( event ):
                return
            tbuffer = event.widget
            i = self.registers[ event.keysym.lower() ]
            i2 = i.split( '.' )
            if len( i2 ) == 2:
                if i2[ 0 ].isdigit() and i2[ 1 ].isdigit():
                    pass
                else:
                    self.invalidRegister( event, 'index' )
                    return
            else:
                self.invalidRegister( event, 'index' )
                return
            tbuffer.mark_set( 'insert', i )
            tbuffer.event_generate( '<Key>' )
            tbuffer.update_idletasks() 
        self.stopControlX( event ) 
    #@-node:mork.20041030164547.55:jumpToRegister
    #@+node:mork.20041030164547.56:invalidRegister
    def invalidRegister( self, event, what ):
        self.deactivateRegister( event )
        svar, label = self.getSvarLabel( event )
        svar.set( 'Register does not contain valid %s'  % what)
        return    
    #@-node:mork.20041030164547.56:invalidRegister
    #@+node:mork.20041030164547.57:setNextRegister
    def setNextRegister( self, event ):
        #global regMeth, registermode
        if event.keysym == 'Shift':
            return
        if self.regMeths.has_key( event.keysym ):
            self.mcStateManager.setState( 'controlx', True )
            self.regMeth = self.regMeths[ event.keysym ]
            self.registermode = 2
            svar = self.svars[ event.widget ]
            svar.set( self.regText[ event.keysym ] )
            return
        self.stopControlX( event )
    #@-node:mork.20041030164547.57:setNextRegister
    #@+node:mork.20041030164547.58:executeRegister
    def executeRegister( self, event ):
        self.regMeth( event )
        if self.registermode: 
            self.stopControlX( event )
        return
    #@-node:mork.20041030164547.58:executeRegister
    #@+node:mork.20041030164547.59:deactivateRegister
    def deactivateRegister( self, event ):
        #global registermode, regMeth
        svar, label = self.getSvarLabel( event )
        svar.set( '' )
        self.setLabelGrey( label )
        self.registermode = False
        self.regMeth = None
    #@-node:mork.20041030164547.59:deactivateRegister
    #@+node:mork.20041102151545:viewRegister
    def viewRegister( self, event ):
        
        self.stopControlX( event )
        if event.keysym in string.letters:
            text = self.registers[ event.keysym.lower() ]
            svar, label = self.getSvarLabel( event )
            svar.set( text )
    #@nonl
    #@-node:mork.20041102151545:viewRegister
    #@-others
    #@nonl
    #@-node:mork.20041031155642:register methods
    #@+node:mork.20041031181701:abbreviation methods
    #@+at
    # 
    # type some text, set its abbreviation with Control-x a i g, type the text 
    # for abbreviation expansion
    # type Control-x a e ( or Alt-x expand-abbrev ) to expand abbreviation
    # type Alt-x abbrev-on to turn on automatic abbreviation expansion
    # Alt-x abbrev-on to turn it off
    # 
    # an example:
    # type:
    # frogs
    # after typing 's' type Control-x a i g.  This will turn the minibuffer 
    # blue, type in your definition. For example: turtles.
    # 
    # Now in the buffer type:
    # frogs
    # after typing 's' type Control-x a e.  This will turn the 'frogs' into:
    # turtles
    # 
    # 
    # 
    #@-at
    #@@c
    
    #@+others
    #@+node:mork.20041030164547.60:abbreviationDispatch
    #self.abbrevMode = False
    #self.abbrevOn = False
    #self.abbrevs = {}
    def abbreviationDispatch( self, event, which ):
        #global abbrevMode
        #if not self.abbrevMode:
        aM = self.mcStateManager.getState( 'abbrevMode' )
        if not aM:
            #self.abbrevMode = which
            self.mcStateManager.setState( 'abbrevMode', which )
            svar, label = self.getSvarLabel( event )
            svar.set( '' )
            self.setLabelBlue( label )
            return 'break'
        if aM:
            self.abbrevCommand1( event )
        return 'break'
    #@-node:mork.20041030164547.60:abbreviationDispatch
    #@+node:mork.20041030164547.61:abbrevCommand1
    def abbrevCommand1( self, event ):
        #global abbrevMode
        if event.keysym == 'Return':
            tbuffer = event.widget
            word = tbuffer.get( 'insert -1c wordstart', 'insert -1c wordend' )
            if word == ' ': return
            svar, label = self.getSvarLabel( event )
            aM = self.mcStateManager.getState( 'abbrevMode' )
            if aM == 1:
                self.abbrevs[ svar.get() ] = word
            elif aM == 2:
                self.abbrevs[ word ] = svar.get()
            #self.abbrevMode = False
            #self.mcStateManager.setState( 'abbrevMode', False )
            self.keyboardQuit( event )
            self.resetMiniBuffer( event )
            return 'break'
        svar, label = self.getSvarLabel( event )
        self.setSvar( event, svar )
        return 'break'
    #@-node:mork.20041030164547.61:abbrevCommand1
    #@+node:mork.20041030164547.62:expandAbbrev
    def expandAbbrev( self,event ):
        tbuffer = event.widget
        word = tbuffer.get( 'insert -1c wordstart', 'insert -1c wordend' )
        c = event.char.strip()
        if c: #We have to do this because this method is called from Alt-x and Control-x, we get two differnt types of data and tbuffer states.
            word = '%s%s' %( word, event.char )
        if self.abbrevs.has_key( word ):
            tbuffer.delete( 'insert -1c wordstart', 'insert -1c wordend' )
            tbuffer.insert( 'insert', self.abbrevs[ word ] ) 
            return self._tailEnd( tbuffer )
            #return True
        else: return False
    #@-node:mork.20041030164547.62:expandAbbrev
    #@+node:mork.20041030164547.63:regionalExpandAbbrev
    #self.regXRpl = None
    #self.regXKey = None
    def regionalExpandAbbrev( self, event ):
        #global regXRpl
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        i1 = tbuffer.index( 'sel.first' )
        i2 = tbuffer.index( 'sel.last' ) 
        ins = tbuffer.index( 'insert' )
        #@    << define a new generator searchXR >>
        #@+node:ekr.20050527111832:<< define a new generator searchXR >>
        # EKR: This is a generator (it contains a yield).
        # EKR: To make this work we must define a new generator for each call to regionalExpandAbbrev.
        def searchXR( i1 , i2, ins, event ):
            tbuffer.tag_add( 'sXR', i1, i2 )
            while i1:
                tr = tbuffer.tag_ranges( 'sXR' )
                if not tr: break
                i1 = tbuffer.search( r'\w', i1, stopindex = tr[ 1 ] , regexp = True )
                if i1:
                    word = tbuffer.get( '%s wordstart' % i1, '%s wordend' % i1 )
                    tbuffer.tag_delete( 'found' )
                    tbuffer.tag_add( 'found',  '%s wordstart' % i1, '%s wordend' % i1 )
                    tbuffer.tag_config( 'found', background = 'yellow' )
                    if self.abbrevs.has_key( word ):
                        svar, label = self.getSvarLabel( event )
                        svar.set( 'Replace %s with %s? y/n' % ( word, self.abbrevs[ word ] ) )
                        yield None
                        if self.regXKey == 'y':
                            ind = tbuffer.index( '%s wordstart' % i1 )
                            tbuffer.delete( '%s wordstart' % i1, '%s wordend' % i1 )
                            tbuffer.insert( ind, self.abbrevs[ word ] )
                    i1 = '%s wordend' % i1
            tbuffer.mark_set( 'insert', ins )
            tbuffer.selection_clear()
            tbuffer.tag_delete( 'sXR' )
            tbuffer.tag_delete( 'found' )
            svar, label = self.getSvarLabel( event )
            svar.set( '' )
            self.setLabelGrey( label )
            self._setRAvars()
        #@nonl
        #@-node:ekr.20050527111832:<< define a new generator searchXR >>
        #@nl
        # EKR: the 'result' of calling searchXR is a generator object.
        self.regXRpl = searchXR( i1, i2, ins, event)
        self.regXRpl.next() # Call it the first time.
        return 'break' 
    #@nonl
    #@-node:mork.20041030164547.63:regionalExpandAbbrev
    #@+node:mork.20041030164547.64:_setRAvars
    def _setRAvars( self ):
        #global regXRpl, regXKey
        self.regXRpl = self.regXKey = None 
    #@-node:mork.20041030164547.64:_setRAvars
    #@+node:mork.20041030164547.65:killAllAbbrevs
    def killAllAbbrevs( self, event ):
        #global abbrevs
        self.abbrevs = {}
        return self.keyboardQuit( event )
    #@-node:mork.20041030164547.65:killAllAbbrevs
    #@+node:mork.20041030164547.66:toggleAbbrevMode
    def toggleAbbrevMode( self, event ):
        #global abbrevOn
        #aO = self.mcStateManager.getState( 'abbrevOn' )
        svar, label = self.getSvarLabel( event )
        if self.abbrevOn:
            self.abbrevOn = False
            self.keyboardQuit( event )
            svar.set( "Abbreviations are Off" )  
            #self.mcStateManager.setState( 'abbrevOn', False ) #This doesnt work too well with the mcStateManager
        else:
            self.abbrevOn = True
            self.keyboardQuit( event )
            svar.set( "Abbreviations are On" )
            #self.mcStateManager.setState( 'abbrevOn', True )
    #@-node:mork.20041030164547.66:toggleAbbrevMode
    #@+node:mork.20041030164547.67:listAbbrevs
    def listAbbrevs( self, event ):
        svar, label = self.getSvarLabel( event )
        txt = ''
        for z in self.abbrevs:
            txt = '%s%s=%s\n' %( txt, z, self.abbrevs[ z ] )
        svar.set( '' )
        svar.set( txt )
        return 'break'
    #@-node:mork.20041030164547.67:listAbbrevs
    #@+node:mork.20041030164547.68:readAbbreviations
    def readAbbreviations( self, event ):
        import tkFileDialog
        f = tkFileDialog.askopenfile()
        if f == None: return 'break'        
        return self._readAbbrevs( f )
    #@-node:mork.20041030164547.68:readAbbreviations
    #@+node:mork.20041030164547.69:_readAbbrevs
    def _readAbbrevs( self, f ):
        for x in f:
            a, b = x.split( '=' )
            b = b[ : -1 ]
            self.abbrevs[ a ] = b
        f.close()        
        return 'break'
    #@-node:mork.20041030164547.69:_readAbbrevs
    #@+node:mork.20041030164547.70:writeAbbreviations
    def writeAbbreviations( self, event ):
        import tkFileDialog
        f = tkFileDialog.asksaveasfile() 
        if f == None: return 'break' 
        return self._writeAbbrevs( f )
    #@-node:mork.20041030164547.70:writeAbbreviations
    #@+node:mork.20041030164547.71:_writeAbbrevs
    def _writeAbbrevs( self, f ):
        for x in self.abbrevs:
            f.write( '%s=%s\n' %( x, self.abbrevs[ x ] ) )
        f.close()    
        return 'break'
    #@-node:mork.20041030164547.71:_writeAbbrevs
    #@-others
    #@nonl
    #@-node:mork.20041031181701:abbreviation methods
    #@+node:mork.20041031182137:paragraph methods
    #@+at
    # 
    # untested as of yet for .5 conversion.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041030164547.72:movingParagraphs
    def movingParagraphs( self, event, way ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        
        if way == 1:
            while 1:
                txt = tbuffer.get( '%s linestart' % i, '%s lineend' %i )
                txt = txt.rstrip().lstrip()
                if not txt:
                    i = tbuffer.search( r'\w', i, regexp = True, stopindex = 'end' )
                    i = '%s' %i
                    break
                else:
                    i = tbuffer.index( '%s + 1 lines' % i )
                    if tbuffer.index( '%s linestart' % i ) == tbuffer.index( 'end' ):
                        i = tbuffer.search( r'\w', 'end', backwards = True, regexp = True, stopindex = '1.0' )
                        i = '%s + 1c' % i
                        break
        else:
            while 1:
                txt = tbuffer.get( '%s linestart' % i, '%s lineend' %i )
                txt = txt.rstrip().lstrip()
                if not txt:
                    i = tbuffer.search( r'\w', i, backwards = True, regexp = True, stopindex = '1.0' )
                    i = '%s +1c' %i
                    break
                else:
                    i = tbuffer.index( '%s - 1 lines' % i )
                    if tbuffer.index( '%s linestart' % i ) == '1.0':
                        i = tbuffer.search( r'\w', '1.0', regexp = True, stopindex = 'end' )
                        break
        if i : 
            tbuffer.mark_set( 'insert', i )
            tbuffer.see( 'insert' )
            return self._tailEnd( tbuffer )
        return 'break'
    #@-node:mork.20041030164547.72:movingParagraphs
    #@+node:mork.20041030164547.74:fillParagraph
    def fillParagraph( self, event ):
        tbuffer = event.widget
        txt = tbuffer.get( 'insert linestart', 'insert lineend' )
        txt = txt.lstrip().rstrip()
        if txt:
            i = tbuffer.index( 'insert' )
            i2 = i
            txt2 = txt
            while txt2:
                pi2 = tbuffer.index( '%s - 1 lines' % i2)
                txt2 = tbuffer.get( '%s linestart' % pi2, '%s lineend' % pi2 )
                if tbuffer.index( '%s linestart' % pi2 ) == '1.0':
                    i2 = tbuffer.search( '\w', '1.0', regexp = True, stopindex = 'end' )
                    break
                if txt2.lstrip().rstrip() == '': break
                i2 = pi2
            i3 = i
            txt3 = txt
            while txt3:
                pi3 = tbuffer.index( '%s + 1 lines' %i3 )
                txt3 = tbuffer.get( '%s linestart' % pi3, '%s lineend' % pi3 )
                if tbuffer.index( '%s lineend' % pi3 ) == tbuffer.index( 'end' ):
                    i3 = tbuffer.search( '\w', 'end', backwards = True, regexp = True, stopindex = '1.0' )
                    break
                if txt3.lstrip().rstrip() == '': break
                i3 = pi3
            ntxt = tbuffer.get( '%s linestart' %i2, '%s lineend' %i3 )
            ntxt = self._addPrefix( ntxt )
            tbuffer.delete( '%s linestart' %i2, '%s lineend' % i3 )
            tbuffer.insert( i2, ntxt )
            tbuffer.mark_set( 'insert', i )
            return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.74:fillParagraph
    #@+node:mork.20041030164547.76:fillRegionAsParagraph
    def fillRegionAsParagraph( self, event ):
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        i1 = tbuffer.index( 'sel.first linestart' )
        i2 = tbuffer.index( 'sel.last lineend' )
        txt = tbuffer.get(  i1,  i2 )
        txt = self._addPrefix( txt )
        tbuffer.delete( i1, i2 )
        tbuffer.insert( i1, txt )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.76:fillRegionAsParagraph
    #@-others
    #@nonl
    #@-node:mork.20041031182137:paragraph methods
    #@+node:mork.20041031182916:fill prefix methods
    #@+others
    #@+node:mork.20041030164547.73:setFillPrefix
    #self.fillPrefix = ''
    def setFillPrefix( self, event ):
        #global fillPrefix
        tbuffer = event.widget
        txt = tbuffer.get( 'insert linestart', 'insert' )
        self.fillPrefix = txt
        return 'break'
    #@-node:mork.20041030164547.73:setFillPrefix
    #@+node:mork.20041030164547.75:_addPrefix
    def _addPrefix( self, ntxt ):
            ntxt = ntxt.split( '.' )
            ntxt = map( lambda a: self.fillPrefix+a, ntxt )
            ntxt = '.'.join( ntxt )               
            return ntxt
    #@-node:mork.20041030164547.75:_addPrefix
    #@-others
    #@nonl
    #@-node:mork.20041031182916:fill prefix methods
    #@+node:mork.20041103085329:fill column and centering
    #@+at
    # These methods are currently just used in tandem to center the line or 
    # region within the fill column.
    # for example, dependent upon the fill column, this text:
    # 
    # cats
    # raaaaaaaaaaaats
    # mats
    # zaaaaaaaaap
    # 
    # may look like
    # 
    #                                  cats
    #                            raaaaaaaaaaaats
    #                                  mats
    #                              zaaaaaaaaap
    # after an center-region command via Alt-x.
    # 
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041103085329.1:centerLine
    def centerLine( self, event ):
        '''Centers line within current fillColumn'''
        
        tbuffer = event.widget
        ind = tbuffer.index( 'insert linestart' )
        txt = tbuffer.get( 'insert linestart', 'insert lineend' )
        txt = txt.strip()
        if len( txt ) >= self.fillColumn: return self._tailEnd( tbuffer )
        amount = ( self.fillColumn - len( txt ) ) / 2
        ws = ' ' * amount
        col, nind = ind.split( '.' )
        ind = tbuffer.search( '\w', 'insert linestart', regexp = True, stopindex = 'insert lineend' )
        if not ind: return 'break'
        tbuffer.delete( 'insert linestart', '%s' % ind )
        tbuffer.insert( 'insert linestart', ws )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041103085329.1:centerLine
    #@+node:mork.20041103095628:centerRegion
    def centerRegion( self, event ):
        '''This method centers the current region within the fill column'''
        tbuffer = event.widget
        start = tbuffer.index( 'sel.first linestart' )
        sindex , x = start.split( '.' )
        sindex = int( sindex )
        end = tbuffer.index( 'sel.last linestart' )
        eindex , x = end.split( '.' )
        eindex = int( eindex )
        while sindex <= eindex:
            txt = tbuffer.get( '%s.0 linestart' % sindex , '%s.0 lineend' % sindex )
            txt = txt.strip()
            if len( txt ) >= self.fillColumn:
                sindex = sindex + 1
                continue
            amount = ( self.fillColumn - len( txt ) ) / 2
            ws = ' ' * amount
            ind = tbuffer.search( '\w', '%s.0' % sindex, regexp = True, stopindex = '%s.0 lineend' % sindex )
            if not ind: 
                sindex = sindex + 1
                continue
            tbuffer.delete( '%s.0' % sindex , '%s' % ind )
            tbuffer.insert( '%s.0' % sindex , ws )
            sindex = sindex + 1
        return self._tailEnd( tbuffer )
    #@-node:mork.20041103095628:centerRegion
    #@+node:mork.20041103085329.2:setFillColumn
    def setFillColumn( self, event ):
        
        if self.mcStateManager.getState( 'set-fill-column' ):
            
            if event.keysym == 'Return':
                svar, label = self.getSvarLabel( event )
                value = svar.get()
                if value.isdigit():
                    self.fillColumn = int( value )
                return self.keyboardQuit( event )
            elif event.char.isdigit() or event.char == '\b':
                svar, label = self.getSvarLabel( event )
                self.setSvar( event, svar )
                return 'break'
            return 'break'
            
            
            
        else:
            self.mcStateManager.setState( 'set-fill-column', 1 )
            svar, label = self.getSvarLabel( event )
            svar.set( '' )
            label.configure( background = 'lightblue' )
            return 'break'
    #@-node:mork.20041103085329.2:setFillColumn
    #@-others
    
    #@-node:mork.20041103085329:fill column and centering
    #@+node:mork.20041031183136:region methods
    #@+others
    #@+node:mork.20041030164547.77:fillRegion
    def fillRegion( self, event ):
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        #i = tbuffer.index( 'insert' ) 
        s1 = tbuffer.index( 'sel.first' )
        s2 = tbuffer.index( 'sel.last' )
        tbuffer.mark_set( 'insert', s1 )
        self.movingParagraphs( event, -1 )
        if tbuffer.index( 'insert linestart' ) == '1.0':
            self.fillParagraph( event )
        while 1:
            self.movingParagraphs( event, 1 )
            if tbuffer.compare( 'insert', '>', s2 ):
                break
            self.fillParagraph( event )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.77:fillRegion
    #@+node:mork.20041030164547.87:setRegion
    def setRegion( self, event ):   
        mrk = 'sel'
        tbuffer = event.widget
        def extend( event ):
            widget = event.widget
            widget.mark_set( 'insert', 'insert + 1c' )
            if self.inRange( widget, mrk ):
                widget.tag_remove( mrk, 'insert -1c' )
            else:
                widget.tag_add( mrk, 'insert -1c' )
                widget.tag_configure( mrk, background = 'lightgrey' )
                self.testinrange( widget )
            return 'break'
            
        def truncate( event ):
            widget = event.widget
            widget.mark_set( 'insert', 'insert -1c' )
            if self.inRange( widget, mrk ):
                self.testinrange( widget )
                widget.tag_remove( mrk, 'insert' )
            else:
                widget.tag_add( mrk, 'insert' )
                widget.tag_configure( mrk, background = 'lightgrey' )
                self.testinrange( widget  )
            return 'break'
            
        def up( event ):
            widget = event.widget
            if not self.testinrange( widget ):
                return 'break'
            widget.tag_add( mrk, 'insert linestart', 'insert' )
            i = widget.index( 'insert' )
            i1, i2 = i.split( '.' )
            i1 = str( int( i1 ) - 1 )
            widget.mark_set( 'insert', i1+'.'+i2)
            widget.tag_add( mrk, 'insert', 'insert lineend + 1c' )
            if self.inRange( widget, mrk ,l = '-1c', r = '+1c') and widget.index( 'insert' ) != '1.0':
                widget.tag_remove( mrk, 'insert', 'end' )  
            return 'break'
            
        def down( event ):
            widget = event.widget
            if not self.testinrange( widget ):
                return 'break'
            widget.tag_add( mrk, 'insert', 'insert lineend' )
            i = widget.index( 'insert' )
            i1, i2 = i.split( '.' )
            i1 = str( int( i1 ) + 1 )
            widget.mark_set( 'insert', i1 +'.'+i2 )
            widget.tag_add( mrk, 'insert linestart -1c', 'insert' )
            if self.inRange( widget, mrk , l = '-1c', r = '+1c' ): 
                widget.tag_remove( mrk, '1.0', 'insert' )
            return 'break'
            
        extend( event )   
        tbuffer.bind( '<Right>', extend, '+' )
        tbuffer.bind( '<Left>', truncate, '+' )
        tbuffer.bind( '<Up>', up, '+' )
        tbuffer.bind( '<Down>', down, '+' )
        return 'break'
    #@-node:mork.20041030164547.87:setRegion
    #@+node:mork.20041030164547.93:indentRegion
    def indentRegion( self, event ):
        tbuffer = event.widget
        mrk = 'sel'
        trange = tbuffer.tag_ranges( mrk )
        if len( trange ) != 0:
            ind = tbuffer.search( '\w', '%s linestart' % trange[ 0 ], stopindex = 'end', regexp = True )
            if not ind : return
            text = tbuffer.get( '%s linestart' % ind ,  '%s lineend' % ind)
            sstring = text.lstrip()
            sstring = sstring[ 0 ]
            ws = text.split( sstring )
            if len( ws ) > 1:
                ws = ws[ 0 ]
            else:
                ws = ''
            s , s1 = trange[ 0 ].split( '.' )
            e , e1 = trange[ -1 ].split( '.' )
            s = int( s )
            s = s + 1
            e = int( e ) + 1
            for z in xrange( s , e ):
                t2 = tbuffer.get( '%s.0' %z ,  '%s.0 lineend'%z)
                t2 = t2.lstrip()
                t2 = ws + t2
                tbuffer.delete( '%s.0' % z ,  '%s.0 lineend' %z)
                tbuffer.insert( '%s.0' % z, t2 )
            tbuffer.event_generate( '<Key>' )
            tbuffer.update_idletasks()
        self.removeRKeys( tbuffer )
        return 'break'
    #@-node:mork.20041030164547.93:indentRegion
    #@+node:mork.20041030164547.94:tabIndentRegion
    def tabIndentRegion( self,event ):
        tbuffer = event.widget
        if not self._chckSel( event ):
            return
        i = tbuffer.index( 'sel.first' )
        i2 = tbuffer.index( 'sel.last' )
        i = tbuffer.index( '%s linestart' %i )
        i2 = tbuffer.index( '%s linestart' % i2)
        while 1:
            tbuffer.insert( i, '\t' )
            if i == i2: break
            i = tbuffer.index( '%s + 1 lines' % i )    
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.94:tabIndentRegion
    #@+node:mork.20041030164547.102:countRegion
    def countRegion( self, event ):
        tbuffer = event.widget
        txt = tbuffer.get( 'sel.first', 'sel.last')
        svar = self.svars[ tbuffer ]
        lines = 1
        chars = 0
        for z in txt:
            if z == '\n': lines = lines + 1
            else:
                chars = chars + 1       
        svar.set( 'Region has %s lines, %s characters' %( lines, chars ) )
        return 'break'
    #@-node:mork.20041030164547.102:countRegion
    #@+node:mork.20041030164547.138:reverseRegion
    def reverseRegion( self, event ):
        tbuffer = event.widget
        if not self._chckSel( event ):
            return
        ins = tbuffer.index( 'insert' )
        is1 = tbuffer.index( 'sel.first' )
        is2 = tbuffer.index( 'sel.last' )    
        txt = tbuffer.get( '%s linestart' % is1, '%s lineend' %is2 )
        tbuffer.delete( '%s linestart' % is1, '%s lineend' %is2  )
        txt = txt.split( '\n' )
        txt.reverse()
        istart = is1.split( '.' )
        istart = int( istart[ 0 ] )
        for z in txt:
            tbuffer.insert( '%s.0' % istart, '%s\n' % z )
            istart = istart + 1
        tbuffer.mark_set( 'insert', ins )
        self.mcStateManager.clear()
        self.resetMiniBuffer( event )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.138:reverseRegion
    #@+node:mork.20041030164547.149:upperLowerRegion
    def upperLowerRegion( self, event, way ):
        tbuffer = event.widget
        mrk = 'sel'
        trange = tbuffer.tag_ranges( mrk )
        if len( trange ) != 0:
            text = tbuffer.get( trange[ 0 ] , trange[ -1 ] )
            i = tbuffer.index( 'insert' )
            if text == ' ': return 'break'
            tbuffer.delete( trange[ 0 ], trange[ -1 ] )
            if way == 'low':
                text = text.lower()
            if way == 'up':
                text = text.upper()
            tbuffer.insert( 'insert', text )
            tbuffer.mark_set( 'insert', i ) 
        self.removeRKeys( tbuffer )
        return 'break'
    #@-node:mork.20041030164547.149:upperLowerRegion
    #@-others
    #@nonl
    #@-node:mork.20041031183136:region methods
    #@+node:mork.20041122190403:searching
    #@+at
    # A tremendous variety of searching methods are available.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041031182837:incremental search methods
    #@+at
    # These methods enable the incremental search functionality.
    # 
    #@-at
    #@@c
    
    #@+others
    #@+node:mork.20041030164547.79:startIncremental
    def startIncremental( self, event, stroke, which='normal' ):
        #global isearch, pref
        #widget = event.widget
        #if self.isearch:
        isearch = self.mcStateManager.getState( 'isearch' )
        if isearch:
            self.search( event, way = self.csr[ stroke ], useregex = self.useRegex() )
            self.pref = self.csr[ stroke ]
            self.scolorizer( event )
            return 'break'
        else:
            svar, label = self.getSvarLabel( event )
            #self.isearch = True'
            self.mcStateManager.setState( 'isearch', which )
            self.pref = self.csr[ stroke ]
            label.configure( background = 'lightblue' )
            label.configure( textvariable = svar )
            return 'break'
    #@-node:mork.20041030164547.79:startIncremental
    #@+node:mork.20041030164547.38:search
    def search( self, event, way , useregex=False):
        '''This method moves the insert spot to position that matches the pattern in the minibuffer'''
        tbuffer = event.widget
        svar, label = self.getSvarLabel( event )
        stext = svar.get()
        if stext == '': return 'break'
        try:
            if way == 'bak': #Means search backwards.
                i = tbuffer.search( stext, 'insert', backwards = True,  stopindex = '1.0' , regexp = useregex )
                if not i: #If we dont find one we start again at the bottom of the buffer. 
                    i = tbuffer.search( stext, 'end', backwards = True, stopindex = 'insert', regexp = useregex)
            else: #Since its not 'bak' it means search forwards.
                i = tbuffer.search(  stext, "insert + 1c", stopindex = 'end', regexp = useregex ) 
                if not i: #If we dont find one we start at the top of the buffer. 
                    i = tbuffer.search( stext, '1.0', stopindex = 'insert', regexp = useregex )
        except:
            return 'break'
        if not i or i.isspace(): return 'break'
        tbuffer.mark_set( 'insert', i )
        tbuffer.see( 'insert' )
    #@-node:mork.20041030164547.38:search
    #@+node:mork.20041030164547.80:iSearch
    def iSearch( self, event, stroke ):
        if len( event.char ) == 0: return
        
        if stroke in self.csr: return self.startIncremental( event, stroke )
        svar, label = self.getSvarLabel( event )
        if event.keysym == 'Return':
              if svar.get() == '':
                  return self.startNonIncrSearch( event, self.pref )
              else:
                return self.stopControlX( event )
              #return self._tailEnd( event.widget )
        widget = event.widget
        label.configure( textvariable = svar )
        #if event.keysym == 'Return':
        #      return self.stopControlX( event )
        self.setSvar( event, svar )
        if event.char != '\b':
           stext = svar.get()
           z = widget.search( stext , 'insert' , stopindex = 'insert +%sc' % len( stext ) )
           if not z:
               self.search( event, self.pref, useregex= self.useRegex() )
        self.scolorizer( event )
        return 'break'
    #@-node:mork.20041030164547.80:iSearch
    #@+node:mork.20041030164547.153:scolorizer
    def scolorizer( self, event ):
    
        tbuffer = event.widget
        svar, label = self.getSvarLabel( event )
        stext = svar.get()
        tbuffer.tag_delete( 'color' )
        tbuffer.tag_delete( 'color1' )
        if stext == '': return 'break'
        ind = '1.0'
        while ind:
            try:
                ind = tbuffer.search( stext, ind, stopindex = 'end', regexp = self.useRegex() )
            except:
                break
            if ind:
                i, d = ind.split('.')
                d = str(int( d ) + len( stext ))
                index = tbuffer.index( 'insert' )
                if ind == index:
                    tbuffer.tag_add( 'color1', ind, '%s.%s' % (i,d) )
                tbuffer.tag_add( 'color', ind, '%s.%s' % (i, d) )
                ind = i +'.'+d
        tbuffer.tag_config( 'color', foreground = 'red' ) 
        tbuffer.tag_config( 'color1', background = 'lightblue' ) 
    #@-node:mork.20041030164547.153:scolorizer
    #@+node:mork.20041121125455:useRegex
    def useRegex( self ):
    
        isearch = self.mcStateManager.getState( 'isearch' )
        risearch = False
        if isearch != 'normal':
            risearch=True
        return risearch
    #@nonl
    #@-node:mork.20041121125455:useRegex
    #@-others
    #@nonl
    #@-node:mork.20041031182837:incremental search methods
    #@+node:mork.20041122154604:non-incremental search methods
    #@+at
    # Accessed by Control-s Enter or Control-r Enter.  Alt-x forward-search or 
    # backward-search, just looks for words...
    # 
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041122154604.1:nonincrSearch
    def nonincrSearch( self, event, stroke ):
        
        if event.keysym in ('Control_L', 'Control_R' ): return
        state = self.mcStateManager.getState( 'nonincr-search' )
        svar, label = self.getSvarLabel( event )
        if state.startswith( 'start' ):
            state = state[ 5: ]
            self.mcStateManager.setState( 'nonincr-search', state )
            svar.set( '' )
            
        if svar.get() == '' and stroke=='<Control-w>':
            return self.startWordSearch( event, state )
        
        if event.keysym == 'Return':
            
            tbuffer = event.widget
            i = tbuffer.index( 'insert' )
            word = svar.get()
            if state == 'for':
                s = tbuffer.search( word, i , stopindex = 'end' )
                if s:
                    s = tbuffer.index( '%s +%sc' %( s, len( word ) ) )
            else:            
                s = tbuffer.search( word,i, stopindex = '1.0', backwards = True )
                
            if s:
                tbuffer.mark_set( 'insert', s )    
            self.keyboardQuit( event )
            return self._tailEnd( tbuffer )        
                
        else:
            self.setSvar( event, svar )
            return 'break'
    
    
    #@-node:mork.20041122154604.1:nonincrSearch
    #@+node:mork.20041122155708:startNonIncrSearch
    def startNonIncrSearch( self, event, which ):
        
        self.keyboardQuit( event )
        tbuffer = event.widget
        self.mcStateManager.setState( 'nonincr-search', 'start%s' % which )
        svar, label = self.getSvarLabel( event )
        self.setLabelBlue( label )
        svar.set( 'Search:' )
        return 'break'
    #@-node:mork.20041122155708:startNonIncrSearch
    #@-others
    #@nonl
    #@-node:mork.20041122154604:non-incremental search methods
    #@+node:mork.20041122171601:word search methods
    #@+at
    # 
    # Control-s(r) Enter Control-w words Enter, pattern entered is treated as 
    # a regular expression.
    # 
    # for example in the buffer we see:
    #     cats......................dogs
    # if we are after this and we enter the backwards look, search for 'cats 
    # dogs' if will take us to the match.
    # 
    #@-at
    #@@c
    
    #@+others
    #@+node:mork.20041122171601.1:startWordSearch
    def startWordSearch( self, event, which ):
    
        self.keyboardQuit( event )
        tbuffer = event.widget
        self.mcStateManager.setState( 'word-search', 'start%s' % which )
        svar, label = self.getSvarLabel( event )
        self.setLabelBlue( label )
        if which == 'bak':
            txt = 'Backward'
        else:
            txt = 'Forward'
        svar.set( 'Word Search %s:' % txt ) 
        return 'break'
    #@-node:mork.20041122171601.1:startWordSearch
    #@+node:mork.20041122171601.2:wordSearch
    def wordSearch( self, event ):
    
        state = self.mcStateManager.getState( 'word-search' )
        svar, label = self.getSvarLabel( event )
        if state.startswith( 'start' ):
            state = state[ 5: ]
            self.mcStateManager.setState( 'word-search', state )
            svar.set( '' )
            
        
        if event.keysym == 'Return':
            
            tbuffer = event.widget
            i = tbuffer.index( 'insert' )
            words = svar.get().split()
            sep = '[%s%s]+' %( string.punctuation, string.whitespace )
            pattern = sep.join( words )
            cpattern = re.compile( pattern )
            if state == 'for':
                
                txt = tbuffer.get( 'insert', 'end' )
                match = cpattern.search( txt )
                if not match: return self.keyboardQuit( event )
                end = match.end()
                
            else:            
                txt = tbuffer.get( '1.0', 'insert' ) #initially the reverse words formula for Python Cookbook was going to be used.
                a = re.split( pattern, txt )         #that didnt quite work right.  This one apparently does.   
                if len( a ) > 1:
                    b = re.findall( pattern, txt )
                    end = len( a[ -1 ] ) + len( b[ -1 ] )
                else:
                    return self.keyboardQuit( event )
                
            wdict ={ 'for': 'insert +%sc', 'bak': 'insert -%sc' }
            
            tbuffer.mark_set( 'insert', wdict[ state ] % end )                                
            tbuffer.see( 'insert' )    
            self.keyboardQuit( event )
            return self._tailEnd( tbuffer )        
                
        else:
            self.setSvar( event, svar )
            return 'break'
    #@nonl
    #@-node:mork.20041122171601.2:wordSearch
    #@-others
    #@nonl
    #@-node:mork.20041122171601:word search methods
    #@+node:mork.20041121103034:re-search methods
    #@+at
    # For the re-search-backward and re-search-forward Alt-x commands
    # 
    #@-at
    #@@c
    
    
    
    #@+others
    #@+node:mork.20041121103034.1:reStart
    def reStart( self, event, which='forward' ):
        self.keyboardQuit( event )
        tbuffer = event.widget
        self.mcStateManager.setState( 're_search', 'start%s' % which )
        svar, label = self.getSvarLabel( event )
        label.configure( background = 'lightblue' )
        svar.set( 'RE Search:' )
        return 'break'
    #@-node:mork.20041121103034.1:reStart
    #@+node:mork.20041121103034.2:re_search
    def re_search( self, event ):
        svar, label = self.getSvarLabel( event )
    
        state = self.mcStateManager.getState( 're_search' )
        if state.startswith( 'start' ):
            state = state[ 5: ]
            self.mcStateManager.setState( 're_search', state )
            svar.set( '' )
           
    
            
        if event.keysym == 'Return':
           
            tbuffer = event.widget
            pattern = svar.get()
            cpattern = re.compile( pattern )
            end = None
            if state == 'forward':
                
                txt = tbuffer.get( 'insert', 'end' )
                match = cpattern.search( txt )
                end = match.end()
            
            else:
    
                txt = tbuffer.get( '1.0', 'insert' ) #initially the reverse words formula for Python Cookbook was going to be used.
                a = re.split( pattern, txt )         #that didnt quite work right.  This one apparently does.   
                if len( a ) > 1:
                    b = re.findall( pattern, txt )
                    end = len( a[ -1 ] ) + len( b[ -1 ] )
            
            if end:
                
                wdict ={ 'forward': 'insert +%sc', 'backward': 'insert -%sc' }
                    
                tbuffer.mark_set( 'insert', wdict[ state ] % end )                                
                self._tailEnd( tbuffer )
                tbuffer.see( 'insert' )
                
            return self.keyboardQuit( event )    
            
            
        else:
            self.setSvar( event, svar )
            return 'break'
    
    #@-node:mork.20041121103034.2:re_search
    #@-others
    #@nonl
    #@-node:mork.20041121103034:re-search methods
    #@-others
    #@nonl
    #@-node:mork.20041122190403:searching
    #@+node:mork.20041121140620:diff methods
    #@+at
    # the diff command, accessed by Alt-x diff.  Creates a buffer and puts the 
    # diff between 2 files into it.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041121140620.1:diff
    def diff( self, event ):
        
        try:
            f, name = self.getReadableTextFile()
            txt1 = f.read()
            f.close()
            
            f2, name2 = self.getReadableTextFile()
            txt2 = f2.read()
            f2.close()
        except:
            return self.keyboardQuit( event )
        
        
        self.switchToBuffer( event, "*diff* of ( %s , %s )" %( name, name2 ) )
        import difflib
        data = difflib.ndiff( txt1, txt2 )
        idata = []
        for z in data:
            idata.append( z )
        tbuffer = event.widget
        tbuffer.delete( '1.0', 'end' )
        tbuffer.insert( '1.0', ''.join( idata ) )
        self._tailEnd( tbuffer )
        return self.keyboardQuit( event )
    #@-node:mork.20041121140620.1:diff
    #@-others
    #@nonl
    #@-node:mork.20041121140620:diff methods
    #@+node:mork.20041031182332:Zap methods
    #@+at
    # These methods start and execute the Zap to functionality.
    #@-at
    #@@c
    
    
    
    #@+others
    #@+node:mork.20041030164547.81:startZap
    def startZap( self, event ):
        #global zap
        #self.zap = True
        self.mcStateManager.setState( 'zap', True )
        svar, label = self.getSvarLabel( event )
        label.configure( background = 'lightblue' )
        svar.set( 'Zap To Character' )
        return 'break'
    #@-node:mork.20041030164547.81:startZap
    #@+node:mork.20041030164547.82:zapTo
    def zapTo( self, event ):
            #global zap
    
            widget = event.widget
            s = string.ascii_letters + string.digits + string.punctuation
            if len( event.char ) != 0 and event.char in s:
                #self.zap = False
                self.mcStateManager.setState( 'zap', False )
                i = widget.search( event.char , 'insert',  stopindex = 'end' )
                self.resetMiniBuffer( event )
                if i:
                    t = widget.get( 'insert', '%s+1c'% i )
                    self.addToKillBuffer( t )
                    widget.delete( 'insert', '%s+1c' % i)
                    return 'break'
            else:
                return 'break'
    #@-node:mork.20041030164547.82:zapTo
    #@-others
    #@nonl
    #@-node:mork.20041031182332:Zap methods
    #@+node:mork.20041031181740:ControlX methods
    #@+others
    #@+node:mork.20041030164547.84:startControlX
    def startControlX( self, event ):
        '''This method starts the Control-X command sequence.'''  
        #global controlx
        #self.controlx = True
        self.mcStateManager.setState( 'controlx', True )
        svar, label = self.getSvarLabel( event )
        svar.set( 'Control - X' )
        label.configure( background = 'lightblue' )
        return 'break'
    #@-node:mork.20041030164547.84:startControlX
    #@+node:mork.20041030164547.85:stopControlX
    def stopControlX( self, event ):  #This will all be migrated to keyboardQuit eventually.
        '''This method clears the state of the Emacs instance'''
        #global controlx, rstring, isearch, sRect,negativeArg, uC, howM, altx
        #self.altx = False
        #self.howM = False
        #self.controlx = False
        #self.isearch = False
        if self.shuttingdown: return
        self.sRect = False
        #self.uC = False
        #self.negativeArg = False
        self.mcStateManager.clear()
        event.widget.tag_delete( 'color' )
        event.widget.tag_delete( 'color1' )
        if self.registermode:
            self.deactivateRegister( event )
        self.rectanglemode = 0
        self.bufferMode = None
        #self.rString = False
        self.resetMiniBuffer( event )
        event.widget.update_idletasks()     
        return 'break'
    
    #@-node:mork.20041030164547.85:stopControlX
    #@+node:mork.20041030164547.78:doControlX
    #self.registermode = False
    def doControlX( self, event, stroke, previous = [] ):
        #global registermode
        """previous.insert( 0, event.keysym )
        if len( previous ) > 10: previous.pop()
        if stroke == '<Key>':
            if event.keysym in ( 'Shift_L', 'Shift_R' ):
                return
            if event.keysym == 'period':
                self.stopControlX( event )
                return self.setFillPrefix( event )
            if event.keysym == 'parenleft':
                self.stopControlX( event )
                return self.startKBDMacro( event )
            if event.keysym == 'parenright':
                self.stopControlX( event )
                return self.stopKBDMacro( event )
            if event.keysym == 'semicolon':
                self.stopControlX( event )
                return self.setCommentColumn( event )
            if event.keysym == 'Tab':
                self.stopControlX( event )
                return self.tabIndentRegion( event )
            if self.sRect:
                self.stringRectangle( event )
                return 'break'
            if event.keysym in ( 'a', 'i' , 'e'):
                svar, label = self.getSvarLabel( event )
                if svar.get() != 'a' and event.keysym == 'a':
                    svar.set( 'a' )
                    return 'break'
                elif svar.get() == 'a':
                    if event.char == 'i':
                        svar.set( 'a i' )
                    elif event.char == 'e':
                        self.stopControlX( event )
                        event.char = ''
                        self.expandAbbrev( event )
                    return 'break'
            if event.keysym == 'g':
                svar, label = self.getSvarLabel( event )
                l = svar.get()
                if l == 'a':
                    self.stopControlX( event )
                    return self.abbreviationDispatch( event, 1 )
                elif l == 'a i':
                    self.stopControlX( event )
                    return self.abbreviationDispatch( event, 2 )
            if event.keysym == 'e':
                self.stopControlX( event )
                return self.executeLastMacro( event )
            if event.keysym == 'x' and previous[ 1 ] not in ( 'Control_L', 'Control_R'):
                event.keysym = 's' 
                self.setNextRegister( event )
                return 'break'
            if event.keysym == 'o' and self.registermode == 1:
                self.openRectangle( event )
                return 'break'
            if event.keysym == 'c' and self.registermode == 1:
                self.clearRectangle( event )
                return 'break'
            if event.keysym == 't' and self.registermode == 1:
                self.stringRectangle( event )
                return 'break'
            if event.keysym == 'y' and self.registermode == 1:
                self.yankRectangle( event )
                return 'break'
            if event.keysym == 'd' and self.registermode == 1:
                self.deleteRectangle( event )
                return 'break'
            if event.keysym == 'k' and self.registermode == 1:
                self.killRectangle( event )
                return 'break'       
            if self.registermode == 1:
                self.setNextRegister( event )
                return 'break'
            elif self.registermode == 2:
                self.executeRegister( event )
                return 'break'
            if event.keysym == 'r':
                self.registermode = 1
                svar = self.svars[ event.widget ]
                svar.set( 'C - x r' )
                return 'break'
            if event.keysym== 'h':
               self.stopControlX( event )
               event.widget.tag_add( 'sel', '1.0', 'end' )
               return 'break' 
            if event.keysym == 'equal':
                self.lineNumber( event )
                return 'break'
            if event.keysym == 'u':
                self.stopControlX( event )
                return self.doUndo( event, 2 )
        if stroke in self.xcommands:
            self.xcommands[ stroke ]( event )
            self.stopControlX( event )
        return 'break' """
        return self.cxHandler( event, stroke )
    #@-node:mork.20041030164547.78:doControlX
    #@-others
    #@nonl
    #@-node:mork.20041031181740:ControlX methods
    #@+node:mork.20041031183614.1:range methods
    #@+others
    #@+node:mork.20041030164547.88:inRange
    def inRange( self, widget, range, l = '', r = '' ):
        ranges = widget.tag_ranges( range )
        #i = widget.index( 'insert' )
        for z in xrange( 0,  len( ranges) , 2 ):
            z1 = z + 1
            l1 = 'insert%s' %l
            r1 = 'insert%s' % r
            if widget.compare( l1, '>=', ranges[ z ]) and widget.compare( r1, '<=', ranges[ z1] ):
                return True
        return False
    #@-node:mork.20041030164547.88:inRange
    #@+node:mork.20041030164547.89:contRanges
    def contRanges( self, widget, range ):
        ranges = widget.tag_ranges( range)
        t1 = widget.get( ranges[ 0 ], ranges[ -1 ] )
        t2 = []
        for z in xrange( 0,  len( ranges) , 2 ):
            z1 = z + 1
            t2.append( widget.get( ranges[ z ], ranges[ z1 ] ) )
        t2 = '\n'.join( t2 )
        return t1 == t2
    #@-node:mork.20041030164547.89:contRanges
    #@+node:mork.20041030164547.90:testinrange
    def testinrange( self, widget ):
        mrk = 'sel'
        #ranges = widget.tag_ranges( mrk)
        if not self.inRange( widget , mrk) or not self.contRanges( widget, mrk ):
            self.removeRKeys( widget )
            return False
        return True
    #@-node:mork.20041030164547.90:testinrange
    #@-others
    #@nonl
    #@-node:mork.20041031183614.1:range methods
    #@+node:mork.20041031182402:delete methods
    #@+others
    #@+node:mork.20041030164547.97:deleteIndentation
    def deleteIndentation( self, event ):
        tbuffer = event.widget
        txt = tbuffer.get( 'insert linestart' , 'insert lineend' )
        txt = ' %s' % txt.lstrip()
        tbuffer.delete( 'insert linestart' , 'insert lineend +1c' )    
        i  = tbuffer.index( 'insert - 1c' )
        tbuffer.insert( 'insert -1c', txt )
        tbuffer.mark_set( 'insert', i )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.97:deleteIndentation
    #@+node:mork.20041030164547.98:deleteNextChar
    def deleteNextChar( self,event ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        tbuffer.delete( i, '%s +1c' % i )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.98:deleteNextChar
    #@+node:mork.20041030164547.99:deleteSpaces
    def deleteSpaces( self, event , insertspace = False):
        tbuffer = event.widget
        char = tbuffer.get( 'insert', 'insert + 1c ' )
        if char.isspace():
            i = tbuffer.index( 'insert' )
            wf = tbuffer.search( r'\w', i, stopindex = '%s lineend' % i, regexp = True )
            wb = tbuffer.search( r'\w', i, stopindex = '%s linestart' % i, regexp = True, backwards = True )
            if '' in ( wf, wb ):
                return 'break'
            tbuffer.delete( '%s +1c' %wb, wf )
            if insertspace:
                tbuffer.insert( 'insert', ' ' )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.99:deleteSpaces
    #@-others
    #@nonl
    #@-node:mork.20041031182402:delete methods
    #@+node:mork.20041031181701.1:query replace methods
    #@+at
    # These methods handle the query-replace and query-replace-regex 
    # commands.  They need to be fully migrated
    # to the self.mcStateManager mechanism, which should simplify things 
    # greatly, or at least the amount of variables its required
    # so far.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041030164547.107:qreplace
    def qreplace( self, event ):
    
        if event.keysym == 'y':
            self._qreplace( event )
            return
        elif event.keysym in ( 'q', 'Return' ):
            self.quitQSearch( event )
        elif event.keysym == 'exclam':
            while self.qrexecute:
                self._qreplace( event )
        elif event.keysym in ( 'n', 'Delete'):
            #i = event.widget.index( 'insert' )
            event.widget.mark_set( 'insert', 'insert +%sc' % len( self.qQ ) )
            self.qsearch( event )
        event.widget.see( 'insert' )
    #@-node:mork.20041030164547.107:qreplace
    #@+node:mork.20041030164547.108:_qreplace
    def _qreplace( self, event ):
        i = event.widget.tag_ranges( 'qR' )
        event.widget.delete( i[ 0 ], i[ 1 ] )
        event.widget.insert( 'insert', self.qR )
        self.qsearch( event )
    #@-node:mork.20041030164547.108:_qreplace
    #@+node:mork.20041030164547.109:getQuery
    #self.qgetQuery = False
    #self.lqQ = Tkinter.StringVar()
    #self.lqQ.set( 'Replace with:' )      
    def getQuery( self, event ):
        #global qQ, qgetQuery, qgetReplace
        l = event.keysym
        svar, label = self.getSvarLabel( event )
        label.configure( textvariable = svar )
        if l == 'Return':
            self.qgetQuery = False
            self.qgetReplace = True
            self.qQ = svar.get()
            svar.set( "Replace with:" )
            self.mcStateManager.setState( 'qlisten', 'replace-caption' )
            #label.configure( textvariable = self.lqQ)
            return
        if self.mcStateManager.getState( 'qlisten' ) == 'replace-caption':
            svar.set( '' )
            self.mcStateManager.setState( 'qlisten', True )
        self.setSvar( event, svar )
    #@-node:mork.20041030164547.109:getQuery
    #@+node:mork.20041030164547.110:getReplace
    #self.qgetReplace = False
    def getReplace( self, event ):
        #global qR, qgetReplace, qrexecute
        l = event.keysym
        svar, label = self.getSvarLabel( event )
        label.configure( textvariable = svar )
        if l == 'Return':
            self.qgetReplace = False
            self.qR = svar.get()
            self.qrexecute = True
            ok = self.qsearch( event )
            if self.querytype == 'regex' and ok:
                tbuffer = event.widget
                range = tbuffer.tag_ranges( 'qR' )
                txt = tbuffer.get( range[ 0 ], range[ 1 ] )
                svar.set( 'Replace %s with %s y/n(! for all )' %( txt, self.qR ) )
            elif ok:
                svar.set( 'Replace %s with %s y/n(! for all )' %( self.qQ, self.qR ) )
            #self.qrexecute = True
            #ok = self.qsearch( event )
            return
        if self.mcStateManager.getState( 'qlisten' ) == 'replace-caption':
            svar.set( '' )
            self.mcStateManager.setState( 'qlisten', True )
        self.setSvar( event, svar )
    #@-node:mork.20041030164547.110:getReplace
    #@+node:mork.20041030164547.111:masterQR
    #self.qrexecute = False   
    def masterQR( self, event ):
    
        if self.qgetQuery:
            self.getQuery( event )
        elif self.qgetReplace:
            self.getReplace( event )
        elif self.qrexecute:
            self.qreplace( event )
        else:
            #svar, label = self.getSvarLabel( event )
            #svar.set( '' )
            self.listenQR( event )
        return 'break'
    #@-node:mork.20041030164547.111:masterQR
    #@+node:mork.20041123113640:startRegexReplace
    def startRegexReplace( self ):
        
        self.querytype = 'regex'
        return True
    #@-node:mork.20041123113640:startRegexReplace
    #@+node:mork.20041031194858:query search methods
    #@+others
    #@+node:mork.20041030164547.104:listenQR
    #self.qQ = None
    #self.qR = None
    #self.qlisten = False
    #self.lqR = Tkinter.StringVar()
    #self.lqR.set( 'Query with: ' )
    def listenQR( self, event ):
        #global qgetQuery, qlisten
        #self.qlisten = True
        self.mcStateManager.setState( 'qlisten', 'replace-caption' )
        #tbuffer = event.widget
        svar, label = self.getSvarLabel( event )
        self.setLabelBlue( label )
        if self.querytype == 'regex':
            svar.set( "Regex Query with:" )
        else:
            svar.set( "Query with:" )
        #label.configure( background = 'lightblue' , textvariable = self.lqR)
        self.qgetQuery = True
    #@-node:mork.20041030164547.104:listenQR
    #@+node:mork.20041030164547.105:qsearch
    def qsearch( self, event ):
        if self.qQ:
            tbuffer = event.widget
            tbuffer.tag_delete( 'qR' )
            svar, label = self.getSvarLabel( event )
            if self.querytype == 'regex':
                try:
                    regex = re.compile( self.qQ )
                except:
                    self.keyboardQuit( event )
                    svar.set( "Illegal regular expression" )
                    
                txt = tbuffer.get( 'insert', 'end' )
                match = regex.search( txt )
                if match:
                    start = match.start()
                    end = match.end()
                    length = end - start
                    tbuffer.mark_set( 'insert', 'insert +%sc' % start )
                    tbuffer.update_idletasks()
                    tbuffer.tag_add( 'qR', 'insert', 'insert +%sc' % length )
                    tbuffer.tag_config( 'qR', background = 'lightblue' )
                    txt = tbuffer.get( 'insert', 'insert +%sc' % length )
                    svar.set( "Replace %s with %s? y/n(! for all )" % ( txt, self.qR ) )
                    return True
            else:
                i = tbuffer.search( self.qQ, 'insert', stopindex = 'end' )
                if i:
                    tbuffer.mark_set( 'insert', i )
                    tbuffer.update_idletasks()
                    tbuffer.tag_add( 'qR', 'insert', 'insert +%sc'% len( self.qQ ) )
                    tbuffer.tag_config( 'qR', background = 'lightblue' )
                    self._tailEnd( tbuffer )
                    return True
            self.quitQSearch( event )
            return False
    
    #@-node:mork.20041030164547.105:qsearch
    #@+node:mork.20041030164547.106:quitQSearch
    def quitQSearch( self,event ):
        #global qQ, qR, qlisten, qrexecute
        event.widget.tag_delete( 'qR' )
        self.qQ = None
        self.qR = None
        #self.qlisten = False
        self.mcStateManager.setState( 'qlisten', False )
        self.qrexecute = False
        svar, label = self.getSvarLabel( event )
        svar.set( '' )
        label.configure( background = 'lightgrey' )
        #self.keyboardQuit( event )
        self.querytype = 'normal'
        self._tailEnd( event.widget )
        #event.widget.event_generate( '<Key>' )
        #event.widget.update_idletasks()
    #@-node:mork.20041030164547.106:quitQSearch
    #@-others
    #@nonl
    #@-node:mork.20041031194858:query search methods
    #@-others
    #@nonl
    #@-node:mork.20041031181701.1:query replace methods
    #@+node:mork.20041031155313:Rectangles methods
    #@+others
    #@+node:mork.20041031202908:activateRectangleMethods
    def activateRectangleMethods( self, event ):
        
        self.rectanglemode = 1
        svar = self.svars[ event.widget ]
        svar.set( 'C - x r' )
        return 'break'
    #@-node:mork.20041031202908:activateRectangleMethods
    #@+node:mork.20041030164547.120:openRectangle
    def openRectangle( self, event ):
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        r1, r2, r3, r4 = self.getRectanglePoints( event )
        lth = ' ' * ( r4 - r2 )
        self.stopControlX( event )
        while r1 <= r3:
            tbuffer.insert( '%s.%s' % ( r1, r2 ) , lth)
            r1 = r1 + 1
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.120:openRectangle
    #@+node:mork.20041030164547.121:clearRectangle
    def clearRectangle( self, event ):
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        r1, r2, r3, r4 = self.getRectanglePoints( event )
        lth = ' ' * ( r4 - r2 )
        self.stopControlX( event )
        while r1 <= r3:
            tbuffer.delete( '%s.%s' % ( r1, r2 ) , '%s.%s' % ( r1, r4 )  )
            tbuffer.insert( '%s.%s' % ( r1, r2 ) , lth)
            r1 = r1 + 1
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.121:clearRectangle
    #@+node:mork.20041030164547.122:deleteRectangle
    def deleteRectangle( self, event ):
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        r1, r2, r3, r4 = self.getRectanglePoints( event )
        #lth = ' ' * ( r4 - r2 )
        self.stopControlX( event )
        while r1 <= r3:
            tbuffer.delete( '%s.%s' % ( r1, r2 ) , '%s.%s' % ( r1, r4 )  )
            r1 = r1 + 1
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.122:deleteRectangle
    #@+node:mork.20041030164547.123:stringRectangle
    #self.sRect = False   
    def stringRectangle( self, event ):
        #global sRect
        svar, label = self.getSvarLabel( event )
        if not self.sRect:
            self.sRect = 1
            svar.set( 'String rectangle :' )
            self.setLabelBlue( label )
            return 'break'
        if event.keysym == 'Return':
            self.sRect = 3
        if self.sRect == 1:
            svar.set( '' )
            self.sRect = 2
        if self.sRect == 2:
            self.setSvar( event, svar )
            return 'break'
        if self.sRect == 3:
            if not self._chckSel( event ):
                self.stopControlX( event )
                return
            tbuffer = event.widget
            r1, r2, r3, r4 = self.getRectanglePoints( event )
            lth = svar.get()
            #self.stopControlX( event )
            while r1 <= r3:
                tbuffer.delete( '%s.%s' % ( r1, r2 ),  '%s.%s' % ( r1, r4 ) )
                tbuffer.insert( '%s.%s' % ( r1, r2 ) , lth )
                r1 = r1 + 1
            #i = tbuffer.index( 'insert' )
            #tbuffer.mark_set( 'insert', 'insert wordend' )
            #tbuffer.tag_remove( 'sel', '1.0', 'end' )
            #return self._tailEnd( tbuffer )
            self.stopControlX( event )
            return self._tailEnd( tbuffer )
            #return 'break'
            #return 'break'
            #tbuffer.mark_set( 'insert', i )
            #return 'break'
    #@-node:mork.20041030164547.123:stringRectangle
    #@+node:mork.20041030164547.124:killRectangle
    #self.krectangle = None       
    def killRectangle( self, event ):
        #global krectangle
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        r1, r2, r3, r4 = self.getRectanglePoints( event )
        #lth = ' ' * ( r4 - r2 )
        self.stopControlX( event )
        self.krectangle = []
        while r1 <= r3:
            txt = tbuffer.get( '%s.%s' % ( r1, r2 ) , '%s.%s' % ( r1, r4 )  )
            self.krectangle.append( txt )
            tbuffer.delete( '%s.%s' % ( r1, r2 ) , '%s.%s' % ( r1, r4 )  )
            r1 = r1 + 1
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.124:killRectangle
    #@+node:mork.20041030164547.125:closeRectangle
    def closeRectangle( self, event ):
        if not self._chckSel( event ):
            return
        tbuffer = event.widget
        r1, r2, r3, r4 = self.getRectanglePoints( event ) 
        ar1 = r1
        txt = []
        while ar1 <= r3:
            txt.append( tbuffer.get( '%s.%s' %( ar1, r2 ), '%s.%s' %( ar1, r4 ) ) )
            ar1 = ar1 + 1 
        for z in txt:
            if z.lstrip().rstrip():
                return
        while r1 <= r3:
            tbuffer.delete( '%s.%s' %(r1, r2 ), '%s.%s' %( r1, r4 ) )
            r1 = r1 + 1
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.125:closeRectangle
    #@+node:mork.20041030164547.126:yankRectangle
    def yankRectangle( self, event , krec = None ):
        self.stopControlX( event )
        if not krec:
            krec = self.krectangle
        if not krec:
            return 'break'
        tbuffer = event.widget
        txt = tbuffer.get( 'insert linestart', 'insert' )
        txt = self.getWSString( txt )
        i = tbuffer.index( 'insert' )
        i1, i2 = i.split( '.' )
        i1 = int( i1 )
        for z in krec:        
            txt2 = tbuffer.get( '%s.0 linestart' % i1, '%s.%s' % ( i1, i2 ) )
            if len( txt2 ) != len( txt ):
                amount = len( txt ) - len( txt2 )
                z = txt[ -amount : ] + z
            tbuffer.insert( '%s.%s' %( i1, i2 ) , z )
            if tbuffer.index( '%s.0 lineend +1c' % i1 ) == tbuffer.index( 'end' ):
                tbuffer.insert( '%s.0 lineend' % i1, '\n' )
            i1 = i1 + 1
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.126:yankRectangle
    #@+node:mork.20041030164547.128:getRectanglePoints
    def getRectanglePoints( self, event ):
        tbuffer = event.widget
        i = tbuffer.index( 'sel.first' )
        i2 = tbuffer.index( 'sel.last' )
        r1, r2 = i.split( '.' )
        r3, r4 = i2.split( '.' )
        r1 = int( r1 )
        r2 = int( r2 )
        r3 = int( r3 )
        r4 = int( r4 )
        return r1, r2, r3, r4
    #@-node:mork.20041030164547.128:getRectanglePoints
    #@-others
    #@nonl
    #@-node:mork.20041031155313:Rectangles methods
    #@+node:mork.20041031181701.2:dynamic abbreviations methods
    #@+others
    #@+node:mork.20041030164547.132:dynamicExpansion
    def dynamicExpansion( self, event ):#, store = {'rlist': [], 'stext': ''} ):
        tbuffer = event.widget
        rlist = self.store[ 'rlist' ]
        stext = self.store[ 'stext' ]
        i = tbuffer.index( 'insert -1c wordstart' )
        i2 = tbuffer.index( 'insert -1c wordend' )
        txt = tbuffer.get( i, i2 )
        dA = tbuffer.tag_ranges( 'dA' )
        tbuffer.tag_delete( 'dA' )
        def doDa( txt, from_ = 'insert -1c wordstart', to_ = 'insert -1c wordend' ):
    
            tbuffer.delete( from_, to_ ) 
            tbuffer.insert( 'insert', txt, 'dA' )
            return self._tailEnd( tbuffer )
            
        if dA:
            dA1, dA2 = dA
            dtext = tbuffer.get( dA1, dA2 )
            if dtext.startswith( stext ) and i2 == dA2: #This seems reasonable, since we cant get a whole word that has the '-' char in it, we do a good guess
                if rlist:
                    txt = rlist.pop()
                else:
                    txt = stext
                    tbuffer.delete( dA1, dA2 )
                    dA2 = dA1 #since the text is going to be reread, we dont want to include the last dynamic abbreviation
                    self.getDynamicList( tbuffer, txt, rlist )
                return doDa( txt, dA1, dA2 )
            else:
                dA = None
                
        if not dA:
            self.store[ 'stext' ] = txt
            self.store[ 'rlist' ] = rlist = []
            self.getDynamicList( tbuffer, txt, rlist )
            if not rlist:
                return 'break'
            txt = rlist.pop()
            return doDa( txt )
    #@-node:mork.20041030164547.132:dynamicExpansion
    #@+node:mork.20041030164547.133:dynamicExpansion2
    def dynamicExpansion2( self, event ):
        tbuffer = event.widget
        i = tbuffer.index( 'insert -1c wordstart' )
        i2 = tbuffer.index( 'insert -1c wordend' )
        txt = tbuffer.get( i, i2 )   
        rlist = []
        self.getDynamicList( tbuffer, txt, rlist )
        dEstring = reduce( self.findPre, rlist )
        if dEstring:
            tbuffer.delete( i , i2 )
            tbuffer.insert( i, dEstring )    
            return self._tailEnd( tbuffer )          
    #@-node:mork.20041030164547.133:dynamicExpansion2
    #@+node:mork.20041030164547.134:getDynamicList
    def getDynamicList( self, tbuffer, txt , rlist ):
    
         ttext = tbuffer.get( '1.0', 'end' )
         items = self.dynaregex.findall( ttext ) #make a big list of what we are considering a 'word'
         if items:
             for word in items:
                 if not word.startswith( txt ) or word == txt: continue #dont need words that dont match or == the pattern
                 if word not in rlist:
                     rlist.append( word )
                 else:
                     rlist.remove( word )
                     rlist.append( word )
                     
            
    
    
    #@-node:mork.20041030164547.134:getDynamicList
    #@-others
    #@nonl
    #@-node:mork.20041031181701.2:dynamic abbreviations methods
    #@+node:mork.20041031183018:sort methods
    #@+others
    #@+node:mork.20041030164547.136:sortLines
    def sortLines( self, event , which = None ):
        tbuffer = event.widget  
        if not self._chckSel( event ):
            return self.keyboardQuit( event )
    
        i = tbuffer.index( 'sel.first' )
        i2 = tbuffer.index( 'sel.last' )
        is1 = i.split( '.' )
        is2 = i2.split( '.' )
        txt = tbuffer.get( '%s.0' % is1[ 0 ], '%s.0 lineend' % is2[ 0 ] )
        ins = tbuffer.index( 'insert' )
        txt = txt.split( '\n' )
        tbuffer.delete( '%s.0' % is1[ 0 ], '%s.0 lineend' % is2[ 0 ] )
        txt.sort()
        if which:
            txt.reverse()
        inum = int(is1[ 0 ])
        for z in txt:
            tbuffer.insert( '%s.0' % inum, '%s\n' % z ) 
            inum = inum + 1
        tbuffer.mark_set( 'insert', ins )
        self.keyboardQuit( event )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.136:sortLines
    #@+node:mork.20041030164547.137:sortColumns
    def sortColumns( self, event ):
        tbuffer = event.widget
        if not self._chckSel( event ):
            return self.keyboardQuit( event )
            
        ins = tbuffer.index( 'insert' )
        is1 = tbuffer.index( 'sel.first' )
        is2 = tbuffer.index( 'sel.last' )   
        sint1, sint2 = is1.split( '.' )
        sint2 = int( sint2 )
        sint3, sint4 = is2.split( '.' )
        sint4 = int( sint4 )
        txt = tbuffer.get( '%s.0' % sint1, '%s.0 lineend' % sint3 )
        tbuffer.delete( '%s.0' % sint1, '%s.0 lineend' % sint3 )
        columns = []
        i = int( sint1 )
        i2 = int( sint3 )
        while i <= i2:
            t = tbuffer.get( '%s.%s' %( i, sint2 ), '%s.%s' % ( i, sint4 ) )
            columns.append( t )
            i = i + 1
        txt = txt.split( '\n' )
        zlist = zip( columns, txt )
        zlist.sort()
        i = int( sint1 )      
        for z in xrange( len( zlist ) ):
             tbuffer.insert( '%s.0' % i, '%s\n' % zlist[ z ][ 1 ] ) 
             i = i + 1
        tbuffer.mark_set( 'insert', ins )
        return self._tailEnd( tbuffer ) 
    
    #@-node:mork.20041030164547.137:sortColumns
    #@+node:mork.20041030164547.139:sortFields
    def sortFields( self, event, which = None ):
        tbuffer = event.widget
        if not self._chckSel( event ):
            return self.keyboardQuit( event )
    
        ins = tbuffer.index( 'insert' )
        is1 = tbuffer.index( 'sel.first' )
        is2 = tbuffer.index( 'sel.last' )
        
        txt = tbuffer.get( '%s linestart' % is1, '%s lineend' % is2 )
        txt = txt.split( '\n' )
        fields = []
        import re
        fn = r'\w+'
        frx = re.compile( fn )
        for z in txt:
            f = frx.findall( z )
            if not which:
                fields.append( f[ 0 ] )
            else:
                i =  int( which )
                if len( f ) < i:
                    return self._tailEnd( tbuffer )
                i = i - 1            
                fields.append( f[ i ] )
        nz = zip( fields, txt )
        nz.sort()
        tbuffer.delete( '%s linestart' % is1, '%s lineend' % is2 )
        i = is1.split( '.' )
        #i2 = is2.split( '.' )
        int1 = int( i[ 0 ] )
        for z in nz:
            tbuffer.insert( '%s.0' % int1, '%s\n'% z[1] )
            int1 = int1 + 1
        tbuffer.mark_set( 'insert' , ins )
        return self._tailEnd( tbuffer )
    
    #@-node:mork.20041030164547.139:sortFields
    #@-others
    #@nonl
    #@-node:mork.20041031183018:sort methods
    #@+node:mork.20041031181929.1:Alt_X methods
    #@+at
    # These methods control the Alt-x command functionality.
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041030164547.140:alt_X
    #self.altx = False
    def alt_X( self, event , which = None):
        #global altx
        if which:
            self.mcStateManager.setState( 'altx', which )
        else:
            self.mcStateManager.setState( 'altx', 'True' )
    
        svar, label = self.getSvarLabel( event )
        if which:
            svar.set( '%s M-x:' % which )
        else:
            svar.set( 'M-x:' )
        self.setLabelBlue( label )
        return 'break'
    #@-node:mork.20041030164547.140:alt_X
    #@+node:mork.20041030164547.141:doAlt_X
    def doAlt_X( self, event ):
        '''This method executes the correct Alt-X command'''
        svar, label = self.getSvarLabel( event )
        if svar.get().endswith( 'M-x:' ): 
            self.axTabList.clear() #clear the list, new Alt-x command is in effect
            svar.set( '' )
        if event.keysym == 'Return':
            txt = svar.get()
            if self.doAltX.has_key( txt ):
                if txt != 'repeat-complex-command':
                    self.altx_history.reverse()
                    self.altx_history.append( txt )
                    self.altx_history.reverse()
                aX = self.mcStateManager.getState( 'altx' )
                if aX.isdigit() and txt in self.x_hasNumeric:
                    self.doAltX[ txt]( event, aX )
                else:
                    self.doAltX[ txt ]( event )
            else:
                self.keyboardQuit( event )
                svar.set('Command does not exist' )
    
            #self.altx = False
            #self.mcStateManager.setState( 'altx', False )
            return 'break'
        if event.keysym == 'Tab':
            
            stext = svar.get().strip()
            if self.axTabList.prefix and stext.startswith( self.axTabList.prefix ):
                svar.set( self.axTabList.next() ) #get next in iteration
            else:
                prefix = svar.get()
                pmatches = self._findMatch2( svar )
                self.axTabList.setTabList( prefix, pmatches )
                svar.set( self.axTabList.next() ) #begin iteration on new lsit
            return 'break'   
        else:
            self.axTabList.clear() #clear the list, any other character besides tab indicates that a new prefix is in effect.    
        self.setSvar( event, svar )
        return 'break'
    #@-node:mork.20041030164547.141:doAlt_X
    #@+node:mork.20041123093234:execute last altx methods
    #@+others
    #@+node:mork.20041122223754:executeLastAltX
    def executeLastAltX( self, event ):
        
        if event.keysym == 'Return' and self.altx_history:
            last = self.altx_history[ 0 ]
            self.doAltX[ last ]( event )
            return 'break'
        else:
            return self.keyboardQuit( event )
    #@-node:mork.20041122223754:executeLastAltX
    #@+node:mork.20041122225107:repeatComplexCommand
    def repeatComplexCommand( self, event ):
    
        self.keyboardQuit( event )
        if self.altx_history:
            svar, label = self.getSvarLabel( event )
            self.setLabelBlue( label )
            svar.set( "Redo: %s" % self.altx_history[ 0 ] )
            self.mcStateManager.setState( 'last-altx', True )
        return 'break'
    #@-node:mork.20041122225107:repeatComplexCommand
    #@-others
    #@nonl
    #@-node:mork.20041123093234:execute last altx methods
    #@-others
    #@nonl
    #@-node:mork.20041031181929.1:Alt_X methods
    #@+node:mork.20041031155455:universal methods
    #@+others
    #@+node:mork.20041030164547.143:universalDispatch
    #self.uC = False
    def universalDispatch( self, event, stroke ):
        #global uC    
        uC = self.mcStateManager.getState( 'uC' )
        if not uC:
            #self.uC = 1
            self.mcStateManager.setState( 'uC', 1 )
            svar, label = self.getSvarLabel( event )
            svar.set( '' )
            self.setLabelBlue( label ) 
        elif uC == 1:
            self.universalCommand1( event, stroke )
        elif uC == 2:
            self.universalCommand3( event, stroke )
        return 'break'
    #@-node:mork.20041030164547.143:universalDispatch
    #@+node:mork.20041030164547.144:universalCommand1
    #import string
    #self.uCstring = string.digits + '\b'
    
    def universalCommand1( self, event, stroke ):
        #global uC
        if event.char not in self.uCstring:
            return self.universalCommand2( event, stroke )
        svar, label = self.getSvarLabel( event )
        self.setSvar( event, svar )
        if event.char != '\b':
            svar.set( '%s ' %svar.get() )
    #@-node:mork.20041030164547.144:universalCommand1
    #@+node:mork.20041030164547.145:universalCommand2
    def universalCommand2(  self, event , stroke ):
        #global uC
        #self.uC = False
        #self.mcStateManager.setState( 'uC', False )
        svar, label = self.getSvarLabel( event )
        txt = svar.get()
        self.keyboardQuit( event )
        txt = txt.replace( ' ', '' )
        self.resetMiniBuffer( event )
        if not txt.isdigit(): #This takes us to macro state.  For example Control-u Control-x (  will execute the last macro and begin editing of it.
            if stroke == '<Control-x>':
                #self.uC = 2
                self.mcStateManager.setState( 'uC', 2 )
                return self.universalCommand3( event, stroke )
            return self._tailEnd( event.widget )
        if self.uCdict.has_key( stroke ): #This executes the keystroke 'n' number of times.
                self.uCdict[ stroke ]( event , txt )
        else:
            tbuffer = event.widget
            i = int( txt )
            stroke = stroke.lstrip( '<' ).rstrip( '>' )
            if self.cbDict.has_key( stroke ):
                for z in xrange( i ):
                    method = self.cbDict[ stroke ]
                    ev = Tkinter.Event()
                    ev.widget = event.widget
                    ev.keysym = event.keysym
                    ev.keycode = event.keycode
                    ev.char = event.char
                    self.masterCommand( ev , method, '<%s>' % stroke )
            else:
                for z in xrange( i ):
                    tbuffer.event_generate( '<Key>', keycode = event.keycode, keysym = event.keysym )
                    self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.145:universalCommand2
    #@+node:mork.20041030164547.146:universalCommand3
    #self.uCdict = { '<Alt-x>' : alt_X }
    def universalCommand3( self, event, stroke ):
        svar, label = self.getSvarLabel( event )
        svar.set( 'Control-u %s' % stroke.lstrip( '<' ).rstrip( '>' ) )
        self.setLabelBlue( label )
        if event.keysym == 'parenleft':
            self.keyboardQuit( event )
            self.startKBDMacro( event )
            self.executeLastMacro( event )
            return 'break'
    #@-node:mork.20041030164547.146:universalCommand3
    #@+node:mork.20041030164547.147:numberCommand
    def numberCommand( self, event, stroke, number ):
        self.universalDispatch( event, stroke )
        tbuffer = event.widget
        tbuffer.event_generate( '<Key>', keysym = number )
        return 'break'       
    #@-node:mork.20041030164547.147:numberCommand
    #@-others
    #@nonl
    #@-node:mork.20041031155455:universal methods
    #@+node:mork.20041121201041:line methods
    #@+at
    # 
    # flush-lines
    # Delete each line that contains a match for regexp, operating on the text 
    # after point. In Transient Mark mode, if the region is active, the 
    # command operates on the region instead.
    # 
    # 
    # keep-lines
    # Delete each line that does not contain a match for regexp, operating on 
    # the text after point. In Transient Mark mode, if the region is active, 
    # the command operates on the region instead.
    # 
    #@-at
    #@@c
    
    #@+others
    #@+node:mork.20041121201041.1:alterLines
    def alterLines( self, event, which ):
        
        tbuffer = event.widget
        i = tbuffer.index( 'insert' )
        end = 'end'
        if tbuffer.tag_ranges( 'sel' ):
            i = tbuffer.index( 'sel.first' )
            end = tbuffer.index( 'sel.last' )
            
        txt = tbuffer.get( i, end )
        tlines = txt.splitlines( True )
        if which == 'flush':
            keeplines = list( tlines )
        else:
            keeplines = []
        svar, label = self.getSvarLabel( event )
        pattern = svar.get()
        try:
            regex = re.compile( pattern )
            for n , z in enumerate( tlines ):
                f = regex.findall( z )
                if which == 'flush' and f:
                    keeplines[ n ] = None
                elif f:
                    keeplines.append( z )
        except Exception,x:
            return
        
        if which == 'flush':
            keeplines = [ x for x in keeplines if x != None ]
        tbuffer.delete( i, end )
        tbuffer.insert( i, ''.join( keeplines ) )
        tbuffer.mark_set( 'insert', i )
        self._tailEnd( tbuffer )
            
        
    
    
    
    #@-node:mork.20041121201041.1:alterLines
    #@+node:mork.20041121210221:processLines
    def processLines( self, event ):
        svar, label = self.getSvarLabel( event )
    
        state = self.mcStateManager.getState( 'alterlines' )
        if state.startswith( 'start' ):
            state = state[ 5: ]
            self.mcStateManager.setState( 'alterlines', state )
            svar.set( '' )
           
    
            
        if event.keysym == 'Return':
           
            self.alterLines( event, state )
                
            return self.keyboardQuit( event )    
            
            
        else:
            self.setSvar( event, svar )
            return 'break'
    #@nonl
    #@-node:mork.20041121210221:processLines
    #@+node:mork.20041121201112:startLines
    def startLines( self , event, which = 'flush' ):
    
        self.keyboardQuit( event )
        tbuffer = event.widget
        self.mcStateManager.setState( 'alterlines', 'start%s' % which )
        svar, label = self.getSvarLabel( event )
        label.configure( background = 'lightblue' )
        return 'break'
        
    #@-node:mork.20041121201112:startLines
    #@-others
    #@nonl
    #@-node:mork.20041121201041:line methods
    #@+node:mork.20041031160002:goto methods
    #@+at
    # These methods take the user to a specific line or a specific character 
    # in the buffer
    # 
    # 
    #@-at
    #@@c
    
    #@+others
    #@+node:mork.20041030164547.154:startGoto
    def startGoto( self, event , ch = False):
        #global goto
        #self.goto = True
        if not ch:
            self.mcStateManager.setState( 'goto', 1 )
        else:
            self.mcStateManager.setState( 'goto', 2 )
        #label = self.mbuffers[ event.widget ] 
        svar , label = self.getSvarLabel( event )
        svar.set( '' )
        label.configure( background = 'lightblue' )
        return 'break'
    #@-node:mork.20041030164547.154:startGoto
    #@+node:mork.20041030164547.155:Goto
    def Goto( self, event ):
        #global goto
        widget = event.widget
        svar, label = self.getSvarLabel( event )
        if event.keysym == 'Return':
              i = svar.get()
              self.resetMiniBuffer( event )
              #self.goto = False
              state = self.mcStateManager.getState( 'goto' )
              self.mcStateManager.setState( 'goto', False )
              if i.isdigit():
                  
                  if state == 1:
                    widget.mark_set( 'insert', '%s.0' % i )
                  elif state == 2:
                    widget.mark_set( 'insert', '1.0 +%sc' % i )
                  widget.event_generate( '<Key>' )
                  widget.update_idletasks()
                  widget.see( 'insert' )
              return 'break'
        t = svar.get()
        if event.char == '\b':
               if len( t ) == 1:
                   t = ''
               else:
                   t = t[ 0 : -1 ]
               svar.set( t )
        else:
                t = t + event.char
                svar.set( t )
        return 'break'
    #@-node:mork.20041030164547.155:Goto
    #@-others
    #@nonl
    #@-node:mork.20041031160002:goto methods
    #@+node:mork.20041122110739:directory methods
    #@+others
    #@+node:mork.20041122110739.1:makeDirectory
    def makeDirectory( self, event ):
        
        svar,label = self.getSvarLabel( event )
        state = self.mcStateManager.getState( 'make_directory' )
        if not state:
            self.mcStateManager.setState( 'make_directory', True )
            self.setLabelBlue( label )
            directory = os.getcwd()
            svar.set( '%s%s' %( directory, os.sep ) )
            return 'break'
        
        if event.keysym == 'Return':
            
            ndirectory = svar.get()
            self.keyboardQuit( event )
            try:
                os.mkdir( ndirectory )
            except:
                svar.set( "Could not make %s%" % ndirectory  )
            return 'break'
        else:
            self.setSvar( event, svar )
            return 'break'
    #@nonl
    #@-node:mork.20041122110739.1:makeDirectory
    #@+node:mork.20041122111431:removeDirectory
    def removeDirectory( self, event ):
        
        svar,label = self.getSvarLabel( event )
        state = self.mcStateManager.getState( 'remove_directory' )
        if not state:
            self.mcStateManager.setState( 'remove_directory', True )
            self.setLabelBlue( label )
            directory = os.getcwd()
            svar.set( '%s%s' %( directory, os.sep ) )
            return 'break'
        
        if event.keysym == 'Return':
            
            ndirectory = svar.get()
            self.keyboardQuit( event )
            try:
                os.rmdir( ndirectory )
            except:
                svar.set( "Could not remove %s%" % ndirectory  )
            return 'break'
        else:
            self.setSvar( event, svar )
            return 'break'
    #@nonl
    #@-node:mork.20041122111431:removeDirectory
    #@-others
    #@nonl
    #@-node:mork.20041122110739:directory methods
    #@+node:mork.20041031182449:file methods
    #@+at
    # These methods load files into buffers and save buffers to files
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041122112210:deleteFile
    def deleteFile( self, event ):
    
        svar,label = self.getSvarLabel( event )
        state = self.mcStateManager.getState( 'delete_file' )
        if not state:
            self.mcStateManager.setState( 'delete_file', True )
            self.setLabelBlue( label )
            directory = os.getcwd()
            svar.set( '%s%s' %( directory, os.sep ) )
            return 'break'
        
        if event.keysym == 'Return':
            
            dfile = svar.get()
            self.keyboardQuit( event )
            try:
                os.remove( dfile )
            except:
                svar.set( "Could not delete %s%" % dfile  )
            return 'break'
        else:
            self.setSvar( event, svar )
            return 'break'
    #@-node:mork.20041122112210:deleteFile
    #@+node:mork.20041030164547.151:insertFile
    def insertFile( self, event ):
        tbuffer = event.widget
        f, name = self.getReadableTextFile()
        if not f: return None
        txt = f.read()
        f.close()
        tbuffer.insert( 'insert', txt )
        return self._tailEnd( tbuffer )
    #@-node:mork.20041030164547.151:insertFile
    #@+node:mork.20041030164547.152:saveFile
    def saveFile( self, event ):
        tbuffer = event.widget
        import tkFileDialog
        txt = tbuffer.get( '1.0', 'end' )
        f = tkFileDialog.asksaveasfile()
        if f == None : return None
        f.write( txt )
        f.close()
    #@-node:mork.20041030164547.152:saveFile
    #@+node:mork.20041121140620.2:getReadableFile
    def getReadableTextFile( self ):
        
        import tkFileDialog
        fname = tkFileDialog.askopenfilename()
        if fname == None: return None, None
        f = open( fname, 'rt' )
        return f, fname
    #@-node:mork.20041121140620.2:getReadableFile
    #@-others
    #@nonl
    #@-node:mork.20041031182449:file methods
    #@+node:mork.20041123192555:Esc methods for Python evaluation
    #@+others
    #@+node:mork.20041123192555.1:watchEscape
    def watchEscape( self, event ):
        
        svar, label = self.getSvarLabel( event )
        if not self.mcStateManager.hasState():
            self.mcStateManager.setState( 'escape' , 'start' )
            self.setLabelBlue( label )
            svar.set( 'Esc' )
            return 'break'
        if self.mcStateManager.whichState() == 'escape':
            
            state = self.mcStateManager.getState( 'escape' )
            hi1 = self.keysymhistory[ 0 ]
            hi2 = self.keysymhistory[ 1 ]
            if state == 'esc esc' and event.keysym == 'colon':
                return self.startEvaluate( event )
            elif state == 'evaluate':
                return self.escEvaluate( event )    
            elif hi1 == hi2 == 'Escape':
                self.mcStateManager.setState( 'escape', 'esc esc' )
                svar.set( 'Esc Esc -' )
                return 'break'
            elif event.keysym in ( 'Shift_L', 'Shift_R' ):
                return
            else:
                return self.keyboardQuit( event )
        
    
    
    #@-node:mork.20041123192555.1:watchEscape
    #@+node:mork.20041124095452:escEvaluate
    def escEvaluate( self, event ):
        
        svar, label = self.getSvarLabel( event )
        if svar.get() == 'Eval:':
            svar.set( '' )
        
        if event.keysym =='Return':
        
            expression = svar.get()
            try:
                ok = False
                tbuffer = event.widget
                result = eval( expression, {}, {} )
                result = str( result )
                tbuffer.insert( 'insert', result )
                ok = True
            finally:
                self.keyboardQuit( event )
                if not ok:
                    svar.set( 'Error: Invalid Expression' )
                return self._tailEnd( tbuffer )
            
            
        else:
            
            self.setSvar( event, svar )
            return 'break'
        
    #@-node:mork.20041124095452:escEvaluate
    #@+node:mork.20041124102729:startEvaluate
    def startEvaluate( self, event ):
        
        svar, label = self.getSvarLabel( event )
        self.setLabelBlue( label )
        svar.set( 'Eval:' )
        self.mcStateManager.setState( 'escape', 'evaluate' )
        return 'break'
    #@-node:mork.20041124102729:startEvaluate
    #@-others
    #@nonl
    #@-node:mork.20041123192555:Esc methods for Python evaluation
    #@+node:mork.20041124123825:tabify/untabify
    #@+at
    # For the tabify and untabify Alt-x commands.  Turns tabs to spaces and 
    # spaces to tabs in the selection
    # 
    #@-at
    #@@c
    
    
    #@+others
    #@+node:mork.20041124123825.1:tabify
    def tabify( self, event, which='tabify' ):
        
        tbuffer = event.widget
        if tbuffer.tag_ranges( 'sel' ):
            i = tbuffer.index( 'sel.first' )
            end = tbuffer.index( 'sel.last' )
            txt = tbuffer.get( i, end )
            if which == 'tabify':
                
                pattern = re.compile( ' {4,4}' )
                ntxt = pattern.sub( '\t', txt )
    
            else:
                
                pattern = re.compile( '\t' )
                ntxt = pattern.sub( '    ', txt )
            tbuffer.delete( i, end )
            tbuffer.insert( i , ntxt )
            self.keyboardQuit( event )
            return self._tailEnd( tbuffer )
        self.keyboardQuit( event )
    
    #@-node:mork.20041124123825.1:tabify
    #@-others
    #@nonl
    #@-node:mork.20041124123825:tabify/untabify
    #@+node:mork.20041208120232:shell and subprocess
    #@+others
    #@+node:mork.20041208120232.1:def startSubprocess
    def startSubprocess( self, event, which = 0 ):
        
        svar, label = self.getSvarLabel( event )
        statecontents = { 'state':'start', 'payload': None }
        self.mcStateManager.setState( 'subprocess', statecontents )
        if which:
            tbuffer = event.widget
            svar.set( "Shell command on region:" )
            is1 = is2 = None
            try:
                is1 = tbuffer.index( 'sel.first' )
                is2 = tbuffer.index( 'sel.last' )
            finally:
                if is1:
                    statecontents[ 'payload' ] = tbuffer.get( is1, is2 )
                else:
                    return self.keyboardQuit( event )
        else:
            svar.set( "Alt - !:" )
        self.setLabelBlue( label )
        return 'break'    
    #@-node:mork.20041208120232.1:def startSubprocess
    #@+node:mork.20041208120232.2:subprocess
    def subprocesser( self, event ):
        
        state = self.mcStateManager.getState( 'subprocess' )
        svar, label = self.getSvarLabel( event )
        if state[ 'state' ] == 'start':
            state[ 'state' ] = 'watching'
            svar.set( "" )
        
        if event.keysym == "Return":
            #cmdline = svar.get().split()
            cmdline = svar.get()
            return self.executeSubprocess( event, cmdline, input=state[ 'payload' ] )
           
        else:
            self.setSvar(  event, svar )
            return 'break'
    #@-node:mork.20041208120232.2:subprocess
    #@+node:mork.20041208121502:executeSubprocess
    def executeSubprocess( self, event, command  ,input = None ):
        import subprocess
        try:
            try:
                out ,err = os.tmpnam(), os.tmpnam()
                ofile = open( out, 'wt+' ) 
                efile = open( err, 'wt+' )
                process = subprocess.Popen( command, bufsize=-1, 
                                            stdout = ofile.fileno(), 
                                            stderr= ofile.fileno(), 
                                            stdin=subprocess.PIPE,
                                            shell=True )
                if input:
                    process.communicate( input )
                process.wait()   
                tbuffer = event.widget
                efile.seek( 0 )
                errinfo = efile.read()
                if errinfo:
                    tbuffer.insert( 'insert', errinfo )
                ofile.seek( 0 )
                okout = ofile.read()
                if okout:
                    tbuffer.insert( 'insert', okout )
            except Exception, x:
                tbuffer = event.widget
                tbuffer.insert( 'insert', x )
        finally:
            os.remove( out )
            os.remove( err )
        self.keyboardQuit( event )
        return self._tailEnd( tbuffer )
    
    
    
    #@-node:mork.20041208121502:executeSubprocess
    #@-others
    #@nonl
    #@-node:mork.20041208120232:shell and subprocess
    #@-others
#@nonl
#@-node:mork.20041030165020:class Emacs
#@-others

if __name__ == '__main__':
    #@    << run standalone tests >>
    #@+node:ekr.20041106100834:<< run standalone tests >>
    #@+at
    # This part runs Temacs with a Text widget.
    # It should be accessible by typing python temacs.py at the command prompt
    # Note: There is no configuration as to buffers and such, so dont access 
    # that functionality.  Just a proof of concept.
    # 
    #@-at
    #@@c
    
    Tl = Tkinter.Tk()
    Tl.title( 'temacs Emacs test' )
    Tx = Tkinter.Text( background = 'white', foreground = 'blue' )
    f2 = Tkinter.Frame()
    f2.pack( side = 'bottom' )
    def onQuit():
        import sys
        sys.exit( 0 )
        
    minibuffer = Tkinter.Label( f2 )
    minibuffer.pack( side = 'right', expand = 1, fill = 'both' )
    quitb = Tkinter.Button( f2, text = 'Quit' , command = onQuit )
    quitb.pack( side = 'left' )
    Tx.pack( side = 'top' )
    emacs = Emacs( Tx, minibuffer, True, True )
    Tl.mainloop()
    #@nonl
    #@-node:ekr.20041106100834:<< run standalone tests >>
    #@nl
#@nonl
#@-node:mork.20041030164547:@thin temacs.py
#@-leo
