#!/bin/bash
workers=$1
settings=$2
for i in $( seq 1 $workers )
do
nohup rq worker -c $settings > workerlogs&
done

rq worker -c $settings
