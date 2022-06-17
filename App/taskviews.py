from flask_smorest import  Blueprint
from flask import jsonify
from App.utils import (
    DatabaseTableMixin, verify_request_headers, client_and_admin_only,
    allow_all__, request_timer
)
from App.models import Tasks
from App.schema import TaskManagerSchema

taskers = Blueprint('Tasks Manager', __name__)


@taskers.route('/', methods=['GET'])
@taskers.response(status_code=200)
@allow_all__
def get_tasks():
    ManagerTable = DatabaseTableMixin(Tasks)
    return jsonify({
        "tasks": [
            items.to_json() for items in iter(ManagerTable)
        ]
    })


@taskers.route('create/', methods=['POST'])
@taskers.response(schema=TaskManagerSchema, status_code=201)
@taskers.arguments(schema=TaskManagerSchema, error_status_code=400)
@request_timer.time()
@verify_request_headers
@client_and_admin_only
def create_tasks(current_user, payload):
    payload['creator_id'] = current_user.id
    ManagerTable = DatabaseTableMixin(Tasks)
    ManagerTable.__create_item__(payload)
    return payload


@taskers.route('patch/', methods=['PATCH'])
@verify_request_headers
@client_and_admin_only
def patch_task(current_user, payload):
    ManagerTable = DatabaseTableMixin(Tasks)
    ManagerTable[payload['id']] = payload
    return payload


@taskers.route('update/', methods=['PUT'])
@verify_request_headers
@client_and_admin_only
def update_task(current_user, payload):
    ManagerTable = DatabaseTableMixin(Tasks)
    ManagerTable[payload['id']] = payload
    return payload


@taskers.route('delete/', methods=['DELETE'])
@verify_request_headers
@client_and_admin_only
def delete_task(current_user, task_id):
    ManagerTable = DatabaseTableMixin(Tasks)
    ManagerTable.__delitem__(task_id)
    return {
        "message": "success"
    }


@taskers.route('/<int:taskid>')
@allow_all__
def get_by_id(taskid):
    res = DatabaseTableMixin(Tasks)[taskid].__getitem__('Tasks').to_json()
    return res