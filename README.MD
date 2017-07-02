# About this branch

The author of sqlite, Dr Richard Hipp, suggest that the sqlite database can and should be used
as a standard document file format. Instead of inventing new document file format for any 
application, developer can use sqlite and enjoy a lot of flexibility and freedom it guarantees:
data consistency, platform/language independency of data format, power loss/hard crash data 
protection… to name a few.

On 18th September 2008. Edward wrote:

> Cool.  I'm becoming more interested in a sqlite back end for Leo.  … I probably won't get 
  around to it for awhile, but it would be great if somebody else could do it sooner.

As a long time Leo user, I have decided to start this branch and try to make it happen *sooner*.

Currently it is possible using code from this branch to save and open Leo document from sqlite
database file. One can open old xml .leo document and then save it as .db document. If the 
extension of document is ‘.db’ Leo assumes sqlite database format. 

All document data are stored in two tables: vnodes and extra_infos. That is certainly not the
most suitable nor efficient way but it was simplest thing that could possible work. For the sake
of prototyping it suffices.

The next thing to address is keeping settings in document and syncing them with the settings
files in specific folders that Leo currently uses.

In far a way future one can imagine even stronger integration between Leo’s runtime data structures
and database. Data can be constantly stored in/retrieved from database while editing document.
Save operation in that case would be just commit on connection object. Perhaps it could make
possible permanent undo/redo history, displaying history of some node since its creation and maybe
even more cool features that are hard to imagine now.

Who knows what the future would bring. 
