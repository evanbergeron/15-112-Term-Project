My term project for CMU's 15-112 Intro To Programming class. Scrapes the web for course information using regular expressions. Generates directed graphs representing prerequisite structure.

The intent of the program is to provide users with a prettier interface to navigate courses and course prerequisites at CMU. By having a centralized location for courses and their description, CrsGrphr lets the user easily examine courses they may wish to take for their major.

There are a couple major parts of the project.

    1) Scrape data from the web.
    2) Organize this data for offline storage.
    3) Create a graph of prereqs based on user input.
    4) Present this data usefully to the user.

1) Is accomplished using regex and python's urllib2 library. The program grabs data from an XML file online and scrapes for name, number, description, units, prereqs, and coreqs.

2) A Course class is created, in order to store this data usefully. A dictionary is created offline mapping strings of course numbers to instances of the course class. Python reads this dictionary and loads it into the program.

3) Here, the goal is to turn a course's prerequisites into a directed graph in the obvious way. Since prerequisite strings are consistently formatted, this is possible to automate (and would be unfeasible otherwise). For this task, the DiGraph, Node, Course, ChooseNode, UnitCountNode, and SpecialNode classes are created.

The method formTree inside the node class is the function that creates an instance of the directed graph class from the prerequisite string. It analyzes the prerequisite structure and adds nodes and edges to the graph as is appropriate. When the user inputs new classes, the vertex set and edge set are union-ed together to form a new graph.

The formTree method is named as such as all prerequisite graphs are connected and acyclic.

4) The UI is kept simple for clarity's sake. The left sidebar displays info about the currently selected course and the majority of the screen depicts the course graph. The primary intent of the UI is to stand in direct contrast to Academic Audit's ugly UI.

Note that the SQL database hasn't been implemented yet and is a work in progress.

If you want to use the code, just run python on termProject.py. No external modules are used.
