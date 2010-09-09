#@+leo-ver=5-thin
#@+node:tbrown.20091214233510.5347: * @thin geotag.py
#@+<< docstring >>
#@+node:tbrown.20091214233510.5348: ** << docstring >>
'''

geotag.py - Tag nodes with lat/long. info
=========================================


'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:tbrown.20091214233510.5349: ** << imports >>
import leo.core.leoGlobals as g

from leo.plugins.pygeotag import pygeotag
#@-<< imports >>
__version__ = "0.1"
#@+<< version history >>
#@+node:tbrown.20091214233510.5350: ** << version history >>
#@@killcolor

#@+at Use and distribute under the same terms as leo itself.
# 
# 0.1 TNB
#   - initial version
#@-<< version history >>

#@+others
#@+node:tbrown.20091214233510.5351: ** init
def init():

    g.app.pluginsController.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)

    g.pygeotag = pygeotag.PyGeoTag(synchronous=True)
    g.pygeotag.start_server()

    return True
#@+node:tbrown.20091214233510.5352: ** onCreate
def onCreate (tag,key):

    c = key.get('c')

    geotag_Controller(c)
#@+node:tbrown.20091214233510.5353: ** class geotag_Controller
class geotag_Controller:

    '''A per-commander class that manages geotagging.'''

    #@+others
    #@+node:tbrown.20091214233510.5354: *3* __init__
    def __init__ (self, c):

        self.c = c
        c.geotag = self
    #@+node:tbrown.20091214233510.5355: *3* __del__
    def __del__(self):
        for i in self.handlers:
            g.app.pluginsController.unregisterHandler(i[0], i[1])
    #@+node:tbrown.20091215204347.11403: *3* getAttr
    @staticmethod
    def getAttr(p):
        for nd in p.children():
            if nd.h.startswith('@LatLng '):
                break
        else:
            nd = p.insertAsLastChild()
        return nd
    #@+node:tbrown.20091214233510.5356: *3* callback
    def callback(self, data):

        c = self.c
        p = c.p

        nd = self.getAttr(p)



        nd.h = '@LatLng %(lat)f %(lng)f %(zoom)d %(maptype)s  %(description)s ' % data
        c.setChanged(True)
        if hasattr(c, 'attribEditor'):
            c.attribEditor.updateEditorInt()
        c.redraw()
    #@-others
#@+node:tbrown.20091214233510.5357: ** cmd_open_server_page
def cmd_OpenServerPage(c):
    g.pygeotag.open_server_page()
    # g.pygeotag.callback = c.geotag.callback

#@+node:tbrown.20091214233510.5358: ** cmd_tag_node
def cmd_TagNode(c):
    data = g.pygeotag.get_position({'description':c.p.h})
    c.geotag.callback(data)
#@+node:tbrown.20091215204347.11402: ** cmd_show_node
def cmd_ShowNode(c):
    nd = geotag_Controller.getAttr(c.p)
    try:
        txt = nd.h.split(None, 5)
        what = 'dummy', 'lat', 'lng', 'zoom', 'maptype', 'description'
        data = dict(zip(what, txt))
        data['lat'] = float(data['lat'])
        data['lng'] = float(data['lng'])
        if 'zoom' in data:
            data['zoom'] = int(data['zoom'])
        if 'description' not in data or not data['description'].strip():
            data['description'] = c.p.h
    except (ValueError,TypeError):
        data = {'description':c.p.h}
    g.pygeotag.show_position(data)
#@-others
#@-leo
