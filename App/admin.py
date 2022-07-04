from flask.views import MethodView
from flask_smorest import Blueprint
from App.models import Advertisement
from App.schema import AdSchema
from App.utils import DatabaseTableMixin

admin = Blueprint('Admin Endpoint', __name__)


@admin.route('/home')
class AdvertisementManager(MethodView):
    def __init__(self):
        self.advertisement = DatabaseTableMixin(Advertisement)

    def get(self):
        return {
            "posts": [
                item.to_json() for item in iter(self.advertisement)
            ]
        }

    @admin.response(schema=AdSchema, status_code=201)
    @admin.arguments(schema=AdSchema)
    def post(self, payload):
        self.advertisement.__create_item__(
            payload
        )
        return payload
