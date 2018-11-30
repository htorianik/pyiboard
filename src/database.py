import string
import datetime
import random

from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()

def dump_time(t):
    return t.strftime('%Y-%m-%d %H:%M:%S')

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
    registered = db.Column(db.DateTime, default=datetime.datetime.today(), nullable=False)
    permissions = db.relationship('Permission')
    sessions = db.relationship('Session')

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

    def dump_to_dict(self, with_posts=False, threads_only=True):
        dumped = {
            'id': self.id,
            'title': self.title,
            'short': self.short
        }

        if with_posts:
            posts = list(filter(
                lambda post: 
                    # 1 -- is GENESIS_POST_ID...
                    not(threads_only and (not post.parent or post.parent.id == 1)),
                self.posts
            ))

            posts = list(map(
                lambda post : post.dump_to_dict()
            ))
            
            dumped.update({
                'posts': posts
            })

        return dumped


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)

    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))
    board = db.relationship('Board', back_populates='posts')

    children = db.relationship('Post', back_populates='parent')
    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent = db.relationship('Post', remote_side=[id], back_populates='children')
    
    head = db.Column(db.String(256), nullable=False)
    body = db.Column(db.String(65536), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.today(), nullable=False)

    def __repr__(self):
        return "<Post %s>" % self.id

    def dump_to_dict(self, with_children=False, child_number=3):
        dumped = {
            'id': self.id,
            'board_id': self.board_id,
            'parent_id': self.parent_id,
            'children_ids': list(map(lambda child : child.id, self.children)),
            'board': self.board.short, 
            'head': self.head,
            'body': self.body,
            'created': dump_time(self.created)
        }

        if(with_children):
            pass

        return dumped


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
    user = db.relationship('User', back_populates='sessions')
    token = db.Column(db.String(32), default=rand_string_wrapper(24), nullable=False)
    opened = db.Column(db.DateTime, default=datetime.datetime.today(), nullable=False)
    ip = db.Column(db.String(32), default='0.0.0.0')
    user_agent = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return "<Session %s>" % self.id