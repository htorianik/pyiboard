#!/usr/bin/python3

import os
import sys

from flask import Flask

from config import Config
from src.server import create_app

app = create_app(Config)

app.run(port=5000)

