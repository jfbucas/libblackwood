import puzzle

class Brendan_10x10( puzzle.Puzzle ):
	"""The Brendan 10x10 puzzle"""

	name = "brendan/pieces_10x10.txt.js"
	aliases = [ "Brendan_10x10", "B10x10", "10x10", "axa", "AxA" ]

	def __init__( self, extra_fixed=[] ):

		self.motifs_order = "jef"
		self.upside_down = False

		self.board_w = 10
		self.board_h = 10

		self.pieces = [

			[0,0,1,1],
			[0,0,1,3],
			[0,0,3,1],
			[0,0,4,1],
			[0,1,7,4],
			[0,1,8,3],
			[0,1,9,2],
			[0,1,10,2],
			[0,1,11,3],
			[0,1,11,4],
			[0,1,14,2],
			[0,2,6,2],
			[0,2,6,3],
			[0,2,7,3],
			[0,2,8,3],
			[0,2,10,4],
			[0,2,11,2],
			[0,2,12,3],
			[0,2,13,1],
			[0,2,14,1],
			[0,3,6,4],
			[0,3,7,1],
			[0,3,8,3],
			[0,3,9,2],
			[0,3,11,4],
			[0,3,12,1],
			[0,3,12,3],
			[0,3,13,1],
			[0,4,5,1],
			[0,4,5,2],
			[0,4,8,2],
			[0,4,9,4],
			[0,4,10,4],
			[0,4,11,2],
			[0,4,11,4],
			[0,4,12,4],
			[5,5,5,11],
			[5,5,5,13],
			[5,5,11,11],
			[5,5,13,11],
			[5,6,8,14],
			[5,6,9,7],
			[5,6,13,13],
			[5,7,9,8],
			[5,7,10,13],
			[5,8,6,14],
			[5,8,10,8],
			[5,8,14,13],
			[5,9,6,9],
			[5,9,7,11],
			[5,9,7,12],
			[5,10,13,10],
			[5,11,8,10],
			[5,12,12,7],
			[5,12,13,12],
			[5,13,14,14],
			[5,14,12,14],
			[5,14,13,10],
			[6,6,12,10],
			[6,6,12,13],
			[6,6,14,12],
			[6,7,7,12],
			[6,7,10,7],
			[6,7,14,7],
			[6,8,12,9],
			[6,9,6,10],
			[6,9,13,14],
			[6,10,9,12],
			[6,10,13,11],
			[6,11,11,10],
			[6,13,7,9],
			[6,13,8,8],
			[6,13,8,9],
			[6,13,12,13],
			[6,14,9,8],
			[6,14,11,13],
			[7,7,13,8],
			[7,8,8,8],
			[7,8,11,10],
			[7,9,8,8],
			[7,9,9,8],
			[7,9,11,12],
			[7,10,10,11],
			[7,10,10,12],
			[7,10,13,8],
			[7,11,14,10],
			[7,14,10,13],
			[7,14,11,9],
			[7,14,14,13],
			[8,9,14,12],
			[8,10,12,12],
			[8,11,14,12],
			[8,14,11,14],
			[8,14,12,9],
			[9,9,12,11],
			[9,11,14,10],
			[9,13,13,12],
			[9,14,10,11],
			[10,13,11,12],
			[10,14,11,12]

		]

		# Fixed piece,space,rotation
		self.fixed = [
			[ 0,0,1 ], # we fix a corner
		]

		# Add extra fixed
		self.fixed.extend(extra_fixed)

		puzzle.Puzzle.__init__( self )

puzzle.global_list.append(Brendan_10x10)
