from flask import Flask
from flask_smorest import Api
from flask_cors import CORS
# from MpesaRest import Mpesa

#mpesa = Mpesa(
 #  consumer_key='GfcDOBUOM4oFzQpmq6QUYL2TR8rJXhvM',
  # consumer_secret='66olbx4MCiDMfoIz',
   #business_code=174379,
   #passcode='bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919',
   #call_back='https://myapp.co.ke/',
   #environment='development',
   #phone_number=254794784462,
   #BusinessShortCode=174379,
   #Accountreference='MyCompany'
#)

api = Api()

cors_inst = CORS(resources={"/*":{
        "origins": "*"
    }
})


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
    cors_inst.init_app(app)
    from App.views import views

    from App.admin import admin

    api.register_blueprint(admin, url_prefix='/admin')

    api.register_blueprint(views, url_prefix='/')

    from App.taskviews import taskers

    api.register_blueprint(taskers, url_prefix='/tasks/')

    from App.workerservice import worker

    api.register_blueprint(worker, url_prefix='/worker')
    return app
