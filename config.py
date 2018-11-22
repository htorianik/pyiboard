import sys
import os

class Config:

    PROJECT_ROOT_DIR = os.path.dirname( os.path.abspath(__file__) )
    PUBLIC_DIR = os.path.join(PROJECT_ROOT_DIR, 'public')
    TEMPLATES_DIR = os.path.join(PROJECT_ROOT_DIR, 'templates')
    VAR_DIR = os.path.join(PROJECT_ROOT_DIR, 'var')
    
    SALT = 'VfXR7TaGqF34bj1Z'

    HOST = 'localhost'
    PORT = 5000
    URL = 'localhost:5000'

    FLASK_CONFIG = {
        'TESTING': True, 
        'FLASK_ENV': "development",
        'TEMPLATES_AUTO_RELOAD': True,
        'DEBUG': True,

        'SQLALCHEMY_DATABASE_URI': 'sqlite:///%s' % os.path.join(VAR_DIR, 'database.sqlite'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }