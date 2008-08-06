//@+leo-ver=4-thin
//@+node:ekr.20080806145258.1:@thin cgi-bin/leo.js
//@@language javascript

/**********************************************
* Contractible Headers script- © Dynamic Drive (www.dynamicdrive.com)
* This notice must stay intact for legal use. Last updated Mar 23rd, 2004.
* Visit http://www.dynamicdrive.com/ for full source code
***********************************************/

// alert("start");

var enablepersist="on" //Enable saving state of content structure using session cookies? (on/off)
var collapseprevious="no" //Collapse previously open content when opening present? (yes/no)

if (document.getElementById){
    document.write('<style type="text/css">')
    document.write('.switchcontent{display:none;}')
    document.write('<\/style>')
}

//@+others
//@+node:ekr.20080806145258.2:getElementbyClass
function getElementbyClass(classname){
    ccollect=new Array()
    var inc=0
    var alltags=document.all? document.all : document.getElementsByTagName("*")
    for (i=0; i<alltags.length; i++){
        if (alltags[i].className==classname)
            ccollect[inc++]=alltags[i]
    }
}

//@-node:ekr.20080806145258.2:getElementbyClass
//@+node:ekr.20080806145258.3:contractcontent
function contractcontent(omit){
    var inc=0
    while (ccollect[inc]){
        if (ccollect[inc].id!=omit)
        ccollect[inc].style.display="none"
        inc++
    }
}
//@-node:ekr.20080806145258.3:contractcontent
//@+node:ekr.20080806145258.4:expandcontent
function expandcontent(cid){
    if (typeof ccollect!="undefined"){
        if (collapseprevious=="yes")
            contractcontent(cid)
        document.getElementById(cid).style.display=(document.getElementById(cid).style.display!="block")? "block" : "none"
    }
}
//@-node:ekr.20080806145258.4:expandcontent
//@+node:ekr.20080806145258.5:revivecontent
function revivecontent(){
    contractcontent("omitnothing")
    selectedItem=getselectedItem()
    selectedComponents=selectedItem.split("|")
    for (i=0; i<selectedComponents.length-1; i++)
        document.getElementById(selectedComponents[i]).style.display="block"
}

//@-node:ekr.20080806145258.5:revivecontent
//@+node:ekr.20080806145258.6:get_cookie
function get_cookie(Name) { 
    var search = Name + "="
    var returnvalue = "";
    if (document.cookie.length > 0) {
        offset = document.cookie.indexOf(search)
        if (offset != -1) { 
            offset += search.length
            end = document.cookie.indexOf(";", offset);
            if (end == -1) end = document.cookie.length;
            returnvalue=unescape(document.cookie.substring(offset, end))
        }
    }
    return returnvalue;
}

//@-node:ekr.20080806145258.6:get_cookie
//@+node:ekr.20080806145258.7:getselectedItem
function getselectedItem(){
    if (get_cookie(window.location.pathname) != ""){
        selectedItem=get_cookie(window.location.pathname)
        return selectedItem
    }
    else
        return ""
}

//@-node:ekr.20080806145258.7:getselectedItem
//@+node:ekr.20080806145258.8:saveswitchstate
function saveswitchstate(){
    var inc=0, selectedItem=""
    while (ccollect[inc]){
        if (ccollect[inc].style.display=="block")
            selectedItem+=ccollect[inc].id+"|"
        inc++
    }
    document.cookie=window.location.pathname+"="+selectedItem
}

//@-node:ekr.20080806145258.8:saveswitchstate
//@+node:ekr.20080806145258.9:do_onload
function do_onload(){
    // alert("do_onload");
    uniqueidn=window.location.pathname+"firsttimeload"
    getElementbyClass("switchcontent")
    if (enablepersist=="on" && typeof ccollect!="undefined"){
        document.cookie=(get_cookie(uniqueidn)=="")? uniqueidn+"=1" : uniqueidn+"=0" 
        firsttimeload=(get_cookie(uniqueidn)==1)? 1 : 0 //check if this is 1st page load
        if (!firsttimeload)
        revivecontent()
    }
}

if (window.addEventListener)
    window.addEventListener("load", do_onload, false)
else if (window.attachEvent)
    window.attachEvent("onload", do_onload)
else if (document.getElementById)
    window.onload=do_onload

if (enablepersist=="on" && document.getElementById)
    window.onunload=saveswitchstate

//@-node:ekr.20080806145258.9:do_onload
//@+node:ekr.20080806145258.10:format
function format() {

    return;

    // var sections = document.getElementsByTagName("pre");  // EKR: was span.
    // //alert("format:" + sections.length + "sections")
    // for(i=0; i < sections.length; i++) {
        // formatText(sections[i]);
    // }
}
//@-node:ekr.20080806145258.10:format
//@+node:ekr.20080806145258.11:formatText
function formatText(item) {

    ;
    // alert(item);
}
//@-node:ekr.20080806145258.11:formatText
//@-others
//@nonl
//@-node:ekr.20080806145258.1:@thin cgi-bin/leo.js
//@-leo
