## Introduction
"""
Welcome to the tutorial for Pyzo! This tutorial should get you
familiarized with Pyzo in just a few minutes. If you feel this tutorial
contains errors or lacks some information, please let us know via
pyzo@googlegroups.com.

Pyzo is a cross-platform Python IDE focused on interactivity and
introspection, which makes it very suitable for scientific computing.
Its practical design is aimed at simplicity and efficiency.

Pyzo consists of two main components, the editor and the shell, and
uses a set of pluggable tools to help the programmer in various ways.

"""


## The editor
"""
The editor (this window) is where your code is located; it is the central
component of Pyzo.

In the editor, each open file is represented as a tab. By right-clicking on
a tab, files can be run, saved, closed, etc.

The right mouse button also enables one to make a file the MAIN FILE of
a project. This file can be recognized by its star symbol and its blue filename,
and it enables running the file more easily (as we will see later in this
tutorial).

For larger projects, the Project manager tool can be used to manage your files
(also described later in this tutorial)
"""


## The shells
"""
The other main component is the window that holds the shells. When Pyzo
starts, a default shell is created. You can add more shells that run
simultaneously, and which may be of different Python versions.

It is good to know that the shells run in a sub-process, such that
when it is busy, Pyzo itself stays responsive, which allows you to
keep coding and even run code in another shell.

Another notable feature is that Pyzo can integrate the event loop of
five different GUI toolkits, thus enabling interactive plotting with
e.g., Visvis or Matplotlib.
  
Via "Shell > Edit shell configurations", you can edit and add shell
configurations. This allows you to for example select the initial
directory, or use a custom PYTHONPATH.

"""


## The tools
"""
Via the "Tools" menu, one can select which tools to use. The tools can
be positioned in any way you want, and can also be un-docked.

Try the "Source Structure" tool to see the outline of this tutorial!

Note that the tools system is designed such that it's quite easy to
create your own tools. Look at the online wiki for more information,
or use one of the existing tools as an example. Also, Pyzo does not
need to restart to see new tools, or to update existing tools.

"""


## Running code
"""
Pyzo supports several ways to run source code in the editor. (see
also the "Run" menu).

  * Run selected lines. If a line is partially selected, the whole
    line is executed. If there is no selection, Pyzo will run the
    current line.
    
  * Run cell. A cell is everything between two commands starting
    with '##', such as the headings in this tutorial. Try running
    the code at the bottom of this cell!

  * Run file. This runs all the code in the current file.
  
  * Run project main file. Runs the code in the current project's
    main file.

Additionally, you can run the current file or the current project's
main file as a script. This will first restart the shell to provide
a clean environment. The shell is also initialized differently:

Things done on shell startup in INTERACTIVE MODE:
  * sys.argv = ['']
  * sys.path is prepended with an empty string (current working directory)
  * The working dir is set to the "Initial directory" of the shell config.
  * The PYTHONSTARTUP script is run.

Things done on shell startup in SCRIPT MODE:
  * __file__ = <script_filename>
  * sys.argv = [ <script_filename> ]
  * sys.path is prepended with the directory containing the script.
  * The working dir is set to the directory containing the script.

Depending on the settings of the Project mananger, the current project
directory may also be inserted in sys.path.
"""

a = 3
b = 4
print('The answer is ' + str(a+b))


## The menu
"""
Almost all functionality of Pyzo can be accessed via the menu. For more
advanced/specific stuff, you can use the logger tool (see also
Settings > Advanced settings)

All actions in the menu can be accessed via a shortcut. Change the
shortcuts using the shortcut editor: Settings > Edit key mappings.
  
"""

  
## Introspection
"""
Pyzo has strong introspection capabilities. Pyzo knows about the objects
in the shell, and parses (not runs) the source code in order to detect
the structure of your code. This enables powerful instospection such
as autocompletion, calltips, interactive help and source structure.
  
"""


## Debugging
"""
Pyzo supports post-mortem debugging, which means that after something
went wrong, you can inspect the stack trace to find the error.

The easiest way to start debugging is to press the "Debug" button
at the upper right corner of the shells.

Once in debug mode, the button becomes expandable, allowing you to
see the stack trace and go to any frame you like. (Starting debug mode
brings you to the bottom frame.) Changing a frame will make all objects
in that frame available in the shell. If possible, Pyzo will also show
the source file belonging to that frame, and select the line where the
error occurred.

Debugging can also be controlled via magic commands, enter "?" in the
shell for more information.

Below follows an example that you can run to test the debugging.
  
"""

import random
someModuleVariable = True

def getNumber():
    return random.choice(range(10))

def foo():
    spam = 'yum'
    eggs = 7
    value = bar()
    
def bar():
    total = 0
    for i1 in range(100):
        i2 = getNumber()
        total += i1/i2
    return total

foo()

## The Project manager
"""
For working on projects, the Project manager tool can help you to keep
an overview of all your files. To open up the Project manager tool,
select it from the menu (Tools > Project manager).

To add, remove, or edit your projects, click the button with the
wrench icon. In the dialog, select 'New project' to add a project and
select the directory where your project is located. When the project
is added, you can change the Project description (name).

You can select wether the project path is added to the Python
sys.path. This feature allows you to import project modules from the
shell, or from scripts which are not in the project root directory.
Note that this feature requires a restart of the shell to take effect
(Shell > Restart)

The Project manager allows you to switch between your projects easily
using the selection box at the top. The tree view shows the files and
directories in your project. Files can be hidden using the filter that
is specified at the bottom of the Project manager, e.g. !*.pyc to hide
all files that have the extension pyc.
"""

