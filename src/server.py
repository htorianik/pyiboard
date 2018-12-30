import hashlib
import random
import string
import os
import json
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, make_response, Blueprint
from functools import wraps
from config import Config
from src.database import db
from src.models import  User, Post, Board, Permission, Session, FileTracker, get_thread_post, FileRefference
from src.utils import GENESIS_POST_ID, rand_string, hash_password

app = Blueprint('/', __name__, template_folder=Config.TEMPLATES_DIR)

######################## UTILS ################################


def check_query_args(required_keys):
    def real_decorator(func):
        @wraps(func)
        def wrapper(**argd):
            given_keys = set(request.args.keys())

            if not required_keys.issubset(given_keys):
                return jsonify({
                    "Response": "You didn't provide all of required arguments",
                    "Missing_arguments": list( required_keys.difference(given_keys) )
                })
            else:
                return func(**argd)

        return wrapper
    return real_decorator


def session_checker():
    def real_decorator(func):
        @wraps(func)
        def wrapper(**argd):
            session_id = request.cookies.get('session_id')
            session_token = request.cookies.get('session_token')
            user_agent = request.headers.get('User-Agent')

            current_session = Session.query.filter_by(
                id=session_id,
                token=session_token,
                user_agent=user_agent
            ).first()

            if not current_session:
                return redirect('/login')
            else:
                return func(**argd)

        return wrapper
    return real_decorator


def get_user():
    def real_decorator(func):
        @wraps(func)
        def wrapper(**argd):
            session_id = request.cookies.get('session_id')
            current_session = Session.query.filter_by(id=session_id).first()
            return func(current_user=current_session.user, **argd)
        return wrapper
    return real_decorator


######################## FRONT END ############################

def render_board(current_board):
    boards = Board.query.all()
    thread_posts = Post.query.filter_by(
        parent_id=GENESIS_POST_ID,
        board=current_board
    ).all()

    thread_posts = list(map(
        lambda post: 
            post.dump_to_dict(with_children=True, child_number=3),
        thread_posts
    ))

    return render_template('board.html', boards=boards, current_board=current_board, posts=thread_posts)


def render_thread_post_constructor(current_board, callback_url=None):
    boards = Board.query.all()
    return render_template(
        'thread_post_constructor.html',
        boards=boards,
        current_board=current_board,
        callback_url=callback_url
    )


def render_post_constructor(current_board, parent_post, callback_url=None):
    boards = Board.query.all()
    return render_template(
        'post_constructor.html',
        boards=boards,
        current_board=current_board,
        parent_post=parent_post,
        callback_url=callback_url
    )


def render_thread(current_board, thread_post):
    boards = Board.query.all()
    posts = Post.query.all()

    posts = Post.query.all()
    posts = list(filter(
        lambda post : 
            get_thread_post(post) == thread_post and post != thread_post,
        posts   
    ))
    posts = list(map(
        lambda post: 
            post.dump_to_dict(),
        posts
    ))
    thread_post = thread_post.dump_to_dict()

    return render_template(
        'thread.html',
        boards=boards,
        current_board=current_board,
        thread_post=thread_post,
        posts=posts
    )


def render_login():
    boards = Board.query.all()
    return render_template('login.html', boards=boards)


def render_registration():
    boards = Board.query.all()
    return render_template('registration.html', boards=boards)


def render_me(current_user):
    boards = Board.query.all()
    current_user = current_user.dump_to_dict()

    return render_template('me.html', boards=boards, current_user=current_user) 

######################## BACK END #############################

def associate_with_post(files, post):
    filetrackers = list(map(
        lambda id:
            FileTracker.query.filter_by(id=id).first(),
        files
    ))

    file_refferences = list(map(
        lambda filetracker:
            FileRefference(
                post=post,
                filetracker=filetracker
            ),
        filetrackers
    ))

    db.session.add_all(file_refferences)
    db.session.commit()


@app.route('/authentication')
@check_query_args({'login', 'password'})
def oauth2_handle():
    login, password = request.args.get('login'), request.args.get('password')
    pass_hash = hash_password(login, password)

    valid_user = User.query.filter_by(
        login=login, 
        pass_hash=pass_hash
    ).first()

    if not valid_user:
        return jsonify({
            "Response": "There is no user with such login or password"
        })

    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    active_session = Session.query.filter_by(
        user=valid_user,
        user_agent=user_agent,
        ip=ip
    ).first()

    session_id = None
    session_token = None

    if active_session:
        session_id = active_session.id
        session_token = active_session.token
    else:
        new_session = Session(
            user=valid_user,
            user_agent=request.headers.get('User-Agent'),
            ip=request.remote_addr
        )
        db.session.add(new_session)
        db.session.commit()
        session_id = new_session.id
        session_token = new_session.token

    response = make_response(redirect('/'))
    response.set_cookie('session_id', str(session_id).encode('utf-8'))
    response.set_cookie('session_token', session_token.encode('utf-8'))

    return response

@app.route('/register')
@check_query_args({'login', 'password'})
def register_handle():
    args = request.args
    same_login_user = User.query.filter_by(login=args.get('login')).first()
    if same_login_user:
        return jsonify({
            "Response": "Pls create an unique login"
        })
        
        return redirect('/register?register_error=true')

    new_user = User(
        login=args.get('login'),
        pass_hash=hash_password(args.get('login'), args.get('password'))
    )

    db.session.add(new_user)
    db.session.commit()
    return redirect('/authentication?login=%s&password=%s' % (
        args.get('login'),
        args.get('password')
        ))


@app.route('/logout')
@session_checker()
def logout_handle():
    response.set_cookie('session_id', str(-1).encode('utf-8'))
    response.set_cookie('session_token', "None".encode('utf-8'))
    return jsonify({
        "Reponse": "You loged out :|"
    })

@app.route('/')
@session_checker()
def index_handle():
    boards = Board.query.all()
    return render_template('index.html', boards=boards)


@app.route('/<board_short>/make_post')
@check_query_args({'parent_post_id', 'head', 'body', 'files'})
@session_checker()
def board_make_post_handle(board_short):
    current_board = Board.query.filter_by(
        short=board_short
    ).first()

    if not current_board:
        return "<h1>There is no such board :|</h1>"

    parent_post_id = request.args.get('parent_post_id')
    body = request.args.get('body')
    head = request.args.get('head')
    files = json.loads(request.args.get('files'))

    parent_post = Post.query.filter_by(
        id=parent_post_id,
        board=current_board
    ).first()


    if not parent_post:
        return "<h1>There is no such post :|</h1>"

    new_post = Post(
        parent=parent_post,
        head=head, 
        body=body,
        board=current_board
    )
    db.session.add(new_post)
    db.session.commit()

    associate_with_post(files, new_post)

    thread_post = get_thread_post(parent_post)
    return redirect(f'/{current_board.short}/thread/{thread_post.id}')


@app.route('/<board_short>/make_thread_post')
@check_query_args({'head', 'body'})
@session_checker()
def board_make_thred_post(board_short):
    current_board = Board.query.filter_by(  
        short=board_short
    ).first()

    if not current_board:
        return "<h1>There is no such</h1>"

    body = request.args.get('body')
    head = request.args.get('head')

    genesis_post = Post.query.filter_by(
        id=GENESIS_POST_ID
    ).first()

    new_post = Post(
        parent=genesis_post,
        head=head, 
        body=body,
        board=current_board
    )
    db.session.add(new_post)
    db.session.commit()
    return redirect(f'/{current_board.short}')



@app.route('/<board_short>/post_constructor')
@check_query_args({'parent_post_id'})
@session_checker()
def board_post_constructor_handle(board_short):
    current_board = Board.query.filter_by(short=board_short).first()

    if not current_board:
        return "<h1>There is no such</h1>"

    parent_post_id = request.args.get('parent_post_id')

    parent_post = Post.query.filter_by(id=parent_post_id).first()

    return render_post_constructor(current_board, parent_post)


@app.route('/<board_short>/thread/<thread_post_id>')
@session_checker()
def board_thread_post_handle(board_short, thread_post_id):
    current_board = Board.query.filter_by(short=board_short).first()

    if not current_board:
        return "<h1>There is no board</h1>"

    thread_post = Post.query.filter_by(
        id=thread_post_id,
        board=current_board,
        parent_id=GENESIS_POST_ID
    ).first()

    if not thread_post:
        return "<h1> There is no such thread post in this board :| </h1>"

    return render_thread(current_board=current_board, thread_post=thread_post)


@app.route('/<board_short>')
@session_checker()
def board_handle(board_short):
    current_board = Board.query.filter_by(
        short=board_short
    ).first()

    if not current_board:
        return "<h1>There is no such</h1>"

    threads = Post.query.filter_by(
        parent_id = GENESIS_POST_ID,
        board_id = current_board.id
    ).all()

    threads = list(map(lambda thread : thread.dump_to_dict(), threads))

    return render_board(current_board)
    

@app.route('/registration')
def registration_handle():
    return render_registration()


@app.route('/login')
def login_handle():
    return render_login()


@app.route('/me')
@session_checker()
@get_user()
def me_handle(current_user):
    return render_me(current_user)


@app.route('/public/<path:filename>')
def public_handle(filename):
    return send_from_directory(
        Config.PUBLIC_DIR, 
        filename, 
        as_attachment=True)


@app.route('/<board_short>/files/<path:filename>')
def files_handle(filename, board_short):
    current_board = Board.query.filter_by(
        short=board_short
    ).first()

    if not current_board:
        return jsonify({
            'Response': 'ERR'
        })

    filetracker = list(filter(
        lambda filetracker:
            filetracker.to_filename() == filename,
        FileTracker.query.all()
        ))

    if not filetracker:
        return jsonify({
            'Response': 'ERR'
        })

    filetracker = filetracker[0]

    if filetracker.board != current_board:
        return jsonify({
            'Response': 'ERR'
        })

    return send_from_directory(
        Config.UPLOAD_DIR,
        filetracker.to_filename()
    )


@app.route('/<board_short>/upload', methods=['POST'])
def upload_handle(board_short):
    current_board = Board.query.filter_by(
        short=board_short
    ).first()

    if not current_board:
        return jsonify({
            'Response': 'ERR'
        })

    if 'file' not in request.files:
        return jsonify({
            'Reponse': 'ERR'
        })

    file = request.files['file']
    if not file.filename:
        return jsonify({
            'Response': 'ERR'
        })

    filetracker = FileTracker.create_from_file(file, board=current_board)
    db.session.add(filetracker)
    db.session.commit()

    file.save(os.path.join(Config.FLASK_CONFIG.get("UPLOAD_FOLDER"), filetracker.to_filename()))
    return jsonify({
        'Response': 'OK',
        'filename': filetracker.to_filename()
    })

### TEST FRONTEND ###

@app.route('/debug', methods=['GET'])
def index_debug_handle():
    boards = Board.query.all()
    return render_template('index_debug.html', boards=boards)