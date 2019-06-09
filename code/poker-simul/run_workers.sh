#!/bin/bash
workers=$1
settings=$2
rq worker -c $settings &
for i in $( seq 1 $workers )
do
nohup rq worker -c $settings > workerlogs&/i&
done
