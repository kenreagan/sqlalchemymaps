import os

class Config(object):
    SECRET_KEY = 'hello Master'
    ENVIRONMENT = 'development'
    ADMIN = os.environ.get('ADMIN_EMAIL')


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    ENVIRONMENT = 'testing'
    FILENAME = 'test.db'
