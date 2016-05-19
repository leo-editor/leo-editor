# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20150514035559.1: * @file ../commands/bufferCommands.py
#@@first
'''Leo's buffer commands.'''
#@+<< imports >>
#@+node:ekr.20150514045750.1: ** << imports >> (bufferCommands.py)
import leo.core.leoGlobals as g
from leo.commands.baseCommands import BaseEditCommandsClass as BaseEditCommandsClass
#@-<< imports >>

def cmd(name):
    '''Command decorator for the BufferCommands class.'''
    return g.new_cmd_decorator(name, ['c', 'bufferCommands',])

#@+others
#@+node:ekr.20160514095727.1: ** class BufferCommandsClass
class BufferCommandsClass(BaseEditCommandsClass):
    '''
    An Emacs instance does not have knowledge of what is considered a
    buffer in the environment.

    '''
    #@+others
    #@+node:ekr.20150514045829.3: *3* buffer.ctor
    def __init__(self, c):
        '''Ctor for the BufferCommandsClass class.'''
        # pylint: disable=super-init-not-called
        self.c = c
        self.fromName = ''
            # Saved name from getBufferName.
        self.nameList = []
            # [n: <headline>]
        self.names = {}
        self.tnodes = {}
            # Keys are n: <headline>, values are tnodes.
    #@+node:ekr.20150514045829.5: *3* buffer.Entry points
    #@+node:ekr.20150514045829.6: *4* appendToBuffer
    @cmd('buffer-append-to')
    def appendToBuffer(self, event):
        '''Add the selected body text to the end of the body text of a named buffer (node).'''
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Append to buffer: ')
            self.getBufferName(event, self.appendToBufferFinisher)

    def appendToBufferFinisher(self, name):
        c, w = self.c, self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            w = self.w
            c.selectPosition(p)
            self.beginCommand(w, 'append-to-buffer: %s' % p.h)
            w.insert('end', s)
            w.setInsertPoint('end')
            w.seeInsertPoint()
            self.endCommand()
            c.redraw_after_icons_changed()
            c.recolor()
    #@+node:ekr.20150514045829.7: *4* copyToBuffer
    def copyToBuffer(self, event):
        '''Add the selected body text to the end of the body text of a named buffer (node).'''
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Copy to buffer: ')
            self.getBufferName(event, self.copyToBufferFinisher)

    def copyToBufferFinisher(self, name):
        c, w = self.c, self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand(w, 'copy-to-buffer: %s' % p.h)
            w.insert('end', s)
            w.setInsertPoint('end')
            self.endCommand()
            c.redraw_after_icons_changed()
            c.recolor()
    #@+node:ekr.20150514045829.8: *4* insertToBuffer
    def insertToBuffer(self, event):
        '''Add the selected body text at the insert point of the body text of a named buffer (node).'''
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Insert to buffer: ')
            self.getBufferName(event, self.insertToBufferFinisher)

    def insertToBufferFinisher(self, name):
        c, w = self.c, self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand(w, undoType=('insert-to-buffer: %s' % p.h))
            i = w.getInsertPoint()
            w.insert(i, s)
            w.seeInsertPoint()
            self.endCommand()
            c.redraw_after_icons_changed()
    #@+node:ekr.20150514045829.9: *4* killBuffer
    @cmd('buffer-kill')
    def killBuffer(self, event):
        '''Delete a buffer (node) and all its descendants.'''
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Kill buffer: ')
            self.getBufferName(event, self.killBufferFinisher)

    def killBufferFinisher(self, name):
        c = self.c
        p = self.findBuffer(name)
        if p:
            h = p.h
            current = c.p
            c.selectPosition(p)
            c.deleteOutline(op_name='kill-buffer: %s' % h)
            c.selectPosition(current)
            self.c.k.setLabelBlue('Killed buffer: %s' % h)
            c.redraw(current)
    #@+node:ekr.20150514045829.10: *4* listBuffers & listBuffersAlphabetically
    @cmd('buffers-list')
    def listBuffers(self, event):
        '''
        List all buffers (node headlines), in outline order. Nodes with the
        same headline are disambiguated by giving their parent or child index.
        '''
        self.computeData()
        g.es('buffers...')
        for name in self.nameList:
            g.es('', name)

    @cmd('buffers-list-alphabetically')
    def listBuffersAlphabetically(self, event):
        '''
        List all buffers (node headlines), in alphabetical order. Nodes with
        the same headline are disambiguated by giving their parent or child
        index.
        '''
        self.computeData()
        names = sorted(self.nameList)
        g.es('buffers...')
        for name in names:
            g.es('', name)
    #@+node:ekr.20150514045829.11: *4* prependToBuffer
    @cmd('buffer-prepend-to')
    def prependToBuffer(self, event):
        '''Add the selected body text to the start of the body text of a named buffer (node).'''
        self.w = self.editWidget(event)
        if self.w:
            self.c.k.setLabelBlue('Prepend to buffer: ')
            self.getBufferName(event, self.prependToBufferFinisher)

    def prependToBufferFinisher(self, name):
        c, w = self.c, self.w
        s = w.getSelectedText()
        p = self.findBuffer(name)
        if s and p:
            c.selectPosition(p)
            self.beginCommand(w, 'prepend-to-buffer: %s' % p.h)
            w.insert(0, s)
            w.setInsertPoint(0)
            w.seeInsertPoint()
            self.endCommand()
            c.redraw_after_icons_changed()
            c.recolor()
    #@+node:ekr.20150514045829.12: *4* renameBuffer
    def renameBuffer(self, event):
        '''Rename a buffer, i.e., change a node's headline.'''
        g.es('rename-buffer not ready yet')
        if 0:
            self.c.k.setLabelBlue('Rename buffer from: ')
            self.getBufferName(event, self.renameBufferFinisher1)

    def renameBufferFinisher1(self, name):
        self.fromName = name
        self.c.k.setLabelBlue('Rename buffer from: %s to: ' % (name))
        event = None
        self.getBufferName(event, self.renameBufferFinisher2)

    def renameBufferFinisher2(self, name):
        c = self.c
        p = self.findBuffer(self.fromName)
        if p:
            c.endEditing()
            c.setHeadString(p, name)
            c.redraw(p)
    #@+node:ekr.20150514045829.13: *4* switchToBuffer
    @cmd('buffer-switch-to')
    def switchToBuffer(self, event):
        '''Select a buffer (node) by its name (headline).'''
        self.c.k.setLabelBlue('Switch to buffer: ')
        self.getBufferName(event, self.switchToBufferFinisher)

    def switchToBufferFinisher(self, name):
        c = self.c
        p = self.findBuffer(name)
        if p:
            c.selectPosition(p)
            c.redraw_after_select(p)
    #@+node:ekr.20150514045829.14: *3* buffer.Utils
    #@+node:ekr.20150514045829.15: *4* computeData
    def computeData(self):
        self.nameList = []
        self.names = {}
        self.tnodes = {}
        for p in self.c.all_unique_positions():
            h = p.h.strip()
            v = p.v
            nameList = self.names.get(h, [])
            if nameList:
                if p.parent():
                    key = '%s, parent: %s' % (h, p.parent().h)
                else:
                    key = '%s, child index: %d' % (h, p.childIndex())
            else:
                key = h
            self.nameList.append(key)
            self.tnodes[key] = v
            nameList.append(key)
            self.names[h] = nameList
    #@+node:ekr.20150514045829.16: *4* findBuffer
    def findBuffer(self, name):
        v = self.tnodes.get(name)
        for p in self.c.all_unique_positions():
            if p.v == v:
                return p
        g.trace("Can't happen", name)
        return None
    #@+node:ekr.20150514045829.17: *4* getBufferName
    def getBufferName(self, event, finisher):
        '''Get a buffer name into k.arg and call k.setState(kind,n,handler).'''
        k = self.c.k
        state = k.getState('getBufferName')
        if state == 0:
            self.computeData()
            self.getBufferNameFinisher = finisher
            prefix = k.getLabel()
            k.getArg(event, 'getBufferName', 1, self.getBufferName,
                prefix=prefix, tabList=self.nameList)
        else:
            k.resetLabel()
            k.clearState()
            finisher = self.getBufferNameFinisher
            self.getBufferNameFinisher = None
            finisher(k.arg)
    #@-others
#@-others
#@-leo
