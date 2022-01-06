import os

# Import the puzzle modules
for x in os.listdir("data"):
	if x.endswith(".py") and x != "__init__.py":
		exec("from . import "+x.replace(".py", ""))


def loadPuzzle( puzzlename = "E2ncud" ):

	if os.environ.get('PUZZLE') != None:
		puzzlename = os.environ.get('PUZZLE')
		print('[ Env PUZZLE found :', puzzlename, ' ]')

	p = None

	if puzzlename in [ "Tomy_EternityII", "EternityII", "E2" ]:
		p = tomy_EternityII.Tomy_EternityII()
	elif puzzlename in [ "E2nc", "E2clueless", "E2noclue", "E2noclues" ]:
		p = tomy_EternityII.Tomy_EternityII(with_clues=False)
	elif puzzlename in [ "E2ncud", "E2cluelessupsidedown", "E2noclueud", "E2nocluesud" ]:
		p = tomy_EternityII.Tomy_EternityII(with_clues=False, upside_down=True)
	elif puzzlename in [ "JB", "jb", "blackwood", "b" ]:
		p = tomy_EternityII_Blackwood.Tomy_EternityII_Blackwood()
	elif puzzlename in [ "Tomy_4x4", "T4x4", "4x4" ]:
		p = tomy_4x4.Tomy_4x4()
	elif puzzlename in [ "Brendan_12x12", "B12x12", "12x12" ]:
		p = brendan_12x12.Brendan_12x12()
	elif puzzlename in [ "Brendan_08x08f", "B8x8f", "8x8f" ]:
		p = brendan_08x08.Brendan_08x08(with_fixed=True)
	elif puzzlename in [ "Brendan_08x08", "B8x8", "8x8" ]:
		p = brendan_08x08.Brendan_08x08()
	elif puzzlename in [ "Brendan_07x07", "B7x7" ]:
		p = brendan_07x07.Brendan_07x07()
	elif puzzlename in [ "Brendan_06x06", "B6x6", "6x6" ]:
		p = brendan_06x06.Brendan_06x06()

	if p == None:
		print( "ERROR: Unknown puzzle: ", puzzlename)
		exit()

	return p

