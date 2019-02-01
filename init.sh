#!/bin/bash

. ../bin/activate

mkdir temp
mkdir resources/uploads
pip install -r requirements.txt

bash reload.sh