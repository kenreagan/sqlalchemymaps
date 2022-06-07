from typing import Dict, Optional, TypeVar

from flask import jsonify
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.security import generate_password_hash

from App.models import User, Tasks, Role
from App.utils import DatabaseTableMixin
from App.schema import UserSchema, UserPrototype, TableIDSchema, TaskManagerSchema


views = Blueprint('views', __name__)

dict_object = TypeVar('dict_object', str, int)


@views.route('/users')
class UserManager(MethodView):
    def __init__(self) -> None:
        self.UserManager = DatabaseTableMixin(User)

    @views.response(schema=UserPrototype, status_code=200)
    def get(self):
        return {
            "users": [
                items.to_json() for items in iter(self.UserManager)
            ]
        }

    @views.response(schema=UserSchema, status_code=201)
    @views.arguments(schema=UserSchema)
    def post(self, payload: Dict[str, Optional[dict_object]]) -> Dict[str, Optional[dict_object]]:
        payload['password'] = generate_password_hash(payload['password'])
        self.UserManager.__create_item__(payload)
        return payload

    @views.arguments(schema=UserSchema)
    def put(self, payload: Dict[str, Optional[dict_object]]) -> Dict[str, Optional[dict_object]]:
        self.UserManager[payload['id']] = payload
        return payload

    @views.arguments(schema=UserSchema)
    def patch(self, payload):
        self.UserManager[payload['id']] = payload
        return payload

    @views.arguments(schema=TableIDSchema)
    @views.response(status_code=200)
    def delete(self, userid):
        self.UserManager.__delitem__(userid['id'])
        return {
            "Message": "success"
        }


@views.route('/user/<int:userid>')
def get_by_id(userid):
    res = DatabaseTableMixin(User)[userid].__getitem__('User').to_json()
    return res


@views.route('/tasks')
class TaskManager(MethodView):
    def __init__(self):
        self.ManagerTable = DatabaseTableMixin(Tasks)

    @views.response(status_code=200)
    def get(self):
        return jsonify({
            "tasks": [
                items.to_json() for items in iter(self.ManagerTable)
            ]
        })

    @views.response(schema=TaskManagerSchema, status_code=201)
    @views.arguments(schema=TaskManagerSchema, error_status_code=400)
    def post(self, payload):
        self.ManagerTable.__create_item__(payload)
        return payload

    def patch(self, payload):
        self.ManagerTable[payload['id']] = payload
        return payload

    def put(self, payload):
        self.ManagerTable[payload['id']] = payload
        return payload

    def delete(self, task_id):
        self.UserManager.__delitem__(task_id)
        return {

        }

@views.route('/tasks/<int:taskid>')
def get_by_id(taskid):
    res = DatabaseTableMixin(User)[taskid].__getitem__('Tasks').to_json()
    return res

@views.route('/roles')
class RoleManager(MethodView):
    def __init__(self):
        self.roleManager = DatabaseTableMixin(Role)

    def get(self):
        return jsonify({
            "roles": [
                item.to_json() for item in iter(self.roleManager)
            ]
        })


@views.route('/claim/task/<int:id>', methods=['POST'])
def claim_task(id):
    return


@views.route('/')
def get_tasks(id):
    return
