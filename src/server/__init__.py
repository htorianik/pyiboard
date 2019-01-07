from flask import Flask
from config import Config
from src.database import db
from src.server.backend import app as backend
from src.server.frontend import app as frontend

app = Flask(__name__, template_folder=Config.TEMPLATES_DIR)
app.config.update(Config.FLASK_CONFIG)
db.init_app(app)
app.register_blueprint(backend)
app.register_blueprint(frontend)