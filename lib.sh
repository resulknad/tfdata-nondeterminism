#!/usr/bin/env bash
collect_results () {
  grep -B 1 "Epoch took" logs/pipeline.log 
}

wait_for_epoch_start () {
  tail -n 0 -f logs/pipeline.log | sed '/Starting worker thread/ q' > /dev/null
  sleep 1
}

wait_for_epoch () {
  tail -n 0 -f logs/pipeline.log | sed '/Epoch took/ q' > /dev/null
}

wait_for_dir_creation () {
  inotifywait -e create outputs/ > /dev/null 2>&1
}

print_title () {
  echo ""
  echo -e "\e[1;44m$1\e[0m"
}

start_worker () {
  echo "starting worker $1"
	exec python sources/worker.py -p $(( 40000 + ${1} )) > logs/worker_${1}.log 2>&1 &
	echo $! > pids/worker_${1}
}

kill_worker () {
  echo "killing worker $1"
  kill `cat pids/worker_$1`
}
