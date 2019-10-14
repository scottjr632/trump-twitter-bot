import os
import os
import logging

from .definitions import ROOT_DIR


class BaseConfig(object):
    DEBUG = False
    TESTING = False
    ENV = "production"

    WEB_DIR = ROOT_DIR + os.environ.get('WEB_DIR', '/public')
    PORT = os.environ.get('SERVER_PORT', 5000)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = "development"
    LOG_LEVEL = logging.DEBUG


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    ENV = "testing"
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    logging.INFO
