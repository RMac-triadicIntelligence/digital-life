#!/bin/bash
cd /home/claude/oct25/run
S=$(date +%s)
( cd conn && python3 -I run_once.py --output /home/claude/oct25/run/out_conn > ../conn_stdout.txt 2> ../conn_stderr.txt; echo "exit $? secs $(( $(date +%s) - S ))" > ../conn_exit.txt )
S=$(date +%s)
( cd diag && python3 -I run_diag.py --output /home/claude/oct25/run/out_diag > ../diag_stdout.txt 2> ../diag_stderr.txt; echo "exit $? secs $(( $(date +%s) - S ))" > ../diag_exit.txt )
S=$(date +%s)
( cd commons/commons_v2 && cp results.json ../../results_commons_sealed.json && python3 run_all.py > ../../commons_stdout.txt 2> ../../commons_stderr.txt; echo "exit $? secs $(( $(date +%s) - S ))" > ../../commons_exit.txt )
echo done > all_done.txt
