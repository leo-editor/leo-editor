# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20210907103011.1: * @file ../commands/testCommands.py
#@@first
"""Unit tests commands"""

import os
import time
from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20210907103024.2: ** coverage test commands...
if 0:
    #@+others
    #@+node:ekr.20210907103024.3: *3* cov-all
    @g.command('cover-all')
    def cover_all(event=None):
        """Run all coverage tests in leo.unittests."""
        g.run_coverage_tests()
    #@+node:ekr.20210907103024.4: *3* cov-leoAst
    @g.command('cover-ast')
    def cover_ast(event=None):
        """Run all coverage tests for leoAst.py."""
        g.run_coverage_tests('leo.core.leoAst', 'leo/unittests/core/test_leoAst.py')
    #@+node:ekr.20210907103024.5: *3* cov-leoAtFile
    @g.command('cover-atfile')
    def cover_atfile(event=None):
        """Run all coverage tests for leoAtFile.py."""
        g.run_coverage_tests('leo.core.leoAtFile', 'leo/core/leoAtFile.py')
    #@+node:ekr.20210907103024.6: *3* cov-edit-commands
    @g.command('cover-edit-commands')
    def cover_edit_commands(event=None):
        """Run all coverage tests for leoEditCommands.py."""    
        g.run_coverage_tests('leo.commands.leoEditCommands', 'leo/unittests/commands/test_editCommands.py')
    #@+node:ekr.20210907103024.7: *3* cov-leoFind
    @g.command('cover-find')
    def cover_find(event=None):
        """Run all coverage tests for leoFind.py."""
        g.run_coverage_tests('leo.core.leoFind', 'leo/unittests/core/test_leoFind.py')
    #@+node:ekr.20210907103024.8: *3* cov-leoNodes
    @g.command('cover-nodes')
    def cover_node(event=None):
        """Run all coverage tests for leoNodes.py."""
        g.run_coverage_tests('leo.core.leoNodes', 'leo/unittests/core/test_leoNodes.py')
    #@-others
#@+node:ekr.20210907113937.1: ** unit test commands...
#@+node:ekr.20210907103024.11: *3* test-all
@g.command('test-all')
def test_all(event=None):
    """Run all unit tests in leo.unittests."""
    g.run_unit_tests()
    g.es_print('all tests complete')
#@+node:ekr.20210907103024.12: *3* test-app
@g.command('test-app')
def test_app(event=None):
    """Run all unit tests for leoApp.py."""
    g.run_unit_tests('leo.unittests.core.test_leoApp')
#@+node:ekr.20210907103024.13: *3* test-ast
@g.command('test-ast')
def test_ast(event=None):
    """Run all unit tests for leoAst.py."""
    g.run_unit_tests('leo.unittests.core.test_leoAst')
#@+node:ekr.20210907103024.14: *3* test-atfile
@g.command('test-atfile')
def test_atfile(event=None):
    """Run all unit tests for leoAtFile.py."""
    g.run_unit_tests('leo.unittests.core.test_leoAtFile')
#@+node:ekr.20210907103024.15: *3* test-bridge
@g.command('test-bridge')
def test_bridge(event=None):
    """Run all unit tests for leoBridge.py."""
    g.run_unit_tests('leo.unittests.core.test_leoBridge')
#@+node:ekr.20210907103024.16: *3* test-checker-commands
@g.command('test-checker-commands')
def test_checker_commands(event=None):
    """Run all unit tests for leoCheckerCommands.py."""
    g.run_unit_tests('leo.unittests.commands.test_leoCheckerCommands')
#@+node:ekr.20210907103024.17: *3* test-colorizer
@g.command('test-colorizer')
def test_colorizer(event=None):
    """Run all unit tests for leoColorizer.py."""
    g.run_unit_tests('leo.unittests.core.test_leoColorizer.TestColorizer')
#@+node:ekr.20210910074026.1: *3* test-config
@g.command('test-config')
def test_config(event=None):
    """Run all unit tests for leoConfig.py."""
    g.run_unit_tests('leo.unittests.core.test_leoConfig.TestConfig')
#@+node:ekr.20210907103024.18: *3* test-commands
@g.command('test-commands')
def test_commands(event=None):
    """Run all unit tests for leoCommands.py."""
    g.run_unit_tests('leo.unittests.core.test_leoCommands')
#@+node:ekr.20210907103024.19: *3* test-edit-commands
@g.command('test-edit-commands')
def test_edit_commands(event=None):
    """Run all unit tests for leo.commands.editCommands."""
    g.run_unit_tests('leo.unittests.commands.test_editCommands.TestEditCommands')
#@+node:ekr.20210907103024.20: *3* test-external-files
@g.command('test-external-files')
def test_external_files(event=None):
    """Run all unit tests for leoExternalFiles.py."""
    g.run_unit_tests('leo.unittests.core.test_leoExternalFiles')
#@+node:ekr.20210907103024.21: *3* test-find
@g.command('test-find')
def test_find(event=None):
    """Run all unit tests for leoFind.py."""
    g.run_unit_tests('leo.unittests.core.test_leoFind.TestFind')
#@+node:ekr.20210910065945.1: *3* test-file-commands
@g.command('test-file-commands')
def test_file_commands(event=None):
    """Run all unit tests for leoFileCommands.py."""
    g.run_unit_tests('leo.unittests.core.test_leoFileCommands.TestFileCommands')
#@+node:ekr.20210907103024.22: *3* test-frame
@g.command('test-frame')
def test_frame(event=None):
    """Run all unit tests for leoFrame.py."""
    g.run_unit_tests('leo.unittests.core.test_leoFrame.TestFrame')
#@+node:ekr.20210907103024.23: *3* test-globals
@g.command('test-globals')
def test_globals(event=None):
    """Run all unit tests for leoGlobals.py."""
    g.run_unit_tests('leo.unittests.core.test_leoGlobals.TestGlobals')
#@+node:ekr.20210910085337.1: *3* test_gui
@g.command('test-gui')
def test_gui(event=None):
    """Run all gui-related unit tests."""
    g.run_unit_tests('leo.unittests.core.test_gui.TestGui')
#@+node:ekr.20210907103024.24: *3* test-import
@g.command('test-import')
def test_import(event=None):
    """Run all unit tests for leoImport.py."""
    g.run_unit_tests('leo.unittests.core.test_leoImport.TestImporter')
#@+node:ekr.20210907103024.25: *3* test-keys
@g.command('test-keys')
def test_keys(event=None):
    """Run all unit tests for leoKeys.py."""
    g.run_unit_tests('leo.unittests.core.test_leoKeys.TestKeys')
#@+node:ekr.20210907103024.29: *3* test-leoserver
@g.command('test-leoserver')
def test_leoserver(event=None):
    """Run all unittests for leoserver.py"""
    g.run_unit_tests('leo.unittests.core.test_leoserver.TestLeoServer')
#@+node:ekr.20210907103024.10: *3* test-leoserver-with-leoclient
@g.command('test-leoserver-with-leoclient')
def test_leo_client_and_server(event=None):
    """
    Test leoserver.py with leoclient.py.
    
    The test-all command does *not* run this command, because there is
    no corresponding test*.py file.
    """
    g.cls()
    leo_dir = os.path.abspath(os.path.join(g.app.loadDir, '..', '..'))
    assert os.path.exists(leo_dir), repr(leo_dir)
    os.chdir(leo_dir)
    g.execute_shell_commands('start cmd /k "python -m leo.core.leoserver --trace=request,response,verbose"')
    time.sleep(1.5)
    g.execute_shell_commands('start cmd /k "python -m leo.core.leoclient"')
#@+node:ekr.20210907103024.26: *3* test-nodes
@g.command('test-nodes')
def test_nodes(event=None):
    """Run all unit tests for leoNodes.py."""
    g.run_unit_tests('leo.unittests.core.test_leoNodes.TestNodes')
#@+node:ekr.20210909091424.1: *3* test-persistence
@g.command('test-persistence')
def test_persistence(event=None):
    """Run all unit tests for leoPersistence.py."""
    g.run_unit_tests('leo.unittests.core.test_leoPersistence.TestPersistence')
#@+node:ekr.20210907103024.27: *3* test-plugins
@g.command('test-plugins')
def test_plugins(event=None):
    """Run all unit tests relating to plugins."""
    g.run_unit_tests('leo.unittests.test_plugins.TestPlugins')
#@+node:ekr.20210907103024.28: *3* test-rst3
@g.command('test-rst3')
def test_rst3(event=None):
    """Run all unit tests for leoRst3.py."""
    g.run_unit_tests('leo.unittests.core.test_leoRst3.TestRst3')
#@+node:ekr.20210907103024.30: *3* test-shadow
@g.command('test-shadow')
def test_shadow(event=None):
    """Run all unit tests for leoShadow.py."""
    g.run_unit_tests('leo.unittests.core.test_leoShadow.TestAtShadow')
#@+node:ekr.20210907103024.31: *3* test-syntax
@g.command('test-syntax')
def test_syntax(event=None):
    """Run all testss in test_syntax.py."""
    g.run_unit_tests('leo.unittests.test_syntax.TestSyntax')
#@+node:ekr.20210907103024.32: *3* test-undo
@g.command('test-undo')
def test_undo(event=None):
    """Run all unit tests for leoUndo.py."""
    g.run_unit_tests('leo.unittests.core.test_leoUndo.TestUndo')
#@+node:ekr.20210910073036.1: *3* test-vim
@g.command('test-vim')
def test_vim(event=None):
    """Run all unit tests for leoVim.py."""
    g.run_unit_tests('leo.unittests.core.test_leoVim.TestVim')
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
