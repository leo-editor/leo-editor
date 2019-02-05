#@+leo-ver=5-thin
#@+node:DSR.20181126072740.2: * @file git_install.py
#@+<< git_install docstring >>
#@+node:DSR.20181126185212.1: ** << git_install docstring >>
#@@language rest

"""
git_install.py

Version 1.0
Copyright David Speed Ream 25 November 2018
This file is released to public domain.


Install leowapp into a virtual python virtual environment on Ubuntu or
Debian.

run python git_install.py for usage information.

This install does not depend upon or install QT.
This install does require git to be installed.

To use this script to install leowapp in a NOT python virtual environment,
go to the routine:

    run_env_cmd()

and comment out everything except the last two lines. Make sure to examine
the consequences of doing this prior to doing it. Or make a backup first.
    
After this install is completed, new updates to any of the projects
(except tornado) can be pulled from github, getting only the most recent
changes, additions or deletions to any of the project files. After such a
change, the project must be reinstalled again using pip using one of the
script commands. For example, after pulling a change to leowapp, reinstall
leowapp again by:

    starting the virtual environment
    running python git_install.py leoins

This install method requires manually getting zip files for each project
and placing them into the ./zips folder.

All the flexx project zips come from github flexxui. Leo which comes from
github leo-editor. Tornado comes from tornadoweb.

In the ./zips directory, place the following zip files:

    dialite-master.zip
    flexx-master.zip
    leo-editor-skeleton.zip
    pscript-master.zip
    tornado-master.zip
    webruntime-master.zip

The directory structure when starting this script:

    ~/anydir
    ~/anydir/zips
    ~/anydir/zips/dialite-master.zip
    ~/anydir/zips/flexx-master.zip
    ~/anydir/zips/leo-editor-skeleton.zip
    ~/anydir/zips/pscript-master.zip
    ~/anydir/zips/tornado-master.zip
    ~/anydir/zips/webruntime-master.zip

Creating the python virtual environment:

    This is what I did on Ubuntu 18.10

    cd ~/anydir
    python3 -m venv env

Prior to running this install script, and always prior to running leowapp,
enter the virtual env by:

    cd ~/anydir
    source env/bin/activate

After done with work:

    cd ~/anydir
    deactivate

"""
#@-<< git_install docstring >>
#@+<< git_install imports >>
#@+node:DSR.20181126190353.1: ** << git_install imports >>
from os      import environ
from os      import getcwd
from os      import mkdir
from os      import system
from os      import unlink
from os.path import exists
from os.path import join
from pickle  import dump
from pickle  import load
from sys     import argv
from sys     import exit
# from subprocess import Popen, PIPE
#@-<< git_install imports >>
#@+<< define u >>
#@+node:ekr.20181211044817.1: ** << define u >>
#@@language rest

u = \
"""
Basic Usage:

cd ~/this_directory

python3 git_install.py
    print this usage message, then:
    list all available steps

python3 git_install.py show
    show the next step in the sequence

python3 git_install.py next
    do the next step in the sequence

python3 git_install.py <step name>
    do the given step

python3 git_install.py restart
    Restart the process over from the start. This deletes the file data.dat
    from the current directory.

python3 git_install.py commands
    show some interesting command lines used by this script

"""
#@-<< define u >>
#@+<< define cmds >>
#@+node:ekr.20181211044817.2: ** << define cmds >>
#@@language python

# The following lines are displayed by entering:  `python git_install.py commands`

#@@language rest

cmds = \
"""

unzip, force overwrite, to destination folder.

unzip -o myzip.zip -d /home/me/working_stuff/destination_folder

From an existing empty project folder, create a valid .git folder for an
existing github project.

-mkdir /home/me/stuff/my-project/.git
-cd /home/me/stuff/my-project/.git
-git clone --bare --single-branch -b mybranch --depth=1 --shallow-submodules https://github.com/my-project/my-project.git .

After making a valid .git folder for the project, and after extracting the
source files from a git zip into the project folder, setup the project for
use and get any recent changes to the project from github.

-cd /home/me/stuff/my-project
-git init
-git reset HEAD
-git pull --depth=1 --allow-unrelated-histories https://github.com/my-project/my-project.git mybranch
-git status
-After running git status, if any items are marked 'modified' or 'deleted',
then manually run git: checkout <item>
-keep running status and checkout until all items are up to date

Using pip, install a package downloaded via the github process above into
the current python installation without pulling in other dependencies.
Please note that all the given command line options must be used, even when installing a package for the first time.

-pip install --upgrade --no-deps --force-reinstall /home/me/stuff/my-project
"""
#@-<< define cmds >>
#@+<< git_install globals >>
#@+node:DSR.20181126190502.1: ** << git_install globals >>
CWD         = getcwd()
DATA_NAME   = "data.dat"
DATA_FILE   = join(CWD,DATA_NAME)
DIAL_REPO   = "https://github.com/flexxui/dialite.git"
SOURCES     = "sources"
VIRTUAL_ENV ="/home/bridge1/Virtual/leowapp/env"
ar1         = ar2 = ar3 = None

#@-<< git_install globals >>
#@+<< git_install_data >>
#@+node:DSR.20181127213619.1: ** << git_install_data >>
repo_list = (
(
"dialite",
"master",
"/home/bridge1/Virtual/leowapp/zips/dialite-master.zip",
"https://github.com/flexxui/dialite.git",
),
(
"pscript",
"master",
"/home/bridge1/Virtual/leowapp/zips/pscript-master.zip",
"https://github.com/flexxui/pscript.git",
),
(
"tornado",
"master",
"/home/bridge1/Virtual/leowapp/zips/tornado-master.zip",
"https://github.com/tornadoweb/tornado.git",
),
(
"webruntime",
"master",
"/home/bridge1/Virtual/leowapp/zips/webruntime-master.zip",
"https://github.com/flexxui/webruntime.git",
),
(
"flexx",
"master",
"/home/bridge1/Virtual/leowapp/zips/flexx-master.zip",
"https://github.com/flexxui/flexx.git",
),
(
"leo-editor",
"skeleton",
"/home/bridge1/Virtual/leowapp/zips/leo-editor-skeleton.zip",
"https://github.com/leo-editor/leo-editor.git",
),
)

order = (
"dialzip",
"dialgit",
"dialins",
"pscrzip",
"pscrgit",
"pscrins",
"tornzip",
"torngit",
"tornins",
"webrzip",
"webrgit",
"webrins",
"flexzip",
"flexgit",
"flexins",
"leozip",
"leogit",
"leoins",
"leocpy",
)

data = {
"dialzip":("setup_zip('dialite')",
           "Unzip the dialite zip and place it in the correct directory",
           False),
"dialgit":("setup_git('dialite')",
           "Setup the dialite github repo.",
           False),
"dialins":("install('dialite')",
           "Using pip, install dialite from the sources directory",
           False),
"pscrzip":("setup_zip('pscript')",
           "Unzip the pscript zip and place it in the correct directory",
           False),
"pscrgit":("setup_git('pscript')",
           "Setup the pcscript github repo.",
           False),
"pscrins":("install('pscript')",
           "Using pip, install pscript from the sources directory",
           False),
"tornzip":("setup_zip('tornado')",
           "Unzip the tornado zip and place it in the correct directory",
           False),
"torngit":("setup_git('tornado')",
           "Setup the tornado github repo.",
           False),
"tornins":("install('tornado')",
           "Using pip, install tornado from the sources directory",
           False),
"webrzip":("setup_zip('webruntime')",
           "Unzip the webruntime zip and place it in the correct directory",
           False),
"webrgit":("setup_git('webruntime')",
           "Setup the webruntime github repo.",
           False),
"webrins":("install('webruntime')",
           "Using pip, install webruntime from the sources directory",
           False),
"flexzip":("setup_zip('flexx')",
           "Unzip the flexx zip and place it in the correct directory",
           False),
"flexgit":("setup_git('flexx')",
           "Setup the flexx github repo.",
           False),
"flexins":("install('flexx')",
           "Using pip, install flexx from the sources directory",
           False),
"leozip" :("setup_zip('leo-editor')",
           "Unzip the leo-editor zip and place it in the correct directory",
           False),
"leogit": ("setup_git('leo-editor')",
           "Setup the leo-editor github repo.",
           False),
"leoins": ("install('leo-editor')",
           "Using pip, install leo-editor from the sources directory",
           False),
"leocpy": ("leo_copy_test()",
           "Copy the leo test directory, which is used by leowapp, but"\
           " is not part of the leo github distribution in the master"\
           " branch",
           False),
}

if exists(DATA_FILE):
    with open(DATA_FILE, "rb") as f:
        data = load(f)
#@-<< git_install_data >>
#@@language python
#@@tabwidth -4
#@+others
#@+node:DSR.20181126185212.2: ** control routines
#@+node:ekr.20181211050632.4: *3* do_step
def do_step(item):
    """
    Do this step in the process, regardless of whether it has been done
    or not. If it completes without failure, mark it done.
    """
    val = data[item]
    print('')
    print("{}: {}".format(item,val[1]))
    print(val[0])
    exec(val[0])
    print('')
    data[item] = (val[0],val[1],True)
#@+node:ekr.20181211050632.2: *3* dump_opts
def dump_opts():
    for item in order:
        print("{}: {}".format(item.ljust(7," "),data[item][1]))
    print("")
#@+node:ekr.20181211050632.1: *3* get_args
def get_args():
    global ar1,ar2,ar3
    try:
        ar1 = argv[0]
        #print("ar1 = " + ar1)
        ar2 = argv[1]
        #print("ar2 = " + ar2)
        ar3 = argv[2]
        #print("ar3 = " + ar3)
    except Exception:
        pass        
#@+node:ekr.20181211050632.5: *3* run
def run():
    # ar2 is the step name.
    global ar2
    get_args()
    if not ar2:
        # If there is no step name, just show usage and the steps
        usage()
        dump_opts()
    elif ar2 in data:
        # If the step name is in the list, just do this step and
        # mark it done
        do_step(ar2)
        save_data()
    if ar2 == "next":
        # do the next step in the process that hasn't been done already,
        # then mark it done
        for item in order:
            if data[item][2] == False:
                do_step(item)
                save_data()
                break
    if ar2 == "steps":
        # list all the steps
        print("")
        dump_opts()
    if ar2 == "show":
        # show the next step in the process that hasn't been done already
        for item in order:
            if data[item][2] == False:
                print("\n{}: {}\n".format(item,data[item][1]))
                break
    if ar2 == "restart":
        # delete data.dat from the current directory
        if exists(DATA_FILE):
            unlink(DATA_FILE)
    if ar2 == "commands":
        # show some interesting command lines used by this script
        print(cmds)
#@+node:ekr.20181211050632.3: *3* save_data
def save_data():
    with open(DATA_FILE, "wb") as f:
        dump(data,f,protocol=0)

#@+node:ekr.20181211050629.1: *3* usage
def usage():
    print(u)
#@+node:DSR.20181127045405.1: ** run routines
#@+node:DSR.20181127174108.1: *3* setup_dirs
# def setup_dirs():
    # for item in dir_list:
        # create_dir(item)
#@+node:DSR.20181203110307.1: *3* leo_copy_test
def leo_copy_test():
    """
    TODO: Copy the entire directory:
        sources/leo-editor-skeleton/test to
    site-packages/leo/test
    """
    pass
#@+node:DSR.20181127050322.1: *3* create_dir
def create_dir(item):
    name = join(CWD,item)
    if not exists(name):
        print("creating {}".format(name))
        mkdir(name)
#@+node:DSR.20181128081455.1: *3* run_env_cmd
def run_env_cmd(cmd):
    msg = "\n\nERROR! Pip install must be run under the "\
          "virtual environment:\n'{}'!\n\n".format(VIRTUAL_ENV)
    try:
        if not environ['VIRTUAL_ENV'] == VIRTUAL_ENV:
            raise RuntimeError
    except Exception:
        print(msg)
        exit(0)
    print(cmd)
    system(cmd)
#@+node:DSR.20181127182839.1: *3* clone_repo
def clone_repo(name,branch,git_name):
    git_dir = join(CWD,SOURCES,"{}-{}/.git".format(name,branch))
    if not exists(git_dir):
        mkdir(git_dir)
    cmd =  "cd {} && git clone --bare --single-branch -b {} --depth=1 --shallow-submodules {} .".format(
        git_dir,branch,git_name)
    print(cmd)
    system(cmd)
    return
#@+node:DSR.20181127071328.1: *3* setup_git
def setup_git(repo_name):
    """
    Clone a bare .git directory for the github repo
    """
    name,branch,zip_name,git_name = get_names(repo_name)
    if not name:
        return
    clone_repo(name,branch,git_name)
    pull_repo(name,branch,git_name)
    return
#@+node:DSR.20181127052138.1: *3* unzip
def unzip(name):
    dest = join(CWD,SOURCES)
    cmd = "unzip -o {} -d {}".format(name,dest)
    print(cmd)
    system(cmd)
    return
    # src  = join(CWD,"zips","{}.zip".format(name))
    # dest = join(CWD,SOURCES)
    #print(src)
#@+node:DSR.20181127193907.1: *3* get_names
def get_names(repo_name):
    for item in repo_list:
        (name,branch,zip_name,git_name) = item
        if name == repo_name:
            stub = "name:{}\nbranch:{}\nzip: {}\ngit: {}"
            print(stub.format(name,branch,zip_name,git_name))
            return name,branch,zip_name,git_name
    return None,None,None,None
#@+node:DSR.20181127195651.1: *3* setup_zip
def setup_zip(repo_name):
    """
    Unzip a master zip file into its source directory
    """
    name,branch,zip_name,git_name = get_names(repo_name)
    if not name:
        return
    unzip(zip_name)
#@+node:DSR.20181127224128.1: *3* pull_repo
def pull_repo(name,branch,git_name):
    print("pull_repo")
    repo_dir = join(CWD,SOURCES,"{}-{}".format(name,branch))
    cmd =  "cd {} && git init".format(repo_dir)
    print(cmd)
    system(cmd)
    cmd =  "cd {} && git pull --depth=1 --allow-unrelated-histories {}  {}".format(repo_dir,git_name,branch)
    print(cmd)
    system(cmd)
    return
#@+node:DSR.20181127235023.1: *3* install
def install(repo_name):

    name,branch,zip_name,git_name = get_names(repo_name)
    if not name:
        return
    src = join(CWD, SOURCES,"{}-{}".format(name,branch))
    cmd = "pip install --upgrade --no-deps --force-reinstall {}"
    cmd = cmd.format(src)
    run_env_cmd(cmd)
#@-others
run()
#@-leo
