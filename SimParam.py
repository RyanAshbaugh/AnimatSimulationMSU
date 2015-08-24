__author__ = 'RJ'

'''

Holder object for all parameters needed to run simulation

For ease of use, readability, simpler to manipulate

'''

class SimParam():

    def __init__(self):
        #general usage vars
        self.worldParams = {1 : (None,None,None,None)}    #animNum,foodNum,worldSize,foodLocs
        ## Note should change calories to be a food/world param
        self.animatParams = {1 : (None,None,None,None,None,None)}  #id, origin, R_center, L_center, R_radii, L_radii

        #vars for evoDriver usage
        self.worldToRun = 1     #used so World.py knows which world param to extract and use
    #####  worldParam access methods  ######

    def setWorld(self,id,animNum,foodNum,worldSize,foodLocs):
        self.worldParams[id] = (animNum,foodNum,worldSize,foodLocs)

    def setAnimNum(self,id,num):
        self.worldParams[id] = (num,self.worldParams[1],self.worldParams[2],self.worldParams[3])

    def setFoodNum(self,id,num):
        self.worldParams[id] = (self.worldParams[0],num,self.worldParams[2],self.worldParams[3])

    def setWorldSize(self,id,size):
        self.worldParams[id] = (self.worldParams[0],self.worldParams[1],size,self.worldParams[3])

    def setFoodLocs(self,id,locs):
        self.worldParams[id] = (self.worldParams[0],self.worldParams[1],self.worldParams[2],locs)


    def getWorldNum(self):
        return len(self.worldParams)

    def getWorld(self,id):
        return self.worldParams[id]

    def getAnimNum(self,id):
        return self.worldParams[id][0]

    def getFoodNum(self,id):
        return self.worldParams[id][1]

    def getWorldSize(self,id):
        return self.worldParams[id][2]

    def getFoodLocs(self,id):
        return self.worldParams[id][3]


    #####  animatParam access methods  ######

    def setAnimParams(self,id,animId,origin):
        self.animatParams[id] = (animId,origin,None,None,None,None)

    def setOrigin(self,id,origin):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],origin,temp[2],temp[3],temp[4],temp[5])

    def setR_center(self,id,R_center):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],R_center,temp[3],temp[4],temp[5])

    def setL_center(self,id,L_center):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],L_center,temp[4],temp[5])

    def setR_radii(self,id,R_radii):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],temp[3],R_radii,temp[5])

    def setL_radii(self,id,L_radii):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],temp[3],temp[4],L_radii)

    # def setX0(self,id,x0):
    #     temp = self.animatParams[id]
    #     self.animatParams[id] = (temp[0],temp[1],x0,temp[3],temp[4])
    #
    # def setY0(self,id,y0):
    #     temp = self.animatParams[id]
    #     self.animatParams[id] = (temp[0],temp[1],temp[2],y0,temp[4])
    #
    # def setSigma(self,id,sigma):
    #     temp = self.animatParams[id]
    #     self.animatParams[id] = (temp[0],temp[1],temp[2],temp[3],sigma)

    def getAnimParams(self,id):
        return self.animatParams[id]

    #confusing, id is id of animat in this simulation, returns the unique id given by evo driver
    def getID(self,id):
        return self.animatParams[id][0]

    def getOrigin(self,id):
        return self.animatParams[id][1]

    def getR_center(self,id):
        return self.animatParams[id][2]

    def getL_center(self,id):
        return self.animatParams[id][3]

    def getR_radii(self,id):
        return self.animatParams[id][4]

    def getL_radii(self,id):
        return self.animatParams[id][5]

    # def getX0(self,id):
    #     return self.animatParams[id][2]
    #
    # def getY0(self,id):
    #     return self.animatParams[id][3]
    #
    # def getSigma(self,id):
    #     return self.animatParams[id][4]


