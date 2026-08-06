# @+leo-ver=5-thin
# @+node:ekr.20251129060454.1: * @file ../scripts/check_leo.py
"""
This script checks Leo's most important files for potential attribute
errors.

This script discovered bugs that neither mypy, nor pylint, nor pyflakes
found. For details, see: https://github.com/leo-editor/leo-editor/pull/4484

This script contains many Leo-specific hacks. In particular, Leo's naming
conventions allow the script to convert names to live objects.

Despite (because of) these hacks, this script does a lot with minimal
infrastructure. Because of this simplicity, this script may be of interest
to devs in other projects.

This script is fast: it checks files about as fast as pyflakes.
"""

# @+<< check_leo: imports >>
# @+node:ekr.20251129080328.1: ** << check_leo: imports >>
# Required directly by script.
import ast
import glob
import os
import sys
import time
from typing import Any
# @-<< check_leo: imports >>

# Not needed: we always print a summary line.
# print(os.path.basename(__file__))

# @+<< check_leo: globals >>
# @+node:ekr.20251130105440.1: ** << check_leo: globals >>
# Global objects.
leoC, leoG, leoP, leoV = None, None, None, None

# Global switches.
all_files_flag = True

# Global stats.
all_attrs: set[str] = set()
all_args: set[str] = set()
chains_seen: set[str] = set()
errors: set[str] = set()
full_check = False  # True: report *all* unknown attrs.
module_name: str = ''
report_all_attrs = False
report_all_args = False
report_unusual_attrs = False  # True: report only unusual attrs containing '{}[]()'
report_all_undefined_chains = True
report_all_unfinished_chains = True
report_all_unknown_bases = True
report_times = False
show_context_flag = False
show_all_context_flag = False
stats_attrs = 0
stats_contexts = 0
unknown_bases: set[str] = set()
undefined_chains: set[str] = set()

# Global directories.
leo_editor_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
commands_dir = os.path.normpath(os.path.join(leo_editor_dir, 'leo', 'commands'))
core_dir = os.path.normpath(os.path.join(leo_editor_dir, 'leo', 'core'))
plugins_dir = os.path.normpath(os.path.join(leo_editor_dir, 'leo', 'plugins'))
for z in (leo_editor_dir, commands_dir, core_dir):
    assert os.path.exists(z), repr(z)


# @-<< check_leo: globals >>
# @+others
# @+node:ekr.20251130081222.1: ** class CheckLeo
class CheckLeo:
    """The controller class of the check_leo.py script."""

    # @+others
    # @+node:ekr.20251129161138.1: *3* CheckLeo.adjust_sys_path
    def adjust_sys_path(self) -> None:
        """Add 'leo-editor' to sys.path"""
        if leo_editor_dir not in sys.path:
            # Caution: path[0] is reserved for script path (or '' in REPL)
            sys.path.insert(1, leo_editor_dir)

    # @+node:ekr.20251129080959.1: *3* CheckLeo.check
    def check(self, path: str) -> None:
        """Check one file, adding cumulative data to the visitor class."""
        assert os.path.exists(path), repr(path)
        contents = leoG.readFile(path)
        tree = ast.parse(contents, filename=path)
        visitor = Visitor(self.known_objects)
        visitor.visit(tree)

    # @+node:ekr.20251129161354.1: *3* CheckLeo.compute_files
    def compute_files(self) -> list[str]:
        """Return the list of files to be checked."""
        files: list[str]
        if all_files_flag:
            core_files = glob.glob(f"{core_dir}{os.sep}*.py")
            commands_files = glob.glob(f"{commands_dir}{os.sep}*.py")
            plugins_names = (
                # 'active_path.py',
                # 'add_directives.py',
                # 'anki.py',
                # 'attrib_edit.py',
                # 'at_folder.py',
                # 'at_produce.py',
                # 'at_view.py',
                # 'auto_colorize2_0.py',
                'backlink.py',
                # 'baseNativeTree.py',
                # 'bibtex.py',
                # 'bigdash.py',
                'bookmarks.py',
                # 'bzr_qcommands.py',
                # 'chapter_hoist.py',
                # 'colorize_headlines.py',
                'contextmenu.py',
                # 'ctagscompleter.py',
                # 'datenodes.py',
                # 'debugger_pudb.py',
                # 'demo.py',
                # 'dragdropgoodies.py',
                # 'dtest.py',
                # 'dump_globals.py',
                # 'empty_leo_file.py',
                # 'enable_gc.py',
                # 'example_rst_filter.py',
                # 'expfolder.py',
                # 'FileActions.py',
                # 'freewin.py',
                # 'free_layout.py',
                # 'ftp.py',
                # 'geotag.py',
                # 'gitarchive.py',
                # 'graphcanvas.py',
                # 'history_tracer.py',
                # 'import_cisco_config.py',
                # 'indented_languages.py',
                # 'initinclass.py',
                # 'interact.py',
                # 'leocursor.py',
                # 'leofeeds.py',
                # 'leofts.py',
                # 'leomail.py',
                # 'leomylyn.py',
                # 'leoOPML.py',
                # 'leoremote.py',
                # 'leoscreen.py',
                # 'leo_cloud.py',
                # 'leo_cloud_server.py',
                # 'leo_interface.py',
                # 'leo_pdf.py',
                # 'leo_to_html.py',
                # 'leo_to_html_outline_viewer.py',
                # 'leo_to_rtf.py',
                # 'lineNumbers.py',
                # 'line_numbering.py',
                # 'livecode.py',
                # 'macros.py',
                # 'markup_inline.py',
                # 'maximizeNewWindows.py',
                # 'md_docer.py',
                # 'mime.py',
                # 'mnplugins.py',
                # 'mod_autosave.py',
                # 'mod_framesize.py',
                # 'mod_http.py',
                # 'mod_leo2ascd.py',
                # 'mod_read_dir_outline.py',
                'mod_scripting.py',
                # 'mod_speedups.py',
                # 'mod_timestamp.py',
                # 'multifile.py',
                'nav_qt.py',
                # 'nested_splitter.py',
                # 'niceNosent.py',
                # 'nodeActions.py',
                # 'nodediff.py',
                'nodetags.py',
                # 'nodewatch.py',
                # 'open_shell.py',
                # 'outline_export.py',
                # 'pane_commands.py',
                # 'paste_as_headlines.py',
                # 'patch_python_colorizer.py',
                'plugins_menu.py',
                # 'projectwizard.py',
                # 'pyplot_backend.py',
                # 'python_terminal.py',
                # 'QNCalendarWidget.py',
                'qtGui.py',
                'qt_commands.py',
                'qt_events.py',
                'qt_frame.py',
                'qt_gui.py',
                'qt_idle_time.py',
                'qt_layout.py',
                'qt_main.py',
                'qt_quickheadlines.py',
                'qt_quicksearch.py',
                'qt_quicksearch_sub.py',
                'qt_text.py',
                'qt_tree.py',
                'quickMove.py',
                'quicksearch.py',
                # 'quit_leo.py',
                # 'read_only_nodes.py',
                # 'redirect_to_log.py',
                # 'richtext.py',
                # 'rpcalc.py',
                # 'rss.py',
                # 'run_nodes.py',
                # 'screencast.py',
                # 'screenshots.py',
                # 'screen_capture.py',
                # 'script_io_to_body.py',
                # 'setHomeDirectory.py',
                # 'settings_finder.py',
                # 'sftp.py',
                'slideshow.py',
                # 'spydershell.py',
                # 'startfile.py',
                # 'stickynotes.py',
                # 'stickynotes_plus.py',
                # 'systray.py',
                # 'tables.py',
                # 'testRegisterCommand.py',
                # 'textnode.py',
                # 'threadutil.py',
                # 'timestamp.py',
                # 'todo.py',
                # 'tomboy_import.py',
                # 'trace_gc_plugin.py',
                # 'trace_tags.py',
                'viewrendered.py',
                'viewrendered3.py',
                # 'vim.py',
                # 'wikiview.py',
                # 'word_count.py',
                # 'word_export.py',
                # 'xdb_pane.py',
                # 'xemacs.py',
                # 'xml_edit.py',
                # 'xsltWithNodes.py',
                # 'zenity_file_dialogs.py',
            )
            plugins_files = [f"{plugins_dir}{os.sep}{z}" for z in plugins_names]
            # z for z in glob.glob(f"{plugins_dir}{os.sep}*.py")
            if 0:
                for z in plugins_files:
                    print(f"plugin: {z}")
            all_files = core_files + commands_files + plugins_files
            files = [z for z in all_files if not z.startswith('_')]
        else:
            files = 'leoApp.py'
            files = [os.path.normpath(os.path.join(core_dir, z)) for z in files]
        for z in files:
            assert os.path.exists(z), repr(z)
        return files

    # @+node:ekr.20251202072018.1: *3* CheckLeo.compute_module_name
    def compute_module_name(self, file_name) -> str:
        """
        Compute the module corresponding to the given file name.

        Used only to set the global module_name var.
        """
        for base in ('commands', 'core', 'plugins'):
            i = file_name.find(base)
            if i > -1:
                s = file_name[i:-3]
                break
        else:
            s = file_name  # Should not happen.
        return s.replace('/', '.').replace('\\', '.')

    # @+node:ekr.20251202174626.1: *3* CheckLeo.create_known_objects
    def create_known_objects(self) -> dict[str, Any]:
        """Create a dictionary linking Leo's most important naming conventions to live objects."""
        assert leoC and leoG and leoP and leoV  # Must be run after create_live_objects.
        d = {
            # Python types
            'aList': [],
            'aList1': [],
            'aList2': [],
            's': ' ',
            's1': ' ',
            's2': ' ',
            # Leo objects.
            'c': leoC,
            'c1': leoC,
            'c2': leoC,
            'g': leoG,
            'p': leoP,
            'p1': leoP,
            'p2': leoP,
            'v': leoV,
            # 'd' can stand for dialog, dict, etc.
            # 'd': {},
        }
        if 0:
            leoG.printObj(d, tag='run:known_objects')
        if 0:
            print('Live objects...')
            for obj in (leoG.app, leoG.app.gui, leoC.frame, leoC.frame.tree):
                print(obj.__class__.__name__)
        return d

    # @+node:ekr.20251129080858.1: *3* CheckLeo.create_live_objects
    def create_live_objects(self) -> tuple[Any, Any, Any, Any]:
        """Use Leo's bridge to create live objects for Leo's c, g, and p symbols."""

        import leo.core.leoBridge as leoBridge
        from leo.core.leoNodes import VNode
        from leo.plugins.qt_gui import LeoQtGui
        from leo.plugins.qt_frame import LeoQtFrame

        controller = leoBridge.controller(
            gui='nullGui',  # Only 'nullGui' is allowed!
            loadPlugins=False,  # True: attempt to load plugins.
            readSettings=False,  # True: read standard settings files.
            silent=False,  # True: don't print signon messages.
            verbose=False,
        )  # True: print informational messages.

        g = controller.globals()
        c = controller.openLeoFile('dummy')
        p = c.p
        v = VNode(c)

        # Monkey-patch g.app.gui and c.frame.
        g.app.use_splash_screen = False
        g.app.gui = LeoQtGui()
        c.frame = LeoQtFrame(c, 'test-frame', g.app.gui)
        return c, g, p, v

    # @+node:ekr.20251201031243.1: *3* CheckLeo.report
    def report(self, t1: float, t2: float, t3: float) -> None:
        """
        Print a report (controlled by global vars) of the data collected by the
        Visitor class.
        """

        def report_set(the_set: set, tag: str = '') -> None:
            if tag:
                print(f"\n{len(list(the_set))} {tag}...")
            for z in sorted(list(the_set)):
                print(f"  {z}")
            print('')

        print(
            f"check_leo.py: files: {len(self.files)} "
            f"contexts: {stats_contexts} "
            f"attrs: {stats_attrs} "
            f"in {t3 - t1:.2f} sec."
        )
        if report_times:
            print(
                f"Setup: {t2 - t1:.2f} sec.\n Scan: {t3 - t2:.2f} sec.\nTotal: {t3 - t1:.2f} sec."
            )
        if report_all_args:
            report_set(all_args, 'function/method args')
        if report_unusual_attrs:
            unusual_attrs = [
                z
                for z in all_attrs
                if not z.startswith(('"', "'")) and any(z2 in z for z2 in '()[]{}')
            ]
            print(f"{len(unusual_attrs)} Unusual attrs..")
            for z in sorted(list(unusual_attrs)):
                print(f"  {z}")
        elif report_all_attrs:
            report_set(all_attrs, 'attrs')
        if errors:
            report_set(errors, 'Errors')
        if unknown_bases:
            print(f"Unknown bases: {len(list(unknown_bases))}")
            if report_all_unknown_bases:
                report_set(unknown_bases)
        if undefined_chains:
            print(f"Undefined chains: {len(list(undefined_chains))}")
            if report_all_undefined_chains:
                report_set(undefined_chains)
        if 0:
            if not any(z for z in (all_attrs, errors, unknown_bases, undefined_chains)):
                print('Done')

    # @+node:ekr.20251130081419.1: *3* CheckLeo.run
    def run(self) -> None:
        """The main line of this script."""
        global leoC, leoG, leoP, leoV
        global module_name
        t1 = time.process_time()
        self.adjust_sys_path()
        leoC, leoG, leoP, leoV = self.create_live_objects()  # Takes about 0.9 sec.
        self.files = self.compute_files()
        self.known_objects = self.create_known_objects()
        t2 = time.process_time()
        for path in self.files:
            module_name = self.compute_module_name(path)
            self.check(path)
        t3 = time.process_time()
        self.report(t1, t2, t3)

    # @-others


# @+node:ekr.20251129092833.1: ** class Visitor(ast.NodeVisitor)
class Visitor(ast.NodeVisitor):
    # Cumulative tracing date...
    shown_contexts: list[ast.AST] = []
    shown_modules: list[ast.AST] = []

    def __init__(self, known_objects: dict[str, Any]) -> None:
        # Per-file data.
        self.args_stack: list[str] = []
        self.context_stack: list[ast.AST] = []
        self.known_objects = known_objects

    # @+others
    # @+node:ekr.20251202084740.1: *3* Visitor.context_name
    def context_name(self) -> str:
        """Return the name of the present traversal context."""
        node = self.context_stack[-1]
        return node.name if isinstance(node, ((ast.ClassDef, ast.FunctionDef))) else module_name

    # @+node:ekr.20251129080749.7: *3* Visitor.visit_Attribute & helpers
    def visit_Attribute(self, node: ast.AST) -> None:
        """
        The heart of the Visitor class.

        This method, and its helpers, check an entire chain of attributes.

        - split_Attribute converts (accurately) an Attribute *tree* to a list
          of strings (**parts**) corresponding to the outer level attributes of
          the attribute chain. The **base** is the first string in this list.

        - Use Leo's naming conventions (the known_objects dict) to get a live
          object for the base. Do nothing if the base is not in the dict.

        - Thereafter, check whether the present (live) object has an attr for
          the next attr of the chain.

        - Check all parts of the chain until finding an unknown attr.
        """
        global stats_attrs
        stats_attrs += 1
        parts = self.split_Attribute(node)
        chain = '.'.join(parts)
        all_attrs.add(chain)
        obj = self.get_obj(parts)
        i = 0
        while obj is not None:
            try:
                attr = parts[i + 1]
            except IndexError:
                return
            if not hasattr(obj, attr):
                head = '.'.join(parts[: i + 1])
                checked = chain if full_check else f"{head}.{attr}"
                # Use full_check = True for testing.
                if not full_check and self.should_ignore(parts):
                    return
                if show_all_context_flag or (show_context_flag and checked not in undefined_chains):
                    self.show_context(node)
                    print(checked)
                undefined_chains.add(checked)
                # undefined_chains.add(chain)
                return
            # Move to the next obj.
            obj = getattr(obj, attr, None)
            i += 1

        # Do *not* call self.generic_visit here.
        # split_Attribute handles all this node's children.

    # @+node:ekr.20251201064630.1: *4* Visitor.get_obj
    required_prefixes = (
        'c',
        'c1',
        'c2',
        'g',
        'p',
        'p1',
        'p2',
        # These produce unknown bases.
        # 'w', 'widget', 'wrapper',
    )

    def get_obj(self, parts: list[str]) -> Any:
        """Return the live object corresponding to the base of the chain."""
        part0 = parts[0]
        # Return dummy objects.
        if part0.startswith(('"', "'", 's[')):
            return ' '  # A dummy string.
        if part0.startswith('['):
            return []
        if part0.startswith('{'):
            return {}  # A dummy dict

        # Is the base a known object?
        obj = self.known_objects.get(part0)
        if obj is not None:  # Careful: allow empty strings, lists, dicts.
            return obj  # Success.
        if part0 in self.required_prefixes:
            unknown_bases.add(f"{part0} in {'.'.join(parts)}")
        return None  # Failure.

    # @+node:ekr.20251203044755.1: *4* Visitor.should_ignore
    # @+<< define Attribute ignore_dict >>
    # @+node:ekr.20251201051957.1: *5* << define Attribute ignore_dict >>
    # A list of (prefixes of) chains to be ignored.
    ignore_list = (
        # Obsolete ast Nodes in leoAst.py.
        'ast.Num',
        'ast.Str',
        # Injected by leoserver.py.
        'c.patched_quicksearch_controller',
        'g.in_leo_server',
        'g.leoServer',
        # Injected by plugins.
        'c._bookmarks',
        'c.cleo',
        'c.menuAccels',
        'c.quickMove',
        'c.pluginsMenu',
        'c.screenCastController',
        'c.theScriptingController',
        'c.theTagController',
        'c.vr',  # viewrendered.py
        'g._bookmarks_target',
        'g._bookmarks_target_v',
        'g._quickmove_target_list',
        'g.app.xdb',  # leoDebugger.py
        'p.update_asciidoc',
        # Injected from Qt plugins.
        'c._style_deltas',
        'c.active_stylesheet',
        'c.frame.detached_body_info',
        'c.frame.nav',
        'c.ftm',
        'c.k.autoCompleter',  # PR #4812
        'c.zoom_delta',
        'g.app.openWithTable',
        'g.insqh',
        # Not always present:
        'g.app.config.context_menus',
        'g.app.drag_source',
        'g.app.globalFindTabManager',
        'g.app.gui.log',
        'g.app.gui.set_minibuffer_label',
        'g.app.gui.show_find_success',
        'g.app.openWithTable',
        # p/v properties.
        'p.script',
        'p.v.h',
        'p.v.gnx',
        'p.v.script',
        'v.h',
        'v.gnx',
        # p/v injected attributes.
        'p.v.tempAttributes',
        'p.v.tempAttributes.get',
        # Injected into v...
        'v.archive_ua',
        'v.undo_info',
        'v.unknownAttributes',
        # Exists only io.StringIO objects.
        'sys.stdout.getvalue',
        # Minor mysteries.
        'c.config.exists',
        's.decode',
    )
    ignore_dict = {z: 1 for z in ignore_list}
    # @-<< define Attribute ignore_dict >>

    def should_ignore(self, parts: list[str]) -> bool:
        """
        Return True if the ignore_dict contains a key matching any prefix of
        the parts.
        """
        prefix = []
        for part in parts:
            prefix.append(part)
            if '.'.join(prefix) in self.ignore_dict:
                return True
        return False

    # @+node:ekr.20251203015013.1: *4* Visitor.show_context
    def show_context(self, node: ast.AST) -> None:
        """Print the traversal context of the given node."""
        context = self.context_stack[-1]
        if context in self.shown_contexts:
            return
        self.shown_contexts.append(context)
        if module_name not in self.shown_modules:
            self.shown_modules.append(module_name)
            print(f"\nmodule {module_name}")
        if isinstance(context, ast.ClassDef):
            print(f"class {context.name}")
        elif isinstance(context, ast.FunctionDef):
            print(f"\nfunction {context.name}")

    # @+node:ekr.20251201032057.1: *4* Visitor.split_Attribute
    def split_Attribute(self, node: ast.AST) -> list[str]:
        """
        Return the (correct!) outer-level components of an attribute chain.

        This would be wrong: ast.unparse(node).split('.')
        """
        result: list[str] = []

        def _helper(node: ast.AST, result: list[str]) -> None:
            if isinstance(node, ast.Attribute):
                _helper(node.value, result)
                tail = node.attr
            elif isinstance(node, ast.Name):
                tail = node.id
            else:
                tail = ast.unparse(node)
            result.append(tail)

        _helper(node, result)
        return result

    # @+node:ekr.20251202073629.1: *3* Visitor.visit_ClassDef
    def visit_ClassDef(self, node: ast.AST) -> None:
        global stats_contexts
        stats_contexts += 1
        try:
            self.context_stack.append(node)
            self.generic_visit(node)
        finally:
            self.context_stack.pop()

    # @+node:ekr.20251202073629.2: *3* Visitor.visit_FunctionDef & get_args
    def visit_FunctionDef(self, node: ast.AST) -> None:
        global stats_contexts
        stats_contexts += 1
        try:
            self.context_stack.append(node)
            args = self.get_args(node)
            self.args_stack.append(args)
            self.generic_visit(node)
        finally:
            self.context_stack.pop()
            self.args_stack.pop()

    def get_func_args(self) -> list[str]:
        return self.context_stack[-1]

    # @+node:ekr.20251203072709.1: *4* Visitor.get_args
    def get_args(self, node) -> list[str]:
        result: list[str] = []
        try:
            args = node.args
            posonlyargs = getattr(args, 'posonlyargs', [])
            vararg = [args.vararg] if getattr(args, 'vararg', None) else []
            kwonlyargs = getattr(args, 'kwonlyargs', [])
            kwarg = [args.kwarg] if getattr(args, 'kwarg', None) else []
            for aList in (posonlyargs, vararg, kwonlyargs, kwarg):
                for z in aList:
                    if z:
                        # result.append(ast.unparse(z))
                        result.append(z.arg)
                        all_args.add(z.arg)
        except Exception as e:
            print(e)
            result = []
        return result

    # @+node:ekr.20251202071202.1: *3* Visitor.visit_Module
    def visit_Module(self, node: ast.AST) -> None:
        global stats_contexts
        stats_contexts += 1
        try:
            self.context_stack.append(node)
            self.generic_visit(node)
        finally:
            self.context_stack.pop()

    # @-others


# @-others
CheckLeo().run()

# @@language python
# @-leo
