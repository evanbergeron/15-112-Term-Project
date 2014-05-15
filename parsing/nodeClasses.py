# nodeClasses.py

import networkx as nx
import re

# All of the useful code in nodeClasses.py is included in termProject.py
# It's presence in this submission is simply to let parseAndSaveOffline.py
# work properly.

class Node(object):
    # No node added to the graph will be just a plain node. Every instance
    # will actually be an instance of a subclass. So we don't need a has 
    # function for nodes. Just ChooseNodes and Courses.
    def __init__(self):
        # These eventually need to become functions of something
        self.x = None
        self.y = None
        self.r = None
        self.fill = None
        self.isSatisfied = False

class Course(Node):
    def __init__(self, name, number, units, description, prereqs, coreqs):
        super(Course, self).__init__()
        self.name = name
        self.number = number
        self.units = units
        self.description = description
        self.prereqs = prereqs
        self.coreqs = coreqs
        # insideParans is a list, outsideParans is a string

    def initForTreeFormation(self):
        self.insideParans = self.parseForParantheticals(self.prereqs)
        # Splits on parantheticals, then grabs the relevent string
        self.outsideParans = self.splitOnParentheticals(self.prereqs)
        self.outermostList = self.parseForCourseNumbers(self.outsideParans)
        self.outsideLogicalConnective = self.findLogicalConnective(self.outsideParans)


    def __repr__(self):
        return ('Course(%r, %r, %r, %r, %r, %r)' % (self.name, self.number, 
                self.units, self.description, self.prereqs, self.coreqs))

    def __str__(self): return self.number

    def __hash__(self):
        return hash(self.name)

    def updateSatisfiability(self, usersTakenCourses):
        self.isSatisfied = (self.number in sersTakenCourses)

    def parseForCourseNumbers(self, text):
        courseList = re.findall('[\\d]{2}.[\\d]{3}', text)
        returnList = []
        for course in courseList:
            if cs.get(course) != None: returnList.append(course)
        return returnList

    def parseForParantheticals(self, text): 
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
        #for entry in outsideParans:
        if 'and' in text: return 'AND'
        elif 'or' in text: return 'OR'
        else: return None

    def addOutsideNodes(self, tree):
        #orNode = ChooseNode([],1)
        outsideNodes = []
        for course in self.outermostList:
            if cs.get(course) != None:
                course = cs.get(course)
                assert(course != None)
                tree.add_node(course)
                outsideNodes.append(course)
                assert(len(tree.nodes()) == len(set(tree.nodes())))
            ################
            #print '--- addOutsideNodes ---'
            #self.debugPrint(tree)
            ################
            #tree.add_edge(root, orNode)
        return outsideNodes

    def addInsideNodes(self, tree):
        newLogicNodes = []
        #print self.number, ':', self.insideParans
        for parans in self.insideParans:
            paransLogicalConnective = self.findLogicalConnective(parans)
            coursesInParans = self.parseForCourseNumbers(parans)
            print paransLogicalConnective
            if paransLogicalConnective == 'OR':
                paranslogicNode = ChooseNode([],0)
            else: paranslogicNode = ChooseNode(coursesInParans, 
                                               len(coursesInParans))
            #tree.add_edge(newRoot, paranslogicNode)
            newLogicNodes.append(paranslogicNode)
            ################
            #print '--- addInsideNodes ---'
            #self.debugPrint(tree)
            ################
            for course in coursesInParans:
                course = cs.get(course)
                # @TODO TEST ASSERTION HERE
                tree.add_node(course)
                tree.add_edge(paranslogicNode, course)
                assert(len(tree.nodes()) == len(set(tree.nodes())))
        return newLogicNodes

    def formTree(self):
        self.initForTreeFormation()
        tree = nx.DiGraph()
        root = self
        tree.add_node(root)
        ################
        #print 'formTree'
        #self.debugPrint(tree)
        ################
        parantheticalLogicNodes = self.addInsideNodes(tree)
        #print parantheticalLogicNodes
        outsideNodes = self.addOutsideNodes(tree)
        if self.outsideLogicalConnective == 'AND':
            almostRoot = root
        elif self.outsideLogicalConnective == 'OR':
            almostRoot = ChooseNode(parantheticalLogicNodes+outsideNodes, 1)
            #print almostRoot
            tree.add_edge(root, almostRoot)
        elif self.outsideLogicalConnective == None: almostRoot = root
        for node in parantheticalLogicNodes+outsideNodes:
            tree.add_edge(almostRoot, node)
        return tree

    def debugPrint(self, tree):
        print '#####'
        print 'List: (len %d)' % len(tree.nodes())
        for course in sorted(tree.nodes()): print str(course)
        print 'Set: (len %d)' % len(set(tree.nodes()))
        for node in sorted(set(tree.nodes())): print str(node)

class ChooseNode(Node):
    def __init__(self, parents, howManyMustBeChosen):
        super(ChooseNode, self).__init__()
        self.parents = parents
        self.howManyMustBeChosen = howManyMustBeChosen

    def __repr__(self):
        return 'ChooseNode(%r, %r)' % (self.parents, self.howManyMustBeChosen)

    def __str__(self):
        stringOfParents = ''
        for parent in self.parents:
            stringOfParents += '%s, ' % parent 
        # Gets rid of last comma and space
        stringOfParents = stringOfParents[:len(stringOfParents)-2]
        if self.howManyMustBeChosen == 1:
            return '(OR node with parents: %s)' % stringOfParents
        if self.howManyMustBeChosen == len(self.parents):
            return '(AND node with parents: %s)' % stringOfParents
        return '(Choose %d node with parents: %s)' % (self.howManyMustBeChosen,
                                                   stringOfParents)

    def __hash__(self):
        # Every choose node will have a nonempty set of parents.
        return hash(tuple(self.parents))

    def updateSatisfiability(self, usersTakenCourses):
        counter = 0
        for course in usersTakenCourses:
            if course in self.parents: counter += 1
        self.isSatisfied = (counter >= self.howManyMustBeChosen)

class UnitCountNode(Node):
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

cs = eval(open('courseDictionary','r').read())
