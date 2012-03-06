#! /usr/bin/env python
#@+leo-ver=4-thin
#@+node:ekr.20051110105027.178:@thin tangle_done.py
#@@first

# Example tangle_done.py file.
# Leo catches all exceptions thrown here; there is no need for try:except blocks.

#@+others
#@+node:ekr.20051110105027.179:run
# Leo calls this routine if "Run tangle-done.py after Tangle" is checked in the Prefs panel.

def run (root_list):

    print("tangle_done roots:")
    for root in root_list:
        print(root)
    
    if 0: # Run code contributed by Paul Paterson.
        convertRSTfilesToHTML(root_list)
#@nonl
#@-node:ekr.20051110105027.179:run
#@+node:ekr.20051110105027.180:convertRSTfilesToHTML
# Adapted from code by Paul Paterson.

def convertRSTfilesToHTML(root_list):

    """This routine creates .html files from all .rst files in root_list, the list of files that have just been tangled."""
    
    for root in root_list: 
        base,fullname = g.os_path_split(root)
        name,ext = g.os_path_splitext(fullname)
        if ext == ".rst":
            file = g.os_path_join(base,name+".html")
            #@            << Convert root to corresponding .html file >>
            #@+node:ekr.20051110105027.181:<< Convert root to corresponding .html file >>
            # Leo will report the execption if docutils is not installed.
            from docutils.core import Publisher 
            from docutils.io import FileInput,StringOutput,StringInput 
            
            # Read .rst file into s.
            f = open(root,"r")
            s = f.read()
            f.close()
            
            # Restucture s into output.
            pub = Publisher() 
            pub.source = StringInput(pub.settings,source=s) 
            pub.destination = StringOutput(pub.settings,encoding="utf-8") 
            pub.set_reader('standalone',None,'restructuredtext') 
            pub.set_writer('html') 
            output = pub.publish()
            
            # EKR: 3/7/03: convert output using the present encoding.
            dict = g.scanDirectives(self.c,p=root)
            encoding = dict.get("encoding",None)
            if encoding == None:
                encoding = g.app.config.default_derived_file_encoding
            output = g.toEncodedString(output,encoding,reportErrors=True) 
            
            # Write the corresponding html file.
            f = open(file,"w")
            f.write(output)
            f.close()
            #@nonl
            #@-node:ekr.20051110105027.181:<< Convert root to corresponding .html file >>
            #@nl
#@-node:ekr.20051110105027.180:convertRSTfilesToHTML
#@-others
#@nonl
#@-node:ekr.20051110105027.178:@thin tangle_done.py
#@-leo
