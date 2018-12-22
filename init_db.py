#!/usr/bin/python3

import os
import json

from flask import Flask

from config import Config
from src.database import db
from src.models import Board, Post, User
from src.server import hash_password

if not os.path.exists(Config.VAR_DIR):
    os.makedirs(Config.VAR_DIR)

fake_app = Flask(__name__)
fake_app.config.update(Config.FLASK_CONFIG)

db.init_app(fake_app)

with fake_app.app_context():
    db.drop_all()
    db.create_all()

    board_data = None
    with open(os.path.join(Config.PROJECT_ROOT_DIR, 'board-list.json'), "r") as f:
        board_data = json.loads(f.read())

    for board in board_data:
        new_board = Board(
            title=board.get("title"),
            short=board.get("short")
        )

        db.session.add(new_board)
    db.session.commit()

    genesis_post = Post(
        head="I Am genesis",
        body="There should be the most secret information because site should't be able to display this post. "
        "SECRET: SHISHKO IS THE BEST GIRL"
    )
    db.session.add(genesis_post)
    db.session.commit()

    genesis_user = User(
        login='root',
        pass_hash=hash_password('root', '1')
    )
    db.session.add(genesis_user)
    db.session.commit()