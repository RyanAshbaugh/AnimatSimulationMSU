import pickle
import os
import time
import clusterDriver
import sys

def simulate(current_time,current_dir,animat_id,simLength):
	sim_start_time = time.time() # start timer           
	simulate_args_infile = open('%s/animat_%s/sim_args/sim_args_%d.txt' % (current_dir, current_time, animat_id), 'rb') # opens pickled simparam file
	simulate_args = pickle.load(simulate_args_infile) # loads objects
	# animat_id = simulate_args[0]
	# simparam = simulate_args[1]
	# simLength = simulate_args[2]	
	simulation_object = clusterDriver.Simulation(1,animat_id,simulate_args,simLength) # runs simulation with specs in all 5 worlds
        object_metrics = simulation_object.startSimulation(["Energy","FoodsEaten","FindsFood","NetworkDensity","FiringRate","TotalMove"]) # uses these metrics to track animats, returns the resulting metrics from the simulation run
	end_sim_time = time.time() # end sim time
	outfile_name = '%s/animat_%s/sim_results/sim_results_%d.txt' % (current_dir, current_time, animat_id) # names file for pickled results
	simulate_outfile = open(outfile_name, 'wb') # opens file for pickled results
	pickle.dump(object_metrics, simulate_outfile) # dumps results in outfile_name
	simulate_outfile.close() # closes file
	print 'Animat time: ', (end_sim_time-sim_start_time)
        print 'object metrics: ', object_metrics
	print 'simulation has run'

if __name__ == '__main__':
	# used to set variables equal to their respective command line arguments
	current_time = sys.argv[1]
	current_dir = sys.argv[2]
	animat_id_command = int(sys.argv[3])
	simLength = int(sys.argv[4])
	sim = simulate(current_time,current_dir,animat_id_command,simLength) # calls simulate function
