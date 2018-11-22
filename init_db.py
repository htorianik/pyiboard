#!/usr/bin/python3

import os

from flask import Flask

from config import Config
from src.database import db

if not os.path.exists(Config.VAR_DIR):
    os.makedirs(Config.VAR_DIR)

fake_app = Flask(__name__)
fake_app.config.update(Config.FLASK_CONFIG)

db.init_app(fake_app)

with fake_app.app_context():
    db.drop_all()
    db.create_all()