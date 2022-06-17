import json
from typing import Dict, Optional, TypeVar
from flask import jsonify, abort
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from App.models import User, Tasks, Role, Worker
from App.utils import (
    DatabaseTableMixin, verify_request_headers, client_and_admin_only, admins_only,
    request_timer
)
from App.schema import UserSchema, UserPrototype, TableIDSchema, LoginSchema
from App.databasemanager import DatabaseContextManager
from prometheus_client import Summary
from App.amqpproducer import SignalProducer
from sqlalchemy import select, and_

views = Blueprint('Main User Manager', __name__)


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

@views.route('/login', methods=['POST'])
@views.arguments(schema=LoginSchema)
def login(payload: Dict):
    statement = select(User).where(
        User.email == payload['email']
    )
    with DatabaseContextManager() as context:
        user = context.session.execute(statement).first()


    if check_password_hash(user['User'].password, payload['password']):
        return user['User'].generate_token(user['User'].id)
    else:
        return abort(403)

@views.route('/user/<int:userid>')
@request_timer.time()
def get_by_id(userid):
    res = DatabaseTableMixin(User)[userid]['User'].to_json()
    return res


@views.route('/claim/task/<int:taskid>', methods=['POST'])
@verify_request_headers
@client_and_admin_only
def claim_task(current_user, taskid):
    task = DatabaseTableMixin(Tasks)
    worker = DatabaseTableMixin(Worker)
    if task[taskid]['Tasks'].creator_id != current_user.id:
        worker.__create_item__(
            **{
                "userid": current_user.id,
                "taskid": taskid
            }
        )
        payload = {
            "progress_status": "claimed"
        }
        task.__setitem__(taskid, **payload)
    return task[taskid]['Tasks'].to_json()


@views.route('/get/task/<int:userid>')
@verify_request_headers
@client_and_admin_only
def get_tasks_users(current_user, userid):
    res = DatabaseTableMixin(Tasks)
    return res.to_json()


# client and administrator
@client_and_admin_only
@verify_request_headers
@request_timer.time()
@views.route('/pay/task/<int:taskid>', methods=["POST"])
def pay_task(taskid):
    """"
    Add the Request to payment que for processing by the payment service
    """
    # get user and task

    task = DatabaseTableMixin(Tasks)[taskid].__getitem__('Tasks').to_json()
    if task:
        # get the user of the task details
        with DatabaseContextManager() as context:
            statements = select(
                User.name,
                User.email,
                User.phone
            )
            x = statements.select_from(
                Tasks.__table__.join(
                    User
                )
            ).where(
                and_(
                    Tasks.creator_id == 2, # replace it with current user.id
                    Tasks.id == taskid
                )
            )

            res = context.session.execute(x).first()
        feedback = res._asdict()

        for key, val in task.items():
            feedback[key] = val

        producer = SignalProducer("Individual Task Payment")
        #  add details to RabbitMq queue
        producer.produce_event(
            'request payment',
            json.dumps(feedback)
        )
        return {
            "status": "Pending payment"
        }
    return {}


# superuser and Administrator
@admins_only
@verify_request_headers
@request_timer.time()
@views.route('/disburse/funds/<int:clientid>')
def disburse_funds(clientid):
    # pay weekly to client
    user = DatabaseTableMixin(User)[clientid].__getitem__('User').to_json()
    if user is not None:
        if user['Amount'] > 500:
            producer = SignalProducer("Disburse Funds")
            producer.produce_event(
                'disburse multiple',
                str(user)
            )
            return {
                "message": "Funds Disbursed"
            }
        return {
            "Message": "user has low account"
        }
    else:
        return user
