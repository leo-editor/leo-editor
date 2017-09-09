.. rst3: filename: html\zodb.html

###################
Using ZODB with Leo
###################

.. _`ZODB`: http://www.zope.org/Wikis/ZODB/guide/zodb.html

This chapter discusses how to write Leo scripts that store and retrieve data using `ZODB`_.

.. contents:: Contents
    :depth: 2
    :local:

Configuring Leo to use zodb
+++++++++++++++++++++++++++

.. _`Installing ZODB`: http://www.zope.org/Wikis/ZODB/guide/node3.html#SECTION000310000000000000000

To enable zodb scripting within Leo, you must set use_zodb = True in the root node of leoNodes.py. You must also install ZODB itself.  See `Installing ZODB`_ for details.

When ZODB is installed and use_zodb is True, Leo's vnode class becomes a subclass of ZODB.Persistence.Persistent. This is all that is needed to save/retrieve vnodes or tnodes to/from the ZODB.

**Important notes**:

- Scripts **should not** store or retrieve positions using the ZODB! Doing so makes sense neither from Leo's point of view nor from ZODB's point of view.

- The examples below show how to store or retrieve Leo data by accessing the so-called root of a ZODB connection. However, these are only examples. Scripts are free to do with Leo's vnodes *anything* that can be done with ZODB.Persistence.Persistent objects.

Initing zodb
++++++++++++

Scripts should call g.init_zodb to open a ZODB.Storage file. g.init_zodb returns an instance of ZODB.DB.  For example::

    db = g.init_zodb (zodbStorageFileName)

You can call g.init_zodb as many times as you like. Only the first call for any path actually does anything: subsequent calls for a previously opened path simply return the same value as the first call.

Writing data to zodb
++++++++++++++++++++

The following script writes v, a tree of vnodes, to zodb::

    db = g.init_zodb (zodbStorageFileName)
    connection = db.open()
    try:
        root = connection.root()
        root[aKey] = v # See next section for how to define aKey.
    finally:
        get_transaction().commit()
        connection.close()

Notes:

- v must be a vnode.
  Scripts should *not* attempt to store Leo positions in the zodb.
  v can be the root of an entire outline or a subtree.
  For example, either of the following would be reasonable::

    root[aKey] = c.rootPosition().v
    root[aKey] = c.p.v

- To write a single vnode without writing any of its children you can use v.detach.
  For example::

    root[aKey] = v.detach()

- **Important**: It is simplest if only one zodb connection is open at any one time,
  so scripts would typically close the zodb connection immediately after processing the data.
  The correct way to do this is in a finally statement, as shown above.

- The script above does not define aKey.
  The following section discusses how to define reasonable zodb keys.

Defining zodb keys
++++++++++++++++++

The keys used to store and retrieve data in connection.root() can be any string that uniquely identifies the data. The following are only suggestions; you are free to use any string you like.

1. When saving a file, you would probably use a key that is similar to a real file path.
   For example::

        aKey = c.fileName()

2. When saving a single vnode or tree of vnodes, say v,
   a good choice would be to use v's gnx, namely::

        aKey = g.app.nodeIndices.toString(v.fileIndex)

   Note that v.detach() does not automatically copy v.fileIndex to the detached node,
   so when writing a detached node you would typically do the following::

       v2 = v.detach()
       v2.fileIndex = v.fileIndex
       aKey = g.app.nodeIndices.toString(v2.fileIndex)

Reading data from zodb
++++++++++++++++++++++

The following script reads a tree of vnodes from zodb and sets p as the root position of the tree::

    try:
        connection = db.open()
        root = connection.root()
        v = root.get(aKey)
        p = leoNodes.position(v)
    finally:
        get_transaction().commit()
        connection.close()

About connections
+++++++++++++++++

The scripts shown above close the zodb connection after processing the data. This is by far the simplest strategy. I recommend it for typical scripts.

**Important**: you must **leave the connection open** if your script modifies persistent data in any way. (Actually, this statement is not really true, but you must define zodb transaction managers if you intend to use multiple connections simultaneously. This complication is beyond the scope of this documentation.) For example, it would be possible to create a new Leo outline from the data just read, but the script must leave the connection open. I do not recommend this tactic, but for the adventurous here is some sample code::

    connection = self.db.open()
    root = connection.root()
    v = root.get(fileName)
    if v:
        c2 = c.new()
        c2.openDirectory = c.openDirectory # A hack.
        c2.mFileName = fileName # Another hack.
        c2.beginUpdate()
        try:
            c2.setRootVnode(v)
            c2Root = c2.rootPosition()
            c2.atFileCommands.readAll(c2Root)
            g.es_print('zodb read: %s' % (fileName))
        finally:
            c2.endUpdate()
        # Do *not* close the connection while the new Leo window is open!
    else:
        g.es_print('zodb read: not found: %s' % (fileName))


This will work **provided** that no other zodb connection is ever opened while this connection is opened. Unless special zodb precautions are taken (like defining zodb transaction managers) calling get_transaction().commit() will affect **all** open connections. You have been warned.

Convenience routines
++++++++++++++++++++



g.init_zodb (pathToZodbStorage,verbose=True)
********************************************

This function inits the zodb. pathToZodbStorage is the full path to the zodb storage file. You can call g.init_zodb as many times as you like. Only the first call for any path actually does anything: subsequent calls for a previously opened path simply return the same value as the first call.

v.detach()
**********

This vnode method returns v2, a copy of v that is completely detached from the outline. v2.fileIndex is unrelated to v.fileIndex initially, but it may be convenient to copy this field::

    v2 = v.detach()
    v2.fileIndex = v.fileIndex

