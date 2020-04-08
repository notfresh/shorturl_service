# -*- coding:utf-8 -*-
import os
from yaml import load as load_yml


class YmlEnv:
    def __init__(self, path):
        self.path = path

    def load_to_env(self):
        if os.path.exists(self.path):

            with open(self.path) as config_file:
                ret = load_yml(config_file)
                os.environ['FLASK_ENV'] = ret.get('FLASK_ENV') or 'development'
            return ret
        else:
            raise RuntimeError('Please complete your env.yml')

# config file must exit
env_config = YmlEnv('env/env.yml').load_to_env()

base_dir = os.path.abspath(os.path.dirname(__file__))

# SAE or local variable
db_host = os.environ.get('MYSQL_HOST', '127.0.0.1')
db_port = os.environ.get('MYSQL_PORT', '3306')
db_user = os.environ.get('MYSQL_USER', 'root')
db_password = os.environ.get('MYSQL_PASS', 'root')
db_name = os.environ.get('MYSQL_DB', 'clockin') # MYSQL_DB: app_zxzx



class BaseConfig(object):
    SECRET_KEY = env_config.get('SECRET_KEY') or 'this is a very simple backend'

    # SQLALCHEMY_DATABASE_URI="mysql+pymysql://{}:{}@{}/{}".format(db_user, db_password, '{}:{}'.format(db_host, db_port), db_name)
    SQLALCHEMY_DATABASE_URI = env_config.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join( base_dir, 'app.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    COS_SECRETID = env_config.get('COS_SECRET_ID')
    COS_SECRETKEY = env_config.get('COS_SECERT_KEEY')
    COS_REGION = env_config.get('COS_REGION')
    COS_BUCKET = env_config.get('COS_BUCKET')
    COS_APPID = env_config.get('COS_APPID')
    DOMAIN_NAME = env_config.get('DOMAIN_NAME')
    PORT = env_config.get('PORT')
    HTTP = env_config.get('HTTP')



class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


CONFIGS = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
