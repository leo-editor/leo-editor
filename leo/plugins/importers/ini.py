#@+leo-ver=5-thin
#@+node:ekr.20140723122936.18142: * @file importers/ini.py
'''The @auto importer for .ini files.'''
import leo.core.leoGlobals as g
import leo.plugins.importers.basescanner as basescanner
#@+others
#@+node:ekr.20140723122936.18043: ** class IniScanner
class IniScanner (basescanner.BaseScanner):

    def __init__ (self,importCommands,atAuto):

        # Init the base class.
        basescanner.BaseScanner.__init__(self,
            importCommands,atAuto=atAuto,language='ini')

        # Override defaults defined in the base class.
        self.classTags = []
        self.functionTags = []
        self.hasClasses = False
        self.hasFunctions = True
        self.lineCommentDelim = ';'

    def startsString(self,s,i):
        return False

    #@+others
    #@+node:ekr.20140723122936.18044: *3* startsHelper (ElispScanner)
    def startsHelper(self,s,i,kind,tags,tag=None):
        '''return True if s[i:] starts section.
        Sets sigStart, sigEnd, sigId and codeEnd ivars.'''

        trace = False
        self.codeEnd = self.sigEnd = self.sigId = None
        self.sigStart = i

        sigStart = i
        ok,sigId,i = self.isSectionLine(s,i)
        if not sigId or not ok:
            # if trace: g.trace('fail',repr(g.getLine(s,i)))
            return False

        i = sigEnd = g.skip_line(s,i)

        # Skip everything until the next section.
        while i < len(s):
            progress = i
            ok,junk,junk = self.isSectionLine(s,i)
            if ok: break # don't change i.
            i = g.skip_line(s,i)
            assert progress < i

        # Success: set the ivars.
        self.sigStart = sigStart
        self.codeEnd = i
        self.sigEnd = sigEnd
        self.sigId = sigId
        self.classId = None

        # Note: backing up here is safe because
        # we won't back up past scan's 'start' point.
        # Thus, characters will never be output twice.
        k = self.sigStart
        if not g.match(s,k,'\n'):
            self.sigStart = g.find_line_start(s,k)

        if trace: g.trace(sigId,'returns\n'+s[self.sigStart:i]+'\nEND')
        return True
    #@+node:ekr.20140723122936.18045: *3* isSectionLine
    def isSectionLine(self,s,i):

        i = g.skip_ws(s,i)
        if not g.match(s,i,'['):
            return False,None,i
        k = s.find('\n',i+1)
        if k == -1: k = len(s)
        j = s.find(']',i+1)
        if -1 < j < k:
            return True,s[i:j+1],i
        else:
            return False,None,i
    #@-others
#@-others
importer_dict = {
    'class': IniScanner,
    'extensions': ['.ini',],
}
#@-leo
