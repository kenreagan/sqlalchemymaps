from flask.views import MethodView
from flask_smorest import Blueprint
from App.utils import DatabaseTableMixin, BaseMapper
from App.models import Role
from flask import jsonify

roles = Blueprint('RoleManager', __name__)


@roles.route('/')
class RoleManager(MethodView):
    def __init__(self):
        self.role_manager = DatabaseTableMixin(Role)
        self.mapper = BaseMapper()
        if len(self.role_manager) < 1:
            self.mapper.create_role_permission()

    def get(self):
        return jsonify({
            "roles": [
                item.to_json() for item in iter(self.role_manager)
            ]
        })
