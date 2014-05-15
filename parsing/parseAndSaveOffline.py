# parseAndSaveOffline.py

from nodeClasses import *
import re
import urllib2
import networkx as nx

# CMU's course data is available online at this address
urlPrefix = 'http://coursecatalog.web.cmu.edu/ribbit/?page=getcourse.rjs&code='

def extractName(description):
    # If doesn't have a name, don't do anything.
    if len(re.split('keepwithnext">[\\d]{2}.[\\d]{3} ', 
                    description)) == 1: return None
    # That string appears cryptic, but it's simply how the website displays info
    name = re.split('keepwithnext">[\\d]{2}.[\\d]{3} ',
                    description)[1]
    # Same story here.
    name = re.split('</dt>', name)[0] # Cut off the extra junk after the name.
    return name

def extractDescription(description):
    if len(re.findall('<br />.*<br />', description)) == 0: return None
    # Formatted consistently as second entry in this list.
    descriptionString = re.split('<br />', description)[1]
    return descriptionString

def extractUnits(description):
    # Find all things that look like this, and grab the first one.
    if len(re.findall('[0-9]{1,2} units?', description)) == 0: return None
    unitString = re.findall('[0-9]{1,2} units?', description)[0]
    # Splits on the space, takes the number prior to it and turns it into int.
    units = int(re.split(' ', unitString)[0])
    return units

def extractPrereqs(description):
    if len(re.split('Prerequisites?:', description)) == 1:
        return ''
    # Split on "Prerequisites:", grab second half
    coursePrereqs = re.split('Prerequisites?: ', description)[1]
    # Split on ".<br" (which typically follows the end of prereqs)
    # and grab the first half.
    coursePrereqs = re.split('.<br', coursePrereqs)[0]
    # @TODO add test cases to make sure that the output is of a valid form
    return coursePrereqs

def extractCoreqs(description):
    # Identical to extractPrereqs in almost every way.
    if len(re.split('Corequisites?:', description)) == 1:
        return None
    # Split on "Prerequisites:", grab second half
    coursePrereqs = re.split('Corequisites?: ', description)[1]
    # Split on ".<br" (which typically follows the end of prereqs)
    # and grab the first half.
    coursePrereqs = re.split('.<br', coursePrereqs)[0]
    # @TODO add test cases to make sure that the output is of a valid form
    return coursePrereqs

def parseForCourseNumbers(prereqs):
    assert(type(prereqs) == str)
    return re.findall('[\\d]{2}.[\\d]{3}', prereqs)

def parseForParantheticals(prereqs):return re.findall('\([^)]*\)', prereqs)

def splitOnParentheticals(prereqs):
    # This grabs the stuff outside parans
    prereqs = re.split('\([^)]*\)', prereqs)
    for entry in prereqs:
        if 'and' in entry or 'or' in entry: return entry

def findLogicalConnective(text):
    #for entry in outsideParans:
    if 'and' in text: 
        return 'AND'
    return 'OR'

citDepartmentNumbers = [42, 39, 12, 06, 18, 19, 04, 14, 24, 27, 96]
cfaDepartmentNumbers = [48, 60, 62, 51, 54, 57]
heinzCollegeDepartmentNumbers = [95, 93, 94, 90, 92, 91]
dietrichDepartmentNumbers = [86, 73, 76, 79, 65, 66, 67, 82, 80, 85, 88, 36]
mcsDepartmentNumbers = [03, 9, 38, 21, 33]
scsDepartmentNumbers = [02, 15, 5, 8, 11, 10, 16, 17]
tepperDepartmentNumbers = [70, 45, 46, 47]
cmuWideDepartmentNumbers = [53, 69, 30, 31, 32, 98, 99]

#smallForSakeOfDemonstration = [03, 18]

allDepartments = (citDepartmentNumbers + cfaDepartmentNumbers + 
                  heinzCollegeDepartmentNumbers + dietrichDepartmentNumbers +
                  mcsDepartmentNumbers + scsDepartmentNumbers 
                  + tepperDepartmentNumbers + cmuWideDepartmentNumbers)

departmentToParse = re.findall('[\\d]{1,2}',
                               raw_input('Enter department numbers to parse: '))
dictionaryToMake = raw_input('Enter the name of the file you wish to make: ')
externalCourseRepository = open(dictionaryToMake, 'w')


def getCourseInfo(departmentNumbers):
    departmentNumbers = [int(entry) for entry in departmentNumbers]
    print departmentNumbers
    allPossibleCourses = ['%02d-%03d' % (departmentNumber, courseNumber)
                          for departmentNumber in departmentNumbers 
                          for courseNumber in xrange(500)]
    # coursePrereqsDictionary = dict()
    courseDictionary = dict([])
    for number in allPossibleCourses:
        # Opens the webpage and converts it to a string.
        description = urllib2.urlopen(urlPrefix + number).read()
        # Parse the string for name, prereqs, and coreqs.
        name = extractName(description)
        # Since we're iterating through every possible course number,
        # we'll hit lots of non-existent courses. That's why this 
        # conditional is here.
        if name != None:
            print number
            units = extractUnits(description)
            actualDescription = extractDescription(description)
            prereqs = extractPrereqs(description)
            # prereqsTree = formTree(coursePrereqsString)
            # If we don't have prereqs, the prereqs set is empty.
            if prereqs != None:
                print prereqs
            coreqsString = extractCoreqs(description)
            # Create courseNumber Key in courseDictionary
            print 
            print 'Creating instance of course...',
            # Create an instance of the Course class.
            course = Course(name, number, units, actualDescription, 
                            prereqs, coreqsString)
            print str(course)
            print repr(course)
            courseDictionary[course.number] = course
            #externalCourseRepository.write(repr(courseDictionary))
    # Push this dictionary to a text file.
    return courseDictionary


externalCourseRepository.write(repr(getCourseInfo(departmentToParse)))
