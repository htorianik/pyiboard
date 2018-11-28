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

def check_query_args(required_keys):
    def real_decorator(func):
        @wraps(func)
        def wrapper():
            given_keys = set(request.args.keys())
            
            print(given_keys)
            print(required_keys)

            if not required_keys.issubset(given_keys):
                return jsonify({
                    "Response": "You didn't provide all of required arguments",
                    "Missing_arguments": list( required_keys.difference(given_keys) )
                })
            else:
                return func()

        return wrapper
    return real_decorator


def session_checker():
    def real_decorator(func):
        @wraps(func)
        def wrapper():
            session_id = request.cookies.get('session_id')
            session_token = request.cookies.get('session_token')
            user_agent = request.headers.get('User-Agent')

            current_session = Session.query.filter_by(
                id=session_id,
                token=session_token,
                user_agent=user_agent
            ).first()

            print(session_id)
            print(session_token)

            if not current_session:
                return jsonify({
                    "Respose": "Couldn't authorize you :|"
                })
            else:
                return func()

        return wrapper
    return real_decorator


def rand_string(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def hash_password(login, password):
    return hashlib.sha256((password + login + Config.SALT).encode('utf-8')).hexdigest()

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
    return "<b1>This is index :D</b1>"


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