from typing import Dict, Optional, TypeVar
from flask import jsonify, abort
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from App.models import User, Tasks
from App.utils import (
    DatabaseTableMixin, verify_request_headers,
    request_timer
)
from App.schema import (
    UserSchema, UserPrototype, TableIDSchema, LoginSchema
)
from App.databasemanager import DatabaseContextManager
from sqlalchemy import select, and_, update
from App import mpesa

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
    res = DatabaseTableMixin(User)[userid]
    return res.to_json() if res else []


@views.route('/get/task/user/<int:userid>')
def get_tasks_users(userid):
    with DatabaseContextManager() as context:
        res = context.session.query(Tasks).filter_by(
            creator_id=userid
        ).all()

    iterable = []
    for elems in res:
        iterable.append(elems.to_json())
    return jsonify(
        {
            'tasks': iterable
        }
    )


# client and administrator
@views.route('/pay/task/<int:taskid>', methods=["POST"])
@request_timer.time()
@verify_request_headers
def pay_task(current_user, taskid):
    # get user and task
    with DatabaseContextManager() as context:
        task = context.session.query(
            Tasks
        ).filter(
            and_(
                Tasks.creator_id == current_user.id,
                Tasks.id == taskid
            )
        ).first()

        if task:
            if task.payment_status == "unpaid":
                req = mpesa.prompt_payment_for_service(
                    {
                        'amount':task.Amount,
                        'phone':current_user.phone,
                        'name': current_user.name
                    }
                )
                if req.status_code != 200:
                    return {
                        "Message": "An error Occurred"
                    }
                statement = update(
                    Tasks
                ).values(
                    **{
                        "payment_status": "paid"
                    }
                ).where(
                    Tasks.id==taskid
                )
                # context.session.execute(statement)
                return {
                    "status": "Task paid success"
                }
            else:
                return {
                    'message': "Task is already paid"
                }
        else:
            return {
                'message': "task already paid"
            }
