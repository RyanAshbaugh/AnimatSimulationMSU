import time
import simulate_function
import os
import sys

def write_qsub(animat_id,current_time,current_dir,simLength):	
	qsub_file = open('%s/animat_%s/sim_qsubs/animat_qsub_%d.qsub' % (current_dir, current_time, animat_id), 'w') # opens file so that it can be written to
	qsub_file.write('#!/bin/bash --login\n') # this is the first line that appears in the qsub, it tells the computer to load bash as the language that is used to write this qsub, this must always be the first line in a qsub
	walltime = 2*((simLength/1000)*5)
	walltime_hms = time.strftime("%H:%M:%S", time.gmtime(walltime))
	qsub_file.write('#PBS -l walltime=%s,nodes=1:ppn=1\n' % walltime_hms) # allocates resources for scheduler, 5 minutes on 1 core
	qsub_file.write('#PBS -l feature=gbe\n') # need to find out what this line does
	qsub_file.write('#PBS -j oe\n') # this joins the input and output file into one
	qsub_file.write('#PBS -o %s/animat_%s/qsub_output_%d.txt\n\n' % (current_dir, current_time, animat_id)) # this sends the output file to the specified directory with the specified name
	qsub_file.write('module load NumPy >& /dev/null\n') # load NumPy, need to figure out how to get output from this line to not print out as it is useless output
	qsub_file.write('module load SciPy >& /dev/null\n\n') # loads SciPy, same as above
	qsub_file.write('python %s/simulate_function.py %s %s %d %d\n' % (current_dir, current_time, current_dir, animat_id, simLength)) # calls simulate_function file with the given command line arguments
	qsub_file.close # closes the file
	qsub_file.flush() # flushes writing to the file from internal buffer to the disk. this line is needed, without it a qsub cannot be submitted from python because the next line will submit the qsub but when it reads it, it will think there is nothing in the file because it would not have been written to the disk yet
	os.system('qsub %s/animat_%s/sim_qsubs/animat_qsub_%d.qsub' % (current_dir, current_time, animat_id)) # makes the call from the command line to submit the qsub

if __name__ == '__main__': # allows function to only be run when called as a main file, and not when it is being imported
	writeq = write_qsub(int(sys.argv[1]))
