# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514040144.1: * @file ../commands/macroCommands.py
#@@first
'''Leo's macros commands.'''
#@+<< imports >>
#@+node:ekr.20150514050425.1: ** << imports >> (macroCommands.py)
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@-<< imports >>

def cmd(name):
    '''Command decorator for the MacroCommandsClass class.'''
    return g.new_cmd_decorator(name, ['c', 'macroCommands',])

#@+others
#@+node:ekr.20160514120837.1: ** class MacroCommandsClass
class MacroCommandsClass(BaseEditCommandsClass):
    '''Records, plays, saves and restores keyboard macros.'''
    #@+others
    #@+node:ekr.20150514063305.432: *3* macro.ctor
    def __init__(self, c):
        '''Ctor for MacroCommandsClass class.'''
        # pylint: disable=super-init-not-called
        self.c = c
        self.lastMacro = None
        self.macros = []
        self.macro = []
        self.namedMacros = {}
        # Important: we must not interfere with k.state in startRecordingMacro!
        self.recordingMacro = False
    #@+node:ekr.20150514063305.434: *3* callLastMacro
    # Called from universal-command.

    @cmd('macro-call-last')
    def callLastMacro(self, event=None):
        '''Call the last recorded keyboard macro.'''
        # g.trace(self.lastMacro)
        if self.lastMacro:
            self.executeMacro(self.lastMacro)
    #@+node:ekr.20150514063305.435: *3* callNamedMacro
    @cmd('macro-call')
    def callNamedMacro(self, event):
        '''Prompts for a macro name, then executes it.'''
        k = self.c.k
        tag = 'macro-name'
        state = k.getState(tag)
        prompt = 'Call macro named: '
        if state == 0:
            k.setLabelBlue(prompt)
            k.getArg(event, tag, 1, self.callNamedMacro)
        else:
            macro = self.namedMacros.get(k.arg)
            # Must do this first!
            k.clearState()
            if macro:
                self.executeMacro(macro)
            else:
                g.es('no macro named %s' % k.arg)
            k.resetLabel()
    #@+node:ekr.20150514063305.436: *3* completeMacroDef
    def completeMacroDef(self, name, macro):
        '''
        Add the macro to the list of macros, and add the macro's name to
        c.commandsDict.
        '''
        # Called from loadFile and nameLastMacro.
        trace = False and not g.unitTesting
        c, k = self.c, self.c.k
        if trace:
            g.trace('macro::%s' % (name))
            for event in macro:
                g.trace(event.stroke)

        def func(event, macro=macro):
            return self.executeMacro(macro)

        if name in c.commandsDict:
            g.es_print('over-riding command: %s' % (name))
        else:
            g.es_print('loaded: %s' % (name))
        c.commandsDict[name] = func
        self.namedMacros[name] = macro
    #@+node:ekr.20150514063305.437: *3* endMacro
    @cmd('macro-end-recording')
    def endMacro(self, event=None):
        '''Stops recording a macro.'''
        k = self.c.k
        self.recordingMacro = False
            # Tell k.masterKeyHandler and k.masterCommandHandler we are done.
        if self.macro:
            # self.macro = self.macro [: -4]
            self.macros.insert(0, self.macro)
            self.lastMacro = self.macro[:]
            self.macro = []
            k.setLabelBlue('Keyboard macro defined, not named')
            # g.es('Keyboard macro defined, not named')
        else:
            k.setLabelBlue('Empty keyboard macro')
            # g.es('Empty keyboard macro')
    #@+node:ekr.20150514063305.438: *3* executeMacro
    def executeMacro(self, macro):
        trace = False and not g.unitTesting
        c, k = self.c, self.c.k
        c.bodyWantsFocus()
        for event in macro:
            if trace: g.trace(repr(event))
            k.masterKeyHandler(event)
    #@+node:ekr.20150514063305.439: *3* getMacrosNode
    def getMacrosNode(self):
        '''Return the position of the @macros node.'''
        c = self.c
        for p in c.all_unique_positions():
            if p.h == '@macros':
                return p
        # Not found.
        for p in c.all_unique_positions():
            if p.h == '@settings':
                # Create as the last child of the @settings node.
                p2 = p.insertAsLastChild()
                break
        else:
            # Create as the root node.
            oldRoot = c.rootPosition()
            p2 = oldRoot.insertAfter()
            p2.moveToRoot(oldRoot)
        c.setHeadString(p2, '@macros')
        g.es_print('Created: %s' % p2.h)
        c.redraw()
        return p2
    #@+node:ekr.20150514063305.440: *3* getWidgetName
    def getWidgetName(self, obj):
        if not obj:
            return ''
        if hasattr(obj, 'objectName'):
            return obj.objectName()
        if hasattr(obj, 'widget'):
            if hasattr(obj.widget, 'objectName'):
                return obj.widget.objectName()
        return ''
    #@+node:ekr.20150514063305.441: *3* loadMacros
    @cmd('macro-load-all')
    def loadMacros(self, event=None):
        '''Load macros from the @macros node.'''
        trace = False and not g.unitTesting
        c = self.c
        create_event = g.app.gui.create_key_event
        p = self.getMacrosNode()

        def oops(message):
            g.trace(message)

        lines = g.splitLines(p.b)
        i = 0
        macro = []; name = None
        while i < len(lines):
            progress = i
            s = lines[i].strip()
            i += 1
            if s.startswith('::') and s.endswith('::'):
                name = s[2: -2]
                if name:
                    macro = []
                    while i < len(lines):
                        s = lines[i].strip()
                        if trace: g.trace(repr(name), repr(s))
                        if s:
                            stroke = s
                            char = c.k.stroke2char(stroke)
                            w = c.frame.body.wrapper
                            macro.append(create_event(c, char, stroke, w))
                            i += 1
                        else: break
                    # Create the entries.
                    if macro:
                        self.completeMacroDef(name, macro)
                        macro = []; name = None
                    else:
                        oops('empty expansion for %s' % (name))
            elif s:
                if s.startswith('#') or s.startswith('@'):
                    pass
                else:
                    oops('ignoring line: %s' % (repr(s)))
            else: pass
            assert progress < i
        # finish of the last macro.
        if macro:
            self.completeMacroDef(name, macro)
    #@+node:ekr.20150514063305.442: *3* nameLastMacro
    @cmd('macro-name-last')
    def nameLastMacro(self, event):
        '''Prompts for the name to be given to the last recorded macro.'''
        k = self.c.k; state = k.getState('name-macro')
        if state == 0:
            k.setLabelBlue('Name of macro: ')
            k.getArg(event, 'name-macro', 1, self.nameLastMacro)
        else:
            k.clearState()
            name = k.arg
            self.completeMacroDef(name, self.lastMacro)
            k.setLabelGrey('Macro defined: %s' % name)
    #@+node:ekr.20150514063305.443: *3* printMacros & printLastMacro
    @cmd('macro-print-all')
    def printMacros(self, event=None):
        '''Prints the name and definition of all named macros.'''
        names = list(self.namedMacros.keys())
        if names:
            names.sort()
            print('macros', names)
            # g.es('\n'.join(names),tabName='Macros')
        else:
            g.es('no macros')

    @cmd('macro-print-last')
    def printLastMacro(self, event=None):
        '''Print the last (unnamed) macro.'''
        if self.lastMacro:
            for event in self.lastMacro:
                g.es(repr(event.stroke))
    #@+node:ekr.20150514063305.444: *3* saveMacros
    @cmd('macro-save-all')
    def saveMacros(self, event=None):
        '''Store macros in the @macros node..'''
        p = self.getMacrosNode()
        result = []
        # g.trace(list(self.namedMacros.keys()))
        for name in self.namedMacros:
            macro = self.namedMacros.get(name)
            result.append('::%s::' % (name))
            for event in macro:
                if 0:
                    w_name = self.getWidgetName(event.w)
                    result.append('%s::%s::%s' % (repr(event.char), event.stroke, w_name))
                result.append(event.stroke)
            result.append('') # Blank line terminates
        p.b = '\n'.join(result)
    #@+node:ekr.20150514063305.445: *3* startRecordingMacro
    @cmd('macro-start-recording')
    def startRecordingMacro(self, event):
        '''Start recording or continue to record a macro.'''
        trace = False and not g.unitTesting
        k = self.c.k
        if event:
            if self.recordingMacro:
                if trace: g.trace('stroke', event.stroke)
                self.macro.append(event)
            else:
                self.recordingMacro = True
                k.setLabelBlue('Recording macro. ctrl-g to end...', protect=True)
                # g.es('Recording macro. ctrl-g to end...')
        else:
            g.trace('can not happen: no event')
    #@-others
#@-others
#@-leo
