__author__ = 'RJ...and pals'

import re
import operator
import math
import numpy as np
import SimulationEngine
import SimParam
import random
import clusterDriver
import time
import os
import sys
import pickle
import animat_qsub_writer
import simulate_function
import subprocess

class EvoQsubDriver():

    def __init__(self):
	SimulationComplete = False
	self.worlds = [] # initialize empty world list
        # Set up worlds
        fLocs1 = [(2,0),(-2,0),(0,2),(0,-2),(0,3),(0,-3),(3,0),(-3,0),(4,0),(-4,0),(0,4),(0,-4),(0,7),(7,0),(-7,0)]
        fLocs2 = [(1,1),(2,2),(3,3),(4,4),(3,5),(2,6),(1,7),(0,8),(-2,6),(-4,4),(-6,2),(-8,0),(-5,0),(-2,-3),(-5,-5)]
        fLocs3 = [(-2,2),(-1,0),(1,0),(-1,0),(2,-2),(3,5),(-5,5),(-8,8),(10,10),(-10,10),(10,-10),(0,-1),(0,-2),(0,-3),(0,-4)]
        fLocs4 = [(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(20)]
        fLocs5 = [(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(20)]
        self.worlds.append([1,15,20,fLocs1])
        self.worlds.append([1,15,20,fLocs2])
        self.worlds.append([1,15,20,fLocs3])
        self.worlds.append([1,20,20,fLocs4])
        self.worlds.append([1,20,20,fLocs5])
        self.animats = []
	self.genData = []
	self.results = []
	self.origin = (0,0) # starting position
        self.IDcntr = 1	# keeps track so each animat gets unique id number
	self.gen_counter = 1

        #parameters
        self.sP = SimParam.SimParam()
        self.sP.setWorld(1,self.worlds[0][0],self.worlds[0][1],self.worlds[0][2],self.worlds[0][3])   #change first index to change default world
        self.sP.setWorld(2,self.worlds[1][0],self.worlds[1][1],self.worlds[1][2],self.worlds[1][3])
        self.sP.setWorld(3,self.worlds[2][0],self.worlds[2][1],self.worlds[2][2],self.worlds[2][3])
        self.sP.setWorld(4,self.worlds[3][0],self.worlds[3][1],self.worlds[3][2],self.worlds[3][3])
        self.sP.setWorld(5,self.worlds[4][0],self.worlds[4][1],self.worlds[4][2],self.worlds[4][3])
        self.sP.setAnimParams(1,1,(0,0))

	self.toTrack = ["Energy","FoodsEaten","FindsFood","NetworkDensity","FiringRate","TotalMove"]  #names of metrics to track - keys to dictionary

	try:
	    self.simLength = int(sys.argv[1]) # used to allow simLength specification from command line
	except IndexError:
	    self.simLength = 5000 # default if none given
	try:
            number_of_gens = int(sys.argv[2]) # used to allow specification for the number of generations from command line
        except IndexError:
            number_of_gens = 10 # default if none given
	try:
            self.gen_size = int(sys.argv[3]) # used to allow generation size specification for number of animats in generations after the first gen from command line
        except IndexError:
            self.gen_size = 100 # default if none given
	try:
            first_gen_size = int(sys.argv[4]) # used to allow  specification for the number of animats from command line
        except IndexError:
            first_gen_size = 200 # default if none given
	# print 'simLength', simLength

	results = [] # initialized empty results
	self.generateParams(self.animats,first_gen_size) # creates the SimParam objects used for animats
        initial_time = time.time() # starts timer
	print 'first_gen_size', first_gen_size
	self.current_dir = str(os.getcwd()) # gets current direcetory to be passed to animat_qsub_writer.py and simulate_function.py so they can find appropriate files
	self.current_time = time.strftime('%m-%d_%H:%M') # this is also passed to both animat_qsub_writer.py and simulate_function.py so they can find appropriate files in the form month-day_hour(24):minute
	print 'current_time: ', self.current_time
	# makes the neccessary directories
	os.mkdir('%s/animat_%s' % (self.current_dir, self.current_time)) # directory for entire simulation
	os.mkdir('%s/animat_%s/sim_args' % (self.current_dir, self.current_time)) # directory for simparam objects
	os.mkdir('%s/animat_%s/sim_qsubs' % (self.current_dir, self.current_time)) # directory for animat qsubs
	os.mkdir('%s/animat_%s/sim_results' % (self.current_dir, self.current_time)) # directory for animat results
	for x in range(1,first_gen_size+1): # goes through all of the animats
		simulate_args = self.animats[x-1] # finds the simparam object for the animat id
		simulate_args_outfile = open('%s/animat_%s/sim_args/sim_args_%d.txt' % (self.current_dir, self.current_time, x),'wb') # create file to pickle.dump 
        	pickle.dump(simulate_args, simulate_args_outfile) # dump simparam object in file
        	simulate_args_outfile.close() # closes file
		results = animat_qsub_writer.write_qsub(x,self.current_time,self.current_dir,self.simLength) # calls animat_qsub_writer for all animats
	# print 'EvoQsubDriver complete'
        # print 'Entire Simulation Time: ', sim_time
	while not SimulationComplete: # while the simulation is not yet completed
	    current_sim_results = self.dir_count('%s/animat_%s/sim_results' % (self.current_dir, self.current_time))
	    total_sims_completed = current_sim_results[0] # all animats completed regardless of generation
	    print '\ntotal_sims_completed: ', total_sims_completed
	    if self.gen_counter == 1:
		sims_completed = total_sims_completed
		gen_percent = float(sims_completed)/float(first_gen_size)
	    else:
		#print 'gen_counter != 1'
		#print 'total_sims_completed: ', total_sims_completed
		#print 'first_gen_size: ', first_gen_size
		#print 'float(self.gen_size): ', float(self.gen_size)
		#print 'self.gen_counter: ', self.gen_counter
		if total_sims_completed - first_gen_size < 0:
		    temp_first_gen = 0
		else:
		    temp_first_gen = total_sims_completed - first_gen_size
		sims_completed = temp_first_gen -(self.gen_size*(self.gen_counter-2)) # gives the number of animats completed within a generation
		gen_percent = float(sims_completed)/float(self.gen_size) # percentage of the generation completed
		#print 'float(sims_completed): ', float(sims_completed)
	    print '%d gen_percent: ' % self.gen_counter, gen_percent*100, '%'
	    time.sleep(30) # makes loop essentially run every 30 seconds
	    if gen_percent >= .8:
		sims_file_list = current_sim_results[1] # list of all completed animat results	
		for result in sims_file_list:
		    result_id = re.findall('\d+',result) # finds the id of the specific result file
		    temp_results_id = [self.results[i][0] for i in range(len(self.results))]
		    if int(result_id[0]) not in temp_results_id: # checks whether already in self.results or not
			results_file = open('%s/animat_%s/sim_results/%s' % (self.current_dir, self.current_time, result), 'rb')
		    	results_list = pickle.load(results_file)
		    	self.results.append(results_list)
		self.rankAnimats()
		self.run()
		gen_percent = 0
		self.gen_counter += 1
	    if self.gen_counter == number_of_gens: # checks to see if on last generation
                while gen_percent < .8:
		    time.sleep(30)
		    current_sim_results = self.dir_count('%s/animat_%s/sim_results' % (self.current_dir, self.current_time))
            	    total_sims_completed = current_sim_results[0] # all animats completed regardless of generation
            	    print '\ntotal_sims_completed: ', total_sims_completed
		    temp_first_gen = total_sims_completed - first_gen_size
                    sims_completed = temp_first_gen -(self.gen_size*(self.gen_counter-2)) # gives the number of animats completed within a generation
		    gen_percent = float(sims_completed)/float(self.gen_size)
		    print '%d gen_percent: ' % self.gen_counter, gen_percent*100, '%'
		SimulationComplete = True
		self.rankAnimats()
		end_time = time.time() # end time
		sim_time = int(end_time-initial_time)
                sim_time_hms = time.strftime("%H:%M:%S", time.gmtime(sim_time))
	print 'Simulation has completed successfully in ', sim_time_hms, ' seconds'



    def dir_count(self,dir):  # counts the number of files in directory	
	os.chdir(dir)
	files_str = subprocess.check_output(['ls','-1'])
	os.chdir(self.current_dir)
	files_list = [word for word in files_str.split()]
	num_files = len(files_list)	
	return [num_files,files_list]


    def generateParams(self,list,size,R_center=-1,L_center=-1,R_radii=-1,L_radii=-1): # generates parameters
        print "Generating Animats\n"
        for i in xrange(size): # does this for as many animats as there are, size=num_animats
            sP = SimParam.SimParam()
	    # sets all the worlds
            for j,world in enumerate(self.worlds): sP.setWorld(j+1,world[0],world[1],world[2],world[3])
            sP.setWorld(4,1,15,20,[(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(15)])
            sP.setWorld(5,1,15,20,[(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(15)])
            sP.setAnimParams(1,self.IDcntr,self.origin)
            if R_center == -1: # if R_center is currently not defined then run code below to create it
		# sets R and L center to equal random number between -1 and 1
                self.R_center = [[random.randrange(-1000,1001,1)/1000,random.randrange(-1000,1001,1)/1000] for x in range(5)]
                self.L_center = [[random.randrange(-1000,1001,1)/1000,random.randrange(-1000,1001,1)/1000] for x in range(5)]
		self.R_radii = [1.0,1.0,1.0,1.0,.5]
		self.L_radii = [1.0,1.0,.15,.15,1]	
		sP.setR_center(1, self.R_center)
		sP.setL_center(1, self.L_center)	
		sP.setR_radii(1, self.R_radii)
		sP.setL_radii(1, self.L_radii)

            else: # if these values are already defined, then set them equal to themselves               
		sP.setR_center(1, R_center)
                sP.setL_center(1, L_center)
                sP.setR_radii(1, R_radii)
                sP.setL_radii(1, L_radii)
      
            list.append(sP) # append simparam objects to self.animats
            self.IDcntr += 1 # increase id number

    # Sorts list of animats based on results from simulations
    def rankAnimats(self):
        print "Ranking Animats"
        genData = []
        scores = {}    #dictionary of scores with ids as keys
        #calculate score based on each metric
        mean_file = open('%s/animat_%s/gen_means.txt' % (self.current_dir, self.current_time), 'a')
	for metric in self.toTrack:
            #build list of all results for this metric
            results = [(id,result[metric]) for id,result in self.results]
            #use simulation results to calculate max,min,mean,std so that evo performance can be tracked
            maxResult = max(results, key= lambda x: x[1])[1]
            minResult = min(results, key= lambda x: x[1])[1]
            mean = np.mean(results,axis=0)[1]
            sd = np.std(results,axis=0)[1]
	    rank_results = '%d %s: [maxResult: %d, minResult: %d, mean: %d, sd: %d]\n' % (self.gen_counter,metric,int(maxResult),int(minResult),int(mean),int(sd))
	    mean_file.write(rank_results)
	    for id,result in results:
                try:
                    if metric == "TotalMove": pass               #Total movement is recorded but not used to rank animats
                    elif (metric == "NetworkDensity") or (metric == "FiringRate"):
                        scores[id] += ((result-mean)/sd)*(-1.0)  #These metrics should dock points
                        #print "NetworkDensity or FiringRate z-scor: ",scores[id],"\n"
                    else:
                        scores[id] += (result-mean)/sd           #score is sum of z scores for all metrics
                        #print "else: ",scores[id], "\n"
                except KeyError:                                 #KeyError when score updated for first time, so catch and set
                    if (metric == "NetworkDensity") or (metric == "FiringRate"):
                        scores[id] = ((result-mean)/sd)*(-1.0)   #These metrics should dock points
                        #print"keyError network density or firingrate:  ", scores[id],"\n"
                    else:
                        scores[id] = (result-mean)/sd            #score is sum of z scores for all metrics
                        #print "else: ",scores[id],"\n"
            genData.append((metric,maxResult,minResult,mean,sd,scores))
	mean_file.close
	#print 'old id order: ',[sP.getID(1) for sP in self.animats]
	self.sorted_animats = self.sortByScores(scores) # sorts animats based scores
        self.genData.append(genData)



    #takes dictionary of scores and sorts animat list accordingly
    def sortByScores(self,scores):
        idOrder = sorted(scores.items(), key=operator.itemgetter(1)) #return ids of animats in sorted order
	newAnim = []
        for id in idOrder:
            for sP in self.animats:
                if sP.getID(1) == id[0]:
                    newAnim.append(sP)
                    break
        newAnim.reverse()	
	return newAnim


    #takes in list of animats, then returns list of mutated animats
    def mutate(self,animats):
        print "Mutating"
        #Random mutation for first half
        randMut = []
	randMut_before = []
        recomb_list = []

	# splices top animats into every other one for the 2 mutations
	for i in xrange(self.gen_size):
	    if i %2 == 0:
		randMut_before.append(animats[i])
	    else:
		recomb_list.append(animats[i])

	# random mutation selection
	for i in xrange(len(randMut_before)):
	    # either increment or decrement
	    choice = random.choice((-1,1))
	    # how much to change the param
	    randMut_change = .1 * choice
	    randMutR_center = randMut_before[i].getR_center(1)
	    randMutL_center = randMut_before[i].getL_center(1)
	    randMutR_radii = randMut_before[i].getR_radii(1)
	    randMutL_radii = randMut_before[i].getL_radii(1)
	    # how to randomly decide which param gets changed
	    selection = random.randint(0,9)
	    if selection < 5:
		randMutR_center[selection][0] += randMut_change
		randMutR_center[selection][1] += randMut_change
	    else:
		randMutL_center[selection-5][0] += randMut_change
		randMutL_center[selection-5][1] += randMut_change
       	    self.generateParams(randMut,1,randMutR_center,randMutL_center,randMutR_radii,randMutL_radii)
        #Random recombination for last half
        #Combines aa,bb
        recomb = []
        for i in xrange(len(recomb_list)):
            r1 = random.randint(0,len(recomb_list)-1)
            r2 = random.randint(0,len(recomb_list)-1)
            newR_center = recomb_list[r1].getR_center(1)
            newR_radii = recomb_list[r1].getR_radii(1)
            newL_center = recomb_list[r2].getL_center(1)
            newL_radii = recomb_list[r2].getL_radii(1)

            self.generateParams(recomb,1,newR_center,newL_center,newR_radii,newL_radii)
        return randMut+recomb


    def run(self):
	self.new_animats = self.mutate(self.sorted_animats[0:self.gen_size]) # list containing mutated simparam objects
	print 'starting new gen'
	gen_animats = [sP.getID(1) for sP in self.new_animats] # ids of all the animats in current generation 
	for x in gen_animats: # goes through all of the animats in a generation
            y = x % self.gen_size 
	    simulate_args = self.new_animats[y-1] # finds the simparam object for the animat id
            simulate_args_outfile = open('%s/animat_%s/sim_args/sim_args_%d.txt' % (self.current_dir, self.current_time, x),'wb') # create file to pickle.dump 
            pickle.dump(simulate_args, simulate_args_outfile) # dump simparam object in file
            simulate_args_outfile.close() # closes file
            results = animat_qsub_writer.write_qsub(x,self.current_time,self.current_dir,self.simLength) # calls animat_qsub_writer for all animats	

evoqsubdriver = EvoQsubDriver() # call EvoQsubDriver
