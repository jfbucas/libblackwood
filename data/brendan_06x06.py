import puzzle

class Brendan_06x06( puzzle.Puzzle ):
	"""The Brendan 06x06 puzzle"""

	name = "brendan/pieces_06x06.txt.js"
	aliases = [ "Brendan_06x06", "B6x6", "6x6" ]

	def __init__( self, extra_fixed=[] ):

		self.motifs_order = "jef"
		self.upside_down = False

		self.board_w = 6
		self.board_h = 6

		self.pieces = [
			[0,0,1,1],
			[0,0,1,3],
			[0,0,2,2],
			[0,0,2,3],
			[0,1,6,1],
			[0,1,6,2],
			[0,1,8,1],
			[0,1,8,2],
			[0,1,8,3],
			[0,2,4,1],
			[0,2,5,1],
			[0,2,6,2],
			[0,2,6,3],
			[0,2,7,3],
			[0,3,4,2],
			[0,3,4,3],
			[0,3,5,1],
			[0,3,6,2],
			[0,3,7,1],
			[0,3,8,2],
			[4,4,7,5],
			[4,5,5,5],
			[4,5,8,8],
			[4,6,6,7],
			[4,6,7,8],
			[4,7,6,5],
			[4,7,7,5],
			[4,7,7,7],
			[4,8,5,6],
			[4,8,5,7],
			[4,8,7,6],
			[4,8,7,8],
			[5,6,5,7],
			[5,6,6,8],
			[5,6,7,8],
			[5,8,6,8],
		]

		# Fixed piece,space,rotation
		self.fixed = [
			[ 0,0,1 ], # we fix a corner
		]

		# Add extra fixed
		self.fixed.extend(extra_fixed)

		puzzle.Puzzle.__init__( self )

puzzle.global_list.append(Brendan_06x06)
