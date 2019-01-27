from functools import wraps
from shutil import copyfile
import datetime
import hashlib
import string
import random
import subprocess
import os

from config import Config

class Utils:
    GENESIS_POST_ID = 1

    VIDEOS_EXTS = ['mp4', 'webm', 'avi', 'mov', 'wmv']
    IMAGES_EXTS = ['jpeg', 'jpg', 'png', 'bmp', 'gif']
    MUSICS_EXTS = ['wav', 'pm3', 'wma', 'ogg', 'flac']

    @staticmethod
    def dump_time(t):
        return t.strftime('%Y-%m-%d %H:%M:%S')


    @staticmethod
    def rand_string_wrapper(length):
        def rand_string():
            letters = string.ascii_lowercase
            return ''.join(random.choice(letters) for i in range(length))
        return rand_string    


    @staticmethod
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


    @staticmethod
    def rand_string(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))


    @staticmethod
    def hash_password(login, password):
        return hashlib.sha256((password + login + Config.SALT).encode('utf-8')).hexdigest()


    @staticmethod
    def get_file_size(filename):
        ls_process = subprocess.Popen(['ls', '-lh', filename], stdout=subprocess.PIPE)
        awk_process = subprocess.Popen(['awk', '{print $5}'], stdin=ls_process.stdout, stdout=subprocess.PIPE)
        output, error = awk_process.communicate()

        if error:
            raise ValueError()
        return output.decode('utf-8')[:-1]


    @staticmethod
    def get_file_resolution(filename):
        bash_command = "ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 %s" % (filename)
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        if error:
            raise ValueError()
        return output.decode('utf-8')[:-1]


    @staticmethod
    # It also can calc length of music! But idk how :\
    def get_media_length(filename):
        bash_command = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s" % (filename)
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        if error:
            raise ValueError()
        length = output.decode('utf-8')[:-1]
        return length[:length.find('.')]


    @staticmethod
    def cut_first_frame(input_file, output_file):
        bash_command = "ffmpeg -i %s -vframes 1 -f image2 %s" % (input_file, output_file)
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            raise ValueError()


    @staticmethod
    def copy_file(src, dst):
        copyfile(src, dst)
        

    @staticmethod
    def get_ext(filename):
        return os.path.splitext(filename)[1][1:]


    @staticmethod
    def mark_resource(rel_path):
        if rel_path[0] == '/':
            raise ValueError("Relative path should't starts with \'/\'")
        local_path = os.path.join(Config.RESOURCES_DIR, rel_path)
        route = Config.FILES_ROUTE + rel_path
        return local_path, route
