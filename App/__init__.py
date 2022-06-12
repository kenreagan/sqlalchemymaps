from flask import Flask
from flask_smorest import Api
# from MpesaRest import Mpesa
import os
# from flask_jwt_extended import JWTManager
api = Api()

# jwtmanager = JWTManager()

# config = {
#     'consumer_secret': os.environ.get('secret'),
#     'consumer_key': os.environ.get('key'),
#     'business_code': os.environ.get('CODE')
# }
# mpesa = Mpesa(**config)


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
    # jwtmanager.init_app(app)
    from App.views import views

    api.register_blueprint(views, url_prefix='/')
    return app
