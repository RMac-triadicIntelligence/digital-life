#!/bin/bash
W=/home/claude/gb_piccolo/work
S=$(date +%s); ( cd $W/conn71 && python3 -I run_once.py --output $W/out_conn71 > $W/conn71_stdout.txt 2> $W/conn71_stderr.txt; echo "exit $? secs $(( $(date +%s) - S ))" > $W/conn71_exit.txt )
S=$(date +%s); ( cd $W/diag71 && python3 -I run_diag.py --output $W/out_diag71 > $W/diag71_stdout.txt 2> $W/diag71_stderr.txt; echo "exit $? secs $(( $(date +%s) - S ))" > $W/diag71_exit.txt )
echo done > $W/oct71_done.txt
