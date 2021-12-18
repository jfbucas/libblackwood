import os
import scenario


for x in os.listdir("scenarios"):
	if x.endswith(".py") and x != "__init__.py":
		exec("from . import "+x.replace(".py", ""))



def loadScenario( puzzle, name = "JB470" ):
	import os

	if os.environ.get('SCENARIO') != None:
		name = os.environ.get('SCENARIO')
		print('[ Env SCENARIO found :', name, ' ]')


	for x in scenario.global_list:
		if name.lower() == x.__name__.lower():
			return x(puzzle)

	puzzle.error( "ERROR: Unknown scenario: "+ name)
	exit()

