import string
import datetime
import random

from flask_sqlalchemy import SQLAlchemy
from src.parser import parse_to_markup

from config import Config

db = SQLAlchemy()