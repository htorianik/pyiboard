import hashlib
import random
import string
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect
from functools import wraps
from config import Config
from src.database import db, User, Post, Board, Permission

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


def rand_string(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def hash_password(login, password):
    return hashlib.sha256((password + login + Config.SALT).encode('utf-8')).hexdigest()


@app.route('/oauth')
def oauth_handle():
    return render_template(
        'oauth.html', 
        title='OAuth'
        )

@app.route('/oauth2')
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
    
    if not valid_user.oauth2_token: 
        valid_user.oauth2_token = rand_string(32)

    db.session.commit()

    return redirect('?login=%s&token=%s' % (
        valid_user.login, 
        valid_user.oauth2_token
    ))

@app.route('/')
def index_handle():
    return "<b1>This is index :D</b1>"

@app.route('/register')
@check_query_args({'login', 'password'})
def register_handle():
    args = request.args
    same_login_user = User.query.filter_by(login=args.get('login')).first()
    if same_login_user:
        return jsonify({
            "Response": "There is already user with such login"
        })

    new_user = User(
        login=args.get('login'),
        pass_hash=hash_password(args.get('login'), args.get('password'))
    )

    db.session.add(new_user)
    db.session.commit()
    return redirect('/oauth2?login=%s&password=%s' % (
        args.get('login'),
        args.get('password')
        ))

@app.route('/public/<path:filename>')
def public_handle(filename):
    return send_from_directory(
        Config.PUBLIC_DIR, 
        filename, 
        as_attachment=True)