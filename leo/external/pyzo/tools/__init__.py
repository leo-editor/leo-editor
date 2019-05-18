# -*- coding: utf-8 -*-
# Copyright (C) 2013, the Pyzo development team
#
# Pyzo is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


""" Package tools of pyzo

A tool consists of a module which contains a class. The id of
a tool is its module name made lower case. The module should
contain a class corresponding to its id. We advise to follow the
common python style and start the class name with a capital
letter, case does not matter for the tool to work though.
For instance, the tool "pyzologger" is the class "PyzoLogger" found
in module "pyzoLogger"

The module may contain the following extra variables (which should
be placed within the first 50 lines of code):

tool_name - A readable name for the tool (may contain spaces,
will be shown in the tab)

tool_summary - A single line short summary of the tool. To be
displayed in the statusbar.
"""

# tools I'd like:
# - find in files
# - workspace
# - source tree
# - snipet manager
# - file browser
# - pythonpath editor, startupfile editor (or as part of pyzo?)

import os, sys, imp

import pyzo
from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa
from pyzo.util import zon as ssdf
from pyzo import translate


class ToolDockWidget(QtWidgets.QDockWidget):
    """ A dock widget that holds a tool.
    It sets all settings, initializes the tool widget, and notifies the
    tool manager on closing.
    """
        
    def __init__(self, parent, toolManager):
        QtWidgets.QDockWidget.__init__(self, parent)
        
        # Store stuff
        self._toolManager = toolManager
        
        # Allow docking anywhere, othwerise restoring state wont work properly
        
        # Set other settings
        self.setFeatures(   QtWidgets.QDockWidget.DockWidgetMovable |
                            QtWidgets.QDockWidget.DockWidgetClosable |
                            QtWidgets.QDockWidget.DockWidgetFloatable
                            #QtWidgets.QDockWidget.DockWidgetVerticalTitleBar
                            )
    
    
    def setTool(self, toolId, toolName, toolClass):
        """ Set the tool information. Call this right after
        initialization. """
        
        # Store id and set object name to enable saving/restoring state
        self._toolId = toolId
        self.setObjectName(toolId)
        
        # Set name
        self.setWindowTitle(toolName)
        
        # Create tool widget
        self.reload(toolClass)
    
    
    def closeEvent(self, event):
        if self._toolManager:
            self._toolManager.onToolClose(self._toolId)
            self._toolManager = None
        # Close and delete widget
        old = self.widget()
        if old:
            old.close()
            old.deleteLater()
        # Close and delete dock widget
        self.close()
        self.deleteLater()
        # We handled the event
        event.accept()
    
    
    def reload(self, toolClass):
        """ Reload the widget with a new widget class. """
        old = self.widget()
        new = toolClass(pyzo.main)
        self.setWidget(new)
        if old:
            old.close()
            old.deleteLater()
    


class ToolDescription:
    """ Provides a description of a tool and has a reference to
    the tool dock instance if it is loaded.
    """
    
    def __init__(self, modulePath, name='', description=''):
        # Set names
        self.modulePath = modulePath
        self.moduleName = os.path.splitext(os.path.basename(modulePath))[0]
        self.id = self.moduleName.lower()
        if name:
            self.name = name
        else:
            self.name = self.id
        
        # Set description
        self.description = description
        # Init instance to None, will be set when loaded
        self.instance = None
    
    def menuLauncher(self, value):
        """ Function that is called by the menu when this tool is selected.
        """
        if value is None:
            return bool(self.instance)
            #return self.id in pyzo.toolManager._activeTools
        elif value:
            pyzo.toolManager.loadTool(self.id)
        else:
            self.widget = None
            pyzo.toolManager.closeTool(self.id)



class ToolManager(QtCore.QObject):
    """ Manages the tools. """
    
    # This signal indicates a change in the loaded tools
    toolInstanceChange = QtCore.Signal()

    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        
        # list of ToolDescription instances
        self._toolInfo = None
        self._activeTools = {}
    
    
    def loadToolInfo(self):
        """ (re)load the tool information.
        """
        # Get paths to load files from
        toolDir1 = os.path.join(pyzo.pyzoDir, 'tools')
        toolDir2 = os.path.join(pyzo.appDataDir, 'tools')
        
        # Create list of tool files
        toolfiles = []
        for toolDir in [toolDir1, toolDir2]:
            tmp = [os.path.join(toolDir, f) for f in os.listdir(toolDir)]
            toolfiles.extend(tmp)
        
        # Note: we do not use the code below anymore, since even the frozen
        # app makes use of the .py files.
#         # Get list of files, also when we're in a zip file.
#         i = tooldir.find('.zip')
#         if i>0:
#             # Get list of files from zipfile
#             tooldir = tooldir[:i+4]
#             import zipfile
#             z = zipfile.ZipFile(tooldir)
#             toolfiles = [os.path.split(i)[1] for i in z.namelist()
#                         if i.startswith('visvis') and i.count('functions')]
#         else:
#             # Get list of files from file system
#             toolfiles = os.listdir(tooldir)
        
        # Iterate over tool modules
        newlist = []
        for file in toolfiles:
            modulePath = file
            
            # Check
            if os.path.isdir(file):
                file = os.path.join(file, '__init__.py')  # A package perhaps
                if not os.path.isfile(file):
                    continue
            elif file.endswith('__.py') or not file.endswith('.py'):
                continue
            elif file.endswith('pyzoFileBrowser.py'):
                # Skip old file browser (the file can be there from a previous install)
                continue
            
            #
            toolName = ""
            toolSummary = ""
            # read file to find name or summary
            linecount = 0
            for line in open(file, encoding='utf-8'):
                linecount += 1
                if linecount > 50:
                    break
                if line.startswith("tool_name"):
                    i = line.find("=")
                    if i<0: continue
                    line = line.rstrip("\n").rstrip("\r")
                    line = line[i+1:].strip(" ")
                    toolName = eval(line)  # applies translation
                elif line.startswith("tool_summary"):
                    i = line.find("=")
                    if i<0: continue
                    line = line.rstrip("\n").rstrip("\r")
                    line = line[i+1:].strip(" ")
                    toolSummary = line.strip("'").strip('"')
                else:
                    pass
            
            # Add stuff
            tmp = ToolDescription(modulePath, toolName, toolSummary)
            newlist.append(tmp)
        
        # Store and return
        self._toolInfo = sorted( newlist, key=lambda x:x.id )
        self.updateToolInstances()
        return self._toolInfo
    
    
    def updateToolInstances(self):
        """ Make tool instances up to date, so that it can be seen what
        tools are now active. """
        for toolDes in self.getToolInfo():
            if toolDes.id in self._activeTools:
                toolDes.instance = self._activeTools[toolDes.id]
            else:
                toolDes.instance = None
        
        # Emit update signal
        self.toolInstanceChange.emit()
    
    
    def getToolInfo(self):
        """ Like loadToolInfo(), but use buffered instance if available.
        """
        if self._toolInfo is None:
            self.loadToolInfo()
        return self._toolInfo
    
    
    def getToolClass(self, toolId):
        """ Get the class of the tool.
        It will import (and reload) the module and get the class.
        Some checks are performed, like whether the class inherits
        from QWidget.
        Returns the class or None if failed...
        """
        
        # Make sure we have the info
        if self._toolInfo is None:
            self.loadToolInfo()
        
        # Get module name and path
        for toolDes in self._toolInfo:
            if toolDes.id == toolId:
                moduleName = toolDes.moduleName
                modulePath = toolDes.modulePath
                break
        else:
            print("WARNING: could not find module for tool", repr(toolId))
            return None
        
        # Remove from sys.modules, to force the module to reload
        for key in [key for key in sys.modules]:
            if key and key.startswith('pyzo.tools.'+moduleName):
                del sys.modules[key]
        
        # Load module
        try:
            m_file, m_fname, m_des = imp.find_module(moduleName, [os.path.dirname(modulePath)])
            mod = imp.load_module('pyzo.tools.'+moduleName, m_file, m_fname, m_des)
        except Exception as why:
            print("Invalid tool " + toolId +":", why)
            return None
        
        # Is the expected class present?
        className = ""
        for member in dir(mod):
            if member.lower() == toolId:
                className = member
                break
        else:
            print("Invalid tool, Classname must match module name '%s'!" % toolId)
            return None
        
        # Does it inherit from QWidget?
        plug = mod.__dict__[className]
        if not (isinstance(plug,type) and issubclass(plug,QtWidgets.QWidget)):
            print("Invalid tool, tool class must inherit from QWidget!")
            return None
        
        # Succes!
        return plug
    
    
    def loadTool(self, toolId, splitWith=None):
        """ Load a tool by creating a dock widget containing the tool widget.
        """
        
        # A tool id should always be lower case
        toolId = toolId.lower()
        
        # Close old one
        if toolId in self._activeTools:
            old = self._activeTools[toolId].widget()
            self._activeTools[toolId].setWidget(QtWidgets.QWidget(pyzo.main))
            if old:
                old.close()
                old.deleteLater()
        
        # Get tool class (returns None on failure)
        toolClass = self.getToolClass(toolId)
        if toolClass is None:
            return
        
        # Already loaded? reload!
        if toolId in self._activeTools:
            self._activeTools[toolId].reload(toolClass)
            return
        
        # Obtain name from buffered list of names
        for toolDes in self._toolInfo:
            if toolDes.id == toolId:
                name = toolDes.name
                break
        else:
            name = toolId
        
        # Make sure there is a config entry for this tool
        if not hasattr(pyzo.config.tools, toolId):
            pyzo.config.tools[toolId] = ssdf.new()
        
        # Create dock widget and add in the main window
        dock = ToolDockWidget(pyzo.main, self)
        dock.setTool(toolId, name, toolClass)
        
        if splitWith and splitWith in self._activeTools:
            otherDock = self._activeTools[splitWith]
            pyzo.main.splitDockWidget(otherDock, dock, QtCore.Qt.Horizontal)
        else:
            pyzo.main.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        
        # Add to list
        self._activeTools[toolId] = dock
        self.updateToolInstances()
        
    
    def reloadTools(self):
        """ Reload all tools. """
        for id in self.getLoadedTools():
            self.loadTool(id)
    
    
    def closeTool(self, toolId):
        """ Close the tool with specified id.
        """
        if toolId in self._activeTools:
            dock = self._activeTools[toolId]
            dock.close()
    
    def getTool(self, toolId):
        """ Get the tool widget instance, or None
        if not available. """
        if toolId in self._activeTools:
            return self._activeTools[toolId].widget()
        else:
            return None
    
    def onToolClose(self, toolId):
        # Remove from dict
        self._activeTools.pop(toolId, None)
        # Set instance to None
        self.updateToolInstances()
    
    
    def getLoadedTools(self):
        """ Get a list with id's of loaded tools. """
        tmp = []
        for toolDes in self.getToolInfo():
            if toolDes.id in self._activeTools:
                tmp.append(toolDes.id)
        return tmp
