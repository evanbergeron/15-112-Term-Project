import sqlite3
conn = sqlite3.connect('courses.db')

c = conn.cursor()

for row in c.execute("""select name, number, units prereqs 
                     from courses where number like '21-%%%'"""):
    print row