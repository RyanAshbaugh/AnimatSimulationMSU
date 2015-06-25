
'''
Network Module
Simulates brain, contains all neurons




'''

from NeuronModule import InhibitoryNeuron
from NeuronModule import ExcitatoryNeuron
from NeuronModule import MotorNeuron
from NeuronModule import SensoryNeuron_A
from NeuronModule import SensoryNeuron_B
from NeuronModule import HungerNeuron
import math
import numpy as np
import random
import SimParam

class Network:

    #kwargs used for evo driver
     def __init__(self,x0,y0,sigma): # mixture of neuron parameters and initializing network numbers
         #some constants/tracking numbers
         self.FIRED_VALUE = 30 # mV
         self.DT = 1 # ms
         self.numExcitatory = 0
         self.numInhibitory = 0
         self.numMotor = 0
         self.numSensory_A = 0
         self.numSensory_B = 0
         self.numHunger = 0
         self.totalNum = 0
         self.voltIncr = 5.0     #multiplier for S matrix connection weights
         self.kSynapseDecay = .7 # Synaptic conductance after 1 ms
         self.L = 3
         self.K = 5
         self.sense_B_fired = [0 for i in range(10)]
         self.sense_A_fired = [0 for i in range(10)]
         self.M1_fp = [0,0,0,0,0,0,0,0]
         self.M2_fp = [0,0,0,0,0,0,0,0]
         self.M1adjusted = [0,0,0,0,0,0,0,0]
         self.M2adjusted = [0,0,0,0,0,0,0,0]

         if x0 == None: # if no values are passed in (unusual) then set up some random - may want to remove this
             self.x0 = [[np.random.random_sample()*3.01 - 1.5 for x in xrange(self.K)] for x in xrange(self.L)]
             self.y0 = [[np.random.random_sample()*3.01 - 1.5 for x in xrange(self.K)] for x in xrange(self.L)]
             self.sigma = [[np.random.exponential() for x in xrange(self.K)] for x in xrange(self.L)]
             # self.sigma = [[1.0, 1.0, 0.0, 1.0, 1.0], [1.0, 1.0, 1.5, 0.0, 0.0]]
             # self.x0 = [[-1.0, 1.0, 0.0, 0.7, -0.7], [-1.0, 1.0, 0.0, 0.0, 0.0]]
             # self.y0 = [[1.0, 1.0, 0.0, -0.7, -0.7], [-1.0, -1.0, -1.0, 0.0, 0.0]]
         else:
             self.x0 = x0
             self.y0 = y0
             self.sigma = sigma


         #Izhikevich Variables ... do we need 32-bit numbers? try np.float16?
         self.v = np.array([], dtype = np.float32) # voltage proxy .
         self.a = np.array([], dtype = np.float32)
         self.b = np.array([], dtype = np.float32)
         self.c = np.array([], dtype = np.float32)
         self.d = np.array([], dtype = np.float32)
         self.u = self.b*self.v                 # Set initial values of u at ceiling
         self.S = np.array([[]], dtype = np.float32) # row-major order; S(2,3) is weight from #2 to #3


         #'Shadow' Variables
         self.fireTogetherCount = np.array([], ndmin = 2, dtype = np.float)
         self.firingCount = np.array([])
         self.recentlyFired = np.array([], dtype = np.float32)
         self.justFired = np.array([], dtype = np.int_, ndmin = 2) # this is int64 ... remove _ to make int8 or int16

         #'Shadow' Variable assistants
         #self.fireTogetherWindow = np.array([])
         self.firingCount_decay = 0.01
         self.fireTogetherCount_decay = 0.98

         #other neuron mappings
         self._neurons = []
         self.inhibitoryNeurons = np.array([], dtype=np.int_)
         self.excitatoryNeurons = np.array([], dtype=np.int_)
         self.motorNeurons = np.array([], dtype=np.int_)
         self.hungerNeurons = np.array([],dtype=np.int_)

         #These will be dictionaries of Lists eventually for different types of sensory neurons!
         self.senseNeurons_A = np.array([], dtype=np.int_) # holds neuron objects
         self.senseNeuronLocations_A = np.array([],ndmin=2) # holds locations on animat
         self.sensitivity_A = np.array([], ndmin = 2) # sensitivity to smell A: hard-coded to 
         self.senseNeurons_B = np.array([], dtype=np.int_) 
         self.senseNeuronLocations_B = np.array([],ndmin=2)
         self.sensitivity_B = np.array([], ndmin = 2)


     #maybe add to OO... then let the network rebuild..?
     def add_neuron(self, type, pos, sensitivity = 1): # change 'type' to 'n_type'
         if type == 'inhibitory':
             loc = self.numInhibitory
             self._neurons.insert(loc, InhibitoryNeuron(pos[0], pos[1], 0)) # insert because mutable
             self.inhibitoryNeurons = np.append(self.inhibitoryNeurons, loc) # assigned because np.append doesn't alter its argument
             self.a = np.insert(self.a, loc, np.float32(0.02))
             self.b = np.insert(self.b, loc, np.float32(0.2))
             self.c = np.insert(self.c, loc, np.float32(-65))
             self.d = np.insert(self.d, loc, np.float32(8))
             self.v = np.insert(self.v, loc, np.float32(-65))
             self.numInhibitory += 1

             self.excitatoryNeurons += 1 # bumps up all indices - to keep track of locations of neuron types for GUIdriver etc
             self.motorNeurons += 1
             self.senseNeurons_A += 1
             self.senseNeurons_B += 1
             self.hungerNeurons += 1

         if type == 'excitatory':
             loc = self.numExcitatory + self.numInhibitory
             self._neurons.insert(loc, ExcitatoryNeuron(pos[0], pos[1], 0))
             self.excitatoryNeurons = np.append(self.excitatoryNeurons, loc)
             self.a = np.insert(self.a, loc, np.float32(0.02))
             self.b = np.insert(self.b, loc, np.float32(0.2))
             self.c = np.insert(self.c, loc, np.float32(-65))
             self.d = np.insert(self.d, loc, np.float32(8))
             self.v = np.insert(self.v, loc, np.float32(-65))
             self.numExcitatory += 1

             self.motorNeurons += 1
             self.senseNeurons_A += 1
             self.senseNeurons_B += 1
             self.hungerNeurons += 1

         if type == 'motor':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor
             self._neurons.insert(loc, MotorNeuron(pos[0], pos[1], 0))
             self.motorNeurons = np.append(self.motorNeurons, loc)
             self.a = np.insert(self.a, loc, np.float32(0.02))
             self.b = np.insert(self.b, loc, np.float32(0.2))
             self.c = np.insert(self.c, loc, np.float32(-65))
             self.d = np.insert(self.d, loc, np.float32(8))
             self.v = np.insert(self.v, loc, np.float32(-65))
             self.numMotor += 1

             self.senseNeurons_A += 1
             self.senseNeurons_B += 1
             self.hungerNeurons += 1

         if type == 'sensory_A':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor + self.numSensory_A
             self._neurons.insert(loc, SensoryNeuron_A(pos[0], pos[1], 0))
             self.senseNeurons_A = np.append(self.senseNeurons_A, loc)
             if self.numSensory_A == 0: self.senseNeuronLocations_A = np.array([pos[0],pos[1]],ndmin=2)
             else: self.senseNeuronLocations_A = np.insert(self.senseNeuronLocations_A, self.numSensory_A, np.array((pos[0], pos[1])), axis = 0)
             self.a = np.insert(self.a, loc, np.float32(0.02))
             self.b = np.insert(self.b, loc, np.float32(0.2))
             self.c = np.insert(self.c, loc, np.float32(-65))
             self.d = np.insert(self.d, loc, np.float32(8))
             self.v = np.insert(self.v, loc, np.float32(-65))
             self.sensitivity_A = np.append(self.sensitivity_A, sensitivity)
             self.numSensory_A += 1

             self.senseNeurons_B += 1
             self.hungerNeurons += 1

         if type == 'sensory_B':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor + self.numSensory_A + self.numSensory_B
             self._neurons.insert(loc, SensoryNeuron_B(pos[0], pos[1], 0))
             self.senseNeurons_B = np.append(self.senseNeurons_B, loc)
             if self.numSensory_B == 0: self.senseNeuronLocations_B = np.array([pos[0],pos[1]],ndmin=2)
             else: self.senseNeuronLocations_B = np.insert(self.senseNeuronLocations_B, self.numSensory_B, np.array((pos[0], pos[1])), axis = 0)
             self.a = np.insert(self.a, loc, np.float32(0.02))
             self.b = np.insert(self.b, loc, np.float32(0.2))
             self.c = np.insert(self.c, loc, np.float32(-65))
             self.d = np.insert(self.d, loc, np.float32(8))
             self.v = np.insert(self.v, loc, np.float32(-65))
             self.sensitivity_B = np.append(self.sensitivity_B, sensitivity)
             self.numSensory_B += 1

             self.hungerNeurons += 1

         if type == 'hunger':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor + self.numSensory_A + self.numSensory_B + self.numHunger
             self._neurons.insert(loc, HungerNeuron(pos[0], pos[1], 0))
             self.hungerNeurons = np.append(self.hungerNeurons, loc)
             self.a = np.insert(self.a, loc, np.float32(0.02))
             self.b = np.insert(self.b, loc, np.float32(0.2))
             self.c = np.insert(self.c, loc, np.float32(-65))
             self.d = np.insert(self.d, loc, np.float32(8))
             self.v = np.insert(self.v, loc, np.float32(-65))
             self.numHunger += 1

         #'Shadow' Variables
         if(self.totalNum == 0):
             self.fireTogetherCount = np.array([0], ndmin = 2, dtype = np.float32)
             self.S = np.array([0], ndmin = 2, dtype = np.float32)
             #self.justFired = np.array([0],ndmin=2)
             self.justFired = np.array([0], dtype = np.float32)
         ## NEEDS FIXING FOR HOW LOC IS DEFINED
         else:
             self.fireTogetherCount = np.insert(self.fireTogetherCount, loc, 0, axis = 0)
             self.fireTogetherCount = np.insert(self.fireTogetherCount, loc, 0, axis = 1)

             self.S = np.insert(self.S, loc, np.float32(0), axis=0)
             self.S = np.insert(self.S, loc, np.float32(0), axis=1)

             self.justFired = np.insert(self.justFired, loc, np.array([np.float32(0)]), axis = 0)

         self.firingCount = np.insert(self.firingCount, loc, 0)
         self.recentlyFired = np.insert(self.recentlyFired, loc, np.float32(0))

         self.totalNum += 1


         #'Shadow' Variable assistants
         #self.fireTogetherWindow = np.insert(self.fireTogetherWindow, loc, 1)
         #self.firingCount_decay = np.array([])
         #self.fireTogetherCount_decay = np.array([])

         self.u=self.b*self.v # should be here; makes earlier one redundant

     def generateNeurons(self):
         #Generate neurons around the circle
         for i in xrange(40): # 0 to 39
             loc = (np.cos(2*np.pi*(i+0.5)/40),np.sin(2*np.pi*(i+0.5)/40))
             if i < 20: # upper half-circle
                 if i % 2 == 0:
                     self.add_neuron("sensory_A",loc)
                 else:
                     self.add_neuron("sensory_B",loc)
             else:
                 self.add_neuron("excitatory",loc)
         #Generate hunger and motor neurons
         self.add_neuron("hunger",(0,0))
         self.add_neuron("motor",(-1.2,0))
         self.add_neuron("motor",(1.2,0))

         # print 'self.senseNeurons_A', self.senseNeurons_A
         # print 'self.senseNeurons_B', self.senseNeurons_B

     def connectNetwork(self):
         #Parameters
         A = 2.0
         B = 20.0
        
         #Set up connection variables
         #set up ligand and receptor lists for each neuron in circle based on parameters
         for index in np.hstack((self.excitatoryNeurons,self.senseNeurons_A,self.senseNeurons_B)): # make one list
            x, y = self._neurons[index].X, self._neurons[index].Y
            rr,ll = [],[]
            for i in xrange(5):
                rVal = self.sigma[0][i] - np.sqrt( np.square(x - self.x0[0][i]) + np.square(y - self.y0[0][i]))
                lVal = self.sigma[1][i] - np.sqrt( np.square(x - self.x0[1][i]) + np.square(y - self.y0[1][i]))
                if rVal < 0.0: rVal = 0.0
                if lVal < 0.0: lVal = 0.0
                rr.append(rVal)
                ll.append(lVal)
            self._neurons[index].setRL(rr,ll) # adds the vectors rr, ll to neuron using setRL method in neuronModule.py

         #Set up ligand and receptor lists for each motor neuron and hunger neuron
         for index in self.hungerNeurons:
             rr = [0 for i in xrange(5)]
             ll = [0 for i in xrange(5)]
             rr[2] = 1
             self._neurons[index].setRL(rr,ll)

         rr = [0 for i in xrange(5)]
         ll = [0 for i in xrange(5)]
         ll[3] = 1 # needs to be changed for L/R difference - CHANGED
         self._neurons[self.motorNeurons[0]].setRL(rr,ll)
         ll[3] = 0
         ll[4] = 1
         self._neurons[self.motorNeurons[1]].setRL(rr,ll)

         # for i in range(len(self._neurons)): print 'r', self._neurons[i].r, 'l', self._neurons[i].l

         #Set up connection weights
         neuronIndices = np.hstack((self.excitatoryNeurons,self.senseNeurons_A,self.senseNeurons_B,self.hungerNeurons,self.motorNeurons))
         # may be simpler to run through all indices in order, since all classes get treated equally
         for n1 in neuronIndices:
             for n2 in neuronIndices:
                 W = np.sum( np.multiply(self._neurons[n1].r, self._neurons[n2].l))
                 max_synapse_strength = 5
                 connectionWeight = max_synapse_strength*(np.exp(A* W) / (B + np.exp(A*W)))
                 ### bring in multiplier from runNetwork
                 if connectionWeight <= 1.0/4.0: connectionWeight = 0
                 self.S[n1,n2] = connectionWeight
         for i in self.senseNeurons_A:
            self.S[i][self.motorNeurons[0]]= 0
            self.S[i][self.motorNeurons[1]]= 0
         for i in self.senseNeurons_B:
            self.S[i][self.motorNeurons[0]]= 0
            self.S[i][self.motorNeurons[1]]= 0
         self.S[self.motorNeurons[0]]= [0 for i in range(43)]
         self.S[self.motorNeurons[1]]= [0 for i in range(43)]

         # print self.S
         # initialize I
         self.I = 2*np.ones( (self.totalNum), dtype = np.float32 ) # should be in initialization
         # np.set_printoptions(edgeitems=100)
         # print self.S[0]

     def copyDynamicState(self): # copies all data for simulation engine 
         state = []
         state.append(self.a.copy())
         state.append(self.b.copy())
         state.append(self.c.copy())
         state.append(self.d.copy())
         state.append(self.u.copy())
         state.append(self.v.copy())
         state.append(self.S.copy())
         try:
             state.append(self.I.copy())
         except AttributeError:
             pass #means its first frame and I has not been set yet ... should be fixed if Initialize() method is made
         return state

     def loadDynamicState(self, state): # for GUI: after pause, allows one to load back previously copied state
         self.a = state[0]
         self.b = state[1]
         self.c = state[2]
         self.d = state[3]
         self.u = state[4]
         self.v = state[5]
         self.S = state[6]
         try:
            self.I = state[7]
         except IndexError:
             pass #not set yet


     def get_neurons_firing(self): # used in GUI driver to change colors
         return (self.v >= self.FIRED_VALUE).nonzero()

     def getNeurons(self):  #populates neuron objects with vectorized data so that upper levels (e.g. GUIDriver) can use them in an OO manner
         for i in range(0, len(self._neurons)):
             self._neurons[i].index = i
             self._neurons[i].a = self.a[i]
             self._neurons[i].b = self.b[i]
             self._neurons[i].membranePotential = self.v[i]
             self._neurons[i].c = self.c[i]
             self._neurons[i].d = self.d[i]
             self._neurons[i].u = self.u[i]

         return self._neurons


     def runNetwork(self,t,dt): # runs Izhikevich model code

         # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.v[self.senseNeurons_A1]',': '\
         #                                                                                                            ,self.v[self.senseNeurons_A][0],self.v[self.senseNeurons_A][1],self.v[self.senseNeurons_A][2]\
         #                                                                                                            ,self.v[self.senseNeurons_A][3],self.v[self.senseNeurons_A][4],self.v[self.senseNeurons_A][5]\
         #                                                                                                            ,self.v[self.senseNeurons_A][6],self.v[self.senseNeurons_A][7],self.v[self.senseNeurons_A][8]\
         #                                                                                                            ,self.v[self.senseNeurons_A][9])
         # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.v[self.senseNeurons_B1]',': '\
         #                                                                                                            ,self.v[self.senseNeurons_B][0],self.v[self.senseNeurons_B][1],self.v[self.senseNeurons_B][2]\
         #                                                                                                            ,self.v[self.senseNeurons_B][3],self.v[self.senseNeurons_B][4],self.v[self.senseNeurons_B][5]\
         #                                                                                                            ,self.v[self.senseNeurons_B][6],self.v[self.senseNeurons_B][7],self.v[self.senseNeurons_B][8]\
         #                                                                                                            ,self.v[self.senseNeurons_B][9])

         self.fired = (self.v >= 30).nonzero()[0] # .nonzero() returns indices from 1/0 (T/F) of v >= 30
         self.recentlyFired[self.fired] = 20

         for i in range(22,32):
             if self.v[i] >= 30:
                self.sense_A_fired[i-22] += 1
         for i in range(32,42):
             if self.v[i] >= 30:
                self.sense_B_fired[i-32] += 1

         self.v[self.fired] = self.c[self.fired]
         self.u[self.fired] = self.u[self.fired] + self.d[self.fired]
         # newI = np.zeros(43,dtype=np.float32)
         # for i in self.fired:
         #     for j in self.S[i]:
         #         newI[j] += (self.S[i][j]*self.voltIncr)
         newI = np.sum(self.S[self.fired],axis=0) * self.voltIncr
         # np.set_printoptions(edgeitems=100)
         # print self.S
         # print np.sum(self.S[self.fired],axis=0)
         # print 'np.sum(self.S[self.senseNeurons_A],axis=0): ', np.sum(self.S[self.senseNeurons_A],axis=0)
         # print 'np.sum(self.S[self.senseNeurons_A],axis=0)*self.voltIncr: ', (np.sum(self.S[self.senseNeurons_A],axis=0)*self.voltIncr)
         # print 'np.sum(self.S[self.senseNeurons_B],axis=0): ', np.sum(self.S[self.senseNeurons_B],axis=0)
         # print 'np.sum(self.S[self.senseNeurons_B],axis=0)*self.voltIncr: ', (np.sum(self.S[self.senseNeurons_B],axis=0)*self.voltIncr)
         print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('newI[self.senseNeurons_A]',': '\
                                                                                                                    ,newI[self.senseNeurons_A][0],newI[self.senseNeurons_A][1],newI[self.senseNeurons_A][2]\
                                                                                                                    ,newI[self.senseNeurons_A][3],newI[self.senseNeurons_A][4],newI[self.senseNeurons_A][5]\
                                                                                                                    ,newI[self.senseNeurons_A][6],newI[self.senseNeurons_A][7],newI[self.senseNeurons_A][8]\
                                                                                                                    ,newI[self.senseNeurons_A][9])
         print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('newI[self.senseNeurons_B]',': '\
                                                                                                                    ,newI[self.senseNeurons_B][0],newI[self.senseNeurons_B][1],newI[self.senseNeurons_B][2]\
                                                                                                                    ,newI[self.senseNeurons_B][3],newI[self.senseNeurons_B][4],newI[self.senseNeurons_B][5]\
                                                                                                                    ,newI[self.senseNeurons_B][6],newI[self.senseNeurons_B][7],newI[self.senseNeurons_B][8]\
                                                                                                                    ,newI[self.senseNeurons_B][9])
         # tempNewIlista = (newI[self.senseNeurons_A] >= 20).nonzero()[0]
         # tempNewIlistb = (newI[self.senseNeurons_B] >= 20).nonzero()[0]
         # if len(tempNewIlista)>0 or len(tempNewIlistb)>0:
            # print 'self.S[self.senseNeurons_A]: ', self.S[self.senseNeurons_A]
            # print 'self.S[self.senseNeurons_B]: ', self.S[self.senseNeurons_B]

         self.I = self.kSynapseDecay*self.I + newI

         self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)
         self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)
         self.cap_v = (self.v >= 50).nonzero()[0]
         self.v[self.cap_v] = 50

         self.u=self.u+self.a*(self.b*self.v - self.u)


     def Bfired(self):
         return self.sense_B_fired
     def Afired(self):
         return self.sense_A_fired


     #uses voltages of firing motorNeurons to return new motor data to AnimatShell to determine wheel (called in animatMovement)
     # NEEDS attention to operate smoothly
     def getMotorData(self):

         newM1 = 0 if(self.v[self.motorNeurons[0]] <= 30) else 1    #(self.v[self.motorNeurons[0]]) # returns 0 if motorNeuron doesn't fire and 1 if it does
         newM2 = 0 if(self.v[self.motorNeurons[1]] <= 30) else 1    #(self.v[self.motorNeurons[1]]) # returns 0 if motorNeuron doesn't fire and 1 if it does

         self.M1_fp= self.M1_fp[:7] # firing pattern of motor neuron 1, M1_fp[0] is the most recent 0/1 and M1_fp[3] gets left, only last three 0/1's are stored at this point
         self.M1_fp.insert(0,newM1) # wether or not the motor neuron fired this run through network is inserted into M1_fp[0] here, so M1_fp[0] is always the latest 0/1
         self.M2_fp= self.M2_fp[:7] # firing pattern of motor neuron 2, M2_fp[0] is the most recent 0/1 and M2_fp[3] gets left, only last three 0/1's are stored at this point
         self.M2_fp.insert(0,newM2) # wether or not the motor neuron fired this run through network is inserted into M2_fp[0] here, so M2_fp[0] is always the latest 0/1
         for i in range(8): # for all four indices in M_fp lists
             self.M1adjusted[i] = self.M1_fp[i]*(.8**i) # gets the adjusted weight of the neuron having fired in the past, 20% reduction for each run in the past
             self.M2adjusted[i] = self.M2_fp[i]*(.8**i) # gets the adjusted weight of the neuron having fired in the past, 20% reduction for each run in the past
         if self.M1adjusted != self.M2adjusted:
            print 'sums: ',sum(self.M1adjusted),sum(self.M2adjusted)


         print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.I[self.senseNeurons_A]',': '\
                                                                                                                    ,self.I[self.senseNeurons_A][0],self.I[self.senseNeurons_A][1],self.I[self.senseNeurons_A][2]\
                                                                                                                    ,self.I[self.senseNeurons_A][3],self.I[self.senseNeurons_A][4],self.I[self.senseNeurons_A][5]\
                                                                                                                    ,self.I[self.senseNeurons_A][6],self.I[self.senseNeurons_A][7],self.I[self.senseNeurons_A][8]\
                                                                                                                    ,self.I[self.senseNeurons_A][9])
         print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.I[self.senseNeurons_B]',': '\
                                                                                                                    ,self.I[self.senseNeurons_B][0],self.I[self.senseNeurons_B][1],self.I[self.senseNeurons_B][2]\
                                                                                                                    ,self.I[self.senseNeurons_B][3],self.I[self.senseNeurons_B][4],self.I[self.senseNeurons_B][5]\
                                                                                                                    ,self.I[self.senseNeurons_B][6],self.I[self.senseNeurons_B][7],self.I[self.senseNeurons_B][8]\
                                                                                                                    ,self.I[self.senseNeurons_B][9])

         print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.v[self.senseNeurons_A]',': '\
                                                                                                                    ,self.v[self.senseNeurons_A][0],self.v[self.senseNeurons_A][1],self.v[self.senseNeurons_A][2]\
                                                                                                                    ,self.v[self.senseNeurons_A][3],self.v[self.senseNeurons_A][4],self.v[self.senseNeurons_A][5]\
                                                                                                                    ,self.v[self.senseNeurons_A][6],self.v[self.senseNeurons_A][7],self.v[self.senseNeurons_A][8]\
                                                                                                                    ,self.v[self.senseNeurons_A][9])
         print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.v[self.senseNeurons_B]',': '\
                                                                                                                    ,self.v[self.senseNeurons_B][0],self.v[self.senseNeurons_B][1],self.v[self.senseNeurons_B][2]\
                                                                                                                    ,self.v[self.senseNeurons_B][3],self.v[self.senseNeurons_B][4],self.v[self.senseNeurons_B][5]\
                                                                                                                    ,self.v[self.senseNeurons_B][6],self.v[self.senseNeurons_B][7],self.v[self.senseNeurons_B][8]\
                                                                                                                    ,self.v[self.senseNeurons_B][9])
         print '{:36s}{:2s}{:12.4f}{:12.4f}'.format('self.I[self.motorNeurons]',': ', self.I[self.motorNeurons[0]],self.I[self.motorNeurons[1]])
         print '{:36s}{:2s}{:12.4f}{:12.4f}'.format('self.v[self.motorNeurons]',': ', self.v[self.motorNeurons[0]],self.v[self.motorNeurons[1]]), '\n'

         return sum(self.M1adjusted),sum(self.M2adjusted)   # returns the adjusted sum of the M_fp's (a+(b*.8)+(c*.64)+(d*.512))


         # if newM1 != newM2: print 'newM1, newM2', newM1, newM2
         # if newM1 or newM2 != 0: print 'newM1,newM2', newM1, newM2, '\n'
         # print 'self.I motor', self.I[self.motorNeurons]
         # print 'self.I sensory_A', self.I[self.senseNeurons_A]
         # print 'self.I sensory_B', self.I[self.senseNeurons_B]
         # return newM1,newM2

     def getTotalNeuronNum(self):
         return self.totalNum

     def smell(self):
        smell_loc_A = [0,5]
        smell_str_A = []
        smell_loc_B = [5,5]
        smell_str_B = []
        # for food in foods: # messy looking because animat doesn't 'know' food locations - belongs to world
        #     if food.getType() == "A":
        #         smell_loc_A.append(food.getPos())
        #         smell_str_A.append(food.getSmell())
        #     if food.getType() == "B":
        #         smell_loc_B.append(food.getPos())
        #         smell_str_B.append(food.getSmell())
        # compute strength of smells at smell sensor locations
        dir = -(self.direc - math.pi/2)   #figure out the clockwise direction of the animat
        if(dir <= 0): dir += math.pi*2    #bound direction to [0, 2*pi]
        rotMat = np.array([[np.cos(dir), -np.sin(dir)], [np.sin(dir), np.cos(dir)]])  #construct the rotation matrix

        worldPos_A = np.dot(self.senseNeuronLocations_A, rotMat) + self.pos           #get the world position of the sense neurons based on the position and rotation of the Animat
        worldPos_B = np.dot(self.senseNeuronLocations_B, rotMat) + self.pos           #get the world position of the sense neurons based on the position and rotation of the Animat

        # print 'worldPos_A', '\n', worldPos_A
        # print 'worldPos_B', '\n', worldPos_B
        # print 'smell_loc_A', smell_loc_A
        # print 'smell_loc_B', smell_loc_B
        # print 'scipy.spatial.distance.cdist(worldPos_A, smell_loc_A )', '\n', scipy.spatial.distance.cdist(worldPos_A, smell_loc_A )
        # print 'scipy.spatial.distance.cdist(worldPos_B, smell_loc_B )', '\n', scipy.spatial.distance.cdist(worldPos_B, smell_loc_B )

        #built-in!
        total_smell_A = self.sensitivity_A * np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_A, smell_loc_A ), 0, 3), axis=1)  #figures out the total smell strength based on the distances (gaussian distribution)
        total_smell_B = self.sensitivity_B * np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_B, smell_loc_B ), 0, 3), axis=1)  #figures out the total smell strength based on the distances (gaussian distribution)

        # print 'np.sum(A)', '\n', total_smell_A/self.net.sensitivity_A
        # print 'np.sum(B)', '\n', total_smell_B/self.net.sensitivity_B

        self.I[self.senseNeurons_A] = np.minimum(np.float32(total_smell_A),np.float32(100))   #caps it at 100 .. may not be necessary
        self.I[self.senseNeurons_B] = np.minimum(np.float32(total_smell_B),np.float32(100))   #sense neuron drive based on smell

        sna = list(self.I[self.senseNeurons_A])
        # sense_Neuron_A_listf = [round(elem, 4) for elem in sense_Neuron_A_list]
        snb = list(self.I[self.senseNeurons_B])
        # sense_Neuron_B_listf = [round(elem, 4) for elem in sense_Neuron_B_list]
        np.set_printoptions(linewidth=200)
        # if self.count == 0 or self.count % 4 == 0:
        #     print 't', self.count
        #     print 'total_smell_A', '\n', total_smell_A

        print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('# of times sense_A fired',': '\
                                                                                                         ,self.net.Afired()[0],self.net.Afired()[1],self.net.Afired()[2]\
                                                                                                         ,self.net.Afired()[3],self.net.Afired()[4],self.net.Afired()[5]\
                                                                                                         ,self.net.Afired()[6],self.net.Afired()[7],self.net.Afired()[8]\
                                                                                                         ,self.net.Afired()[9])
        print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('# of times sense_B fired',': '\
                                                                                                         ,self.net.Bfired()[0],self.net.Bfired()[1],self.net.Bfired()[2]\
                                                                                                         ,self.net.Bfired()[3],self.net.Bfired()[4],self.net.Bfired()[5]\
                                                                                                         ,self.net.Bfired()[6],self.net.Bfired()[7],self.net.Bfired()[8]\
                                                                                                         ,self.net.Bfired()[9])

        # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.net.I[self.net.senseNeurons_A]',': '\
        #                                                                                                  ,sna[0],sna[1],sna[2],sna[3],sna[4],sna[5],sna[6],sna[7],sna[8],sna[9])
        # #     print 'sense A fired', '\n', self.net.Afired()
        # #     print 'total_smell_B', '\n', total_smell_B
        #
        # print '{:36s}{:2s}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}{:12.4f}'.format('self.net.I[self.net.senseNeurons_B]',': '\
        #                                                                                                  ,snb[0],snb[1],snb[2],snb[3],snb[4],snb[5],snb[6],snb[7],snb[8],snb[9])

        #     print 'sense B fired', '\n', self.net.Bfired(), '\n'
        # self.count += 1


     def move(self):
         # new proposed method to move the animat
         M1_sum,M2_sum = self.net.getMotorData() # sets M1_sum and M2_sum equal to the adjusted sum from getMotorData()
         new_theta = math.atan(-(M1_sum-M2_sum)/2.4)
         self.direc = self.direc + (new_theta/75)
         if M1_sum != 0 or M2_sum != 0:
             self.pos = self.pos + [math.cos(self.direc)*.005, math.sin(self.direc)*.005]
         else:
             self.pos = self.pos

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


A = Network(None, None, None)
A.direc = np.pi/2
for i in range(50):
    A.smell()
    A.move()