from flask import Flask
from flask_smorest import Api


api = Api()

def create_app(configuration_file='configuration.Config'):
    app = Flask(__name__)
    app.config.from_object(configuration_file)
    api.init_app(app)

    from App.views import views

    api.register_blueprint(views, url_prefix='/')
    return app
