#!/usr/bin/python3

import os
import sys
from flask import Flask
from src.server import app

try:
    app.run(port=5000)
except Exception as _:
    exit(1)
else:
    exit(0)

