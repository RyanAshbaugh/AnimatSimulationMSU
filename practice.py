#!/bin/bash --login
#PBS -l nodes=1:ppn=1,walltime=00:05:00,mem=200mb
#PBS -j oe

a = 0
for i in range(1000):
    a+=1
print a