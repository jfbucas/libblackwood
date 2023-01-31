import os
import puzzle

# Import the puzzle modules
for x in os.listdir("data"):
	if x.endswith(".py") and x != "__init__.py":
		exec("from . import "+x.replace(".py", ""))


def loadPuzzle( name="E2ncud", params={}):

	if os.environ.get('PUZZLE') != None:
		name = os.environ.get('PUZZLE')
		if os.environ.get('QUIET') == None:
			print('[ Env PUZZLE found :', name, ' ]')

	if os.environ.get('PARAMS') != None:
		params = eval(os.environ.get('PARAMS'))
		if os.environ.get('QUIET') == None:
			print('[ Env PARAMS found :', params, ' ]')

	# Try to match the name with one of the classes imported
	for x in puzzle.global_list:
		if name in x.aliases:
			params["alias"] = name
			return x(params=params)

	print( "ERROR: Unknown puzzle: ", name)
	exit()
