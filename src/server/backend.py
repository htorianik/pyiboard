import hashlib
import random
import string
import os
import json
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, make_response, Blueprint
from config import Config
from src.database import db
from src.database import  User, Post, Board, Permission, Session, FileTracker, get_thread_post, FileRefference
from src.utils import GENESIS_POST_ID, rand_string, hash_password
from src.engine import register_user, login_user, associate_with_post, get_board_by_short, get_last_upload_id
from src.server.utils import check_query_args, get_user, session_checker, errors_handler
from src.utils import get_ext

app = Blueprint('backend', __name__, template_folder=Config.TEMPLATES_DIR)


@app.route('/authentication')
@check_query_args({'login', 'password'})
def uthentication_handle():
    login = request.args.get('login')
    password = request.args.get('password')

    try:
        session_id, session_token = login_user(login, password, request.remote_addr, request.headers.get('User-Agent'))
    except ValueError as err:
        return redirect(f'/login?err={str(err)}')

    response = make_response(redirect('/'))
    response.set_cookie('session_id', str(session_id).encode('utf-8'))
    response.set_cookie('session_token', session_token.encode('utf-8'))
    return response


@app.route('/register')
@check_query_args({'login', 'password'})
def register_handle():
    login = request.args.get('login')
    password = request.args.get('password')

    try:
        register_user(login, password)
    except ValueError as err:
        return redirect(f'/registration?err={str(err)}')
    else:
        return redirect(f'/authentication?login={login}&password={password}')


@app.route('/logout')
@session_checker()
def logout_handle():
    response = make_response(redirect('/login'))
    response.set_cookie('session_id', str(-1).encode('utf-8'))
    response.set_cookie('session_token', "None".encode('utf-8'))
    return response


@app.route('/<board_short>/make_post')
@check_query_args({'parent_post_id', 'head', 'body', 'files'})
@session_checker()
def board_make_post_handle(board_short):
    board = get_board_by_short(board_short)
    parent_post_id = int(request.args.get('parent_post_id'))
    body = request.args.get('body')
    head = request.args.get('head')
    files = json.loads(request.args.get('files'))

    parent_post = None
    if parent_post_id == 1:
        parent_post = Post.query.filter_by(
            id=parent_post_id
        ).first()
    else:
        parent_post = Post.query.filter_by(
            id=parent_post_id,
            board=board
        ).first()

    if not parent_post:
        return "<h1>There is no such post :|</h1>"

    new_post = Post(
        parent=parent_post,
        head=head, 
        body=body,
        board=board
    )
    db.session.add(new_post)
    db.session.commit()

    associate_with_post(files, new_post)

    thread_post = get_thread_post(new_post)
    return redirect(f'/{board.short}/thread/{thread_post.id}')

"""
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
    files = json.loads(request.args.get('files'))

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

    associate_with_post(files, new_post)

    return redirect(f'/{current_board.short}')
"""

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


"""
get resolution of video and image file:
>>ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 uoloads/9.webm
>>1280x1080
get size of any file:
>>ls -lh ./uploads/1.png | awk '{print $5}'
>>228
"""
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

    file_id = get_last_upload_id() + 1
    file_ext = get_ext(file.filename)
    save_path = os.path.join(Config.FLASK_CONFIG.get("UPLOAD_FOLDER"), f"{file_id}.{file_ext}")
    file.save(save_path)

    filetracker = FileTracker.create_from_file(path=save_path, board=current_board)
    db.session.add(filetracker)
    db.session.commit()
    
    return jsonify({
        'Response': 'OK',
        'filename': filetracker.to_filename()
    })