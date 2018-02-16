jQ = jQuery
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
function show_result(response) {
    jQ('#results').append(response.answer)
}
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
function update() {
    jQ.ajax('/get_tree', {
        method: 'GET',
        dataType: 'json',
        success: show_tree,
        error: () => show_result({answer:"FAILED\n"})
    })
}

