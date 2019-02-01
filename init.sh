#!/bin/bash

. ../bin/activate

mkdir var
mkdir resources/uploads
pip install -r requirements.txt

bash reload.sh