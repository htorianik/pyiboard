import hashlib
from config import Config

def hash_password(login, password):
    return hashlib.sha256((password + login + Config.SALT).encode('utf-8')).hexdigest()