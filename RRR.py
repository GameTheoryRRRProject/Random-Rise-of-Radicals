from random import shuffle
from random import randint
from random import uniform
from numpy import linspace
from math import *
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
from tkinter import *

def sign(x):
    y = 0.0
    if x > 0.0:
        y = 1.0
    elif x < 0.0:
        y = -1.0
    return y

# Agents can get opinions, locations, neighbourhoods...
class Agent:
    def __init__(self):
        self.partners = []
        self.family = []
        self.x = 0
        self.y = 0
        # pop level 2 properties
        self.neighbourhood = []
        self.broadneighbourhood = []
        self.localcommunity = []
        # pop level 3 properties
        self.citizen = False
        #opinion parameters
        self.sw = 0 # 0 for sheep, 1 for wolf
        self.opinion = 0
        self.discop = 0 #discretized opinion
        self.history = []
        self.perc = 0 #percentages for level 2 meeting game


    def set_opinion(self,opinion):
        #don't change if opinion is 5 or -5 already
        if self.opinion != -5 and self.opinion != 5:
            self.opinion = opinion
        #Don't allow values larger than 5 or smaller than -5
        if self.opinion < -5:
            self.opinion = -5
        if self.opinion > 5:
            self.opinion = 5
        self.discop = round(self.opinion)

    def reset_opinion(self):
        self.opinion = 0.0

    def get_opinion(self):
        return self.opinion

    def get_discop(self):
        return self.discop

    def add_to_history(self, opinion):
        self.history.append(opinion)

    def get_history(self):
        return self.history.copy()

    def set_x(self, xValue):
        self.x = xValue

    def get_x(self):
        return self.x

    def set_y(self, yValue):
        self.y = yValue

    def get_y(self):
        return self.y

    def set_loc(self, location):
        self.loc = location

    def get_loc(self):
        return self.loc

    def set_neighbourhood(self, neighbourhood):
        self.neighbourhood = neighbourhood.copy()

    def get_neighbourhood(self):
        return self.neighbourhood

    def set_broadneighbourhood(self, broadneighbourhood):
        self.broadneighbourhood = broadneighbourhood.copy()

    def get_broadneighbourhood(self):
        return self.broadneighbourhood.copy()

    def set_localcommunity(self, localcommunity):
        self.localcommunity = localcommunity.copy()

    def get_localcommunity(self):
        return self.localcommunity.copy()

    def set_family(self, input):
        self.family = input.copy()

    def get_family(self):
        return self.family

    def add_partner(self, partner):
        self.partners.append(partner)

    def reset_partners(self):
        self.partners = []

    def get_partners(self):
        return self.partners.copy()

    def set_citizen(self, is_citizen):
        self.citizen = is_citizen

    def get_citizen(self):
        return self.citizen

    def set_sw(self, input):
        # zero for sheep, 1 for wolf
        self.sw = input

    def get_sw(self):
        return self.sw

    def set_perc(self, perc):
        self.perc = perc

    def get_perc(self):
        return self.perc


# The agents live on the board.
# All agents are listed in self.agents
class board:
    def __init__(self, x, y, NumberofPlayers):
        self.agents = [Agent() for i in range(NumberofPlayers)]
        self.X = x
        self.Y = y
        self.set_locations() # these locations are in the self.agents list, not on the board
        self.rounds = -1 #number of rounds run, -1 as not to count round zero (setting up the opinions)
        #discretized opinion categories
        self.l5 = []  # opinion = -5
        self.l45 = []  # -4 >= opinion > -5
        self.l34 = [] # -3 >= opinion > -4
        self.l23 = [] # -2 >= opinion > -3
        self.l12 = [] # -1 >= opinion > -2
        self.l01 = []
        self.f10 = []
        self.f21 = []
        self.f32 = []
        self.f43 = []
        self.f54 = []
        self.f5 = []
        self.colormap = ['#000080', '#0000CC', '#6666FF', '#3399FF', '#99CCFF', '#CCFFFF', '#FFE5FF', '#FFCCCC', '#FF9999', '#FF6666', '#FF0000', '#990000']
        #Initial opinions
        self.initalopinions = []
        self.liberals = []
        self.fascists = []
    # General Functions

    def set_dimensions(self, x, y):
        self.X = x
        self.Y = y

    def get_X(self):
        return self.X

    def get_Y(self):
        return self.Y

    def shuffle(self):
        shuffle(self.agents)
        self.set_locations()

    def set_locations(self):
        count = 0
        for item in self.agents:
            item.set_loc(count)
            count = count + 1

    def get_colormap(self):
        return self.colormap

    def print_types(self):
        for item in self.agents:
            print(item.get_type())

    def set_coordinates(self):
        #Go through the list of agents, give them coordinates according to their position on the list
        n = sqrt(len(self.agents))
        i = 0
        j = 0
        for item in self.agents:
            if j < n-1:
                item.set_x(i)
                item.set_y(j)
                j += 1
            else:
                item.set_x(i)
                item.set_y(j)
                j = 0
                i += 1

    def print_coordinates(self):
        for item in self.agents:
            print(item.get_x(), item.get_y())

    def distance(self,i,j):
        #Returns distance between self.agents elements i and j
        dx = abs(self.agents[i].get_x() - self.agents[j].get_x())
        dy = abs(self.agents[i].get_y() - self.agents[j].get_y())
        ds = sqrt(dx*dx + dy*dy)
        return ds


    def get_number(self, x, y):
        # Use this if only one agent is allowed for a certain x,y, returns integer
        # Returns value i, the point where the agent at x,y is in self.agents
        # Use self.agents[i] to access the agent
        i = 0
        for item in self.agents:
            if item.get_x() == x and item.get_y() == y:
                return i
            else:
                i += 1

    def get_numbers(self, x, y):
        # Use this if multiple agents are allowed on a certain x,y, returns list
        # Returns list of values i, point where agents at x,y are in self.agents
        numbers = []
        i = 0
        for item in self.agents:
            if item.get_x() == x and item.get_y() == y:
                numbers.append(i)
            else:
                i += 1
        return numbers

    def roundrun(self):
        self.rounds = self.rounds + 1

    def get_rounds(self):
        return self.rounds

    def add_opinions(self, opinions):
        self.l5.append(opinions[0])  # opinion = -5
        self.l45.append(opinions[1])  # -4 >= opinion > -5
        self.l34.append(opinions[2])# -3 >= opinion > -4
        self.l23.append(opinions[3]) # -2 >= opinion > -3
        self.l12.append(opinions[4]) # -1 >= opinion > -2
        self.l01.append(opinions[5])
        self.f10.append(opinions[6])
        self.f21.append(opinions[7])
        self.f32.append(opinions[8])
        self.f43.append(opinions[9])
        self.f54.append(opinions[10])
        self.f5.append(opinions[11])

    def get_discrete_opinions(self):
        return [self.l5, self.l45, self.l34, self.l23, self.l12, self.l01, self.f10, self.f21, self.f32, self.f43, self.f54, self.f5]

    def save_initalopinions(self):
        for item in self.agents:
            self.initalopinions.append(item.get_opinion())
            item.add_to_history(item.get_opinion())

    def get_initialopinions(self):
        return self.initalopinions.copy()

    def set_n(self):
        libs = 0
        fasc = 0
        for item in self.agents:
            if item.get_opinion() > 0:
                fasc = fasc + 1
            else:
                libs = libs + 1
        self.liberals.append(libs)
        self.fascists.append(fasc)

    def get_n_fascists(self):
        return self.fascists

    def get_n_liberals(self):
        return self.liberals

    def set_percs(self,percs):
        #perc list, 3 politicians, 2 celebrities, 1 commoners, 0 underdogs
        #reverse order to comply with game algorithm
        n = len(self.agents)
        n_politicians = int(percs[3]*n)
        n_celebrities = int(percs[2]*n)
        n_commoners = int(percs[1]*n)
        n_underdogs = int(n - n_politicians - n_celebrities - n_commoners)
        if n_underdogs < 0:
            n_underdogs = 0
        perclist = []
        for i in range(0, n_politicians):
            perclist.append(4)
        for i in range(0, n_celebrities):
            perclist.append(3)
        for i in range(0, n_commoners):
            perclist.append(2)
        for i in range(0, n_underdogs):
            perclist.append(1)
        shuffle(perclist)
        i = 0
        for item in self.agents:
            item.set_perc(perclist[i])
            i = i+1


    #Plotting and Animation

    def plot_board(self, Level):
        colors = self.get_colormap()
        if Level == 1:
            pyplot.figure()
            for item in self.agents:
                pyplot.scatter(item.get_x(), item.get_y(), color = colors[item.get_discop()+5])
            pyplot.axis([-1, self.get_X(), -1, self.get_Y()])
            pyplot.grid(True)
            pyplot.title("Grid after %d"%(self.get_rounds(),) + " rounds")
            pyplot.show()
        else:
            fig = pyplot.figure()
            ax = fig.add_subplot(111, projection='3d')
            X = self.get_X()
            Y = self.get_Y()
            for i in range(0, X):
                for j in range(0, Y):
                    xyagents = self.get_numbers(i, j)
                    z = 0
                    x = []
                    y = []
                    z2 = []
                    for m in xyagents:
                        ax.scatter(i, j, z, color = colors[self.agents[m].get_discop()+5], marker = 's', s = 100)
                        x.append(i)
                        y.append(j)
                        z2.append(z)
                        z = z + 1
                    ax.plot(x, y, z2, color="black", linestyle = '-')
                    xyagents = []
            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.set_title("Grid after %d"%(self.get_rounds(),) + " rounds")
            pyplot.show()

    def plot_opinions(self):
        opinions = self.get_discrete_opinions()
        n = self.get_rounds()
        x = linspace(0, n, n+1) #x axis are the rounds
        colors = self.get_colormap()  #set up color map
        pyplot.figure()
        for i in range(0, 12):
            pyplot.plot(x, opinions[i], color = colors[i], linestyle='-', label = "level = %d"%(i+1,))
        leg = pyplot.legend(loc = 'upper left', ncol = 6, prop={'size': 6})
        leg.get_frame().set_alpha(0.5)
        pyplot.ylabel("Opinion Categories")
        pyplot.xlabel("Rounds")
        pyplot.title("Opinions after %d"%(self.get_rounds())+ " rounds")
        pyplot.show()

    def plot_binary(self):
        libs = self.get_n_liberals()
        fasc = self.get_n_fascists()
        x = linspace(0, len(libs), len(libs))
        pyplot.figure()
        pyplot.plot(x, libs, color = "blue", linestyle='-', label = "Liberals")
        pyplot.plot(x, fasc, color = "red", linestyle = '-', label = "Fascists")
        pyplot.ylabel("Number of agents")
        pyplot.xlabel("Rounds")
        pyplot.title("Liberals and Fascists after %d"%(self.get_rounds(),) + " rounds")
        leg = pyplot.legend(loc = 'upper left')
        leg.get_frame().set_alpha(0.5)
        pyplot.show()


    #--- Level 1 population algorithm---
    #Todo: add interaction
    #Location is not important in level 1, so no locations are set

    def set_partners1(self):
        #Give all agents a random partner
        #All agents get added a random integer, this corresponds to the place of the partner agent in the self.agents list
        for item in self.agents:
            item.add_partner(randint(0, len(self.agents)-1))

    def reset_partners1(self):
        #deletes all partners
        for item in self.agents:
            item.reset_partners()

    def populate1(self):
        #use standard coordinate setting, one agent on each grid point on the board
        self.set_coordinates()

    #--- End Level 1 population algorithm



    #--- Level 2 population algorithm ---
    def set_coordinates2(self):
        #Assigns random x,y coordinates
        xbound = self.get_X()
        ybound = self.get_Y()
        for item in self.agents:
            item.set_x(randint(0, xbound-1))
            item.set_y(randint(0, ybound-1))

    def set_neighbourhoods(self, R = 0):
        #sets all neighbourhoods and family
        #if no input for R is given it only sets families
        #direct adaption from interaction-algorithm document for level 2
        for item in self.agents:
            family = []
            neighbours = []
            broadneighbours = []
            localcommunity = []
            for item2 in self.agents:
                dist = self.distance(item.get_loc(), item2.get_loc())
                if dist == 0 and item2.get_loc() != item.get_loc():
                    family.append(item2.get_loc())
                elif dist <= R:
                    neighbours.append(item2.get_loc())
                elif dist <= 2*R:
                    broadneighbours.append(item2.get_loc())
                elif dist <= 4*R:
                    localcommunity.append(item2.get_loc())
            item.set_family(family)
            item.set_neighbourhood(neighbours)
            item.set_broadneighbourhood(broadneighbours)
            item.set_localcommunity(localcommunity)

    def set_partners2(self, POI):
        #Sets up the partners according to the interaction-algorithm document
        for item in self.agents:
            X = uniform(0, 1)
            family = item.get_family().copy()
            if X <= POI and family != []:
                item.add_partner(family[randint(0, len(family)-1)])
            else:
                X = uniform(0, 1)
                if X <= POI and item.get_neighbourhood() != []:
                    item.add_partner(item.get_neighbourhood()[randint(0, len(item.get_neighbourhood())-1)])
                else:
                    X = uniform(0, 1)
                    if X <= POI and item.get_neighbourhood() != 0 and item.get_broadneighbourhood() != []:
                        item.add_partner(item.get_broadneighbourhood()[randint(0, len(item.get_broadneighbourhood()) - 1)])

    #Use this before anything else, sets up coordinates and families
    def populate2(self, R):
        self.set_coordinates2()
        self.set_neighbourhoods(R)



    #--- End Level 2 population algorithm ---




    #--- Begin Level 3 population algorithm ---

    #use from level 2:
    # set_neighbourhoods
    # set_partners

    def set_citizens(self, rate = 0.5):
        values = []
        n_citizens = round(rate*len(self.agents))
        for i in range(0,n_citizens):
            values.append(True)
        for i in range(n_citizens, len(self.agents)):
            values.append(False)
        shuffle(values)
        count = 0
        for item in self.agents:
            item.set_citizen(values[count])
            count = count + 1

    def set_coordinates3(self, cityarea = 0.1):
        xbound = self.get_X()
        ybound = self.get_Y()
        #X, Y lengths of the city area
        Lx = round(cityarea * xbound)
        Ly = round(cityarea * ybound)
        #Down Left point of the city area
        Xcity = round(0.5*(xbound - Lx))
        Ycity = round(0.5*(ybound - Ly))
        for item in self.agents:
            citizen = item.get_citizen()
            if citizen: #Go to origin of city rectangle, add random x and y value with upper limit of the rectangle bounds Lx and Ly
                item.set_x(Xcity + randint(0, Lx))
                item.set_y(Ycity +randint(0, Ly))
            else:
                X = randint(0, xbound - 1)
                item.set_x(X)
                if X > 0.5*(xbound - Lx) and X < 0.5*(xbound + Lx):
                    #Any value for y is out of the rectangle in this case
                    item.set_y(randint(0, ybound - 1))
                else:
                    YFound = False
                    while YFound == False:
                        #generate random Y, if it is outside of city bounds we found our Y. Otherwise generate again.
                        Y = randint(0, ybound - 1)
                        if Y < Ycity or Y > Ycity + Ly:
                            YFound = True
                    item.set_y(Y)


    def populate3(self, R):
        self.set_citizens()
        self.set_coordinates3()
        self.set_neighbourhoods(R)

    #--- End Level 3 population algorithm ---

    #--- Opinion algorithm

    def game(self, x, y, wx ,wy):
        delX = (abs(x)-5.0)*(abs(x)-5.0)*abs(x-y)/125.0
        delY = (abs(y)-5.0)*(abs(y)-5.0)*abs(x-y)/125.0
        xnew = x - sign(x - y)*wx*delX
        ynew = y - sign(y - x)*wy*delY
        return [xnew, ynew]

    def opiniongame(self, n1, n2):
        #takes as input positions n1, n2 on the self.agents list, a
        #default values for GPF,SSF are set s.t. they cancel out in the formula (leave default for level 1 opinion algorithm)
        agent1 = self.agents[n1]
        agent2 = self.agents[n2]
        a1s = agent1.get_sw()   # 0 for sheep, 1 for wolf
        a2s = agent2.get_sw()
        a1o = agent1.get_opinion()
        a2o = agent2.get_opinion()
        delta = abs(a1o-a2o)
        if a1s == 0 and a2s == 0:
            wx = 1
            wy = 1
        elif a1s == 1 and a2s ==0:
            wx = 0
            wy = 2
        elif a1s == 0 and a2s ==1:
            wx = 2
            wy = 0
        else:
            wx = 0.5
            wy = 0.5
        newopinions = self.game(a1o, a2o, wx, wy)
        #Set opinions, throw dice
        #don't throw if perc is 0 -> level 1 meeting game
        nthrows1 = agent1.get_perc()
        nthrows2 = agent2.get_perc()
        success1 = False
        success2 = False
        if nthrows1 == 0:
            agent1.set_opinion(newopinions[0])
        if nthrows2 == 0:
            agent2.set_opinion(newopinions[1])
        for i in range(0, nthrows1):
            roll = uniform(0, 10)
            if roll > delta:
                success1 = True
        for i in range(0, nthrows2):
            roll = uniform(0, 10)
            if roll > delta:
                success2 = True
        if success1:
            agent2.set_opinion(newopinions[1])
        if success2:
            agent1.set_opinion(newopinions[0])





    #--- End Level 1 Opinion Algorithm

    #On opinions
    def set_opinions(self):
        for item in self.agents:
            #Todo: implement real opinion distributing method
            value = randint(-5, 5)
            item.set_opinion(value)
        opinions = field.get_opinions().copy()
        opinions = field.discretize(opinions)
        field.add_opinions(opinions)
        field.save_initalopinions()
        field.set_n()
        field.roundrun()

    def set_opinions2(self, avgs, var):
        #Opinion distribution based on averages and percs
        print(avgs)
        for item in self.agents:
            item.reset_opinion()
            p = item.get_perc()
            average = avgs[p-1]
            opinion = average + ((-1)**randint(1, 2))*uniform(0, 1)*var
            item.set_opinion(opinion)

    def set_sw(self, pWolf = 0.25):
        for item in self.agents:
            value = uniform(0, 1)
            if value < pWolf:
                item.set_sw(1)
            else:
                item.set_sw(0)

    def get_opinions(self):
        opinions = []
        for item in self.agents:
            opinions.append(item.get_opinion())
        return opinions

    def discretize(self, opinions):
        l5 = 0  # opinion = -5
        l45 = 0  # -4 >= opinion > -5
        l34 = 0  # -3 >= opinion > -4
        l23 = 0  # -2 >= opinion > -3
        l12 = 0  # -1 >= opinion > -2
        l01 = 0
        f10 = 0
        f21 = 0
        f32 = 0
        f43 = 0
        f54 = 0
        f5 = 0
        for opinion in opinions:
            if opinion == -5:
                l5 = l5 + 1
            elif opinion <= -4:
                l45 = l45 + 1
            elif opinion <= -3:
                l34 = l34 + 1
            elif opinion <= -2:
                l23 = l23 + 1
            elif opinion <= -1:
                l12 = l12 + 1
            elif opinion <= 0:
                l01 = l01 + 1
            elif opinion <= 1:
                f10 = f10 + 1
            elif opinion <= 2:
                f21 = f21 + 1
            elif opinion <= 3:
                f32 = f32 + 1
            elif opinion <= 4:
                f43 = f43 + 1
            elif opinion < 5:
                f54 = f54 + 1
            else:
                f5 = f5 + 1
        distribution = [l5, l45, l34, l23, l12, l01, f10, f21, f32, f43, f54, f5]
        return distribution



    #--- Iteration and running ---

    # To be filled out later when games are implemented

    def iterate(self, poplevel, POI=0.5):
        #input population level algorithm as partners are assigned differently
        #Output: list of number of agents in the discretized opinion states
        self.reset_partners1()
        #Find Partners
        if poplevel == 1:
            self.set_partners1()
        else:
            self.set_partners2(POI)
        #Play games
        for item in self.agents:
            partnerlist = item.get_partners()
            if partnerlist != []:
                for n in partnerlist:
                    self.opiniongame(item.get_loc(), n)
        opinions = self.get_opinions()
        opinions = self.discretize(opinions)
        self.add_opinions(opinions)
        self.set_n()
        self.roundrun()
        #Add opinions to agent history
        for item in self.agents:
            item.add_to_history(item.get_opinion())


    def RunRounds(self, nRounds, poplevel):
        for i in range(0, nRounds):
            self.iterate(poplevel)

OPTIONS = [
"1",
"2",
"3"
]

OPTIONS2 = [
"1",
"2"
]

def showboard(Level):
    if 'field' in globals():
        field.plot_board(Level)
    else:
        print('Agents not yet generated.')

def advancecheck(GLevel):
    if 'field' in globals():
        advance(GLevel)
    else:
        print('Agents not yet generated.')

def getHistory(desiredopinion, n):
    #Input desired opinion of agents, n number of agents
    numbers = []
    delta = 0
    initialopinions = field.get_initialopinions()
    # go through opinions and find those close to desiredopinion
    # increase allowed delta until list is full
    while len(numbers) < n:
        i = 0
        for item in field.agents:
            if abs(desiredopinion - initialopinions[i]) <= delta:
                numbers.append(i)
            i = i+1
        delta = delta + 0.1
    histories = []
    wolf = []
    for i in range(0, n):
        histories.append(field.agents[numbers[i]].get_history())
        wolf.append(field.agents[numbers[i]].get_sw())
    return histories, wolf

def plotHistories(histories, wolf):
    pyplot.figure()
    for i in range(0, len(histories)):
        xi = linspace(0, len(histories[i])-1, len(histories[i]))
        if wolf[i] == 0:
            pyplot.plot(xi, histories[i], linestyle = '-', label="Initial Opinion = %d"%(histories[i][0],))
        else:
            pyplot.plot(xi, histories[i], linestyle = '--', label="Initial Opinion = %d"%(histories[i][0],))
    leg = pyplot.legend(loc='upper left', ncol=4, prop={'size': 6})
    leg.get_frame().set_alpha(0.5)
    pyplot.ylabel("Opinions")
    pyplot.xlabel("Rounds")
    pyplot.title("Opinions after %d" % (field.get_rounds()) + " rounds")
    pyplot.show()

def history(desiredopinion, n):
    histories, wolf = getHistory(desiredopinion, n)
    plotHistories(histories, wolf)

#Open window to enter population parameters
master = Tk()
first = True #To check if we can rebuild windows
def PopWindow():
    #Function to save and exit population window
    def save_values():
        #Check if a field has already been generated, if yes delete
        global valuelist
        valuelist = []
        valuelist.append(int(e1.get())) #Xval
        valuelist.append(int(e2.get())) #Yval
        valuelist.append(int(e3.get())) #N
        valuelist.append(int(e4.get())) #R
        valuelist.append(int(variable.get()))   #Level
        valuelist.append(float(e5.get()))   #Pwolf
        valuelist.append(int(variable2.get()))
        global field
        field = board(int(e1.get()), int(e2.get()), int(e3.get()))
        if int(variable.get()) == 1:
            field.populate1()
        elif int(variable.get()) == 2:
            field.populate2(int(e4.get()))
        else:
            field.populate3(int(e4.get()))
        field.set_opinions()
        field.set_sw(float(e5.get()))
        print("New field generated")



    master.title('Population')
    global LX
    global LY
    global LN
    global LR
    global LP
    global LW
    global e1
    global e2
    global e3
    global e4
    global e5
    global Tinfo
    global Bgen
    global w
    global v
    global LA
    global Bgoto
    global Bplot


    LX = Label(master, text="X Size")
    LX.grid(row=0)
    LY = Label(master, text="Y Size")
    LY.grid(row=1)
    LN = Label(master, text="Number of Agents")
    LN.grid(row=2)
    LR = Label(master, text="Neighbour radius R")
    LR.grid(row=3)
    LP = Label(master, text="Population algorithm")
    LP.grid(row=5)
    LW = Label(master, text="Wolf probability")
    LW.grid(row=4)
    LA = Label(master,text ="Game algorithm")
    LA.grid(row=6, column=0)

    variable = StringVar(master)
    variable.set(OPTIONS[0]) # default value

    w = OptionMenu(master, variable, *OPTIONS)
    w.grid(row=5, column=1)

    variable2 = StringVar(master)
    variable2.set(OPTIONS2[0])

    v = OptionMenu(master, variable2, *OPTIONS2)
    v.grid(row=6, column=1)

    e1 = Entry(master)
    e1.insert(0, "10")
    e2 = Entry(master)
    e2.insert(0, "10")
    e3 = Entry(master)
    e3.insert(0, "100")
    e4 = Entry(master)
    e4.insert(0, "1")
    e5 = Entry(master)
    e5.insert(0, "0.333")

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)
    e4.grid(row=3, column=1)
    e5.grid(row=4, column=1)

    Tinfo = Text(master, width=51, height = 34)
    Tinfo.grid(row=0, column = 3, rowspan = 7)
    Tinfo.insert(END, "The agents are randomly assigned a position on\na X by Y grid. Each combination of integer \nx and y defines a possible position.\nR is the radius to define neighbourhoods.\nAgents are wolves (change own opinion slowly)\nor sheep (change own opinions quickly).\n\nPopulation Algorithm 1:\nPosition on the grid does not matter.\nEvery agent is randomly assigned a partner in each\nround with equal probabilities.\n\nPopulation Algorithm 2:\nAgents are randomly distributed on the grid.\nAgents on the same grid position form a family.\nAgents within radius R form direct neighbourhood.\nAgents within radius 2R form broader neighbourhood.\nAgents within radius 4R form local community.\nThe groups are exclusive, e.g. agents in the family\ngroup are not in the neighbourhood groups.\nThe partner assignment is still random, but\nconnected to the distance. Family members are more likely to be assigned than neighbourhood members.\n\nPopulation Algorithm 3:\nSame rules as in population algorithm 2, but 50% of\nplayers are positioned in city area in the center\nof the grid.\n\nGame Alogrithms:\nBoth game algorithm rely on the sheep wolf factor.\nIn game algorithm 2, different social statuses are\nassigned. Higher social statuses are more likely to\nchange other opinions.")

    Bgen = Button(master, text='Generate Agents', command=lambda: save_values())
    Bgen.grid(row=7, column=0)

    # Add Button to plot Board
    Bplot = Button(master, text='Show Grid', command=lambda: showboard(int(variable.get())))
    Bplot.grid(row=7, column=1)
    # Add Button to advance
    Bgoto = Button(master, text='Go to opinion algorithm', command=lambda: advancecheck(int(variable2.get())))
    Bgoto.grid(row=8, column=0, columnspan=2)


def hidePopWindow():
    global LX
    global LY
    global LN
    global LR
    global LP
    global LW
    global e1
    global e2
    global e3
    global e4
    global e5
    global Tinfo
    global Bgen
    global Bplot
    global Bgoto
    global w
    global v
    global LA

    LX.grid_remove()
    LY.grid_remove()
    LN.grid_remove()
    LR.grid_remove()
    LP.grid_remove()
    LW.grid_remove()
    e1.grid_remove()
    e2.grid_remove()
    e3.grid_remove()
    e4.grid_remove()
    e5.grid_remove()
    Tinfo.grid_remove()
    Bgen.grid_remove()
    Bplot.grid_remove()
    Bgoto.grid_remove()
    w.grid_remove()
    v.grid_remove()
    LA.grid_remove()

def RebuildPopWindow():
    global LX
    global LY
    global LN
    global LR
    global LP
    global LW
    global e1
    global e2
    global e3
    global e4
    global e5
    global Tinfo
    global Bgen
    global Bplot
    global Bgoto
    global w
    global v
    global LA

    LX.grid()
    LY.grid()
    LN.grid()
    LR.grid()
    LP.grid()
    LW.grid()
    e1.grid()
    e2.grid()
    e3.grid()
    e4.grid()
    e5.grid()
    Tinfo.grid()
    Bgen.grid()
    Bplot.grid()
    Bgoto.grid()
    w.grid()
    v.grid()
    LA.grid()


PopWindow()

#Todo: put second window here as well, add option to reset -> everything needs to be in one window to keep figures from the first when advancing to the second
def GameWindow():
    master.title('Run Opinion Algorithm')
    global g1
    global LRUN
    global LADD
    global BRUN
    global BCAT
    global BBIN
    global LAG
    global LNAG
    global LSOP
    global BSAD
    global g2
    global g3
    global LSW
    global LSW2
    global BGRD
    global RST
    global QT
    global TRounds

    global first
    first = False

    def Run(nRounds, Level):
        global TRounds
        field.RunRounds(nRounds, Level)
        textline = "Rounds run: %d" % field.get_rounds()
        TRounds.configure(text = textline)

    global valuelist
    Level = valuelist[4]

    g1 = Entry(master)
    g1.insert(0, "25")
    g1.grid(row=1, column=1)

    LRUN = Label(master, text="Run opinion algorithm:")
    LRUN.grid(row=0)
    LADD = Label(master, text="Add Rounds")
    LADD.grid(row=1)

    BRUN = Button(master, text='Run Rounds', command=lambda: Run(int(g1.get()), int(Level)))
    BRUN.grid(row=2, column=0)

    TRounds = Label(master, text = "Rounds run: %d" % field.get_rounds())
    TRounds.grid(row = 2, column = 1)

    BCAT = Button(master, text = 'Show categorical development', command= lambda:field.plot_opinions())
    BCAT.grid(row = 3, column = 0)
    BBIN = Button(master, text = 'Show Liberal/Radical development', command= lambda:field.plot_binary())
    BBIN.grid(row = 3, column = 1)

    LAG = Label(master, text="Show opinion development of agents:")
    LAG.grid(row=4)
    LNAG = Label(master, text="Enter number of individual agents:")
    LNAG.grid(row=5)
    LSOP = Label(master, text="Enter desired opinion at round zero")
    LSOP.grid(row=6)

    g2 = Entry(master)  #number of agents
    g2.insert(0, "5")
    g2.grid(row = 5, column = 1)

    g3 = Entry(master)
    g3.insert(0, "0")   #desired opinion
    g3.grid(row = 6, column = 1)

    BSAD = Button(master, text = 'Show individual agents history', command=lambda: history(int(g3.get()), int(g2.get())))
    BSAD.grid(row = 7, column = 0)
    LSW = Label(master, text="Dashed line for wolves, solid for sheep.")
    LSW.grid(row=7, column = 1)
    LSW2 = Label(master, text="Show the positions and opinions of the agents on the grid:")
    LSW2.grid(row = 8, column = 0)
    BGRD = Button(master, text = "Show grid", command = lambda: field.plot_board(Level))
    BGRD.grid(row = 9, column =0)
    RST = Button(master, text ="Back to population algorithm", command = lambda: goback())
    RST.grid(row = 10, column = 0)
    QT = Button(master, text ="Quit Program", command = lambda: master.destroy())
    QT.grid(row=10, column = 1)


def hideGameWindow():
    global g1
    global LRUN
    global LADD
    global BRUN
    global BCAT
    global BBIN
    global LAG
    global LNAG
    global LSOP
    global g2
    global g3
    global BSAD
    global LSW
    global LSW2
    global BGRD
    global RST
    global QT
    global TRounds

    g1.grid_remove()
    LRUN.grid_remove()
    LADD.grid_remove()
    BRUN.grid_remove()
    BCAT.grid_remove()
    BBIN.grid_remove()
    LAG.grid_remove()
    LNAG.grid_remove()
    LSOP.grid_remove()
    g2.grid_remove()
    g3.grid_remove()
    BSAD.grid_remove()
    LSW.grid_remove()
    LSW2.grid_remove()
    BGRD.grid_remove()
    RST.grid_remove()
    QT.grid_remove()
    TRounds.grid_remove()

def rebuildGameWindow():
    global g1
    global LRUN
    global LADD
    global BRUN
    global BCAT
    global BBIN
    global LAG
    global LNAG
    global LSOP
    global g2
    global g3
    global BSAD
    global LSW
    global LSW2
    global BGRD
    global RST
    global QT
    global TRounds

    g1.grid()
    LRUN.grid()
    LADD.grid()
    BRUN.grid()
    BCAT.grid()
    BBIN.grid()
    LAG.grid()
    LNAG.grid()
    LSOP.grid()
    g2.grid()
    g3.grid()
    BSAD.grid()
    LSW.grid()
    LSW2.grid()
    BGRD.grid()
    RST.grid()
    QT.grid()
    TRounds.grid()

def ProsperityWindow():
    global Phead
    global a1
    global a2
    global a3
    global a4
    global p1
    global p2
    global p3
    global p4
    global PLhead
    global PRhead
    global PL1
    global PL2
    global PL3
    global PL4
    global CNT
    global variance
    global LVar

    p1 = Entry(master)
    p1.insert(0, "0.3")
    p2 = Entry(master)
    p2.insert(0, "0.6")
    p3 = Entry(master)
    p3.insert(0, "0.09")
    p4 = Entry(master)
    p4.insert(0, "0.01")


    a1 = Entry(master)
    a1.insert(0, "0.0")
    a2 = Entry(master)
    a2.insert(0, "0.0")
    a3 = Entry(master)
    a3.insert(0, "0.0")
    a4 = Entry(master)
    a4.insert(0, "0.0")

    a1.grid(row=3, column=2)
    a2.grid(row=4, column=2)
    a3.grid(row=5, column=2)
    a4.grid(row=6, column=2)


    p1.grid(row=3, column=1)
    p2.grid(row=4, column=1)
    p3.grid(row=5, column=1)
    p4.grid(row=6, column=1)


    variance = Entry(master)
    variance.grid(row = 1, column =1)
    variance.insert(0, '0.5')

    LVar = Label(master, text = "Opinion variance")
    LVar.grid(row = 1, column = 0)

    Phead = Label(master, text = "Enter population percentages as numbers between 0 and 1 and mean average opinions between -5 and 5")
    PLhead = Label(master, text = "Percentages")
    PRhead = Label(master, text = "Average Opinion")
    PL1 = Label(master,text = "Underdogs")
    PL2 = Label(master,text = "Commoners")
    PL3 = Label(master,text = "Celebrities")
    PL4 = Label(master,text = "Politicians")

    Phead.grid(row=0, column = 0, columnspan = 3)
    PLhead.grid(row = 2, column = 1)
    PRhead.grid(row = 2, column = 2)
    PL1.grid(row = 3, column = 0)
    PL2.grid(row = 4, column = 0)
    PL3.grid(row = 5, column = 0)
    PL4.grid(row = 6, column = 0)

    CNT = Button(master, text = "Continue to Game", command = lambda: popcheck([float(p1.get()), float(p2.get()), float(p3.get()), float(p4.get())], [float(a1.get()), float(a2.get()), float(a3.get()), float(a4.get())], float(variance.get())))
    CNT.grid(row = 7, column = 0)

def hideProsperityWindow():
    global Phead
    global a1
    global a2
    global a3
    global a4
    global p1
    global p2
    global p3
    global p4
    global PLhead
    global PRhead
    global PL1
    global PL2
    global PL3
    global PL4
    global CNT
    global variance
    global LVar

    Phead.grid_remove()
    a1.grid_remove()
    a2.grid_remove()
    a3.grid_remove()
    a4.grid_remove()
    p1.grid_remove()
    p2.grid_remove()
    p3.grid_remove()
    p4.grid_remove()
    PRhead.grid_remove()
    PLhead.grid_remove()
    PL1.grid_remove()
    PL2.grid_remove()
    PL3.grid_remove()
    PL4.grid_remove()
    CNT.grid_remove()
    variance.grid_remove()
    LVar.grid_remove()

def popcheck(percs, avgs, var):
    percentages = sum(percs)
    if percentages > 0.9999:
        hideProsperityWindow()
        field.set_percs(percs)
        field.set_opinions2(avgs, var)
        global first
        if first == True:
            GameWindow()
        else:
            GameWindow()
    else:
        print("Sum of percentages needs to add up to 1")


def advance(GLevel):
    global first
    hidePopWindow()
    if first == True:
        if GLevel == 1:
            GameWindow()
        else:
            ProsperityWindow()
    else:
        if GLevel == 1:
            GameWindow()
        else:
            ProsperityWindow()

def goback():
    hideGameWindow()
    RebuildPopWindow()

mainloop( )


