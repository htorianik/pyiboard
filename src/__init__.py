from flask import Flask

from config import Config
from src.server import app
from src.database import db

app1 = Flask(__name__, template_folder=Config.TEMPLATES_DIR)
app1.config.update(Config.FLASK_CONFIG)
db.init_app(app1)
app1.register_blueprint(app)