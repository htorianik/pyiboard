from functools import wraps
import datetime
import hashlib
import string
import random

from config import Config

GENESIS_POST_ID = 1

def dump_time(t):
    return t.strftime('%Y-%m-%d %H:%M:%S')


def rand_string_wrapper(length):
    def rand_string():
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
    return rand_string    


def get_children(base_post, sort_by_date=True):
    children = []

    def append_children(parent_post):
        for child_post in parent_post.children:
            children.append(child_post)
            append_children(child_post)

    append_children(base_post)

    if sort_by_date:
        children = sorted(children, key=lambda post: post.created)

    return children


def rand_string(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def hash_password(login, password):
    return hashlib.sha256((password + login + Config.SALT).encode('utf-8')).hexdigest()
