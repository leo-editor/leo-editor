import whoosh
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
import os

g = None

def set_leo(gg):
    global g
    g = gg

def init ():

    print ("bigdash init")
    import leo.core.leoGlobals as g
    
    set_leo(g)
    ok = g.app.gui.guiName() == "qt"
    g._fts = None
    
    return ok


class LeoFts:    
    def __init__(self, idx_dir):
        self.idx_dir = idx_dir
        if not os.path.exists(idx_dir):
            os.mkdir(idx_dir)
            self.create()
        else:
            self.ix = open_dir(idx_dir)
    
    def create(self):
        
        schema = Schema(h=TEXT(stored=True), gnx=ID(stored=True), b=TEXT, parent=ID(stored=True))
        
        self.ix = ix = create_in(self.idx_dir, schema)
        
        
    def index_nodes(self, c):
        writer = self.ix.writer()
        
        for p in c.all_unique_positions():
            #print "pushing",p
            if p.hasParent():
                par = p.parent().get_UNL()
            else:
                par = c.mFileName
            
            writer.add_document(h=p.h, b=p.b, gnx=unicode(p.gnx), parent=par)
            
        writer.commit()

    def search(self, searchstring):        
        
        res = []
        with self.ix.searcher() as searcher:
            query = MultifieldParser(["h", "b"], schema=self.ix.schema).parse(searchstring)
            results = searcher.search(query)
            print (results)
            for r in results:
                res.append(r.fields())
        return res
            
    def close(self):
        self.ix.close()
def main():
    fts = LeoFts("c:/t/ltest")
    fts.create()
    
    
if __name__ == '__main__':
    main()