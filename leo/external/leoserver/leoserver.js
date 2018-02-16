//@+leo-ver=5-thin
//@+node:ekr.20180216133454.1: * @file c:/leo.repo/leo-editor/leo/external/leoserver/leoserver.js
jQ = jQuery
//@+others
//@+node:ekr.20180216151656.1: ** key press
// Somehow this prevents the Tree button from working!

if (false) {
    var console = document.getElementById("console");
    
    console.addEventListener("keyup", function(event) {
      // event.preventDefault();
      if (event.keyCode === 13) {
        document.getElementById("go").click();
      }
    });
}
//@+node:ekr.20180216133513.1: ** go
function go() {
    let console = jQ('#console').val()
    jQ('#console').val('')
    jQ('#results').append('>>> '+console+'\n')
    let data = {cmd: console}
    jQ.ajax('/exec', {
        method: 'POST',
        dataType: 'json',
        data: JSON.stringify(data),
        success: show_result,
        error: () => show_result({answer:"FAILED\n"})
    })
}
//@+node:ekr.20180216133513.2: ** show_result
function show_result(response) {
    jQ('#results').append(response.answer)
}
//@+node:ekr.20180216133513.3: ** show_tree
function show_tree(response) {
    // FIXME should recurse nodes
    console.log(response)
    for (let node of response.nodes) {
        jQ('#results').append(node.h+'\n')
    }
}

jQ('#go').click(go)
jQ('#update').click(update)
jQ('#clear').click(() => jQ('#results').text(''))
//@+node:ekr.20180216133513.4: ** update
function update() {
    jQ.ajax('/get_tree', {
        method: 'GET',
        dataType: 'json',
        success: show_tree,
        error: () => show_result({answer:"FAILED\n"})
    })
}

//@-others
//@@language javascript
//@@tabwidth -4
//@-leo
