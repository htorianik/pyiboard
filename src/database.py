from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # login = db.Column(db.String(32), nullable=False)
    # pass_hash = db.Column(db.String(32), nullable=False)
    # registered = db.Column(db.DateTime, default=datetime.today(), nullable=False)
    # oauth2_token = db.Column(db.String(32), default="")
    posts = db.relationship('Post', back_populates='user')
    permissions = db.relationship('Permission')

    def __repr__(self):
        return "<User %s>" % self.id


class Board(db.Model):
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(32), nullable=False)
    # short = db.Column(db.String(32), nullable=False)
    posts = db.relationship('Post', back_populates='board')

    def __repr__(self):
        return "<Board %s>" % self.id


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='posts')
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))
    board = db.relationship('Board', back_populates='posts')
    # children = db.relationship('Post', back_populates='child')
    # parent_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    # child = db.relationship('Post', back_populates='children')
    # head = db.Column(db.String(256), nullable=False)
    # body = db.Column(db.String(65536), nullable=False)
    # created = db.Column(db.DateTime, default=datetime.today(), nullable=False)

    def __repr__(self):
        return "<Post %s>" % self.id


class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='permissions')
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))
    board = db.relationship('Board')

    def __repr__(self):
        return "<Permission %s>" % self.id