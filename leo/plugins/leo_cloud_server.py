#@+leo-ver=5-thin
#@+node:ekr.20170925083853.1: * @file ../plugins/leo_cloud_server.py
#@+others
#@+node:ekr.20201012111338.43: ** Declarations (leo_cloud_server.py)
"""
leo_cloud.py - synchronize Leo subtrees with remote central server

Terry N. Brown, terrynbrown@gmail.com, Fri Sep 22 10:34:10 2017

(this is the server half, see also leo_cloud.py for the Leo plugin)

This file is a *stub* for a Leo aware LeoCloudIOLeoServer which allows more
granular and real-time synchronization than simple git / Google Drive / DropBox
style LeoCloudIO* classes.

I.e. as of 20170924 this is just a place holder awaiting development.

# Notes

Sub-trees include head and body content *and* v.u

## Phase 1

On load, on save, and on demand, synchronize @leo_cloud subtrees with
remote server by complete download / upload

(leo_cloud.py accomplishes this without need for this module)

## Phase 2

Maybe more granular and regular synchronization.

 - experiments show recursive hash of 7000 node subtree, covering
   v.h, v.b, and v.u, can be done in 0.02 seconds on a 4GHz CPU.

## General notes

 - todo.py used to put datetime.datetime objects in v.u, the tags.py
   plugin puts set() objects in v.u.  Neither are JSON serializable.
   Plan is to serialize to text (ISO date and JSON list), and not
   fix on the way back in - tags.py can coerce the things it expects
   to be sets to be sets.

 - for Phase 1 functionality at least it might be possible to use
   non-server back ends like Google Drive / Drop Box / git / WebDAV.
   Probably worth a layer to handle this for people with out access to a
   server.

 - goal would be for an older Raspberry Pi to be sufficient server
   wise, so recursive hash speed there might be an issue (Phase 2)
"""
#@-others
#@@language python
#@@tabwidth -4
#@-leo
