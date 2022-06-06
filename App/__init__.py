from flask import Flask


def create_app(configuration_file='configuration.Config'):
    app = Flask(__name__)
    app.config.from_object(configuration_file)

    from App.views import views

    app.register_blueprint(views, url_prefix='/')
    return app
