import os
from dotenv import load_dotenv

class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    @property
    def BING_MAPS_API_KEY(self):
        return os.getenv('BING_MAPS_API_KEY', 'default_secret_key')
    

class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    URL = "http://127.0.0.1:5000/"

    load_dotenv()
    engine = os.environ.get('SQL_ENGINE')
    username = os.environ.get('SQL_USER')
    password = os.environ.get('SQL_PASSWORD')
    host = os.environ.get('SQL_HOST')
    port = os.environ.get('SQL_PORT')
    database = os.environ.get('SQL_DATABASE')

    SQLALCHEMY_DATABASE_URI = f'{engine}://{username}:{password}@{host}:{port}/{database}'

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False

    URL = "https://uproute.app/api/"

    engine = os.environ.get('SQL_ENGINE')
    username = os.environ.get('SQL_USER')
    password = os.environ.get('SQL_PASSWORD')
    host = os.environ.get('SQL_HOST')
    port = os.environ.get('SQL_PORT')
    database = os.environ.get('SQL_DATABASE')

    SQLALCHEMY_DATABASE_URI = f'{engine}://{username}:{password}@{host}:{port}/{database}'