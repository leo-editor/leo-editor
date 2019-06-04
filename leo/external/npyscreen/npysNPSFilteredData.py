#@+leo-ver=5-thin
#@+node:ekr.20170428084207.353: * @file ../external/npyscreen/npysNPSFilteredData.py
#@+others
#@+node:ekr.20170428084207.354: ** class NPSFilteredDataBase
class NPSFilteredDataBase:
    #@+others
    #@+node:ekr.20170428084207.355: *3* __init__
    def __init__(self, values=None):
        self._values  = None
        self._filter  = None
        self._filtered_values = None
        self.set_values(values)

    #@+node:ekr.20170428084207.356: *3* set_values
    def set_values(self, value):
        self._values = value

    #@+node:ekr.20170428084207.357: *3* get_all_values
    def get_all_values(self):
        return self._values

    #@+node:ekr.20170428084207.358: *3* set_filter
    def set_filter(self, this_filter):
        self._filter = this_filter
        self._apply_filter()

    #@+node:ekr.20170428084207.359: *3* filter_data
    def filter_data(self):
        # should set self._filtered_values to the filtered values
        raise Exception("You need to define the way the filter operates")

    #@+node:ekr.20170428084207.360: *3* get
    def get(self):
        self._apply_filter()
        return self._filtered_values

    #@+node:ekr.20170428084207.361: *3* _apply_filter
    def _apply_filter(self):
        # Could do some caching here - but the default definition does not.
        self._filtered_values = self.filter_data()

    #@-others
#@+node:ekr.20170428084207.362: ** class NPSFilteredDataList
class NPSFilteredDataList(NPSFilteredDataBase):
    #@+others
    #@+node:ekr.20170428084207.363: *3* filter_data
    def filter_data(self):
        if self._filter and self.get_all_values():
            return [x for x in self.get_all_values() if self._filter in x]
        else:
            return self.get_all_values()


    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
