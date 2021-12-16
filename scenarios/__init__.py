from . import jb469
from . import jb470
from . import jb471

from . import jb470circle
from . import jb470diag
from . import jb470rowscan
from . import jb470tiles64
from . import jb470tiles64diag

from . import rowscan


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

	elif name in [ "rowscan" ]:
		s = rowscan.RowScan(puzzle)

	if s == None:
		print( "ERROR: Unknown scenario: ", name)

	return s

