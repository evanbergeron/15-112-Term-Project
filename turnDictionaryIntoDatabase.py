import sqlite3
from termProject import *
conn = sqlite3.connect('courses.db')

c = conn.cursor()

c.execute('''CREATE TABLE courses (name, number, units, description, prereqs, coreqs);''')

courseDictionary = eval(open('courseDictionary','r').read())


def formatStringForSQL(description):
    description = getRidOfSingleQuotes(description)
    description = removeDoubleQuotes(description)
    return description

def removeDoubleQuotes(description):
    newDescription = ''
    for part in description.split('"'): newDescription += part
    return newDescription

def getRidOfSingleQuotes(quote):
    quoteList = quote.split("'")
    newQuote = ''
    for part in quoteList: newQuote += part
    return newQuote

for key in courseDictionary:
    course = courseDictionary.get(key)
    if course.name != None: name = formatStringForSQL(course.name)
    if course.description != None: description = formatStringForSQL(course.description)
    units = course.units
    if units == None: 
        print 'changed units'
        units = 0
    sqlCommand = ("INSERT INTO courses VALUES ('%s', '%s', %d, '%s', '%s', '%s');"
                  % (name, course.number, units,
                     description, course.prereqs, course.coreqs))
    print sqlCommand
    print
    c.execute(sqlCommand)
    conn.commit()
conn.close()
