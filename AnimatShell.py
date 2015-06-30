# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 17:57:04 2014

@author: RJ

Base Class for Animat Object
"""

import numpy as np
import math as math
import scipy.spatial
import time
import NetworkModule
import SimParam



##################### Animat Base Class ######################################################
    ## Child Class for all Animat Types ##
class Animat():
    
    #constructor
    #  startPos : takes (x,y) coordinate for starting position
    def __init__(self,(id,origin,R_center,L_center,R_radii,L_radii)):

        self.net = NetworkModule.Network(R_center,L_center,R_radii,L_radii)
        self.net.generateNeurons()
        self.net.connectNetwork()
        self.pos = np.array([origin[0], origin[1]])
        self.id = id
        self.direc = np.pi/2
        self.Eating = False
        self.Energy = 200
        self.hungerThreshold = .75 * self.Energy
        self.count = 0  # used for print things out when testing

##################### Wheel Animat Class ######################################################
    ##Simplest Type of Animat, Conists of circular body with 2 "wheels" for movement##        
class WheelAnimat(Animat):
    
    #constructor keyword arguments
    #  origin : takes (x,y) coordinate for starting position
    #  rad : sets the radius of the animat
    #  cal : sets amt of energy in an item of food
    def __init__(self,(id,origin,R_center,L_center,R_radii,L_radii),rad=1):
        Animat.__init__(self,(id,origin,R_center,L_center,R_radii,L_radii))
        self.radius = rad
        self.motors = np.array([[0],[0]]) # how fast the motors are running ... could be running
        self.cMotionEnergy = 0.01 # coefficient to convert motion into energy expended in calories 
        self.kBasalEnergy = 0.01 # rate of burning energy 'at rest'
        self.benchmark = [] # storage for times determined by benchmark code in GUI driver 

    def runNetwork(self, t, dt):
        sTime = time.clock()
        self.net.runNetwork(t, dt)
        eTime = time.clock()
        self.benchmark.append(eTime-sTime)

    def copyDynamicState(self):
        state = []
        state.append(self.cMotionEnergy)
        state.append(self.kBasalEnergy)
        state.append(self.Energy)
        state.append(self.pos.copy())
        state.append(self.direc)
        state.append(self.Eating)
        state.append(self.net.copyDynamicState())
        state.append(self.benchmark)
        return state


    def loadDynamicState(self,state):
        self.cMotionEnergy = state[0]
        self.kBasalEnergy = state[1]
        self.Energy = state[2]
        self.pos = state[3]
        self.direc = state[4]
        self.Eating = state[5]
        self.net.loadDynamicState(state[6])
        self.benchmark = state[7]
       
    # def motorNeuronPos(self):
    #     motorL_pos = self.pos + [(math.cos(self.direc+(math.pi/2))*1.2),(math.sin(self.direc+(math.pi/2))*1.2)] # finds the position of the Left motor
    #     motorR_pos = self.pos + [(math.cos(self.direc-(math.pi/2))*1.2),(math.sin(self.direc-(math.pi/2))*1.2)] # finds the position of the right motor
    #     return motorL_pos,motorR_pos

    # called in order smell, move, eat
    def move(self, trac, t):
        # new proposed method to move the animat
        M1_sum,M2_sum = self.net.getMotorData() # sets M1_sum and M2_sum equal to the adjusted sum from getMotorData()
        motion_sum = M1_sum+M2_sum
        # print 'M1_sum: ', M1_sum, 'M2_sum: ', M2_sum
        new_theta = math.atan(-(M1_sum-M2_sum)/2.4)
        self.direc = self.direc + (new_theta/4.0)
        if not self.Eating:
            if M1_sum != 0 or M2_sum != 0:
                self.pos = self.pos + [(motion_sum)*math.cos(self.direc)*.01, (motion_sum)*math.sin(self.direc)*.01]
                self.Energy = self.Energy - (self.cMotionEnergy * motion_sum) - self.kBasalEnergy
        else:
            self.pos = self.pos
            self.Energy = self.Energy - self.kBasalEnergy






        # #set each wheel
        # self.motors[0],self.motors[1] = self.net.getMotorData()  # motors[] is an array (mutable) but getMotorData returns tuple - could change that to return array
        # if self.Eating:
        #     self.motors = np.array([[0],[0]]) # stops it when eating
        #
        # # rotate body depending on the difference (hopefully small) of two motors along direction of travel
        # # print 'self.direc1', self.direc
        # self.direc = self.direc + math.atan(trac*(self.motors[1]-self.motors[0])/self.radius)
        # self.unwind() #the angle direc could exceed 2*pi and 'wind up' ... should test if needed
        # self.determineMotion(trac) # later function computes how much animat moves ... could move inline.. trac passed in


    def smell(self, foods):
        self.count += 1
        smell_loc_A = []
        smell_str_A = []
        smell_loc_B = []
        smell_str_B = []
        for food in foods: # messy looking because animat doesn't 'know' food locations - belongs to world
            if food.getType() == "A":
                smell_loc_A.append(food.getPos())
                smell_str_A.append(food.getSmell())
            if food.getType() == "B":
                smell_loc_B.append(food.getPos())
                smell_str_B.append(food.getSmell())
        # compute strength of smells at smell sensor locations
        dir = -(self.direc - math.pi/2)   #figure out the clockwise direction of the animat
        if(dir <= 0): dir += math.pi*2    #bound direction to [0, 2*pi]
        rotMat = np.array([[np.cos(dir), -np.sin(dir)], [np.sin(dir), np.cos(dir)]])  #construct the rotation matrix

        worldPos_A = np.dot(self.net.senseNeuronLocations_A, rotMat) + self.pos           #get the world position of the sense neurons based on the position and rotation of the Animat
        worldPos_B = np.dot(self.net.senseNeuronLocations_B, rotMat) + self.pos           #get the world position of the sense neurons based on the position and rotation of the Animat

        # print 'worldPos_A', '\n', worldPos_A
        # print 'worldPos_B', '\n', worldPos_B
        # print 'smell_loc_A', smell_loc_A
        # print 'smell_loc_B', smell_loc_B
        # print 'scipy.spatial.distance.cdist(worldPos_A, smell_loc_A )', '\n', scipy.spatial.distance.cdist(worldPos_A, smell_loc_A )
        # print 'scipy.spatial.distance.cdist(worldPos_B, smell_loc_B )', '\n', scipy.spatial.distance.cdist(worldPos_B, smell_loc_B )

        #built-in!
        total_smell_A = self.net.sensitivity_A * np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_A, smell_loc_A ), 0, 3),axis=1)  #figures
        #  out
        # the total smell strength based on the distances (gaussian distribution)
        total_smell_B = self.net.sensitivity_B * np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_B, smell_loc_B ), 0, 3),axis=1)  #figures
        #  out
        # the total smell strength based on the distances (gaussian distribution)

        # print 'total_smell_A', '\n', total_smell_A
        # print 'total_smell_B', '\n', total_smell_B

        # total_smell_A = total_smell_A
        # total_smell_B = (10/7)*total_smell_B

        self.net.I[self.net.senseNeurons_A] = np.minimum(np.float32(total_smell_A),np.float32(100))   #caps it at 100 .. may not be necessary
        self.net.I[self.net.senseNeurons_B] = np.minimum(np.float32(total_smell_B),np.float32(100))   #sense neuron drive based on smell

        sna = list(self.net.I[self.net.senseNeurons_A])
        # sense_Neuron_A_listf = [round(elem, 4) for elem in sense_Neuron_A_list]
        snb = list(self.net.I[self.net.senseNeurons_B])
        # sense_Neuron_B_listf = [round(elem, 4) for elem in sense_Neuron_B_list]
        np.set_printoptions(linewidth=200)
        # if self.count == 0 or self.count % 4 == 0:
        #     print 't', self.count
        #     print 'total_smell_A', '\n', total_smell_A

        # if self.count > 1000:
        #     print 'scipy.spatial.distance.cdist(worldPos_A, smell_loc_A )', '\n', scipy.spatial.distance.cdist(worldPos_A, smell_loc_A )
        #     print 'scipy.spatial.distance.cdist(worldPos_B, smell_loc_B )', '\n', scipy.spatial.distance.cdist(worldPos_B, smell_loc_B )
        #     print 'self.gaussian(scipy.spatial.distance.cdist(worldPos_A, smell_loc_A )', '\n', self.gaussian(scipy.spatial.distance.cdist(worldPos_A, smell_loc_A ), 0, 3)
        #     print 'self.gaussian(scipy.spatial.distance.cdist(worldPos_B, smell_loc_B )', '\n', self.gaussian(scipy.spatial.distance.cdist(worldPos_B, smell_loc_B ), 0, 3)
        #     print 'np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_A, smell_loc_A ), 0, 3),axis=1)', '\n', np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_A, smell_loc_A ), 0, 3),axis=1)
        #     print 'np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_B, smell_loc_B ), 0, 3),axis=1)', '\n', np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_B, smell_loc_B ), 0, 3),axis=1)
        #     print 'total_smell_A', '\n', total_smell_A
        #     print 'total_smell_B', '\n', total_smell_B, '\n'

        # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('# of times sense_A fired',': '\
        #                                                                                                  ,self.net.Afired()[0],self.net.Afired()[1],self.net.Afired()[2]\
        #                                                                                                  ,self.net.Afired()[3],self.net.Afired()[4],self.net.Afired()[5]\
        #                                                                                                  ,self.net.Afired()[6],self.net.Afired()[7],self.net.Afired()[8]\
        #                                                                                                  ,self.net.Afired()[9])
        # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('# of times sense_B fired',': '\
        #                                                                                                  ,self.net.Bfired()[0],self.net.Bfired()[1],self.net.Bfired()[2]\
        #                                                                                                  ,self.net.Bfired()[3],self.net.Bfired()[4],self.net.Bfired()[5]\
        #                                                                                                  ,self.net.Bfired()[6],self.net.Bfired()[7],self.net.Bfired()[8]\
        #                                                                                                  ,self.net.Bfired()[9])

        # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.net.I[self.net.senseNeurons_A]',': '\
        #                                                                                                  ,sna[0],sna[1],sna[2],sna[3],sna[4],sna[5],sna[6],sna[7],sna[8],sna[9])
        # #     print 'sense A fired', '\n', self.net.Afired()
        # #     print 'total_smell_B', '\n', total_smell_B
        #
        # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.net.I[self.net.senseNeurons_B]',': '\
        #                                                                                                  ,snb[0],snb[1],snb[2],snb[3],snb[4],snb[5],snb[6],snb[7],snb[8],snb[9])

        #     print 'sense B fired', '\n', self.net.Bfired(), '\n'
        # self.count += 1


    def gaussian(self, x, mu, sig):
         # print '(-1 * (x - mu)**2 / (2 * sig**2))', '\n', (-1 * (x - mu)**2 / (2 * sig**2))
         # print 'self.gaussian', '\n', np.exp(-1 * (x - mu)**2 / (2 * sig**2))
         return np.exp(-1 * (x - mu)**2 / (2 * sig**2))

    # direction and traction determine motion -- maybe should check self.direc before calling
    def unwind(self):
        if self.direc > math.pi + .5:
            self.direc = self.direc - 2*math.pi
        if self.direc < -1*math.pi -.5:
            self.direc = self.direc + 2*math.pi
        
    # direction, motor neuron activity and traction determine motion ... should fold into move() method
    # def determineMotion(self,trac):
    #     self.posInc = trac * np.mean(self.motors) * np.array([np.cos(self.direc), np.sin(self.direc)])
    #     np.set_printoptions(linewidth= 100)
    #     # if self.posInc[0] >0 or self.posInc[1] > 0: print 'self.direc',self.direc,'\n','np.array([np.cos(self.direc), np.sin(self.direc)])',\
    #     #     np.array([np.cos(self.direc), np.sin(self.direc)]),'\n','self.motors',self.motors,'\n', 'np.mean(self.motors)', np.mean(self.motors),'\n',\
    #     #     'self.posInc', self.posInc,'\n','\n','\n'
    #     self.pos = self.pos + self.posInc
        
    # 'Eat' if at food    
    def eat(self, foods):
        possibleFoods = []
        for i,food in enumerate(foods): # could pass in only at one possible food
            x1,y1 = self.pos
            x2,y2 = food.getPos()
            dist = np.sqrt(np.square(np.abs(x2-x1))+np.square(np.abs(y2-y1)))
            if((dist < 0.5) and (food.getAmount() > 0)):
                possibleFoods.append(i)

        #print(whichFoods.size)
        if len(possibleFoods) > 0:
            toEat = possibleFoods[0] #pick first food in list, change maybe to whichever is closer?
            self.Eating = 1
            self.Energy += foods[toEat].getCalories()  # amount set in Stimuli class
            foods[toEat].decrAmt() # set in Stimuli class
        else:
            self.Eating = 0 # allow to move if not near food
        #check if hungry ... maybe should check before starting to eat
        if self.Energy <= self.hungerThreshold: # right now this just stimulates activity in network ... SHOULD PUT IN NETWORK
            self.net.I[self.net.hungerNeurons] = 105  # brings it suddenly from -65 (rest) to 30 = 95 + 10 = 105to ensure firing
        return foods

    def getStats(self): # for GUIDriver's animatStatWindow method; this is not used for evolution
        #stat list = Type,Energy,
        stats = ["Wheel Animat"]
        stats.append(str(self.Energy))
        stats.append(str(self.cMotionEnergy))
        stats.append(str(self.kBasalEnergy))
        #add function call to network to get neuron stats
        return stats

    def calcBenchmark(self,bufferedTime,runTime): # used in GUIDriver to track 
        log = open("Benchmarks.txt","w")
        log.write("Benchmark Log\n")
        neuronNums = self.net.getNeuronNums()
        log.write("Number of Sensory Neurons: " + str(neuronNums[0]) + "\n")
        log.write("Number of Excitatory Neurons: " + str(neuronNums[1]) + "\n")
        log.write("Number of Inhibitory Neurons: " + str(neuronNums[2]) + "\n")
        log.write("Number of Motor Neurons: " + str(neuronNums[3]) + "\n")
        #print self.benchmark
        log.write("Buffered Time: " + str(bufferedTime*.001) + "s" + " completed in " + str(runTime) + "s\n")
        avg = math.fsum(self.benchmark)/(float)(len(self.benchmark))
        log.write("\nAverage Run Time: " + str(avg))
        log.close()
        self.net.calcBenchmark()
