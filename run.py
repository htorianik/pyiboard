#!/usr/bin/python3

import os
import sys
from flask import Flask
from src.server import app

app.run(port=5000)

