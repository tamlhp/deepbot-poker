#!/bin/bash
workers="$(($1-1))"
ip=$2
python3 worker_script.py $ip &
for i in $( seq 1 $workers )
do
nohup python3 worker_script.py $ip > workerlogs &
done
