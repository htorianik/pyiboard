
import subprocess
import os
from functools import wraps
from src.models import  User, Post, Board, Permission, Session, FileTracker, get_thread_post, FileRefference
from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, make_response, Blueprint

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


def errors_handler():
    def real_decorator(func):
        @wraps(func)
        def wrapper(**argd):
            try:
                return func(**argd)
            except Exception as err:
                return jsonify({
                    "success": False, 
                    "response": str(err)
                })
        return wrapper
    return real_decorator
