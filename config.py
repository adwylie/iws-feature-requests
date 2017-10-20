import os
import subprocess


SQLITE_PATH = 'sqlite:///../sqlite.db'
PSQL_HEROKU_PATH = os.environ.get(
    'DATABASE_URL',
    subprocess.run(
        'heroku config:get DATABASE_URL -a adwylie-iws-feature-requests',
        shell=True,
        stdout=subprocess.PIPE
    ).stdout
)


class Config():
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = SQLITE_PATH


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = SQLITE_PATH


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = PSQL_HEROKU_PATH
