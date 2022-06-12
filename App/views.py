from typing import Dict, Optional, TypeVar
from werkzeug.exceptions import abort
# from App import mpesa
from flask import jsonify
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from App.models import User, Tasks, Role
from App.utils import DatabaseTableMixin
from App.schema import UserSchema, UserPrototype, TableIDSchema, TaskManagerSchema
from functools import wraps
# from flask_jwt_extended import verify_jwt_in_request
from prometheus_client import Summary

views = Blueprint('views', __name__)

request_timer = Summary(
    'time_request_summary',
    'track endpoint request summary to track the slow endpoints'
)


def verify_request_headers(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # verify_jwt_in_request()
        return func(*args, **kwargs)

    return wrapper


@views.before_request
def before_request():
    pass


def admins_only(func):
    @wraps(func)
    def allow_admin(*args, **kwargs):
        pass

    return allow_admin


def client_and_admin_only(func):
    @wraps(func)
    def allow_admin_and_client(*args, **kwargs):
        pass

    return allow_admin_and_client


def allow_all__(func):
    @wraps(func)
    def allow_all(*args, **kwargs):
        pass

    return allow_all


dict_object = TypeVar('dict_object', str, int)


@views.route('/users')
class UserManager(MethodView):
    def __init__(self) -> None:
        self.UserManager = DatabaseTableMixin(User)

    @views.response(schema=UserPrototype, status_code=200)
    @request_timer.time()
    def get(self):
        return {
            "users": [
                items.to_json() for items in iter(self.UserManager)
            ]
        }

    @views.response(schema=UserSchema, status_code=201)
    @views.arguments(schema=UserSchema)
    @request_timer.time()
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
@request_timer.time()
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

    @verify_request_headers
    @views.response(schema=TaskManagerSchema, status_code=201)
    @views.arguments(schema=TaskManagerSchema, error_status_code=400)
    def post(self, payload):
        self.ManagerTable.__create_item__(payload)
        return payload

    @verify_request_headers
    def patch(self, payload):
        self.ManagerTable[payload['id']] = payload
        return payload

    @verify_request_headers
    def put(self, payload):
        self.ManagerTable[payload['id']] = payload
        return payload

    @verify_request_headers
    def delete(self, task_id):
        self.UserManager.__delitem__(task_id)
        return {
            "message": "success"
        }


@views.route('/tasks/<int:taskid>')
def get_by_id(taskid):
    res = DatabaseTableMixin(Tasks)[taskid].__getitem__('Tasks').to_json()
    return res


@verify_request_headers
@views.route('/claim/task/<int:id>', methods=['POST'])
def claim_task(id):
    return


@verify_request_headers
@views.route('/get/task/<int:userid>')
def get_tasks_users(userid):
    res = DatabaseTableMixin(Tasks)
    return res.to_json()


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


# client and administrator
@client_and_admin_only
@verify_request_headers
@views.route('/pay/task/<int:taskid>', methods=["POST"])
def pay_task(taskid):
    # get user and task
    user = current_user()
    task = DatabaseTableMixin(Tasks)
    pay = task[taskid]
    # start payment
    if pay.creator_id == user.id:
        mpesa.prompt_payment_for_service(
            {
                'name': user.name,
                'phone': user.phone,
                'amount': pay.amount
            }
        )
        return {
            "message": "success"
        }
    else:
        abort(403)


# superuser and Administrator
@admins_only
@verify_request_headers
@views.route('/disburse/funds/<int:clientid>')
def disburse_funds(clientid):
    # pay weekly to client
    pass
