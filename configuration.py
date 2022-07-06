import os

base = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ENVIRONMENT = 'development'
    ADMIN = os.environ.get('ADMIN_EMAIL')
    API_TITLE = 'Documentation'
    API_VERSION = '0.0.1'
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_JSON_PATH = os.path.join(base, 'swagger.json')
    SECRET_KEY = 'a2facfb845405ef5de81d346f625023251bde71aae8b6e24c8d4081d938debc58de162b7f124239a36e40c10fcae7ad9f115'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_PATH = '/api/documentation'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    JSONIFY_PRETTYPRINT_REGULAR = True

class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    ENVIRONMENT = 'testing'
    FILENAME = 'test.db'
