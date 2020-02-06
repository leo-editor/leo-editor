#@+leo-ver=5-thin
#@+node:ekr.20181209120925.1: * @file flaskapp.py
#!flask/bin/python
unicode = str # Assume python 3
#@+<< flask imports >>
#@+node:ekr.20181209122016.1: ** << flask imports >>
import sys
assert sys.version_info >= (3, 0, 0), "Not Python 3"
from flask import Flask
from flask import abort
from flask import jsonify
from flask import make_response
from flask import request
#@-<< flask imports >>
#@+<< curl reference >>
#@+node:ekr.20181209131100.1: ** << curl reference >>
#
# List all tasks
#
# curl -i http://localhost:5000/todo/api/v1.0/tasks
#
# List task 2
#
# curl -i http://localhost:5000/todo/api/v1.0/tasks/2
#
# Delete task 2
#
# curl -i -H "Content-Type: application/json" -X PUT -d '{"done":true}' http://localhost:5000/todo/api/v1.0/tasks/2
#@-<< curl reference >>
# 
# pylint: disable=len-as-condition
# pylint: disable=unidiomatic-typecheck
app = Flask(__name__)
#@+<< define tasks >>
#@+node:ekr.20181209121948.1: ** << define tasks >>
tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]
#@-<< define tasks >>
#@+others
#@+node:ekr.20181212042856.1: ** init
def init():
    '''Dummy top-level init for Leo's unit tests and TravisCI.'''
    return False
#@+node:ekr.20181209123709.1: ** @app.errorhandler(404, 405)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': '404: Not found'}), 404)
    
@app.errorhandler(405)
def unauthorized(error):
    return make_response(jsonify({'error': '405: Unauthorized'}), 405)
    
#@+node:ekr.20181209123711.2: ** @app.route DELETE
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})
#@+node:ekr.20181209123710.1: ** @app.route GET: tasks, tasks/id
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})
#@+node:ekr.20181209123710.2: ** @app.route POST
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201
#@+node:ekr.20181209123711.1: ** @app.route PUT
@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

#@-others
if __name__ == '__main__':
    app.run(debug=True)
#@-leo
