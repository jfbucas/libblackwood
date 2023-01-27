import os
import puzzle

# Import the puzzle modules
for x in os.listdir("data"):
	if x.endswith(".py") and x != "__init__.py":
		exec("from . import "+x.replace(".py", ""))


def loadPuzzle( name = "E2ncud", extra_fixed=[]):

	if os.environ.get('PUZZLE') != None:
		name = os.environ.get('PUZZLE')
		if os.environ.get('QUIET') == None:
			print('[ Env PUZZLE found :', name, ' ]')

	if os.environ.get('PREFIX') != None:
		extra_prefix = eval(os.environ.get('PREFIX'))
		if os.environ.get('QUIET') == None:
			print('[ Env PREFIX found :', extra_prefix, ' ]')
	"""
	p = None

	if name in [ "Tomy_EternityII", "EternityII", "E2" ]:
		p = tomy_EternityII.Tomy_EternityII(extra_fixed)
	elif name in [ "E2nc", "E2clueless", "E2noclue", "E2noclues" ]:
		p = tomy_EternityII.Tomy_EternityII(extra_fixed, with_clues=False)
	elif name in [ "E2ncud", "E2cluelessupsidedown", "E2noclueud", "E2nocluesud" ]:
		p = tomy_EternityII.Tomy_EternityII(extra_fixed, with_clues=False, upside_down=True)
	elif name in [ "JB", "jb", "blackwood", "b" ]:
		p = tomy_EternityII_Blackwood.Tomy_EternityII_Blackwood(extra_fixed)
	elif name in [ "Tomy_4x4", "T4x4", "4x4" ]:
		p = tomy_4x4.Tomy_4x4(extra_fixed)
	elif name in [ "Brendan_12x12", "B12x12", "12x12" ]:
		p = brendan_12x12.Brendan_12x12(extra_fixed)
	elif name in [ "Brendan_10x10", "B10x10", "10x10", "axa", "AxA" ]:
		p = brendan_10x10.Brendan_10x10(extra_fixed)
	elif name in [ "Brendan_08x08f", "B8x8f", "8x8f" ]:
		p = brendan_08x08.Brendan_08x08(extra_fixed, with_fixed=True)
	elif name in [ "Brendan_08x08", "B8x8", "8x8" ]:
		p = brendan_08x08.Brendan_08x08(extra_fixed)
	elif name in [ "Brendan_07x07", "B7x7" ]:
		p = brendan_07x07.Brendan_07x07(extra_fixed)
	elif name in [ "Brendan_06x06", "B6x6", "6x6" ]:
		p = brendan_06x06.Brendan_06x06(extra_fixed)

	if p == None:
		print( "ERROR: Unknown puzzle: ", name)
		exit()

	return p
	"""

	# Try to match the name with one of the classes imported
	for x in puzzle.global_list:
		if name in x.aliases:
			return x(alias=name, extra_fixed=extra_fixed)

	print( "ERROR: Unknown puzzle: ", name)
	exit()
