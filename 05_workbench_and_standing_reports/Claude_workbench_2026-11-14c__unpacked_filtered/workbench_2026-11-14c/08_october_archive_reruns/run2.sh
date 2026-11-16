#!/bin/bash
cd /home/claude/oct25/run/gw && python3 -I run_v1.py > ../gw_stdout.txt 2> ../gw_stderr.txt; echo "exit $?" > ../gw_exit.txt
cd /home/claude/oct25/run/gld && python3 tools/verify_seal.py > ../gld_seal.txt 2>&1; python3 tools/reproduce.py > ../gld_stdout.txt 2> ../gld_stderr.txt; echo "exit $?" > ../gld_exit.txt
