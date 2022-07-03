from flask import Flask
from flask_smorest import Api
from MpesaRest import Mpesa

mpesa = Mpesa(
    'x6GCRysuUJKUzyLZ2Ylujlb4fEbt882r',
    'QErq8SPCFBxwCDzK',
    174379,
    '254794784462',
    '0b2b4d8482fddaf34d7ea78b402c2b40ed0db4b101007b46a89d0b9cd12b3fb2',
    'http://127.0.0.1:5000/payment/status/callback'
)

api = Api()


def create_app(configuration_file='configuration.Config'):
    app = Flask(__name__)
    app.config.from_object(configuration_file)
    app.config['API_SPEC_OPTIONS'] = {
        'security': [
            {
                "bearerAuth": [

                ]
            }
        ],
        'components': dict(securitySchemes={
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        })
    }
    api.init_app(app)

    from App.views import views

    from App.admin import admin

    api.register_blueprint(admin, url_prefix='/admin')

    api.register_blueprint(views, url_prefix='/')

    from App.taskviews import taskers

    api.register_blueprint(taskers, url_prefix='/tasks/')

    from App.workerservice import worker

    api.register_blueprint(worker, url_prefix='/worker')
    return app
