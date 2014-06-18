# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20140527115626.17955: * @file ../test/stc_unit_tests.py
#@@first
#@+others
#@+node:ekr.20140527073639.16704: ** @testsetup
# Common setup code for all unit tests.
# **Note**: Only included for "all" and "marked" *local* runs.
trace = False
do_gc = True
    # Takes about 0.5 sec. per test.
    # Can be done at end of test.
if c.isChanged():
    c.save()
import ast
import gc
import leo.core.leoSTC as stc
import time
import imp
imp.reload(stc) # Takes about 0.003 sec.
u = stc.Utils()
u.update_run_count(verbose=True)
t2 = time.clock()
if do_gc:
    gc.collect()
if trace:
    print('@testsetup gc.collect: %s %s' % (
        (do_gc,g.timeSince(t2))))
#@+node:ekr.20140527073639.16706: ** @test DataTraverser
#@+others
#@+node:ekr.20140527125017.17956: *3* check_class_names
def check_class_names(defs_d,refs_d):
    aList = [ 
    #@+<< non-pep8 class names >>
    #@+node:ekr.20140528065727.17958: *4* << non-pep8 class names >>
    # This list was created with find-all: ^class ([a-z]\w+)
    # It should test for underscores, but doesn't.

    # Fixed by hand:
    # 'anchor_htmlParserClass', # AnchorHtmlParserClass
    # 'atFile',
    # 'htmlParserClass',
    # 'link_htmlParserClass', # -> LinHtmlParserClass
    # 'posList',
    # 'poslist',

    # new list:
    'cacher',
    'bridgeController',
    'bufferCommandsClass',
    'editCommandsClass',
    'fileCommands',
    'pythonScanner',
    'def_node',
    'tangleCommands',
    'leoCompare',
    'searchWidget',
    'baseTextWidget',
    'editBodyTestCase',
    'importExportTestCase',

    # Original list:
    # 'abbrevCommandsClass',
    # 'anchor_htmlParserClass',
    # 'atShadowTestCase',
    # 'baseEditCommandsClass',
    # 'baseFileCommands',
    # 'baseLeoCompare',
    # 'baseLeoPlugin',
    # 'baseNativeTreeWidget',
    # 'baseTangleCommands',
    # 'baseTextWidget',
    # 'bridgeController',
    # 'bufferCommandsClass',
    # 'cScanner',
    # 'cSharpScanner',
    # 'cacher',
    # 'chapterCommandsClass',
    # 'controlCommandsClass',
    # 'debugCommandsClass',
    # 'def_node',
    # 'editBodyTestCase',
    # 'editCommandsClass',
    # 'editFileCommandsClass',
    # 'elispScanner',
    # 'emergencyDialog',
    # 'fileCommands',
    # 'fileLikeObject',
    # 'goToLineNumber',
    # 'helpCommandsClass',
    # 'htmlParserClass',
    # 'htmlScanner',
    # 'importExportTestCase',
    # 'iniScanner',
    # 'invalidPaste',
    # 'jEditColorizer',
    # 'javaScanner',
    # 'keyHandlerClass',
    # 'keyHandlerCommandsClass',
    # 'killBufferCommandsClass',
    # 'killBuffer_iter_class',
    # 'leoBody',
    # 'leoCommandsClass',
    # 'leoCompare',
    # 'leoFind',
    # 'leoGui',
    # 'leoImportCommands',
    # 'leoKeyEvent',
    # 'leoMenu',
    # 'leoQLineEditWidget',
    # 'leoQScintillaWidget',
    # 'leoQTextEditWidget',
    # 'leoQtBaseTextWidget',
    # 'leoQtBody',
    # 'leoQtColorizer',
    # 'leoQtEventFilter',
    # 'leoQtFrame',
    # 'leoQtGui',
    # 'leoQtHeadlineWidget',
    # 'leoQtLog',
    # 'leoQtMenu',
    # 'leoQtMinibuffer',
    # 'leoQtSpellTab',
    # 'leoQtSyntaxHighlighter',
    # 'leoQtTree',
    # 'leoQtTreeTab',
    # 'leoTree',
    # 'leoTreeTab',
    # 'linkAnchorParserClass',
    # 'link_htmlparserClass',
    # 'macroCommandsClass',
    # 'markerClass',
    # 'nodeHistory',
    # 'nullBody',
    # 'nullColorizer',
    # 'nullFrame',
    # 'nullGui',
    # 'nullIconBarClass',
    # 'nullLog',
    # 'nullMenu',
    # 'nullObject',
    # 'nullScriptingControllerClass',
    # 'nullStatusLineClass',
    # 'nullTree',
    # 'part_node',
    # 'pascalScanner',
    # 'phpScanner',
    # 'pythonScanner',
    # 'qtIconBarClass',
    # 'qtMenuWrapper',
    # 'qtSearchWidget',
    # 'qtStatusLineClass',
    # 'qtTabBarWrapper',
    # 'readLinesClass',
    # 'rectangleCommandsClass',
    # 'recursiveImportController',
    # 'redirectClass',
    # 'registerCommandsClass',
    # 'root_attributes',
    # 'rstCommands',
    # 'rstScanner',
    # 'runTestExternallyHelperClass',
    # 'saxContentHandler',
    # 'saxNodeClass',
    # 'scanUtility',
    # 'searchCommandsClass',
    # 'searchWidget',
    # 'sourcereader',
    # 'sourcewriter',
    # 'spellCommandsClass',
    # 'spellTabHandler',
    # 'stringTextWidget',
    # 'tangleCommands',
    # 'tst_node',
    # 'undoer',
    # 'unitTestGui',
    # 'ust_node',
    # 'vimoutlinerScanner',
    # 'xmlScanner',
    #@-<< non-pep8 class names >>
    ]
    ambiguous,replace,undefined = [],[],[]
    for s in aList:
        aSet = defs_d.get(s,set())
        n = len(sorted(aSet))
        if n == 0:
            undefined.append(s)
        elif n > 1:
            ambiguous.append(s)
        else:
            replace.append(s)
        s2 = g.pep8_class_name(s)
        aSet = defs_d.get(s2,set())
        if len(sorted(aSet)) > 1:
            g.trace('conflict',s,s2)
    print('undefined...\n  %s' % '\n  '.join(sorted(undefined)))
    print('ambiguous...\n')
    for s in sorted(ambiguous):
        aSet = defs_d.get(s,set())
        # print('%20s %s' % (s,sorted(aSet)))
        print('%3s %s' % (len(sorted(aSet)),s))
    print('replace...\n  %s' % '\n  '.join(sorted(replace)))
#@+node:ekr.20140527083058.16708: *3* report
def report():
    '''Report ambiguous symbols.'''
    n = 0
    for s in sorted(defs_d.keys()):
        aSet = defs_d.get(s)
        aList = sorted(aSet)
        if len(aList) > 1:
            n += 1
            # g.trace('multiple defs',s)
    return n
#@-others
project_name = 'leo'
flags = (
    'check',
    'print',
    'report',
    # 'skip',
    # 'stats',
)
files = [
    # r'c:\leo.repo\leo-editor\leo\core\leoApp.py',
    # r'c:\leo.repo\leo-editor\leo\core\leoFileCommands.py',
] or u.project_files(project_name)
if g.app.runningAllUnitTests and (len(files) > 1 or 'skip' in flags):
    self.skipTest('slow test')
# Pass 0
t = time.time()
root_d = u.p0(files,project_name,False)
p0_time = u.diff_time(t)
# DataTraverser
t = time.time()
defs_d, refs_d = {},{}
dt = stc.DataTraverser(defs_d,refs_d)
for fn in sorted(files):
    dt(fn,root_d.get(fn))
dt_time = u.diff_time(t)
if 'check' in flags:
    check_class_names(defs_d,refs_d)
if 'print' in flags:
    print('files: %s' % len(files))
    print('parse: %s' % p0_time)
    print('   DT: %s' % dt_time)
    print('defs: %s refs: %s: ambiguous: %s' % (
        len(sorted(defs_d.keys())),
        len(sorted(refs_d.keys())),
        report(),
    ))
    if 'stats' in flags:
        dt.print_stats()
#@+node:ekr.20140528102444.17997: ** @test replace class names
'''Replace only unambiguously defined non-pep8 class names.'''
replace = False # True: actually make the replacements.
aList = [
#@+<< non-pep8 class names >>
#@+node:ekr.20140528102444.19375: *3* << non-pep8 class names >>
# These survived the second run of this script:
# They were fixed by hand.

# 'nullFrame',
# 'nullGui',
# 'leoKeyEvent',
# 'leoBody',
# 'leoLog',

# These survived the first run of this script:
# Most of these problems were due to a bug in check_new_name.

# 'atFile',
# 'baseTextWidget',
# 'bridgeController',
# 'bufferCommandsClass',
# 'cacher',
# 'def_node',
# 'editBodyTestCase',
# 'editCommandsClass',
# 'fileCommands',
# 'htmlParserClass',
# 'importExportTestCase',
# 'leoCompare',
# 'pythonScanner',
# 'searchWidget',
# 'tangleCommands',
#@-<< non-pep8 class names >>
]
if 0: # not needed when @testsetup exists.
    import leo.core.leoSTC as stc
    import time
    import imp
    imp.reload(stc) # Takes about 0.003 sec.
u = stc.Utils()
#@+others
#@+node:ekr.20140528102444.19376: *3* class ReplaceController
class ReplaceController:
    #@+others
    #@+node:ekr.20140530134300.17617: *4*  ctor
    def __init__(self,c,files):
        self.c = c
        self.changed = set()
        self.files_d = {} # Keys are full paths, values are file contents.
        self.files = sorted(files) # List of full paths.
    #@+node:ekr.20140528102444.19379: *4* check_new_name
    def check_new_name(self,old_name,new_name):
        '''Verify that new_name is found nowhere in Leo.'''
        for fn in sorted(self.files_d.keys()):
            s = self.files_d.get(fn)
            if self.find_word(s,old_name) and self.find_word(s,new_name):
                print('***** %20s -> %-20s exists in %s' % (
                    old_name,new_name,g.shortFileName(fn)))
                return False
        return True

    #@+node:ekr.20140601073705.17614: *4* find_word
    def find_word(self,s,word):
        '''Return True if word is found anywhere in s.'''
        i = 0
        while True:
            progress = i
            i = s.find(word,i)
            if i == -1:
                return False
            # Make sure we are at the start of a word.
            if i > 0:
                ch = s[i-1]
                if ch == '_' or ch.isalnum():
                    i += len(word)
                    continue
            if g.match_word(s,i,word):
                # g.trace(i,word,s[i-10:i+10])
                return True
            else:
                i += len(word)
            assert progress < i
    #@+node:ekr.20140528102444.19380: *4* load_files
    def load_files(self):
        for fn in self.files:
            assert g.os_path_exists(fn),fn
            f = open(fn,'r')
            s = f.read()
            f.close()
            self.files_d[fn] = s
            assert s,fn
        
    #@+node:ekr.20140528102444.19378: *4* replace_class_name
    def replace_class_name(self,old_name,new_name):
        assert old_name != new_name,old_name
        if not self.check_new_name(old_name,new_name):
            return
        for fn in self.files:
            s = self.files_d.get(fn)
            i = s.count(old_name)
            if i > 0:
                self.changed.add(fn)
                self.files_d[fn] = s.replace(old_name,new_name)
                print('%2s instances of %s in %s' % (
                    i,old_name,g.shortFileName(fn)))
    #@+node:ekr.20140528102444.19377: *4* run
    def run(self,aList):
        self.load_files()
        for s in aList:
            self.replace_class_name(s,g.pep8_class_name(s))
        self.write_files()
    #@+node:ekr.20140530134300.17616: *4* write_files
    def write_files(self):
        '''Write all changed files.'''
        if replace:
            for fn in sorted(self.changed):
                if replace:
                    print('writing: %s' % fn)
                    f = open(fn,'w')
                    s = self.files_d.get(fn)
                    f.write(s)
                    f.close()
        else:
            print('changed, not written:...\n%s' % (
                '\n'.join(sorted(self.changed))))
    #@-others
#@-others
files = u.project_files('leo')
ReplaceController(c,files).run(aList)
#@+node:ekr.20140601151054.17619: ** @test Data2
#@+others
#@+node:ekr.20140616055519.17771: *3* dump_contexts_d
def dump_contexts_d(dt):
    d = dt.contexts_d
    print('Dump of contexts_d...')
    for name in sorted(d.keys()):
        cx = d.get(name)
        print(cx.full_name())
        # for child in cx.child_contexts:
            # print('  %s' % child.full_name())
    print('')
#@+node:ekr.20140604135104.17796: *3* dump_global_d
def dump_global_d(dt):
    d = dt.global_d
    for name in sorted(d.keys()):
        aList = d.get(name)
        print('%s:\n%s' % (
            name,
            '  \n'.join(['  %r' % (z) for z in aList])))
#@+node:ekr.20140603074103.17640: *3* pass0
def pass0(files):
    '''Do all p0 processing.'''
    t = time.time()
    if 's' in flags:
        if 'src' in flags:
            print(s)
        node1 = u.p0s(s,report=False,tag='s')
        if 'dump_ast1' in flags:
            print('ast for s1...\n%s\n' % (u.dump_ast(node1)))
        node2 = u.p0s(s2,report=False,tag='s2') if s2 else None
        root_d = {'s': node1, 's2': node2,}
        files = root_d.keys()
    else:
        root_d = u.p0(
            files or u.project_files(project_name),
            project_name,report=False)
    p0_time = u.diff_time(t)
    return files,p0_time,root_d
#@+node:ekr.20140603074103.17642: *3* pass1
def pass1(files,root_d):
    '''Apply dt to all files.'''
    t = time.time()
    for fn in sorted(files):
        dt(fn,root_d.get(fn))
    dt_time = u.diff_time(t)
    return dt_time
#@+node:ekr.20140616202104.17702: *3* pickle
def pickle(root_d):
    import pickle
    import pprint
    t = time.time()
    for fn in sorted(root_d.keys()):
        node = root_d.get(fn)
        f = g.fileLikeObject()
        pickle.dump(node,f)
        s = f.read()
        # g.trace(pprint.pformat(s))
        g.trace('%7s %s' % (len(s),g.shortFileName(fn)))
    g.trace('%s' % u.diff_time(t))
#@+node:ekr.20140603074103.17641: *3* report
def report():
    '''Print final report.'''
    print('')
    print('files: %s' % len(files))
    print('parse: %s' % p0_time)
    print('   DT: %s' % dt_time)
    print('defs: %s refs: %s: ambiguous: %s' % (
        len(sorted(dt.defs_d.keys())),
        len(sorted(dt.refs_d.keys())),
        report_ambiguous(dt),
    ))
    if 'stats' in flags:
        dt.print_stats()
#@+node:ekr.20140601151054.17660: *4* report_ambiguous
def report_ambiguous(dt):
    '''Report ambiguous symbols.'''
    d = dt.defs_d
    n = 0
    for s in sorted(d.keys()):
        aSet = d.get(s)
        aList = sorted(aSet)
        if len(aList) > 1:
            n += 1
    return n
#@-others
project_name = 'leo'
flags = (
    # 'dump_ast1', # Dump s1
    # 'dump_global_d',
    # 'dump_contexts_d',
    # 'pickle',
    'report',
    'stats',
    # 's',
    'src',
    'self_alias', # detect aliases to self.
)
files = [
    # 'c:\leo.repo\leo-editor\leo\core\leoApp.py',
    # r'c:\leo.repo\leo-editor\leo\core\leoFileCommands.py',
]
#@+<< define s for Data2 test >>
#@+node:ekr.20140603074103.17639: *3* << define s for Data2 test >>
s = '''
# module s
class aClass:
    def aDef(arg):
        print(arg)
a = aClass()
a.b = 2
a.aDef(5)
'''

#@-<< define s for Data2 test >>
#@+<< define s2 for Data2 test >>
#@+node:ekr.20140603074103.17644: *3* << define s2 for Data2 test >>
s2 = '''
# module s2
import s
'''
#@-<< define s2 for Data2 test >>
dt = stc.Data2()
files,p0_time,root_d = pass0(files)
dt_time = pass1(files,root_d)
if 'pickle' in flags:
    pickle(root_d)
if 'dump_contexts_d' in flags:
    dump_contexts_d(dt)
if 'dump_global_d' in flags:
    dump_global_d(dt)
if 'report' in flags:
    report()
#@-others
#@@language python
#@@tabwidth -4
#@-leo
