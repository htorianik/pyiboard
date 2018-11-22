from flask import Flask
from src.database import db, User, Post, Board, Permission

app = Flask(__name__)

@app.route("/hello")
def hello_handle():
    
    user1 = User()
    db.session.add(user1)
    db.session.commit()

    return "Hello :D"

def create_app(Config):
    app.config.update(Config.FLASK_CONFIG)
    db.init_app(app)

    return app