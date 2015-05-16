# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040234.1: * @file ../commands/registerCommands.py
#@@first
'''Leo's register commands.'''
#@+<< imports >>
#@+node:ekr.20150514050501.1: ** << imports >> (registerCommands.py)
import leo.core.leoGlobals as g

from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@-<< imports >>

def cmd(name):
    '''Command decorator for the RegisterCommandsClass class.'''
    return g.new_cmd_decorator(name,['c','registerCommands',])

class RegisterCommandsClass (BaseEditCommandsClass):
    '''Create registers a-z and the corresponding Emacs commands.'''
    #@+others
    #@+node:ekr.20150514063305.463: ** register.ctor
    def __init__ (self,c):
        '''Ctor for RegisterCommandsClass class.'''
        self.c = c
        self.methodDict, self.helpDict = self.addRegisterItems()
        # Init these here to keep pylint happy.
        self.method = None 
        self.registerMode = 0 # Must be an int.
        self.registers = g.app.globalRegisters
    #@+node:ekr.20150514063305.465: ** register.addRegisterItems
    def addRegisterItems( self ):

        methodDict = {
            '+':        self.incrementRegister,
            ' ':        self.pointToRegister,
            'a':        self.appendToRegister,
            'i':        self.insertRegister,
            'j':        self.jumpToRegister,
            # 'n':        self.numberToRegister,
            'p':        self.prependToRegister,
            'r':        self.copyRectangleToRegister,
            's':        self.copyToRegister,
            'v' :       self.viewRegister,
        }    
        helpDict = {
            's':    'copy to register',
            'i':    'insert from register',
            '+':    'increment register',
            'n':    'number to register',
            'p':    'prepend to register',
            'a':    'append to register',
            ' ':    'point to register',
            'j':    'jump to register',
            'r':    'rectangle to register',
            'v':    'view register',
        }
        return methodDict, helpDict
    #@+node:ekr.20150514063305.466: ** register.checkBodySelection
    def checkBodySelection (self,warning='No text selected'):

        return self._chckSel(event=None,warning=warning)
    #@+node:ekr.20150514063305.467: ** register.Entries
    #@+node:ekr.20150514063305.468: *3* appendToRegister
    @cmd('register-append-to')
    def appendToRegister (self,event):
        '''Prompt for a register name and append the selected text to the register's contents.'''
        c,k = self.c,self.c.k
        tag = 'append-to-register'
        state = k.getState(tag)
        char = event and event.char or ''
        if state == 0:
            k.commandName = tag
            k.setLabelBlue('Append to Register: ')
            k.setState(tag,1,self.appendToRegister)
        else:
            k.clearState()
            if self.checkBodySelection():
                if char.isalpha():
                    w = c.frame.body.wrapper
                    c.bodyWantsFocus()
                    key = char.lower()
                    val = self.registers.get(key,'')
                    val = val + w.getSelectedText()
                    self.registers[key] = val
                    k.setLabelGrey('Register %s = %s' % (key,repr(val)))
                else:
                    k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20150514063305.469: *3* prependToRegister
    @cmd('register-prepend-to')
    def prependToRegister (self,event):
        '''Prompt for a register name and prepend the selected text to the register's contents.'''
        c,k = self.c,self.c.k
        tag = 'prepend-to-register'
        state = k.getState(tag)
        char = event and event.char or ''
        if state == 0:
            k.commandName = tag
            k.setLabelBlue('Prepend to Register: ')
            k.setState(tag,1,self.prependToRegister)
        else:
            k.clearState()
            if self.checkBodySelection():
                if char.isalpha():
                    w = c.frame.body.wrapper
                    c.bodyWantsFocus()
                    key = char.lower()
                    val = self.registers.get(key,'')
                    val = w.getSelectedText() + val
                    self.registers[key] = val
                    k.setLabelGrey('Register %s = %s' % (key,repr(val)))
                else:
                    k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20150514063305.470: *3* copyRectangleToRegister
    @cmd('register-copy-rectangle-to')
    def copyRectangleToRegister (self,event):
        '''
        Prompt for a register name and append the rectangle defined by selected
        text to the register's contents.
        '''
        c,k = self.c,self.c.k
        state = k.getState('copy-rect-to-reg')
        char = event and event.char or ''
        if state == 0:
            self.w = self.editWidget(event)
            if self.w:
                k.commandName = 'copy-rectangle-to-register'
                k.setLabelBlue('Copy Rectangle To Register: ')
                k.setState('copy-rect-to-reg',1,self.copyRectangleToRegister)
        elif self.checkBodySelection('No rectangle selected'):
            k.clearState()
            if char.isalpha():
                key = char.lower()
                w = self.w
                c.widgetWantsFocusNow(w)
                r1, r2, r3, r4 = self.getRectanglePoints(w)
                rect = []
                while r1 <= r3:
                    txt = w.get('%s.%s' % (r1,r2),'%s.%s' % (r1,r4))
                    rect.append(txt)
                    r1 = r1 + 1
                self.registers [key] = rect
                k.setLabelGrey('Register %s = %s' % (key,repr(rect)))
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20150514063305.471: *3* copyToRegister
    @cmd('register-copy-to')
    def copyToRegister (self,event):
        '''Prompt for a register name and append the selected text to the register's contents.'''
        c,k = self.c,self.c.k
        tag = 'copy-to-register'
        state = k.getState(tag)
        char = event and event.char or ''
        if state == 0:
            k.commandName = tag
            k.setLabelBlue('Copy to Register: ')
            k.setState(tag,1,self.copyToRegister)
        else:
            k.clearState()
            if self.checkBodySelection():
                if char.isalpha():
                    key = char.lower()
                    w = c.frame.body.wrapper
                    c.bodyWantsFocus()
                    val = w.getSelectedText()
                    self.registers[key] = val
                    k.setLabelGrey('Register %s = %s' % (key,repr(val)))
                else:
                    k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20150514063305.472: *3* incrementRegister
    @cmd('register-increment')
    def incrementRegister (self,event):
        '''Prompt for a register name and increment its value if it has a numeric value.'''
        c,k = self.c,self.c.k
        state = k.getState('increment-reg')
        char = event and event.char or ''
        if state == 0:
            k.setLabelBlue('Increment register: ')
            k.setState('increment-reg',1,self.incrementRegister)
        else:
            k.clearState()
            if self.checkIfRectangle(event):
                pass # Error message is in the label.
            elif char.isalpha():
                key = char.lower()
                val = self.registers.get(key,0)
                try:
                    val = str(int(val)+1)
                    self.registers[key] = val
                    k.setLabelGrey('Register %s = %s' % (key,repr(val)))
                except ValueError:
                    k.setLabelGrey("Can't increment register %s = %s" % (key,val))
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20150514063305.473: *3* insertRegister
    @cmd('register-insert')
    def insertRegister (self,event):
        '''Prompt for a register name and and insert the value of another register into its contents.'''
        c,k = self.c,self.c.k
        state = k.getState('insert-reg')
        char = event and event.char or ''
        if state == 0:
            k.commandName = 'insert-register'
            k.setLabelBlue('Insert register: ')
            k.setState('insert-reg',1,self.insertRegister)
        else:
            k.clearState()
            if char.isalpha():
                w = c.frame.body.wrapper
                c.bodyWantsFocus()
                key = char.lower()
                val = self.registers.get(key)
                if val:
                    if type(val)==type([]):
                        c.rectangleCommands.yankRectangle(val)
                    else:
                        i = w.getInsertPoint()
                        w.insert(i,val)
                    k.setLabelGrey('Inserted register %s' % key)
                else:
                    k.setLabelGrey('Register %s is empty' % key)
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20150514063305.474: *3* jumpToRegister
    @cmd('register-jump-to')
    def jumpToRegister (self,event):
        '''Prompt for a register name and set the insert point to the value in its register.'''
        c,k = self.c,self.c.k
        state = k.getState('jump-to-reg')
        char = event and event.char or ''
        if state == 0:
            k.setLabelBlue('Jump to register: ')
            k.setState('jump-to-reg',1,self.jumpToRegister)
        else:
            k.clearState()
            if char.isalpha():
                if self.checkIfRectangle(event): return
                key = char.lower()
                val = self.registers.get(key)
                w = c.frame.body.wrapper
                c.bodyWantsFocus()
                if val:
                    try:
                        w.setInsertPoint(val)
                        k.setLabelGrey('At %s' % repr(val))
                    except Exception:
                        k.setLabelGrey('Register %s is not a valid location' % key)
                else:
                    k.setLabelGrey('Register %s is empty' % key)
        c.bodyWantsFocus()
    #@+node:ekr.20150514063305.475: *3* numberToRegister (not used)
    #@+at
    # C-u number C-x r n reg
    #     Store number into register reg (number-to-register).
    # C-u number C-x r + reg
    #     Increment the number in register reg by number (increment-register).
    # C-x r g reg
    #     Insert the number from register reg into the buffer.
    #@@c

    def numberToRegister (self,event):

        c,k = self.c,self.c.k
        state = k.getState('number-to-reg')
        char = event and event.char or ''
        if state == 0:
            k.commandName = 'number-to-register'
            k.setLabelBlue('Number to register: ')
            k.setState('number-to-reg',1,self.numberToRegister)
        else:
            k.clearState()
            if char.isalpha():
                # self.registers[char.lower()] = str(0)
                k.setLabelGrey('number-to-register not ready yet.')
            else:
                k.setLabelGrey('Register must be a letter')
    #@+node:ekr.20150514063305.476: *3* pointToRegister
    @cmd('register-point-to')
    def pointToRegister (self,event):
        '''Prompt for a register name and put a value indicating the insert point in the register.'''
        c,k = self.c,self.c.k
        state = k.getState('point-to-reg')
        char = event and event.char or ''
        if state == 0:
            k.commandName = 'point-to-register'
            k.setLabelBlue('Point to register: ')
            k.setState('point-to-reg',1,self.pointToRegister)
        else:
            k.clearState()
            if char.isalpha():
                w = c.frame.body.wrapper
                c.bodyWantsFocus()
                key = char.lower()
                val = w.getInsertPoint()
                self.registers[key] = val
                k.setLabelGrey('Register %s = %s' % (key,repr(val)))
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20150514063305.477: *3* viewRegister
    @cmd('register-view')
    def viewRegister (self,event):
        '''Prompt for a register name and print its contents.'''
        c,k = self.c,self.c.k
        state = k.getState('view-reg')
        char = event and event.char or ''
        if state == 0:
            k.commandName = 'view-register'
            k.setLabelBlue('View register: ')
            k.setState('view-reg',1,self.viewRegister)
        else:
            k.clearState()
            if char.isalpha():
                key = char.lower()
                val = self.registers.get(key)
                k.setLabelGrey('Register %s = %s' % (key,repr(val)))
            else:
                k.setLabelGrey('Register must be a letter')
        c.bodyWantsFocus()
    #@+node:ekr.20150514043714.12: ** register.checkIfRectangle
    def checkIfRectangle (self,event):

        c,k = self.c,self.c.k
        key = event and event.char.lower() or ''
        val = self.registers.get(key)
        if val and type(val) == type([]):
            k.clearState()
            k.setLabelGrey("Register contains Rectangle, not text")
            return True
        else:
            return False
    #@-others
#@-leo
