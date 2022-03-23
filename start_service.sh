#!/usr/bin/env bash
source lib.sh
# Set up environment
cd "$(dirname "$0")"
#source <set_your_venv_here>

# Remove old traces
./kill_service.sh

rm pids/* && rm -rf outputs/materialized

truncate -s0 logs/*

# Get the desired worker count
worker_count=${1:-2}

# pipeline arg
pipeline_arg=${2:-"pipeline.py"}

# Start the service
script -c "python sources/dispatcher.py 2>&1"  -f logs/dispatcher.log > /dev/null 2>&1 &
echo $! > pids/dispatcher
sleep 1

for i in $(seq 1 ${worker_count}); do
  start_worker $i
	sleep 1
done

echo "starting $pipeline_arg"
script -c "python sources/$pipeline_arg 2>&1" -f logs/pipeline.log > /dev/null 2>&1 &
echo $! > pids/pipeline
