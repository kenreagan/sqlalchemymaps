from flask_smorest import Blueprint
from flask import jsonify, abort
from App.utils import (
    DatabaseTableMixin, verify_request_headers, request_timer
)
from App.models import Tasks
from App.schema import TaskManagerSchema

taskers = Blueprint('Tasks Manager', __name__)


@taskers.route('/', methods=['GET'])
@taskers.response(status_code=200)
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
@verify_request_headers
def create_tasks(current_user, payload):
    payload['creator_id'] = current_user.id
    ManagerTable = DatabaseTableMixin(Tasks)
    ManagerTable.__create_item__(payload)
    return payload


@taskers.route('patch/', methods=['PATCH'])
@verify_request_headers
def patch_task(current_user, payload):
    ManagerTable = DatabaseTableMixin(Tasks)
    ManagerTable[payload['id']] = payload
    return payload


@taskers.route('update/', methods=['PUT'])
@verify_request_headers
def update_task(current_user, payload):
    ManagerTable = DatabaseTableMixin(Tasks)
    ManagerTable[payload['id']] = payload
    return payload


@taskers.route('delete/<int:taskid>', methods=['DELETE'])
@verify_request_headers
def delete_task(current_user, taskid):
    ManagerTable = DatabaseTableMixin(Tasks)
    if current_user.id == ManagerTable[taskid].creator_id:
        ManagerTable.__delitem__(taskid)
        return {
            "message": "success"
        }
    abort(403)


@taskers.route('/<int:taskid>')
def get_by_id(taskid):
    res = DatabaseTableMixin(Tasks)[taskid]
    return res.to_json() if res else []
