import puzzle

class Brendan_12x12( puzzle.Puzzle ):
	"""The Brendan 12x12 puzzle"""

	def __init__( self ):

		self.name = "brendan/pieces_12x12.txt.js"
		self.motifs_order = "jef"
		self.upside_down = False

		self.board_w = 12
		self.board_h = 12

		self.pieces = [

			[0,0,1,1],
			[0,0,3,2],
			[0,0,4,1],
			[0,0,4,4],
			[0,1,5,2],
			[0,1,5,3],
			[0,1,7,1],
			[0,1,7,2],
			[0,1,8,2],
			[0,1,8,4],
			[0,1,11,2],
			[0,1,13,4],
			[0,1,14,3],
			[0,1,15,4],
			[0,2,5,2],
			[0,2,8,2],
			[0,2,8,3],
			[0,2,9,1],
			[0,2,10,1],
			[0,2,11,4],
			[0,2,12,4],
			[0,2,13,3],
			[0,2,14,4],
			[0,2,15,2],
			[0,2,16,1],
			[0,3,6,3],
			[0,3,8,3],
			[0,3,9,1],
			[0,3,9,4],
			[0,3,10,1],
			[0,3,11,4],
			[0,3,15,2],
			[0,3,15,3],
			[0,3,16,2],
			[0,3,16,3],
			[0,4,6,3],
			[0,4,7,1],
			[0,4,8,3],
			[0,4,10,1],
			[0,4,10,3],
			[0,4,11,2],
			[0,4,13,4],
			[0,4,14,1],
			[0,4,15,4],
			[5,5,5,7],
			[5,5,6,11],
			[5,5,10,7],
			[5,5,12,16],
			[5,5,14,7],
			[5,6,5,13],
			[5,6,13,12],
			[5,6,16,13],
			[5,7,11,9],
			[5,7,12,10],
			[5,8,7,9],
			[5,8,8,8],
			[5,8,13,15],
			[5,8,14,8],
			[5,8,15,7],
			[5,9,9,15],
			[5,9,10,12],
			[5,10,8,11],
			[5,11,9,7],
			[5,11,14,7],
			[5,12,10,8],
			[5,12,12,12],
			[5,12,16,8],
			[5,13,11,15],
			[5,15,8,9],
			[5,15,10,13],
			[5,16,7,12],
			[5,16,11,7],
			[6,6,10,14],
			[6,6,16,9],
			[6,7,8,14],
			[6,7,12,13],
			[6,7,15,16],
			[6,7,16,13],
			[6,7,16,16],
			[6,8,13,7],
			[6,8,14,11],
			[6,9,8,12],
			[6,9,10,13],
			[6,9,11,14],
			[6,9,12,12],
			[6,9,14,8],
			[6,9,14,16],
			[6,10,8,14],
			[6,10,10,8],
			[6,10,10,10],
			[6,10,14,15],
			[6,11,6,14],
			[6,13,8,7],
			[6,13,14,10],
			[6,13,15,11],
			[6,13,16,14],
			[6,14,13,9],
			[6,15,7,9],
			[6,15,16,12],
			[6,16,14,7],
			[6,16,16,11],
			[7,7,7,11],
			[7,9,12,14],
			[7,9,13,15],
			[7,10,13,11],
			[7,10,15,10],
			[7,12,8,10],
			[7,12,14,9],
			[7,12,14,10],
			[7,12,16,12],
			[7,14,9,16],
			[7,14,14,12],
			[7,14,16,12],
			[7,16,11,16],
			[8,10,9,10],
			[8,11,12,13],
			[8,11,15,10],
			[8,12,8,13],
			[8,12,9,9],
			[8,12,10,15],
			[8,13,16,14],
			[8,15,9,9],
			[8,15,13,13],
			[8,16,9,13],
			[9,12,9,15],
			[9,12,12,15],
			[9,13,15,12],
			[9,15,11,11],
			[9,15,13,10],
			[9,16,16,14],
			[10,11,14,11],
			[10,11,16,16],
			[10,12,15,13],
			[10,13,15,13],
			[10,14,11,16],
			[10,15,16,14],
			[11,11,11,15],
			[11,11,12,16],
			[11,11,13,15],
			[11,11,13,16],
			[12,12,13,14],
			[13,15,15,14],
			[13,16,14,14],
			[14,16,15,15]
		]

		# Fixed piece,space,rotation
		self.fixed = [
			[ 0,0,1 ], # we fix a corner
		]

		puzzle.Puzzle.__init__( self )

