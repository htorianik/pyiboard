#!/bin/bash

. ../bin/activate
python3 run.py &> nohup.out &
echo $! > var/pid