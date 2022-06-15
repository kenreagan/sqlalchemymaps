from flask_smorest import  Blueprint
from flask.views import MethodView
from flask import jsonify
from App.utils import DatabaseTableMixin, verify_request_headers
from App.models import Tasks
from App.schema import TaskManagerSchema
from prometheus_client import Summary

taskers = Blueprint('Tasks Manager', __name__)

task_funcs_summary = Summary(
    "time_task_summary",
    "time the total time for tasks"
)


@taskers.route('/')
class TaskManager(MethodView):
    def __init__(self):
        self.ManagerTable = DatabaseTableMixin(Tasks)

    @taskers.response(status_code=200)
    @task_funcs_summary.time()
    def get(self):
        return jsonify({
            "tasks": [
                items.to_json() for items in iter(self.ManagerTable)
            ]
        })

    @verify_request_headers
    @taskers.response(schema=TaskManagerSchema, status_code=201)
    @taskers.arguments(schema=TaskManagerSchema, error_status_code=400)
    @task_funcs_summary.time()
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
        self.ManagerTable.__delitem__(task_id)
        return {
            "message": "success"
        }


@taskers.route('/<int:taskid>')
def get_by_id(taskid):
    res = DatabaseTableMixin(Tasks)[taskid].__getitem__('Tasks').to_json()
    return res