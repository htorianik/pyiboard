from datetime import datetime
import string
import random

from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()

def rand_string_wrapper(length):
    def rand_string():
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
    return rand_string    

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(32), nullable=False)
    pass_hash = db.Column(db.String(32), nullable=False)
    registered = db.Column(db.DateTime, default=datetime.today(), nullable=False)
    posts = db.relationship('Post', back_populates='user')
    permissions = db.relationship('Permission')

    def __repr__(self):
        return "<User %s>" % self.id


class Board(db.Model):
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    short = db.Column(db.String(32), nullable=False)
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
    #children = db.relationship('Post', back_populates='child')
    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    #child = db.relationship('Post', back_populates='children')
    head = db.Column(db.String(256), nullable=False)
    body = db.Column(db.String(65536), nullable=False)
    created = db.Column(db.DateTime, default=datetime.today(), nullable=False)

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


class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='permissions')
    token = db.Column(db.String(32), default=rand_string_wrapper(24), nullable=False)
    opened = db.Column(db.DateTime, default=datetime.today(), nullable=False)
    ip = db.Column(db.String(32), default='0.0.0.0')
    user_agent = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return "<Session %s>" % self.id