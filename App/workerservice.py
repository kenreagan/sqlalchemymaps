import json

from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify, abort
from werkzeug.security import generate_password_hash
from App.models import Worker, Tasks
from App.utils import DatabaseTableMixin, verify_worker_request_headers
from App.schema import UserSchema, LoginSchema, TaskViewSchema
from sqlalchemy import select, update
from App.databasemanager import DatabaseContextManager
from typing import Dict
from werkzeug.security import check_password_hash
from App.amqpproducer import SignalProducer

worker = Blueprint('Worker Manager', __name__)

# producer = SignalProducer("Worker Manager")

@worker.route('/')
class WorkerManager(MethodView):
    def __init__(self):
        self.worker = DatabaseTableMixin(Worker)

    def get(self):
        return jsonify({
            "worker": [
                items.to_json() for items in iter(self.worker)
            ]
        })

    @worker.response(schema=UserSchema, status_code=201)
    @worker.arguments(schema=UserSchema)
    def post(self, payload):
        payload['password'] = generate_password_hash(payload['password'])
        self.worker.__create_item__(payload)
        return payload

    def patch(self):
        pass


@worker.route('/login', methods=['POST'])
@worker.arguments(schema=LoginSchema)
def login(payload: Dict):
    statement = select(Worker).where(
        Worker.email == payload['email']
    )
    with DatabaseContextManager() as context:
        user = context.session.execute(statement).first()

    if check_password_hash(user['Worker'].password, payload['password']):
        return user['Worker'].generate_token(user['Worker'].id)
    else:
        return abort(403)


@worker.route('/claim/task/<int:taskid>', methods=['POST'])
@verify_worker_request_headers
@worker.response(schema=TaskViewSchema, status_code=201)
def claim_task(current_user, taskid):
    with DatabaseContextManager() as context:
        task = context.session.query(Tasks).filter_by(
            id=taskid
        ).first()
        if task.progress_status == "unclaimed":
            statement = update(
                Tasks
            ).values(
                **{
                    "task": current_user.id,
                    "progress_status": "claimed"
                }
            ).where(
               Tasks.id == taskid
            )

            user_statement = update(
                Worker
            ).values(
                **{
                    "account": current_user.account + task.Amount
                }
            ).where(
                Worker.id == current_user.id
            )

            context.session.execute(statement)
            context.session.execute(user_statement)

            context.commit()

            return task.to_json()

        else:
            return task.to_json()


@worker.route('/get/task/<int:workerid>', methods=['GET'])
@worker.response(schema=TaskViewSchema, status_code=201)
def get_work(workerid):
    with DatabaseContextManager() as context:
        res = context.session.query(Tasks).filter_by(
            task=workerid
        ).all()

    iterable = []
    for elems in res:
        iterable.append(elems.to_json())
    return jsonify(
        {
            'tasks': iterable
        }
    )
