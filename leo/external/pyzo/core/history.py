import os
import datetime

import pyzo
from pyzo.util.qt import QtCore, QtGui, QtWidgets  # noqa


class CommandHistory(QtCore.QObject):
    """ Keep track of a (global) history of commands.
    
    This kinda assumes Python commands, but should be easy enough to generalize.
    """
    
    max_commands = 2000
    
    command_added = QtCore.Signal(str)
    command_removed = QtCore.Signal(int)
    commands_reset = QtCore.Signal()
    
    
    def __init__(self, fname):
        super().__init__()
        self._commands = []
        self._fname = fname
        self._last_date = datetime.date(2000, 1, 1)
        self._load()
    
    def _load(self):
        """ Load commands from file.
        """
        if not self._fname:
            return
        
        assert not self._commands
        
        try:
            filename = os.path.join(pyzo.appDataDir, self._fname)
            if not os.path.isfile(filename):
                with open(filename, 'wb'):
                    pass
            
            # Load lines and add to commands
            lines = open(filename, 'r', encoding='utf-8').read().splitlines()
            self._commands.extend([line.rstrip() for line in lines[-self.max_commands:]])
            
            # Resolve last date
            for c in reversed(lines):
                if c.startswith('# ==== '):
                    try:
                        c = c.split('====')[1].strip()
                        self._last_date = datetime.datetime.strptime(c, '%Y-%m-%d').date()
                        break
                    except Exception:
                        pass
        
        except Exception as e:
            print('An error occurred while loading the history: ' + str(e))
    
    def save(self):
        """ Save the commands to disk.
        """
        if not self._fname:
            return
        filename = os.path.join(pyzo.appDataDir, self._fname)
        try:
            with open(filename, 'wt', encoding='utf-8') as f:
                f.write('\n'.join(self._commands))
        except Exception:
            print('Could not save command history')
    
    def get_commands(self):
        """ Get a list of all commands (latest last).
        """
        return self._commands.copy()
    
    def append(self, command):
        """ Add a command to the list.
        """
        command = command.rstrip()
        if not command:
            return
        
        # Add date?
        today = datetime.date.today()
        if today > self._last_date:
            self._last_date = today
            self._commands.append('# ==== ' + today.strftime('%Y-%m-%d'))
            self.command_added.emit(self._commands[-1])
        
        # Clear it
        try:
            index = self._commands.index(command)
        except ValueError:
            pass
        else:
            self._commands.pop(index)
            self.command_removed.emit(index)
        
        # Append
        self._commands.append(command)
        self.command_added.emit(self._commands[-1])
        
        # Reset?
        if len(self._commands) > self.max_commands:
            self._commands[:self.max_commands // 2] = []
            self.commands_reset.emit()
    
    def pop(self, index):
        """ Remove a command by index.
        """
        self._commands.pop(index)
        self.command_removed.emit(index)
    
    def find_starting_with(self, firstpart, n=1):
        """ Find the nth (1-based) command that starts with firstpart, or None.
        """
        count = 0
        for c in reversed(self._commands):
            if c.startswith(firstpart):
                count += 1
                if count >= n:
                    return c
        return None

    def find_all(self, needle):
        """ Find all commands that contain the given text. In order
        of being used.
        """
        commands = []
        for c in reversed(self._commands):
            if needle in c:
                commands.append(c)
        return commands
