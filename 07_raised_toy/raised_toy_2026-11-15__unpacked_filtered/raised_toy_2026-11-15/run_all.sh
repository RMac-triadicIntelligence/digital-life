#!/bin/bash
# two workers: A takes even seeds of the full toy then ladder seed 0,1; B takes odd seeds then the rest
cd /home/claude/raised_toy
A() { for s in 0 2 4 6 8 10; do python3 commons_raised.py $s 29200 full/seed_$(printf %02d $s).json HSFW; done
      for arm in H HS; do for s in 0 1 2; do python3 commons_raised.py $s 29200 $arm/seed_$(printf %02d $s).json $arm; done; done; }
B() { for s in 1 3 5 7 9; do python3 commons_raised.py $s 29200 full/seed_$(printf %02d $s).json HSFW; done
      for s in 0 1 2; do python3 commons_raised.py $s 29200 HSF/seed_$(printf %02d $s).json HSF; done; }
A > logA.txt 2>&1 &
B > logB.txt 2>&1 &
wait
