#!/bin/bash
workers=$1
settings=$2
for i in $( seq 1 $workers )
do
rq worker -c $settings &
done
