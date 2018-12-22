import string
import datetime
import random
from src.database import db
from src.parser import parse_to_markup
from src.utils import dump_time, rand_string_wrapper, get_children, GENESIS_POST_ID

def get_thread_post(post):
    current_post = post

    while(current_post.parent and current_post.parent.id != GENESIS_POST_ID):
        current_post = Post.query.filter_by(id=current_post.parent.id).first()

        if not current_post:
            return None

    return current_post

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

    def dump_to_dict(self):
        return {
            'id': self.id,
            'login': self.login,
            'registered': dump_time(self.registered)
        }


class Board(db.Model):
    __tablename__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    short = db.Column(db.String(32), nullable=False)
    posts = db.relationship('Post', back_populates='board')
    files = db.relationship('FileTracker')

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

    files = db.relationship('FileRefference')

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
            'body': parse_to_markup(self.body),
            'created': dump_time(self.created)
        }

        if(with_children):
            children = get_children(self)[:child_number]
            children = list(map(
                lambda post:
                    post.dump_to_dict(),
                children
            ))

            dumped.update({
                'children': children
            })

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


class FileRefference(db.Model):
    __tablename__ = 'file_refference'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='files')
    filetracker_id = db.Column(db.Integer, db.ForeignKey('filetracker.id'))
    filetracker = db.relationship('FileTracker')


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


class FileTracker(db.Model):
    __tablename__ = 'filetracker'
    id = db.Column(db.Integer, primary_key=True)
    uploaded = db.Column()
    origin = db.Column(db.String(32))
    ext = db.Column(db.String(32))
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'))
    board = db.relationship('Board', back_populates='files')
    uploaded = db.Column(db.DateTime, default=datetime.datetime.today(), nullable=False)

    @staticmethod
    def create_from_file(file, board):
        ext = file.filename.rsplit('.', 1)[1].lower()
        origin = file.filename[:-(len(ext) + 1)]
        return FileTracker(
            origin=origin,
            ext=ext,
            board=board
        )

    def to_filename(self):
        return f"{str(self.id)}.{self.ext}"

    def to_origin_filename(self):
        return f"{self.origin}.{self.ext}"