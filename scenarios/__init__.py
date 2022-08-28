import os
import scenario


# Import the scenarios modules
for x in os.listdir("scenarios"):
	if x.endswith(".py") and x != "__init__.py":
		exec("from . import "+x.replace(".py", ""))


def loadScenario( puzzle, name = "JB470" ):

	if os.environ.get('SCENARIO') != None:
		name = os.environ.get('SCENARIO')
		if os.environ.get('QUIET') == None:
			print('[ Env SCENARIO found :', name, ' ]')


	# Try to match the name with one of the classes imported
	for x in scenario.global_list:
		if name.lower() == x.__name__.lower():
			return x(puzzle)

	puzzle.error( "ERROR: Unknown scenario: '"+ name +"'")
	exit()

