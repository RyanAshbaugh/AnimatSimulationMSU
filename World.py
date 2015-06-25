# -*- coding: utf-8 -*-
# Author - RJ
"""
Created on Sun Feb 16 21:33:58 2014

Main Simulation Driver File
Doubles as simulation driver and simulated "World"

contains all objects in simulated world
as well as controls flow of operations of simulation

"""


import numpy as np
import AnimatShell
import Stimuli
import random
import SimParam

class World:

    def __init__(self,simParam):
        self.sP = simParam
        self.arenaSize = (self.sP.getWorldSize(1),self.sP.getWorldSize(1)) #square arena
        self.numBounds = [0 - self.arenaSize[0]/2., 0 + self.arenaSize[0]/2.,0 - self.arenaSize[1]/2., 0 + self.arenaSize[1]/2.]
        self.animats = []
        for x in range(1,self.sP.getAnimNum(1)+1):
            self.animats.append(AnimatShell.WheelAnimat(self.sP.getAnimParams(x)))
        self.smells = []
        self.foods = self.setup_food()

    def setup_food(self):
        foods = []
        food_loc = self.sP.getFoodLocs(self.sP.worldToRun)
        for i,loc in enumerate(food_loc):
            if i > len(food_loc)*.75: foods.append(Stimuli.Food_B(loc))
            else: foods.append(Stimuli.Food_A(loc))
        return foods

    def determineTraction(self,pos):
        return 1

    def copyDynamicState(self):
        state = []
        foodState = []
        for food in self.foods:
            foodState.append(food.getAmount())
        state.append(foodState)
        animat_state = []
        for animat in self.animats:
            animat_state.append(animat.copyDynamicState())
        state.append(animat_state)
        return DynamicWorldState(state)

    def loadDynamicState(self, state):
        state = state.state
        foodState = state[0]
        animat_state = state[1]
        for i in range(0, len(foodState)):
            self.foods[i].amt = foodState[i]
        for i in range(0, len(animat_state)):
            self.animats[i].loadDynamicState(animat_state[i])

    def update(self, t, dt):
        for animat in self.animats:
            animat.smell(self.foods)
            animat.runNetwork(t, dt)
            traction = self.determineTraction(animat.pos)
            animat.move(traction, t)
            self.foods = animat.eat(self.foods) #returns array with updated food amounts
            #self.updateFood(foodArray[1][1])        #updates food objects

    #get rid of foods that are eaten
    def updateFood(self,amts):
        for amt,food in zip(amts,self.foods):
            food.amt = amt


    def getFoodLocs(self):
        return [food.getPos() for food in self.foods]

class DynamicWorldState:
    def __init__(self, state):
        self.state = state

    def getFood(self):
        return self.state[0]

    def getAnimatState(self):
        return self.state[1][0]     #hardcoded for only one animat in simulation

    def getEnergy(self):
        #depending on state, may be stored as integer or an array object
        try:
            return self.getAnimatState()[2][0]
        except:
            return self.getAnimatState()[2]

    def getPos(self):
        return self.getAnimatState()[4]

    def getA(self):
        return self.getAnimatState()[7][0]

    def getB(self):
        return self.getAnimatState()[7][1]

    def getC(self):
        return self.getAnimatState()[7][2]

    def getD(self):
        return self.getAnimatState()[7][3]

    def getU(self):
        return self.getAnimatState()[7][4]

    def getV(self):
        return self.getAnimatState()[7][5]

    def getS(self):
        return self.getAnimatState()[7][6]

    def getI(self):
        return self.getAnimatState()[7][7]

