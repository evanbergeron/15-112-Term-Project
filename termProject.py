# termProject.py

import re
import random
import time
import numpy
from Tkinter import *

class Animation(object):
    # Override these methods when creating your own animation
    def mousePressed(self, event): pass
    def mouseDragged(self, event): pass
    def keyPressed(self, event): pass
    def timerFired(self): pass
    def init(self): pass
    def redrawAll(self): pass
    
    # Call app.run(width,height) to get your app started
    def run(self, width=1280, height=710):
        # create the root and the canvas
        root = Tk()
        root.title('CrsGrphr')
        self.width = width
        #print width, width/10
        self.height = height
        self.frame = Frame(root, width=self.width,height=self.height,
                           bg='#FFFFFF', colormap='new')
        # Tells tk if window resized, resize with it.
        self.frame.columnconfigure(0,weight=1)
        self.frame.rowconfigure(0,weight=1)
        self.frame.grid(column=0,row=0, sticky=(N, W, E, S))
        self.courseEntry = Entry(self.frame,width=width/40)
        self.courseEntry.grid(column=0,row=0,sticky=(N,W))
        self.canvas = Canvas(self.frame, width=width, 
                             height=height,bg='#FFFFFF')
        self.canvas.grid(column=1,row=1,sticky=(N,E,S,W))#, rowspan=2)
        self.sidebar = Canvas(self.frame, width=width/40, 
                              height=height,bg='#EEEEEE')
        self.sidebar.grid(column=0,row=1,sticky=(N,W,E,S))
        self.recursiveAdd = IntVar()
        self.prereqDepthToggle = Checkbutton(self.frame,
                                             text='Full Recursive Depth',
                                             variable=self.recursiveAdd)
        self.prereqDepthToggle.grid(column=1,row=0, sticky=(N,W))
        for child in self.frame.winfo_children():
            child.grid_configure(padx=3,pady=3)
        # set up events
        def redrawAllWrapper():
            self.canvas.delete(ALL)
            self.sidebar.delete(ALL)
            self.redrawAll()
        def mousePressedWrapper(event):
            self.mousePressed(event)
            redrawAllWrapper()
        def mouseDraggedWrapper(event):
            self.mouseDragged(event)
            redrawAllWrapper()
        def keyPressedWrapper(event):
            self.keyPressed(event)
            redrawAllWrapper()
        root.bind("<Button-1>", mousePressedWrapper)
        root.bind('<B1-Motion>',mouseDraggedWrapper)
        root.bind("<Key>", keyPressedWrapper)
        # set up timerFired events
        self.timerFiredDelay = 25 # milliseconds
        def timerFiredWrapper():
            self.timerFired()
            redrawAllWrapper()
            # pause, then call timerFired again
            self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
        # init and get timerFired running
        self.init()
        timerFiredWrapper()
        # and launch the app
        root.mainloop()  # This call BLOCKS 

class GraphAnimation(Animation):
    def __init__(self, graph):
        self.graph = graph
        self.takenCourses = []
        self.originalTakenCourses = self.takenCourses
        self.scheduledCourses = []
        self.selectedNodes = []
        self.havePutNodesOnScreen = False

    def keyPressed(self, event):
        #print event.keysym
        if event.keysym == 'Return':
            self.considerUserInput()
        if event.keysym == 'BackSpace':
            self.removeSelectedNode()
            lengthOfInput = len(self.courseEntry.get())+1
            self.courseEntry.delete(0,lengthOfInput)
        if event.keysym == 'p':#'Control_L':
            self.expandNode(event)
        if event.keysym == 'ampersand':#'Meta_L':
            self.soloNode(event)
            
    def removeSelectedNode(self):
        # SelectedNodes will always be length 1 or 0.
        if self.selectedNodes != []:
            selectedNode = self.selectedNodes[0]
            self.graph.vertexSet -= {selectedNode}
            toDelete = set([])
            for edge in self.graph.edges():
                if selectedNode in edge:
                    toDelete |= {edge}
            self.graph.edgeSet -= toDelete

    def mousePressed(self, event):
        self.selectNode(event)

    def mouseDragged(self, event):
        self.dragNode(event)

    def soloNode(self, event):
        # Forms an instance of the DiGraph class with one node.
        if self.selectedNodes != []:
            trivialGraph = DiGraph()
            trivialGraph.addNode(self.selectedNodes[-1])
            self.graph = trivialGraph

    def selectNode(self, event):
        counter = 0
        def distance(x1, y1, x2, y2):
            return ((x2-x1)**2 + (y2-y1)**2)**.5
        # If we clicked a node, add it to selectedNodes
        for node in self.graph.nodes():
            (nodeX, nodeY) = node.location 
            if distance(event.x,event.y,nodeX,nodeY) <= node.r:
                counter += 1
                if node in self.selectedNodes:
                    self.selectedNodes = []
                else:
                    self.selectedNodes = [node]
        if counter == 0: 
            # Clicked outside of any of the nodes
            self.selectedNodes = []

    def dragNode(self, event):
        def distance(x1, y1, x2, y2):
            return ((x2-x1)**2 + (y2-y1)**2)**.5
        for node in self.graph.nodes():
            (nodeX, nodeY) = node.location 
            if distance(event.x,event.y,nodeX,nodeY) <= node.r:
                node.location = numpy.array([event.x, event.y])

    def expandNode(self, event):
        if self.selectedNodes != []:
            affectedNode = self.selectedNodes[-1] # Last one
            self.addTree(affectedNode)

    def timerFired(self):
        self.updateNodes()
        self.redrawAll()

    def clearGraph(self):
        self.scheduledCourses = []
        self.takenCourses = self.originalTakenCourses
        self.graph = DiGraph()

    def userForgotDashes(self):
        # If user forgot dashes, there will be a 5 digit course number in input
        return re.findall('[\\d]{5}',self.courseEntry.get()) != []

    def fixLackOfDashes(self):
        # Takes care of whether or not the course number includes a dash.
        dashlessCourseNumbers = re.findall('[\\d]{5}',self.courseEntry.get())
        newScheduledCourse = self.courseEntry.get()
        if dashlessCourseNumbers != []:
            departmentNumber = dashlessCourseNumbers[0][:2]
            courseNumber = dashlessCourseNumbers[0][2:]
            newScheduledCourse = '%s-%s' % (departmentNumber, courseNumber)
        return newScheduledCourse

    def considerUserInput(self):
        self.considerSpecialInputs()
        if self.courseEntry.get()[:4] == 'Took':
            # get everything after the space
            newTakenCourse = self.courseEntry.get()[5:]
            if self.userForgotDashes():
                newTakenCourse = self.fixLackOfDashes()
            if courseDictionary.get(newTakenCourse)!= None:
                self.havePutNodesOnScreen = True
                newTakenCourse = courseDictionary.get(newTakenCourse)
                self.takenCourses.append(newTakenCourse.number)
            if newTakenCourse not in self.graph.nodes():
                self.graph = self.recursivelyAddNodesToTree(newTakenCourse)
        # Takes care of whether or not the course number includes a dash.
        dashlessCourseNumbers = re.findall('[\\d]{5}',self.courseEntry.get())
        newScheduledCourse = self.courseEntry.get()
        if dashlessCourseNumbers != []:
            departmentNumber = dashlessCourseNumbers[0][:2]
            courseNumber = dashlessCourseNumbers[0][2:]
            newScheduledCourse = '%s-%s' % (departmentNumber, courseNumber)
        if courseDictionary.get(newScheduledCourse) != None:
            newScheduledCourse = courseDictionary.get(newScheduledCourse)
            self.scheduledCourses.append(newScheduledCourse.number)
            self.addTree(newScheduledCourse)
            self.havePutNodesOnScreen = True

    def considerSpecialInputs(self):
        # Some shortcuts, mostly for myself.
        if self.courseEntry.get() == 'Clear': 
            self.clearGraph()
        if self.courseEntry.get() == 'cs':
            self.havePutNodesOnScreen = True
            self.addTree(csDegree)
        if self.courseEntry.get() == 'showme15':
            self.havePutNodesOnScreen = True
            self.showEligibleCourses()
        if self.courseEntry.get() == 'showAll':
            for takenCourse in self.takenCourses:
                course = courseDictionary.get(takenCourse)
                self.graph = self.recursivelyAddNodesToTree(course)
        if self.courseEntry.get() == 'la':
            self.addTree(linearAlgebraOptions)
        if self.courseEntry.get() == 'pr':
            self.addTree(probabilityOptions)
        if self.courseEntry.get() == 'math':
            self.addTree(mathCore)
        if self.courseEntry.get() == 'test1':
            self.addTree(testnode)
        if self.courseEntry.get() == 'test2':
            self.addTree(testnode2)
        if self.courseEntry.get() == "Instructions":
            self.havePutNodesOnScreen = False

    def addTree(self, node):
        # We can add either recursively down to the leaves of the tree,
        if self.recursiveAdd.get():
            self.graph = self.recursivelyAddNodesToTree(node)
        # Or just add immediate prereqs
        else:
            nodeTree = node.formTree()
            # Want to make sure we're not adding duplicate nodes.
            trivialGraph = DiGraph()
            assert(None not in nodeTree.nodes())
            for node in nodeTree.nodes():
                if node == None: continue
                node.initForTreeFormation()
                node.updateSatisfiability(self.takenCourses)
                if node in self.graph.nodes():
                    trivialGraph.addNode(node)
                else: pass
            nodeTree -= trivialGraph
            self.graph |= nodeTree

    def removeTree(self, node):
        if self.recursiveAdd.get():
            pass
        else:
            nodeTree = node.formTree()
            graphForDeletion = DiGraph()
            for parent in set(nodeTree.nodes()) - {node}:
                graphForDeletion.addNode(parent)
            self.graph -= graphForDeletion

    def recursivelyAddNodesToTree(self, course):
        # This function recurses through all prereqs all the way down to nodes
        # which have inDegree of 0.
        newGraph = self.graph
        newGraph |= course.formTree()
        if len(course.formTree().nodes()) == 1: # Only itself.
                newGraph |= course.formTree()
                return newGraph
        for node in set(course.formTree().nodes()) - {course}:
            if isinstance(node, Course) or isinstance(node, ChooseNode):
                newGraph |= self.recursivelyAddNodesToTree(node)
        return newGraph
        
    def showEligibleCourses(self):
        # Used for shortcut cmd 'showme15', which shows all the courses for
        # which the user is eligible in the CS department.
        for key in courseDictionary:
            if key[:2] == '15':
                course = courseDictionary.get(key)
                course.initForTreeFormation()
                course.updateSatisfiability(self.takenCourses)
                if course.isSatisfied:
                    self.addTree(course)                    

    def updateNodes(self):
        for node in self.graph.nodes():
            node.updatePosition(self.graph)

    def drawCourseInfo(self):
        if self.selectedNodes == []: return
        node = self.selectedNodes[0]
        self.drawName(node)
        if isinstance(node, Course): 
            self.drawDescription(node)
            self.drawUnits(node)

    def drawUnits(self, node):
        if node.units == None: return
        self.sidebar.create_text(10,33,anchor='nw',text='%d units' % node.units)

    ########################################################################
    # IMPORTANT!!! 
    # lengthToIthWord and justifyTest are NOT my code.
    # Taylor Bell, a current 112 student, wrote this for bonus this semester.
    # She has kindly allowed me to use it. I have adjusted it slightly to be
    # a class method.
    ########################################################################

    def lengthToIthWord(self, words, i):
    #includes spaces between words
        sumlength=0
        spacelength=0
        for x in range(i):
            sumlength+= len(words[x])
            spacelength= i-1
            final=sumlength+spacelength
        return final

    def justifyText(self, text, n):
        #lines up text all fancy with n characters on a line
        splittext, final=text.split(), ""
        while (self.lengthToIthWord(splittext, len(splittext))>n):
        #loops until last line
            i=1
            while(self.lengthToIthWord(splittext, i)<=n):
                i+=1
            splittext[i-2]=splittext[i-2]+'\n'
            #splitting lines up with correct number of words
            extraspace=n-self.lengthToIthWord(splittext, i-1)+1
            for j in range(i-2):
            #adds one space between words
                splittext[j]=splittext[j]+" "
            while(extraspace>0):
            #adds needed extra spaces between words
                for j in range(i-2):
                    splittext[j]=splittext[j]+' '
                    extraspace-=1
                    if (extraspace==0): break
            for k in splittext[:i-1]:
            #removes first line from splittext
                final+= str(k)
            splittext=splittext[i-1::]
            for l in range(len(splittext)):
            #takes away added spaces from other lines
                splittext[l]=splittext[l].strip()
        for i in range(len(splittext)-1):
        #adds spaces between words in last line
            splittext[i]=splittext[i]+" "
        for i in range(len(splittext)):
        #adds last line to final string
            final+=str(splittext[i])
        return final

    ########################################################################
    # All of the remaining code is mine.
    ########################################################################

    def drawDescription(self, node):
        self.sidebar.create_text(10,50,anchor='nw',
                                 text=self.justifyText(node.description,37)) 

    def drawName(self, node):
        if len(node.name) <= 23:
            self.sidebar.create_text(10,10,anchor='nw',text=node.name,
                                     font=('Georgia',20))
        else:
            textToDisplay = node.name[:23] + '...'
            self.sidebar.create_text(10,10,anchor='nw',text=textToDisplay,
                                     font=('Georgia',20))

    def redrawAll(self):
        if self.havePutNodesOnScreen == False:
            self.drawInstructions()
        for edge in self.graph.edges():
            self.graph.drawEdges(self.canvas) 
        for node in self.graph.nodes():
            node.updateSatisfiability(self.takenCourses)
            (node.fill, node.outline) = node.getColor(self)
            node.draw(self.canvas)
        self.drawCourseInfo()
        self.drawSampleNodes()

    def drawInstructions(self):
        verticalAdjust = 30
        horizontalAdjust = 120
        self.canvas.create_text(self.width / 2 - horizontalAdjust, 
                                self.height / 2 - 50 - verticalAdjust,
                                text = 'Welcome To CrsGrphr!',
                                font='Helvetica 26 bold')
        self.canvas.create_text(self.width / 2 - horizontalAdjust, 
                                self.height / 2 - verticalAdjust,
                                text='''
Type course numbers in the entry.
Type "Took " + (course number) to take a course.
Select nodes with the mouse.
"&" makes graph a single node.
"p" generates the given node's parents.
"Clear" clears the screen.''',
                                fill='black')

    def drawSampleNodes(self):
        # Draws the sample nodes at the bottom of the screen.
        colorScheme = {'taken':'#60B5D1','ineligible':'#E63740',
                       'eligible':'#91D63C','selected':'#FC7E00'}
        sampleNodeRadius = 20 # Aesthetically chosen
        spaceBetween = 90 # Likewise
        height = 700
        (node1X, node1Y) = (sampleNodeRadius + 10, height - sampleNodeRadius)
        (node2X, node2Y) = (node1X + spaceBetween + 2*sampleNodeRadius, node1Y)
        (node3X, node3Y) = (node2X + spaceBetween + 2*sampleNodeRadius, node2Y)
        self.canvas.create_oval(node1X-sampleNodeRadius,node1Y-sampleNodeRadius,
                                node1X+sampleNodeRadius,node1Y+sampleNodeRadius,
                                fill=colorScheme.get('taken'),
                                outline=colorScheme.get('taken'))
        self.canvas.create_text(node1X+sampleNodeRadius+10,
                                node1Y,
                                anchor='w',text=' - Taken')
        self.canvas.create_oval(node2X-sampleNodeRadius,node2Y-sampleNodeRadius,
                                node2X+sampleNodeRadius,node2Y+sampleNodeRadius,
                                fill=colorScheme.get('eligible'),
                                outline=colorScheme.get('eligible'))
        self.canvas.create_text(node2X+sampleNodeRadius+10,
                                node2Y,
                                anchor='w',text=' - Eligible')
        self.canvas.create_oval(node3X-sampleNodeRadius,node3Y-sampleNodeRadius,
                                node3X+sampleNodeRadius,node3Y+sampleNodeRadius,
                                fill=colorScheme.get('ineligible'),
                                outline=colorScheme.get('ineligible'))
        self.canvas.create_text(node3X+sampleNodeRadius+10,
                                node3Y,
                                anchor='w',text=' - Ineligible')

class DiGraph(GraphAnimation):
    nodeDistanceConstant = 75.0 # Arbitrarily chosen.
    springConstant = 7.0 # Arbitrarily chosen.
    repulsiveConstant = 2000.0 # Arbitrarily chosen.
    dampeningConstant = 1.0 # Arbitrarily chosen.
    lastSeenTime = time.time()
    deltaTime = time.time() - lastSeenTime

    def __init__(self): #, nodes, edges):
        self.vertexSet = set([]) #set(nodes)
        self.edgeSet = set([]) #set(edges)

    def addNode(self, node):
        self.vertexSet.add(node)

    def addEdge(self, *edge):
        assert(len(edge) == 2)
        # Just automatically add the nodes to the vertexSet
        self.vertexSet.add(edge[0])
        self.vertexSet.add(edge[1])
        self.edgeSet.add(edge)

    def nodes(self): return self.vertexSet

    def edges(self): return self.edgeSet

    def printEdges(self):
        for edge in self.edges():
            (node1, node2) = edge

    def __repr__(self):
        return 'DiGraph()'

    def __or__(self, other):
        # Uses bitwise operator OR to union two graphs.
        return self.union(other)

    def __sub__(self, other):
        # Acts as set difference.
        newGraph = DiGraph()
        newGraph.vertexSet = self.vertexSet - other.vertexSet
        newGraph.edgeSet = self.edgeSet - other.edgeSet
        return newGraph

    def union(self, other):
        newGraph = DiGraph()
        newGraph.vertexSet = self.vertexSet.union(other.vertexSet)
        newGraph.edgeSet = self.edgeSet.union(other.edgeSet)
        return newGraph

    def indexedUnion(self, listOfGraphs):
        unionGraph = DiGraph()
        for graph in listOfGraphs:
            unionGraph = unionGraph.union(graph)
        return unionGraph

    def adjacentEdges(self, node):
        adjacentEdgeSet = set([])
        for edge in self.edges():
            if node in edge:
                adjacentEdgeSet.add(edge)
        return adjacentEdgeSet

    def neighbors(self, node):
        neighborSet = set([])
        for edge in self.edges():
            if node in edge:
                for subnode in edge: neighborSet.add(subnode)
        return neighborSet - {node}

    def springForce(self, node1, node2):
        # Keeps connected nodes close to the optimal distance apart.
        (node1X, node1Y) = node1.location
        (node2X, node2Y) = node2.location
        desiredDistance = DiGraph.nodeDistanceConstant
        # CurrentDistance is a vector pointing toward node1
        currentDistance = (node1X - node2X, node1Y - node2Y)
        def normSquared(vector): return vector[0]**2 + vector[1]**2
        displacement = (normSquared(currentDistance)**0.5 - desiredDistance)
        scalar =- (DiGraph.springConstant*displacement /
                   (normSquared(currentDistance))**.5)
        return numpy.array((scalar*currentDistance[0], 
                           scalar*currentDistance[1]))

    def repulsiveForce(self, node1, node2):
        # Node that aren't connected repel each other.
        currentDistance = node1.location - node2.location
        def normSquared(vector): return vector[0]**2 + vector[1]**2
        n2 = normSquared(currentDistance)
        # Prevents dividing by very small numbers.
        if n2 < .01: n2 = 1
        scalar = DiGraph.repulsiveConstant / n2
        if n2 > 150**2: scalar = 0.0
        if isinstance(node1, ChooseNode) or isinstance(node2, ChooseNode): 
            return .5*scalar*currentDistance
        return scalar*currentDistance

    def drawEdges(self, canvas):
        for edge in self.edges(): self.drawEdge(canvas, edge)

    def drawEdge(self, canvas, edge):
        (firstNode, secondNode) = edge
        (node1X, node1Y) = firstNode.location
        (node2X, node2Y) = secondNode.location
        (midX, midY) = (.5*(node2X + node1X), .5*(node2Y + node1Y))
        canvas.create_line(node1X, node1Y, node2X, node2Y, fill='#AD9A7D')
        canvas.create_line(node1X,node1Y,midX,midY, fill='#AD9A7D',width=5)

    def fixPositionsOfCertainNodes(self):
        # Not used anymore, was used in earlier versions.
        self.fixedNodesStrs = []
        for node in self.nodes():
            if node.inDegree(self) == 0 and isinstance(node, Course):
                self.fixedNodesStrs.append(str(node))
        return self.fixedNodesStrs

class Node(DiGraph):
    gravity = numpy.array([0.0,9000.8]) # arbitrary
    graphWidth = 1040
    graphHeight = 710
    # No node added to the graph will be just a plain node. Every instance
    # will actually be an instance of a subclass. So we don't need a has 
    # function for nodes. Just ChooseNodes and Courses.
    def __init__(self):
        self.r = 25
        self.x = float(random.randint(self.r, Node.graphWidth - self.r))
        self.y = float(random.randint(self.r, Node.graphHeight - self.r))
        self.location = numpy.array((self.x, self.y))
        self.acceleration = numpy.array((0.0,0.0))
        self.velocity = numpy.array((0.0,0.0))
        #self.fill = '#0064C5'
        self.isSatisfied = False
        self.name = ''

    def getColor(self, animation):
        colorScheme = {'taken':'#60B5D1','ineligible':'#E63740',
                       'eligible':'#91D63C','selected':'#FC7E00'}
        self.updateSatisfiability(animation.takenCourses)
        if str(self) in animation.takenCourses:
            fill = colorScheme.get('taken')
        elif not self.isSatisfied: 
            fill = colorScheme.get('ineligible')
        elif self.isSatisfied: 
            fill = colorScheme.get('eligible')
        if self in animation.selectedNodes:
            outline = colorScheme.get('selected')
        elif self not in animation.selectedNodes:
            outline = fill
        return (fill, outline)

    def initForTreeFormation(self): pass # Subclass-specific

    def updateSatisfiability(self, usersTakenCourses): pass # Subclass-specific

    def inDegree(self, diGraph):
        counter = 0
        for edge in diGraph.edges():
            if self == edge[0]: counter += 1
        return counter

    def adjacentEdges(self, graph):
        return graph.adjacentEdges(self)

    def neighbors(self, graph):
        return graph.neighbors(self)

    def updatePosition(self, graph):
        # This line prevents isolated nodes from falling off the screen.
        if self.inDegree(graph) == 0: self.weight = 1
        dt = 1.0 / 30.0 # Rough approximation, just need a small number.
        originalLocation = self.location
        height = 720
        width = 1040
        # Gravity is 9.8 m/s**2
        self.acceleration = numpy.array([0.0,9.8])*self.weight
        for node in self.neighbors(graph):
            assert(node != None)
            self.acceleration += graph.springForce(self, node)
        for node in graph.nodes() - self.neighbors(graph):
            assert(node != None)
            self.acceleration += graph.repulsiveForce(self, node)
        # Dampening:
        self.acceleration -= DiGraph.dampeningConstant * self.velocity
        self.velocity += self.acceleration * dt
        self.location += self.velocity * dt
        # Prevents going off the top of the screen.
        if self.location[0] <= self.r: self.location[0] = float(self.r)
        if self.location[1] <= self.r: self.location[1] = float(self.r)
        if ((self.location[0] >= height - self.r) or 
            (self.location[1] >= width - self.r)):
            #print 'Offscreen!'
            self.location = originalLocation
        fixedNodes = graph.fixPositionsOfCertainNodes()
        # Nodes are always falling, we just adjust the screen center to appear
        # as if they're not.
        self.updateCenter(graph)

    def fixPosition(self, fixedNodes):
        width = 1040
        if str(self) in fixedNodes:
            fixedX = width*(fixedNodes.index(str(self)) + .5) / len(fixedNodes)
            fixedY = self.r + 1
            self.location = numpy.array([fixedX, fixedY])

    def updateCenter(self, graph):
        adjustX = 410.0 # Arbitrarily chosen for aesthetics
        adjustY = 260.0 # Likewise.
        total = numpy.array([0.0,0.0])
        for node in graph.nodes():
            total += node.location
        total /= -float(len(graph.nodes()))
        total += numpy.array([adjustX,adjustY])
        for node in graph.nodes():
            node.location += total

    def draw(self, canvas):
        colorScheme = {'taken':'#60B5D1','ineligible':'#E63740',
                       'eligible':'#91D63C','selected':'#FC7E00'}
        (x , y) = self.location
        (x, y) = (int(x), int(y))
        r = self.r
        if isinstance(self, ChooseNode):
            r -= 5 # Choose nodes are smaller.
            self.fill = '#AAEEEE'
            canvas.create_rectangle(x-r, y-r, x+r, y+r, fill=self.fill,
                                    outline=self.fill)
            canvas.create_text(x,y,text=str(self))
        else:
            if self.outline == colorScheme.get('selected'):
                selectR = r + 5
                canvas.create_oval(x-selectR, y-selectR, x+selectR, y+selectR, 
                                   fill=self.outline, outline=self.outline)
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.fill,
                               outline=self.fill,width=5)
            canvas.create_text(x,y,text=str(self),fill='white')

class Course(Node):
    def __init__(self, name, number, units, description, prereqs, coreqs):
        super(Course, self).__init__()
        self.name = name
        self.number = number
        self.units = units
        self.description = description
        self.prereqs = prereqs
        self.coreqs = coreqs
        self.hundredsPlace = int(number[3])
        # Choose a random location somewhere corresponding to it's 100-place
        # number. Since courses are weighted, it makes sense to put heavier
        # courses initially at the bottom.   
        self.y = random.randint(self.hundredsPlace*100-50, 
                                self.hundredsPlace*100+50)
        self.location = numpy.array([self.x, self.y])
        self.weight = self.hundredsPlace**3 
    
    def initForTreeFormation(self):
        # insideParans is a list, outsideParans is a string
        self.insideParans = self.parseForParantheticals(self.prereqs)
        # Splits on parantheticals, then grabs the relevent string
        self.outsideParans = self.splitOnParentheticals(self.prereqs)
        outsideParans = self.outsideParans
        self.outermostList = self.parseForCourseNumbers(self.outsideParans)
        self.outsideLogicalConnective=self.findLogicalConnective(outsideParans)

    def __repr__(self):
        return ('Course(%r, %r, %r, %r, %r, %r)' % (self.name, self.number, 
                self.units, self.description, self.prereqs, self.coreqs))

    def __str__(self): return self.number

    def __hash__(self):
        return hash(self.name)

    def updateSatisfiability(self, usersTakenCourses):
        if self.outsideLogicalConnective == '':
            # Either no prereqs or only one course as prereqs
            if len(self.parseForCourseNumbers(self.prereqs)) == 0:
                #print 'A'
                self.isSatisfied = True
                return
            elif len(self.parseForCourseNumbers(self.prereqs)) == 1:
                prereq = self.parseForCourseNumbers(self.prereqs)[0]
                self.isSatisfied = (prereq in usersTakenCourses)
                #print 'BB'
                return
        if self.outsideLogicalConnective == 'AND': # Must take all
            # If AND, all the outside courses must be satisfied

            for courseStr in self.parseForCourseNumbers(self.outsideParans):
                # If the user hasn't taken ONE of the outsideCourses...
                if courseStr not in usersTakenCourses:
                    #print 'B'
                    self.isSatisfied = False
                    return

            # So all the outside courses have been taken.
            # Now check the parans:
            for parans in self.insideParans:
                if self.findLogicalConnective(parans) == 'AND': # Must take all
                    for couseStr in self.parseForCourseNumbers(parans):
                        # If the user hasn't taken ONE of the paranCourses...
                        if courseStr not in usersTakenCourses:
                            #print 'C'
                            self.isSatisfied = False
                            return
                if self.findLogicalConnective(parans) == 'OR': # Must take one
                    counter = 0
                    for courseStr in self.parseForCourseNumbers(parans):
                        if courseStr in usersTakenCourses: counter += 1
                    # If the user hasn't take at least one course from the OR:
                    if counter == 0:
                        #print 'D'
                        self.isSatisfied = False
                        return

        if self.outsideLogicalConnective == 'OR': # Must take one

            counter = 0
            for courseStr in self.parseForCourseNumbers(self.outsideParans):
                if courseStr in usersTakenCourses: counter += 1
            if counter == 0: pass # Still need to check parans.
            else: # We're satisfied!
                #print 'E'
                self.isSatisfied = True
                return

            # Now we check parans. All we need is ONE of the overall parans
            # (or outside courses) to be satsifed.
            for parans in self.insideParans:
                if self.findLogicalConnective(parans) == 'AND': # Must take all
                    paranCounter = 0
                    print self.parseForCourseNumbers(parans)
                    for courseStr in self.parseForCourseNumbers(parans):
                        # If the user hasn't taken ONE of the paranCourses...
                        if courseStr not in usersTakenCourses:
                            pass
                        if courseStr in usersTakenCourses:
                            paranCounter += 1
                    if paranCounter == len(self.parseForCourseNumbers(parans)):
                        # We took all the inside courses and satisfied the
                        # outside or!
                        #print 'F'
                        self.isSatisfied = True
                        return
                if self.findLogicalConnective(parans) == 'OR': # Must take one
                    paranCounter = 0
                    for courseStr in self.parseForCourseNumbers(parans):
                        if courseStr in usersTakenCourses: paranCounter += 1
                    # If the user took a course in the parans, the parans are
                    # satisfied! So the overall OR structure is satisfied!
                    if paranCounter > 0:
                        #print 'G'
                        self.isSatisfied = True
                        return
            if counter == 0:
                # We didn't satisfy any of the outside courses of parans.
                #print 'GG'
                self.isSatisfied = False
                return
        # We got out and everything has been satisfied!
        #print 'H'
        self.isSatisfied = True
        return

    def parseForCourseNumbers(self, text):
        courseList = re.findall('[\\d]{2}.[\\d]{3}', text)
        returnList = []
        for course in courseList:
            # Creates list of Course class instances, not strings.
            if courseDictionary.get(course) != None: returnList.append(course)
        return returnList

    def parseForParantheticals(self, text): 
        # Returns a list.
        assert(type(text) == str)
        return re.findall('\([^)]*\)', text)

    def splitOnParentheticals(self, text):
        # This grabs the stuff outside parans
        prereqs = re.split('\([^)]*\)', text)
        for entry in prereqs:
            if 'and' in entry or 'or' in entry: return entry
        # If didn't find anything, there were no prereqs to begin with.
        # So just return the original text.
        return text

    def findLogicalConnective(self, text):
        if 'and' in text: return 'AND'
        elif 'or' in text: return 'OR'
        else: return ''

    def addOutsideNodes(self, tree):
        # Adds the prereqs that are not in parans
        outsideNodes = []
        for course in self.outermostList:
            if courseDictionary.get(course) != None:
                course = courseDictionary.get(course)
                assert(course != None)
                tree.addNode(course)
                outsideNodes.append(course)
                assert(len(tree.nodes()) == len(set(tree.nodes())))
            if isinstance(course, SpecialNode):
                print 'SpecialNode:',str(course)
                tree.addNode(course)
                outsideNodes.append(course)
            ################
            #print '--- addOutsideNodes ---'
            #self.debugPrint(tree)
            ################
        return outsideNodes

    def addInsideNodes(self, tree):
        # Iterates through the parantheticals and add them to the tree.
        newLogicNodes = []
        for parans in self.insideParans:
            paransLogicalConnective = self.findLogicalConnective(parans)
            coursesInParans = self.parseForCourseNumbers(parans)
            if paransLogicalConnective == 'OR':
                # Need the logical connective or node.
                paranslogicNode = ChooseNode([],1)
            else: paranslogicNode = ChooseNode(coursesInParans, 
                                               len(coursesInParans))
            newLogicNodes.append(paranslogicNode)
            ################
            #print '--- addInsideNodes ---'
            #self.debugPrint(tree)
            ################
            for course in coursesInParans:
                course = courseDictionary.get(course)
                # @TODO TEST ASSERTION HERE
                tree.addNode(course)
                tree.addEdge(paranslogicNode, course)
                assert(len(tree.nodes()) == len(set(tree.nodes())))
        return newLogicNodes

    def formTree(self):
        # This function takes the node's prereq string and turns it into a
        # an instance of the directed graph class. This function is a major
        # backbone of the project.
        self.initForTreeFormation()
        tree = DiGraph()
        root = self
        # We add the course itself to the tree.
        tree.addNode(root)
        ################
        #print 'formTree'
        #self.debugPrint(tree)
        ################
        # We first go through the parans, form their tree, then report back.
        parantheticalLogicNodes = self.addInsideNodes(tree)
        # We then grab the outside nodes.
        outsideNodes = self.addOutsideNodes(tree)
        if self.outsideLogicalConnective == 'AND':
            # Can connect directing to the root
            almostRoot = root
        elif self.outsideLogicalConnective == 'OR':
            # Make a new logical connective node. Add it to the graph,
            # connect it to the root.
            almostRoot = ChooseNode(parantheticalLogicNodes+outsideNodes, 1)
            tree.addEdge(root, almostRoot)
        # If there's no prereqs:
        elif self.outsideLogicalConnective == '': almostRoot = root
        # Iterate through all the nodes from parans and outside, connect them
        # to the new root.
        for node in parantheticalLogicNodes+outsideNodes:
            tree.addNode(node)
            tree.addEdge(almostRoot, node)
        return tree

    def debugPrint(self, tree):
        # For personal use.
        print '#####'
        print 'List: (len %d)' % len(tree.nodes())
        for course in sorted(tree.nodes()): print str(course)
        print 'Set: (len %d)' % len(set(tree.nodes()))
        for node in sorted(set(tree.nodes())): print str(node)

class ChooseNode(Node):
    # This is the main logical connective node class. An OR node has a
    # howManyMustBeChosen value of 1. An AND node's value is the
    # length of its parents.
    def __init__(self, parents, howManyMustBeChosen):
        super(ChooseNode, self).__init__()
        self.parents = parents
        self.howManyMustBeChosen = howManyMustBeChosen
        self.weight = 1

    def __repr__(self):
        return 'ChooseNode(%r, %r)' % (self.parents, self.howManyMustBeChosen)

    def __str__(self):
        # @TODO: change this back, real strs are edited out for visiblity
        # The commented-out code is kept for development use later if needed.
        stringOfParents = ''
        for parent in self.parents:
            stringOfParents += '%s, ' % parent 
        # Gets rid of last comma and space
        stringOfParents = stringOfParents[:len(stringOfParents)-2]
        if self.howManyMustBeChosen == 1:
            return 'OR'
            #return '(OR node with parents: %s)' % stringOfParents
        if self.howManyMustBeChosen == len(self.parents):
            #return '(AND node with parents: %s)' % stringOfParents
            return 'AND'
        #return '(Choose %d node with parents: %s)' % (self.howManyMustBeChosen,
        #                                           stringOfParents)
        return 'Choose %d Node' % self.howManyMustBeChosen

    def __hash__(self):
        # Every choose node will have a nonempty set of parents.
        return hash(tuple(self.parents))

    def updateSatisfiability(self, usersTakenCourses):
        counter = 0
        for course in usersTakenCourses:
            if course in self.parents: counter += 1
        self.isSatisfied = (counter >= self.howManyMustBeChosen)

    def formTree(self):
        graph = DiGraph()
        #print str(self)
        for parent in self.parents:
            #print type(parent)
            if type(parent) == str:
                parent = courseDictionary.get(parent)
            graph.addNode(parent)
            graph.addEdge(self, parent)
        return graph

class UnitCountNode(Node):
    # Generally comes up when you need X-many units of humanities electives.
    def __init__(self, parents, count):
        super(Node, self).__init__()
        self.parents = parents
        self.count = count

    def __str__(self):
        return 'UnitCountNode with count %s' % self.count

    def __repr__(self):
        return 'UnitCountNode(%r, %r)' % (self.parents, self.count)

    def __hash__(self):
        # Every choose unit node will have a nonempty set of parents.
        return hash(tuple(self.parents))

    def updateSatisfiability(self, usersTakenCourses):
        counter = 0
        for course in self.parents:
            if course in usersTakenCourses:
                counter += course.units
        return counter >= self.count

class SpecialNode(ChooseNode):
    # Basically just allows the user to choose what the str is.
    # Makes UI a lot prettier.
    def __init__(self, parents, howManyMustBeChosen, name):
        super(SpecialNode, self).__init__(parents, howManyMustBeChosen)
        self.weight = 10
        self.name = name

    def __str__(self):
        return self.name

courseDictionary = eval(open('courseDictionary','r').read())

def readFile(fileName):
    return eval(open('%s' % fileName, 'r').read())

##############################################################################
########################## HARDCODED CS DEGREE ###############################
##############################################################################

csCoreClasses = ['15-112','15-122','21-127','15-150','15-210','15-213','15-251',
                 '15-451','15-221']
csCore = SpecialNode(csCoreClasses, len(csCoreClasses),'CS Core')
algoElective = ['15-354','15-355','15-453','15-455','21-301','21-484']
algoElectiveNode = SpecialNode(algoElective,1,'Algo')
applicationElective = ['02-450', '05-391', '05-431', '05-433', '10-601', 
                       '11-411', '15-313', '15-322', '15-323', '15-381', 
                       '15-415', '15-462', '16-384', '16-385']
applicationElectiveNode = SpecialNode(applicationElective, 1,'Application')
logicElective = ['15-312', '15-317', '15-414', '15-424', '21-300', '80-310', 
                 '80-311']
logicElectiveNode = SpecialNode(logicElective,1,'Logic')
systemsElective = ['15-410', '15-411', '15-418', '15-440', '15-441']
systemsElectiveNode = SpecialNode(systemsElective, 1, 'Syst')
csElectives = []
csElectivesNode = SpecialNode(csElectives,1,'CS Electives')
linearAlgebraOptions = SpecialNode(['21-241','21-242','21-341'], 1,
                                   'Linear Algebra')
probabilityOptions = SpecialNode(['15-359', '21-325', '36-217', '36-225'], 1,
                                 'Probability')
mathCore = SpecialNode([linearAlgebraOptions, probabilityOptions,
                       '21-120', '21-122'], 4,'Math')
testnode2 = SpecialNode(['15-110'],1,'test2')
testnode = SpecialNode([testnode2],1,'test')
labRequirement = SpecialNode(['02-261', '03-124', '03-121', '09-101', '09-105', 
                             '09-221', '15-321', '27-100', '33-104', '42-203', 
                             '03-206', '85-310'], 1, 'Lab')
sciEngCore = SpecialNode([labRequirement], 1,'Sci/Eng')
humanities = UnitCountNode([], 63)
minor = []
csDegreeParents = [csCore, 
                   algoElectiveNode, 
                   logicElectiveNode,
                   applicationElectiveNode,
                   logicElectiveNode,
                   systemsElectiveNode, 
                   mathCore, 
                   sciEngCore, 
                   csElectivesNode
                   ]
csDegree = SpecialNode(csDegreeParents, len(csDegreeParents),'CS')

coureDictionary = readFile('courseDictionary')

def replaceStringsWithCourses():
    for requirement in [csCoreClasses, algoElective, applicationElective,
                        logicElective, systemsElective, csElectives, 
                        linearAlgebraOptions.parents, 
                        probabilityOptions.parents, 
                        mathCore.parents, labRequirement.parents,
                        sciEngCore.parents,  
                        humanities.parents, minor]:
        for i in xrange(len(requirement)): 
            if courseDictionary.get(requirement[i]) != None:
                requirement[i] = courseDictionary.get(requirement[i])

replaceStringsWithCourses()

##############################################################################
##############################################################################
##############################################################################

graphAnimation = GraphAnimation(DiGraph())
#graphAnimation.run()
