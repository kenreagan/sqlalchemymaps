from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify
from werkzeug.security import generate_password_hash
from App.models import Worker
from App.utils import DatabaseTableMixin
from App.schema import UserSchema


worker = Blueprint('Worker Manager', __name__)


@worker.route('/')
class WorkerManager(MethodView):
    def __init__(self):
        self.worker = DatabaseTableMixin(Worker)

    def get(self):
        return jsonify({
            "worker": [
                items.to_json() for items in iter(self.UserManager)
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