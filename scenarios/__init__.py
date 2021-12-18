import os

for x in os.listdir("scenarios"):
	if x.endswith(".py") and x != "__init__.py":
		exec("from . import "+x.replace(".py", ""))



def loadScenario( puzzle, name = "JB470" ):
	import os

	if os.environ.get('SCENARIO') != None:
		name = os.environ.get('SCENARIO')
		print('[ Env SCENARIO found :', name, ' ]')

	s = None

	if name in [ "JB471" ]:
		s = jb471.JB471(puzzle)
	elif name in [ "JB470" ]:
		s = jb470.JB470(puzzle)
	elif name in [ "JB469" ]:
		s = jb469.JB469(puzzle)


	elif name in [ "JB470circle" ]:
		s = jb470circle.JB470Circle(puzzle)
	elif name in [ "JB470diag" ]:
		s = jb470diag.JB470Diag(puzzle)
	elif name in [ "JB470rowscan" ]:
		s = jb470rowscan.JB470RowScan(puzzle)
	elif name in [ "JB470tiles64" ]:
		s = jb470tiles64.JB470Tiles64(puzzle)
	elif name in [ "JB470tiles64diag" ]:
		s = jb470tiles64diag.JB470Tiles64Diag(puzzle)
	elif name in [ "JB470tiles64diag2" ]:
		s = jb470tiles64diag2.JB470Tiles64Diag2(puzzle)
	elif name in [ "JB470tiles64diag3" ]:
		s = jb470tiles64diag3.JB470Tiles64Diag3(puzzle)
	elif name in [ "JB470tiles64diag4" ]:
		s = jb470tiles64diag4.JB470Tiles64Diag4(puzzle)

	elif name in [ "rowscan" ]:
		s = rowscan.RowScan(puzzle)

	if s == None:
		print( "ERROR: Unknown scenario: ", name)
		exit()

	return s

