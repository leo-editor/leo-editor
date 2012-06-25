<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo (http://webpages.charter.net/edreamleo/front.html) -->
<?xml-stylesheet ekr_test?>
<leo_file xmlns:leo="http://www.leo-editor.org/2011/leo" >
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20120625092120.12815"><vh>Unused from leoGlobals.py</vh>
<v t="ekr.20120625092120.12471"><vh>&lt;&lt; imports &gt;&gt;</vh></v>
<v t="ekr.20120625092120.12474"><vh>Checking Leo Files</vh>
<v t="ekr.20120625092120.12475"><vh>createTopologyList</vh></v>
</v>
<v t="ekr.20120625092120.12476"><vh>Commands &amp; Directives</vh>
<v t="ekr.20120625092120.12477"><vh>g.Directive utils...</vh>
<v t="ekr.20120625092120.12478"><vh>g.comment_delims_from_extension</vh></v>
<v t="ekr.20120625092120.12479"><vh>g.findAtTabWidthDirectives (must be fast)</vh></v>
<v t="ekr.20120625092120.12480"><vh>g.findLanguageDirectives (must be fast)</vh></v>
<v t="ekr.20120625092120.12481"><vh>g.findReference</vh></v>
<v t="ekr.20120625092120.12482"><vh>g.get_directives_dict (must be fast)</vh>
<v t="ekr.20120625092120.12483"><vh>compute_directives_re</vh></v>
</v>
<v t="ekr.20120625092120.12484"><vh>g.get_directives_dict_list (must be fast)</vh></v>
<v t="ekr.20120625092120.12485"><vh>g.getLanguageFromAncestorAtFileNode (New)</vh></v>
<v t="ekr.20120625092120.12486"><vh>g.getOutputNewline</vh></v>
<v t="ekr.20120625092120.12487"><vh>g.scanAtCommentAndLanguageDirectives</vh></v>
<v t="ekr.20120625092120.12488"><vh>g.scanAtEncodingDirectives</vh></v>
<v t="ekr.20120625092120.12489"><vh>g.scanAtHeaderDirectives</vh></v>
<v t="ekr.20120625092120.12490"><vh>g.scanAtLineendingDirectives</vh></v>
<v t="ekr.20120625092120.12491"><vh>g.scanAtPagewidthDirectives</vh></v>
<v t="ekr.20120625092120.12492"><vh>g.scanAtPathDirectives scanAllAtPathDirectives</vh></v>
<v t="ekr.20120625092120.12493"><vh>g.scanAtRootDirectives</vh></v>
<v t="ekr.20120625092120.12494"><vh>g.scanAtRootOptions</vh>
<v t="ekr.20120625092120.12495"><vh>&lt;&lt; scan another @root option &gt;&gt;</vh></v>
</v>
<v t="ekr.20120625092120.12496"><vh>g.scanAtTabwidthDirectives &amp; scanAllTabWidthDirectives</vh></v>
<v t="ekr.20120625092120.12497"><vh>g.scanAtWrapDirectives &amp; scanAllAtWrapDirectives</vh></v>
<v t="ekr.20120625092120.12498"><vh>g.scanDirectives  (for compatibility only)</vh></v>
<v t="ekr.20120625092120.12499"><vh>g.scanForAtIgnore</vh></v>
<v t="ekr.20120625092120.12500"><vh>g.scanForAtLanguage</vh></v>
<v t="ekr.20120625092120.12501"><vh>g.scanForAtSettings</vh></v>
<v t="ekr.20120625092120.12502"><vh>g.set_delims_from_language</vh></v>
<v t="ekr.20120625092120.12503"><vh>g.set_delims_from_string</vh></v>
<v t="ekr.20120625092120.12504"><vh>g.set_language</vh></v>
<v t="ekr.20120625092120.12505"><vh>g.setDefaultDirectory &amp; helper</vh>
<v t="ekr.20120625092120.12506"><vh>g.checkOpenDirectory</vh></v>
</v>
<v t="ekr.20120625092120.12507"><vh>g.stripPathCruft</vh></v>
</v>
</v>
<v t="ekr.20120625092120.12816"><vh>Debugging</vh>
<v t="ekr.20120625092120.12553"><vh>class Tracer &amp; g.startTracer</vh>
<v t="ekr.20120625092120.12554"><vh> __init__ (Tracer)</vh></v>
<v t="ekr.20120625092120.12555"><vh>computeName</vh></v>
<v t="ekr.20120625092120.12556"><vh>report</vh></v>
<v t="ekr.20120625092120.12557"><vh>stop</vh></v>
<v t="ekr.20120625092120.12558"><vh>tracer</vh></v>
<v t="ekr.20120625092120.12559"><vh>updateStats</vh></v>
</v>
<v t="ekr.20120625092120.12818"><vh>Dumps</vh>
<v t="ekr.20120625092120.12514"><vh>dump</vh></v>
<v t="ekr.20120625092120.12515"><vh>es_dump</vh></v>
<v t="ekr.20120625092120.12522"><vh>printBindings</vh></v>
<v t="ekr.20120625092120.12523"><vh>printGlobals</vh></v>
</v>
<v t="ekr.20120625092120.12509"><vh>g.alert</vh></v>
<v t="ekr.20120625092120.12524"><vh>g.printEntireTree</vh></v>
<v t="ekr.20120625092120.12819"><vh>Getters</vh>
<v t="ekr.20120625092120.12542"><vh>g.get_line &amp; get_line__after</vh></v>
<v t="ekr.20120625092120.12541"><vh>g.getIvarsDict and checkUnchangedIvars</vh></v>
<v t="ekr.20120625092120.12545"><vh>g.print_dict &amp; dictToString</vh></v>
<v t="ekr.20120625092120.12546"><vh>g.print_list &amp; listToString</vh></v>
<v t="ekr.20120625092120.12544"><vh>g.print_obj &amp; toString</vh></v>
<v t="ekr.20120625092120.12547"><vh>g.print_stack (printStack)</vh></v>
</v>
<v t="ekr.20120625092120.12525"><vh>printLeoModules</vh></v>
<v t="ekr.20120625092120.12527"><vh>redirecting stderr and stdout to Leo's log pane</vh>
<v t="ekr.20120625092120.12528"><vh>&lt;&lt; redirectClass methods &gt;&gt;</vh>
<v t="ekr.20120625092120.12529"><vh>redirectClass.__init__</vh></v>
<v t="ekr.20120625092120.12530"><vh>isRedirected</vh></v>
<v t="ekr.20120625092120.12531"><vh>flush</vh></v>
<v t="ekr.20120625092120.12532"><vh>rawPrint</vh></v>
<v t="ekr.20120625092120.12533"><vh>redirect</vh></v>
<v t="ekr.20120625092120.12534"><vh>undirect</vh></v>
<v t="ekr.20120625092120.12535"><vh>write</vh></v>
</v>
<v t="ekr.20120625092120.12536"><vh>&lt;&lt; define convenience methods for redirecting streams &gt;&gt;</vh>
<v t="ekr.20120625092120.12537"><vh>redirectStderr &amp; redirectStdout</vh></v>
<v t="ekr.20120625092120.12538"><vh>restoreStderr &amp; restoreStdout</vh></v>
<v t="ekr.20120625092120.12539"><vh>stdErrIsRedirected &amp; stdOutIsRedirected</vh></v>
<v t="ekr.20120625092120.12540"><vh>rawPrint</vh></v>
</v>
</v>
<v t="ekr.20120625092120.12548"><vh>Statistics</vh>
<v t="ekr.20120625092120.12549"><vh>clear_stats</vh></v>
<v t="ekr.20120625092120.12550"><vh>print_stats</vh></v>
<v t="ekr.20120625092120.12551"><vh>stat</vh></v>
</v>
<v t="ekr.20120625092120.12552"><vh>Timing</vh></v>
</v>
<v t="ekr.20120625092120.12820"><vh>Files &amp; Directories</vh>
<v t="ekr.20120625092120.12561"><vh> Redirection to LoadManager methods</vh></v>
<v t="ekr.20120625092120.12562"><vh>g.chdir</vh></v>
<v t="ekr.20120625092120.12563"><vh>g.create_temp_file</vh></v>
<v t="ekr.20120625092120.12564"><vh>g.ensure_extension</vh></v>
<v t="ekr.20120625092120.12526"><vh>g.file/module/plugin_date</vh></v>
<v t="ekr.20120625092120.12565"><vh>g.getBaseDirectory</vh></v>
<v t="ekr.20120625092120.12566"><vh>g.guessExternalEditor</vh></v>
<v t="ekr.20120625092120.12567"><vh>g.is_binary_file</vh></v>
<v t="ekr.20120625092120.12568"><vh>g.is_sentinel</vh>
<v t="ekr.20120625092120.12569"><vh>&lt;&lt; is_sentinel doc tests &gt;&gt;</vh></v>
</v>
<v t="ekr.20120625092120.12570"><vh>g.makeAllNonExistentDirectories</vh></v>
<v t="ekr.20120625092120.12571"><vh>g.makePathRelativeTo</vh></v>
<v t="ekr.20120625092120.12572"><vh>g.openWithFileName</vh></v>
<v t="ekr.20120625092120.12573"><vh>g.readFileIntoString (Leo 4.7)</vh></v>
<v t="ekr.20120625092120.12574"><vh>g.readlineForceUnixNewline</vh></v>
<v t="ekr.20120625092120.12575"><vh>g.recursiveUNLSearch</vh></v>
<v t="ekr.20120625092120.12576"><vh>g.sanitize_filename</vh></v>
<v t="ekr.20120625092120.12577"><vh>g.setGlobalOpenDir</vh></v>
<v t="ekr.20120625092120.12579"><vh>Used by tangle code &amp; leoFileCommands</vh>
<v t="ekr.20120625092120.12580"><vh>g.update_file_if_changed</vh></v>
<v t="ekr.20120625092120.12581"><vh>g.utils_remove</vh></v>
<v t="ekr.20120625092120.12582"><vh>g.utils_rename</vh></v>
<v t="ekr.20120625092120.12583"><vh>g.utils_chmod</vh></v>
<v t="ekr.20120625092120.12584"><vh>g.utils_stat</vh></v>
</v>
</v>
<v t="ekr.20120625092120.12585"><vh>Garbage Collection</vh>
<v t="ekr.20120625092120.12586"><vh>clearAllIvars</vh></v>
<v t="ekr.20120625092120.12587"><vh>collectGarbage</vh></v>
<v t="ekr.20120625092120.12588"><vh>enable_gc_debug</vh></v>
<v t="ekr.20120625092120.12589"><vh>printGc</vh>
<v t="ekr.20120625092120.12590"><vh>printGcRefs</vh></v>
</v>
<v t="ekr.20120625092120.12591"><vh>printGcAll</vh></v>
<v t="ekr.20120625092120.12592"><vh>printGcObjects   (printNewObjects=pno)</vh>
<v t="ekr.20120625092120.12593"><vh>&lt;&lt; print number of each type of object &gt;&gt;</vh></v>
<v t="ekr.20120625092120.12594"><vh>&lt;&lt; print added functions &gt;&gt;</vh></v>
</v>
<v t="ekr.20120625092120.12595"><vh>printGcSummary</vh></v>
<v t="ekr.20120625092120.12596"><vh>printGcVerbose</vh></v>
</v>
<v t="ekr.20120625092120.12597"><vh>Hooks &amp; plugins</vh>
<v t="ekr.20120625092120.12598"><vh>idle time functions (leoGlobals)</vh>
<v t="ekr.20120625092120.12599"><vh>enableIdleTimeHook</vh></v>
<v t="ekr.20120625092120.12600"><vh>disableIdleTimeHook</vh></v>
<v t="ekr.20120625092120.12601"><vh>idleTimeHookHandler</vh></v>
</v>
<v t="ekr.20120625092120.12602"><vh>g.act_on_node</vh></v>
<v t="ekr.20120625092120.12603"><vh>g.doHook</vh></v>
<v t="ekr.20120625092120.12604"><vh>g.command (decorator for creating global commands)</vh></v>
<v t="ekr.20120625092120.12605"><vh>g.childrenModifiedSet, g.contentModifiedSet</vh></v>
<v t="ekr.20120625092120.12606"><vh>Wrappers for g.app.pluginController methods</vh>
<v t="ekr.20120625092120.12607"><vh>Loading &amp; registration</vh></v>
<v t="ekr.20120625092120.12608"><vh>Information</vh></v>
</v>
</v>
<v t="ekr.20120625092120.12827"><vh>Most used</vh>
<v t="ekr.20120625092120.12610"><vh>g.choose</vh></v>
<v t="ekr.20120625092120.12612"><vh>g.enl, ecnl &amp; ecnls</vh></v>
<v t="ekr.20120625092120.12614"><vh>g.es</vh></v>
<v t="ekr.20120625092120.12615"><vh>g.es_print</vh></v>
<v t="ekr.20120625092120.12616"><vh>g.es_trace</vh></v>
<v t="ekr.20120625092120.12618"><vh>g.posList</vh>
<v t="ekr.20120625092120.12619"><vh>&lt;&lt; docstring for posList &gt;&gt;</vh></v>
</v>
</v>
<v t="ekr.20120625092120.12830"><vh>Scanning</vh>
<v t="ekr.20120625092120.12649"><vh>Functions that call scanError</vh>
<v t="ekr.20120625092120.12650"><vh>skip_block_comment</vh></v>
<v t="ekr.20120625092120.12651"><vh>skip_braces</vh></v>
<v t="ekr.20120625092120.12652"><vh>skip_php_braces (no longer used)</vh></v>
<v t="ekr.20120625092120.12653"><vh>skip_parens</vh></v>
<v t="ekr.20120625092120.12654"><vh>skip_pascal_begin_end</vh></v>
<v t="ekr.20120625092120.12655"><vh>skip_pascal_block_comment</vh></v>
<v t="ekr.20120625092120.12656"><vh>skip_pascal_string : called by tangle</vh></v>
<v t="ekr.20120625092120.12657"><vh>skip_heredoc_string : called by php import (Dave Hein)</vh></v>
<v t="ekr.20120625092120.12658"><vh>skip_pp_directive</vh></v>
<v t="ekr.20120625092120.12659"><vh>skip_pp_if</vh></v>
<v t="ekr.20120625092120.12660"><vh>skip_pp_part</vh></v>
<v t="ekr.20120625092120.12661"><vh>skip_python_string</vh></v>
<v t="ekr.20120625092120.12662"><vh>skip_string</vh></v>
<v t="ekr.20120625092120.12663"><vh>skip_to_semicolon</vh></v>
<v t="ekr.20120625092120.12664"><vh>skip_typedef</vh></v>
</v>
<v t="ekr.20120625092120.12647"><vh>scanError</vh></v>
<v t="ekr.20120625092120.12648"><vh>scanf</vh></v>
</v>
<v t="ekr.20120625092120.12691"><vh>Script Tools</vh>
<v t="ekr.20120625092120.12692"><vh>g.executeFile</vh></v>
<v t="ekr.20120625092120.12693"><vh>g.findNode... &amp;,findTopLevelNode</vh></v>
<v t="ekr.20120625092120.12694"><vh>g.getScript</vh></v>
<v t="ekr.20120625092120.12695"><vh>g.handleScriptException</vh>
<v t="ekr.20120625092120.12696"><vh>&lt;&lt; dump the lines near the error &gt;&gt;</vh></v>
</v>
<v t="ekr.20120625092120.12697"><vh>g.initScriptFind (set up dialog)</vh></v>
</v>
<v t="ekr.20120625092120.12698"><vh>Tokenizing &amp; parsing</vh>
<v t="ekr.20120625092120.12699"><vh>g.python_tokenize</vh></v>
</v>
<v t="ekr.20120625092120.12834"><vh>Unicode</vh>
<v t="ekr.20120625092120.12709"><vh>toEncodedStringWithErrorCode (for unit testing)</vh></v>
<v t="ekr.20120625092120.12710"><vh>toUnicodeWithErrorCode (for unit testing)</vh></v>
</v>
<v t="ekr.20120625092120.12711"><vh>Unit testing</vh>
<v t="ekr.20120625092120.12712"><vh>g.getTestVars</vh></v>
<v t="ekr.20120625092120.12713"><vh>g.findTestScript</vh></v>
</v>
<v t="ekr.20120625092120.12714"><vh>Urls</vh>
<v t="ekr.20120625092120.12715"><vh>g.computeFileUrl</vh></v>
<v t="ekr.20120625092120.12716"><vh>g.getUrlFromNode</vh></v>
<v t="ekr.20120625092120.12717"><vh>g.handleUrl</vh></v>
<v t="ekr.20120625092120.12718"><vh>g.isValidUrl</vh></v>
<v t="ekr.20120625092120.12719"><vh>g.openUrl</vh></v>
<v t="ekr.20120625092120.12720"><vh>g.openUrlOnClick (open-url-under-cursor)</vh></v>
</v>
<v t="ekr.20120625092120.12821"><vh>Utility classes, functions &amp; objects</vh>
<v t="ekr.20120625092120.12722"><vh> Index utilities</vh>
<v t="ekr.20120625092120.12723"><vh>g.convertPythonIndexToRowCol</vh></v>
<v t="ekr.20120625092120.12724"><vh>g.convertRowColToPythonIndex</vh></v>
</v>
<v t="ekr.20120625092120.12725"><vh> List utilities...</vh>
<v t="ekr.20120625092120.12726"><vh>appendToList</vh></v>
<v t="ekr.20120625092120.12727"><vh>flattenList</vh></v>
<v t="ekr.20120625092120.12728"><vh>maxStringListLength</vh></v>
</v>
<v t="ekr.20120625092120.12730"><vh>CheckVersion</vh>
<v t="ekr.20120625092120.12731"><vh>CheckVersion, helper</vh>
<v t="ekr.20120625092120.12732"><vh>CheckVersionToInt</vh></v>
</v>
<v t="ekr.20120625092120.12733"><vh>oldCheckVersion (Dave Hein)</vh></v>
</v>
<v t="ekr.20120625092120.12736"><vh>g.assertui</vh></v>
<v t="ekr.20120625092120.12738"><vh>g.computeWindowTitle</vh></v>
<v t="ekr.20120625092120.12739"><vh>g.ensureLeading/TrailingNewlines</vh></v>
<v t="ekr.20120625092120.12740"><vh>g.executeScript</vh></v>
<v t="ekr.20120625092120.12750"><vh>g.GeneralSetting &amp; isGeneralSetting</vh></v>
<v t="ekr.20120625092120.12751"><vh>g.getDocString</vh></v>
<v t="ekr.20120625092120.12752"><vh>g.getDocStringForFunction</vh></v>
<v t="ekr.20120625092120.12754"><vh>g.isMacOS</vh></v>
<v t="ekr.20120625092120.12784"><vh>g.KeyStroke &amp; isStroke/OrNone</vh>
<v t="ekr.20120625092120.12785"><vh> ks.ctor</vh></v>
<v t="ekr.20120625092120.12786"><vh> Special methods</vh>
<v t="ekr.20120625092120.12787"><vh>ks.__hash__</vh></v>
<v t="ekr.20120625092120.12788"><vh>ks.__repr___ &amp; __str__</vh></v>
<v t="ekr.20120625092120.12789"><vh>ks.rich comparisons</vh></v>
</v>
<v t="ekr.20120625092120.12790"><vh>ks.find, lower &amp; startswith</vh></v>
<v t="ekr.20120625092120.12791"><vh>ks.isFKey</vh></v>
<v t="ekr.20120625092120.12792"><vh>ks.toGuiChar</vh></v>
</v>
<v t="ekr.20120625092120.12755"><vh>g.longestCommonPrefix &amp; g.itemsMatchingPrefixInList</vh></v>
<v t="ekr.20120625092120.12757"><vh>g.prettyPrintType</vh></v>
<v t="ekr.20120625092120.12758"><vh>g.removeLeading/Trailing</vh></v>
<v t="ekr.20120625092120.12759"><vh>g.ShortcutInfo &amp; isShortcutInfo</vh>
<v t="ekr.20120625092120.12760"><vh> ctor (ShortcutInfo)</vh></v>
<v t="ekr.20120625092120.12761"><vh>__hash__ (ShortcutInfo)</vh></v>
<v t="ekr.20120625092120.12762"><vh>__repr__ &amp; ___str_&amp; dump (ShortcutInfo)</vh></v>
<v t="ekr.20120625092120.12763"><vh>isModeBinding</vh></v>
</v>
<v t="ekr.20120625092120.12765"><vh>g.toPythonIndex</vh></v>
<v t="ekr.20120625092120.12766"><vh>g.TypedDict/OfLists &amp; isTypedDict/OfLists</vh>
<v t="ekr.20120625092120.12767"><vh>td.ctor</vh></v>
<v t="ekr.20120625092120.12768"><vh>td.__repr__ &amp; __str__</vh></v>
<v t="ekr.20120625092120.12769"><vh>td._checkKey/ValType</vh></v>
<v t="ekr.20120625092120.12770"><vh>td.add &amp; td.replace</vh></v>
<v t="ekr.20120625092120.12771"><vh>td.copy</vh></v>
<v t="ekr.20120625092120.12772"><vh>td.dump</vh></v>
<v t="ekr.20120625092120.12773"><vh>td getters</vh></v>
<v t="ekr.20120625092120.12774"><vh>td.setName</vh></v>
<v t="ekr.20120625092120.12775"><vh>td.update</vh></v>
</v>
<v t="ekr.20120625092120.12624"><vh>g.windows</vh></v>
<v t="ekr.20120625092120.12776"><vh>import wrappers</vh>
<v t="ekr.20120625092120.12777"><vh>g.cantImport</vh></v>
<v t="ekr.20120625092120.12778"><vh>g.importModule</vh></v>
<v t="ekr.20120625092120.12779"><vh>g.importExtension &amp; helpers</vh></v>
<v t="ekr.20120625092120.12780"><vh>g.importFromPath</vh></v>
</v>
<v t="ekr.20120625092120.12781"><vh>readLines class and generator</vh>
<v t="ekr.20120625092120.12782"><vh>g.readLinesGenerator</vh></v>
<v t="ekr.20120625092120.12783"><vh>class readLinesClass</vh></v>
</v>
</v>
<v t="ekr.20120625092120.12835"><vh>Whitesapce</vh>
<v t="ekr.20120625092120.12799"><vh>wrap_lines</vh>
<v t="ekr.20120625092120.12800"><vh>&lt;&lt; place blank and word on the present line &gt;&gt;</vh></v>
<v t="ekr.20120625092120.12801"><vh>&lt;&lt; place word on a new line &gt;&gt;</vh></v>
</v>
</v>
<v t="ekr.20120625092120.12837"><vh>Wrappers for os.path</vh>
<v t="ekr.20120625092120.12630"><vh>os_path_expandExpression</vh></v>
</v>
<v t="ekr.20120625092120.12812"><vh>ZODB support</vh>
<v t="ekr.20120625092120.12813"><vh>g.init_zodb</vh></v>
</v>
</v>
<v t="ekr.20120625092120.12838"><vh>test</vh></v>
<v t="ekr.20120625092120.12469" descendentVnodeUnknownAttributes="7d71005805000000302e362e3071017d71025808000000616e6e6f7461746571037d710473732e"
expanded="ekr.20120625092120.12646,"><vh>@file leoStandAloneGlobals.py</vh></v>
</vnodes>
<tnodes>
<t tx="ekr.20120625092120.12471"># Don't import this here: it messes up Leo's startup code.
# import leo.core.leoTest as leoTest

try:
    import gc
except ImportError:
    gc = None

try:
    import filecmp
except ImportError: # does not exist in jython.
    filecmp = None

try:
    import gettext
except ImportError: # does not exist in jython.
    gettext = None

if isPython3:
    from functools import reduce

if isPython3:
    import io
    StringIO = io.StringIO
else:
    import cStringIO
    StringIO = cStringIO.StringIO

import imp
import inspect
import operator
import os

# Module 'urllib' has no 'parse' member.
import urllib # pylint: disable=E0611

# Do NOT import pdb here!  We shall define pdb as a _function_ below.
# import pdb

import re
import shutil
import string
import subprocess
# import sys
import tempfile
import time
import traceback
import types

if isPython3:
    # E0611: No name 'parse' in urllib.
    import urllib.parse as urlparse # pylint: disable=E0611
else:
    import urlparse

# import zipfile

# These do not exist in IronPython.
# However, it *is* valid for IronPython to use the Python 2.4 libs!
    # import os
    # import string
    # import tempfile
    # import traceback
    # import types
</t>
<t tx="ekr.20120625092120.12474"></t>
<t tx="ekr.20120625092120.12475">def createTopologyList (c,root=None,useHeadlines=False):

    """Creates a list describing a node and all its descendents"""

    if not root: root = c.rootPosition()
    v = root
    if useHeadlines:
        aList = [(v.numberOfChildren(),v.headString()),]
    else:
        aList = [v.numberOfChildren()]
    child = v.firstChild()
    while child:
        aList.append(g.createTopologyList(c,child,useHeadlines))
        child = child.next()
    return aList
</t>
<t tx="ekr.20120625092120.12476"></t>
<t tx="ekr.20120625092120.12477"># New in Leo 4.6:
# g.findAtTabWidthDirectives, g.findLanguageDirectives and
# g.get_directives_dict use re module for faster searching.
</t>
<t tx="ekr.20120625092120.12478">def comment_delims_from_extension(filename):

    """
    Return the comment delims corresponding to the filename's extension.

    &gt;&gt;&gt; import leo.core.leoGlobals as g
    &gt;&gt;&gt; g.comment_delims_from_extension(".py")
    ('#', '', '')

    &gt;&gt;&gt; g.comment_delims_from_extension(".c")
    ('//', '/*', '*/')

    &gt;&gt;&gt; g.comment_delims_from_extension(".html")
    ('', '&lt;!--', '--&gt;')

    """

    if filename.startswith('.'):
        # Python 2.6 changes how splitext works.
        root,ext = None,filename
    else:
        root, ext = os.path.splitext(filename)
    if ext == '.tmp':
        root, ext = os.path.splitext(root)

    language = g.app.extension_dict.get(ext[1:])
    if ext:
        return g.set_delims_from_language(language)
    else:
        g.trace("unknown extension: %s, filename: %s, root: %s" % (
            repr(ext),repr(filename),repr(root)))
        return '','',''
</t>
<t tx="ekr.20120625092120.12479">g_tabwidth_pat = re.compile(r'(^@tabwidth)',re.MULTILINE)

def findTabWidthDirectives(c,p):

    '''Return the language in effect at position p.'''

    if c is None:
        return # c may be None for testing.

    w = None
    # 2009/10/02: no need for copy arg to iter
    for p in p.self_and_parents():
        if w: break
        for s in p.h,p.b:
            if w: break
            anIter = g_tabwidth_pat.finditer(s)
            for m in anIter:
                word = m.group(0)
                i = m.start(0)
                j = g.skip_ws(s,i + len(word))
                junk,w = g.skip_long(s,j)
                if w == 0: w = None
    return w
</t>
<t tx="ekr.20120625092120.12480">g_language_pat = re.compile(r'(^@language)',re.MULTILINE)

def findLanguageDirectives(c,p):

    '''Return the language in effect at position p.'''

    trace = False and not g.unitTesting

    if c is None:
        return # c may be None for testing. 
    if c.target_language:
        language = c.target_language.lower()
    else:
        language = 'python'
    found = False
    # 2009/10/02: no need for copy arg to iter.
    for p in p.self_and_parents():
        if found: break
        for s in p.h,p.b:
            if found: break
            anIter = g_language_pat.finditer(s)
            for m in anIter:
                word = m.group(0)
                i = m.start(0)
                j = i + len(word)
                k = g.skip_line(s,j)
                language = s[j:k].strip()
                found = True

    if trace: g.trace(language)
    return language
</t>
<t tx="ekr.20120625092120.12481"># Called from the syntax coloring method that colorizes section references.

def findReference(c,name,root):

    '''Find the section definition for name.

    If a search of the descendants fails,
    and an ancestor is an @root node,
    search all the descendants of the @root node.
    '''

    for p in root.subtree():
        assert(p!=root)
        if p.matchHeadline(name) and not p.isAtIgnoreNode():
            return p

    # New in Leo 4.7: expand the search for @root trees.
    for p in root.self_and_parents():
        d = g.get_directives_dict(p)
        if 'root' in d:
            for p2 in p.subtree():
                if p2.matchHeadline(name) and not p2.isAtIgnoreNode():
                    return p2

    # g.trace("not found:",name,root)
    return c.nullPosition()
</t>
<t tx="ekr.20120625092120.12482"># The caller passes [root_node] or None as the second arg.
# This allows us to distinguish between None and [None].

g_noweb_root = re.compile('&lt;'+'&lt;'+'*'+'&gt;'+'&gt;'+'=',re.MULTILINE)

def get_directives_dict(p,root=None,scanToCursor=False):

    """Scan p for @directives found in globalDirectiveList.

    Returns a dict containing the stripped remainder of the line
    following the first occurrence of each recognized directive"""

    trace = False and not g.unitTesting
    verbose = False
    if trace: g.trace('*'*20,p.h)

    if root: root_node = root[0]
    d = {}

    # Do this every time so plugins can add directives.
    pat = g.compute_directives_re()
    directives_pat = re.compile(pat,re.MULTILINE)

    # The headline has higher precedence because it is more visible.
    for kind,s in (('head',p.h),('body',p.b)):
        anIter = directives_pat.finditer(s)
        for m in anIter:
            word = m.group(0)[1:] # Omit the @
            i = m.start(0)
            if (
                # 2012/03/9: Special case @language directive in the body.
                (kind == 'body' and scanToCursor and word.strip() == 'language')
                or word.strip() not in d
            ):
                j = i + 1 + len(word)
                k = g.skip_line(s,j)
                val = s[j:k].strip()
                if j &lt; len(s) and s[j] not in (' ','\t','\n'):
                    # g.es_print('invalid character after directive',s[max(0,i-1):k-1],color='red')
                    # if trace:g.trace(word,repr(val),s[i:i+20])
                    pass # Not a valid directive: just ignore it.
                else:
                    directive_word = word.strip()
                    if directive_word == 'language':
                        if kind == 'body' and scanToCursor:
                            # 2012/03/09:Only add preceding @language directives.
                            c = p.v.context
                            w = c.frame.body.bodyCtrl
                            ins = w.getInsertPoint()
                            i1,i2 = g.getLine(s,i)
                            if trace: g.trace(kind,directive_word,val)
                            if ins &gt;= i2:
                                d[directive_word] = val
                        else:
                            d[directive_word] = val
                    else:
                        if directive_word in ('root-doc', 'root-code'):
                            d['root'] = val # in addition to optioned version
                        d[directive_word] = val
                        
                    # g.trace(kind,directive_word,val)

                    if trace: g.trace(word.strip(),kind,repr(val))
                    # A special case for @path in the body text of @&lt;file&gt; nodes.
                    # Don't give an actual warning: just set some flags.
                    if kind == 'body' and word.strip() == 'path' and p.isAnyAtFileNode():
                        g.app.atPathInBodyWarning = p.h
                        d['@path_in_body'] = p.h
                        if trace: g.trace('@path in body',p.h)

    if root:
        anIter = g_noweb_root.finditer(p.b)
        for m in anIter:
            if root_node:
                d["root"]=0 # value not immportant
            else:
                g.es('%s= may only occur in a topmost node (i.e., without a parent)' % (
                    g.angleBrackets('*')))
            break

    if trace and verbose: g.trace('%4d' % (len(p.h) + len(p.b)),g.callers(5))
    return d
</t>
<t tx="ekr.20120625092120.12483">def compute_directives_re ():

    '''Return an re pattern which will match all Leo directives.'''

    global globalDirectiveList

    aList = ['^@%s' % z for z in globalDirectiveList
                if z != 'others']

    if 0: # 2010/02/01
        # The code never uses this, and this regex is broken
        # because it can confuse g.get_directives_dict.
        # @others can have leading whitespace.
        aList.append(r'^\s@others\s')

    return '|'.join(aList)
</t>
<t tx="ekr.20120625092120.12484">def get_directives_dict_list(p,scanToCursor=False):

    """Scans p and all its ancestors for directives.

    Returns a list of dicts containing pointers to
    the start of each directive"""

    trace = False and not g.unitTesting

    # if trace: time1 = g.getTime()

    result = []
    p1 = p.copy()

    for p in p1.self_and_parents():
        if p.hasParent(): root = None
        else:             root = [p.copy()]
        result.append(g.get_directives_dict(p,
            root=root,
            scanToCursor=scanToCursor and p == p1))

    # if trace:
        # n = len(p1.h) + len(p1.b)
        # g.trace('%4d %s' % (n,g.timeSince(time1)))

    return result
</t>
<t tx="ekr.20120625092120.12485">def getLanguageFromAncestorAtFileNode(p):
    
    '''Return the language in effect as determined
    by the file extension of the nearest enclosing @&lt;file&gt; node.
    '''
    
    for p in p.self_and_parents():
        if p.isAnyAtFileNode():
            name = p.anyAtFileNodeName()
            junk,ext = g.os_path_splitext(name)
            ext = ext[1:] # strip the leading .
            language = g.app.extension_dict.get(ext)
            
            # g.trace('found extension',p.h,ext,language)
            return language
    
    return None
</t>
<t tx="ekr.20120625092120.12486">def getOutputNewline (c=None,name=None):

    '''Convert the name of a line ending to the line ending itself.

    Priority:
    - Use name if name given
    - Use c.config.output_newline if c given,
    - Otherwise use g.app.config.output_newline.'''

    if name: s = name
    elif c:  s = c.config.output_newline
    else:    s = app.config.output_newline

    if not s: s = ''
    s = s.lower()
    if s in ( "nl","lf"): s = '\n'
    elif s == "cr": s = '\r'
    elif s == "platform": s = os.linesep  # 12/2/03: emakital
    elif s == "crlf": s = "\r\n"
    else: s = '\n' # Default for erroneous values.
    # g.trace(c,name,c.config.output_newline,'returns',repr(s))

    if g.isPython3:
        s = str(s)
    return s
</t>
<t tx="ekr.20120625092120.12487">def scanAtCommentAndAtLanguageDirectives(aList):

    '''Scan aList for @comment and @language directives.

    @comment should follow @language if both appear in the same node.'''

    trace = False and not g.unitTesting
    lang = None

    for d in aList:

        comment = d.get('comment')
        language = d.get('language')

        # Important: assume @comment follows @language.
        if language:
            # if g.unitTesting: g.trace('language',language)
            lang,delim1,delim2,delim3 = g.set_language(language,0)

        if comment:
            # if g.unitTesting: g.trace('comment',comment)
            delim1,delim2,delim3 = g.set_delims_from_string(comment)

        if comment or language:
            delims = delim1,delim2,delim3
            d = {'language':lang,'comment':comment,'delims':delims}
            if trace: g.trace(d)
            return d

    if trace: g.trace(repr(None))
    return None
</t>
<t tx="ekr.20120625092120.12488">def scanAtEncodingDirectives(aList):

    '''Scan aList for @encoding directives.'''

    for d in aList:
        encoding = d.get('encoding')
        if encoding and g.isValidEncoding(encoding):
            # g.trace(encoding)
            return encoding
        elif encoding and not g.app.unitTesting:
            g.es("invalid @encoding:",encoding,color="red")

    return None
</t>
<t tx="ekr.20120625092120.12489">def scanAtHeaderDirectives(aList):

    '''scan aList for @header and @noheader directives.'''

    for d in aList:
        if d.get('header') and d.get('noheader'):
            g.es_print("conflicting @header and @noheader directives",color='red')
</t>
<t tx="ekr.20120625092120.12490">def scanAtLineendingDirectives(aList):

    '''Scan aList for @lineending directives.'''

    for d in aList:

        e = d.get('lineending')
        if e in ("cr","crlf","lf","nl","platform"):
            lineending = g.getOutputNewline(name=e)
            return lineending
        # else:
            # g.es("invalid @lineending directive:",e,color="red")

    return None
</t>
<t tx="ekr.20120625092120.12491">def scanAtPagewidthDirectives(aList,issue_error_flag=False):

    '''Scan aList for @pagewidth directives.'''

    for d in aList:
        s = d.get('pagewidth')
        if s is not None:
            i, val = g.skip_long(s,0)
            if val != None and val &gt; 0:
                # g.trace(val)
                return val
            else:
                if issue_error_flag and not g.app.unitTesting:
                    g.es("ignoring @pagewidth",s,color="red")

    return None
</t>
<t tx="ekr.20120625092120.12492">def scanAtPathDirectives(c,aList):

    path = c.scanAtPathDirectives(aList)
    return path

def scanAllAtPathDirectives(c,p):

    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
    return path
</t>
<t tx="ekr.20120625092120.12493">def scanAtRootDirectives(aList):

    '''Scan aList for @root directives.'''

    for d in aList:
        s = d.get('root')
        if s is not None:
            i, mode = g.scanAtRootOptions(s,0)
            g.trace(mode)
            return mode

    return None
</t>
<t tx="ekr.20120625092120.12494">def scanAtRootOptions (s,i,err_flag=False):

    # The @root has been eaten when called from tangle.scanAllDirectives.
    if g.match(s,i,"@root"):
        i += len("@root")
        i = g.skip_ws(s,i)

    mode = None 
    while g.match(s,i,'-'):
        &lt;&lt; scan another @root option &gt;&gt;

    if mode == None:
        doc = app.config.at_root_bodies_start_in_doc_mode
        mode = g.choose(doc,"doc","code")

    # g.trace(mode,g.callers(3))

    return i,mode
</t>
<t tx="ekr.20120625092120.12495">i += 1 ; err = -1

if g.match_word(s,i,"code"): # Just match the prefix.
    if not mode: mode = "code"
    elif err_flag: g.es("modes conflict in:",g.get_line(s,i))
elif g.match(s,i,"doc"): # Just match the prefix.
    if not mode: mode = "doc"
    elif err_flag: g.es("modes conflict in:",g.get_line(s,i))
else:
    err = i-1

# Scan to the next minus sign.
while i &lt; len(s) and s[i] not in (' ','\t','\n','-'):
    i += 1

if err &gt; -1 and err_flag:
    z_opt = s[err:i]
    z_line = g.get_line(s,i)
    g.es("unknown option:",z_opt,"in",z_line)
</t>
<t tx="ekr.20120625092120.12496">def scanAtTabwidthDirectives(aList,issue_error_flag=False):

    '''Scan aList for @tabwidth directives.'''

    for d in aList:
        s = d.get('tabwidth')
        if s is not None:
            junk,val = g.skip_long(s,0)
            if val not in (None,0):
                return val
            else:
                if issue_error_flag and not g.app.unitTesting:
                    g.es("ignoring @tabwidth",s,color="red")
    return None

def scanAllAtTabWidthDirectives(c,p):

    '''Scan p and all ancestors looking for @tabwidth directives.'''

    if c and p:
        aList = g.get_directives_dict_list(p)
        val = g.scanAtTabwidthDirectives(aList)
        ret = g.choose(val is None,c.tab_width,val)
    else:
        ret = None
    # g.trace(ret,p and p.h,ret)
    return ret
</t>
<t tx="ekr.20120625092120.12497">def scanAtWrapDirectives(aList,issue_error_flag=False):

    '''Scan aList for @wrap and @nowrap directives.'''

    for d in aList:
        if d.get('wrap') is not None:
            return True
        elif d.get('nowrap') is not None:
            return False

    return None

def scanAllAtWrapDirectives(c,p):

    '''Scan p and all ancestors looking for @wrap/@nowrap directives.'''

    if c and p:
        default = c and c.config.getBool("body_pane_wraps")
        aList = g.get_directives_dict_list(p)

        val = g.scanAtWrapDirectives(aList)
        ret = g.choose(val is None,default,val)
    else:
        ret = None
    # g.trace(ret,p.h)
    return ret
</t>
<t tx="ekr.20120625092120.12498">def scanDirectives(c,p=None):

    return c.scanAllDirectives(p)
</t>
<t tx="ekr.20120625092120.12499">def scanForAtIgnore(c,p):

    """Scan position p and its ancestors looking for @ignore directives."""

    if g.app.unitTesting:
        return False # For unit tests.

    for p in p.self_and_parents():
        d = g.get_directives_dict(p)
        if 'ignore' in d:
            return True

    return False
</t>
<t tx="ekr.20120625092120.12500">def scanForAtLanguage(c,p):

    """Scan position p and p's ancestors looking only for @language and @ignore directives.

    Returns the language found, or c.target_language."""

    # Unlike the code in x.scanAllDirectives, this code ignores @comment directives.

    if c and p:
        for p in p.self_and_parents():
            d = g.get_directives_dict(p)
            if 'language' in d:
                z = d["language"]
                language,delim1,delim2,delim3 = g.set_language(z,0)
                return language

    return c.target_language
</t>
<t tx="ekr.20120625092120.12501">def scanForAtSettings(p):

    """Scan position p and its ancestors looking for @settings nodes."""

    for p in p.self_and_parents():
        h = p.h
        h = g.app.config.canonicalizeSettingName(h)
        if h.startswith("@settings"):
            return True

    return False
</t>
<t tx="ekr.20120625092120.12502"># Returns a tuple (single,start,end) of comment delims

def set_delims_from_language(language):

    trace = False and not g.unitTesting

    val = g.app.language_delims_dict.get(language)
    # if language.startswith('huh'): g.pdb()

    if val:
        delim1,delim2,delim3 = g.set_delims_from_string(val)
        if trace: g.trace(repr(language),
            repr(delim1),repr(delim2),repr(delim3),g.callers(5))
        if delim2 and not delim3:
            return '',delim1,delim2
        else: # 0,1 or 3 params.
            return delim1,delim2,delim3
    else:
        return '','','' # Indicate that no change should be made
</t>
<t tx="ekr.20120625092120.12503">def set_delims_from_string(s):

    """Returns (delim1, delim2, delim2), the delims following the @comment directive.

    This code can be called from @language logic, in which case s can point at @comment"""

    # Skip an optional @comment
    tag = "@comment"
    i = 0
    if g.match_word(s,i,tag):
        i += len(tag)

    count = 0 ; delims = ['','','']
    while count &lt; 3 and i &lt; len(s):
        i = j = g.skip_ws(s,i)
        while i &lt; len(s) and not g.is_ws(s[i]) and not g.is_nl(s,i):
            i += 1
        if j == i: break
        delims[count] = s[j:i] or ''
        count += 1

    # 'rr 09/25/02
    if count == 2: # delims[0] is always the single-line delim.
        delims[2] = delims[1]
        delims[1] = delims[0]
        delims[0] = ''

    # 7/8/02: The "REM hack": replace underscores by blanks.
    # 9/25/02: The "perlpod hack": replace double underscores by newlines.
    for i in range(0,3):
        if delims[i]:
            delims[i] = delims[i].replace("__",'\n').replace('_',' ')

    return delims[0], delims[1], delims[2]
</t>
<t tx="ekr.20120625092120.12504">def set_language(s,i,issue_errors_flag=False):

    """Scan the @language directive that appears at s[i:].

    The @language may have been stripped away.

    Returns (language, delim1, delim2, delim3)
    """

    tag = "@language"
    # g.trace(g.get_line(s,i))
    assert(i != None)
    # assert(g.match_word(s,i,tag))
    if g.match_word(s,i,tag):
        i += len(tag)
    # Get the argument.
    i = g.skip_ws(s, i)
    j = i ; i = g.skip_c_id(s,i)
    # Allow tcl/tk.
    arg = s[j:i].lower()
    if app.language_delims_dict.get(arg):
        language = arg
        delim1, delim2, delim3 = g.set_delims_from_language(language)
        return language, delim1, delim2, delim3

    if issue_errors_flag:
        g.es("ignoring:",g.get_line(s,i))

    return None, None, None, None,
</t>
<t tx="ekr.20120625092120.12505">def setDefaultDirectory(c,p,importing=False):

    ''' Return a default directory by scanning @path directives.'''

    name = p.anyAtFileNodeName()
    if name:
        # An absolute path overrides everything.
        d = g.os_path_dirname(name)
        if d and g.os_path_isabs(d):
            return d

    aList = g.get_directives_dict_list(p)
    path = c.scanAtPathDirectives(aList)
        # Returns g.getBaseDirectory(c) by default.
        # However, g.getBaseDirectory can return ''
    if path:
        path = g.os_path_finalize(path)
    else:
        g.checkOpenDirectory(c)
        for d in (c.openDirectory,g.getBaseDirectory(c)):
            # Errors may result in relative or invalid path.
            if d and g.os_path_isabs(d):
                path = d
                break
        else:
            path = ''

    if not importing and not path:
        # This should never happen, but is not serious if it does.
        g.warning("No absolute directory specified anywhere.")

    return path
</t>
<t tx="ekr.20120625092120.12506">def checkOpenDirectory (c):

    if c.openDirectory != c.frame.openDirectory:
        g.error(
            'c.openDirectory != c.frame.openDirectory\n'
            'c.openDirectory: %s\n'
            'c.frame.openDirectory: %s' % (
                c.openDirectory,c.frame.openDirectory))

    if not g.os_path_isabs(c.openDirectory):
        g.error ('relative c.openDirectory: %s' % (
            c.openDirectory))
</t>
<t tx="ekr.20120625092120.12507">def stripPathCruft (path):

    '''Strip cruft from a path name.'''

    if not path:
        return path # Retain empty paths for warnings.

    if len(path) &gt; 2 and (
        (path[0]=='&lt;' and path[-1] == '&gt;') or
        (path[0]=='"' and path[-1] == '"') or
        (path[0]=="'" and path[-1] == "'")
    ):
        path = path[1:-1].strip()

    # We want a *relative* path, not an absolute path.
    return path
</t>
<t tx="ekr.20120625092120.12509">def alert(message,c=None):
    
    '''Raise an alert.
    
    This method is deprecated: use c.alert instead.
    '''

    # The unit tests just tests the args.
    if not g.unitTesting:
        g.es(message)
        g.app.gui.alert(c,message)
</t>
<t tx="ekr.20120625092120.12514">def dump(s):

    out = ""
    for i in s:
        out += str(ord(i)) + ","
    return out

def oldDump(s):

    out = ""
    for i in s:
        if i=='\n':
            out += "[" ; out += "n" ; out += "]"
        if i=='\t':
            out += "[" ; out += "t" ; out += "]"
        elif i==' ':
            out += "[" ; out += " " ; out += "]"
        else: out += i
    return out
</t>
<t tx="ekr.20120625092120.12515">def es_dump (s,n = 30,title=None):

    if title:
        g.es_print('',title)

    i = 0
    while i &lt; len(s):
        aList = ''.join(['%2x ' % (ord(ch)) for ch in s[i:i+n]])
        g.es_print('',aList)
        i += n
</t>
<t tx="ekr.20120625092120.12522">def print_bindings (name,window):

    bindings = window.bind()

    g.pr("\nBindings for", name)
    for b in bindings:
        g.pr(b)
</t>
<t tx="ekr.20120625092120.12523">def printGlobals(message=None):

    # Get the list of globals.
    globs = list(globals())
    globs.sort()

    # Print the list.
    if message:
        leader = "-" * 10
        g.pr(leader, ' ', message, ' ', leader)
    for glob in globs:
        g.pr(glob)
</t>
<t tx="ekr.20120625092120.12524">def printEntireTree(c,tag=''):

    g.pr('printEntireTree','=' * 50)
    g.pr('printEntireTree',tag,'root',c.rootPosition())
    for p in c.all_positions():
        g.pr('..'*p.level(),p.v)
</t>
<t tx="ekr.20120625092120.12525">def printLeoModules(message=None):

    # Create the list.
    mods = []
    for name in sys.modules:
        if name and name[0:3] == "leo":
            mods.append(name)

    # Print the list.
    if message:
        leader = "-" * 10
        g.pr(leader, ' ', message, ' ', leader)
    mods.sort()
    for m in mods:
        g.pr(m,newline=False)
    g.pr('')
</t>
<t tx="ekr.20120625092120.12526">def module_date (mod,format=None):
    theFile = g.os_path_join(app.loadDir,mod.__file__)
    root,ext = g.os_path_splitext(theFile) 
    return g.file_date(root + ".py",format=format)

def plugin_date (plugin_mod,format=None):
    theFile = g.os_path_join(app.loadDir,"..","plugins",plugin_mod.__file__)
    root,ext = g.os_path_splitext(theFile) 
    return g.file_date(root + ".py",format=format)

def file_date (theFile,format=None):
    if theFile and len(theFile)and g.os_path_exists(theFile):
        try:
            n = g.os_path_getmtime(theFile)
            if format == None:
                format = "%m/%d/%y %H:%M:%S"
            return time.strftime(format,time.gmtime(n))
        except (ImportError,NameError):
            pass # Time module is platform dependent.
    return ""
</t>
<t tx="ekr.20120625092120.12527">class redirectClass:

    """A class to redirect stdout and stderr to Leo's log pane."""

    &lt;&lt; redirectClass methods &gt;&gt;

# Create two redirection objects, one for each stream.
redirectStdErrObj = redirectClass()
redirectStdOutObj = redirectClass()

&lt;&lt; define convenience methods for redirecting streams &gt;&gt;
</t>
<t tx="ekr.20120625092120.12528">@others
</t>
<t tx="ekr.20120625092120.12529">def __init__ (self):

    self.old = None
    self.encoding = 'utf-8' # 2019/03/29 For pdb.
</t>
<t tx="ekr.20120625092120.12530">def isRedirected (self):

    return self.old != None
</t>
<t tx="ekr.20120625092120.12531"># For LeoN: just for compatibility.

def flush(self, *args):
    return
</t>
<t tx="ekr.20120625092120.12532">def rawPrint (self,s):

    if self.old:
        self.old.write(s+'\n')
    else:
        g.pr(s)
</t>
<t tx="ekr.20120625092120.12533">def redirect (self,stdout=1):

    if g.app.batchMode:
        # Redirection is futile in batch mode.
        return

    if not self.old:
        if stdout:
            self.old,sys.stdout = sys.stdout,self
        else:
            self.old,sys.stderr = sys.stderr,self
</t>
<t tx="ekr.20120625092120.12534">def undirect (self,stdout=1):

    if self.old:
        if stdout:
            sys.stdout,self.old = self.old,None
        else:
            sys.stderr,self.old = self.old,None
</t>
<t tx="ekr.20120625092120.12535">def write(self,s):

    trace = False

    if self.old:
        if app.log:
            if trace: self.old.write(
                'redirectClass: to log: %s\n' % repr(s))
            app.log.put(s)
        else:
            self.old.write(s +'\n')
    else:
        # Can happen when g.batchMode is True.
        g.pr(s)
</t>
<t tx="ekr.20120625092120.12536">@others
</t>
<t tx="ekr.20120625092120.12537"># Redirect streams to the current log window.
def redirectStderr():
    global redirectStdErrObj
    redirectStdErrObj.redirect(stdout=False)

def redirectStdout():
    global redirectStdOutObj
    redirectStdOutObj.redirect()
</t>
<t tx="ekr.20120625092120.12538"># Restore standard streams.
def restoreStderr():
    global redirectStdErrObj
    redirectStdErrObj.undirect(stdout=False)

def restoreStdout():
    global redirectStdOutObj
    redirectStdOutObj.undirect()
</t>
<t tx="ekr.20120625092120.12539">def stdErrIsRedirected():
    global redirectStdErrObj
    return redirectStdErrObj.isRedirected()

def stdOutIsRedirected():
    global redirectStdOutObj
    return redirectStdOutObj.isRedirected()
</t>
<t tx="ekr.20120625092120.12540"># Send output to original stdout.

def rawPrint(s):

    global redirectStdOutObj

    redirectStdOutObj.rawPrint(s)
</t>
<t tx="ekr.20120625092120.12541">def getIvarsDict(obj):

    '''Return a dictionary of ivars:values for non-methods of obj.'''

    import types

    d = dict(
        [[key,getattr(obj,key)] for key in dir(obj)
            if type (getattr(obj,key)) != types.MethodType])

    # g.pr(g.listToString(sorted(d)))
    return d

def checkUnchangedIvars(obj,d,exceptions=None):

    if not exceptions: exceptions = []
    ok = True

    for key in d:
        if key not in exceptions:
            if getattr(obj,key) != d.get(key):
                g.trace('changed ivar: %s old: %s new: %s' % (
                    key,repr(d.get(key)),repr(getattr(obj,key))))
                ok = False
    return ok
</t>
<t tx="ekr.20120625092120.12542"># Very useful for tracing.

def get_line (s,i):

    nl = ""
    if g.is_nl(s,i):
        i = g.skip_nl(s,i)
        nl = "[nl]"
    j = g.find_line_start(s,i)
    k = g.skip_to_end_of_line(s,i)
    return nl + s[j:k]

# Important: getLine is a completely different function.
# getLine = get_line

def get_line_after (s,i):

    nl = ""
    if g.is_nl(s,i):
        i = g.skip_nl(s,i)
        nl = "[nl]"
    k = g.skip_to_end_of_line(s,i)
    return nl + s[i:k]

getLineAfter = get_line_after
</t>
<t tx="ekr.20120625092120.12544">def print_obj (obj,tag=None,sort=False,verbose=True,indent=''):

    if type(obj) in (type(()),type([])):
        g.print_list(obj,tag,sort,indent)
    elif type(obj) == type({}):
        g.print_dict(obj,tag,verbose,indent)
    else:
        g.pr('%s%s' % (indent,repr(obj).strip()))

def toString (obj,tag=None,sort=False,verbose=True,indent=''):

    if type(obj) in (type(()),type([])):
        return g.listToString(obj,tag,sort,indent)
    elif type(obj) == type({}):
        return g.dictToString(obj,tag,verbose,indent)
    else:
        return '%s%s' % (indent,repr(obj).strip())
</t>
<t tx="ekr.20120625092120.12545">def print_dict(d,tag='',verbose=True,indent=''):

    if not d:
        if tag: g.pr('%s...{}' % tag)
        else:   g.pr('{}')
        return

    n = 6
    for key in sorted(d):
        if type(key) == type(''):
            n = max(n,len(key))
    if tag: g.es('%s...{\n' % tag)
    else:   g.es('{\n')
    for key in sorted(d):
        g.pr("%s%*s: %s" % (indent,n,key,repr(d.get(key)).strip()))
    g.pr('}')

printDict = print_dict

def dictToString(d,tag=None,verbose=True,indent=''):

    if not d:
        if tag: return '%s...{}' % tag
        else:   return '{}'
    n = 6
    for key in sorted(d):
        if g.isString(key):
            n = max(n,len(key))
    lines = ["%s%*s: %s" % (indent,n,key,repr(d.get(key)).strip())
        for key in sorted(d)]
    s = '\n'.join(lines)
    if tag:
        return '%s...{\n%s}\n' % (tag,s)
    else:
        return '{\n%s}\n' % s
</t>
<t tx="ekr.20120625092120.12546">def print_list(aList,tag=None,sort=False,indent=''):

    if not aList:
        if tag: g.pr('%s...[]' % tag)
        else:   g.pr('[]')
        return
    if sort:
        bList = aList[:] # Sort a copy!
        bList.sort()
    else:
        bList = aList
    if tag: g.pr('%s...[' % tag)
    else:   g.pr('[')
    for e in bList:
        g.pr('%s%s' % (indent,repr(e).strip()))
    g.pr(']')

printList = print_list

def listToString(aList,tag=None,sort=False,indent='',toRepr=False):

    if not aList:
        if tag: return '%s...{}' % tag
        else:   return '[]'
    if sort:
        bList = aList[:] # Sort a copy!
        bList.sort()
    else:
        bList = aList
    lines = ["%s%s" % (indent,repr(e).strip()) for e in bList]
    s = '\n'.join(lines)
    if toRepr: s = repr(s)
    if tag:
        return '[%s...\n%s\n]' % (tag,s)
    else:
        return '[%s]' % s
</t>
<t tx="ekr.20120625092120.12547">def print_stack():

    traceback.print_stack()

printStack = print_stack
</t>
<t tx="ekr.20120625092120.12548"></t>
<t tx="ekr.20120625092120.12549">def clear_stats():

    g.trace()

    g.app.statsDict = {}

clearStats = clear_stats
</t>
<t tx="ekr.20120625092120.12550">def print_stats (name=None):

    if name:
        if type(name) != type(""):
            name = repr(name)
    else:
        name = g._callerName(n=2) # Get caller name 2 levels back.

    g.printDict(g.app.statsDict,tag='statistics at %s' % name)

printStats = print_stats
</t>
<t tx="ekr.20120625092120.12551">def stat (name=None):

    """Increments the statistic for name in g.app.statsDict
    The caller's name is used by default.
    """

    d = g.app.statsDict

    if name:
        if type(name) != type(""):
            name = repr(name)
    else:
        name = g._callerName(n=2) # Get caller name 2 levels back.

    # g.trace(name)

    d [name] = 1 + d.get(name,0)
</t>
<t tx="ekr.20120625092120.12552">def getTime():
    return time.clock()

def esDiffTime(message, start):
    delta = time.clock()-start
    g.es('',"%s %6.3f sec." % (message,delta))
    return time.clock()
    
def pause (s):
    g.pr(s)
    i = 0 ; n = long(1000) * long(1000)
    while i &lt; n:
        i += 1

def printDiffTime(message, start):
    delta = time.clock()-start
    g.pr("%s %6.3f sec." % (message,delta))
    return time.clock()

def timeSince(start):
    return "%6.3f sec." % (time.clock()-start)
</t>
<t tx="ekr.20120625092120.12553">class Tracer:

    '''A "debugger" that computes a call graph.

    To trace a function and its callers, put the following at the function's start:

    g.startTracer()
    '''

    @others

def startTracer():

    import sys
    t = g.Tracer()
    sys.settrace(t.tracer)
    return t
</t>
<t tx="ekr.20120625092120.12554">def __init__(self):

    self.callDict = {}
        # Keys are function names.
        # Values are the number of times the function was called by the caller.
    self.calledDict = {}
        # Keys are function names.
        # Values are the total number of times the function was called.

    self.count = 0
    self.inited = False
    self.limit = 2 # 0: no limit, otherwise, limit trace to n entries deep.
    self.stack = []
    self.trace = False
    self.verbose = False # True: print returns as well as calls.
</t>
<t tx="ekr.20120625092120.12555">def computeName (self,frame):

    import inspect

    if not frame: return ''

    code = frame.f_code ; result = []

    module = inspect.getmodule(code)
    if module:
        module_name = module.__name__
        if module_name == 'leo.core.leoGlobals':
            result.append('g')
        else:
            tag = 'leo.core.'
            if module_name.startswith(tag):
                module_name = module_name[len(tag):]
            result.append(module_name)

    try:
        # This can fail during startup.
        self_obj = frame.f_locals.get('self')
        if self_obj: result.append(self_obj.__class__.__name__)
    except Exception:
        pass

    result.append(code.co_name)

    return '.'.join(result)
</t>
<t tx="ekr.20120625092120.12556">def report (self):

    if 0:
        g.pr('\nstack')
        for z in self.stack:
            g.pr(z)

    g.pr('\ncallDict...')

    for key in sorted(self.callDict):

        # Print the calling function.
        g.pr('%d' % (self.calledDict.get(key,0)),key)

        # Print the called functions.
        d = self.callDict.get(key)
        for key2 in sorted(d):
            g.pr('%8d' % (d.get(key2)),key2)
</t>
<t tx="ekr.20120625092120.12557">def stop (self):

    sys.settrace(None)
    self.report()
</t>
<t tx="ekr.20120625092120.12558">def tracer (self, frame, event, arg):

    '''A function to be passed to sys.settrace.'''

    n = len(self.stack)
    if event == 'return': n = max(0,n-1)
    pad = '.' * n

    if event == 'call':
        if not self.inited:
            # Add an extra stack element for the routine containing the call to startTracer.
            self.inited = True
            name = self.computeName(frame.f_back)
            self.updateStats(name)
            self.stack.append(name)
        name = self.computeName(frame)
        if self.trace and (self.limit == 0 or len(self.stack) &lt; self.limit):
            g.trace('%scall' % (pad),name)
        self.updateStats(name)
        self.stack.append(name)
        return self.tracer
    elif event == 'return':
        if self.stack:
            name = self.stack.pop()
            if self.trace and self.verbose and (self.limit == 0 or len(self.stack) &lt; self.limit):
                g.trace('%sret ' % (pad),name)
        else:
            g.trace('return underflow')
            self.stop()
            return None
        if self.stack:
            return self.tracer
        else:
            self.stop()
            return None
    else:
        return self.tracer
</t>
<t tx="ekr.20120625092120.12559">def updateStats (self,name):

    if not self.stack:
        return

    caller = self.stack[-1]
    d = self.callDict.get(caller,{})
        # d is a dict reprenting the called functions.
        # Keys are called functions, values are counts.
    d[name] = 1 + d.get(name,0)
    self.callDict[caller] = d

    # Update the total counts.
    self.calledDict[name] = 1 + self.calledDict.get(name,0)
</t>
<t tx="ekr.20120625092120.12561"># For compatibility with old code.
def computeGlobalConfigDir():
    return g.app.loadManager.computeGlobalConfigDir()
    
def computeHomeDir():
    return g.app.loadManager.computeHomeDir()
    
def computeLeoDir():
    return g.app.loadManager.computeLeoDir()
    
def computeLoadDir():
    return g.app.loadManager.computeLoadDir()
    
def computeMachineName():
    return g.app.loadManager.computeMachineName()
    
def computeStandardDirectories():
    return g.app.loadManager.computeStandardDirectories()
</t>
<t tx="ekr.20120625092120.12562">def chdir (path):

    if not g.os_path_isdir(path):
        path = g.os_path_dirname(path)

    if g.os_path_isdir(path) and g.os_path_exists(path):
        os.chdir(path)
</t>
<t tx="ekr.20120625092120.12563">def create_temp_file (textMode=False):
    '''Return a tuple (theFile,theFileName)

    theFile: a file object open for writing.
    theFileName: the name of the temporary file.'''

    try:
        # fd is an handle to an open file as would be returned by os.open()
        fd,theFileName = tempfile.mkstemp(text=textMode)
        # mode = g.choose(textMode,'w','wb')
        mode = 'w' if textMode else 'wb'
        theFile = os.fdopen(fd,mode)
    except Exception:
        g.es('unexpected exception in g.create_temp_file',color='red')
        g.es_exception()
        theFile,theFileName = None,''

    return theFile,theFileName
</t>
<t tx="ekr.20120625092120.12564">def ensure_extension (name, ext):

    theFile, old_ext = g.os_path_splitext(name)
    if not name:
        return name # don't add to an empty name.
    elif old_ext and old_ext == ext:
        return name
    else:
        return name + ext
</t>
<t tx="ekr.20120625092120.12565"># Handles the conventions applying to the "relative_path_base_directory" configuration option.

def getBaseDirectory(c):

    '''Convert '!' or '.' to proper directory references.'''

    base = app.config.relative_path_base_directory

    if base and base == "!":
        base = app.loadDir
    elif base and base == ".":
        base = c.openDirectory

    if base and g.os_path_isabs(base):
        # Set c.chdir_to_relative_path as needed.
        if not hasattr(c,'chdir_to_relative_path'):
            c.chdir_to_relative_path = c.config.getBool('chdir_to_relative_path')
        # Call os.chdir if requested.
        if c.chdir_to_relative_path:
            os.chdir(base)
        # g.trace(base)
        return base # base need not exist yet.
    else:
        return "" # No relative base given.
</t>
<t tx="ekr.20120625092120.12566">def guessExternalEditor(c=None):
    """ Return a 'sensible' external editor """

    editor = (
        os.environ.get("LEO_EDITOR") or
        os.environ.get("EDITOR"))
        # or g.app.db and g.app.db.get("LEO_EDITOR") or
        # c and c.config.getString('external_editor'))

    if editor: return editor

    # fallbacks
    platform = sys.platform.lower()
    if platform.startswith('win'):
        return "notepad"
    elif platform.startswith('linux'):
        return 'gedit'
    else:
        g.es('''No editor set.\nPlease set LEO_EDITOR or EDITOR environment variable,''')
        return None
</t>
<t tx="ekr.20120625092120.12567">def is_binary_file (f):

    if g.isPython3:
        return f and isinstance(f,io.BufferedIOBase)
    else:
        g.internalError('g.is_binary_file called from Python 2.x code')
</t>
<t tx="ekr.20120625092120.12568">def is_sentinel (line,delims):

    &lt;&lt; is_sentinel doc tests &gt;&gt;

    delim1,delim2,delim3 = delims

    line = line.lstrip()

    if delim1:
        return line.startswith(delim1+'@')
    elif delim2 and delim3:
        i = line.find(delim2+'@')
        j = line.find(delim3)
        return 0 == i &lt; j
    else:
        g.trace("can't happen. delims: %s" % repr(delims),color="red")
        return False
</t>
<t tx="ekr.20120625092120.12569">"""

Return True if line starts with a sentinel comment.

&gt;&gt;&gt; import leo.core.leoGlobals as g
&gt;&gt;&gt; py_delims = g.comment_delims_from_extension('.py')
&gt;&gt;&gt; g.is_sentinel("#@+node",py_delims)
True
&gt;&gt;&gt; g.is_sentinel("#comment",py_delims)
False

&gt;&gt;&gt; c_delims = g.comment_delims_from_extension('.c')
&gt;&gt;&gt; g.is_sentinel("//@+node",c_delims)
True
&gt;&gt;&gt; g.is_sentinel("//comment",c_delims)
False

&gt;&gt;&gt; html_delims = g.comment_delims_from_extension('.html')
&gt;&gt;&gt; g.is_sentinel("&lt;!--@+node--&gt;",html_delims)
True
&gt;&gt;&gt; g.is_sentinel("&lt;!--comment--&gt;",html_delims)
False

"""
</t>
<t tx="ekr.20120625092120.12570"># This is a generalization of os.makedir.

def makeAllNonExistentDirectories (theDir,c=None,force=False,verbose=True):

    """Attempt to make all non-existent directories"""

    trace = False and not g.unitTesting
    testing = trace # True: don't actually make the directories.

    if force:
        create = True # Bug fix: g.app.config will not exist during startup.
    elif c:
        create = c.config and c.config.create_nonexistent_directories
    else:
        create = (g.app and g.app.config and
            g.app.config.create_nonexistent_directories)

    if c: theDir = g.os_path_expandExpression(theDir,c=c)

    dir1 = theDir = g.os_path_normpath(theDir)

    ok = g.os_path_isdir(dir1) and g.os_path_exists(dir1)

    if trace: g.trace('ok',ok,'create',create,'force',force,dir1,g.callers())

    if ok:
        return ok
    elif not force and not create:
        if trace:
            g.trace('did not create: force and create are both false')
        return False

    if trace:
        g.trace('\n',theDir,'\n',g.callers(4))
        # g.trace('c exists: %s force: %s create: %s dir: %s' % (
            # c is not None,force,create,theDir))

    # Split theDir into all its component parts.
    paths = []
    while len(theDir) &gt; 0:
        head,tail=g.os_path_split(theDir)
        if len(tail) == 0:
            paths.append(head)
            break
        else:
            paths.append(tail)
            theDir = head
    path = ""
    paths.reverse()
    if trace: g.trace('paths:',paths)
    for s in paths:
        path = g.os_path_finalize_join(path,s)
        if not g.os_path_exists(path):
            try:
                if testing:
                    g.trace('***making',path)
                else:
                    os.mkdir(path)
                if verbose and not testing and not g.app.unitTesting:
                    # g.trace('***callers***',g.callers(5))
                    g.es_print("created directory:",path,color='red')
            except Exception:
                # g.trace(g.callers())
                if verbose: g.es_print("exception creating directory:",path,color='red')
                g.es_exception()
                return None
    return dir1 # All have been created.
</t>
<t tx="ekr.20120625092120.12571">def makePathRelativeTo (fullPath,basePath):

    if fullPath.startswith(basePath):
        s = fullPath[len(basePath):]
        if s.startswith(os.path.sep):
            s = s[len(os.path.sep):]
        return s
    else:
        return fullPath
</t>
<t tx="ekr.20120625092120.12572">def openWithFileName(fileName,old_c=None,gui=None):

    """Create a Leo Frame for the indicated fileName if the file exists.

    returns the commander of the newly-opened outline.
    """
    
    return g.app.loadManager.loadLocalFile(fileName,gui,old_c)
</t>
<t tx="ekr.20120625092120.12573">def readFileIntoString (fn,
    encoding='utf-8',
    kind=None,
    mode='rb',
    raw=False,
    silent=False,
):

    '''Return the contents of the file whose full path is fn.

    Return (s,e)
    s is the string, converted to unicode, or None if there was an error.
    e the encoding line for Python files: it is usually None.
    '''

    try:
        e = None
        f = open(fn,mode)
        s = f.read()
        f.close()
        if raw:
            return s,None
        else:
            # Python's encoding comments override everything else.
            if s:
                junk,ext = g.os_path_splitext(fn)
                if ext == '.py':
                    e = g.getPythonEncodingFromString(s)
            s = g.toUnicode(s,encoding=e or encoding)
            return s,e
    except IOError:
        # Translate 'can not open' and kind, but not fn.
        # g.trace(g.callers(5))
        if not silent:
            if kind:
                g.es('can not open','',kind,fn,color='red')
            else:
                g.es('can not open',fn,color='red')
    except Exception:
        g.trace('unexpected exception reading %s' % (fn),color='red')
        g.es_exception()

    return None,None
</t>
<t tx="ekr.20120625092120.12574">@ Stephen P. Schaefer 9/7/2002

The Unix readline() routine delivers "\r\n" line end strings verbatim,
while the windows versions force the string to use the Unix convention
of using only "\n". This routine causes the Unix readline to do the
same.
@c

def readlineForceUnixNewline(f,fileName=None):

    try:
        s = f.readline()
        # g.trace(repr(s))
    except UnicodeDecodeError:
        g.trace('UnicodeDecodeError: %s' % (fileName),f,g.callers())
        s = g.u('')

    if len(s) &gt;= 2 and s[-2] == "\r" and s[-1] == "\n":
        s = s[0:-2] + "\n"
    return s
</t>
<t tx="ekr.20120625092120.12575">def recursiveUNLSearch(unlList, c, depth=0, p=None, maxdepth=0, maxp=None):
    """try and move to unl in the commander c
    
    NOTE: maxdepth is max depth seen in recursion so far, not a limit on
          how fast we will recurse.  So it should default to 0 (zero).
    """
        
    if g.unitTesting:
        g.app.unitTestDict['g.recursiveUNLSearch']=True
        return True, maxdepth, maxp

    def moveToP(c, p):
        c.expandAllAncestors(p)
        c.selectPosition(p)
        c.redraw()
        c.frame.bringToFront()
        
    found, maxdepth, maxp = recursiveUNLFind(unlList, c, depth, p, maxdepth, maxp)
    
    if maxp:
        moveToP(c, maxp)
        
    return found, maxdepth, maxp

def recursiveUNLFind(unlList, c, depth=0, p=None, maxdepth=0, maxp=None):
    """Internal part of recursiveUNLSearch which doesn't change the
    selected position or call c.frame.bringToFront()"""
    
    if depth == 0:
        nds = c.rootPosition().self_and_siblings()
        unlList = [i.replace('--%3E', '--&gt;') for i in unlList if i.strip()]
        # drop empty parts so "--&gt;node name" works
    else:
        nds = p.children()

    for i in nds:

        if unlList[depth] == i.h:

            if depth+1 == len(unlList):  # found it
                #X moveToP(c, i)
                return True, maxdepth, i
            else:
                if maxdepth &lt; depth+1:
                    maxdepth = depth+1
                    maxp = i.copy()
                found, maxdepth, maxp = g.recursiveUNLSearch(unlList, c, depth+1, i, maxdepth, maxp)
                if found:
                    return found, maxdepth, maxp
                # else keep looking through nds

    if depth == 0 and maxp:  # inexact match
        #X moveToP(c, maxp)
        g.es('Partial UNL match')

    return False, maxdepth, maxp
</t>
<t tx="ekr.20120625092120.12576">def sanitize_filename(s):

    """Prepares string s to be a valid file name:

    - substitute '_' whitespace and characters used special path characters.
    - eliminate all other non-alphabetic characters.
    - strip leading and trailing whitespace.
    - return at most 128 characters."""

    result = ""
    for ch in s.strip():
        if ch in string.ascii_letters:
            result += ch
        elif ch in string.whitespace: # Translate whitespace.
            result += '_'
        elif ch in ('.','\\','/',':'): # Translate special path characters.
            result += '_'
    while 1:
        n = len(result)
        result = result.replace('__','_')
        if len(result) == n:
            break
    result = result.strip()
    return result [:128]
</t>
<t tx="ekr.20120625092120.12577">def setGlobalOpenDir (fileName):

    if fileName:
        g.app.globalOpenDir = g.os_path_dirname(fileName)
        # g.es('current directory:',g.app.globalOpenDir)
</t>
<t tx="ekr.20120625092120.12579"></t>
<t tx="ekr.20120625092120.12580"># This is part of the tangle code.

def update_file_if_changed(c,file_name,temp_name):

    """Compares two files.

    If they are different, we replace file_name with temp_name.
    Otherwise, we just delete temp_name. Both files should be closed."""

    if g.os_path_exists(file_name):
        if filecmp.cmp(temp_name, file_name):
            kind = 'unchanged'
            ok = g.utils_remove(temp_name)
        else:
            kind = '***updating'
            mode = g.utils_stat(file_name)
            ok = g.utils_rename(c,temp_name,file_name,mode)
    else:
        kind = 'creating'
        # 2010/02/04: g.utils_rename no longer calls
        # makeAllNonExistentDirectories
        head, tail = g.os_path_split(file_name)
        ok = True
        if head:
            ok = g.makeAllNonExistentDirectories(head,c=c)
        if ok:
            ok = g.utils_rename(c,temp_name,file_name)

    if ok:
        g.es('','%12s: %s' % (kind,file_name))
    else:
        g.es("rename failed: no file created!",color="red")
        g.es('',file_name," may be read-only or in use")
</t>
<t tx="ekr.20120625092120.12581">def utils_remove (fileName,verbose=True):

    try:
        os.remove(fileName)
        return True
    except Exception:
        if verbose:
            g.es("exception removing:",fileName)
            g.es_exception()
        return False
</t>
<t tx="ekr.20120625092120.12582">def utils_rename (c,src,dst,verbose=True):

    '''Platform independent rename.'''

    # Don't call g.makeAllNonExistentDirectories.
    # It's not right to do this here!!

    # head, tail = g.os_path_split(dst)
    # if head: g.makeAllNonExistentDirectories(head,c=c)

    try:
        shutil.move(src,dst)
        return True
    except Exception:
        if verbose:
            g.es('exception renaming',src,'to',dst,color='red')
            g.es_exception(full=False)
        return False
</t>
<t tx="ekr.20120625092120.12583">def utils_chmod (fileName,mode,verbose=True):

    if mode is None:
        return

    try:
        os.chmod(fileName,mode)
    except Exception:
        if verbose:
            g.es("exception in os.chmod",fileName)
            g.es_exception()
</t>
<t tx="ekr.20120625092120.12584">def utils_stat (fileName):

    '''Return the access mode of named file, removing any setuid, setgid, and sticky bits.'''

    try:
        mode = (os.stat(fileName))[0] &amp; (7*8*8 + 7*8 + 7) # 0777
    except Exception:
        mode = None

    return mode
</t>
<t tx="ekr.20120625092120.12585">lastObjectCount = 0
lastObjectsDict = {}
lastTypesDict = {}
lastFunctionsDict = {}

@others
</t>
<t tx="ekr.20120625092120.12586">def clearAllIvars (o):

    """Clear all ivars of o, a member of some class."""

    if o:
        o.__dict__.clear()
</t>
<t tx="ekr.20120625092120.12587">def collectGarbage():

    try:
        if not g.trace_gc_inited:
            g.enable_gc_debug()

        if g.trace_gc_verbose or g.trace_gc_calls:
            g.pr('collectGarbage:')

        gc.collect()
    except Exception:
        pass

    # Only init once, regardless of what happens.
    g.trace_gc_inited = True
</t>
<t tx="ekr.20120625092120.12588">no_gc_message = False

def enable_gc_debug(event=None):

    if gc:
        if g.trace_gc_verbose:
            gc.set_debug(
                gc.DEBUG_STATS | # prints statistics.
                gc.DEBUG_LEAK | # Same as all below.
                gc.DEBUG_COLLECTABLE |
                gc.DEBUG_UNCOLLECTABLE |
                gc.DEBUG_INSTANCES |
                gc.DEBUG_OBJECTS |
                gc.DEBUG_SAVEALL
            )
        # else:
            # gc.set_debug(gc.DEBUG_STATS)
    elif not g.no_gc_message:
        g.no_gc_message = True
        g.es('can not import gc module',color='blue')
</t>
<t tx="ekr.20120625092120.12589"># Formerly called from unit tests.

def printGc(tag=None):

    if not g.trace_gc: return None

    tag = tag or g._callerName(n=2)

    printGcObjects(tag=tag)
    printGcRefs(tag=tag)

    if g.trace_gc_verbose:
        printGcVerbose(tag=tag)
</t>
<t tx="ekr.20120625092120.12590">def printGcRefs (tag=''):

    refs = gc.get_referrers(app.windowList[0])
    g.pr('-' * 30,tag)

    if g.trace_gc_verbose:
        g.pr("refs of", app.windowList[0])
        for ref in refs:
            g.pr(type(ref))
    else:
        g.pr("%d referers" % len(refs))
</t>
<t tx="ekr.20120625092120.12591">def printGcAll (tag=''):

    # Suppress warning about keywords arg not supported in sort.

    tag = tag or g._callerName(n=2)
    d = {} ; objects = gc.get_objects()
    if not g.unitTesting:
        g.pr('-' * 30)
        g.pr('%s: %d objects' % (tag,len(objects)))

    for obj in objects:
        t = type(obj)
        if t == 'instance':
            try: t = obj.__class__
            except Exception: pass
        # if type(obj) == type(()):
            # g.pr(id(obj),repr(obj))
            
        # 2011/02/28: Some types may not be hashable.
        try:
            d[t] = d.get(t,0) + 1
        except TypeError:
            d = {}

    if 1: # Sort by n
        items = list(d.items())
        items.sort(key=lambda x: x[1])
            # key is a function that extracts args.
        if not g.unitTesting:
            for z in items:
                g.pr('%40s %7d' % (z[0],z[1]))
    else: # Sort by type
        for t in sorted(d):
            g.pr('%40s %7d' % (t,d.get(t)))
</t>
<t tx="ekr.20120625092120.12592">def printGcObjects(tag=''):

    '''Print newly allocated objects.'''

    tag = tag or g._callerName(n=2)
    global lastObjectCount

    try:
        n = len(gc.garbage)
        n2 = len(gc.get_objects())
        delta = n2-lastObjectCount
        if delta == 0: return
        lastObjectCount = n2

        &lt;&lt; print number of each type of object &gt;&gt;
        if 0:
            &lt;&lt; print added functions &gt;&gt;

    except Exception:
        traceback.print_exc()

printNewObjects = pno = printGcObjects

</t>
<t tx="ekr.20120625092120.12593">global lastTypesDict
typesDict = {}

for obj in gc.get_objects():
    t = type(obj)
    if t == 'instance' and t != types.UnicodeType:
        try: t = obj.__class__
        except Exception: pass
    if t != types.FrameType:
        r = repr(t) # was type(obj) instead of repr(t)
        n = typesDict.get(r,0) 
        typesDict[r] = n + 1

# Create the union of all the keys.
keys = {}
for key in lastTypesDict:
    if key not in typesDict:
        keys[key]=None

empty = True
for key in keys:
    n3 = lastTypesDict.get(key,0)
    n4 = typesDict.get(key,0)
    delta2 = n4-n3
    if delta2 != 0:
        empty = False
        break

if not empty:
    g.pr('-' * 30)
    g.pr("%s: garbage: %d, objects: %d, delta: %d" % (tag,n,n2,delta))

    if 0:
        for key in sorted(keys):
            n1 = lastTypesDict.get(key,0)
            n2 = typesDict.get(key,0)
            delta2 = n2-n1
            if delta2 != 0:
                g.pr("%+6d =%7d %s" % (delta2,n2,key))

lastTypesDict = typesDict
typesDict = {}
</t>
<t tx="ekr.20120625092120.12594"># import types
import inspect

global lastFunctionsDict

funcDict = {}

# Don't print more than 50 objects.
n = 0
for obj in gc.get_objects():
    if type(obj) == types.FunctionType:
        n += 1

for obj in gc.get_objects():
    if type(obj) == types.FunctionType:
        key = repr(obj) # Don't create a pointer to the object!
        funcDict[key]=None 
        if n &lt; 50 and key not in lastFunctionsDict:
            g.pr(obj)
            args, varargs, varkw,defaults  = inspect.getargspec(obj)
            g.pr("args", args)
            if varargs: g.pr("varargs",varargs)
            if varkw: g.pr("varkw",varkw)
            if defaults:
                g.pr("defaults...")
                for s in defaults: g.pr(s)

lastFunctionsDict = funcDict
funcDict = {}
</t>
<t tx="ekr.20120625092120.12595">def printGcSummary (tag=''):

    tag = tag or g._callerName(n=2)

    g.enable_gc_debug()

    try:
        n = len(gc.garbage)
        n2 = len(gc.get_objects())
        s = '%s: printGCSummary: garbage: %d, objects: %d' % (tag,n,n2)
        g.pr(s)
    except Exception:
        traceback.print_exc()
</t>
<t tx="ekr.20120625092120.12596"># WARNING: the id trick is not proper because newly allocated objects
#          can have the same address as old objets.

def printGcVerbose(tag=''):

    tag = tag or g._callerName(n=2)
    global lastObjectsDict
    objects = gc.get_objects()
    newObjects = [o for o in objects if id(o) not in lastObjectsDict]
    lastObjectsDict = {}
    for o in objects:
        lastObjectsDict[id(o)]=o

    dicts = 0 ; seqs = 0

    i = 0 ; n = len(newObjects)
    while i &lt; 100 and i &lt; n:
        o = newObjects[i]
        if type(o) == type({}): dicts += 1
        elif type(o) in (type(()),type([])):
            #g.pr(id(o),repr(o))
            seqs += 1
        #else:
        #    g.pr(o)
        i += 1
    g.pr('=' * 40)
    g.pr('dicts: %d, sequences: %d' % (dicts,seqs))
    g.pr("%s: %d new, %d total objects" % (tag,len(newObjects),len(objects)))
    g.pr('-' * 40)
</t>
<t tx="ekr.20120625092120.12597"></t>
<t tx="ekr.20120625092120.12598"></t>
<t tx="ekr.20120625092120.12599">@ Enables the "idle" hook.
After enableIdleTimeHook is called, Leo will call the "idle" hook
approximately every g.idleTimeDelay milliseconds.
@c

def enableIdleTimeHook(idleTimeDelay=500):
    
    # g.trace(idleTimeDelay)

    if not g.app.idleTimeHook:
        # g.trace('start idle-time hook: %d msec.' % idleTimeDelay)
        # Start idle-time processing only after the first idle-time event.
        g.app.gui.setIdleTimeHook(g.idleTimeHookHandler)
        g.app.afterHandler = g.idleTimeHookHandler

    # 1/4/05: Always update these.
    g.app.idleTimeHook = True
    g.app.idleTimeDelay = idleTimeDelay # Delay in msec.
</t>
<t tx="ekr.20120625092120.12600"># Disables the "idle" hook.
def disableIdleTimeHook():

    g.app.idleTimeHook = False
</t>
<t tx="ekr.20120625092120.12601"># An internal routine used to dispatch the "idle" hook.
trace_count = 0

def idleTimeHookHandler(*args,**keys):

    trace = False and not g.unitTesting

    if trace: # Do not use g.trace here!
        global trace_count ; trace_count += 1
        if 0:
            g.pr('idleTimeHookHandler',trace_count)
        else:
            if trace_count % 10 == 0:
                for z in g.app.windowList:
                    c = z.c
                    g.pr("idleTimeHookHandler",trace_count,c.shortFileName())

    # New for Python 2.3: may be called during shutdown.
    if g.app.killed: return

    for z in g.app.windowList:
        c = z.c
        # Do NOT compute c.currentPosition.
        # This would be a MAJOR leak of positions.
        g.doHook("idle",c=c)

    # Requeue this routine after g.app.idleTimeDelay msec.
    # (This delay is set by g.enableIdleTimeHook.)
    # Faster requeues overload the system.
    if g.app.idleTimeHook:
        g.app.gui.setIdleTimeHookAfterDelay(g.idleTimeHookHandler)
        g.app.afterHandler = g.idleTimeHookHandler
    else:
        g.app.afterHandler = None
</t>
<t tx="ekr.20120625092120.12602">def dummy_act_on_node(c,p,event):
    pass

# This dummy definition keeps pylint happy.
# Plugins can change this.
act_on_node = dummy_act_on_node
</t>
<t tx="ekr.20120625092120.12603">@ This global function calls a hook routine.  Hooks are identified by the tag param.
Returns the value returned by the hook routine, or None if the there is an exception.

We look for a hook routine in three places:
1. c.hookFunction
2. app.hookFunction
3. leoPlugins.doPlugins()
We set app.hookError on all exceptions.  Scripts may reset app.hookError to try again.
@c

def doHook(tag,*args,**keywords):

    trace = False ; verbose = False

    if g.app.killed or g.app.hookError: # or (g.app.gui and g.app.gui.isNullGui):
        return None

    if args:
        # A minor error in Leo's core.
        g.pr("***ignoring args param.  tag = %s" % tag)

    if not g.app.config.use_plugins:
        
        if tag in ('open0','start1'):
            s = "Plugins disabled: use_plugins is 0 in a leoSettings.leo file."
            g.es_print(s,color="blue")
        return None

    # Get the hook handler function.  Usually this is doPlugins.
    c = keywords.get("c")
    f = (c and c.hookFunction) or g.app.hookFunction

    if trace and (verbose or tag != 'idle'):
        g.trace('tag',tag,'f',f and f.__name__)

    if not f:
        g.app.hookFunction = f = g.app.pluginsController.doPlugins

    try:
        # Pass the hook to the hook handler.
        # g.pr('doHook',f.__name__,keywords.get('c'))
        return f(tag,keywords)
    except Exception:
        g.es_exception()
        g.app.hookError = True # Supress this function.
        g.app.idleTimeHook = False # Supress idle-time hook
        return None # No return value
</t>
<t tx="ekr.20120625092120.12604">class command:
    """ Decorator to create global commands """
    def __init__(self, name, **kwargs):
        """ Registration for command 'name'

        kwargs reserved for future use (shortcut, button, ...?)

        """
        self.name = name
        self.args = kwargs

    def __call__(self,func):
        # register command for all future commanders
        g.app.global_commands_dict[self.name] = func

        # ditto for all current commanders
        for co in g.app.commanders():
            co.k.registerCommand(self.name,shortcut = None, func = func, pane='all',verbose=False)        

        return func


</t>
<t tx="ekr.20120625092120.12605">childrenModifiedSet = set()
contentModifiedSet = set()
</t>
<t tx="ekr.20120625092120.12606"># Important: we can not define g.pc here!

</t>
<t tx="ekr.20120625092120.12607">def loadOnePlugin (pluginName,verbose=False):
    pc = g.app.pluginsController
    return pc.loadOnePlugin(pluginName,verbose=verbose)

def registerExclusiveHandler(tags,fn):
    pc = g.app.pluginsController
    return pc.registerExclusiveHandler(tags,fn)

def registerHandler (tags,fn):
    pc = g.app.pluginsController
    return pc.registerHandler(tags,fn)

def plugin_signon(module_name,verbose=False):
    pc = g.app.pluginsController
    return pc.plugin_signon(module_name,verbose)

def unloadOnePlugin (moduleOrFileName,verbose=False):
    pc = g.app.pluginsController
    return pc.unloadOnePlugin(moduleOrFileName,verbose)

def unregisterHandler (tags,fn):
    pc = g.app.pluginsController
    return pc.unregisterHandler(tags,fn)
</t>
<t tx="ekr.20120625092120.12608">def getHandlersForTag(tags):
    pc = g.app.pluginsController
    return pc.getHandlersForTag(tags)

def getLoadedPlugins():
    pc = g.app.pluginsController
    return pc.getLoadedPlugins()

def getPluginModule(moduleName):
    pc = g.app.pluginsController
    return pc.getPluginModule(moduleName)

def pluginIsLoaded(fn):
    pc = g.app.pluginsController
    return pc.isLoaded(fn)

</t>
<t tx="ekr.20120625092120.12610">def choose(cond, a, b): # warning: evaluates all arguments

    if cond: return a
    else: return b
</t>
<t tx="ekr.20120625092120.12612">def ecnl(tabName='Log'):
    g.ecnls(1,tabName)

def ecnls(n,tabName='Log'):
    log = app.log
    if log and not log.isNull:
        while log.newlines &lt; n:
            g.enl(tabName)

def enl(tabName='Log'):
    log = app.log
    if log and not log.isNull:
        log.newlines += 1
        log.putnl(tabName)
</t>
<t tx="ekr.20120625092120.12614">def es(*args,**keys):

    '''Put all non-keyword args to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''
    
    trace = False

    if not app or app.killed: return
    log = app.log
    
    if trace: # Effective for debugging.
        print()
        print('***es',args,keys)
        print('***es','logInited',app.logInited,'log',log and id(log))
        print('***es',g.callers())

    # Compute the effective args.
    d = {'color':'black','commas':False,'newline':True,'spaces':True,'tabName':'Log'}
    d = g.doKeywordArgs(keys,d)
    color = d.get('color')
    if color == 'suppress': return # New in 4.3.
    tabName = d.get('tabName') or 'Log'
    newline = d.get('newline')
    s = g.translateArgs(args,d)

    if app.batchMode:
        if app.log:
            app.log.put(s)
    elif g.unitTesting:
        if log and not log.isNull:
            # This makes the output of unit tests match the output of scripts.
            # s = g.toEncodedString(s,'ascii')
            g.pr(s,newline=newline)
    elif log and app.logInited:
        log.put(s,color=color,tabName=tabName)
        for ch in s:
            if ch == '\n': log.newlines += 1
            else: log.newlines = 0
        if newline:
            g.ecnl(tabName=tabName) # only valid here
    # 2012/05/20: Don't do this.
    # elif app.logInited:
        # print(s.rstrip()) # Happens only rarely.
    elif newline:
        app.logWaiting.append((s+'\n',color),)
    else:
        app.logWaiting.append((s,color),)
</t>
<t tx="ekr.20120625092120.12615"># see: http://www.diveintopython.org/xml_processing/unicode.html

def es_print(*args,**keys):

    '''Print all non-keyword args, and put them to the log pane.
    The first, third, fifth, etc. arg translated by g.translateString.
    Supports color, comma, newline, spaces and tabName keyword arguments.
    '''

    g.pr(*args,**keys)

    if not g.app.unitTesting:
        g.es(*args,**keys)
</t>
<t tx="ekr.20120625092120.12616">def es_trace(*args,**keys):

    if args:
        try:
            s = args[0]
            g.trace(g.toEncodedString(s,'ascii'))
        except Exception:
            pass

    g.es(*args,**keys)
</t>
<t tx="ekr.20120625092120.12618">class posList(list):
    &lt;&lt; docstring for posList &gt;&gt;
    def __init__ (self,c,aList=None):
        self.c = c
        list.__init__(self) # Init the base class
        if aList is None:
            for p in c.all_positions():
                self.append(p.copy())
        else:
            for p in aList:
                self.append(p.copy())

    def dump (self,sort=False,verbose=False):
        if verbose: return g.listToString(self,sort=sort)
        else: return g.listToString([p.h for p in self],sort=sort)

    def select(self,pat,regex=False,removeClones=True):
        '''Return a new posList containing all positions
        in self that match the given pattern.'''
        c = self.c ; aList = []
        if regex:
            for p in self:
                if re.match(pat,p.h):
                    aList.append(p.copy())
        else:
            for p in self:
                if p.h.find(pat) != -1:
                    aList.append(p.copy())
        if removeClones:
            aList = self.removeClones(aList)
        return posList(c,aList)

    def removeClones(self,aList):
        seen = {} ; aList2 = []
        for p in aList:
            if p.v not in seen:
                seen[p.v] = p.v
                aList2.append(p)
        return aList2
</t>
<t tx="ekr.20120625092120.12619">'''A subclass of list for creating and selecting lists of positions.

    This is deprecated, use leoNodes.poslist instead!

    aList = g.posList(c)
        # Creates a posList containing all positions in c.

    aList = g.posList(c,aList2)
        # Creates a posList from aList2.

    aList2 = aList.select(pattern,regex=False,removeClones=True)
        # Creates a posList containing all positions p in aList
        # such that p.h matches the pattern.
        # The pattern is a regular expression if regex is True.
        # if removeClones is True, all positions p2 are removed
        # if a position p is already in the list and p2.v == p.v.

    aList.dump(sort=False,verbose=False)
        # Prints all positions in aList, sorted if sort is True.
        # Prints p.h, or repr(p) if verbose is True.
'''
</t>
<t tx="ekr.20120625092120.12624">def windows():
    return app.windowList
</t>
<t tx="ekr.20120625092120.12630">def os_path_expandExpression (s,**keys):

    '''Expand {{anExpression}} in c's context.'''

    trace = False
    
    s1 = s
    c = keys.get('c')
    if not c:
        g.trace('can not happen: no c',g.callers())
        return s

    if not s:
        if trace: g.trace('no s')
        return ''

    i = s.find('{{')
    j = s.find('}}')
    if -1 &lt; i &lt; j:
        exp = s[i+2:j].strip()
        if exp:
            try:
                import os
                import sys
                p = c.p
                d = {'c':c,'g':g,'p':p,'os':os,'sys':sys,}
                val = eval(exp,d)
                s = s[:i] + str(val) + s[j+2:]
                if trace: g.trace('returns',s)
            except Exception:
                g.trace(g.callers())
                g.es_exception(full=True, c=c, color='red')

    return s
</t>
<t tx="ekr.20120625092120.12647">def scanError(s):

    g.es('',s)
</t>
<t tx="ekr.20120625092120.12648"># A quick and dirty sscanf.  Understands only %s and %d.

def scanf (s,pat):
    count = pat.count("%s") + pat.count("%d")
    pat = pat.replace("%s","(\S+)")
    pat = pat.replace("%d","(\d+)")
    parts = re.split(pat,s)
    result = []
    for part in parts:
        if len(part) &gt; 0 and len(result) &lt; count:
            result.append(part)
    # g.trace("scanf returns:",result)
    return result

if 0: # testing
    g.scanf("1.0","%d.%d",)
</t>
<t tx="ekr.20120625092120.12649">@ These scanners all call g.scanError() directly or indirectly, so they
will call g.es if they find an error. g.scanError() also bumps
c.tangleCommands.errors, which is harmless if we aren't tangling, and
useful if we are.

These routines are called by the Import routines and the Tangle routines.
</t>
<t tx="ekr.20120625092120.12650"># Scans past a block comment (an old_style C comment).

def skip_block_comment (s,i):

    assert(g.match(s,i,"/*"))
    j = i ; i += 2 ; n = len(s)

    k = s.find("*/",i)
    if k == -1:
        g.scanError("Run on block comment: " + s[j:i])
        return n
    else: return k + 2
</t>
<t tx="ekr.20120625092120.12651">@ This code is called only from the import logic, so we are allowed to
try some tricks. In particular, we assume all braces are matched in
#if blocks.
@c

def skip_braces(s,i):

    '''Skips from the opening to the matching brace.

    If no matching is found i is set to len(s)'''

    # start = g.get_line(s,i)
    assert(g.match(s,i,'{'))
    level = 0 ; n = len(s)
    while i &lt; n:
        c = s[i]
        if c == '{':
            level += 1 ; i += 1
        elif c == '}':
            level -= 1
            if level &lt;= 0: return i
            i += 1
        elif c == '\'' or c == '"': i = g.skip_string(s,i)
        elif g.match(s,i,'//'): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,'/*'): i = g.skip_block_comment(s,i)
        # 7/29/02: be more careful handling conditional code.
        elif g.match_word(s,i,"#if") or g.match_word(s,i,"#ifdef") or g.match_word(s,i,"#ifndef"):
            i,delta = g.skip_pp_if(s,i)
            level += delta
        else: i += 1
    return i
</t>
<t tx="ekr.20120625092120.12652">@ 08-SEP-2002 DTHEIN: Added for PHP import support
Skips from the opening to the matching . If no matching is found i is set to len(s).

This code is called only from the import logic, and only for PHP imports.
@c

def skip_php_braces(s,i):

    # start = g.get_line(s,i)
    assert(g.match(s,i,'{'))
    level = 0 ; n = len(s)
    while i &lt; n:
        c = s[i]
        if c == '{':
            level += 1 ; i += 1
        elif c == '}':
            level -= 1
            if level &lt;= 0: return i + 1
            i += 1
        elif c == '\'' or c == '"': i = g.skip_string(s,i)
        elif g.match(s,i,"&lt;&lt;&lt;"): i = g.skip_heredoc_string(s,i)
        elif g.match(s,i,'//') or g.match(s,i,'#'): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,'/*'): i = g.skip_block_comment(s,i)
        else: i += 1
    return i
</t>
<t tx="ekr.20120625092120.12653">def skip_parens(s,i):

    '''Skips from the opening ( to the matching ).

    If no matching is found i is set to len(s)'''

    level = 0 ; n = len(s)
    assert(g.match(s,i,'('))
    while i &lt; n:
        c = s[i]
        if c == '(':
            level += 1 ; i += 1
        elif c == ')':
            level -= 1
            if level &lt;= 0:  return i
            i += 1
        elif c == '\'' or c == '"': i = g.skip_string(s,i)
        elif g.match(s,i,"//"): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,"/*"): i = g.skip_block_comment(s,i)
        else: i += 1
    return i
</t>
<t tx="ekr.20120625092120.12654">def skip_pascal_begin_end(s,i):

    '''Skips from begin to matching end.
    If found, i points to the end. Otherwise, i &gt;= len(s)
    The end keyword matches begin, case, class, record, and try.'''

    assert(g.match_c_word(s,i,"begin"))
    level = 1 ; i = g.skip_c_id(s,i) # Skip the opening begin.
    while i &lt; len(s):
        ch = s[i]
        if ch =='{' : i = g.skip_pascal_braces(s,i)
        elif ch =='"' or ch == '\'': i = g.skip_pascal_string(s,i)
        elif g.match(s,i,"//"): i = g.skip_line(s,i)
        elif g.match(s,i,"(*"): i = g.skip_pascal_block_comment(s,i)
        elif g.match_c_word(s,i,"end"):
            level -= 1
            if level == 0:
                # lines = s[i1:i+3] ; g.trace('\n' + lines + '\n')
                return i
            else: i = g.skip_c_id(s,i)
        elif g.is_c_id(ch):
            j = i ; i = g.skip_c_id(s,i) ; name = s[j:i]
            if name in ["begin", "case", "class", "record", "try"]:
                level += 1
        else: i += 1
    return i
</t>
<t tx="ekr.20120625092120.12655"># Scans past a pascal comment delimited by (* and *).

def skip_pascal_block_comment(s,i):

    j = i
    assert(g.match(s,i,"(*"))
    i = s.find("*)",i)
    if i &gt; -1: return i + 2
    else:
        g.scanError("Run on comment" + s[j:i])
        return len(s)
</t>
<t tx="ekr.20120625092120.12656">def skip_pascal_string(s,i):

    j = i ; delim = s[i] ; i += 1
    assert(delim == '"' or delim == '\'')

    while i &lt; len(s):
        if s[i] == delim:
            return i + 1
        else: i += 1

    g.scanError("Run on string: " + s[j:i])
    return i
</t>
<t tx="ekr.20120625092120.12657">@ 08-SEP-2002 DTHEIN:  added function skip_heredoc_string
A heredoc string in PHP looks like:

  &lt;&lt;&lt;EOS
  This is my string.
  It is mine. I own it.
  No one else has it.
  EOS

It begins with &lt;&lt;&lt; plus a token (naming same as PHP variable names).
It ends with the token on a line by itself (must start in first position.

@c
def skip_heredoc_string(s,i):

    j = i
    assert(g.match(s,i,"&lt;&lt;&lt;"))
    m = re.match("\&lt;\&lt;\&lt;([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)", s[i:])
    if (None == m):
        i += 3
        return i

    # 14-SEP-2002 DTHEIN: needed to add \n to find word, not just string
    delim = m.group(1) + '\n' 

    i = g.skip_line(s,i) # 14-SEP-2002 DTHEIN: look after \n, not before
    n = len(s)
    while i &lt; n and not g.match(s,i,delim):
        i = g.skip_line(s,i) # 14-SEP-2002 DTHEIN: move past \n

    if i &gt;= n:
        g.scanError("Run on string: " + s[j:i])
    elif g.match(s,i,delim):
        i += len(delim)
    return i
</t>
<t tx="ekr.20120625092120.12658"># Now handles continuation lines and block comments.

def skip_pp_directive(s,i):

    while i &lt; len(s):
        if g.is_nl(s,i):
            if g.escaped(s,i): i = g.skip_nl(s,i)
            else: break
        elif g.match(s,i,"//"): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,"/*"): i = g.skip_block_comment(s,i)
        else: i += 1
    return i
</t>
<t tx="ekr.20120625092120.12659"># Skips an entire if or if def statement, including any nested statements.

def skip_pp_if(s,i):

    start_line = g.get_line(s,i) # used for error messages.
    # g.trace(start_line)

    assert(
        g.match_word(s,i,"#if") or
        g.match_word(s,i,"#ifdef") or
        g.match_word(s,i,"#ifndef"))

    i = g.skip_line(s,i)
    i,delta1 = g.skip_pp_part(s,i)
    i = g.skip_ws(s,i)
    if g.match_word(s,i,"#else"):
        i = g.skip_line(s,i)
        i = g.skip_ws(s,i)
        i,delta2 = g.skip_pp_part(s,i)
        if delta1 != delta2:
            g.es("#if and #else parts have different braces:",start_line)
    i = g.skip_ws(s,i)
    if g.match_word(s,i,"#endif"):
        i = g.skip_line(s,i)
    else:
        g.es("no matching #endif:",start_line)

    # g.trace(delta1,start_line)
    return i,delta1
</t>
<t tx="ekr.20120625092120.12660"># Skip to an #else or #endif.  The caller has eaten the #if, #ifdef, #ifndef or #else

def skip_pp_part(s,i):

    # g.trace(g.get_line(s,i))

    delta = 0
    while i &lt; len(s):
        c = s[i]
        if 0:
            if c == '\n':
                g.trace(delta,g.get_line(s,i))
        if g.match_word(s,i,"#if") or g.match_word(s,i,"#ifdef") or g.match_word(s,i,"#ifndef"):
            i,delta1 = g.skip_pp_if(s,i)
            delta += delta1
        elif g.match_word(s,i,"#else") or g.match_word(s,i,"#endif"):
            return i,delta
        elif c == '\'' or c == '"': i = g.skip_string(s,i)
        elif c == '{':
            delta += 1 ; i += 1
        elif c == '}':
            delta -= 1 ; i += 1
        elif g.match(s,i,"//"): i = g.skip_line(s,i)
        elif g.match(s,i,"/*"): i = g.skip_block_comment(s,i)
        else: i += 1
    return i,delta
</t>
<t tx="ekr.20120625092120.12661">def skip_python_string(s,i,verbose=True):

    if g.match(s,i,"'''") or g.match(s,i,'"""'):
        j = i ; delim = s[i]*3 ; i += 3
        k = s.find(delim,i)
        if k &gt; -1: return k+3
        if verbose:
            g.scanError("Run on triple quoted string: " + s[j:i])
        return len(s)
    else:
        return g.skip_string(s,i)
</t>
<t tx="ekr.20120625092120.12662">def skip_string(s,i,verbose=True):

    '''Scan forward to the end of a string.
    New in Leo 4.4.2 final: give error only if verbose is True'''

    j = i ; delim = s[i] ; i += 1
    assert(delim == '"' or delim == '\'')

    n = len(s)
    while i &lt; n and s[i] != delim:
        if s[i] == '\\' : i += 2
        else: i += 1

    if i &gt;= n:
        if verbose:
            g.scanError("Run on string: " + s[j:i])
    elif s[i] == delim:
        i += 1

    # g.trace(s[j:i])
    return i
</t>
<t tx="ekr.20120625092120.12663"># Skips to the next semicolon that is not in a comment or a string.

def skip_to_semicolon(s,i):

    n = len(s)
    while i &lt; n:
        c = s[i]
        if c == ';': return i
        elif c == '\'' or c == '"' : i = g.skip_string(s,i)
        elif g.match(s,i,"//"): i = g.skip_to_end_of_line(s,i)
        elif g.match(s,i,"/*"): i = g.skip_block_comment(s,i)
        else: i += 1
    return i
</t>
<t tx="ekr.20120625092120.12664">def skip_typedef(s,i):

    n = len(s)
    while i &lt; n and g.is_c_id(s[i]):
        i = g.skip_c_id(s,i)
        i = g.skip_ws_and_nl(s,i)
    if g.match(s,i,'{'):
        i = g.skip_braces(s,i)
        i = g.skip_to_semicolon(s,i)
    return i
</t>
<t tx="ekr.20120625092120.12691"></t>
<t tx="ekr.20120625092120.12692">def executeFile(filename, options= ''):

    if not os.access(filename, os.R_OK): return

    cwd = os.getcwdu()
    fdir, fname = g.os_path_split(filename)
    
    # New in Leo 4.10: alway use subprocess.
    def subprocess_wrapper(cmdlst):

        # g.trace(cmdlst, fdir)
        # g.trace(subprocess.list2cmdline([cmdlst]))
        p = subprocess.Popen(cmdlst, cwd=fdir,
            universal_newlines=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        stdo, stde = p.communicate()
        return p.wait(), stdo, stde
    
    rc, so, se = subprocess_wrapper('%s %s %s'%(sys.executable, fname, options))
    if rc:
        g.pr('return code', rc)
    g.pr(so, se)
</t>
<t tx="ekr.20120625092120.12693">def findNodeInChildren(c,p,headline):

    """Search for a node in v's tree matching the given headline."""

    for p in p.children():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findNodeInTree(c,p,headline):

    """Search for a node in v's tree matching the given headline."""

    for p in p.subtree():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findNodeAnywhere(c,headline):

    for p in c.all_unique_positions():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()

def findTopLevelNode(c,headline):

    for p in c.rootPosition().self_and_siblings():
        if p.h.strip() == headline.strip():
            return p.copy()
    return c.nullPosition()
</t>
<t tx="ekr.20120625092120.12694">def getScript (c,p,useSelectedText=True,forcePythonSentinels=True,useSentinels=True):

    '''Return the expansion of the selected text of node p.
    Return the expansion of all of node p's body text if
    p is not the current node or if there is no text selection.'''

    # New in Leo 4.6 b2: use a pristine atFile handler
    # so there can be no conflict with c.atFileCommands.
    # at = c.atFileCommands
    import leo.core.leoAtFile as leoAtFile
    at = leoAtFile.atFile(c)

    w = c.frame.body.bodyCtrl
    p1 = p and p.copy()
    if not p:
        p = c.p
    try:
        if g.app.inBridge:
            s = p.b
        elif p1:
            s = p.b # Bug fix: Leo 8.8.4.
        elif p == c.p:
            if useSelectedText and w.hasSelection():
                s = w.getSelectedText()
            else:
                s = w.getAllText()
        else:
            s = p.b
        # Remove extra leading whitespace so the user may execute indented code.
        s = g.removeExtraLws(s,c.tab_width)
        if s.strip():
            g.app.scriptDict["script1"]=s
            # Important: converts unicode to utf-8 encoded strings.
            script = at.writeFromString(p.copy(),s,
                forcePythonSentinels=forcePythonSentinels,
                useSentinels=useSentinels)
            script = script.replace("\r\n","\n") # Use brute force.
            # Important, the script is an **encoded string**, not a unicode string.
            g.app.scriptDict["script2"]=script
        else: script = ''
    except Exception:
        g.es_print("unexpected exception in g.getScript")
        g.es_exception()
        script = ''

    # g.trace(type(script),repr(script))
    return script
</t>
<t tx="ekr.20120625092120.12695">def handleScriptException (c,p,script,script1):

    g.es("exception executing script",color='blue')

    full = c.config.getBool('show_full_tracebacks_in_scripts')

    fileName, n = g.es_exception(full=full)

    if p and not script1 and fileName == "&lt;string&gt;":
        c.goToScriptLineNumber(p,script,n)

    &lt;&lt; dump the lines near the error &gt;&gt;
</t>
<t tx="ekr.20120625092120.12696">if g.os_path_exists(fileName):
    f = open(fileName)
    lines = f.readlines()
    f.close()
else:
    lines = g.splitLines(script)

s = '-' * 20
g.es_print('',s)

# Print surrounding lines.
i = max(0,n-2)
j = min(n+2,len(lines))
while i &lt; j:
    ch = g.choose(i==n-1,'*',' ')
    s = "%s line %d: %s" % (ch,i+1,lines[i])
    g.es('',s,newline=False)
    i += 1
</t>
<t tx="ekr.20120625092120.12697">def initScriptFind(c,findHeadline,changeHeadline=None,firstNode=None,
    script_search=True,script_change=True):

    import leo.core.leoGlobals as g

    # Find the scripts.
    p = c.p
    tm = c.testManager
    find_p = tm.findNodeInTree(p,findHeadline)
    if find_p:
        find_text = find_p.b
    else:
        g.es("no Find script node",color="red")
        return
    if changeHeadline:
        change_p = tm.findNodeInTree(p,changeHeadline)
    else:
        change_p = None
    if change_p:
        change_text = change_p.b
    else:
        change_text = ""
    # g.pr(find_p,change_p)

    # Initialize the find panel.
    c.script_search_flag = script_search
    c.script_change_flag = script_change and change_text
    if script_search:
        c.find_text = find_text.strip() + "\n"
    else:
        c.find_text = find_text
    if script_change:
        c.change_text = change_text.strip() + "\n"
    else:
        c.change_text = change_text
    c.frame.findPanel.init(c)
    c.showFindPanel()
</t>
<t tx="ekr.20120625092120.12698"></t>
<t tx="ekr.20120625092120.12699">def python_tokenize (s,line_numbers=True):

    '''Tokenize string s and return a list of tokens (kind,value,line_number)

    where kind is in ('comment,'id','nl','other','string','ws').
    '''

    result,i,line_number = [],0,0
    while i &lt; len(s):
        progress = j = i
        ch = s[i]
        if ch == '\n':
            kind,i = 'nl',i+1
        elif ch in ' \t':
            kind = 'ws'
            while i &lt; len(s) and s[i] in ' \t':
                i += 1
        elif ch == '#':
            kind,i = 'comment',g.skip_to_end_of_line(s,i)
        elif ch in '"\'':
            kind,i = 'string',g.skip_python_string(s,i,verbose=False)
        elif ch == '_' or ch.isalpha():
            kind,i = 'id',g.skip_id(s,i)
        else:
            kind,i = 'other',i+1
            
        assert progress &lt; i and j == progress
        val = s[j:i]
        assert val
        
        if line_numbers:
            line_number += val.count('\n') # A comment.
            result.append((kind,val,line_number),)
        else:
            result.append((kind,val),)

    return result
</t>
<t tx="ekr.20120625092120.12709">def toEncodedStringWithErrorCode (s,encoding,reportErrors=False):

    ok = True

    if g.isUnicode(s):
        try:
            s = s.encode(encoding,"strict")
        except Exception:
            if reportErrors: g.reportBadChars(s,encoding)
            s = s.encode(encoding,"replace")
            ok = False
    return s, ok
</t>
<t tx="ekr.20120625092120.12710">def toUnicodeWithErrorCode (s,encoding,reportErrors=False):

    ok = True
    if g.isPython3: f = str
    else: f = unicode
    if s is None:
        s = g.u('')
    if not g.isUnicode(s):
        try:
            s = f(s,encoding,'strict')
        except Exception:
            if reportErrors:
                g.reportBadChars(s,encoding)
            s = f(s,encoding,'replace')
            ok = False
    return s,ok
</t>
<t tx="ekr.20120625092120.12711"></t>
<t tx="ekr.20120625092120.12712">def getTestVars ():

    d = g.app.unitTestDict
    c = d.get('c')
    p = d.get('p')
    # Indicate that getTestVars has run.
    # This is an indirect test that some unit test has run.
    d['getTestVars'] = True
    return c,p and p.copy()
</t>
<t tx="ekr.20120625092120.12713">def findTestScript(c,h,where=None,warn=True):

    if where:
        p = g.findNodeAnywhere(c,where)
        if p:
            p = g.findNodeInTree(c,p,h)
    else:
        p = g.findNodeAnywhere(c,h)

    if p:
        return g.getScript(c,p)
    else:
        if warn: g.trace('Not found',h)
        return None
</t>
<t tx="ekr.20120625092120.12714">kinds = '(file|ftp|gopher|http|https|mailto|news|nntp|prospero|telnet|wais)'
url_regex = re.compile(r"""%s://[^\s'"]+[\w=/]""" % (kinds))
</t>
<t tx="ekr.20120625092120.12715">def computeFileUrl(fn,c=None,p=None):
    
    '''Compute finalized url for filename fn.
    This involves adding url escapes and evaluating Leo expressions.'''
    
    
    # Module 'urllib' has no 'parse' member.
    unquote = urllib.parse.unquote if isPython3 else urllib.unquote # pylint: disable=E1101

    # First, replace special characters (especially %20, by their equivalent).
    url = unquote(fn)

    # Finalize the path *before* parsing the url.
    i = url.find('~')
    if i &gt; -1:
        # Expand '~' and handle Leo expressions.
        path = url[i:]
        path = g.os_path_expanduser(path)
        path = g.os_path_expandExpression(path,c=c)
        path = g.os_path_finalize(path)
        url = url[:i] + path
    else:
        # Handle Leo expressions.
        tag = 'file://'
        tag2 = 'file:///'
        if sys.platform.startswith('win') and url.startswith(tag2):
            path = url[len(tag2):].lstrip()
        elif url.startswith(tag):
            path = url[len(tag):].lstrip()
        else:
            path = url
        path = g.os_path_expandExpression(path,c=c)
        # Handle ancestor @path directives.
        if c and c.openDirectory:
            base = c.getNodePath(p)
            path = g.os_path_finalize_join(c.openDirectory,base,path)
        else:
            path = g.os_path_finalize(path)
        url = '%s%s' % (tag,path)

    return url
</t>
<t tx="ekr.20120625092120.12716">def getUrlFromNode(p):
    
    '''Get an url from node p:
        
    1. Use the headline if it contains a valid url.
    2. Otherwise, look *only* at the first line of the body.
    '''
    
    if not p: return None
    c = p.v.context
    assert c
    
    table = [p.h,g.splitLines(p.b)[0] if p.b else '']
    table = [s[4:] if g.match_word(s,0,'@url') else s for s in table]
    table = [s.strip() for s in table if s.strip()]
        
    # First, check for url's with an explicit scheme.
    for s in table:
        if g.isValidUrl(s):
            return s
                
    # Next check for existing file and add a file:// scheme.
    for s in table:
        tag = 'file://'
        url = computeFileUrl(s,c=c,p=p)
        if url.startswith(tag):
            fn = url[len(tag):].lstrip()
            fn = fn.split('#',1)[0]
            # g.trace('fn',fn)
            if g.os_path_isfile(fn):
                # Return the *original* url, with a file:// scheme.
                # g.handleUrl will call computeFileUrl again.
                return 'file://'+s

    # Finally, check for local url's.
    for s in table:
        if s.startswith("#"):
            return s
            
    return None
</t>
<t tx="ekr.20120625092120.12717">@ Most browsers should handle the following urls:
  ftp://ftp.uu.net/public/whatever.
  http://localhost/MySiteUnderDevelopment/index.html
  file:///home/me/todolist.html
@c

def handleUrl(url,c=None,p=None):
    
    # E1101: Module 'urllib' has no 'parse' member
    unquote = urllib.parse.unquote if isPython3 else urllib.unquote # pylint: disable=E1101
    
    trace = False and not g.unitTesting ; verbose = False
    if c and not p:
        p = c.p
        
    if url.startswith('@url'):
        url = url[4:].lstrip()

    try:
        tag = 'file://'
        if url.startswith(tag) and not url.startswith(tag+'#'):
            # Finalize the path *before* parsing the url.
            url = g.computeFileUrl(url,c=c,p=p)

        parsed   = urlparse.urlparse(url)

        # pylint: disable=E1103
        # E1103: Instance of 'ParseResult' has no 'fragment' member
        # E1103: Instance of 'ParseResult' has no 'netloc' member
        # E1103: Instance of 'ParseResult' has no 'path' member
        # E1103: Instance of 'ParseResult' has no 'scheme' member
        fragment = parsed.fragment 
        netloc   = parsed.netloc
        path     = parsed.path
        scheme   = parsed.scheme

        if netloc:
            leo_path = os.path.join(netloc, path)
            # "readme.txt" gets parsed into .netloc...
        else:
            leo_path = path
            
        if leo_path.endswith('\\'): leo_path = leo_path[:-1]
        if leo_path.endswith('/'):  leo_path = leo_path[:-1]
            
        if trace and verbose:
            print()
            g.trace('url          ',url)
            g.trace('c.frame.title',c.frame.title)
            g.trace('leo_path     ',leo_path)
            g.trace('parsed.netloc',netloc)
            g.trace('parsed.path  ',path)
            g.trace('parsed.scheme',scheme)

        if c and scheme in ('', 'file'):
            
            if not leo_path:
                if '--&gt;' in path:
                    g.recursiveUNLSearch(unquote(path).split("--&gt;"), c)
                    return
                if not path and fragment:
                    g.recursiveUNLSearch(unquote(fragment).split("--&gt;"), c)
                    return
    
            # .leo file
            if leo_path.lower().endswith('.leo') and os.path.exists(leo_path):
                # Immediately end editing, so that typing in the new window works properly.
                c.endEditing()
                c.redraw_now()
                if g.unitTesting:
                    g.app.unitTestDict['g.openWithFileName']=leo_path
                else:
                    c2 = g.openWithFileName(leo_path,old_c=c)
                    # with UNL after path
                    if c2 and fragment:
                        g.recursiveUNLSearch(fragment.split("--&gt;"),c2)
                    if c2:
                        c2.bringToFront()
                        return

        # isHtml = leo_path.endswith('.html') or leo_path.endswith('.htm')
        
        # Use g.os_startfile for *all* files.
        if scheme in ('', 'file'):
            if g.os_path_exists(leo_path):
                if trace: g.trace('g.os_startfile(%s)' % (leo_path))
                leo_path = unquote(leo_path)
                g.os_startfile(leo_path)
            else:
                g.es("File '%s' does not exist"%leo_path)
        else:
            import webbrowser
    
            if trace: g.trace('webbrowser.open(%s)' % (url))
            if g.unitTesting:
                g.app.unitTestDict['browser']=url
            else:
                # Mozilla throws a weird exception, then opens the file!
                try: webbrowser.open(url)
                except: pass
        
    except:
        g.es("exception opening",leo_path)
        g.es_exception()
</t>
<t tx="ekr.20120625092120.12718">def isValidUrl(url):
    
    '''Return true if url *looks* like a valid url.'''
    
    table = (
        'file','ftp','gopher','hdl','http','https','imap',
        'mailto','mms','news','nntp','prospero','rsync','rtsp','rtspu',
        'sftp','shttp','sip','sips','snews','svn','svn+ssh','telnet','wais',
    )

    if url.startswith('#--&gt;'):
        # All Leo UNL's.
        return True
    elif url.startswith('@'):
        return False
    else:
        parsed = urlparse.urlparse(url)
        # E1103: Instance of 'ParseResult' has no 'scheme' member.
        scheme = parsed.scheme # pylint: disable=E1103
        for s in table:
            if scheme.startswith(s):
                return True
        return False
</t>
<t tx="ekr.20120625092120.12719">def openUrl(p):
    
    if not p:
        return
    
    url = g.getUrlFromNode(p)
    if url:
        c = p.v.context
        if not g.doHook("@url1",c=c,p=p,v=p,url=url):
            g.handleUrl(url,c=c,p=p)
        g.doHook("@url2",c=c,p=p,v=p)
</t>
<t tx="ekr.20120625092120.12720">@g.command('open-url-under-cursor')
def openUrlUnderCursor(event):
    return openUrlOnClick(event)
    
def openUrlOnClick(event):
    '''Open the URL under the cursor.  Return it for unit testing.'''
    c = event.get('c')
    if not c: return None
    w = event.get('w') or c.frame.body.bodyCtrl
    s = w.getAllText()
    ins = w.getInsertPoint()
    i,j = w.getSelectionRange()
    if i != j: return None # So find doesn't open the url.
    row,col = g.convertPythonIndexToRowCol(s,ins)
    i,j = g.getLine(s,ins)
    line = s[i:j]
    for match in g.url_regex.finditer(line):
        if match.start() &lt;= col &lt; match.end(): # Don't open if we click after the url.
            url = match.group()
            if g.isValidUrl(url):
                p = c.p
                if not g.doHook("@url1",c=c,p=p,v=p,url=url):
                    g.handleUrl(url,c=c,p=p)
                g.doHook("@url2",c=c,p=p,v=p)
                return url
    return None
</t>
<t tx="ekr.20120625092120.12722"></t>
<t tx="ekr.20120625092120.12723">def convertPythonIndexToRowCol (s,i):

    '''Convert index i into string s into zero-based row/col indices.'''

    if not s or i &lt;= 0:
        return 0,0

    i = min(i,len(s))

    # works regardless of what s[i] is
    row = s.count('\n',0,i) # Don't include i
    if row == 0:
        return row,i
    else:
        prevNL = s.rfind('\n',0,i) # Don't include i
        # g.trace('prevNL',prevNL,'i',i,g.callers())
        return row,i-prevNL-1
</t>
<t tx="ekr.20120625092120.12724">def convertRowColToPythonIndex (s,row,col,lines=None):

    '''Convert zero-based row/col indices into a python index into string s.'''

    if row &lt; 0: return 0

    if lines is None:
        lines = g.splitLines(s)

    if row &gt;= len(lines):
        return len(s)

    col = min(col, len(lines[row]))

    # A big bottleneck
    prev = 0
    for line in lines[:row]:
        prev += len(line)

    return prev + col
</t>
<t tx="ekr.20120625092120.12725"></t>
<t tx="ekr.20120625092120.12726">def appendToList(out, s):

    for i in s:
        out.append(i)
</t>
<t tx="ekr.20120625092120.12727">def flattenList (theList):

    result = []
    for item in theList:
        if type(item) == types.ListType:
            result.extend(g.flattenList(item))
        else:
            result.append(item)
    return result
</t>
<t tx="ekr.20120625092120.12728">def maxStringListLength(aList):

    '''Return the maximum string length in a list of strings.'''

    n = 0
    for z in aList:
        if g.isString():
            n = max(n,len(z))

    return n
</t>
<t tx="ekr.20120625092120.12730"></t>
<t tx="ekr.20120625092120.12731"># Simplified version by EKR: stringCompare not used.

def CheckVersion (s1,s2,condition="&gt;=",stringCompare=None,delimiter='.',trace=False):

    # CheckVersion is called early in the startup process.

    vals1 = [g.CheckVersionToInt(s) for s in s1.split(delimiter)] ; n1 = len(vals1)
    vals2 = [g.CheckVersionToInt(s) for s in s2.split(delimiter)] ; n2 = len(vals2)
    n = max(n1,n2)
    if n1 &lt; n: vals1.extend([0 for i in range(n - n1)])
    if n2 &lt; n: vals2.extend([0 for i in range(n - n2)])
    for cond,val in (
        ('==', vals1 == vals2), ('!=', vals1 != vals2),
        ('&lt;',  vals1 &lt;  vals2), ('&lt;=', vals1 &lt;= vals2),
        ('&gt;',  vals1 &gt;  vals2), ('&gt;=', vals1 &gt;= vals2),
    ):
        if condition == cond:
            result = val ; break
    else:
        raise EnvironmentError("condition must be one of '&gt;=', '&gt;', '==', '!=', '&lt;', or '&lt;='.")

    if trace:
        # g.pr('%10s' % (repr(vals1)),'%2s' % (condition),'%10s' % (repr(vals2)),result)
        g.pr('%7s' % (s1),'%2s' % (condition),'%7s' % (s2),result)
    return result
</t>
<t tx="ekr.20120625092120.12732">def CheckVersionToInt (s):

    try:
        return int(s)
    except ValueError:
        aList = []
        for ch in s:
            if ch.isdigit(): aList.append(ch)
            else: break
        if aList:
            s = ''.join(aList)
            return int(s)
        else:
            return 0
</t>
<t tx="ekr.20120625092120.12733">@ g.CheckVersion() is a generic version checker.  Assumes a
version string of up to four parts, or tokens, with
leftmost token being most significant and each token
becoming less signficant in sequence to the right.

RETURN VALUE

1 if comparison is True
0 if comparison is False

PARAMETERS

version: the version string to be tested
againstVersion: the reference version string to be
              compared against
condition: can be any of "==", "!=", "&gt;=", "&lt;=", "&gt;", or "&lt;"
stringCompare: whether to test a token using only the
             leading integer of the token, or using the
             entire token string.  For example, a value
             of "0.0.1.0" means that we use the integer
             value of the first, second, and fourth
             tokens, but we use a string compare for the
             third version token.
delimiter: the character that separates the tokens in the
         version strings.

The comparison uses the precision of the version string
with the least number of tokens.  For example a test of
"8.4" against "8.3.3" would just compare the first two
tokens.

The version strings are limited to a maximum of 4 tokens.
@c

def oldCheckVersion( version, againstVersion, condition="&gt;=", stringCompare="0.0.0.0", delimiter='.' ):

    # tokenize the stringCompare flags
    compareFlag = stringCompare.split('.')

    # tokenize the version strings
    testVersion = version.split(delimiter)
    testAgainst = againstVersion.split(delimiter)

    # find the 'precision' of the comparison
    tokenCount = 4
    if tokenCount &gt; len(testAgainst):
        tokenCount = len(testAgainst)
    if tokenCount &gt; len(testVersion):
        tokenCount = len(testVersion)

    # Apply the stringCompare flags
    justInteger = re.compile("^[0-9]+")
    for i in range(tokenCount):
        if "0" == compareFlag[i]:
            m = justInteger.match( testVersion[i] )
            testVersion[i] = m.group()
            m = justInteger.match( testAgainst[i] )
            testAgainst[i] = m.group()
        elif "1" != compareFlag[i]:
            errMsg = "stringCompare argument must be of " +\
                 "the form \"x.x.x.x\" where each " +\
                 "'x' is either '0' or '1'."
            raise EnvironmentError(errMsg)

    # Compare the versions
    if condition == "&gt;=":
        for i in range(tokenCount):
            if testVersion[i] &lt; testAgainst[i]:
                return 0
            if testVersion[i] &gt; testAgainst[i]:
                return 1 # it was greater than
        return 1 # it was equal
    if condition == "&gt;":
        for i in range(tokenCount):
            if testVersion[i] &lt; testAgainst[i]:
                return 0
            if testVersion[i] &gt; testAgainst[i]:
                return 1 # it was greater than
        return 0 # it was equal
    if condition == "==":
        for i in range(tokenCount):
            if testVersion[i] != testAgainst[i]:
                return 0 # any token was not equal
        return 1 # every token was equal
    if condition == "!=":
        for i in range(tokenCount):
            if testVersion[i] != testAgainst[i]:
                return 1 # any token was not equal
        return 0 # every token was equal
    if condition == "&lt;":
        for i in range(tokenCount):
            if testVersion[i] &gt;= testAgainst[i]:
                return 0
            if testVersion[i] &lt; testAgainst[i]:
                return 1 # it was less than
        return 0 # it was equal
    if condition == "&lt;=":
        for i in range(tokenCount):
            if testVersion[i] &gt; testAgainst[i]:
                return 0
            if testVersion[i] &lt; testAgainst[i]:
                return 1 # it was less than
        return 1 # it was equal

    # didn't find a condition that we expected.
    raise EnvironmentError("condition must be one of '&gt;=', '&gt;', '==', '!=', '&lt;', or '&lt;='.")
</t>
<t tx="ekr.20120625092120.12736">class UiTypeException(Exception):
    pass

def assertUi(uitype):
    if not g.app.gui.guiName() == uitype:
        raise UiTypeException
</t>
<t tx="ekr.20120625092120.12738">def computeWindowTitle (fileName):

    if fileName == None:
        return "untitled"
    else:
        path,fn = g.os_path_split(fileName)
        if path:
            title = fn + " in " + path
        else:
            title = fn
        return title
</t>
<t tx="ekr.20120625092120.12739">def ensureLeadingNewlines (s,n):

    s = g.removeLeading(s,'\t\n\r ')
    return ('\n' * n) + s

def ensureTrailingNewlines (s,n):

    s = g.removeTrailing(s,'\t\n\r ')
    return s + '\n' * n


</t>
<t tx="ekr.20120625092120.12740">def executeScript (name):

    """Execute a script whose short python file name is given.

    This is called only from the scripts_menu plugin."""

    mod_name,ext = g.os_path_splitext(name)
    theFile = None
    try:
        # This code is in effect an import or a reload.
        # This allows the user to modify scripts without leaving Leo.
        import imp
        theFile,filename,description = imp.find_module(mod_name)
        imp.load_module(mod_name,theFile,filename,description)
    except Exception:
        g.es("exception executing",name,color="red")
        g.es_exception()

    if theFile:
        theFile.close()
</t>
<t tx="ekr.20120625092120.12750"># Important: The startup code uses this class,
# so it is convenient to define it in leoGlobals.py.
class GeneralSetting:
    
    '''A class representing any kind of setting except shortcuts.'''
    
    def __init__ (self,kind,encoding=None,ivar=None,setting=None,val=None,path=None,tag='setting'):
    
        self.encoding = encoding
        self.ivar = ivar
        self.kind = kind
        self.path = path
        self.setting = setting
        self.val = val
        self.tag = tag
        
    def __repr__ (self):
        
        result = ['GeneralSetting kind: %s' % (self.kind)]
        ivars = ('ivar','path','setting','val','tag')
        for ivar in ivars:
            if hasattr(self,ivar):
                val =  getattr(self,ivar)
                if val is not None:
                    result.append('%s: %s' % (ivar,val))
        return ','.join(result)
        
    dump = __repr__
        
def isGeneralSetting(obj):
    return isinstance(obj,GeneralSetting)
</t>
<t tx="ekr.20120625092120.12751">def getDocString(s):
    
    '''Return the text of the first docstring found in s.'''

    tags = ('"""',"'''")
    tag1,tag2 = tags
    i1,i2 = s.find(tag1),s.find(tag2)

    if i1 == -1 and i2 == -1:
        return ''
    if i1 &gt; -1 and i2 &gt; -1:
        i = min(i1,i2)
    else:
        i = max(i1,i2)
    tag = s[i:i+3]
    assert tag in tags

    j = s.find(tag,i+3)
    if j &gt; -1:
        return s[i+3:j]
    else:
        return ''

</t>
<t tx="ekr.20120625092120.12752">def getDocStringForFunction (func):
    
    '''Return the docstring for a function that creates a Leo command.'''
    
    def name(func):
        return hasattr(func,'__name__') and func.__name__ or ''
        
    def get_defaults(func,i):
        args, varargs, keywords, defaults = inspect.getargspec(func)
        return defaults[i]
    
    if name(func) == 'minibufferCallback':
        func = get_defaults(func,0)
        if name(func) == 'commonCommandCallback':
            script = get_defaults(func,1)
            s = g.getDocString(script)
        elif hasattr(func,'docstring'): # atButtonCallback object.
            s = func.docstring()
        elif hasattr(func,'__doc__'):
            s = func.__doc__ or ''
        else:
            print('**oops',func)
            s = ''
    else:
        s = func.__doc__ or ''
        
    return s
</t>
<t tx="ekr.20120625092120.12754">def isMacOS():
    
    return sys.platform == 'darwin'
</t>
<t tx="ekr.20120625092120.12755">def longestCommonPrefix (s1,s2):

    '''Find the longest prefix common to strings s1 and s2.'''

    prefix = ''
    for ch in s1:
        if s2.startswith(prefix + ch):
            prefix = prefix + ch
        else:
            return prefix
    return prefix

def itemsMatchingPrefixInList (s,aList,matchEmptyPrefix=False):

    '''This method returns a sorted list items of aList whose prefix is s.

    It also returns the longest common prefix of all the matches.'''

    if s:
        pmatches = [a for a in aList if a.startswith(s)]
    elif matchEmptyPrefix:
        pmatches = aList[:]
    else: pmatches = []

    if pmatches:
        pmatches.sort()
        common_prefix = reduce(g.longestCommonPrefix,pmatches)
    else:
        common_prefix = ''

    # g.trace(repr(s),len(pmatches))
    return pmatches,common_prefix
</t>
<t tx="ekr.20120625092120.12757">def prettyPrintType (obj):

    if g.isPython3:
        if type(obj) in (types.MethodType,types.BuiltinMethodType):
            return 'method'
        elif type(obj) in (types.BuiltinFunctionType,types.FunctionType):
            return 'function'
        elif type(obj) == types.ModuleType:
            return 'module'
        elif g.isString(obj):
            return 'string'
        else:
            theType = str(type(obj))
            if theType.startswith("&lt;type '"): theType = theType[7:]
            if theType.endswith("'&gt;"): theType = theType[:-2]
            return theType
    else:
        if type(obj) in (
            types.MethodType,types.UnboundMethodType,types.BuiltinMethodType):
            return 'method'
        elif type(obj) in (types.BuiltinFunctionType,types.FunctionType):
            return 'function'
        elif type(obj) == types.ModuleType:
            return 'module'
        elif type(obj) == types.InstanceType:
            return 'object'
        elif type(obj) in (types.UnicodeType,types.StringType):
            return 'string'
        else:
            theType = str(type(obj))
            if theType.startswith("&lt;type '"): theType = theType[7:]
            if theType.endswith("'&gt;"): theType = theType[:-2]
            return theType
</t>
<t tx="ekr.20120625092120.12758"># Warning: g.removeTrailingWs already exists.
# Do not change it!

def removeLeading (s,chars):

    '''Remove all characters in chars from the front of s.'''

    i = 0
    while i &lt; len(s) and s[i] in chars:
        i += 1
    return s[i:]

def removeTrailing (s,chars):

    '''Remove all characters in chars from the end of s.'''

    i = len(s)-1
    while i &gt;= 0 and s[i] in chars:
        i -= 1
    i += 1
    return s[:i]
</t>
<t tx="ekr.20120625092120.12759"># bindKey:            ShortcutInfo(kind,commandName,func,pane)
# bindKeyToDict:      ShortcutInfo(kind,commandName,func,pane,stroke)
# createModeBindings: ShortcutInfo(kind,commandName,func,nextMode,stroke)

# Important: The startup code uses this class,
# so it is convenient to define it in leoGlobals.py.
class ShortcutInfo:
    
    '''A class representing any kind of key binding line.
    
    This includes other information besides just the KeyStroke.'''
        
    @others

def isShortcutInfo(obj):
    return isinstance(obj,ShortcutInfo)
</t>
<t tx="ekr.20120625092120.12760">def __init__ (self,kind,commandName='',func=None,nextMode=None,pane=None,stroke=None):
    
    trace = False and commandName=='new' and not g.unitTesting

    if not (stroke is None or g.isStroke(stroke)):
        g.trace('***** (ShortcutInfo) oops',repr(stroke))

    self.kind = kind
    self.commandName = commandName
    self.func = func
    self.nextMode = nextMode
    self.pane = pane
    self.stroke = stroke
        # The *caller* must canonicalize the shortcut.

    if trace: g.trace('(ShortcutInfo)',commandName,stroke,g.callers())
</t>
<t tx="ekr.20120625092120.12761">def __hash__ (self):
    
    return self.stroke.__hash__() if self.stroke else 0
</t>
<t tx="ekr.20120625092120.12762">def __repr__ (self):
    
    return self.dump()

__str__ = __repr__

def dump (self):
    si = self    
    result = ['ShortcutInfo %17s' % (si.kind)]
    # Print all existing ivars.
    table = ('commandName','func','nextMode','pane','stroke')
    for ivar in table:
        if hasattr(si,ivar):
            val =  getattr(si,ivar)
            if val not in (None,'none','None',''):
                if ivar == 'func': val = val.__name__
                s = '%s %s' % (ivar,val)
                result.append(s)
    return '[%s]' % ' '.join(result).strip()
</t>
<t tx="ekr.20120625092120.12763">def isModeBinding (self):
    
    return self.kind.startswith('*mode')
</t>
<t tx="ekr.20120625092120.12765">def toPythonIndex (s,index):
    
    '''Convert index to a Python int.
    
    index may be a Tk index (x.y) or 'end'.
    '''
    
    if index is None:
        return 0
    elif type(index) == type(99):
        return index
    elif index == '1.0':
        return 0
    elif index == 'end':
        return len(s)
    else:
        data = index.split('.')
        if len(data) == 2:
            row,col = data
            row,col = int(row),int(col)
            i = g.convertRowColToPythonIndex(s,row-1,col)
            return i
        else:
            g.trace('bad string index: %s' % index)
            return 0

toGuiIndex = toPythonIndex
</t>
<t tx="ekr.20120625092120.12766">class TypedDict:
    
    '''A class containing a name and enforcing type checking.'''
    
    @others
    
def isTypedDict(obj):
    return isinstance(obj,TypedDict)
    
class TypedDictOfLists (TypedDict):
    
    '''A class whose values are lists of typed values.'''
    
    def __init__(self,name,keyType,valType):
        TypedDict.__init__(self,name,keyType,valType) # Init the base class
        self.isList = True
        
    def __repr__(self):
        return '&lt;TypedDictOfLists name:%s keys:%s values:%s len(keys): %s' % (
            self._name,self.keyType.__name__,self.valType.__name__,len(list(self.keys())))
    __str__ = __repr__
            
    def copy(self,name=None):
        d = TypedDictOfLists(name or self._name,self.keyType,self.valType)
        d.d = dict(self.d)
        return d
    
def isTypedDictOfLists(obj):
    return isinstance(obj,TypedDictOfLists)
</t>
<t tx="ekr.20120625092120.12767">def __init__(self,name,keyType,valType):

    trace = False and not g.unitTesting and name == 'g.app.config.defaultsDict'
    self.d = {}
    self.isList = False
    self._name = name # name is a method.
    self.keyType = keyType
    self.valType = valType

    if trace:
        print(self)
        # g.trace(self)
</t>
<t tx="ekr.20120625092120.12768">def __repr__(self):

    return '&lt;TypedDict name:%s keys:%s values:%s len(keys): %s' % (
        self._name,self.keyType.__name__,self.valType.__name__,len(list(self.keys())))
        
__str__ = __repr__
    
</t>
<t tx="ekr.20120625092120.12769">def _checkKeyType(self,key):
    
    # These fail on Python 2.x for strings.
    if g.isPython3:
        # assert key.__class__ == self.keyType,self._reportTypeError(key,self.keyType)
        if key and key.__class__ != self.keyType:
            self._reportTypeError(key,self.keyType)

def _checkValType(self,val):

    # This doesn't fail, either on Python 2.x or 3.x.
    assert val.__class__ == self.valType,self._reportTypeError(val,self.valType)
        
def _reportTypeError(self,obj,objType):
    
    print('obj',obj,'obj.__class__',obj.__class__,'objType',objType)
    
    return 'dict: %s expected %s got %s' % (
        self._name,obj.__class__.__name__,objType.__name__)
</t>
<t tx="ekr.20120625092120.12770">def add(self,key,val):
    self._checkKeyType(key)
    self._checkValType(val)
    if self.isList:
        aList = self.d.get(key,[])
        if val not in aList:
            aList.append(val)
            self.d[key] = aList
    else:
        self.d[key] = val

def replace(self,key,val):
    self._checkKeyType(key)
    if self.isList:
        try:
            for z in val:
                self._checkValType(z)
        except TypeError:
            self._checkValType(val) # val is not iterable.
        self.d[key] = val
    else:
        self._checkValType(val)
        self.d[key] = val
        
__setitem__ = replace # allow d[key] = val.
</t>
<t tx="ekr.20120625092120.12771">def copy(self,name=None):
    
    '''Return a new dict with the same contents.'''

    d = TypedDict(name or self._name,self.keyType,self.valType)
    d.d = dict(self.d)
    return d

</t>
<t tx="ekr.20120625092120.12772">def dump (self):
    
    result = ['Dump of %s' % (self)]
    
    for key in sorted(self.d.keys()):
        if self.isList:
            result.append(key)
            aList = self.d.get(key,[])
            for z in aList:
                result.append('  '+repr(z))
        else:
            result.append(key,self.d.get(key))
            
    return '\n'.join(result)
</t>
<t tx="ekr.20120625092120.12773">def get(self,key,default=None):
    self._checkKeyType(key)
    if default is None and self.isList:
        default = []
    return self.d.get(key,default)
        
def keys(self):
    return self.d.keys()
    
def name(self):
    return self._name
</t>
<t tx="ekr.20120625092120.12774">def setName (self,name):
    self._name =  name
</t>
<t tx="ekr.20120625092120.12775">def update(self,d):
    
    if isinstance(d,TypedDict):
        self.d.update(d.d)
    else:
        self.d.update(d)
</t>
<t tx="ekr.20120625092120.12776"></t>
<t tx="ekr.20120625092120.12777">def cantImport (moduleName,pluginName=None,verbose=True):

    """Print a "Can't Import" message and return None."""

    s = "Can not import %s" % moduleName
    if pluginName: s = s + " from plugin %s" % pluginName

    if not g.app or not g.app.gui:
        print (s)
    elif g.unitTesting:
        # print s
        return
    # elif g.app.gui.guiName() == 'tkinter' and moduleName in ('Tkinter','Pmw'):
        # return
    else:
        g.es_print('',s,color="blue")

</t>
<t tx="ekr.20120625092120.12778">def importModule (moduleName,pluginName=None,verbose=False):

    '''Try to import a module as Python's import command does.

    moduleName is the module's name, without file extension.'''

    trace = False and not g.unitTesting
    module = sys.modules.get(moduleName)
    if module:  return module

    g.es('loading %s' % moduleName, color='blue')
    exceptions = [] 

    try:
        theFile = None
        import imp
        try:
            # New in Leo 4.7. We no longer add Leo directories to sys.path,
            # so search extensions and external directories here explicitly.
            for findPath in (None,'extensions','external'):
                if findPath:
                    findPath2 = g.os_path_finalize_join(
                        g.app.loadDir,'..',findPath)
                    findPath = [findPath2]
                if trace: g.trace('findPath',findPath)
                try:
                    data = imp.find_module(moduleName,findPath) # This can open the file.
                    theFile,pathname,description = data
                    if trace: g.trace(theFile,moduleName,pathname)
                    module = imp.load_module(moduleName,theFile,pathname,description)
                    if module: 
                        g.es("%s loaded" % moduleName)
                        break
                except Exception:
                    t, v, tb = sys.exc_info()
                    del tb  # don't need the traceback
                    v = v or str(t) # in case v is empty, we'll at least have the execption type
                    if trace: g.trace(v,moduleName,findPath)
                    if v not in exceptions:
                        exceptions.append(v)
            else:
                #unable to load module, display all exception messages
                for e in exceptions:
                    g.es(e, color='blue') 
        except Exception: # Importing a module can throw exceptions other than ImportError.
            t, v, tb = sys.exc_info()
            del tb  # don't need the traceback
            v = v or str(t) # in case v is empty, we'll at least have the execption type
            g.es_exception(v)
    finally:
        if theFile: theFile.close()

    if not module:
        g.cantImport(moduleName,pluginName=pluginName,verbose=verbose)
    return module
</t>
<t tx="ekr.20120625092120.12779">def importExtension (moduleName,pluginName=None,verbose=False,required=False):

    '''Try to import a module.  If that fails,
    try to import the module from Leo's extensions directory.

    moduleName is the module's name, without file extension.'''

    # g.trace(verbose,moduleName,pluginName)

    import os

    module = g.importModule(moduleName,pluginName=pluginName,verbose=False)

    # this is basically only used for Pmw these days - we'll prevent plugins 
    # from killing all of Leo by returning None here instead
    if not module:
        g.pr("Warning: plugin '%s' failed to import '%s'" % (pluginName, moduleName))

    return module
</t>
<t tx="ekr.20120625092120.12780">def importFromPath (name,path,pluginName=None,verbose=False):

    trace = False and not g.unitTesting
    fn = g.shortFileName(name)
    moduleName,ext = g.os_path_splitext(fn)
    path = g.os_path_normpath(path)
    path = g.toEncodedString(path)
    
    if 0: # Bug fix 2011/10/28: Always import the path from the specified path!
        module = sys.modules.get(moduleName)
        if module:
            if trace: g.trace('already loaded',moduleName,module)
            return module

    try:
        module,theFile = None,None
        try:
            data = imp.find_module(moduleName,[path]) # This can open the file.
            theFile,pathname,description = data
            module = imp.load_module(moduleName,theFile,pathname,description)
        except ImportError:
            if trace: # or verbose:
                g.es_print("exception in g.importFromPath",color='blue')
                g.es_exception()
        except UiTypeException:
            if not g.unitTesting and not g.app.batchMode:
                g.es_print('Plugin %s does not support %s gui' % (
                    name,g.app.gui.guiName()))          
        except Exception:
            g.es_print("unexpected exception in g.importFromPath(%s)" %
                (name),color='blue')
            g.es_exception()
    # Put no return statements before here!
    finally: 
        if theFile: theFile.close()

    if module:
        if trace: g.trace('loaded',moduleName)
    else:
        g.cantImport(moduleName,pluginName=pluginName,verbose=verbose)

    return module
</t>
<t tx="ekr.20120625092120.12781"></t>
<t tx="ekr.20120625092120.12782"># This has been replaced by readLinesClass because
# yield is not valid in jython.

# def readLinesGenerator(s):

    # for line in g.splitLines(s):
        # # g.trace(repr(line))
        # yield line
    # yield ''
</t>
<t tx="ekr.20120625092120.12783">class readLinesClass:

    """A class whose next method provides a readline method for Python's tokenize module."""

    def __init__ (self,s):
        self.lines = g.splitLines(s)
        self.i = 0

    def next(self):
        if self.i &lt; len(self.lines):
            line = self.lines[self.i]
            self.i += 1
        else:
            line = ''
        # g.trace(repr(line))
        return line

    __next__ = next
</t>
<t tx="ekr.20120625092120.12784">class KeyStroke:
    
    '''A class that announces that its contents has been canonicalized by k.strokeFromSetting.
    
    This allows type-checking assertions in the code.'''
    
    @others

def isStroke(obj):
    return isinstance(obj,KeyStroke)
    
def isStrokeOrNone(obj):
    return obj is None or isinstance(obj,KeyStroke)
</t>
<t tx="ekr.20120625092120.12785">def __init__ (self,s):
    
    trace = False and not g.unitTesting and s == 'name'
    if trace: g.trace('(KeyStroke)',s,g.callers())

    assert s,repr(s)
    assert g.isString(s)
        # type('s') does not work in Python 3.x.
    self.s = s
</t>
<t tx="ekr.20120625092120.12786"></t>
<t tx="ekr.20120625092120.12787"># Allow KeyStroke objects to be keys in dictionaries.

def __hash__ (self):

    return self.s.__hash__() if self.s else 0
</t>
<t tx="ekr.20120625092120.12788">def __str__ (self):

    return '&lt;KeyStroke: %s&gt;' % (self.s)
    
__repr__ = __str__
</t>
<t tx="ekr.20120625092120.12789">@ All these must be defined in order to say, for example:
    for key in sorted(d)
where the keys of d are KeyStroke objects.
@c

def __eq__ (self,other): 
    if not other:               return False
    elif hasattr(other,'s'):    return self.s == other.s
    else:                       return self.s == other
    
def __lt__ (self,other):
    if not other:               return False
    elif hasattr(other,'s'):    return self.s &lt; other.s
    else:                       return self.s &lt; other
        
def __le__ (self,other): return self.__lt__(other) or self.__eq__(other)    
def __ne__ (self,other): return not self.__eq__(other)
def __gt__ (self,other): return not self.__lt__(other) and not self.__eq__(other)  
def __ge__ (self,other): return not self.__lt__(other)
</t>
<t tx="ekr.20120625092120.12790"># These may go away later, but for now they make conversion of string strokes easier.

def find (self,pattern):
    
    return self.s.find(pattern)
    
def lower (self):

    return self.s.lower()

def startswith(self,s):
    
    return self.s.startswith(s)
</t>
<t tx="ekr.20120625092120.12791">def isFKey (self):

    s = self.s.lower()

    return s.startswith('f') and len(s) &lt;= 3 and s[1:].isdigit()
</t>
<t tx="ekr.20120625092120.12792">def toGuiChar (self):
    
    '''Replace special chars by the actual gui char.'''
    
    s = self.s.lower()
    if s in ('\n','return'):        s = '\n'
    elif s in ('\t','tab'):         s = '\t'
    elif s in ('\b','backspace'):   s = '\b'
    elif s in ('.','period'):       s = '.'
    return s
</t>
<t tx="ekr.20120625092120.12799">@
Important note: this routine need not deal with leading whitespace.
Instead, the caller should simply reduce pageWidth by the width of
leading whitespace wanted, then add that whitespace to the lines
returned here.

The key to this code is the invarient that line never ends in whitespace.
@c

def wrap_lines (lines,pageWidth,firstLineWidth=None):

    """Returns a list of lines, consisting of the input lines wrapped to the given pageWidth."""

    if pageWidth &lt; 10:
        pageWidth = 10

    # First line is special
    if not firstLineWidth:
        firstLineWidth = pageWidth
    if firstLineWidth &lt; 10:
        firstLineWidth = 10
    outputLineWidth = firstLineWidth

    # Sentence spacing
    # This should be determined by some setting, and can only be either 1 or 2
    sentenceSpacingWidth = 1
    assert(0 &lt; sentenceSpacingWidth &lt; 3)
    
    # g.trace(lines)
    result = [] # The lines of the result.
    line = "" # The line being formed.  It never ends in whitespace.
    for s in lines:
        i = 0
        while i &lt; len(s):
            assert(len(line) &lt;= outputLineWidth) # DTHEIN 18-JAN-2004
            j = g.skip_ws(s,i)   # ;   ws = s[i:j]
            k = g.skip_non_ws(s,j) ; word = s[j:k]
            assert(k&gt;i)
            i = k
            # DTHEIN 18-JAN-2004: wrap at exactly the text width, 
            # not one character less
            # 
            wordLen = len(word)
            if line.endswith('.') or line.endswith('?') or line.endswith('!'):
                space = ' ' * sentenceSpacingWidth
            else:
                space = ' '
            if len(line) &gt; 0 and wordLen &gt; 0: wordLen += len(space)
            if wordLen + len(line) &lt;= outputLineWidth:
                if wordLen &gt; 0:
                    &lt;&lt; place blank and word on the present line &gt;&gt;
                else: pass # discard the trailing whitespace.
            else:
                &lt;&lt; place word on a new line &gt;&gt;
    if len(line) &gt; 0:
        result.append(line)
    # g.trace(result)
    return result
</t>
<t tx="ekr.20120625092120.12800">if len(line) == 0:
    # Just add the word to the start of the line.
    line = word
else:
    # Add the word, preceeded by a blank.
    line = space.join((line,word)) # DTHEIN 18-JAN-2004: better syntax
</t>
<t tx="ekr.20120625092120.12801"># End the previous line.
if len(line) &gt; 0:
    result.append(line)
    outputLineWidth = pageWidth # DTHEIN 3-NOV-2002: width for remaining lines

# Discard the whitespace and put the word on a new line.
line = word

# Careful: the word may be longer than pageWidth.
if len(line) &gt; pageWidth: # DTHEIN 18-JAN-2004: line can equal pagewidth
    result.append(line)
    outputLineWidth = pageWidth # DTHEIN 3-NOV-2002: width for remaining lines
    line = ""
</t>
<t tx="ekr.20120625092120.12812"></t>
<t tx="ekr.20120625092120.12813">init_zodb_import_failed = False
init_zodb_failed = {} # Keys are paths, values are True.
init_zodb_db = {} # Keys are paths, values are ZODB.DB instances.

def init_zodb (pathToZodbStorage,verbose=True):

    '''Return an ZODB.DB instance from ZODB.FileStorage.FileStorage(pathToZodbStorage)
    return None on any error.'''

    global init_zodb_db, init_zodb_failed, init_zodb_import_failed

    db = init_zodb_db.get(pathToZodbStorage)
    if db: return db

    if init_zodb_import_failed: return None

    failed = init_zodb_failed.get(pathToZodbStorage)
    if failed: return None

    try:
        import ZODB
    except ImportError:
        if verbose:
            g.es('g.init_zodb: can not import ZODB')
            g.es_exception()
        init_zodb_import_failed = True
        return None

    try:
        storage = ZODB.FileStorage.FileStorage(pathToZodbStorage)
        init_zodb_db [pathToZodbStorage] = db = ZODB.DB(storage)
        return db
    except Exception:
        if verbose:
            g.es('g.init_zodb: exception creating ZODB.DB instance')
            g.es_exception()
        init_zodb_failed [pathToZodbStorage] = True
        return None
</t>
<t tx="ekr.20120625092120.12815"># The following are not defined in leoStandAloneGlobals
# because they are not needed outside of Leo...
if 0:
    @others</t>
<t tx="ekr.20120625092120.12816"></t>
<t tx="ekr.20120625092120.12818"></t>
<t tx="ekr.20120625092120.12819"></t>
<t tx="ekr.20120625092120.12820"></t>
<t tx="ekr.20120625092120.12821"></t>
<t tx="ekr.20120625092120.12827"># These are now all synonyms for g.pr
</t>
<t tx="ekr.20120625092120.12830"></t>
<t tx="ekr.20120625092120.12834"></t>
<t tx="ekr.20120625092120.12835"></t>
<t tx="ekr.20120625092120.12837"></t>
<t tx="ekr.20120625092120.12838">import leoStandAloneGlobals as g
import imp
imp.reload(g)
print(g,g.trace)</t>
</tnodes>
</leo_file>
