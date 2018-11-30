import hashlib
import random
import string
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, make_response
from functools import wraps
from config import Config
from src.database import db, User, Post, Board, Permission, Session

app = Flask(__name__, template_folder=Config.TEMPLATES_DIR)
app.config.update(Config.FLASK_CONFIG)
db.init_app(app)

# the root of roots
GENESIS_POST_ID = 1


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
                return jsonify({
                    "Respose": "Couldn't authorize you :|"
                })
            else:
                return func(**argd)

        return wrapper
    return real_decorator


def rand_string(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def hash_password(login, password):
    return hashlib.sha256((password + login + Config.SALT).encode('utf-8')).hexdigest()


def get_thread_post(post):
    current_post = post

    while(current_post.parent and current_post.parent.id != GENESIS_POST_ID):
        current_post = Post.query.filter_by(id=current_post.parent.id).first()

        if not current_post:
            return None

    return current_post

######################## FRONT END ############################

def render_board(current_board):
    boards = Board.query.all()
    thread_posts = Post.query.filter_by(parent_id=GENESIS_POST_ID, board=current_board).all()
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

    return render_template(
        'thread.html',
        boards=boards,
        current_board=current_board,
        thread_post=thread_post,
        posts=posts
    )

######################## BACK END #############################

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

    return render_template('base.html', boards=boards)


@app.route('/board/<board_short>')
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


@app.route('/board/<board_short>/make_post')
@check_query_args({'parent_post_id', 'head', 'body'})
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

    thread_post = get_thread_post(parent_post)
    return redirect(f'/board/{current_board.short}/thread/{thread_post.id}')


@app.route('/board/<board_short>/make_thread_post')
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
    return redirect(f'/board/{current_board.short}')


@app.route('/board/<board_short>/thread_post_constructor')
@session_checker()
def board_thread_post_constructor(board_short):
    current_board = Board.query.filter_by(  
        short=board_short
    ).first()

    if not current_board:
        return "<h1>There is no such</h1>"

    return render_thread_post_constructor(current_board)


@app.route('/board/<board_short>/post_constructor')
@check_query_args({'parent_post_id'})
@session_checker()
def board_post_constructor_handle(board_short):
    current_board = Board.query.filter_by(short=board_short).first()

    if not current_board:
        return "<h1>There is no such</h1>"

    parent_post_id = request.args.get('parent_post_id')

    parent_post = Post.query.filter_by(id=parent_post_id).first()

    return render_post_constructor(current_board, parent_post)


@app.route('/board/<board_short>/thread/<thread_post_id>')
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

    

@app.route('/registration')
def registration_handle():
    return render_template(
        'register.html',
        login='Registration'
    )


@app.route('/login')
def login_handle():
    return render_template(
        'login.html', 
        title='Login'
        )

@app.route('/public/<path:filename>')
def public_handle(filename):
    return send_from_directory(
        Config.PUBLIC_DIR, 
        filename, 
        as_attachment=True)