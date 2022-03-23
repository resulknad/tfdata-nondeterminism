#!/usr/bin/env bash

source lib.sh
print_title "Executing with 3 Workers"
./start_service.sh 3
sleep 10
collect_results
./kill_service.sh

print_title "Executing with 1 Worker"
./start_service.sh 1
sleep 10
collect_results
./kill_service.sh
