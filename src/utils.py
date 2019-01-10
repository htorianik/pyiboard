from functools import wraps
import datetime
import hashlib
import string
import random
import subprocess
import os

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


def get_file_size(filename):
    ls_process = subprocess.Popen(['ls', '-lh', filename], stdout=subprocess.PIPE)
    awk_process = subprocess.Popen(['awk', '{print $5}'], stdin=ls_process.stdout, stdout=subprocess.PIPE)
    output, error = awk_process.communicate()

    if error:
        raise ValueError()
    return output.decode('utf-8')[:-1]


def get_file_resolution(filename):
    bash_command = "ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 %s" % (filename)
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if error:
        raise ValueError()
    return output.decode('utf-8')[:-1]


def get_ext(filename):
    return os.path.splitext(filename)[1][1:]
