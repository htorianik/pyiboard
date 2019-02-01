#!/bin/bash

. ../bin/activate

rm /resources/uploads/*
python3 reload_db.py