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
#@+node:ekr.20210907103024.3: *3* cover-all
#@@nowrap
@g.command('cover-all')
def cover_all(event=None):
    """Run all coverage tests in leo.unittests."""
    if 1:
        # This is usually best:
        # - It creates a full report in leo/unittests/htmlcov/index.html.
        # - It runs all unit tests in the leo.unittests directory.
        g.run_coverage_tests()
    else:
        unittests_dir = g.os_path_finalize_join(g.app.loadDir, '..', 'unittests')
        assert os.path.exists(unittests_dir)
        os.chdir(unittests_dir)
        # This runs only the listed files. index.html describes only the last file.
        table = (
            ('leo.core.leoApp', 'core/test_leoApp.py'),
            ('leo.core.leoAst', 'core/test_leoAst.py'),
            ('leo.core.leoAtFile', 'core/test_leoAtFile.py'),
            ('leo.core.leoBridge', 'core/test_leoBridge.py'),
            ('leo.commands.checkerCommands', 'commands/test_checkerCommands.py'),
            ('leo.core.leoColorizer', 'core/test_leoColorizer.py'),
            ('leo.core.leoCommands', 'core/test_leoCommands.py'),
            ('leo.core.leoConfig', 'core/test_leoConfig.py'),
            ('leo.commands.convertCommands', 'commands/test_convertCommands.py'),
            ('leo.commands.editCommands', 'commands/test_editCommands.py'),
            ('leo.core.leoFileCommands', 'core/test_leoFileCommands.py'),
            ('leo.core.leoFind', 'core/test_leoFind.py'),
            ('leo.core.leoFrame', 'core/test_leoFrame.py'),
            ('leo.core.leoGlobals', 'core/test_leoGlobals.py'),
            ('leo.core.leoImport', 'core/test_leoImport.py'),
            ('leo.core.leoKeys', 'core/test_leoKeys.py'),
            ('leo.core.leoserver', 'core/test_leoserver.py'),
            ('leo.core.leoNodes', 'core/test_leoNodes.py'),
            ('leo.core.leoPersistence', 'core/test_leoPersistence.py'),
            ('leo.core.leoRst', 'core/test_leoRst.py'),
            ('leo.core.leoShadow', 'core/test_leoShadow.py'),
            ('leo.core.leoUndo', 'core/test_leoUndo.py'),
            ('leo.core.leoVim', 'core/test_leoVim.py'),
        )
        for module, filename in table:
            g.run_coverage_tests(module, filename)
#@+node:ekr.20210911072153.3: *3* cover-app
@g.command('cover-app')
def cover_app(event=None):
    """Run all coverage tests for leoApp.py."""
    g.run_coverage_tests('leo.core.leoApp', 'core/test_leoApp.py')
#@+node:ekr.20210907103024.4: *3* cover-ast
@g.command('cover-ast')
def cover_ast(event=None):
    """Run all coverage tests for leoAst.py."""
    g.run_coverage_tests('leo.core.leoAst', 'core/test_leoAst.py')
#@+node:ekr.20210907103024.5: *3* cover-atfile
@g.command('cover-atfile')
def cover_atfile(event=None):
    """Run all coverage tests for leoAtFile.py."""
    g.run_coverage_tests('leo.core.leoAtFile', 'core/test_leoAtFile.py')
#@+node:ekr.20210911072153.6: *3* cover-bridge
@g.command('cover-bridge')
def cover_bridge(event=None):
    """Run all coverage tests for leoBridge.py."""
    g.run_coverage_tests('leo.core.leoBridge', 'core/test_leoBridge.py')
#@+node:ekr.20210911072153.7: *3* cover-checker-commands
@g.command('cover-checker-commands')
def cover_checker_commands(event=None):
    """Run all coverage tests for leoCheckerCommands.py."""
    g.run_coverage_tests('leo.commands.checkerCommands', 'commands/test_checkerCommands.py')
#@+node:ekr.20210911072153.8: *3* cover-colorizer
@g.command('cover-colorizer')
def cover_colorizer(event=None):
    """Run all coverage tests for leoColorizer.py."""
    g.run_coverage_tests('leo.core.leoColorizer', 'core/test_leoColorizer.py')
#@+node:ekr.20210911072153.10: *3* cover-commands
@g.command('cover-commands')
def cover_commands(event=None):
    """Run all coverage tests for leoCommands.py."""
    g.run_coverage_tests('leo.core.leoCommands', 'core/test_leoCommands.py')
#@+node:ekr.20220109041701.1: *3* cover-convert-commands
@g.command('cover-convert-commands')
def cover_convert_commands(event=None):
    """Run all coverage tests for convertCommands.py."""
    g.run_coverage_tests('leo.commands.convertCommands', 'commands/test_convertCommands.py')
#@+node:ekr.20210911072153.9: *3* cover-config
@g.command('cover-config')
def cover_config(event=None):
    """Run all coverage tests for leoConfig.py."""
    g.run_coverage_tests('leo.core.leoConfig', 'core/test_leoConfig.py')
#@+node:ekr.20210907103024.6: *3* cover-edit-commands
@g.command('cover-edit-commands')
def cover_edit_commands(event=None):
    """Run all coverage tests for leoEditCommands.py."""
    g.run_coverage_tests('leo.commands.editCommands', 'commands/test_editCommands.py')
#@+node:ekr.20210911072153.12: *3* cover-external-files
@g.command('cover-external-files')
def cover_external_files(event=None):
    """Run all coverage tests for leoExternalFiles.py."""
    g.run_coverage_tests('leo.core.leoExternalFiles', 'core/test_leoExternalFiles.py')
#@+node:ekr.20210911072153.14: *3* cover-file-commands
@g.command('cover-file-commands')
def cover_file_commands(event=None):
    """Run all coverage tests for leoFileCommands.py."""
    g.run_coverage_tests('leo.core.leoFileCommands', 'core/test_leoFileCommands.py')
#@+node:ekr.20210907103024.7: *3* cover-find
@g.command('cover-find')
def cover_find(event=None):
    """Run all coverage tests for leoFind.py."""
    g.run_coverage_tests('leo.core.leoFind', 'core/test_leoFind.py')
#@+node:ekr.20210911072153.15: *3* cover-frame
@g.command('cover-frame')
def cover_frame(event=None):
    """Run all coverage tests for leoFrame.py."""
    g.run_coverage_tests('leo.core.leoFrame', 'core/test_leoFrame.py')
#@+node:ekr.20210911072153.16: *3* cover-globals
@g.command('cover-globals')
def cover_globals(event=None):
    """Run all coverage tests for leoGlobals.py."""
    g.run_coverage_tests('leo.core.leoGlobals', 'core/test_leoGlobals.py')
#@+node:ekr.20210911072153.18: *3* cover-import
@g.command('cover-import')
def cover_import(event=None):
    """Run all coverage tests for leoImport.py."""
    g.run_coverage_tests('leo.core.leoImport', 'core/test_leoImport.py')
#@+node:ekr.20210911072153.19: *3* cover-keys
@g.command('cover-keys')
def cover_keys(event=None):
    """Run all coverage tests for leoKeys.py."""
    g.run_coverage_tests('leo.core.leoKeys', 'core/test_leoKeys.py')
#@+node:ekr.20210911072153.20: *3* cover-leoserver
@g.command('cover-leoserver')
def cover_leoserver(event=None):
    """Run all unittests for leoserver.py"""
    g.run_coverage_tests('leo.core.leoserver', 'core/test_leoserver.py')
#@+node:ekr.20210907103024.8: *3* cover-nodes
@g.command('cover-nodes')
def cover_node(event=None):
    """Run all coverage tests for leoNodes.py."""
    g.run_coverage_tests('leo.core.leoNodes', 'core/test_leoNodes.py')
#@+node:ekr.20210911072153.23: *3* cover-persistence
@g.command('cover-persistence')
def cover_persistence(event=None):
    """Run all coverage tests for leoPersistence.py."""
    g.run_coverage_tests('leo.core.leoPersistence', 'core/test_leoPersistence.py')
#@+node:ekr.20210911072153.25: *3* cover-rst
@g.command('cover-rst')
def cover_rst3(event=None):
    """Run all coverage tests for leoRst.py."""
    g.run_coverage_tests('leo.core.leoRst', 'core/test_leoRst.py')
#@+node:ekr.20210911072153.26: *3* cover-shadow
@g.command('cover-shadow')
def cover_shadow(event=None):
    """Run all coverage tests for leoShadow.py."""
    g.run_coverage_tests('leo.core.leoShadow', 'core/test_leoShadow.py')
#@+node:ekr.20210911072153.28: *3* cover-undo
@g.command('cover-undo')
def cover_undo(event=None):
    """Run all coverage tests for leoUndo.py."""
    g.run_coverage_tests('leo.core.leoUndo', 'core/test_leoUndo.py')
#@+node:ekr.20210911072153.29: *3* cover-vim
@g.command('cover-vim')
def cover_vim(event=None):
    """Run all coverage tests for leoVim.py."""
    g.run_coverage_tests('leo.core.leoVim', 'core/test_leoVim.py')
#@+node:ekr.20210907113937.1: ** unit test commands...
#@+node:ekr.20210907103024.11: *3* test-all
@g.command('test-all')
def test_all(event=None):
    """Run all unit tests in leo.unittests."""
    g.run_unit_tests()
    # g.es_print('test-all: all tests complete')
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
    g.run_unit_tests('leo.unittests.commands.test_checkerCommands')
#@+node:ekr.20210907103024.17: *3* test-colorizer
@g.command('test-colorizer')
def test_colorizer(event=None):
    """Run all unit tests for leoColorizer.py."""
    g.run_unit_tests('leo.unittests.core.test_leoColorizer')
#@+node:ekr.20211013080906.1: *3* test-convert
@g.command('test-convert')
def test_convert(event=None):
    """Run all unit tests for leo/commands/leoConvertCommands.py."""
    g.run_unit_tests('leo.unittests.commands.test_convertCommands')
        #.TestPythonToTypeScript')
#@+node:ekr.20210907103024.18: *3* test-commands
@g.command('test-commands')
def test_commands(event=None):
    """Run all unit tests for leoCommands.py."""
    g.run_unit_tests('leo.unittests.core.test_leoCommands')
#@+node:ekr.20210910074026.1: *3* test-config
@g.command('test-config')
def test_config(event=None):
    """Run all unit tests for leoConfig.py."""
    g.run_unit_tests('leo.unittests.core.test_leoConfig')
#@+node:ekr.20210926051147.1: *3* test-doctests
@g.command('test-doctests')
def test_doctests(event=None):
    """Run all doctests in Leo."""
    g.run_unit_tests('leo.unittests.test_doctests')
#@+node:ekr.20210907103024.19: *3* test-edit-commands
@g.command('test-edit-commands')
def test_edit_commands(event=None):
    """Run all unit tests for leo.commands.editCommands."""
    g.run_unit_tests('leo.unittests.commands.test_editCommands')
#@+node:ekr.20210907103024.20: *3* test-external-files
@g.command('test-external-files')
def test_external_files(event=None):
    """Run all unit tests for leoExternalFiles.py."""
    g.run_unit_tests('leo.unittests.core.test_leoExternalFiles')
#@+node:ekr.20210910065945.1: *3* test-file-commands
@g.command('test-file-commands')
def test_file_commands(event=None):
    """Run all unit tests for leoFileCommands.py."""
    g.run_unit_tests('leo.unittests.core.test_leoFileCommands')
#@+node:ekr.20210907103024.21: *3* test-find
@g.command('test-find')
def test_find(event=None):
    """Run all unit tests for leoFind.py."""
    g.run_unit_tests('leo.unittests.core.test_leoFind')
#@+node:ekr.20210907103024.22: *3* test-frame
@g.command('test-frame')
def test_frame(event=None):
    """Run all unit tests for leoFrame.py."""
    g.run_unit_tests('leo.unittests.core.test_leoFrame')
#@+node:ekr.20210907103024.23: *3* test-globals
@g.command('test-globals')
def test_globals(event=None):
    """Run all unit tests for leoGlobals.py."""
    g.run_unit_tests('leo.unittests.core.test_leoGlobals')
#@+node:ekr.20210907103024.24: *3* test-import
@g.command('test-import')
def test_import(event=None):
    """Run all unit tests for leoImport.py."""
    g.run_unit_tests('leo.unittests.core.test_leoImport')
#@+node:ekr.20210907103024.25: *3* test-keys
@g.command('test-keys')
def test_keys(event=None):
    """Run all unit tests for leoKeys.py."""
    g.run_unit_tests('leo.unittests.core.test_leoKeys.TestKeys')
#@+node:ekr.20210907103024.29: *3* test-leoserver
@g.command('test-leoserver')
def test_leoserver(event=None):
    """Run all unittests for leoserver.py"""
    g.run_unit_tests('leo.unittests.core.test_leoserver')
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
    g.run_unit_tests('leo.unittests.core.test_leoNodes')
#@+node:ekr.20210909091424.1: *3* test-persistence
@g.command('test-persistence')
def test_persistence(event=None):
    """Run all unit tests for leoPersistence.py."""
    g.run_unit_tests('leo.unittests.core.test_leoPersistence')
#@+node:ekr.20210907103024.27: *3* test-plugins
@g.command('test-plugins')
def test_plugins(event=None):
    """Run all unit tests relating to plugins."""
    g.run_unit_tests('leo.unittests.test_plugins')
#@+node:ekr.20210907103024.28: *3* test-rst
@g.command('test-rst')
def test_rst3(event=None):
    """Run all unit tests for leoRst.py."""
    g.run_unit_tests('leo.unittests.core.test_leoRst')
#@+node:ekr.20210907103024.30: *3* test-shadow
@g.command('test-shadow')
def test_shadow(event=None):
    """Run all unit tests for leoShadow.py."""
    g.run_unit_tests('leo.unittests.core.test_leoShadow')
#@+node:ekr.20210907103024.31: *3* test-syntax
@g.command('test-syntax')
def test_syntax(event=None):
    """Run all testss in test_syntax.py."""
    g.run_unit_tests('leo.unittests.test_syntax')
#@+node:ekr.20210907103024.32: *3* test-undo
@g.command('test-undo')
def test_undo(event=None):
    """Run all unit tests for leoUndo.py."""
    g.run_unit_tests('leo.unittests.core.test_leoUndo')
#@+node:ekr.20210910073036.1: *3* test-vim
@g.command('test-vim')
def test_vim(event=None):
    """Run all unit tests for leoVim.py."""
    g.run_unit_tests('leo.unittests.core.test_leoVim')
#@+node:ekr.20210910085337.1: *3* test_gui
@g.command('test-gui')
def test_gui(event=None):
    """Run all gui-related unit tests."""
    g.run_unit_tests('leo.unittests.test_gui')
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
