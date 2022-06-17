from flask import Flask
from flask_smorest import Api

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
    # jwtmanager.init_app(app)
    from App.views import views

    api.register_blueprint(views, url_prefix='/')

    from App.taskviews import taskers

    api.register_blueprint(taskers, url_prefix='/tasks/')

    from App.workerservice import  worker

    api.register_blueprint(worker, url_prefix='/worker')
    return app
