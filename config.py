import sys
import os

class Config:

    PROJECT_ROOT_DIR = os.path.dirname( os.path.abspath(__file__) )
    PUBLIC_DIR = os.path.join(PROJECT_ROOT_DIR, 'public')
    TEMPLATES_DIR = os.path.join(PROJECT_ROOT_DIR, 'templates')
    VAR_DIR = os.path.join(PROJECT_ROOT_DIR, 'var')

    FLASK_CONFIG = {
        "TESTING": True, 
        "FLASK_ENV": "development",

        'SQLALCHEMY_DATABASE_URI': 'sqlite:///%s' % os.path.join(VAR_DIR, 'database.sqlite'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }