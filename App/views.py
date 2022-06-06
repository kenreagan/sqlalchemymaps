from typing import Dict, Optional, TypeVar

from flask_smorest import Blueprint
from flask.views import MethodView
from App.models import User, Tasks, Role
from App.utils import DatabaseTableMixin


views = Blueprint('views', __name__)

dict_object = TypeVar('dict_object', str, int)


@views.route('/users')
class UserManager(MethodView):
    def __init__(self) -> None:
        self.UserManager = DatabaseTableMixin(User)

    def get(self):
        return {
            "users": [
                items.__getitem__('User').to_json() for items in iter(self.UserManager)
            ]
        }

    def post(self, payload: Dict[str, Optional[dict_object]]) -> Dict[str, Optional[dict_object]]:
        self.UserManager.__create_item__(payload)
        return payload

    def put(self, payload: Dict[str, Optional[dict_object]]) -> Dict[str, Optional[dict_object]]:
        self.UserManager[payload['id']] = payload
        return payload

    def patch(self, payload):
        self.UserManager[payload['id']] = payload
        return payload

    def delete(self, userid):
        self.UserManager.__delitem__(userid)
        return {

        }


@views.route('/tasks')
class TaskManager(MethodView):
    def __init__(self):
        self.ManagerTable = DatabaseTableMixin(Tasks)

    def get(self):
        return {
            "tasks": [
                items.__getitem__('Tasks').to_json() for items in iter(self.ManagerTable)
            ]
        }

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


@views.route('/roles')
class RoleManager(MethodView):
    def __init__(self):
        self.roleManager = DatabaseTableMixin(Role)

    def get(self):
        return {
            "roles": [
                item.__getitem__('Tasks').to_json() for item in iter(self.roleManager)
            ]
        }
